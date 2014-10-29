import wx
import os
import Utils

class PageDialog( wx.Dialog ):
	def __init__(
			self, parent, pageClass, closeCallback=None, title=_("Change Properties"),
			ID = wx.ID_ANY, size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX,
		):

		if size == wx.DefaultSize:
			size = tuple( int(v*0.5) for v in wx.GetDisplaySize() )
		super( PageDialog, self ).__init__( parent, ID, title=title, size=size, pos=pos, style=style )
		
		# Set the upper left icon.
		icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'CrossMgr16x16.ico'), wx.BITMAP_TYPE_ICO )
		self.SetIcon( icon )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer(sizer)

		self.page = pageClass( self )
		sizer.Add(self.page, 1, flag=wx.ALL|wx.EXPAND, border=5)
		self.closeCallback = closeCallback
				
		self.Bind( wx.EVT_CLOSE, self.onCloseWindow )
		self.Bind( wx.EVT_LEAVE_WINDOW, self.onLeaveWindow )
	
	def refresh( self ):
		if self.page.IsShown():
			try:
				self.page.refresh()
			except AttributeError:
				pass

	def commit( self ):
		if self.page.IsShown():
			try:
				self.page.commit()
			except AttributeError:
				pass
	
	def onCloseWindow( self, event ):
		self.commit()
		if self.closeCallback:
			self.closeCallback()
		event.Skip()
			
	def onLeaveWindow( self, event ):
		self.commit()
		event.Skip()
		
			
			

