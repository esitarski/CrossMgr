import wx
import os
import copy
import datetime
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.scrolledpanel as scrolled
import wx.adv as adv
import Utils
import Model
from Undo import undo
from Excel import GetExcelReader
import HelpSearch

#-----------------------------------------------------------------------------------------------------
Fields = ['Bib#', 'StartTime']

class FileNamePage(adv.WizardPageSimple):
	def __init__(self, parent):
		super().__init__(parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Specify the Excel File containing TT Start Times in HH:MM:SS format.')),
					flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = _('Each race must be in a separate sheet.')), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = _('This is the Stopwatch Time usually beginning at 00:01:00, with 30 to 60 second gaps - not the clock time.')), flag=wx.ALL, border = border )
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
		super().__init__(parent)
		self.choices = []
		self.expectedSheetName = None
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Specify the sheet containing the start times for this race:')),
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
		super().__init__(parent)

		self.expectedFieldCol = None
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Specify the spreadsheet columns corresponding to the Start Time fields.')),
				flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = _('Both Bib and Start Time must be specified.')),
				flag=wx.ALL, border = border )
		vbs.AddSpacer( 8 )
		
		self.startTimesInTimeOfDay = wx.CheckBox( self, label=_('Start times are in Time of Day.  Fix them by subtracting the scheduled race start time.') )
				
		border = 4
		# Create a map for the field names we are looking for
		# and the headers we found in the Excel sheet.
		sp = scrolled.ScrolledPanel( self, size=(750, 64), style = wx.TAB_TRAVERSAL )
		
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
			self.choices.append( wx.Choice(sp, choices = self.headers ) )
			gs.Add( self.choices[-1] )
		
		sp.SetSizer( gs )
		sp.SetAutoLayout(1)
		sp.SetupScrolling( scroll_y = False )
		self.sp = sp
		self.gs = gs
		vbs.Add( sp, flag=wx.ALL, border = border )
		vbs.Add( self.startTimesInTimeOfDay, flag=wx.ALL, border = 8 )
		
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
		while self.headers and (self.headers[-1].isspace() or not self.headers[-1]):
			self.headers.pop()
			
		if not self.headers:
			raise ValueError( 'Could not find a Header Row {}::{}.'.format(fileName, sheetName) )
		
		# Rename empty columns so as not to confuse the user.
		self.headers = [h if h else 'BlankHeaderName{:03d}'.format(c+1) for c, h in enumerate(self.headers)]
		
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
			
class SummaryPage(adv.WizardPageSimple):
	def __init__(self, parent):
		super().__init__(parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Summary:')), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = ' '), flag=wx.ALL, border = border )

		self.fileLabel = wx.StaticText( self, label = _('Excel File:') )
		self.fileName = wx.StaticText( self )

		self.sheetLabel = wx.StaticText( self, label = _('Sheet Name:') )
		self.sheetName = wx.StaticText( self )

		self.riderLabel = wx.StaticText( self, label = _('Rider Start Times:') )
		self.riderNumber = wx.StaticText( self )

		self.statusLabel = wx.StaticText( self, label = _('Status:') )
		self.statusName = wx.StaticText( self )

		fbs = wx.FlexGridSizer( rows=0, cols=2, hgap=5, vgap=2 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fbs.AddMany( [(self.fileLabel, 0, labelAlign),		(self.fileName, 	1, wx.EXPAND),
					  (self.sheetLabel, 0, labelAlign),		(self.sheetName, 	1, wx.EXPAND),
					  (self.riderLabel, 0, labelAlign),		(self.riderNumber,	1, wx.EXPAND),
					  (self.statusLabel, 0, labelAlign),	(self.statusName,	1, wx.EXPAND),
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
	
class GetExcelTTStartTimeLink:
	def __init__( self, parent, excelLink = None ):
		img_filename = os.path.join( Utils.getImageFolder(), '20100718-Excel_icon.png' )
		img = wx.Bitmap(img_filename) if img_filename and os.path.exists(img_filename) else wx.NullBitmap
		
		self.wizard = adv.Wizard()
		self.wizard.SetExtraStyle( adv.WIZARD_EX_HELPBUTTON )
		self.wizard.Create( parent, wx.ID_ANY, _('Import TT Start Times'), img )
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
		self.wizard.SetPageSize( wx.Size(500,200) )
		self.wizard.FitToPage( self.fileNamePage )
	
	def show( self ):
		if self.wizard.RunWizard(self.fileNamePage):
			if not self.excelLink:
				self.excelLink = ExcelLink()
			self.excelLink.setFileName( self.fileNamePage.getFileName() )
			self.excelLink.setSheetName( self.sheetNamePage.getSheetName() )
			self.excelLink.setFieldCol( self.headerNamesPage.getFieldCol() )
		return self.excelLink, self.headerNamesPage.startTimesInTimeOfDay.GetValue()
	
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
						message = '{}:\n\n    "{}"\n\n{}'.format(_('Cannot open file'), fileName, _('Please check the file name and/or its read permissions.') )
					Utils.MessageOK( self.wizard, message, title=_('File Open Error'), iconMask=wx.ICON_ERROR)
					evt.Veto()
			elif page == self.sheetNamePage:
				try:
					self.headerNamesPage.setFileNameSheetName(self.fileNamePage.getFileName(), self.sheetNamePage.getSheetName())
				except ValueError:
					Utils.MessageOK( self.wizard, _('Cannot find at least 5 header names in the Excel sheet.') + '\n' + _('Check the format.'),
										title=_('Excel Format Error'), iconMask=wx.ICON_ERROR)
					evt.Veto()
			elif page == self.headerNamesPage:
				excelLink = ExcelLink()
				excelLink.setFileName( self.fileNamePage.getFileName() )
				excelLink.setSheetName( self.sheetNamePage.getSheetName() )
				fieldCol = self.headerNamesPage.getFieldCol()
				if fieldCol[Fields[0]] < 0:
					Utils.MessageOK( self.wizard, '{}: "{}"'.format(_('You must specify column'), GetTranslation(Fields[0])),
										title=_('Excel Format Error'), iconMask=wx.ICON_ERROR)
					evt.Veto()
				else:
					excelLink.setFieldCol( fieldCol )
					try:
						info = excelLink.read()
						self.summaryPage.setFileNameSheetNameInfo(self.fileNamePage.getFileName(), self.sheetNamePage.getSheetName(), info)
					except ValueError as e:
						Utils.MessageOK( self.wizard, _('Problem extracting rider info.') + '\n' + _('Check the Excel format.'),
											title=_('Data Error'), iconMask=wx.ICON_ERROR)
						evt.Veto()
		
#----------------------------------------------------------------------------------
class ExcelLink:
	def __init__( self ):
		self.fileName = None
		self.sheetName = None
		self.fieldCol = {f:c for c, f in enumerate(Fields) }
	
	def __eq__( self, e ):
		return (self.fileName, self.sheetName, self.fieldCol) == (e.fileName, e.sheetName, e.fieldCol)
	
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
					data[field] = row[col]
				except IndexError:
					pass
			try:
				info[int(float(data[Fields[0]]))] = data
			except (ValueError, TypeError, KeyError):
				pass
		
		return info

def DoImportTTStartTimes( race, excelLink, startTimesInTimeOfDay=False ):
	startTimes = {}
	errors = []
	
	if not excelLink:
		errors.append( _('Missing excelLink') )
		return errors, startTimes, 0
		
	info = excelLink.read()
	
	scheduledStartSeconds = Utils.StrToSeconds( race.scheduledStart ) * 60.0	# race.scheduledStart has no seconds.
	
	for num, data in info.items():
		try:
			startTime = data['StartTime']
		except KeyError:
			errors.append( '{} {}: {}'.format(_('Bib'), num, _('missing start time')) )
			continue
			
		# Try to make sense of the StartTime (Stopwatch time, not clock time).
		if isinstance(startTime, float):
			t = startTime * 24.0*60.0*60.0	# Excel decimal days.
		elif isinstance(startTime, str):
			# Otherwise, string of format hh:mm:ss.ddd or mm:ss.ddd.
			fields = startTime.split( ':' )
			try:
				hh, mm, ss = [float(f.strip()) for f in fields[:3]]
			except Exception:
				try:
					hh = 0.0
					mm, ss = [float(f.strip()) for f in fields[:2]]
				except Exception:
					errors.append( '{} {}:  {}: "{}"'.format(_('Bib'), num, _('cannot read time format'), startTime) )
					continue
			t = hh * 60.0*60.0 + mm * 60.0 + ss
		elif isinstance(startTime, (datetime.time, datetime.datetime)):
			t = startTime.hour * 60.0*60.0 + startTime.minute * 60.0 + startTime.second + startTime.microsecond / 1000000.0
		else:
			errors.append( '{} {}:  {}'.format(_('Bib'), num, _('cannot read start time') ) )
			continue
		
		if startTimesInTimeOfDay and t >= scheduledStartSeconds:
			t -= scheduledStartSeconds
		
		startTimes[num] = t
	
	changeCount = 0
	if startTimes:
		undo.pushState()
		for num, startTime in startTimes.items():
			rider = race.getRider( num )
			
			# Compute the time change difference.
			try:
				firstTime = getattr(rider, 'firstTime', startTime)
			except TypeError:
				continue
				
			if rider.times:
				# Convert the race times to time of day by adding the existing first time.
				riderTimeOfDay = [(firstTime or 0.0) + rt for rt in rider.times]
				
				# Compute new lap times by subtracting the new start time.
				rider.times = [rtod - startTime for rtod in riderTimeOfDay]
			
			if rider.firstTime != startTime:
				rider.firstTime = startTime
				changeCount += 1
		
		race.setChanged()
		
	return errors, startTimes, changeCount

def AutoImportTTStartTimes():
	race = Model.race
	if not race or not race.isUnstarted() or not getattr(race, 'isTimeTrial', False) or not getattr(race, 'excelLink', None):
		return False
	
	# Create a subset Excel link with two field, Bib# and StartTime, and read the times.
	excelLink = ExcelLink()
	excelLink.setFileName( race.excelLink.fileName )
	excelLink.setSheetName( race.excelLink.sheetName )
	excelLink.setFieldCol( {'Bib#': race.excelLink.fieldCol['Bib#'], 'StartTime': 0} )	# Hack to hardcode StartTime as the first column.
	errors, startTimes, changeCount = DoImportTTStartTimes( race, excelLink )
	return True

def ImportTTStartTimes( parent ):
	race = Model.race
	if not race or not getattr(race, 'isTimeTrial', False):
		return
		
	excelLink, startTimesInTimeOfDay = GetExcelTTStartTimeLink( parent ).show()
	if not excelLink:
		return
	
	errors, startTimes, changeCount = DoImportTTStartTimes( race, excelLink, startTimesInTimeOfDay)
	if errors:
		errorStr = '\n'.join( errors[:20] )
		if len(errors) > 20:
			errorStr += '\n...'
		Utils.MessageOK( parent, errorStr, _('Start Time Import Errors') )
		
	Utils.refresh()
	Utils.MessageOK( parent, '{}: {}'.format(_('Start Times Changed'), changeCount), _('Start Times Success') )
	if Utils.getMainWin():
		Utils.getMainWin().menuFind()

#-----------------------------------------------------------------------------------------------------

if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	Model.getRace().isTimeTrial = True
	mainWin.Show()
	ImportTTStartTimes( mainWin )
	app.MainLoop()
