import wx
import wx.grid
import wx.lib.intctrl as intctrl
import wx.lib.masked as masked
import random
import bisect
import re
import Utils
from Utils				import logCall
import Model
import ColGrid
import EditEntry
from LineGraph import LineGraph
from GanttChartPanel import GanttChartPanel
from ReadSignOnSheet import GetTagNums, TagFields
from Undo import undo
import Gantt
from EditEntry import CorrectNumber, ShiftNumber, DeleteEntry
from HighPrecisionTimeEdit import HighPrecisionTimeEdit
from GetResults import GetResults, GetEntriesForNum, GetCategoryDetails
from NumberEntryDialog import NumberEntryDialog

def getStFtLaps( rider ):
	with Model.LockRace() as race:
		laps = race.getCategoryNumLaps( rider.num )
	st = rider.firstTime
	try:
		ft = st + rider.times[max( 0, min(laps-1, len(rider.times)-1) )]
	except (TypeError, AttributeError, IndexError):
		ft = None
	return st, ft, laps
	
class AdjustTimeDialog( wx.Dialog ):
	def __init__( self, parent, rider, riderName, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, _("Adjust Time Trial Times"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		self.rider = rider
		self.riderName = riderName
		fgs = wx.FlexGridSizer(rows=0, cols=2, vgap=4, hgap=4)
		fgs.AddGrowableCol( 1 )
		
		st, ft, laps = getStFtLaps( self.rider )
		ttPenalty = getattr( self.rider, 'ttPenalty', 0.0 )
			
		self.startTime = HighPrecisionTimeEdit( self, allow_none=not bool(st), seconds=st, size=(128,-1) )
		self.startTime.Bind( wx.EVT_TEXT, self.updateRideTime )
		self.finishTime = HighPrecisionTimeEdit( self, allow_none=not bool(ft), seconds=ft, size=(128,-1) )
		self.finishTime.Bind( wx.EVT_TEXT, self.updateRideTime )
		self.rideTime = wx.StaticText( self )
		self.penaltyTime = HighPrecisionTimeEdit( self, allow_none=True, seconds=ttPenalty, size=(128,-1) )
		self.note = wx.TextCtrl( self, size=(400, -1), value=getattr(self.rider, 'ttNote', u'') )
		self.updateRideTime( None )
				
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		fgs.Add( wx.StaticText( self ) )
		fgs.Add( wx.StaticText( self, label=((riderName + u': ') if riderName else u'') + unicode(rider.num) ), flag=wx.ALIGN_LEFT )
			
		fgs.Add( wx.StaticText( self, label=u'{}:'.format(_("Start"))), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.startTime, flag=wx.ALIGN_LEFT  )
		
		fgs.Add( wx.StaticText( self, label=u'{}:'.format(_("Finish"))), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.finishTime, flag=wx.ALIGN_LEFT )
		
		fgs.Add( wx.StaticText( self, label=u'{}:'.format(_("Ride Time"))), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.rideTime, flag=wx.ALIGN_LEFT )
		
		fgs.Add( wx.StaticText( self, label=u'{}:'.format(_("Penalty Time"))), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.penaltyTime, flag=wx.ALIGN_LEFT )
		
		fgs.Add( wx.StaticText( self, label=u'{}:'.format(_("Note"))),  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.note, flag=wx.ALIGN_LEFT )

		sizer = wx.BoxSizer( wx.VERTICAL )
		sizer.Add( fgs, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.okBtn, border=4, flag=wx.ALL )
		self.okBtn.SetDefault()
		hs.Add( self.cancelBtn, border=4, flag=wx.ALL )
		sizer.Add( hs, flag=wx.ALIGN_RIGHT|wx.ALL, border=4 )
		
		self.SetSizerAndFit(sizer)
		sizer.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )

	def updateRideTime( self, event = None ):
		st = self.startTime.GetSeconds()
		ft = self.finishTime.GetSeconds()
		ft = ft if ft else None
		try:
			self.rideTime.SetLabel( Utils.formatTime(ft - st, True) )
		except:
			self.rideTime.SetLabel( '' )

	def onOK( self, event ):
		stOld, ftOld, laps = getStFtLaps(self.rider)
		st, ft = self.startTime.GetSeconds() or None, self.finishTime.GetSeconds() or None
		if st is not None and ft is not None and st >= ft:
			Utils.MessageOK( self, _('Start Time must be before Finish Time'), _('Time Error'), wx.ICON_ERROR )
			return
			
		if stOld == st and ftOld == ft:
			Utils.refresh()
			self.EndModal( wx.ID_OK )
			return
		
		undo.pushState()
		
		firstTime = self.rider.firstTime
		if firstTime is None and not st:
			Utils.MessageOK( self, _('You must specify the Missing Start Time'), _('Missing Start Time'), wx.ICON_ERROR )
			return
			
		if firstTime is None:
			self.rider.times = []
			firstTime = 0.0
		
		riderTimeOfDay = [rt + firstTime for rt in self.rider.times]
		
		if ft:
			riderTimeOfDay = [rtod for rtod in riderTimeOfDay if rtod < ft][:laps]
			try:
				riderTimeOfDay[laps-1] = ft
			except IndexError:
				riderTimeOfDay.append( ft )

		if st:
			self.rider.firstTime = st
			
		self.rider.times = [rtod - self.rider.firstTime for rtod in riderTimeOfDay]
		self.rider.times = [rt for rt in self.rider.times if rt > 0.0]
		self.rider.ttPenalty = self.penaltyTime.GetSeconds()
		self.rider.ttNote = self.note.GetValue().strip()
					
		Model.race.setChanged()
		Utils.refresh()
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

class ChangeOffsetDialog( wx.Dialog ):
	def __init__( self, parent, rider, riderName, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, _("Adjust Start Time"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
		
		self.rider = rider
		self.riderName = riderName
		fgs = wx.FlexGridSizer(rows=0, cols=2, vgap=4, hgap=4)
		fgs.AddGrowableCol( 1 )

		self.earlyLate = wx.Choice( self, choices=(_("Rider Started Early"), _("Rider Started Late")) )
		self.earlyLate.SetSelection( 0 )
		self.adjustTime = HighPrecisionTimeEdit( self, allow_none=False, seconds=0.0, size=(128,-1) )
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		fgs.Add( wx.StaticText( self ) )
		fgs.Add( wx.StaticText( self, label=((riderName + u': ') if riderName else u'') + unicode(rider.num) ), flag=wx.ALIGN_LEFT )
			
		fgs.Add( wx.StaticText( self, label=u'{}:'.format(_("Adjust for"))), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.earlyLate, flag=wx.ALIGN_LEFT  )
		
		fgs.Add( wx.StaticText( self, label=u'{}:'.format(_("Adjustment Time"))), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.adjustTime, flag=wx.ALIGN_LEFT )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		sizer.Add( fgs, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.okBtn, border=4, flag=wx.ALL )
		self.okBtn.SetDefault()
		hs.Add( self.cancelBtn, border=4, flag=wx.ALL )
		sizer.Add( hs, flag=wx.ALIGN_RIGHT|wx.ALL, border=4 )
		
		self.SetSizerAndFit(sizer)
		sizer.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )

	def onOK( self, event ):
		race = Model.race
		adjustTime = self.adjustTime.GetSeconds()
		if not race or adjustTime == 0.0:
			self.EndModal( wx.ID_CANCEL )
			return
		
		if not race.isFinished():
			Utils.MessageOK( self, _('The race must be Finished before you can adjust a Start Wave Offset.'), _('Race Must be Finished'), wx.ICON_ERROR )
			self.EndModal( wx.ID_CANCEL )
			return
		
		if self.earlyLate.GetSelection() == 1:
			adjustTime = -adjustTime 
		
		undo.pushState()
		self.rider.times = [t + adjustTime for t in self.rider.times]
		Model.race.setChanged()
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

class RiderDetail( wx.Panel ):
	yellowColour = wx.Colour( 255, 255, 0 )
	orangeColour = wx.Colour( 255, 165, 0 )
	ignoreColour = wx.Colour( 180, 180, 180 )
		
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		
		self.SetDoubleBuffered( True )
		
		self.idCur = 0

		self.num = None
		self.iLap = None
		self.entry = None
		self.firstCall = True
		
		self.visibleRow = None
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		
		hs = wx.BoxSizer( wx.VERTICAL )
		
		gbs = wx.GridBagSizer(7, 4)
		row = 0
		self.numName = wx.StaticText( self, label = u'{} '.format(_('Number')) )
		gbs.Add( self.numName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.num = intctrl.IntCtrl( self, min=0, max=9999, allow_none=True, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER )
		self.num.Bind( wx.EVT_TEXT, self.onNumChange )
		#self.num.Bind( wx.EVT_TEXT_ENTER, self.onNumChange )
		#self.num.Bind( wx.EVT_KILL_FOCUS, self.onNumChange )
		gbs.Add( self.num, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		
		self.menu = wx.Menu()
		self.deleteMenuId = wx.NewId()
		self.menu.Append( self.deleteMenuId, _('&Delete Rider from Race...'), _('Delete this rider from the race') )
		self.Bind( wx.EVT_MENU, self.onDeleteRider, id = self.deleteMenuId )
		self.changeNumberMenuId = wx.NewId()
		self.menu.Append( self.changeNumberMenuId, _("&Change Rider's Number..."), _("Change this rider's number") )
		self.Bind( wx.EVT_MENU, self.onChangeNumber, id = self.changeNumberMenuId )
		self.swapNumberMenuId = wx.NewId()
		self.menu.Append( self.swapNumberMenuId, _('&Swap Number with Other Rider...'), _("Swap this rider's number with another rider's number") )
		self.Bind( wx.EVT_MENU, self.onSwapNumber, id = self.swapNumberMenuId )
		self.copyRiderMenuId = wx.NewId()
		self.menu.Append( self.copyRiderMenuId, _('C&opy Rider Times to New Number...'), _("Copy these rider's times to another number") )
		self.Bind( wx.EVT_MENU, self.onCopyRider, id = self.copyRiderMenuId )
		self.changeOffsetMenuId = wx.NewId()
		self.menu.Append( self.changeOffsetMenuId, _('Change Start W&ave Time...'), _("Fix lap times if the rider started in the wrong start wave") )
		self.Bind( wx.EVT_MENU, self.onChangeOffset, id = self.changeOffsetMenuId )
		
		self.editRiderBtn = wx.Button( self, label = u'{}...'.format(_('Edit')) )
		self.Bind( wx.EVT_BUTTON, self.onEditRider, self.editRiderBtn )
		gbs.Add( self.editRiderBtn, pos=(row, 3), span=(1,1), flag=wx.EXPAND )
		
		self.riderName = wx.StaticText( self )
		gbs.Add( self.riderName, pos=(row, 4), span=(1,1) )
		
		row += 1
		
		self.nameName = wx.StaticText( self, label = u'{} '.format(_('Name')) )
		gbs.Add( self.nameName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.riderName = wx.StaticText( self )
		gbs.Add( self.riderName, pos=(row,1), span=(1,4), flag=wx.EXPAND )
		
		self.startTimeName = wx.StaticText( self, label = u'{} '.format(_('Start')) )
		gbs.Add( self.startTimeName, pos=(row,5), span=(1,1), flag=labelAlign )
		self.startTime = wx.StaticText( self, label = u'00:00:00' )
		gbs.Add( self.startTime, pos=(row,6), span=(1,1), flag=wx.EXPAND )
		
		row += 1
		
		self.teamName = wx.StaticText( self, label = u'{} '.format(_('Team')) )
		gbs.Add( self.teamName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.riderTeam = wx.StaticText( self )
		gbs.Add( self.riderTeam, pos=(row,1), span=(1,4), flag=wx.EXPAND )
		
		self.finishTimeName = wx.StaticText( self, label = u'{} '.format(_('Finish')) )
		gbs.Add( self.finishTimeName, pos=(row,5), span=(1,1), flag=labelAlign )
		
		self.finishTime = wx.StaticText( self, label = u'00:00:00' )
		gbs.Add( self.finishTime, pos=(row,6), span=(1,1), flag=wx.EXPAND )
		
		row += 1
		
		self.tagsName = wx.StaticText( self, label = u'{} '.format(_('Tag(s)')) )
		gbs.Add( self.tagsName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.tags = wx.StaticText( self )
		gbs.Add( self.tags, pos=(row,1), span=(1,4), flag=wx.EXPAND )

		self.rideTimeName = wx.StaticText( self, label = u'{} '.format(_('Ride Time')) )
		gbs.Add( self.rideTimeName, pos=(row,5), span=(1,1), flag=labelAlign )
		
		self.rideTime = wx.StaticText( self, label = u'00:00:00' )
		gbs.Add( self.rideTime, pos=(row,6), span=(1,1), flag=wx.EXPAND )
		
		row += 1
		
		self.categoryName = wx.StaticText( self, label = u'{} '.format(_('Category')) )
		gbs.Add( self.categoryName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.category = wx.Choice( self )
		self.Bind( wx.EVT_CHOICE, self.onCategoryChoice, self.category )
		gbs.Add( self.category, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		
		self.penaltyTimeName = wx.StaticText( self, label = u'{} '.format(_('Penalty Time')) )
		gbs.Add( self.penaltyTimeName, pos=(row,5), span=(1,1), flag=labelAlign )
		self.penaltyTime = wx.StaticText( self, label = u'00:00:00' )
		gbs.Add( self.penaltyTime, pos=(row,6), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL )
		
		row += 1
		
		GetTranslation = _
		self.statusName = wx.StaticText( self, label = u'{} '.format(_('Status')) )
		gbs.Add( self.statusName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.statusOption = wx.Choice( self, choices=[GetTranslation(n) for n in Model.Rider.statusNames] )
		gbs.Add( self.statusOption, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		self.Bind(wx.EVT_CHOICE, self.onStatusChanged, self.statusOption)
		
		self.atRaceTimeName = wx.StaticText( self, label= u'{} '.format(_('at race time')) )
		gbs.Add( self.atRaceTimeName, pos=(row,2), span=(1,1), flag=labelAlign )
		self.atRaceTime = HighPrecisionTimeEdit( self, size=(128,-1) )
		self.atRaceTime.SetSeconds( 0 )
		self.atRaceTime.SetEditable( False )
		self.atRaceTime.Enable( False )
		gbs.Add( self.atRaceTime, pos=(row,3), span=(1,1), flag=wx.EXPAND )
		
		self.noteName = wx.StaticText( self, label =  u'{} '.format(_('Note')) )
		gbs.Add( self.noteName, pos=(row,5), span=(1,1), flag=labelAlign )
		self.note = wx.StaticText( self )
		gbs.Add( self.note, pos=(row,6), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL )
		row += 1
		
		self.relegatedName = wx.StaticText( self, label = u'{} '.format(_('Relegated to')) )
		gbs.Add( self.relegatedName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.relegatedPosition = intctrl.IntCtrl( self, min=2, max=9999, allow_none=True, value=None, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER )

		gbs.Add( self.relegatedPosition, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		row += 1
		
		self.autocorrectLaps = wx.CheckBox( self, label = _('Autocorrect Lap Data') )
		self.Bind( wx.EVT_CHECKBOX, self.onAutocorrectLaps, self.autocorrectLaps )
		self.alwaysFilterMinPossibleLapTime = wx.CheckBox( self, label = _('Always Filter on Min Possble Lap Time'), style=wx.ALIGN_RIGHT )
		self.Bind( wx.EVT_CHECKBOX, self.onAutocorrectLaps, self.alwaysFilterMinPossibleLapTime )
		
		vb = wx.BoxSizer( wx.VERTICAL )
		vb.Add( self.autocorrectLaps, flag=wx.ALL, border=2 )
		vb.Add( self.alwaysFilterMinPossibleLapTime, flag=wx.ALL, border=2 )
		gbs.Add( vb, pos = (row, 0), span=(1, 2), flag = wx.ALIGN_RIGHT )
		
		self.showPhotos = wx.Button( self, label = u'{}...'.format(_('Show Photos')) )
		gbs.Add( self.showPhotos, pos = (row, 3), span=(1, 1), flag = wx.ALIGN_CENTRE|wx.EXPAND )
		self.Bind( wx.EVT_BUTTON, self.onShowPhotos, self.showPhotos )
		self.adjustTime = wx.Button( self, label = u'{}...'.format(_('Adjust Time Trial Times')) )
		self.Bind( wx.EVT_BUTTON, self.onAdjustTime, self.adjustTime )
		gbs.Add( self.adjustTime, pos=(row,5), span=(1,2), flag=wx.EXPAND )
		row += 1
		
		self.showPhotos.Disable()

		self.notInLap = wx.StaticText( self, label = u'              ' )
		gbs.Add( self.notInLap, pos=(row,0), span=(1,4) )
		row += 1
	
		hs.Add( gbs, proportion = 0 )
		
		splitter = wx.SplitterWindow( self )
		self.splitter = splitter
		
		colnames = (
			'Lap', 'Lap Time', 'Race', 'Clock',
			'Edit', 'By', 'On', 'Note',
			'Lap Speed', 'Race Speed',
		)
		self.nameCol = {c:i for i, c in enumerate(colnames)}
		
		self.colnames = [Utils.translate(c) for c in colnames]
		self.grid = ColGrid.ColGrid( splitter, self.colnames, style=wx.BORDER_SUNKEN )
		
		self.grid.SetRowLabelSize( 0 )
		self.grid.SetRightAlign( True )
		self.grid.SetLeftAlignCols( [4, 5, 6] )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()
		try:
			self.grid.SetSelectionMode( wx.grid.Grid.SelectRows )
		except AttributeError:
			self.grid.SetSelectionMode( 1 )
		self.Bind( wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.getPopupFuncCB(self.OnPopupCorrect) )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doRightClick )

		panel = wx.Panel( splitter, wx.ID_ANY, style = wx.BORDER_SUNKEN )
		
		self.lineGraph = LineGraph( panel, style = wx.NO_BORDER )
		
		self.ganttChart = GanttChartPanel( panel, style = wx.NO_BORDER )
		self.ganttChart.getNowTimeCallback = Gantt.GetNowTime
		self.ganttChart.minimizeLabels = True
		self.ganttChart.rClickCallback = self.onEditGantt
		
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( self.ganttChart, proportion=0, border = 0, flag = wx.ALL | wx.EXPAND )
		vbs.Add( self.lineGraph, proportion=1, border = 0, flag = wx.ALL | wx.EXPAND )
		panel.SetSizer( vbs )
		
		splitter.SetMinimumPaneSize( 100 )
		splitter.SplitVertically( self.grid, panel, 300 )
		
		sFirstRecordedTime = wx.BoxSizer( wx.HORIZONTAL )
		self.earlyStartWaveName = wx.StaticText( self, label=_('Started in Early Wave') )
		self.earlyStartWave = wx.StaticText( self, label=_('            ') )
		sFirstRecordedTime.Add( self.earlyStartWaveName )
		sFirstRecordedTime.Add( self.earlyStartWave, flag=wx.LEFT, border=4 )
		hs.Add( sFirstRecordedTime, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=4 )
		
		hs.Add( splitter, proportion = 1, flag = wx.EXPAND|wx.TOP, border = 4 )
		
		self.setAtRaceTime()
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		mainSizer.Add( hs, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		self.SetSizer( mainSizer )
		self.hs = hs
		self.setRider()
	
	@logCall
	def onShowPhotos( self, event ):
		mainWin = Utils.mainWin
		if not mainWin:
			return
		mainWin.photoDialog.Show( True )
		mainWin.photoDialog.setNumSelect( self.num.GetValue() )
	
	@logCall
	def onAdjustTime( self, event ):
		if self.num.GetValue() is None:
			return
		num = int(self.num.GetValue())
		with Model.LockRace() as race:
			if not getattr(race, 'isTimeTrial', False) or num not in race.riders:
				return
			rider = race.getRider( num )
		dlg = AdjustTimeDialog( self, rider, self.riderName.GetLabel() )
		dlg.ShowModal()
		dlg.Destroy()
	
	def onCategoryChoice( self, event ):
		if self.num.GetValue() is None:
			return
		num = int(self.num.GetValue())
		catName = self.category.GetStringSelection()
		
		undo.pushState()
		with Model.LockRace() as race:
			if not race:
				return
			for c in race.getCategories( startWaveOnly = False, excludeCustom = True, excludeCombined = True ):
				if c.fullname == catName:
					race.addCategoryException( c, num )
					break
		wx.CallAfter( self.refresh )
	
	def getLapClicked( self, event ):
		row = event.GetRow()
		if row >= self.grid.GetNumberRows():
			return None
		lapValue = self.grid.GetCellValue(row, self.nameCol['Lap']).strip()
		try:
			return int(lapValue)
		except:
			return None
		
	ids = []
	def NewId( self ):
		try:
			id = RiderDetail.ids[self.idCur]
		except IndexError:
			id = wx.NewId()
			RiderDetail.ids.append( id )
		self.idCur += 1
		return id
	
	def getEntryFromClick( self, event ):
		self.eventRow = event.GetRow()
		self.visibleRow = self.eventRow
		if self.num.GetValue() is None:
			return False
		
		try:
			num = int(self.num.GetValue())
		except:
			return False
			
		self.iLap = self.getLapClicked( event )
		if not self.iLap:
			return False
		
		race = Model.race
		if not race or num not in race.riders:
			return False
		
		entries = race.riders[num].interpolate()
		
		try:
			self.entry = entries[self.iLap]
		except:
			return False
			
		return True
	
	def getPopupFuncCB( self, func ):
		def handler( event ):
			if self.getEntryFromClick( event ):
				func( event )
		return handler
	
	def doRightClick( self, event ):
		if not self.getEntryFromClick( event ):
			return
		
		allCases = 0
		interpCase = 1
		nonInterpCase = 2
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				(self.NewId(), _('Add Missing Last Lap'),	_('Add Missing Last Lap'),	self.OnPopupAddMissingLastLap, allCases),
				(None, None, None, None, None),
				(self.NewId(), _('Pull After Lap') + u'...',_('Pull After lap'),	self.OnPopupPull, allCases),
				(self.NewId(), _('DNF After Lap') + u'...',	_('DNF After lap'),	self.OnPopupDNF, allCases),
				(None, None, None, None, None),
				(self.NewId(), _('Correct') + u'...',		_('Change number or lap time') + u'...',	self.OnPopupCorrect, interpCase),
				(self.NewId(), _('Shift') + u'...',			_('Move lap time earlier/later') + u'...',	self.OnPopupShift, interpCase),
				(self.NewId(), _('Delete') + u'...',		_('Delete lap time(s)') + u'...',	self.OnPopupDelete, nonInterpCase),
				(None, None, None, None, None),
				(self.NewId(), _('Note') + u'...',			_('Add/Edit lap note'),	self.OnPopupNote, nonInterpCase),
			]
			for p in self.popupInfo:
				if p[0]:
					self.Bind( wx.EVT_MENU, p[3], id=p[0] )
			
			self.menuOptions = []
			for caseCode in xrange(3):
				menu = wx.Menu()
				for id, name, text, callback, cCase in self.popupInfo:
					if not id:
						if not Utils.hasTrailingSeparator(menu):
							menu.AppendSeparator()
						continue
					if caseCode >= cCase:
						menu.Append( id, name, text )
				self.menuOptions.append( menu )
		
		try:
			caseCode = 1 if self.entry.interp else 2
		except (TypeError, IndexError, KeyError):
			caseCode = 0
		
		menu = self.menuOptions[caseCode]
		try:
			self.PopupMenu( menu )
		except Exception as e:
			Utils.writeLog( 'RiderDetail:doRightClick: {}'.format(e) )

	def OnPopupPull( self, event ):
		self.grid.SelectRow( self.eventRow )
		self.OnGanttPopupPull( event )
		
	def OnPopupDNF( self, event ):
		self.grid.SelectRow( self.eventRow )
		self.OnGanttPopupDNF( event )
		
	def OnPopupCorrect( self, event ):
		self.grid.SelectRow( self.eventRow )
		CorrectNumber( self, self.entry )
		
	def OnPopupShift( self, event ):
		self.grid.SelectRow( self.eventRow )
		ShiftNumber( self, self.entry )

	def OnPopupDelete( self, event ):
		rows = Utils.GetSelectedRows( self.grid )
		
		try:
			self.visibleRow = min( rows )
		except:
			self.visibleRow = None
			
		if len(rows) > 1:
			try:
				num = int(self.num.GetValue())
			except:
				return
			if not Model.race or num not in Model.race:
				return
			rider = Model.race.riders[num]
			times = []
			for r in rows:
				try:
					times.append( rider.times[r] )
				except IndexError:
					pass
			timeStr = []
			timesPerRow = 4
			for i in xrange(0, len(times), timesPerRow):
				timeStr.append(
					u',  '.join( u'{} {}: {}'.format(_('Lap'), rows[j]+1, Utils.formatTime(times[i]))
							for j in xrange(i, min(len(times), i+timesPerRow) ) ) )
			timeStr = u',\n'.join( timeStr )
			message = u'{} {}:\n\n{}\n\n{}?'.format(_('Delete entries of Bib'), num, timeStr, _('Confirm Delete'))
			if Utils.MessageOKCancel( self, message, _('Delete Times'), wx.ICON_WARNING ):
				undo.pushState()
				with Model.LockRace() as race:
					if race:
						for t in times:
							race.deleteTime( num, t )
				wx.CallAfter( self.refresh )
		else:
			self.grid.SelectRow( self.eventRow )
			DeleteEntry( self, self.entry )
	
	def OnPopupAddMissingLastLap( self, event ):
		try:
			num = int(self.num.GetValue())
		except:
			return
			
		race = Model.race
		if not race or num not in race.riders:
			return
			
		rider = race.riders[num]
			
		times = list(rider.times)
		times.insert(0, 0.0)		# Add a zero starting time.
			
		if rider.status != rider.Finisher:
			Utils.MessageOK( self, _('Cannot add Last Lap unless Rider is Finisher'), _('Cannot add Last Lap') )
			return
				
		undo.pushState()
		if rider.autocorrectLaps:
			if Utils.MessageOKCancel( self, _('Turn off Autocorrect first?'), _('Turn off Autocorrect') ):
				rider.autocorrectLaps = False
		
		if not race.isTimeTrial:
			waveCategory = race.getCategory( num )
			if waveCategory:
				times[0] = waveCategory.getStartOffsetSecs()
		
		if len(times) >= 2:
			tNewLast = times[-1] + times[-1] - times[-2]
		elif len(times) == 1:
			tNewLast = times[0] + 10*60
				
		race.numTimeInfo.add( num, tNewLast )
		race.addTime( num, tNewLast + ((rider.firstTime or 0.0) if race.isTimeTrial else 0.0) )
		race.setChanged()
		self.visibleRow = self.grid.GetNumberRows()
		
		wx.CallAfter( self.refresh )
	
	def OnPopupNote( self, event ):
		self.grid.SelectRow( self.eventRow )
		try:
			num = int(self.num.GetValue())
		except:
			return
			
		if not Model.race or num not in Model.race:
			return
			
		lap = self.eventRow + 1
		race = Model.race
		rider = race.riders[num]
			
		race.lapNote = getattr(race, 'lapNote', {})
		dlg = wx.TextEntryDialog( self, u'{}: {}: {}: {}'.format(_("Bib"), num, _("Note on Lap"), lap), _("Lap Note"),
					Model.race.lapNote.get( (num, lap), '' ) )
		ret = dlg.ShowModal()
		value = dlg.GetValue().strip()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return
		
		undo.pushState()
		if value:
			race.lapNote[(self.entry.num, self.entry.lap)] = value
			race.setChanged()
		else:
			try:
				del race.lapNote[(self.entry.num, self.entry.lap)]
				race.setChanged()
			except KeyError:
				pass
		wx.CallAfter( self.refresh )
	
	def onEditRider( self, event ):
		self.PopupMenu( self.menu )
	
	def onDeleteRider( self, event ):
		if not Model.race:
			return
			
		try:
			num = int(self.num.GetValue())
		except:
			return
			
		with Model.LockRace() as race:
			if not num in race:
				self.setRider( None )
				self.refresh()
				return
			
		if Utils.MessageOKCancel( self, u'{}: {}: {}'.format(_('Bib'), num, _("Confirm Delete")), _("Delete Rider") ):
			undo.pushState()
			with Model.LockRace() as race:
				race.deleteRider( num )
			self.setRider( None )
			self.refresh()
			wx.CallAfter( Utils.refreshForecastHistory )
			wx.CallAfter( Utils.refresh )
		
	def onChangeNumber( self, event ):
		if not Model.race:
			return
			
		try:
			num = int(self.num.GetValue())
		except:
			return
			
		with Model.LockRace() as race:
			if not num in race:
				return
		
		dlg = wx.TextEntryDialog( self, _("Rider's new number:"), _('New Number'), u'{}'.format(self.num.GetValue()) )
		ret = dlg.ShowModal()
		newNum = dlg.GetValue()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return
			
		try:
			newNum = int(re.sub( '[^0-9]', '', newNum ))
		except ValueError:
			return
			
		with Model.LockRace() as race:
			inRace = (newNum in race.riders)
		if inRace:
			Utils.MessageOK(
				self,
				u'{}\n{}'.format(
					_("Cannot Change Bib."),
					_("There is a rider with this number already.")
				),
				_('Cannot Change Rider Number'), iconMask = wx.ICON_ERROR )
			return
			
		if Utils.MessageOKCancel( self, u"{}: {}.".format(_("Confirm Change rider's number"), newNum), _("Change Rider Number") ):
			undo.pushState()
			with Model.LockRace() as race:
				race.renumberRider( num, newNum )
				race.numTimeInfo.renumberRider( num, newNum )
			self.setRider( newNum )
			self.refresh()
			wx.CallAfter( Utils.refreshForecastHistory )
			wx.CallAfter( Utils.refresh )
	
	def onSwapNumber( self, event ):
		if not Model.race:
			return
			
		try:
			num = int(self.num.GetValue())
		except:
			return
			
		with Model.LockRace() as race:
			if not num in race:
				return
		
		dlg = wx.TextEntryDialog( self, _("Number to swap with:"), _('Swap Numbers'), u'{}'.format(self.num.GetValue()) )
		ret = dlg.ShowModal()
		newNum = dlg.GetValue()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return
			
		try:
			newNum = int(re.sub( '[^0-9]', '', newNum))
		except ValueError:
			return
			
		race = Model.race
		if newNum not in race.riders:
			Utils.MessageOK(
				self,
				u'{}\n{}'.format(
					_("Cannot swap with specified rider."),
					_("This rider is not in race."),
				),
				_('Cannot Swap Rider Numbers'), iconMask = wx.ICON_ERROR
			)
			return
			
		if Utils.MessageOKCancel( self, u"{}\n\n   {} \u21D4 {}.".format(_('Confirm Swap numbers'), num, newNum), _("Swap Rider Number") ):
			undo.pushState()
			race.swapRiders( num, newNum )
			race.numTimeInfo.swapRiders( num, newNum )
			self.setRider( newNum )
			self.refresh()
			wx.CallAfter( Utils.refreshForecastHistory )
			wx.CallAfter( Utils.refresh )

		
	def onCopyRider( self, event ):
		if not Model.race:
			return
			
		try:
			num = int(self.num.GetValue())
		except:
			return
			
		with Model.LockRace() as race:
			if not num in race:
				return
		
		dlg = wx.TextEntryDialog(
			self,
			u'{} {}: {}\n\n{}:'.format(
				_('Bib'), num,
				_("All time entries will be copied to the new bib number."), 
				_("New Bib Number")
			),
			_('Copy Rider Times'), u'{}'.format(self.num.GetValue())
		)
		ret = dlg.ShowModal()
		newNum = dlg.GetValue()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return
			
		try:
			newNum = int(re.sub( '[^0-9]', '', newNum))
		except ValueError:
			return
			
		with Model.LockRace() as race:
			inRace = (newNum in race.riders)
		if inRace:
			if num != newNum:
				if not Utils.MessageOKCancel( self,
							u'{} ({}).\n\n{}\n\n{}'.format(
								_("New Bib Number Exists"), newNum,
								_("This operation will replace all existing data."),
								_("Continue?"),
							),
							_('New Bib Number Exists'), iconMask = wx.ICON_WARNING
						):
					return
			else:
				Utils.MessageOK( self,
					u'{} ({})'.format(_('Cannot Copy to Same Number'), newNum),
					_('Cannot Copy to Same Number'), iconMask = wx.ICON_ERROR
				)
				return
			
		if Utils.MessageOKCancel( self,
				u'{} {}:  {}: {}\n\n{}\n\n{}?'.format(
					_('Bib'), num,
					_('Entries will be copied to new Bib'), newNum,
					_('All entries will be slightly earlier.'),
					_('Continue'),
				),
				_("Confirm Copy Rider Times") ):
			undo.pushState()
			with Model.LockRace() as race:
				race.riders.pop( newNum, None )
				race.copyRiderTimes( num, newNum )
				rNew = race.getRider( newNum )
				numTimeInfo = race.numTimeInfo
				for t in rNew.times:
					numTimeInfo.add( newNum, t )
			self.setRider( newNum )
			self.onNumChange()
			wx.CallAfter( Utils.refreshForecastHistory )
			wx.CallAfter( Utils.refresh )
	
	def onChangeOffset( self, event ):
		if self.num.GetValue() is None:
			return
		num = int(self.num.GetValue())
		with Model.LockRace() as race:
			if num not in race.riders:
				return
			rider = race.getRider( num )
		dlg = ChangeOffsetDialog( self, rider, self.riderName.GetLabel() )
		ret = dlg.ShowModal()
		dlg.Destroy()
		if ret == wx.ID_OK:
			wx.CallAfter( self.refresh )
			wx.CallAfter( Utils.refresh )
	
	def onNumChange( self, event = None ):
		self.refresh()
	
	def onStatusChanged( self, event ):
		num = self.num.GetValue()
		if not Model.race or num not in Model.race:
			return
			
		statusOption = self.statusOption.GetSelection()
		if statusOption in [Model.Rider.DNF, Model.Rider.Pulled]:
			# Get any existing rider status time.
			with Model.LockRace() as race:
				rider = race.getRider( num )
				tStatusCur = rider.tStatus
				
			# Try to fill in a reasonable default value.
			if not tStatusCur:
				tStatus = race.lastRaceTime()
				# If a DNF, set the time to just after the last recorded lap.
				# User can always adjust it later.
				if statusOption == Model.Rider.DNF or (not race.isRunning() and statusOption == Model.Rider.Pulled):
					try:
						tStatus = rider.times[-1] + 1.0
					except (IndexError, TypeError):
						pass
				tStatus = min( tStatus, 7*24*60*60 )
				self.atRaceTime.SetValue( Utils.SecondsToStr(tStatus) )
				
		self.commitChange()
		wx.CallAfter( self.refresh )
		wx.CallAfter( Utils.refresh )
		wx.CallAfter( Utils.refreshForecastHistory )
		
	def onAutocorrectLaps( self, event ):
		num = self.num.GetValue()
		if not Model.race or num not in Model.race:
			self.autocorrectLaps.SetValue( True )
			self.alwaysFilterMinPossibleLapTime.SetValue( True )
			return
		undo.pushState()
		with Model.LockRace() as race:
			rider = race.riders[num]
			rider.autocorrectLaps = self.autocorrectLaps.GetValue()
			rider.alwaysFilterMinPossibleLapTime = self.alwaysFilterMinPossibleLapTime.GetValue()
			race.setChanged()
		self.refresh()
		wx.CallAfter( Utils.refreshForecastHistory )
		wx.CallAfter( Utils.refresh )
	
	def setRider( self, n = None ):
		Utils.SetValue( self.num, int(n) if n is not None else None )
		
	def getGanttChartPanelNumLapTimes( self ):
		lapCur = getattr(self, 'lapCur', None)
		if lapCur is None:
			return None, None, None

		num = self.num.GetValue()
		try:
			num = int(num)
		except:
			return None, None, None
			
		with Model.LockRace() as race:
			if not race or num not in race:
				return None, None, None

		try:
			times = self.ganttChart.data[0]
		except:
			return None, None, None
		return num, lapCur, times
	
	def doSplitLap( self, splits ):
		num, lap, times = self.getGanttChartPanelNumLapTimes()
		if num is None:
			return
		EditEntry.AddLapSplits( num, lap, times, splits )
		self.refresh()
	
	def doCustomSplitLap( self ):
		dlg = NumberEntryDialog( self, message = "", caption = _("Add Missing Splits"), prompt = _("Missing Splits to Add:"),
									value = 1, min = 1, max = 500 )
		splits = None
		if dlg.ShowModal() == wx.ID_OK:
			splits = dlg.GetValue() + 1
		dlg.Destroy()
		if splits is not None:
			self.doSplitLap( splits )
	
	def OnGanttPopupLapDetail( self, event ):
		num, lap, times = self.getGanttChartPanelNumLapTimes()
		if num is None:
			return
		with Model.LockRace() as race:
			if not race:
				return
			tLapStart = times[lap-1]
			tLapEnd = times[lap]
		
			try:
				riderInfo = race.excelLink.read()[num]
			except:
				riderInfo = {}
				
			try:
				riderName = u'{}, {} {}: {}'.format(riderInfo['LastName'], riderInfo['FirstName'], _('Bib'), num)
			except KeyError:
				try:
					riderName = u'{} {}: {}'.format(riderInfo['LastName'], _('Bib'), num)
				except KeyError:
					try:
						riderName = u'{} {}: {}'.format(riderInfo['FirstName'], _('Bib'), num)
					except KeyError:
						riderName = u'{}: {}'.format(_('Bib'), num)

			try:
				riderName += u' {}: {}'.format( _('Age'), riderInfo['Age'] )
			except KeyError:
				pass
			
			infoStart = race.numTimeInfo.getInfoStr( num, tLapStart )
			if infoStart:
				infoStart = _('\nLap Start ') + infoStart
			infoEnd = race.numTimeInfo.getInfoStr( num, tLapEnd )
			if infoEnd:
				infoEnd = _('\nLap End ') + infoEnd
		
			info = (u'{}: {}  {}: {}\n{}: {}  {}: {}\n{}: {}\n{}{}'.format(
					_('Rider'), riderName,
					_('Lap'), lap,
					_('Lap Start'), Utils.formatTime(tLapStart),
					_('Lap End'), Utils.formatTime(tLapEnd),
					_('Lap Time'), Utils.formatTime(tLapEnd - tLapStart), infoStart, infoEnd )).strip()
					
		Utils.MessageOK( self, info, _('Lap Details'), pos=wx.GetMousePosition() )

	def onEditGantt( self, xPos, yPos, num, iRider, lap ):
		allCases = 0
		interpCase = 1
		nonInterpCase = 2
		
		self.lapCur = lap
		num = self.num.GetValue()
		if num is None:
			return
		with Model.LockRace() as race:
			if not race:
				return
			try:
				entries = race.getRider(num).interpolate()
				self.entry = entries[lap]
				caseCode = 1 if entries[lap].interp else 2
			except IndexError:
				return

		if not hasattr(self, 'ganttMenuInfo'):
			self.ganttMenuInfo = [
				(wx.NewId(), _('Add Missing Last Lap'),			_('Add missing last lap'),				self.OnPopupAddMissingLastLap, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Pull after Lap End') + u'...',	_('Pull after Lap End'),				self.OnGanttPopupPull, allCases),
				(wx.NewId(), _('DNF after Lap End') + u'...',	_('DNF after Lap End'),					self.OnGanttPopupDNF, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Correct lap End Time') + u'...',_('Correct lap End Time'),				lambda event, s = self: CorrectNumber(s, s.entry), interpCase),
				(wx.NewId(), _('Shift Lap End Time') + u'...',	_('Move lap end time earlier/later'),	lambda event, s = self: ShiftNumber(s, s.entry), interpCase),
				(wx.NewId(), _('Delete Lap End Time') + u'...',	_('Delete Lap End Time'),				lambda event, s = self: DeleteEntry(s, s.entry), nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), _('Note') + u'...',				_('Add/Edit lap Note'),					self.OnGanttPopupLapNote, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Show Lap Details') + u'...', 	_('Show Lap Details'),					self.OnGanttPopupLapDetail, allCases),
			]
			self.splitMenuInfo = [
					(wx.NewId(),
					u'{} {}'.format( split-1, _('Splits') if split > 2 else _('Split') ),
					lambda evt, s = self, splits = split: s.doSplitLap(splits)) for split in xrange(2,8) ] + [
					(wx.NewId(),
					_('Custom') + u'...',
					lambda evt, s = self: s.doCustomSplitLap())]
			for id, name, text, callback, cCase in self.ganttMenuInfo:
				if id:
					self.Bind( wx.EVT_MENU, callback, id=id )
			for id, name, callback in self.splitMenuInfo:
				self.Bind( wx.EVT_MENU, callback, id=id )
			self.splitMenuId = wx.NewId()
		
		menu = wx.Menu()
		for id, name, text, callback, cCase in self.ganttMenuInfo:
			if not id:
				Utils.addMissingSeparator( menu )
				continue
			if caseCode < cCase:
				continue
			menu.Append( id, name, text )
			
		if caseCode == 2:
			submenu = wx.Menu()
			for id, name, callback in self.splitMenuInfo:
				submenu.Append( id, name )
			Utils.addMissingSeparator( menu )
			menu.PrependSeparator()
			menu.Prepend( self.splitMenuId, _('Add Missing Split'), submenu )
			
		Utils.deleteTrailingSeparators( menu )
		try:
			self.PopupMenu( menu )
			menu.Destroy()
		except Exception as e:
			Utils.writeLog( 'RiderDetail:onEditGantt: {}'.format(e) )
	
	def OnGanttPopupPull( self, event ):
		if not self.entry:
			return
		if not Utils.MessageOKCancel( self,
			u'{}: {}  {} {} - {}?'.format(
				_('Bib'), self.entry.num,
				_('Pull after lap'), self.entry.lap, Utils.formatTime(self.entry.t+1, True), ),
			_('Pull Rider') ):
			return
		try:
			undo.pushState()
			with Model.LockRace() as race:
				race.getRider(self.entry.num).setStatus( Model.Rider.Pulled, self.entry.t + 1 )
				race.setChanged()
		except:
			pass
		wx.CallAfter( self.refresh )
		wx.CallAfter( Utils.refreshForecastHistory )
	
	def OnGanttPopupDNF( self, event ):
		if not Utils.MessageOKCancel( self,
			u'{}: {}  {} {} - {}?'.format(
				_('Bib'), self.entry.num,
				_('DNF after lap'), self.entry.lap, Utils.formatTime(self.entry.t+1, True), ),
			_('DNF Rider') ):
			return
		try:
			undo.pushState()
			with Model.LockRace() as race:
				race.getRider(self.entry.num).setStatus( Model.Rider.DNF, self.entry.t + 1 )
				race.setChanged()
		except:
			pass
		wx.CallAfter( self.refresh )
		wx.CallAfter( Utils.refreshForecastHistory )
		
	def OnGanttPopupLapNote( self, event ):
		if not self.entry or not Model.race:
			return
		if not hasattr(Model.race, 'lapNote'):
			Model.race.lapNote = {}
		dlg = wx.TextEntryDialog( self,
				u"{}: {}  {}: {}".format(
					_('Bib'), self.entry.num,
					_('Note for lap'), self.entry.lap,
				),
				_("Lap Note"),
				Model.race.lapNote.get( (self.entry.num, self.entry.lap), u'' ) )
		ret = dlg.ShowModal()
		value = dlg.GetValue().strip()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return
		undo.pushState()
		with Model.LockRace() as race:
			if value:
				race.lapNote[(self.entry.num, self.entry.lap)] = value
				race.setChanged()
			else:
				try:
					del race.lapNote[(self.entry.num, self.entry.lap)]
					race.setChanged()
				except KeyError:
					pass
		wx.CallAfter( self.refresh )

	def setNumSelect( self, num ):
		self.setRider( num )
	
	def setAtRaceTime( self, secs = 0.0, editable = False ):
		self.atRaceTime.SetSeconds( secs )
		self.atRaceTime.SetEditable( editable )
		self.atRaceTime.Enable( editable )
		self.atRaceTimeName.Enable( editable )
	
	def skipUpdate( self ):
		race = Model.race
		if not race:
			return False
		rider = race.riders.get( self.num.GetValue(), None )
		if not rider:
			return False
		attr = ('num', 'times', 'status', 'firstTime', 'relegatedPosition', 'autocorrectLaps', 'alwaysFilterMinPossibleLapTime')
		riderInfo = {a: getattr(rider,a) for a in attr}
		riderInfo['category'] = race.getCategory( rider.num )
		riderInfo['lapNote'] = getattr(race, 'lapNote', {})
		if riderInfo != getattr(self, 'riderInfoCache', {}):
			riderInfo['times'] = list(riderInfo['times'])		# Make a copy so we can compare to the original.
			riderInfo['lapNote'] = riderInfo['lapNote'].copy()	# There don't change much, so make a copy.
			self.riderInfoCache = riderInfo
			return False
		return True
	
	def refresh( self, forceUpdate=False ):
		if not forceUpdate and self.skipUpdate():
			return
	
		num = self.num.GetValue()
		
		visibleRow = self.visibleRow
		self.visibleRow = None

		data = [ [] for c in xrange(len(self.colnames)) ]
		self.grid.Set( data = data )
		self.grid.Reset()
		self.category.Clear()
		self.autocorrectLaps.SetValue( True )
		self.alwaysFilterMinPossibleLapTime.SetValue( True )
		
		self.statusOption.SetSelection( 0 )
		self.setAtRaceTime( 0.0, False )
		
		self.lineGraph.SetData( None )
		self.ganttChart.SetData( [] )
		self.riderName.SetLabel( '' )
		self.riderTeam.SetLabel( '' )
		self.tags.SetLabel( '' )
		
		for w in [	'startTimeName',	'startTime',
					'finishTimeName',	'finishTime',
					'rideTimeName',		'rideTime',
					'penaltyTimeName',	'penaltyTime',
					'noteName',			'note',
					'earlyStartWaveName','earlyStartWave',
					'adjustTime']:
			getattr( self, w ).Show( False )
		
		tagNums = GetTagNums()
		
		highPrecisionTimes = Model.highPrecisionTimes()
		with Model.LockRace() as race:
		
			self.showPhotos.Enable( bool(race and num and race.enableUSBCamera) )
		
			if race is None or num is None:
				return
				
			try:
				externalInfo = race.excelLink.read()
			except AttributeError:
				externalInfo = {}
			
			info = externalInfo.get(int(num), {})
			riderName = u', '.join( n for n in [info.get('LastName', u''), info.get('FirstName', u'')] if n )
			try:
				riderName += u'      {}  {}'.format( _('Age'), info['Age'] )
			except KeyError:
				pass
				
			self.riderName.SetLabel( riderName )
			self.riderTeam.SetLabel( u'{}'.format(info.get('Team', '')) )

			tags = []
			for tagName in TagFields:
				try:
					tags.append( u'{}'.format(info[tagName]).lstrip('0').upper() )
				except (KeyError, ValueError):
					pass
			if tags:
				self.tags.SetLabel( u', '.join(tags) )
			
			waveCategory = race.getCategory( num )
			category = None
			iCategory = None
			categories = race.getCategories( startWaveOnly = False, excludeCustom = True, excludeCombined = True  )
			for i, c in enumerate(categories):
				if race.inCategory(num, c) and c.catType != Model.Category.CatCustom:
					iCategory = i
					category = c
					if c.catType == Model.Category.CatComponent:
						break
			
			if iCategory is not None:
				self.category.AppendItems( [c.fullname for c in categories] )
				self.category.SetSelection( iCategory )
			else:
				self.category.AppendItems( [c.fullname for c in categories] + [' '] )
				self.category.SetSelection( len(categories) )
				
			catName = category.fullname if category else ''
			#--------------------------------------------------------------------------------------
			if num not in race.riders:
				return
				
			rider = race.getRider( num )
				
			if waveCategory and getattr(waveCategory, 'distance', None) and waveCategory.distanceIsByLap:
				distanceByLap = getattr(waveCategory, 'distance')
			else:
				distanceByLap = None
			
			# Default set the relegated position.
			self.relegatedPosition.SetValue( rider.relegatedPosition )
			self.relegatedPosition.Enable( False )
			
			# Trigger adding the rider to the race if it isn't in already.
			self.statusOption.SetSelection( rider.status )
			if rider.status == Model.Rider.Finisher:
				self.relegatedPosition.Enable( True )
				results = GetResults( None )
				self.setAtRaceTime( 0.0, False )
				for rr in results:
					if rr.num == num:
						self.setAtRaceTime( rr.lastTime, False )
						break
			elif rider.status == Model.Rider.DNS:
				rider.tStatus = 0.0
				self.setAtRaceTime( 0.0, False )
			else:
				if rider.tStatus is None:
					rider.tStatus = 0.0
				self.setAtRaceTime( rider.tStatus, True )
				
			self.autocorrectLaps.SetValue( rider.autocorrectLaps )
			self.alwaysFilterMinPossibleLapTime.SetValue( rider.alwaysFilterMinPossibleLapTime )
			
			isTimeTrial = race.isTimeTrial
			if isTimeTrial:
				st, ft, laps = getStFtLaps( rider )
				self.startTime.SetLabel( Utils.formatTime(st, True) if st is not None else '')
				self.finishTime.SetLabel( Utils.formatTime(ft, True) if ft is not None else '')
				self.rideTime.SetLabel( Utils.formatTime(ft-st, True) if ft is not None and st is not None else '')
				self.penaltyTime.SetLabel( Utils.formatTime(getattr(rider, 'ttPenalty', 0.0)) )
				self.note.SetLabel( getattr(rider, 'ttNote', '') )
				for w in [	'startTimeName',	'startTime',
							'finishTimeName',	'finishTime',
							'rideTimeName',		'rideTime',
							'penaltyTimeName',	'penaltyTime',
							'noteName',			'note',
							'adjustTime']:
					getattr( self, w ).Show( True )
			else:
				earlyStartOffset = rider.getEarlyStartOffset()
				if earlyStartOffset is not None:
					self.earlyStartWaveName.Show( True )
					self.earlyStartWave.SetLabel( u'offset: {}  firstRead:{}'.format(
							Utils.formatTime(earlyStartOffset), 
							Utils.formatTime(rider.firstTime) if rider.firstTime is not None else u'',
						)
					)
					self.earlyStartWave.Show( True )
			
			categoryDetails = dict( (cd['name'], cd) for cd in GetCategoryDetails() )
			try:
				catInfo = categoryDetails[category.fullname]
				maxLap = catInfo['laps']
			except:
				maxLap = race.getMaxLap()
				
			maxLap = (maxLap or 0)		# Ensure that maxLap is not None
			
			raceStartTimeOfDay = Utils.StrToSeconds(race.startTime.strftime('%H:%M:%S.%f')) if race and race.startTime else 0.0

			startOffset = race.getStartOffset( num )
			entries = GetEntriesForNum(waveCategory, num) if rider.autocorrectLaps else race.getRider(num).interpolate()
			entries = [e for e in entries if e.t > startOffset]
			
			unfilteredTimes = [t for t in race.getRider(num).times if t > startOffset]
			entryTimes = set( e.t for e in entries )
			ignoredTimes = [t for t in unfilteredTimes if t not in entryTimes]
			dataFields = []
			for t in ignoredTimes:
				fields = {c:u'\u2715' for c in self.nameCol.iterkeys()}
				del fields['Lap']
				fields.update( {
					'Race': Utils.formatTime(t, highPrecisionTimes),
					'Clock': Utils.formatTime(t + raceStartTimeOfDay, highPrecisionTimes),
					'highlightColour': self.ignoreColour,
				} )
				dataFields.append( fields )
			
			# Figure out which laps this rider was lapped in.
			leaderTimes, leaderNums = race.getLeaderTimesNums(waveCategory)
			appearedInLap = [False] * (maxLap + 1)
			appearedInLap[0] = True
			for e in entries:
				i = bisect.bisect_left( leaderTimes, e.t, 0, len(leaderTimes)-1 )
				if e.t < leaderTimes[i]:
					i -= 1
				i = min( i, len(appearedInLap) - 1 )	# Handle if rider would have been lapped again on the last lap.
				appearedInLap[i] = True

			try:
				missingCount = sum( 1 for b in appearedInLap if not b ) if rider.status == Model.Rider.Finisher else 0
			except:
				missingCount = 0
			if missingCount:
				notInLapStr = u'{}: {}'.format(_('Lapped by Leader'), u', '.join( '{}'.format(i) for i, b in enumerate(appearedInLap) if not b ))
			else:
				notInLapStr = ''
			self.notInLap.SetLabel( notInLapStr )
			
			# Populate the lap times.
			try:
				raceTime = min(waveCategory.getStartOffsetSecs() if waveCategory else 0.0, entries[0].t)
			except IndexError:
				raceTime = 0.0
			ganttData = [raceTime]
			ganttInterp = [False]
			data = [ [] for c in xrange(len(self.colnames)) ]
			graphData = []
			numTimeInfo = race.numTimeInfo
			tSum = 0.0
			for r, e in enumerate(entries):
				tLap = max( e.t - raceTime, 0.0 )
				tSum += tLap
				
				# 'Lap', 'Lap Time', 'Race', 'Clock', 'Edit', 'By', 'On', 'Note', 'Lap Speed', 'Race Speed'
				fields = {
					'Lap': u'{}'.format(r+1),
					'Lap Time': Utils.formatTime(tLap, highPrecisionTimes),
					'Race': Utils.formatTime(e.t, highPrecisionTimes),
					'Clock': Utils.formatTime(e.t + raceStartTimeOfDay, highPrecisionTimes),
				}
				
				graphData.append( tLap )
				ganttData.append( e.t )
				ganttInterp.append( e.interp )
				
				if e.interp:
					fields['Edit'] = _('Auto')
					fields['By'] = u'CrossMgr'
					fields['highlightColour'] = self.yellowColour
				else:
					info = numTimeInfo.getInfo( e.num, e.t )
					if info:
						fields['Edit'] = Model.NumTimeInfo.ReasonName[info[0]]
						fields['By'] = info[1]
						fields['On'] =  info[2].ctime()
						fields['highlightColour'] = self.orangeColour
						
				fields['Note'] = getattr(race, 'lapNote', {}).get( (e.num, e.lap), u'' )
				if distanceByLap:
					fields['Lap Speed'] = u'{:.2f}'.format(1000.0 if tLap <= 0.0 else (waveCategory.getLapDistance(r+1) / (tLap / (60.0*60.0))))
					fields['Race Speed'] = u'{:.2f}'.format(1000.0 if tSum <= 0.0 else (waveCategory.getDistanceAtLap(r+1) / (tSum / (60.0*60.0))))
				
				dataFields.append( fields )
				
				raceTime = e.t

			# Merge the ignored times with the actual times.
			dataFields.sort( key=lambda x: (Utils.StrToSeconds(x.get('Race', '0')), int(x.get('Lap', '999999'))) )
			backgroundColour = {}
			for r, fields in enumerate(dataFields):
				for name, i in self.nameCol.iteritems():
					data[i].append( fields.get(name, u'') )
				if fields.get('highlightColour',None):
					highlightColour = fields.get('highlightColour',None)
					for i in xrange(len(self.colnames)):
						backgroundColour[(r,i)] = highlightColour
			
			self.grid.Set( data=data, backgroundColour=backgroundColour, colnames=self.colnames )
			self.grid.AutoSizeColumns( True )
			self.grid.Reset()
			
			self.ganttChart.SetData( [ganttData], [num], Gantt.GetNowTime(), [ganttInterp], numTimeInfo = numTimeInfo )
			self.lineGraph.SetData( [graphData], [[e.interp for e in entries]] )
		
		if self.firstCall:
			self.firstCall = False
			self.splitter.SetSashPosition( 300 )
		self.hs.RecalcSizes()
		self.hs.Layout()
		self.grid.FitInside()
		
		if visibleRow is not None and self.grid.GetNumberRows() > 0:
			self.grid.MakeCellVisible( min(visibleRow, self.grid.GetNumberRows()-1), 0 )
	
	def commitChange( self ):
		num = self.num.GetValue()
		status = self.statusOption.GetSelection()
		relegatedPosition = self.relegatedPosition.GetValue()
		
		undo.pushState();
		with Model.LockRace() as race:
			# Allow new numbers to be added if status is DNS, DNF or DQ.
			if race is None or (num not in race.riders and status not in [Model.Rider.DNS, Model.Rider.DNF, Model.Rider.DQ]):
				return
				
			rider = race.getRider(num)
			oldValues = (rider.status, rider.tStatus, rider.relegatedPosition)

			tStatus = None
			if status not in [Model.Rider.Finisher, Model.Rider.DNS, Model.Rider.DQ]:
				tStatus = Utils.StrToSeconds( self.atRaceTime.GetValue() )
			
			rider.setStatus( status, tStatus )
			rider.relegatedPosition = relegatedPosition

			newValues = (rider.status, rider.tStatus, rider.relegatedPosition)
			if oldValues != newValues:
				race.setChanged()
				wx.CallAfter( Utils.refresh )
		
		if Utils.isMainWin():
			Utils.getMainWin().setNumSelect( num )
		wx.CallAfter( Utils.refreshForecastHistory )
			
	def commit( self ):
		self.commitChange()
		
class RiderDetailDialog( wx.Dialog ):
	def __init__( self, parent, num = None, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, _("RiderDetail"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL|wx.RESIZE_BORDER )
						
		vs = wx.BoxSizer( wx.VERTICAL )
		
		self.riderDetail = RiderDetail( self )
		self.riderDetail.SetMinSize( (700, 500) )
		
		vs.Add( self.riderDetail, 1, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		self.commitBtn = wx.Button( self, id=wx.ID_SAVE, label=_('Save (Ctrl-S)') )
		self.commitBtn.Bind( wx.EVT_BUTTON, self.onSave )
		
		self.closeBtn = wx.Button( self, id=wx.ID_CLOSE, label = _('&Close (Ctrl-Q)') )
		self.Bind( wx.EVT_BUTTON, self.onClose, self.closeBtn )
		self.Bind( wx.EVT_CLOSE, self.onClose )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.AddStretchSpacer()
		hs.Add( self.commitBtn, flag=wx.ALIGN_RIGHT )
		hs.Add( self.closeBtn, flag=wx.LEFT|wx.ALIGN_RIGHT, border=32 )
		vs.Add( hs, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.SetSizerAndFit(vs)
		vs.Fit( self )
		
		# Add Ctrl-Q to close the dialog.
		self.Bind(wx.EVT_MENU, self.onSave, id=wx.ID_SAVE)
		self.Bind(wx.EVT_MENU, self.onClose, id=wx.ID_CLOSE)
		self.Bind(wx.EVT_MENU, self.onUndo, id=wx.ID_UNDO)
		self.Bind(wx.EVT_MENU, self.onRedo, id=wx.ID_REDO)
		accel_tbl = wx.AcceleratorTable([
			(wx.ACCEL_CTRL,  ord('S'), wx.ID_SAVE),
			(wx.ACCEL_CTRL,  ord('Q'), wx.ID_CLOSE),
			(wx.ACCEL_CTRL,  ord('Z'), wx.ID_UNDO),
			(wx.ACCEL_CTRL,  ord('Y'), wx.ID_REDO),
			])
		self.SetAcceleratorTable(accel_tbl)
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )
		
		self.riderDetail.setRider( num )
		wx.CallAfter( self.riderDetail.refresh )

	def refresh( self ):
		self.riderDetail.refresh()
		
	def commit( self ):
		self.riderDetail.commit()
		
	def setRider( self, num ):
		self.riderDetail.setRider( num )
	
	def onUndo( self, event ):
		undo.doUndo()
		self.refresh()
		
	def onRedo( self, event ):
		undo.doRedo()
		self.refresh()
	
	def onSave( self, event ):
		self.commit()
	
	def onClose( self, event ):
		self.commit()
		self.EndModal( wx.ID_OK )

dlgRiderDetail = None
@logCall
def ShowRiderDetailDialog( parent, num = None ):
	global dlgRiderDetail
	mainWin = Utils.getMainWin()
	if not dlgRiderDetail:
		dlgRiderDetail = RiderDetailDialog( mainWin or parent, num )
	if mainWin:
		mainWin.riderDetailDialog = dlgRiderDetail
	dlgRiderDetail.setRider( num )
	dlgRiderDetail.ShowModal()
	if mainWin:
		mainWin.riderDetailDialog = None
	wx.CallAfter( Utils.refresh )
		
if __name__ == '__main__':
	race = Model.newRace()
	race._populate()
	race.isTimeTrial = True
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMgr", size=(600,400))
	riderDetail = RiderDetail(mainWin)
	riderDetail.refresh()
	lineData = [random.normalvariate(100,15) for x in xrange(12)]
	ganttData = [0, lineData[0] * 3]
	ganttInterp = [False, False]
	for i, d in enumerate(lineData):
		ganttData.append( ganttData[-1] + d )
		ganttInterp.append( i % 4 == 0 )
	riderDetail.ganttChart.SetData( [ganttData], [106], interp = [ganttInterp] )
	riderDetail.lineGraph.SetData( [lineData] )
	mainWin.Show()
	app.MainLoop()
