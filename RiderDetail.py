import wx
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
from JChipSetup import GetTagNums
from Undo import undo
import Gantt
from EditEntry import CorrectNumber, ShiftNumber, DeleteEntry
from HighPrecisionTimeEdit import HighPrecisionTimeEdit
from GetResults import GetResults, GetCategoryDetails
from PhotoFinish import HasPhotoFinish

def getStFtLaps( rider ):
	with Model.LockRace() as race:
		laps = race.getCategoryNumLaps( rider.num )
	laps = max( 0, min(laps, len(rider.times)-1) )
	st = getattr( rider, 'firstTime', None )
	try:
		ft = st + rider.times[laps]
	except (TypeError, AttributeError, IndexError):
		ft = None
	return st, ft, laps
	
class AdjustTimeDialog( wx.Dialog ):
	def __init__( self, parent, rider, riderName, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, _("Adjust Times"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
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
			
		fgs.Add( wx.StaticText( self, label=_("Start:")), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.startTime, flag=wx.ALIGN_LEFT  )
		
		fgs.Add( wx.StaticText( self, label=_("Finish:")), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.finishTime, flag=wx.ALIGN_LEFT )
		
		fgs.Add( wx.StaticText( self, label=_("Ride Time:")), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.rideTime, flag=wx.ALIGN_LEFT )
		
		fgs.Add( wx.StaticText( self, label=_("Penalty Time:")), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.penaltyTime, flag=wx.ALIGN_LEFT )
		
		fgs.Add( wx.StaticText( self, label=_("Note:")),  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
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
		self.SetFocus()

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
		st, ft = self.startTime.GetSeconds(), self.finishTime.GetSeconds()
		ft = ft if ft else None
		if st is not None and ft is not None and st >= ft:
			Utils.MessageOK( self, _('Start Time must be before Finish Time'), _('Time Error'), wx.ICON_ERROR )
			return
			
		if stOld == st and ftOld == ft:
			Utils.refresh()
			self.EndModal( wx.ID_OK )
			return
		
		undo.pushState()
		self.rider.firstTime = st
		self.rider.ttPenalty = self.penaltyTime.GetSeconds()
		self.rider.ttNote = self.note.GetValue().strip()
		if st and ft:
			rt = ft - st
			if not self.rider.times:
				self.rider.addTime( rt )
			elif len(self.rider.times) == 2:
				self.rider.times[1] = rt
			else:
				self.rider.times = [t for t in self.rider.times if t < rt]
				self.rider.times.append( rt )
		elif st:
			self.rider.firstTime = st
			
		Model.race.setChanged()
		Utils.refresh()
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

class RiderDetail( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		
		self.num = None
		self.iLap = None
		self.entry = None
		self.firstTime = True
		
		self.visibleRow = None
		
		self.yellowColour = wx.Colour( 255, 255, 0 )
		self.orangeColour = wx.Colour( 255, 165, 0 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		
		hs = wx.BoxSizer( wx.VERTICAL )
		
		gbs = wx.GridBagSizer(7, 4)
		row = 0
		self.numName = wx.StaticText( self, label = _('Number: ') )
		gbs.Add( self.numName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.num = intctrl.IntCtrl( self, min=0, max=9999, allow_none=True, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER )
		self.Bind( wx.EVT_TEXT_ENTER, self.onNumChange, self.num )
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
		
		self.editRiderBtn = wx.Button( self, label = _('Edit...') )
		self.Bind( wx.EVT_BUTTON, self.onEditRider, self.editRiderBtn )
		gbs.Add( self.editRiderBtn, pos=(row, 3), span=(1,1), flag=wx.EXPAND )
		
		self.riderName = wx.StaticText( self )
		gbs.Add( self.riderName, pos=(row, 4), span=(1,1) )
		
		row += 1
		
		self.nameName = wx.StaticText( self, label = _('Name: ') )
		gbs.Add( self.nameName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.riderName = wx.StaticText( self )
		self.riderName.SetDoubleBuffered( True )
		gbs.Add( self.riderName, pos=(row,1), span=(1,4), flag=wx.EXPAND )
		
		self.startTimeName = wx.StaticText( self, label = _('Start:') )
		gbs.Add( self.startTimeName, pos=(row,5), span=(1,1), flag=labelAlign )
		self.startTime = wx.StaticText( self, label = u'00:00:00' )
		gbs.Add( self.startTime, pos=(row,6), span=(1,1), flag=wx.EXPAND )
		
		row += 1
		
		self.teamName = wx.StaticText( self, label = _('Team: ') )
		gbs.Add( self.teamName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.riderTeam = wx.StaticText( self )
		self.riderTeam.SetDoubleBuffered( True )
		gbs.Add( self.riderTeam, pos=(row,1), span=(1,4), flag=wx.EXPAND )
		
		self.finishTimeName = wx.StaticText( self, label = _('Finish:') )
		gbs.Add( self.finishTimeName, pos=(row,5), span=(1,1), flag=labelAlign )
		
		self.finishTime = wx.StaticText( self, label = u'00:00:00' )
		gbs.Add( self.finishTime, pos=(row,6), span=(1,1), flag=wx.EXPAND )
		
		row += 1
		
		self.tagsName = wx.StaticText( self, label = _('Tag(s): ') )
		gbs.Add( self.tagsName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.tags = wx.StaticText( self )
		self.tags.SetDoubleBuffered( True )
		gbs.Add( self.tags, pos=(row,1), span=(1,4), flag=wx.EXPAND )

		self.rideTimeName = wx.StaticText( self, label = _('Ride Time:') )
		gbs.Add( self.rideTimeName, pos=(row,5), span=(1,1), flag=labelAlign )
		
		self.rideTime = wx.StaticText( self, label = u'00:00:00' )
		gbs.Add( self.rideTime, pos=(row,6), span=(1,1), flag=wx.EXPAND )
		
		row += 1
		
		self.categoryName = wx.StaticText( self, label = _('Category: ') )
		gbs.Add( self.categoryName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.category = wx.Choice( self )
		self.Bind( wx.EVT_CHOICE, self.onCategoryChoice, self.category )
		gbs.Add( self.category, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		
		self.penaltyTimeName = wx.StaticText( self, label = _('Penalty Time:') )
		gbs.Add( self.penaltyTimeName, pos=(row,5), span=(1,1), flag=labelAlign )
		self.penaltyTime = wx.StaticText( self, label = u'00:00:00' )
		gbs.Add( self.penaltyTime, pos=(row,6), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL )
		
		row += 1
		
		self.statusName = wx.StaticText( self, label = _('Status: ') )
		gbs.Add( self.statusName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.statusOption = wx.Choice( self, choices=Model.Rider.statusNames )
		gbs.Add( self.statusOption, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		self.Bind(wx.EVT_CHOICE, self.onStatusChanged, self.statusOption)
		
		self.atRaceTimeName = wx.StaticText( self, label= _('at race time: ') )
		gbs.Add( self.atRaceTimeName, pos=(row,2), span=(1,1), flag=labelAlign )
		self.atRaceTime = HighPrecisionTimeEdit( self, size=(128,-1) )
		self.atRaceTime.SetSeconds( 0 )
		self.atRaceTime.SetEditable( False )
		self.atRaceTime.Enable( False )
		gbs.Add( self.atRaceTime, pos=(row,3), span=(1,1), flag=wx.EXPAND )
		
		self.noteName = wx.StaticText( self, label =  _('Note:') )
		gbs.Add( self.noteName, pos=(row,5), span=(1,1), flag=labelAlign )
		self.note = wx.StaticText( self )
		gbs.Add( self.note, pos=(row,6), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL )
		row += 1
		
		self.relegatedName = wx.StaticText( self, label = _('Relegated to:') )
		gbs.Add( self.relegatedName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.relegatedPosition = intctrl.IntCtrl( self, min=2, max=9999, allow_none=True, value=None, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER )
		gbs.Add( self.relegatedPosition, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		row += 1
		
		self.autocorrectLaps = wx.CheckBox( self, label = _('Autocorrect Lap Data') )
		gbs.Add( self.autocorrectLaps, pos = (row, 0), span=(1, 2), flag = wx.ALIGN_CENTRE|wx.EXPAND )
		self.Bind( wx.EVT_CHECKBOX, self.onAutocorrectLaps, self.autocorrectLaps )
		
		self.showPhotos = wx.Button( self, label = _('Show Photos...') )
		gbs.Add( self.showPhotos, pos = (row, 3), span=(1, 1), flag = wx.ALIGN_CENTRE|wx.EXPAND )
		self.Bind( wx.EVT_BUTTON, self.onShowPhotos, self.showPhotos )
		self.adjustTime = wx.Button( self, label = _('Adjust...') )
		self.Bind( wx.EVT_BUTTON, self.onAdjustTime, self.adjustTime )
		gbs.Add( self.adjustTime, pos=(row,5), span=(1,2), flag=wx.EXPAND )
		row += 1
		
		if not HasPhotoFinish():
			self.showPhotos.Disable()

		self.notInLap = wx.StaticText( self, label = u'              ' )
		gbs.Add( self.notInLap, pos=(row,0), span=(1,4) )
		row += 1
	
		hs.Add( gbs, proportion = 0 )
		
		splitter = wx.SplitterWindow( self )
		self.splitter = splitter
		
		self.grid = ColGrid.ColGrid(	splitter,
										colnames = [_('Lap'), _('Lap Time'), _('Race Time'),
													_('Edit'), _('By'), _('On'), _('Note'),
													_('Lap Speed'), _('Race Speed')],
										style = wx.BORDER_SUNKEN )
		self.grid.SetRowLabelSize( 0 )
		self.grid.SetRightAlign( True )
		self.grid.SetLeftAlignCols( [4, 5, 6] )
		#self.grid.SetDoubleBuffered( True )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()
		self.grid.SetSelectionMode( wx.grid.Grid.wxGridSelectRows )
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
		
		hs.Add( splitter, proportion = 1, flag = wx.EXPAND|wx.TOP, border = 4 )
		splitter.SizeWindows()
		
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
			if not getattr(race, 'isTimeTrial', False) or num not in race:
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
		return row + 1
		
	def doRightClick( self, event ):
		self.eventRow = event.GetRow()
		self.visibleRow = self.eventRow
		
		allCases = 0
		interpCase = 1
		nonInterpCase = 2
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				(wx.NewId(), _('Add Missing Last Lap'),	_('Add missing last lap'),	self.OnPopupAddMissingLastLap, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Pull After Lap...'),	_('Pull after lap'),	self.OnPopupPull, allCases),
				(wx.NewId(), _('DNF After Lap...'),		_('DNF after lap'),	self.OnPopupDNF, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Correct...'),			_('Change number or lap time...'),	self.OnPopupCorrect, interpCase),
				(wx.NewId(), _('Shift...'),				_('Move lap time earlier/later...'),	self.OnPopupShift, interpCase),
				(wx.NewId(), _('Delete...'),			_('Delete lap time(s)...'),	self.OnPopupDelete, nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), _('Note...'),				_('Add/Edit lap note'),	self.OnPopupNote, nonInterpCase),
			]
			for p in self.popupInfo:
				if p[0]:
					self.Bind( wx.EVT_MENU, p[3], id=p[0] )
		
		if self.num.GetValue() is None:
			return
		num = int(self.num.GetValue())
			
		self.iLap = self.getLapClicked( event )
		if self.iLap is None:
			return
		
		with Model.LockRace() as race:
			if not race or num not in race:
				return
			entries = race.getRider(num).interpolate()
		
		try:
			self.entry = entries[self.iLap]
			caseCode = 1 if self.entry.interp else 2
		except (TypeError, IndexError, KeyError):
			caseCode = 0
		
		menu = wx.Menu()
		for id, name, text, callback, cCase in self.popupInfo:
			if not id:
				if not Utils.hasTrailingSeparator(menu):
					menu.AppendSeparator()
				continue
			if caseCode >= cCase:
				menu.Append( id, name, text )
		
		self.PopupMenu( menu )
		menu.Destroy()

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
			rider = Model.race[num]
			times = [rider.times[r] for r in rows]
			timeStr = []
			timesPerRow = 4
			for i in xrange(0, len(times), timesPerRow):
				timeStr.append(
					',  '.join( _('Lap {}: {}').format(rows[j]+1, Utils.formatTime(times[i]))
							for j in xrange(i, min(len(times), i+timesPerRow) ) ) )
			timeStr = ',\n'.join( timeStr )
			message = _('Delete entries of Rider {}:\n\n{}\n\nConfirm Delete?').format(num, timeStr)
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
		if not race or num not in race:
			return
			
		rider = race.riders[num]
			
		times = [t for t in rider.times]
		if len(times) < 2:
			return
			
		if rider.status != rider.Finisher:
			Utils.MessageOK( self, _('Cannot add Last Lap unless Rider is Finisher'), _('Cannot add Last Lap') )
			return
				
		undo.pushState()
		if rider.autocorrectLaps:
			if Utils.MessageOKCancel( self, _('Turn off Autocorrect first?'), _('Turn off Autocorrect') ):
				rider.autocorrectLaps = False
				
		waveCategory = race.getCategory( num )
		if waveCategory:
			times[0] = waveCategory.getStartOffsetSecs()
		tNewLast = times[-1] + times[-1] - times[-2]
				
		race.numTimeInfo.add( num, tNewLast )
		race.addTime( num, tNewLast )
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
		dlg = wx.TextEntryDialog( self, _("Note for Rider {} on Lap {}:").format(num, lap), _("Lap Note"),
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
			
		if Utils.MessageOKCancel( self, _("Confirm Delete rider {} and all associated entries.").format(num), _("Delete Rider") ):
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
		
		dlg = wx.TextEntryDialog( self, _("Rider's new number:"), _('New Number'), '{}'.format(self.num.GetValue()) )
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
			inRace = (newNum in race)
		if inRace:
			Utils.MessageOK( self, _("Cannot Change rider to {}.\nThere is a rider with this number already.").format(newNum),
									_('Cannot Change Rider Number'), iconMask = wx.ICON_ERROR )
			return
			
		if Utils.MessageOKCancel( self, _("Confirm Change rider's number to {}.").format(newNum), _("Change Rider Number") ):
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
		
		dlg = wx.TextEntryDialog( self, _("Number to swap with:"), _('Swap Numbers'), '{}'.format(self.num.GetValue()) )
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
			inRace = (newNum in race)
		if not inRace:
			Utils.MessageOK( self, _("Cannot swap with rider {}.\nThis rider is not in race.").format(newNum),
									_('Cannot Swap Rider Numbers'), iconMask = wx.ICON_ERROR )
			return
			
		if Utils.MessageOKCancel( self, _("Confirm Swap numbers {} and {}.").format(num, newNum), _("Swap Rider Number") ):
			undo.pushState()
			with Model.LockRace() as race:
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
		
		dlg = wx.TextEntryDialog( self, _("All time entries for {} will be copied to the new bib number.\n\nNew Bib Number:").format(num),
								_('Copy Rider Times'), '{}'.format(self.num.GetValue()) )
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
			inRace = (newNum in race)
		if inRace:
			if num != newNum:
				Utils.MessageOK( self, _("New Bib {} already exists.\nIf you really want to copy times to this number, delete it first.").format(newNum),
								_('New Bib Number Already Exists'), iconMask = wx.ICON_ERROR )
			else:
				Utils.MessageOK( self, _("Cannot copy to the same number ({}).").format(newNum),
								
								_('Cannot Copy to Same Number'), iconMask = wx.ICON_ERROR )
			return
			
		if Utils.MessageOKCancel( self,
				_("Entries from {} will be copied to new Bib {}.\n\nAll entries for {} will be slightly earlier then entries for {}.\nContinue?").format(
					num, newNum, newNum, num),
				_("Confirm Copy Rider Times") ):
			undo.pushState()
			with Model.LockRace() as race:
				race.copyRiderTimes( num, newNum )
				rNew = race.getRider( newNum )
				numTimeInfo = race.numTimeInfo
				for t in rNew.times:
					numTimeInfo.add( newNum, t )
			self.setRider( newNum )
			self.onNumChange()
			wx.CallAfter( Utils.refreshForecastHistory )
			wx.CallAfter( Utils.refresh )
	
	def onNumChange( self, event = None ):
		self.refresh()
		if Utils.isMainWin():
			Utils.getMainWin().setNumSelect( self.num.GetValue() )
	
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
			return
		undo.pushState()
		with Model.LockRace() as race:
			rider = race[num]
			rider.autocorrectLaps = self.autocorrectLaps.GetValue()
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
		dlg = wx.NumberEntryDialog( self, message = "", caption = _("Add Missing Splits"), prompt = _("Missing Splits to Add:"),
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
				riderName = u'{}, {} {}'.format(riderInfo['LastName'], riderInfo['FirstName'], num)
			except KeyError:
				try:
					riderName = u'{} {}'.format(riderInfo['LastName'], num)
				except KeyError:
					try:
						riderName = u'{} {}'.format(riderInfo['FirstName'], num)
					except KeyError:
						riderName = u'{}'.format(num)
						
			infoStart = race.numTimeInfo.getInfoStr( num, tLapStart )
			if infoStart:
				infoStart = _('\nLap Start ') + infoStart
			infoEnd = race.numTimeInfo.getInfoStr( num, tLapEnd )
			if infoEnd:
				infoEnd = _('\nLap End ') + infoEnd
		
			info = (_('Rider: {}  Lap: {}\nLap Start:  {} Lap End: {}\nLap Time: {}\n{}{}').format(
					riderName, lap,
					Utils.formatTime(tLapStart),
					Utils.formatTime(tLapEnd),
					Utils.formatTime(tLapEnd - tLapStart),
					infoStart, infoEnd )).strip()
					
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
				(wx.NewId(), _('Add Missing Last Lap'),		_('Add missing last lap'),				self.OnPopupAddMissingLastLap, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Pull after Lap End...'),	_('Pull after lap...'),					self.OnGanttPopupPull, allCases),
				(wx.NewId(), _('DNF after Lap End...'),		_('DNF after lap...'),					self.OnGanttPopupDNF, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Correct lap End Time...'),	_('Change lap end time...'),			lambda event, s = self: CorrectNumber(s, s.entry), interpCase),
				(wx.NewId(), _('Shift Lap End Time...'),	_('Move lap end time earlier/later...'),lambda event, s = self: ShiftNumber(s, s.entry), interpCase),
				(wx.NewId(), _('Delete Lap End Time...'),	_('Delete lap end time...'),			lambda event, s = self: DeleteEntry(s, s.entry), nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), _('Note...'),					_('Add/Edit lap Note'),					self.OnGanttPopupLapNote, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Show Lap Details...'), 		_('Show Lap Details'),					self.OnGanttPopupLapDetail, allCases),
			]
			self.splitMenuInfo = [
					(wx.NewId(),
					'%d Split%s' % (split-1, 's' if split > 2 else ''),
					lambda evt, s = self, splits = split: s.doSplitLap(splits)) for split in xrange(2,8) ] + [
					(wx.NewId(),
					_('Custom...'),
					lambda evt, s = self: s.doCustomSplitLap())]
			for id, name, text, callback, cCase in self.ganttMenuInfo:
				if id:
					self.Bind( wx.EVT_MENU, callback, id=id )
			for id, name, callback in self.splitMenuInfo:
				self.Bind( wx.EVT_MENU, callback, id=id )
		
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
			menu.PrependMenu( wx.NewId(), _('Add Missing Split'), submenu )
			
		Utils.deleteTrailingSeparators( menu )
		self.PopupMenu( menu )
		menu.Destroy()
	
	def OnGanttPopupPull( self, event ):
		if not self.entry:
			return
		if not Utils.MessageOKCancel( self,
			_('Pull Rider {} at {} after lap {}?').format(self.entry.num, Utils.formatTime(self.entry.t+1, True), self.entry.lap),
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
			_('DNF Rider {} at {} after lap {}?').format(self.entry.num, Utils.formatTime(self.entry.t+1, True), self.entry.lap),
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
		dlg = wx.TextEntryDialog( self, _("Note for Rider {} on Lap {}:").format(self.entry.num, self.entry.lap), _("Lap Note"),
					Model.race.lapNote.get( (self.entry.num, self.entry.lap), '' ) )
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
	
	def refresh( self ):
		self.num.SelectAll()
		wx.CallAfter( self.num.SetFocus )
		
		visibleRow = self.visibleRow
		self.visibleRow = None

		data = [ [] for c in xrange(self.grid.GetNumberCols()) ]
		self.grid.Set( data = data )
		self.grid.Reset()
		self.category.Clear()
		self.autocorrectLaps.SetValue( True )
		num = self.num.GetValue()
		
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
					'adjustTime']:
			getattr( self, w ).Show( False )
		
		tagNums = GetTagNums()
		
		highPrecisionTimes = Model.highPrecisionTimes()
		with Model.LockRace() as race:
			if race is None or num is None:
				return
				
			try:
				externalInfo = race.excelLink.read()
			except AttributeError:
				externalInfo = {}
			
			try:
				info = externalInfo[int(num)]
				name = info.get( 'LastName', '' )
				firstName = info.get( 'FirstName', '' )
				if firstName:
					if name:
						name = '%s, %s' % (name, firstName)
					else:
						name = firstName
				self.riderName.SetLabel( name )
				self.riderTeam.SetLabel( u'{}'.format(info.get('Team', '')) )
			except KeyError:
				pass

			try:
				info = externalInfo[int(num)]
				tags = []
				for tagName in ['Tag', 'Tag2']:
					try:
						tags.append( u'{}'.format(info[tagName]).lstrip('0').upper() )
					except (KeyError, ValueError):
						pass
				if tags:
					self.tags.SetLabel( ', '.join(tags) )
			except KeyError:
				pass
			
			waveCategory = race.getCategory( num )
			category = None
			iCategory = None
			categories = race.getCategories( startWaveOnly = False, excludeCustom = True, excludeCombined = True  )
			for i, c in enumerate(categories):
				if race.inCategory( num, c ) and c.catType != Model.Category.CatCustom:
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
			if num not in race:
				return
				
			if waveCategory and getattr(waveCategory, 'distance', None) and waveCategory.distanceIsByLap:
				distanceByLap = getattr(waveCategory, 'distance')
			else:
				distanceByLap = None
			
			rider = race.getRider( num )
			
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
				
			self.autocorrectLaps.SetValue( getattr(rider, 'autocorrectLaps', True) )
			
			isTimeTrial = getattr(race, 'isTimeTrial', False)
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
			
			categoryDetails = dict( (cd['name'], cd) for cd in GetCategoryDetails() )
			try:
				catInfo = categoryDetails[category.fullname]
				maxLap = catInfo['laps']
			except:
				maxLap = race.getMaxLap()
			
			# Figure out which laps this rider was lapped in.
			if getattr(rider, 'autocorrectLaps', True):
				entries = race.interpolateLap( maxLap, False )
			else:
				entries = race.getRider(num).interpolate()
			
			entries = [e for e in entries if e.num == num and e.t > 0]

			leaderTimes, leaderNums = race.getLeaderTimesNums()
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
				notInLapStr = _('Lapped by Race Leader in {}').format(', '.join( '{}'.format(i) for i, b in enumerate(appearedInLap) if not b ))
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
			data = [ [] for c in xrange(self.grid.GetNumberCols()) ]
			graphData = []
			backgroundColour = {}
			numTimeInfo = race.numTimeInfo
			tSum = 0.0
			for r, e in enumerate(entries):
				tLap = max( e.t - raceTime, 0.0 )
				tSum += tLap
				
				row = [''] * self.grid.GetNumberCols()
				
				row[0:3] = ( '{}'.format(r+1), Utils.formatTime(tLap, highPrecisionTimes), Utils.formatTime(e.t, highPrecisionTimes) )
				
				graphData.append( tLap )
				ganttData.append( e.t )
				ganttInterp.append( e.interp )
				
				highlightColour = None
				if e.interp:
					row[3:5] = (_('Auto'), 'CrossMgr')
					highlightColour = self.yellowColour
				else:
					info = numTimeInfo.getInfo( e.num, e.t )
					if info:
						row[3:6] = ( Model.NumTimeInfo.ReasonName[info[0]], info[1], info[2].ctime() )
						highlightColour = self.orangeColour
						
				row[6] = getattr(race, 'lapNote', {}).get( (e.num, e.lap), '' )
				if distanceByLap:
					row[7:9] = ('%.2f' % (1000.0 if tLap <= 0.0 else (waveCategory.getLapDistance(r+1) / (tLap / (60.0*60.0)))),
								'%.2f' % (1000.0 if tSum <= 0.0 else (waveCategory.getDistanceAtLap(r+1) / (tSum / (60.0*60.0)))) )
				
				for i, d in enumerate(row):
					data[i].append( d )
				if highlightColour:
					for i in xrange(self.grid.GetNumberCols()):
						backgroundColour[(r,i)] = highlightColour
				raceTime = e.t

			self.grid.Set( data = data, backgroundColour = backgroundColour )
			self.grid.AutoSizeColumns( True )
			self.grid.Reset()
			
			self.ganttChart.SetData( [ganttData], [num], Gantt.GetNowTime(), [ganttInterp], numTimeInfo = numTimeInfo )
			self.lineGraph.SetData( [graphData], [[e.interp for e in entries]] )
		
		if self.firstTime:
			self.firstTime = False
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
		
		wx.CallAfter( Utils.refreshForecastHistory )
		
		undo.pushState();
		with Model.LockRace() as race:
			# Allow new numbers to be added if status is DNS, DNF or DQ.
			if race is None or (num not in race and status not in [Model.Rider.DNS, Model.Rider.DNF, Model.Rider.DQ]):
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
	
	def commit( self ):
		self.commitChange()
		
class RiderDetailDialog( wx.Dialog ):
	def __init__( self, parent, num = None, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, _("RiderDetail"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		vs = wx.BoxSizer( wx.VERTICAL )
		
		self.riderDetail = RiderDetail( self )
		self.riderDetail.SetMinSize( (700, 500) )
		
		vs.Add( self.riderDetail, 1, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		self.closeBtn = wx.Button( self, label = _('&Close (Ctrl-Q)') )
		self.Bind( wx.EVT_BUTTON, self.onClose, self.closeBtn )
		self.Bind( wx.EVT_CLOSE, self.onClose )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.AddStretchSpacer()
		hs.Add( self.closeBtn, flag=wx.ALL|wx.ALIGN_RIGHT, border = 4 )
		vs.Add( hs, flag=wx.EXPAND )
		
		self.SetSizerAndFit(vs)
		vs.Fit( self )
		
		# Add Ctrl-Q to close the dialog.
		self.Bind(wx.EVT_MENU, self.onClose, id=wx.ID_CLOSE)
		self.Bind(wx.EVT_MENU, self.onUndo, id=wx.ID_UNDO)
		self.Bind(wx.EVT_MENU, self.onRedo, id=wx.ID_REDO)
		accel_tbl = wx.AcceleratorTable([
			(wx.ACCEL_CTRL,  ord('Q'), wx.ID_CLOSE),
			(wx.ACCEL_CTRL,  ord('Z'), wx.ID_UNDO),
			(wx.ACCEL_CTRL,  ord('Y'), wx.ID_REDO),
			])
		self.SetAcceleratorTable(accel_tbl)
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()
		
		self.riderDetail.setRider( num )
		wx.CallAfter( self.riderDetail.refresh )

	def refresh( self ):
		self.riderDetail.refresh()
	
	def onUndo( self, event ):
		undo.doUndo()
		self.refresh()
		
	def onRedo( self, event ):
		undo.doRedo()
		self.refresh()
	
	def onClose( self, event ):
		self.riderDetail.commit()
		self.EndModal( wx.ID_OK )

@logCall
def ShowRiderDetailDialog( parent, num = None ):
	dlg = RiderDetailDialog( parent, num )
	if Utils.getMainWin():
		Utils.getMainWin().riderDetailDialog = dlg
	dlg.ShowModal()
	dlg.Destroy()
	if Utils.getMainWin():
		Utils.getMainWin().riderDetailDialog = None
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
