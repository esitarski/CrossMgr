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
	HeaderNames = ['Category', 'Long Name', 'Indiv Publish', 'Points', 'Consider', 'Must Have Completed', 'Team Publish', 'Team Points', 'Use Nth Result Only', 'Team N']
	
	CategoryCol, LongNameCol, PublishCol, PointsCol, BestResultsToConsiderCol, MustHaveCompletedCol, TeamPublishCol, TeamPointsCol, UseNthScoreCol, TeamNCol = list(range(len(HeaderNames)))

	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.alphaSort = wx.Button( self, label='Sort Alphabetically' )
		self.alphaSort.Bind( wx.EVT_BUTTON, self.onSort )

		self.explanation = wx.StaticText( self, label='\n'.join( [
				_("Change the Category order by dragging-and-dropping the first grey column in the table."),
				_("If 'Use Nth Result Only' is True, 'Team N' specifies the top Nth rider's time to use for the team's time (eg. Team TT, scored on 3rd rider's result)"),
				_("If 'Use Nth Result Only' if False, 'Team N' specifies the top riders' times to be totaled for the team result (eg. Team Stage Finish, scored on sum of top 3 results for each team)."),
				_("If 'Points', 'TeamPoints' or 'Must Have Completed' are configured, they will override the values specified for the Races."),
			] )
		)
		
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(self.HeaderNames) )
		for col in range(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, self.HeaderNames[col] )
		
		maxOptions = 30
		self.bestResultsToConsiderChoices = ['', 'All Results', 'Best Result Only'] + ['{} {} {}'.format('Best', i, 'Results Only') for i in range(2,maxOptions+1)]
		self.mustHaveCompletedChoices = [''] + ['{} {}'.format(i, 'or more Events') for i in range(0,maxOptions+1)]

		for col in range(self.grid.GetNumberCols()):
			attr = gridlib.GridCellAttr()
			if col == self.CategoryCol:
				attr.SetReadOnly( True )
			elif col == self.LongNameCol:
				attr.SetReadOnly( False )
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
			elif col == self.PointsCol:
				self.pointsChoiceEditor = gridlib.GridCellChoiceEditor([], allowOthers=False)
				attr.SetEditor( self.pointsChoiceEditor )
			elif col == self.TeamPointsCol:
				self.teamPointsChoiceEditor = gridlib.GridCellChoiceEditor([], allowOthers=False)
				attr.SetEditor( self.teamPointsChoiceEditor )
			elif col == self.BestResultsToConsiderCol:
				self.bestResultsToConsiderChoiceEditor = gridlib.GridCellChoiceEditor(
					choices = self.bestResultsToConsiderChoices,
					allowOthers = False
				)
				attr.SetEditor( self.bestResultsToConsiderChoiceEditor )
			elif col == self.MustHaveCompletedCol:
				self.mustHaveCompletedChoiceEditor = gridlib.GridCellChoiceEditor(
					choices = self.mustHaveCompletedChoices,
					allowOthers = False
				)
				attr.SetEditor( self.mustHaveCompletedChoiceEditor )

			self.grid.SetColAttr( col, attr )
		
		self.grid.Bind( gridlib.EVT_GRID_CELL_LEFT_CLICK, self.onGridLeftClick )
		self.grid.Bind( wx.grid.EVT_GRID_EDITOR_CREATED, self.onGridEditorCreated )
		self.grid.Bind( wx.grid.EVT_GRID_CELL_CHANGING, self.onCellChanged )
		self.gridAutoSize()
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		sizer.Add( self.alphaSort, 0, flag=wx.ALL|wx.ALIGN_RIGHT, border=4 )
		sizer.Add( self.explanation, 0, flag=wx.ALL, border=4 )
		sizer.Add( self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6 )
		self.SetSizer( sizer )

	def onGridLeftClick( self, event ):
		if event.GetCol() in (self.PublishCol, self.TeamPublishCol, self.UseNthScoreCol):
			r, c = event.GetRow(), event.GetCol()
			self.grid.SetCellValue( r, c, '1' if self.grid.GetCellValue(r, c)[:1] != '1' else '0' )
		event.Skip()
	
	def getGrid( self ):
		return self.grid
	
	def updatePointsChoices( self ):
		try:
			comboBox = self.comboBox
		except AttributeError:
			return
		# Create a list of points structure with a blank default.
		comboBox.SetItems( [''] + [p.name for p in SeriesModel.model.pointStructures] )
	
	def onGridEditorCreated(self, event):
		if event.GetCol() in (self.PointsCol, self.TeamPointsCol):
			self.comboBox = event.GetControl()
			self.updatePointsChoices()
		event.Skip()

	def gridAutoSize( self ):
		self.grid.AutoSize()
		self.grid.EnableDragGridSize( False )
		self.grid.EnableDragColSize( False )
		self.Layout()
		self.Refresh()
		
	def onCellChanged( self, event ):
		wx.CallAfter( self.gridAutoSize )
	
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
			self.grid.SetCellValue( row, self.LongNameCol, c.longName )
			self.grid.SetCellValue( row, self.PublishCol, '01'[int(c.publish)] )
			self.grid.SetCellValue( row, self.PointsCol, c.pointStructure.name if c.pointStructure else '' )
			self.grid.SetCellValue( row, self.BestResultsToConsiderCol, self.bestResultsToConsiderChoices[c.bestResultsToConsider+1 if c.bestResultsToConsider is not None else 0] )
			self.grid.SetCellValue( row, self.MustHaveCompletedCol, self.mustHaveCompletedChoices[c.mustHaveCompleted+1 if c.mustHaveCompleted is not None else 0] )

			self.grid.SetCellValue( row, self.TeamPublishCol, '01'[int(c.teamPublish)] )
			self.grid.SetCellValue( row, self.TeamPointsCol, c.teamPointStructure.name if c.teamPointStructure else '' )
			self.grid.SetCellValue( row, self.TeamNCol, '{}'.format(c.teamN) )
			self.grid.SetCellValue( row, self.UseNthScoreCol, '01'[int(c.useNthScore)] )

		wx.CallAfter( self.gridAutoSize )
	
	def getCategoryList( self ):
		model = SeriesModel.model
		pointsStructureByName = {p.name:p for p in model.pointStructures}
		
		Category = SeriesModel.Category
		gc = self.grid.GetCellValue
		categories = []
		for row in range(self.grid.GetNumberRows()):
			c = Category(
				name = gc(row, self.CategoryCol).strip(),
				longName = gc(row, self.LongNameCol).strip(),
				iSequence=row,
				
				publish=gc(row, self.PublishCol) == '1',
				pointStructure = pointsStructureByName.get(gc(row, self.PointsCol), None),
				bestResultsToConsider = (self.bestResultsToConsiderChoices.index(gc(row, self.BestResultsToConsiderCol)) - 1) if gc(row, self.BestResultsToConsiderCol) else None,
				mustHaveCompleted = (self.mustHaveCompletedChoices.index(gc(row, self.MustHaveCompletedCol)) - 1) if gc(row, self.MustHaveCompletedCol) else None,

				teamPublish=gc(row, self.TeamPublishCol) == '1',
				teamPointStructure = pointsStructureByName.get(gc(row, self.TeamPointsCol), None),
				useNthScore=gc(row, self.UseNthScoreCol) == '1',
				teamN=max(1, int(gc(row, self.TeamNCol))),
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
