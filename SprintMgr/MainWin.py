import wx
import wx.adv
from wx.lib.wordwrap import wordwrap
import wx.lib.agw.flatnotebook as flatnotebook
import os
import re
import sys
import datetime
import random
import time
import json
import webbrowser
import locale
import traceback
import xlsxwriter
from argparse import ArgumentParser
import codecs
import base64
import uuid
import pickle
from io import StringIO

import Utils
import Model
import Version

from Properties			import Properties
from Seeding			import Seeding
from Qualifiers			import Qualifiers
from Events				import Events
from Results			import Results
from Chart				import Chart
from GraphDraw			import GraphDraw
from Competitions		import SetDefaultData
from Printing			import SprintMgrPrintout, GraphDrawPrintout
from ExportGrid			import ExportGrid, tag, writeHtmlHeader
from FitSheetWrapper	import FitSheetWrapperXLSX
from Events				import FontSize

from SetGraphic			import SetGraphicDialog

#----------------------------------------------------------------------------------

def ShowSplashScreen():
	bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SprintMgrSplash.png'), wx.BITMAP_TYPE_PNG )
	
	# Write in the version number into the bitmap.
	w, h = bitmap.GetSize()
	dc = wx.MemoryDC()
	dc.SelectObject( bitmap )
	dc.SetFont( wx.Font( wx.Size(0,h//10), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ) )
	dc.DrawText( Version.AppVerName.replace('SprintMgr','Version'), w // 20, int(h * 0.4) )
	dc.SelectObject( wx.NullBitmap )
	
	showSeconds = 2.5
	
	# Show the splash screen.
	splashStyle = wx.adv.SPLASH_CENTRE_ON_PARENT|wx.adv.SPLASH_TIMEOUT
	frame = wx.adv.SplashScreen(
		parent=Utils.getMainWin(),
		splashStyle=splashStyle,
		bitmap=bitmap,
		milliseconds=int(showSeconds*1000) )

#----------------------------------------------------------------------------------
		
class MyTipProvider( wx.adv.TipProvider ):
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

def replaceJsonVar( s, varName, value ):
	return s.replace( '%s = null' % varName, '%s = %s' % (varName, json.dumps(value)), 1 )

def showHelp( url ):
	webbrowser.open( 'file:///' + os.path.join(Utils.getHtmlFolder(), url) )

#----------------------------------------------------------------------------------
		
class MainWin( wx.Frame ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(200,200) ):
		wx.Frame.__init__(self, parent, id, title, size=size)

		Utils.setMainWin( self )

		# Add code to configure file history.
		self.filehistory = wx.FileHistory(8)
		self.config = wx.Config(appName="SprintMgr",
								vendorName="SmartCyclingSolutions",
								#style=wx.CONFIG_USE_LOCAL_FILE
		)
		self.filehistory.Load(self.config)
		
		self.fileName = None
		
		# Default print options.
		self.printData = wx.PrintData()
		self.printData.SetPaperId(wx.PAPER_LETTER)
		self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
		#self.printData.SetOrientation(wx.PORTRAIT)

		# Configure the main menu.
		self.menuBar = wx.MenuBar(wx.MB_DOCKABLE)

		#-----------------------------------------------------------------------
		self.fileMenu = wx.Menu()

		self.fileMenu.Append( wx.ID_NEW , "&New...", "Create a new competition" )
		self.Bind(wx.EVT_MENU, self.menuNew, id=wx.ID_NEW )

		item = self.fileMenu.Append( wx.ID_ANY , "New N&ext...", "Create a new competition from the existing competition" )
		self.Bind(wx.EVT_MENU, self.menuNewNext, item )

		self.fileMenu.Append( wx.ID_OPEN , "&Open...", "Open an existing competition" )
		self.Bind(wx.EVT_MENU, self.menuOpen, id=wx.ID_OPEN )

		self.fileMenu.Append( wx.ID_SAVE , "&Save\tCtrl+S", "Save competition" )
		self.Bind(wx.EVT_MENU, self.menuSave, id=wx.ID_SAVE )

		self.fileMenu.Append( wx.ID_SAVEAS , "Save &As...", "Save to a different filename" )
		self.Bind(wx.EVT_MENU, self.menuSaveAs, id=wx.ID_SAVEAS )

		self.fileMenu.AppendSeparator()
		self.fileMenu.Append( wx.ID_PAGE_SETUP , "Page &Setup...", "Setup the print page" )
		self.Bind(wx.EVT_MENU, self.menuPageSetup, id=wx.ID_PAGE_SETUP )

		self.fileMenu.Append( wx.ID_PREVIEW , "Print P&review...\tCtrl+R", "Preview the current page on screen" )
		self.Bind(wx.EVT_MENU, self.menuPrintPreview, id=wx.ID_PREVIEW )

		self.fileMenu.Append( wx.ID_PRINT , "&Print...\tCtrl+P", "Print the current page to a printer" )
		self.Bind(wx.EVT_MENU, self.menuPrint, id=wx.ID_PRINT )

		self.fileMenu.AppendSeparator()

		item = self.fileMenu.Append( wx.ID_ANY , "&Export Current Screen to Excel...", "Export Current Screen to Excel (.xlsx)" )
		self.Bind(wx.EVT_MENU, self.menuExportToExcel, item )
		
		item = self.fileMenu.Append( wx.ID_ANY , "Export Current Screen to &HTML...", "Export to HTML (.html)" )
		self.Bind(wx.EVT_MENU, self.menuExportToHtml, item )

		self.fileMenu.AppendSeparator()
		
		item = self.fileMenu.Append( wx.ID_ANY , "Export Final &Classification to Excel...", "Export Final Classification Only to Excel (.xlsx)" )
		self.Bind(wx.EVT_MENU, self.menuExportFinalClassificationToExcel, item )
		
		self.fileMenu.AppendSeparator()
		
		recent = wx.Menu()
		self.fileMenu.AppendSubMenu(recent, "&Recent Files" )
		self.filehistory.UseMenu( recent )
		self.filehistory.AddFilesToMenu()
		
		self.fileMenu.AppendSeparator()

		self.fileMenu.Append( wx.ID_EXIT, "E&xit", "Exit SprintMan" )
		self.Bind(wx.EVT_MENU, self.menuExit, id=wx.ID_EXIT )
		
		self.Bind(wx.EVT_MENU_RANGE, self.menuFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9)
		
		self.menuBar.Append( self.fileMenu, "&File" )

		#-----------------------------------------------------------------------

		# Configure the field of the display.

		self.notebook = flatnotebook.FlatNotebook( self, agwStyle=flatnotebook.FNB_NO_X_BUTTON | flatnotebook.FNB_NO_NAV_BUTTONS )
		self.notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanging )
		
		# Add all the pages to the notebook.
		self.pages = []

		def addPage( page, name ):
			self.notebook.AddPage( page, name )
			self.pages.append( page )
			
		self.attrClassName = (
			( 'properties',		Properties,			'Properties' ),
			( 'seeding',		Seeding,			'Seeding' ),
			( 'qualifiers',		Qualifiers,			'Qualifiers' ),
			( 'events',			Events,				'Events' ),
			( 'results',		Results,			'Results' ),
			( 'graphDraw',		GraphDraw,			'Summary' ),
			( 'chart',			Chart,				'Full Table' ),
		)
		self.iQualifiersPage = next( i for i, (attr, cls, title) in enumerate(self.attrClassName) if attr == 'qualifiers' )
		self.iSeedingPage = next( i for i, (attr, cls, title) in enumerate(self.attrClassName) if attr == 'seeding' )			
		
		for i, (a, c, n) in enumerate(self.attrClassName):
			setattr( self, a, c(self.notebook) )
			addPage( getattr(self, a), n )
			
		self.notebook.SetSelection( 0 )
		
		#-----------------------------------------------------------------------
		self.toolsMenu = wx.Menu()
		
		item = self.toolsMenu.Append( wx.ID_ANY , _("Copy Log File to &Clipboard..."), _("Copy Log File to &Clipboard") )
		self.Bind(wx.EVT_MENU, self.menuCopyLogFileToClipboard, item )

		self.menuBar.Append( self.toolsMenu, _("&Tools") )
		
		#-----------------------------------------------------------------------
		self.optionsMenu = wx.Menu()
		
		item = self.optionsMenu.Append( wx.ID_ANY , _("Set &Graphic..."), _("Set Graphic for Output") )
		self.Bind(wx.EVT_MENU, self.menuSetGraphic, item )
		
		self.menuBar.Append( self.optionsMenu, _("&Options") )
		
		#-----------------------------------------------------------------------
		self.helpMenu = wx.Menu()

		'''
		item = self.helpMenu.Append( wx.ID_ANY , "&QuickStart...", "Get started with SprintMgr Now..." )
		self.Bind(wx.EVT_MENU, self.menuHelpQuickStart, item )
		item = self.helpMenu.Append( wx.ID_HELP , "&Help...", "Help about SprintMgr..." )
		self.Bind(wx.EVT_MENU, self.menuHelp, item )
		
		self.helpMenu.AppendSeparator()
		'''

		item = self.helpMenu.Append( wx.ID_ABOUT , "&About...", "About SprintMgr..." )
		self.Bind(wx.EVT_MENU, self.menuAbout, item )

		'''
		item = self.helpMenu.Append( wx.ID_ANY , "&Tips at Startup...", "Enable/Disable Tips at Startup..." )
		self.Bind(wx.EVT_MENU, self.menuTipAtStartup, item )
		'''

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
		
	def menuUndo( self, event ):
		undo.doUndo()
		self.refresh()
		
	def menuRedo( self, event ):
		undo.doRedo()
		self.refresh()
		
	def menuTipAtStartup( self, event ):
		showing = self.config.ReadBool('showTipAtStartup', True)
		if Utils.MessageOKCancel( self, 'Turn Off Tips at Startup?' if showing else 'Show Tips at Startup?', 'Tips at Startup' ):
			self.config.WriteBool( 'showTipAtStartup', showing ^ True )

	def menuChangeProperties( self, event ):
		if not Model.race:
			Utils.MessageOK(self, "You must have a valid race.", "No Valid Race", iconMask=wx.ICON_ERROR)
			return
		ChangeProperties( self )
				
	def getDirName( self ):
		return Utils.getDirName()
		
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

	def getTitle( self ):
		model = Model.model
		iSelection = self.notebook.GetSelection()
		try:
			pageTitle = self.pages[iSelection].getTitle()
		except Exception:
			pageTitle = self.attrClassName[iSelection][2]
			
		title = '%s\n%s (%s)\n%s' % (
			pageTitle,
			model.competition_name, model.date.strftime('%Y-%m-%d'),
			model.category,
		)
		return title
	
	def setFontSize( self, fontSize ):
		font = wx.Font( (0,fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		for attr, _1, _2 in self.attrClassName:
			page = getattr( self, attr )
			Utils.ChangeFontInChildren( page, font )
			page.GetSizer().Layout()
		Events.FontSize = fontSize
	
	def menuPrintPreview( self, event ):
		self.commit()
		title = self.getTitle()
		page = self.pages[self.notebook.GetSelection()]
		try:
			grid = page.getGrid()
			printout = SprintMgrPrintout( title, grid )
			printout2 = SprintMgrPrintout( title, grid )
		except AttributeError:
			if page == self.graphDraw:
				printout = GraphDrawPrintout( title, page )
				printout2 = GraphDrawPrintout( title, page )
			else:
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
			printout = SprintMgrPrintout( title, grid )
		except AttributeError:
			if page == self.graphDraw:
				printout = GraphDrawPrintout( title, page )
			else:
				return
		
		pdd = wx.PrintDialogData(self.printData)
		pdd.SetAllPages( 1 )
		pdd.EnablePageNumbers( 0 )
		pdd.EnableHelp( 0 )
		
		printer = wx.Printer(pdd)

		if not printer.Print(self, printout, True):
			if printer.GetLastError() == wx.PRINTER_ERROR:
				Utils.MessageOK(self, "There was a printer problem.\nCheck your printer setup.", "Printer Error",iconMask=wx.ICON_ERROR)
		else:
			self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )

		printout.Destroy()

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
		xlFName = self.fileName[:-4] + '-' + pageTitle + '.xlsx'
		dlg = wx.DirDialog( self, 'Folder to write "{}"'.format(os.path.basename(xlFName)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(xlFName) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		xlFName = os.path.join( dName, os.path.basename(xlFName) )

		title = self.getTitle()
		
		wb = xlsxwriter.Workbook( xlFName )
		sheetName = pageTitle
		sheetName = re.sub('[+!#$%&+~`".:;|\\/?*\[\] ]+', ' ', sheetName)[:31]
		sheetCur = wb.add_worksheet( sheetName )
		export = ExportGrid( title, grid )
		formats = ExportGrid.getExcelFormatsXLSX( wb )
		export.toExcelSheet( sheetCur, formats )

		try:
			wb.close()
			Utils.MessageOK(self, 'Exported to:\n\n   {}'.format(xlFName), 'Excel Export')
		except IOError:
			Utils.MessageOK(self,
						'Cannot write:\n\n\t{}.\n\nCheck if this spreadsheet is open.\nIf so, close it, and try again.'.format(xlFName),
						'Excel File Error', iconMask=wx.ICON_ERROR )
						
	def menuExportFinalClassificationToExcel( self, event ):
		self.commit()
		
		pageTitle = 'Final Classification'
		
		if not self.fileName or len(self.fileName) < 4:
			Utils.MessageOK(self, 'You must Save before you can Export to Excel', 'Excel Write')
			return
			
		model = Model.model
		competition = model.competition

		pageTitle = Utils.RemoveDisallowedFilenameChars( pageTitle.replace('/', '_') )
		xlFName = self.fileName[:-4] + '-' + pageTitle + '.xlsx'
		dlg = wx.DirDialog( self, 'Folder to write "{}"'.format(os.path.basename(xlFName)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(xlFName) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		xlFName = os.path.join( dName, os.path.basename(xlFName) )

		title = self.getTitle()
		
		wb = xlsxwriter.Workbook( xlFName )
		sheetName = 'Final Classification'
		sheetName = re.sub('[+!#$%&+~`".:;|\\/?*\[\] ]+', ' ', sheetName)[:31]

		sheetCur = wb.add_worksheet( sheetName )
		sheetFit = FitSheetWrapperXLSX( sheetCur )
		
		headerNames = ['Pos', 'Bib', 'LastName', 'FirstName', 'Team', 'UCI ID', 'Team']
		leftJustifyCols = { h for h in headerNames if h not in {'Pos', 'Bib'} }
		
		formats = ExportGrid.getExcelFormatsXLSX( wb )
		styleLeft = formats['styleLeft']
		styleRight = formats['styleRight']
		headerStyleLeft = formats['headerStyleLeft']
		headerStyleRight = formats['headerStyleRight']

		rowTop = 0
		results, dnfs, dqs = competition.getResults()
		for col, c in enumerate(headerNames):
			sheetFit.write( rowTop, col, c, headerStyleLeft if c in leftJustifyCols else headerStyleRight, bold=True )
		rowTop += 1
		
		for row, r in enumerate(results):
			if r:
				for col, value in enumerate([row+1, r.bib if r.bib else '', r.last_name.upper(), r.first_name, r.team, r.uci_id, model.category]):
					sheetFit.write( rowTop, col, value, styleLeft if headerNames[col] in leftJustifyCols else styleRight )
			rowTop += 1
		
		for r in dnfs:
			for col, value in enumerate(['DNF', r.bib if r.bib else '', r.last_name.upper(), r.first_name, r.team, r.uci_id, model.category]):
				sheetFit.write( rowTop, col, value, styleLeft if headerNames[col] in leftJustifyCols else styleRight )
			rowTop += 1
			
		for r in dqs:
			for col, value in enumerate(['DQ', r.bib if r.bib else '', r.last_name.upper(), r.first_name, r.team, r.uci_id, model.category]):
				sheetFit.write( rowTop, col, value, styleLeft if headerNames[col] in leftJustifyCols else styleRight )
			rowTop += 1
			
		for r in model.getDNQs():
			for col, value in enumerate(['DQ', r.bib if r.bib else '', r.last_name.upper(), r.first_name, r.team, r.uci_id, model.category]):
				sheetFit.write( rowTop, col, value, styleLeft if headerNames[col] in leftJustifyCols else styleRight )
			rowTop += 1

		try:
			wb.close()
			Utils.MessageOK(self, 'Excel file written to:\n\n\t{}'.format(xlFName), 'Excel Export')
		except IOError:
			Utils.MessageOK(self,
						'Cannot write\n\n\t{}\n\nCheck if this spreadsheet is open.\nIf so, close it, and try again.'.format(xlFName),
						'Excel File Error', iconMask=wx.ICON_ERROR )
	
	def menuExportToHtml( self, event ):
		self.commit()
		iSelection = self.notebook.GetSelection()
		page = self.pages[iSelection]
		
		grid = None
		image = None
		try:
			grid = page.getGrid()
		except Exception as e:
			pass
		
		if not grid:
			try:
				image = page.getImage()
			except Exception as e:
				pass
				
		if not (grid or image):
			return
		
		try:
			pageTitle = self.pages[iSelection].getTitle()
		except Exception:
			pageTitle = self.attrClassName[iSelection][2]
		
		if not self.fileName or len(self.fileName) < 4:
			Utils.MessageOK(self, 'You must Save before you can Export to Html', 'Excel Export')
			return

		pageTitle = Utils.RemoveDisallowedFilenameChars( pageTitle.replace('/', '_') )
		htmlFName = self.fileName[:-4] + '-' + pageTitle + '.html'
		dlg = wx.DirDialog( self, 'Folder to write "{}"'.format(os.path.basename(htmlFName)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(htmlFName) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		htmlFName = os.path.join( dName, os.path.basename(htmlFName) )

		title = self.getTitle()
		
		htmlStream = StringIO()
		html = htmlStream
		
		with tag(html, 'html'):
			with tag(html, 'head'):
				with tag(html, 'title'):
					html.write( title.replace('\n', ' ') )
				with tag(html, 'meta', dict(author="Edward Sitarski", copyright="Edward Sitarski, 2013", generator="SprintMgr")):
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
				if grid:
					ExportGrid( title, grid ).toHtml(html)
				elif image:
					pngFName = os.path.join( dName, '{}.png'.format(uuid.uuid4()) )
					image.SaveFile( pngFName, wx.BITMAP_TYPE_PNG )
					with open(pngFName, 'rb') as fp:
						data = base64.b64encode( fp.read() )
					os.remove( pngFName )
					writeHtmlHeader( html, title )
					html.write( '<img id="idResultsSummary" src="data:image/png;base64,{}" />'.format(data.decode()) )
		
		html = htmlStream.getvalue()
		
		try:
			with open(htmlFName, 'w') as fp:
				fp.write( html )
			webbrowser.open( htmlFName, new = 2, autoraise = True )
			Utils.MessageOK(self, 'Html file written to:\n\n   {}'.format(htmlFName), 'Html Write')
		except IOError:
			Utils.MessageOK(self,
						'Cannot write "{}".\n\nCheck if this file is open.\nIf so, close it, and try again.'.format(htmlFName),
						'Html File Error', iconMask=wx.ICON_ERROR )
	
	#--------------------------------------------------------------------------------------------
	def onCloseWindow( self, event ):
		self.showResultsPage()
		self.writeRace()
		wx.Exit()

	def writeRace( self ):
		self.commit()
		if not self.fileName:
			self.setTitle()
			return
		model = Model.model
		with open(self.fileName, 'wb') as fp:
			pickle.dump( model, fp, 2 )
		model.setChanged( False )
		self.setTitle()
		
	def showResultsPage( self ):
		for i, (a, c, n) in enumerate(self.attrClassName):
			if 'Results' in n:
				self.showPage( i )
				break

	def menuNew( self, event ):
		self.showResultsPage()
		model = Model.model
		if model.changed:
			ret = Utils.MessageOKCancel( self, 'Save Existing Competition?', 'Save Existing Competition?' ) 
			if ret == wx.ID_CANCEL:
				return
			if ret == wx.ID_OK:
				self.writeRace()
				
		Model.model = SetDefaultData()
		self.fileName = ''
		self.showPageName( 'Properties' )
		self.refresh()
	
	def menuNewNext( self, event ):
		if not self.fileName:
			self.menuSaveAs( event )
			return
	
		self.showResultsPage()
		model = Model.model
		if model.changed and Utils.MessageOKCancel(self, 'Save Existing Competition?', u'Save Existing Competition?')  == wx.ID_OK:
			try:
				self.writeRace()
			except Exception:
				Utils.MessageOK(self, 'Write Failed.  Competition NOT saved.\n\n"{}".'.format(self.fileName),
									'Write Failed', iconMask=wx.ICON_ERROR )
				return
			
		fileName, ext = os.path.splitext( self.fileName )
		s = re.search( ' \((\d+)\)$', fileName )
		if s:
			fileName = fileName[:fileName.index(' (')] + ' ({})'.format(int(s.group(1))+1) + ext
		else:
			fileName = fileName + ' (2)' + ext
			
		if (	os.path.isfile(fileName) and
				Utils.MessageOKCancel(self, 'File exists.  Replace?:\n\n"{}"'.format(fileName), u'File exists' ) != wx.ID_OK ):
			return
		
		self.fileName = fileName
				
		properties = model.getProperties()
		Model.model = model = SetDefaultData()
		model.setProperties( properties )
		
		self.showPageName( 'Properties' )
		self.refresh()
			
	def updateRecentFiles( self ):
		self.filehistory.AddFileToHistory(self.fileName)
		self.filehistory.Save(self.config)
		self.config.Flush()
		
	def openRace( self, fileName ):
		if not fileName:
			return
		try:
			with open(fileName, 'rb') as fp:
				Model.model = pickle.load( fp )
		except IOError:
			Utils.MessageOK(self, 'Cannot Open File "{}".'.format(fileName), 'Cannot Open File', iconMask=wx.ICON_ERROR )
			return
		
		Model.model.competition.fixHangingStarts()	# Fix up any interrupted starts.
		self.fileName = fileName
		self.updateRecentFiles()
		Model.model.setChanged( False )
		# Model.model.competition.reset()
		Model.model.competition.propagate()
		self.refreshAll()
		if Model.model.canReassignStarters():
			self.showPageName( 'Properties' )
		else:
			self.showPageName( 'Summary' )

	def menuOpen( self, event ):
		if Model.model.changed:
			if Utils.MessageOKCancel(self, 'You have Unsaved Changes.  Save Now?', 'Unsaved Changes') == wx.ID_OK:
				self.writeRace()
			else:
				return
				
		dlg = wx.FileDialog( self, message="Choose a SprintMgr file",
							defaultFile = '',
							wildcard = 'SprintMgr files (*.smr)|*.smr',
							style=wx.FD_OPEN | wx.FD_CHANGE_DIR )
		if dlg.ShowModal() == wx.ID_OK:
			self.openRace( dlg.GetPath() )
		dlg.Destroy()

	def menuSave( self, event ):
		if not self.fileName:
			self.menuSaveAs( event )
			return
		
		try:
			self.writeRace()
		except Exception:
			Utils.MessageOK(self, 'Write Failed.  Competition NOT saved.\n\n"{}".'.format(fileName),
								'Write Failed', iconMask=wx.ICON_ERROR )
		self.updateRecentFiles()

	def setTitle( self ):
		model = Model.model
		if self.fileName:
			title = '{}: {}{} - {}'.format(model.category, '*' if model.changed else '', self.fileName, Version.AppVerName)
		else:
			title = '{}: {}'.format( model.category, Version.AppVerName )
		self.SetTitle( title )
		isKeirin = (model.competition and model.competition.isKeirin)
		self.notebook.EnableTab( self.iQualifiersPage, not isKeirin )
		self.notebook.SetPageText( self.iQualifiersPage, ' ' if isKeirin else self.attrClassName[self.iQualifiersPage][2] )
			
	def menuSaveAs( self, event ):
		dlg = wx.FileDialog( self, message="Choose a file for your Competition",
							defaultFile = '',
							wildcard = 'SprintMgr files (*.smr)|*.smr',
							style=wx.FD_SAVE | wx.FD_CHANGE_DIR )
		fileName = dlg.GetPath() if dlg.ShowModal() == wx.ID_OK else None
		dlg.Destroy()
		
		if not fileName:
			return
			
		if not fileName.endswith('.smr'):
			fileName += '.smr'
		
		try:
			with open(fileName, 'rb') as fp:
				pass
			if not Utils.MessageOKCancel(self, 'File Exists.  Replace?', 'File Exists'):
				return
		except IOError:
			pass
		
		try:
			with open(fileName, 'wb') as fp:
				pass
		except Exception:
			Utils.MessageOK(self, 'Cannot open file "{}".'.format(fileName), 'Cannot Open File', iconMask=wx.ICON_ERROR )
			return
			
		self.fileName = fileName
		self.menuSave( event )
		
	def menuFileHistory( self, event ):
		fileNum = event.GetId() - wx.ID_FILE1
		fileName = self.filehistory.GetHistoryFile(fileNum)
		self.filehistory.AddFileToHistory(fileName)  # move up the list
		self.openRace( fileName )
		
	def menuExit(self, event):
		if Model.model.changed:
			response = Utils.MessageYesNoCancel(self, 'You have Unsaved Changes.\nSave Before Closing?', 'Unsaved Changes')
			if response == wx.ID_CANCEL:
				return
			if response == wx.ID_OK:
				self.writeRace()
				
		self.onCloseWindow( event )
	
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
			Utils.MessageOK(self, _("Unable to open the clipboard."), _("Error"), wx.ICON_ERROR )

	def menuSetGraphic( self, event ):
		imgPath = self.getGraphicFName()
		dlg = SetGraphicDialog( self, graphic = imgPath )
		if dlg.ShowModal() == wx.ID_OK:
			imgPath = dlg.GetValue()
			self.config.Write( 'graphic', imgPath )
			self.config.Flush()
		dlg.Destroy()
	
	def getGraphicFName( self ):
		defaultFName = os.path.join(Utils.getImageFolder(), 'SprintMgr.png')
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
		fileType = fileType[1:].replace('jpg', 'jpeg')
		if fileType not in ('png', 'gif', 'jpeg'):
			return None
		try:
			with open(graphicFName, 'rb') as f:
				b64 = 'data:image/{};base64,{}'.format(fileType, base64.standard_b64encode(f.read().decode()))
				return b64
		except IOError:
			pass
		return None
		
	def menuHelpQuickStart( self, event ):
		showHelp( 'QuickStart.html' )
	
	def menuHelp( self, event ):
		showHelp( 'Main.html' )
	
	def onContextHelp( self, event ):
		showHelp( self.attrClassName[self.notebook.GetSelection()][2] + '.html' )
	
	def menuAbout( self, event ):
		# First we create and fill the info object
		info = wx.adv.AboutDialogInfo()
		info.Name = Version.AppVerName
		info.Version = ''
		info.Copyright = "(C) 2013"
		info.Description = wordwrap(
			"Manage a Track Sprint, Keirin, XCE or 4-Cross competition efficiently and easily.\n\n"
			"A brief list of features:\n"
			"   * Easy Seeding of qualifiers\n"
			"   * Automatic rider renumbering (for XCE and 4-Cross)\n"
			"   * Randomization for seeding unknown riders\n"
			"   * Always shows the available events at all rounds of the competition\n"
			"   * Run available events out-of-order if necessary\n"
			"   * Manages start positions\n"
			"   * Handles Restarts, Relegations, DQ, DNF and DNS\n"
			"   * Automatically promotes riders to the next event based on their results\n"
			"   * Shows results at all times\n"
			"   * Graphical summary shows riders progression through the chart\n"
			"",
			500, wx.ClientDC(self))
		info.WebSite = ("http://sites.google.com/site/crossmgrsoftware/", "CrossMgr Home Page")
		info.Developers = [
					"Edward Sitarski (edward.sitarski@gmail.com)",
					]

		licenseText = "User Beware!\n\n" \
			"This program is experimental, under development and may have bugs.\n" \
			"Feedback is sincerely appreciated.\n\n" \
			"Donations are also appreciated - see website for details.\n\n" \
			"CRITICALLY IMPORTANT MESSAGE!\n" \
			"This program is not warranted for any use whatsoever.\n" \
			"It may not produce correct results, it might lose your data.\n" \
			"The authors of this program assume no responsibility or liability for data loss or erroneous results produced by this program.\n\n" \
			"Use entirely at your own risk.\n" \
			"Do not come back and tell me that this program screwed up your event!\n" \
			"Computers fail, screw-ups happen.  Always use a paper manual backup."
		info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

		wx.adv.AboutBox(info)

	#--------------------------------------------------------------------------------------

	def getCurrentPage( self ):
		return self.pages[self.notebook.GetSelection()]
	
	def showPage( self, iPage ):
		try:
			self.writeRace()
		except Exception:
			self.commit()
		self.callPageRefresh( iPage )
		self.notebook.SetSelection( iPage )

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
		notebook = event.GetEventObject()
		self.callPageCommit( event.GetOldSelection() )
		self.callPageRefresh( event.GetSelection() )
		try:
			Utils.writeLog( 'page: {}\n'.format(notebook.GetPage(event.GetSelection()).__class__.__name__) )
		except IndexError:
			pass
		event.Skip()	# Required to properly repaint the screen.
		
		if event.GetSelection() == self.iQualifiersPage and (Model.model and Model.model.competition and Model.model.competition.isKeirin):
			wx.CallAfter( self.callPageRefresh, self.iSeedingPage )
			wx.CallAfter( notebook.SetSelection, self.iSeedingPage )

	def refreshAll( self ):
		self.refresh()
		iSelect = self.notebook.GetSelection()
		for i, p in enumerate(self.pages):
			if i != iSelect:
				self.callPageRefresh( i )
		self.setTitle()

# Set log file location.
dataDir = ''
redirectFileName = ''
			
def MainLoop():
	global dataDir
	global redirectFileName
	
	app = wx.App( False )
	app.SetAppName("SprintMgr")
	
	random.seed()

	parser = ArgumentParser( prog="SprintMgr", description='Sprint competitions with qualifications, eliminations and repechages' )
	parser.add_argument("-q", "--quiet", action="store_false", dest="verbose", default=True, help='hide splash screen')
	parser.add_argument("-r", "--regular", action="store_false", dest="fullScreen", default=True, help='regular size (not full screen)')
	parser.add_argument(dest="filename", default=None, nargs='?', help="CrossMgr race file, or Excel generated by RaceDB", metavar="RaceFile.cmn or .xls, .xlsx, .xlsm file")
	args = parser.parse_args()

	dataDir = Utils.getHomeDir()
	redirectFileName = os.path.join(dataDir, 'SprintMgr.log')
	
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
	
	Utils.writeLog( 'start: {}'.format(Version.AppVerName) )
	
	# Create some sample data.
	Model.model = SetDefaultData()
	
	# Configure the main window.
	sWidth, sHeight = wx.GetDisplaySize()
	mainWin = MainWin( None, title=Version.AppVerName, size=(int(sWidth*0.9),int(sHeight*0.9)) )
	if args.fullScreen:
		mainWin.Maximize( True )
		
	mainWin.refreshAll()
	mainWin.CenterOnScreen()
	mainWin.Show()

	# Set the upper left icon.
	icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'SprintMgr.ico'), wx.BITMAP_TYPE_ICO )
	mainWin.SetIcon( icon )

	# Set the taskbar icon.
	#tbicon = wx.TaskBarIcon()
	#tbicon.SetIcon( icon, "SprintMgr" )

	if args.verbose:
		ShowSplashScreen()
		ShowTipAtStartup()
	
	# Try to open a specified filename.
	fileName = args.filename
	
	# Try to load a race.
	if fileName:
		try:
			mainWin.openRace( fileName )
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
