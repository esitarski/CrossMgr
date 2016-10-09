import wx
import wx.lib.mixins.listctrl as listmix
import os
import sys
import itertools

import Model
import Utils
from FixCategories import FixCategories
import HelpSearch
from Undo import undo

class AutoWidthListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID = wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

class DNSManager( wx.Panel, listmix.ColumnSorterMixin ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		
		self.category = None

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, label = _('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.selectAll = wx.Button( self, label = _('Select All'), style=wx.BU_EXACTFIT )
		self.Bind( wx.EVT_BUTTON, self.onSelectAll, self.selectAll )
		
		self.deSelectAll = wx.Button( self, label = _('Deselect All'), style=wx.BU_EXACTFIT )
		self.Bind( wx.EVT_BUTTON, self.onDeselectAll, self.deSelectAll )
		
		self.setDNS = wx.Button( self, label = _('DNS Selected'), style=wx.BU_EXACTFIT )
		self.Bind( wx.EVT_BUTTON, self.onSetDNS, self.setDNS )
		
		self.il = wx.ImageList(16, 16)
		self.sm_rt = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallRightArrow.png'), wx.BITMAP_TYPE_PNG))
		self.sm_up = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallUpArrow.png'), wx.BITMAP_TYPE_PNG))
		self.sm_dn = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallDownArrow.png'), wx.BITMAP_TYPE_PNG ))
		
		self.list = AutoWidthListCtrl( self, style = wx.LC_REPORT 
														 | wx.BORDER_NONE
														 | wx.LC_SORT_ASCENDING
														 | wx.LC_HRULES
														 )
		self.list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
				
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL, border=4 )
		self.hbs.AddSpacer( 32 )
		self.hbs.Add( self.selectAll, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.deSelectAll, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.AddSpacer( 32 )
		self.hbs.Add( self.setDNS, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )

		bs = wx.BoxSizer(wx.VERTICAL)
		
		bs.Add(self.hbs, 0, wx.EXPAND )
		bs.Add(wx.StaticText(self, label = u'  ' + _('Potential DNS Entrants (use Shift-Click and Ctrl-Click to multi-select)')), 0, wx.ALL, 4 )
		bs.Add(self.list, 1, wx.EXPAND|wx.GROW|wx.ALL, 5 )
		
		self.SetSizer(bs)
		bs.SetSizeHints(self)
	
	def onSelectAll(self, evt):
		for row in xrange(self.list.GetItemCount()):
			self.list.SetItemState(row, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
		wx.CallAfter( self.list.SetFocus )
		
	def onDeselectAll( self, evt ):
		for row in xrange(self.list.GetItemCount()):
			self.list.SetItemState(row, 0, wx.LIST_STATE_SELECTED)
		wx.CallAfter( self.list.SetFocus )
		
	def onSetDNS( self, evt ):
		if not self.list.GetItemCount() or not Model.race:
			return
		
		nums = [int(self.list.GetItem(i, 0).GetText()) for i in Utils.GetListCtrlSelectedItems(self.list)]
		
		if not nums:
			Utils.MessageOK( self, _('No entrants selected to DNS'), _('No entrants selected to DNS') )
			return
		
		lines = []
		for i in xrange( 0, len(nums), 10 ):
			lines.append( ', '.join( '{}'.format(n) for n in itertools.islice( nums, i, min(i+10, len(nums)) ) ) )
		message = u'{}\n\n{}'.format(_('DNS the following entrants?'), u',\n'.join(lines))
			
		if not Utils.MessageOKCancel( self, message, _('DNS Entrants') ):
			return
		
		undo.pushState()
		DNS = Model.Rider.DNS
		with Model.LockRace() as race:
			for n in nums:
				if n > 0:
					race.getRider(n).status = DNS
			race.setChanged()
			race.resetAllCaches()
		
		wx.CallAfter( self.refresh )
		wx.CallAfter( Utils.refresh )
		wx.CallAfter( self.list.SetFocus )
		
	def doChooseCategory( self, event ):
		Model.setCategoryChoice( self.categoryChoice.GetSelection(), 'DNSManagerCategory' )
		self.refresh()

	def clearGrid( self ):
		self.list.ClearAll()
		
	def GetListCtrl( self ):
		return self.list
		
	def GetSortImages(self):
		return (self.sm_dn, self.sm_up)
		
	def refresh( self ):
		self.category = None
		self.clearGrid()
		
		potentialDNS = {}
		with Model.LockRace() as race:
			if not race:
				return
			self.category = FixCategories( self.categoryChoice, getattr(race, 'DNSManagerCategory', 0) )
			self.hbs.RecalcSizes()
			self.hbs.Layout()
			for si in self.hbs.GetChildren():
				if si.IsWindow():
					si.GetWindow().Refresh()
			
			try:
				externalFields = race.excelLink.getFields()
				externalInfo = race.excelLink.read()
			except:
				self.clearGrid()
				return
		
			for num, info in externalInfo.iteritems():
				if num <= 0 or (self.category and not race.inCategory(num, self.category)):
					continue
				rider = race.riders.get( num, None )
				if not rider:
					potentialDNS[num] = info
				else:
					# Also add riders marked as Finishers that have no times.
					if rider.status == rider.Finisher and not rider.times:
						potentialDNS[num] = info
			
		if not potentialDNS:
			return
		
		# Add the headers.
		GetTranslation = _
		for c, f in enumerate(externalFields):
			self.list.InsertColumn( c+1, GetTranslation(f), wx.LIST_FORMAT_RIGHT if f.startswith('Bib') else wx.LIST_FORMAT_LEFT )
		
		# Create the data.  Sort by Bib#
		data = [tuple( num if i == 0 else info.get(f, '') for i, f in enumerate(externalFields)) for num, info in potentialDNS.iteritems()]
		data.sort()
		
		# Populate the list.
		for row, d in enumerate(data):
			index = self.list.InsertImageStringItem(sys.maxint, u'{}'.format(d[0]), self.sm_rt)
			for i, v in enumerate(itertools.islice(d, 1, len(d))):
				self.list.SetStringItem( index, i+1, unicode(v) )
			self.list.SetItemData( row, d[0] )		# This key links to the sort fields used by ColumnSorterMixin
		
		# Set the sort fields and configure the sorter mixin.
		self.itemDataMap = dict( (d[0], d) for d in data )
		listmix.ColumnSorterMixin.__init__(self, len(externalFields))

		# Make all column widths autosize.
		for i, f in enumerate(externalFields):
			self.list.SetColumnWidth( i, wx.LIST_AUTOSIZE )
			
		# Fixup the Bib number, as autosize gets confused with the graphic.
		self.list.SetColumnWidth( 0, 64 )
		wx.CallAfter( self.list.SetFocus )

	def commit( self ):
		pass

class DNSManagerDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "DNS Manager",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		vs = wx.BoxSizer( wx.VERTICAL )
		
		self.dnsManager = DNSManager( self )
		self.dnsManager.SetMinSize( (700, 500) )
		
		vs.Add( self.dnsManager, 1, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		self.helpBtn = wx.Button( self, label = _('&Help') )
		self.Bind( wx.EVT_BUTTON, self.onHelp, self.helpBtn )
		
		self.closeBtn = wx.Button( self, label = _('&Close (Ctrl-Q)') )
		self.Bind( wx.EVT_BUTTON, self.onClose, self.closeBtn )
		self.Bind( wx.EVT_CLOSE, self.onClose )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.AddStretchSpacer()
		hs.Add( self.helpBtn, flag=wx.ALL|wx.ALIGN_RIGHT, border = 4 )
		hs.Add( self.closeBtn, flag=wx.ALL|wx.ALIGN_RIGHT, border = 4 )
		vs.Add( hs, flag=wx.EXPAND )
		
		self.SetSizerAndFit(vs)
		vs.Fit( self )
		
		# Add Ctrl-Q to close the dialog.
		self.Bind(wx.EVT_MENU, self.onClose, id=wx.ID_CLOSE)
		self.Bind(wx.EVT_MENU, self.onUndo, id=wx.ID_UNDO)
		self.Bind(wx.EVT_MENU, self.onRedo, id=wx.ID_REDO)
		accel_tbl = wx.AcceleratorTable([
			(wx.ACCEL_CTRL,  ord('Q'), wx.ID_CLOSE),
			(wx.ACCEL_CTRL,  ord('Z'), wx.ID_UNDO),
			(wx.ACCEL_CTRL,  ord('Y'), wx.ID_REDO),
			])
		self.SetAcceleratorTable(accel_tbl)
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )
		
		wx.CallAfter( self.dnsManager.refresh )

	def refresh( self ):
		self.dnsManager.refresh()
	
	def onUndo( self, event ):
		undo.doUndo()
		self.refresh()
		
	def onRedo( self, event ):
		undo.doRedo()
		self.refresh()
	
	def onHelp( self, event ):
		HelpSearch.showHelp( 'Menu-DataMgmt.html#add-dns-from-external-excel-data' )
		
	def onClose( self, event ):
		wx.CallAfter( Utils.refresh )
		self.dnsManager.commit()
		self.EndModal( wx.ID_OK )

		
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,600))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	
	from ReadSignOnSheet import ExcelLink, TagFields
	e = ExcelLink()
	e.fileName = r'Wyoming\chips and bibs for Wyoming August 26 2012.xls'
	e.sheetName = r'chips and bibs'
	e.fieldCol = {'Bib#':2, 'LastName':3, 'FirstName':4, 'Team':-1, 'License':-1, 'Category':-1}
	e.fieldCol.update( {tf:-1 for tf in TagFields} )
	e.read()
	Model.race.excelLink = e
	
	dnsManager = DNSManager(mainWin)
	dnsManager.refresh()
	mainWin.Show()
	app.MainLoop()
