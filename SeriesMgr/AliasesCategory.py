import wx
import SeriesModel
import Utils
from AliasGrid import AliasGrid

import unicodedata
def stripAccentsCase( n ):
	try:
		return unicodedata.normalize("NFD",n).lower()
	except Exception:
		return n

class AliasesCategory(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		text =	(
			'Category Aliases match alternate category names to the same category.\n'
			'This can be more convenient than editing race results when the same category appears with a different spelling.\n'
			'\n'
			'To create a Category Alias, first press the "Add Reference Category" button.\n'
			'The first column is the Category that will appear in Results.\n'
			'The second column are the Category Aliases, separated by ";".  These are the alternate category names.\n'
			'SeriesMgr will match all aliased Categories to the Reference Category in the Results.\n'
			'\n'
			'For example, Reference Category="Cannondale pb Fortius", AliasesCategory="Cannondale; Cannondale Pro".  Results for the alternate Categories will appear as "Cannondale pb Fortius".\n'
			'\n'
			'You can Copy-and-Paste Categories from the Results without retyping them.  Right-click and Copy the name in the Results page,'
			'then Paste the Category into a Reference Category or Alias field.\n'
			'Aliased Categories will not be applied until you press the "Refresh" button on the Results screen (or reload).\n'
			'This allows you to configure many Categories without having to wait for the Results update after each change.\n'
		)
		
		self.explain = wx.StaticText( self, label=text )
		self.explain.SetFont( wx.Font((0,15), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False) )
		
		self.addButton = wx.Button( self, label='Add Reference Category' )
		self.addButton.Bind( wx.EVT_BUTTON, self.onAddButton )
		
		headerNames = ('Category','Aliases separated by ";"')
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
		
		# Initialize the category from the clipboard.
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
		
		Utils.AdjustGridSize( self.grid, rowsRequired=len(model.referenceCategories) )
		for row, (reference, aliases) in enumerate(sorted( model.referenceCategories, key=lambda ra: stripAccentsCase(ra[0])) ):
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
				aliases = set( a.strip() for a in self.grid.GetCellValue(row, 1).split(';') )
				references.append( (reference, sorted( (a for a in aliases if a), key=stripAccentsCase )) )
		
		references.sort( key=lambda ra: stripAccentsCase(ra[0]) )
		
		model = SeriesModel.model
		model.setReferenceCategories( references )
		
#----------------------------------------------------------------------------

class AliasesCategoryFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="AliasesCategory Test", size=(800,600) )
		self.panel = AliasesCategory(self)
		self.Show()
 
if __name__ == "__main__":
	app = wx.App(False)
	model = SeriesModel.model
	model.setReferenceCategories( [
		['BC04567', ['BC1234', 'BC5678', 'BC445']],
		['BC04567a', ['BC1234b', 'BC5678c', 'BC445d']],
	] )
	frame = AliasesCategoryFrame()
	frame.panel.refresh()
	app.MainLoop()
