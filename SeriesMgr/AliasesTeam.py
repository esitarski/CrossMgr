import wx

import os
import sys
import SeriesModel
import Utils

def getText(parent, message=u'', defaultValue=u'', pos=wx.DefaultPosition):
	dlg = wx.TextEntryDialog(parent, message, defaultValue=defaultValue, pos=pos)
	ret = dlg.ShowModal()
	if ret == wx.ID_OK:
		result = dlg.GetValue()
	else:
		result = None
	dlg.Destroy()
	return result
	
class AliasesTeam(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		text =	(
			u'Team Aliases match alternate team names to the same team.\n'
			u'This can be more convenient than editing race results when the same team appears with a different spelling.\n'
			u'\n'
			u'To create a Team Alias, first press the "Add Reference Team" button.  This is the Team that will appear in Results.'
			u'Then, right-click on the Reference Team you just added, and choose "Add Alias...".  This is an alternate Team.\n'
			u'SeriesMgr will match all aliased Teams to the Reference Team in the Results.\n'
			u'You can have any number of Team Aliases for the same Reference Team.\n'
			u'\n'
			u'For example, Reference Team="Cannondale pb Fortius", AliasesTeam="Cannondale", "Cannondale Pro".  Results for the alternate Teams will appear as "Cannondale pb Fortius".\n'
			u'\n'
			u'You can Copy-and-Paste Teams from the Results without retyping them.  Right-click and Copy the name in the Results page,'
			u'then Paste the Team into a Reference Team or Alias field.\n'
			u'Aliased Teams will not be applied until you press the "Refresh" button on the Results screen (or reload).\n'
			u'This allows you to configure many Teams without having to wait for the Results update after each change.\n'
		)
		
		self.explain = wx.StaticText( self, label=text )
		self.explain.SetFont( wx.Font((0,15), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False) )
		
		self.addButton = wx.Button( self, label=u'Add Reference Team' )
		self.addButton.Bind( wx.EVT_BUTTON, self.onAddButton )
		
		self.itemCur = None
		self.tree = wx.TreeCtrl( self, style = wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS )
		self.tree.AddRoot( u'AliaseTeams' )
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

		text = getText( self, u'Reference Team', defaultText )
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
			
		text = getText( self, u'Alias Team', defaultText )
		if not text:
			return
		item = self.tree.AppendItem( self.itemCur, text )
		self.tree.Expand( self.itemCur )
		self.tree.SortChildren( self.itemCur )
		self.tree.SelectItem( item )
		
	def onEdit( self, event ):
		if not self.itemCur:
			return
		text = getText( self, u'Team', self.tree.GetItemText(self.itemCur) )
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

	def getTeam( self, item ):
		team = self.tree.GetItemText(item)
		if not team:
			return None
		return team
		
	def refresh( self ):
		model = SeriesModel.model
		
		expanded = set()
		r, cookieReference = self.tree.GetFirstChild(self.tree.GetRootItem())
		while r.IsOk():
			if self.tree.GetItemText(r) and self.tree.ItemHasChildren(r) and self.tree.IsExpanded(r):
				expanded.add( self.tree.GetItemText(r) )
			r, cookieReference = self.tree.GetNextChild(r, cookieReference)		
		
		self.tree.DeleteAllItems()
		rootItem = self.tree.AddRoot( u'AliasesTeam' )
		for reference, aliases in model.referenceTeams:
			name = reference
			nameItem = self.tree.AppendItem( rootItem, name )
			for alias in aliases:
				aliasItem = self.tree.AppendItem( nameItem, alias )
			if name in expanded:
				self.tree.Expand( nameItem )
		
		self.tree.ExpandAll()
	
	def commit( self ):
		references = []
		
		r, cookieReference = self.tree.GetFirstChild(self.tree.GetRootItem())
		while r.IsOk():
			name = self.getTeam( r )
			
			if name:
				references.append( [name, []] )
				
				a, cookieAlias = self.tree.GetFirstChild( r )
				while a.IsOk():
					name = self.getTeam( a )
					if name:
						references[-1][1].append( name )
					a, cookieAlias = self.tree.GetNextChild( a, cookieAlias )
				
			r, cookieReference = self.tree.GetNextChild(r, cookieReference)
		
		references.sort()
		for reference, aliases in references:
			aliases.sort()
		
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
	frame.panel.getTree().ExpandAll()
	app.MainLoop()
