# -*- coding: utf-8 -*-
import wx
from wx.lib.wordwrap import wordwrap
import wx.lib.imagebrowser as imagebrowser
import wx.lib.agw.flatnotebook as flatnotebook
import os
import re
import io
import cgi
import sys
import time
import copy
import json
import random
import bisect
import datetime
import webbrowser
import zipfile
import base64
import hashlib
import urllib

import locale
try:
	localDateFormat = locale.nl_langinfo( locale.D_FMT )
	localTimeFormat = locale.nl_langinfo( locale.T_FMT )
except:
	localDateFormat = '%b %d, %Y'
	localTimeFormat = '%I:%M%p'

import cPickle as pickle
from optparse import OptionParser
import xlwt
import xlsxwriter
from setpriority import setpriority

import Utils

from LogPrintStackStderr import LogPrintStackStderr
from ForecastHistory	import ForecastHistory
from NumKeypad			import NumKeypad
from Actions			import Actions
from Gantt				import Gantt
from History			import History
from RiderDetail		import RiderDetail
from Results			import Results
from Categories			import Categories, PrintCategories
from Properties			import Properties, PropertiesDialog, ChangeProperties
from Recommendations	import Recommendations
from RaceAnimation		import RaceAnimation, GetAnimationData
from Search				import SearchDialog
from Situation			import Situation
from LapCounter			import LapCounter
from Primes				import Primes, GetGrid
import FtpWriteFile
from FtpWriteFile		import realTimeFtpPublish
from SetAutoCorrect		import SetAutoCorrectDialog
from DNSManager			import DNSManagerDialog
from USACExport			import USACExport
from UCIExport			import UCIExport
from VTTAExport			import VTTAExport
from CrossResultsExport	import CrossResultsExport
from WebScorerExport	import WebScorerExport
from HelpSearch			import HelpSearchDialog
from Utils				import logCall, logException
from FileDrop			import FileDrop
import Model
import JChipSetup
import JChipImport
import JChip
from JChip import EVT_CHIP_READER 
import OrionImport
import AlienImport
import ImpinjImport
import OutputStreamer
import GpxImport
from Undo import undo
from Printing			import CrossMgrPrintout, CrossMgrPrintoutPNG, CrossMgrPodiumPrintout, getRaceCategories
from Printing			import ChoosePrintCategoriesDialog, ChoosePrintCategoriesPodiumDialog
from ExportGrid			import ExportGrid
import SimulationLapTimes
import Version
from ReadSignOnSheet	import GetExcelLink, ResetExcelLinkCache, ExcelLink, ReportFields, SyncExcelLink, IsValidRaceDBExcel
from SetGraphic			import SetGraphicDialog
from GetResults			import GetCategoryDetails, UnstartedRaceWrapper, GetLapDetails
from PhotoFinish		import DeletePhotos, okTakePhoto
from SendPhotoRequests	import SendPhotoRequests
from PhotoViewer		import PhotoViewerDialog
from ReadTTStartTimesSheet import ImportTTStartTimes, AutoImportTTStartTimes
from TemplateSubstitute import TemplateSubstitute
import ChangeRaceStartTime
from PageDialog			import PageDialog

import traceback
'''
# Monkey patch threading so we can see where each thread gets started.
import traceback
import types
threading_start = threading.Thread.start
def loggingThreadStart( self, *args, **kwargs ):
	threading_start( self, *args, **kwargs )
	print self
	traceback.print_stack()
	print '----------------------------------'
threading.Thread.start = types.MethodType(loggingThreadStart, None, threading.Thread)
'''
#----------------------------------------------------------------------------------

def ShowSplashScreen():
	bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'CrossMgrSplash.png'), wx.BITMAP_TYPE_PNG )
	
	# Write in the version number into the bitmap.
	w, h = bitmap.GetSize()
	dc = wx.MemoryDC()
	dc.SelectObject( bitmap )
	dc.SetFont( wx.FontFromPixelSize( wx.Size(0,h//10), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL ) )
	dc.DrawText( Version.AppVerName.replace('CrossMgr','Version'), w // 20, int(h * 0.44) )
	dc.SelectObject( wx.NullBitmap )
	
	showSeconds = 2.5
	frame = wx.SplashScreen(bitmap, wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT, int(showSeconds*1000), None)
			
#----------------------------------------------------------------------------------
		
class MyTipProvider( wx.PyTipProvider ):
	def __init__( self, fname, tipNo = None ):
		self.tips = []
		try:
			with open(fname, 'r') as f:
				for line in f:
					line = line.strip()
					if line and line[0] != '#':
						self.tips.append( line )
			if tipNo is None:
				tipNo = (int(round(time.time() * 1000)) * 13) % (len(self.tips) - 1)
		except:
			pass
		if tipNo is None:
			tipNo = 0
		self.tipNo = tipNo
		wx.PyTipProvider.__init__( self, self.tipNo )
			
	def GetCurrentTip( self ):
		if self.tipNo < 0 or self.tipNo >= len(self.tips):
			self.tipNo = 0
		return self.tipNo
		
	def GetTip( self ):
		if not self.tips:
			return _('No tips available.')
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
	except:
		pass

def replaceJsonVar( s, varName, value ):
	return s.replace( u'%s = null' % varName, u'%s = %s' % (varName, json.dumps(value)), 1 )

#----------------------------------------------------------------------------------
def AppendMenuItemBitmap( menu, id, name, help, bitmap ):
	mi = wx.MenuItem( menu, id, name, help )
	mi.SetBitmap( bitmap )
	menu.AppendItem( mi )
		
class MainWin( wx.Frame ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(200,200) ):
		wx.Frame.__init__(self, parent, id, title, size=size)

		Utils.setMainWin( self )
		
		self.updateLater = None	# Used for delayed updates after chip reads.
		self.numTimes = []

		# Add code to configure file history.
		self.filehistory = wx.FileHistory(8)
		self.config = wx.Config(appName="CrossMgr",
								vendorName="SmartCyclingSolutions",
								style=wx.CONFIG_USE_LOCAL_FILE)
		self.filehistory.Load(self.config)
		
		self.fileName = None
		self.numSelect = None
		
		# Setup the objects for the race clock.
		self.timer = wx.Timer( self, id=wx.NewId() )
		self.secondCount = 0
		self.Bind( wx.EVT_TIMER, self.updateRaceClock, self.timer )

		self.simulateTimer = None
		self.simulateSeen = set()

		# Default print options.
		self.printData = wx.PrintData()
		self.printData.SetPaperId(wx.PAPER_LETTER)
		self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
		self.printData.SetOrientation(wx.LANDSCAPE)

		# Configure the main menu.
		self.menuBar = wx.MenuBar(wx.MB_DOCKABLE)

		#-----------------------------------------------------------------------
		self.fileMenu = wx.Menu()

		AppendMenuItemBitmap( self.fileMenu, wx.ID_NEW , _("&New..."), _("Create a new race"), Utils.GetPngBitmap('document-new.png') )
		self.Bind(wx.EVT_MENU, self.menuNew, id=wx.ID_NEW )

		idCur = wx.NewId()
		AppendMenuItemBitmap( self.fileMenu, idCur , _("New Nex&t..."), _("Create a new race starting from the current race"), Utils.GetPngBitmap('document-new-next.png') )
		self.Bind(wx.EVT_MENU, self.menuNewNext, id=idCur )

		self.fileMenu.AppendSeparator()
		
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.fileMenu, idCur , _("New from &RaceDB..."), _("Create a new race from RaceDB output"), Utils.GetPngBitmap('database-add.png') )
		self.Bind(wx.EVT_MENU, self.menuNewRaceDB, id=idCur )

		self.fileMenu.AppendSeparator()
		AppendMenuItemBitmap( self.fileMenu, wx.ID_OPEN , _("&Open..."), _("Open a race"), Utils.GetPngBitmap('document-open.png') )
		self.Bind(wx.EVT_MENU, self.menuOpen, id=wx.ID_OPEN )

		idCur = wx.NewId()
		self.fileMenu.Append( idCur , _("Open N&ext..."), _("Open the next race starting from the current race") )
		self.Bind(wx.EVT_MENU, self.menuOpenNext, id=idCur )

		self.fileMenu.AppendSeparator()
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.fileMenu, idCur , _("&Restore from Original Input..."), _("Restore from Original Input"),
			Utils.GetPngBitmap('document-revert.png') )
		self.Bind(wx.EVT_MENU, self.menuRestoreFromInput, id=idCur )

		self.fileMenu.AppendSeparator()
		
		recent = wx.Menu()
		menu = self.fileMenu.AppendMenu(wx.ID_ANY, _("Recent Fil&es"), recent)
		menu.SetBitmap( Utils.GetPngBitmap('document-open-recent.png') )
		self.filehistory.UseMenu( recent )
		self.filehistory.AddFilesToMenu()
		
		self.fileMenu.AppendSeparator()
		
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.fileMenu, idCur, _('&Close Race'), _('Close this race without exiting CrossMgr'),
			Utils.GetPngBitmap('document-close.png') )
		self.Bind(wx.EVT_MENU, self.menuCloseRace, id=idCur )
		
		AppendMenuItemBitmap( self.fileMenu, wx.ID_EXIT, _("E&xit"), _("Exit CrossMgr"), Utils.GetPngBitmap('exit.png') )
		self.Bind(wx.EVT_MENU, self.menuExit, id=wx.ID_EXIT )
		
		self.Bind(wx.EVT_MENU_RANGE, self.menuFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9)
		
		self.menuBar.Append( self.fileMenu, _("&File") )

		#-----------------------------------------------------------------------
		self.publishMenu = wx.Menu()
		
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur, _("Page &Setup..."), _("Setup the print page"), Utils.GetPngBitmap('page-setup.png') )
		self.Bind(wx.EVT_MENU, self.menuPageSetup, id=idCur )

		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur, _("P&review Print Results..."), _("Preview the printed results on screen"),
								Utils.GetPngBitmap('print-preview.png') )
		self.Bind(wx.EVT_MENU, self.menuPrintPreview, id=idCur )

		AppendMenuItemBitmap( self.publishMenu, wx.ID_PRINT, _("&Print Results..."), _("Print the results to a printer"),
								Utils.GetPngBitmap('Printer.png') )
		self.Bind(wx.EVT_MENU, self.menuPrint, id=wx.ID_PRINT )

		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur, _("Print P&odium Results..."), _("Print the top position results to a printer"),
								Utils.GetPngBitmap('Podium.png') )
		self.Bind(wx.EVT_MENU, self.menuPrintPodium, id=idCur )

		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur , _("Print C&ategories..."), _("Print Categories"), Utils.GetPngBitmap('categories.png') )
		self.Bind(wx.EVT_MENU, self.menuPrintCategories, id=idCur )

		self.publishMenu.AppendSeparator()
		
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur,
							_("&Excel Publish..."), _("Publish Results as an Excel Spreadsheet (.xls)"), Utils.GetPngBitmap('excel-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuPublishAsExcel, id=idCur )
		
		self.publishMenu.AppendSeparator()
		
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur,
							_("&HTML Publish..."), _("Publish Results as HTML (.html)"), Utils.GetPngBitmap('html-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuPublishHtmlRaceResults, id=idCur )

		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur,
							_("&Ftp HTML Publish..."), _("Publish HTML Results to FTP"),
							Utils.GetPngBitmap('ftp-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuExportHtmlFtp, id=idCur )

		self.publishMenu.AppendSeparator()
		
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur,
							_("&CrossResults.com Publish..."), _("Publish Results to the CrossResults.com web site"),
							Utils.GetPngBitmap('crossresults-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuExportCrossResults, id=idCur )

		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur,
							_("&WebScorer.com Publish..."), _("Publish Results in WebScorer.com format"),
							Utils.GetPngBitmap('webscorer-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuExportWebScorer, id=idCur )

		self.publishMenu.AppendSeparator()
		
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur,
							_("&USAC Excel Publish..."), _("Publish Results in USAC Excel Format"),
							Utils.GetPngBitmap('usac-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuExportUSAC, id=idCur )

		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur,
							_("UCI (&Infostrada) Excel Publish..."), _("Publish Results in UCI (&Infostrada) Excel Format"),
							Utils.GetPngBitmap('infostrada-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuExportUCI, id=idCur )

		self.publishMenu.AppendSeparator()
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur,
							_("&VTTA Excel Publish..."), _("Publish Results in Excel Format for VTTA analysis"),
							Utils.GetPngBitmap('vtta-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuExportVTTA, id=idCur )

		self.publishMenu.AppendSeparator()
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur,
							_("&Facebook PNG Publish..."), _("Publish Results as PNG files for posting on Facebook"),
							Utils.GetPngBitmap('facebook-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuPrintPNG, id=idCur )
		
		self.publishMenu.AppendSeparator()
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.publishMenu, idCur,
							_("TT Start HTML Publish..."), _("Publish Time Trial Start page"),
							Utils.GetPngBitmap('stopwatch-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuPublishHtmlTTStart, id=idCur )
		
		self.menuBar.Append( self.publishMenu, _("&Publish") )
		
		#-----------------------------------------------------------------------
		self.editMenu = wx.Menu()
		self.undoMenuButton = wx.MenuItem( self.editMenu, wx.ID_UNDO , _("&Undo\tCtrl+Z"), _("Undo the last edit") )
		img = wx.Image(os.path.join(Utils.getImageFolder(), 'Undo-icon.png'))
		self.undoMenuButton.SetBitmap( img.ConvertToBitmap(8) )
		self.editMenu.AppendItem( self.undoMenuButton )
		self.Bind(wx.EVT_MENU, self.menuUndo, id=wx.ID_UNDO )
		self.undoMenuButton.Enable( False )

		self.redoMenuButton = wx.MenuItem( self.editMenu, wx.ID_REDO , _("&Redo\tCtrl+Y"), _("Redo the last edit") )
		img = wx.Image(os.path.join(Utils.getImageFolder(), 'Redo-icon.png'))
		self.redoMenuButton.SetBitmap( img.ConvertToBitmap(8) )
		self.editMenu.AppendItem( self.redoMenuButton )
		self.Bind(wx.EVT_MENU, self.menuRedo, id=wx.ID_REDO )
		self.redoMenuButton.Enable( False )
		self.editMenu.AppendSeparator()
		
		self.editMenu.Append( wx.ID_FIND, _("&Find...\tCtrl+F"), _("Find a Rider") )
		self.Bind(wx.EVT_MENU, self.menuFind, id=wx.ID_FIND )
		
		self.editMenu.AppendSeparator()
		idCur = wx.NewId()
		self.editMenu.Append( idCur, _('&Change "Autocorrect"...'), _('Change "Autocorrect"...') )
		self.Bind( wx.EVT_MENU, self.menuAutocorrect, id=idCur )
		
		img = None
		self.editMenuItem = self.menuBar.Append( self.editMenu, _("&Edit") )

		#-----------------------------------------------------------------------
		self.dataMgmtMenu = wx.Menu()
		
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.dataMgmtMenu, idCur , _("&Link to External Excel Data..."), _("Link to information in an Excel spreadsheet"),
			Utils.GetPngBitmap('excel-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuLinkExcel, id=idCur )
		
		self.dataMgmtMenu.AppendSeparator()
		
		#-----------------------------------------------------------------------
		idCur = wx.NewId()
		self.dataMgmtMenu.Append( idCur, _('&Add DNS from External Excel Data...'), _('Add DNS...') )
		self.Bind( wx.EVT_MENU, self.menuDNS, id=idCur )
		
		self.dataMgmtMenu.AppendSeparator()
		
		#-----------------------------------------------------------------------
		idCur = wx.NewId()
		AppendMenuItemBitmap(self.dataMgmtMenu, idCur , _("&Import Time Trial Start Times..."), _("Import Time Trial Start Times"),
			Utils.GetPngBitmap('clock-add.png') )
		self.Bind(wx.EVT_MENU, self.menuImportTTStartTimes, id=idCur )
		
		#-----------------------------------------------------------------------
		self.dataMgmtMenu.AppendSeparator()
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.dataMgmtMenu, idCur , _("&Import Course in GPX format..."), _("Import Course in GPX format"),
			Utils.GetPngBitmap('gps-icon.png') )
		self.Bind(wx.EVT_MENU, self.menuImportGpx, id=idCur )
		
		self.exportGpxMenu = wx.Menu()
		
		idCur = wx.NewId()
		self.exportGpxMenu.Append( idCur, _("in GPX Format..."), _("Export Course in GPX format") )
		self.Bind(wx.EVT_MENU, self.menuExportGpx, id=idCur )
		
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.exportGpxMenu, idCur , _("as HTML &Preview..."),
			_("Export Course Preview in HTML"),
			Utils.GetPngBitmap('html-icon.png')
		)
		self.Bind(wx.EVT_MENU, self.menuExportCoursePreviewAsHtml, id=idCur )
		
		idCur = wx.NewId()
		AppendMenuItemBitmap( self.exportGpxMenu, idCur,
			_("as KMZ Virtual Tour..."),
			_("Export Course as KMZ Virtual Tour (Requires Google Earth to View)"),
			Utils.GetPngBitmap('Google-Earth-icon.png')
		)
		self.Bind(wx.EVT_MENU, self.menuExportCourseAsKml, id=idCur )
		
		self.dataMgmtMenu.AppendMenu( wx.NewId(), _('Export Course'), self.exportGpxMenu  )
		
		#-----------------------------------------------------------------------
		
		self.dataMgmtMenu.AppendSeparator()
		
		idCur = wx.NewId()
		self.dataMgmtMenu.Append( idCur , _("&Import Categories from File..."), _("Import Categories from File") )
		self.Bind(wx.EVT_MENU, self.menuImportCategories, id=idCur )

		idCur = wx.NewId()
		self.dataMgmtMenu.Append( idCur , _("&Export Categories to File..."), _("Export Categories to File") )
		self.Bind(wx.EVT_MENU, self.menuExportCategories, id=idCur )
		
		self.dataMgmtMenu.AppendSeparator()

		idCur = wx.NewId()
		self.dataMgmtMenu.Append( idCur , _("Export History to Excel..."), _("Export History to Excel File") )
		self.Bind(wx.EVT_MENU, self.menuExportHistory, id=idCur )

		idCur = wx.NewId()
		self.dataMgmtMenu.Append( idCur , _("Export Raw Data as &HTML..."), _("Export raw data as HTML (.html)") )
		self.Bind(wx.EVT_MENU, self.menuExportHtmlRawData, id=idCur )

		self.menuBar.Append( self.dataMgmtMenu, _("&DataMgmt") )

		#----------------------------------------------------------------------------------------------

		# Configure the field of the display.

		# Forecast/History shown in left pane of scrolled window.
		forecastHistoryWidth = 265
		sty = wx.BORDER_SUNKEN
		self.splitter = wx.SplitterWindow( self )
		self.splitter.SetMinimumPaneSize( forecastHistoryWidth )
		self.forecastHistory = ForecastHistory( self.splitter, style=sty )

		# Other data shown in right pane.
		bookStyle = (
			  flatnotebook.FNB_NO_X_BUTTON
			| flatnotebook.FNB_FF2
			| flatnotebook.FNB_NODRAG
			| flatnotebook.FNB_DROPDOWN_TABS_LIST
			| flatnotebook.FNB_NO_NAV_BUTTONS
		)
		self.notebook = flatnotebook.FlatNotebook( self.splitter, 1000, agwStyle=bookStyle )
		self.notebook.SetBackgroundColour( wx.WHITE )
		self.notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanging )
		
		self.fileDrop = FileDrop()	# Create a file drop target for all the main pages.
		
		# Add all the pages to the notebook.
		self.pages = []

		def addPage( page, name ):
			self.notebook.AddPage( page, name )
			self.pages.append( page )
			
		self.attrClassName = [
			[ 'actions',		Actions,			_('Actions') ],
			[ 'record',			NumKeypad,			_('Record') ],
			[ 'results',		Results,			_('Results') ],
			[ 'history',		History,			_('History') ],
			[ 'riderDetail',	RiderDetail,		_('RiderDetail') ],
			[ 'gantt', 			Gantt,				_('Chart') ],
			[ 'raceAnimation',	RaceAnimation,		_('Animation') ],
			[ 'recommendations',Recommendations,	_('Recommendations') ],
			[ 'categories', 	Categories,			_('Categories') ],
			[ 'properties',		Properties,			_('Properties') ],
			[ 'primes',			Primes,				_('Primes') ],
			[ 'situation',		Situation,			_('Situation') ],
			[ 'lapCounter',		LapCounter,			_('LapCounter') ],
		]
		self.attrWindowSet = {'results', 'history', 'gantt', 'raceAnimation', 'situation', 'lapCounter'}
		
		for i, (a, c, n) in enumerate(self.attrClassName):
			setattr( self, a, c(self.notebook) )
			getattr( self, a ).SetDropTarget( self.fileDrop )
			addPage( getattr(self, a), u'{}. {}'.format(i+1, n) )

		self.riderDetailDialog = None
		self.splitter.SplitVertically( self.forecastHistory, self.notebook, forecastHistoryWidth + 80)
		self.splitter.UpdateSize()

		#-----------------------------------------------------------------------
		self.chipMenu = wx.Menu()

		idCur = wx.NewId()
		AppendMenuItemBitmap( self.chipMenu, idCur, _("RFID Reader &Setup..."), _("Configure and Test the RFID Reader"), Utils.GetPngBitmap('rfid-signal.png') )
		self.Bind(wx.EVT_MENU, self.menuJChip, id=idCur )
		
		self.chipMenu.AppendSeparator()
		
		idCur = wx.NewId()
		self.chipMenu.Append( idCur , _("Import JChip File..."), _("JChip Formatted File") )
		self.Bind(wx.EVT_MENU, self.menuJChipImport, id=idCur )
		
		idCur = wx.NewId()
		self.chipMenu.Append( idCur , _("Import Impinj File..."), _("Impinj Formatted File") )
		self.Bind(wx.EVT_MENU, self.menuImpinjImport, id=idCur )
		
		idCur = wx.NewId()
		self.chipMenu.Append( idCur , _("Import Alien File..."), _("Alien Formatted File") )
		self.Bind(wx.EVT_MENU, self.menuAlienImport, id=idCur )
		
		idCur = wx.NewId()
		self.chipMenu.Append( idCur , _("Import Orion File..."), _("Orion Formatted File") )
		self.Bind(wx.EVT_MENU, self.menuOrionImport, id=idCur )
		
		self.menuBar.Append( self.chipMenu, _("Chip&Reader") )

		#----------------------------------------------------------------------------------------------
		self.toolsMenu = wx.Menu()
		
		idCur = wx.NewId()
		self.toolsMenu.Append( idCur , _("&Simulate Race..."), _("Simulate a race") )
		self.Bind(wx.EVT_MENU, self.menuSimulate, id=idCur )

		self.toolsMenu.AppendSeparator()
		
		idCur = wx.NewId()
		self.toolsMenu.Append( idCur , _("&Change Race Start Time..."), _("Change the Start Time of the Race") )
		self.Bind(wx.EVT_MENU, self.menuChangeRaceStartTime, id=idCur )
		
		self.toolsMenu.AppendSeparator()

		idCur = wx.NewId()
		self.toolsMenu.Append( idCur , _("Copy Log File to &Clipboard..."), _("Copy Log File to Clipboard") )
		self.Bind(wx.EVT_MENU, self.menuCopyLogFileToClipboard, id=idCur )

		self.toolsMenu.AppendSeparator()

		idCur = wx.NewId()
		self.toolsMenu.Append( idCur , _("&Reload Checklist..."), _("Reload the Checklist from the Checklist File") )
		self.Bind(wx.EVT_MENU, self.menuReloadChecklist, id=idCur )
		
		self.menuBar.Append( self.toolsMenu, _("&Tools") )
		
		#-----------------------------------------------------------------------
		self.optionsMenu = wx.Menu()
		idCur = wx.NewId()
		self.menuItemHighPrecisionTimes = self.optionsMenu.Append( idCur , _("&Show 100s of a second"), _("Show 100s of a second"), wx.ITEM_CHECK )
		self.Bind( wx.EVT_MENU, self.menuShowHighPrecisionTimes, id=idCur )
		
		idCur = wx.NewId()
		self.menuItemPlaySounds = self.optionsMenu.Append( idCur , _("&Play Sounds"), _("Play Sounds"), wx.ITEM_CHECK )
		self.playSounds = self.config.ReadBool('playSounds', True)
		self.menuItemPlaySounds.Check( self.playSounds )
		self.Bind( wx.EVT_MENU, self.menuPlaySounds, id=idCur )
		
		idCur = wx.NewId()
		self.menuItemSyncCategories = self.optionsMenu.Append( idCur , _("Sync &Categories between Tabs"), _("Sync Categories between Tabs"), wx.ITEM_CHECK )
		self.Bind( wx.EVT_MENU, self.menuSyncCategories, id=idCur )
		
		self.optionsMenu.AppendSeparator()
		idCur = wx.NewId()
		self.menuItemLaunchExcelAfterPublishingResults = self.optionsMenu.Append( idCur,
			_("&Launch Excel after Publishing Results"),
			_("Launch Excel after Publishing Results"), wx.ITEM_CHECK )
		self.launchExcelAfterPublishingResults = self.config.ReadBool('menuLaunchExcelAfterPublishingResults', True)
		self.menuItemLaunchExcelAfterPublishingResults.Check( self.launchExcelAfterPublishingResults )
		self.Bind( wx.EVT_MENU, self.menuLaunchExcelAfterPublishingResults, id=idCur )
		
		self.optionsMenu.AppendSeparator()
		idCur = wx.NewId()
		self.optionsMenu.Append( idCur , _("Set Contact &Email..."), _("Set Contact Email for HTML Output") )
		self.Bind(wx.EVT_MENU, self.menuSetContactEmail, id=idCur )
		
		idCur = wx.NewId()
		self.optionsMenu.Append( idCur , _("Set &Graphic..."), _("Set Graphic for Output") )
		self.Bind(wx.EVT_MENU, self.menuSetGraphic, id=idCur )
		
		self.menuBar.Append( self.optionsMenu, _("&Options") )
		

		#------------------------------------------------------------------------------
		# Create a menu for quick navigation
		self.pageMenu = wx.Menu()
		self.idPage = {}
		jumpToIds = []
		for i, p in enumerate(self.pages):
			name = self.notebook.GetPageText(i)
			idCur = wx.NewId()
			self.idPage[idCur] = i
			self.pageMenu.Append( idCur, u'{}\tF{}'.format(name, i+1), u"{} {}".format(_('Jump to'), name) )
			self.Bind(wx.EVT_MENU, self.menuShowPage, id=idCur )
			jumpToIds.append( idCur )
			
		self.menuBar.Append( self.pageMenu, _("&JumpTo") )

		#------------------------------------------------------------------------------
		self.windowMenu = wx.Menu()

		self.menuIdToWindowInfo = {}
		for attr, cls, name in self.attrClassName:
			if attr not in self.attrWindowSet:
				continue
			idCur = wx.NewId()
			menuItem = self.windowMenu.Append( idCur, name, name, wx.ITEM_CHECK )
			self.Bind(wx.EVT_MENU, self.menuWindow, id=idCur )
			pageDialog = PageDialog(self, cls, closeCallback=lambda idIn=idCur: self.windowCloseCallback(idIn), title=name)
			if attr == 'lapCounter':
				self.lapCounterDialog = pageDialog
			self.menuIdToWindowInfo[idCur] = [
				attr, name, menuItem,
				pageDialog,
			]
		
		self.menuBar.Append( self.windowMenu, _("&Windows") )
		
		#------------------------------------------------------------------------------
		self.helpMenu = wx.Menu()

		idCur = wx.NewId()
		self.helpMenu.Append( idCur, _("Help &Search..."), _("Search Help...") )
		self.Bind(wx.EVT_MENU, self.menuHelpSearch, id=idCur )
		self.helpSearch = HelpSearchDialog( self, title=_('Help Search') )
		self.helpMenu.Append( wx.ID_HELP, _("&Help..."), _("Help about CrossMgr...") )
		self.Bind(wx.EVT_MENU, self.menuHelp, id=wx.ID_HELP )
		idCur = wx.NewId()
		self.helpMenu.Append( idCur , _("&QuickStart..."), _("Get started with CrossMgr Now...") )
		self.Bind(wx.EVT_MENU, self.menuHelpQuickStart, id=idCur )
		
		self.helpMenu.AppendSeparator()

		self.helpMenu.Append( wx.ID_ABOUT , _("&About..."), _("About CrossMgr...") )
		self.Bind(wx.EVT_MENU, self.menuAbout, id=wx.ID_ABOUT )

		idCur = wx.NewId()
		self.helpMenu.Append( idCur , _("&Tips at Startup..."), _("Enable/Disable Tips at Startup...") )
		self.Bind(wx.EVT_MENU, self.menuTipAtStartup, id=idCur )


		self.menuBar.Append( self.helpMenu, _("&Help") )

		#------------------------------------------------------------------------------
		#------------------------------------------------------------------------------
		#------------------------------------------------------------------------------
		self.SetMenuBar( self.menuBar )

		#------------------------------------------------------------------------------
		# Set the accelerator table so we can switch windows with the function keys.
		accTable = [(wx.ACCEL_NORMAL, wx.WXK_F1 + i, jumpToIds[i]) for i in xrange(max(12,len(jumpToIds)))]
		self.contextHelp = wx.NewId()
		self.Bind(wx.EVT_MENU, self.onContextHelp, id=self.contextHelp )
		accTable.append( (wx.ACCEL_CTRL, ord('H'), self.contextHelp) )
		accTable.append( (wx.ACCEL_SHIFT, wx.WXK_F1, self.contextHelp) )
		aTable = wx.AcceleratorTable( accTable )
		self.SetAcceleratorTable(aTable)
		
		#------------------------------------------------------------------------------
		self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
		self.Bind(EVT_CHIP_READER, self.handleChipReaderEvent)
		self.lastPhotoTime = datetime.datetime.now()
		
		self.photoDialog = PhotoViewerDialog( self, title = _("PhotoViewer"), size=(600,400) )

	def handleChipReaderEvent( self, event ):
		race = Model.race
		if not race or not race.isRunning() or not race.enableUSBCamera:
			return
		if not getattr(race, 'tagNums', None):
			JChipSetup.GetTagNums()
		if not race.tagNums:
			return
		
		requests = []
		for tag, dt in event.tagTimes:
			if race.startTime > dt:
				continue
			
			try:
				num = race.tagNums[tag]
			except (TypeError, ValueError, KeyError):
				continue
			
			requests.append( (num, (dt - race.startTime).total_seconds()) )
			
		success, error = SendPhotoRequests( requests )
		if success:
			race.photoCount += len(requests) * 2
	
	def updateLapCounter( self, labels=None ):
		labels = labels or []
		self.lapCounter.SetLabels( labels )
		self.lapCounterDialog.page.SetLabels( labels )
	
	def menuDNS( self, event ):
		dns = DNSManagerDialog( self )
		dns.ShowModal()
		dns.Destroy()
		
	def menuFind( self, event = None ):
		if not getattr(self, 'findDialog', None):
			self.findDialog = SearchDialog( self, wx.ID_ANY )
		self.findDialog.refresh()
		self.findDialog.Show()
		
	def menuUndo( self, event ):
		undo.doUndo()
		self.refresh()
		
	def menuRedo( self, event ):
		undo.doRedo()
		self.refresh()
		
	def menuAutocorrect( self, event ):
		undo.pushState()
		with Model.LockRace() as race:
			if not race:
				return
			categories = race.getCategoriesInUse()
			if not categories:
				return
		SetAutoCorrectDialog( self, categories ).ShowModal()
	
	def menuShowHighPrecisionTimes( self, event ):
		with Model.LockRace() as race:
			if race:
				race.highPrecisionTimes = self.menuItemHighPrecisionTimes.IsChecked()
		wx.CallAfter( self.refresh )
	
	def menuSyncCategories( self, event ):
		with Model.LockRace() as race:
			if race:
				race.syncCategories = self.menuItemSyncCategories.IsChecked()
				
	def menuChangeRaceStartTime( self, event ):
		with Model.LockRace() as race:
			if not race:
				return
			if race.isUnstarted():
				Utils.MessageOK( self, _('Cannot change Start Time of unstarted race.  Start the race from Actions.'), _('Race Not Started') )
				return
			if race.isTimeTrial and race.hasRiderTimes():
				Utils.MessageOK( self, _('Cannot change Start Time of a Time Trial with recorded times'), _('Cannot Change Start Time') )
				return
			dlg = ChangeRaceStartTime.ChangeRaceStartTimeDialog( self )
			dlg.ShowModal()
			dlg.Destroy()
	
	def menuPlaySounds( self, event ):
		self.playSounds = self.menuItemPlaySounds.IsChecked()
		self.config.WriteBool( 'playSounds', self.playSounds )
		
	def menuLaunchExcelAfterPublishingResults( self, event ):
		self.launchExcelAfterPublishingResults = self.menuItemLaunchExcelAfterPublishingResults.IsChecked()
		self.config.WriteBool( 'launchExcelAfterPublishingResults', self.launchExcelAfterPublishingResults )
	
	def menuTipAtStartup( self, event ):
		showing = self.config.ReadBool('showTipAtStartup', True)
		if Utils.MessageOKCancel( self, _('Turn Off Tips at Startup?') if showing else _('Show Tips at Startup?'), _('Tips at Startup') ):
			self.config.WriteBool( 'showTipAtStartup', showing ^ True )

	def menuRestoreFromInput( self, event ):
		if not Model.race:
			Utils.MessageOK(self, _("You must have a valid race."), _("No Valid Race"), iconMask=wx.ICON_ERROR)
			return
		if not Utils.MessageOKCancel( self,
				_("This will restore the race from the original input and replace your adds/splits/deletes.\nAre you sure you want to continue?"),
				_("Restore from Original Input"), iconMask=wx.ICON_WARNING ):
			return
				
		startTime, endTime, numTimes = OutputStreamer.ReadStreamFile()
		if not numTimes:
			Utils.MessageOK( self, u'{}.\n\n{} "{}".'.format(
				_('No Data Found'),
				_('Check file'),
				OutputStreamer.getFileName()), _("No Data Found")
			)
			return
		undo.pushState()
		with Model.LockRace() as race:
			race.clearAllRiderTimes()
			race.startTime = startTime
			race.endTime = endTime
			for num, t in numTimes:
				race.addTime( num, t )
			race.numLaps = race.getMaxLap()
			race.setChanged()
		wx.CallAfter( self.refresh )
			
	def menuChangeProperties( self, event ):
		if not Model.race:
			Utils.MessageOK(self, _("You must have a valid race."), _("No Valid Race"), iconMask=wx.ICON_ERROR)
			return
		ChangeProperties( self )
		
	def menuJChip( self, event ):
		self.commit()
		dlg = JChipSetup.JChipSetupDialog( self )
		dlg.ShowModal()
		dlg.Destroy()

	def menuJChipImport( self, event ):
		correct, reason = JChipSetup.CheckExcelLink()
		explain = u'{}\n\n{}'.format(
			_('You must have a valid Excel sheet with associated tags and Bib numbers.'),
			_('See documentation for details.')
		)
		if not correct:
			Utils.MessageOK( self, u'{}\n\n    {}\n\n{}'.format(_('Problems with Excel sheet.'), reason, explain),
									title = _('Excel Link Problem'), iconMask = wx.ICON_ERROR )
			return
			
		dlg = JChipImport.JChipImportDialog( self )
		dlg.ShowModal()
		dlg.Destroy()
		wx.CallAfter( self.refresh )
		
	def menuAlienImport( self, event ):
		correct, reason = JChipSetup.CheckExcelLink()
		explain = u'{}\n\n{}'.format(
			_('You must have a valid Excel sheet with associated tags and Bib numbers.'),
			_('See documentation for details.')
		)
		if not correct:
			Utils.MessageOK( self, u'{}\n\n    {}\n\n{}'.format(_('Problems with Excel sheet.'), reason, explain),
									title = _('Excel Link Problem'), iconMask = wx.ICON_ERROR )
			return
			
		dlg = AlienImport.AlienImportDialog( self )
		dlg.ShowModal()
		dlg.Destroy()
		wx.CallAfter( self.refresh )
		
	def menuImpinjImport( self, event ):
		correct, reason = JChipSetup.CheckExcelLink()
		explain = u'{}\n\n{}'.format(
			_('You must have a valid Excel sheet with associated tags and Bib numbers.'),
			_('See documentation for details.')
		)
		if not correct:
			Utils.MessageOK( self, '{}\n\n    {}\n\n{}'.format(_('Problems with Excel sheet.'), reason, explain),
									title = _('Excel Link Problem'), iconMask = wx.ICON_ERROR )
			return
			
		dlg = ImpinjImport.ImpinjImportDialog( self )
		dlg.ShowModal()
		dlg.Destroy()
		wx.CallAfter( self.refresh )
		
	def menuOrionImport( self, event ):
		correct, reason = JChipSetup.CheckExcelLink()
		explain = u'{}\n\n{}'.format(
			_('You must have a valid Excel sheet with associated tags and Bib numbers.'),
			_('See documentation for details.')
		)
		if not correct:
			Utils.MessageOK( self, '{}\n\n    {}\n\n{}'.format(_('Problems with Excel sheet.'), reason, explain),
									title = _('Excel Link Problem'), iconMask = wx.ICON_ERROR )
			return
			
		dlg = OrionImport.OrionImportDialog( self )
		dlg.ShowModal()
		dlg.Destroy()
		wx.CallAfter( self.refresh )
		
	def menuShowPage( self, event ):
		self.showPage( self.idPage[event.GetId()] )
		
	def getDirName( self ):
		return Utils.getDirName()
		
	def menuSetContactEmail( self, event = None ):
		email = self.config.Read( 'email', 'my_name@my_address' )
		dlg = wx.TextEntryDialog( self, message=_('Contact Email:'), caption=_('Contact Email for HTML output'), defaultValue=email )
		result = dlg.ShowModal()
		if result == wx.ID_OK:
			value = dlg.GetValue()
			self.config.Write( 'email', value )
			self.config.Flush()
		dlg.Destroy()

	def menuSetGraphic( self, event ):
		imgPath = self.getGraphicFName()
		dlg = SetGraphicDialog( self, graphic = imgPath )
		if dlg.ShowModal() == wx.ID_OK:
			imgPath = dlg.GetValue()
			self.config.Write( 'graphic', imgPath )
			self.config.Flush()
		dlg.Destroy()
	
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
			Utils.MessageOK(self, u'\n\n'.join( [_("Log file copied to clipboard."), _("You can now paste it into an email.")] ), _("Success") )
		else:
			Utils.MessageOK(self, _("Unable to open the clipboard."), _("Error"), wx.ICON_ERROR )
	
	def menuReloadChecklist( self, event ):
		try:
			Model.race.checklist = None
		except:
			pass
		self.refresh()
	
	def getGraphicFName( self ):
		defaultFName = os.path.join(Utils.getImageFolder(), 'CrossMgrHeader.png')
		graphicFName = self.config.Read( 'graphic', defaultFName )
		if graphicFName != defaultFName:
			try:
				with open(graphicFName, 'rb') as f:
					return graphicFName
			except IOError:
				pass
		return defaultFName
	
	def getGraphicBase64( self ):
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
				b64 = 'data:image/%s;base64,%s' % (fileType, base64.standard_b64encode(f.read()))
				return b64
		except IOError:
			pass
		return None
	
	def menuPageSetup( self, event ):
		psdd = wx.PageSetupDialogData(self.printData)
		psdd.CalculatePaperSizeFromId()
		dlg = wx.PageSetupDialog(self, psdd)
		dlg.ShowModal()

		# this makes a copy of the wx.PrintData instead of just saving
		# a reference to the one inside the PrintDialogData that will
		# be destroyed when the dialog is destroyed
		self.printData = wx.PrintData( dlg.GetPageSetupData().GetPrintData() )
		dlg.Destroy()

	PrintCategoriesDialogSize = (450, 400)
	def menuPrintPreview( self, event ):
		if not Model.race:
			return
		self.commit()
	
		cpcd = ChoosePrintCategoriesDialog( self )
		x, y = self.GetPosition().Get()
		x += wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_X, self)
		y += wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_Y, self)
		cpcd.SetPosition( (x, y) )
		cpcd.SetSize( self.PrintCategoriesDialogSize )
		result = cpcd.ShowModal()
		categories = cpcd.categories
		cpcd.Destroy()
		if not categories or result != wx.ID_OK:
			return
	
		data = wx.PrintDialogData(self.printData)
		printout = CrossMgrPrintout( categories )
		printout2 = CrossMgrPrintout( categories )
		self.preview = wx.PrintPreview(printout, printout2, data)

		self.preview.SetZoom( 110 )
		if not self.preview.Ok():
			return

		pfrm = wx.PreviewFrame(self.preview, self, _("Print preview"))

		pfrm.Initialize()
		pfrm.SetPosition(self.GetPosition())
		pfrm.SetSize(self.GetSize())
		pfrm.Show(True)

	@logCall
	def menuPrint( self, event ):
		if not Model.race:
			return
		self.commit()

		cpcd = ChoosePrintCategoriesDialog( self )
		x, y = self.GetPosition().Get()
		x += wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_X, self)
		y += wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_Y, self)
		cpcd.SetPosition( (x, y) )
		cpcd.SetSize( self.PrintCategoriesDialogSize )
		result = cpcd.ShowModal()
		categories = cpcd.categories
		cpcd.Destroy()
		if not categories or result != wx.ID_OK:
			return
	
		self.printData.SetFilename( os.path.splitext(self.fileName)[0] + '.pdf' if self.fileName else 'Results.pdf' )
		pdd = wx.PrintDialogData(self.printData)
		self.printData.SetPrintMode( wx.PRINT_MODE_FILE if 'pdf' in self.printData.GetPrinterName().lower() else wx.PRINT_MODE_PRINTER )
		pdd.SetAllPages( True )
		pdd.EnableSelection( False )
		pdd.EnablePageNumbers( False )
		pdd.EnableHelp( False )
		pdd.EnablePrintToFile( False )
		
		printer = wx.Printer(pdd)
		printout = CrossMgrPrintout( categories )

		if not printer.Print(self, printout, True):
			if printer.GetLastError() == wx.PRINTER_ERROR:
				Utils.MessageOK(self, u'\n\n'.join( [_("There was a printer problem."), _("Check your printer setup.")] ), _("Printer Error"), iconMask=wx.ICON_ERROR)
		else:
			self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )

		printout.Destroy()

	@logCall
	def menuPrintPodium( self, event ):
		if not Model.race:
			return
		self.commit()

		cpcd = ChoosePrintCategoriesPodiumDialog( self )
		x, y = self.GetPosition().Get()
		x += wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_X, self)
		y += wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_Y, self)
		cpcd.SetPosition( (x, y) )
		cpcd.SetSize( self.PrintCategoriesDialogSize )
		result = cpcd.ShowModal()
		categories, positions = cpcd.categories, cpcd.positions
		cpcd.Destroy()
		if not categories or result != wx.ID_OK:
			return
	
		self.printData.SetFilename( self.fileName if self.fileName else '' )
		pdd = wx.PrintDialogData(self.printData)
		pdd.SetAllPages( True )
		pdd.EnableSelection( False )
		pdd.EnablePageNumbers( False )
		pdd.EnableHelp( False )
		pdd.EnablePrintToFile( False )
		
		printer = wx.Printer(pdd)
		printout = CrossMgrPodiumPrintout( categories, positions )

		if not printer.Print(self, printout, True):
			if printer.GetLastError() == wx.PRINTER_ERROR:
				Utils.MessageOK(self, u'\n\n'.join( [_("There was a printer problem."), _("Check your printer setup.")] ), _("Printer Error"), iconMask=wx.ICON_ERROR)
		else:
			self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )

		printout.Destroy()

	@logCall
	def menuPrintPNG( self, event ):
		if not Model.race:
			return
		self.commit()
		
		if Utils.MessageYesNo( self,
				u'{}\n\n{}'.format(
					_('This is not the recommended method to publish results to Facebook.'),
					_('Would you like to see the recommended options?')
				),
				_('Publish to Facebook') ):
			Utils.showHelp( 'Facebook.html' )
			return

		cpcd = ChoosePrintCategoriesDialog( self )
		x, y = self.GetPosition().Get()
		x += wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_X, self)
		y += wx.SystemSettings.GetMetric(wx.SYS_FRAMESIZE_Y, self)
		cpcd.SetPosition( (x, y) )
		cpcd.SetSize( self.PrintCategoriesDialogSize )
		result = cpcd.ShowModal()
		categories = cpcd.categories
		cpcd.Destroy()
		if not categories or result != wx.ID_OK:
			return
	
		dir, fnameBase = os.path.split( self.fileName )
		dir = os.path.join( dir, 'ResultsPNG' )
		fnameBase = os.path.splitext( fnameBase )[0]
		printout = CrossMgrPrintoutPNG( dir, fnameBase, self.printData.GetOrientation(), categories )
		pages = printout.GetPageInfo()[-1]
		
		fname = None
		success = True
		wx.BeginBusyCursor()
		for page in xrange(1, pages+1):
			try:
				printout.OnPrintPage( page )
				if fname is None:
					fname = printout.lastFName
			except Exception as e:
				logException( e, sys.exc_info() )
				Utils.MessageOK(self,
							u'{}:\n\n    {}.'.format(_('Error creating PNG files'), e),
							_('PNG File Error'), iconMask=wx.ICON_ERROR )
				success = False
				break

		printout.Destroy()
		wx.EndBusyCursor()
		
		if success:
			if fname:
				webbrowser.open( fname, new = 2, autoraise = True )
			Utils.MessageOK( self, u'{}:\n\n    {}'.format(_('Results written as PNG files to'), dir), _('PNG Publish') )

	@logCall
	def menuPrintCategories( self, event ):
		self.commit()
		PrintCategories()

	@logCall
	def menuLinkExcel( self, event = None ):
		if not Model.race:
			Utils.MessageOK(self, _("You must have a valid race."), _("Link ExcelSheet"), iconMask=wx.ICON_ERROR)
			return
		self.showPageName( _('Results') )
		self.closeFindDialog()
		ResetExcelLinkCache()
		gel = GetExcelLink( self, getattr(Model.race, 'excelLink', None) )
		link = gel.show()
		undo.pushState()
		with Model.LockRace() as race:
			if not link:
				try:
					del race.excelLink
				except AttributeError:
					pass
			else:
				#if os.path.dirname(link.fileName) == os.path.dirname(self.fileName):
				#	link.fileName = os.path.join( '.', os.path.basename(link.fileName) )
				race.excelLink = link
			race.setChanged()
			race.resetAllCaches()
		self.writeRace()
		ResetExcelLinkCache()
		self.refresh()
		
		wx.CallAfter( self.menuFind )
		
	#--------------------------------------------------------------------------------------------

	@logCall
	def menuPublishAsExcel( self, event ):
		self.commit()
		if self.fileName is None or len(self.fileName) < 4:
			return

		xlFName = self.fileName[:-4] + '.xls'
		dlg = wx.DirDialog( self, u'{} "{}"'.format(_('Folder to write'), os.path.basename(xlFName)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(xlFName) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		xlFName = os.path.join( dName, os.path.basename(xlFName) )

		wb = xlwt.Workbook()
		with UnstartedRaceWrapper():
			raceCategories = getRaceCategories()
			for catName, category in raceCategories:
				if catName == 'All' and len(raceCategories) > 1:
					continue
				sheetName = re.sub('[+!#$%&+~`".:;|\\/?*\[\] ]+', ' ', Utils.toAscii(catName))
				sheetName = sheetName[:31]
				sheetCur = wb.add_sheet( sheetName )
				export = ExportGrid()
				export.setResultsOneList( category, showLapsFrequency = 1 )
				export.toExcelSheet( sheetCur )
				
			race = Model.race
			if race and getattr(race, 'primes', None):
				sheetName = 'Primes'
				sheetCur = wb.add_sheet( sheetName )
				export = ExportGrid( **GetGrid() )
				export.toExcelSheet( sheetCur )

		try:
			wb.save( xlFName )
			if self.launchExcelAfterPublishingResults:
				webbrowser.open( xlFName, new = 2, autoraise = True )
			Utils.MessageOK(self, u'{}:\n\n   {}'.format(_('Excel file written to'), xlFName), _('Excel Write'))
		except IOError:
			Utils.MessageOK(self,
						u'{} "{}"\n\n{}\n{}'.format(
							_('Cannot write'), xlFName,
							_('Check if this spreadsheet is already open.'),
							_('If so, close it, and try again.')
						),
						_('Excel File Error'), iconMask=wx.ICON_ERROR )
						
	#--------------------------------------------------------------------------------------------
	def getEmail( self ):
		return self.config.Read('email', '')
	
	reLeadingWhitespace = re.compile( r'^[ \t]+', re.MULTILINE )
	reComments = re.compile( r'// .*$', re.MULTILINE )
	reBlankLines = re.compile( r'\n+' )
	reRemoveTags = re.compile( r'\<html\>|\</html\>|\<body\>|\</body\>|\<head\>|\</head\>', re.I )
	def cleanHtml( self, html ):
		# Remove leading whitespace, comments and consecutive blank lines to save space.
		html = self.reLeadingWhitespace.sub( '', html )
		html = self.reComments.sub( '', html )
		html = self.reBlankLines.sub( '\n', html )
		return html
		
	def addResultsToHtmlStr( self, html ):
		html = self.cleanHtml( html )
	
		payload = {}
		payload['raceName'] = os.path.basename(self.fileName)[:-4]
		iTeam = ReportFields.index('Team')
		payload['infoFields'] = ReportFields[:iTeam] + ['Name'] + ReportFields[iTeam:]
			
		with Model.LockRace() as race:
			year, month, day = [int(v) for v in race.date.split('-')]
			timeComponents = [int(v) for v in race.scheduledStart.split(':')]
			if len(timeComponents) < 3:
				timeComponents.append( 0 )
			hour, minute, second = timeComponents
			raceTime = datetime.datetime( year, month, day, hour, minute, second )
			title = u'{} - {} {} {}'.format( race.name, _('Starting'), raceTime.strftime(localTimeFormat), raceTime.strftime(localDateFormat) )
			html = html.replace( u'CrossMgr Race Results by Edward Sitarski', cgi.escape(title) )
			
			payload['organizer']		= getattr(race, 'organizer', '')
			payload['reverseDirection']	= getattr(race, 'reverseDirection', False)
			payload['finishTop']		= getattr(race, 'finishTop', False)
			payload['isTimeTrial']		= getattr(race, 'isTimeTrial', False)
			payload['rfid']				= getattr(race, 'enableJChipIntegration', False)
			payload['primes']			= getattr(race, 'primes', [])
			payload['raceNameText']		= race.name
			payload['raceDate']			= race.date
			payload['raceAddress']      = u', '.join( n for n in [race.city, race.stateProv, race.country] if n )
			payload['raceIsRunning']	= race.isRunning()
			payload['raceIsUnstarted']	= race.isUnstarted()
			payload['lapDetails']		= GetLapDetails() if not race.hideDetails else {}
			payload['hideDetails']		= race.hideDetails
			payload['showCourseAnimation'] = race.showCourseAnimationInHtml
			payload['licenseLinkTemplate'] = race.licenseLinkTemplate
			
			notes = TemplateSubstitute( getattr(race, 'notes', ''), race.getTemplateValues() )
			if notes.lstrip()[:6].lower().startswith( '<html>' ):
				notes = self.reRemoveTags.sub( '', notes )
				notes = notes.replace('<', '{{').replace( '>', '}}' )
				payload['raceNotes']	= notes
			else:
				payload['raceNotes']	= cgi.escape(notes).replace('\n','{{br/}}')
			if race.startTime:
				raceStartTime = (race.startTime - race.startTime.replace( hour=0, minute=0, second=0 )).total_seconds()
				payload['raceStartTime']= raceStartTime
			tLastRaceTime = race.lastRaceTime()
			courseCoordinates, gpsPoints, gpsAltigraph, totalElevationGain, isPointToPoint = None, None, None, None, None
			geoTrack = getattr(race, 'geoTrack', None)
			if geoTrack is not None:
				courseCoordinates = geoTrack.asCoordinates()
				gpsPoints = geoTrack.asExportJson()
				gpsAltigraph = geoTrack.getAltigraph()
				totalElevationGain = geoTrack.totalElevationGainM
				isPointToPoint = getattr( geoTrack, 'isPointToPoint', False )
		
		tNow = datetime.datetime.now()
		payload['timestamp']			= [tNow.ctime(), tLastRaceTime]
		payload['email']				= self.getEmail()
		payload['data']					= GetAnimationData(getExternalData = True)
		payload['catDetails']			= GetCategoryDetails()
		payload['version']				= Version.AppVerName
		if gpsPoints:
			payload['gpsPoints']		= gpsPoints
			
		def sanitize( template ):
			# Sanitize the template into a safe json string.
			template = self.reLeadingWhitespace.sub( '', template )
			template = self.reComments.sub( '', template )
			template = self.reBlankLines.sub( '\n', template )
			template = template.replace( '<', '{{' ).replace( '>', '}}' )
			return template
		
		# If a map is defined, add the course viewers.
		if courseCoordinates:
			payload['courseCoordinates'] = courseCoordinates
			
			# Add the google maps template.
			templateFile = os.path.join(Utils.getHtmlFolder(), 'VirtualTourTemplate.html')
			try:
				with io.open(templateFile, 'r', encoding='utf-8') as fp:
					template = fp.read()
				payload['virtualRideTemplate'] = sanitize( template )
			except:
				pass
				
			# Add the course viewer template.
			templateFile = os.path.join(Utils.getHtmlFolder(), 'CourseViewerTemplate.html')
			try:
				with io.open(templateFile, 'r', encoding='utf-8') as fp:
					template = fp.read()
				payload['courseViewerTemplate'] = sanitize( template )
			except:
				pass
			
		# Add the rider dashboard.
		templateFile = os.path.join(Utils.getHtmlFolder(), 'RiderDashboard.html')
		try:
			with io.open(templateFile, 'r', encoding='utf-8') as fp:
				template = fp.read()
			payload['riderDashboard'] = sanitize( template )
		except:
			pass
	
		# Add the travel map if the riders have locations.
		try:
			excelLink = race.excelLink
			if excelLink.hasField('City') and any(excelLink.hasField(f) for f in ('Prov','State','StateProv')):
				templateFile = os.path.join(Utils.getHtmlFolder(), 'TravelMap.html')
				try:
					with io.open(templateFile, 'r', encoding='utf-8') as fp:
						template = fp.read()
					payload['travelMap'] = sanitize( template )
				except:
					pass				
		except Exception as e:
			pass
		
		if totalElevationGain:
			payload['gpsTotalElevationGain'] = totalElevationGain
		if gpsAltigraph:
			payload['gpsAltigraph'] = gpsAltigraph
		if isPointToPoint:
			payload['gpsIsPointToPoint'] = isPointToPoint

		html = replaceJsonVar( html, 'payload', payload )
		graphicBase64 = self.getGraphicBase64()
		if graphicBase64:
			try:
				iStart = html.index( 'src="data:image/png' )
				iEnd = html.index( '"/>', iStart )
				html = ''.join( [html[:iStart], 'src="%s"' % graphicBase64, html[iEnd+1:]] )
			except ValueError:
				pass
		return html
	
	def addCourseToHtmlStr( self, html ):
		# Remove leading whitespace, comments and consecutive blank lines to save space.
		html = self.reLeadingWhitespace.sub( '', html )
		html = self.reComments.sub( '', html )
		html = self.reBlankLines.sub( '\n', html )
	
		payload = {}
		payload['raceName'] = os.path.basename(self.fileName)[:-4]
			
		with Model.LockRace() as race:
			year, month, day = [int(v) for v in race.date.split('-')]
			timeComponents = [int(v) for v in race.scheduledStart.split(':')]
			if len(timeComponents) < 3:
				timeComponents.append( 0 )
			hour, minute, second = timeComponents
			raceTime = datetime.datetime( year, month, day, hour, minute, second )
			title = u'{} {} {}'.format( race.name, _('Course for'), raceTime.strftime(localDateFormat) )
			html = html.replace( 'CrossMgr Race Results by Edward Sitarski', cgi.escape(title) )
			
			payload['raceName']			= cgi.escape(race.name)
			payload['organizer']		= getattr(race, 'organizer', '')
			payload['rfid']				= getattr(race, 'enableJChipIntegration', False)
			payload['displayUnits']		= race.distanceUnitStr

			notes = getattr(race, 'notes', '')
			if notes.lstrip()[:6].lower().startswith( '<html>' ):
				notes = self.reRemoveTags.sub( '', notes )
				notes = notes.replace('<', '{{').replace( '>', '}}' )
				payload['raceNotes']	= notes
			else:
				payload['raceNotes']	= cgi.escape(notes).replace('\n','{{br/}}')
			courseCoordinates, gpsAltigraph, totalElevationGain, lengthKm, isPointToPoint = None, None, None, None, None
			geoTrack = getattr(race, 'geoTrack', None)
			if geoTrack is not None:
				courseCoordinates = geoTrack.asCoordinates()
				gpsAltigraph = geoTrack.getAltigraph()
				totalElevationGain = geoTrack.totalElevationGainM
				lengthKm = geoTrack.lengthKm
				isPointToPoint = getattr( geoTrack, 'isPointToPoint', False )
		
		tNow = datetime.datetime.now()
		payload['email']				= self.getEmail()
		payload['version']				= Version.AppVerName
		if courseCoordinates:
			payload['courseCoordinates'] = courseCoordinates
			# Fix the google maps template.
			templateFile = os.path.join(Utils.getHtmlFolder(), 'VirtualTourTemplate.html')
			try:
				with io.open(templateFile, 'r', encoding='utf-8') as fp:
					template = fp.read()
				# Sanitize the template into a safe json string.
				template = self.reLeadingWhitespace.sub( '', template )
				template = self.reComments.sub( '', template )
				template = self.reBlankLines.sub( '\n', template )
				template = template.replace( '<', '{{' ).replace( '>', '}}' )
				payload['virtualRideTemplate'] = template
			except:
				pass

		if totalElevationGain:
			payload['gpsTotalElevationGain'] = totalElevationGain
		if gpsAltigraph:
			payload['gpsAltigraph'] = gpsAltigraph
		if lengthKm:
			payload['lengthKm'] = lengthKm
		if isPointToPoint:
			payload['gpsIsPointToPoint'] = isPointToPoint
			
		html = replaceJsonVar( html, 'payload', payload )
		graphicBase64 = self.getGraphicBase64()
		if graphicBase64:
			try:
				iStart = html.index( 'src="data:image/png' )
				iEnd = html.index( '"/>', iStart )
				html = ''.join( [html[:iStart], 'src="%s"' % graphicBase64, html[iEnd+1:]] )
			except ValueError:
				pass
		return html
	
	@logCall
	def menuPublishHtmlRaceResults( self, event ):
		self.commit()
		if self.fileName is None or len(self.fileName) < 4:
			return
			
		if not self.getEmail():
			if Utils.MessageOKCancel( self,
				_('Your Email contact is not set.\n\nConfigure it now?\n\n(you can always change it later from "Options|Set Contact Email...")'),
				_('Set Email Contact'), wx.ICON_EXCLAMATION ):
				self.menuSetContactEmail()
	
		# Get the folder to write the html file.
		fname = os.path.splitext(self.fileName)[0] + '.html'
		dlg = wx.DirDialog( self, u'{} "{}"'.format(_('Folder to write'), os.path.basename(fname)),
							style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(fname) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		# Read the html template.
		htmlFile = os.path.join(Utils.getHtmlFolder(), 'RaceAnimation.html')
		try:
			with io.open(htmlFile, 'r', encoding='utf-8') as fp:
				html = fp.read()
		except:
			Utils.MessageOK(self, _('Cannot read HTML template file.  Check program installation.'),
							_('Html Template Read Error'), iconMask=wx.ICON_ERROR )
			return
			
		html = self.addResultsToHtmlStr( html )
			
		# Write out the results.
		fname = os.path.join( dName, os.path.basename(fname) )
		try:
			with io.open(fname, 'w', encoding='utf-8') as fp:
				fp.write( html )
			webbrowser.open( fname, new = 0, autoraise = True )
			Utils.MessageOK(self, u'{}:\n\n   {}'.format(_('Html Race Animation written to'), fname), _('Html Write'))
		except:
			Utils.MessageOK(self, u'{} ({}).'.format(_('Cannot write HTML file'), fname),
							_('Html Write Error'), iconMask=wx.ICON_ERROR )
	
	@logCall
	def menuExportHtmlFtp( self, event ):
		self.commit()
		if not self.fileName or len(self.fileName) < 4:
			Utils.MessageOK(
				self,
				u'{}.  {}:\n\n    {}'.format(
					_('Ftp Upload Failed'), _('Error'), _('No race loaded.')
				),
				_('Ftp Upload Failed'),
				iconMask=wx.ICON_ERROR
			)
			return
	
		dlg = FtpWriteFile.FtpPublishDialog( self )
		ret = dlg.ShowModal()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return
	
		race = Model.race
		host = getattr( race, 'ftpHost', '' )
			
		if not host:
			Utils.MessageOK(self, u'{}\n\n    {}'.format(_('Error'), _('Missing host name.')), _('Ftp Upload Failed'), iconMask=wx.ICON_ERROR )
			return
		
		wx.BeginBusyCursor()
		e = FtpWriteFile.FtpWriteRaceHTML()
		wx.EndBusyCursor()

		if e:
			Utils.MessageOK(self, u'{}  {}\n\n{}'.format(_('Ftp Upload Failed.'), _('Error'), e), _('Ftp Upload Failed'), iconMask=wx.ICON_ERROR )
		else:
			# Automatically open the browser on the published file for testing.
			if race.urlFull and race.urlFull != 'http://':
				webbrowser.open( race.urlFull, new = 0, autoraise = True )
			
	@logCall
	def menuPublishHtmlTTStart( self, event=None ):
		self.commit()
		race = Model.race
		if not race or self.fileName is None or len(self.fileName) < 4:
			return
			
		if not race.isTimeTrial:
			Utils.MessageOK( self, _('TT Start can only be created for a Time Trial event.'), _('Cannot Create TTStart Page') )
			return
			
		if not race.isRunning():
			Utils.MessageOK( self,
				u'\n'.join( [
					_('The Time Trial has not started.'),
					_('The TTStart page will act as countdown clock for the scheduled start time.'),
					_('You must publish this page again after you start the Time Trial.'),
				]),
				_('Reminder: Publish after Time Trial is Started') )
		
		# Get the folder to write the html file.
		fname = os.path.splitext(self.fileName)[0] + '_TTStart.html'
		dlg = wx.DirDialog( self, u'{} "{}"'.format(_('Folder to write'), os.path.basename(fname)),
							style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(fname) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		# Read the html template.
		htmlFile = os.path.join(Utils.getHtmlFolder(), 'TTStart.html')
		try:
			with io.open(htmlFile, 'r', encoding='utf-8') as fp:
				html = fp.read()
		except:
			Utils.MessageOK(self, _('Cannot read HTML template file.  Check program installation.'),
							_('Html Template Read Error'), iconMask=wx.ICON_ERROR )
			return
			
		html = self.cleanHtml( html )
		
		payload = {}
		payload['raceName'] = race.name
		if race.isRunning():
			payload['raceStartTuple'] = [
				race.startTime.year, race.startTime.month-1, race.startTime.day,
				race.startTime.hour, race.startTime.minute, race.startTime.second, int(race.startTime.microsecond/1000)
			]
		else:
			y, m, d = [int(f) for f in race.date.split('-')]
			m -= 1
			HH, MM = [int(f) for f in race.scheduledStart.split(':')[:2]]
			payload['raceScheduledStartTuple'] = [y, m, d, HH, MM, 0, 0]
		
		tNow = datetime.datetime.now()
		payload['lastUpdatedTuple'] = [
				tNow.year, tNow.month-1, tNow.day,
				tNow.hour, tNow.minute, tNow.second, int(tNow.microsecond/1000)
		]
		
		data = GetAnimationData(getExternalData = True)
		startList = []
		for bib, info in data.iteritems():
			try:
				catName = race.getCategory(bib).fullname
			except:
				catName = ''
			try:
				firstTime = int(race[bib].firstTime + 0.1)
			except:
				continue
			row = [
				firstTime,
				bib,
				' '.join(v for v in [info.get('FirstName',''), info.get('LastName')] if v),
				info.get('Team', ''),
				catName,
			]
			startList.append( row )

		payload['startList'] = startList
		
		html = replaceJsonVar( html, 'payload', payload )
		html = html.replace( '<title>TTStartPage</title>', '<title>TT {} {} {}</title>'.format(
				cgi.escape(race.name),
				cgi.escape(race.date), cgi.escape(race.scheduledStart),
			)
		)
		
		# Write out the results.
		fname = os.path.join( dName, os.path.basename(fname) )
		try:
			with io.open(fname, 'w', encoding='utf-8') as fp:
				fp.write( html )
			webbrowser.open( fname, new = 0, autoraise = True )
			Utils.MessageOK(self, u'{}:\n\n   {}'.format(_('Html TTStart written to'), fname), _('Html Write'))
		except:
			Utils.MessageOK(self, u'{} ({}).'.format(_('Cannot write HTML file'), fname),
							_('Html Write Error'), iconMask=wx.ICON_ERROR )
			return
			
		if FtpWriteFile.FtpIsConfigured():
			if Utils.MessageOKCancel(self, _('Upload with FTP?'), _('FTP Upload')):
				FtpWriteFile.FtpUploadFileAsync( fname )
	
	#--------------------------------------------------------------------------------------------
	@logCall
	def menuImportTTStartTimes( self, event ):
		if self.fileName is None or len(self.fileName) < 4:
			return
		
		with Model.LockRace() as race:
			if not race:
				return
			if not race.isTimeTrial:
				Utils.MessageOK( self, _('You must set TimeTrial mode first.'), _('Race must be TimeTrial') )
				return
			
		ImportTTStartTimes( self )
	
	@logCall
	def menuImportGpx( self, event ):
		if self.fileName is None or len(self.fileName) < 4:
			return
		
		self.showPageName( _('Animation') )
		with Model.LockRace() as race:
			if not race:
				return
			gt = GpxImport.GetGeoTrack( self, getattr(race, 'geoTrack', None), getattr(race, 'geoTrackFName', '') )
			
		geoTrack, geoTrackFName = gt.show()
		
		with Model.LockRace() as race:
			if not geoTrackFName:
				race.geoTrack, race.geoTrackFName = None, None
			else:
				race.geoTrack, race.geoTrackFName = geoTrack, geoTrackFName
			race.showOval = (race.geoTrack is None)
			race.setChanged()
			
		self.refresh()
		
	@logCall
	def menuExportGpx( self, event ):
		if self.fileName is None or len(self.fileName) < 4:
			return
		
		with Model.LockRace() as race:
			if not race:
				return
				
			if not getattr(race, 'geoTrack', None):
				Utils.MessageOK( self, u'{}\n\n{}'.format(_('No GPX Course Loaded.'), _('Nothing to export.')), _('No GPX Course Loaded') )
				return
				
			geoTrack = race.geoTrack
			
		# Get the folder to write the html file.
		fname = self.fileName[:-4] + 'Course.gpx'
		dlg = wx.DirDialog( self, u'{} "{}"'.format( _('Folder to write'), os.path.basename(fname)),
							style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(fname) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return
		
		fname = os.path.join( dName, os.path.basename(fname) )
		
		doc = geoTrack.getGPX( os.path.splitext(os.path.basename(fname))[0] )
		xml = doc.toprettyxml( indent = '', encoding = 'utf-8' )
		doc.unlink()
		try:
			with open(fname, 'wb') as f:
				f.write( xml )
			Utils.MessageOK(self, u'{}\n\n    {}.'.format(_('Course written to GPX file'), fname), _('GPX Export'))
		except Exception as e:
			Utils.MessageOK(self, u'{}  {}\n\n    {}\n\n"{}"'.format(_('Write to GPX file Failed.'), _('Error'), e, fname), _('GPX Export'))
		
	@logCall
	def menuExportCourseAsKml( self, event ):
		with Model.LockRace() as race:
			if not race:
				return
				
			if not getattr(race, 'geoTrack', None):
				Utils.MessageOK( self, u'{}.\n{}'.format(_('No GPX Course Loaded'), _('Nothing to export.')), _('No GPX Course Loaded') )
				return
				
			geoTrack = race.geoTrack
			
			# Get the folder to write the html file.
			fname = self.fileName[:-4] + 'Course.kmz'
			dlg = wx.DirDialog( self, u'{} "{}"'.format(_('Folder to write'), os.path.basename(fname)),
								style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(fname) )
			ret = dlg.ShowModal()
			dName = dlg.GetPath()
			dlg.Destroy()
			if ret != wx.ID_OK:
				return
			
			fname = os.path.join( dName, os.path.basename(fname) )
			courseFName = os.path.splitext(os.path.basename(fname))[0] + '.kml'
			
			zf = zipfile.ZipFile( fname, 'w', zipfile.ZIP_DEFLATED )
			zf.writestr( courseFName, geoTrack.asKmlTour(race.name) )
			zf.close()
			
		webbrowser.open( fname, new = 0, autoraise = True )
		Utils.MessageOK(self, u'{}:\n\n   {}\n\n{}'.format(_('Course Virtual Tour written to KMZ file'), fname, _('Google Earth Launched.')), _('KMZ Write'))
	
	@logCall
	def menuExportCoursePreviewAsHtml( self, event ):
		with Model.LockRace() as race:
			if not race:
				return
				
			if not getattr(race, 'geoTrack', None):
				Utils.MessageOK( self, u'{}\n\n{}'.format(_('No GPX Course Loaded.'), _('Nothing to export.')), _('No GPX Course Loaded') )
				return
				
			geoTrack = race.geoTrack
			
			# Get the folder to write the html file.
			fname = self.fileName[:-4] + 'CoursePreview.html'
			dlg = wx.DirDialog( self, u'{} "{}"'.format(_('Folder to write'), os.path.basename(fname)),
								style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(fname) )
			ret = dlg.ShowModal()
			dName = dlg.GetPath()
			dlg.Destroy()
			if ret != wx.ID_OK:
				return
			
			fname = os.path.join( dName, os.path.basename(fname) )
			
			# Read the html template.
			htmlFile = os.path.join(Utils.getHtmlFolder(), 'CourseViewer.html')
			try:
				with io.open(htmlFile, 'r', encoding='utf-8') as fp:
					html = fp.read()
			except:
				Utils.MessageOK(_('Cannot read HTML template file.  Check program installation.'),
								_('Html Template Read Error'), iconMask=wx.ICON_ERROR )
				return
				
			
		# Write out the results.
		html = self.addCourseToHtmlStr( html )
		fname = os.path.join( dName, os.path.basename(fname) )
		try:
			with io.open(fname, 'w', encoding='utf-8') as fp:
				fp.write( html )
			webbrowser.open( fname, new = 0, autoraise = True )
			Utils.MessageOK(self, u'{}:\n\n   {}'.format(_('Course Preview written to'), fname), _('Html Write'))
		except:
			Utils.MessageOK(self, u'{} ({}).'.format(_('Cannot write HTML file'), fname),
							_('Html Write Error'), iconMask=wx.ICON_ERROR )
	
	@logCall
	def menuExportHtmlRawData( self, event ):
		self.commit()
		if self.fileName is None or len(self.fileName) < 4:
			return
		
		with Model.LockRace() as race:
			startTime, endTime, rawData = race.getRawData()
		
		if not rawData:
			Utils.MessageOK( self, u'{}\n\n    "{}".'.format(_('Raw race data file is empty/missing.'), OutputStreamer.getFileName()),
					_('Missing Raw Race Data'), wx.ICON_ERROR )
			return
		
		# Get the folder to write the html file.
		fname = self.fileName[:-4] + 'RawData.html'
		dlg = wx.DirDialog( self, u'"{}"'.format(_('Folder to write'), os.path.basename(fname)),
							style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(fname) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		# Read the html template.
		htmlFile = os.path.join(Utils.getHtmlFolder(), 'RawData.html')
		try:
			with io.open(htmlFile, 'r', encoding='utf-8') as fp:
				html = fp.read()
		except:
			Utils.MessageOK(_('Cannot read HTML template file.  Check program installation.'),
							_('Html Template Read Error'), iconMask=wx.ICON_ERROR )
			return
		
		# Replace parts of the file with the race information.
		html = replaceJsonVar( html, 'raceName', os.path.basename(self.fileName)[:-4] )
		html = replaceJsonVar( html, 'raceStart', (startTime - datetime.datetime.combine(startTime.date(), datetime.time())).total_seconds() )
		html = replaceJsonVar( html, 'rawData', rawData )
		
		with Model.LockRace() as race:
			try:
				externalFields = race.excelLink.getFields()
				externalInfo = race.excelLink.read()
			except:
				externalFields = []
				externalInfo = {}

			ignoreFields = set( ['Bib#', 'License'] )
			for f in ignoreFields:
				try:
					externalFields.remove( f )
				except ValueError:
					pass
			
			# Add the race category to the info.
			externalFields.insert( 0, 'Race Cat.' )
			if 'LastName' in externalFields or 'FirstName' in externalFields:
				externalFields.insert( 1, 'Name' )
				try:
					externalFields.remove( 'LastName' )
				except ValueError:
					pass
				try:
					externalFields.remove( 'FirstName' )
				except ValueError:
					pass
			
			seen = set()
			for d in rawData:
				num = d[1]
				if num not in seen:
					seen.add( num )
					category = race.getCategory( num )
					externalInfo.setdefault(num, {})['Race Cat.'] = category.name if category else 'Unknown'
					info = externalInfo[num]
					info['Name'] = Utils.CombineFirstLastName( info.get('FirstName', ''), info.get('LastName', '') )
			
			# Remove info that does not correspond to a rider in the race.
			for num in [n for n in externalInfo.iterkeys() if n not in seen]:
				del externalInfo[num]
			
			# Remove extra info fields.
			for num, info in externalInfo.iteritems():
				for f in ignoreFields:
					try:
						del info[f]
					except KeyError:
						pass
			
			html = replaceJsonVar( html, 'externalFields', externalFields )
			html = replaceJsonVar( html, 'externalInfo', externalInfo )
			
			year, month, day = [int(v) for v in race.date.split('-')]
			timeComponents = [int(v) for v in race.scheduledStart.split(':')]
			if len(timeComponents) < 3:
				timeComponents.append( 0 )
			hour, minute, second = timeComponents
			raceTime = datetime.datetime( year, month, day, hour, minute, second )
			title = u'{} Raw Data for {} Start on {}'.format( race.name, raceTime.strftime(localTimeFormat), raceTime.strftime(localDateFormat) )
			html = html.replace( 'CrossMgr Race Results by Edward Sitarski', cgi.escape(title) )
			html = replaceJsonVar( html, 'organizer', getattr(race, 'organizer', '') )
			
		html = replaceJsonVar( html, 'timestamp', datetime.datetime.now().ctime() )
		
		graphicBase64 = self.getGraphicBase64()
		if graphicBase64:
			try:
				iStart = html.index( u'var imageSrc =' )
				iEnd = html.index( "';", iStart )
				html = ''.join( [html[:iStart], u"var imageSrc = '{}';".format(graphicBase64), html[iEnd+2:]] )
			except ValueError:
				pass
			
		# Write out the results.
		fname = os.path.join( dName, os.path.basename(fname) )
		try:
			with io.open(fname, 'w', encoding='utf-8') as fp:
				fp.write( html )
			webbrowser.open( fname, new = 0, autoraise = True )
			Utils.MessageOK(self, u'{}:\n\n   {}'.format(_('Html Raw Data written to'), fname), _('Html Write'))
		except:
			Utils.MessageOK(self,
							u'{} ({}).'.format(_('Cannot write HTML file'), fname),
							_('Html Write Error'), iconMask=wx.ICON_ERROR )
	
	#--------------------------------------------------------------------------------------------
	def doCleanup( self ):
		self.showPageName( _('Results') )
		with Model.LockRace() as race:
			if race is not None:
				race.resetAllCaches()
		
		self.writeRace()
		self.config.Flush()

		try:
			self.timer.Stop()
		except AttributeError:
			pass

		try:
			self.simulateTimer.Stop()
			self.simulateTimer = None
		except AttributeError:
			pass
		
		OutputStreamer.StopStreamer()
		JChip.Cleanuplistener()
	
	@logCall
	def onCloseWindow( self, event ):
		self.doCleanup()
		wx.Exit()

	def writeRace( self, doCommit = True ):
		if doCommit:
			self.commit()
		with Model.LockRace() as race:
			if race is not None:
				with open(self.fileName, 'wb') as fp:
					pickle.dump( race, fp, 2 )
				race.setChanged( False )

	def setActiveCategories( self ):
		with Model.LockRace() as race:
			if race is None:
				return
			race.setActiveCategories()

	@logCall
	def menuNew( self, event ):
		self.showPageName( _('Actions') )
		self.closeFindDialog()
		
		race = Model.race
		if race:
			geoTrack, geoTrackFName = getattr(race, 'geoTrack', None), getattr(race, 'geoTrackFName', None)
			excelLink = getattr(race, 'excelLink', None)
		else:
			geoTrack, geoTrackFName, excelLink = None, None, None
			
		geoTrack, geoTrackFName = None, None		# Do not retain the GPX file after a full new.
		
		dlg = PropertiesDialog(self, title=_('Configure Race'), style=wx.DEFAULT_DIALOG_STYLE )
		ret = dlg.ShowModal()
		fileName = dlg.GetPath()
		categoriesFile = dlg.GetCategoriesFile()
		properties = dlg.properties

		if ret != wx.ID_OK:
			return
			
		# Check for existing file.
		if os.path.exists(fileName) and \
		   not Utils.MessageOKCancel(
				self,
				u'{}.\n\n    "{}"\n\n{}?'.format_(
					_('File already exists'), fileName, _('Overwrite')
				)
			):
			return

		# Try to open the file.
		try:
			with open(fileName, 'wb') as fp:
				pass
		except IOError:
			Utils.MessageOK( self, u'{}\n\n    "{}"'.format(_('Cannot Open File'),fileName), _('Cannot Open File'), iconMask=wx.ICON_ERROR )
			return

		with Model.LockRace() as race:
			if race:
				race.resetAllCaches()
		
		self.writeRace()
		
		# Create a new race and initialize it with the properties.
		self.fileName = fileName
		Model.resetCache()
		ResetExcelLinkCache()
		Model.setRace( Model.Race() )
		properties.commit()
		self.updateRecentFiles()

		importedCategories = False
		race = Model.race
		if categoriesFile:
			try:
				with io.open(categoriesFile, 'r', encoding='utf-8') as fp:
					race.importCategories( fp )
				importedCategories = True
			except IOError:
				Utils.MessageOK( self, u"{}:\n{}".format(_('Cannot open file'), categoriesFile), _("File Open Error"), iconMask=wx.ICON_ERROR)
			except (ValueError, IndexError):
				Utils.MessageOK( self, u"{}:\n{}".format(_('Bad file format'), categoriesFile), _("File Read Error"), iconMask=wx.ICON_ERROR)

		# Create some defaults so the page is not blank.
		if not importedCategories:
			race.categoriesImportFile = ''
			race.setCategories( [{'name':u'{} {}-{}'.format(_('Category'), max(1, i*100), (i+1)*100-1),
								  'catStr':u'{}-{}'.format(max(1, i*100), (i+1)*100-1)} for i in xrange(8)] )
		else:
			race.categoriesImportFile = categoriesFile
			
		if geoTrack:
			race.geoTrack, race.geoTrackFName = geoTrack, geoTrackFName
			distance = geoTrack.length if race.distanceUnit == race.UnitKm else geoTrack.length * 0.621371
			if distance > 0.0:
				for c in race.categories.itervalues():
					c.distance = distance
			race.showOval = False
		if excelLink:
			race.excelLink = excelLink

		self.setNumSelect( None )
		self.writeRace()
		self.showPageName( _('Actions') )
		self.refreshAll()
	
	@logCall
	def menuNewNext( self, event ):
		race = Model.race
		if race is None:
			self.menuNew( event )
			return

		self.closeFindDialog()
		self.showPageName( _('Actions') )
		race.resetAllCaches()
		ResetExcelLinkCache()
		self.writeRace()
		
		# Save categories, gpx track and Excel link and use them in the next race.
		categoriesSave = race.categories
		geoTrack, geoTrackFName = getattr(race, 'geoTrack', None), getattr(race, 'geoTrackFName', None)
		excelLink = getattr(race, 'excelLink', None)
		race = None
		
		# Configure the next race.
		dlg = PropertiesDialog(self, title=_('Configure Race'), style=wx.DEFAULT_DIALOG_STYLE )
		dlg.properties.refresh()
		dlg.properties.incNext()
		dlg.properties.setEditable( True )
		dlg.folder.SetValue(os.path.dirname(self.fileName))
		dlg.properties.updateFileName()
		ret = dlg.ShowModal()
		fileName = dlg.GetPath()
		categoriesFile = dlg.GetCategoriesFile()
		properties = dlg.properties

		# Check if user cancelled.
		if ret != wx.ID_OK:
			return

		# Check for existing file.
		if os.path.exists(fileName) and \
		   not Utils.MessageOKCancel(self, u'{}\n\n    {}'.format(_('File already exists.  Overwrite?'), fileName), _('File Exists')):
			return

		# Try to open the file.
		try:
			with open(fileName, 'wb') as fp:
				pass
		except IOError:
			Utils.MessageOK(self, u'{}\n\n    "{}".'.format(_('Cannot open file.'), fileName), _('Cannot Open File'), iconMask=wx.ICON_ERROR )
			return
		except Exception as e:
			Utils.MessageOK(self, u'{}\n\n    "{}".\n\n{}: {}'.format(_('Cannot open file.'), fileName, _('Error'), e), _('Cannot Open File'), iconMask=wx.ICON_ERROR )
			return

		# Create a new race and initialize it with the properties.
		self.fileName = fileName
		Model.resetCache()
		ResetExcelLinkCache()
		
		# Save the current Ftp settings.
		ftpPublish = FtpWriteFile.FtpPublishDialog( self )

		Model.newRace()
		properties.commit()			# Apply the new properties
		ftpPublish.setRaceAttr()	# Apply the ftp properties
		ftpPublish.Destroy()
		
		self.updateRecentFiles()

		# Restore the previous categories.
		race = Model.race
		importedCategories = False
		if categoriesFile:
			try:
				with io.open(categoriesFile, 'r', encoding='utf-8') as fp:
					race.importCategories( fp )
				importedCategories = True
			except IOError:
				Utils.MessageOK( self, u"{}:\n\n    {}".format(_('Cannot open file'), categoriesFile), _("File Open Error"), iconMask=wx.ICON_ERROR)
			except (ValueError, IndexError) as e:
				Utils.MessageOK( self, u"{}:\n\n    {}\n\n{}".format(_('Bad file format'), categoriesFile, e), _("File Read Error"), iconMask=wx.ICON_ERROR)

		if not importedCategories:
			race.categories = categoriesSave

		if geoTrack:
			race.geoTrack, race.geoTrackFName = geoTrack, geoTrackFName
			distance = geoTrack.lengthKm if race.distanceUnit == race.UnitKm else geoTrack.lengthMiles
			if distance > 0.0:
				for c in race.categories.itervalues():
					c.distance = distance
			race.showOval = False
		if excelLink:
			race.excelLink = excelLink
		
		self.setActiveCategories()
		self.setNumSelect( None )
		self.writeRace()
		self.showPageName( _('Actions') )
		self.refreshAll()

	@logCall
	def openRaceDBExcel( self, fname ):
		race = Model.race
		self.showPageName( _('Actions') )
		self.closeFindDialog()
		
		ftpPublish = FtpWriteFile.FtpPublishDialog( self )
		
		geoTrack, geoTrackFName = None, None
		if race:
			race.resetAllCaches()
			ResetExcelLinkCache()
			self.writeRace()
			geoTrack, geoTrackFName = getattr(race, 'geoTrack', None), getattr(race, 'geoTrackFName', None)
		
		# Create a new race, but keep the old one in case we fail somewhere.
		raceSave = Model.race
		Model.newRace()
		race = Model.race
		
		# Create the link to the RaceDB excel sheet.
		try:
			excelLink = ExcelLink()
			excelLink.setFileName( fname )
			excelLink.setSheetName( 'Registration' )
			excelLink.bindDefaultFieldCols()
		except Exception as e:
			logException( e, sys.exc_info() )
			Utils.MessageOK( self, u"{}:\n\n   {}".format(_('Excel Read Failure'), e), _("Excel Read Failure"), iconMask=wx.ICON_ERROR )
			Model.race = raceSave
			return
		
		race.excelLink = excelLink
		Model.resetCache()
		ResetExcelLinkCache()
		SyncExcelLink( race )
		
		# Get the start times from the spreadsheet.
		AutoImportTTStartTimes()
		
		# Show the Properties screen for the user to review.
		dlg = PropertiesDialog(self, title=_('Configure Race'), style=wx.DEFAULT_DIALOG_STYLE )
		dlg.properties.refresh()
		dlg.properties.setEditable( True )
		dlg.folder.SetValue(os.path.dirname(fname))
		dlg.properties.updateFileName()
		ret = dlg.ShowModal()
		fileName = dlg.GetPath()
		categoriesFile = dlg.GetCategoriesFile()
		properties = dlg.properties

		# Check if user cancelled.
		if ret != wx.ID_OK:
			Model.race = raceSave
			return

		# Check for existing file.
		if os.path.exists(fileName) and \
		   not Utils.MessageOKCancel(self, u'{}\n\n    "{}"'.format(_("File already exists.  Overwrite?"), fileName), _('File Exists')):
			Model.race = raceSave
			return

		# Try to open the file.
		try:
			with open(fileName, 'wb') as fp:
				pass
		except IOError:
			Utils.MessageOK(self, u'{}\n\n    "{}".'.format(_('Cannot Open File'), fileName), _('Cannot Open File'), iconMask=wx.ICON_ERROR )
			Model.race = raceSave
			return

		# Set the new race with the updated properties.
		self.fileName = fileName
		Model.resetCache()
		ResetExcelLinkCache()
		
		properties.commit()			# Apply the new properties
		ftpPublish.setRaceAttr()	# Apply the ftp properties
		ftpPublish.Destroy()
		
		self.updateRecentFiles()

		if geoTrack:
			race.geoTrack, race.geoTrackFName = geoTrack, geoTrackFName
			distance = geoTrack.lengthKm if race.distanceUnit == race.UnitKm else geoTrack.lengthMiles
			if distance > 0.0:
				for c in race.categories.itervalues():
					c.distance = distance
			race.showOval = False
		
		self.setActiveCategories()
		self.setNumSelect( None )
		self.writeRace()
		self.showPageName( _('Actions') )
		self.refreshAll()
		
	@logCall
	def menuNewRaceDB( self, event ):
		# Get the RaceDB Excel sheet.
		dlg = wx.FileDialog( self, message=_("Choose a RaceDB Excel file"),
					defaultFile = '',
					wildcard = _('RaceDB Excel files (*.xlsx)|*.xlsx'),
					style=wx.OPEN | wx.CHANGE_DIR )
		fname = dlg.GetPath() if dlg.ShowModal() == wx.ID_OK else None
		dlg.Destroy()
		if not fname:
			return
			
		if not IsValidRaceDBExcel(fname):
			Utils.MessageOK( self, _("Excel file not in RaceDB format"), _("Excel Read Failure"), iconMask=wx.ICON_ERROR )
			return
		
		self.openRaceDBExcel( fname )

	def updateRecentFiles( self ):
		self.filehistory.AddFileToHistory(self.fileName)
		self.filehistory.Save(self.config)
		self.config.Flush()
		
	def closeFindDialog( self ):
		if getattr(self, 'findDialog', None):
			self.findDialog.Show( False )

	def openRace( self, fileName ):
		if not fileName:
			return
		self.showPageName( _('Results') )
		self.refresh()
		Model.resetCache()
		ResetExcelLinkCache()
		self.writeRace()
		self.closeFindDialog()
		
		try:
			with open(fileName, 'rb') as fp, Model.LockRace() as race:
				race = pickle.load( fp )
				race.sortLap = None			# Remove results lap sorting to avoid confusion.
				isFinished = race.isFinished()
				race.tagNums = None
				race.resetAllCaches()
				Model.setRace( race )
			
			self.fileName = fileName
			
			undo.clear()
			ResetExcelLinkCache()
			Model.resetCache()
			
			self.updateRecentFiles()
			
			self.setNumSelect( None )
			self.record.setTimeTrialInput( race.isTimeTrial )
			self.showPageName( _('Results') if isFinished else _('Actions'))
			self.refreshAll()
			Utils.writeLog( 'call: openRace: "%s"' % fileName )
			
			# Check if we have a missing spreadsheet, but can find one in the same folder as the race.
			if getattr(race, 'excelLink', None):
				excelLink = race.excelLink
				if excelLink.fileName and not os.path.isfile(excelLink.fileName):
					newFileName = os.path.join( os.path.dirname(fileName), os.path.basename(excelLink.fileName) )
					if os.path.isfile(newFileName) and Utils.MessageOKCancel(self,
							u'{}:\n\n"{}"\n\n{}:\n\n"{}"\n\n{}'.format(
								_('Could not find Excel file'), excelLink.fileName,
								_('Found this Excel file in the race folder with the same name'), newFileName, _('Use this Excel file from now on?')
							),
							_('Excel Link Not Found') ):
						race.excelLink.fileName = newFileName
						race.setChanged()
						ResetExcelLinkCache()
						Model.resetCache()
						self.refreshAll()
						Utils.writeLog( 'openRace: changed Excel file to "%s"' % newFileName )

		except Exception as e:
			Utils.logException( e, sys.exc_info() )
			Utils.MessageOK(self, u'{} "{}"\n\n{}.'.format(_('Cannot Open File'), fileName, e), _('Cannot Open File'), iconMask=wx.ICON_ERROR )

	@logCall
	def menuOpen( self, event ):
		dlg = wx.FileDialog( self, message=_("Choose a Race file"),
							defaultFile = '',
							wildcard = _('CrossMgr files (*.cmn)|*.cmn'),
							style=wx.OPEN | wx.CHANGE_DIR )
		if dlg.ShowModal() == wx.ID_OK:
			self.openRace( dlg.GetPath() )
		dlg.Destroy()

	def menuFileHistory( self, event ):
		fileNum = event.GetId() - wx.ID_FILE1
		fileName = self.filehistory.GetHistoryFile(fileNum)
		self.filehistory.AddFileToHistory(fileName)  # move up the list
		self.openRace( fileName )
		
	@logCall
	def menuOpenNext( self, event ):
		race = Model.race

		if race is None or not self.fileName:
			self.menuOpen( event )
			return

		if race is not None and race.isRunning():
			if not Utils.MessageOKCancel(self,	_('The current race is still running.\nFinish it and continue?'),
												_('Current race running') ):
				return
			race.finishRaceNow()
			self.writeRace()

		path, file = os.path.split( self.fileName )
		patRE = re.compile( '\-r[0-9]+\-' )
		try:
			pos = patRE.search(file).start()
			prefix = file[:pos+2] + '{}'.format(race.raceNum+1)
			suffix = os.path.splitext(file)[1]
			fileName = (f for f in os.listdir(path) if f.startswith(prefix) and f.endswith(suffix)).next()
			fileName = os.path.join( path, fileName )
			self.openRace( fileName )
		except (AttributeError, IndexError, StopIteration) as e:
			Utils.MessageOK(self, u'{}.\n\n{}'.format(_('No next race'),e), _('No next race'), iconMask=wx.ICON_ERROR )

	@logCall
	def menuCloseRace(self, event ):
		race = Model.race

		if race is None or not self.fileName:
			return

		if race is not None and race.isRunning():
			if not Utils.MessageOKCancel(self,	_('The current race is still running.\nFinish it and continue?'),
												_('Current race running') ):
				return
			race.finishRaceNow()
			
		self.doCleanup()
		Model.setRace( None )
		self.refresh()
	
	@logCall
	def menuExit(self, event):
		self.onCloseWindow( event )

	def genTimes( self ):
		regen = False
		if regen:
			fname = 'SimulationLapTimes.py'
		
			# Generate all the random rider events.
			random.seed( 10101021 )

			self.raceMinutes = 8
			mean = 8*60.0 / 8	# Average lap time.
			var = mean/20		# Variance between riders.
			lapsTotal = int(self.raceMinutes * 60 / mean + 3)
			raceTime = mean * lapsTotal
			errorPercent = 1.0/25.0

			riders = 30
			numStart = 200 - riders/2

			self.lapTimes = []
			for num in xrange(numStart,numStart+riders+1):
				t = 0
				if num < numStart + riders / 2:
					mu = random.normalvariate( mean, mean/20.0 )			# Rider's random average lap time.
				else:
					mu = random.normalvariate( mean * 1.15, mean/20.0 )		# These riders are slower, on average.
					t += 60.0												# Account for offset start.
				for laps in xrange(lapsTotal):
					t += random.normalvariate( mu, var/2 )	# Rider's lap time.
					if random.random() > errorPercent:		# Respect error rate.
						self.lapTimes.append( (t, num) )

			self.lapTimes.sort()
			
			# Get the times and leaders for each lap.
			leaderTimes = [self.lapTimes[0][0]]
			leaderNums  = [self.lapTimes[0][1]]
			numSeen = set()
			for t, n in self.lapTimes:
				if n in numSeen:
					leaderTimes.append( t )
					leaderNums.append( n )
					numSeen.clear()
				numSeen.add( n )
			
			# Find the leader's time after the end of the race.
			iLast = bisect.bisect_left( leaderTimes, self.raceMinutes * 60.0, hi = len(leaderTimes) - 1 )
			if leaderTimes[iLast] < self.raceMinutes * 60.0:
				iLast += 1
				
			# Trim out everything except next arrivals after the finish time.
			tLeaderLast = leaderTimes[iLast]
			numSeen = set()
			afterLeaderFinishEvents = [evt for evt in self.lapTimes if evt[0] >= tLeaderLast]
			self.lapTimes = [evt for evt in self.lapTimes if evt[0] < tLeaderLast]
			
			# Find the next unique arrival of all finishers.
			lastLapFinishers = []
			tStop = self.raceMinutes * 60.0
			numSeen = set()
			for t, n in afterLeaderFinishEvents:
				if n not in numSeen:
					numSeen.add( n )
					lastLapFinishers.append( (t, n) )
					
			self.lapTimes.extend( lastLapFinishers )
			
			with open(fname, 'w') as f:
				print >> f, 'raceMinutes =', self.raceMinutes
				print >> f, 'lapTimes =', self.lapTimes
		else:
			self.raceMinutes = SimulationLapTimes.raceMinutes
			self.lapTimes = copy.copy(SimulationLapTimes.lapTimes)
			
			# Add some out-of-category numbers to test.
			for e in xrange(10, 50, 10):
				self.lapTimes[e] = ( self.lapTimes[e][0], 1111+e )
		
		return self.lapTimes
		
	@logCall
	def menuSimulate( self, event ):
		fName = os.path.join( os.path.expanduser('~'), 'Simulation.cmn' )
		if not Utils.MessageOKCancel(self, u'\n'.join( [
				_('Simulate Race'),
				u'',
				_('This will simulate a race using randomly generated data.'),
				_("It is a good illustration of CrossMgr's functionality with real time data."),
				u'',
				_('The simulation takes about 8 minutes.'),
				_('Unlike a real race, the simulation will show riders crossing the line right from the start.'),
				_('In a real race, riders would have to finish the first lap before they were recorded.'),
				u'',
				u'{}: "{}".'.format(_('The race will be written to'), fName),
				u'',
				_('Continue?'),
				] ),
				_('Simulate Race') ):
			return

		try:
			with open(fName, 'wb') as fp:
				pass
		except IOError:
			Utils.MessageOK(self, u'{} "{}".'.format(_('Cannot open file'), fName), _('File Open Error'),iconMask = wx.ICON_ERROR)
			return

		self.showPageName( _('Results') )	# Switch to a read-only view.
		self.updateLapCounter()
		self.refresh()
		
		self.lapTimes = self.genTimes()
		tMin = self.lapTimes[0][0]
		self.lapTimes.reverse()			# Reverse the times so we can pop them from the stack later.

		# Set up a new file and model for the simulation.
		self.fileName = fName
		OutputStreamer.DeleteStreamerFile()
		self.simulateSeen = set()
		undo.clear()
		with Model.lock:
			Model.setRace( None )
			race = Model.newRace()
			race.name = 'Simulate'
			race.organizer = 'Edward Sitarski'
			race.memo = ''
			race.minutes = self.raceMinutes
			race.raceNum = 1
			#race.isTimeTrial = True
			#race.enableUSBCamera = True
			#race.photosAtRaceEndOnly = True
			#race.enableJChipIntegration = True
			race.setCategories( [	{'name':'Junior', 'catStr':'100-199', 'startOffset':'00:00', 'distance':0.5, 'gender':'Men'},
									{'name':'Senior', 'catStr':'200-299', 'startOffset':'00:15', 'distance':0.5, 'gender':'Women'}] )
			self.lapTimes = [(lt[0] + race.getStartOffset(lt[1]), lt[1]) for lt in self.lapTimes]

		self.writeRace()
		DeletePhotos( self.fileName )
		
		# Create an Excel data file of rider data.
		fnameInfo = os.path.join( Utils.getImageFolder(), 'NamesTeams.csv' )
		riderInfo = []
		try:
			with open(fnameInfo) as fp:
				header = None
				for line in fp:
					line = line.decode('iso-8859-1')
					if not header:
						header = line.split(',')
						continue
					riderInfo.append( line.split(',') )
		except IOError:
			pass
			
		if riderInfo:
			fnameRiderInfo = os.path.join(Utils.getHomeDir(), 'SimulationRiderData.xlsx')
			sheetName = 'RiderData'
			wb = xlsxwriter.Workbook( fnameRiderInfo )
			ws = wb.add_worksheet(sheetName)
			for c, h in enumerate(['Bib#', 'LastName', 'FirstName', 'Team']):
				ws.write(0, c, h)
			for r, row in enumerate(riderInfo):
				ws.write( r+1, 0, r+100 )
				for c, v in enumerate(row):
					ws.write( r+1, c+1, v )
			wb.close()
			
			race.excelLink = ExcelLink()
			race.excelLink.setFileName( fnameRiderInfo )
			race.excelLink.setSheetName( sheetName )
			race.excelLink.setFieldCol( {'Bib#':0, 'LastName':1, 'FirstName':2, 'Team':3} )

		# Start the simulation.
		self.showPageName( _('Chart') )
		self.refresh()

		self.nextNum = None
		with Model.LockRace() as race:
			race.startRaceNow()		
			# Backup all the events and race start so we don't have to wait for the first lap.
			race.startTime -= datetime.timedelta( seconds = (tMin-1) )

		OutputStreamer.writeRaceStart()
		self.simulateTimer = wx.CallLater( 1, self.updateSimulation, True )
		self.updateRaceClock()
		self.refresh()

	def updateSimulation( self, num ):
		if Model.race is None:
			return
		if self.nextNum is not None and self.nextNum not in self.simulateSeen:
			self.forecastHistory.logNum( self.nextNum )

		with Model.LockRace() as race:
			if race.curRaceTime() > race.minutes * 60.0:
				self.simulateSeen.add( self.nextNum )

		try:
			t, self.nextNum = self.lapTimes.pop()
			with Model.LockRace() as race:
				if t < (self.raceMinutes*60.0 + race.getAverageLapTime()*1.5):
					self.simulateTimer.Restart( int(max(1,(t - race.curRaceTime()) * 1000)), True )
					return
		except IndexError:
			pass
		
		self.simulateTimer.Stop()
		self.nextNum = None
		with Model.LockRace() as race:
			race.finishRaceNow()
		JChip.Cleanuplistener()
		
		OutputStreamer.writeRaceFinish()
		# Give the streamer a chance to write the last message.
		wx.CallLater( 2000, OutputStreamer.StopStreamer )
		
		Utils.writeRace()
		self.refresh()

	@logCall
	def menuImportCategories( self, event ):
		self.commit()
		if not Model.race:
			Utils.MessageOK( self, _("A race must be loaded first."), _("Import Categories"), iconMask=wx.ICON_ERROR)
			return
			
		dlg = wx.FileDialog( self, message=_("Choose Race Categories File"),
							defaultDir=os.getcwd(), 
							defaultFile="",
							wildcard=_("Bicycle Race Categories (*.brc)|*.brc"),
							style=wx.OPEN )
		if dlg.ShowModal() == wx.ID_OK:
			categoriesFile = dlg.GetPath()
			try:
				with io.open(categoriesFile, 'r', encoding='utf-8') as fp, Model.LockRace() as race:
					race.importCategories( fp )
			except IOError:
				Utils.MessageOK( self, u"{}:\n\n{}".format(_('Cannot open file'), categoriesFile), _("File Open Error"), iconMask=wx.ICON_ERROR)
			except (ValueError, IndexError):
				Utils.MessageOK( self, u"{}:\n\n{}".format(_('Bad file format'), categoriesFile), _("File Read Error"), iconMask=wx.ICON_ERROR)
			else:
				self.refresh()
				
		dlg.Destroy()
	
	@logCall
	def menuExportCategories( self, event ):
		self.commit()
		race = Model.getRace()
		if not race:
			Utils.MessageOK( self, _("A race must be loaded first."), _("Export Categories"), iconMask=wx.ICON_ERROR)
			return
			
		dlg = wx.FileDialog( self, message=_("Choose Race Categories File"),
							defaultDir=os.getcwd(), 
							defaultFile="",
							wildcard=_("Bicycle Race Categories (*.brc)|*.brc"),
							style=wx.SAVE )
							
		if dlg.ShowModal() == wx.ID_OK:
			fname = dlg.GetPath()
			try:
				with io.open(fname, 'w', encoding='utf-8') as fp, Model.LockRace() as race:
					race.exportCategories( fp )
			except IOError:
				Utils.MessageOK( self, u"{}:\n{}".format(_('Cannot open file'), fname), _("File Open Error"), iconMask=wx.ICON_ERROR)
				
		dlg.Destroy()	
		
	@logCall
	def menuExportHistory( self, event ):
		self.commit()
		if self.fileName is None or len(self.fileName) < 4 or not Model.race:
			return

		self.showPageName( _('History') )
		self.history.setCategoryAll()
		self.history.refresh()
		
		xlFName = self.fileName[:-4] + '-History.xls'
		dlg = wx.DirDialog( self, u'{} "{}"'.format(_('Folder to write'), os.path.basename(xlFName)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(xlFName) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		xlFName = os.path.join( dName, os.path.basename(xlFName) )

		colnames = self.history.grid.GetColNames()
		data = self.history.grid.GetData()
		if data:
			rowMax = max( len(c) for c in data )
			colnames = ['Count'] + colnames
			data = [['{}'.format(i) for i in xrange(1, rowMax+1)]] + data
		with Model.LockRace() as race:
			title = u'{}\n{}\n{}'.format( race.name, Utils.formatDate(race.date), _('Race History') )
		export = ExportGrid( title, colnames, data )

		wb = xlwt.Workbook()
		sheetCur = wb.add_sheet( 'History' )
		export.toExcelSheet( sheetCur )
		
		try:
			wb.save( xlFName )
			webbrowser.open( xlFName, new = 2, autoraise = True )
			Utils.MessageOK(self, u'{}:\n\n   {}'.format(_('Excel file written to'), xlFName), _('Excel Write'))
		except IOError:
			Utils.MessageOK(self,
						u'{} "{}".\n\n{}\n{}'.format(
							_('Cannot write'), xlFName,
							_('Check if this spreadsheet is open.'),
							_('If so, close it, and try again.')
						),
						_('Excel File Error'), iconMask=wx.ICON_ERROR )
	
	@logCall
	def menuExportUSAC( self, event ):
		self.commit()
		if self.fileName is None or len(self.fileName) < 4 or not Model.race:
			return

		self.showPageName( _('Results') )
		
		xlFName = self.fileName[:-4] + '-USAC.xls'
		dlg = wx.DirDialog( self, u'{} "{}"'.format(_('Folder to write'), os.path.basename(xlFName)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(xlFName) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		xlFName = os.path.join( dName, os.path.basename(xlFName) )

		wb = xlwt.Workbook()
		sheetCur = wb.add_sheet( 'Combined Results' )
		USACExport( sheetCur )
		
		try:
			wb.save( xlFName )
			if self.launchExcelAfterPublishingResults:
				webbrowser.open( xlFName, new = 2, autoraise = True )
			Utils.MessageOK(self, u'{}:\n\n   {}'.format(_('Excel file written to'), xlFName), _('Excel Write'))
		except IOError:
			Utils.MessageOK(self,
						u'{} "{}".\n\n{}\n{}'.format(_('Cannot write'), xlFName, _('Check if this spreadsheet is open.'), _('If so, close it, and try again.')),
						_('Excel File Error'), iconMask=wx.ICON_ERROR )
	
	@logCall
	def menuExportVTTA( self, event ):
		self.commit()
		if self.fileName is None or len(self.fileName) < 4 or not Model.race:
			return

		self.showPageName( _('Results') )
		
		xlFName = self.fileName[:-4] + '-VTTA.xls'
		dlg = wx.DirDialog( self, u'{} "{}"'.format(_('Folder to write'), os.path.basename(xlFName)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(xlFName) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		xlFName = os.path.join( dName, os.path.basename(xlFName) )

		wb = xlwt.Workbook()
		sheetCur = wb.add_sheet( 'Combined Results' )
		VTTAExport( sheetCur )
		
		try:
			wb.save( xlFName )
			if self.launchExcelAfterPublishingResults:
				webbrowser.open( xlFName, new = 2, autoraise = True )
			Utils.MessageOK(self, u'{}:\n\n   {}'.format(_('Excel file written to'), xlFName), _('Excel Write'))
		except IOError:
			Utils.MessageOK(self,
						u'{} "{}".\n\n{}\n{}'.format(_('Cannot write'), xlFName, _('Check if this spreadsheet is open.'), _('If so, close it, and try again.')),
						_('Excel File Error'), iconMask=wx.ICON_ERROR )
	
	@logCall
	def menuExportUCI( self, event ):
		self.commit()
		if self.fileName is None or len(self.fileName) < 4:
			return

		xlFName = self.fileName[:-4] + '-UCI.xls'
		dlg = wx.DirDialog( self, u'{} "{}"'.format(_('Folder to write'), os.path.basename(xlFName)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(xlFName) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		xlFName = os.path.join( dName, os.path.basename(xlFName) )

		wb = xlwt.Workbook()
		raceCategories = getRaceCategories()
		for catName, category in raceCategories:
			if catName == 'All':
				continue
			if not category.uploadFlag:
				continue
			sheetName = re.sub('[+!#$%&+~`".:;|\\/?*\[\] ]+', ' ', Utils.toAscii(catName))
			sheetName = sheetName[:31]
			sheetCur = wb.add_sheet( sheetName )
			UCIExport( sheetCur, category )

		try:
			wb.save( xlFName )
			if self.launchExcelAfterPublishingResults:
				webbrowser.open( xlFName, new = 2, autoraise = True )
			Utils.MessageOK(self, u'{}:\n\n   {}'.format(_('Excel file written to'), xlFName), _('Excel Write'))
		except IOError:
			Utils.MessageOK(self,
						u'{} "{}".\n\n{}\n{}'.format(_('Cannot write'), xlFName, _('Check if this spreadsheet is open.'), _('If so, close it, and try again.')),
						_('Excel File Error'), iconMask=wx.ICON_ERROR )
	
	def resultsCheck( self ):
		return Utils.MessageOKCancel( self,
				u'\n'.join([
					_('Make sure you publish correct results!'),
					_('Take a few minutes to check the following:'),
					'',
					'\n'.join( u'{}. {}'.format(i+1, s) for i, s in enumerate([
							_('Is the Race Name spelled correctly?'),
							_('Is the Race Organizer spelled correctly?'),
							_('Are the City, State/Prov and Country fields correctly filled in?'),
							_('Are all the Category Names spelled and coded correctly?'),
							_('Are the Category Number Ranges correct?'),
							_('Have you fixed all scoring and data problems with the Race?'),
							_('Are the Rider Names / Teams / License data correct (spelling?  missing data)?'),
						]) ),
					'',
					_('If not, press Cancel, fix the issues and publish again.')
				]),
				_('Results Publish') )
	
	@logCall
	def menuExportCrossResults( self, event ):
		self.commit()
		if self.fileName is None or len(self.fileName) < 4 or not Model.race:
			return
			
		race = Model.race

		if not race.city or not race.stateProv or not race.country:
			Utils.MessageOK(self,
						_('Missing City, State/Prov or Country fields.') + u'\n\n' +
							_('Please fill in these fields in Properties.'),
						_('Missing Location Fields'), iconMask=wx.ICON_ERROR )
			ChangeProperties( self )
			self.showPageName( _('Properties') )
			return
			
		if not self.resultsCheck():
			return
			
		self.showPageName( _('Results') )
		
		fname = self.fileName[:-4] + '-CrossResults.csv'
		dlg = wx.DirDialog( self, u'{} "{}"'.format(_('Folder to write'), os.path.basename(fname)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(fname) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		fname = os.path.join( dName, os.path.basename(fname) )
		
		year, month, day = race.date.split( '-' )
		raceName = race.name
		raceDate = datetime.date( year = int(year), month = int(month), day = int(day) ).strftime( '%m/%d/%Y' )
		
		try:
			success, message = CrossResultsExport( fname )
			if not success:
				Utils.MessageOK(self,
							u'CrossResults {}: "{}"'.format(_('Error'), message),
							u'CrossResults {}'.format(_('Error')), iconMask=wx.ICON_ERROR )
				return
			
			url = 'http://www.crossresults.com/?n=results&sn=upload&crossmgr={MD5}&name={RaceName}&date={RaceDate}&loc={Location}&presentedby={PresentedBy}'.format(
				RaceName	= urllib.quote(unicode(raceName).encode('utf-8')),
				RaceDate	= urllib.quote(unicode(raceDate).encode('utf-8')),
				MD5			= hashlib.md5( race.name + raceDate ).hexdigest(),
				Location	= urllib.quote(unicode(u', '.join([race.city, race.stateProv, race.country])).encode('utf-8')),
				PresentedBy = urllib.quote(unicode(race.organizer).encode('utf-8')),
			)
			if self.launchExcelAfterPublishingResults:
				webbrowser.open( url, new = 2, autoraise = True )
		except Exception as e:
			logException( e, sys.exc_info() )
			Utils.MessageOK(self,
						u'{} "{}"\n\n{}'.format(_('Cannot write'), fname, e),
						u'CrossResults {}'.format(_('File Error')), iconMask=wx.ICON_ERROR )
	
	@logCall
	def menuExportWebScorer( self, event ):
		self.commit()
		if self.fileName is None or len(self.fileName) < 4 or not Model.race:
			return
			
		race = Model.race

		if not self.resultsCheck():
			return
			
		self.showPageName( _('Results') )
		
		fname = self.fileName[:-4] + '-WebScorer.txt'
		dlg = wx.DirDialog( self, u'{} "{}"'.format(_('Folder to write'), os.path.basename(fname)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(fname) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		fname = os.path.join( dName, os.path.basename(fname) )
		
		try:
			success, message = WebScorerExport( fname )
			if not success:
				Utils.MessageOK(self,
							u'WebScorer {}: "{}".'.format(_('Error'), message),
							u'WebScorer {}'.format(_('Error')), iconMask=wx.ICON_ERROR )
				return
			Utils.MessageOK(self, _('WebScorer file written to:') + u'\n\n   {}'.format(fname), _('WebScorer Publish'))
		except Exception as e:
			logException( e, sys.exc_info() )
			Utils.MessageOK(self,
						u'{} "{}"\n\n{}.'.format(_('Cannot write'), fname, e),
						_('WebScorer Publish Error'), iconMask=wx.ICON_ERROR )
	
	def windowCloseCallback( self, menuId ):
		try:
			attr, name, menuItem, dialog = self.menuIdToWindowInfo[menuId]
		except KeyError:
			return
		menuItem.Check( False )
	
	@logCall
	def menuWindow( self, event ):
		try:
			attr, name, menuItem, dialog = self.menuIdToWindowInfo[event.GetId()]
		except KeyError:
			return
		
		if dialog.IsShown():
			dialog.commit()
			dialog.Show( False )
		else:
			dialog.Show( True )
			wx.CallAfter( dialog.refresh )

	@logCall
	def openMenuWindow( self, windowAttr ):
		for attr, name, menuItem, dialog in self.menuIdToWindowInfo.itervalues():
			if windowAttr == attr:
				dialog.Show( True )
				wx.CallAfter( dialog.refresh )
				break
	
	@logCall
	def menuHelpQuickStart( self, event ):
		Utils.showHelp( 'QuickStart.html' )
	
	@logCall
	def menuHelpSearch( self, event ):
		self.helpSearch.Show()
	
	@logCall
	def menuHelp( self, event ):
		Utils.showHelp( 'Main.html' )
	
	@logCall
	def onContextHelp( self, event ):
		Utils.showHelp( self.attrClassName[self.notebook.GetSelection()][2] + '.html' )
	
	@logCall
	def menuAbout( self, event ):
		# First we create and fill the info object
		info = wx.AboutDialogInfo()
		info.Name = Version.AppVerName
		info.Version = ''
		info.Copyright = "(C) 2009-{}".format( datetime.datetime.now().year )
		info.Description = wordwrap(
_("""Create Cycling race results quickly and easily with little preparation.

A brief list of features:
   * Input riders on the first lap
   * Predicts riders for all other laps based on lap times
   * Indicates race leader by category and tracks missing riders
   * Interpolates missing numbers.  Ignores duplicate rider entries.
   * Shows results instantly by category during and after race
   * Shows rider history
   * Allows rider lap adjustments
   * UCI 80% Rule Countdown
"""),
			500, wx.ClientDC(self))
		info.WebSite = ("http://sites.google.com/site/crossmgrsoftware/", "CrossMgr Home Page")
		info.Developers = [
					"Edward Sitarski (edward.sitarski@gmail.com)",
					"Andrew Paradowski (andrew.paradowski@gmail.com)"
					]

		licenseText = \
_("""User Beware!

This program is experimental, under development and may have bugs.
Feedback is sincerely appreciated.
Donations are also appreciated - see website for details.

CRITICALLY IMPORTANT MESSAGE!
This program is not warranted for any use whatsoever.
It may not produce correct results, it might lose your data.
The authors of this program assume no responsibility or liability for data loss or erroneous results produced by this program.

Use entirely at your own risk.
Do not come back and tell me that this program screwed up your event!
Computers fail, screw-ups happen.  Always use a paper manual backup.
""")
		info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

		wx.AboutBox(info)

	#--------------------------------------------------------------------------------------

	def getCurrentPage( self ):
		return self.pages[self.notebook.GetSelection()]
		
	def isShowingPage( self, page ):
		return page == self.pages[self.notebook.GetSelection()]
	
	def showRiderDetail( self, num = None ):
		self.riderDetail.setRider( num )
		for i, p in enumerate(self.pages):
			if p == self.riderDetail:
				self.showPage( i )
				break

	def setRiderDetail( self, num = None ):
		self.riderDetail.setRider( num )

	def showPage( self, iPage ):
		self.callPageCommit( self.notebook.GetSelection() )
		self.callPageRefresh( iPage )
		self.notebook.SetSelection( iPage )
		self.pages[self.notebook.GetSelection()].Layout()

	def showPageName( self, name ):
		name = name.replace(' ', '')
		for i, (a, c, n) in enumerate(self.attrClassName):
			if n == name:
				self.showPage( i )
				break

	def callPageRefresh( self, i ):
		try:
			page = self.pages[i]
		except IndexError:
			return
		
		try:
			page.refresh()
		except AttributeError:
			pass

	def refreshWindows( self ):
		try:
			for d in (dialog for attr, name, menuItem, dialog in self.menuIdToWindowInfo.itervalues() if dialog.IsShown()):
				try:
					wx.CallAfter( d.refresh )
				except AttributeError:
					pass
		except AttributeError:
			pass

	def callPageCommit( self, i ):
		try:
			self.pages[i].commit()
		except (AttributeError, IndexError):
			pass
		self.refreshWindows()

	def commit( self ):
		self.callPageCommit( self.notebook.GetSelection() )
				
	def refreshCurrentPage( self ):
		self.callPageRefresh( self.notebook.GetSelection() )
		self.refreshWindows()

	def refresh( self ):
		self.refreshCurrentPage()
		self.forecastHistory.refresh()
		if self.riderDetailDialog:
			wx.CallAfter( self.riderDetailDialog.refresh )
		self.updateRaceClock()
		with Model.LockRace() as race:
			self.menuItemHighPrecisionTimes.Check( bool(race and getattr(race, 'highPrecisionTimes', False)) ) 
			self.menuItemSyncCategories.Check( bool(race and getattr(race, 'syncCategories', True)) ) 
		if self.photoDialog.IsShown():
			self.photoDialog.refresh()

	def updateUndoStatus( self, event = None ):
		with Model.LockRace() as race:
			isRunning = bool(race and race.isRunning())
		self.undoMenuButton.Enable( bool(not isRunning and undo.isUndo()) )
		self.redoMenuButton.Enable( bool(not isRunning and undo.isRedo()) )
		
	def onPageChanging( self, event ):
		notebook = event.GetEventObject()
		if notebook == self.notebook:
			self.callPageCommit( event.GetOldSelection() )
			self.callPageRefresh( event.GetSelection() )
		try:
			Utils.writeLog( u'page: {}\n'.format(notebook.GetPage(event.GetSelection()).__class__.__name__) )
		except IndexError:
			pass
		event.Skip()	# Required to properly repaint the screen.

	def refreshRaceAnimation( self ):
		if self.pages[self.notebook.GetSelection()] == self.raceAnimation:
			self.raceAnimation.refresh()
	
	def refreshAll( self ):
		self.refresh()
		iSelect = self.notebook.GetSelection()
		for i, p in enumerate(self.pages):
			if i != iSelect:
				self.callPageRefresh( i )

	def setNumSelect( self, num ):
		try:
			num = int(num)
		except (TypeError, ValueError):
			num = None
			
		if num is None or num != self.numSelect:
			self.history.setNumSelect( num )
			self.results.setNumSelect( num )
			self.riderDetail.setNumSelect( num )
			self.gantt.setNumSelect( num )
			self.raceAnimation.setNumSelect( num )
			if self.photoDialog.IsShown():
				self.photoDialog.setNumSelect( num )
			self.numSelect = num

	#-------------------------------------------------------------
	
	def processNumTimes( self ):
		race = Model.race
		
		for num, t in self.numTimes:
			race.addTime( num, t )
		
		OutputStreamer.writeNumTimes( self.numTimes )
		photoRequests = [(num, t) for num, t in self.numTimes if okTakePhoto(num, t)]
		if photoRequests:
			success, error = SendPhotoRequests( photoRequests )
			if success:
				race.photoCount += len(photoRequests) * 2
			else:
				Utils.writeLog( 'USB Camera Error: {}'.format(error) )
		
		if race.ftpUploadDuringRace:
			realTimeFtpPublish.publishEntry()
		
		if self.getCurrentPage() == self.results:
			wx.CallAfter( self.results.showLastLap )
			
		self.numTimes = []
		self.updateLater = None
	
	def processJChipListener( self ):
		race = Model.race
		
		if not race or not race.enableJChipIntegration:
			if JChip.listener:
				JChip.StopListener()
			return False
		
		if not JChip.listener:
			JChip.StartListener( race.startTime )
			JChipSetup.GetTagNums( True )
		
		data = JChip.GetData()
		
		if not getattr(race, 'tagNums', None):
			JChipSetup.GetTagNums()
		if not race.tagNums:
			return False
		
		lastNumTimesLen = len(self.numTimes)
		for d in data:
			if d[0] != 'data':
				continue
			try:
				num, dt = race.tagNums[d[1]], d[2]
			except (TypeError, ValueError, KeyError):
				race.missingTags.add( d[1] )
				continue
				
			# Only process times after the start of the race.
			if race.isRunning() and race.startTime <= dt:
				self.numTimes.append( (num, (dt - race.startTime).total_seconds()) )
		
		doRefresh = (lastNumTimesLen != len(self.numTimes))
		
		self.processNumTimes()
		return doRefresh

	def updateRaceClock( self, event = None ):
		if hasattr(self, 'record'):
			self.record.refreshRaceTime()

		doRefresh = False
		with Model.LockRace() as race:
			if race is None:
				self.SetTitle( Version.AppVerName )
				JChip.StopListener()
				self.timer.Stop()
				return

			if race.isUnstarted():
				status = _('Unstarted')
			elif race.isRunning():
				status = _('Running')
				if race.enableJChipIntegration:
					doRefresh = self.processJChipListener()
				elif JChip.listener:
					JChip.StopListener()
			else:
				status = _('Finished')

			if not race.isRunning():
				self.SetTitle( u'{}-r{} - {} - {} {}'.format(
								race.name, race.raceNum,
								status,
								Version.AppVerName,
								u'<{}>'.format(_('TimeTrial')) if race.isTimeTrial else u'') )
				self.timer.Stop()
				return

			self.SetTitle( u'{} {}-r{} - {} - {} {} {}'.format(
							Utils.formatTime(race.curRaceTime()),
							race.name, race.raceNum,
							status, Version.AppVerName,
							u'<{}>'.format(_('JChip')) if JChip.listener else u'',
							u'<{}>'.format(_('TimeTrial')) if race.isTimeTrial else u'') )

			if not self.timer.IsRunning():
				wx.CallLater( 1000 - (datetime.datetime.now() - race.startTime).microseconds // 1000, self.timer.Start, 1000 )

		self.secondCount += 1
		if self.secondCount % 30 == 0 and race.isChanged():
			self.writeRace()
			
		if doRefresh:
			wx.CallAfter( self.refresh )
			wx.CallAfter( self.record.refreshLaps )

# Set log file location.
dataDir = ''
redirectFileName = ''

def MainLoop():
	global dataDir
	global redirectFileName
	
	app = wx.App(False)
	app.SetAppName("CrossMgr")
	
	if 'WXMAC' in wx.Platform:
		wx.Log.SetActiveTarget( LogPrintStackStderr() )
	
	random.seed()
	setpriority( priority=4 )	# Set to real-time priority.

	parser = OptionParser( usage = "usage: %prog [options] [RaceFile.cmn]" )
	parser.add_option("-f", "--file", dest="filename", help="race file", metavar="RaceFile.cmn")
	parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help='hide splash screen')
	parser.add_option("-r", "--regular", action="store_false", dest="fullScreen", default=True, help='regular size (not full screen)')
	(options, args) = parser.parse_args()
	
	dataDir = Utils.getHomeDir()
	redirectFileName = os.path.join(dataDir, 'CrossMgr.log')
			
	# Set up the log file.  Otherwise, show errors on the screen unbuffered.
	if __name__ == '__main__':
		Utils.disable_stdout_buffering()
	else:
		try:
			logSize = os.path.getsize( redirectFileName )
			if logSize > 1000000:
				os.remove( redirectFileName )
		except:
			pass
	
		try:
			app.RedirectStdio( redirectFileName )
		except:
			pass
	
	Utils.writeLog( 'start: {}'.format(Version.AppVerName) )
	
	# Configure the main window.
	mainWin = MainWin( None, title=Version.AppVerName, size=(1128,600) )
	
	if options.fullScreen:
		mainWin.Maximize( True )
	mainWin.Show()

	# Set the upper left icon.
	icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'CrossMgr16x16.ico'), wx.BITMAP_TYPE_ICO )
	mainWin.SetIcon( icon )

	# Set the taskbar icon.
	#tbicon = wx.TaskBarIcon()
	#tbicon.SetIcon( icon, "CrossMgr" )

	if options.verbose:
		ShowSplashScreen()
		ShowTipAtStartup()
	
	# Try to open a specified filename.
	fileName = options.filename
	
	# If nothing, try a positional argument.
	if not fileName and args:
		fileName = args[0]
	
	# Try to load a race.
	raceLoaded = False
	if fileName:
		try:
			ext = os.path.splitext( fileName )[1]
			if ext == '.cmn':
				mainWin.openRace( fileName )
				raceLoaded = True
			elif ext in ('.xls', '.xlsx', '.xlsm') and IsValidRaceDBExcel(fileName):
				mainWin.openRaceDBExcel( fileName )
				raceLoaded = True
		except (IndexError, AttributeError, ValueError):
			pass

	mainWin.forecastHistory.setSash()
	
	# Start processing events.
	app.MainLoop()

if __name__ == '__main__':
	MainLoop()
