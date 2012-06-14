import Model
import Utils
import ReadSignOnSheet
import wx
import wx.grid		as gridlib
import ColGrid
import os
import re

class Search( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY, style = 0, size=(-1-1) ):
		wx.Panel.__init__(self, parent, id, style=style, size=size )

		self.sortCol = 0
		self.numSelect = None
		self.textColour = {}
		self.backgroundColour = {}
		self.lastRow = -1
		self.isEmpty = True
		
		self.vbs = wx.BoxSizer(wx.VERTICAL)
		
		hbs = wx.BoxSizer( wx.HORIZONTAL )
		
		self.searchLabel = wx.StaticText( self, wx.ID_ANY, 'Search:' )
		self.search = wx.SearchCtrl(self, style=wx.TE_PROCESS_ENTER )
		self.search.ShowCancelButton( True )
		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
		self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCloseSearch, self.search)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch, self.search)
		self.Bind(wx.EVT_TEXT, self.OnDoSearch, self.search)
		
		self.closeButton = wx.Button( self, wx.ID_CANCEL, 'Close' )
		self.Bind(wx.EVT_BUTTON, self.OnClose, self.closeButton )
		
		hbs.Add( self.searchLabel, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border = 4 )
		hbs.Add( self.search, 1, flag=wx.ALL|wx.EXPAND, border = 4 )
		hbs.Add( self.closeButton, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border = 4 )
		
		self.grid = ColGrid.ColGrid( self )
		self.grid.SetRightAlign( True )
		self.grid.SetRowLabelSize( 0 )
		self.grid.SetMargins( 0, 0 )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()
		self.grid.SetMinSize( (650, 120) )
		self.grid.SetDoubleBuffered( True )

		self.Bind( wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.doNumDrilldown )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doRightClick )
		self.grid.Bind( wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.doLabelClick )
		self.grid.GetGridWindow().Bind( wx.EVT_MOTION, self.doMouseMove )
		
		self.vbs.Add( hbs, proportion=0, flag=wx.EXPAND )
		self.vbs.Add( self.grid, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border = 4 )
		
		self.SetSizer(self.vbs)
		self.vbs.SetSizeHints(self)

	def OnClose( self, event ):
		if self.GetParent():
			self.GetParent().Show( False )
		
	def OnSearch( self, event ):
		self.OnDoSearch()
		
	def OnCloseSearch( self, event ):
		self.search.SetValue( '' )
		
	def OnDoSearch( self, event = None ):
		self.refresh()

	def doMouseMove( self, event ):
		if self.isEmpty:
			return
		
		pos = self.grid.CalcUnscrolledPosition( wx.Point(event.GetX(), event.GetY()) )
		row = self.grid.YToRow(pos.y)
		if not (0 <= row < self.grid.GetNumberRows()):
			return
		
		if row != self.lastRow:
			self.lastRow = row
			colour = wx.Colour( 255, 255, 128 )
			self.grid.Set( backgroundColour	= dict(((row, c), colour) for c in xrange(self.grid.GetNumberCols())))
			self.grid.Refresh()
		
	def doRightClick( self, event ):
		wx.CallAfter( self.search.SetFocus )
		pass
		
	def showNumSelect( self ):
		pass
	
	def doLabelClick( self, event ):
		sortCol = event.GetCol()
		if sortCol == self.sortCol:
			self.sortCol = 0
		else:
			self.sortCol = sortCol
		wx.CallAfter( self.refresh )
	
	def doNumDrilldown( self, event ):
		self.doNumSelect( event )
		mainWin = Utils.getMainWin()
		if self.numSelect is not None and mainWin:
			mainWin.showPageName( 'RiderDetail' )
	
	def getCellNum( self, row, col ):
		numSelect = None
		if row < self.grid.GetNumberRows() and col < self.grid.GetNumberCols():
			value = self.grid.GetCellValue( row, col )
			if value:
				m = reIntPrefix.match( value )
				if m:
					numSelect = m.group(0)
		return numSelect
	
	def doNumSelect( self, event ):
		self.numSelect = None
		if self.isEmpty:
			return
		self.numSelect = self.grid.GetCellValue( event.GetRow(), 0 )
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.setNumSelect( self.numSelect )
	
	def clearGrid( self ):
		self.textColour = {}
		self.backgroundColour = {}
		self.grid.Set( data = [], colnames = [], textColour = {}, backgroundColour = {} )
		self.grid.Reset()
	
	def refresh( self, searchStr = None ):
		wx.CallAfter( self.search.SetFocus )
		self.isEmpty = True
		self.lastRow = -1
		
		with Model.LockRace() as race:
			if race is None:
				self.clearGrid()
				return

			try:
				externalInfo = race.excelLink.read()
			except AttributeError:
				externalInfo = {}
				
			inRace = set()
			for num in externalInfo.iterkeys():
				if num in race:
					inRace.add( num )

		if not externalInfo:
			self.clearGrid()
			return
			
		self.isEmpty = False
		if searchStr is not None:
			self.search.SetValue( searchStr )
		searchText = Utils.removeDiacritic(self.search.GetValue().lower())
		
		fields = ReadSignOnSheet.Fields
		info = externalInfo.itervalues().next()
		colnames = [f for f in fields if f in info]
		colnames.append( 'In Race' )
		data = [ [] for c in colnames ]
		for num, info in externalInfo.iteritems():
			if searchText:
				matched = False
				for f in colnames:
					try:
						if Utils.removeDiacritic(str(info[f]).lower()).find(searchText) >= 0:
							matched = True
							break
					except KeyError:
						pass
				if not matched:
					continue
				
			for c, f in enumerate(colnames):
				try:
					data[c].append( str(info[f]) )
				except KeyError:
					if f == 'In Race' and num in inRace:
						data[c].append( 'yes' )
					else:
						data[c].append( '' )
					
		sortPairs = []
		isBib = colnames[self.sortCol].startswith('Bib')
		isInRace = (colnames[self.sortCol] == 'In Race')
		for r, d in enumerate(data[self.sortCol]):
			if isBib:
				sortPairs.append( (int(d), int(data[0][r]), r) )
			elif isInRace:
				sortPairs.append( (-1 if d else 1, int(data[0][r]), r) )
			else:
				sortPairs.append( (Utils.removeDiacritic(d.lower()) if d else '~~~~~~~~~~~~~~~~~~', int(data[0][r]), r) )

		sortPairs.sort()
		for c, col in enumerate(data):
			data[c] = [col[r] for v, n, r in sortPairs]
		
		colnames[self.sortCol] = '<%s>' % colnames[self.sortCol]
		self.grid.Set( data = data, colnames = colnames )
		self.grid.SetLeftAlignCols( set(range(1, len(colnames))) )
		self.grid.AutoSizeColumns( True )
		self.grid.Reset()
			
		# Fix the grid's scrollbars.
		self.grid.FitInside()
	
class SearchDialog( wx.Dialog ):
	def __init__(
			self, parent, ID, title='Find Rider', size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER ):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		pre = wx.PreDialog()
		#pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)

		self.search = Search( self, wx.ID_ANY, size=(600,400) )
		sizer.Add(self.search, 1, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
		
		self.SetSizer(sizer)
		sizer.Fit(self)

	def refresh( self, searchStr = None ):
		self.search.refresh( searchStr )
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	mainWin.Show()
	searchDialog = SearchDialog( mainWin, wx.ID_ANY, "Search Dialog Test", size=(600,400) )
	searchDialog.Show()
	app.MainLoop()
