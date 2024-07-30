import re

import wx
from ReorderableGrid import ReorderableGrid
import SeriesModel
import Utils
	
class TeamResultsNames(wx.Panel):
	#----------------------------------------------------------------------
	headerNames = ['Team']
	
	iTeamNameCol = 0
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		self.explanation = wx.StaticText( self, label='\n'.join( [
				_("Teams included here will be the only teams used for Team Results."),
				_("If this is empty, all teams will be included."),
			] )
		)
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(self.headerNames) )
		for col in range(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, self.headerNames[col] )
				
		self.gridAutoSize()
		
		self.addButton = wx.Button( self, label='Add Team(s)' )
		self.addButton.Bind( wx.EVT_BUTTON, self.doAddTeamName )

		self.removeButton = wx.Button( self, label='Remove Team' )
		self.removeButton.Bind( wx.EVT_BUTTON, self.doRemoveTeamName )

		fgs = wx.FlexGridSizer( rows=2, cols=2, vgap=2, hgap=2 )
		fgs.AddGrowableCol( 1, proportion=1 )
		
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
	
	def doAddTeamName( self, event ):
		with wx.TextEntryDialog( self, "Enter Team Name(s) (or cut-and-paste from Excel)" ) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				names = re.split( '[\t\n]', dlg.GetValue() )	# Split by tabs and newlines to facilitate pasting from Excel.
				model = SeriesModel.model
				model.setTeamResultsNames( model.teamResultsNames + names )
				wx.CallAfter( self.refresh )
		
	def doRemoveTeamName( self, event ):
		row = self.grid.GetGridCursorRow()
		if row < 0:
			Utils.MessageOK(self, 'No Selected Team.\nPlease Select a Team to Remove.', 'No Selected Team')
			return
		if Utils.MessageOKCancel(self, 'Confirm Remove Team:\n\n    {}'.format( self.grid.GetCellValue(row, self.iTeamNameCol) ), 'Remove Team'):
			self.grid.DeleteRows( row )
			self.commit()
	
	def gridAutoSize( self ):
		self.grid.AutoSize()
		self.grid.EnableDragGridSize( False )
		self.grid.EnableDragColSize( False )
		self.Layout()
		self.Refresh()
	
	def refresh( self ):
		model = SeriesModel.model
		Utils.AdjustGridSize( self.grid, len(model.teamResultsNames) )
		for row, teamName in enumerate(model.teamResultsNames):
			self.grid.SetCellValue( row, self.iTeamNameCol, teamName )
		wx.CallAfter( self.gridAutoSize )
	
	def commit( self ):
		self.grid.SaveEditControlValue()
		self.grid.DisableCellEditControl()	# Make sure the current edit is committed.
		
		teamList = []
		for row in range(self.grid.GetNumberRows()):
			teamList.append( self.grid.GetCellValue(row, self.iTeamNameCol).strip() )
		
		model = SeriesModel.model
		if model.setTeamResultsNames( teamList ):
			wx.CallAfter( self.refresh )
		
#----------------------------------------------------------------------------

class TeamResultsNamesFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		wx.Frame.__init__(self, None, title="TeamResultsNames Test", size=(800,600) )
		self.panel = TeamResultsNames(self)
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	frame = TeamResultsNamesFrame()
	frame.panel.refresh()
	app.MainLoop()
