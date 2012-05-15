import wx
import wx.lib.intctrl as intctrl
import wx.lib.masked as masked
import Model
import Utils
import ColGrid
from LineGraph import LineGraph
from GanttChart import GanttChart
import Gantt
import random
import bisect
import sys
import re

class RiderDetail( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		
		self.num = None
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		
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
		
		self.categoryName = wx.StaticText( self, wx.ID_ANY, 'Category: ' )
		gbs.Add( self.categoryName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.category = wx.StaticText( self, wx.ID_ANY, '' )
		self.category.SetDoubleBuffered( True )
		gbs.Add( self.category, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		row += 1
		
		self.nameName = wx.StaticText( self, wx.ID_ANY, 'Name: ' )
		gbs.Add( self.nameName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.riderName = wx.StaticText( self, wx.ID_ANY, '' )
		self.riderName.SetDoubleBuffered( True )
		gbs.Add( self.riderName, pos=(row,1), span=(1,4), flag=wx.EXPAND )
		row += 1
		
		self.teamName = wx.StaticText( self, wx.ID_ANY, 'Team: ' )
		gbs.Add( self.teamName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.riderTeam = wx.StaticText( self, wx.ID_ANY, '' )
		self.riderTeam.SetDoubleBuffered( True )
		gbs.Add( self.riderTeam, pos=(row,1), span=(1,4), flag=wx.EXPAND )
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
		
		self.autoCorrectLaps = wx.CheckBox( self, wx.ID_ANY, 'Autocorrect Lap Data' )
		gbs.Add( self.autoCorrectLaps, pos = (row, 0), span=(1, 2), flag = wx.ALIGN_CENTRE|wx.EXPAND )
		self.Bind( wx.EVT_CHECKBOX, self.onAutoCorrectLaps, self.autoCorrectLaps )
		row += 1

		self.notInLap = wx.StaticText( self, wx.ID_ANY, '              ' )
		gbs.Add( self.notInLap, pos=(row,0), span=(1,4) )
		row += 1
	
		self.grid = ColGrid.ColGrid( self, colnames = ['Rider Lap', 'Race Time', 'Lap Time'] )
		self.grid.SetRowLabelSize( 0 )
		self.grid.SetRightAlign( True )
		#self.grid.SetDoubleBuffered( True )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()
		
		gbs.Add( self.grid, pos=(row,0), span=(1,2), flag=wx.EXPAND )
		
		self.lineGraph = LineGraph( self, wx.ID_ANY, style = wx.NO_BORDER )
		self.ganttChart = GanttChart( self, wx.ID_ANY, style = wx.NO_BORDER )
		self.ganttChart.getNowTimeCallback = Gantt.GetNowTime
		self.ganttChart.minimizeLabels = True
		self.ganttChart.rClickCallback = self.onEditGantt
		
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( self.ganttChart, proportion=0, border = 0, flag = wx.ALL | wx.EXPAND )
		vbs.Add( self.lineGraph, proportion=1, border = 0, flag = wx.ALL | wx.EXPAND )
		
		gbs.Add( vbs, pos=(row, 2), span=(1, 3), flag=wx.EXPAND )
		
		gbs.AddGrowableRow( row )
		gbs.AddGrowableCol( 4 )
		
		self.setAtRaceTime()
		self.SetSizer( gbs )
		self.gbs = gbs
		self.setRider()
		
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
			
		if Utils.MessageOKCancel( self, "Confirm Delete rider %d and all associated entries.\nOnly do this in case of a mistaken entry.\nThere is no undo - please be careful." % num,
									"Delete Rider" ):
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
			
		if Utils.MessageOKCancel( self, "Conform Change rider's number to %d.\nThere is no undo - be careful." % newNum, "Change Rider Number" ):
			with Model.LockRace() as race:
				race.renumberRider( num, newNum )
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
			
		if Utils.MessageOKCancel( self, "Confirm Swap numbers %d and %d.\nThere is no undo - be careful." % (num, newNum), "Swap Rider Number" ):
			with Model.LockRace() as race:
				race.swapRiders( num, newNum )
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
			with Model.LockRace() as race:
				race.copyRiderTimes( num, newNum )
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
				if statusOption == Model.Rider.DNF:
					try:
						tStatus = rider.times[-1] + 1.0
					except (IndexError, TypeError):
						pass
				self.atRaceTime.SetValue( Utils.SecondsToStr(tStatus) )
				
		self.commitChange()
		self.refresh()
		
	def onAutoCorrectLaps( self, event ):
		num = self.num.GetValue()
		if not Model.race or num not in Model.race:
			self.autoCorrectLaps.SetValue( True )
			return
		with Model.LockRace() as race:
			rider = race[num]
			rider.autoCorrectLaps = self.autoCorrectLaps.GetValue()
			race.setChanged()
		self.refresh()
	
	def setRider( self, n = None ):
		Utils.SetValue( self.num, int(n) if n is not None else None )
		
	def getGanttChartNumLapTimes( self ):
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
		num, lap, times = self.getGanttChartNumLapTimes()
		if num is None:
			return
		with Model.LockRace() as race:
			if race is None:
				return
			tLeft = times[lap-1]
			tRight = times[lap]
			splitTime = (tRight - tLeft) / float(splits)
			for i in xrange( 1, splits ):
				newTime = tLeft + splitTime * i
				race.addTime( num, newTime )
		self.refresh()
	
	def onDeleteLapStart( self, event ):
		num, lap, times = self.getGanttChartNumLapTimes()
		if num is None:
			return
		if self.lapCur != 1:
			with Model.LockRace() as race:
				race.deleteTime( num, times[lap-1] )
			self.refresh()
			
	def onDeleteLapEnd( self, event ):
		num, lap, times = self.getGanttChartNumLapTimes()
		if num is None:
			return
		with Model.LockRace() as race:
			race.deleteTime( num, times[lap] )
		self.refresh()
			
	def onEditGantt( self, xPos, yPos, num, iRider, lap ):
		if not hasattr(self, "ganttMenuInfo"):
			self.ganttMenuInfo = [
				[	wx.NewId(),
					'Add %d Missing Split%s' % (split-1, 's' if split > 2 else ''),
					lambda evt, s = self, splits = split: s.doSplitLap(splits)] for split in xrange(2,8) ] + [
				[None, None, None],
				[wx.NewId(),	'Delete Lap Start Time',	self.onDeleteLapStart],
				[wx.NewId(),	'Delete Lap End Time',		self.onDeleteLapEnd],
			]

		menu = wx.Menu()		
		for id, name, callback in self.ganttMenuInfo:
			if not id:
				menu.AppendSeparator()
				continue
			item = menu.Append( id, name )
			self.Bind( wx.EVT_MENU, callback, item )
			
		self.lapCur = lap
		self.PopupMenu( menu )
		menu.Destroy()
	
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

		self.grid.Set( data = [ [], [], [] ] )
		self.grid.Reset()
		self.category.SetLabel( '' )
		self.autoCorrectLaps.SetValue( True )
		num = self.num.GetValue()
		
		self.statusOption.SetSelection( 0 )
		self.setAtRaceTime( 0.0, False )
		
		self.lineGraph.SetData( None )
		self.ganttChart.SetData( [] )
		self.riderName.SetLabel( '' )
		self.riderTeam.SetLabel( '' )
		
		with Model.LockRace() as race:
			if race is None or num not in race:
				return
			rider = race.getRider( num )
			catName = race.getCategoryName( num )
			category = race.categories.get( catName, None )
			
			try:
				externalInfo = race.excelLink.read()
			except:
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
				
			self.category.SetLabel( catName if catName else 'Unmatched' )
			self.statusOption.SetSelection( rider.status )
			if rider.status in [Model.Rider.Finisher, Model.Rider.DNS, Model.Rider.DQ]:
				self.setAtRaceTime()
			else:
				if rider.tStatus is None:
					rider.tStatus = 0.0
				self.setAtRaceTime( rider.tStatus, True )
				
			self.autoCorrectLaps.SetValue( getattr(rider, 'autoCorrectLaps', True) )
			
			maxLap = race.getMaxLap()
			if race.numLaps is not None and race.numLaps < maxLap:
				maxLap = race.numLaps
			
			# Figure out which laps this rider was lapped in.
			entries = race.interpolateLap( maxLap )
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

			missingCount = sum( 1 for b in appearedInLap if not b ) if rider.status == Model.Rider.Finisher else 0
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
			data = [ [], [], [] ]
			graphData = []
			backgroundColour = {}
			for r, e in enumerate(entries):
				data[0].append( str(r+1) )
				data[1].append( Utils.formatTime(e.t) )
				tLap = max( e.t - raceTime, 0.0 )
				data[2].append( Utils.formatTime(tLap) )
				graphData.append( tLap )
				
				ganttData.append( e.t )
				ganttInterp.append( e.interp )
				
				raceTime = e.t
				if e.interp:
					for i in xrange(0,3):
						backgroundColour[(r,i)] = (255,255,0)

			self.grid.Set( data = data, backgroundColour = backgroundColour )
			self.grid.AutoSizeColumns( True )
			self.grid.Reset()
			self.grid.FitInside()
			
			self.ganttChart.SetData( [ganttData], [num], Gantt.GetNowTime(), [ganttInterp] )
			self.lineGraph.SetData( [graphData], [[e.interp for e in entries]] )
			
		self.gbs.Layout()
	
	def commitChange( self ):
		num = self.num.GetValue()
		status = self.statusOption.GetSelection()
			
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
	
if __name__ == '__main__':
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
