import wx
import wx.adv
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.agw.flatnotebook as flatnotebook
import wx.lib.mixins.listctrl as listmix

import os
import datetime
import traceback
from argparse import ArgumentParser
from roundbutton import RoundButton

import Utils
import Model
from StageRaceGCToExcel import StageRaceGCToExcel
from StageRaceGCToGrid import StageRaceGCToGrid
from MakeExampleExcel import MakeExampleExcel

from Version import AppVerName

def ShowSplashScreen():
	bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'StageRaceGC.png'), wx.BITMAP_TYPE_PNG )
	showSeconds = 2.5
	wx.adv.SplashScreen(bitmap, wx.adv.SPLASH_CENTRE_ON_SCREEN|wx.adv.SPLASH_TIMEOUT, int(showSeconds*1000), None)

class ListMixCtrl( wx.ListCtrl, listmix.ListCtrlAutoWidthMixin ):
	def __init__( self, parent, ID=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0 ):
		wx.ListCtrl.__init__( self, parent, ID, pos, size, style )
		listmix.ListCtrlAutoWidthMixin.__init__( self )

class MainWin( wx.Frame ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(200,200) ):
		wx.Frame.__init__(self, parent, id, title, size=size)

		self.SetBackgroundColour( wx.Colour(240,240,240) )
		
		self.fname = None
		self.updated = False
		self.firstTime = True
		self.lastUpdateTime = None
		self.comments = []
		
		self.filehistory = wx.FileHistory(16)
		self.config = wx.Config(
			appName="StageRaceGC",
			vendorName="Edward.Sitarski@gmail.com",
			style=wx.CONFIG_USE_LOCAL_FILE
		)
		self.filehistory.Load(self.config)
		
		inputBox = wx.StaticBox( self, label=_('Input') )
		inputBoxSizer = wx.StaticBoxSizer( inputBox, wx.VERTICAL )
		self.fileBrowse = filebrowse.FileBrowseButtonWithHistory(
			self,
			labelText=_('Excel File'),
			buttonText=('Browse...'),
			startDirectory=os.path.expanduser('~'),
			fileMask='Excel Spreadsheet (*.xlsx; *.xlsm; *.xls)|*.xlsx; *.xlsml; *.xls',
			size=(400,-1),
			history=lambda: [ self.filehistory.GetHistoryFile(i) for i in range(self.filehistory.GetCount()) ],
			changeCallback=self.doChangeCallback,
		)
		inputBoxSizer.Add( self.fileBrowse, 0, flag=wx.EXPAND|wx.ALL, border=4 )
				
		horizontalControlSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.updateButton = RoundButton( self, size=(96,96) )
		self.updateButton.SetLabel( _('Update') )
		self.updateButton.SetFontToFitLabel()
		self.updateButton.SetForegroundColour( wx.Colour(0,100,0) )
		self.updateButton.Bind( wx.EVT_BUTTON, self.doUpdate )
		horizontalControlSizer.Add( self.updateButton, flag=wx.ALL, border=4 )
		
		horizontalControlSizer.AddSpacer( 48 )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		self.tutorialButton = wx.Button( self, label=_('Help/Tutorial...') )
		self.tutorialButton.Bind( wx.EVT_BUTTON, self.onTutorial )
		vs.Add( self.tutorialButton, flag=wx.ALL, border=4 )
		branding = wx.adv.HyperlinkCtrl( self, id=wx.ID_ANY, label=u"Powered by CrossMgr", url=u"http://www.sites.google.com/site/crossmgrsoftware/" )
		vs.Add( branding, flag=wx.ALL, border=4 )
		horizontalControlSizer.Add( vs )

		self.openExcel = wx.Button( self, label=_('Open Excel File...') )
		self.openExcel.Bind( wx.EVT_BUTTON, self.onOpenExcel )
		
		horizontalControlSizer.AddSpacer( 48 )
		horizontalControlSizer.Add( self.openExcel, flag=wx.ALL, border=4 )
				
		inputBoxSizer.Add( horizontalControlSizer, flag=wx.EXPAND )
		
		self.stageList = ListMixCtrl( self, style=wx.LC_REPORT, size=(-1,160) )
		self.stageList.InsertColumn(0, "Sheet")
		self.stageList.InsertColumn(1, "Bibs", wx.LIST_FORMAT_RIGHT)
		self.stageList.InsertColumn(2, "Errors/Warnings")
		self.stageList.setResizeColumn( 2 )
		
		bookStyle = (
			  flatnotebook.FNB_NO_X_BUTTON
			| flatnotebook.FNB_FF2
			| flatnotebook.FNB_NODRAG
			| flatnotebook.FNB_DROPDOWN_TABS_LIST
			| flatnotebook.FNB_NO_NAV_BUTTONS
			| flatnotebook.FNB_BOTTOM
		)
		self.notebook = flatnotebook.FlatNotebook( self, 1000, agwStyle=bookStyle )
		self.notebook.SetBackgroundColour( wx.WHITE )
		
		self.saveAsExcelButton = wx.Button( self, label=u'Save as Excel' )
		self.saveAsExcelButton.Bind( wx.EVT_BUTTON, self.saveAsExcel )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		mainSizer.Add( inputBoxSizer, flag=wx.EXPAND|wx.ALL, border = 4 )
		mainSizer.Add( self.stageList, flag=wx.EXPAND|wx.ALL, border = 4 )
		mainSizer.Add( self.notebook, 1, flag=wx.EXPAND|wx.ALL, border = 4 )
		mainSizer.Add( self.saveAsExcelButton, flag=wx.ALL, border = 4 )
		
		self.SetSizer( mainSizer )
		
	def onOpenExcel( self, event ):
		filename = self.fileBrowse.GetValue()
		if not filename:
			Utils.MessageOK( self, "\n".join( [
					_("Please Enter or Browse... an Excel file."),
				] )
			)
			return
		with wx.BusyCursor():
			Utils.LaunchApplication( filename )
		
	def onTutorial( self, event ):
		if not Utils.MessageOKCancel( self, u"\n".join( [
					_("Launch the StageRaceGC Tutorial."),
					_("This open a sample Excel input file created into your home folder."),
					_("This data in this sheet is made-up, although it does include some current rider's names."),
					"",
					_("It will also open the Tutorial page in your browser.  If you can't see your browser, make sure you bring to the front."),
					"",
					_("Continue?"),
					] )
				):
			return
		try:
			fname_excel = MakeExampleExcel()
		except Exception as e:
			traceback.print_exc()
			Utils.MessageOK( self, '{}\n\n{}\n\n{}'.format(
					'Problem creating Excel sheet.',
					e,
					_('If the Excel file is open, please close it and try again')
				)
			)
			return
		self.fileBrowse.SetValue( fname_excel )
		self.doUpdate( event )
		Utils.LaunchApplication( fname_excel )
		Utils.LaunchApplication( os.path.join(Utils.getHtmlDocFolder(), 'Tutorial.html') )
	
	def doChangeCallback( self, event ):
		fname = event.GetString()
		if not fname:
			self.setUpdated( False )
			return
		if fname != self.fname:
			wx.CallAfter( self.doUpdate, fnameNew=fname )
		
	def setUpdated( self, updated=True ):
		self.updated = updated
		for w in [self.stageList, self.saveAsExcelButton]:
			w.Enable( updated )
		if not updated:
			self.stageList.DeleteAllItems()
			self.notebook.DeleteAllPages()
			
	def updateStageList( self, registration=None, stages=None ):
		self.stageList.DeleteAllItems()
		
		registration = (registration or (Model.model and Model.model.registration) or None)
		if not registration:
			return
		stages = (stages or (Model.model and Model.model.stages) or [])
			
		def insert_stage_info( stage ):
			idx = self.stageList.InsertItem( 999999, stage.sheet_name )
			self.stageList.SetItem( idx, 1, str(len(stage)) )
			if stage.errors:
				self.stageList.SetItem( idx, 2, '{}: {}'.format(len(stage.errors), '  '.join('[{}]'.format(e) for e in stage.errors)) )
			else:
				self.stageList.SetItem( idx, 2, '                                                                ' )
		
		insert_stage_info( registration )
		for stage in stages:
			insert_stage_info( stage )
		
		for col in range(3):
			self.stageList.SetColumnWidth( col, wx.LIST_AUTOSIZE )
		self.stageList.SetColumnWidth( 1, 52 )
		self.stageList.Refresh()

	def callbackUpdate( self, message ):
		pass
		
	def doUpdate( self, event=None, fnameNew=None ):
		try:
			self.fname = (fnameNew or event.GetString() or self.fileBrowse.GetValue())
		except Exception:
			self.fname = u''
		
		if not self.fname:
			Utils.MessageOK( self, _('Missing Excel file.  Please select an Excel file.'), _('Missing Excel File') )
			self.setUpdated( False )
			return
		
		if self.lastUpdateTime and (datetime.datetime.now() - self.lastUpdateTime).total_seconds() < 1.0:
			return
		
		try:
			with open(self.fname, 'rb'):
				pass
		except Exception as e:
			traceback.print_exc()
			Utils.MessageOK( self, '{}:\n\n    {}\n\n{}'.format( _('Cannot Open Excel file'), self.fname, e), _('Cannot Open Excel File') )
			self.setUpdated( False )
			return
		
		self.filehistory.AddFileToHistory( self.fname )
		self.filehistory.Save( self.config )
		self.fileBrowse.SetValue( self.fname )
		
		with wx.BusyCursor():
			try:
				Model.read( self.fname, callbackfunc=self.updateStageList )
			except Exception as e:
				traceback.print_exc()
				Utils.MessageOK( self, '{}:\n\n    {}\n\n{}'.format( _('Excel File Error'), self.fname, e), _('Excel File Error') )
				self.setUpdated( False )
				return
			
			Model.model.getGCs()
			self.setUpdated( True )
			
			self.updateStageList()
			StageRaceGCToGrid( self.notebook )
		
			self.lastUpdateTime = datetime.datetime.now()
	
	def getOutputExcelName( self ):
		fname_base, fname_suffix = os.path.splitext(self.fname)
		fname_excel = '{}-{}{}'.format(fname_base, 'GC', '.xlsx')
		return fname_excel
	
	def saveAsExcel( self, event ):
		fname_excel = self.getOutputExcelName()
		if os.path.isfile( fname_excel ):
			if not Utils.MessageOKCancel(
						self,
						u'"{}"\n\n{}'.format(fname_excel, _('File exists.  Replace?')),
						_('Output Excel File Exists'),
					):
				return
		
		try:
			StageRaceGCToExcel( fname_excel, Model.model )
		except Exception as e:
			Utils.MessageOK( self,
				'{}: "{}"\n\n{}\n\n"{}"'.format(
						_("Write Failed"),
						e,
						_("If you have this file open, close it and try again."),
						fname_excel),
				_("Excel Write Failed."),
				iconMask = wx.ICON_ERROR,
			)
			return
			
		with wx.BusyCursor():
			Utils.LaunchApplication( fname_excel )

# Set log file location.
dataDir = ''
redirectFileName = ''
			
def MainLoop():
	global dataDir
	global redirectFileName
	
	app = wx.App( False )
	app.SetAppName("StageRaceGC")
	
	parser = ArgumentParser()
	parser.add_argument("-q", "--quiet", action="store_false", dest="verbose", default=True, help='hide splash screen')
	parser.add_argument("-r", "--regular", action="store_true", dest="regular", default=False, help='regular size')
	parser.add_argument("filename", nargs='?', default=None, help="stage race info file", metavar="StageRaceGCSpreadsheet.xlsx")
	args = parser.parse_args( )

	# Try to open a specified filename.
	fileName = args.filename
	
	dataDir = Utils.getHomeDir()
	redirectFileName = os.path.join(dataDir, 'StageRaceGC.log')
	
	if __name__ == '__main__':
		Utils.disable_stdout_buffering()
	else:
		try:
			logSize = os.path.getsize( redirectFileName )
			if logSize > 1000000:
				os.remove( redirectFileName )
		except Exception:
			pass
	
		try:
			app.RedirectStdio( redirectFileName )
		except Exception:
			pass
	
	mainWin = MainWin( None, title=AppVerName, size=(800,600) )
	if not args.regular:
		mainWin.Maximize( True )

	# Set the upper left icon.
	try:
		icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'StageRaceGC.ico'), wx.BITMAP_TYPE_ICO )
		mainWin.SetIcon( icon )
	except Exception:
		pass

	mainWin.Show()
	if fileName:
		wx.CallAfter( mainWin.doUpdate, fnameNew=fileName )
	
	if args.verbose:
		ShowSplashScreen()
	
	# Start processing events.
	app.MainLoop()

if __name__ == '__main__':
	MainLoop()

