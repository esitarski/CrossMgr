import os

import wx
import wx.grid as gridlib

from ReorderableGrid import ReorderableGrid
import SeriesModel
import Utils
	
class Competitions(wx.Panel):
	#----------------------------------------------------------------------
	headerNames = [_('Competition'), _('UUID')]
	
	NameCol = 0
	UUIDCol = 1
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.explanation = wx.StaticText( self, label='\n'.join( [
				_("Add Competitions for your Series."),
				_("Make sure the Competitions are in chronological order."),
				_("You can change the order by dragging-and-dropping the first grey column in the table."),
				'',
				_("Competitions are used to combine Race results for top K of N results."),
				_("Currently, this only works with races with Points."),
			] )
		)
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(self.headerNames) )
		for col in range(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, self.headerNames[col] )
		
		attr = gridlib.GridCellAttr()
		attr.SetAlignment( wx.ALIGN_LEFT, wx. ALIGN_CENTRE )
		self.grid.SetColAttr( self.NameCol, attr )
		
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly( True )
		self.grid.SetColAttr( self.UUIDCol, attr )
		
		self.grid.Bind( gridlib.EVT_GRID_CELL_CHANGED, self.onGridChange )
		self.gridAutoSize()
		
		self.addButton = wx.Button( self, wx.ID_ANY, 'Add Competition' )
		self.addButton.Bind( wx.EVT_BUTTON, self.doAddCompetition )

		self.removeButton = wx.Button( self, wx.ID_ANY, 'Remove Competitions' )
		self.removeButton.Bind( wx.EVT_BUTTON, self.doRemoveCompetitions )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.addButton, 0, flag=wx.ALL, border = 4 )
		hs.Add( self.removeButton, 0, flag=wx.ALL, border = 4 )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add( self.explanation, 0, flag=wx.EXPAND|wx.ALL, border=4 )
		sizer.Add(hs, 0, flag=wx.EXPAND)
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6)
		self.SetSizer(sizer)

	def getGrid( self ):
		return self.grid
	
	def doAddCompetition( self, event ):
		Utils.AdjustGridSize( self.grid, self.grid.GetNumberRows()+1 )
		self.grid.SetCellValue( self.grid.GetNumberRows()-1, 0, ' '*32 )
		self.gridAutoSize()
		self.grid.SetGridCursor( self.grid.GetNumberRows()-1, 0 )
		self.grid.MakeCellVisible( self.grid.GetNumberRows()-1, 0 )
	
	def doRemoveCompetitions( self, event ):
		selectedRows = set()
		selectedRows.update( c.GetRow() for c in self.grid.GetSelectedCells() )
		selectedRows.update( self.grid.GetSelectedRows() )
		if (row := self.grid.GetGridCursorRow()) >= 0:
			selectedRows.add( row )
		selectedRows = sorted( selectedRows )
		
		if not selectedRows:
			Utils.MessageOK(self, 'No Selected Competitions.\nPlease Select one or more Competitions to Remove.', 'No Selected Competitions')
			return
		
		raceNames = []
		for i, r in enumerate(selectedRows, 1):
			# Make a name from the last two components of the path.
			name = self.grid.GetCellValue(r, 0).replace( '\\', '/' )
			rName = os.path.join( *name.split('/')[-2:] )
			raceNames.append( f'{i}.  {rName}' )
		raceList = '\n'.join( raceNames )
		
		if Utils.MessageOKCancel(self, 'Confirm Remove Competitions:\n\n{}'.format( raceList ), 'Remove Competitions'):
			for r in reversed(selectedRows):
				self.grid.DeleteRows( r )
			self.commit()
	
	def gridAutoSize( self ):
		self.grid.AutoSize()
		self.grid.SetColSize( self.UUIDCol, 0 )
		self.grid.EnableDragGridSize( False )
		self.grid.EnableDragColSize( False )
		self.Layout()
		self.Refresh()
	
	def onGridChange( self, event ):
		wx.CallAfter( self.gridAutoSize )
	
	def refresh( self ):
		model = SeriesModel.model
		Utils.AdjustGridSize( self.grid, len(model.competitions) )
		for row, competition in enumerate(model.competitions):
			self.grid.SetCellValue( row, self.NameCol, competition.name )
			self.grid.SetCellValue( row, self.UUIDCol, competition.uuid )
		wx.CallAfter( self.gridAutoSize )
	
	def commit( self ):
		self.grid.SaveEditControlValue()
		self.grid.DisableCellEditControl()	# Make sure the current edit is committed.
		
		competitionList = []
		for row in range(self.grid.GetNumberRows()):
			name = self.grid.GetCellValue(row, self.NameCol).strip()
			uuid = self.grid.GetCellValue(row, self.UUIDCol).strip()
			if name:
				competitionList.append( (name, uuid) )
		
		model = SeriesModel.model
		competitionsChanged = model.setCompetitions( competitionList )
		
		wx.CallAfter( self.refresh )
		if competitionsChanged and Utils.getMainWin():
			wx.CallAfter( Utils.getMainWin().refreshAll )
		
#----------------------------------------------------------------------------

class CompetitionsFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		wx.Frame.__init__(self, None, title="Competitions Test", size=(800,600) )
		self.panel = Competitions(self)
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	frame = CompetitionsFrame()
	frame.panel.refresh()
	app.MainLoop()
