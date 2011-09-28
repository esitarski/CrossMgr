import xlrd
import os
import itertools
import unicodedata
import wx
import copy
import wx.lib.filebrowsebutton as filebrowse
import wx.wizard as wiz
import Utils

#-----------------------------------------------------------------------------------------------------
Fields = ['Bib#', 'LastName', 'FirstName', 'Team', 'License', 'Category', 'Tag']
IgnoreFields = ['Bib#', 'Tag']		# Fields to ignore when adding data to standard reports.

class FileNamePage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Specify the Excel Sign-on File containing the additional rider information.'),
					flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Each race must be in a separate sheet.'), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'See documentation for examples.'), flag=wx.ALL, border = border )
		self.fbb = filebrowse.FileBrowseButton( self, -1, size=(450, -1),
												labelText = 'Excel File:',
												fileMode=wx.OPEN,
												fileMask='Excel (*.xls)|*.xls' )
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
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Specify the sheet containing the information for this race:'),
				flag=wx.ALL, border = border )
		self.ch = wx.Choice( self, -1, choices = self.choices )
		vbs.Add( self.ch, flag=wx.ALL, border = border )
		self.SetSizer( vbs )
	
	def setFileName( self, fileName ):
		reader = readexcel( fileName )
		self.choices = reader.book.sheet_names()
		
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
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Specify the columns names corresponding to the CrossMgr fields.'),
				flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Set missing fields to blank.'),
				flag=wx.ALL, border = border )
				
		border = 4
		# Create a map for the field names we are looking for
		# and the headers we found in the Excel sheet.
		gs = wx.GridSizer( 2, len(Fields) )
		for c, f in enumerate(Fields):
			gs.Add( wx.StaticText(self, label=f) )
		
		self.headers = []
		self.choices = []
		for c, f in enumerate(Fields):
			self.choices.append( wx.Choice(self, -1, choices = self.headers ) )
			gs.Add( self.choices[-1] )
		
		vbs.Add( gs, flag=wx.ALL, border = border )
		
		self.SetSizer( vbs )
	
	def setExpectedFieldCol( self, fieldCol ):
		self.expectedFieldCol = copy.copy(fieldCol)
	
	def setFileNameSheetName( self, fileName, sheetName ):
		reader = readexcel( fileName )
		self.headers = None
		for r, row in enumerate(reader.iter_list(sheetName)):
			if sum( 1 for d in row if toAscii(d) ) > 4:
				self.headers = [toAscii(h) for h in row]
				break

		if not self.headers:
			raise ValueError, 'No headers found in %s::%s.' % (fileName, sheetName)
			
		# Set a blank final entry.
		self.headers.append( '' )
			
		# Create a map for the field names we are looking for
		# and the self.headers we found in the Excel sheet.
		for c, f in enumerate(Fields):
			# Figure out some reasonable defaults for the self.headers.
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
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Summary:'), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, ' '), flag=wx.ALL, border = border )

		rows = 0
		
		self.fileLabel = wx.StaticText( self, wx.ID_ANY, 'Excel File:' )
		self.fileName = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.sheetLabel = wx.StaticText( self, wx.ID_ANY, 'Sheet Name:' )
		self.sheetName = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.riderLabel = wx.StaticText( self, wx.ID_ANY, 'Rider Data Entries:' )
		self.riderNumber = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.statusLabel = wx.StaticText( self, wx.ID_ANY, 'Status:' )
		self.statusName = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		fbs = wx.FlexGridSizer( rows=rows, cols=2, hgap=5, vgap=2 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fbs.AddMany( [(self.fileLabel, 0, labelAlign),		(self.fileName, 	1, wx.EXPAND|wx.GROW),
					  (self.sheetLabel, 0, labelAlign),		(self.sheetName, 	1, wx.EXPAND|wx.GROW),
					  (self.riderLabel, 0, labelAlign),		(self.riderNumber,	1, wx.EXPAND|wx.GROW),
					  (self.statusLabel, 0, labelAlign),	(self.statusName,	1, wx.EXPAND|wx.GROW),
					 ] )
		fbs.AddGrowableCol( 1 )
		
		vbs.Add( fbs )
		
		self.SetSizer(vbs)
	
	def setFileNameSheetNameInfo( self, fileName, sheetName, info ):
		self.fileName.SetLabel( fileName )
		self.sheetName.SetLabel( sheetName )
		try:
			infoLen = len(info)
		except TypeError:
			infoLen = 0
		self.riderNumber.SetLabel( str(infoLen) )
		self.statusName.SetLabel( 'Success!' if infoLen else 'Failure' )
	
class GetExcelLink( object ):
	def __init__( self, parent, excelLink = None ):
		img_filename = os.path.join( Utils.getImageFolder(), '20100718-Excel_icon.png' )
		img = wx.Bitmap(img_filename) if img_filename and os.path.exists(img_filename) else wx.NullBitmap
		
		self.wizard = wiz.Wizard( parent, -1, 'Define Excel Link', img )
		self.wizard.Bind( wiz.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		
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
						message = 'Please specify an Excel file.'
					else:
						message = 'Cannot open file "%s".\nPlease check the file name and/or its read permissions.' % fileName
					Utils.MessageOK( self.wizard, message, title='File Open Error', iconMask=wx.ICON_ERROR)
					evt.Veto()
			elif page == self.sheetNamePage:
				try:
					self.headerNamesPage.setFileNameSheetName(self.fileNamePage.getFileName(), self.sheetNamePage.getSheetName())
				except ValueError:
					Utils.MessageOK( self.wizard, 'Cannot find headers in the Excel sheet.\nCheck the format.',
										title='Excel Format Error', iconMask=wx.ICON_ERROR)
					evt.Veto()
			elif page == self.headerNamesPage:
				excelLink = ExcelLink()
				excelLink.setFileName( self.fileNamePage.getFileName() )
				excelLink.setSheetName( self.sheetNamePage.getSheetName() )
				fieldCol = self.headerNamesPage.getFieldCol()
				if fieldCol[Fields[0]] < 0:
					Utils.MessageOK( self.wizard, 'You must specify a "%s" column.' % Fields[0],
										title='Excel Format Error', iconMask=wx.ICON_ERROR)
					evt.Veto()
				else:
					excelLink.setFieldCol( fieldCol )
					try:
						info = excelLink.read()
						self.summaryPage.setFileNameSheetNameInfo(self.fileNamePage.getFileName(), self.sheetNamePage.getSheetName(), info)
					except:
						Utils.MessageOK( self.wizard, 'Problem extracting rider info.\nCheck the Excel format.' % fileName,
											title='Data Error', iconMask=wx.ICON_ERROR)
						evt.Veto()
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
#-----------------------------------------------------------------------------------------------------

class ExcelLink( object ):
	def __init__( self ):
		self.fileName = None
		self.sheetName = None
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
		
	def read( self ):
		# Read the sheet and return the rider data.
		reader = readexcel( self.fileName )
		if self.sheetName not in reader.book.sheet_names():
			raise ValueError, "%s is not a valid sheetname" % self.sheetName
		
		info = {}
		for r, row in enumerate(reader.iter_list(self.sheetName)):
			data = {}
			for field, col in self.fieldCol.iteritems():
				if col < 0:					# Skip unmapped columns.
					continue
				try:
					data[field] = toAscii(row[col])
					if field == 'LastName':
						data[field] = data[field].upper()
				except IndexError:
					pass
			try:
				info[int(data[Fields[0]])] = data
			except (ValueError, TypeError, KeyError):
				pass
		return info

#-----------------------------------------------------------------------------------------------------

def toAscii( s ):
	return unicodedata.normalize('NFKD', s).encode('ascii','ignore') if type(s) == unicode else str(s)

class readexcel(object):
	""" Simple OS-independent class for extracting data from an Excel File.

	Uses the xlrd module (version 0.5.2 or later), supporting Excel versions:
	2004, 2002, XP, 2000, 97, 95, 5, 4, 3

	Data is extracted via iterators that return one row at a time -- either
	as a dict or as a list. The dict generator assumes that the worksheet is
	in tabular format with the first "data" row containing the variable names
	and all subsequent rows containing values.

	Extracted data is represented fairly logically. By default dates are
	returned as strings in "yyyy/mm/dd" format or "yyyy/mm/dd hh:mm:ss", as
	appropriate. However, when specifying date_as_tuple=True, dates will be
	returned as a (Year, Month, Day, Hour, Min, Second) tuple, for usage with
	mxDateTime or DateTime. Numbers are returned as either INT or FLOAT,
	whichever is needed to support the data. Text, booleans, and error codes
	are also returned as appropriate representations. Quick Example:

		xls = readexcel('testdata.xls')
		for sname in xls.book.sheet_names():
			for row in xls.iter_dict(sname):
				print row
	"""
	def __init__(self, filename):
		""" Wraps an XLRD book """
		if not os.path.isfile(filename):
			raise ValueError, "%s is not a valid filename" % filename
		self.book = xlrd.open_workbook(filename)
		self.sheet_keys = {}
		
	def is_nonempty_row(self, sheet, i):
		values = sheet.row_values(i)
		if isinstance(values[0], basestring) and values[0].startswith('#'):
			return False # ignorable comment row
		return any( bool(v) for v in values )
		
	def _parse_row(self, sheet, row_index, date_as_tuple):
		""" Sanitize incoming excel data """
		# Data Type Codes:
		#  EMPTY 0
		#  TEXT 1 a Unicode string
		#  NUMBER 2 float
		#  DATE 3 float
		#  BOOLEAN 4 int; 1 means TRUE, 0 means FALSE
		#  ERROR 5
		values = []
		for type, value in itertools.izip(sheet.row_types(row_index), sheet.row_values(row_index)):
			if type == 2:
				if value == int(value):
					value = int(value)
			elif type == 3:
				datetuple = xlrd.xldate_as_tuple(value, self.book.datemode)
				if date_as_tuple:
					value = datetuple
				else:
					# time only - no date component
					if datetuple[0] == 0 and datetuple[1] == 0 and  datetuple[2] == 0:
						value = "%02d:%02d:%02d" % datetuple[3:]
					# date only, no time
					elif datetuple[3] == 0 and datetuple[4] == 0 and datetuple[5] == 0:
						value = "%04d/%02d/%02d" % datetuple[:3]
					else: # full date
						value = "%04d/%02d/%02d %02d:%02d:%02d" % datetuple
			elif type == 5:
				value = xlrd.error_text_from_code[value]
			values.append(value)
		return values

	def _get_header( self, sheet ):
		# parse first row, set dict keys & first_row_index
		keys = []
		first_row_index = None
		for i in range(sheet.nrows):
			if self.is_nonempty_row(sheet, i):
				headings = self._parse_row(sheet, i, False)
				for j, var in enumerate(headings):
					# replace duplicate or missing headings with "ColHeader_#".
					if not var or var in keys:
						var = u'ColHeader_%s' % (j)
					keys.append(var.strip() if type(var) in [str, unicode] else var)
				first_row_index = i + 1
				break
		return keys, first_row_index

	def get_header( self, sname = None ):
		sheet = self.book.sheet_by_name(sname) # XLRDError
		return self._get_header(sheet)[0]
		
	def iter_dict(self, sname, date_as_tuple=False):
		""" Iterator for the worksheet's rows as dicts """
		# parse first row, set dict keys & first_row_index
		sheet = self.book.sheet_by_name(sname) # XLRDError
		keys, first_row_index = self._get_header( sheet )
		if first_row_index is None:
			return

		self.sheet_keys[sname] = keys
		# generate a dict per data row
		for i in range(first_row_index, sheet.nrows):
			if self.is_nonempty_row(sheet, i):
				yield dict( f for f in itertools.izip(keys, self._parse_row(sheet, i, date_as_tuple)) )
				
	def iter_list(self, sname, date_as_tuple=False):
		""" Iterator for the worksheet's rows as lists """
		sheet = self.book.sheet_by_name(sname) # XLRDError
		for i in range(sheet.nrows):
			if self.is_nonempty_row(sheet, i):
				yield self._parse_row(sheet, i, date_as_tuple)

if __name__ == '__main__':
	print Utils.approximateMatch("Team", "Last Name")

	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	excelLink = GetExcelLink(mainWin)
	mainWin.Show()
	excelLink.show()
	app.MainLoop()
	'''
	reader = readexcel( 'DataSamples\\Guelph Cross PreReg SignOn-sample.xls' )
	for s in xrange(len(reader.book.sheet_names())):
		print '----------------------------------------------------------------------'
		sheet_name = reader.book.sheet_names()[s]
		for r, row in enumerate(reader.iter_list(sheet_name)):
			print r+1, ','.join( toAscii(v) for v in row )
	'''