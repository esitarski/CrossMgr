import wx
import wx.lib.intctrl as intctrl
import wx.lib.masked as masked
import Model
import Utils
from Utils				import logCall
import ColGrid
import EditEntry
from LineGraph import LineGraph
from GanttChartPanel import GanttChartPanel
from JChipSetup import GetTagNums
from Undo import undo
import Gantt
from EditEntry import CorrectNumber, ShiftNumber, DeleteEntry
from HighPrecisionTimeEdit import HighPrecisionTimeEdit
from GetResults import GetResults
import random
import bisect
import sys
import re

def getStFtLaps( rider ):
	with Model.LockRace() as race:
		laps = race.getCategoryNumLaps( rider.num )
	laps = min( laps, len(rider.times)-1 )
	st = getattr( rider, 'firstTime', None )
	if laps:
		ft = st + rider.times[laps]
	else:
		ft = None
	return st, ft, laps
	
class AdjustTimeDialog( wx.Dialog ):
	def __init__( self, parent, rider, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Adjust Times",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		self.rider = rider
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		
		st, ft, laps = getStFtLaps( self.rider )
			
		self.startTime = HighPrecisionTimeEdit( self, wx.ID_ANY, allow_none = not bool(st), seconds = st )
		self.startTime.Bind( wx.EVT_TEXT, self.updateRideTime )
		self.finishTime = HighPrecisionTimeEdit( self, wx.ID_ANY, allow_none = not bool(ft), seconds = ft )
		self.finishTime.Bind( wx.EVT_TEXT, self.updateRideTime )
		self.rideTime = wx.StaticText( self, wx.ID_ANY, '' )
		self.updateRideTime( None )
				
		self.okBtn = wx.Button( self, wx.ID_ANY, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_ANY, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		row = 0
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'Rider %d' % rider.num ),
			pos=(row,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		row += 1
		bs.Add( wx.StaticText( self, -1, "Start:"),  pos=(row,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.startTime, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.BOTTOM|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, -1, "Finish:"),  pos=(row,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.finishTime, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.BOTTOM|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, -1, "Ride Time:"),  pos=(row,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.rideTime, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.BOTTOM|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( self.okBtn, pos=(row, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(row, 1), span=(1,1), border = border, flag=wx.ALL )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()
		

	def updateRideTime( self, event = None ):
		st = self.startTime.GetSeconds()
		ft = self.finishTime.GetSeconds()
		try:
			self.rideTime.SetLabel( Utils.formatTime(ft - st, True) )
		except:
			self.rideTime.SetLabel( '' )

	def onOK( self, event ):
		stOld, ftOld, laps = getStFtLaps(self.rider)
		st, ft = self.startTime.GetSeconds(), self.finishTime.GetSeconds()
		if st is not None and ft is not None and st >= ft:
			Utils.MessageOK( self, 'Start Time must be before Finish Time', 'Time Error', wx.ICON_ERROR )
			return
		if stOld == st and ftOld == ft:
			self.EndModel( wx.IDOK )
			return
		
		undo.pushState()
		self.rider.firstTime = st
		if st and ft:
			rt = ft - st
			if not self.rider.times:
				self.rider.addTime( rt )
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
		
		self.yellowColour = wx.Colour( 255, 255, 0 )
		self.orangeColour = wx.Colour( 255, 165, 0 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		
		hs = wx.BoxSizer( wx.VERTICAL )
		
		gbs = wx.GridBagSizer(7, 4)
		row = 0
		self.numName = wx.StaticText( self, wx.ID_ANY, 'Number: ' )
		gbs.Add( self.numName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.num = intctrl.IntCtrl( self, wx.ID_ANY, min=0, max=9999, allow_none=True, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER )
		self.Bind( wx.EVT_TEXT_ENTER, self.onNumChange, self.num )
		gbs.Add( self.num, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		
		self.menu = wx.Menu()
		self.deleteMenuId = wx.NewId()
		self.menu.Append( self.deleteMenuId, '&Delete Rider from Race...', 'Delete this rider from the race' )
		self.Bind( wx.EVT_MENU, self.onDeleteRider, id = self.deleteMenuId )
		self.changeNumberMenuId = wx.NewId()
		self.menu.Append( self.changeNumberMenuId, "&Change Rider's Number...", "Change this rider's number" )
		self.Bind( wx.EVT_MENU, self.onChangeNumber, id = self.changeNumberMenuId )
		self.swapNumberMenuId = wx.NewId()
		self.menu.Append( self.swapNumberMenuId, '&Swap Number with Other Rider...', "Swap this rider's number with another rider's number" )
		self.Bind( wx.EVT_MENU, self.onSwapNumber, id = self.swapNumberMenuId )
		self.copyRiderMenuId = wx.NewId()
		self.menu.Append( self.copyRiderMenuId, 'C&opy Rider Times to New Number...', "Copy these rider's times to another number" )
		self.Bind( wx.EVT_MENU, self.onCopyRider, id = self.copyRiderMenuId )
		
		self.editRiderBtn = wx.Button( self, wx.ID_ANY, 'Edit...' )
		self.Bind( wx.EVT_BUTTON, self.onEditRider, self.editRiderBtn )
		gbs.Add( self.editRiderBtn, pos=(row, 3), span=(1,1), flag=wx.EXPAND )
		
		self.riderName = wx.StaticText( self, wx.ID_ANY, '' )
		gbs.Add( self.riderName, pos=(row, 4), span=(1,1) )
		
		row += 1
		
		self.nameName = wx.StaticText( self, wx.ID_ANY, 'Name: ' )
		gbs.Add( self.nameName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.riderName = wx.StaticText( self, wx.ID_ANY, '' )
		self.riderName.SetDoubleBuffered( True )
		gbs.Add( self.riderName, pos=(row,1), span=(1,4), flag=wx.EXPAND )
		
		self.startTimeName = wx.StaticText( self, wx.ID_ANY, 'Start:' )
		gbs.Add( self.startTimeName, pos=(row,5), span=(1,1), flag=labelAlign )
		self.startTime = wx.StaticText( self, wx.ID_ANY, '00:00:00' )
		gbs.Add( self.startTime, pos=(row,6), span=(1,1), flag=wx.EXPAND )
		
		row += 1
		
		self.teamName = wx.StaticText( self, wx.ID_ANY, 'Team: ' )
		gbs.Add( self.teamName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.riderTeam = wx.StaticText( self, wx.ID_ANY, '' )
		self.riderTeam.SetDoubleBuffered( True )
		gbs.Add( self.riderTeam, pos=(row,1), span=(1,4), flag=wx.EXPAND )
		
		self.finishTimeName = wx.StaticText( self, wx.ID_ANY, 'Finish:' )
		gbs.Add( self.finishTimeName, pos=(row,5), span=(1,1), flag=labelAlign )
		
		self.finishTime = wx.StaticText( self, wx.ID_ANY, '00:00:00' )
		gbs.Add( self.finishTime, pos=(row,6), span=(1,1), flag=wx.EXPAND )
		
		row += 1
		
		self.tagsName = wx.StaticText( self, wx.ID_ANY, 'Tag(s): ' )
		gbs.Add( self.tagsName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.tags = wx.StaticText( self, wx.ID_ANY, '' )
		self.tags.SetDoubleBuffered( True )
		gbs.Add( self.tags, pos=(row,1), span=(1,4), flag=wx.EXPAND )

		self.rideTimeName = wx.StaticText( self, wx.ID_ANY, 'Ride Time:' )
		gbs.Add( self.rideTimeName, pos=(row,5), span=(1,1), flag=labelAlign )
		
		self.rideTime = wx.StaticText( self, wx.ID_ANY, '00:00:00' )
		gbs.Add( self.rideTime, pos=(row,6), span=(1,1), flag=wx.EXPAND )
		
		row += 1
		
		self.categoryName = wx.StaticText( self, wx.ID_ANY, 'Category: ' )
		gbs.Add( self.categoryName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.category = wx.Choice( self, wx.ID_ANY )
		self.Bind( wx.EVT_CHOICE, self.onCategoryChoice, self.category )
		gbs.Add( self.category, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		self.adjustTime = wx.Button( self, wx.ID_ANY, 'Adjust...' )
		self.Bind( wx.EVT_BUTTON, self.onAdjustTime, self.adjustTime )
		gbs.Add( self.adjustTime, pos=(row,5), span=(1,2), flag=wx.EXPAND )
		
		row += 1
		
		self.statusName = wx.StaticText( self, wx.ID_ANY, 'Status: ' )
		gbs.Add( self.statusName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.statusOption = wx.Choice( self, wx.ID_ANY, choices=Model.Rider.statusNames )
		gbs.Add( self.statusOption, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		self.Bind(wx.EVT_CHOICE, self.onStatusChanged, self.statusOption)
		
		self.atRaceTimeName = wx.StaticText( self, wx.ID_ANY, 'at race time: ' )
		gbs.Add( self.atRaceTimeName, pos=(row,2), span=(1,1), flag=labelAlign )
		self.atRaceTime = masked.TimeCtrl( self, wx.ID_ANY, fmt24hr=True, value=Utils.SecondsToStr(0) )
		self.atRaceTime.SetEditable( False )
		self.atRaceTime.Enable( False )
		gbs.Add( self.atRaceTime, pos=(row,3), span=(1,1), flag=wx.EXPAND )
		row += 1
		
		self.autocorrectLaps = wx.CheckBox( self, wx.ID_ANY, 'Autocorrect Lap Data' )
		gbs.Add( self.autocorrectLaps, pos = (row, 0), span=(1, 2), flag = wx.ALIGN_CENTRE|wx.EXPAND )
		self.Bind( wx.EVT_CHECKBOX, self.onAutocorrectLaps, self.autocorrectLaps )
		
		self.showPhotos = wx.Button( self, wx.ID_ANY, 'Show Photos...' )
		gbs.Add( self.showPhotos, pos = (row, 3), span=(1, 1), flag = wx.ALIGN_CENTRE|wx.EXPAND )
		self.Bind( wx.EVT_BUTTON, self.onShowPhotos, self.showPhotos )
		row += 1

		self.notInLap = wx.StaticText( self, wx.ID_ANY, '              ' )
		gbs.Add( self.notInLap, pos=(row,0), span=(1,4) )
		row += 1
	
		hs.Add( gbs, proportion = 0 )
		
		splitter = wx.SplitterWindow( self, wx.ID_ANY )
		self.splitter = splitter
		
		self.grid = ColGrid.ColGrid(	splitter,
										colnames = ['Lap', 'Lap Time', 'Race Time', 'Edit', 'By', 'On', 'Lap Speed', 'Race Speed'],
										style = wx.BORDER_SUNKEN )
		self.grid.SetRowLabelSize( 0 )
		self.grid.SetRightAlign( True )
		#self.grid.SetDoubleBuffered( True )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()
		self.grid.SetSelectionMode( wx.grid.Grid.wxGridSelectRows )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doRightClick )

		panel = wx.Panel( splitter, wx.ID_ANY, style = wx.BORDER_SUNKEN )
		
		self.lineGraph = LineGraph( panel, wx.ID_ANY, style = wx.NO_BORDER )
		self.ganttChart = GanttChartPanel( panel, wx.ID_ANY, style = wx.NO_BORDER )
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
		self.SetSizer( hs )
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
		dlg = AdjustTimeDialog( self, rider )
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
			for c in race.getCategories():
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
		
		allCases = 0
		interpCase = 1
		nonInterpCase = 2
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				(wx.NewId(), 'Pull After Lap...',	'Pull after Lap',	self.OnPopupPull, allCases),
				(wx.NewId(), 'DNF After Lap...',	'DNF after Lap',	self.OnPopupDNF, allCases),
				(None, None, None, None, None),
				(wx.NewId(), 'Correct...',			'Change number or lap time...',	self.OnPopupCorrect, interpCase),
				(wx.NewId(), 'Shift...',			'Move lap time earlier/later...',	self.OnPopupShift, interpCase),
				(wx.NewId(), 'Delete...',			'Delete lap time...',	self.OnPopupDelete, nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), 'Add Missing Last Lap','Add Missing Last Lap',	self.OnPopupAddMissingLastLap, allCases),

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
					',  '.join( 'Lap %d: %s' % (rows[j]+1, Utils.formatTime(times[i]))
							for j in xrange(i, min(len(times), i+timesPerRow) ) ) )
			timeStr = ',\n'.join( timeStr )
			message = 'Delete entries of Rider %d:\n\n%s\n\nConfirm Delete?' % (num, timeStr)
			if Utils.MessageOKCancel( self, message, 'Delete Times', wx.ICON_WARNING ):
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
			
		if not Model.race or num not in Model.race:
				return
			
		with Model.LockRace() as race:
			rider = race.riders[num]
			
		times = [t for t in rider.times]
		if len(times) < 2:
			return
			
		if rider.status != rider.Finisher:
			Utils.MessageOK( self, 'Cannot add Last Lap unless Rider is Finisher', 'Cannot add Last Lap' )
			return
				
		undo.pushState()
		if rider.autocorrectLaps:
			if Utils.MessageOKCancel( self, 'Turn off Autocorrect first?', 'Turn off Autocorrect' ):
				rider.autocorrectLaps = False
				
		category = race.getCategory( num )
		if category:
			times[0] = category.getStartOffsetSecs()
		tNewLast = times[-1] + times[-1] - times[-2]
				
		with Model.LockRace() as race:
			race.numTimeInfo.add( num, tNewLast )
			race.addTime( num, tNewLast )
			race.setChanged()
			
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
				return
			
		if Utils.MessageOKCancel( self, "Confirm Delete rider %d and all associated entries." % num,
									"Delete Rider" ):
			undo.pushState()
			with Model.LockRace() as race:
				race.deleteRider( num )
			self.setRider( None )
			self.refresh()
		
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
		
		dlg = wx.TextEntryDialog( self, "Rider's new number:", 'New Number', str(self.num.GetValue()) )
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
			Utils.MessageOK( self, "Cannot Change rider to %d.\nThere is a rider with this number already." % newNum, 'Cannot Change Rider Number', iconMask = wx.ICON_ERROR )
			return
			
		if Utils.MessageOKCancel( self, "Conform Change rider's number to %d." % newNum, "Change Rider Number" ):
			undo.pushState()
			with Model.LockRace() as race:
				race.renumberRider( num, newNum )
				race.numTimeInfo.renumberRider( num, newNum )
			self.setRider( newNum )
			self.refresh()
		
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
		
		dlg = wx.TextEntryDialog( self, "Number to swap with:", 'Swap Numbers', str(self.num.GetValue()) )
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
			Utils.MessageOK( self, "Cannot swap with rider %d.\nThis rider is not in race." % newNum, 'Cannot Swap Rider Numbers', iconMask = wx.ICON_ERROR )
			return
			
		if Utils.MessageOKCancel( self, "Confirm Swap numbers %d and %d." % (num, newNum), "Swap Rider Number" ):
			undo.pushState()
			with Model.LockRace() as race:
				race.swapRiders( num, newNum )
				race.numTimeInfo.swapRiders( num, newNum )
			self.setRider( newNum )
			self.refresh()
		
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
		
		dlg = wx.TextEntryDialog( self, "All time entries for %d will be copied to the new bib number.\n\nNew Bib Number:" % num,
								'Copy Rider Times', str(self.num.GetValue()) )
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
				Utils.MessageOK( self, "New Bib %d already exists.\nIf you really want to copy times to this number, delete it first." % newNum,
								'New Bib Number Already Exists', iconMask = wx.ICON_ERROR )
			else:
				Utils.MessageOK( self, "Cannot copy to the same number (%d)." % newNum,
								'Cannot Copy to Same Number', iconMask = wx.ICON_ERROR )
			return
			
		if Utils.MessageOKCancel( self, "Entries from %d will be copied to new Bib %d.\n\nAll entries for %d will be slightly earlier then entries for %d.\nContinue?" % (num, newNum, newNum, num), "Confirm Copy Rider Times" ):
			undo.pushState()
			with Model.LockRace() as race:
				race.copyRiderTimes( num, newNum )
				rNew = race.getRider( newNum )
				numTimeInfo = race.numTimeInfo
				for t in rNew.times:
					numTimeInfo.add( newNum, t )
			self.setRider( newNum )
			self.onNumChange()
	
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
				tStatus = min( tStatus, 23*60*60 )	# Assume that no race runs longer than 23 hours.
				self.atRaceTime.SetValue( Utils.SecondsToStr(tStatus) )
				
		self.commitChange()
		wx.CallAfter( self.refresh )
		
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
		dlg = wx.NumberEntryDialog( self, message = "", caption = "Add Missing Splits", prompt = "Missing Splits to Add:",
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
				riderName = '%s, %s %d' % (riderInfo['LastName'], riderInfo['FirstName'], num)
			except KeyError:
				try:
					riderName = '%s %d' % (riderInfo['LastName'], num)
				except KeyError:
					try:
						riderName = '%s %d' % (riderInfo['FirstName'], num)
					except KeyError:
						riderName = str(num)
						
			infoStart = race.numTimeInfo.getInfoStr( num, tLapStart )
			if infoStart:
				infoStart = '\nLap Start ' + infoStart
			infoEnd = race.numTimeInfo.getInfoStr( num, tLapEnd )
			if infoEnd:
				infoEnd = '\nLap End ' + infoEnd
		
			info = ('Rider: %s  Lap: %d\nLap Start:  %s Lap End: %s\nLap Time: %s\n%s%s' %
					(riderName, lap,
					Utils.formatTime(tLapStart),
					Utils.formatTime(tLapEnd),
					Utils.formatTime(tLapEnd - tLapStart),
					infoStart, infoEnd )).strip()
					
		Utils.MessageOK( self, info, 'Lap Details', pos=wx.GetMousePosition() )

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
				(wx.NewId(), 'Correct Lap End Time...',	'Change lap end time...',				lambda event, s = self: CorrectNumber(s, s.entry), interpCase),
				(wx.NewId(), 'Shift Lap End Time...',	'Move lap end time earlier/later...',	lambda event, s = self: ShiftNumber(s, s.entry), interpCase),
				(wx.NewId(), 'Delete Lap End Time...',	'Delete lap end time...',				lambda event, s = self: DeleteEntry(s, s.entry), nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), 'Note...',					'Add/Edit Lap Note',					self.OnGanttPopupLapNote, allCases),
				(None, None, None, None, None),
				(wx.NewId(), 'Pull after Lap End...',	'Pull after lap end...',				self.OnGanttPopupPull, allCases),
				(wx.NewId(), 'DNF after Lap End...',	'DNF after lap end...',					self.OnGanttPopupDNF, allCases),
				(None, None, None, None, None),
				(wx.NewId(), 'Show Lap Details...', 	'Show Lap Details',			self.OnGanttPopupLapDetail, allCases),
			]
			self.splitMenuInfo = [
					(wx.NewId(),
					'%d Split%s' % (split-1, 's' if split > 2 else ''),
					lambda evt, s = self, splits = split: s.doSplitLap(splits)) for split in xrange(2,8) ] + [
					(wx.NewId(),
					'Custom...',
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
			menu.PrependMenu( wx.NewId(), 'Add Missing Split', submenu )
			
		Utils.deleteTrailingSeparators( menu )
		self.PopupMenu( menu )
		menu.Destroy()
	
	def OnGanttPopupPull( self, event ):
		if not self.entry:
			return
		if not Utils.MessageOKCancel( self,
			'Pull Rider %d at %s after lap %d?' % (self.entry.num, Utils.formatTime(self.entry.t+1, True), self.entry.lap),
			'Pull Rider' ):
			return
		try:
			undo.pushState()
			with Model.LockRace() as race:
				race.getRider(self.entry.num).setStatus( Rider.Pulled, self.entry.t + 1 )
				race.setChanged()
		except:
			pass
		wx.CallAfter( self.refresh )
	
	def OnGanttPopupDNF( self, event ):
		if not Utils.MessageOKCancel( self,
			'DNF Rider %d at %s after lap %d?' % (self.entry.num, Utils.formatTime(self.entry.t+1, True), self.entry.lap),
			'DNF Rider' ):
			return
		try:
			undo.pushState()
			with Model.LockRace() as race:
				race.getRider(self.entry.num).setStatus( Rider.DNF, self.entry.t + 1 )
				race.setChanged()
		except:
			pass
		wx.CallAfter( self.refresh )
		
	def OnGanttPopupLapNote( self, event ):
		if not self.entry or not Model.race:
			return
		if not hasattr(Model.race, 'lapNote'):
			Model.race.lapNote = {}
		dlg = wx.TextEntryDialog( self, "Note for Rider %d on Lap %d:" % (self.entry.num, self.entry.lap), "Lap Note",
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
		self.atRaceTime.SetValue( Utils.SecondsToStr(secs) )
		self.atRaceTime.SetEditable( editable )
		self.atRaceTime.Enable( editable )
		self.atRaceTimeName.Enable( editable )
	
	def refresh( self ):
		self.num.SelectAll()
		wx.CallAfter( self.num.SetFocus )

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
		
		for w in [	'startTimeName', 'startTime',
					'finishTimeName', 'finishTime',
					'rideTimeName', 'rideTime',
					'adjustTime']:
			getattr( self, w ).Show( False )
		
		tagNums = GetTagNums()
		
		highPrecisionTimes = Utils.highPrecisionTimes()
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
				self.riderTeam.SetLabel( info.get('Team', '') )
			except KeyError:
				pass

			try:
				info = externalInfo[int(num)]
				tags = []
				for tagName in ['Tag', 'Tag2']:
					try:
						tags.append( info[tagName].lstrip('0') )
					except (KeyError, ValueError):
						pass
				if tags:
					self.tags.SetLabel( ', '.join(tags) )
			except KeyError:
				pass
				
			category = race.getCategory( num )
			catName = category.fullname if category else ''
			categories = race.getCategories()
			try:
				iCategory = (i for i, c in enumerate(categories) if c == category).next()
				self.category.AppendItems( [c.fullname for c in categories] )
				self.category.SetSelection( iCategory )
			except StopIteration:
				self.category.AppendItems( [c.fullname for c in categories] + [' '] )
				self.category.SetSelection( len(categories) )
				
			#--------------------------------------------------------------------------------------
			if num not in race:
				return
				
			if category and getattr(category, 'distance', None) and category.distanceIsByLap:
				distanceByLap = getattr(category, 'distance')
			else:
				distanceByLap = None
			
			# Trigger adding the rider to the race if it isn't in already.
			rider = race.getRider( num )
			self.statusOption.SetSelection( rider.status )
			if rider.status == Model.Rider.Finisher:
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
				for w in [	'startTimeName', 'startTime',
							'finishTimeName', 'finishTime',
							'rideTimeName', 'rideTime',
							'adjustTime']:
					getattr( self, w ).Show( True )
				st, ft, laps = getStFtLaps( rider )
				self.startTime.SetLabel( Utils.formatTime(st, True) if st is not None else '')
				self.finishTime.SetLabel( Utils.formatTime(ft, True) if ft is not None else '')
				self.rideTime.SetLabel( Utils.formatTime(ft-st, True) if ft is not None and st is not None else '')
			
			maxLap = race.getMaxLap()
			if race.numLaps is not None and race.numLaps < maxLap:
				maxLap = race.numLaps
			
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
				notInLapStr = 'Lapped by Race Leader in %s' % (', '.join( str(i) for i, b in enumerate(appearedInLap) if not b ))
			else:
				notInLapStr = ''
			self.notInLap.SetLabel( notInLapStr )

			# Populate the lap times.
			try:
				raceTime = min(category.getStartOffsetSecs() if category else 0.0, entries[0].t)
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
				
				row[0:3] = ( str(r+1), Utils.formatTime(tLap, highPrecisionTimes), Utils.formatTime(e.t, highPrecisionTimes) )
				
				graphData.append( tLap )
				ganttData.append( e.t )
				ganttInterp.append( e.interp )
				
				highlightColour = None
				if e.interp:
					row[3:5] = ('Auto', 'CrossMgr')
					highlightColour = self.yellowColour
				else:
					info = numTimeInfo.getInfo( e.num, e.t )
					if info:
						row[3:6] = ( Model.NumTimeInfo.ReasonName[info[0]], info[1], info[2].ctime() )
						highlightColour = self.orangeColour
						
				if distanceByLap:
					row[6:8] = ('%.2f' % (1000.0 if tLap <= 0.0 else (category.getLapDistance(r+1) / (tLap / (60.0*60.0)))),
								'%.2f' % (1000.0 if tSum <= 0.0 else (category.getDistanceAtLap(r+1) / (tSum / (60.0*60.0)))) )
				
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
			self.splitter.SetSashPosition( 260 )
		self.hs.RecalcSizes()
		self.hs.Layout()
		self.grid.FitInside()
	
	def commitChange( self ):
		num = self.num.GetValue()
		status = self.statusOption.GetSelection()
		
		undo.pushState();
		with Model.LockRace() as race:
			# Allow new numbers to be added if status is DNS or DQ.
			if race is None or (num not in race and status not in [Model.Rider.DNS, Model.Rider.DQ]):
				return
				
			rider = race.getRider(num)
			oldValues = (rider.status, rider.tStatus)

			tStatus = None
			if status not in [Model.Rider.Finisher, Model.Rider.DNS, Model.Rider.DQ]:
				tStatus = Utils.StrToSeconds( self.atRaceTime.GetValue() )
			
			rider.setStatus( status, tStatus )

			newValues = (rider.status, rider.tStatus)
			if oldValues != newValues:
				race.setChanged()
			
	def commit( self ):
		self.commitChange()
		
class RiderDetailDialog( wx.Dialog ):
	def __init__( self, parent, num = None, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "RiderDetail",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		vs = wx.BoxSizer( wx.VERTICAL )
		
		self.riderDetail = RiderDetail( self )
		self.riderDetail.SetMinSize( (700, 500) )
		
		vs.Add( self.riderDetail, 1, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		self.closeBtn = wx.Button( self, wx.ID_ANY, '&Close (Ctrl-Q)' )
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
	
	app = wx.PySimpleApp()
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
