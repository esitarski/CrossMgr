import wx
import wx.grid as gridlib

import os
import sys
from ReorderableGrid import ReorderableGrid
import SeriesModel
import Utils
from ReadRaceResultsSheet import GetExcelResultsLink, ExcelLink
	
class Races(wx.Panel):
	#----------------------------------------------------------------------
	RaceCol = 0
	PointsCol = 1
	RaceFileCol = 2
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.seriesNameLabel = wx.StaticText( self, wx.ID_ANY, 'Series Name:' )
		self.seriesName = wx.TextCtrl( self, wx.ID_ANY )

		self.headerNames = ['Race', 'Points', 'Race File']
		
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
		
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly( True )
		self.grid.SetColAttr( self.RaceFileCol, attr )
		
		self.grid.Bind( gridlib.EVT_GRID_CELL_CHANGE, self.onGridChange )
		self.gridAutoSize()
		self.grid.Bind( wx.grid.EVT_GRID_EDITOR_CREATED, self.onGridEditorCreated )
		self.grid.Bind( wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onEditRaceFileName )
		
		self.addButton = wx.Button( self, wx.ID_ANY, 'Add Race' )
		self.addButton.Bind( wx.EVT_BUTTON, self.doAddRace )

		self.removeButton = wx.Button( self, wx.ID_ANY, 'Remove Race' )
		self.removeButton.Bind( wx.EVT_BUTTON, self.doRemoveRace )

		hsName = wx.BoxSizer( wx.HORIZONTAL )
		hsName.Add( self.seriesNameLabel, 0, flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL, border = 4 )
		hsName.Add( self.seriesName, 1, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.addButton, 0, flag=wx.ALL, border = 4 )
		hs.Add( self.removeButton, 0, flag=wx.ALL, border = 4 )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(hsName, 0, flag=wx.EXPAND)
		sizer.Add(hs, 0, flag=wx.EXPAND)
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6)
		self.SetSizer(sizer)

	def getGrid( self ):
		return self.grid
	
	wildcard = 'CrossMgr or Excel files (*.cmn, *.xlsx, *.xlsm, *.xls)|*.cmn;*.xlsx;*.xlsm;*.xls;'
	
	def doExcelLink( self, race, row ):
		excelLink = race.excelLink if race.excelLink else ExcelLink()
		excelLink.setFileName( race.fileName )
		race.excelLink = GetExcelResultsLink( self, excelLink ).show()
		self.grid.SetCellValue( row, self.RaceCol, race.getRaceName() )
		wx.CallAfter( self.refresh )
	
	def onEditRaceFileName( self, event ):
		col = event.GetCol()
		if col != self.RaceFileCol:
			event.Skip()
			return
			
		row = event.GetRow()
		dlg = wx.FileDialog( self, message="Choose a CrossMgr or Excel file",
					defaultFile = '',
					wildcard = self.wildcard,
					style=wx.OPEN | wx.CHANGE_DIR )
		ret = dlg.ShowModal()
		fileName = ''
		if ret == wx.ID_OK:
			fileName = dlg.GetPath()
			self.grid.SetCellValue( row, self.RaceCol, SeriesModel.RaceNameFromPath(fileName) )
			self.grid.SetCellValue( row, self.RaceFileCol, fileName )
		dlg.Destroy()
		self.refresh()
		if ret == wx.ID_OK and os.path.splitext(fileName)[1] != '.cmn':
			race = SeriesModel.model.races[row]
			race.fileName = fileName
			race.excelLink = ExcelLink()
			race.excelLink.setFileName( fileName )
			wx.CallAfter( self.doExcelLink, race, row )
	
	def doAddRace( self, event ):
		dlg = wx.FileDialog( self, message="Choose a CrossMgr or Excel file",
					defaultFile = '',
					wildcard = self.wildcard,
					style=wx.OPEN | wx.CHANGE_DIR )
		ret = dlg.ShowModal()
		if ret == wx.ID_OK:
			fileName = dlg.GetPath()
			SeriesModel.model.addRace( fileName )
		dlg.Destroy()
		self.refresh()
		if ret == wx.ID_OK and os.path.splitext(fileName)[1] != '.cmn':
			wx.CallAfter( self.doExcelLink, SeriesModel.model.races[-1], len(SeriesModel.model.races) - 1 )
		
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
		Utils.AdjustGridSize( self.grid, len(model.races) )
		for row, race in enumerate(model.races):
			self.grid.SetCellValue( row, self.RaceCol, race.getRaceName() )
			self.grid.SetCellValue( row, self.PointsCol, race.pointStructure.name )
			self.grid.SetCellValue( row, self.RaceFileCol, race.fileName )
		wx.CallAfter( self.gridAutoSize )
		
		self.seriesName.SetValue( SeriesModel.model.name )
	
	def commit( self ):
		self.grid.DisableCellEditControl()	# Make sure the current edit is committed.
		
		raceList = []
		for row in xrange(self.grid.GetNumberRows()):
			race = SeriesModel.model.races[row]
			excelLink = race.excelLink
			fileName = self.grid.GetCellValue(row, self.RaceFileCol).strip()
			pname = self.grid.GetCellValue( row, self.PointsCol )
			if not fileName or not pname:
				continue
			raceList.append( (fileName, pname, excelLink) )
		
		model = SeriesModel.model
		model.setRaces( raceList )
		
		if self.seriesName.GetValue() != model.name:
			model.name = self.seriesName.GetValue()
			model.changed = True
			
		wx.CallAfter( self.refresh )
		
#----------------------------------------------------------------------------

class RacesFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		wx.Frame.__init__(self, None, title="Races Test", size=(800,600) )
		self.panel = Races(self)
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	frame = RacesFrame()
	frame.panel.refresh()
	app.MainLoop()