import Model
import Utils
import wx
import wx.grid		as gridlib
import re
import os
import sys
import itertools
from string import Template
import ColGrid
from FixCategories import FixCategories, SetCategory
from GetResults import GetResults, RidersCanSwap
from ExportGrid import ExportGrid
from GetResults import GetResults
from EditEntry import CorrectNumber, ShiftNumber, InsertNumber, DeleteEntry, SwapEntry
from Undo import undo

reNonDigits = re.compile( '[^0-9]' )
reLapMatch = re.compile( '<?Lap>? ([0-9]+)' )

class Results( wx.Panel ):
	DisplayLapTimes = 0
	DisplayRaceTimes = 1
	DisplayLapSpeeds = 2
	DisplayRaceSpeeds = 3

	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		
		self.category = None
		self.showRiderData = True
		self.selectDisplay = 0
		self.firstDraw = True
		
		self.rcInterp = set()
		self.numSelect = None
		self.isEmpty = True
		self.reSplit = re.compile( '[\[\]\+= ]+' )	# seperators for the fields.
		self.iLap = None
		self.entry = None
		self.iRow, self.iCol = None, None
		self.iLastLap = 0
		self.fastestLapRC = None

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.showRiderDataToggle = wx.ToggleButton( self, wx.ID_ANY, 'Show Rider Data', style=wx.BU_EXACTFIT )
		self.showRiderDataToggle.SetValue( self.showRiderData )
		self.Bind( wx.EVT_TOGGLEBUTTON, self.onShowRiderData, self.showRiderDataToggle )
		
		self.showLapTimesRadio = wx.RadioButton( self, wx.ID_ANY, 'Lap Times', style=wx.BU_EXACTFIT|wx.RB_GROUP )
		self.showLapTimesRadio.SetValue( self.selectDisplay == Results.DisplayLapTimes )
		self.Bind( wx.EVT_RADIOBUTTON, self.onSelectDisplayOption, self.showLapTimesRadio )
		
		self.showRaceTimesRadio = wx.RadioButton( self, wx.ID_ANY, 'Race Times', style=wx.BU_EXACTFIT )
		self.showRaceTimesRadio.SetValue( self.selectDisplay == Results.DisplayRaceTimes )
		self.Bind( wx.EVT_RADIOBUTTON, self.onSelectDisplayOption, self.showRaceTimesRadio )
		
		self.showLapSpeedsRadio = wx.RadioButton( self, wx.ID_ANY, 'Lap Speeds', style=wx.BU_EXACTFIT )
		self.showLapSpeedsRadio.SetValue( self.selectDisplay == Results.DisplayLapSpeeds )
		self.Bind( wx.EVT_RADIOBUTTON, self.onSelectDisplayOption, self.showLapSpeedsRadio )
		
		self.showRaceSpeedsRadio = wx.RadioButton( self, wx.ID_ANY, 'Race Speeds', style=wx.BU_EXACTFIT )
		self.showRaceSpeedsRadio.SetValue( self.selectDisplay == Results.DisplayRaceSpeeds )
		self.Bind( wx.EVT_RADIOBUTTON, self.onSelectDisplayOption, self.showRaceSpeedsRadio )
		
		f = self.showLapTimesRadio.GetFont()
		self.boldFont = wx.Font( f.GetPointSize()+2, f.GetFamily(), f.GetStyle(),
								wx.FONTWEIGHT_BOLD, f.GetUnderlined(), f.GetFaceName(), f.GetEncoding() )
		
		self.search = wx.SearchCtrl(self, size=(80,-1), style=wx.TE_PROCESS_ENTER )
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
		self.hbs.Add( self.categoryChoice, flag=wx.ALL, border=4 )
		self.hbs.Add( self.showRiderDataToggle, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showLapTimesRadio, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showRaceTimesRadio, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showLapSpeedsRadio, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showRaceSpeedsRadio, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( wx.StaticText(self, wx.ID_ANY, ' '), proportion=2 )
		self.hbs.Add( self.search, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomInButton, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomOutButton, flag=wx.TOP | wx.BOTTOM | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border=4 )

		self.whiteColour = wx.Colour( 255, 255, 255 )
		self.blackColour = wx.Colour( 0, 0, 0 )
		self.yellowColour = wx.Colour( 255, 255, 0 )
		self.greyColour = wx.Colour( 150, 150, 150 )
		self.greenColour = wx.Colour( 127, 255, 0 )
		
		self.splitter = wx.SplitterWindow( self, wx.ID_ANY )
		
		self.labelGrid = ColGrid.ColGrid( self.splitter, style=wx.BORDER_SUNKEN )
		self.labelGrid.SetRowLabelSize( 0 )
		self.labelGrid.SetMargins( 0, 0 )
		self.labelGrid.SetRightAlign( True )
		self.labelGrid.SetDoubleBuffered( True )
		self.labelGrid.AutoSizeColumns( True )
		self.labelGrid.DisableDragColSize()
		self.labelGrid.DisableDragRowSize()
		
		self.lapGrid = ColGrid.ColGrid( self.splitter, style=wx.BORDER_SUNKEN )
		self.lapGrid.SetRowLabelSize( 0 )
		self.lapGrid.SetMargins( 0, 0 )
		self.lapGrid.SetRightAlign( True )
		self.lapGrid.SetDoubleBuffered( True )
		self.lapGrid.AutoSizeColumns( True )
		self.lapGrid.DisableDragColSize()
		self.lapGrid.DisableDragRowSize()
		
		self.splitter.SetMinimumPaneSize(100)
		self.splitter.SplitVertically(self.labelGrid, self.lapGrid, 400)
		
		# Sync the two vertical scrollbars.
		self.labelGrid.Bind(wx.EVT_SCROLLWIN, self.onScroll)
		self.lapGrid.Bind(wx.EVT_SCROLLWIN, self.onScroll)
		
		self.Bind( wx.grid.EVT_GRID_SELECT_CELL, self.doNumSelect )
		self.Bind( wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.doNumDrilldown )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doRightClick )
		self.lapGrid.Bind( wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.doLabelClick )
		self.labelGrid.Bind( wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.doLabelClick )
		
		bs = wx.BoxSizer(wx.VERTICAL)
		#bs.Add(self.hbs)
		#bs.Add(self.lapGrid, 1, wx.GROW|wx.ALL, 5)
		
		bs.Add(self.hbs, 0, wx.EXPAND )
		bs.Add(self.splitter, 1, wx.EXPAND|wx.GROW|wx.ALL, 5 )
		
		self.SetSizer(bs)
		bs.SetSizeHints(self)
	
	def onScroll(self, evt): 
		grid = evt.GetEventObject()
		orientation = evt.GetOrientation()
		if orientation == wx.SB_VERTICAL:
			if grid == self.lapGrid:
				wx.CallAfter( lambda: Utils.AlignVerticalScroll(self.lapGrid, self.labelGrid) ) 
			else:
				wx.CallAfter( lambda: Utils.AlignVerticalScroll(self.labelGrid, self.lapGrid) )
		evt.Skip() 
	
	def alignLabelToLapScroll(self): 
		Utils.AlignVerticalScroll( self.labelGrid, self.lapGrid )

	def alignLapToLabelScroll(self): 
		Utils.AlignVerticalScroll( self.lapGrid, self.labelGrid )
	
	def OnSearch( self, event ):
		self.OnDoSearch()
		
	def OnCancelSearch( self, event ):
		self.search.SetValue( '' )
		
	def OnDoSearch( self, event = None ):
		wx.CallAfter( self.search.SetFocus )
		n = self.search.GetValue()
		if n:
			n = reNonDigits.sub( '', n )
			self.search.SetValue( n )
		if not n:
			n = None
		if n:
			self.numSelect = n
			if self.category and not self.category.matches( int(n) ):
				self.setCategoryAll()

			self.refresh()
			if Utils.isMainWin():
				Utils.getMainWin().setNumSelect( n )

	def onZoomOut( self, event ):
		self.lapGrid.Zoom( False )
			
	def onZoomIn( self, event ):
		self.lapGrid.Zoom( True )
		
	def onShowRiderData( self, event ):
		self.showRiderData ^= True
		wx.CallAfter( self.refresh )
		
	def onSelectDisplayOption( self, event ):
		for i, r in enumerate([self.showLapTimesRadio, self.showRaceTimesRadio, self.showLapSpeedsRadio, self.showRaceSpeedsRadio]):
			if r.GetValue():
				self.selectDisplay = i
				break
		wx.CallAfter( self.refresh )
		
	def doLabelClick( self, event ):
		col = event.GetCol()
		label = self.lapGrid.GetColLabelValue(col)
		with Model.LockRace() as race:
			if event.GetEventObject() != self.lapGrid or label.startswith( '<' ) or not label.startswith('Lap'):
				setattr( race, 'sortLap', None )
			else:
				setattr( race, 'sortLap', int(label.split()[1]) )
		wx.CallAfter( self.refresh )
		
	def doRightClick( self, event ):
		wx.CallAfter( self.search.SetFocus )

		self.doNumSelect( event )
		if self.numSelect is None:
			return
			
		allCases = 0
		interpCase = 1
		nonInterpCase = 2
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				(wx.NewId(), 'History', 	'Switch to History tab', self.OnPopupHistory, allCases),
				(wx.NewId(), 'RiderDetail',	'Switch to RiderDetail tab', self.OnPopupRiderDetail, allCases),
				(None, None, None, None, None),
				(wx.NewId(), 'Correct...',	'Change number or lap time...',	self.OnPopupCorrect, interpCase),
				(wx.NewId(), 'Shift...',	'Move lap time earlier/later...',	self.OnPopupShift, interpCase),
				(wx.NewId(), 'Delete...',	'Delete lap time...',	self.OnPopupDelete, nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), 'Swap with Rider before',	'Swap with Rider before',	self.OnPopupSwapBefore, allCases),
				(wx.NewId(), 'Swap with Rider after',	'Swap with Rider after',	self.OnPopupSwapAfter, allCases),
			]
			for p in self.popupInfo:
				if p[0]:
					self.Bind( wx.EVT_MENU, p[3], id=p[0] )
		
		num = int(self.numSelect)
		with Model.LockRace() as race:
			if not race or num not in race:
				return
			entries = race.getRider(num).interpolate()
			catName = FixCategories( self.categoryChoice, getattr(race, 'resultsCategory', 0) )
			
		riderResults = dict( (r.num, r) for r in GetResults(catName) )
		
		try:
			self.entry = entries[self.iLap]
			caseCode = 1 if self.entry.interp else 2
		except (TypeError, IndexError, KeyError):
			caseCode = 0
	
		self.numBefore, self.numAfter = None, None
		for iRow, attr in [(self.iRow - 1, 'numBefore'), (self.iRow + 1, 'numAfter')]:
			if not (0 <= iRow < self.lapGrid.GetNumberRows()):
				continue
			numAdjacent = int( self.labelGrid.GetCellValue(iRow, 1) )
			if RidersCanSwap( riderResults, num, numAdjacent ):
				setattr( self, attr, numAdjacent )
			
		menu = wx.Menu()
		for id, name, text, callback, cCase in self.popupInfo:
			if not id:
				Utils.addMissingSeparator( menu )
				continue
			if caseCode >= cCase:
				if (name.endswith('before') and not self.numBefore) or (name.endswith('after') and not self.numAfter):
					continue
				menu.Append( id, name, text )
				
		Utils.deleteTrailingSeparators( menu )
		self.PopupMenu( menu )
		menu.Destroy()
		
	def OnPopupCorrect( self, event ):
		CorrectNumber( self, self.entry )
		
	def OnPopupShift( self, event ):
		ShiftNumber( self, self.entry )

	def OnPopupDelete( self, event ):
		DeleteEntry( self, self.entry )
	
	def swapEntries( self, num, numAdjacent ):
		if not num or not numAdjacent:
			return
		with Model.LockRace() as race:
			if (not race or
				num not in race or
				numAdjacent not in race ):
				return
			e1 = race.getRider(num).interpolate()
			e2 = race.getRider(numAdjacent).interpolate()
			catName = FixCategories( self.categoryChoice, getattr(race, 'resultsCategory', 0) )
			
		riderResults = dict( (r.num, r) for r in GetResults(catName) )
		try:
			laps = riderResults[num].laps
			undo.pushState()
			with Model.LockRace() as race:
				SwapEntry( e1[laps], e2[laps] )
			wx.CallAfter( self.refresh )
		except KeyError:
			pass
	
	def showLastLap( self ):
		if not self.isEmpty:
			self.iLastLap = max( min(self.lapGrid.GetNumberCols()-1, self.iLastLap), 0 )
			self.labelGrid.MakeCellVisible( 0, 0 )
			self.lapGrid.MakeCellVisible( 0, self.iLastLap )
	
	def OnPopupSwapBefore( self, event ):
		self.swapEntries( int(self.numSelect), self.numBefore )
		
	def OnPopupSwapAfter( self, event ):
		self.swapEntries( int(self.numSelect), self.numAfter )
	
	def OnPopupHistory( self, event ):
		if Utils.isMainWin():
			Utils.getMainWin().showPageName( 'History' )
			
	def OnPopupRiderDetail( self, event ):
		if Utils.isMainWin():
			Utils.getMainWin().showRiderDetail()
		
	def showNumSelect( self ):
		race = Model.race
		if race is None:
			return
			
		textColourLap = {}
		backgroundColourLap = dict( ((rc, self.yellowColour) for rc in self.rcInterp) )
		if self.fastestLapRC is not None:
			backgroundColourLap[self.fastestLapRC] = self.greenColour
		
		textColourLabel = {}
		backgroundColourLabel = {}
		
		for r in xrange(self.lapGrid.GetNumberRows()):
		
			value = self.labelGrid.GetCellValue( r, 1 )
			if not value:
				break	
			
			cellNum = value
			if cellNum == self.numSelect:
				for c in xrange(self.lapGrid.GetNumberCols()):
					textColourLap[ (r,c) ] = self.whiteColour
					backgroundColourLap[ (r,c) ] = self.blackColour if (r,c) not in self.rcInterp else self.greyColour
					
				for c in xrange(self.labelGrid.GetNumberCols()):
					textColourLabel[ (r,c) ] = self.whiteColour
					backgroundColourLabel[ (r,c) ] = self.blackColour if (r,c) not in self.rcInterp else self.greyColour
				break
		
		try:
			c = (i for i in xrange(self.lapGrid.GetNumberCols()) if self.lapGrid.GetColLabelValue(i).startswith('<')).next()
			for r in xrange(self.lapGrid.GetNumberRows()):
				textColourLap[ (r,c) ] = self.whiteColour
				backgroundColourLap[ (r,c) ] = self.blackColour if (r,c) not in self.rcInterp else self.greyColour
		except StopIteration:
			pass

		self.labelGrid.Set( textColour = textColourLabel, backgroundColour = backgroundColourLabel )
		self.labelGrid.Reset()
		self.lapGrid.Set( textColour = textColourLap, backgroundColour = backgroundColourLap )
		self.lapGrid.Reset()
			
	def doNumDrilldown( self, event ):
		self.doNumSelect( event )
		if self.numSelect is not None and Utils.isMainWin():
			Utils.getMainWin().showPageName( 'RiderDetail' )
	
	def doNumSelect( self, event ):
		self.iLap = None
		
		if self.isEmpty:
			return
		row, col = event.GetRow(), event.GetCol()
		self.iRow, self.iCol = row, col
		if row >= self.lapGrid.GetNumberRows() or col >= self.lapGrid.GetNumberCols():
			return
			
		if self.lapGrid.GetCellValue(row, col):
			try:
				colName = self.lapGrid.GetColLabelValue( col )
				self.iLap = int( reLapMatch.match(colName).group(1) )
			except:
				pass
		
		col = 1
		value = self.labelGrid.GetCellValue( row, col )
		numSelect = None
		if value:
			numSelect = value
		if self.numSelect != numSelect:
			self.numSelect = numSelect
			self.showNumSelect()
		mainWin = Utils.getMainWin()
		if mainWin:
			historyCategoryChoice = mainWin.history.categoryChoice
			historyCatName = FixCategories( historyCategoryChoice )
			if historyCatName and historyCatName != 'All':
				catName = FixCategories( self.categoryChoice )
				if historyCatName != catName:
					if Model.race:
						Model.race.resultsCategory = self.categoryChoice.GetSelection()
					SetCategory( historyCategoryChoice, catName )
			mainWin.setNumSelect( numSelect )
				
	def setCategoryAll( self ):
		FixCategories( self.categoryChoice, 0 )
		if Model.race:
			Model.race.resultsCategory = 0
	
	def doChooseCategory( self, event ):
		if Model.race:
			Model.race.resultsCategory = self.categoryChoice.GetSelection()
		self.refresh()
	
	def reset( self ):
		self.numSelect = None
	
	def setNumSelect( self, num ):
		self.numSelect = num if num is None else str(num)
		if self.numSelect:
			self.search.SetValue( self.numSelect )

	def clearGrid( self ):
		self.lapGrid.Set( data = [], colnames = [], textColour = {}, backgroundColour = {} )
		self.lapGrid.Reset()

	def refresh( self ):
		self.category = None
		self.isEmpty = True
		self.iLastLap = 0
		self.rcInterp = set()	# Set of row/col coordinates of interpolated numbers.
		
		self.search.SelectAll()
		wx.CallAfter( self.search.SetFocus )
		
		with Model.LockRace() as race:
			if not race:
				self.clearGrid()
				return
			catName = FixCategories( self.categoryChoice, getattr(race, 'resultsCategory', 0) )
			self.hbs.RecalcSizes()
			self.hbs.Layout()
			self.category = race.categories.get( catName, None )
			sortLap = getattr( race, 'sortLap', None )
		
		labelLastX, labelLastY = self.labelGrid.GetViewStart()
		lapLastX, lapLastY = self.lapGrid.GetViewStart()
		
		exportGrid = ExportGrid()
		exportGrid.setResultsOneList( catName, self.showRiderData )

		if not exportGrid.colnames:
			self.clearGrid()
			return
		
		# Fix the speed column.
		try:
			speedUnit = None
			iSpeedCol = (i for i, c in enumerate(exportGrid.colnames) if c == 'Speed').next()
			for r, d in enumerate(exportGrid.data[iSpeedCol]):
				if not d:
					continue
				if not speedUnit:
					exportGrid.colnames[iSpeedCol] = speedUnit = d.split()[1]
				exportGrid.data[iSpeedCol][r] = d.split()[0]
		except StopIteration:
			pass
			
		colnames = exportGrid.colnames
		data = exportGrid.data
		
		sortCol = None
		if sortLap:
			for i, name in enumerate(colnames):
				if name.startswith('Lap') and int(name.split()[1]) == sortLap:
					sortCol = i
					break
		
		results = GetResults( catName )
		hasSpeeds = False
		for result in results:
			if getattr(result, 'lapSpeeds', None) or getattr(result, 'raceSpeeds', None):
				hasSpeeds = True
				break
				
		if not hasSpeeds:
			self.showLapSpeedsRadio.Enable( False )
			self.showRaceSpeedsRadio.Enable( False )
			if self.selectDisplay > Results.DisplayRaceTimes:
				self.selectDisplay = Results.DisplayRaceTimes
				self.showRaceTimesRadio.SetValue( True )
		else:
			self.showLapSpeedsRadio.Enable( True )
			self.showRaceSpeedsRadio.Enable( True )
			
		for r in [self.showLapTimesRadio, self.showRaceTimesRadio, self.showLapSpeedsRadio, self.showRaceSpeedsRadio]:
			if r.GetValue():
				r.SetFont( self.boldFont )
			else:
				r.SetFont( wx.NullFont )
		self.hbs.RecalcSizes()
		self.hbs.Layout()
		
		# Find the fastest lap time.
		self.fastestLapRC, fastestLapTime = None, sys.float_info.max
		for r, result in enumerate(results):
			if result.lapTimes:
				for c, t in enumerate(result.lapTimes):
					if c > 0 and t < fastestLapTime:
						fastestLapTime = t
						self.fastestLapRC = (r, c-1)	# Correct by off-by-one problem.
		
		highPrecision = Utils.highPrecisionTimes()
		try:
			firstLapCol = (i for i, name in enumerate(colnames) if name.startswith('Lap')).next()
		except StopIteration:
			firstLapCol = len(colnames)
		
		# Convert to race times, lap speeds or race speeds as required.
		'''
			DisplayLapTimes = 0
			DisplayRaceTimes = 1
			DisplayLapSpeeds = 2
			DisplayRaceSpeeds = 3
		'''
		if self.selectDisplay == Results.DisplayRaceTimes:
			for r, result in enumerate(results):
				for i, t in enumerate(result.raceTimes[1:]):
					data[i+firstLapCol][r] = Utils.formatTime(t, highPrecision)
		elif self.selectDisplay == Results.DisplayLapSpeeds:
			for r, result in enumerate(results):
				if getattr(result, 'lapSpeeds', None):
					for i, t in enumerate(result.lapSpeeds[1:]):
						data[i+firstLapCol][r] = '%.2f' % t
		elif self.selectDisplay == Results.DisplayRaceSpeeds:
			for r, result in enumerate(results):
				if getattr(result, 'raceSpeeds', None):
					for i, t in enumerate(result.raceSpeeds[1:]):
						data[i+firstLapCol][r] = '%.2f' % t
		
		# Sort by the given lap, if there is one.
		# Also, add a position for the lap itself.
		if sortLap is not None:
			rowMax = len( results )
			sortPairs = []
			for r, result in enumerate(results):
				try:
					if   self.selectDisplay == Results.DisplayLapTimes:
						t = result.lapTimes[sortLap]
					elif self.selectDisplay == Results.DisplayRaceTimes:
						t = result.raceTimes[sortLap]
					elif self.selectDisplay == Results.DisplayLapSpeeds:
						t = -result.lapSpeeds[sortLap]
					elif self.selectDisplay == Results.DisplayRaceSpeeds:
						t = -result.raceSpeeds[sortLap]
				except:
					t = 1000.0*60.0*60.0 + r
				sortPairs.append( (t, r) )
			sortPairs.sort()
				
			for c in xrange(len(data)):
				col = data[c]
				data[c] = [col[i] if i < len(col) else '' for t, i in sortPairs]
				
			for r in xrange(len(data[sortLap])):
				if data[sortCol][r]:
					data[sortCol][r] += ' [%d: %s]' % (r+1, data[1][r])
		
		# Highlight the sorted column.
		if sortLap is not None:
			colnames = []
			for name in exportGrid.colnames:
				try:
					if int(name.split()[1]) == sortLap:
						name = '<%s>\n%s' % (name,
											['by Lap Time', 'by Race Time', 'by Lap Speed', 'by Race Speed'][self.selectDisplay])
				except:
					pass
				colnames.append( name )
		else:
			colnames = exportGrid.colnames
		
		try:
			iLabelMax = (i for i, name in enumerate(colnames) if name.startswith('Lap') or name.startswith('<')).next()
		except StopIteration:
			iLabelMax = len(colnames)
		colnamesLabels = colnames[:iLabelMax]
		dataLabels = data[:iLabelMax]
		
		colnameLaps = colnames[iLabelMax:]
		dataLaps = data[iLabelMax:]
		
		self.labelGrid.Set( data = dataLabels, colnames = colnamesLabels )
		self.labelGrid.SetLeftAlignCols( exportGrid.leftJustifyCols )
		self.labelGrid.AutoSizeColumns( True )
		self.labelGrid.Reset()
		
		self.lapGrid.Set( data = dataLaps, colnames = colnameLaps )
		self.lapGrid.AutoSizeColumns( True )
		self.lapGrid.Reset()
		
		self.isEmpty = False
		
		# Highlight interpolated entries.
		with Model.LockRace() as race:
			for r in xrange(self.lapGrid.GetNumberRows()):
				try:
					rider = race[int(self.labelGrid.GetCellValue(r, 1))]
					entries = rider.interpolate()
					if not entries:
						continue
				except (ValueError, IndexError):
					continue
				for c in xrange(self.lapGrid.GetNumberCols()):
					if not self.lapGrid.GetCellValue(r, c):
						break
					try:
						if entries[c+1].interp:
							self.rcInterp.add( (r, c) )
						elif c > self.iLastLap:
							self.iLastLap = c
					except IndexError:
						pass
		
		self.labelGrid.Scroll( labelLastX, labelLastY )
		self.lapGrid.Scroll( lapLastX, lapLastY )
		self.showNumSelect()
		
		if self.firstDraw:
			self.firstDraw = False
			self.splitter.SetSashPosition( 400 )
		
		# Fix the grids' scrollbars.
		self.labelGrid.FitInside()
		self.lapGrid.FitInside()

	def commit( self ):
		pass
		
if __name__ == '__main__':
	import cPickle as pickle
	Utils.disable_stdout_buffering()
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,200))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	results = Results(mainWin)
	results.refresh()
	mainWin.Show()
	app.MainLoop()
