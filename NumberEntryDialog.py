import wx
from wx.lib.intctrl import IntCtrl

class NumberEntryDialog( wx.Dialog ):
	def __init__( self, parent, message = "Please enter a number.", caption = "Number Entry",
		prompt="Number:", value=None, min=None, max=None ):
		
		super().__init__( parent, title=caption )
		kwargs = {
			'parent': self,
			'min': min,
			'max': max,
			'value': value,
			'limited': True,
			'allow_none': False,
		}
		self.intctrl = IntCtrl( **{k:v for k,v in kwargs.items() if v is not None} )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		if message:
			sizer.Add( wx.StaticText(self, label=message), flag=wx.ALL, border=4 )
		hSizer = wx.BoxSizer( wx.HORIZONTAL )
		if prompt:
			hSizer.Add( wx.StaticText(self, label=prompt), flag=wx.ALIGN_CENTER_VERTICAL )
		hSizer.Add( self.intctrl, 1, flag=wx.EXPAND )
		sizer.Add( hSizer, flag=wx.ALL|wx.EXPAND, border=4 )

		btnsizer = wx.StdDialogButtonSizer()

		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		btnsizer.Realize()

		sizer.Add(btnsizer, 0, flag=wx.ALL, border=5)
		
		self.SetSizer( sizer )
		self.SetSize( 200, 50*(2+int(bool(message))) )
		#self.Fit()

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
