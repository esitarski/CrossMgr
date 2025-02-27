import re
import os
import wx
import wx.grid as gridlib
import xlsxwriter
import Utils
import Model
from AddExcelInfo import AddExcelInfo

from Undo import undo
from ReorderableGrid import ReorderableGrid
from HighPrecisionTimeEdit import HighPrecisionTimeEdit

from GetResults import GetCategoryDetails, UnstartedRaceWrapper
from ExportGrid import ExportGrid
from RaceInputState import RaceInputState
from SetLaps import SetLaps
from wx.grid import GridCellNumberEditor

#--------------------------------------------------------------------------------

allName = _('All')

def getExportGrid():
	race = Model.race
	try:
		race.excelLink.read()
	except Exception:
		pass
	
	GetTranslation = _
	allZeroStarters = True
	with UnstartedRaceWrapper():
		catMap = { c.fullname:c for c in race.getCategories( startWaveOnly=False ) }
		catDetails = GetCategoryDetails( False, True )
		
		title = '\n'.join( [_('Categories'), race.title, race.scheduledStart + ' ' + _('Start on') + ' ' + Utils.formatDate(race.date)] )
		colnames = [_('Start Time'), _('Category'), _('Gender'), _('Numbers'), _('Laps'), _('Distance'), _('Starters')]
		
		raceStart = Utils.StrToSeconds( race.scheduledStart + ':00' )
		catData = []
		for catInfo in catDetails:
			c = catMap.get( catInfo['name'], None )
			if not c:
				continue
			
			starters = race.catCount(c)
			if starters:
				allZeroStarters = False
			else:
				starters = ''
			
			laps = catInfo.get( 'laps', '' ) or ''
			raceDistance = catInfo.get( 'raceDistance', '' )
			raceDistanceUnit = catInfo.get( 'distanceUnit', '')
			
			if raceDistance:
				raceDistance = '{:.2n}'.format(raceDistance)
				
			if c.catType == c.CatWave:
				catStart = Utils.SecondsToStr( raceStart + c.getStartOffsetSecs() )
			elif c.catType == c.CatCustom:
				catStart = Utils.SecondsToStr( raceStart )
			else:
				catStart = ''
				
			catData.append( [
				catStart,
				' - ' + c.name if c.catType == c.CatComponent else c.name,
				GetTranslation(catInfo.get('gender', 'Open')),
				c.catStr,
				'{}'.format(laps),
				' '.join([raceDistance, raceDistanceUnit]) if raceDistance else '',
				'{}'.format(starters)
			])
	
	if allZeroStarters:
		colnames.remove( _('Starters') )
	data = [[None] * len(catData) for i in range(len(colnames))]
	for row in range(len(catData)):
		for col in range(len(colnames)):
			data[col][row] = catData[row][col]
			
	exportGrid = ExportGrid( title = title, colnames = colnames, data = data )
	exportGrid.leftJustifyCols = { 1, 2, 3 }
	return exportGrid

class CategoriesPrintout( wx.Printout ):
	def __init__(self, categories = None):
		super().__init__()

	def OnBeginDocument(self, start, end):
		return super().OnBeginDocument(start, end)

	def OnEndDocument(self):
		super().OnEndDocument()

	def OnBeginPrinting(self):
		super().OnBeginPrinting()

	def OnEndPrinting(self):
		super().OnEndPrinting()

	def OnPreparePrinting(self):
		super().OnPreparePrinting()

	def HasPage(self, page):
		return page == 1

	def GetPageInfo(self):
		return (1,1,1,1)

	def OnPrintPage(self, page):
		race = Model.race
		if not race:
			return
		exportGrid = getExportGrid()
		exportGrid.drawToFitDC( self.GetDC() )
		return True

def PrintCategories():
	mainWin = Utils.getMainWin()
	race = Model.race
	if not mainWin or not race:
		return
	
	pdd = wx.PrintDialogData(mainWin.printData)
	pdd.EnableSelection( False )
	pdd.EnablePageNumbers( False )
	pdd.EnableHelp( False )
	pdd.EnablePrintToFile( False )
	
	printer = wx.Printer(pdd)
	printout = CategoriesPrintout()

	if not printer.Print(mainWin, printout, True):
		if printer.GetLastError() == wx.PRINTER_ERROR:
			Utils.MessageOK(mainWin, '\n\n'.join( [_("There was a printer problem."), _("Check your printer setup.")] ), _("Printer Error"), iconMask=wx.ICON_ERROR)
	else:
		mainWin.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )

#--------------------------------------------------------------------------------
class TimeEditor(gridlib.GridCellEditor):
	defaultValue = '00:00:00'

	def __init__(self):
		self._tc = None
		self.startValue = self.defaultValue
		gridlib.GridCellEditor.__init__(self)
		
	def Create( self, parent, id = wx.ID_ANY, evtHandler = None ):
		self._tc = HighPrecisionTimeEdit( parent, id, style=wx.TE_CENTRE, value=self.defaultValue, display_milliseconds=False )
		self.SetControl( self._tc )
		if evtHandler:
			self._tc.PushEventHandler( evtHandler )
	
	def SetSize( self, rect ):
		self._tc.SetSize(rect.x, rect.y, rect.width+2, rect.height+2, wx.SIZE_ALLOW_MINUS_ONE )
	
	def BeginEdit( self, row, col, grid ):
		self.startValue = grid.GetTable().GetValue(row, col)
		self._tc.SetValue( self.startValue or self.defaultValue )
		self._tc.SetFocus()
		
	def EndEdit( self, row, col, grid, value = None ):
		val = self._tc.GetValue()
		grid.GetTable().SetValue( row, col, val )
		
	def Reset( self ):
		self._tc.SetValue( self.startValue )
		
	def Clone( self ):
		return TimeEditor()

class CategoryIconRenderer(gridlib.GridCellRenderer):
	def __init__( self ):
		self.bitmaps = [
			wx.Bitmap( os.path.join(Utils.getImageFolder(), 'bullhorn_2.png'), wx.BITMAP_TYPE_PNG ),
			wx.Bitmap( os.path.join(Utils.getImageFolder(), 'arrow_right_alt.png'), wx.BITMAP_TYPE_PNG ),
			wx.Bitmap( os.path.join(Utils.getImageFolder(), 'point-of-interest-icon.png'), wx.BITMAP_TYPE_PNG ),
		]
		wMax = hMax = 0
		for b in self.bitmaps:
			w, h = b.GetSize()
			wMax = max( wMax, w )
			hMax = max( hMax, h )
		self.wMax = wMax
		self.hMax = hMax
		gridlib.GridCellRenderer.__init__(self)

	def Draw(self, grid, attr, dc, rect, row, col, isSelected):
		if col+1 >= grid.GetNumberCols():
			return
		value = grid.GetCellValue( row, col+1 ).strip()
		
		if value.endswith( _('Start Wave') ):
			value = 0
		elif value.endswith( _('Component') ):
			value = 1
		else:
			value = 2
		
		dc.SetClippingRegion( rect )
		dc.SetBackgroundMode(wx.SOLID)
		dc.SetBrush(wx.WHITE_BRUSH)
		dc.SetPen(wx.TRANSPARENT_PEN)
		dc.DrawRectangle(rect)
		
		bitmap = self.bitmaps[value]
		w, h = bitmap.GetSize()
		x = (rect.GetWidth() - w) // 2
		y = (rect.GetHeight() - h) // 2
		dc.DrawBitmap(bitmap, rect.x + x, rect.y + y)
		
		dc.DestroyClippingRegion()

	def GetBestSize(self, grid, attr, dc, row, col):
		return wx.Size(self.wMax, self.hMax)

	def Clone(self):
		return CategoryIconRenderer()

class BitmapRenderer(wx.grid.PyGridCellRenderer):
	def __init__( self, *args, **kwargs ):
		self.bmp = kwargs.pop( 'bmp' )
		super().__init__( *args, **kwargs )
	
	def Draw(self, grid, attr, dc, rect, row, col, is_selected):
		dc.DrawBitmap(self.bmp, rect.X, rect.Y)

	def Clone(self):
		return self.__class__()

#--------------------------------------------------------------------------------
class Categories( wx.Panel ):
	CategoryTypeChoices = [_('Start Wave'),'    ' + _('Component'),_('Custom')]
	DistanceTypeChoices = [_('Lap'),_('Race')]
	
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id )
		
		self.state = RaceInputState()
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		self.ignoreColour = wx.Colour( 80, 80, 80 )
		self.inactiveColour = wx.Colour( 200, 200, 200 )
		
		border = 4
		flag = wx.ALL
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		
		self.activateAllButton = wx.Button(self, label=_('Activate All'))
		self.Bind( wx.EVT_BUTTON, self.onActivateAll, self.activateAllButton )
		hs.Add( self.activateAllButton, 0, border = border, flag = flag )

		hs.AddSpacer( 6 )
		
		self.newCategoryButton = wx.Button(self, label=_('New'))
		self.Bind( wx.EVT_BUTTON, self.onNewCategory, self.newCategoryButton )
		hs.Add( self.newCategoryButton, 0, border = border, flag = flag )
		
		self.delCategoryButton = wx.Button(self, label=_('Delete'))
		self.Bind( wx.EVT_BUTTON, self.onDelCategory, self.delCategoryButton )
		hs.Add( self.delCategoryButton, 0, border = border, flag = (flag & ~wx.LEFT) )

		hs.AddSpacer( 6 )
		
		self.upCategoryButton = wx.Button(self, label='\u2191')
		self.Bind( wx.EVT_BUTTON, self.onUpCategory, self.upCategoryButton )
		hs.Add( self.upCategoryButton, 0, border = border, flag = flag )

		self.downCategoryButton = wx.Button(self, label='\u2193')
		self.Bind( wx.EVT_BUTTON, self.onDownCategory, self.downCategoryButton )
		hs.Add( self.downCategoryButton, 0, border = border, flag = (flag & ~wx.LEFT) )

		hs.AddSpacer( 6 )
		
		self.setGpxDistanceButton = wx.Button(self, label=_('Set Gpx Distance') )
		self.Bind( wx.EVT_BUTTON, self.onSetGpxDistance, self.setGpxDistanceButton )
		hs.Add( self.setGpxDistanceButton, 0, border = border, flag = flag )
		
		hs.AddSpacer( 6 )
		
		self.addExceptionsButton = wx.Button(self, label=_('Bib Exceptions'))
		self.Bind( wx.EVT_BUTTON, self.onAddExceptions, self.addExceptionsButton )
		hs.Add( self.addExceptionsButton, 0, border = border, flag = flag )

		hs.AddSpacer( 6 )
		
		'''
		self.updateStartWaveNumbersButton = wx.Button(self, label=_('Update Start Wave Bibs'))
		self.Bind( wx.EVT_BUTTON, self.onUpdateStartWaveNumbers, self.updateStartWaveNumbersButton )
		hs.Add( self.updateStartWaveNumbersButton, 0, border = border, flag = flag )
		'''

		self.normalizeButton = wx.Button(self, label=_('Normalize'))
		self.Bind( wx.EVT_BUTTON, self.onNormalize, self.normalizeButton )
		hs.Add( self.normalizeButton, 0, border = border, flag = flag )

		hs.AddStretchSpacer()
		
		self.printButton = wx.Button( self, label='{}...'.format(_('Print')) )
		self.Bind( wx.EVT_BUTTON, self.onPrint, self.printButton )
		hs.Add( self.printButton, 0, border = border, flag = flag )
		
		self.excelButton = wx.Button( self, label='{}...'.format(_('Excel')) )
		self.Bind( wx.EVT_BUTTON, self.onExcel, self.excelButton )
		hs.Add( self.excelButton, 0, border = border, flag = flag )
		
		self.grid = ReorderableGrid( self )
		self.colNameFields = [
			('',						None),
			(_('Category Type'),		'catType'),
			(_('Active'),				'active'),
			(_('Name'),					'name'),
			(_('Gender'),				'gender'),
			(_('Numbers'),				'catStr'),
			(_('Start\nOffset'),		'startOffset'),
			(_('Race\nLaps'),			'numLaps'),
			('',						'setLaps'),
			(_('Race\nMinutes'),		'raceMinutes'),
			(_('Lapped\nRiders\nContinue'),	'lappedRidersMustContinue'),
			(_('Distance'),				'distance'),
			(_('Dist.\nBy'),			'distanceType'),
			(_('First\nLap\nDist.'),	'firstLapDistance'),
			(_('80%\nLap\nTime'),		'rule80Time'),
			(_('CrossMgr\nEstimated\nLaps'),	'suggestedLaps'),
			(_('Early\nBell\nTime'),	'earlyBellTime'),
			(_('Publish'),				'publishFlag'),
			(_('Upload'),				'uploadFlag'),
			(_('Series'),				'seriesFlag'),
		]
		self.computedFields = {'rule80Time', 'suggestedLaps', 'setLaps'}
		self.colnames = [colName if not colName.startswith('_') else _('Name Copy') for colName, fieldName in self.colNameFields]
		self.iCol = { fieldName:i for i, (colName, fieldName) in enumerate(self.colNameFields) if fieldName and not colName.startswith('_') }
		
		self.activeColumn = self.iCol['active']
		self.genderColumn = self.iCol['gender']
		self.numbersColumn = self.iCol['catStr']
		self.grid.CreateGrid( 0, len(self.colnames) )
		self.grid.SetRowLabelSize(32)
		self.grid.SetMargins(0,0)
		for col, name in enumerate(self.colnames):
			self.grid.SetColLabelValue( col, name )
			
		self.cb = None
		
		self.boolCols = set()
		self.choiceCols = set()
		self.readOnlyCols = set()
		self.dependentCols = set()
		
		# Set column attributes for the table.
		for col, (colName, fieldName) in enumerate(self.colNameFields):
			attr = gridlib.GridCellAttr()
			
			if fieldName is None:
				attr.SetRenderer( CategoryIconRenderer() )
				attr.SetAlignment( wx.ALIGN_LEFT, wx.ALIGN_CENTRE )
				attr.SetReadOnly( True )
				self.readOnlyCols.add( col )
				
			elif fieldName == 'setLaps':
				attr.SetReadOnly( True )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
				self.readOnlyCols.add( col )
				self.dependentCols.add( col )
				
			elif fieldName == 'catType':
				self.catTypeWidth = 64
				attr.SetEditor( gridlib.GridCellChoiceEditor(self.CategoryTypeChoices, False) )
				attr.SetAlignment( wx.ALIGN_LEFT, wx.ALIGN_CENTRE )
				self.choiceCols.add( col )
				
			elif fieldName in {'active', 'lappedRidersMustContinue', 'publishFlag', 'uploadFlag', 'seriesFlag'}:
				boolEditor = gridlib.GridCellBoolEditor()
				boolEditor.UseStringValues( '1', '0' )
				attr.SetEditor( boolEditor )
				attr.SetRenderer( gridlib.GridCellBoolRenderer() )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
				self.boolCols.add( col )
				if fieldName == 'lappedRidersMustContinue':
					self.dependentCols.add( col )
				
			elif fieldName == 'gender':
				attr.SetEditor( gridlib.GridCellChoiceEditor([_('Open'),_('Men'),_('Women')], False) )
				self.choiceCols.add( col )
				
			elif fieldName == 'startOffset':
				attr.SetEditor( TimeEditor() )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
				self.dependentCols.add( col )
				
			elif fieldName == 'earlyBellTime':
				attr.SetEditor( TimeEditor() )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
				self.dependentCols.add( col )
				
			elif fieldName == 'numLaps':
				attr.SetEditor( GridCellNumberEditor() )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
				self.dependentCols.add( col )
				
			elif fieldName == 'raceMinutes':
				attr.SetEditor( GridCellNumberEditor() )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
				self.dependentCols.add( col )
				
			elif fieldName in ['rule80Time', 'suggestedLaps']:
				attr.SetReadOnly( True )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
				self.readOnlyCols.add( col )
				self.dependentCols.add( col )
				
			elif fieldName in ('distance', 'firstLapDistance'):
				attr.SetRenderer( gridlib.GridCellFloatRenderer(7, 3) )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
				self.dependentCols.add( col )
				
			elif fieldName == 'distanceType':
				attr.SetEditor( gridlib.GridCellChoiceEditor(self.DistanceTypeChoices, False) )
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTRE )
				self.choiceCols.add( col )
				self.dependentCols.add( col )
				
			elif colName == '_name2':
				attr.SetAlignment( wx.ALIGN_LEFT, wx.ALIGN_CENTRE )
				attr.SetBackgroundColour( wx.Colour(240,240,240) )
				attr.SetReadOnly( True )
				
			self.grid.SetColAttr( col, attr )
		
		self.grid.Bind( gridlib.EVT_GRID_CELL_LEFT_CLICK, self.onGridLeftClick )
		self.grid.Bind( gridlib.EVT_GRID_SELECT_CELL, self.onCellSelected )
		self.grid.Bind( gridlib.EVT_GRID_CELL_CHANGED, self.onCellChanged )
		self.grid.Bind( gridlib.EVT_GRID_EDITOR_CREATED, self.onEditorCreated )
		
		vs.Add( hs, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		vs.Add( self.grid, 1, flag=wx.GROW|wx.ALL|wx.EXPAND )
		
		self.rowCur = 0
		self.colCur = 0
		self.SetSizer(vs)

	def onPrint( self, event ):
		self.commit()
		PrintCategories()
		
	def onExcel( self, event ):
		self.commit()
		export = getExportGrid()
		xlFName = Utils.getMainWin().getFormatFilename('excel')
		xlFName = os.path.splitext( xlFName )[0] + '-Categories' + os.path.splitext( xlFName )[1]

		wb = xlsxwriter.Workbook( xlFName )
		sheetCur = wb.add_worksheet( _('Categories') )
		export.toExcelSheetXLSX( ExportGrid.getExcelFormatsXLSX(wb), sheetCur )
		
		AddExcelInfo( wb )
		try:
			wb.close()
			if Utils.getMainWin().launchExcelAfterPublishingResults:
				Utils.LaunchApplication( xlFName )
			Utils.MessageOK(self, '{}:\n\n   {}'.format(_('Excel file written to'), xlFName), _('Excel Write'))
		except IOError:
			Utils.MessageOK(self,
						'{} "{}"\n\n{}\n{}'.format(
							_('Cannot write'), xlFName,
							_('Check if this spreadsheet is already open.'),
							_('If so, close it, and try again.')
						),
						_('Excel File Error'), iconMask=wx.ICON_ERROR )		
	
	def onSetGpxDistance( self, event ):
		race = Model.race
		geoTrack = getattr(race, 'geoTrack', None)
		if not geoTrack:
			return
		if not Utils.MessageOK( self, _('Set the GPX distance for all Categories?'), _('Set GPX Distance'), wx.ICON_QUESTION ):
			return
		self.commit()	# Commit any current changes on the screen.
		distance = geoTrack.lengthKm if race.distanceUnit == Model.Race.UnitKm else geoTrack.lengthMiles
		for category in race.getCategories():
			category.distance = distance
		race.setChanged()
		self.refresh( forceRefresh=True )
	
	def onNormalize( self, event ):
		self.commit()
		if Model.race:
			Model.race.normalizeCategories()
			self.state.reset()
			self.refresh()
			
	#------------------------------------------
	
	def onGridLeftClick( self, event ):
		if event.GetCol() in self.boolCols:
			r, c = event.GetRow(), event.GetCol()
			if c == self.iCol['active']:
				active = (self.grid.GetCellValue(r, self.iCol['active']) == '1')
				wx.CallAfter( self.fixRowColours, r, self.CategoryTypeChoices.index(self.grid.GetCellValue(r, self.iCol['catType'])), not active )
			self.grid.SetCellValue( r, c, '1' if self.grid.GetCellValue(r, c)[:1] != '1' else '0' )
		event.Skip()
		
	def onCellSelected( self, event ):
		self.rowCur = event.GetRow()
		self.colCur = event.GetCol()
		if self.colCur in self.choiceCols or self.colCur in self.boolCols:
			wx.CallAfter( self.grid.EnableCellEditControl )
		elif self.colCur == self.iCol['setLaps']:
			race = Model.race
			if race and race.isRunning():
				self.commit()
				try:
					category = race.getAllCategories()[self.rowCur]
				except IndexError:
					category = None
				if category and category.catType == Model.Category.CatWave:
					with SetLaps( self, category ) as setLaps:
						setLaps.ShowModal()
					return
		
		event.Skip()

	def onCellChanged( self, event ):
		self.rowCur = event.GetRow()
		self.colCur = event.GetCol()
		if self.colNameFields[self.colCur][1] in ('catType','active'):
			wx.CallAfter( self.fixCells )
		elif self.colNameFields[self.colCur][1] in ('distance', 'firstLapDistance'):
			d = Utils.positiveFloatLocale( self.grid.GetCellValue(self.rowCur, self.colCur) )
			self.grid.SetCellValue( self.rowCur, self.colCur, f'{d:.3n}' if d>0.0 else '' )
			
		event.Skip()

	def onEditorCreated( self, event ):
		if event.GetCol() == self.numbersColumn:
			ctrl = event.GetControl()
			ctrl.Bind( wx.EVT_KEY_DOWN, self.onNumbersKeyEvent )
			ctrl.Bind( wx.EVT_TEXT_PASTE, self.onPaste )
		event.Skip()
	
	def getCleanClipboardText( self ):
		if wx.TheClipboard.Open():
			data = wx.TextDataObject()
			if wx.TheClipboard.GetData(data):
				txt = data.GetText()
				txt = re.sub( '[^0-9,-]+', ',', txt )
			wx.TheClipboard.Close()
			return txt
		return None
		
	def isExternalChange( self ):
		if not Model.race:
			return False
		
		# Check if we need to update the Categories page if something relevant changes externally.
		categories = Model.race.getAllCategories()
		
		for cat in categories:
			try:
				cat.distance = float(cat.distance)
			except Exception:
				cat.distance = None
			try:
				cat.firstLapDistance = float(cat.firstLapDistance)
			except Exception:
				cat.firstLapDistance = None
		
		if self.grid.GetNumberRows() != len(categories):
			return True
			
		def distanceMatches( distance, cellValue ):
			try:
				value = float(cellValue)
			except ValueError:
				value = None
				
			if not distance and not value:
				return True
			return '{:.3n}'.format(distance or 0.0) == cellValue
		
		def numLapsMatches( numLaps, cellValue ):
			v = '{}'.format( numLaps if numLaps is not None else '' )
			return v == cellValue
		
		return any(	(
						cat.name != self.grid.GetCellValue(r, self.iCol['name']) or
						cat.catStr != self.grid.GetCellValue(r, self.iCol['catStr']) or
						not distanceMatches(cat.distance, self.grid.GetCellValue(r, self.iCol['distance'])) or
						not distanceMatches(cat.firstLapDistance, self.grid.GetCellValue(r, self.iCol['firstLapDistance'])) or
						not numLapsMatches( cat.numLaps, self.grid.GetCellValue(r, self.iCol['numLaps']))
					) for r, cat in enumerate(categories) )
	
	def pasteFromClipboard( self, event ):
		txt = self.getCleanClipboardText()
		if txt:
			event.GetEventObject().WriteText( txt )
			return True
		return False
		
	def onNumbersKeyEvent( self, event ):
		# Handle column pastes from Excel when there are newlines.
		if event.GetModifiers() == wx.MOD_CONTROL and event.GetKeyCode() == 86:
			if self.pasteFromClipboard( event ):
				return
		event.Skip()

	def onPaste( self, event ):
		self.pasteFromClipboard( event )
		event.Skip()
		
	#------------------------------------------

	def onUpdateStartWaveNumbers( self, event ):
		self.commit()
		undo.pushState()
		with Model.LockRace() as race:
			race.adjustAllCategoryWaveNumbers()
		self.state.reset()
		wx.CallAfter( self.refresh )
		wx.CallAfter( Utils.refreshForecastHistory )

	def onAddExceptions( self, event ):
		with Model.LockRace() as race:
			if not race or not race.getAllCategories():
				return
				
		r = self.grid.GetGridCursorRow()
		if r is None or r < 0:
			Utils.MessageOK( self, _('You must select a Category first'), _('Select a Category') )
			return
		
		with Model.LockRace() as race:
			categories = race.getAllCategories()
			category = categories[r]
			
		with wx.TextEntryDialog(
			self,
			'{}: {}'.format(
				category.name,
				_('''Add Bib Exceptions (comma separated).
This will add the given list of Bibs to this category,
and remove them from other categories.'''),
			),
			_('Add Bib Exceptions')
		) as dlg:
			if dlg.ShowModal() != wx.ID_OK:
				return
			response = dlg.GetValue()

		self.commit()
		response = re.sub( '[^0-9,]', '', response.replace(' ', ',') )
		with Model.LockRace() as race:
			for numException in response.split(','):
				race.addCategoryException( category, numException )

		self.state.reset()
		self.refresh()
		
	def _setRow( self, r, cat ):
		def bToS( b ):
			return ('0','1')[int(b)]
		
		startOffset = cat.startOffset
		while len(startOffset) < len('00:00:00'):
			startOffset = '00:' + startOffset
		earlyBellTime = cat.earlyBellTime or ''
		if isinstance( earlyBellTime, (float, int) ):
			earlyBellTime = Utils.formatTime( float(earlyBellTime) ) if earlyBellTime else ''

		GetTranslation = _
		gender = cat.gender if cat.gender in ['Men', 'Women'] else 'Open'
		self.grid.SetRowLabelValue( r, '' )
		self.grid.SetCellValue( r, self.iCol['active'], bToS(cat.active) )
		self.grid.SetCellValue( r, self.iCol['catType'], self.CategoryTypeChoices[cat.catType] )
		self.grid.SetCellValue( r, self.iCol['name'], cat.name )
		self.grid.SetCellValue( r, self.iCol['gender'], GetTranslation(gender) )
		self.grid.SetCellValue( r, self.iCol['catStr'], cat.catStr )
		self.grid.SetCellValue( r, self.iCol['startOffset'], startOffset )
		self.grid.SetCellValue( r, self.iCol['numLaps'], f'{cat.numLaps}' if cat.numLaps else '' )
		self.grid.SetCellValue( r, self.iCol['setLaps'], '\u27F3' )
		self.grid.SetCellValue( r, self.iCol['raceMinutes'], f'{cat.raceMinutes}' if cat.raceMinutes else '' )
		self.grid.SetCellValue( r, self.iCol['lappedRidersMustContinue'], bToS(cat.lappedRidersMustContinue) )
		self.grid.SetCellValue( r, self.iCol['rule80Time'], '' )
		self.grid.SetCellValue( r, self.iCol['suggestedLaps'], '' )
		self.grid.SetCellValue( r, self.iCol['distance'], ('{:.3n}'.format(cat.distance)) if cat.distance else '' )
		self.grid.SetCellValue( r, self.iCol['distanceType'], self.DistanceTypeChoices[cat.distanceType if cat.distanceType else 0] )
		self.grid.SetCellValue( r, self.iCol['firstLapDistance'], ('{:.3n}'.format(cat.firstLapDistance)) if cat.firstLapDistance else '' )
		self.grid.SetCellValue( r, self.iCol['earlyBellTime'], earlyBellTime )
		self.grid.SetCellValue( r, self.iCol['publishFlag'], bToS(cat.publishFlag) )
		self.grid.SetCellValue( r, self.iCol['uploadFlag'], bToS(cat.uploadFlag) )
		self.grid.SetCellValue( r, self.iCol['seriesFlag'], bToS(cat.seriesFlag) )
		
		# Update the computed fields.
		if not cat.active or cat.catType != Model.Category.CatWave:
			return
			
		# Get the 80% time.
		race = Model.race
		if race:		
			rule80Time = race.getRule80CountdownTime( cat ) if race else None
			if rule80Time:
				self.grid.SetCellValue( r, self.iCol['rule80Time'], Utils.formatTime(rule80Time) )
			
			laps = race.getNumLapsFromCategory( cat ) if race else None
			if laps:
				self.grid.SetCellValue( r, self.iCol['suggestedLaps'], f'{laps}' )
	
	def fixRowColours( self, row, catType, active ):
		activeColour = wx.WHITE if active else self.inactiveColour
		colour = activeColour if catType == Model.Category.CatWave else self.ignoreColour
		for colName, fieldName in self.colNameFields:
			if not fieldName:
				continue
			col = self.iCol[fieldName]
			if fieldName == 'setLaps' and not (Model.race and Model.race.isRunning()):
				self.grid.SetCellBackgroundColour( row, col, self.inactiveColour )
			else:
				self.grid.SetCellBackgroundColour( row, col, colour if col in self.dependentCols else activeColour )
		
	def fixCells( self, event = None ):
		for row in range(self.grid.GetNumberRows()):
			active = self.grid.GetCellValue( row, self.iCol['active'] )[:1] in 'TtYy1'
			catType = self.CategoryTypeChoices.index(self.grid.GetCellValue(row, self.iCol['catType']) )
			self.fixRowColours( row, catType, active )
	
	def onActivateAll( self, event ):
		self.commit()
		if Model.race:
			for c in Model.race.getAllCategories():
				if not c.active:
					c.active = True
					Model.race.setChanged()
		self.state.reset()
		wx.CallAfter( self.refresh )
		
	def onDeactivateAll( self, event ):
		self.commit()
		if Model.race:
			for c in Model.race.getAllCategories():
				if c.active:
					c.active = False
					Model.race.setChanged()
		self.state.reset()
		wx.CallAfter( self.refresh )
	
	def doAutosize( self ):
		self.grid.AutoSizeColumns( False )
		colWidth = self.grid.GetColSize( self.iCol['catStr'] )
		maxWidth = wx.GetDisplaySize().width // 3
		if colWidth > maxWidth:
			self.grid.SetColSize( self.iCol['catStr'], maxWidth )
			self.grid.ForceRefresh()
	
	def onNewCategory( self, event ):
		self.grid.AppendRows( 1 )
		self._setRow( self.grid.GetNumberRows() - 1, Model.Category(active=True, name='<{}>     '.format(_('CategoryName')), catStr='100-199,504,-128') )
		self.doAutosize()
		
	def onDelCategory( self, event ):
		r = self.grid.GetGridCursorRow()
		if r is None or r < 0:
			return
		if Utils.MessageOKCancel(
					self,
					'{} "{} ({})"?'.format(
						_('Delete Category'),
						self.grid.GetCellValue(r, 3).strip(),
						self.grid.GetCellValue(r, 4).strip(),
					),
					_('Delete Category') ):
			self.grid.DeleteRows( r, 1, True )
		
	def onUpCategory( self, event ):
		self.grid.SaveEditControlValue()
		self.grid.DisableCellEditControl()
		r = self.grid.GetGridCursorRow()
		Utils.SwapGridRows( self.grid, r, r-1 )
		if r-1 >= 0:
			self.grid.MoveCursorUp( False )
		self.grid.ClearSelection()
		self.grid.SelectRow( max(r-1, 0), True )
		
	def onDownCategory( self, event ):
		self.grid.SaveEditControlValue()
		self.grid.DisableCellEditControl()
		r = self.grid.GetGridCursorRow()
		Utils.SwapGridRows( self.grid, r, r+1 )
		if r+1 < self.grid.GetNumberRows():
			self.grid.MoveCursorDown( False )
		self.grid.ClearSelection()
		self.grid.SelectRow( min(r+1, self.grid.GetNumberRows()-1), True )
		
	def refresh( self, forceRefresh=False ):
		self.setGpxDistanceButton.Enable( hasattr(Model.race, 'geoTrack') )
		
		if not (forceRefresh or self.isExternalChange() or self.state.changed()):
			return
			
		# Fix the height of the column labels.
		dc = wx.WindowDC( self.grid )
		dc.SetFont( self.grid.GetLabelFont() )
		textHeight = dc.GetTextExtent( 'Label' )[1]
		self.colLabelHeight = textHeight * max(name.count('\n') + 1 for name in self.colnames) + textHeight // 4
		self.grid.SetColLabelSize( self.colLabelHeight )
			
		with Model.LockRace() as race:
			self.grid.ClearGrid()
			if race is None:
				return
			
			for c in range(self.grid.GetNumberCols()):
				if self.grid.GetColLabelValue(c).startswith(_('Distance')):
					self.grid.SetColLabelValue( c, '{}\n({})'.format(_('Distance'), ['km', 'miles'][getattr(race, 'distanceUnit', 0)]) )
					break
			
			categories = race.getAllCategories()
			
			if self.grid.GetNumberRows() > 0:
				self.grid.DeleteRows( 0, self.grid.GetNumberRows() )
			self.grid.AppendRows( len(categories) )
			
			for r, cat in enumerate(categories):
				self._setRow( r, cat )
				
			self.doAutosize()
			self.fixCells()
			
			# Force the grid to the correct size.
			self.grid.FitInside()
			self.GetSizer().Layout()

	def commit( self ):
		undo.pushState()
		with Model.LockRace() as race:
			self.grid.SaveEditControlValue()
			self.grid.DisableCellEditControl()	# Make sure the current edit is committed.
			if race is None:
				return
			numStrTuples = []
			for r in range(self.grid.GetNumberRows()):
				values = { name:self.grid.GetCellValue(r, c)
					for name, c in self.iCol.items() if name not in self.computedFields
				}
				for field in ('distance', 'firstLapDistance'):
					d = Utils.positiveFloatLocale( values[field] )
					s = f'{d:.3n}' if d>0.0 else ''
					self.grid.SetCellValue( r, self.iCol[field], s )
					values[field] = s
				
				values['catType'] = self.CategoryTypeChoices.index(values['catType'])
				values['distanceType'] = self.DistanceTypeChoices.index(values['distanceType'])
				numStrTuples.append( values )
				
			race.setCategories( numStrTuples )
			race.adjustAllCategoryWaveNumbers()
		wx.CallAfter( Utils.refreshForecastHistory )
	
if __name__ == '__main__':
	'''
	import locale
	locale.setlocale(locale.LC_ALL,'fr_FR.UTF-8')
	'''
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1000,400))
	Model.setRace( Model.Race() )
	race = Model.getRace()
	race._populate()
	race.setCategories( [
		# {'name':'test1', 'catStr':'100-199,999'+','+','.join('{}'.format(i) for i in range(1, 50, 2)),'gender':'Men'},
		{'name':'test2', 'catStr':'200-299,888', 'startOffset':'00:10', 'distance':'6'},
		{'name':'test3', 'catStr':'300-399', 'startOffset':'00:20','gender':'Women', 'lappedRidersMustContinue':True},
		{'name':'test4', 'catStr':'400-499', 'startOffset':'00:30','gender':'Open'},
		{'name':'test5', 'catStr':'500-599', 'startOffset':'01:00','gender':'Men', 'lappedRidersMustContinue':True},
	] )
	categories = Categories(mainWin)
	categories.refresh()
	categories.grid.SetCellValue( 0, categories.iCol['distance'], '10,2' )
	categories.grid.SetCellValue( 0, categories.iCol['numLaps'], '9' )
	mainWin.Show()
	app.MainLoop()
