import wx
from wx.lib.intctrl import IntCtrl

class NumberEntryDialog( wx.Dialog ):
	def __init__( self, parent, message = "Please enter a number.", caption = "Number Entry",
		prompt="Number:", value=None, min=None, max=None ):
		
		super( NumberEntryDialog, self ).__init__( parent, title=caption )
		kwargs = {
			'parent': self,
			'min': min,
			'max': max,
			'value': value,
			'limited': True,
			'allow_none': False,
		}
		self.intctrl = IntCtrl( **{k:v for k,v in kwargs.iteritems() if v is not None} )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		if message:
			mainSizer.Add( wx.StaticText(self, label=message), flag=wx.ALL, border=4 )
		hSizer = wx.BoxSizer( wx.HORIZONTAL )
		if prompt:
			hSizer.Add( wx.StaticText(self, label=prompt), flag=wx.ALIGN_CENTER_VERTICAL )
		hSizer.Add( self.intctrl )
		mainSizer.Add( hSizer, flag=wx.ALL, border=4 )
		
		buttonSizer = wx.BoxSizer( wx.HORIZONTAL )
		okButton = wx.Button( self, wx.ID_OK )
		okButton.SetDefault()
		buttonSizer.Add( okButton )
		buttonSizer.AddStretchSpacer()
		buttonSizer.Add( wx.Button(self, wx.ID_CANCEL) )
		mainSizer.Add( buttonSizer, flag=wx.ALL|wx.EXPAND, border = 8 )
		
		self.SetSizer( mainSizer )
		self.Fit()
		self.CenterOnParent() 
		
	def SetValue( self, v ):
		self.intctrl.SetValue( v )
		
	def GetValue( self ):
		return self.intctrl.GetValue()

if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMgr", size=(600,400))
	ned = NumberEntryDialog( mainWin )
	ned.Show()
	app.MainLoop()
