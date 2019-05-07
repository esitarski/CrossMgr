import wx
import six
import os
import sys
import SeriesModel
import Utils
from AliasGrid import AliasGrid

class AliasesLicense(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		text =	(
			u'License Aliases match alternate license codes to the same code.\n'
			u'This can be more convenient than editing race results when the same participant has results under different license codes.\n'
			u'\n'
			u'To create a License Alias, first press the "Add Reference License" button.\n'
			u'The first column is the license that will appear in Results.\n'
			u'Then, add license aliases in the next column.  These are the alternate licenses.\n'
			u'SeriesMgr will match all aliased Licenses to the Reference License in the Results.\n'
			u'\n'
			u'For example, Reference License="BC03457", Aliases="BC03449; BC32749".  Results for the alternate licenses will appear as "BC03457".\n'
			u'\n'
			u'You can Copy-and-Paste licenses from the Results without retyping them.  Right-click and Copy the name in the Results page,'
			u'then Paste the license into a Reference License or Alias field.\n'
			u'Aliased Licenses will not be applied until you press the "Refresh" button on the Results screen (or reload).\n'
			u'This allows you to configure many licenses without having to wait for the Results update after each change.\n'
		)
		
		self.explain = wx.StaticText( self, label=text )
		self.explain.SetFont( wx.Font((0,15), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False) )
		
		self.addButton = wx.Button( self, label=u'Add Reference License' )
		self.addButton.Bind( wx.EVT_BUTTON, self.onAddButton )
		
		headerNames = ('License','Aliases separated by ";"')
		self.itemCur = None
		self.grid = AliasGrid( self )
		self.grid.CreateGrid( 0, len(headerNames) )
		self.grid.SetRowLabelSize( 64 )
		for col in six.moves.range(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, headerNames[col] )

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.explain, 0, flag=wx.ALL, border=4 )
		sizer.Add(self.addButton, 0, flag=wx.ALL, border = 4)
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 4)
		self.SetSizer(sizer)
	
	def onAddButton( self, event ):
		defaultText = u''
		
		# Initialize the license from the clipboard.
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
		
		Utils.AdjustGridSize( self.grid, rowsRequired=len(model.referenceLicenses) )
		for row, (reference, aliases) in enumerate(model.referenceLicenses):
			self.grid.SetCellValue( row, 0, reference )
			self.grid.SetCellValue( row, 1, u'; '.join(aliases) )
			
		self.grid.AutoSize()
		self.GetSizer().Layout()
	
	def commit( self ):
		references = []
		
		self.grid.SaveEditControlValue()
		for row in six.moves.range(self.grid.GetNumberRows()):
			reference = self.grid.GetCellValue( row, 0 ).strip()
			if reference:
				aliases = [a.strip() for a in self.grid.GetCellValue(row, 1).split(';')]
				references.append( (reference, sorted( a for a in aliases if a )) )
		
		references.sort()
		
		model = SeriesModel.model
		model.setReferenceLicenses( references )
		
#----------------------------------------------------------------------------

class AliasesLicenseFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="AliasesLicense Test", size=(800,600) )
		self.panel = AliasesLicense(self)
		self.Show()
 
if __name__ == "__main__":
	app = wx.App(False)
	model = SeriesModel.model
	model.setReferenceLicenses( [
		['BC04567', ['BC1234', 'BC5678', 'BC445']],
		['BC04567a', ['BC1234b', 'BC5678c', 'BC445d']],
	] )
	frame = AliasesLicenseFrame()
	frame.panel.refresh()
	app.MainLoop()
