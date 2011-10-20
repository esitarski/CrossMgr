import Model
import Utils
import wx
import wx.grid		as gridlib
import ColGrid
import os
import re
from string import Template
from FixCategories import FixCategories
from EditEntry import CorrectNumber, SplitNumber, DeleteEntry, SwapEntry

reNonDigits = re.compile( '[^0-9]' )

def GetFontFromExisting( font, pointSize = None, family = None, style = None, weight = None, underline = None, face = None, encoding = None ):
	if pointSize is None: 	pointSize = font.GetPointSize()
	if family is None: 		family = font.GetFamily()
	if style is None: 		style = font.GetStyle()
	if weight is None: 		weight = font.GetWeight()
	if underline is None: 	underline = font.GetUnderlined()
	if face is None: 		face = font.GetFaceName()
	if encoding is None: 	encoding = font.GetEncoding()
	fNew = wx.Font( pointSize=pointSize, family=family, style=style, weight=weight, underline=underline, face=face, encoding=encoding) 
	return fNew

class History( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)

		self.showTimes = False
		self.showLapTimes = False
		self.showTimeDown = False
		self.numSelect = None
		self.isEmpty = True
		self.history = None
		self.rcInterp = set()
		self.textColour = {}
		self.backgroundColour = {}
		self.category = None
		
		self.whiteColour = wx.Colour( 255, 255, 255 )
		self.blackColour = wx.Colour( 0, 0, 0 )
		self.yellowColour = wx.Colour( 255, 255, 0 )
		self.greyColour = wx.Colour( 150, 150, 150 )
		
		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.showTimesToggle = wx.ToggleButton( self, wx.ID_ANY, 'Race Times' )
		self.showTimesToggle.SetValue( self.showTimes )
		self.Bind( wx.EVT_TOGGLEBUTTON, self.onShowTimes, self.showTimesToggle )
		
		self.showLapTimesToggle = wx.ToggleButton( self, wx.ID_ANY, 'Lap Times' )
		self.showLapTimesToggle.SetValue( self.showLapTimes )
		self.Bind( wx.EVT_TOGGLEBUTTON, self.onShowLapTimes, self.showLapTimesToggle )
		
		self.showTimeDownToggle = wx.ToggleButton( self, wx.ID_ANY, 'Time Down per Lap' )
		self.showTimeDownToggle.SetValue( self.showTimeDown )
		self.Bind( wx.EVT_TOGGLEBUTTON, self.onShowTimeDown, self.showTimeDownToggle )
		
		self.search = wx.SearchCtrl(self, size=(70,-1), style=wx.TE_PROCESS_ENTER )
		# self.search.ShowCancelButton( True )
		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
		self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancelSearch, self.search)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch, self.search)
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'Zoom-In-icon.png'), wx.BITMAP_TYPE_PNG )
		self.zoomInButton = wx.BitmapButton( self, wx.ID_ZOOM_IN, bitmap, style=wx.BU_EXACTFIT | wx.BU_AUTODRAW )
		self.Bind( wx.EVT_BUTTON, self.onZoomIn, self.zoomInButton )
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'Zoom-Out-icon.png'), wx.BITMAP_TYPE_PNG )
		self.zoomOutButton = wx.BitmapButton( self, wx.ID_ZOOM_OUT, bitmap, style=wx.BU_EXACTFIT | wx.BU_AUTODRAW )
		self.Bind( wx.EVT_BUTTON, self.onZoomOut, self.zoomOutButton )
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showTimesToggle, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showLapTimesToggle, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showTimeDownToggle, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( wx.StaticText(self, wx.ID_ANY, ' '), proportion=2 )
		self.hbs.Add( self.search, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomInButton, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomOutButton, flag=wx.TOP | wx.BOTTOM | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border=4 )

		self.grid = ColGrid.ColGrid( self )
		self.grid.SetRightAlign( True )
		self.grid.SetRowLabelSize( 32 )
		self.grid.SetMargins( 0, 0 )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()

		# Set the col labels tall enough for lap, lapsToGo, lapTime, raceTime.
		width, height, lineHeight = wx.ClientDC(self).GetMultiLineTextExtent( "0\n0\n0\n0" )
		self.grid.SetColLabelSize( height )
		
		self.Bind( wx.grid.EVT_GRID_SELECT_CELL, self.doNumSelect )
		self.Bind( wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.doNumDrilldown )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doRightClick )
		
		bs = wx.BoxSizer(wx.VERTICAL)
		bs.Add(self.hbs, flag=wx.GROW|wx.HORIZONTAL)
		bs.Add(self.grid, 1, wx.GROW|wx.ALL, 5)
		self.SetSizer(bs)
		bs.SetSizeHints(self)

	def OnSearch( self, event ):
		self.OnDoSearch()
		
	def OnCancelSearch( self, event ):
		self.search.SetValue( '' )
		
	def OnDoSearch( self, event = None ):
		n = self.search.GetValue()
		if n:
			n = reNonDigits.sub( '', n )
			self.search.SetValue( n )
		if not n:
			n = None
		if n:
			self.numSelect = n
			self.refresh()
			if Utils.isMainWin():
				Utils.getMainWin().setNumSelect( n )

	def onZoomOut( self, event ):
		self.grid.Zoom( False )
			
	def onZoomIn( self, event ):
		self.grid.Zoom( True )
		
	def doRightClick( self, event ):
		if self.isEmpty:
			return
			
		self.rowPopup = event.GetRow()
		self.colPopup = event.GetCol()
		numSelect = self.getCellNum( self.rowPopup, self.colPopup )
		if not numSelect:
			return
			
		self.doNumSelect( event )
		
		allCases = 0
		interpCase = 1
		nonInterpCase = 2
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				('Results', 	wx.NewId(), self.OnPopupResults, allCases),
				('Rider Detail',wx.NewId(), self.OnPopupRiderDetail, allCases),
				
				('Correct...',	wx.NewId(), self.OnPopupCorrect, interpCase),
				('Split...',	wx.NewId(), self.OnPopupSplit, nonInterpCase),
				('Delete...',	wx.NewId(), self.OnPopupDelete, nonInterpCase),
				
				('Swap with Before...',	wx.NewId(), self.OnPopupSwapBefore, nonInterpCase),
				('Swap with After...',	wx.NewId(), self.OnPopupSwapAfter, nonInterpCase),
			]
			self.numEditActions = 2
			self.numSwapActions = 5
			for p in self.popupInfo:
				self.Bind( wx.EVT_MENU, p[2], id=p[1] )

		isInterp = self.history[self.colPopup][self.rowPopup].interp
		if isInterp:
			caseCode = 1
		else:
			caseCode = 2
		
		race = Model.getRace()
		menu = wx.Menu()
		for i, p in enumerate(self.popupInfo):
			if i == self.numEditActions or i == self.numSwapActions:
				menu.AppendSeparator()
			if caseCode < p[3]:
				continue
			menu.Append( p[1], p[0] )
		
		self.PopupMenu( menu )
		menu.Destroy()
			
	def OnPopupSwapBefore( self, event ):
		if hasattr(self, 'rowPopup'):
			c, r, h = self.colPopup, self.rowPopup, self.history
			for rPrev in xrange( r - 1, -1, -1 ):
				if not h[c][rPrev].interp and (self.category is None or Model.race.getCategory(h[c][rPrev]) == self.category):
					SwapEntry( self, h[c][r], h[c][rPrev] )
					break
		
	def OnPopupSwapAfter( self, event ):
		if hasattr(self, 'rowPopup'):
			c, r, h = self.colPopup, self.rowPopup, self.history
			for rNext in xrange( r + 1, len(h[c]) ):
				if not h[c][rNext].interp and (self.category is None or Model.race.getCategory(h[c][rNext]) == self.category):
					SwapEntry( self, h[c][r], h[c][rNext] )
					break
			
	def OnPopupCorrect( self, event ):
		if hasattr(self, 'rowPopup'):
			CorrectNumber( self, self.history[self.colPopup][self.rowPopup] )
		
	def OnPopupSplit( self, event ):
		if hasattr(self, 'rowPopup'):
			SplitNumber( self, self.history[self.colPopup][self.rowPopup] )
		
	def OnPopupDelete( self, event ):
		if hasattr(self, 'rowPopup'):
			DeleteEntry( self, self.history[self.colPopup][self.rowPopup] )
		
	def OnPopupResults( self, event ):
		if Utils.isMainWin():
			Utils.getMainWin().showPageName( 'Results' )
			
	def OnPopupRiderDetail( self, event ):
		if Utils.isMainWin():
			Utils.getMainWin().showPageName( 'Rider Detail' )
		
	def onShowTimes( self, event ):
		self.showTimes = not self.showTimes
		self.refresh()
		
	def onShowLapTimes( self, event ):
		self.showLapTimes = not self.showLapTimes
		self.refresh()
		
	def onShowTimeDown( self, event ):
		self.showTimeDown = not self.showTimeDown
		self.refresh()
		
	def updateColours( self ):
		self.textColour = {}
		self.backgroundColour = {}
		for c in xrange(self.grid.GetNumberCols()):
			for r in xrange(self.grid.GetNumberRows()):
				value = self.grid.GetCellValue( r, c )
				if not value:
					break	
				
				cellNum = value.split('=')[0]
				if cellNum == self.numSelect:
					self.textColour[ (r,c) ] = self.whiteColour
					self.backgroundColour[ (r,c) ] = self.blackColour if (r,c) not in self.rcInterp else self.greyColour
				elif (r, c) in self.rcInterp:
					self.backgroundColour[ (r,c) ] = self.yellowColour
		
	def showNumSelect( self ):
		self.updateColours()
		self.grid.Set( textColour = self.textColour, backgroundColour = self.backgroundColour )
		self.grid.Reset()
	
	def doNumDrilldown( self, event ):
		self.doNumSelect( event )
		mainWin = Utils.getMainWin()
		if self.numSelect is not None and mainWin:
			mainWin.showPageName( 'Rider Detail' )
	
	def getCellNum( self, row, col ):
		numSelect = None
		if row < self.grid.GetNumberRows() and col < self.grid.GetNumberCols():
			value = self.grid.GetCellValue( row, col )
			if value is not None and value != '':
				numSelect = value.split('=')[0]
		return numSelect
	
	def doNumSelect( self, event ):
		if self.isEmpty:
			return
		numSelect = self.getCellNum(event.GetRow(), event.GetCol())
		if numSelect is not None:
			if self.numSelect != numSelect:
				self.numSelect = numSelect
				self.showNumSelect()
			if Utils.isMainWin():
				Utils.getMainWin().setNumSelect( numSelect )
	
	def doChooseCategory( self, event ):
		if Model.race is not None:
			Model.race.historyCategory = self.categoryChoice.GetSelection()
		self.refresh()
	
	def setCategoryAll( self ):
		FixCategories( self.categoryChoice, 0 )
		Model.race.historyCategory = 0
	
	def reset( self ):
		self.numSelect = None

	def setNumSelect( self, num ):
		self.numSelect = num if num is None else str(num)
		if self.numSelect:
			self.search.SetValue( self.numSelect )
	
	def clearGrid( self ):
		self.textColour = {}
		self.backgroundColour = {}
		self.grid.Set( data = [], colnames = [], textColour = {}, backgroundColour = {} )
		self.grid.Reset()
	
	def refresh( self ):
		self.isEmpty = True
		self.history = None
		self.category = None
		self.rcInterp = set()
		race = Model.race
		
		self.search.SelectAll()
		wx.CallAfter( self.search.SetFocus )
		
		if race is None:
			self.clearGrid()
			return

		catName = FixCategories( self.categoryChoice, getattr(race, 'historyCategory', 0) )
		self.hbs.Layout()

		maxLaps = race.numLaps
		doLapsToGo = True
		if maxLaps is None:
			maxLaps = race.getMaxLap()
			if race.isRunning():
				maxLaps += 2
			doLapsToGo = False
				
		entries = race.interpolateLap( maxLaps )
		
		# Collect the number and times for all entries so we can compute lap times.
		numTimes = {}
		for e in entries:
			if e.lap == 0:
				c = race.getCategory( e.num )
				try:
					startOffset = c.getStartOffsetSecs()
				except:
					startOffset = 0.0
				numTimes[(e.num, 0)] = startOffset
			else:
				numTimes[(e.num, e.lap)] = e.t
			
		# Trim out the 0 time starts.
		try:
			iFirstNonZero = (i for i, e in enumerate(entries) if e.t > 0).next()
			entries = entries[iFirstNonZero:]
		except StopIteration:
			self.clearGrid()
			return

		self.isEmpty = False
			
		# Organize all the entries into a grid as we would like to see them.
		self.history = [ [] ]
		numSeen = set()
		lapCur = 0
		for e in entries:
			if e.num in numSeen:
				numSeen.clear()
				lapCur += 1
				self.history.append( [] )
			self.history[lapCur].append( e )
			numSeen.add( e.num )
		
		colnames = []
		raceTime = 0
		for c, h in enumerate(self.history):
			lapTime = h[0].t - raceTime
			raceTime = h[0].t
			colnames.append( '%s\n%s\n%s\n%s' %(str(c+1),
												str(maxLaps - c - 1) if doLapsToGo else ' ',
												Utils.formatTime(lapTime),
												Utils.formatTime(raceTime)) )
		
		category = race.categories.get( catName, None )
		self.category = category
		if category is not None:
			def match( num ):
				return race.getCategory(num) == category
		else:
			def match( num ):
				return True
			
		leaderTimes, leaderNums = race.getLeaderTimesNums()
		
		formatStr = ['$num']
		if self.showTimes:		formatStr.append('=$raceTime')
		if self.showLapTimes:	formatStr.append(' [$lapTime]')
		if self.showTimeDown:	formatStr.append(' ($downTime)')
		template = Template( ''.join(formatStr) )
		
		data = []
		for col, h in enumerate(self.history):
			data.append( [ template.safe_substitute(
				{
					'num':		e.num,
					'raceTime':	Utils.formatTime(e.t) if self.showTimes else '',
					'lapTime':	Utils.formatTime(e.t - numTimes[(e.num,e.lap-1)]) if self.showLapTimes else '',
					'downTime':	Utils.formatTime(e.t - leaderTimes[col+1])
				} ) for e in h if match(e.num) ] )
			self.rcInterp.update( (row, col) for row, e in enumerate(h) if e.interp and match(e.num) )

		self.grid.Set( data = data, colnames = colnames )
		self.grid.AutoSizeColumns( True )
		self.grid.Reset()
		self.updateColours()
		self.grid.Set( textColour = self.textColour, backgroundColour = self.backgroundColour )
		self.grid.MakeCellVisible( 0, len(colnames)-1 )
		
		# Fix the grid's scrollbars.
		self.grid.FitInside()
	
	def commit( self ):
		pass
	
if __name__ == '__main__':
	#for x in dir(wx):
	#	if x.startswith('MOD_'):
	#		print x
	Utils.disable_stdout_buffering()
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	history = History(mainWin)
	history.refresh()
	mainWin.Show()
	app.MainLoop()
