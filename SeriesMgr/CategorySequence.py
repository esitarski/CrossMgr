import wx
import wx.grid as gridlib

import os
import sys
import operator
from ReorderableGrid import ReorderableGrid
import SeriesModel
import Utils
from ReadRaceResultsSheet import GetExcelResultsLink, ExcelLink
	
class CategorySequence(wx.Panel):
	CategoryCol = 0
	PublishCol = 1
	TeamNCol = 2
	UseNthScoreCol = 3
	TeamPublishCol = 4

	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.alphaSort = wx.Button( self, label='Sort Alphabetically' )
		self.alphaSort.Bind( wx.EVT_BUTTON, self.onSort )

		self.explanation = wx.StaticText( self, label='\n'.join( [
				_("Change the Category order by dragging-and-dropping the first grey column in the table."),
				_("If 'Use Nth Result Only' is True, 'Team N' specifies the top Nth rider's time to use for the team's time (eg. Team TT, scored on 3rd rider's result)"),
				_("If 'Use Nth Result Only' if False, 'Team N' specifies the top riders' times to be totaled for the team result (eg. Team Stage Finish, scored on sum of top 3 results for each team)."),
			] )
		)
		
		self.headerNames = ['Category', 'Ind. Publish', 'Team N', 'Use Nth Result Only', 'Team Publish']
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(self.headerNames) )
		for col in range(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, self.headerNames[col] )
		
		for col in range(self.grid.GetNumberCols()):
			attr = gridlib.GridCellAttr()
			if col == self.CategoryCol:
				attr.SetReadOnly( True )
			elif col in (self.PublishCol, self.UseNthScoreCol, self.TeamPublishCol):
				editor = gridlib.GridCellBoolEditor()
				editor.UseStringValues( '1', '0' )
				attr.SetEditor( editor )
				attr.SetRenderer( gridlib.GridCellBoolRenderer() )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
			elif col == self.TeamNCol:
				editor = gridlib.GridCellNumberEditor()
				attr.SetEditor( editor )
				attr.SetRenderer( gridlib.GridCellNumberRenderer() )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )				

			self.grid.SetColAttr( col, attr )
		
		self.Bind( gridlib.EVT_GRID_CELL_LEFT_CLICK, self.onGridLeftClick )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		sizer.Add( self.alphaSort, 0, flag=wx.ALL|wx.ALIGN_RIGHT, border=4 )
		sizer.Add( self.explanation, 0, flag=wx.ALL, border=4 )
		sizer.Add( self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6 )
		self.SetSizer( sizer )

	def onGridLeftClick( self, event ):
		if event.GetCol() in (self.PublishCol, self.UseNthScoreCol, self.TeamPublishCol):
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
	
	def refresh( self, backgroundUpdate=False ):
		model = SeriesModel.model
		
		if backgroundUpdate:
			categoryList = []
		else:
			with wx.BusyCursor() as wait:
				model.extractAllRaceResults()	# Also harmonizes the categorySequence
				categoryList = model.getCategoriesSorted()
		
		Utils.AdjustGridSize( self.grid, len(categoryList) )
		for row, c in enumerate(categoryList):
			self.grid.SetCellValue( row, self.CategoryCol, c.name )
			self.grid.SetCellValue( row, self.PublishCol, '01'[int(c.publish)] )
			self.grid.SetCellValue( row, self.TeamNCol, '{}'.format(c.teamN) )
			self.grid.SetCellValue( row, self.UseNthScoreCol, '01'[int(c.useNthScore)] )
			self.grid.SetCellValue( row, self.TeamPublishCol, '01'[int(c.teamPublish)] )
		wx.CallAfter( self.gridAutoSize )
	
	def getCategoryList( self ):
		Category = SeriesModel.Category
		gc = self.grid.GetCellValue
		categories = []
		for row in range(self.grid.GetNumberRows()):
			c = Category(
				name=gc(row, self.CategoryCol),
				iSequence=row,
				publish=gc(row, self.PublishCol) == '1',
				teamN=max(1, int(gc(row, self.TeamNCol))),
				useNthScore=gc(row, self.UseNthScoreCol) == '1',
				teamPublish=gc(row, self.TeamPublishCol) == '1'
			)
			categories.append( c )
		return categories
	
	def commit( self ):
		categoryList = self.getCategoryList()
		SeriesModel.model.setCategories( categoryList )
	
	def onSort( self, event ):
		categoryList = self.getCategoryList()
		categoryList.sort( key = operator.attrgetter('name') )
		SeriesModel.model.setCategories( categoryList )
		wx.CallAfter( self.Refresh )
		
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
