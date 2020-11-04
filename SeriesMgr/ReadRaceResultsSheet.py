import wx
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.scrolledpanel as scrolled
import wx.adv
import os
import sys
import copy
import Utils
import traceback
import datetime
import Model
from Excel import GetExcelReader

#-----------------------------------------------------------------------------------------------------
Fields = ['Bib#', 'Pos', 'Time', 'FirstName', 'LastName', 'Category', 'License', 'Team']

class FileNamePage(wx.adv.WizardPageSimple):
	def __init__(self, parent):
		wx.adv.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, _('Specify the Excel File containing the Results info.')),
					flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, _('Each result must be in a separate sheet.')), flag=wx.ALL, border = border )
		fileMask = [
			'Excel Worksheets (*.xlsx;*.xlsm;*.xls)|*.xlsx;*.xlsm;*.xls',
		]
		self.fbb = filebrowse.FileBrowseButton( self, -1, size=(450, -1),
												labelText = 'Excel Workbook:',
												fileMode=wx.FD_OPEN,
												fileMask='|'.join(fileMask) )
		vbs.Add( self.fbb, flag=wx.ALL, border = border )
		
		self.SetSizer( vbs )
	
	def setFileName( self, fileName ):
		self.fbb.SetValue( fileName )
	
	def getFileName( self ):
		return self.fbb.GetValue()
	
class SheetNamePage(wx.adv.WizardPageSimple):
	def __init__(self, parent):
		wx.adv.WizardPageSimple.__init__(self, parent)
		self.choices = []
		self.expectedSheetName = None
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, _('Specify the Sheet containing the results:')),
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
	
class HeaderNamesPage(wx.adv.WizardPageSimple):
	def __init__(self, parent):
		wx.adv.WizardPageSimple.__init__(self, parent)

		self.expectedFieldCol = None
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, _('Specify the spreadsheet columns corresponding to the Results fields.')),
				flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, _('You should define Pos, LastName, Category and License (at least).')),
				flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, _('You must also define a Time column if you are Scoring by Time.')),
				flag=wx.ALL, border = border )
		vbs.AddSpacer( 8 )
				
		border = 4
		# Create a map for the field names we are looking for
		# and the headers we found in the Excel sheet.
		sp = scrolled.ScrolledPanel( self, wx.ID_ANY, size=(750, 64), style = wx.TAB_TRAVERSAL )
		
		boldFont = None
		
		gs = wx.GridSizer( 2, len(Fields), 4, 4 )
		for c, f in enumerate(Fields):
			label = wx.StaticText(sp, label=f)
			if boldFont is None:
				font = label.GetFont()
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
		
		self.SetSizer( vbs )
	
	def setExpectedFieldCol( self, fieldCol ):
		self.expectedFieldCol = copy.copy(fieldCol)
	
	def setFileNameSheetName( self, fileName, sheetName ):
		reader = GetExcelReader( fileName )
		self.headers = None
		
		# Try to find the header columns.
		# Look for the first row with more than 4 columns.
		for r, row in enumerate(reader.iter_list(sheetName)):
			cols = sum( 1 for d in row if d )
			if cols > 4:
				self.headers = ['{}'.format(h or '').strip() for h in row]
				break

		# If we haven't found a header row yet, assume the first non-empty row is the header.
		if not self.headers:
			for r, row in enumerate(reader.iter_list(sheetName)):
				cols = sum( 1 for d in row if d )
				if cols > 0:
					self.headers = ['{}'.format(h or '').strip() for h in row]
					break
		
		# Ignore empty columns on the end.
		while self.headers and not self.headers[-1]:
			self.headers.pop()
			
		if not self.headers:
			raise ValueError( 'Could not find a Header Row %s::%s.' % (fileName, sheetName) )
		
		# Rename empty columns so as not to confuse the user.
		self.headers = [h if h else 'BlankHeaderName%03d' % (c+1) for c, h in enumerate(self.headers)]
		
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

		self.gs.Layout()
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling( scroll_y = False )

	def getFieldCol( self ):
		fieldCol = {}
		for c, f in enumerate(Fields):
			fieldCol[f] = self.choices[c].GetSelection()
		return fieldCol
			
class SummaryPage(wx.adv.WizardPageSimple):
	def __init__(self, parent):
		wx.adv.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, _('Summary:')), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, ' '), flag=wx.ALL, border = border )

		rows = 0
		
		self.fileLabel = wx.StaticText( self, wx.ID_ANY, _('Excel File:') )
		self.fileName = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.sheetLabel = wx.StaticText( self, wx.ID_ANY, _('Sheet Name:') )
		self.sheetName = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.riderLabel = wx.StaticText( self, wx.ID_ANY, _('Valid Results:') )
		self.riderNumber = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.statusLabel = wx.StaticText( self, wx.ID_ANY, _('Status:') )
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
		self.riderNumber.SetLabel( '{}'.format(infoLen) )
		self.statusName.SetLabel( _('Success!') if infoLen else _('Failure') )
	
class GetExcelResultsLink( object ):
	def __init__( self, parent, excelLink = None ):
		#img_filename = os.path.join( Utils.getImageFolder(), '20100718-Excel_icon.png' )
		#img = wx.Bitmap(img_filename) if img_filename and os.path.exists(img_filename) else wx.NullBitmap
		img = wx.Bitmap(os.path.join( Utils.getImageFolder(), '20100718-Excel_icon.png' ))
		
		prewizard = wx.adv.PreWizard()
		prewizard.SetExtraStyle( wx.adv.WIZARD_EX_HELPBUTTON )
		prewizard.Create( parent, wx.ID_ANY, _('Link Excel Info'), img )
		self.wizard = prewizard
		self.wizard.Bind( wx.adv.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		#self.wizard.Bind( wx.adv.EVT_WIZARD_HELP,
		#	lambda evt: Utils.showHelp('Menu-DataMgmt.html#link-to-external-excel-data') )
		
		self.fileNamePage = FileNamePage( self.wizard )
		self.sheetNamePage = SheetNamePage( self.wizard )
		self.headerNamesPage = HeaderNamesPage( self.wizard )
		self.summaryPage = SummaryPage( self.wizard )
		
		wx.adv.WizardPageSimple.Chain( self.fileNamePage, self.sheetNamePage )
		wx.adv.WizardPageSimple.Chain( self.sheetNamePage, self.headerNamesPage )
		wx.adv.WizardPageSimple.Chain( self.headerNamesPage, self.summaryPage )

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
						self.summaryPage.setFileNameSheetNameInfo(self.fileNamePage.getFileName(), self.sheetNamePage.getSheetName(), info)
					except ValueError as e:
						Utils.MessageOK( self.wizard, _('Problem extracting rider info.\nCheck the Excel format.'),
											title=_('Data Error'), iconMask=wx.ICON_ERROR)
						evt.Veto()
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
#----------------------------------------------------------------------------------
class ExcelLink( object ):
	def __init__( self ):
		self.fileName = None
		self.sheetName = None
		self.raceDate = None
		self.raceTime = None
		self.fieldCol = dict( (f, c) for c, f in enumerate(Fields) )
	
	def __repr__( self ):
		return ', '.join( '{}={}'.format(a, getattr(self, a)) for a in ['fileName', 'sheetName', 'raceDate', 'raceTime', 'fieldCol'] )
	
	def key( self ):
		return (self.fileName, self.sheetName, self.fieldCol)
	
	def setFileName( self, fileName ):
		self.fileName = fileName
		
	def setSheetName( self, sname ):
		self.sheetName = sname
	
	def setFieldCol( self, fieldCol ):
		self.fieldCol = fieldCol
		
	def hasField( self, field ):
		return self.fieldCol.get( field, -1 ) >= 0
		
	def getFields( self ):
		return [f for f in Fields if self.hasField(f)]
	
	def read( self ):
		reader = GetExcelReader( self.fileName )
		
		self.raceDate = None
		self.raceTime = None
		
		info = []
		for r, row in enumerate(reader.iter_list(self.sheetName)):
			if len(row) == 2:
				try:
					if row[0] == 'Date' and row[1] and isinstance(row[1], datetime.date):
						self.raceDate = row[1]
					elif row[0] == 'Time' and row[1] and isinstance(row[1], datetime.time):
						self.raceTime = row[1]
				except:
					pass
				
			data = {}
			for field, col in self.fieldCol.items():
				if col < 0:					# Skip unmapped columns.
					continue
				try:
					data[field] = row[col]
				except IndexError:
					pass
					
				try:
					data[field] = '{}'.format(data[field])
				except:
					data[field] = ''
			
			if not data.get('Category', ''):
				continue
		
			try:
				int(data.get('Pos',''))
			except ValueError:
				continue
			
			data['Pos'] = int(data['Pos'])
			info.append( data )
		
		return info

#-----------------------------------------------------------------------------------------------------

if __name__ == '__main__':
	app = wx.App( False )
	mainWin = wx.Frame(None,title="SeriesMan", size=(600,400))
	mainWin.Show()
	app.MainLoop()
