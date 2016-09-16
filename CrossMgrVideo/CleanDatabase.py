import wx
import datetime

class CleanDatabase( wx.Dialog ):
	def __init__( self, parent, dbSize, id=wx.ID_ANY, title='', size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE ):
		super(CleanDatabase, self).__init__( parent, id, title=title, size=size, style=style )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		vs.Add( wx.StaticText(self, label='Current Database Size: {:.1f} meg'.format(dbSize/1048576.0)),
			flag=wx.ALL, border=4 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		
		hs.Add( wx.StaticText(self, label='Delete all data before') )
		tQuery = datetime.datetime.now() - datetime.timedelta(days=7)
		self.date = wx.DatePickerCtrl(
			self,
			dt=wx.DateTimeFromDMY( tQuery.day, tQuery.month-1, tQuery.year ),
			style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY
		)
		hs.Add( self.date, flag=wx.LEFT, border=4 )

		vs.Add( hs, flag=wx.ALL, border=4)
		
		vs.Add( wx.StaticText(self, label='Be Careful!  There is no undo.'), flag=wx.ALL, border=4 )
		
		btnsizer = wx.StdDialogButtonSizer()
        
		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		btnsizer.Realize()

		vs.Add( btnsizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5 )

		self.SetSizer(vs)
		vs.Fit(self)
		
	def GetDate( self ):
		v = self.date.GetValue()
		return datetime.datetime( v.GetYear(), v.GetMonth() + 1, v.GetDay() )

if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CleanDatabase", size=(200,100))
	mainWin.Show()
	
	dlg = CleanDatabase( mainWin, 1000000 )
	print dlg.ShowModal() == wx.ID_OK
	dlg.Destroy()
	
	app.MainLoop()
