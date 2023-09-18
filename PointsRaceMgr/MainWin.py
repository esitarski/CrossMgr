import wx
import wx.adv as adv
from wx.lib.wordwrap import wordwrap
import wx.lib.dialogs

import sys
from html import escape
import os
import io
import re
import datetime
import xlsxwriter
import webbrowser
import pickle
import subprocess
import traceback
from argparse import ArgumentParser

import Utils
from Utils import tag
import Model
import Version
from EventList import EventList
from Configure import Configure
from RankDetails import RankDetails
from RankSummary import RankSummary
from StartList import StartList
from Commentary import Commentary
from ToPrintout import ToPrintout, ToHtml, ToExcel
from ExportGrid import ExportGrid

from Version import AppVerName

def ShowSplashScreen():
	bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'TrackSprint.jpg'), wx.BITMAP_TYPE_JPEG )
	showSeconds = 2.5
	adv.SplashScreen(bitmap, adv.SPLASH_CENTRE_ON_SCREEN|adv.SPLASH_TIMEOUT, int(showSeconds*1000), None)

class MainWin( wx.Frame ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(200,200) ):
		super().__init__(parent, id, title, size=size)
		
		isMac = ('WXMAC' in wx.Platform)
		
		Model.newRace()
		
		self.SetBackgroundColour( wx.WHITE )
		
		# Add code to configure file history.
		self.filehistory = wx.FileHistory(8)		
		
		dataDir = Utils.getHomeDir()
		configFileName = os.path.join(dataDir, 'PointsRaceMgr.cfg')
		self.config = wx.Config(appName="PointsRaceMgr",
								vendorName="Edward.Sitarski@gmail.com",
								localFilename=configFileName
		)
		self.filehistory.Load(self.config)
		
		self.fileName = None
		self.inRefresh = False	# Flag to indicate we are doing a refresh.
		
		# Default print options.
		self.printData = wx.PrintData()
		self.printData.SetPaperId(wx.PAPER_LETTER)
		self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
		# self.printData.SetOrientation(wx.LANDSCAPE)
		
		self.splitter = splitter = wx.SplitterWindow( self )

		self.eventList = EventList( splitter )
		mainPanel = wx.Panel( splitter )
				
		self.configure = Configure( mainPanel )
		
		#---------------------------------------------------------------
		# Configure the notebook.
		#
		self.notebook = wx.Notebook(mainPanel)
		self.notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onPageChanging )
		
		# Add all the pages to the notebook.
		self.pages = []

		def addPage( page, name ):
			self.notebook.AddPage( page, name )
			self.pages.append( page )
			
		self.attrClassName = [
			[ 'rankDetails',	RankDetails,	'Detail', 
				{'labelClickCallback':self.onRankDetailsColSelect,'labelDClickCallback':self.onRankDetailsColDClick}
			],
			[ 'rankSummary',	RankSummary,	'Summary',	{} ],
			[ 'startList',		StartList,		'StartList',{} ],
			[ 'commentary',		Commentary,		'Commentary',{} ],
		]
		
		for i, (a, c, n, kw) in enumerate(self.attrClassName):
			kw.update( {'parent': self.notebook} )
			setattr( self, a, c(**kw) )
			addPage( getattr(self, a), n )
			
		vsPanel = wx.BoxSizer( wx.VERTICAL )
		vsPanel.Add( self.configure, 0, wx.EXPAND )
		vsPanel.Add( self.notebook, 1, wx.EXPAND )
		mainPanel.SetSizer( vsPanel )
		
		#---------------------------------------------------------------
		# Configure the main menu.
		
		self.menuBar = wx.MenuBar(wx.MB_DOCKABLE)

		#---------------------------------------------------------------
		self.fileMenu = wx.Menu()

		self.fileMenu.Append( wx.ID_NEW , "&New...", "Create a new race" )
		self.Bind(wx.EVT_MENU, self.menuNew, id=wx.ID_NEW )

		item = self.fileMenu.Append( wx.ID_ANY, "&New Next...", "Create a new race from the Current Race" )
		self.Bind(wx.EVT_MENU, self.menuNewNext, item )
		
		self.fileMenu.Append( wx.ID_OPEN , "&Open...", "Open a race" )
		self.Bind(wx.EVT_MENU, self.menuOpen, id=wx.ID_OPEN )

		self.fileMenu.Append( wx.ID_SAVE , "&Save\tCtrl+S", "Save the race" )
		self.Bind(wx.EVT_MENU, self.menuSave, id=wx.ID_SAVE )

		self.fileMenu.Append( wx.ID_SAVEAS , "Save &As...", "Save the race under a different name" )
		self.Bind(wx.EVT_MENU, self.menuSaveAs, id=wx.ID_SAVEAS )

		self.fileMenu.AppendSeparator()
		
		item = self.fileMenu.Append( wx.ID_ANY, "&Export to HTML...\tCtrl+H", "Export as an HTML Web Page" )
		self.Bind(wx.EVT_MENU, self.menuExportToHtml, item )

		item = self.fileMenu.Append( wx.ID_ANY, "&Export to Excel...\tCtrl+E", "Export as an Excel Spreadsheet" )
		self.Bind(wx.EVT_MENU, self.menuExportToExcel, item )

		self.fileMenu.AppendSeparator()
		
		recent = wx.Menu()
		self.fileMenu.AppendSubMenu( recent, "&Recent Files" )
		self.filehistory.UseMenu( recent )
		self.filehistory.AddFilesToMenu()
		
		self.fileMenu.AppendSeparator()

		self.fileMenu.Append( wx.ID_EXIT , "E&xit", "Exit PointsRaceMgr" )
		self.Bind(wx.EVT_MENU, self.menuExit, id=wx.ID_EXIT )
		
		self.Bind(wx.EVT_MENU_RANGE, self.menuFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9)
		
		self.menuBar.Append( self.fileMenu, "&File" )

		self.configureMenu = wx.Menu()
		
		item = self.configureMenu.Append( wx.ID_ANY, "&Points Race", "Configure Points Race" )
		self.Bind(wx.EVT_MENU, lambda e: self.configure.ConfigurePointsRace(), item )
		
		self.configureMenu.Append( wx.ID_ANY, "&Madison", "Configure Madison" )
		self.Bind(wx.EVT_MENU, lambda e: self.configure.ConfigureMadison(), item )
		
		self.configureMenu.AppendSeparator()
		
		item = self.configureMenu.Append( wx.ID_ANY, "&Tempo", "Configure UCI Tempo Points Race" )
		self.Bind(wx.EVT_MENU, lambda e: self.configure.ConfigureTempoRace(), item )

		item = self.configureMenu.Append( wx.ID_ANY, "&Tempo Top 2", "Configure Tempo Points Race Top 2" )
		self.Bind(wx.EVT_MENU, lambda e: self.configure.ConfigureTempoTop2Race(), item )

		self.configureMenu.AppendSeparator()
		
		item = self.configureMenu.Append( wx.ID_ANY, "&Snowball", "Configure Snowball Points Race" )
		self.Bind(wx.EVT_MENU, lambda e: self.configure.ConfigureSnowballRace(), item )
		
		self.configureMenu.AppendSeparator()
		
		item = self.configureMenu.Append( wx.ID_ANY, "&Criterium", "Configure Criterium Race" )
		self.Bind(wx.EVT_MENU, lambda e: self.configure.ConfigureCriteriumRace(), item )
		
		self.menuBar.Append( self.configureMenu, "&ConfigureRace" )
		#---------------------------------------------------------------
		self.helpMenu = wx.Menu()

		self.helpMenu.Append( wx.ID_HELP , "&Help...", "Help..." )
		self.Bind(wx.EVT_MENU, self.menuHelp, id=wx.ID_HELP )

		self.helpMenu.Append( wx.ID_ABOUT , "&About...", "About PointsRaceMgr..." )
		self.Bind(wx.EVT_MENU, self.menuAbout, id=wx.ID_ABOUT )

		self.menuBar.Append( self.helpMenu, "&Help" )

		self.SetMenuBar( self.menuBar )
		#---------------------------------------------------------------
		self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
		
		#---------------------------------------------------------------
		splitter.SetMinimumPaneSize( 100 )
		splitter.SplitVertically( self.eventList, mainPanel, 350 )
		#---------------------------------------------------------------

		self.vbs = wx.BoxSizer( wx.VERTICAL )
		self.vbs.Add( splitter, 1, wx.EXPAND )
		self.SetSizer( self.vbs )
		
		#---------------------------------------------------------------
		Utils.setMainWin( self )
		
		Model.newRace()
		self.configure.ConfigurePointsRace()
		Model.race.setChanged( False )
		
		self.notebook.SetSelection( 0 )
		self.refresh()
		wx.CallAfter( self.eventList.bibText.SetFocus )
	
	def callPageRefresh( self, i ):
		try:
			page = self.pages[i]
		except IndexError:
			return
		try:
			page.refresh()
		except Exception as e:
			traceback.print_exc()
			pass

	def setTitle( self ):
		race = Model.race
		if self.fileName:
			title = '{}: {}{} - {}'.format(race.category, '*' if race.isChanged() else '', self.fileName, Version.AppVerName)
		else:
			title = '{}: {}'.format( race.category, Version.AppVerName )
		self.SetTitle( title )
	
	def callPageCommit( self, i ):
		try:
			self.pages[i].commit()
			self.setTitle()
		except (IndexError, AttributeError) as e:
			pass
			
	def onRankDetailsColSelect( self, grid, col, edit=False ):
		race = Model.race
		label = grid.GetColLabelValue(col)
		labels = [label]
		if label == race.getSprintLabel(race.getNumSprints()):
			labels.append( 'Finish' )
		
		egrid = self.eventList.grid
		egrid.ClearSelection()
		for row in range(egrid.GetNumberRows()):
			v = egrid.GetCellValue(row, 0)
			if any(v.startswith(lab) for lab in labels):
				if edit:
					self.eventList.editRow( row )
					break
				else:
					egrid.SelectRow( row, True )
		
	def onRankDetailsColDClick( self, grid, col ):
		# Select the entry, but also open the edit window.
		self.onRankDetailsColSelect( grid, col, True )
		
	def onPageChanging( self, event ):
		notebook = event.GetEventObject()
		self.callPageCommit( event.GetOldSelection() )
		self.callPageRefresh( event.GetSelection() )
		try:
			Utils.writeLog( 'page: {}\n'.format(notebook.GetPage(event.GetSelection()).__class__.__name__) )
		except IndexError:
			pass
		event.Skip()	# Required to properly repaint the screen.

	def getDirName( self ):
		return Utils.getDirName()

	#-------------------------------------------------------------------

	def menuExportToHtml( self, event ):
		self.commit()
		self.refresh()
		if not self.fileName:
			if not Utils.MessageOKCancel( self, 'You must save first.\n\nSave now?', 'Save Now'):
				return
			if not self.menuSaveAs( event ):
				return

		htmlFName = os.path.splitext(self.fileName)[0] + '.html'
		
		race = Model.race

		try:
			with io.open( htmlFName, 'w', encoding='utf8' ) as html:
				def write( v ):
					html.write( '{}'.format(v) )
				
				with tag(html, 'html'):
					with tag(html, 'head'):
						with tag(html, 'title'):
							write( race.name.replace('\n', ' ') )
						with tag(html, 'meta', dict(charset="UTF-8")):
							pass
						with tag(html, 'meta', dict(name='author', content="Edward Sitarski")):
							pass
						with tag(html, 'meta', dict(name='copyright', content="Edward Sitarski, 2013-{}".format(datetime.datetime.now().strftime('%Y')))):
							pass
						with tag(html, 'meta', dict(name='generator', content="PointsRaceMgr")):
							pass
						with tag(html, 'style', dict(type="text/css")):
							write( '''
body{ font-family: sans-serif; }

h1{ font-size: 250%; }
h2{ font-size: 200%; }

#idRaceName {
	font-size: 200%;
	font-weight: bold;
}
#idImgHeader { box-shadow: 4px 4px 4px #888888; }
.smallfont { font-size: 80%; }
.bigfont { font-size: 120%; }
.hidden { display: none; }

table.results td.numeric { text-align: right; }
table.details td.numeric { text-align: right; }

table.results {
	font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
	border-collapse:collapse;
}
table.results td, table.results th {
	font-size:1em;
	padding:3px 7px 2px 7px;
	text-align: left;
}
table.results th {
	font-size:1.1em;
	text-align:left;
	padding-top:5px;
	padding-bottom:4px;
	background-color:#7FE57F;
	color:#000000;
	vertical-align:bottom;
}
table.results tr.odd {
	color:#000000;
	background-color:#EAF2D3;
}

table.details {
	font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
	border-collapse:collapse;
}
table.details td, table.details th {
	font-size:1em;
	padding:3px 7px 2px 7px;
	text-align: left;
}
table.details th {
	font-size:1.1em;
	text-align:left;
	padding-top:5px;
	padding-bottom:4px;
	background-color:#7FE57F;
	color:#000000;
	vertical-align:bottom;
}

table.details td.rightAlign, table.details th.rightAlign {
	text-align:right;
}

table.details td.leftAlign, table.details th.leftAlign {
	text-align:left;
}

table.details td.leftBorder { border-left: 1pt solid #CCC; }
table.details td.rightBorder { border-right: 1pt solid #CCC; }
table.details td.topBorder { border-top: 1pt solid #CCC; }
table.details td.bottomBorder { border-bottom: 1pt solid #CCC; }

.smallFont {
	font-size: 75%;
}

table.results td.leftBorder, table.results th.leftBorder
{
	border-left:1px solid #98bf21;
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

table.results td.rightAlign, table.results th.rightAlign {
	text-align:right;
}

table.results td.leftAlign, table.results th.leftAlign {
	text-align:left;
}

.topAlign {
	vertical-align:top;
}

table.results th.centerAlign, table.results td.centerAlign {
	text-align:center;
}

.ignored {
	color: #999;
	font-style: italic;
}

table.points tr.odd {
	color:#000000;
	background-color:#EAF2D3;
}

.rank {
	color: #999;
	font-style: italic;
}

.points-cell {
	text-align: right;
	padding:3px 7px 2px 7px;
}

hr { clear: both; }

@media print {
	.noprint { display: none; }
	.title { page-break-after: avoid; }
}
''')
					with tag(html, 'body'):
						with tag(html, 'h1'):
							write( '{}: {}'.format(escape(race.name), race.date.strftime('%Y-%m-%d')) )
							if race.communique:
								write( ': Communiqu\u00E9 {}'.format(escape(race.communique)) )
						with tag(html, 'h2'):
							write( 'Category: {}'.format(escape(race.category)) )
						
						d = race.courseLength*race.laps
						if d == int(d):
							d = '{:,d}'.format(int(d))
						else:
							d = '{:,.1f}'.format(float(d))
						
						with tag(html, 'h3'):
							s =  [
								'Laps: {}'.format(race.laps),
								'Sprint Every: {} laps'.format(race.sprintEvery),
								'Distance: {}{}'.format( d, ['m','km'][race.courseLengthUnit] ),
							]
							write( ',  '.join(s) )
						write( '<br/>' )
						write( '<hr/>' )
						write( '<br/>' )
						ToHtml( html )
						write( '<br/>' )
						write( 'Powered by ' )
						with tag(html, 'a', {
								'href':'http://sites.google.com/site/crossmgrsoftware/',
								'target':'_blank'
							} ):
							write( 'CrossMgr' )

		except Exception as e:
			traceback.print_exc()
			Utils.MessageOK(self,
						'Cannot write "{}"\n\n{}\n\nCheck if this file is open.\nIf so, close it, and try again.'.format(htmlFName,e),
						'HTML File Error', iconMask=wx.ICON_ERROR )
		
		try:
			webbrowser.open( htmlFName )
		except:
			pass
		#Utils.MessageOK(self, 'Excel file written to:\n\n   {}'.format(htmlFName), 'Excel Write', iconMask=wx.ICON_INFORMATION)

	def menuExportToExcel( self, event ):
		self.commit()
		self.refresh()
		if not self.fileName:
			if not Utils.MessageOKCancel( self, 'You must save first.\n\nSave now?', 'Save Now'):
				return
			if not self.menuSaveAs( event ):
				return

		xlFName = os.path.splitext(self.fileName)[0] + '.xlsx'
		
		if (
				os.path.exists( xlFName ) and not
				Utils.MessageOKCancel(
					self,
					'Export file exists:\n\n\t{}\n\nReplace?'.format(xlFName),
					'Excel Export', iconMask=wx.ICON_INFORMATION
				)
			):
			return
		
		wb = xlsxwriter.Workbook( xlFName )
		ToExcel( wb )

		try:
			wb.close()
			Utils.MessageOK(self,
						'Exported to:\n\n\t{}.'.format(xlFName),
						'Excel Export', iconMask=wx.ICON_INFORMATION )
		except Exception as e:
			traceback.print_exc()
			Utils.MessageOK(self,
						'Cannot write\n\n\t{}\n\n{}\n\nCheck if this spreadsheet is open.\nIf so, close it, and try again.'.format(xlFName,e),
						'Excel File Error', iconMask=wx.ICON_ERROR )

	#-------------------------------------------------------------------
	
	def onCloseWindow( self, event ):
		self.commit()
		self.refresh()
		race = Model.race
		if not self.fileName:
			ret = Utils.MessageYesNoCancel(self, 'Unsaved changes!\n\nSave to a file?', 'Missing filename')
			if ret == wx.ID_YES:
				if not self.menuSaveAs():
					event.StopPropagation()
					return
			elif ret == wx.ID_CANCEL:
				event.StopPropagation()
				return
		elif race.isChanged():
				ret = Utils.MessageYesNoCancel(self, 'Unsaved changes!\n\nSave changes before Exit?', 'Unsaved Changes')
				if ret == wx.ID_YES:
					self.writeRace()
				elif ret == wx.ID_CANCEL:
					event.StopPropagation()
					return
		wx.Exit()

	def writeRaceValidFileName( self ):
		race = Model.race
		if not race:
			return
		with io.open(self.fileName, 'wb') as f:
			race.setChanged( False )
			pickle.dump( race, f, 2 )
		self.updateRecentFiles()
		self.setTitle()
		
	def writeRace( self ):
		race = Model.race
		if not race:
			return
		if not self.fileName:
			if Utils.MessageOKCancel(self, 'WriteRace:\n\nMissing filename.\nSave to a file?', 'Missing filename'): 
				wx.CallAfter( self.menuSaveAs )
			return
			
		try:
			self.writeRaceValidFileName()
		except Exception as e:
			Utils.MessageOK( self, 'WriteRace:\n\n{}\n\nError writing to file.\n\nRace NOT saved.\n\nTry "File|Save As..." again.'.format(e), iconMask = wx.ICON_ERROR )

	def menuNew( self, event ):
		if Model.race.isChanged():
			ret = Utils.MessageYesNoCancel( self, 'NewRace:\n\nYou have unsaved changes.\n\nSave now?', 'Unsaved changes')
			if ret == wx.ID_YES:
				self.menuSave()
			elif ret == wx.ID_NO:
				pass
			elif ret == wx.ID_CANCEL:
				return
		self.fileName = ''
		Model.newRace()
		self.refresh()
	
	def menuNewNext( self, event ):
		if Model.race.isChanged():
			ret = Utils.MessageYesNoCancel( self, 'NewRace:\n\nYou have unsaved changes.\n\nSave now?', 'Unsaved changes')
			if ret == wx.ID_YES:
				self.menuSave()
			elif ret == wx.ID_NO:
				pass
			elif ret == wx.ID_CANCEL:
				return
		if self.fileName:
			self.fileName = os.path.splitext(self.fileName)[0]
			for i in range(1,100):
				s = '-{}'.format(i)
				if self.fileName.endswith(s):
					self.fileName[:-len(s)] + '-{}'.format(i+1)
					break
			else:
				self.fileName += '-1'
			self.fileName += '.tp5'
		else:
			self.fileName = ''
		Model.race.newNext()
		self.refresh()
	
	def updateRecentFiles( self ):
		self.filehistory.AddFileToHistory(self.fileName)
		self.filehistory.Save(self.config)
		self.config.Flush()

	def openRace( self, fileName ):
		if not fileName:
			return
		if Model.race.isChanged():
			ret = Utils.MessageYesNoCancel( self, 'OpenRace:\n\nYou have unsaved changes.\n\nSave now?', 'Unsaved changes')
			if ret == wx.ID_YES:
				self.menuSave()
			elif ret == wx.ID_NO:
				pass
			elif ret == wx.ID_CANCEL:
				return

		try:
			with io.open(fileName, 'rb') as fp:
				race = pickle.load( fp, fix_imports=True, encoding='latin1', errors='replace')
			# Check a few fields to confirm we have the right file.
			a = race.sprintEvery
			a = race.courseLengthUnit
			Model.race = race
			self.fileName = fileName
			self.updateRecentFiles()
			self.refresh()

		except IOError:
			Utils.MessageOK(self, 'Cannot open file "{}".'.format(fileName), 'Cannot Open File', iconMask=wx.ICON_ERROR )
		except AttributeError:
			Utils.MessageOK(self, 'Bad race file "{}".'.format(fileName), 'Cannot Open File', iconMask=wx.ICON_ERROR )

	def menuOpen( self, event ):
		dlg = wx.FileDialog( self, message="Choose a Race file",
							defaultFile = '',
							wildcard = 'PointsRaceMgr files (*.tp5)|*.tp5',
							style=wx.FD_OPEN | wx.FD_CHANGE_DIR )
		if dlg.ShowModal() == wx.ID_OK:
			self.openRace( dlg.GetPath() )
		dlg.Destroy()
		
	def menuSave( self, event = None ):
		self.commit()
		if not self.fileName:
			self.menuSaveAs( event )
		else:
			self.writeRace()
		
	def menuSaveAs( self, event = None ):
		race = Model.race
		if not race:
			return False
			
		self.commit()		
		dlg = wx.FileDialog( self, message="Save a Race File",
							defaultFile = '',
							wildcard = 'PointsRaceMgr files (*.tp5)|*.tp5',
							style=wx.FD_SAVE | wx.FD_CHANGE_DIR )
		while True:
			ret = dlg.ShowModal()
			if ret != wx.ID_OK:
				dlg.Destroy()
				return False
				
			fileName = os.path.splitext(dlg.GetPath())[0] + '.tp5'
			
			if os.path.exists(fileName):
				if Utils.MessageOKCancel( self, 'File Exists.\n\nOverwrite?', iconMask=wx.ICON_WARNING ):
					break
			else:
				break	
		
		dlg.Destroy()	
		self.fileName = fileName	
		try:
			self.writeRaceValidFileName()
			return True
		except:
			Utils.MessageOK( self, 'WriteRace:\n\nError writing to file.\n\nRace NOT saved.\n\nTry "File|Save As..." again.', iconMask = wx.ICON_ERROR )
			return False

	def menuFileHistory( self, event ):
		fileNum = event.GetId() - wx.ID_FILE1
		fileName = self.filehistory.GetHistoryFile(fileNum)
		self.filehistory.AddFileToHistory(fileName)  # move up the list
		self.openRace( fileName )
		
	def menuExit(self, event):
		self.onCloseWindow( event )
		
	def menuHelp(self, event):
		message = '{}'.format(
			"Manage a Points Race: Track or Criterium.\n\n"
			"Click on ConfigureRace menu and choose a standard Race Format "
			" (or customize your own format).\n"
			"Configure all other race information at the top.\n"
			"\n"
			"While the race is underway, enter Bibs at the top (space or comma separated).\n"
			"Then, hit the Event Type button that applies to those Bibs.  This can be a Sprint (default), +/- Laps, DNF, DNS or DSQ.\n"
			"\n"
			"Use keyboard shortcuts to avoid pressing a button (much faster).\n"
			"To use keyboard shorcuts, enter the bib numbers, then the following character(s) for the Event Type, then press Enter:\n"
			"(nothing): means Sprint\n"
			"+ : means + Lap\n"
			"- : means - Lap\n"
			"DNF : means DNF\n"
			"DNS : means DNS\n"
			"DSQ,DQ : means DSQ\n"
			"\n"
			"Upper/Lower case is unimportant.  For example, '10 11 13+' is the shortcut for '+ Lap'.  '14 15 18-' is shorcut for '- Lap'.\n"
			"'19 20 21dnf' is short cut for pressing 'DNF'\n"
			"\n"
			"Ties are entered with an equals sign (=) between bib numbers (eg. 10=20, 30 40) means 10, 20 tied for first, 30 in 3rd, 40 in 4th\n"
			"\n"
			"Edit events by clicking on them."
			"Delete unwanted events by right-clicking on the Event column in the list.\n"
			"Rearrange the sequence of Events by dragging-and-dropping rows from Column 1.\n"
			"\n"
			"\n"
			"During the race, you can enter Bibs on a Break, in a Chase, Off the Back (OTB) or in No Man's Land (NML).\n"
			"You can then update the changing status of those bibs later by Editing those entries.\n"
			"To do so, click on the Event, then change the Event Type from the dialog window.\n"
			"For example, say bibs 10, 20, 30 go OTB.  Then a few laps later, they both get lapped.\n"
			"To handle this, create an entry when 10, 20, 30 go OTB.  Then, when they get lapped, click on the OTB entry you entered previously,\n"
			"then click on '-Lap' in the dialog.\n"
			"You can edit the bib numbers before you record the '- Lap', for example, if 30 does not get caught, remove 30 before pressing '- Lap'\n"
			"in the dialog.\n"
			"\n"
			"Up-to-date results are always shown on the Details and Summary screens.\n"
			"Double-click the Sp column header to edit the results for that sprint.\n"
			"Click on the Sp column header to see the Event corresponding\nto that sprint.\n"
			"\n"
			"Use the 'Start List' screen to enter rider information (you can also import it from Excel).\n"
			"Use the 'Existing Points' column in the 'Start List' to initialize the points when scoring an Omnimum.\n"
			"\n"
			"It is possible to enter Race Events without using a mouse.\n"
			"Press Enter to trigger 'New Race Event', then enter the Bibs, then press Tab and Space to change the Event type,\nthen press Enter to save.\n"
			"\n"
			"If ranking by 'Points, then Finish Order' (eg. Points Race, Madison), riders are ranked by:\n"
			"  1.  Most Points\n"
			"  2.  If a tie, by Finish Order\n"
			"If ranking by 'Laps Completed, Points, Num Wins, then Finish Order' (eg. UCI Criterium with Points), riders are ranked by:\n"
			"  1.  Most Laps Completed (as specified by +/- Laps)\n"
			"  2.  If a tie, by Most Points\n"
			"  3.  If still a tie, by Most Sprint Wins\n"
			"  4.  If still a tie, by Finish Order\n\n"
			"If ranking by 'Laps Completed, Points, then Finish Order', riders are ranßked by:\n"
			"  1.  Most Laps Completed (as specified by +/- Laps)\n"
			"  2.  If a tie, by Most Points\n"
			"  3.  If still a tie, by Finish Order\n\n"
			"")
		dlg = wx.lib.dialogs.ScrolledMessageDialog(self, message, "PointsRaceMgr Help" )
		dlg.ShowModal()
		dlg.Destroy()

	def menuAbout( self, event ):
		self.commit()
		self.refresh()
		
		# First we create and fill the info object
		info = wx.AboutDialogInfo()
		info.Name = AppVerName
		info.Version = ''
		info.SetCopyright( "(C) 2011-{}".format( datetime.datetime.now().year ) )
		info.Description = wordwrap( (
			"Manage a Points Race: Track or Criterium.\n\n"
			"For details, see Help"
			""),
			600, wx.ClientDC(self))
		info.WebSite = ("http://sites.google.com/site/crossmgrsoftware", "CrossMgr home page")
		info.Developers = [
			"Edward Sitarski (edward.sitarski@gmail.com)",
		]

		licenseText = ( "User Beware!\n\n"
			"This program is experimental, under development and may have bugs.\n"
			"Feedback is sincerely appreciated.\n\n"
			"CRITICALLY IMPORTANT MESSAGE:\n"
			"This program is not warrented for any use whatsoever.\n"
			"It may not produce correct results, it might lose your data.\n"
			"The authors of this program assume no reponsibility or liability for data loss or erronious results produced by this program.\n\n"
			"Use entirely at your own risk."
			"Always use a paper manual backup."
		)
		info.License = wordwrap(licenseText, 600, wx.ClientDC(self))

		wx.AboutBox(info)

	#-------------------------------------------------------------------
	def commit( self ):
		self.configure.commit()
		self.eventList.commit()
		self.setTitle()
	
	def refreshCurrentPage( self ):
		self.callPageRefresh( self.notebook.GetSelection() )

	def refresh( self, includeConfigure=True ):
		self.setTitle()
		if includeConfigure:
			self.configure.refresh()
		self.eventList.refresh()
		self.refreshCurrentPage()

def MainLoop():
	parser = ArgumentParser( prog="PointsRaceMgr", description='Software for Points Races and Criteriums' )
	parser.add_argument("-q", "--quiet", action="store_false", dest="verbose", default=True, help='hide splash screen')
	parser.add_argument("-r", "--regular", action="store_true", dest="regular", default=False, help='regular size')
	parser.add_argument(dest="filename", default=None, nargs='?', help="PointsRaceMgr race file", metavar="RaceFile.tp5")
	args = parser.parse_args()

	app = wx.App( False )
	
	dataDir = Utils.getHomeDir()
	os.chdir( dataDir )
	redirectFileName = os.path.join(dataDir, 'PointsRaceMgr.log')
	
	'''
	def my_handler( type, value, traceback ):
		print 'my_handler'
		print type, value, trackback
	sys.excepthook = my_handler
	'''
	
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
	
	Model.newRace()
	Model.race._populate()
	
	mainWin = MainWin( None, title=AppVerName, size=(800,600) )
	if not args.regular:
		mainWin.Maximize( True )
	mainWin.Show()

	# Set the upper left icon.
	try:
		icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'PointsRaceMgr16x16.ico'), wx.BITMAP_TYPE_ICO )
		mainWin.SetIcon( icon )
	except:
		pass

	if args.verbose:
		ShowSplashScreen()
	
	# Try a specified filename.
	fileName = args.filename
	
	# Try to load a race.
	if fileName:
		try:
			mainWin.openRace( fileName )
		except (IndexError, AttributeError, ValueError) as e:
			print( e )
			pass

	# Start processing events.
	app.MainLoop()

if __name__ == '__main__':
	MainLoop()
	
