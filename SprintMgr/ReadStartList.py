import wx
import re
import os
import sys
import itertools
import copy
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.scrolledpanel as scrolled
import wx.adv as adv
import string
import webbrowser
import traceback

import Utils
import Model
from Excel import GetExcelReader, toAscii

#-----------------------------------------------------------------------------------------------------
Fields = ['Bib#', 'FirstName', 'LastName', 'Team', 'TeamCode', 'UCIID', 'UCI Points']

FieldToAttr = {f:Model.Rider.aliases[f.strip().lower().replace(' ', '_')] for f in Fields}

class FileNamePage(adv.WizardPageSimple):
	def __init__(self, parent):
		adv.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Specify the Excel File containing the Start List.'),
					flag=wx.ALL, border = border )
		fileMask = [
			'Excel Worksheets (*.xlsx;*.xlsm;*.xls)|*.xlsx;*.xlsm;*.xls',
		]
		self.fbb = filebrowse.FileBrowseButton( self, size=(450, -1),
												labelText = 'Excel Workbook:',
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
		vbs.Add( wx.StaticText(self, label='Specify the sheet containing the Start List for this race:'),
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
	
class HeaderNamesPage(adv.WizardPageSimple):
	def __init__(self, parent):
		adv.WizardPageSimple.__init__(self, parent)

		self.expectedFieldCol = None
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label='Specify the spreadsheet columns corresponding to the Start List fields.'),
				flag=wx.ALL, border = border )
		vbs.AddSpacer( 8 )
				
		border = 4
		# Create a map for the field names we are looking for
		# and the headers we found in the Excel sheet.
		sp = scrolled.ScrolledPanel( self, size=(750, 64), style=wx.TAB_TRAVERSAL )
		
		gs = wx.GridSizer( 2, len(Fields), 4, 4 )
		for c, f in enumerate(Fields):
			label = wx.StaticText(sp, label=f)
			gs.Add( label )
		
		self.headers = []
		self.choices = []
		for c, f in enumerate(Fields):
			self.choices.append( wx.Choice(sp, choices=self.headers ) )
			gs.Add( self.choices[-1] )
		
		sp.SetSizer( gs )
		sp.SetAutoLayout(1)
		sp.SetupScrolling( scroll_y = False )
		self.sp = sp
		self.gs = gs
		vbs.Add( sp, flag=wx.ALL, border = border )
		
		self.SetSizerAndFit( vbs )
	
	def setExpectedFieldCol( self, fieldCol ):
		self.expectedFieldCol = copy.copy(fieldCol)
	
	def setFileNameSheetName( self, fileName, sheetName ):
		reader = GetExcelReader( fileName )
		self.headers = None
		
		# Try to find the header columns.
		# Look for the first row with at least 3 columns.
		for r, row in enumerate(reader.iter_list(sheetName)):
			cols = sum( 1 for d in row if toAscii(d) )
			if cols >= 3:
				self.headers = [toAscii(h).strip() for h in row]
				break

		# If we haven't found a header row yet, assume the first non-empty row is the header.
		if not self.headers:
			for r, row in enumerate(reader.iter_list(sheetName)):
				cols = sum( 1 for d in row if toAscii(d) )
				if cols > 0:
					self.headers = [toAscii(h).strip() for h in row]
					break
		
		# Ignore empty columns on the end.
		while self.headers and (self.headers[-1].isspace() or not self.headers[-1]):
			self.headers.pop()
			
		# Rename empty columns so as not to confuse the user.
		self.headers = [h if h else 'BlankHeaderName{:03d}'.format(c+1) for c, h in enumerate(self.headers)]
		
		if not self.headers:
			raise ValueError( 'Could not find a Header Row {}::{}.'.format(fileName, sheetName) )
			
		# Add an unmapped field at the end.
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

		self.gs.Layout()
		self.sp.SetAutoLayout(1)
		self.sp.SetupScrolling( scroll_y = False )

	def getFieldCol( self ):
		fieldCol = {}
		for c, f in enumerate(Fields):
			fieldCol[f] = self.choices[c].GetSelection()
			if fieldCol[f] == self.choices[c].GetCount() - 1:
				fieldCol[f] = -1
		return fieldCol
			
class SummaryPage(adv.WizardPageSimple):
	def __init__(self, parent):
		adv.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label='Summary:'), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label=' '), flag=wx.ALL, border = border )

		rows = 0
		
		self.fileLabel = wx.StaticText( self, label='Excel File:' )
		self.fileName = wx.StaticText( self )
		rows += 1

		self.sheetLabel = wx.StaticText( self, label='Sheet Name:' )
		self.sheetName = wx.StaticText( self )
		rows += 1

		self.riderLabel = wx.StaticText( self, label='Rider Start Times:' )
		self.riderNumber = wx.StaticText( self )
		rows += 1

		self.statusLabel = wx.StaticText( self, label='Status:' )
		self.statusName = wx.StaticText( self )
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
	
class GetExcelStartListLink:
	def __init__( self, parent, excelLink = None ):
		img_filename = os.path.join( Utils.getImageFolder(), '20100718-Excel_icon.png' )
		img = wx.Bitmap(img_filename) if img_filename and os.path.exists(img_filename) else wx.NullBitmap
		
		self.wizard = adv.Wizard()
		self.wizard.SetExtraStyle( adv.WIZARD_EX_HELPBUTTON )
		self.wizard.Create( parent, wx.ID_ANY, 'Import Start List', img )
		self.wizard.Bind( adv.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		
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
						message = 'Cannot open file "{}".\nPlease check the file name and/or its read permissions.'.format(fileName)
					Utils.MessageOK( self.wizard, message, title='File Open Error', iconMask=wx.ICON_ERROR)
					evt.Veto()
			elif page == self.sheetNamePage:
				try:
					self.headerNamesPage.setFileNameSheetName(self.fileNamePage.getFileName(), self.sheetNamePage.getSheetName())
				except ValueError:
					Utils.MessageOK( self.wizard, 'Cannot find header names in the Excel sheet.\nCheck the format.',
										title='Excel Format Error', iconMask=wx.ICON_ERROR)
					evt.Veto()
			elif page == self.headerNamesPage:
				excelLink = ExcelLink()
				excelLink.setFileName( self.fileNamePage.getFileName() )
				excelLink.setSheetName( self.sheetNamePage.getSheetName() )
				fieldCol = self.headerNamesPage.getFieldCol()
				if fieldCol[Fields[0]] < 0:
					Utils.MessageOK( self.wizard, 'You must specify a "{}" column.'.format(Fields[0]),
										title='Excel Format Error', iconMask=wx.ICON_ERROR)
					evt.Veto()
				else:
					excelLink.setFieldCol( fieldCol )
					try:
						info = excelLink.read()
						self.summaryPage.setFileNameSheetNameInfo(self.fileNamePage.getFileName(), self.sheetNamePage.getSheetName(), info)
					except ValueError as e:
						Utils.MessageOK( self.wizard, 'Problem extracting rider info.\nCheck the Excel format.',
											title='Data Error', iconMask=wx.ICON_ERROR)
						evt.Veto()
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
#----------------------------------------------------------------------------------
class ExcelLink:
	def __init__( self ):
		self.fileName = None
		self.sheetName = None
		self.fieldCol = dict( (f, c) for c, f in enumerate(Fields) )
	
	def key( self ):
		return (self.fileName, self.sheetName, self.fieldCol)
	
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
		if stateCache and infoCache:
			try:
				state = (self.fileName, self.sheetName, self.fieldCol)
				if state == stateCache[-3:]:
					return infoCache
			except Exception:
				pass
		return None
	
	def read( self ):
		try:
			reader = GetExcelReader( self.fileName )
			if self.sheetName not in reader.sheet_names():
				return None
		except (IOError, ValueError):
				return None
		
		info = {}
		for r, row in enumerate(reader.iter_list(self.sheetName)):
			data = {}
			for field, col in self.fieldCol.items():
				if col < 0:					# Skip unmapped columns.
					continue
				try:
					data[field] = toAscii(row[col])
				except IndexError:
					pass
			try:
				info[int(float(data[Fields[0]]))] = data
			except (ValueError, TypeError, KeyError):
				pass
		
		return info

def ImportStartList( parent ):
	excelLink = GetExcelStartListLink( parent ).show()
	if not excelLink:
		return
		
	info = excelLink.read()
	errors = []
	
	if Utils.MessageYesNo( parent, 'Replace existing Riders from Spreadsheet?\n\nOtherwise, data will be merged by Bib number.',
		'Replace existing Riders' ):
		Model.model.riders = []
	
	riders = Model.model.riders
	riderBib = { r.bib:r for r in riders }
	importCount = 0
	for bib, data in info.items():
		# Merge with existing information.
		if sum(int(bool(n)) for n in (data.get('FirstName',None), data.get('LastName',None))) == 1:
			combinedName = data.get('FirstName',None) or data.get('LastName',None)
			firstIsFirst = int(bool(data.get('FirstName',None)))
			if ',' in combinedName:
				names = combinedName.split(',',2)
				data['FirstName'] = names[1-firstIsFirst].strip()
				data['LastName'] = names[firstIsFirst].strip()
		
		if bib in riderBib:
			r = riderBib[bib]
			for f in Fields:
				if f in data:
					setattr(r, FieldToAttr[f], data[f])
		else:
			r = Model.Rider( **dict((FieldToAttr[f], v) for f, v in data.items()) )
			riders.append( r )
			riderBib[bib] = r
		importCount += 1
		
	if errors:
		errorStr = '\n'.join( errors[:20] )
		if len(errors) > 20:
			errorStr += '\n...'
		Utils.MessageOK( parent, errorStr, 'Start List Errors' )
		
	Utils.refresh()
	Utils.MessageOK( parent, 'Imported Start List:{} entries'.format(importCount), 'Start List Import Success' )

#-----------------------------------------------------------------------------------------------------

if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="SprintMan", size=(600,400))
	mainWin.Show()
	ImportStartList( mainWin )
	app.MainLoop()
