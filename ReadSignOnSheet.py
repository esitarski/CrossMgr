from __future__ import print_function

import os
import itertools
import wx
import copy
import wx.lib.filebrowsebutton as filebrowse
import wx.wizard as wiz
import Utils
from Excel import GetExcelReader, toAscii

#-----------------------------------------------------------------------------------------------------
Fields = ['Bib#', 'LastName', 'FirstName', 'Team', 'License', 'Category', 'Tag', 'Tag2']
IgnoreFields = ['Bib#', 'Tag', 'Tag2']		# Fields to ignore when adding data to standard reports.
ReportFields = [f for f in Fields if f not in IgnoreFields]

class FileNamePage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Specify the Excel Sign-on File containing the additional rider information.'),
					flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Each race must be in a separate sheet.'), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'See documentation for examples.'), flag=wx.ALL, border = border )
		fileMask = [
			'Excel Worksheets (*.xlsx;*.xlsm;*.xls)|*.xlsx;*.xlsm;*.xls',
		]
		self.fbb = filebrowse.FileBrowseButton( self, -1, size=(450, -1),
												labelText = 'Excel Workbook:',
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
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Specify the sheet containing the information for this race:'),
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
		reader = GetExcelReader( fileName )
		self.headers = None
		
		# Try to find the header columns.
		# Look for the first row with more than 4 columns.
		for r, row in enumerate(reader.iter_list(sheetName)):
			cols = sum( 1 for d in row if toAscii(d) )
			if cols > 4:
				self.headers = [toAscii(h) for h in row]
				break

		# If we haven't found a header row yet, assume the first non-empty row is the header.
		if not self.headers and minCols == maxCols:
			for r, row in enumerate(reader.iter_list(sheetName)):
				cols = sum( 1 for d in row if toAscii(d) )
				if cols > 0:
					self.headers = [toAscii(h) for h in row]
					break
				
		if not self.headers:
			raise ValueError, 'Could not find a Header Row %s::%s.' % (fileName, sheetName)
			
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
		self.wizard.SetPageSize( wx.Size(500,200) )
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
					Utils.MessageOK( self.wizard, 'Cannot find at least 5 header names in the Excel sheet.\nCheck the format.',
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
					except ValueError, str:
						Utils.MessageOK( self.wizard, 'Problem extracting rider info.\nCheck the Excel format.',
											title='Data Error', iconMask=wx.ICON_ERROR)
						evt.Veto()
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
#-----------------------------------------------------------------------------------------------------
# Cache the Excel sheet so we don't have to re-read it if it has not changed.
stateCache = None
infoCache = None

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
		global stateCache
		global infoCache
		if stateCache and infoCache:
			try:
				state = (os.path.getmtime(self.fileName), self.fileName, self.sheetName, self.fieldCol)
				if state == stateCache:
					return infoCache.copy()
			except:
				pass
	
		# Read the sheet and return the rider data.
		try:
			reader = GetExcelReader( self.fileName )
			if self.sheetName not in reader.sheet_names():
				return {}
		except (IOError, ValueError):
			return {}
		
		info = {}
		for r, row in enumerate(reader.iter_list(self.sheetName)):
			data = {}
			for field, col in self.fieldCol.iteritems():
				if col < 0:					# Skip unmapped columns.
					continue
				try:
					data[field] = toAscii(row[col])
					if field == 'LastName' or field.startswith('Tag'):
						data[field] = data[field].upper()
				except IndexError:
					pass
			try:
				info[int(float(data[Fields[0]]))] = data
			except (ValueError, TypeError, KeyError):
				pass
				
		stateCache = (os.path.getmtime(self.fileName), self.fileName, self.sheetName, self.fieldCol)
		infoCache = info
		return infoCache.copy()

#-----------------------------------------------------------------------------------------------------

if __name__ == '__main__':
	print( Utils.approximateMatch("Team", "Last Name") )

	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	excelLink = GetExcelLink(mainWin)
	mainWin.Show()
	excelLink.show()
	app.MainLoop()
	'''
	reader = readexcel( 'DataSamples\\Guelph Cross PreReg SignOn-sample.xls' )
	for s in xrange(len(reader.sheet_names())):
		print '----------------------------------------------------------------------'
		sheet_name = reader.sheet_names()[s]
		for r, row in enumerate(reader.iter_list(sheet_name)):
			print r+1, ','.join( toAscii(v) for v in row )
	'''