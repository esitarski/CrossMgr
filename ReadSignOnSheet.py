import wx
import wx.adv as adv
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.scrolledpanel as scrolled
import os
import re
import sys
import cgi
import copy
import string
from io import StringIO
import Utils
from Utils import tag
import Model
from Excel import GetExcelReader
from ReadCategoriesFromExcel import ReadCategoriesFromExcel
from ReadPropertiesFromExcel import ReadPropertiesFromExcel
from ReadCategoriesFromExcel import sheetName as CategorySheetName
from ReadPropertiesFromExcel import sheetName as PropertySheetName
import MatchingCategory
import HelpSearch

with Utils.SuspendTranslation():
	TagFields = [
		_('Tag'), _('Tag1'), _('Tag2'), _('Tag3'), _('Tag4'), _('Tag5'), _('Tag6'), _('Tag7'), _('Tag8'), _('Tag9'),
	]

with Utils.SuspendTranslation():
	CustomCategoryFields = [
		_('CustomCategory'), _('CustomCategory1'), _('CustomCategory2'), _('CustomCategory3'), _('CustomCategory4'), _('CustomCategory5'), _('CustomCategory6'), _('CustomCategory7'), _('CustomCategory8'), _('CustomCategory9'),
	]

with Utils.SuspendTranslation():
	Fields = [
		_('Bib#'),
		_('LastName'), _('FirstName'),
		_('Team'),
		_('City'), _('State'), _('Prov'), _('StateProv'), _('Nat.'),
		_('Category'), _('EventCategory'), _('Age'), _('Gender'),
		_('License'),
		_('NatCode'), _('UCIID'), _('UCICode'), _('TeamCode'),
		_('Factor'),
	] + TagFields + CustomCategoryFields

IgnoreFields = ['Bib#', 'Factor', 'EventCategory', 'CustomCategory', 'TeamCode'] + TagFields	# Fields to ignore when adding data to standard reports.
NumericFields = ['Age','Factor']
ReportFields = [f for f in Fields if f not in IgnoreFields]
ReportFields = (lambda s: [f for f in Fields if f not in s])(set(IgnoreFields))

class FileNamePage(adv.WizardPageSimple):
	def __init__(self, parent):
		adv.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Specify the Excel File containing additional rider information.')),
					flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = _('Each race must be in a separate sheet.')), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = _('See documentation for examples.')), flag=wx.ALL, border = border )
		fileMask = [
			'Excel Worksheets (*.xlsx;*.xlsm;*.xls)|*.xlsx;*.xlsm;*.xls',
		]
		self.fbb = filebrowse.FileBrowseButton( self, size=(450, -1),
												labelText = _('Excel Workbook:'),
												fileMode=wx.FD_OPEN,
												fileMask='|'.join(fileMask) )
		vbs.Add( self.fbb, flag=wx.ALL, border = border )
		
		self.SetSizer( vbs )
	
	def setFileName( self, fileName ):
		self.fbb.SetValue( fileName )
	
	def getFileName( self ):
		return self.fbb.GetValue()
	
class SheetNamePage(adv.WizardPageSimple):
	def __init__(self, parent):
		adv.WizardPageSimple.__init__(self, parent)
		self.choices = []
		self.expectedSheetName = None
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Specify the sheet containing the information for this race:')),
				flag=wx.ALL, border = border )
		self.ch = wx.Choice( self, -1, choices = self.choices )
		vbs.Add( self.ch, flag=wx.ALL, border = border )
		self.SetSizer( vbs )
	
	def setFileName( self, fileName ):
		reader = GetExcelReader( fileName )
		self.choices = reader.sheet_names()
		
		self.ch.Clear()
		self.ch.AppendItems( self.choices )
		try:
			self.ch.SetSelection( self.choices.index(self.expectedSheetName) )
		except ValueError:
			self.ch.SetSelection( 0 )
	
	def setExpectedSheetName( self, expectedSheetName ):
		self.expectedSheetName = expectedSheetName
	
	def getSheetName( self ):
		return self.choices[self.ch.GetCurrentSelection()]

def getDefaultFieldMap( fileName, sheetName, expectedFieldCol = None ):
	reader = GetExcelReader( fileName )
	headers, fieldCol = [], {}
	
	# Try to find the header columns.
	# Look for the first row with more than 4 columns.
	for r, row in enumerate(reader.iter_list(sheetName)):
		cols = sum( 1 for d in row if d and '{}'.format(d).strip() )
		if cols > 4:
			headers = ['{}'.format(h or '').strip() for h in row]
			break

	# If we haven't found a header row yet, assume the first non-empty row is the header.
	if not headers:
		for r, row in enumerate(reader.iter_list(sheetName)):
			cols = sum( 1 for d in row if d and '{}'.format(d).strip() )
			if cols > 0:
				headers = ['{}'.format(h or '').strip() for h in row]
				break
	
	# Ignore empty columns on the end.
	while headers and (not headers[-1] or headers[-1].isspace()):
		headers.pop()
		
	if not headers:
		raise ValueError( u'{} {}::{}.'.format(_('Could not find a Header Row'), fileName, sheetName) )
	
	# Rename empty columns so as not to confuse the user.
	headers = [h if h else u'<{} {:03d}>'.format(_('Blank Header Column'), (c+1)) for c, h in enumerate(headers)]
	headers = [h if len(h) < 32 else h[:29].strip() + u'...' for h in headers]
	
	# Set a blank final entry.
	headers.append( u'' )
		
	# Create a map for the field names we are looking for
	# and the headers we found in the Excel sheet.
	sStateField = 'State'
	sProvField = 'Prov'
	sStateProvField = 'StateProv'
	
	GetTranslation = _
	iNoMatch = len(headers) - 1
	exactMatch = { h.lower():(100.0, i) for i, h in enumerate(headers) }
	# For Tag fields, try remove spaces.
	exactMatch.update( {h.lower().replace(u' ', u''):(100.0, i) for i, h in enumerate(headers) if h.lower().startswith('tag')} )
	
	matchStrength = {}
	for c, f in enumerate(Fields):
		# Figure out some reasonable defaults for headers.
		
		# First look for a perfect match ignoring case.
		matchBest, iBest = exactMatch.get( f.lower(), (0.0, iNoMatch) )
		
		if not f.lower().startswith('tag'):
			# Then try the local translation of the header name.
			if matchBest < 2.0:
				fTrans = GetTranslation( f )
				matchBest, iBest = max( ((Utils.approximateMatch(fTrans, h), i) for i, h in enumerate(headers)), key=lambda x: x[0] )
			
			# If that fails, try matching the untranslated header fields.
			if matchBest <= 0.34:
				matchBest, iBest = max( ((Utils.approximateMatch(f, h), i) for i, h in enumerate(headers)), key=lambda x: x[0] )
			
			# If we don't get a high enough match, set to blank.
			if matchBest <= 0.34:
				try:
					iBest = min( expectedFieldCol[c], iNoMatch )
				except (TypeError, KeyError):
					iBest = iNoMatch			
		
		fieldCol[f] = iBest
		matchStrength[f] = matchBest
	
	# If we already have a match for State of Prov, don't match on StateProv, etc.
	if matchStrength.get(sStateProvField,0.0) > matchStrength.get(sStateField,0.0):
		fieldCol[sStateField] = iNoMatch
		fieldCol[sProvField] = iNoMatch
	elif matchStrength.get(sProvField,0.0) > matchStrength.get(sStateProvField,0.0):
		fieldCol[sStateProvField] = iNoMatch
	elif matchStrength.get(sStateField,0.0) > matchStrength.get(sStateProvField,0.0):
		fieldCol[sStateProvField] = iNoMatch
		
	return headers, fieldCol

class HeaderNamesPage(adv.WizardPageSimple):
	def __init__(self, parent):
		adv.WizardPageSimple.__init__(self, parent)

		self.expectedFieldCol = None
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Specify the spreadsheet columns corresponding to CrossMgr fields.')),
				flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = _('Set ignored or missing fields to blank.')),
				flag=wx.ALL, border = border )
		vbs.AddSpacer( 8 )
				
		border = 4
		# Create a map for the field names we are looking for
		# and the headers we found in the Excel sheet.
		sp = scrolled.ScrolledPanel( self, size=(750, 64), style = wx.TAB_TRAVERSAL )
		
		boldFont = None
		
		GetTranslation = _
		gs = wx.GridSizer( 2, len(Fields), 4, 4 )
		gs.SetHGap( 3 )
		for c, f in enumerate(Fields):
			label = wx.StaticText(sp, label=GetTranslation(f))
			if boldFont is None:
				font = label.GetFont()
				boldFont = wx.Font( int(font.GetPointSize()*1.2), font.GetFamily(), font.GetStyle(), wx.FONTWEIGHT_BOLD )
			label.SetFont( boldFont )
			gs.Add( label )
		
		self.headers = []
		self.choices = []
		for c, f in enumerate(Fields):
			self.choices.append( wx.Choice(sp, -1, choices = self.headers ) )
			gs.Add( self.choices[-1] )
		
		self.initCategoriesFromExcel = wx.CheckBox( self, label=_('Initialize CrossMgr Categories from Excel EventCategory/CustomCategory and Bib# columns') )
		self.initCategoriesFromExcel.SetToolTip( wx.ToolTip(u'\n'.join([
				_('Updates, adds or deletes CrossMgr categories, with bib numbers, using the EventCategory/CustomCategory and Bib# columns in the Excel sheet.  Use with care as the Categories will be updated every time the Excel sheet changes.  Read the documentation first!'),
			])
		) )
		
		sp.SetSizer( gs )
		sp.SetAutoLayout(1)
		sp.SetupScrolling( scroll_y = False )
		self.sp = sp
		self.gs = gs
		vbs.Add( sp, flag=wx.ALL, border = border )
		
		self.mapSummary = wx.ListCtrl( self, wx.ID_ANY, style = wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.BORDER_NONE )
		self.mapSummary.InsertColumn( 0, _('CrossMgr'),		wx.LIST_FORMAT_RIGHT,	120 )
		self.mapSummary.InsertColumn( 1, _('Spreadsheet'),	wx.LIST_FORMAT_LEFT,	120 )
		vbs.Add( self.mapSummary, 1, flag=wx.ALL|wx.EXPAND, border = border )
		
		vbs.Add( self.initCategoriesFromExcel, 0, flag=wx.ALL, border=8 )
		
		self.SetSizer( vbs )
	
	def setExpectedFieldCol( self, fieldCol ):
		self.expectedFieldCol = copy.copy(fieldCol)
	
	def setFileNameSheetName( self, fileName, sheetName ):
		self.headers, fieldCol = getDefaultFieldMap( fileName, sheetName, self.expectedFieldCol )
		iNoMatch = len(self.headers) - 1
		for c, f in enumerate(Fields):
			self.choices[c].Clear()
			self.choices[c].AppendItems( self.headers )
			self.choices[c].SetSelection( fieldCol[f] )
			self.choices[c].Bind( wx.EVT_CHOICE, self.doUpdateSummary )

		self.gs.Layout()
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling( scroll_y = False )
		self.doUpdateSummary()

	def doUpdateSummary( self, event = None ):
		self.mapSummary.DeleteAllItems()
		GetTranslation = _
		for c, f in enumerate(Fields):
			r = self.mapSummary.InsertItem( 999999, GetTranslation(f) )
			self.mapSummary.SetItem( r, 1, self.choices[c].GetStringSelection() )
		
	def getFieldCol( self ):
		headerLen = len(self.headers) - 1
		fieldCol = {}
		for c, f in enumerate(Fields):
			s = self.choices[c].GetSelection()
			fieldCol[f] = s if s < headerLen else -1
		return fieldCol
		
	def hasTagField( self ):
		fieldCol = self.getFieldCol()
		return any( fieldCol.get(tf,-1) >= 0 for tf in TagFields )
			
class SummaryPage(adv.WizardPageSimple):
	def __init__(self, parent):
		adv.WizardPageSimple.__init__(self, parent)
		
		self.errors = []
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label=u'{}'.format(_('Summary'))), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label=u' '), flag=wx.ALL, border = border )

		rows = 0
		
		self.fileLabel = wx.StaticText( self, label=u'{}:'.format(_('Excel File')) )
		self.fileName = wx.StaticText( self )
		rows += 1

		self.sheetLabel = wx.StaticText( self, label=u'{}:'.format(_('Sheet Name')) )
		self.sheetName = wx.StaticText( self )
		rows += 1

		self.riderLabel = wx.StaticText( self, label=u'{}:'.format(_('Rider Data Entries')) )
		self.riderNumber = wx.StaticText( self )
		rows += 1

		self.getCategoriesFromCategoriesLabel = wx.StaticText( self, label=u'{}:'.format(_('CrossMgr Categories from Excel EventCategory/CustomCategory')) )
		self.initCategoriesFromExcel = wx.StaticText( self )
		rows += 1

		self.categoryAndPropertiesLabel = wx.StaticText( self, label=u'{}:'.format(_('Categories and Properties')) )
		self.categoryAndProperties = wx.StaticText( self )
		rows += 1

		self.statusLabel = wx.StaticText( self, label=u'{}:'.format(_('Status')) )
		self.statusName = wx.StaticText( self )
		rows += 1

		self.errorLabel = wx.StaticText( self, label=u'{}:'.format(_('Errors')) )
		self.errorName = wx.TextCtrl( self, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(-1,128) )
		rows += 1
		
		self.copyErrorsToClipboard = wx.Button( self, label = _('Copy Errors to Clipboard') )
		self.copyErrorsToClipboard.Bind( wx.EVT_BUTTON, self.doCopyErrorsToClipboard )
		rows += 1

		fbs = wx.GridBagSizer( hgap=2, vgap=1 )
		
		labelAlign = wx.ALIGN_RIGHT
		fieldAlign = wx.EXPAND|wx.GROW
		blank = lambda : None
		
		labelFieldFormats = [
					  (self.fileLabel, 0, labelAlign),		(self.fileName, 	1, fieldAlign),
					  (self.sheetLabel, 0, labelAlign),		(self.sheetName, 	1, fieldAlign),
					  (self.riderLabel, 0, labelAlign),		(self.riderNumber,	1, fieldAlign),
					  (self.getCategoriesFromCategoriesLabel, 0, labelAlign),		(self.initCategoriesFromExcel,	1, fieldAlign),
					  (self.categoryAndPropertiesLabel, 0, labelAlign),		(self.categoryAndProperties,	1, fieldAlign),
					  (self.statusLabel, 0, labelAlign),	(self.statusName,	1, fieldAlign),
					  (self.errorLabel, 0, labelAlign),		(self.errorName,	1, fieldAlign),
					  (blank(), 0, labelAlign),				(self.copyErrorsToClipboard,	1, fieldAlign),
					 ]
		
		row = 0
		for i, (item, column, flag) in enumerate(labelFieldFormats):
			if not item:
				continue
			if column == 1:
				flag |= wx.EXPAND
			if item == self.errorName:
				fbs.Add( item, pos=(row, 1), span=(1,1), flag=flag )
				row += 1
			else:
				fbs.Add( item, pos=(row, column), span=(1,1), flag=flag )
				if column == 1:
					row += 1
		
		vbs.Add( fbs )
		
		self.SetSizer(vbs)
		
	def doCopyErrorsToClipboard( self, event ):
		if not self.errors:
			return
			
		clipboard = wx.Clipboard.Get()
		if not clipboard.IsOpened():
			clipboard.Open()
			clipboard.SetData( wx.TextDataObject('\n'.join( err for num, err in self.errors )) )
			clipboard.Close()
			Utils.MessageOK( self, _('Excel Errors Copied to Clipboard.'), _('Excel Errors Copied to Clipboard') )

	def setFileNameSheetNameInfo( self,
			fileName, sheetName, info, errors, headerMap,
			hasCategoriesSheet, hasPropertiesSheet, initCategoriesFromExcel ):
			
		self.fileName.SetLabel( fileName )
		self.sheetName.SetLabel( sheetName )
		cp = []
		if hasCategoriesSheet:
			cp.append( _('Read Categories') )
		if hasPropertiesSheet:
			cp.append( _('Read Properties') )
		self.categoryAndProperties.SetLabel( u', '.join(cp) )
		
		self.initCategoriesFromExcel.SetLabel( _('Yes') if initCategoriesFromExcel else _('No') )
		
		self.errors = errors
		
		try:
			infoLen = len(info)
		except TypeError:
			infoLen = 0
		self.riderNumber.SetLabel( '{}'.format(infoLen) )
		
		errStr = '\n'.join( [err for num, err in errors] if errors else ['None'] )
		
		self.statusName.SetLabel( _('Success!') if infoLen and not errors else u'{} {}'.format(len(errors), _('Error') if len(errors) == 1 else _('Errors')) )
		self.errorName.SetValue( errStr )
		
		self.copyErrorsToClipboard.Enable( bool(self.errors) )
		
		self.Layout()
		
		if hasPropertiesSheet and Utils.getMainWin():
			mainWin = Utils.getMainWin()
			wx.CallAfter( mainWin.showPage, mainWin.iPropertiesPage )
	
class GetExcelLink:
	def __init__( self, parent, excelLink = None ):
		img_filename = os.path.join( Utils.getImageFolder(), '20100718-Excel_icon.png' )
		img = wx.Bitmap(img_filename) if img_filename and os.path.exists(img_filename) else wx.NullBitmap
		
		self.wizard = adv.Wizard()
		self.wizard.SetExtraStyle( adv.WIZARD_EX_HELPBUTTON )
		self.wizard.Create( parent, wx.ID_ANY, _('Define Excel Link'), img )
		self.wizard.Bind( adv.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		self.wizard.Bind( adv.EVT_WIZARD_HELP,
			lambda evt: HelpSearch.showHelp('Menu-DataMgmt.html#link-to-external-excel-data') )
		
		self.fileNamePage = FileNamePage( self.wizard )
		self.sheetNamePage = SheetNamePage( self.wizard )
		self.headerNamesPage = HeaderNamesPage( self.wizard )
		self.summaryPage = SummaryPage( self.wizard )
		
		adv.WizardPageSimple.Chain( self.fileNamePage, self.sheetNamePage )
		adv.WizardPageSimple.Chain( self.sheetNamePage, self.headerNamesPage )
		adv.WizardPageSimple.Chain( self.headerNamesPage, self.summaryPage )
		
		self.excelLink = excelLink
		if excelLink:
			if excelLink.fileName:
				self.fileNamePage.setFileName( excelLink.fileName )
			if excelLink.sheetName:
				self.sheetNamePage.setExpectedSheetName( excelLink.sheetName )
			if excelLink.fieldCol:
				self.headerNamesPage.setExpectedFieldCol( excelLink.fieldCol )

		self.wizard.GetPageAreaSizer().Add( self.fileNamePage )
		self.wizard.SetPageSize( wx.Size(800,560) )
		self.wizard.FitToPage( self.fileNamePage )
	
	def show( self ):
		if self.wizard.RunWizard(self.fileNamePage):
			if not self.excelLink:
				self.excelLink = ExcelLink()
			self.excelLink.setFileName( self.fileNamePage.getFileName() )
			self.excelLink.setSheetName( self.sheetNamePage.getSheetName() )
			self.excelLink.setFieldCol( self.headerNamesPage.getFieldCol() )
			self.excelLink.initCategoriesFromExcel = self.headerNamesPage.initCategoriesFromExcel.GetValue()
		return self.excelLink
	
	def onPageChanging( self, evt ):
		isForward = evt.GetDirection()
		GetTranslation = _
		if isForward:
			page = evt.GetPage()
			if page == self.fileNamePage:
				fileName = self.fileNamePage.getFileName()
				try:
					open(fileName).close()
					self.sheetNamePage.setFileName(self.fileNamePage.getFileName())
				except IOError:
					if fileName == '':
						message = _('Please specify an Excel file.')
					else:
						message = u'{}\n\n   "{}".\n\n{}'.format(
							_('Cannot open file'),
							fileName,
							_('Please check the file name and/or its read permissions.'),
						)
					Utils.MessageOK( self.wizard, message, title=_('File Open Error'), iconMask=wx.ICON_ERROR)
					evt.Veto()
			elif page == self.sheetNamePage:
				try:
					self.headerNamesPage.setFileNameSheetName(self.fileNamePage.getFileName(), self.sheetNamePage.getSheetName())
				except ValueError:
					Utils.MessageOK(
						self.wizard, u'\n'.join( [_('Cannot find at least 5 header names in the Excel sheet.'), _('Check the format.')] ),
						title=_('Excel Format Error'), iconMask=wx.ICON_ERROR)
					evt.Veto()
			elif page == self.headerNamesPage:
				if Model.race and Model.race.enableJChipIntegration and not self.headerNamesPage.hasTagField():
					if Utils.MessageOKCancel(
							self.wizard, u'{}\n\n{}'.format(_('No RFID Tag Columns Specified.'),_('Fix it now?')),
							title=_('No RFID Tag Columns'), iconMask=wx.ICON_ERROR):
						evt.Veto()
						return
				
				excelLink = ExcelLink()
				excelLink.setFileName( self.fileNamePage.getFileName() )
				excelLink.setSheetName( self.sheetNamePage.getSheetName() )
				excelLink.initCategoriesFromExcel = self.headerNamesPage.initCategoriesFromExcel.GetValue()
				fieldCol = self.headerNamesPage.getFieldCol()
				if fieldCol[Fields[0]] < 0:
					Utils.MessageOK( self.wizard, u'{}: "{}"'.format(_('You must specify column'), GetTranslation(Fields[0])),
										title=_('Excel Format Error'), iconMask=wx.ICON_ERROR)
					evt.Veto()
				else:
					excelLink.setFieldCol( fieldCol )
					try:
						info = excelLink.read()
						errors = excelLink.getErrors()
						headerMap = []
						for f in Fields:
							i = excelLink.fieldCol.get( f, 0 )
							if i >= 0:
								headerMap.append( (f, self.headerNamesPage.headers[i]) )
						self.summaryPage.setFileNameSheetNameInfo(
							self.fileNamePage.getFileName(),
							self.sheetNamePage.getSheetName(),
							info, errors, headerMap,
							excelLink.hasCategoriesSheet, excelLink.hasPropertiesSheet,
							excelLink.initCategoriesFromExcel,
						)
					except ValueError as e:
						Utils.MessageOK(self.wizard, u'{}\n{}\n\n"{}"'.format(
												_('Problem extracting rider info.'),
												_('Check the Excel format.'),
												e,
											),
										title=_('Data Error'), iconMask=wx.ICON_ERROR)
						evt.Veto()
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
#----------------------------------------------------------------------------------

JChipTagLength = 6
OrionTagLength = 16

trantab = str.maketrans( 'lOo', '100', ' \t\n\r' ) # Translate lower-case l's to ones and Os to zeros. Also, remove any extra spaces.
def GetCleanTag( tag ):
	return '{}'.format(tag).translate(trantab)

def FixJChipTag( tag ):
	return GetCleanTag(tag).zfill(JChipTagLength)
	
def FixOrionTag( tag ):
	return GetCleanTag(tag).zfill(OrionTagLength)

def GetFixTag( externalInfo ):
	# Check if we have JChip or Orion tags.
	countJChip, countOrion = 0, 0
	for num, edata in externalInfo.items():
		for tagName in TagFields:
			try:
				tag = edata[tagName]
			except (KeyError, ValueError):
				continue
			try:
				int( GetCleanTag(tag), 10 )		# Orion tags are all numeric, but some JChip tags might also be all numeric.
				countOrion += 1
			except ValueError:					# JChip tags are hex, so int() base 10 fails.
				countJChip += 1
	
	# Assign the tag to the greatest number of matches as some JChip tags might be all numeric.
	return FixJChipTag if countJChip >= countOrion else FixOrionTag

def FixTagFormat( externalInfo ):
	fixTagFunc = GetFixTag( externalInfo )
	for num, edata in externalInfo.items():
		for tagName in TagFields:
			try:
				tag = edata[tagName]
			except (KeyError, ValueError):
				continue
			edata[tagName] = fixTagFunc( tag )

def GetTagNums( forceUpdate = False ):
	race = Model.race
	if not race:
		return {}
		
	# Get the linked external data.
	try:
		excelLink = race.excelLink
	except:
		race.tagNums = {}
	else:
		try:
			externalInfo = excelLink.read()
		except:
			race.tagNums = {}
		else:
			if excelLink.readFromFile or not getattr(race, 'tagNums', None) or forceUpdate:
				race.tagNums = {}
				for tagName in TagFields:
					if excelLink.hasField( tagName ):
						tn = {}
						for num, edata in externalInfo.items():
							try:
								tag = Utils.removeDiacritic('{}'.format(edata[tagName] or '')).lstrip('0').upper()
							except (KeyError, ValueError):
								continue
							if tag:
								tn[tag] = num
						race.tagNums.update( tn )
	return race.tagNums

def UnmatchedTagsUpdate():
	race = Model.race
	if not race or not race.unmatchedTags:
		return
	
	tagNums = GetTagNums( forceUpdate=True )
	tagsFound = False
	for tag, times in race.unmatchedTags.items():
		try:
			num = tagNums[tag]
		except KeyError:
			continue
		
		for t in times:
			race.addTime( num, t )
		tagsFound = True
	
	if tagsFound:
		race.unmatchedTags = { tag: times for tag, times in race.unmatchedTags.items() if tag not in tagNums }
	
#-----------------------------------------------------------------------------------------------------
# Cache the Excel sheet so we don't have to re-read if it has not changed.
stateCache = None
infoCache = None
errorCache = None

def ResetExcelLinkCache():
	global stateCache
	global infoCache
	global errorCache
	stateCache = None
	infoCache = None
	errorCache = None

class ExcelLink:
	OpenCode = 0
	MenCode = 1
	WomenCode = 2

	hasCategoriesSheet = False
	hasPropertiesSheet = False
	
	initCategoriesFromExcel = False
	
	def __init__( self ):
		self.fileName = None
		self.sheetName = None
		self.readFromFile = True
		self.fieldCol = dict( (f, c) for c, f in enumerate(Fields) )
	
	def key( self ):
		return (self.fileName, self.sheetName, self.fieldCol)
	
	def __eq__(self, other):
		return self.key() == other.key()

	def __ne__(self, other):
		return self.key() != other.key()

	def __lt__(self, other):
		return self.key() < other.key()

	def __le__(self, other):
		return self.key() <= other.key()

	def __gt__(self, other):
		return self.key() > other.key()

	def __ge__(self, other):
		return self.key() >= other.key()
		
	def setFileName( self, fname ):
		self.fileName = fname
		
	def setSheetName( self, sname ):
		self.sheetName = sname
	
	def setFieldCol( self, fieldCol ):
		self.fieldCol = fieldCol
		
	def bindDefaultFieldCols( self ):
		headers, fieldCol = getDefaultFieldMap( self.fileName, self.sheetName )
		iNoMatch = len(headers) - 1
		self.fieldCol = { f: fieldCol[f] if fieldCol[f] != iNoMatch else -1 for f in fieldCol }

	def hasField( self, field ):
		return self.fieldCol.get( field, -1 ) >= 0
		
	def getFields( self ):
		return [f for f in Fields if self.hasField(f)]
	
	def get( self ):
		# Check the cache, but don't bother with the modification date of the file for performance.
		global stateCache
		global infoCache
		if stateCache and infoCache:
			try:
				state = (self.fileName, self.sheetName, self.fieldCol)
				if state == stateCache[-3:]:
					return infoCache
			except:
				pass
		return None
	
	def getErrors( self ):
		global errorCache
		self.read()
		return errorCache
		
	def isSynced( self ):
		global stateCache
		try:
			state = (os.path.getmtime(self.fileName), self.fileName, self.sheetName, self.fieldCol)
			return state == stateCache
		except:
			return False
	
	reVersionField = re.compile( '^(.+) \(([0-9]+)\)\.(?:xls|xlsx|xlsm)$', re.IGNORECASE )
	def getMostRecentFilename( self ):
		dirname, basename = os.path.split(self.fileName)
		
		m = ExcelLink.reVersionField.match( basename )
		nameCur = m.group(1) if m else basename.splitext()[0]
		versionCur = int(m.group(2)) if m else 0
		
		mostRecentFilename = None
		for f in os.listdir(dirname):
			m = ExcelLink.reVersionField.match( f )
			if not m or m.group(1) != nameCur:
				continue
			version = int(m.group(2))
			if version > versionCur:
				versionCur = version
				mostRecentFilename = f
		return os.path.join(dirname, mostRecentFilename) if mostRecentFilename else None
	
	def updateFilenameToMostRecent( self ):
		self.fileName = (self.getMostRecentFilename() or self.fileName)
		
	def read( self, alwaysReturnCache = False ):
		# Check the cache.  Return the last info if the file has not been modified, and the name, sheet and fields are the same.
		global stateCache
		global infoCache
		global errorCache
		
		self.readFromFile = False
		if alwaysReturnCache and infoCache is not None:
			return infoCache

		if stateCache and infoCache:
			try:
				state = (os.path.getmtime(self.fileName), self.fileName, self.sheetName, self.fieldCol)
				if state == stateCache:
					return infoCache
			except:
				pass
	
		# Read the sheet and return the rider data.
		self.readFromFile = True
		try:
			reader = GetExcelReader( self.fileName )
			if self.sheetName not in reader.sheet_names():
				infoCache = {}
				errorCache = []
				return {}
		except (IOError, ValueError):
			infoCache = {}
			errorCache = []
			return {}
		
		info = {}
		rowInfo = []
		hasTags = False
		
		for r, row in enumerate(reader.iter_list(self.sheetName)):
			data = {}
			for field, col in self.fieldCol.items():
				if col < 0:					# Skip unmapped columns.
					continue
				try:
					try:
						data[field] = row[col].strip()
					except AttributeError:
						data[field] = row[col]
					
					if data[field] == None:
						data[field] = u''
						
					if field == 'LastName':
						try:
							data[field] = '{}'.format(data[field] or '').upper()
						except:
							data[field] = _('Unknown')
					elif field.startswith('Tag'):
						try:
							data[field] = int( data[field] )
						except (ValueError, TypeError):
							pass
						try:
							data[field] = '{}'.format(data[field] or '').upper()
							hasTags = True
						except:
							pass
					elif field == 'Gender':
						# Normalize and encode the gender information.
						try:
							genderFirstChar = '{}'.format(data[field] or 'Open').strip().lower()[:1]
							if genderFirstChar in 'mhu':	# Men, Male, Hommes, Uomini
								data[field] = 'Men'
							elif genderFirstChar in 'wlfd':	# Women, Ladies, Female, Femmes, Donne
								data[field] = 'Women'
							else:
								data[field] = 'Open'		# Otherwise Open
						except:
							data[field] = 'Open'
							pass
					else:
						if field in NumericFields:
							try:
								data[field] = float(data[field])
								if data[field] == int(data[field]):
									data[field] = int(data[field])
							except ValueError:
								data[field] = 0
						else:
							data[field] = '{}'.format(data[field])
						
				except IndexError:
					pass
			
			try:
				num = int(float(data[Fields[0]]))
			except (ValueError, TypeError, KeyError) as e:
				pass
			else:
				data[Fields[0]] = num
				info[num] = data
				rowInfo.append( (r+1, num, data) )	# Add one to the row to make error reporting consistent.
			
		# Fix all the tag formats
		FixTagFormat( info )
		
		# Check for duplicate numbers, duplicate tags and missing tags.
		numRow = {}
		
		# Collect how many tag fields we have.
		tagFields = []
		if hasTags:
			for tf in TagFields:
				if self.fieldCol.get(tf, -1) >= 0:
					tagFields.append( (tf, {}) )
			
		errors = []
		rowBib = {}
		for row, num, data in rowInfo:
			rowBib[row] = num
			
			if num in numRow:
				errors.append( (
						num,
						u'{}: {}  {}: {}  {} {}.'.format(
							_('Row'), row,
							_('Duplicate Bib#'), num,
							_('Same as row'), numRow[num],
						)
					)
				)
			else:
				numRow[num] = row
				
			for tField, tRow in tagFields:
				if tField not in data and tField == 'Tag':		# Don't check for missing Tag2s as they are optional.
					errors.append( (
							num,
							u'{}: {}  {}: {}  {}: {}'.format(
								_('Row'), row,
								_('Bib'), num, 
								_('Missing field'), tField,
							)
						)
					)
					continue
					
				tag = '{}'.format(data.get(tField,u'')).lstrip('0').upper()
				if tag:
					if tag in tRow:
						errors.append( (
								num,
								u'{}: {}  {}: {} {}.  {} {}: {}  {}: {}'.format(
									_('Row'), row,
									_('Duplicate Field'), tField, tag,
									_('Same as'),
									_('Bib'), rowBib[tRow[tag]],
									_('Row'), tRow[tag]
								)
							)
						)
					else:
						tRow[tag] = row
				else:
					if tField == 'Tag':					# Don't check for empty Tag2s as they are optional.
						errors.append( (
								num,
								u'{}: {}  {}: {}  {}: {}'.format(
									_('Row'), row,
									_('Bib'), num,
									_('Missing Field'), tField,
								)
							)
						)
		
		stateCache = (os.path.getmtime(self.fileName), self.fileName, self.sheetName, self.fieldCol)
		infoCache = info
		errorCache = errors
		
		# Clear the tagNums cache
		try:
			Model.race.tagNums = None
		except AttributeError:
			pass
		
		# Do not read properties or categories after the race has started to avoid overwriting local changes.
		if Model.race and Model.race.startTime:
			self.hasPropertiesSheet = False
			self.hasCategoriesSheet = False
			UnmatchedTagsUpdate()
		else:
			self.hasPropertiesSheet = ReadPropertiesFromExcel( reader )
			self.hasCategoriesSheet = ReadCategoriesFromExcel( reader )
			
		if not self.hasCategoriesSheet and self.initCategoriesFromExcel and (
				self.hasField('EventCategory') or any( self.hasField(f) for f in CustomCategoryFields )):
			MatchingCategory.PrologMatchingCategory()
			for bib, fields in infoCache.items():
				MatchingCategory.AddToMatchingCategory( bib, fields )
			MatchingCategory.EpilogMatchingCategory()
			
		try:
			Model.race.resetAllCaches()
		except:
			pass
		
		return infoCache

def IsValidRaceDBExcel( fileName ):
	try:
		reader = GetExcelReader( fileName )
	except:
		return False
	for sheetName in ['Registration', PropertySheetName, CategorySheetName]:
		if sheetName not in reader.sheet_names():
			return False
	return True

def HasExcelLink( race ):
	try:
		externalInfo = race.excelLink.read()
		return True
	except Exception as e:
		#Utils.logException( e, sys.exc_info() )
		return False

def SyncExcelLink( race ):
	return HasExcelLink( race )

#-----------------------------------------------------------------------------------------------------

reSeparators = re.compile( r'[,;:.]+' )
class BibInfo:
	AllFields = (
		'Name',
		'License',
		'UCIID',
		'Team',
		'Wave',
	)
	def __init__( self ):
		self.race = Model.race
		excelLink = getattr(self.race, 'excelLink', None)
		if excelLink:
			self.externalInfo = excelLink.read()
			self.fields = ['Name'] + [f for f in self.AllFields if excelLink.hasField(f)] + ['Wave']
		else:
			self.externalInfo = {}
			self.fields = []
			
	def getData( self, bib ):
		try:
			bib = int(bib)
		except:
			return {}
		
		try:
			data = { k:'{}'.format(v) for k, v in self.externalInfo.get(bib, {}).items() }
		except ValueError:
			data = {}
		
		data['Name'] = u', '.join( v for v in (data.get('LastName',None), data.get('FirstName',None)) if v )
		
		category = self.race.getCategory( bib )
		data['Wave'] = category.name if category else u''
		return data
		
	def bibField( self, bib ):
		data = self.getData( bib )
		if not data:
			return '{}'.format(bib)
		values = [(u'<strong>{}</strong>' if 'Name' in f else u'{}').format(cgi.escape(data[f])) for f in self.fields if data.get(f, None)]
		return u'{}: {}'.format(bib, u', '.join(values))
	
	def bibList( self, bibs ):
		bibs = [b for b in bibs if b]
		html = StringIO()
		with tag( html, 'ul', 'bibList' ):
			for bib in bibs:
				with tag( html, 'li' ):
					html.write( self.bibField(bib) )
		return html.getvalue()
	
	def bibTable( self, bibs ):
		bibs = [b for b in bibs if b]
		if not bibs:
			return '<br/>'
		GetTranslation = _
		html = StringIO()
		with tag( html, 'table', 'bibTable' ):
			with tag( html, 'thead' ):
				with tag( html, 'tr' ):
					for f in ['Bib#'] + self.fields:
						with tag( html, 'th', {'style':"text-align:left"} if 'Bib' in f else {'style':"text-align:left"} ):
							html.write( GetTranslation(f) )
			with tag( html, 'tbody' ):
				for bib in bibs:
					with tag( html, 'tr' ):
						data = self.getData( bib )
						with tag( html, 'td', {'style':"text-align:right"} ):
							html.write( '{}'.format(bib) )
						for f in self.fields:
							with tag( html, 'td', {'style':"text-align:left"}):
								if 'Name' in f:
									with tag( html,'strong'):
										html.write( cgi.escape(data.get(f,u'')) )
								else:
									html.write( cgi.escape(data.get(f,u'')) )
		return html.getvalue()
		
	def getSubValue( self, subkey ):
		if subkey.startswith('BibTable'):					# {=BibTable 132,110,98}
			return self.bibTable( reSeparators.sub(u' ', subkey).split()[1:] )
		elif subkey.startswith('BibList'):					# {=BibList 132,110,98}
			return self.bibList( reSeparators.sub(u' ', subkey).split()[1:] )
		elif subkey.startswith('Bib'):						# {=Bib 111}
			return self.bibField( u' '.join(reSeparators.sub(u' ', subkey).split()[1:]) )
		return None

if __name__ == '__main__':
	print( Utils.approximateMatch("Team", "Last Name") )
	race = Model.newRace()
	race._populate()
	race.enableJChipIntegration = True
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,300))
	excelLink = GetExcelLink(mainWin)
	mainWin.Show()
	excelLink.show()
	app.MainLoop()
