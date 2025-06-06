import os

import wx
import wx.grid as gridlib

from ReorderableGrid import ReorderableGrid
import SeriesModel
import Utils
	
class Races(wx.Panel):
	#----------------------------------------------------------------------
	headerNames = ['Race', 'Comp', 'Grade', 'Default Points', 'Default Team Pts', 'Race File']
	
	RaceCol = 0
	CompetitionCol = 1
	GradeCol = 2
	PointsCol = 3
	TeamPointsCol = 4
	RaceFileCol = 5
	RaceStatusCol = 6
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.seriesNameLabel = wx.StaticText( self, label='Series Name:' )
		self.seriesName = wx.TextCtrl( self )

		self.organizerNameLabel = wx.StaticText( self, label='Organizer:' )
		self.organizerName = wx.TextCtrl( self )
		
		self.explanation = wx.StaticText( self, label='\n'.join( [
				_("Add all the races in your Series."),
				_("Make sure the races are in chronological order."),
				_("You can change the order by dragging-and-dropping the first grey column in the table."),
				'',
				_("You can configure the Point Structures and Team Scoring parameters on the Scoring Criteria page."),
				_("Each race can have its own Points Structure.  For example, you could create 'Double Points' for one race."),
				_("You can also configure Point Structures by Category, which will override the structures defined by race."),
				'',
				_("Results are shown Last-to-First in the output by default."),
				_("You can change this on the Options page."),
			] )
		)
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(self.headerNames) )
		for col in range(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, self.headerNames[col] )
		
		self.pointsChoiceEditor = gridlib.GridCellChoiceEditor([], allowOthers=False)
		attr = gridlib.GridCellAttr()
		attr.SetEditor( self.pointsChoiceEditor )
		self.grid.SetColAttr( self.PointsCol, attr )
		
		self.competitionChoiceEditor = gridlib.GridCellChoiceEditor([], allowOthers=False)
		attr = gridlib.GridCellAttr()
		attr.SetEditor( self.competitionChoiceEditor )
		self.grid.SetColAttr( self.CompetitionCol, attr )
		
		self.teamPointsChoiceEditor = gridlib.GridCellChoiceEditor([], allowOthers=False)
		attr = gridlib.GridCellAttr()
		attr.SetEditor( self.teamPointsChoiceEditor )
		self.grid.SetColAttr( self.TeamPointsCol, attr )
		
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly( True )
		self.grid.SetColAttr( self.RaceCol, attr )
		
		attr = gridlib.GridCellAttr()
		attr.SetAlignment( wx.ALIGN_CENTRE, wx. ALIGN_CENTRE )
		self.grid.SetColAttr( self.GradeCol, attr )
		
		'''
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly( True )
		self.grid.SetColAttr( self.RaceStatusCol, attr )
		'''
		
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly( True )
		self.grid.SetColAttr( self.RaceFileCol, attr )
		
		self.grid.Bind( gridlib.EVT_GRID_CELL_CHANGED, self.onGridChange )
		self.gridAutoSize()
		self.grid.Bind( wx.grid.EVT_GRID_EDITOR_CREATED, self.onGridEditorCreated )
		self.grid.Bind( wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onEditRaceFileName )
		
		self.addButton = wx.Button( self, wx.ID_ANY, 'Add Races' )
		self.addButton.Bind( wx.EVT_BUTTON, self.doAddRace )

		self.removeButton = wx.Button( self, wx.ID_ANY, 'Remove Races' )
		self.removeButton.Bind( wx.EVT_BUTTON, self.doRemoveRaces )

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
		
	def doRemoveRaces( self, event ):
		selectedRows = set()
		selectedRows.update( c.GetRow() for c in self.grid.GetSelectedCells() )
		selectedRows.update( self.grid.GetSelectedRows() )
		if (row := self.grid.GetGridCursorRow()) >= 0:
			selectedRows.add( row )
		selectedRows = sorted( selectedRows )
		
		if not selectedRows:
			Utils.MessageOK(self, 'No Selected Races.\nPlease Select one or more Races to Remove.', 'No Selected Races')
			return
		
		raceNames = []
		for i, r in enumerate(selectedRows, 1):
			# Make a name from the last two components of the path.
			name = self.grid.GetCellValue(r, 0).replace( '\\', '/' )
			rName = os.path.join( *name.split('/')[-2:] )
			raceNames.append( f'{i}.  {rName}' )
		raceList = '\n'.join( raceNames )
		
		if Utils.MessageOKCancel(self, 'Confirm Remove Races:\n\n{}'.format( raceList ), 'Remove Races'):
			for r in reversed(selectedRows):
				self.grid.DeleteRows( r )
			self.commit()
	
	def updatePointsChoices( self ):
		try:
			comboBox = self.comboBox
		except AttributeError:
			return
		comboBox.SetItems( [p.name for p in SeriesModel.model.pointStructures] )
	
	def updateTeamPointsChoices( self ):
		try:
			teamComboBox = self.teamComboBox
		except AttributeError:
			return
		teamComboBox.SetItems( [''] + [p.name for p in SeriesModel.model.pointStructures] )
	
	def updateCompetitionChoices( self ):
		try:
			competitionComboBox = self.competitionComboBox
		except AttributeError:
			return
		competitionComboBox.SetItems( [''] + [c.name for c in SeriesModel.model.competitions] )
	
	def onGridEditorCreated(self, event):
		if event.GetCol() == self.PointsCol:
			self.comboBox = event.GetControl()
			self.updatePointsChoices()
		elif event.GetCol() == self.TeamPointsCol:
			self.teamComboBox = event.GetControl()
			self.updateTeamPointsChoices()
		elif event.GetCol() == self.CompetitionCol:
			self.competitionComboBox = event.GetControl()
			self.updateCompetitionChoices()
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
		
		uuidToCompetition = {c.uuid:c for c in model.competitions}
		
		Utils.AdjustGridSize( self.grid, len(model.races) )
		for row, race in enumerate(model.races):
			self.grid.SetCellValue( row, self.RaceCol, race.getRaceName() )
			self.grid.SetCellValue( row, self.CompetitionCol, race.competition.name if race.competition else '')
			self.grid.SetCellValue( row, self.GradeCol, race.grade )
			self.grid.SetCellValue( row, self.PointsCol, race.pointStructure.name )
			self.grid.SetCellValue( row, self.TeamPointsCol, race.teamPointStructure.name if race.teamPointStructure else '' )
			self.grid.SetCellValue( row, self.RaceFileCol, race.fileName )
		wx.CallAfter( self.gridAutoSize )
		
		self.seriesName.SetValue( SeriesModel.model.name )
		self.organizerName.SetValue( SeriesModel.model.organizer )
	
	def commit( self ):
		self.grid.SaveEditControlValue()
		self.grid.DisableCellEditControl()	# Make sure the current edit is committed.
		
		model = SeriesModel.model
		
		nameToCompetition = {c.name:c for c in model.competitions}
		
		raceList = []
		for row in range(self.grid.GetNumberRows()):
			fileName = self.grid.GetCellValue(row, self.RaceFileCol).strip()
			pname = self.grid.GetCellValue( row, self.PointsCol )
			pteamname = self.grid.GetCellValue( row, self.TeamPointsCol ) or None
			grade = self.grid.GetCellValue(row, self.GradeCol).strip().upper()[:1]
			if not (grade and ord('A') <= ord(grade) <= ord('Z')):
				grade = 'A'
			pcompetition = self.grid.GetCellValue( row, self.CompetitionCol ).strip()
			competition = nameToCompetition.get( pcompetition, None ) if pcompetition else None
			if not fileName or not pname:
				continue
			raceList.append( (fileName, pname, pteamname, grade, competition) )
		
		racesChanged = model.setRaces( raceList )
		
		if self.seriesName.GetValue() != model.name:
			model.name = self.seriesName.GetValue()
			model.changed = True
			
		if self.organizerName.GetValue() != model.organizer:
			model.organizer = self.organizerName.GetValue()
			model.changed = True
		
		wx.CallAfter( self.refresh )
		if racesChanged and Utils.getMainWin():
			wx.CallAfter( Utils.getMainWin().refreshAll )
		
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
