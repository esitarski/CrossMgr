import wx
import re

import Utils
import Model
import ColGrid
import ReadSignOnSheet

reIntPrefix = re.compile( '^[0-9]+' )
class Search( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, style=0, size=wx.DefaultSize ):
		super().__init__(parent, id, style=style, size=size )

		self.sortCol = 0
		self.numSelect = None
		self.textColour = {}
		self.backgroundColour = {}
		self.lastRow = -1
		self.isEmpty = True
		
		self.vbs = wx.BoxSizer(wx.VERTICAL)
		
		hbs = wx.BoxSizer( wx.HORIZONTAL )
		
		self.searchLabel = wx.StaticText( self, label=_('Search:') )
		self.search = wx.SearchCtrl(self, style=wx.TE_PROCESS_ENTER )
		self.search.ShowCancelButton( True )
		self.search.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnDoSearch )
		self.search.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCloseSearch )
		self.search.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
		self.search.Bind(wx.EVT_TEXT, self.OnDoSearch)
		
		self.closeButton = wx.Button( self, wx.ID_CANCEL, label=_('Close') )
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
		self.grid.SetMinSize( (650, 360) )
		self.grid.SetDoubleBuffered( True )

		self.grid.Bind( wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.doNumDrilldown )
		self.grid.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doRightClick )
		self.grid.Bind( wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.doLabelClick )
		self.grid.GetGridWindow().Bind( wx.EVT_MOTION, self.doMouseMove )
		
		self.vbs.Add( hbs, proportion=0, flag=wx.EXPAND )
		self.vbs.Add( self.grid, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border = 4 )
		
		self.SetSizer(self.vbs)
		self.vbs.SetSizeHints(self)

	def OnClose( self, event ):
		if self.GetParent():
			self.GetParent().Show( False )
		
	def OnCloseSearch( self, event ):
		self.search.ChangeValue( '' )
		
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
			self.grid.Set( backgroundColour	= dict(((row, c), colour) for c in range(self.grid.GetNumberCols())))
			self.grid.Refresh()
		
	def doRightClick( self, event ):
		wx.CallAfter( self.search.SetFocus )
		
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
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.riderDetail.commit()
		self.doNumSelect( event )
		if self.numSelect is not None and mainWin:
			mainWin.showPage( mainWin.iRiderDetailPage )
	
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
		self.grid.Set( data=[], colnames=[], textColour={}, backgroundColour={} )
		self.grid.Reset()
	
	def refresh( self, searchStr = None ):
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
				
			inRace = { num for num in externalInfo.keys() if num in race }

		if not externalInfo:
			self.clearGrid()
			return
			
		self.isEmpty = False
		if searchStr is not None:
			self.search.ChangeValue( searchStr )
		searchText = Utils.removeDiacritic(self.search.GetValue().lower())
		
		fields = ReadSignOnSheet.Fields
		colnames = [_('StartTime')] if race.isTimeTrial else []
		colnames.extend( f for f in fields if f in next(iter(externalInfo.values())) )
		colnames.append( _('In Race') )
		data = [ [] for c in colnames ]
		
		for num, info in externalInfo.items():
			if searchText:
				matched = False
				for f in colnames:
					try:
						if Utils.removeDiacritic('{}'.format(info[f]).lower()).find(searchText) >= 0:
							matched = True
							break
					except KeyError:
						pass
				if not matched:
					continue
			
			for c, f in enumerate(colnames):
				if f.startswith('Tag'):
					try:
						data[c].append( '{}'.format(info[f]).lstrip('0') )
					except Exception:
						data[c].append( '' )
				else:
					try:
						data[c].append( '{}'.format(info[f]) )
						continue
					except KeyError:
						pass
					if f == _('In Race') and num in inRace:
						data[c].append( _('yes') )
					elif f == _('StartTime'):
						r = race.riders.get(num, None)
						st = r.firstTime if r and hasattr(r, 'firstTime') else None
						data[c].append( Utils.formatTime(st) if st is not None else '' )
					else:
						data[c].append( '' )
					
		sortPairs = []
		
		iBib = 1 if race.isTimeTrial else 0
		
		if colnames[self.sortCol].startswith('Bib'):
			for r, d in enumerate(data[self.sortCol]):
				sortPairs.append( (int(d), int(data[iBib][r]), r) )			# Sort bib numbers as ints.
				
		elif colnames[self.sortCol] == _('In Race'):
			for r, d in enumerate(data[self.sortCol]):
				sortPairs.append( (-1 if d else 1, int(data[iBib][r]), r) )	# Sort 'In Race' to the front.
				
		elif colnames[self.sortCol].startswith('Tag'):
			for r, d in enumerate(data[self.sortCol]):
				sortPairs.append( (d.zfill(32), int(data[iBib][r]), r) )		# Sort tags with leading zeros.
				
		elif colnames[self.sortCol] == _('StartTime'):
			for r, d in enumerate(data[self.sortCol]):
				sortPairs.append( (Utils.StrToSeconds(d), int(data[iBib][r]), r) )	# Sort by start time.
				
		else:
			for r, d in enumerate(data[self.sortCol]):						# Default sort as non-diacritic text.
				sortPairs.append( (Utils.removeDiacritic(d.lower()) if d else '~~~~~~~~~~~~~~~~~~', int(data[iBib][r]), r) )

		sortPairs.sort()
		for c, col in enumerate(data):
			data[c] = [col[r] for v, n, r in sortPairs]
			
		colnames[self.sortCol] = '<{}>'.format(colnames[self.sortCol])
		self.grid.Set( data = data, colnames = colnames )
		self.grid.SetLeftAlignCols( set(i for i in range(0, len(colnames)) if not any(a in colnames[i] for a in ('StartTime','Tag', 'Bib'))) )
		self.grid.AutoSizeColumns( True )
		self.grid.Reset()
		self.grid.SetRowLabelSize( 32 )	
		
		# Fix the grid's scrollbars.
		self.grid.FitInside()
	
class SearchDialog( wx.Dialog ):
	def __init__(
			self, parent, ID = wx.ID_ANY, title=_('Find Rider'), size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER ):

		super().__init__(parent, ID, title, pos, size, style)

		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)

		self.search = Search( self, wx.ID_ANY, size=(600,700) )
		sizer.Add(self.search, 1, flag=wx.ALL|wx.EXPAND, border=5)
		
		self.SetSizer(sizer)
		sizer.Fit(self)

	def refresh( self, searchStr = None ):
		self.search.refresh( searchStr )
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None, title="CrossMan")
	mainWin.Show()
	searchDialog = SearchDialog( mainWin, title = "Search Dialog Test" )
	searchDialog.Show()
	app.MainLoop()
