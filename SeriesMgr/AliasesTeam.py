import wx
import os
import sys
import SeriesModel
import Utils
from AliasGrid import AliasGrid

class AliasesTeam(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		text =	(
			'Team Aliases match alternate team names to the same team.\n'
			'This can be more convenient than editing race results when the same team appears with a different spelling.\n'
			'\n'
			'To create a Team Alias, first press the "Add Reference Team" button.\n'
			'The first column is the Team that will appear in Results.\n'
			'The second column are the Team Aliases, separated by ";".  These are the alternate team names.\n'
			'SeriesMgr will match all aliased Teams to the Reference Team in the Results.\n'
			'\n'
			'For example, Reference Team="Cannondale pb Fortius", AliasesTeam="Cannondale; Cannondale Pro".  Results for the alternate Teams will appear as "Cannondale pb Fortius".\n'
			'\n'
			'You can Copy-and-Paste Teams from the Results without retyping them.  Right-click and Copy the name in the Results page,'
			'then Paste the Team into a Reference Team or Alias field.\n'
			'Aliased Teams will not be applied until you press the "Refresh" button on the Results screen (or reload).\n'
			'This allows you to configure many Teams without having to wait for the Results update after each change.\n'
		)
		
		self.explain = wx.StaticText( self, label=text )
		self.explain.SetFont( wx.Font((0,15), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False) )
		
		self.addButton = wx.Button( self, label='Add Reference Team' )
		self.addButton.Bind( wx.EVT_BUTTON, self.onAddButton )
		
		headerNames = ('Team','Aliases separated by ";"')
		self.itemCur = None
		self.grid = AliasGrid( self )
		self.grid.CreateGrid( 0, len(headerNames) )
		self.grid.SetRowLabelSize( 64 )
		for col in range(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, headerNames[col] )

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.explain, 0, flag=wx.ALL, border=4 )
		sizer.Add(self.addButton, 0, flag=wx.ALL, border = 4)
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 4)
		self.SetSizer(sizer)
	
	def onAddButton( self, event ):
		defaultText = ''
		
		# Initialize the team from the clipboard.
		if wx.TheClipboard.Open():
			do = wx.TextDataObject()
			if wx.TheClipboard.GetData(do):
				defaultText = do.GetText()
			wx.TheClipboard.Close()

		self.grid.AppendRows( 1 )
		self.grid.SetCellValue( self.grid.GetNumberRows()-1, 0, defaultText )
		self.grid.AutoSize()
		self.GetSizer().Layout()
		self.grid.MakeCellVisible( self.grid.GetNumberRows()-1, 0 )
	
	def refresh( self ):
		model = SeriesModel.model
		
		Utils.AdjustGridSize( self.grid, rowsRequired=len(model.referenceTeams) )
		for row, (reference, aliases) in enumerate(model.referenceTeams):
			self.grid.SetCellValue( row, 0, reference )
			self.grid.SetCellValue( row, 1, '; '.join(aliases) )
			
		self.grid.AutoSize()
		self.GetSizer().Layout()
	
	def commit( self ):
		references = []
		
		self.grid.SaveEditControlValue()
		for row in range(self.grid.GetNumberRows()):
			reference = self.grid.GetCellValue( row, 0 ).strip()
			if reference:
				aliases = [a.strip() for a in self.grid.GetCellValue(row, 1).split(';')]
				references.append( (reference, sorted( a for a in aliases if a )) )
		
		references.sort()
		
		model = SeriesModel.model
		model.setReferenceTeams( references )
		
#----------------------------------------------------------------------------

class AliasesTeamFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="AliasesTeam Test", size=(800,600) )
		self.panel = AliasesTeam(self)
		self.Show()
 
if __name__ == "__main__":
	app = wx.App(False)
	model = SeriesModel.model
	model.setReferenceTeams( [
		['BC04567', ['BC1234', 'BC5678', 'BC445']],
		['BC04567a', ['BC1234b', 'BC5678c', 'BC445d']],
	] )
	frame = AliasesTeamFrame()
	frame.panel.refresh()
	app.MainLoop()
