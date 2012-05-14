import Model
import Utils
import wx
import wx.grid		as gridlib
import re
import os
import itertools
from string import Template
import ColGrid
from FixCategories import FixCategories, SetCategory
from GetResults import GetResults
from ExportGrid import ExportGrid
from EditEntry import CorrectNumber, ShiftNumber, InsertNumber, DeleteEntry, SwapEntry

reNonDigits = re.compile( '[^0-9]' )
reLapMatch = re.compile( 'Lap ([0-9]+)' )

class Results( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		
		self.category = None
		self.showRiderData = True
		
		self.rcInterp = set()
		self.numSelect = None
		self.isEmpty = True
		self.reSplit = re.compile( '[\[\]\+= ]+' )	# seperators for the fields.
		self.iLap = None
		self.entry = None
		self.iRow, self.iCol = None, None

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.showRiderDataToggle = wx.ToggleButton( self, wx.ID_ANY, 'Show Rider Data', style=wx.BU_EXACTFIT )
		self.showRiderDataToggle.SetValue( self.showRiderData )
		self.Bind( wx.EVT_TOGGLEBUTTON, self.onShowRiderData, self.showRiderDataToggle )
		
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
		self.hbs.Add( wx.StaticText(self, wx.ID_ANY, ' '), proportion=2 )
		self.hbs.Add( self.search, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomInButton, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomOutButton, flag=wx.TOP | wx.BOTTOM | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border=4 )

		self.whiteColour = wx.Colour( 255, 255, 255 )
		self.blackColour = wx.Colour( 0, 0, 0 )
		self.yellowColour = wx.Colour( 255, 255, 0 )
		self.greyColour = wx.Colour( 150, 150, 150 )
		
		self.grid = ColGrid.ColGrid( self )
		self.grid.SetRowLabelSize( 0 )
		self.grid.SetMargins( 0, 0 )
		self.grid.SetRightAlign( True )
		#self.grid.SetDoubleBuffered( True )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()
		
		self.Bind( wx.grid.EVT_GRID_SELECT_CELL, self.doNumSelect )
		self.Bind( wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.doNumDrilldown )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doRightClick )
		
		bs = wx.BoxSizer(wx.VERTICAL)
		#bs.Add(self.hbs)
		#bs.Add(self.grid, 1, wx.GROW|wx.ALL, 5)
		
		bs.Add(self.hbs, 0, wx.EXPAND )
		bs.Add(self.grid, 1, wx.EXPAND|wx.GROW|wx.ALL, 5 )
		
		self.SetSizer(bs)
		bs.SetSizeHints(self)
		
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
		self.grid.Zoom( False )
			
	def onZoomIn( self, event ):
		self.grid.Zoom( True )
		
	def onShowRiderData( self, event ):
		self.showRiderData ^= True
		self.refresh()
		
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
				(None, None, None, None),
				(wx.NewId(), 'Correct...',	'Change number or lap time...',	self.OnPopupCorrect, interpCase),
				(wx.NewId(), 'Shift...',	'Move lap time earlier/later...',	self.OnPopupShift, interpCase),
				(wx.NewId(), 'Delete...',	'Delete lap time...',	self.OnPopupDelete, nonInterpCase),
				(None, None, None, None),
				(wx.NewId(), 'Swap with Rider before',	'Swap with Rider before',	self.OnPopupSwapBefore, nonInterpCase),
				(wx.NewId(), 'Swap with Rider after',	'Swap with Rider after',	self.OnPopupSwapAfter, nonInterpCase),
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
			showSeparators = True
		except (TypeError, IndexError, KeyError):
			caseCode = 0
			showSeparators = False
	
		self.numBefore, self.numAfter = None, None
		with Model.LockRace() as race:
			for iRow, attr in [(self.iRow - 1, 'numBefore'), (self.iRow + 1, 'numAfter')]:
				if 0 <= iRow < self.grid.GetNumberRows():
					try:
						numAdjacent = int( self.grid.GetCellValue(iRow, 1) )
						rr1 = riderResults[num]
						rr2 = riderResults[numAdjacent]
						if (rr1.status != Model.Rider.Finisher or
							rr2.status != Model.Rider.Finisher or
							rr1.laps != rr2.laps ):
							continue
						# Check if swapping the last times would result in race times out of order.
						rt1 = [e.t for e in race.getRider(num).interpolate()]
						rt2 = [e.t for e in race.getRider(numAdjacent).interpolate()]
						rt1[rr1.laps], rt2[rr1.laps] = rt2[rr1.laps], rt1[rr1.laps]
						if 	all( x < y for x, y in itertools.izip(rt1, rt1[1:]) ) and \
							all( x < y for x, y in itertools.izip(rt2, rt2[1:]) ):
							setattr( self, attr, numAdjacent )
					except (IndexError, ValueError, KeyError):
						pass
			
		menu = wx.Menu()
		for i, p in enumerate(self.popupInfo):
			if not p[0]:
				if showSeparators:
					menu.AppendSeparator()
				continue
			if caseCode >= p[4]:
				if (p[1].endswith('before') and not self.numBefore) or (p[1].endswith('after') and not self.numAfter):
					continue
				menu.Append( p[0], p[1], p[2] )
		
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
			with Model.LockRace() as race:
				SwapEntry( e1[laps], e2[laps] )
			wx.CallAfter( self.refresh )
		except KeyError:
			pass
	
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
			
		textColour = {}
		backgroundColour = dict( ((rc, self.yellowColour) for rc in self.rcInterp) )
		for r in xrange(self.grid.GetNumberRows()):
		
			value = self.grid.GetCellValue( r, 1 )
			if not value:
				break	
			
			cellNum = value
			if cellNum == self.numSelect:
				for c in xrange(self.grid.GetNumberCols()):
					textColour[ (r,c) ] = self.whiteColour
					backgroundColour[ (r,c) ] = self.blackColour if (r,c) not in self.rcInterp else self.greyColour
					
				self.grid.MakeCellVisible( r, 0 )
				break
					
		self.grid.Set( textColour = textColour, backgroundColour = backgroundColour )
		self.grid.Reset()
			
	def doNumDrilldown( self, event ):
		self.doNumSelect( event )
		if self.numSelect is not None and Utils.isMainWin():
			Utils.getMainWin().showPageName( 'History' )
	
	def doNumSelect( self, event ):
		self.iLap = None
		
		if self.isEmpty:
			return
		row, col = event.GetRow(), event.GetCol()
		self.iRow, self.iCol = row, col
		if row >= self.grid.GetNumberRows() or col >= self.grid.GetNumberCols():
			return
			
		if self.grid.GetCellValue(row, col):
			try:
				colName = self.grid.GetColLabelValue( col )
				self.iLap = int( reLapMatch.match(colName).group(1) )
			except:
				pass
		
		col = 1
		value = self.grid.GetCellValue( row, col )
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
		self.grid.Set( data = [], colnames = [], textColour = {}, backgroundColour = {} )
		self.grid.Reset()

	def refresh( self ):
		self.category = None
		self.isEmpty = True
		self.rcInterp = set()	# Set of row/col coordinates of interpolated numbers.
		
		self.search.SelectAll()
		wx.CallAfter( self.search.SetFocus )
		
		with Model.LockRace() as race:
			if not race:
				self.clearGrid()
				return
			catName = FixCategories( self.categoryChoice, getattr(race, 'resultsCategory', 0) )
			self.hbs.Layout()
			self.category = race.categories.get( catName, None )
		
		exportGrid = ExportGrid()
		exportGrid.setResultsOneList( catName, self.showRiderData )

		if not exportGrid.colnames:
			self.clearGrid()
			return
			
		self.grid.Set( data = exportGrid.data, colnames = exportGrid.colnames )
		self.grid.SetLeftAlignCols( exportGrid.leftJustifyCols )
		self.grid.AutoSizeColumns( True )
		self.grid.Reset()
		self.isEmpty = False

		# Highlight interpolated entries.
		with Model.LockRace() as race:
			for r in xrange(self.grid.GetNumberRows()):
				try:
					rider = race[int(self.grid.GetCellValue(r, 1))]
					entries = rider.interpolate()
					if not entries:
						continue
				except (ValueError, IndexError):
					continue
				eItr = (e for e in entries)
				eItr.next()						# Skip the first zero entry.
				for c in xrange(exportGrid.iLapTimes, self.grid.GetNumberCols()):
					if not self.grid.GetCellValue(r, c):
						break
					if eItr.next().interp:
						self.rcInterp.add( (r, c) )
		
		self.grid.MakeCellVisible( 0, 0 )
		self.showNumSelect()
						
		# Fix the grid's scrollbars.
		self.grid.FitInside()

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
