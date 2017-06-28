import wx

import os
import sys
import SeriesModel
import Utils

def normalizeText( text ):
	return u', '.join( [t.strip() for t in text.split(',')][:2] )

def getText(parent, message=u'', defaultValue=u'', pos=wx.DefaultPosition):
	dlg = wx.TextEntryDialog(parent, message, value=defaultValue, pos=pos)
	ret = dlg.ShowModal()
	if ret == wx.ID_OK:
		result = normalizeText( dlg.GetValue() )
	else:
		result = None
	dlg.Destroy()
	return result
	
class Aliases(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		text =	(
			u'Name Aliases match different name spellings to the same participant.\n'
			u'This can be more convenient than editing race results when the same participant has resullts under different names.\n'
			u'\n'
			u'To create a name Alias, first press the "Add Reference Name" button.  This is the name that will appear in Results.'
			u'Then, right-click on the Reference Name you just added, and choose "Add Alias...".  This is an alternate spelling.\n'
			u'SeriesMgr will match all Aliases to the Reference Name in the Results.\n'
			u'You can have any number of Aliases for the same Reference Name.\n'
			u'\n'
			u'For example, Reference Name="Bell, Robert", Aliases="Bell, Bobby", "Bell, Bob".  Results for the alternate spellings will appear as "Bell, Robert".\n'
			u'Accents and upper/lower case are ignored.\n'
			u'\n'
			u'You can Copy-and-Paste names from the Results without retyping them.  Right-click and Copy the name in the Results page,'
			u'then Paste the name into a Reference Name or Alias field.\n'
			u'Aliases will not be applied until you press the "Refresh" button on the Results screen (or reload).\n'
			u'This allows you to configure many Aliases without having to wait for the Results update after each change.\n'
		)
		
		self.explain = wx.StaticText( self, label=text )
		self.explain.SetFont( wx.Font((0,15), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False) )
		
		self.addButton = wx.Button( self, label=u'Add Reference Name' )
		self.addButton.Bind( wx.EVT_BUTTON, self.onAddButton )
		
		self.itemCur = None
		self.tree = wx.TreeCtrl( self, style = wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS )
		self.tree.AddRoot( u'Aliases' )
		self.tree.Bind( wx.EVT_TREE_ITEM_RIGHT_CLICK, self.onTreeRightClick )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.explain, 0, flag=wx.ALL, border=4 )
		sizer.Add(self.addButton, 0, flag=wx.ALL, border = 4)
		sizer.Add(self.tree, 1, flag=wx.EXPAND|wx.ALL, border = 4)
		self.SetSizer(sizer)
	
	def onTreeRightClick( self, event ):
		item = event.GetItem()
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				(u'{}...'.format(_('Add Alias')),	wx.NewId(), self.onAddAlias),
				(u'{}...'.format(_('Edit')),		wx.NewId(), self.onEdit),
				(u'{}...'.format(_('Delete')),		wx.NewId(), self.onDelete),
				(u'{}...'.format(_('Copy to Clipboard')),	wx.NewId(), self.onCopy),
			]
			for p in self.popupInfo:
				if p[2]:
					self.Bind( wx.EVT_MENU, p[2], id=p[1] )

		menu = wx.Menu()
		for i, p in enumerate(self.popupInfo[0 if self.tree.GetItemParent(item) == self.tree.GetRootItem() else 1:]):
			if p[2]:
				menu.Append( p[1], p[0] )
			else:
				menu.AppendSeparator()
		
		self.itemCur = item
		self.PopupMenu( menu )
		menu.Destroy()
	
	def onCopy( self, event ):
		if not self.itemCur:
			return
			
		if wx.TheClipboard.Open():
			# Create a wx.TextDataObject
			do = wx.TextDataObject()
			do.SetText( self.tree.GetItemText(self.itemCur) )

			# Add the data to the clipboard
			wx.TheClipboard.SetData(do)
			# Close the clipboard
			wx.TheClipboard.Close()
		else:
			wx.MessageBox(u"Unable to open the clipboard", u"Error")
	
	def onAddButton( self, event ):
		defaultText = u''
		
		# Initialize the name with the clipboard.
		if wx.TheClipboard.Open():
			do = wx.TextDataObject()
			if wx.TheClipboard.GetData(do):
				defaultText = do.GetText()
			wx.TheClipboard.Close()

		text = getText( self, u'Reference Name (Last, First)', defaultText )
		if text:
			item = self.tree.PrependItem( self.tree.GetRootItem(), text )
			self.tree.SortChildren( self.tree.GetRootItem() )
			self.tree.SelectItem( item )
	
	def onAddAlias( self, event ):
		if not self.itemCur:
			return
			
		defaultText = self.tree.GetItemText(self.itemCur)
		# Initialize the name with the clipboard.
		if wx.TheClipboard.Open():
			do = wx.TextDataObject()
			if wx.TheClipboard.GetData(do):
				defaultText = do.GetText()
			wx.TheClipboard.Close()
			
		text = getText( self, u'Alias (First, Last)', defaultText )
		if not text:
			return
		item = self.tree.AppendItem( self.itemCur, text )
		self.tree.Expand( self.itemCur )
		self.tree.SortChildren( self.itemCur )
		self.tree.SelectItem( item )
		
	def onEdit( self, event ):
		if not self.itemCur:
			return
		text = getText( self, u'Name (First, Last)', self.tree.GetItemText(self.itemCur) )
		if not text:
			return
		self.tree.SetItemText( self.itemCur, text )
		self.tree.SortChildren( self.tree.GetParent(self.itemCur) )
		self.tree.SelectItem( self.itemCur )
	
	def onDelete( self, event ):
		if not self.itemCur:
			return
		dlg = wx.MessageDialog( self, u'Confirm Delete:\n\n    {}'.format(self.tree.GetItemText(self.itemCur)), u'Confirm Delete')
		ret = dlg.ShowModal()
		if ret == wx.ID_OK:
			self.tree.Delete( self.itemCur )
			self.itemCur = None
		dlg.Destroy()
	
	def getTree( self ):
		return self.tree

	def getName( self, item ):
		name = [t.strip() for t in self.tree.GetItemText(item).split(u',')[:2]]
		if not name:
			return None
		name.extend( [u''] * (2 - len(name)) )
		return tuple( name )
		
	def refresh( self ):
		model = SeriesModel.model
		
		expanded = set()
		r, cookieReference = self.tree.GetFirstChild(self.tree.GetRootItem())
		while r.IsOk():
			if self.tree.GetItemText(r) and self.tree.ItemHasChildren(r) and self.tree.IsExpanded(r):
				expanded.add( self.tree.GetItemText(r) )
			r, cookieReference = self.tree.GetNextChild(r, cookieReference)		
		
		self.tree.DeleteAllItems()
		rootItem = self.tree.AddRoot( u'Aliases' )
		for reference, aliases in model.references:
			name = u'{}, {}'.format(*reference)
			nameItem = self.tree.AppendItem( rootItem, name )
			for alias in aliases:
				aliasItem = self.tree.AppendItem( nameItem, u'{}, {}'.format(*alias) )
			if name in expanded:
				self.tree.Expand( nameItem )
		
		self.tree.ExpandAll()
	
	def commit( self ):
		references = []
		
		r, cookieReference = self.tree.GetFirstChild(self.tree.GetRootItem())
		while r.IsOk():
			name = self.getName( r )
			
			if name:
				references.append( [name, []] )
				
				a, cookieAlias = self.tree.GetFirstChild( r )
				while a.IsOk():
					name = self.getName( a )
					if name:
						references[-1][1].append( name )
					a, cookieAlias = self.tree.GetNextChild( a, cookieAlias )
				
			r, cookieReference = self.tree.GetNextChild(r, cookieReference)
		
		references.sort()
		for reference, aliases in references:
			aliases.sort()
		
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
	frame.panel.getTree().ExpandAll()
	app.MainLoop()
