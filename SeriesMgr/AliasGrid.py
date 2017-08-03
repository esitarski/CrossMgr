import wx.grid as gridlib
import wx.lib.mixins.grid as gae
from ReorderableGrid import KeyboardNavigationGridMixin, SaveEditWhenFocusChangesGridMixin

class AliasGrid(	gridlib.Grid,
						KeyboardNavigationGridMixin,
						SaveEditWhenFocusChangesGridMixin,
						gae.GridAutoEditMixin ):
	def __init__( self, parent, style = 0 ):
		gridlib.Grid.__init__( self, parent, style=style )
		KeyboardNavigationGridMixin.__init__( self )
		SaveEditWhenFocusChangesGridMixin.__init__( self )
		gae.GridAutoEditMixin.__init__(self)
