import wx
import wx.grid as gridlib

import os
import sys
from ReorderableGrid import ReorderableGrid
import SeriesModel
import Utils
from ReadRaceResultsSheet import GetExcelResultsLink, ExcelLink
	
class Sequence(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.seriesNameLabel = wx.StaticText( self, label='Series Name:' )
		self.seriesName = wx.TextCtrl( self )

		self.organizerNameLabel = wx.StaticText( self, label='Organizer:' )
		self.organizerName = wx.TextCtrl( self )
		
		self.explanation = wx.StaticText( self, label='\n'.join( [
				_("Change the Category order by dragging-and-dropping the first grey column in the table."),
			] )
		)
		
		self.headerNames = ['Category', 'Races']
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(self.headerNames) )
		for col in xrange(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, self.headerNames[col] )
		
		self.pointsChoiceEditor = gridlib.GridCellChoiceEditor([], allowOthers=False)
		attr = gridlib.GridCellAttr()
		attr.SetEditor( self.pointsChoiceEditor )
		self.grid.SetColAttr( self.PointsCol, attr )
		
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly( True )
		self.grid.SetColAttr( self.RaceCol, attr )
		
		'''
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly( True )
		self.grid.SetColAttr( self.SequencetatusCol, attr )
		'''
		
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly( True )
		self.grid.SetColAttr( self.RaceFileCol, attr )
		
		self.grid.Bind( gridlib.EVT_GRID_CELL_CHANGE, self.onGridChange )
		self.gridAutoSize()
		self.grid.Bind( wx.grid.EVT_GRID_EDITOR_CREATED, self.onGridEditorCreated )
		self.grid.Bind( wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onEditRaceFileName )
		
		self.addButton = wx.Button( self, wx.ID_ANY, 'Add Sequence' )
		self.addButton.Bind( wx.EVT_BUTTON, self.doAddRace )

		self.removeButton = wx.Button( self, wx.ID_ANY, 'Remove Race' )
		self.removeButton.Bind( wx.EVT_BUTTON, self.doRemoveRace )

		fgs = wx.FlexGridSizer( rows=2, cols=2, vgap=2, hgap=2 )
		fgs.AddGrowableCol( 1, proportion=1 )
		
		fgs.Add( self.seriesNameLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		fgs.Add( self.seriesName, flag=wx.EXPAND )
		fgs.Add( self.organizerNameLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		fgs.Add( self.organizerName, flag=wx.EXPAND )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.addButton, 0, flag=wx.ALL, border = 4 )
		hs.Add( self.removeButton, 0, flag=wx.ALL, border = 4 )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(fgs, 0, flag=wx.EXPAND|wx.ALL, border=4 )
		sizer.Add( self.explanation, 0, flag=wx.EXPAND|wx.ALL, border=4 )
		sizer.Add(hs, 0, flag=wx.EXPAND)
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6)
		self.SetSizer(sizer)

	def getGrid( self ):
		return self.grid
	
	wildcard = 'CrossMgr or Excel files (*.cmn, *.xlsx, *.xlsm, *.xls)|*.cmn;*.xlsx;*.xlsm;*.xls;'
	
	def onEditRaceFileName( self, event ):
		col = event.GetCol()
		if col != self.RaceFileCol:
			event.Skip()
			return
			
		row = event.GetRow()
		with wx.FileDialog( self, message="Choose a CrossMgr or Excel file",
					defaultFile = '',
					wildcard = self.wildcard,
					style=wx.FD_OPEN | wx.FD_CHANGE_DIR ) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				fileName = dlg.GetPath()
				self.grid.SetCellValue( row, self.RaceCol, SeriesModel.RaceNameFromPath(fileName) )
				self.grid.SetCellValue( row, self.RaceFileCol, fileName )
		
		self.commit()
	
	def doAddRace( self, event ):
		with wx.FileDialog( self, message="Choose a CrossMgr or Excel file",
					defaultFile = '',
					wildcard = self.wildcard,
					style=wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_MULTIPLE ) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				for fileName in dlg.GetPaths():
					SeriesModel.model.addRace( fileName )
		
		self.refresh()
		
	def doRemoveRace( self, event ):
		row = self.grid.GetGridCursorRow()
		if row < 0:
			Utils.MessageOK(self, 'No Selected Race.\nPlease Select a Race to Remove.', 'No Selected Race')
			return
		if Utils.MessageOKCancel(self, 'Confirm Remove Race:\n\n    {}'.format( self.grid.GetCellValue(row, 0) ), 'Remove Race'):
			self.grid.DeleteRows( row )
			self.commit()
	
	def updatePointsChoices( self ):
		try:
			comboBox = self.comboBox
		except AttributeError:
			return
		comboBox.SetItems( [p.name for p in SeriesModel.model.pointStructures] )
	
	def onGridEditorCreated(self, event):
		if event.GetCol() == self.PointsCol:
			self.comboBox = event.GetControl()
			self.updatePointsChoices()
		event.Skip()

	def gridAutoSize( self ):
		self.grid.AutoSize()
		self.grid.EnableDragGridSize( False )
		self.grid.EnableDragColSize( False )
		self.Layout()
		self.Refresh()
	
	def onGridChange( self, event ):
		wx.CallAfter( self.gridAutoSize )
	
	def refresh( self ):
		model = SeriesModel.model
		Utils.AdjustGridSize( self.grid, len(model.Sequence) )
		for row, race in enumerate(model.Sequence):
			self.grid.SetCellValue( row, self.RaceCol, race.getRaceName() )
			self.grid.SetCellValue( row, self.PointsCol, race.pointStructure.name )
			self.grid.SetCellValue( row, self.RaceFileCol, race.fileName )
		wx.CallAfter( self.gridAutoSize )
		
		self.seriesName.SetValue( SeriesModel.model.name )
		self.organizerName.SetValue( SeriesModel.model.organizer )
	
	def commit( self ):
		self.grid.SaveEditControlValue()
		self.grid.DisableCellEditControl()	# Make sure the current edit is committed.
		
		raceList = []
		for row in xrange(self.grid.GetNumberRows()):
			race = SeriesModel.model.Sequence[row]
			fileName = self.grid.GetCellValue(row, self.RaceFileCol).strip()
			pname = self.grid.GetCellValue( row, self.PointsCol )
			if not fileName or not pname:
				continue
			raceList.append( (fileName, pname) )
		
		model = SeriesModel.model
		model.setSequence( raceList )
		
		if self.seriesName.GetValue() != model.name:
			model.name = self.seriesName.GetValue()
			model.changed = True
			
		if self.organizerName.GetValue() != model.organizer:
			model.organizer = self.organizerName.GetValue()
			model.changed = True
			
		wx.CallAfter( self.refresh )
		
#----------------------------------------------------------------------------

class SequenceFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		wx.Frame.__init__(self, None, title="Sequence Test", size=(800,600) )
		self.panel = Sequence(self)
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	frame = SequenceFrame()
	frame.panel.refresh()
	app.MainLoop()
