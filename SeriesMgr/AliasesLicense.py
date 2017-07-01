import wx

import os
import sys
import SeriesModel
import Utils
from Aliases import getText

class AliasesLicense(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		text =	(
			u'License Aliases match alternate license codes to the same code.\n'
			u'This can be more convenient than editing race results when the same participant has results under different license codes.\n'
			u'\n'
			u'To create a License Alias, first press the "Add Reference License" button.  This is the license that will appear in Results.'
			u'Then, right-click on the Reference License you just added, and choose "Add Alias...".  This is an alternate license.\n'
			u'SeriesMgr will match all aliased Licenses to the Reference License in the Results.\n'
			u'You can have any number of License Aliases for the same Reference License.\n'
			u'\n'
			u'For example, Reference License="BC03457", AliasesLicense="BC03449", "BC32749".  Results for the alternate licenses will appear as "BC03457".\n'
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
		
		self.itemCur = None
		self.tree = wx.TreeCtrl( self, style = wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS )
		self.tree.AddRoot( u'AliaseLicenses' )
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
		
		# Initialize the license with the clipboard.
		if wx.TheClipboard.Open():
			do = wx.TextDataObject()
			if wx.TheClipboard.GetData(do):
				defaultText = do.GetText()
			wx.TheClipboard.Close()

		text = getText( self, u'Reference License', defaultText )
		if text:
			item = self.tree.PrependItem( self.tree.GetRootItem(), text )
			self.tree.SortChildren( self.tree.GetRootItem() )
			self.tree.Select( item )
	
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
			
		text = getText( self, u'Alias License', defaultText )
		if not text:
			return
		item = self.tree.AppendItem( self.itemCur, text )
		self.tree.Expand( self.itemCur )
		self.tree.SortChildren( self.itemCur )
		self.tree.Select( item )
		
	def onEdit( self, event ):
		if not self.itemCur:
			return
		text = getText( self, u'License', self.tree.GetItemText(self.itemCur) )
		if not text:
			return
		self.tree.SetItemText( self.itemCur, text )
		self.tree.SortChildren( self.tree.GetParent(self.itemCur) )
		self.tree.Select( self.itemCur )
	
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

	def getLicense( self, item ):
		license = self.tree.GetItemText(item).upper()
		if not license:
			return None
		return license
		
	def refresh( self ):
		model = SeriesModel.model
		
		expanded = set()
		r = self.tree.GetFirstChild(self.tree.GetRootItem())
		while r.IsOk():
			if self.tree.GetItemText(r) and self.tree.ItemHasChildren(r) and self.tree.IsExpanded(r):
				expanded.add( self.tree.GetItemText(r) )
			r = self.tree.GetNextChild(r)
		
		self.tree.DeleteAllItems()
		rootItem = self.tree.AddRoot( u'AliasesLicense' )
		for reference, aliases in model.referenceLicenses:
			name = reference
			nameItem = self.tree.AppendItem( rootItem, name )
			for alias in aliases:
				aliasItem = self.tree.AppendItem( nameItem, alias )
			if name in expanded:
				self.tree.Expand( nameItem )
		
		self.tree.ExpandAll()
	
	def commit( self ):
		references = []
		
		r = self.tree.GetFirstChild(self.tree.GetRootItem())
		while r.IsOk():
			name = self.getLicense( r )
			
			if name:
				references.append( [name, []] )
				
				a = self.tree.GetFirstChild( r )
				while a.IsOk():
					name = self.getLicense( a )
					if name:
						references[-1][1].append( name )
					a = self.tree.GetNextChild( a )
				
			r = self.tree.GetNextChild(r)
		
		references.sort()
		for reference, aliases in references:
			aliases.sort()
		
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
	frame.panel.getTree().ExpandAll()
	app.MainLoop()
