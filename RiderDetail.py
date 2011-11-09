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

class RiderDetail( wx.Panel ):
	lapAdjustOptions = ['+5','+4','+3','+2','+1','0','-1','-2','-3','-4','-5']
	
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		
		self.num = None
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		
		gbs = wx.GridBagSizer(4, 5)
		row = 0
		self.numName = wx.StaticText( self, wx.ID_ANY, 'Number: ' )
		gbs.Add( self.numName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.num = intctrl.IntCtrl( self, wx.ID_ANY, min=0, max=9999, allow_none=True, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER )
		self.Bind( wx.EVT_TEXT_ENTER, self.onNumChange, self.num )
		gbs.Add( self.num, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		
		self.deleteRiderBtn = wx.Button( self, wx.ID_ANY, 'Delete' )
		self.Bind( wx.EVT_BUTTON, self.onDeleteRider, self.deleteRiderBtn )
		gbs.Add( self.deleteRiderBtn, pos=(row, 3), span=(1,1), flag=wx.EXPAND )
		row += 1
		
		self.categoryName = wx.StaticText( self, wx.ID_ANY, 'Category: ' )
		gbs.Add( self.categoryName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.category = wx.StaticText( self, wx.ID_ANY, '' )
		self.category.SetDoubleBuffered( True )
		gbs.Add( self.category, pos=(row,1), span=(1,1), flag=wx.EXPAND )
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
		
		self.lapAdjustName	= wx.StaticText( self, wx.ID_ANY, 'Lap Adjust: ' )
		gbs.Add( self.lapAdjustName, pos=(row,0), span=(1,1), flag=labelAlign )
		self.lapAdjust = wx.Choice( self, 2, choices=RiderDetail.lapAdjustOptions )
		gbs.Add( self.lapAdjust, pos=(row,1), span=(1,1), flag=wx.EXPAND )
		self.Bind(wx.EVT_CHOICE, self.onLapAdjustChanged, self.lapAdjust)
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
		self.setRider()
		
	def onDeleteRider( self, event ):
		with Model.LockRace() as race:
			if race is None:
				return
			try:
				num = int(self.num.GetValue())
			except:
				return
				
			if num in race:
				if Utils.MessageOKCancel( self, "This will permenently delete this rider.\nOnly do this in case of a misidentified entry.\nThere is no undo - be careful.", "Delete Rider" ):
					race.deleteRider( num )
		
	def onNumChange( self, event ):
		self.refresh()
		if Utils.isMainWin():
			Utils.getMainWin().setNumSelect( self.num.GetValue() )
	
	def onLapAdjustChanged( self, event ):
		self.commitChange()
		self.refresh()
	
	def onStatusChanged( self, event ):
		race = Model.getRace()
		if race is None:
			return
		num = self.num.GetValue()
		statusOption = self.statusOption.GetSelection()
		if num in race and statusOption in [Model.Rider.DNF, Model.Rider.Pulled]:
			rider = race.getRider( num )
			# Try to fill in a reasonable default value.
			if not rider.tStatus:
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
	
	def setRider( self, n = None ):
		Utils.SetValue( self.num, int(n) if n is not None else None )
		
	def getGanttChartNumLapTimes( self ):
		lapCur = getattr(self, 'lapCur', None)
		if lapCur is None:
			return None, None, None

		race = Model.race
		if not race:
			return None, None, None
			
		num = self.num.GetValue()
		try:
			num = int(num)
		except:
			return None, None, None
		if num not in race:
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
	
	def onSplitLap2( self, event ):
		self.doSplitLap( 2 )
		
	def onSplitLap3( self, event ):
		self.doSplitLap( 3 )
		
	def onSplitLap4( self, event ):
		self.doSplitLap( 4 )
		
	def onSplitLap5( self, event ):
		self.doSplitLap( 5 )
		
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
			
	def onEditGantt( self, xPos, yPos, num, lap ):
		if not hasattr(self, "ganttMenuInfo"):
			self.ganttMenuInfo = [
				[wx.NewId(),	'Split Lap in 2 Pieces',	self.onSplitLap2],
				[wx.NewId(),	'Split Lap in 3 Pieces',	self.onSplitLap3],
				[wx.NewId(),	'Split Lap in 4 Pieces',	self.onSplitLap4],
				[wx.NewId(),	'Split Lap in 5 Pieces',	self.onSplitLap5],
				[wx.NewId(),	'Delete Lap Start Time',	self.onDeleteLapStart],
				[wx.NewId(),	'Delete Lap End Time',		self.onDeleteLapEnd],
			]

		menu = wx.Menu()		
		for id, name, callback in self.ganttMenuInfo:
			item = menu.Append( id, name )
			self.Bind( wx.EVT_MENU, callback, item )
			
		self.lapCur = lap
		self.PopupMenu( menu )
		menu.Destroy()
	
	def setNumSelect( self, num ):
		self.setRider( num )
	
	def getLapAdjustIndex( self, adjust = 0 ):
		if adjust is None:
			adjust = '0'
		else:
			adjust = '+%d' % adjust if adjust > 0 else str(adjust)
		for i, o in enumerate(RiderDetail.lapAdjustOptions):
			if o == adjust:
				return i
		return self.getLapAdjustIndex( 0 )
	
	def setAtRaceTime( self, secs = 0.0, editable = False ):
		self.atRaceTime.SetValue( Utils.SecondsToStr(secs) )
		self.atRaceTime.SetEditable( editable )
		self.atRaceTime.Enable( editable )
		self.atRaceTimeName.Enable( editable )
	
	def refresh( self ):
		with Model.LockRace() as race:
			self.num.SelectAll()
			wx.CallAfter( self.num.SetFocus )

			self.grid.Set( data = [ [], [], [] ] )
			self.grid.Reset()
			self.category.SetLabel( '' )
			self.lapAdjust.SetSelection( self.getLapAdjustIndex() )
			num = self.num.GetValue()
			
			self.statusOption.SetSelection( 0 )
			self.setAtRaceTime( 0.0, False )
			
			self.lineGraph.SetData( None )
			
			if race is None or num not in race:
				return
			rider = race.getRider( num )
			catName = race.getCategoryName( num )
			category = race.categories.get( catName, None )
			
			self.category.SetLabel( catName )
			self.lapAdjust.SetSelection( self.getLapAdjustIndex(rider.lapAdjust) )
			self.statusOption.SetSelection( rider.status )
			if rider.status in [Model.Rider.Finisher, Model.Rider.DNS, Model.Rider.DQ]:
				self.setAtRaceTime()
			else:
				if rider.tStatus is None:
					rider.tStatus = 0.0
				self.setAtRaceTime( rider.tStatus, True )
			
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
				i = bisect.bisect_left( leaderTimes, e.t )
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
				raceTime = e.t
				if e.interp:
					for i in xrange(0,3):
						backgroundColour[(r,i)] = (255,255,0)

			self.grid.Set( data = data, backgroundColour = backgroundColour )
			self.grid.AutoSizeColumns( True )
			self.grid.Reset()
			self.grid.FitInside()
			
			self.ganttChart.SetData( [ganttData], [num], Gantt.GetNowTime() )
			self.lineGraph.SetData( [graphData], [[e.interp for e in entries]] )
	
	def commitChange( self ):
		with Model.LockRace() as race:
			num = self.num.GetValue()
			status = self.statusOption.GetSelection()
			
			# Allow new numbers to be added if status is DNS or DQ.
			if race is None or (num not in race and status not in [Model.Rider.DNS, Model.Rider.DQ]):
				return
				
			rider = race.getRider(num)
			oldValues = [rider.lapAdjust, rider.status, rider.tStatus]

			tStatus = None
			if status not in [Model.Rider.Finisher, Model.Rider.DNS, Model.Rider.DQ]:
				tStatus = Utils.StrToSeconds( self.atRaceTime.GetValue() )
			
			rider.lapAdjust = int(self.lapAdjust.GetStringSelection())
			rider.setStatus( status, tStatus )

			newValues = [ rider.lapAdjust, rider.status, rider.tStatus ]
			if oldValues != newValues:
				Model.resetCache()
				Utils.writeRace()
			
	def commit( self ):
		self.commitChange()
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMgr", size=(600,400))
	riderDetail = RiderDetail(mainWin)
	riderDetail.refresh()
	lineData = [random.normalvariate(100,15) for x in xrange(12)]
	ganttData = [0, lineData[0] * 3]
	for d in lineData:
		ganttData.append( ganttData[-1] + d )
	riderDetail.ganttChart.SetData( [ganttData], [106] )
	riderDetail.lineGraph.SetData( [lineData] )
	mainWin.Show()
	app.MainLoop()
