import wx
import six
import os
import sys
import SeriesModel
import Utils
from AliasGrid import AliasGrid

def normalizeText( text ):
	return u', '.join( [t.strip() for t in text.split(',')][:2] )

class Aliases(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		text =	(
			u'Name Aliases match different name spellings to the same participant.\n'
			u'This can be more convenient than editing race results when the same participant has resullts under different names.\n'
			u'\n'
			u'To create a name Alias, first press the "Add Reference Name" button.\n'
			u'The first column is the name that will appear in Results.'
			u'Then, add Aliases in the next column separated by ";" (semicolons). These are the alternate spellings of the name.\n'
			u'SeriesMgr will match all Aliases to the Reference Name in the Results.\n'
			u'\n'
			u'For example, Reference Name="Bell, Robert", Aliases="Bell, Bobby; Bell, Bob".  Results for the alternate spellings will appear as "Bell, Robert".\n'
			u'Accents and upper/lower case are ignored.\n'
			u'\n'
			u'You can Copy-and-Paste names from the Results without retyping them.  Right-click and Copy the name in the Results page,'
			u'then Paste the name into the Reference Name or Alias field.\n'
			u'Aliases will not be applied until you press the "Refresh" button on the Results screen (or reload).\n'
			u'This allows you to configure many Aliases without having to wait for the Results update after each change.\n'
		)
		
		self.explain = wx.StaticText( self, label=text )
		self.explain.SetFont( wx.Font((0,15), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False) )
		
		self.addButton = wx.Button( self, label=u'Add Reference Name' )
		self.addButton.Bind( wx.EVT_BUTTON, self.onAddButton )
		
		headerNames = ('Name (Last, First)','Aliases separated by ";"')
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
		defaultText = u''
		
		# Initialize the name from the clipboard.
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
	
	def getName( self, s ):
		name = [t.strip() for t in s.split(u',')[:2]]
		if not name or not any(name):
			return None
		name.extend( [u''] * (2 - len(name)) )
		return tuple( name )
		
	def refresh( self ):
		model = SeriesModel.model
		
		Utils.AdjustGridSize( self.grid, rowsRequired=len(model.references) )
		for row, (reference, aliases) in enumerate(model.references):
			self.grid.SetCellValue( row, 0, u'{}, {}'.format(*reference) )
			self.grid.SetCellValue( row, 1, u'; '.join(u'{}, {}'.format(*a) for a in aliases) )
			
		self.grid.AutoSize()
		self.GetSizer().Layout()
	
	def commit( self ):
		references = []
		
		self.grid.SaveEditControlValue()
		for row in range(self.grid.GetNumberRows()):
			reference = self.getName( self.grid.GetCellValue( row, 0 ) )
			if reference:
				aliases = [a.strip() for a in self.grid.GetCellValue(row, 1).split(';')]
				aliases = [self.getName(a) for a in aliases if a]
				aliases = [a for a in aliases if a]
				references.append( (reference, aliases) )
		
		references.sort()
		
		model = SeriesModel.model
		model.setReferences( references )

#----------------------------------------------------------------------------

class AliasesFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="Aliases Test", size=(800,600) )
		self.panel = Aliases(self)
		self.Show()
 
if __name__ == "__main__":
	app = wx.App(False)
	model = SeriesModel.model
	model.setReferences( [
		[('Bell', 'Robert'), [('Bell', 'Bobby'), ('Bell', 'Bob'), ('Bell', 'B')]],
		[('Sitarski', 'Stephen'), [('Sitarski', 'Steve'), ('Sitarski', 'Steven')]],
	] )
	frame = AliasesFrame()
	frame.panel.refresh()
	app.MainLoop()
