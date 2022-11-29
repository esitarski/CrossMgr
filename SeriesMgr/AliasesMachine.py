import wx
import os
import sys
import SeriesModel
import Utils
from AliasGrid import AliasGrid

class AliasesMachine(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		text =	(
			'Machine Aliases match alternate machine names to the same machine.\n'
			'This can be more convenient than editing race results when the same machine appears with a different spelling.\n'
			'\n'
			'To create a machine Alias, first press the "Add Reference Machine" button.\n'
			'The first column is the Machine that will appear in Results.\n'
			'The second column are the Machine Aliases, separated by ";".  These are the alternate machine names.\n'
			'SeriesMgr will match all aliased Machines to the Reference Machine in the Results.\n'
			'\n'
			'For example, Reference Machine="ICE Trike", AliasesMachine="Trice; ICE".  Results for the alternate Machines will appear as "ICE Trike".\n'
			'\n'
			'You can Copy-and-Paste Machines from the Results without retyping them.  Right-click and Copy the name in the Results page,'
			'then Paste the Machine into a Reference Machine or Alias field.\n'
			'Aliased Machines will not be applied until you press the "Refresh" button on the Results screen (or reload).\n'
			'This allows you to configure many Machines without having to wait for the Results update after each change.\n'
		)
		
		self.explain = wx.StaticText( self, label=text )
		self.explain.SetFont( wx.Font((0,15), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False) )
		
		self.addButton = wx.Button( self, label='Add Reference Machine' )
		self.addButton.Bind( wx.EVT_BUTTON, self.onAddButton )
		
		headerNames = ('Machine','Aliases separated by ";"')
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
		
		Utils.AdjustGridSize( self.grid, rowsRequired=len(model.referenceMachines) )
		for row, (reference, aliases) in enumerate(model.referenceMachines):
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
		model.setReferenceMachines( references )
		
#----------------------------------------------------------------------------

class AliasesMachineFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="Machine Aliases Test", size=(800,600) )
		self.panel = AliasesMachine(self)
		self.Show()
 
if __name__ == "__main__":
	app = wx.App(False)
	model = SeriesModel.model
	model.setReferenceMachines( [
		['ICE Trike', ['ICE', 'I.C.E.', 'Trice']],
		['Windcheetah', ['Windy', 'Speedy']],
	] )
	frame = AliasesMachineFrame()
	frame.panel.refresh()
	app.MainLoop()
