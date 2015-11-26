
import  wx
import  wx.grid as  Grid
import  copy

#---------------------------------------------------------------------------

class ColTable( Grid.PyGridTableBase ):
	"""
	A custom wx.Grid Table using user supplied data
	"""
	def __init__( self ):
		"""
		data is a list, indexed by col, containing a list of row values
		"""
		self.attrs = {}				# Set of unique cell attributes.
		self.rightAlign = False
		self.leftAlignCols = set()
		self.colRenderer = {}
		
		# The base class must be initialized *first*
		Grid.PyGridTableBase.__init__(self)
		
		# Column-oriented data.
		# textColour and backgroundColour are store as a dict indexed by (row, col).
		# Colour is a wx.Colour.
		self.data = []
		self.colnames = []
		self.textColour = {}
		self.backgroundColour = {}

	def __del__( self ):
		# Make sure we free up our allocated attribues.
		#for a in attrs:
		#	a.DecRef()
		pass
		
	def SetRightAlign( self, ra = True ):
		self.rightAlign = ra
		
	def SetLeftAlignCols( self, col, la = True ):
		if la:
			self.leftAlignCols.add( col )
		else:
			try:
				self.leftAlignCols.remove( col )
			except KeyError:
				pass
	
	def SetColRenderer( self, col, renderer ):
		self.colRenderer[col] = renderer
	
	def _adjustDimension( self, grid, current, new, isCol ):
		if isCol:
			delmsg, addmsg = Grid.GRIDTABLE_NOTIFY_COLS_DELETED, Grid.GRIDTABLE_NOTIFY_COLS_APPENDED
		else:
			delmsg, addmsg = Grid.GRIDTABLE_NOTIFY_ROWS_DELETED, Grid.GRIDTABLE_NOTIFY_ROWS_APPENDED
			
		if new < current:
			msg = Grid.GridTableMessage( self, delmsg, new, current-new )
			grid.ProcessTableMessage( msg )
		elif new > current:
			msg = Grid.GridTableMessage( self, addmsg, new-current )
			grid.ProcessTableMessage( msg )
	
	def Set( self, grid, data = None, colnames = None, textColour = None, backgroundColour = None ):
		if colnames is not None:
			self._adjustDimension( grid, len(self.colnames), len(colnames), True )
			self.colnames = list(colnames)
			
		if data is not None:
			current = max( len(c) for c in self.data )	if self.data	else 0
			new     = max( len(c) for c in data )		if data 		else 0
			self._adjustDimension( grid, current, new, False )
			self.data = copy.copy(data)
			
		if textColour is not None:
			self.textColour = dict(textColour)
			
		if backgroundColour is not None:
			self.backgroundColour = dict(backgroundColour)
	
	def SetColumn( self, grid, iCol, colData ):
		self.data[iCol] = copy.copy(colData)
		self.UpdateValues( grid )
	
	def SortByColumn( self, iCol, descending = False ):
		if not self.data:
			return
			
		colLen = len(self.data[0])
		if not all(len(colData) == colLen for colData in self.data):
			raise ValueError( 'Cannot sort with different column lengths' )
		
		allNumeric = True
		for e in self.data[iCol]:
			try:
				i = float(e)
			except:
				allNumeric = False
				break
		
		if allNumeric:
			elementIndex = [(float(e), i) for i, e in enumerate(self.data[iCol])]
		else:
			elementIndex = [(e, i) for i, e in enumerate(self.data[iCol])]
		elementIndex.sort()
		
		for c in xrange(len(self.data)):
			self.data[c] = [self.data[c][i] for e, i in elementIndex]
			if descending:
				self.data[c].reverse()
	
	def GetData( self ):
		return self.data

	def GetColNames( self ):
		return self.colnames
	
	def isEmpty( self ):
		return True if not self.data else False
	
	def GetNumberCols(self):
		try:
			return len(self.colnames)
		except TypeError:
			return 0

	def GetNumberRows(self):
		try:
			return max( len(c) for c in self.data )
		except (TypeError, ValueError):
			return 0

	def GetColLabelValue(self, col):
		try:
			return self.colnames[col]
		except (TypeError, IndexError):
			return ''

	def GetRowLabelValue(self, row):
		return unicode(row+1)

	def IsEmptyCell( self, row, col ):
		try:
			v = self.data[col][row]
			return v is None or v == ''
		except (TypeError, IndexError):
			return True
		
	def GetRawValue(self, row, col):
		return '' if self.IsEmptyCell(row, col) else self.data[col][row]

	def GetValue(self, row, col):
		return unicode(self.GetRawValue(row, col))

	def SetValue(self, row, col, value):
		# Nothing to do - everthing is read-only.
		pass
		
	def DeleteCols( self, pos = 0, numCols = 1, updateLabels = True, grid = None ):
		oldCols = len(self.colnames) if self.colnames else 0
		if self.data:
			del self.data[pos:pos+numCols]
		if self.colnames:
			del self.colnames[pos:pos+numCols]
		posMax = pos + numCols
		for a in ['textColour', 'backgroundColour']:
			if not getattr(self, a, None):
				continue
			colD = {}
			for (r, c), colour in getattr(self, a).iteritems():
				if c < pos:
					colD[(r, c)] = colour
				elif posMax <= c:
					colD[(r, c-numCols)] = colour
			setattr( self, a, colD )
		newCols = len(self.colnames) if self.colnames else 0
		self._adjustDimension( grid, oldCols, newCols, True )

	def GetAttr(self, row, col, someExtraParameter ):
		rc = (row, col)
		key = (self.textColour.get(rc, None), self.backgroundColour.get(rc, None), col)
		try:
			attr = self.attrs[key]
		except KeyError:
			# Create an attribute for the cache.
			attr = Grid.GridCellAttr()
			attr.SetReadOnly( 1 )			# All cells read-only.
			if rc in self.textColour:
				attr.SetTextColour( self.textColour[rc] )
			if rc in self.backgroundColour:
				attr.SetBackgroundColour( self.backgroundColour[rc] )
			self.attrs[key] = attr
		
		hCellAlign = None
		if col in self.leftAlignCols:
			hCellAlign = wx.ALIGN_LEFT
		elif self.rightAlign:
			hCellAlign = wx.ALIGN_RIGHT
		if hCellAlign is not None:
			attr.SetAlignment( hAlign = hCellAlign, vAlign = wx.ALIGN_CENTRE )
		attr.SetRenderer( self.colRenderer.get(col, wx.grid.GridCellStringRenderer()).Clone() )
			
		# We must increment the ref count so the attr does not get GC'd after it is referenced.
		attr.IncRef()
		return attr

	def SetAttr( self, row, col, attr ): pass
	def SetRowAttr( self, row, attr ): pass
	def SetColAttr( self, col, attr ) : pass
	def UpdateAttrRows( self, pos, numRows ) : pass
	def UpdateAttrCols( self, pos, numCols ) : pass
	
	def ResetView(self, grid):
		"""
		(Grid) -> Reset the grid view.   Call this to redraw the grid.
		"""
		for col in xrange(self.GetNumberCols()):
			attr = Grid.GridCellAttr()
			if col in self.leftAlignCols:
				hCellAlign = wx.ALIGN_LEFT
			elif self.rightAlign:
				hCellAlign = wx.ALIGN_RIGHT
			else:
				hCellAlign = wx.ALIGN_CENTRE
			attr.SetAlignment( hAlign = hCellAlign, vAlign = wx.ALIGN_CENTRE )
			self.SetColAttr( col, attr )

		grid.AdjustScrollbars()
		grid.ForceRefresh()

	def UpdateValues(self, grid):
		"""Update all displayed values"""
		# This sends an event to the grid table to update all of the values
		msg = Grid.GridTableMessage(self, Grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
		grid.ProcessTableMessage(msg)

# --------------------------------------------------------------------
# Sample Grid

class ColGrid(Grid.Grid):
	def __init__(self, parent, data = None, colnames = None, textColour = None, backgroundColour = None, style = 0 ):
		"""parent, data, colnames, plugins=None
		Initialize a grid using the data defined in data and colnames
		"""

		# The base class must be initialized *first*
		Grid.Grid.__init__(self, parent, style = style)
		self._table = ColTable()
		self.SetTable( self._table )
		self.Set( data, colnames, textColour, backgroundColour )
		
		self.zoomLevel = 1.0

	def Reset( self ):
		"""reset the view based on the data in the table.  Call this when rows are added or destroyed"""
		self._table.ResetView(self)

	def Set( self, data = None, colnames = None, textColour = None, backgroundColour = None ):
		self._table.Set( self, data, colnames, textColour, backgroundColour )
	
	def SetColumn( self, iCol, colData ):
		self._table.SetColumn( self, iCol, colData )
	
	def SetColRenderer( self, col, renderer ):
		self._table.SetColRenderer( col, renderer )
	
	def GetData( self ):
		return self._table.GetData()

	def GetColNames( self ):
		return self._table.GetColNames()
		
	def DeleteCols( self, pos = 0, numCols = 1, updateLabels = True ):
		self._table.DeleteCols(pos, numCols, updateLabels, self)
		self.Reset()
	
	def Zoom( self, zoomIn = True ):
		factor = 2 if zoomIn else 0.5
		if not 1.0/4.0 <= self.zoomLevel * factor <= 4.0:
			return
		self.zoomLevel *= factor
		
		font = self.GetDefaultCellFont()
		font.SetPointSize( int(font.GetPointSize() * factor) )
		self.SetDefaultCellFont( font )
		
		font = self.GetLabelFont()
		font.SetPointSize( int(font.GetPointSize() * factor) )
		self.SetLabelFont( font )
		
		self.SetColLabelSize( int(self.GetColLabelSize() * factor) )
		self.AutoSize()
		self.Reset()
	
	def SetRightAlign( self, ra = True ):
		self._table.SetRightAlign( ra )
		self.Reset()
		
	def SetLeftAlignCols( self, cols ):
		self._table.leftAlignCols = set()
		for c in cols:
			self._table.leftAlignCols.add( c )
		self.Reset()
	
	def SortByColumn( self, iCol, descending = False ):
		self._table.SortByColumn( iCol, descending )
		self.Refresh()
	
	def clearGrid( self ):
		self.Set( data = [], colnames = [], textColour = {}, backgroundColour = {} )
		self.Reset()
