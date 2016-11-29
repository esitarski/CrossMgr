import wx

import os
import sys
import SeriesModel
import Utils

def normalizeText( text ):
	return u', '.join( [t.strip() for t in text.split(',')][:2] )

def getText(parent, message=u'', defaultValue=u'', pos=wx.DefaultPosition):
	dlg = wx.TextEntryDialog(parent, message, defaultValue=defaultValue, pos=pos)
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
			u'Aliases allow you to match different name spellings to the same participant.\n'
			u'This can be more convenient than going into all your races to make the name spelling consistent.\n'
			u'\n'
			u'To use, add a Reference Name.  Then, right-click on the Reference Name to add Aliases (different spellings).\n'
			u'SeriesMgr will then match all Aliases to the Reference Name in the results.\n'
			u'\n'
			u'For example, if Reference Name="Bell, Robert", Aliases="Bell, Bobby", "Bell, Bob", those alternate spellings will match "Bell, Robert".\n'
			u'\n'
			u'Accents and upper/lower case are ignored.\n'
			u'\n'
			u'Copy names from the Results screen by right-clicking in the table.\n'
		)
		
		self.explain = wx.StaticText( self, label=text )
		
		self.addButton = wx.Button( self, label=u'Add Reference Name' )
		self.addButton.Bind( wx.EVT_BUTTON, self.onAddButton )
		
		self.itemCur = None
		self.tree = wx.TreeCtrl( self, style = wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS )
		self.tree.Bind( wx.EVT_TREE_ITEM_RIGHT_CLICK, self.onTreeRightClick )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.explain, 0, flag=wx.ALL, border=6 )
		sizer.Add(self.addButton, 0, flag=wx.ALL, border = 6)
		sizer.Add(self.tree, 1, flag=wx.EXPAND|wx.ALL, border = 6)
		self.SetSizer(sizer)
	
	def onTreeRightClick( self, event ):
		item = event.GetItem()
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				(u'{}...'.format(_('Add Alias')),	wx.NewId(), self.onAddAlias),
				(u'{}...'.format(_('Edit')),		wx.NewId(), self.onEdit),
				(u'{}...'.format(_('Delete')),		wx.NewId(), self.onDelete),
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
	
	def onAddButton( self, event ):
		defaultText = u''
		
		# Initialize the name with the clipboard.
		if wx.TheClipboard.Open():
			# Create a wx.TextDataObject
			do = wx.TextDataObject()
			# Get the data from the clipboard
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
		text = getText( self, u'Alias (First, Last)', self.tree.GetItemText(self.itemCur) )
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

	def refresh( self ):
		model = SeriesModel.model
		self.tree.DeleteAllItems()
		rootItem = self.tree.AddRoot( u'Aliases' )
		for name, aliases in model.aliases:
			nameItem = self.tree.AppendItem( rootItem, u'{}, {}'.format(*name) )
			for a in aliases:
				aliasItem = self.tree.AppendItem( nameItem, u'{}, {}'.format(*a) )
	
	def commit( self ):
		aliases = []
		a, cookieRoot = self.tree.GetFirstChild(self.tree.GetRootItem())
		
		def getName( item ):
			name = [t.strip() for t in self.tree.GetItemText(item).split(u',')[:2]]
			if not name:
				return None
			name.extend( [u''] * (2 - len(name)) )
			return tuple( name )
		
		while a.IsOk():
			name = getName( a )
			
			if name:
				aliases.append( [name, []] )
				
				v, cookieAlias = self.tree.GetFirstChild( a )
				while v.IsOk():
					name = getName( item )
					if name:
						aliases[-1][1].append( name )
					v, cookieAlias = self.tree.GetNextChild( a, cookieAlias )
				
			a, cookieRoot = self.tree.GetNextChild(a, cookieRoot)
		
		aliases.sort()
		for name, aliases in aliases:
			aliases.sort()
		
		model = SeriesModel.model
		model.setAliases( aliases )
		
#----------------------------------------------------------------------------

class AliasesFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="Aliases Test", size=(800,600) )
		self.panel = Aliases(self)
		self.Show()
 
if __name__ == "__main__":
	app = wx.App(False)
	model = SeriesModel.model
	model.setAliases( [
		[['Bell', 'Robert'], [('Bell', 'Bobby'), ('Bell', 'Bob'), ('Bell', 'B')]],
		[['Sitarski', 'Stephen'], [('Sitarski', 'Steve'), ('Sitarski', 'Steven')]],
	] )
	frame = AliasesFrame()
	frame.panel.refresh()
	frame.panel.getTree().ExpandAll()
	app.MainLoop()
