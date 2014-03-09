from __future__ import print_function

import wx
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.scrolledpanel as scrolled
import wx.wizard as wiz
import os
import copy
import string
import Utils
import Model
from Excel import GetExcelReader
from ReadCategoriesFromExcel import ReadCategoriesFromExcel
from ReadPropertiesFromExcel import ReadPropertiesFromExcel

#-----------------------------------------------------------------------------------------------------
Fields = [	_('Bib#'),
			_('LastName'), _('FirstName'),
			_('Team'),
			_('Nat.'), _('State'), _('Prov.'), _('City'),
			_('Category'), _('Age'), _('Gender'),
			_('License'),
			_('UCICode'),
			_('Tag'), _('Tag2')]
IgnoreFields = [_('Bib#'), _('Tag'), _('Tag2'), _('Gender')]		# Fields to ignore when adding data to standard reports.
ReportFields = [f for f in Fields if f not in IgnoreFields]

mapFmt = u'{:15}\t\u2192   {}'

class FileNamePage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Specify the Excel Sign-on File containing the additional rider information.')),
					flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = _('Each race must be in a separate sheet.')), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = _('See documentation for examples.')), flag=wx.ALL, border = border )
		fileMask = [
			'Excel Worksheets (*.xlsx;*.xlsm;*.xls)|*.xlsx;*.xlsm;*.xls',
		]
		self.fbb = filebrowse.FileBrowseButton( self, -1, size=(450, -1),
												labelText = _('Excel Workbook:'),
												fileMode=wx.OPEN,
												fileMask='|'.join(fileMask) )
		vbs.Add( self.fbb, flag=wx.ALL, border = border )
		
		self.SetSizer( vbs )
	
	def setFileName( self, fileName ):
		self.fbb.SetValue( fileName )
	
	def getFileName( self ):
		return self.fbb.GetValue()
	
class SheetNamePage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
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
	
class HeaderNamesPage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)

		self.expectedFieldCol = None
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Specify the spreadsheet columns corresponding to CrossMgr fields.')),
				flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = _('Set missing fields to blank.')),
				flag=wx.ALL, border = border )
		vbs.AddSpacer( 8 )
				
		border = 4
		# Create a map for the field names we are looking for
		# and the headers we found in the Excel sheet.
		sp = scrolled.ScrolledPanel( self, size=(750, 64), style = wx.TAB_TRAVERSAL )
		
		boldFont = None
		
		gs = wx.GridSizer( 2, len(Fields) )
		for c, f in enumerate(Fields):
			label = wx.StaticText(sp, label=f)
			if boldFont is None:
				font = label.GetFont()
				fontSize = label.GetFont()
				boldFont = wx.Font( font.GetPointSize()+1, font.GetFamily(), font.GetStyle(), wx.FONTWEIGHT_BOLD )
			label.SetFont( boldFont )
			gs.Add( label )
		
		self.headers = []
		self.choices = []
		for c, f in enumerate(Fields):
			self.choices.append( wx.Choice(sp, -1, choices = self.headers ) )
			gs.Add( self.choices[-1] )
		
		sp.SetSizer( gs )
		sp.SetAutoLayout(1)
		sp.SetupScrolling( scroll_y = False )
		self.sp = sp
		self.gs = gs
		vbs.Add( sp, flag=wx.ALL, border = border )
		
		self.mapSummary = wx.TextCtrl( self, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(-1,128) )
		vbs.Add( self.mapSummary, 1, flag=wx.ALL|wx.EXPAND, border = border )
		
		self.SetSizer( vbs )
	
	def setExpectedFieldCol( self, fieldCol ):
		self.expectedFieldCol = copy.copy(fieldCol)
	
	def setFileNameSheetName( self, fileName, sheetName ):
		reader = GetExcelReader( fileName )
		self.headers = None
		
		# Try to find the header columns.
		# Look for the first row with more than 4 columns.
		for r, row in enumerate(reader.iter_list(sheetName)):
			cols = sum( 1 for d in row if d and unicode(d).strip() )
			if cols > 4:
				self.headers = [unicode(h or '').strip() for h in row]
				break

		# If we haven't found a header row yet, assume the first non-empty row is the header.
		if not self.headers:
			for r, row in enumerate(reader.iter_list(sheetName)):
				cols = sum( 1 for d in row if d and unicode(d).strip() )
				if cols > 0:
					self.headers = [unicode(h or '').strip() for h in row]
					break
		
		# Ignore empty columns on the end.
		while self.headers and (not self.headers[-1] or self.headers[-1].isspace()):
			self.headers.pop()
			
		if not self.headers:
			raise ValueError, _('Could not find a Header Row {}::{}.').format(fileName, sheetName)
		
		# Rename empty columns so as not to confuse the user.
		self.headers = [h if h else _('BlankHeaderName%03d') % (c+1) for c, h in enumerate(self.headers)]
		
		# Set a blank final entry.
		self.headers.append( '' )
			
		# Create a map for the field names we are looking for
		# and the self.headers we found in the Excel sheet.
		for c, f in enumerate(Fields):
			# Figure out some reasonable defaults for self.headers.
			iBest = len(self.headers) - 1
			matchBest = 0.0
			for i, h in enumerate(self.headers):
				matchCur = Utils.approximateMatch(f, h)
				if matchCur > matchBest:
					matchBest = matchCur
					iBest = i
			# If we don't get a high enough match, set to blank.
			if matchBest <= 0.34:
				try:
					iBest = min( self.expectedFieldCol[h], len(self.headers) - 1 )
				except (TypeError, KeyError):
					iBest = len(self.headers) - 1
			self.choices[c].Clear()
			self.choices[c].AppendItems( self.headers )
			self.choices[c].SetSelection( iBest )
			self.choices[c].Bind( wx.EVT_CHOICE, self.doUpdateSummary )

		self.gs.Layout()
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling( scroll_y = False )
		self.doUpdateSummary()

	def doUpdateSummary( self, event = None ):
		mapStr = mapFmt.format( 'CrossMgr', _('Spreadsheet') )
		mapStr += '\n\n'

		map = [(f, self.choices[c].GetStringSelection()) for c, f in enumerate(Fields)]
		mapStr += '\n'.join( mapFmt.format(a, b) for a, b in map )
		
		self.mapSummary.SetValue( mapStr )
		
	def getFieldCol( self ):
		headerLen = len(self.headers) - 1
		fieldCol = {}
		for c, f in enumerate(Fields):
			s = self.choices[c].GetSelection()
			fieldCol[f] = s if s < headerLen else -1
		return fieldCol
			
class SummaryPage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		self.errors = []
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Summary:')), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = u' '), flag=wx.ALL, border = border )

		rows = 0
		
		self.fileLabel = wx.StaticText( self, label = _('Excel File:') )
		self.fileName = wx.StaticText( self )
		rows += 1

		self.sheetLabel = wx.StaticText( self, label = _('Sheet Name:') )
		self.sheetName = wx.StaticText( self )
		rows += 1

		self.riderLabel = wx.StaticText( self, label = _('Rider Data Entries:') )
		self.riderNumber = wx.StaticText( self )
		rows += 1

		self.statusLabel = wx.StaticText( self, label = _('Status:') )
		self.statusName = wx.StaticText( self )
		rows += 1

		self.errorLabel = wx.StaticText( self, label =  _('Errors:') )
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

	def setFileNameSheetNameInfo( self, fileName, sheetName, info, errors, headerMap ):
		self.fileName.SetLabel( fileName )
		self.sheetName.SetLabel( sheetName )
		self.errors = errors
		
		try:
			infoLen = len(info)
		except TypeError:
			infoLen = 0
		self.riderNumber.SetLabel( '{}'.format(infoLen) )
		
		errStr = '\n'.join( [err for num, err in errors] if errors else ['None'] )
		
		errStr += '\n\n' + mapFmt.format( 'CrossMgr', _('Spreadsheet') )
		errStr += '\n\n'
		headerMapStr = '\n'.join( mapFmt.format( _(f), h ) for f, h in headerMap )
		errStr += headerMapStr
		
		self.statusName.SetLabel( _('Success!') if infoLen and not errors else _('{num} Error(s)').format( num=len(errors) ) )
		self.errorName.SetValue( errStr )
		
		self.copyErrorsToClipboard.Enable( bool(self.errors) )
		
		self.Layout()
	
class GetExcelLink( object ):
	def __init__( self, parent, excelLink = None ):
		img_filename = os.path.join( Utils.getImageFolder(), '20100718-Excel_icon.png' )
		img = wx.Bitmap(img_filename) if img_filename and os.path.exists(img_filename) else wx.NullBitmap
		
		prewizard = wiz.PreWizard()
		prewizard.SetExtraStyle( wiz.WIZARD_EX_HELPBUTTON )
		prewizard.Create( parent, wx.ID_ANY, _('Define Excel Link'), img )
		self.wizard = prewizard
		self.wizard.Bind( wiz.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		self.wizard.Bind( wiz.EVT_WIZARD_HELP,
			lambda evt: Utils.showHelp('Menu-DataMgmt.html#link-to-external-excel-data') )
		
		self.fileNamePage = FileNamePage( self.wizard )
		self.sheetNamePage = SheetNamePage( self.wizard )
		self.headerNamesPage = HeaderNamesPage( self.wizard )
		self.summaryPage = SummaryPage( self.wizard )
		
		wiz.WizardPageSimple_Chain( self.fileNamePage, self.sheetNamePage )
		wiz.WizardPageSimple_Chain( self.sheetNamePage, self.headerNamesPage )
		wiz.WizardPageSimple_Chain( self.headerNamesPage, self.summaryPage )
		
		self.excelLink = excelLink
		if excelLink:
			if excelLink.fileName:
				self.fileNamePage.setFileName( excelLink.fileName )
			if excelLink.sheetName:
				self.sheetNamePage.setExpectedSheetName( excelLink.sheetName )
			if excelLink.fieldCol:
				self.headerNamesPage.setExpectedFieldCol( excelLink.fieldCol )

		self.wizard.GetPageAreaSizer().Add( self.fileNamePage )
		self.wizard.SetPageSize( wx.Size(800,400) )
		self.wizard.FitToPage( self.fileNamePage )
	
	def show( self ):
		if self.wizard.RunWizard(self.fileNamePage):
			if not self.excelLink:
				self.excelLink = ExcelLink()
			self.excelLink.setFileName( self.fileNamePage.getFileName() )
			self.excelLink.setSheetName( self.sheetNamePage.getSheetName() )
			self.excelLink.setFieldCol( self.headerNamesPage.getFieldCol() )
		return self.excelLink
	
	def onPageChanging( self, evt ):
		isForward = evt.GetDirection()
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
						message = _('Cannot open file "{}".\nPlease check the file name and/or its read permissions.').format(fileName)
					Utils.MessageOK( self.wizard, message, title=_('File Open Error'), iconMask=wx.ICON_ERROR)
					evt.Veto()
			elif page == self.sheetNamePage:
				try:
					self.headerNamesPage.setFileNameSheetName(self.fileNamePage.getFileName(), self.sheetNamePage.getSheetName())
				except ValueError:
					Utils.MessageOK( self.wizard, _('Cannot find at least 5 header names in the Excel sheet.\nCheck the format.'),
										title=_('Excel Format Error'), iconMask=wx.ICON_ERROR)
					evt.Veto()
			elif page == self.headerNamesPage:
				excelLink = ExcelLink()
				excelLink.setFileName( self.fileNamePage.getFileName() )
				excelLink.setSheetName( self.sheetNamePage.getSheetName() )
				fieldCol = self.headerNamesPage.getFieldCol()
				if fieldCol[Fields[0]] < 0:
					Utils.MessageOK( self.wizard, _('You must specify a "{}" column.').format(Fields[0]),
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
						self.summaryPage.setFileNameSheetNameInfo(self.fileNamePage.getFileName(), self.sheetNamePage.getSheetName(), info, errors, headerMap)
					except ValueError as e:
						Utils.MessageOK( self.wizard, _('Problem extracting rider info.\nCheck the Excel format.\n\n"{}"').format(e),
											title=_('Data Error'), iconMask=wx.ICON_ERROR)
						evt.Veto()
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
#----------------------------------------------------------------------------------

JChipTagLength = 6
OrionTagLength = 16

trantab = string.maketrans( 'lOo', '100' )	# Translate lower-case l's to ones and Os to zeros. 
def GetCleanTag( tag ):
	return str(tag).translate(trantab, ' \t\n\r')	# Also, remove any extra spaces.

def FixJChipTag( tag ):
	return GetCleanTag(tag).zfill(JChipTagLength)
	
def FixOrionTag( tag ):
	return GetCleanTag(tag).zfill(OrionTagLength)

def GetFixTag( externalInfo ):
	# Check if we have JChip or Orion tags.
	countJChip, countOrion = 0, 0
	for num, edata in externalInfo.iteritems():
		for tagName in ['Tag', 'Tag2']:
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
	for num, edata in externalInfo.iteritems():
		for tagName in ['Tag', 'Tag2']:
			try:
				tag = edata[tagName]
			except (KeyError, ValueError):
				continue
			edata[tagName] = fixTagFunc( tag )

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

class ExcelLink( object ):
	OpenCode = 0
	MenCode = 1
	WomenCode = 2

	def __init__( self ):
		self.fileName = None
		self.sheetName = None
		self.readFromFile = True
		self.fieldCol = dict( (f, c) for c, f in enumerate(Fields) )
	
	def __cmp__( self, e ):
		return cmp((self.fileName, self.sheetName, self.fieldCol), (e.fileName, e.sheetName, e.fieldCol))
	
	def setFileName( self, fname ):
		self.fileName = fname
		
	def setSheetName( self, sname ):
		self.sheetName = sname
	
	def setFieldCol( self, fieldCol ):
		self.fieldCol = fieldCol
		
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
		for r, row in enumerate(reader.iter_list(self.sheetName)):
			data = {}
			for field, col in self.fieldCol.iteritems():
				if col < 0:					# Skip unmapped columns.
					continue
				try:
					try:
						data[field] = row[col].strip()
					except AttributeError as e:
						data[field] = row[col]
					
					if data[field] == None:
						data[field] = ''
						
					if field == 'LastName':
						try:
							data[field] = unicode(data[field] or '').upper()
						except:
							pass
					elif field.startswith('Tag'):
						try:
							data[field] = int( data[field] )
						except (ValueError, TypeError) as e:
							pass
						try:
							data[field] = unicode(data[field] or '').upper()
						except:
							pass
					elif field == 'Gender':
						# Normalize and encode the gender information.
						genderFirstChar = unicode(data[field] or 'O').strip().upper()[:1]
						if genderFirstChar in 'MH':		# Men, Male, Hommes
							data[field] = 'M'
						elif genderFirstChar in 'WLF':	# Women, Ladies, Female, Femmes
							data[field] = 'F'
						else:
							data[field] = 'O'			# Otherwise Open
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
		
		tagFields = []
		if self.fieldCol.get('Tag', -1) >= 0:
			tagFields.append( ('Tag', {}) )
		if self.fieldCol.get('Tag2', -1) >= 0:
			tagFields.append( ('Tag2', {}) )
			
		errors = []
		rowBib = {}
		for row, num, data in rowInfo:
			rowBib[row] = num
			
			if num in numRow:
				errors.append( (num,
								_('Duplicate Bib# {num} in row {row} (same as Bib# in row {dupRow})').format(
									num=num, row=row, dupRow=numRow[num])) )
			else:
				numRow[num] = row
				
			for tField, tRow in tagFields:
				if tField not in data and tField == 'Tag':		# Don't check for missing Tag2s as they are optional.:
					errors.append( (num, _('Missing "{field}" in row {row} for Bib# {num}').format( field=tField, row=row, num=num)) )
					continue
					
				tag = unicode(data[tField] or '').lstrip('0').upper()
				if tag:
					if tag in tRow:
						errors.append( (num,
										_('Duplicate "{field}" {tag} for Bib# {num} in row {row} (same as "{field}" for Bib# {dupNum} in row {dupRow})').format(
											field=tField, tag=tag, num=num, row=row, dupNum = rowBib[tRow[tag]], dupRow=tRow[tag] ) ) )
					else:
						tRow[tag] = row
				else:
					if tField == 'Tag':					# Don't check for empty Tag2s as they are optional.
						errors.append( (num, _('Empty "{field}" in row {row} for Bib# {num}').format(field=tField, row=row, num=num)) )
		
		stateCache = (os.path.getmtime(self.fileName), self.fileName, self.sheetName, self.fieldCol)
		infoCache = info
		errorCache = errors
		
		# Clear the tagNums cache
		try:
			Model.race.tagNums = None
		except AttributeError:
			pass
		
		ReadCategoriesFromExcel( reader )
		ReadPropertiesFromExcel( reader )
		
		return infoCache

#-----------------------------------------------------------------------------------------------------

if __name__ == '__main__':
	print( Utils.approximateMatch("Team", "Last Name") )
	race = Model.newRace()
	race._populate()
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,300))
	excelLink = GetExcelLink(mainWin)
	mainWin.Show()
	excelLink.show()
	app.MainLoop()
