import  wx
import os
import sys
from  ExportGrid import ExportGrid
from DNSManager import AutoWidthListCtrl
from collections import defaultdict
import Model
import Utils

#----------------------------------------------------------------------

class ChoosePrintCategoriesDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Print Categories",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		title = wx.StaticText( self, wx.ID_ANY, 'Click and Ctrl-Click to Select Categories to Print:' )
		
		self.selectAllButton = wx.Button( self, wx.ID_ANY, 'Select All' )
		self.selectAllButton.Bind( wx.EVT_BUTTON, self.onSelectAll )
		
		self.il = wx.ImageList(16, 16)
		self.sm_rt = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallRightArrow.png'), wx.BITMAP_TYPE_PNG))
		self.sm_up = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallUpArrow.png'), wx.BITMAP_TYPE_PNG))
		self.sm_dn = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallDownArrow.png'), wx.BITMAP_TYPE_PNG ))
		
		self.list = AutoWidthListCtrl( self, wx.ID_ANY, style = wx.LC_REPORT 
														 | wx.BORDER_SUNKEN
														 | wx.LC_HRULES
														 )
		self.list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		self.list.InsertColumn(0, "Name")
		self.list.InsertColumn(1, "Gender")
		self.list.InsertColumn(2, "Count", wx.LIST_FORMAT_RIGHT)
		self.list.InsertColumn(3, '' )
		race = Model.race
		if race:
			catCount = defaultdict( int )
			for r in race.riders.itervalues():
				catCount[race.getCategory(r.num)] += 1
			for c in race.getCategories():
				if catCount[c] == 0:
					continue
				index = self.list.InsertStringItem(sys.maxint, c.name, self.sm_rt)
				self.list.SetStringItem( index, 1, getattr(c, 'gender', 'Open') )
				self.list.SetStringItem( index, 2, str(catCount[c]) )
			
		self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(3, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth( 1, 64 )
		self.list.SetColumnWidth( 2, 42 )

		self.okButton = wx.Button( self, wx.ID_OK )
		self.okButton.Bind( wx.EVT_BUTTON, self.onOK )
		
		self.cancelButton = wx.Button( self, wx.ID_CANCEL )
		self.cancelButton.Bind( wx.EVT_BUTTON, self.onCancel )
		
		vs.Add( title, flag = wx.ALL, border = 4 )
		vs.Add( self.selectAllButton, flag = wx.ALL|wx.ALIGN_RIGHT, border = 4 )
		vs.Add( self.list, 1, flag = wx.ALL|wx.EXPAND, border = 4 )
		
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
		for row, c in enumerate(race.getCategories()):
			if self.list.GetItemState(row, wx.LIST_STATE_SELECTED) == wx.LIST_STATE_SELECTED:
				self.categories.append( c )
		self.EndModal( wx.ID_OK )

	def onCancel( self, event ):
		self.categories = []
		self.EndModal( wx.ID_CANCEL )
		
def getRaceCategories():
	# Get all the categories available to print.
	with Model.LockRace() as race:
		if race is None:
			return []
		categories = [ (c.fullname, c) for c in race.getCategories() if race.hasCategory(c) ]
	categories.append( ('All', None) )
	return categories

class CrossMgrPrintout(wx.Printout):
    def __init__(self, categories = None):
		wx.Printout.__init__(self)
		if not categories:
			self.categories = Model.race.getCategories()
		else:
			self.categories = categories

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
		if page - 1 < len(self.categories):
			return True
		return False

    def GetPageInfo(self):
		numCategories = len(self.categories)
		if numCategories == 0:
			return (1,1,1,1)
		return (1, numCategories, 1, numCategories)

    def OnPrintPage(self, page):
		category = self.categories[page-1]
		
		exportGrid = ExportGrid()
		exportGrid.setResultsOneList( category, True )

		dc = self.GetDC()
		
		exportGrid.drawToFitDC( dc )
		return True

if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,200))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	cpcd = ChoosePrintCategoriesDialog(mainWin)
	cpcd.SetSize( (450, 300) )
	mainWin.Show()
	cpcd.ShowModal()
	for c in cpcd.categories:
		print c
	app.MainLoop()

