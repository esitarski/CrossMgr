import Model
from Utils import formatTime, SetLabel
import wx
import datetime
import bisect
import Utils
import ColGrid
import StatusBar
import OutputStreamer
import NumKeypad
from EditEntry import CorrectNumber, SplitNumber, ShiftNumber, InsertNumber, DeleteEntry, DoDNS, DoDNF, DoPull
from FtpWriteFile import realTimeFtpPublish

# Define columns for recorded and expected infomation.
iNumCol, iNoteCol, iTimeCol, iLapCol, iGapCol, iNameCol, iColMax = range(7)
colnames = [None] * iColMax
colnames[iNumCol]  = 'Num'
colnames[iNoteCol] = 'Note'
colnames[iLapCol]  = 'Lap'
colnames[iTimeCol] = 'Time'
colnames[iGapCol]  = 'Gap'
colnames[iNameCol] = 'Name'

fontSize = 14

def GetLabelGrid( parent ):
	font = wx.Font( fontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL )
	dc = wx.WindowDC( parent )
	dc.SetFont( font )
	w, h = dc.GetTextExtent( '999' )

	label = wx.StaticText( parent, wx.ID_ANY, 'Recorded:' )
	
	grid = ColGrid.ColGrid( parent, colnames = colnames )
	grid.SetLeftAlignCols( [iNameCol] )
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
		self.quickExpected = None
		self.orangeColour = wx.Colour(255, 165, 0)
		self.redColour = wx.Colour(255, 51, 51)

		# Main sizer.
		bsMain = wx.BoxSizer( wx.VERTICAL )
		
		# Put Recorded and Expected in a splitter window.
		self.splitter = wx.SplitterWindow( self )
		
		self.lgHistory = LabelGrid( self.splitter, style = wx.BORDER_SUNKEN )
		self.historyName = self.lgHistory.label
		self.historyName.SetLabel( 'Recorded:' )
		self.historyGrid = self.lgHistory.grid
		self.Bind( wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.doNumDrilldown, self.historyGrid )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doHistoryPopup, self.historyGrid )
		
		self.lgExpected = LabelGrid( self.splitter, style = wx.BORDER_SUNKEN )
		self.expectedName = self.lgExpected.label
		self.expectedGrid = self.lgExpected.grid
		self.expectedGrid.SetDoubleBuffered( True )
		colnames[iTimeCol] = 'ETA'
		self.expectedGrid.Set( colnames = colnames )
		self.expectedName.SetLabel( 'Expected:' )
		self.expectedGrid.SetDefaultCellBackgroundColour( wx.Colour(230,255,255) )
		self.Bind( wx.grid.EVT_GRID_SELECT_CELL, self.doExpectedSelect, self.expectedGrid )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doExpectedPopup, self.expectedGrid )	
		
		self.splitter.SetMinimumPaneSize( 64 )
		self.splitter.SetSashGravity( 0.5 )
		self.splitter.SplitHorizontally( self.lgHistory, self.lgExpected, 100 )
		self.Bind( wx.EVT_SPLITTER_DCLICK, self.doSwapOrientation, self.splitter )
		bsMain.Add( self.splitter, 1, flag=wx.EXPAND | wx.ALL, border = 4 )
				
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
		width = 285
		if self.splitter.GetSplitMode() == wx.SPLIT_VERTICAL:
			self.splitter.SetSplitMode( wx.SPLIT_HORIZONTAL )
			mainWin = Utils.getMainWin()
			if mainWin:
				mainWin.splitter.SetSashPosition( width )
		else:
			self.splitter.SetSplitMode( wx.SPLIT_VERTICAL )
			mainWin = Utils.getMainWin()
			if mainWin:
				mainWin.splitter.SetSashPosition( width * 2 )
		self.setSash()
		
	def doSwapOrientation( self, event ):
		self.swapOrientation()
	
	def doNumDrilldown( self, event ):
		with Model.LockRace() as race:
			if not race or not race.isRunning():
				return
		grid = event.GetEventObject()
		row = event.GetRow()
		value = ''
		if row < grid.GetNumberRows():
			value = grid.GetCellValue( row, 0 )
		if not value:
			return
		numSelect = value
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.setNumSelect( numSelect )
			mainWin.showPageName( 'RiderDetail' )
	
	def doHistoryPopup( self, event ):
		self.rowPopup = event.GetRow()
		with Model.LockRace() as race:
			if self.rowPopup >= len(self.quickHistory) or not race or not race.isRunning():
				return
		value = ''
		if self.rowPopup < self.historyGrid.GetNumberRows():
			value = self.historyGrid.GetCellValue( self.rowPopup, 0 )
		if not value:
			return
			
		if not hasattr(self, 'historyPopupInfo'):
			self.historyPopupInfo = [
				('Correct...',	wx.NewId(), self.OnPopupHistoryCorrect),
				('Split...',	wx.NewId(), self.OnPopupHistorySplit),
				('Shift...',	wx.NewId(), self.OnPopupHistoryShift),
				('Insert...',	wx.NewId(), self.OnPopupHistoryInsert),
				('Delete...',	wx.NewId(), self.OnPopupHistoryDelete),
				(None,			None,		None),
				('DNF...',		wx.NewId(), self.OnPopupHistoryDNF),
				(None,			None,		None),
				('RiderDetail',wx.NewId(),self.OnPopupHistoryRiderDetail),

			]
			for p in self.historyPopupInfo:
				if p[2]:
					self.Bind( wx.EVT_MENU, p[2], id=p[1] )

		menu = wx.Menu()
		for i, p in enumerate(self.historyPopupInfo):
			if p[2]:
				menu.Append( p[1], p[0] )
			else:
				menu.AppendSeparator()
		
		self.PopupMenu( menu )
		menu.Destroy()
		
	def OnPopupHistoryCorrect( self, event ):
		if hasattr(self, 'rowPopup'):
			CorrectNumber( self, self.quickHistory[self.rowPopup] )
		
	def OnPopupHistorySplit( self, event ):
		if hasattr(self, 'rowPopup'):
			SplitNumber( self, self.quickHistory[self.rowPopup] )
		
	def OnPopupHistoryShift( self, event ):
		if hasattr(self, 'rowPopup'):
			ShiftNumber( self, self.quickHistory[self.rowPopup] )
		
	def OnPopupHistoryInsert( self, event ):
		if hasattr(self, 'rowPopup'):
			InsertNumber( self, self.quickHistory[self.rowPopup] )
		
	def OnPopupHistoryDelete( self, event ):
		if hasattr(self, 'rowPopup'):
			DeleteEntry( self, self.quickHistory[self.rowPopup] )
			
	def OnPopupHistoryDNF( self, event ):
		try:
			num = self.quickHistory[getattr(self, 'rowPopup')].num
			NumKeypad.DoDNF( self, num )
		except:
			pass
	
	def OnPopupHistoryRiderDetail( self, event ):
		try:
			num = self.quickHistory[getattr(self, 'rowPopup')].num
			mainWin = Utils.getMainWin()
			mainWin.setNumSelect( num )
			mainWin.showPageName( 'RiderDetail' )
		except:
			pass
				
	#--------------------------------------------------------------------
	
	def doExpectedPopup( self, event ):
		self.rowPopup = event.GetRow()
		with Model.LockRace() as race:
			if self.rowPopup >= len(self.quickExpected) or not race or not race.isRunning():
				return
		if self.rowPopup < self.expectedGrid.GetNumberRows():
			value = self.expectedGrid.GetCellValue( self.rowPopup, 0 )
		if not value:
			return
			
		if not hasattr(self, 'expectedPopupInfo'):
			self.expectedPopupInfo = [
				('Enter',			wx.NewId(), self.OnPopupExpectedEnter),
				('DNF...',			wx.NewId(), self.OnPopupExpectedDNF),
				('Pull...',			wx.NewId(), self.OnPopupExpectedPull),
				(None,				None,		None),
				('RiderDetail',wx.NewId(),	self.OnPopupExpectedRiderDetail),
			]
			for p in self.expectedPopupInfo:
				if p[2]:
					self.Bind( wx.EVT_MENU, p[2], id=p[1] )

		menu = wx.Menu()
		for i, p in enumerate(self.expectedPopupInfo):
			if p[2]:
				menu.Append( p[1], p[0] )
			else:
				menu.AppendSeparator()
		
		self.PopupMenu( menu )
		menu.Destroy()
		
	def OnPopupExpectedEnter( self, event ):
		try:
			num = self.quickExpected[getattr(self, 'rowPopup')].num
			self.logNum( num )
		except:
			pass
		
	def OnPopupExpectedDNF( self, event ):
		try:
			num = self.quickExpected[getattr(self, 'rowPopup')].num
			NumKeypad.DoDNF( self, num )
		except:
			pass
		
	def OnPopupExpectedPull( self, event ):
		try:
			num = self.quickExpected[getattr(self, 'rowPopup')].num
			NumKeypad.DoPull( self, num )
		except:
			pass

	def OnPopupExpectedRiderDetail( self, event ):
		try:
			num = self.quickExpected[getattr(self, 'rowPopup')].num
			mainWin = Utils.getMainWin()
			mainWin.setNumSelect( num )
			mainWin.showPageName( 'RiderDetail' )
		except:
			pass
				
	#--------------------------------------------------------------------
	
	def logNum( self, nums ):
		if nums is None:
			return
		if not isinstance(nums, (list, tuple)):
			nums = [nums]
		with Model.LockRace() as race:
			if race is None or not race.isRunning():
				return
			t = race.curRaceTime()
			for num in nums:
				try:
					num = int(num)
				except:
					continue
				race.addTime( num, t )
				OutputStreamer.writeNumTime( num, t )
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.record.numEdit.SetValue( '' )
			mainWin.record.refreshLaps()
			wx.CallAfter( mainWin.refresh )
		if getattr(race, 'ftpUploadDuringRace', False):
			realTimeFtpPublish.publishEntry()
		
	def doExpectedSelect( self, event ):
		r = event.GetRow()
		if r < self.expectedGrid.GetNumberRows():
			self.logNum( self.expectedGrid.GetCellValue(r, 0) )
		
	def clearGrids( self ):
		self.historyGrid.Set( data = [] )
		self.historyGrid.Reset()
		self.expectedGrid.Set( data = [] )
		self.expectedGrid.Reset()
	
	def updatedExpectedTimes( self, tRace = None ):
		if not self.quickExpected:
			return
		if not tRace:
			tRace = Model.race.curRaceTime()
		self.expectedGrid.SetColumn( iTimeCol, [formatTime(max(0.0, e.t - tRace)) for e in self.quickExpected] )
	
	def refresh( self ):
		with Model.LockRace() as race:
			if race is None or not race.isRunning():
				self.quickExpected = None
				self.clearGrids()
				return
				
			try:
				externalInfo = race.excelLink.read( True )
			except:
				externalInfo = {}
						
			tRace = race.curRaceTime()
			tRaceLength = race.minutes * 60.0
			
			entries = race.interpolateLapNonZeroFinishers( race.numLaps if race.numLaps is not None else race.getMaxLap() + 1 )
			entries = [e for e in entries if e.lap <= race.getCategoryNumLaps(e.num) ]
			
			isTimeTrial = getattr(race, 'isTimeTrial', False)
			if isTimeTrial:
				for rider in race.riders.itervalues():
					if rider.status == Model.Rider.Finisher and rider.firstTime:
						entries.append( Model.Entry(rider.num, 0, rider.firstTime, False) )
				entries.sort( cmp=Model.CmpEntryTT )
			#------------------------------------------------------------------
			# Select the interpolated entries around now.
			leaderPrev, leaderNext = race.getPrevNextLeader( tRace )
			averageLapTime = race.getAverageLapTime()
			backSecs = averageLapTime / 4.0
			
			expectedShowMax = 32
			
			tMin = tRace - backSecs
			tMax = tRace + averageLapTime
			iCur = bisect.bisect_left( entries, Model.Entry(0, 0, tRace, True) )
			iLeft = max(0, iCur - expectedShowMax/2)
			seen = {}
			expected = [ seen.setdefault(e.num, e) for e in entries[iLeft:] if e.interp and tMin <= e.t <= tMax and e.num not in seen ]
			expected = expected[:expectedShowMax]
			
			prevCatLeaders, nextCatLeaders = race.getCatPrevNextLeaders( tRace )
			prevRiderPosition, nextRiderPosition = race.getPrevNextRiderPositions( tRace )
			prevRiderGap, nextRiderGap = race.getPrevNextRiderGaps( tRace )
			
			backgroundColour = {}
			textColour = {}
			#------------------------------------------------------------------
			# Highlight the missing riders.
			tMissing = tRace - averageLapTime / 8.0
			iNotMissing = 0
			for r in (i for i, e in enumerate(expected) if e.t < tMissing):
				for c in xrange(iColMax):
					backgroundColour[(r, c)] = self.orangeColour
				iNotMissing = r + 1
				
			#------------------------------------------------------------------
			# Highlight the leaders in the expected list.
			iBeforeLeader = None
			# Highlight the leader by category.
			catNextTime = {}
			outsideTimeBound = set()
			for r, e in enumerate(expected):
				if e.num in nextCatLeaders:
					backgroundColour[(r, iNoteCol)] = wx.GREEN
					catNextTime[nextCatLeaders[e.num]] = e.t
					if e.num == leaderNext:
						backgroundColour[(r, iNumCol)] = wx.GREEN
						iBeforeLeader = r
				elif tRace < tRaceLength and race.isOutsideTimeBound(e.num):
					backgroundColour[(r, iNumCol)] = backgroundColour[(r, iNoteCol)] = self.redColour
					textColour[(r, iNumCol)] = textColour[(r, iNoteCol)] = wx.WHITE
					outsideTimeBound.add( e.num )
			
			data = [None] * iColMax
			data[iNumCol] = [str(e.num) for e in expected]
			data[iTimeCol] = [formatTime(max(0.0, e.t - tRace)) for e in expected]
			data[iLapCol] = [str(e.lap) for e in expected]
			def getNoteExpected( e ):
				try:
					position = prevRiderPosition.get(e.num, -1) if e.t < catNextTime[race.getCategory(e.num)] else \
							   nextRiderPosition.get(e.num, -1)
				except KeyError:
					position = prevRiderPosition.get(e.num, -1)
					
				if position == 1:
					return 'Lead'
				elif e.t < tMissing:
					return 'miss'
				elif position >= 0:
					return Utils.ordinal(position)
				else:
					return ' '
			data[iNoteCol] = [getNoteExpected(e) for e in expected]
			def getGapExpected( e ):
				try:
					gap = prevRiderGap.get(e.num, ' ') if e.t < catNextTime[race.getCategory(e.num)] else \
							   nextRiderGap.get(e.num, ' ')
				except KeyError:
					gap = prevRiderGap.get(e.num, ' ')
				return gap
			data[iGapCol] = [getGapExpected(e) for e in expected]
			def getName( e ):
				info = externalInfo.get(e.num, {})
				last, first = info.get('LastName',''), info.get('FirstName','')
				if last and first:
					return '%s, %s' % (last, first[:1].upper())
				return last or first
			data[iNameCol] = [getName(e) for e in expected]
			
			self.quickExpected = expected
			
			self.expectedGrid.Set( data = data, backgroundColour = backgroundColour, textColour = textColour )
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
			recorded = recorded[-recordedDisplayMax:]
			self.quickHistory = recorded
				
			backgroundColour = {}
			textColour = {}
			outsideTimeBound = set()
			# Highlight the leader in the recorded list.
			for r, e in enumerate(recorded):
				if prevRiderPosition.get(e.num,-1) == 1:
					backgroundColour[(r, iNoteCol)] = wx.GREEN
					if e.num == leaderPrev:
						backgroundColour[(r, iNumCol)] = wx.GREEN
				elif tRace < tRaceLength and race.isOutsideTimeBound(e.num):
					backgroundColour[(r, iNumCol)] = backgroundColour[(r, iNoteCol)] = self.redColour
					textColour[(r, iNumCol)] = textColour[(r, iNoteCol)] = wx.WHITE
					outsideTimeBound.add( e.num )
									
			data = [None] * iColMax
			data[iNumCol] = [str(e.num) for e in recorded]
			data[iTimeCol] = [formatTime(e.t) if e.lap > 0 else '[%s]' % formatTime(e.t) for e in recorded]
			data[iLapCol] = [str(e.lap) for e in recorded]
			def getNoteHistory( e ):
				if e.lap == 0:
					return 'Start'

				position = nextRiderPosition.get(e.num, -1)
				if position == 1:
					return 'Lead'
				elif position >= 0:
					return Utils.ordinal(position)
				else:
					return ' '
			data[iNoteCol] = [getNoteHistory(e) for e in recorded]
			def getGapHistory( e ):
				if e.lap == 0:
					return ' '
				return prevRiderGap.get(e.num, ' ')
			data[iGapCol] = [getGapHistory(e) for e in recorded]
			data[iNameCol] = [getName(e) for e in expected]

			self.historyGrid.Set( data = data, backgroundColour = backgroundColour, textColour = textColour )
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
