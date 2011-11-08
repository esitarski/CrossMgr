import Model
from Utils import formatTime, SetLabel
import wx
import datetime
import bisect
import Utils
import ColGrid
import StatusBar
import OutputStreamer
from EditEntry import CorrectNumber, SplitNumber, DeleteEntry

# Define columns for recorded and expected infomation.
iNumCol = 0
iLdrCol = 1
iLapCol = 2
iTimeCol = 3
iColMax = 4
colnames = [None] * iColMax
colnames[iNumCol] = 'Num'
colnames[iLdrCol] = 'Ldr'
colnames[iLapCol] = 'Lap'
colnames[iTimeCol] = 'Time'

fontSize = 14

def GetLabelGrid( parent ):
	font = wx.Font( fontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL )
	dc = wx.WindowDC( parent )
	dc.SetFont( font )
	w, h = dc.GetTextExtent( '999' )

	label = wx.StaticText( parent, wx.ID_ANY, 'Recorded:' )
	
	grid = ColGrid.ColGrid( parent, colnames = colnames )
	grid.SetRowLabelSize( 0 )
	grid.SetRightAlign( True )
	grid.AutoSizeColumns( True )
	grid.DisableDragColSize()
	grid.DisableDragRowSize()
	grid.SetDoubleBuffered( True )
	grid.SetDefaultCellFont( font )
	grid.SetDefaultRowSize( int(h * 1.15), True )
	return label, grid
		
class LabelGrid( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY, style = 0 ):
		wx.Panel.__init__(self, parent, id, style=style)
		
		bsMain = wx.BoxSizer( wx.VERTICAL )
		
		self.label, self.grid = GetLabelGrid( self )
		bsMain.Add( self.label, 0, flag=wx.ALL, border=4 )		
		bsMain.Add( self.grid, 1, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		self.SetSizer( bsMain )
		self.Layout()
		
class ForecastHistory( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY, style = 0 ):
		wx.Panel.__init__(self, parent, id, style=style)
		
		self.quickHistory = None
		self.orangeColour = wx.Colour(255, 165, 0)

		# Main sizer.
		bsMain = wx.BoxSizer( wx.VERTICAL )
		
		# Put Recorded and Expected in a splitter window.
		self.splitter = wx.SplitterWindow( self )
		
		self.lgHistory = LabelGrid( self.splitter, style = wx.BORDER_SUNKEN )
		self.historyName = self.lgHistory.label
		self.historyName.SetLabel( 'Recorded:' )
		self.historyGrid = self.lgHistory.grid
		self.Bind( wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.doPopup, self.historyGrid )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doPopup, self.historyGrid )		
		
		self.lgExpected = LabelGrid( self.splitter, style = wx.BORDER_SUNKEN )
		self.expectedName = self.lgExpected.label
		self.expectedGrid = self.lgExpected.grid
		self.expectedName.SetLabel( 'Expected:' )
		self.expectedGrid.SetDefaultCellBackgroundColour( wx.Colour(238,255,255) )
		self.Bind( wx.grid.EVT_GRID_SELECT_CELL, self.doExpectedSelect, self.expectedGrid )
		
		self.splitter.SetMinimumPaneSize( 64 )
		self.splitter.SetSashGravity( 0.5 )
		self.splitter.SplitHorizontally( self.lgHistory, self.lgExpected, 100 )
		self.Bind( wx.EVT_SPLITTER_DCLICK, self.doSwapOrientation, self.splitter )
		bsMain.Add( self.splitter, 1, flag=wx.EXPAND | wx.ALL, border = 4 )
		#-----------------------------------------------------------------------------------
		# 80% rule countdown
		#
		self.rule80Gauge = StatusBar.StatusBar(self, wx.ID_ANY, value=0, range=0)
		self.rule80Gauge.SetFont( wx.Font(fontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL) )
		bsMain.Add( self.rule80Gauge, 0, flag=wx.EXPAND | wx.ALL, border = 4 )
				
		self.historyGrid.Reset()
		self.expectedGrid.Reset()
		
		self.SetSizer( bsMain )
		self.refresh()
		self.Layout()
		
	def setSash( self ):
		size = self.GetClientSize()
		if self.splitter.GetSplitMode() == wx.SPLIT_VERTICAL:
			self.splitter.SetSashPosition( size.width // 2 )
		else:
			self.splitter.SetSashPosition( size.height // 2 )

	def swapOrientation( self ):
		if self.splitter.GetSplitMode() == wx.SPLIT_VERTICAL:
			self.splitter.SetSplitMode( wx.SPLIT_HORIZONTAL )
		else:
			self.splitter.SetSplitMode( wx.SPLIT_VERTICAL )
		self.setSash()
		
	def doSwapOrientation( self, event ):
		self.swapOrientation()
			
	def doPopup( self, event ):
		self.rowPopup = event.GetRow()
		race = Model.getRace()
		if self.rowPopup >= len(self.quickHistory) or not race or not race.isRunning():
			return
		if self.rowPopup < self.historyGrid.GetNumberRows():
			value = self.historyGrid.GetCellValue( self.rowPopup, 0 )
		if not value:
			return
			
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				('Correct...',	wx.NewId(), self.OnPopupCorrect),
				('Split...',	wx.NewId(), self.OnPopupSplit),
				('Delete...',	wx.NewId(), self.OnPopupDelete),
			]
			for p in self.popupInfo:
				self.Bind( wx.EVT_MENU, p[2], id=p[1] )

		menu = wx.Menu()
		for i, p in enumerate(self.popupInfo):
			menu.Append( p[1], p[0] )
		
		self.PopupMenu( menu )
		menu.Destroy()
		
	def OnPopupCorrect( self, event ):
		if hasattr(self, 'rowPopup'):
			CorrectNumber( self, self.quickHistory[self.rowPopup] )
		
	def OnPopupSplit( self, event ):
		if hasattr(self, 'rowPopup'):
			SplitNumber( self, self.quickHistory[self.rowPopup] )
		
	def OnPopupDelete( self, event ):
		if hasattr(self, 'rowPopup'):
			DeleteEntry( self, self.quickHistory[self.rowPopup] )
	
	def resetRule80( self ):
		self.rule80Gauge.SetRange( 0 )
		self.rule80Gauge.SetValue( 0 )

	def refreshRule80( self ):
		with Model.lock:
			race = Model.getRace()
			if not race or not race.isRunning() or race.getMaxLap() >= race.numLaps:
				self.resetRule80()
				return
			if race.getMaxLap() == race.numLaps - 1:
				leaderTime, leaderNum, leaderLapTime = race.getNextExpectedLeaderTNL( race.lastRaceTime() )
				if leaderTime is not None and race.lastRaceTime() + leaderLapTime * 0.05 > leaderTime:
					self.resetRule80()
					return
				
			remaining = race.getRule80RemainingCountdown()
			if remaining is None:
				self.rule80Gauge.SetRange( 10 )
				self.rule80Gauge.SetValue( 0 )
				return
			
			maxSeconds = int(race.getRule80CountdownTime())
			currentValue = self.rule80Gauge.GetValue()
			if self.rule80Gauge.GetRange() != maxSeconds:
				if currentValue > maxSeconds:
					self.rule80Gauge.SetValue( 0 )
					currentValue = 0
				self.rule80Gauge.SetRange( maxSeconds )
			remaining = int(remaining)
			if currentValue == 0 or currentValue > remaining:
				self.rule80Gauge.SetValue( remaining )
	
	def logNum( self, num ):
		if not num:
			return
		with Model.lock:
			race = Model.race
			if race is None or not race.isRunning():
				return
			t = race.curRaceTime()
			num = int(num)
			race.addTime( num, t )
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.record.numEdit.SetValue( None )
			mainWin.record.refreshLaps()
			mainWin.refresh()
		OutputStreamer.writeNumTime( num, t )
		
	def doExpectedSelect( self, event ):
		r = event.GetRow()
		if r < self.expectedGrid.GetNumberRows():
			self.logNum( self.expectedGrid.GetCellValue(r, 0) )
		
	def clearGrids( self ):
		self.historyGrid.Set( data = [] )
		self.historyGrid.Reset()
		self.expectedGrid.Set( data = [] )
		self.expectedGrid.Reset()
	
	def refresh( self ):
		with Model.lock:
			race = Model.race
			if race is None or not race.isRunning():
				self.clearGrids()
				return
						
			tRace = race.curRaceTime()
			
			entries = race.interpolateLap( race.numLaps if race.numLaps is not None else race.getMaxLap() + 1 )
			# Filter out zero start times and pulled or dnf riders.
			entries = [e for e in entries if e.t > 0 and race[e.num].status == Model.Rider.Finisher]
			
			#------------------------------------------------------------------
			# Select the interpolated entries around now.
			leaderNext = race.getNextLeader( tRace )
			leaderPrev = race.getPrevLeader( tRace )
			backSecs = race.getAverageLapTime() / 4.0
			
			expectedShowMax = 32
			
			tMin = tRace - backSecs
			tMax = tRace + race.getAverageLapTime()
			times = [e.t for e in entries]
			iCur = bisect.bisect_left( times, tRace )
			iLeft = max(0, iCur - expectedShowMax/2)
			times = None
			seen = {}
			expected = [ seen.setdefault(e.num, e) for e in entries[iLeft:] if e.interp and tMin <= e.t <= tMax and e.num not in seen ]
			expected = expected[:min(expectedShowMax, len(entries))]
			
			catNextLeaders = race.getCatNextLeaders( tRace )
			catPrevLeaders = race.getCatPrevLeaders( tRace )
			
			backgroundColour = {}
			#------------------------------------------------------------------
			# Highlight the missing riders.
			tMissing = tRace - race.getAverageLapTime() / 8.0
			iNotMissing = 0
			for r in (i for i, e in enumerate(expected) if e.t < tMissing):
				for c in xrange(iColMax):
					backgroundColour[(r, c)] = self.orangeColour
				iNotMissing = r + 1
			#------------------------------------------------------------------
			# Highlight the leader in the expected list.
			iBeforeLeader = None
			try:
				r = (i for i, e in enumerate(expected) if e.num == leaderNext).next()
				backgroundColour[(r, iNumCol)] = wx.GREEN
				iBeforeLeader = r
			except StopIteration:
				pass
				
			# Highlight the leader by category.
			for r, e in enumerate(expected):
				if e.num in catNextLeaders:
					backgroundColour[(r, iLdrCol)] = wx.GREEN
			
			data = [None] * iColMax
			data[iNumCol] = [str(e.num) for e in expected]
			data[iTimeCol] = [formatTime(e.t) for e in expected]
			data[iLapCol] = [str(e.lap) for e in expected]
			data[iLdrCol] = ['*' if e.num in catNextLeaders else ' ' for e in expected]
			
			self.expectedGrid.Set( data = data, backgroundColour = backgroundColour )
			self.expectedGrid.AutoSizeColumns()
			self.expectedGrid.AutoSizeRows()
			
			if iBeforeLeader:
				Utils.SetLabel( self.expectedName, 'Expected: %d before Race Leader' % iBeforeLeader )
			else:
				Utils.SetLabel( self.expectedName, 'Expected:' )
			
			#------------------------------------------------------------------
			# Update recorded.
			recordedDisplayMax = 32
			recorded = [ e for e in entries if not e.interp and e.t <= tRace ]
			recorded = recorded[-min(recordedDisplayMax, len(entries)):]
			self.quickHistory = recorded
				
			backgroundColour = {}
			data = [None] * iColMax
			data[iNumCol] = [str(e.num) for e in recorded]
			data[iTimeCol] = [formatTime(e.t) for e in recorded]
			data[iLapCol] = [str(e.lap) for e in recorded]
			data[iLdrCol] = ['*' if e.num in catPrevLeaders else ' ' for e in recorded]

			# Highlight the leader in the recorded list.
			for r, e in enumerate(recorded):
				if e.num == leaderPrev:
					backgroundColour[(r, iNumCol)] = wx.GREEN
				if e.num in catPrevLeaders:
					backgroundColour[(r, iLdrCol)] = wx.GREEN
				
			self.historyGrid.Set( data = data, backgroundColour = backgroundColour )
			self.historyGrid.AutoSizeColumns()
			self.historyGrid.AutoSizeRows()
			
			# Show the relevant cells in each table.
			if recorded:
				self.historyGrid.MakeCellVisible( len(recorded)-1, 0 )
			if iNotMissing < self.expectedGrid.GetNumberRows():
				self.expectedGrid.MakeCellVisible( iNotMissing, 0 )

if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	
	fh = ForecastHistory(mainWin)
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	fh.refresh()
	mainWin.Show()
	fh.setSash()
	fh.swapOrientation()
	app.MainLoop()
