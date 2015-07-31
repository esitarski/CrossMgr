import wx
import os
import sys
import math
import getpass
import Utils
Utils.initTranslation()
from  ExportGrid import ExportGrid
import Primes
from DNSManager import AutoWidthListCtrl
from GetResults import GetResults, UnstartedRaceWrapper
import Model
from pdf import PDF
from ReadSignOnSheet import SyncExcelLink
import Version

def getCatCountImagesCategoryList( parent ):
	il = wx.ImageList(16, 16)
	sm_rt = il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallRightArrow.png'), wx.BITMAP_TYPE_PNG))
	sm_up = il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallUpArrow.png'), wx.BITMAP_TYPE_PNG))
	sm_dn = il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallDownArrow.png'), wx.BITMAP_TYPE_PNG ))
	
	list = AutoWidthListCtrl( parent, style = wx.LC_REPORT 
									 | wx.BORDER_SUNKEN
									 | wx.LC_HRULES
	)
	list.SetImageList(il, wx.IMAGE_LIST_SMALL)
	
	list.InsertColumn(0, _("Name"))
	list.InsertColumn(1, _("Gender"))
	list.InsertColumn(2, _("Type"))
	list.InsertColumn(3, _("Count"), wx.LIST_FORMAT_RIGHT)
	list.InsertColumn(4, '' )
	
	catCount = {}
	race = Model.race
	if race:
		with UnstartedRaceWrapper():
			SyncExcelLink( race )
			for c in race.getCategories(False):
				catCount[c] = race.catCount( c )
				if catCount[c] == 0:
					continue
				index = list.InsertStringItem(sys.maxint, c.name, sm_rt)
				list.SetStringItem( index, 1, getattr(c, 'gender', 'Open') )
				list.SetStringItem( index, 2, [_('Start Wave'), _('Component'), _('Custom')][c.catType] )
				list.SetStringItem( index, 3, u'{}'.format(catCount[c]) )
	
	for col in xrange(4+1):
		list.SetColumnWidth( 0, wx.LIST_AUTOSIZE )
	list.SetColumnWidth( 1, 64 )
	list.SetColumnWidth( 3, 52 )
	
	return catCount, il, list

#----------------------------------------------------------------------

class ChoosePrintCategoriesDialog( wx.Dialog ):
	def __init__( self, parent, title=_("Print Categories"), id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, title,
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		title = wx.StaticText( self, label = _('Click to select Categories.  Use Ctrl-Click to select Multiple Categories.') )
		
		self.selectAllButton = wx.Button( self, label = _('Select All') )
		self.selectAllButton.Bind( wx.EVT_BUTTON, self.onSelectAll )
		
		self.catCount, self.il, self.list = getCatCountImagesCategoryList( self )
		
		self.includeLapTimesInPrintoutCheckBox = wx.CheckBox( self, label = _('Include Lap Times in Printout') )
		self.includePrimesInPrintoutCheckBox = wx.CheckBox( self, label = _('Include Primes in Printout') )
		
		race = Model.race
		if race:
			self.includeLapTimesInPrintoutCheckBox.SetValue( getattr(race, 'includeLapTimesInPrintout', True) )
			self.includePrimesInPrintoutCheckBox.Show( bool(getattr(race, 'primes', None)) )
			self.includePrimesInPrintoutCheckBox.SetValue( getattr(race, 'includePrimesInPrintout', True) )
		else:
			self.includeLapTimesInPrintoutCheckBox.SetValue( True )
			self.includePrimesInPrintoutCheckBox.SetValue( True )
			
		self.printFormatRadioBox = wx.RadioBox(
				self, wx.ID_ANY, 'Format', wx.DefaultPosition, wx.DefaultSize,
				[_('Fit Entire Category on One Page'), _('Small Text (max 60 riders per page)'), _('Big Text (max 30 riders per page)')],
				1, wx.RA_SPECIFY_COLS )
		if race:
			self.printFormatRadioBox.SetSelection( getattr(race, 'printFormat', 0) )
		else:
			self.printFormatRadioBox.SetSelection( 0 )
		self.printFormatRadioBox.Bind( wx.EVT_RADIOBOX, self.onPrintFormat )

		self.okButton = wx.Button( self, wx.ID_OK )
		self.okButton.Bind( wx.EVT_BUTTON, self.onOK )
		
		self.cancelButton = wx.Button( self, wx.ID_CANCEL )
		self.cancelButton.Bind( wx.EVT_BUTTON, self.onCancel )
		
		vs.Add( title, flag = wx.ALL, border = 4 )
		vs.Add( self.selectAllButton, flag = wx.ALL, border = 4 )
		vs.Add( self.list, 1, flag = wx.ALL|wx.EXPAND, border = 4 )
		
		vs.Add( self.includeLapTimesInPrintoutCheckBox, flag = wx.EXPAND|wx.ALL, border = 4 )
		vs.Add( self.includePrimesInPrintoutCheckBox, flag = wx.EXPAND|wx.ALL, border = 4 )
		vs.Add( self.printFormatRadioBox, flag = wx.EXPAND|wx.ALL, border = 4 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.okButton )
		hs.Add( self.cancelButton, flag = wx.LEFT, border = 16 )
		
		vs.Add( hs, flag = wx.ALL|wx.ALIGN_CENTER, border = 4 )
		self.SetSizer( vs )
		
		self.onSelectAll()
		self.categories = []

	def onPrintFormat( self, event ):
		race = Model.race
		if race:
			race.printFormat = event.GetInt()
		
	def onSelectAll(self, evt = None):
		for row in xrange(self.list.GetItemCount()):
			self.list.SetItemState(row, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
		wx.CallAfter( self.list.SetFocus )
		
	def onOK( self, event ):
		self.categories = []
		race = Model.race
		row = 0
		with UnstartedRaceWrapper():
			for c in race.getCategories(False):
				if self.catCount[c] == 0:
					continue
				if self.list.GetItemState(row, wx.LIST_STATE_SELECTED) == wx.LIST_STATE_SELECTED:
					self.categories.append( c )
				row += 1
		
		race.includeLapTimesInPrintout = self.includeLapTimesInPrintoutCheckBox.GetValue()
		race.includePrimesInPrintout = self.includePrimesInPrintoutCheckBox.GetValue()
		self.EndModal( wx.ID_OK )

	def onCancel( self, event ):
		self.categories = []
		self.EndModal( wx.ID_CANCEL )

#---------------------------------------------------------------------------------------------------------------------
class ChoosePrintCategoriesPodiumDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, _("Print Podium Positions"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		title = wx.StaticText( self, label = _('Click to select Categories.  Use Ctrl-Click to select Multiple Categories.') )
		
		self.selectAllButton = wx.Button( self, label=_('Select All') )
		self.selectAllButton.Bind( wx.EVT_BUTTON, self.onSelectAll )
		
		self.catCount, self.il, self.list = getCatCountImagesCategoryList( self )
		
		race = Model.race
			
		self.podiumPositionsLabel = wx.StaticText( self, label=_('Podium Positions to Print:') )
		self.podiumPositions = wx.Choice( self, choices=[unicode(i+1) for i in xrange(10)] )
		self.podiumPositions.SetSelection( 2 )
		
		self.includePrimesInPrintoutCheckBox = wx.CheckBox( self, label = _('Include Primes in Printout') )
		if race:
			self.includePrimesInPrintoutCheckBox.Show( bool(getattr(race, 'primes', None)) )
			self.includePrimesInPrintoutCheckBox.SetValue( getattr(race, 'includePrimesInPrintout', True) )
		else:
			self.includePrimesInPrintoutCheckBox.SetValue( True )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.podiumPositionsLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT, border=4 )
		hs.Add( self.podiumPositions )

		self.okButton = wx.Button( self, wx.ID_OK )
		self.okButton.Bind( wx.EVT_BUTTON, self.onOK )
		
		self.cancelButton = wx.Button( self, wx.ID_CANCEL )
		self.cancelButton.Bind( wx.EVT_BUTTON, self.onCancel )
		
		vs.Add( title, flag = wx.ALL, border = 4 )
		vs.Add( self.selectAllButton, flag = wx.ALL, border = 4 )
		vs.Add( self.list, 1, flag = wx.ALL|wx.EXPAND, border = 4 )
		
		vs.Add( hs, flag = wx.EXPAND|wx.ALL, border = 4 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.okButton )
		hs.Add( self.cancelButton, flag = wx.LEFT, border = 16 )
		
		vs.Add( hs, flag = wx.ALL|wx.ALIGN_CENTER, border = 4 )
		self.SetSizer( vs )
		
		self.onSelectAll()
		self.categories = []

	def onSelectAll(self, evt = None):
		for row in xrange(self.list.GetItemCount()):
			self.list.SetItemState(row, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
		wx.CallAfter( self.list.SetFocus )
		
	def onOK( self, event ):
		self.categories = []
		race = Model.race
		row = 0
		with UnstartedRaceWrapper():
			for c in race.getCategories(False):
				if self.catCount[c] == 0:
					continue
				if self.list.GetItemState(row, wx.LIST_STATE_SELECTED) == wx.LIST_STATE_SELECTED:
					self.categories.append( c )
				row += 1
		
		self.positions = self.podiumPositions.GetSelection() + 1
		race.includePrimesInPrintout = self.includePrimesInPrintoutCheckBox.GetValue()
		self.EndModal( wx.ID_OK )

	def onCancel( self, event ):
		self.categories = []
		self.EndModal( wx.ID_CANCEL )

#---------------------------------------------------------------------------------------------------------------------

def getRaceCategories():
	# Get all the categories available to print.
	with UnstartedRaceWrapper():
		with Model.LockRace() as race:
			if race is None:
				return []
			categories = [ (c.fullname, c) for c in race.getCategories(False) if race.hasCategory(c) ]
		categories.append( ('All', None) )
	return categories

#---------------------------------------------------------------------------------------------------------------------

class CrossMgrPrintout( wx.Printout ):
	def __init__(self, categories = None):
		wx.Printout.__init__(self)
		if not categories:
			with UnstartedRaceWrapper():
				self.categories = Model.race.getCategories(False)
		else:
			self.categories = categories
		self.pageInfo = {}

	def OnBeginDocument(self, start, end):
		return super(CrossMgrPrintout, self).OnBeginDocument(start, end)

	def OnEndDocument(self):
		super(CrossMgrPrintout, self).OnEndDocument()

	def OnBeginPrinting(self):
		super(CrossMgrPrintout, self).OnBeginPrinting()

	def OnEndPrinting(self):
		super(CrossMgrPrintout, self).OnEndPrinting()

	def OnPreparePrinting(self):
		super(CrossMgrPrintout, self).OnPreparePrinting()

	def HasPage(self, page):
		return page in self.pageInfo

	def GetPageInfo(self):
		self.pageInfo = {}
		numCategories = len(self.categories)
		if numCategories == 0:
			return (1,1,1,1)
			
		iPrintFormat = getattr( Model.race, 'printFormat', 0 ) if Model.race else 0
		if   iPrintFormat == 0:	# Fit Entire Category to One Page
			rowDrawCount = 1000000
		elif iPrintFormat == 1:	# Small Text (max 60 riders per page)
			rowDrawCount = 60
		else:					# Big Text (max 30 riders per page)
			rowDrawCount = 30
		
		# Compute a map by category and range for each page.
		page = 0
		with UnstartedRaceWrapper():
			for c in self.categories:
				categoryLength = len(GetResults(c))
				pageNumberTotal = int( math.ceil( float(categoryLength) / float(rowDrawCount) ) + 0.1 )
				pageNumber = 0
				for i in xrange(0, categoryLength, rowDrawCount):
					page += 1
					pageNumber += 1
					self.pageInfo[page] = [c, i, min(categoryLength, rowDrawCount), pageNumber, pageNumberTotal, categoryLength]
		race = Model.race
		if race and getattr(race, 'primes', None) and getattr(race, 'includePrimesInPrintout', True):
			page += 1
			pageNumber += 1
			self.pageInfo[page] = ['Primes', 0, len(race.primes), 1, 1, len(race.primes)]
		return (1, page, 1, page)

	def prepareGrid( self, page ):
		showLapTimes = (not Model.race) or getattr( Model.race, 'includeLapTimesInPrintout', True )
		with UnstartedRaceWrapper():
			if self.pageInfo[page][0] == 'Primes':
				exportGrid = ExportGrid( **Primes.GetGrid() )
			else:
				exportGrid = ExportGrid()
				exportGrid.setResultsOneList( self.pageInfo[page][0], True, showLapTimes=showLapTimes )
		return exportGrid
		
	def OnPrintPage(self, page):
		exportGrid = self.prepareGrid( page )
		exportGrid.drawToFitDC( *([self.GetDC()] + self.pageInfo[page][1:-1]) )
		return True

class CrossMgrPrintoutPNG( CrossMgrPrintout ):
	def __init__( self, dir, fileBase, orientation, categories = None ):
		CrossMgrPrintout.__init__(self, categories)
		self.dir = dir
		self.fileBase = fileBase
		self.orientation = orientation
		self.lastFName = None

	def OnPrintPage( self, page ):
		exportGrid = self.prepareGrid( page )
		
		pxPerInch = 148
		if self.orientation == wx.LANDSCAPE:
			bitmap = wx.EmptyBitmap( pxPerInch*11, int(pxPerInch*8.5) )
		else:
			bitmap = wx.EmptyBitmap( int(pxPerInch*8.5), pxPerInch*11 )
		dc = wx.MemoryDC()
		dc.SelectObject( bitmap )
		
		dc.SetBrush( wx.WHITE_BRUSH )
		dc.Clear()
		dc.SetBrush( wx.BLACK_BRUSH )
		exportGrid.drawToFitDC( *([dc] + self.pageInfo[page][1:-1]) )
		dc.SelectObject( wx.NullBitmap )
		image = bitmap.ConvertToImage()
		
		category = self.pageInfo[page][0]
		pageNumber = self.pageInfo[page][3]
		pageTotal = self.pageInfo[page][4]
		
		if pageTotal != 1:
			fname = u'{categoryName}-({pageNumber})-{fileBase}.png'.format(
				fileBase = self.fileBase,
				categoryName = category.fullname if category != 'Primes' else 'Primes',
				pageNumber = pageNumber
			)
		else:
			fname = u'{categoryName}-{fileBase}.png'.format(
				fileBase = self.fileBase,
				categoryName = category.fullname if category != 'Primes' else 'Primes'
			)
								
		fname = Utils.RemoveDisallowedFilenameChars( fname ).replace( ' ', '-' )
		
		if self.dir and not os.path.isdir( self.dir ):
			os.mkdir( self.dir )
		fname = os.path.join( self.dir, fname )
		
		self.lastFName = fname
			
		image.SaveFile( fname, wx.BITMAP_TYPE_PNG )
		return True

class CrossMgrPrintoutPDF( CrossMgrPrintout ):
	def __init__( self, dir, fileBase, orientation, categories = None, allInOne = False ):
		CrossMgrPrintout.__init__(self, categories)
		self.dir = dir
		self.fileBase = fileBase
		self.orientation = orientation
		self.allInOne = allInOne
		self.pdf = None
		self.lastFName = None
		
	def OnEndPrinting(self):
		if self.pdf and self.allInOne:
			if self.dir and not os.path.isdir( self.dir ):
				os.mkdir( self.dir )
			fname = u'{fileBase}-{all}.pdf'.format( fileBase=self.fileBase, all=_('All') )
			self.pdf.set_title( unicode(os.path.splitext(fname)[0].replace('-', ' ')).encode('iso-8859-1','ignore') )
			fname = os.path.join( self.dir, fname )
			self.pdf.output( fname, 'F' )
			self.lastFName = fname
			self.pdf = None
		super(CrossMgrPrintoutPDF, self).OnEndPrinting()

	def OnPrintPage( self, page ):
		exportGrid = self.prepareGrid( page )

		category = self.pageInfo[page][0]
		pageNumber = self.pageInfo[page][3]
		pageTotal = self.pageInfo[page][4]
		
		fname = u'{fileBase}-{categoryName}.pdf'.format(
			fileBase = self.fileBase,
			categoryName = category.fullname if category != 'Primes' else 'Primes'
		)
		fname = Utils.RemoveDisallowedFilenameChars( fname ).replace( ' ', '-' )
		
		if not self.pdf:
			self.pdf = PDF( orientation = 'L' if self.orientation == wx.LANDSCAPE else 'P' )
			self.pdf.set_font( 'Arial', '', 12 )
			self.pdf.set_author( unicode(getpass.getuser()).encode('iso-8859-1','ignore') )
			self.pdf.set_keywords( unicode('CrossMgr Results').encode('iso-8859-1','ignore') )
			self.pdf.set_creator( unicode(Version.AppVerName).encode('iso-8859-1','ignore') )
			self.pdf.set_title( unicode(os.path.splitext(fname)[0].replace('-', ' ')).encode('iso-8859-1','ignore') )
		
		exportGrid.drawToFitPDF( *([self.pdf, self.orientation] + self.pageInfo[page][1:-1]) )
		
		if not self.allInOne and pageNumber == pageTotal:
			if self.dir and not os.path.isdir( self.dir ):
				os.mkdir( self.dir )
			fname = os.path.join( self.dir, fname )
			self.pdf.output( fname, 'F' )
			self.lastFName = fname
			self.pdf = None
		
		return True

class CrossMgrPodiumPrintout( CrossMgrPrintout ):
	def __init__(self, categories = None, positions = 5):
		CrossMgrPrintout.__init__( self, categories )
		self.positions = positions

	def GetPageInfo(self):
		self.pageInfo = {}
		numCategories = len(self.categories)
		if numCategories == 0:
			return (1,1,1,1)
		
		rowDrawCount = self.positions
		
		# Compute a map by category and range for each page.
		Finisher = Model.Rider.Finisher
		page = 0
		with UnstartedRaceWrapper():
			for c in self.categories:
				categoryLength = min( sum(1 for r in GetResults(c) if r.status == Finisher), rowDrawCount )
				pageNumberTotal = 1
				pageNumber = 0
				for i in xrange(0, categoryLength, rowDrawCount):
					page += 1
					pageNumber += 1
					self.pageInfo[page] = [c, i, min(categoryLength, rowDrawCount), pageNumber, pageNumberTotal, categoryLength]
		
		return (1, page, 1, page)
	
	def prepareGrid( self, page ):
		exportGrid = ExportGrid()
		with UnstartedRaceWrapper():
			exportGrid.setResultsOneList( self.pageInfo[page][0], True, showLapTimes=False )
		exportGrid.title = u'\n'.join( [_('Podium Results'), u'', exportGrid.title] )
		return exportGrid
		
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,200))
	#cpcd = ChoosePrintCategoriesPodiumDialog(mainWin)
	cpcd = ChoosePrintCategoriesDialog(mainWin)
	cpcd.SetSize( (450, 600) )
	mainWin.Show()
	cpcd.ShowModal()
	for c in cpcd.categories:
		print c
	app.MainLoop()

