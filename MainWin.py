import wx
from wx.lib.wordwrap import wordwrap
import sys
import os
import re
import datetime
import random
import time
import copy
import bisect
import cPickle as pickle
from optparse import OptionParser

from ForecastHistory	import ForecastHistory
from NumKeypad			import NumKeypad
from Actions			import Actions
from Stats				import Stats
from Gantt				import Gantt
from History			import History
from RiderDetail		import RiderDetail
from Results			import Results
from Categories			import Categories
from Properties			import Properties, PropertiesDialog
from Recommendations	import Recommendations
import Utils
import Model
from setpriority import setpriority
from Printing			import CrossMgrPrintout, getRaceCategories
import xlwt
from ExportGrid			import ExportGrid
import SimulationLapTimes
from Version			import AppVerName
from ReadSignOnSheet	import GetExcelLink

try:
	import wx.lib.agw.advancedsplash as AS
	def ShowSplashScreen():
		#bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), '20081124_cyclocross02.jpg'), wx.BITMAP_TYPE_JPEG )
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'vintage_CX.jpg'), wx.BITMAP_TYPE_JPEG )
		estyle = AS.AS_TIMEOUT | AS.AS_CENTER_ON_PARENT
		shadow = wx.WHITE
		try:
			frame = AS.AdvancedSplash(Utils.getMainWin(), bitmap=bitmap, timeout=3000,
									  extrastyle=estyle, shadowcolour=shadow)
		except:
			try:
				frame = AS.AdvancedSplash(Utils.getMainWin(), bitmap=bitmap, timeout=3000,
										  shadowcolour=shadow)
			except:
				pass
								  
except ImportError:
	def ShowSplashScreen():
		pass

class MainWin( wx.Frame ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(200,200) ):
		wx.Frame.__init__(self, parent, id, title, size=size)

		Utils.setMainWin( self )

		# Add code to configure file history.
		self.filehistory = wx.FileHistory(8)
		self.config = wx.Config(appName="CrossMgr",
								vendorName="SmartCyclingSolutions",
								style=wx.CONFIG_USE_LOCAL_FILE)
		self.filehistory.Load(self.config)
		
		self.fileName = None
		self.numSelect = None

		# Setup the objects for the race clock.
		self.timer = wx.Timer( self, id=1000 )
		self.secondCount = 0
		self.Bind( wx.EVT_TIMER, self.updateRaceClock, self.timer )

		self.simulateTimer = None
		self.simulateSeen = set()

		# Default print options.
		self.printData = wx.PrintData()
		self.printData.SetPaperId(wx.PAPER_LETTER)
		self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)

		# Configure the main menu.
		self.menuBar = wx.MenuBar(wx.MB_DOCKABLE)

		#-----------------------------------------------------------------------
		self.fileMenu = wx.Menu()

		self.fileMenu.Append( wx.ID_NEW , "&New...", "Create a new race" )
		self.Bind(wx.EVT_MENU, self.menuNew, id=wx.ID_NEW )

		idCur = wx.NewId()
		self.fileMenu.Append( idCur , "New Nex&t...", "Create a new race starting from the current race" )
		self.Bind(wx.EVT_MENU, self.menuNewNext, id=idCur )

		self.fileMenu.AppendSeparator()
		self.fileMenu.Append( wx.ID_OPEN , "&Open...", "Open a race" )
		self.Bind(wx.EVT_MENU, self.menuOpen, id=wx.ID_OPEN )

		idCur = wx.NewId()
		self.fileMenu.Append( idCur , "Open N&ext...", "Open the next race starting from the current race" )
		self.Bind(wx.EVT_MENU, self.menuOpenNext, id=idCur )

		self.fileMenu.AppendSeparator()
		
		self.fileMenu.Append( wx.ID_PAGE_SETUP , "Page &Setup...", "Setup the print page" )
		self.Bind(wx.EVT_MENU, self.menuPageSetup, id=wx.ID_PAGE_SETUP )

		self.fileMenu.Append( wx.ID_PREVIEW , "P&review Results...", "Preview the results on screen" )
		self.Bind(wx.EVT_MENU, self.menuPrintPreview, id=wx.ID_PREVIEW )

		self.fileMenu.Append( wx.ID_PRINT , "&Print Results...", "Print the results to a printer" )
		self.Bind(wx.EVT_MENU, self.menuPrint, id=wx.ID_PRINT )

		self.fileMenu.AppendSeparator()

		idCur = wx.NewId()
		self.fileMenu.Append( idCur , "&Export Results to Excel...", "Export as an Excel Spreadsheet" )
		self.Bind(wx.EVT_MENU, self.menuExportToExcel, id=idCur )

		self.fileMenu.AppendSeparator()
		
		recent = wx.Menu()
		self.fileMenu.AppendMenu(wx.ID_ANY, "Recent Fil&es", recent)
		self.filehistory.UseMenu( recent )
		self.filehistory.AddFilesToMenu()
		
		self.fileMenu.AppendSeparator()

		self.fileMenu.Append( wx.ID_EXIT , "E&xit", "Exit CrossMan" )
		self.Bind(wx.EVT_MENU, self.menuExit, id=wx.ID_EXIT )
		
		self.Bind(wx.EVT_MENU_RANGE, self.menuFileHistory, id=wx.ID_FILE1, id2=wx.ID_FILE9)
		
		self.menuBar.Append( self.fileMenu, "&File" )

		#-----------------------------------------------------------------------
		self.dataMgmtMenu = wx.Menu()

		idCur = wx.NewId()
		self.dataMgmtMenu.Append( idCur , "&Link to External Excel Data...", "Link to information in an Excel spreadsheet" )
		self.Bind(wx.EVT_MENU, self.menuLinkExcel, id=idCur )
		
		self.dataMgmtMenu.AppendSeparator()

		idCur = wx.NewId()
		self.dataMgmtMenu.Append( idCur , "&Import Categories from File...", "Import Categories from File" )
		self.Bind(wx.EVT_MENU, self.menuImportCategories, id=idCur )

		idCur = wx.NewId()
		self.dataMgmtMenu.Append( idCur , "&Export Categories to File...", "Export Categories to File" )
		self.Bind(wx.EVT_MENU, self.menuExportCategories, id=idCur )

		self.menuBar.Append( self.dataMgmtMenu, "&DataMgmt" )

		#-----------------------------------------------------------------------
		self.demoMenu = wx.Menu()

		idCur = wx.NewId()
		self.demoMenu.Append( idCur , "&Simulate Race...", "Simulate a race" )
		self.Bind(wx.EVT_MENU, self.menuSimulate, id=idCur )

		self.menuBar.Append( self.demoMenu, "Dem&o" )

		#-----------------------------------------------------------------------
		self.helpMenu = wx.Menu()

		self.helpMenu.Append( wx.ID_ABOUT , "&About...", "About CrossMgr..." )
		self.Bind(wx.EVT_MENU, self.menuAbout, id=wx.ID_ABOUT )

		self.menuBar.Append( self.helpMenu, "&Help" )

		#-----------------------------------------------------------------------
		self.SetMenuBar( self.menuBar )

		# Configure the field of the display.

		# Forecast/History shown in left pane of scrolled window.
		sty = wx.BORDER_SUNKEN
		self.splitter = wx.SplitterWindow( self )
		self.forecastHistory = ForecastHistory( self.splitter, style=sty )

		# Other data shown in right pane.
		self.notebook		= wx.Notebook(	self.splitter, 1000, style=sty )
		self.notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanging )
		
		self.pages = []

		def addPage( page, name ):
			self.notebook.AddPage( page, name )
			self.pages.append( page )

		self.actions		= Actions(	self.notebook )
		addPage( self.actions,   'Actions' )

		self.record		= NumKeypad(	self.notebook )
		addPage( self.record, 	 'Record' )

		self.results		= Results(		self.notebook )
		addPage( self.results,   'Results' )

		self.history		= History(		self.notebook )
		addPage( self.history,   'History' )

		self.riderDetail	= RiderDetail(	self.notebook )
		addPage( self.riderDetail,'Rider Detail' )

		self.recommendations = Recommendations(	self.notebook )
		addPage( self.recommendations, 'Recommendations' )

		self.stats			= Stats(		self.notebook )
		addPage( self.stats,     'Stats' )

		self.categories		= Categories(	self.notebook )
		addPage( self.categories,'Categories' )

		self.gantt			= Gantt(		self.notebook )
		addPage( self.gantt,     'Chart' )

		self.properties		= Properties(	self.notebook )
		addPage( self.properties,'Properties' )

		self.splitter.SplitVertically( self.forecastHistory, self.notebook, 200 )

		#------------------------------------------------------------------------------
		self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

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

	def menuPrintPreview( self, event ):
		data = wx.PrintDialogData(self.printData)
		printout = CrossMgrPrintout()
		printout2 = CrossMgrPrintout()
		self.preview = wx.PrintPreview(printout, printout2, data)

		if not self.preview.Ok():
			return

		pfrm = wx.PreviewFrame(self.preview, self, "Print preview")

		pfrm.Initialize()
		pfrm.SetPosition(self.GetPosition())
		pfrm.SetSize(self.GetSize())
		pfrm.Show(True)

	def menuPrint( self, event ):
		pdd = wx.PrintDialogData(self.printData)
		pdd.SetAllPages( 1 )
		pdd.EnablePageNumbers( 0 )
		pdd.EnableHelp( 0 )
		
		printer = wx.Printer(pdd)
		printout = CrossMgrPrintout()

		if not printer.Print(self, printout, True):
			if printer.GetLastError() == wx.PRINTER_ERROR:
				Utils.MessageOK(self, "There was a printer problem.\nCheck your printer setup.", "Printer Error",iconMask=wx.ICON_ERROR)
		else:
			self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )
		printout.Destroy()

	def menuLinkExcel( self, event ):
		race = Model.getRace()
		if not race:
			Utils.MessageOK(self, "A race must be loaded first.", "Link ExcelSheet", iconMask=wx.ICON_ERROR)
			return
		gel = GetExcelLink( self, getattr(race, 'excelLink', None) )
		race.excelLink = gel.show()
		if not race.excelLink:
			del race.excelLink
		self.writeRace()
		
	#--------------------------------------------------------------------------------------------

	def menuExportToExcel( self, event ):
		if self.fileName is None or len(self.fileName) < 4:
			return

		xlFName = self.fileName[:-4] + '.xls'
		dlg = wx.DirDialog( self, 'Folder to write "%s"' % os.path.basename(xlFName),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(xlFName) )
		ret = dlg.ShowModal()
		dName = dlg.GetPath()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return

		xlFName = os.path.join( dName, os.path.basename(xlFName) )

		wb = xlwt.Workbook()
		for catName in getRaceCategories():
			sheetCur = wb.add_sheet( re.sub('[:\\/?*\[\]]', ' ', catName) )
			export = ExportGrid()
			export.setResultsOneListRiderTimes( catName )
			export.toExcelSheet( sheetCur )

		try:
			wb.save( xlFName )
		except IOError:
			Utils.MessageOK(self,
						'Cannot write "%s".\n\nCheck if this spreadsheet open.\nIf so, close it, and try again.' % xlFName,
						'Excel File Error', iconMask=wx.ICON_ERROR )

	#--------------------------------------------------------------------------------------------

	def onCloseWindow( self, event ):
		self.writeRace()

		try:
			self.timer.Stop()
			del self.timer
		except AttributeError:
			pass

		try:
			self.simulateTimer.Stop()
			del self.simulateTimer
		except AttributeError:
			pass
		sys.exit()

	def writeRace( self ):
		race = Model.race
		if race is not None:
			cache = race.popCache()
			pickle.dump( race, open(self.fileName, 'wb'), 2 )
			race.pushCache( cache )
			race.setChanged( False )

	def setActiveCategories( self ):
		race = Model.race
		if race is None:
			return
		race.setActiveCategories()

	def menuNew( self, event ):
		dlg = PropertiesDialog(self, -1, 'Configure Race', style=wx.DEFAULT_DIALOG_STYLE )
		ret = dlg.ShowModal()
		fileName = dlg.GetPath()
		categoriesFile = dlg.GetCategoriesFile()
		properties = dlg.properties

		if ret != wx.ID_OK:
			return
			
		# Check for existing file.
		if os.path.exists(fileName) and \
		   not Utils.MessageOKCancel(self, 'File "%s" already exists.  Overwrite?' % fileName, 'File Exists', iconMask = wx.ICON_QUESTION):
			return

		# Try to open the file.
		try:
			open( fileName, 'wb' )
		except IOError:
			Utils.MessageOK( self, 'Cannot open "%s".' % fileName, 'Cannot Open File', iconMask=wx.ICON_ERROR )
			return

		# Create a new race and initialize it with the properties.
		self.fileName = fileName
		Model.setRace( Model.Race() )
		properties.update()
		self.updateRecentFiles()

		race = Model.getRace()
		importedCategories = False
		if categoriesFile:
			try:
				fp = open( categoriesFile, 'r' )
				race.importCategories( fp )
				importedCategories = True
			except IOError:
				Utils.MessageOK( self, "Cannot open file:\n%s" % categoriesFile, "File Open Error", iconMask=wx.ICON_ERROR)
			except (ValueError, IndexError):
				Utils.MessageOK( self, "Bad file format:\n%s" % categoriesFile, "File Read Error", iconMask=wx.ICON_ERROR)

		# Create some defaults so the page is not blank.
		if not importedCategories:
			race.setCategories( [(True,
								'Category %d-%d'	% (max(1, i*100), (i+1)*100-1),
								'%d-%d'				% (max(1, i*100), (i+1)*100-1),
								'00:00',
								None) for i in xrange(8)] )

		self.writeRace()
		self.showPageName( 'Actions' )
		self.refresh()
	
	def menuNewNext( self, event ):
		race = Model.getRace()
		if race is None:
			self.menuNew( event )
			return

		# Save the categories to use them in the next race.
		categoriesSave = race.categories
		race = None

		dlg = PropertiesDialog(self, -1, 'Configure Race', style=wx.DEFAULT_DIALOG_STYLE )
		dlg.properties.refresh()
		dlg.properties.incNext()
		dlg.folder.SetValue(os.path.dirname(self.fileName))
		dlg.properties.updateFileName()
		ret = dlg.ShowModal()
		fileName = dlg.GetPath()
		categoriesFile = dlg.GetCategoriesFile()
		properties = dlg.properties

		# Check if user canceled.
		if ret != wx.ID_OK:
			return

		# Check for existing file.
		if os.path.exists(fileName) and \
		   not Utils.MessageOKCancel(self, 'File "%s" already exists.  Overwrite?' % fileName, 'File Exists'):
			return

		# Try to open the file.
		try:
			open( fileName, 'wb' )
		except IOError:
			Utils.MessageOK(self, 'Cannot open "%s".' % fileName, 'Cannot Open File', iconMask=wx.ICON_ERROR )
			return

		# Create a new race and initialize it with the properties.
		self.fileName = fileName
		Model.newRace()
		properties.update()
		self.updateRecentFiles()

		# Restore the previous categories.
		race = Model.getRace()
		importedCategories = False
		if categoriesFile:
			try:
				fp = open( categoriesFile, 'r' )
				race.importCategories( fp )
				importedCategories = True
			except IOError:
				Utils.MessageOK( self, "Cannot open file:\n%s" % categoriesFile, "File Open Error", iconMask=wx.ICON_ERROR)
			except (ValueError, IndexError):
				Utils.MessageOK( self, "Bad file format:\n%s" % categoriesFile, "File Read Error", iconMask=wx.ICON_ERROR)

		if not importedCategories:
			race.categories = categoriesSave

		self.setActiveCategories()
		self.writeRace()
		self.showPageName( 'Actions' )
		self.refresh()

	def updateRecentFiles( self ):
		self.filehistory.AddFileToHistory(self.fileName)
		self.filehistory.Save(self.config)
		self.config.Flush()

	def openRace( self, fileName ):
		if not fileName:
			return
		Model.resetCache()
		self.writeRace()

		try:
			race = pickle.load( open(fileName, 'rb') )
			self.fileName = fileName
			Model.setRace( race )
			
			self.updateRecentFiles()
			
			if race.isFinished():
				self.showPageName( 'Results' )
			self.refresh()

		except IOError:
			Utils.MessageOK(self, 'Cannot open file "%s".' % fileName, 'Cannot Open File', iconMask=wx.ICON_ERROR )

	def menuOpen( self, event ):
		dlg = wx.FileDialog( self, message="Choose a Race file",
							defaultFile = '',
							wildcard = 'CrossMan files (*.cmn)|*.cmn',
							style=wx.OPEN | wx.CHANGE_DIR )
		if dlg.ShowModal() == wx.ID_OK:
			self.openRace( dlg.GetPath() )
		dlg.Destroy()

	def menuFileHistory( self, event ):
		fileNum = event.GetId() - wx.ID_FILE1
		fileName = self.filehistory.GetHistoryFile(fileNum)
		self.filehistory.AddFileToHistory(fileName)  # move up the list
		self.openRace( fileName )
		
	def menuOpenNext( self, event ):
		race = Model.getRace()

		if race is None or not self.fileName:
			self.menuOpen( event )
			return

		if race is not None and race.isRunning():
			if not Utils.MessageOKCancel(self,	'The current race is still running.\nFinish it and continue?',
												'Current race running', iconMask = wx.ICON_QUESTION ):
				return
			race.finishRaceNow()
			self.writeRace()

		path, file = os.path.split( self.fileName )
		patRE = re.compile( '\-r[0-9]+\-' )
		try:
			pos = patRE.search(file).start()
			prefix = file[:pos+2] + str(race.raceNum+1)
			fileName = (f for f in os.listdir(path) if f.startswith(prefix)).next()
			fileName = os.path.join( path, fileName )
			self.openRace( fileName )
		except (AttributeError, IndexError, StopIteration):
			Utils.MessageOK(self, 'No next race.', 'No next race', iconMask=wx.ICON_ERROR )

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
			
			f = open( fname, 'w' )
			print >> f, 'raceMinutes =', self.raceMinutes
			print >> f, 'lapTimes =', self.lapTimes
		else:
			self.raceMinutes = SimulationLapTimes.raceMinutes
			self.lapTimes = copy.copy(SimulationLapTimes.lapTimes)
			
		return self.lapTimes
		
	def menuSimulate( self, event ):
		fName = os.path.join( Utils.getHomeDir(), 'Simulation.cmn' )
		if not Utils.MessageOKCancel(self,
'''
This will simulate a race using randomly generated data.
It is a good illustration of CrossMgr's functionality with realtime data.

The simulation takes about 10 minutes.

The race will be written to:
"%s".

Continue?''' % fName, 'Simulate a Race', iconMask = wx.ICON_QUESTION ):
			return

		try:
			open(fName, 'wb')
		except IOError:
			Utils.MessageOK(self, 'Cannot open file "%s".' % fName, 'File Open Error')
			return

		self.lapTimes = self.genTimes()
		tMin = self.lapTimes[0][0]
		self.lapTimes.reverse()			# Reverse the times so we can pop them from the stack later.

		# Set up a new file and model for the simulation.
		self.fileName = fName
		self.simulateSeen = set()
		Model.setRace( None )
		race = Model.newRace()
		race.name = 'Simulate'
		race.memo = ''
		race.minutes = self.raceMinutes
		race.raceNum = 1
		race.setCategories( [(True, 'Junior', '100-199', '00:00', None), (True, 'Senior','200-299', '00:15', None)] )
		self.writeRace()
		self.showPageName( 'History' )
		self.refresh()

		# Start the simulation.

		self.nextNum = None
		race.startRaceNow()
		# Backup all the events and race start so we don't have to wait for the first lap.
		#race.startTime -= datetime.timedelta( seconds = (tMin-1) )
		#self.lapTimes = [(t-tMin, n) for t, n in self.lapTimes]

		self.simulateTimer = wx.CallLater( 1, self.updateSimulation, True )
		self.updateRaceClock()
		self.refresh()

	def updateSimulation( self, num ):
		race = Model.getRace()
		if race is None:
			return
		if self.nextNum is not None and self.nextNum not in self.simulateSeen:
			if 	self.notebook.GetPageText(self.notebook.GetSelection()) == 'Record':
				self.record.numEdit.SetValue( self.nextNum )
				self.record.onEnterPress()
				self.record.refresh()
			else:
				self.forecastHistory.logNum( self.nextNum )
				self.record.refresh()
			if race.curRaceTime() > race.minutes * 60.0:
				self.simulateSeen.add( self.nextNum )

		try:
			t, self.nextNum = self.lapTimes.pop()
			if t < (self.raceMinutes*60.0 + race.getAverageLapTime()*1.5):
				self.simulateTimer.Restart( int(max(1,(t - race.curRaceTime()) * 1000)), True )
				return
		except IndexError:
			pass
			
		self.simulateTimer.Stop()
		self.nextNum = None
		race.finishRaceNow()
		race.resetCache()
		Utils.writeRace()
		self.refresh()

	def menuImportCategories( self, event ):
		self.commit()
		race = Model.getRace()
		if not race:
			Utils.MessageOK( self, "A race must be loaded first.", "Import Categories", iconMask=wx.ICON_ERROR)
			return
			
		dlg = wx.FileDialog( self, message="Choose Race Categories File",
							defaultDir=os.getcwd(), 
							defaultFile="",
							wildcard="Bicycle Race Categories (*.brc)|*.brc",
							style=wx.OPEN )
		if dlg.ShowModal() == wx.ID_OK:
			categoriesFile = dlg.GetPath()
			try:
				fp = open( categoriesFile, 'r' )
				race.importCategories( fp )
			except IOError:
				Utils.MessageOK( self, "Cannot open file:\n%s" % categoriesFile, "File Open Error", iconMask=wx.ICON_ERROR)
			except (ValueError, IndexError):
				Utils.MessageOK( self, "Bad file format:\n%s" % categoriesFile, "File Read Error", iconMask=wx.ICON_ERROR)
				
		dlg.Destroy()
	
	def menuExportCategories( self, event ):
		self.commit()
		race = Model.getRace()
		if not race:
			Utils.MessageOK( self, "A race must be loaded first.", "Import Categories", iconMask=wx.ICON_ERROR)
			return
			
		dlg = wx.FileDialog( self, message="Choose Race Categories File",
							defaultDir=os.getcwd(), 
							defaultFile="",
							wildcard="Bicycle Race Categories (*.brc)|*.brc",
							style=wx.SAVE )
							
		if dlg.ShowModal() == wx.ID_OK:
			fname = dlg.GetPath()
			try:
				fp = open( fname, 'w' )
				race.exportCategories( fp )
			except IOError:
				Utils.MessageOK( self, "Cannot open file:\n%s" % fname, "File Open Error", iconMask=wx.ICON_ERROR)
				
		dlg.Destroy()	
		
	def menuAbout( self, event ):
		# First we create and fill the info object
		info = wx.AboutDialogInfo()
		info.Name = AppVerName
		info.Version = ''
		info.Copyright = "(C) 2009-2010"
		info.Description = wordwrap(
			"CrossMgr: produce Cyclo-cross race results quickly and easily with no preparation.\n\n"
			"A brief list of features:\n"
			"   * Input riders on the first lap\n"
			"   * Predicts riders for all other laps based on their lap times\n"
			"   * Indicates race leader by category and tracks missing riders\n"
			"   * Interpolates missing numbers.  Ignores duplicate rider entries.\n"
			"   * Shows results instantly by category during and after race\n"
			"   * Shows rider history\n"
			"   * Allows rider lap adjustments\n"
			"   * UCI 80% Rule Countdown\n"
			"",
			350, wx.ClientDC(self))
		info.WebSite = ("http://en.wikipedia.org/wiki/Hello_world", "Hello World home page")
		info.Developers = [
					"Edward Sitarski (edward.sitarski@gmail.com)",
					"Andrew Paradowski (andrew.paradowski@gmail.com)"
					]

		licenseText = "User Beware!\n\n" \
			"This program is experimental, under development and may have bugs.\n" \
			"Feedback is sincerely appreciated.\n\n" \
			"CRITICALLY IMPORTANT MESSAGE:\n" \
			"This program is not warrented for any use whatsoever.\n" \
			"It may not produce correct results, it might lose your data.\n" \
			"The authors of this program assume no reponsibility or liability for data loss or erronious results produced by this program.\n\n" \
			"Use entirely at your own risk." \
			"Always use a paper manual backup."
		info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

		# Then we call wx.AboutBox giving it that info object
		wx.AboutBox(info)

	#--------------------------------------------------------------------------------------

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
		self.notebook.ChangeSelection( iPage )

	def showPageName( self, name ):
		for i, p in enumerate(self.pages):
			if self.notebook.GetPageText(i) == name:
				self.showPage( i )
				break

	def callPageRefresh( self, i ):
		if 0 <= i < len(self.pages):
			try:
				self.pages[i].refresh()
			except AttributeError:
				pass

	def callPageCommit( self, i ):
		if 0 <= i < len(self.pages):
			try:
				self.pages[i].commit()
			except AttributeError:
				pass

	def commit( self ):
		self.callPageCommit( self.notebook.GetSelection() )
				
	def refreshCurrentPage( self ):
		self.callPageRefresh( self.notebook.GetSelection() )

	def refresh( self ):
		self.refreshCurrentPage()
		self.forecastHistory.refresh()
		self.updateRaceClock()

	def onPageChanging( self, event ):
		self.callPageCommit( event.GetOldSelection() )
		self.callPageRefresh( event.GetSelection() )
		event.Skip()	# Required to properly repaint the screen.

	def refreshAll( self ):
		self.refresh()
		iSelect = self.notebook.GetSelection()
		for i, p in enumerate(self.pages):
			if i != iSelect:
				self.callPageRefresh( i )

	def setNumSelect( self, num ):
		num = int(num) if num is not None else None
		if num != self.numSelect:
			self.history.setNumSelect( num )
			self.results.setNumSelect( num )
			self.riderDetail.setNumSelect( num )
			self.numSelect = num

	#-------------------------------------------------------------

	def updateRaceClock( self, event = None ):
		self.record.refreshRaceTime()

		race = Model.getRace()
		if race is None:
			self.SetTitle( AppVerName )
			self.timer.Stop()
			return

		if race.isUnstarted():
			status = 'Unstarted'
		elif race.isRunning():
			status = 'Running'
		else:
			status = 'Finished'

		if not race.isRunning():
			self.SetTitle( '%s-r%d - %s - %s' % (race.name, race.raceNum, status, AppVerName) )
			self.timer.Stop()
			return

		self.SetTitle( '%s %s-r%d - %s - %s' % (Utils.formatTime(race.curRaceTime()), race.name, race.raceNum, status, AppVerName) )

		if self.timer is None or not self.timer.IsRunning():
			self.timer.Start( 1000 )
			self.secondCount = 0

		self.secondCount += 1
		if self.secondCount % 30 == 0 and race.isChanged():
			self.writeRace()

def MainLoop():
	setpriority( priority=4 )	# Set to real-time priority.

	parser = OptionParser( usage = "usage: %prog [options] [RaceFile.cmn]" )
	parser.add_option("-f", "--file", dest="filename", help="race file", metavar="RaceFile.cmn")
	parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help='hide splash screen')
	(options, args) = parser.parse_args()

	app = wx.PySimpleApp()
	mainWin = MainWin( None, title=AppVerName, size=(800,600) )
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
	
	# Try a specified filename.
	fileName = options.filename
	
	# If nothing, try a positional argument.
	if not fileName and args:
		fileName = args[0]
	
	# Try to load a race.
	if fileName:
		try:
			mainWin.openRace( fileName )
		except (IndexError, AttributeError, ValueError):
			pass

	# Start processing events.
	app.MainLoop()

if __name__ == '__main__':
	MainLoop()
