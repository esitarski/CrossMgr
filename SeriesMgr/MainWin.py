import os
import sys
import time
import xlwt
import base64
import random
import locale
import datetime
import traceback
import threading
import webbrowser

import wx
from wx.lib.wordwrap import wordwrap
import wx.adv as adv

FontSize = 20

try:
	localDateFormat = locale.nl_langinfo( locale.D_FMT )
	localTimeFormat = locale.nl_langinfo( locale.T_FMT )
except Exception:
	localDateFormat = '%b %d, %Y'
	localTimeFormat = '%I:%M%p'
	
import pickle
from argparse import ArgumentParser
from io import StringIO

import Dependencies

import Utils
import SeriesModel
from Races				import Races
from Competitions		import Competitions
from Points				import Points
from Upgrades			import Upgrades
from Results			import Results
from TeamResults		import TeamResults
from TeamResultsNames	import TeamResultsNames
from CategorySequence	import CategorySequence
from Aliases			import Aliases
from AliasesLicense		import AliasesLicense
from AliasesTeam		import AliasesTeam
from AliasesCategory	import AliasesCategory
from Options			import Options
from Errors				import Errors
from Printing			import SeriesMgrPrintout
from ExportGrid			import ExportGrid, tag
from SetGraphic			import SetGraphicDialog
from ModuleUnpickler	import ModuleUnpickler
import CmdLine
import Version

#----------------------------------------------------------------------------------

def ShowSplashScreen():
	bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SeriesMgrSplash.png'), wx.BITMAP_TYPE_PNG )
	
	# Write in the version number into the bitmap.
	w, h = bitmap.GetSize()
	dc = wx.MemoryDC()
	dc.SelectObject( bitmap )
	dc.SetFont( wx.Font( (0,h//10), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ) )
	dc.DrawText( Version.AppVerName.replace('SeriesMgr','Version'), w // 20, int(h * 0.4) )
	dc.SelectObject( wx.NullBitmap )
	
	showSeconds = 2.5
	adv.SplashScreen(bitmap, wx.adv.SPLASH_CENTRE_ON_SCREEN|wx.adv.SPLASH_TIMEOUT, int(showSeconds*1000), None)

#----------------------------------------------------------------------------------
		
class MyTipProvider( wx.adv.TipProvider ):
	def __init__( self, fileName, tipNo = None ):
		self.tips = []
		try:
			with open(fileName, 'r') as f:
				for line in f:
					line = line.strip()
					if line and line[0] != '#':
						self.tips.append( line )
			if tipNo is None:
				tipNo = (int(round(time.time() * 1000)) * 13) % (len(self.tips) - 1)
		except Exception:
			pass
		if tipNo is None:
			tipNo = 0
		self.tipNo = tipNo
		wx.adv.TipProvider.__init__( self, self.tipNo )
			
	def GetCurrentTip( self ):
		if self.tipNo < 0 or self.tipNo >= len(self.tips):
			self.tipNo = 0
		return self.tipNo
		
	def GetTip( self ):
		if not self.tips:
			return 'No tips available.'
		tip = self.tips[self.GetCurrentTip()].replace(r'\n','\n').replace(r'\t','    ')
		self.tipNo += 1
		return tip
		
	def PreprocessTip( self, tip ):
		return tip
		
	def DeleteFirstTip( self ):
		if self.tips:
			self.tips.pop(0)
		
	def __len__( self ):
		return len(self.tips)
		
	@property
	def CurrentTip( self ):
		return self.GetCurrentTip()
		
	@property
	def Tip( self ):
		return self.GetTip()

def ShowTipAtStartup():
	mainWin = Utils.getMainWin()
	if mainWin and not mainWin.config.ReadBool('showTipAtStartup', True):
		return
	
	tipFile = os.path.join(Utils.getImageFolder(), "tips.txt")
	try:
		provider = MyTipProvider( tipFile )
		'''
		if VersionMgr.isUpgradeRecommended():
			provider.tipNo = 0
		else:
			provider.DeleteFirstTip()
		'''
		showTipAtStartup = wx.ShowTip( None, provider, True )
		if mainWin:
			mainWin.config.WriteBool('showTipAtStartup', showTipAtStartup)
	except Exception:
		pass

#----------------------------------------------------------------------------------

class Counter():
	count = 0
	lock = threading.Lock()
	
	def __enter__(self):
		with Counter.lock:
			Counter.count += 1
			return Counter.count
	
	def __exit__(self, type, value, traceback):
		with Counter.lock:
			Counter.count -= 1

	@staticmethod
	def getCount():
		with Counter.lock:
			return Counter.count
		
#----------------------------------------------------------------------------------

class MainWin( wx.Frame ):
	def __init__( self, parent, id=wx.ID_ANY, title='', size=(200,200) ):
		wx.Frame.__init__(self, parent, id, title, size=size)

		Utils.setMainWin( self )

		# Add code to configure file history.
		self.filehistory = wx.FileHistory(8)
		dataDir = Utils.getHomeDir('SeriesMgr')
		configFileName = os.path.join(dataDir, 'SeriesMgr.cfg')
		self.config = wx.Config(appName="SeriesMgr",
								vendorName="Edward.Sitarski@gmail.com",
								localFilename=configFileName
		)
		self.filehistory.Load(self.config)
		
		self.fileName = None
		
		# Setup the objects for the race clock.
		self.timer = wx.Timer( self, id=wx.ID_ANY )
		self.secondCount = 0

		# Default print options.
		self.printData = wx.PrintData()
		self.printData.SetPaperId(wx.PAPER_LETTER)
		self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
		#self.printData.SetOrientation(wx.PORTRAIT)

		# Configure the main menu.
		self.menuBar = wx.MenuBar(wx.MB_DOCKABLE)

		#-----------------------------------------------------------------------
		self.fileMenu = wx.Menu()

		item = self.fileMenu.Append( wx.ID_NEW , "&New...", "Create a new Series" )
		self.Bind(wx.EVT_MENU, self.menuNew, item )

		item = self.fileMenu.Append( wx.ID_OPEN , "&Open...", "Open an existing Series" )
		self.Bind(wx.EVT_MENU, self.menuOpen, item )

		item = self.fileMenu.Append( wx.ID_SAVE , "&Save\tCtrl+S", "Save Series" )
		self.Bind(wx.EVT_MENU, self.menuSave, item )

		item = self.fileMenu.Append( wx.ID_SAVEAS , "Save &As...", "Save to a different filename" )
		self.Bind(wx.EVT_MENU, self.menuSaveAs, item )

		self.fileMenu.AppendSeparator()
		item = self.fileMenu.Append( wx.ID_PAGE_SETUP , "Page &Setup...", "Setup the print page" )
		self.Bind(wx.EVT_MENU, self.menuPageSetup, item )

		item = self.fileMenu.Append( wx.ID_PREVIEW , "Print P&review...\tCtrl+R", "Preview Results" )
		self.Bind(wx.EVT_MENU, self.menuPrintPreview, item )

		item = self.fileMenu.Append( wx.ID_PRINT , "&Print...\tCtrl+P", "Print Results" )
		self.Bind(wx.EVT_MENU, self.menuPrint, item )

		self.fileMenu.AppendSeparator()

		'''
		item = self.fileMenu.Append( wx.ID_ANY, "&Export to Excel...", "Export to an Excel Spreadsheet (.xls)" )
		self.Bind(wx.EVT_MENU, self.menuExportToExcel, item )
		
		item = self.fileMenu.Append( wx.ID_ANY, "Export to &HTML...", "Export to HTML (.html)" )
		self.Bind(wx.EVT_MENU, self.menuExportToHtml, item )

		self.fileMenu.AppendSeparator()
		'''
		
		recent = wx.Menu()
		menu = self.fileMenu.AppendSubMenu( recent, _("&Recent Files") )
		self.filehistory.UseMenu( recent )
		self.filehistory.AddFilesToMenu()
		
		self.fileMenu.AppendSeparator()

		item = self.fileMenu.Append( wx.ID_EXIT, "E&xit", "Exit" )
		self.Bind(wx.EVT_MENU, self.menuExit, item)
		
		self.Bind(wx.EVT_MENU_RANGE, self.menuFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9)
		
		self.menuBar.Append( self.fileMenu, "&File" )

		self.optionsMenu = wx.Menu()
		item = self.optionsMenu.Append( wx.ID_ANY, _("Set &Graphic..."), _("Set Graphic for Output") )
		self.Bind(wx.EVT_MENU, self.menuSetGraphic, item )
		
		self.menuBar.Append( self.optionsMenu, _("&Options") )

		#-----------------------------------------------------------------------
		
		self.toolsMenu = wx.Menu()
		item = self.toolsMenu.Append( wx.ID_ANY, _("Set &Root Folder"), _("Set Root Folder") )
		self.Bind(wx.EVT_MENU, self.menuSetRootFolder, item )
		
		item = self.toolsMenu.Append( wx.ID_ANY, _("Delete All Races..."), _("Delete All Races") )
		self.Bind(wx.EVT_MENU, self.menuDeleteAllRaces, item )
		
		self.toolsMenu.AppendSeparator()

		item = self.toolsMenu.Append( wx.ID_ANY , _("Copy Log File to &Clipboard..."), _("Copy Log File to &Clipboard") )
		self.Bind(wx.EVT_MENU, self.menuCopyLogFileToClipboard, item )
		
		self.menuBar.Append( self.toolsMenu, _("&Tools") )

		#-----------------------------------------------------------------------

		# Configure the main field of the display.

		self.notebook = wx.Notebook( self )
		self.notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanging )
		
		# Add all the pages to the notebook.
		self.pages = []

		def addPage( page, name ):
			self.notebook.AddPage( page, name )
			self.pages.append( page )
			
		self.attrClassName = [
			[ 'races',			Races,				'Races' ],
			[ 'results',		Results,			'Results' ],
			[ 'teamResults',	TeamResults,		'Team Results' ],
			[ 'points',			Points,				'Scoring Criteria' ],
			[ 'competitions',	Competitions,		'Competitions' ],
			[ 'categorySequence',CategorySequence,	'Category Options' ],
			[ 'upgrades',		Upgrades,			'Upgrades' ],
			[ 'errors',			Errors,				'Errors' ],
			[ 'options',		Options,			'Options' ],
			[ 'teamResultsNames', TeamResultsNames, 'Team Results Names' ],
			[ 'aliases',		Aliases,			'Name Aliases' ],
			[ 'licenseAliases',	AliasesLicense,		'License Aliases' ],
			[ 'teamAliases',	AliasesTeam,		'Team Aliases' ],
			[ 'categoryAliases',  AliasesCategory,  'Category Aliases' ],
		]
		
		for i, (a, c, n) in enumerate(self.attrClassName):
			setattr( self, a, c(self.notebook) )
			addPage( getattr(self, a), n )
			
		self.notebook.SetSelection( 0 )
		
		# Pages that are updated in background.
		self.backgroundUpdatePages = {'results', 'teamResults', 'categorySequence'}
		
		#-----------------------------------------------------------------------
		self.helpMenu = wx.Menu()

		item = self.helpMenu.Append( wx.ID_HELP , "&Help...", "Help about SeriesMgr..." )
		self.Bind(wx.EVT_MENU, self.menuHelp, item )
		
		self.helpMenu.AppendSeparator()

		item = self.helpMenu.Append( wx.ID_ABOUT , "&About...", "About SeriesMgr..." )
		self.Bind(wx.EVT_MENU, self.menuAbout, item )

		item = self.helpMenu.Append( wx.ID_ANY, "&Tips at Startup...", "Enable/Disable Tips at Startup..." )
		self.Bind(wx.EVT_MENU, self.menuTipAtStartup, item )

		self.menuBar.Append( self.helpMenu, "&Help" )

		#------------------------------------------------------------------------------
		self.SetMenuBar( self.menuBar )
		
		#------------------------------------------------------------------------------
		self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		sizer.Add( self.notebook, 1, flag=wx.EXPAND )
		self.SetSizer( sizer )
		
		wx.CallAfter( self.Refresh )

	def resetEvents( self ):
		self.events.reset()
		
	def menuTipAtStartup( self, event ):
		showing = self.config.ReadBool('showTipAtStartup', True)
		if Utils.MessageOKCancel( self, 'Turn Off Tips at Startup?' if showing else 'Show Tips at Startup?', 'Tips at Startup' ):
			self.config.WriteBool( 'showTipAtStartup', showing ^ True )

	def getDirName( self ):
		return Utils.getDirName()
		
	def getGraphicFName( self ):
		defaultFName = os.path.join(Utils.getImageFolder(), 'SeriesMgr128.png')
		graphicFName = self.config.Read( 'graphic', defaultFName )
		if graphicFName != defaultFName:
			try:
				with open(graphicFName, 'rb'):
					return graphicFName
			except IOError:
				pass
		return defaultFName
	
	def getGraphicBase64( self ):
		model = SeriesModel.model
		if model.graphicBase64 and model.graphicBase64.startswith('data:image/'):
			try:
				base64.standard_b64decode( model.graphicBase64.split(',',1)[1].encode() )
				return model.graphicBase64
			except Exception:
				pass
		
		graphicFName = self.getGraphicFName()
		if not graphicFName:
			return None
		fileType = os.path.splitext(graphicFName)[1].lower()
		if not fileType:
			return None
		fileType = fileType[1:]
		if fileType == 'jpg':
			fileType = 'jpeg'
		if fileType not in ['png', 'gif', 'jpeg']:
			return None
		try:
			with open(graphicFName, 'rb') as f:
				b64 = 'data:image/{};base64,{}'.format(fileType, base64.standard_b64encode(f.read()).decode())
				model.graphicBase64 = b64
				model.setChanged()
				self.setTitle()
				return b64
		except IOError:
			pass
		return None
	
	def menuSetGraphic( self, event ):
		imgPath = self.getGraphicFName()
		with SetGraphicDialog( self, graphic=imgPath ) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				imgPath = dlg.GetValue()
				self.config.Write( 'graphic', imgPath )
				self.config.Flush()
				
				SeriesModel.model.graphicBase64 = None
				self.getGraphicBase64()

	def menuSetRootFolder( self, event ):
		with wx.DirDialog(
				self,
				message='Set Root Folder where All Race Files can be Found',
				defaultPath=os.path.dirname(self.fileName) if self.fileName else '',
			) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				SeriesModel.model.setRootFolder( dlg.GetPath() )
				wx.CallAfter( self.refreshAll )

	def menuDeleteAllRaces( self, event ):
		if Utils.MessageOKCancel(self, "Delete All Races\n\nThere is no undo.   Continue?", "Delete All Races"):
			SeriesModel.model.removeAllRaces()
			self.refreshAll()			
		
	def menuPageSetup( self, event ):
		psdd = wx.PageSetupDialogData(self.printData)
		with wx.PageSetupDialog(self, psdd) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				# this makes a copy of the wx.PrintData instead of just saving
				# a reference to the one inside the PrintDialogData that will
				# be destroyed when the dialog is destroyed
				self.printData = wx.PrintData( dlg.GetPageSetupData().GetPrintData() )

	def getTitle( self ):
		model = SeriesModel.model
		iSelection = self.notebook.GetSelection()
		try:
			pageTitle = self.pages[iSelection].getTitle()
		except Exception:
			pageTitle = self.attrClassName[iSelection][2]
		
		if pageTitle == 'Results':
			return model.name
		return '{}\n{}'.format( pageTitle, model.name )
	
	def menuPrintPreview( self, event ):
		self.commit()
		title = self.getTitle()
		page = self.pages[self.notebook.GetSelection()]
		try:
			grid = page.getGrid()
			printout = SeriesMgrPrintout( title, grid )
			printout2 = SeriesMgrPrintout( title, grid )
		except AttributeError:
			return
		
		data = wx.PrintDialogData(self.printData)
		self.preview = wx.PrintPreview(printout, printout2, data)

		self.preview.SetZoom( 110 )
		if not self.preview.IsOk():
			return

		pfrm = wx.PreviewFrame(self.preview, self, "Print preview")

		pfrm.Initialize()
		pfrm.SetPosition(self.GetPosition())
		pfrm.SetSize(self.GetSize())
		pfrm.Show(True)

	def menuPrint( self, event ):
		self.commit()
		title = self.getTitle()
		page = self.pages[self.notebook.GetSelection()]
		try:
			grid = page.getGrid()
			printout = SeriesMgrPrintout( title, grid )
		except AttributeError:
			return
		
		pdd = wx.PrintDialogData(self.printData)
		pdd.EnablePageNumbers( 0 )
		pdd.EnableHelp( 0 )
		
		with wx.Printer(pdd) as printer:
			if not printer.Print(self, printout, True):
				if printer.GetLastError() == wx.PRINTER_ERROR:
					Utils.MessageOK(self, "There was a printer problem.\nCheck your printer setup.", "Printer Error", iconMask=wx.ICON_ERROR)
			else:
				self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )

	#--------------------------------------------------------------------------------------------

	def menuExportToExcel( self, event ):
		self.commit()
		iSelection = self.notebook.GetSelection()
		page = self.pages[iSelection]
		try:
			grid = page.getGrid()
		except Exception:
			return
		
		try:
			pageTitle = self.pages[iSelection].getTitle()
		except Exception:
			pageTitle = self.attrClassName[iSelection][2]
		
		if not self.fileName or len(self.fileName) < 4:
			Utils.MessageOK(self, 'You must Save before you can Export to Excel', 'Excel Write')
			return

		pageTitle = Utils.RemoveDisallowedFilenameChars( pageTitle.replace('/', '_') )
		xlfileName = self.fileName[:-4] + '-' + pageTitle + '.xls'
		with wx.DirDialog( self, 'Folder to write "{}"'.format(os.path.basename(xlfileName)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(xlfileName) ) as dlg:
			if dlg.ShowModal() != wx.ID_OK:
				return
			dName = dlg.GetPath()

		xlfileName = os.path.join( dName, os.path.basename(xlfileName) )

		title = self.getTitle()
		
		wb = xlwt.Workbook()
		sheetName = self.attrClassName[self.notebook.GetSelection()][2]
		sheetCur = wb.add_sheet( sheetName )
		export = ExportGrid( title, grid )
		export.toExcelSheet( sheetCur )

		try:
			wb.save( xlfileName )
			webbrowser.open( xlfileName, new = 2, autoraise = True )
			#Utils.MessageOK(self, 'Excel file written to:\n\n   {}'.format(xlfileName), 'Excel Export')
		except IOError:
			Utils.MessageOK(self,
						'Cannot write "{}".\n\nCheck if this spreadsheet is open.\nIf so, close it, and try again.'.format(xlfileName),
						'Excel File Error', iconMask=wx.ICON_ERROR )
						
	def menuExportToHtml( self, event ):
		self.commit()
		iSelection = self.notebook.GetSelection()
		page = self.pages[iSelection]
		try:
			grid = page.getGrid()
		except Exception:
			return
		
		try:
			pageTitle = self.pages[iSelection].getTitle()
		except Exception:
			pageTitle = self.attrClassName[iSelection][2]
		
		if not self.fileName or len(self.fileName) < 4:
			Utils.MessageOK(self, 'You must Save before you can Export to Html', 'Html Export')
			return

		pageTitle = Utils.RemoveDisallowedFilenameChars( pageTitle.replace('/', '_') )
		htmlfileName = self.fileName[:-4] + '-' + pageTitle + '.html'
		with wx.DirDialog( self, 'Folder to write "{}"'.format(os.path.basename(htmlfileName)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(htmlfileName) ) as dlg:
			if dlg.ShowModal() != wx.ID_OK:
				return
			dName = dlg.GetPath()

		htmlfileName = os.path.join( dName, os.path.basename(htmlfileName) )

		title = self.getTitle()
		
		html = StringIO()
		
		with tag(html, 'html'):
			with tag(html, 'head'):
				with tag(html, 'title'):
					html.write( title.replace('\n', ' ') )
				with tag(html, 'meta', {'charset':'UTF-8'}):
					pass
				for k, v in SeriesModel.model.getMetaTags():
					with tag(html, 'meta', {'name':k, 'content':v}):
						pass
				with tag(html, 'style', dict( type="text/css")):
					html.write( '''
body{ font-family: sans-serif; }

#idRaceName {
	font-size: 200%;
	font-weight: bold;
}
#idImgHeader { box-shadow: 4px 4px 4px #888888; }
.smallfont { font-size: 80%; }
.bigfont { font-size: 120%; }
.hidden { display: none; }

table.results
{
	font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
	border-collapse:collapse;
}
table.results td, table.results th 
{
	font-size:1em;
	padding:3px 7px 2px 7px;
	text-align: left;
}
table.results th 
{
	font-size:1.1em;
	text-align:left;
	padding-top:5px;
	padding-bottom:4px;
	background-color:#7FE57F;
	color:#000000;
}
table.results tr.odd
{
	color:#000000;
	background-color:#EAF2D3;
}
table.results tr:hover
{
	color:#000000;
	background-color:#FFFFCC;
}
table.results tr.odd:hover
{
	color:#000000;
	background-color:#FFFFCC;
}

table.results td {
	border-top:1px solid #98bf21;
}

table.results td.noborder {
	border-top:0px solid #98bf21;
}

table.results td.rAlign, table.results th.rAlign {
	text-align:right;
}

table.results tr td.fastest{
	color:#000000;
	background-color:#80FF80;
}

@media print { .noprint { display: none; } }''' )

			with tag(html, 'body'):
				ExportGrid( title, grid ).toHtml(html)
		
		html = html.getvalue()
		
		try:
			with open(htmlfileName, 'w') as fp:
				fp.write( html )
			webbrowser.open( htmlfileName, new = 2, autoraise = True )
			#Utils.MessageOK(self, 'Html file written to:\n\n  [}'.format(htmlfileName), 'Html Write')
		except IOError:
			Utils.MessageOK(self,
						'Cannot write "{}".\n\nCheck if this file is open.\nIf so, close it, and try again.'.format(htmlfileName),
						'Html File Error', iconMask=wx.ICON_ERROR )
	
	#--------------------------------------------------------------------------------------------
	def menuCopyLogFileToClipboard( self, event ):
		try:
			logData = open(redirectFileName).read()
		except IOError:
			Utils.MessageOK(self, _("Unable to open log file."), _("Error"), wx.ICON_ERROR )
			return
			
		logData = logData.split( '\n' )
		logData = logData[-1000:]
		logData = '\n'.join( logData )
		
		dataObj = wx.TextDataObject()
		dataObj.SetText(logData)
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData( dataObj )
			wx.TheClipboard.Close()
			Utils.MessageOK(self, _("Log file copied to clipboard.\nYou can now paste it into an email."), _("Success") )
		else:
			Utils.MessageOK(self, "Unable to open the clipboard.", "Error", wx.ICON_ERROR )
	
	#--------------------------------------------------------------------------------------------

	def saveExistingSeries( self ):
		self.commit()
		self.showPageName( 'Races' )
		model = SeriesModel.model
		if not model.changed:
			return True
			
		ret = Utils.MessageYesNoCancel( self, 'Save Existing Series?', 'Save Existing Series?' ) 
		if ret == wx.ID_YES:
			self.writeSeries()
			return True
		elif ret == wx.ID_NO:
			return True
		else:
			return False
	
	def onCloseWindow( self, event ):
		if self.saveExistingSeries():
			wx.Exit()

	def writeSeries( self ):
		self.commit()
		if not self.fileName:
			self.setTitle()
			return
		model = SeriesModel.model
		
		# Make the race file name relative to the series file name.
		model.racesFullToRelative( self.fileName )
		with open(self.fileName, 'wb') as fp:
			pickle.dump( model, fp, 2 )
		# Reset back to full file names.
		model.racesRelativeToFull( self.fileName )
		
		model.setChanged( False )
		self.setTitle()

	def menuNew( self, event ):
		if self.saveExistingSeries():
			SeriesModel.model = SeriesModel.SeriesModel()
			SeriesModel.model.postReadFix()
			
			self.fileName = ''
			self.showPageName( 'Races' )
			self.refresh()
	
	def updateRecentFiles( self ):
		self.filehistory.AddFileToHistory(self.fileName)
		self.filehistory.Save(self.config)
		self.config.Flush()
		
	def fixPaths( self ):
		model = SeriesModel.model
		if not self.fileName or not model:
			return False

		# Check if we can find all race files.
		for r in model.races:
			if not os.path.isfile( r.fileName ):
				dirname = os.path.dirname( r.fileName )
				fname = os.path.basename( r.fileName )
				break
		else:
			return False
		
		# Check if all the race files are rooted from the same folder as the .smn file.
		path = os.path.dirname(self.fileName)
		if model.setRootFolderWillSucceed( path ):
			model.setRootFolder( path )
			return True
		
		# Otherwise, ask the user where the Root folder is.
		if not Utils.MessageOKCancel(
				self,
				'Cannot find Race File:\n\n    "{}"\nin    "{}"\n\nSet new Root Folder?'.format(fname, dirname),
				'Cannot find Race Files'
				):
			return False
		
		with wx.DirDialog(
				self,
				message='Select Root Folder where all Race Files can be found:',
				defaultPath=os.path.dirname(self.fileName) if self.fileName else '',
			) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				result = model.setRootFolder( dlg.GetPath() )
			else:
				result = False
		
		return result
		
	def openSeries( self, fileName ):
		if not fileName:
			return
		
		self.commit()
		self.showPageName( 'Races' )
		self.refresh()
		
		try:
			with open(fileName, 'rb') as fp:
				try:
					SeriesModel.model = pickle.load( fp, encoding='latin1', errors='replace' )
				except Exception as e:
					fp.seek( 0 )
					SeriesModel.model = ModuleUnpickler( fp, module='SeriesMgr', encoding='latin1', errors='replace' ).load()
		except IOError:
			Utils.MessageOK(self, f'Cannot Open File "{fileName}".', 'Cannot Open File', iconMask=wx.ICON_ERROR )
			return
		
		SeriesModel.model.postReadFix()
		self.fileName = fileName
		SeriesModel.model.racesRelativeToFull( self.fileName )
		self.updateRecentFiles()
		
		SeriesModel.model.setChanged( self.fixPaths() )
		self.readResetAll()
		try:
			self.refreshAll()
		except Exception as e:
			Utils.MessageOK(self, 'Error:\n\n"{}\n\n{}".'.format(e, traceback.format_exc()), 'Error', iconMask=wx.ICON_ERROR )
		self.showPageName( 'Races' )

	def menuOpen( self, event ):
		if SeriesModel.model.changed:
			if Utils.MessageOKCancel(self, 'You have Unsaved Changes.  Save Now?', 'Unsaved Changes'):
				try:
					self.writeSeries()
				except Exception:
					Utils.MessageOK(self, f'Write Failed.  Series NOT saved..\n\n    "{self.fileName}"', 'Write Failed', iconMask=wx.ICON_ERROR )
					return
				
		with wx.FileDialog( self, message="Choose a file for your Competition",
							defaultFile = '',
							wildcard = 'SeriesMgr files (*.smn)|*.smn',
							style=wx.FD_OPEN | wx.FD_CHANGE_DIR ) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.openSeries( dlg.GetPath() )

	def menuSave( self, event ):
		if not self.fileName:
			self.menuSaveAs( event )
			return
		
		try:
			self.writeSeries()
		except Exception:
			Utils.MessageOK(self, f'Write Failed.  Series NOT saved.\n\n    "{self.fileName}".', 'Write Failed', iconMask=wx.ICON_ERROR )
		self.updateRecentFiles()

	def setTitle( self ):
		if self.fileName:
			title = '{}{} - {}'.format('*' if SeriesModel.model.changed else '', self.fileName, Version.AppVerName)
		else:
			title = Version.AppVerName
		self.SetTitle( title )
			
	def menuSaveAs( self, event ):
		with wx.FileDialog( self, message="Choose a file for your Series",
							defaultFile = '',
							wildcard = 'SeriesMgr files (*.smn)|*.smn',
							style=wx.FD_SAVE | wx.FD_CHANGE_DIR ) as dlg:
			if dlg.ShowModal() != wx.ID_OK:
				return
			fileName = dlg.GetPath()
		
		if not fileName.endswith('.smn'):
			fileName += '.smn'
		
		try:
			with open(fileName, 'rb'):
				pass
			if not Utils.MessageOKCancel(self, f'File Exists.\n\n    "{fileName}"\n\nReplace?', 'File Exists'):
				return
		except IOError:
			pass
		
		try:
			with open(fileName, 'wb'):
				pass
		except Exception:
			Utils.MessageOK(self, f'Cannot open file:\n\n    "{fileName}"', 'Cannot Open File', iconMask=wx.ICON_ERROR )
			return
			
		self.fileName = fileName
		self.menuSave( event )
		
	def menuFileHistory( self, event ):
		fileNum = event.GetId() - wx.ID_FILE1
		fileName = self.filehistory.GetHistoryFile(fileNum)
		self.filehistory.AddFileToHistory(fileName)  # move up the list
		self.openSeries( fileName )
	
	def menuHelp( self, event ):
		fname = os.path.join( Utils.getHelpFolder().replace('CrossMgrHtmlDoc','SeriesMgrHtmlDoc'), 'QuickStart.html' )
		Utils.LaunchApplication( fname )
	
	def menuExit(self, event):
		self.onCloseWindow( event )

	def menuAbout( self, event ):
		# First we create and fill the info object
		info = wx.adv.AboutDialogInfo()
		info.Name = Version.AppVerName
		info.Version = ''
		info.Copyright = "(C) 2013-{}".format(datetime.datetime.now().year)
		info.Description = wordwrap(
			"Combine CrossMgr results into a Series.\n\n"
			"",
			500, wx.ClientDC(self))
		info.WebSite = ("http://sites.google.com/site/crossmgrsoftware/", "CrossMgr Home Page")
		info.Developers = [
					"Edward Sitarski (edward.sitarski@gmail.com)"
					]

		licenseText = "User Beware!\n\n" \
			"This program is experimental, under development and may have bugs.\n" \
			"Feedback is sincerely appreciated.\n\n" \
			"Donations are also appreciated - see website for details.\n\n" \
			"CRITICALLY IMPORTANT MESSAGE!\n" \
			"This program is not warrented for any use whatsoever.\n" \
			"It may not produce correct results, it might lose your data.\n" \
			"The authors of this program assume no reponsibility or liability for data loss or erronious results produced by this program.\n\n" \
			"Use entirely at your own risk.\n" \
			"Do not come back and tell me that this program screwed up your event!\n" \
			"Computers fail, screw-ups happen.  Always use a paper manual backup."
		info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

		wx.adv.AboutBox(info)

	#--------------------------------------------------------------------------------------

	def getCurrentPage( self ):
		return self.pages[self.notebook.GetSelection()]
	
	def showPage( self, iPage ):
		self.callPageCommit( self.notebook.GetSelection() )
		self.callPageRefresh( iPage )
		#self.notebook.ChangeSelection( iPage )
		self.notebook.SetSelection( iPage )
		self.pages[self.notebook.GetSelection()].Layout()
		self.Layout()

	def showPageName( self, name ):
		name = name.replace(' ', '')
		for i, (a, c, n) in enumerate(self.attrClassName):
			if n == name:
				self.showPage( i )
				break

	def commit( self ):
		self.callPageCommit( self.notebook.GetSelection() )
		self.setTitle()
				
	def refreshCurrentPage( self ):
		self.setTitle()
		self.callPageRefresh( self.notebook.GetSelection() )

	def refresh( self ):
		self.refreshCurrentPage()

	def callPageRefresh( self, i ):
		if Counter.getCount() and self.attrClassName[self.notebook.GetSelection()][0] in self.backgroundUpdatePages:
			# Don't update the page while a background update is running.
			# The page will be updated when the update finishes.
			return
		try:
			self.pages[i].refresh()
		except (AttributeError, IndexError) as e:
			pass

	def callPageCommit( self, i ):
		try:
			self.pages[i].commit()
			self.setTitle()
		except (AttributeError, IndexError) as e:
			pass

	def onPageChanging( self, event ):
		self.callPageCommit( event.GetOldSelection() )
		self.callPageRefresh( event.GetSelection() )
		event.Skip()	# Required to properly repaint the screen.

	def refreshAll( self ):
		self.refresh()
		
		model = SeriesModel.model
		
		self.results.refresh( backgroundUpdate=True )
		self.teamResults.refresh( backgroundUpdate=True )
		self.categorySequence.refresh( backgroundUpdate=True )
		
		# Use a thread to update Results and TeamResults.
		# This eliminates user timeouts.
		def backgroundRefresh():
			with Counter():
				model.extractAllRaceResults()
				wx.CallAfter( self.results.refresh )
				wx.CallAfter( self.teamResults.refresh )
				wx.CallAfter( self.categorySequence.refresh )
				wx.CallAfter( wx.EndBusyCursor )	# End the busy cursor at the end of the thread.
		
		wx.BeginBusyCursor()	# Start a busy cursor befpre we start the thread.
		t = threading.Thread( target=backgroundRefresh, name='refreshResultsBackground' )
		t.start()
		
		pagesToSkip = self.backgroundUpdatePages | { self.attrClassName[self.notebook.GetSelection()][0] }
		for i, p in enumerate(self.pages):
			if self.attrClassName[i][0] not in pagesToSkip:
				self.callPageRefresh( i )

	def readResetAll( self ):
		for p in self.pages:
			try:
				p.readReset()
			except AttributeError:
				pass
		
# Set log file location.
dataDir = ''
redirectFileName = ''
locale = None

def MainLoop():
	global dataDir
	global redirectFileName
	global locale
	
	random.seed()

	app = wx.App(False)
	app.SetAppName("SeriesMgr")
	
	parser = ArgumentParser( epilog='Example: {} --series MySeries.smn --races MyRace1.cmn=RegularPoints" "MyRace2.cmn=DoublePoints" MyRace2.cmn'.format(os.path.basename(sys.argv[0])) )
	parser.add_argument("filename", help="series file", nargs="?", metavar="SeriesFile.smn")
	parser.add_argument("-q", "--quiet", action="store_false", dest="verbose", default=True, help='hide splash screen')
	parser.add_argument("-r", "--regular", action="store_false", dest="fullScreen", default=True, help='regular size (not full screen)')
	parser.add_argument('--series', default=None, metavar="SeriesFile.smn", help='Specifiy a <series_mgr_file>.smn file to use for the points structures.  Optional if --score_by_time or --score_by_points options are used.')
	parser.add_argument('--score_by_points', action='store_true', help='If specified, races will be scored by the points structures.  This is the default.' )
	parser.add_argument('--score_by_time', action='store_true', help='If specified, races will be scored by the total time.' )
	parser.add_argument('--score_by_percent', action='store_true', help='If specified, races will be scored by the percent of the winning time.' )
	parser.add_argument('--output', default=None, help='Output file (default is <series_mgr_file>.html)' )
	parser.add_argument('--races', metavar="Race.cmn[=point_structure]", nargs='+', default=[],
		help='  '.join( (
			'Each race is of the form "Race.cmn[=point_structure]" and Race.cmn is a CrossMgr race, with the optional name of the points structure of the series to use to score that race.',
			'If no point_structure is specified for a race, the first point_structure in the --series will be used.',
			'No point_structure is required if the --score_by_time or --score_by_percent options are specified.',
			'If no --races are defined, the races defined in the --series file will be used.',
		) )
	)
	args = parser.parse_args()
	
	if not args.filename and any(
			[args.series, args.score_by_points, args.score_by_time, args.score_by_percent, args.output, args.races]):
		sys.exit( CmdLine.CmdLine(args) )

	dataDir = Utils.getHomeDir()
	redirectFileName = os.path.join(dataDir, 'SeriesMgr.log')
	
	# Set up the log file.  Otherwise, show errors on the screen unbuffered.
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
	
	Utils.initTranslation()
	locale = wx.Locale(wx.LANGUAGE_ENGLISH)	

	Utils.writeLog( 'start: {}'.format(Version.AppVerName) )
	
	# Configure the main window.
	sWidth, sHeight = wx.GetDisplaySize()
	mainWin = MainWin( None, title=Version.AppVerName, size=(int(sWidth*0.9),int(sHeight*0.9)) )
	if args.fullScreen:
		mainWin.Maximize( True )
		
	mainWin.refreshAll()
	mainWin.CenterOnScreen()
	mainWin.Show()

	# Set the upper left icon.
	icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'SeriesMgr.ico'), wx.BITMAP_TYPE_ICO )
	#mainWin.SetIcon( icon )

	# Set the taskbar icon.
	#tbicon = wx.TaskBarIcon()
	#tbicon.SetIcon( icon, "SeriesMgr" )

	if args.verbose:
		ShowSplashScreen()
	#	ShowTipAtStartup()
	
	# Try to open a specified filename.
	fileName = args.filename
	
	# Try to load a series.
	if fileName:
		if os.path.splitext( fileName )[1] != '.smn':
			print( f'Cannot open non SeriesMgr file "{fileName}".  Aborting.', file=sys.stderr )
			sys.exit( 1 )
		try:
			mainWin.openSeries( fileName )
		except (IndexError, AttributeError, ValueError):
			pass

	# Start processing events.
	mainWin.GetSizer().Layout()
	try:
		app.MainLoop()
	except Exception:
		xc = traceback.format_exception(*sys.exc_info())
		wx.MessageBox(''.join(xc))

if __name__ == '__main__':
	MainLoop()
