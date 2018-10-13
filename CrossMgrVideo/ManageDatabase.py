import wx
import wx.adv
import datetime
import os

DatePickerCtrl = wx.adv.DatePickerCtrl

class ManageDatabase( wx.Dialog ):
	def __init__( self, parent, dbSize, dbName, trigFirst, trigLast, id=wx.ID_ANY, title='', size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE ):
		super(ManageDatabase, self).__init__( parent, id, title=title, size=size, style=style )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		self.dbName = dbName
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( wx.StaticText(self, label='Database File:'), flag=wx.ALIGN_CENTER_VERTICAL )
		self.dbNameText = wx.TextCtrl(self, value=dbName, style=wx.TE_READONLY, size=(300,-1))
		hs.Add( self.dbNameText, flag=wx.LEFT, border=4 )
		vs.Add( hs, flag=wx.ALL, border=4 )
		
		self.changeDirButton = wx.Button( self, label='Change Database Folder' )
		self.changeDirButton.Bind( wx.EVT_BUTTON, self.doChangeDir )
		vs.Add( self.changeDirButton, flag=wx.ALL, border=4 )
			
		self.dbSizeText = wx.StaticText(self)
		self.setDbSize( dbSize )
		vs.Add( self.dbSizeText, flag=wx.ALL, border=4 )
		vs.Add( wx.StaticText(
					self,
					label='Triggers Recorded from {}  to {} '.format(
						trigFirst.strftime('%Y-%m-%d') if trigFirst else '',
						trigLast.strftime('%Y-%m-%d') if trigLast else ''
					),
			),
			flag=wx.ALL, border=4
		)
		
		vs.Add( wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.ALL|wx.EXPAND, border=4 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( wx.StaticText(self, label='Delete all data (inclusive) from'), flag=wx.ALIGN_CENTER_VERTICAL )
		tQuery = datetime.datetime.now() - datetime.timedelta(days=7)
		self.dateFrom = DatePickerCtrl(
			self,
			dt=wx.DateTime.FromDMY( tQuery.day, tQuery.month-1, tQuery.year ),
			style=wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE
		)
		hs.Add( self.dateFrom, flag=wx.LEFT, border=4 )
		
		hs.Add( wx.StaticText(self, label='to'), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4 )
		tQuery = datetime.datetime.now() - datetime.timedelta(days=1)
		self.dateTo = DatePickerCtrl(
			self,
			dt=wx.DateTime.FromDMY( tQuery.day, tQuery.month-1, tQuery.year ),
			style=wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY|wx.adv.DP_ALLOWNONE
		)
		hs.Add( self.dateTo, flag=wx.LEFT, border=4 )

		vs.Add( hs, flag=wx.ALL, border=4)
		
		vs.Add( wx.StaticText(self, label='(uncheck date fields to get min and max values)'), flag=wx.ALL|wx.ALIGN_RIGHT, border=4 )
		
		vs.Add( wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.ALL|wx.EXPAND, border=4 )		

		self.vacuum = wx.CheckBox( self, label='Vacuum Database (reduces file size but may take a few minutes)' )
		self.vacuum.SetValue( False )
		vs.Add( self.vacuum, flag=wx.ALL, border=4 )
		
		vs.Add( wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.ALL|wx.EXPAND, border=4 )		

		vs.Add( wx.StaticText(self, label='Be Careful!  There is no undo.'), flag=wx.ALL, border=4 )
		
		btnsizer = wx.StdDialogButtonSizer()
        
		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		btnsizer.Realize()

		vs.Add( btnsizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, border=5 )

		self.SetSizer(vs)
		vs.Fit(self)
	
	def setDbSize( self, dbSize ):
		self.dbSizeText.SetLabel( 'Database Size: {:.1f} meg'.format(dbSize/1048576.0) )
	
	def doChangeDir( self, event ):
		dbDir = os.path.dirname( self.dbName )
		dlg = wx.DirDialog( None, "Choose database directory", dbDir, wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST )
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.dbName = os.path.join( path, os.path.basename(self.dbName) )
			self.dbNameText.SetValue( self.dbName )
	
	def GetValues( self ):
		v = self.dateFrom.GetValue()
		dateFrom = datetime.datetime( v.GetYear(), v.GetMonth() + 1, v.GetDay() ) if v else None
		v = self.dateTo.GetValue()
		dateTo = datetime.datetime( v.GetYear(), v.GetMonth() + 1, v.GetDay() ) if v else None
		vacuum = self.vacuum.GetValue()
		return dateFrom, dateTo, vacuum, self.dbName

if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="ManageDatabase", size=(200,100))
	mainWin.Show()
	
	dlg = ManageDatabase( mainWin, 1000000, 'TestDatabase', None, None )
	print dlg.ShowModal() == wx.ID_OK
	print dlg.GetValues()
	dlg.Destroy()
	
	app.MainLoop()
