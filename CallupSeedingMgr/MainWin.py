import wx
import wx.adv
from wx.lib.wordwrap import wordwrap
import wx.lib.filebrowsebutton as filebrowse
import sys
import os
import re
import datetime
import traceback
import webbrowser
from optparse import OptionParser
from roundbutton import RoundButton

import Utils
from ReorderableGrid import ReorderableGrid
import Model
import Version
from GetCallups import GetCallups, make_title
from CallupResultsToGrid import CallupResultsToGrid
from CallupResultsToExcel import CallupResultsToExcel
from MakeExampleExcel import MakeExampleExcel

from Version import AppVerName

def ShowSplashScreen():
	bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'CallupSeedingMgr.png'), wx.BITMAP_TYPE_PNG )
	showSeconds = 2.5
	frame = wx.adv.SplashScreen(bitmap, wx.adv.SPLASH_CENTRE_ON_SCREEN|wx.adv.SPLASH_TIMEOUT, int(showSeconds*1000), None)
	
class ErrorDialog( wx.Dialog ):
	def __init__( self, parent, errors, id=wx.ID_ANY, title='Errors', size=(800,600) ):
		wx.Dialog.__init__( self, parent, id, title, size=size, style=wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX )
		bs = wx.BoxSizer( wx.VERTICAL )
		self.text = wx.TextCtrl( self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP )
		self.text.SetValue( '\n'.join( '{}'.format(e).replace( "u'", '' ).replace("'", '') for e in errors ) )
		bs.Add( self.text, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		self.okButton = wx.Button( self, id=wx.ID_OK )
		self.okButton.SetDefault()
		bs.Add( self.okButton, flag=wx.ALIGN_RIGHT|wx.ALL, border=4 )
		self.SetSizer( bs )

class MainWin( wx.Frame ):
	def __init__( self, parent, id=wx.ID_ANY, title='', size=(200,200) ):
		wx.Frame.__init__(self, parent, id, title, size=size)

		self.SetBackgroundColour( wx.Colour(240,240,240) )
		
		self.fname = None
		self.updated = False
		self.firstTime = True
		self.lastUpdateTime = None
		self.sources = []
		self.errors = []
		
		self.filehistory = wx.FileHistory(16)

		dataDir = Utils.getHomeDir()
		configFileName = os.path.join(dataDir, 'CallupSeedingMgr.cfg')
		self.config = wx.Config(appName="CallupSeedingMgr",
								vendorName="SmartCyclingSolutions",
								localFilename=configFileName
		)

		self.filehistory.Load(self.config)

		ID_MENU_UPDATE = wx.NewIdRef()
		ID_MENU_HELP = wx.NewIdRef()
		self.menuBar = wx.MenuBar(wx.MB_DOCKABLE)
		if 'WXMAC' in wx.Platform:
			self.appleMenu = self.menuBar.OSXGetAppleMenu()
			self.appleMenu.SetTitle("CallupSeedingMgr")

			self.appleMenu.Insert(0, wx.ID_ABOUT, "&About")

			self.Bind(wx.EVT_MENU, self.OnAboutBox, id=wx.ID_ABOUT)

			self.editMenu = wx.Menu()
			self.editMenu.Append(wx.MenuItem(self.editMenu, ID_MENU_UPDATE,"&Update"))

			self.Bind(wx.EVT_MENU, self.doUpdate, id=ID_MENU_UPDATE)
			self.menuBar.Append(self.editMenu, "&Edit")

			self.helpMenu = wx.Menu()
			self.helpMenu.Append(wx.MenuItem(self.helpMenu, ID_MENU_HELP, "&Help"))

			self.menuBar.Append(self.helpMenu, "&Help")
			self.Bind(wx.EVT_MENU, self.onTutorial, id=ID_MENU_HELP)

		else:
			self.fileMenu = wx.Menu()
			self.fileMenu.Append(wx.MenuItem(self.fileMenu, ID_MENU_UPDATE,"&Update"))
			self.fileMenu.Append(wx.ID_EXIT)
			self.Bind(wx.EVT_MENU, self.doUpdate, id=ID_MENU_UPDATE)
			self.Bind(wx.EVT_MENU, self.onClose, id=wx.ID_EXIT)
			self.menuBar.Append(self.fileMenu, "&File")
			self.helpMenu = wx.Menu()
			self.helpMenu.Insert(0, wx.ID_ABOUT, "&About")
			self.helpMenu.Insert(1, ID_MENU_HELP, "&Help")
			self.Bind(wx.EVT_MENU, self.OnAboutBox, id=wx.ID_ABOUT)
			self.Bind(wx.EVT_MENU, self.onTutorial, id=ID_MENU_HELP)
			self.menuBar.Append(self.helpMenu, "&Help")

		self.SetMenuBar(self.menuBar)

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
		
		#-------------------------------------------------------------------------------------------
		verticalControlSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.useUciIdCB = wx.CheckBox( self, label=_("Use UCI ID (assume no errors)") )
		self.useUciIdCB.SetValue( True )
		verticalControlSizer.Add( self.useUciIdCB, flag=wx.ALL, border=4 )

		self.useLicenseCB = wx.CheckBox( self, label=_("Use License (assume no errors)") )
		self.useLicenseCB.SetValue( True )
		verticalControlSizer.Add( self.useLicenseCB, flag=wx.ALL, border=4 )

		self.soundalikeCB = wx.CheckBox( self, label=_("Match misspelled names with Sound-Alike") )
		self.soundalikeCB.SetValue( True )
		verticalControlSizer.Add( self.soundalikeCB, flag=wx.ALL, border=4 )
		
		self.callupSeedingRB = wx.RadioBox(
			self,
			style=wx.RA_SPECIFY_COLS,
			majorDimension=1,
			label=_("Sequence"),
			choices=[
				_("Callups: Highest ranked FIRST (Cyclo-cross, MTB)"),
				_("Seeding: Highest ranked LAST (Time Trials)"),
			],
		)
		self.cycleLabel = wx.StaticText(self, label=_('Cycle Criteria'))
		self.cycle = wx.Choice( self, choices=(_('None'), _('Last 2'), _('Last 3'), _('Last 4')) )
		self.cycle.SetSelection( 0 )
		self.cycle.Bind( wx.EVT_CHOICE, lambda w: self.doUpdate() )
		cycleSizer = wx.BoxSizer( wx.HORIZONTAL )
		cycleSizer.Add( self.cycleLabel, flag=wx.ALIGN_CENTRE_VERTICAL )
		cycleSizer.Add( self.cycle, flag=wx.LEFT, border=2 )
		
		verticalControlSizer.Add( self.callupSeedingRB, flag=wx.EXPAND|wx.ALL, border=4 )
		verticalControlSizer.Add( cycleSizer, flag=wx.EXPAND|wx.ALL, border=4 )
		verticalControlSizer.Add( wx.StaticText(self, label=_('Riders with no criteria will be sequenced randomly.')), flag=wx.ALL, border=4 )
		
		horizontalControlSizer.Add( verticalControlSizer, flag=wx.EXPAND )
		
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
		branding = wx.adv.HyperlinkCtrl( self, id=wx.ID_ANY, label="Powered by CrossMgr", url=u"http://www.sites.google.com/site/crossmgrsoftware/" )
		vs.Add( branding, flag=wx.ALL, border=4 )
		horizontalControlSizer.Add( vs )

		inputBoxSizer.Add( horizontalControlSizer, flag=wx.EXPAND )
		
		self.sourceList = wx.ListCtrl( self, style=wx.LC_REPORT, size=(-1,100) )
		inputBoxSizer.Add( self.sourceList, flag=wx.ALL|wx.EXPAND, border=4 )
		self.sourceList.InsertColumn(0, "Sheet")
		self.sourceList.InsertColumn(1, "Data Columns and Derived Information")
		self.sourceList.InsertColumn(2, "Key Fields")
		self.sourceList.InsertColumn(3, "Rows", wx.LIST_FORMAT_RIGHT)
		self.sourceList.InsertColumn(4, "Errors/Warnings", wx.LIST_FORMAT_RIGHT)
		self.sourceList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected )
		
		instructions = [
			_('Drag-and-Drop the row numbers on the Left to change the sequence.'),
			_('Click on Points or Position cells for details.'),
			_('Orange Cells: Multiple Matches.  Click on the cell to see what you need to fix in the spreadsheet.'),
			_('Yellow Cells: Soundalike Matches.  Click on the cell to validate if the names are matched correctly.'),
		]
		
		self.grid = ReorderableGrid( self )
		self.grid.CreateGrid( 0, 1 )
		self.grid.SetColLabelValue( 0, '' )
		self.grid.EnableDragRowSize( False )
		self.grid.Bind( wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onGridCellClick )
		#self.grid.Bind( wx.EVT_MOTION, self.onMouseOver )
		
		outputBox = wx.StaticBox( self, label=_('Output') )
		outputBoxSizer = wx.StaticBoxSizer( outputBox, wx.VERTICAL )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.excludeUnrankedCB = wx.CheckBox( self, label=_("Exclude riders with no ranking info") )
		hs.Add( self.excludeUnrankedCB, flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL, border=4 )
		hs.AddSpacer( 24 )
		hs.Add( wx.StaticText(self, label=_("Output:") ), flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.topRiders = wx.Choice( self, choices=[_('All Riders'), _('Top 5'), _('Top 10'), _('Top 15'), _('Top 20'), _('Top 25')] )
		self.topRiders.SetSelection( 0 )
		hs.Add( self.topRiders, flag=wx.ALIGN_CENTRE_VERTICAL )
		
		self.saveAsExcel = wx.Button( self, label=_('Save as Excel...') )
		self.saveAsExcel.Bind( wx.EVT_BUTTON, self.doSaveAsExcel )
		hs.AddSpacer( 48 )
		hs.Add( self.saveAsExcel, flag=wx.ALL, border=4 )
		
		outputBoxSizer.Add( hs )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		mainSizer.Add( inputBoxSizer, flag=wx.EXPAND|wx.ALL, border = 4 )
		for i, instruction in enumerate(instructions):
			flag = wx.LEFT|wx.RIGHT
			if i == len(instructions)-1:
				flag |= wx.BOTTOM
			mainSizer.Add( wx.StaticText(self, label=instruction), flag=flag, border=8 )
		mainSizer.Add( self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 4 )
		mainSizer.Add( outputBoxSizer, flag=wx.EXPAND|wx.ALL, border = 4 )

		self.SetSizer( mainSizer )

	def onClose( self, event ):
			wx.Exit()

 
	def OnAboutBox(self, e):
			description = """CallupSeedingMgr is an Seeding Manager for CrossMgr
	"""

			licence = """CallupSeedingMgr free software; you can redistribute 
	it and/or modify it under the terms of the GNU General Public License as 
	published by the Free Software Foundation; either version 2 of the License, 
	or (at your option) any later version.

	CallupSeedingMgr is distributed in the hope that it will be useful, 
	but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
	See the GNU General Public License for more details. You should have 
	received a copy of the GNU General Public License along with File Hunter; 
	if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
	Suite 330, Boston, MA  02111-1307  USA"""

			info = wx.adv.AboutDialogInfo()

			crossMgrPng = Utils.getImageFolder() + '/CallupSeedingMgr.png'
			info.SetIcon(wx.Icon(crossMgrPng, wx.BITMAP_TYPE_PNG))
			info.SetName('CallupSeedingMgr')
			info.SetVersion(AppVerName.split(' ')[1])
			info.SetDescription(description)
			info.SetCopyright('(C) 2020 Edward Sitarski')
			info.SetWebSite('http://www.sites.google.com/site/crossmgrsoftware/')
			info.SetLicence(licence)

			wx.adv.AboutBox(info, self)

	def onTutorial( self, event ):
		if not Utils.MessageOKCancel( self, "\n".join( [
					_("Launch the CallupSeedingMgr Tutorial."),
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
			self.fileBrowse.SetValue( fname_excel )
		except Exception as e:
			Utils.MessageOK( self, '{}\n\n{}\n\n{}'.format(
					'Problem creating Excel sheet.',
					e,
					_('If the Excel file is open, please close it and try again')
				)
			)
		self.doUpdate( event )
		Utils.LaunchApplication( [fname_excel, os.path.join(Utils.getHtmlDocFolder(), 'Tutorial.html')] )
	
	def onItemSelected(self, event):
		currentItem = event.GetIndex()
		errors = self.errors[(currentItem+len(self.errors)-1) % len(self.errors)]
		if not errors:
			return
		dialog = ErrorDialog( self, errors=errors )
		dialog.ShowModal()
		dialog.Destroy()
		event.Skip()

	def onMouseOver(self, event):
		'''
		Method to calculate where the mouse is pointing and
		then set the tooltip dynamically.
		'''

		# Use CalcUnscrolledPosition() to get the mouse position
		# within the
		# entire grid including what's offscreen
		x, y = self.grid_area.CalcUnscrolledPosition(event.GetX(),event.GetY())

		coords = self.grid_area.XYToCell(x, y)
		# you only need these if you need the value in the cell
		row = coords[0]
		col = coords[1]
		iRecord = int( self.grid.GetCellValue(row, self.grid.GetNumberCols()-1) )
		iSource = self.grid.GetNumberCols() - col
		try:
			v = self.callup_results[iRecord][-iSource+1]
		except IndexError:
			event.Skip()
			return
		
		try:
			status = v.get_status()
		except AttributeError:
			event.Skip()
			return
		
		if status == v.NoMatch:
			event.Skip()
			return
		
		message = '{}\n\n{}'.format(
			v.get_message(),
			_('Make changes in the Spreadsheet (if necessary), then press "Update" to refresh the screen.'),
		)
		event.GetEventObject().SetToolTipString(message)  
		event.Skip()
        
	def onGridCellClick( self, event ):
		row = event.GetRow()
		col = event.GetCol()
		iRecord = int( self.grid.GetCellValue(row, self.grid.GetNumberCols()-1) )
		iSource = self.grid.GetNumberCols() - col
		try:
			v = self.callup_results[iRecord][-iSource+1]
		except IndexError:
			return
		
		try:
			status = v.get_status()
		except AttributeError:
			return
		
		if status == v.NoMatch:
			return
		
		message = '{}\n\n{}'.format(
			v.get_message(),
			_('Make changes in the Spreadsheet (if necessary), then press "Update" to refresh the screen.'),
		)
		Utils.MessageOK( self, message, _('Soundalike Match') if status == v.SuccessSoundalike else
										_('Multiple Matches') if status == v.MultiMatch else
										_('Match Success') )
	
	def getTopRiders( self ):
		i = self.topRiders.GetSelection()
		return 5 * i if i > 0 else 999999
		
	def getIsCallup( self ):
		return self.callupSeedingRB.GetSelection() == 0
		
	def getIsSoundalike( self ):
		return self.soundalikeCB.GetValue()
	
	def getUseUciId( self ):
		return self.useUciIdCB.GetValue()
	
	def getUseLicense( self ):
		return self.useLicenseCB.GetValue()
	
	def getOutputExcelName( self ):
		fname = os.path.abspath( self.fname )
		dirname, basename = os.path.dirname( fname ), os.path.basename( fname )
		fname_base, fname_suffix = os.path.splitext( basename )
		dirchild = 'CallupsOutput' if self.getIsCallup() else 'SeedingOutput'
		try:
			os.makedirs( os.path.join(dirname, dirchild) )
		except Exception as e:
			pass
		fname_excel = os.path.join(
			dirname,
			dirchild,
			'{}{}{}'.format(fname_base, '_Callups' if self.getIsCallup() else '_Seeding', '.xlsx')
		)
		return fname_excel
	
	def doChangeCallback( self, event ):
		fname = event.GetString()
		if not fname:
			self.setUpdated( False )
			return
		if fname != self.fname:
			wx.CallAfter( self.doUpdate, fnameNew=fname )
		
	def setUpdated( self, updated=True ):
		self.updated = updated
		for w in [self.sourceList, self.grid, self.saveAsExcel]:
			w.Enable( updated )
		if not updated:
			self.sourceList.DeleteAllItems()
			Utils.DeleteAllGridRows( self.grid )
			
	def updateSourceList( self, sources=None, errors=None ):
		self.sourceList.DeleteAllItems()
		sources = (sources or self.sources)
		errors = (errors or self.errors)
		if not sources:
			return
			
		def insert_source_info( source, errors, add_value_field=True ):
			idx = self.sourceList.InsertItem( self.sourceList.GetItemCount(), source.sheet_name )
			fields = source.get_ordered_fields()
			if add_value_field and source.get_cmp_policy_name():
				fields = [source.get_cmp_policy_name()] + list(fields)
			self.sourceList.SetItem( idx, 1, ', '.join( make_title(f) for f in fields ) )
			match_fields = source.get_match_fields(sources[-1]) if source != sources[-1] else []
			self.sourceList.SetItem( idx, 2, ', '.join( make_title(f) for f in match_fields ) )
			self.sourceList.SetItem( idx, 3, '{}'.format(len(source.results)) )
			self.sourceList.SetItem( idx, 4, '{}'.format(len(errors)) )
		
		insert_source_info( sources[-1], errors[-1], False )
		for i, source in enumerate(sources[:-1]):
			insert_source_info( source, errors[i] )
		
		for col in range(3):
			self.sourceList.SetColumnWidth( col, wx.LIST_AUTOSIZE )
		self.sourceList.SetColumnWidth( 3, 52 )
		self.sourceList.Refresh()

	def callbackUpdate( self, message ):
		pass
	
	def getCycleLast( self ):
		selection = self.cycle.GetSelection()
		if selection == wx.NOT_FOUND:
			return None
		return selection + 1 if selection >= 1 else None
	
	def doUpdate( self, event=None, fnameNew=None ):
		try:
			self.fname = fnameNew or (event and event.GetString()) or self.fileBrowse.GetValue()
		except:
			self.fname = ''
		
		if not self.fname:
			Utils.MessageOK( self, _('Missing Excel file.  Please select an Excel file.'), _('Missing Excel File') )
			self.setUpdated( False )
			return
		
		if self.lastUpdateTime and (datetime.datetime.now() - self.lastUpdateTime).total_seconds() < 1.0:
			return
		
		try:
			with open(self.fname, 'rb') as f:
				pass
		except Exception as e:
			Utils.MessageOK( self, '{}:\n\n    {}\n\n{}'.format( _('Cannot Open Excel file'), self.fname, e), _('Cannot Open Excel File') )
			self.setUpdated( False )
			return
		
		self.filehistory.AddFileToHistory( self.fname )
		self.filehistory.Save( self.config )
		
		wait = wx.BusyCursor()
		labelSave, backgroundColourSave = self.updateButton.GetLabel(), self.updateButton.GetForegroundColour()
		
		try:
			self.registration_headers, self.callup_headers, self.callup_results, self.sources, self.errors = GetCallups(
				self.fname,
				soundalike = self.getIsSoundalike(),
				useUciId = self.getUseUciId(),
				useLicense = self.getUseLicense(),
				callbackfunc = self.updateSourceList,
				callbackupdate = self.callbackUpdate,
				cycleLast = self.getCycleLast(),
			)
		except Exception as e:
			traceback.print_exc()
			Utils.MessageOK( self, '{}:\n\n    {}\n\n{}'.format( _('Excel File Error'), self.fname, e), _('Excel File Error') )
			self.setUpdated( False )
			return
		
		self.setUpdated( True )
		
		self.updateSourceList()
		
		CallupResultsToGrid(
			self.grid,
			self.registration_headers, self.callup_headers, self.callup_results,
			is_callup=(self.callupSeedingRB.GetSelection() == 0),
			top_riders=self.getTopRiders(),
			exclude_unranked=self.excludeUnrankedCB.GetValue(),
		)
		self.GetSizer().Layout()
		self.lastUpdateTime = datetime.datetime.now()
	
	def doSaveAsExcel( self, event ):
		if self.grid.GetNumberRows() == 0:
			return
			
		fname_excel = self.getOutputExcelName()
		if os.path.isfile( fname_excel ):
			if not Utils.MessageOKCancel(
						self,
						'"{}"\n\n{}'.format(fname_excel, _('File exists.  Replace?')),
						_('Output Excel File Exists'),
					):
				return
		
		user_sequence = [int(self.grid.GetCellValue(row, self.grid.GetNumberCols()-1)) for row in range(self.grid.GetNumberRows())]
		user_callup_results = [self.callup_results[i] for i in user_sequence]
		
		try:
			CallupResultsToExcel(
				fname_excel,
				self.registration_headers, self.callup_headers, user_callup_results,
				is_callup=self.getIsCallup(),
				top_riders=self.getTopRiders(),
				exclude_unranked=self.excludeUnrankedCB.GetValue(),
			)
		except Exception as e:
			traceback.print_exc()
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
			
		webbrowser.open( fname_excel, new = 2, autoraise = True )

# Set log file location.
dataDir = ''
redirectFileName = ''
			
def MainLoop():
	global dataDir
	global redirectFileName
	
	app = wx.App( False )
	app.SetAppName("CallupSeedingMgr")
	
	parser = OptionParser( usage = "usage: %prog [options] [CallupSpreadsheet.xlsx]" )
	parser.add_option("-f", "--file", dest="filename", help="callup info file", metavar="CallupSpreadsheet.xlsx")
	parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help='hide splash screen')
	parser.add_option("-r", "--regular", action="store_true", dest="regular", default=False, help='regular size')
	(options, args) = parser.parse_args()

	# Try to open a specified filename.
	fileName = options.filename
	
	# If nothing, try a positional argument.
	if not fileName and args:
		fileName = args[0]
	
	dataDir = Utils.getHomeDir()
	redirectFileName = os.path.join(dataDir, 'CallupSeedingMgr.log')
	
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
	
	mainWin = MainWin( None, title=AppVerName, size=(800,600) )
	if not options.regular:
		mainWin.Maximize( True )

	# Set the upper left icon.
	try:
		icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'CallupSeedingMgr.ico'), wx.BITMAP_TYPE_ICO )
		mainWin.SetIcon( icon )
	except:
		pass

	mainWin.Show()
	if fileName:
		wx.CallAfter( mainWin.doUpdate, fnameNew=fileName )
	
	if options.verbose:
		ShowSplashScreen()
	
	# Start processing events.
	app.MainLoop()

if __name__ == '__main__':
	MainLoop()

