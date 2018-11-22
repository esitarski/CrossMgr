import wx
import re
import os
import sys
import Model
import Utils
import ColGrid
from collections import defaultdict
from FixCategories import FixCategories, SetCategory
from GetResults import GetResults, RidersCanSwap
from ExportGrid import ExportGrid
from RiderDetail import ShowRiderDetailDialog
from EditEntry import CorrectNumber, ShiftNumber, InsertNumber, DeleteEntry, SwapEntry
from Undo import undo
import Flags

bitmapCache = {}
class IOCCodeRenderer(wx.grid.GridCellRenderer):
	def __init__(self):
		super( IOCCodeRenderer, self ).__init__()

	def getImgWidth( self, ioc, height ):
		img = Flags.GetFlagImage( ioc )
		if img:
			imgHeight = int( height * 0.8 )
			imgWidth = int( float(img.GetWidth()) / float(img.GetHeight()) * float(imgHeight) )
			padding = int(height * 0.1)
			return img, imgWidth, imgHeight, padding
		return None, 0, 0, 0

	def Draw(self, grid, attr, dc, rect, row, col, isSelected):
		text = grid.GetCellValue(row, col)

		dc.SetFont( attr.GetFont() )
		w, h = dc.GetTextExtent( text )
		
		ioc = text[:3]
		img, imgWidth, imgHeight, padding = self.getImgWidth(ioc, h)
		
		fg = attr.GetTextColour()
		bg = attr.GetBackgroundColour()
		if isSelected:
			fg, bg = bg, fg
		
		dc.SetBrush( wx.Brush(bg, wx.SOLID) )
		dc.SetPen( wx.TRANSPARENT_PEN )
		dc.DrawRectangle( rect )

		rectText = wx.Rect( rect.GetX()+padding+imgWidth, rect.GetY(), rect.GetWidth()-padding-imgWidth, rect.GetHeight() )
		
		hAlign, vAlign = attr.GetAlignment()
		dc.SetTextForeground( fg )
		dc.SetTextBackground( bg )
		grid.DrawTextRectangle(dc, text, rectText, hAlign, vAlign)

		if img:
			key = (ioc, imgHeight)
			if key not in bitmapCache:
				bitmapCache[key] = img.Scale(imgWidth, imgHeight, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
			dc.DrawBitmap( bitmapCache[key], rect.GetX(), rect.GetY()+(rect.GetHeight()-imgHeight)//2 )

	def GetBestSize(self, grid, attr, dc, row, col):
		text = grid.GetCellValue(row, col)
		dc.SetFont(attr.GetFont())
		w, h = dc.GetTextExtent( text )
		
		img, imgWidth, imgHeight, padding = self.getImgWidth(text[:3], h)
		if img:
			return wx.Size(w + imgWidth + padding, h)
		else:
			return wx.Size(w, h)

	def Clone(self):
		return IOCCodeRenderer()

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
		self.rcNumTime = set()
		self.numSelect = None
		self.isEmpty = True
		self.reSplit = re.compile( '[\[\]\+= ]+' )	# separators for the fields.
		self.iLap = None
		self.entry = None
		self.iRow, self.iCol = None, None
		self.iLastLap = 0
		self.fastestLapRC = None

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, label = _('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.showRiderDataToggle = wx.ToggleButton( self, label = _('Show Rider Data'), style=wx.BU_EXACTFIT )
		self.showRiderDataToggle.SetValue( self.showRiderData )
		self.Bind( wx.EVT_TOGGLEBUTTON, self.onShowRiderData, self.showRiderDataToggle )
		
		self.showLapTimesRadio = wx.RadioButton( self, label = _('Lap Times'), style=wx.BU_EXACTFIT|wx.RB_GROUP )
		self.showLapTimesRadio.SetValue( self.selectDisplay == Results.DisplayLapTimes )
		self.Bind( wx.EVT_RADIOBUTTON, self.onSelectDisplayOption, self.showLapTimesRadio )
		self.showLapTimesRadio.SetToolTip(wx.ToolTip(_('Useful for finding the fastest lap.')))
		
		self.showRaceTimesRadio = wx.RadioButton( self, label = _('Race Times'), style=wx.BU_EXACTFIT )
		self.showRaceTimesRadio.SetValue( self.selectDisplay == Results.DisplayRaceTimes )
		self.Bind( wx.EVT_RADIOBUTTON, self.onSelectDisplayOption, self.showRaceTimesRadio )
		self.showRaceTimesRadio.SetToolTip(wx.ToolTip(_('Useful for finding for Prime winners.\nAfter selecting, click on a lap header to sort.')))
		
		self.showLapSpeedsRadio = wx.RadioButton( self, label = _('Lap Speeds'), style=wx.BU_EXACTFIT )
		self.showLapSpeedsRadio.SetValue( self.selectDisplay == Results.DisplayLapSpeeds )
		self.Bind( wx.EVT_RADIOBUTTON, self.onSelectDisplayOption, self.showLapSpeedsRadio )
		self.showLapSpeedsRadio.SetToolTip(wx.ToolTip(_('Useful for finding the fastest lap.')))
		
		self.showRaceSpeedsRadio = wx.RadioButton( self, label = _('Race Speeds'), style=wx.BU_EXACTFIT )
		self.showRaceSpeedsRadio.SetValue( self.selectDisplay == Results.DisplayRaceSpeeds )
		self.Bind( wx.EVT_RADIOBUTTON, self.onSelectDisplayOption, self.showRaceSpeedsRadio )
		self.showRaceSpeedsRadio.SetToolTip(wx.ToolTip(_("Useful to predict how long a race will take based on rider's average speed.")))
		
		f = self.showLapTimesRadio.GetFont()
		self.boldFont = wx.Font( f.GetPointSize()+2, f.GetFamily(), f.GetStyle(), wx.FONTWEIGHT_BOLD, f.GetUnderlined() )
		
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
		self.hbs.AddStretchSpacer()
		self.hbs.Add( self.search, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomInButton, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomOutButton, flag=wx.TOP | wx.BOTTOM | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border=4 )

		self.whiteColour = wx.Colour( 255, 255, 255 )
		self.blackColour = wx.Colour( 0, 0, 0 )
		self.yellowColour = wx.Colour( 255, 255, 0 )
		self.orangeColour = wx.Colour( 255, 165, 0 )
		self.greyColour = wx.Colour( 150, 150, 150 )
		self.greenColour = wx.Colour( 127, 255, 0 )
		self.lightBlueColour = wx.Colour( 153, 205, 255 )
		
		self.splitter = wx.SplitterWindow( self )
		
		self.labelGrid = ColGrid.ColGrid( self.splitter, style=wx.BORDER_SUNKEN )
		self.labelGrid.SetRowLabelSize( 0 )
		self.labelGrid.SetMargins( 0, 0 )
		self.labelGrid.SetRightAlign( True )
		self.labelGrid.AutoSizeColumns( True )
		self.labelGrid.DisableDragColSize()
		self.labelGrid.DisableDragRowSize()
		# put a tooltip on the cells in a column
		self.labelGrid.GetGridWindow().Bind(wx.EVT_MOTION, self.onMouseOver)
		
		self.lapGrid = ColGrid.ColGrid( self.splitter, style=wx.BORDER_SUNKEN )
		self.lapGrid.SetRowLabelSize( 0 )
		self.lapGrid.SetMargins( 0, 0 )
		self.lapGrid.SetRightAlign( True )
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
		
		self.SetDoubleBuffered( True )
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
	
	def onMouseOver( self, event ):
		"""
		Displays a tooltip for the close finishes.
		"""
		x, y = self.labelGrid.CalcUnscrolledPosition(event.GetX(),event.GetY())
		row, col = self.labelGrid.XYToCell(x, y)
		
		try:
			num = int(self.labelGrid.GetCellValue(row, 1))
		except:
			return

		if num in self.closeFinishBibs:
			try:
				pos = int(self.labelGrid.GetCellValue(row, 0))
			except:
				return
			event.GetEventObject().SetToolTip(u'{} {}, {} {}: {} {}'.format(
					_('Pos'), pos,
					_('Bib'), num,
					_('close finish to'), u','.join( u'{} {}'.format(_('Bib'), bib) for bib in self.closeFinishBibs[num]),
				)
			)
		else:
			event.GetEventObject().SetToolTip(u'')
	
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
		self.labelGrid.Zoom( False )
		self.lapGrid.Zoom( False )
		self.splitter.UpdateSize()
		wx.CallAfter( self.refresh )
			
	def onZoomIn( self, event ):
		self.labelGrid.Zoom( True )
		self.lapGrid.Zoom( True )
		self.splitter.UpdateSize()
		wx.CallAfter( self.refresh )
		
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
		with Model.LockRace() as race:
			race.sortLap = None
			race.sortLabel = None
			if event.GetEventObject() == self.lapGrid:
				label = self.lapGrid.GetColLabelValue( col )
				if label.startswith( _('Lap') ):
					race.sortLap = int(label.split()[1])
			else:
				label = self.labelGrid.GetColLabelValue( col )
				if label[:1] != u'<':
					race.sortLabel = label
		
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
				(_('Passings'), 	_('Switch to Passings tab'), self.OnPopupHistory, allCases),
				(_('RiderDetail'),	_('Show RiderDetail Dialog'), self.OnPopupRiderDetail, allCases),
				(None, None, None, None),
				(_('Show Photos'),	_('Show Photos'), self.OnPopupShowPhotos, allCases),
				(None, None, None, None),
				(_('Correct...'),	_('Change number or lap time...'),	self.OnPopupCorrect, interpCase),
				(_('Shift...'),	_('Move lap time earlier/later...'),	self.OnPopupShift, interpCase),
				(_('Delete...'),	_('Delete lap time...'),	self.OnPopupDelete, nonInterpCase),
				(None, None, None, None),
				(_('Swap with Rider before'),	_('Swap with Rider before'),	self.OnPopupSwapBefore, allCases),
				(_('Swap with Rider after'),	_('Swap with Rider after'),	self.OnPopupSwapAfter, allCases),
			]

			self.menuOptions = {}
			for numBefore in [False, True]:
				for numAfter in [False, True]:
					for caseCode in xrange(3):
						menu = wx.Menu()
						for name, text, callback, cCase in self.popupInfo:
							if not name:
								Utils.addMissingSeparator( menu )
								continue
							if caseCode < cCase:
								continue
							if (name.endswith(_('before')) and not numBefore) or (name.endswith(_('after')) and not numAfter):
								continue
							item = menu.Append( wx.ID_ANY, name, text )
							self.Bind( wx.EVT_MENU, callback, item )
					
						Utils.deleteTrailingSeparators( menu )
						self.menuOptions[(numBefore,numAfter,caseCode)] = menu
		
		num = int(self.numSelect)
		with Model.LockRace() as race:
			if not race or num not in race.riders:
				return
			category = FixCategories( self.categoryChoice, getattr(race, 'resultsCategory', 0) )
			
		riderResults = dict( (r.num, r) for r in GetResults(category) )
		
		entries = race.riders[num].interpolate()
		try:
			laps = riderResults[num].laps
			self.entry = next(e for e in entries if e.t == riderResults[num].raceTimes[laps])
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
			
		menu = self.menuOptions[(self.numBefore is not None, self.numAfter is not None, caseCode)]
		try:
			self.PopupMenu( menu )
		except Exception as e:
			Utils.writeLog( 'Results:doRightClick: {}'.format(e) )
		
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
				num not in race.riders or
				numAdjacent not in race ):
				return
			e1 = race.getRider(num).interpolate()
			e2 = race.getRider(numAdjacent).interpolate()
			category = FixCategories( self.categoryChoice, getattr(race, 'resultsCategory', 0) )
			
		riderResults = dict( (r.num, r) for r in GetResults(category) )
		try:
			rr1, rr2 = riderResults[num], riderResults[numAdjacent]
			laps = rr1.laps
			undo.pushState()
			ee1 = next( e for e in e1 if e.t == rr1.raceTimes[laps] )
			ee2 = next( e for e in e2 if e.t == rr2.raceTimes[laps] )
			with Model.LockRace() as race:
				SwapEntry( ee1, ee2 )
			wx.CallAfter( self.refresh )
		except KeyError, StopIteration:
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
			Utils.getMainWin().showPageName( _('Passings') )
			
	def OnPopupRiderDetail( self, event ):
		ShowRiderDetailDialog( self, self.numSelect )
		
	def OnPopupShowPhotos( self, event ):
		mainWin = Utils.mainWin
		if not mainWin:
			return
		mainWin.photoDialog.Show( True )
		mainWin.photoDialog.setNumSelect( int(self.numSelect) )
		
	def showNumSelect( self ):
		race = Model.race
		if race is None:
			return
			
		try:
			numSelectSearch = int(self.numSelect)
		except (TypeError, ValueError):
			numSelectSearch = None
		
		textColourLap = {}
		backgroundColourLap = dict( ((rc, self.yellowColour) for rc in self.rcInterp) )
		backgroundColourLap.update( dict( ((rc, self.orangeColour) for rc in self.rcNumTime) ) )
		if self.fastestLapRC is not None:
			backgroundColourLap[self.fastestLapRC] = self.greenColour
		
		textColourLabel = {}
		backgroundColourLabel = {}
		
		timeCol = None
		for c in xrange(self.labelGrid.GetNumberCols()):
			if self.labelGrid.GetColLabelValue(c) == _('Time'):
				timeCol = c
				break
		
		for r in xrange(self.lapGrid.GetNumberRows()):		
			try:
				cellNum = int(self.labelGrid.GetCellValue(r,1))
			except:
				continue
			
			if cellNum == numSelectSearch:
				for c in xrange(self.labelGrid.GetNumberCols()):
					textColourLabel[ (r,c) ] = self.whiteColour
					backgroundColourLabel[ (r,c) ] = self.blackColour

				for c in xrange(self.lapGrid.GetNumberCols()):
					textColourLap[ (r,c) ] = self.whiteColour
					backgroundColourLap[ (r,c) ] = self.blackColour if (r,c) not in self.rcInterp and (r,c) not in self.rcNumTime else self.greyColour
					
			if cellNum in self.closeFinishBibs:
				textColourLabel[ (r,0) ] = self.blackColour
				backgroundColourLabel[ (r,0) ] = self.lightBlueColour
				if timeCol is not None:
					textColourLabel[ (r,timeCol) ] = self.blackColour
					backgroundColourLabel[ (r,timeCol) ] = self.lightBlueColour
		
		# Highlight the sorted columns.
		for c in xrange(self.lapGrid.GetNumberCols()):
			if self.lapGrid.GetColLabelValue(c).startswith('<'):
				for r in xrange(self.lapGrid.GetNumberRows()):
					textColourLap[ (r,c) ] = self.whiteColour
					backgroundColourLap[ (r,c) ] = self.blackColour \
						if (r,c) not in self.rcInterp and (r,c) not in self.rcNumTime else self.greyColour
				break
			
		for c in xrange(self.labelGrid.GetNumberCols()):
			if self.labelGrid.GetColLabelValue(c).startswith('<'):
				for r in xrange(self.labelGrid.GetNumberRows()):
					textColourLabel[ (r,c) ] = self.whiteColour
					backgroundColourLabel[ (r,c) ] = self.blackColour
				break

		self.labelGrid.Set( textColour=textColourLabel, backgroundColour=backgroundColourLabel )
		self.lapGrid.Set( textColour=textColourLap, backgroundColour=backgroundColourLap )
		self.labelGrid.Reset()
		self.lapGrid.Reset()
			
	def doNumDrilldown( self, event ):
		self.doNumSelect( event )
		mainWin = Utils.getMainWin()
		if self.numSelect is not None and mainWin:
			ShowRiderDetailDialog( self, self.numSelect )
	
	def doNumSelect( self, event ):
		grid = event.GetEventObject()
		self.iLap = None
		
		if self.isEmpty:
			return
		row, col = event.GetRow(), event.GetCol()
		self.iRow, self.iCol = row, col
		if row >= self.labelGrid.GetNumberRows():
			return
			
		if grid == self.lapGrid and self.lapGrid.GetCellValue(row, col):
			try:
				colName = self.lapGrid.GetColLabelValue( col )
				self.iLap = int( reLapMatch.match(colName).group(1) )
			except:
				pass
		
		value = self.labelGrid.GetCellValue( row, 1 )
		numSelect = value if value else None
		if self.numSelect != numSelect:
			self.numSelect = numSelect
			self.showNumSelect()
		mainWin = Utils.getMainWin()
		if mainWin:
			historyCategoryChoice = mainWin.history.categoryChoice
			historyCat = FixCategories( historyCategoryChoice )
			if historyCat is not None:
				cat = FixCategories( self.categoryChoice )
				if historyCat != cat:
					Model.setCategoryChoice( self.categoryChoice.GetSelection(), 'resultsCategory' )
					SetCategory( historyCategoryChoice, cat )
			mainWin.setNumSelect( numSelect )
				
	def setCategoryAll( self ):
		FixCategories( self.categoryChoice, 0 )
		Model.setCategoryChoice( 0, 'resultsCategory' )
	
	def setCategory( self, category ):
		for i, c in enumerate(Model.race.getCategories( startWaveOnly=False ) if Model.race else [], 1):
			if c == category:
				SetCategory( self.categoryChoice, c )
				Model.setCategoryChoice( i, 'resultsCategory' )
				return
		SetCategory( self.categoryChoice, None )
		Model.setCategoryChoice( 0, 'resultsCategory' )
	
	def doChooseCategory( self, event ):
		Model.setCategoryChoice( self.categoryChoice.GetSelection(), 'resultsCategory' )
		self.refresh()
	
	def reset( self ):
		self.numSelect = None
	
	def setNumSelect( self, num ):
		self.numSelect = num if num is None else u'{}'.format(num)
		if self.numSelect:
			self.search.SetValue( self.numSelect )

	def clearGrid( self ):
		self.labelGrid.Set( data = [], colnames = [], textColour = {}, backgroundColour = {} )
		self.labelGrid.Reset()
		self.lapGrid.Set( data = [], colnames = [], textColour = {}, backgroundColour = {} )
		self.lapGrid.Reset()

	def refresh( self ):
		self.category = None
		self.isEmpty = True
		self.iLastLap = 0
		self.rcInterp = set()	# Set of row/col coordinates of interpolated numbers.
		self.rcNumTime = set()
		
		self.search.SelectAll()
		
		CloseFinishTime = 0.07
		self.closeFinishBibs = defaultdict( list )
		
		race = Model.race
		if not race:
			self.clearGrid()
			return
		category = FixCategories( self.categoryChoice, getattr(race, 'resultsCategory', 0) )
		self.hbs.RecalcSizes()
		self.hbs.Layout()
		for si in self.hbs.GetChildren():
			if si.IsWindow():
				si.GetWindow().Refresh()
		self.category = category
		sortLap = getattr( race, 'sortLap', None )
		sortLabel = getattr( race, 'sortLabel', None )

		if race.isTimeTrial:
			def getSortTime( rr ):
				try:
					return rr.firstTime + rr._lastTimeOrig
				except:
					return 0
		else:
			def getSortTime( rr ):
				try:
					return rr._lastTimeOrig
				except:
					return 0
					
		results = sorted(
			(rr for rr in GetResults(category)
				if rr.status==Model.Rider.Finisher and rr.lapTimes and getSortTime(rr) > 0),
			key = getSortTime
		)
		for i in xrange(1, len(results)):
			if results[i]._lastTimeOrig - results[i-1]._lastTimeOrig <= CloseFinishTime:
				self.closeFinishBibs[results[i-1].num].append( results[i].num )
				self.closeFinishBibs[results[i].num].append( results[i-1].num )
		
		labelLastX, labelLastY = self.labelGrid.GetViewStart()
		lapLastX, lapLastY = self.lapGrid.GetViewStart()
		
		exportGrid = ExportGrid()
		exportGrid.setResultsOneList( category, self.showRiderData, showLapsFrequency = 1 )
		
		if not exportGrid.colnames:
			self.clearGrid()
			return

		# Fix the speed column.
		speedUnit = None
		iSpeedCol = None
		try:
			iSpeedCol = (i for i, c in enumerate(exportGrid.colnames) if c == _('Speed')).next()
		except StopIteration:
			pass
		if iSpeedCol is not None:
			for r, d in enumerate(exportGrid.data[iSpeedCol]):
				d = d.strip()
				if not d:
					continue
				dSplit = d.split()
				if not speedUnit and len(dSplit) > 1:
					exportGrid.colnames[iSpeedCol] = speedUnit = dSplit[1]
				exportGrid.data[iSpeedCol][r] = dSplit[0]
				if exportGrid.data[iSpeedCol][r] == '"':
					exportGrid.data[iSpeedCol][r] += '    '
			
		colnames = exportGrid.colnames
		data = exportGrid.data
		
		sortCol = None
		if sortLap:
			race.sortLabel = sortLabel = None
			for i, name in enumerate(colnames):
				if name.startswith(_('Lap')) and int(name.split()[1]) == sortLap:
					sortCol = i
					break
		elif sortLabel:
			race.sortLap = sortLap = None
			if sortLabel not in {_('Pos'), _('Gap'), _('Time'), _('mph'), _('km/h')}:
				for i, name in enumerate(colnames):
					if name == sortLabel:
						sortCol = i
						break
		if sortCol is None:
			race.sortLabel = race.sortLap = sortLabel = sortLap = None
		
		results = GetResults( category )
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
		self.fastestLapRC, fastestLapSpeed, fastestLapTime = None, 0.0, sys.float_info.max
		for r, result in enumerate(results):
			if getattr(result, 'lapSpeeds', None):			# Use speeds if available.
				for c, s in enumerate(result.lapSpeeds):
					if s > fastestLapSpeed:
						fastestLapSpeed = s
						self.fastestLapRC = (r, c)
			elif result.lapTimes:							# Else, use times.
				for c, t in enumerate(result.lapTimes):
					if t < fastestLapTime:
						fastestLapTime = t
						self.fastestLapRC = (r, c)
		
		highPrecision = Model.highPrecisionTimes()
		try:
			firstLapCol = (i for i, name in enumerate(colnames) if name.startswith(_('Lap'))).next()
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
					try:
						data[i+firstLapCol][r] = Utils.formatTimeCompressed(t, highPrecision)
					except IndexError:
						pass
		elif self.selectDisplay == Results.DisplayLapSpeeds:
			for r, result in enumerate(results):
				if getattr(result, 'lapSpeeds', None):
					for i, s in enumerate(result.lapSpeeds):
						try:
							data[i+firstLapCol][r] = u'{:.2f}'.format(s)
						except IndexError:
							pass
		elif self.selectDisplay == Results.DisplayRaceSpeeds:
			for r, result in enumerate(results):
				if getattr(result, 'raceSpeeds', None):
					for i, s in enumerate(result.raceSpeeds):
						try:
							data[i+firstLapCol][r] = u'{:.2f}'.format(s)
						except IndexError:
							pass
		
		# Sort by the given lap, if there is one.
		# Also, add a position for the lap itself.
		if sortCol is not None:
			maxVal = 1000.0*24.0*60.0*60.0
			if sortLap:
				if self.selectDisplay in [Results.DisplayLapTimes, Results.DisplayRaceTimes]:
					getFunc = Utils.StrToSeconds
				else:
					getFunc = lambda x: -float(x)
			else:
				if colnames[sortCol] in [_('Start'), _('Finish'), _('Time')]:
					getFunc = Utils.StrToSeconds
				elif colnames[sortCol] in [_('mph'), _('km')]:
					getFunc = lambda x: -float(x) if x else 0.0
				elif colnames[sortCol] == _('Factor'):
					getFunc = lambda x: float(x) if x else maxVal
				elif colnames[sortCol] in [_('Pos'), _('Bib')]:
					getFunc = lambda x: int(x) if x and unicode(x).isdigit() else maxVal
				else:
					getFunc = lambda x: u'{}'.format(x)
					maxVal = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
			sortPairs = []
			for r, result in enumerate(results):
				try:
					k = (getFunc(data[sortCol][r]), r)
				except Exception as e:
					k = (maxVal, r)
				sortPairs.append( (k, r) )
			sortPairs.sort()
			
			for c in xrange(len(data)):
				col = data[c]
				data[c] = [col[i] if i < len(col) else u'' for k, i in sortPairs]
			
			if colnames[sortCol] != _('Bib'):
				for r in xrange(len(data[sortCol])):
					if data[sortCol][r]:
						data[sortCol][r] = u'{} [{}: {}]'.format(data[sortCol][r], r+1, data[1][r])
		
		# Highlight the sorted column.
		if sortLap:
			colnames = []
			for name in exportGrid.colnames:
				try:
					if int(name.split()[1]) == sortLap:
						name = u'<{}>\n{}'.format(name,
												[_('by Lap Time'), _('by Race Time'), _('by Lap Speed'), _('by Race Speed')][self.selectDisplay])
				except:
					pass
				colnames.append( name )
		elif sortLabel:
			colnames = []
			for name in exportGrid.colnames:
				if name == sortLabel:
					name = u'<{}>'.format(name)
				colnames.append( name )
		else:
			colnames = exportGrid.colnames
		
		try:
			iLabelMax = (i for i, name in enumerate(colnames) if name.startswith(_('Lap')) or name.startswith('<' + _('Lap'))).next()
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
		try:
			iUCICodeCol = colnamesLabels.index( _('UCICode') )
			self.labelGrid.SetColRenderer( iUCICodeCol, IOCCodeRenderer() )
		except ValueError:
			pass
		try:
			iNatCodeCol = colnamesLabels.index( _('NatCode') )
			self.labelGrid.SetColRenderer( iNatCodeCol, IOCCodeRenderer() )
		except ValueError:
			pass
		
		self.lapGrid.Set( data = dataLaps, colnames = colnameLaps )
		self.lapGrid.Reset()
		self.lapGrid.AutoSizeColumns( self.lapGrid.GetNumberCols() < 100 )
		
		self.isEmpty = False
		
		# Find interpolated entries.
		with Model.LockRace() as race:
			numTimeInfo = race.numTimeInfo
			riders = race.riders
			for r in xrange(self.lapGrid.GetNumberRows()):
				try:
					rider = riders[int(self.labelGrid.GetCellValue(r, 1))]
				except:
					continue
					
				try:
					entries = rider.interpolate()
				except (ValueError, IndexError):
					continue
				
				if not entries:
					continue
				for c in xrange(self.lapGrid.GetNumberCols()):
					if not self.lapGrid.GetCellValue(r, c):
						break
					try:
						if entries[c+1].interp:
							self.rcInterp.add( (r, c) )
						elif numTimeInfo.getInfo(entries[c+1].num, entries[c+1].t) is not None:
							self.rcNumTime.add( (r, c) )
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
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,200))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	Model.race.winAndOut = True
	results = Results(mainWin)
	results.refresh()
	mainWin.Show()
	app.MainLoop()
