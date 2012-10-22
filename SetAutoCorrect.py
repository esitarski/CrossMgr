import Utils
from Utils				import logCall
import wx
import Model
from Undo import undo
import math

#------------------------------------------------------------------------------------------------
class SetAutoCorrectDialog( wx.Dialog ):
	def __init__( self, parent, categories, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Correct Number",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		self.categories = categories
		self.categoryNames = ['All'] + [c.name for c in categories]
		vs = wx.BoxSizer(wx.VERTICAL)
		
		font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)
		self.title1 = wx.StaticText( self, wx.ID_ANY, "Change the Autocorrect Flag by Category" )
		self.title1.SetFont( font )
		self.title2 = wx.StaticText( self, wx.ID_ANY, "Select Categories:" )
		
		self.categoryList = wx.ListBox( self, wx.ID_ANY, style=wx.LB_MULTIPLE, choices=self.categoryNames )
		
		self.title3 = wx.StaticText( self, wx.ID_ANY, "For all Riders in the Categories above:" )
		self.setBtn = wx.Button( self, wx.ID_ANY, 'Set Autocorrect Flag' )
		self.Bind( wx.EVT_BUTTON, self.onSetAutocorrect, self.setBtn )

		self.clearBtn = wx.Button( self, wx.ID_ANY, 'Clear Autocorrect Flag' )
		self.Bind( wx.EVT_BUTTON, self.onClearAutocorrect, self.clearBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )

		border = 4
		vs.Add( self.title1, border = border, flag = wx.ALL|wx.EXPAND )
		vs.Add( self.title2, border = border, flag = wx.ALL|wx.EXPAND )
		vs.Add( self.categoryList, border = border, flag = wx.ALL|wx.EXPAND )
		vs.Add( self.title3, border = border, flag = wx.ALL|wx.EXPAND )
		vs.Add( self.setBtn, border = border, flag = wx.ALL|wx.EXPAND )
		vs.Add( self.clearBtn, border = border, flag = wx.ALL|wx.EXPAND )
		vs.Add( self.cancelBtn, border = border, flag = wx.ALL|wx.ALIGN_RIGHT )
		
		self.SetSizerAndFit(vs)
		vs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def doSet( self, action ):
		selections = self.categoryList.GetSelections()
		if not selections:
			return
		
		if 0 in selections:
			doAll = True
			selectedCats = []
		else:
			doAll = False
			selectedCats = [self.categories[s-1] for s in selections]
		undo.pushState()
		with Model.LockRace() as race:
			for num, rider in race.riders.iteritems():
				if doAll or race.getCategory(num) in selectedCats:
					rider.autocorrectLaps = action
				race.setChanged()
		Utils.refresh()
		
	@logCall
	def onSetAutocorrect( self, event ):
		self.doSet( True )
		self.EndModal( wx.ID_OK )
		
	@logCall
	def onClearAutocorrect( self, event ):
		self.doSet( False )
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
