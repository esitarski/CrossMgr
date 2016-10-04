import wx
import wx.grid as gridlib

import os
import sys
from ReorderableGrid import ReorderableGrid
import SeriesModel
import Utils
from ReadRaceResultsSheet import GetExcelResultsLink, ExcelLink
	
class CategorySequence(wx.Panel):
	CategoryCol = 0
	PublishCol = 1

	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.alphaSort = wx.Button( self, label=u'Sort Alphabetically' )
		self.alphaSort.Bind( wx.EVT_BUTTON, self.onSort )

		self.explanation = wx.StaticText( self, label=u'\n'.join( [
				_("Change the Category order by dragging-and-dropping the first grey column in the table."),
			] )
		)
		
		self.headerNames = ['Category', 'Publish']
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(self.headerNames) )
		for col in xrange(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, self.headerNames[col] )
		
		for col in xrange(self.grid.GetNumberCols()):
			attr = gridlib.GridCellAttr()
			if col == self.CategoryCol:
				attr.SetReadOnly( True )
			elif col == self.PublishCol:
				boolEditor = gridlib.GridCellBoolEditor()
				boolEditor.UseStringValues( '1', '0' )
				attr.SetEditor( boolEditor )
				attr.SetRenderer( gridlib.GridCellBoolRenderer() )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )

			self.grid.SetColAttr( col, attr )
		
		self.Bind( gridlib.EVT_GRID_CELL_LEFT_CLICK, self.onGridLeftClick )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		sizer.Add( self.alphaSort, 0, flag=wx.ALL|wx.ALIGN_RIGHT, border=4 )
		sizer.Add( self.explanation, 0, flag=wx.ALL, border=4 )
		sizer.Add( self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6 )
		self.SetSizer( sizer )

	def onGridLeftClick( self, event ):
		if event.GetCol() == self.PublishCol:
			r, c = event.GetRow(), event.GetCol()
			self.grid.SetCellValue( r, c, '1' if self.grid.GetCellValue(r, c)[:1] != '1' else '0' )
		event.Skip()
	
	def getGrid( self ):
		return self.grid
	
	def gridAutoSize( self ):
		self.grid.AutoSize()
		self.grid.EnableDragGridSize( False )
		self.grid.EnableDragColSize( False )
		self.Layout()
		self.Refresh()
	
	def refresh( self ):
		model = SeriesModel.model
		model.extractAllRaceResults()	# Also harmonizes the categorySequence
		categories = model.getCategoryNamesSorted()
		
		Utils.AdjustGridSize( self.grid, len(categories) )
		for row, c in enumerate(categories):
			self.grid.SetCellValue( row, self.CategoryCol, c )
			self.grid.SetCellValue( row, self.PublishCol, '10'[int(c in model.categoryHide)] )
		wx.CallAfter( self.gridAutoSize )
	
	def getCategories( self ):
		categories = []
		for row in xrange(self.grid.GetNumberRows()):
			categories.append( self.grid.GetCellValue(row, self.CategoryCol) )
		return categories
	
	def getCategoryHide( self ):
		categoryHide = set()
		for row in xrange(self.grid.GetNumberRows()):
			if self.grid.GetCellValue(row, self.PublishCol) != '1':
				categoryHide.add( self.grid.GetCellValue(row, self.CategoryCol) )
		return categoryHide
	
	def commit( self ):
		SeriesModel.model.setCategorySequence( self.getCategories(), self.getCategoryHide() )
	
	def onSort( self, event ):
		categories = self.getCategories()
		categories.sort()
		SeriesModel.model.setCategorySequence( categories )
		wx.CallAfter( self.refresh )
		
#----------------------------------------------------------------------------

class CategorySequenceFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		wx.Frame.__init__(self, None, title="CategorySequence Test", size=(800,600) )
		self.panel = CategorySequence(self)
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	frame = CategorySequenceFrame()
	frame.panel.refresh()
	app.MainLoop()
