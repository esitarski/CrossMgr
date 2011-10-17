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

class ForecastHistory( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY, style = 0 ):
		wx.Panel.__init__(self, parent, id, style=style)
		
		self.quickHistory = None
		self.orangeColour = wx.Colour(255, 165, 0)

		fontSize = 14
		font = wx.Font(fontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		dc = wx.WindowDC( self )
		dc.SetFont( font )
		w, h = dc.GetTextExtent( '999' )

		bsMain = wx.BoxSizer(wx.VERTICAL)
		
		#-----------------------------------------------------------------------------------
		# Recorded Numbers
		#
		bsMain.Add( wx.StaticText( self, wx.ID_ANY, 'Recorded:' ), 0, flag=wx.EXPAND | wx.ALL, border=4 )
		
		self.iNumCol = 0
		self.iLdrCol = 1
		self.iLapCol = 2
		self.iTimeCol = 3
		self.iColMax = 4
		colnames = [None] * self.iColMax
		colnames[self.iNumCol] = 'Num'
		colnames[self.iLdrCol] = 'Ldr'
		colnames[self.iLapCol] = 'Lap'
		colnames[self.iTimeCol] = 'Time'
		
		self.historyGrid = ColGrid.ColGrid( self, colnames = colnames )
		self.historyGrid.SetRowLabelSize( 0 )
		self.historyGrid.SetRightAlign( True )
		self.historyGrid.AutoSizeColumns( True )
		self.historyGrid.DisableDragColSize()
		self.historyGrid.DisableDragRowSize()
		self.historyGrid.SetDoubleBuffered( True )
		self.historyGrid.SetDefaultCellFont( font )
		#self.historyGrid.SetLabelFont( font )
		self.historyGrid.SetDefaultRowSize( int(h * 1.15), True)
		self.Bind( wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.doPopup,self.historyGrid )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doPopup,self.historyGrid )		
		bsMain.Add( self.historyGrid, 1, flag=wx.EXPAND|wx.GROW|wx.ALL, border = 4 )

		#-----------------------------------------------------------------------------------
		# Expected numbers
		#
		self.expectedName = wx.StaticText( self, wx.ID_ANY, 'Expected:' )
		bsMain.Add( self.expectedName, 0, flag=wx.EXPAND | wx.ALL, border=4 )
		
		self.expectedGrid = ColGrid.ColGrid( self, colnames = colnames )
		self.expectedGrid.SetRowLabelSize( 0 )
		self.expectedGrid.SetColLabelSize( 0 )
		self.expectedGrid.SetRightAlign( True )
		self.expectedGrid.AutoSizeColumns( True )
		self.expectedGrid.DisableDragColSize()
		self.expectedGrid.DisableDragRowSize()
		self.expectedGrid.SetDoubleBuffered( True )
		self.expectedGrid.SetDefaultCellFont( font )
		#self.expectedGrid.SetLabelFont( font )
		self.expectedGrid.SetDefaultRowSize( int(h * 1.25), True)
		self.Bind( wx.grid.EVT_GRID_SELECT_CELL, self.doExpectedSelect, self.expectedGrid )		
		bsMain.Add( self.expectedGrid, 1, flag=wx.EXPAND|wx.GROW|wx.ALL, border = 4 )
		
		#-----------------------------------------------------------------------------------
		# 80% rule countdown
		#
		self.rule80Gauge = StatusBar.StatusBar(self, wx.ID_ANY, value=0, range=0)
		self.rule80Gauge.SetFont( font )
		
		bsMain.Add( self.rule80Gauge, 0, flag=wx.EXPAND | wx.ALL |  wx.GROW, border = 4 )
				
		self.historyGrid.Reset()
		self.expectedGrid.Reset()
		
		self.SetSizer( bsMain )
		self.refresh()

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
		
		expectedShowMax = 20
		
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
			for c in xrange(self.iColMax):
				backgroundColour[(r, c)] = self.orangeColour
			iNotMissing = r + 1
		#------------------------------------------------------------------
		# Highlight the leader in the expected list.
		iBeforeLeader = None
		try:
			r = (i for i, e in enumerate(expected) if e.num == leaderNext).next()
			backgroundColour[(r, self.iNumCol)] = wx.GREEN
			iBeforeLeader = r
		except StopIteration:
			pass
			
		# Highlight the leader by category.
		for r, e in enumerate(expected):
			if e.num in catNextLeaders:
				backgroundColour[(r, self.iLdrCol)] = wx.GREEN
		
		data = [None] * self.iColMax
		data[self.iNumCol] = [str(e.num) for e in expected]
		data[self.iTimeCol] = [formatTime(e.t) for e in expected]
		data[self.iLapCol] = [str(e.lap) for e in expected]
		data[self.iLdrCol] = ['*' if e.num in catNextLeaders else ' ' for e in expected]
		
		self.expectedGrid.Set( data = data, backgroundColour = backgroundColour )
		self.expectedGrid.AutoSizeColumns()
		self.expectedGrid.AutoSizeRows()
		
		if iBeforeLeader:
			Utils.SetLabel( self.expectedName, 'Expected: %d before Race Leader' % iBeforeLeader )
		else:
			Utils.SetLabel( self.expectedName, 'Expected:' )
		
		#------------------------------------------------------------------
		# Update recorded.
		recordedDisplayMax = 25
		recorded = [ e for e in entries if not e.interp and e.t <= tRace ]
		recorded = recorded[-min(recordedDisplayMax, len(entries)):]
		self.quickHistory = recorded
			
		backgroundColour = {}
		data = [None] * self.iColMax
		data[self.iNumCol] = [str(e.num) for e in recorded]
		data[self.iTimeCol] = [formatTime(e.t) for e in recorded]
		data[self.iLapCol] = [str(e.lap) for e in recorded]
		data[self.iLdrCol] = ['*' if e.num in catPrevLeaders else ' ' for e in recorded]

		# Highlight the leader in the recorded list.
		for r, e in enumerate(recorded):
			if e.num == leaderPrev:
				backgroundColour[(r, self.iNumCol)] = wx.GREEN
			if e.num in catPrevLeaders:
				backgroundColour[(r, self.iLdrCol)] = wx.GREEN
			
		self.historyGrid.Set( data = data, backgroundColour = backgroundColour )
		self.historyGrid.AutoSizeColumns()
		self.historyGrid.AutoSizeRows()
			
		# Force the grids to the correct size.
		self.expectedGrid.FitInside()
		self.historyGrid.FitInside()
		
		self.Layout()

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
	app.MainLoop()
