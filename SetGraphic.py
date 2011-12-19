import wx
import os
import imagebrowser

#------------------------------------------------------------------------------------------------
class SetGraphicDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY, graphic = None ):
		wx.Dialog.__init__( self, parent, id, "Set Graphic",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		label = wx.StaticText( self, wx.ID_ANY, 'Graphic Displayed in Results:' )
		mainSizer.Add( label, flag = wx.ALL, border = 4 )
		
		bhh = wx.BoxSizer( wx.HORIZONTAL )
		
		self.chooseButton = wx.Button( self, wx.ID_ANY, 'Choose...' )
		bhh.Add( self.chooseButton, flag = wx.ALL, border = 4 )
		self.Bind( wx.EVT_BUTTON, self.onChoose, self.chooseButton )

		self.graphic = wx.TextCtrl( self, wx.ID_ANY, size=(600,-1) )
		if graphic:
			self.graphic.SetValue( graphic )
		bhh.Add( self.graphic, flag = wx.ALL | wx.EXPAND, border = 4 )
		
		mainSizer.Add( bhh )
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		bh = wx.StdDialogButtonSizer()
		bh.AddButton( self.okBtn )
		bh.AddButton( self.cancelBtn )
		bh.Realize()
		
		mainSizer.Add( bh, flag = wx.ALIGN_RIGHT | wx.ALL, border = 4 )
		self.SetSizerAndFit( mainSizer )

	def GetValue( self ):
		return self.graphic.GetValue()
		
	def onChoose( self, event ):
		imgPath = self.GetValue()
		set_dir = os.path.dirname(imgPath)
		dlg = imagebrowser.ImageDialog( self, set_dir = set_dir )
		dlg.ChangeFileTypes([
			('All Formats (GIF, PNG, JPEG)', '*.gif|*.png|*.jpg'),
			('GIF (*.gif)', '*.gif'),
			('PNG (*.png)', '*.png'),
			('JPEG (*.jpg)', '*.jpg')
		])
		if os.path.isfile(imgPath):
			dlg.SetFileName( imgPath )
		if dlg.ShowModal() == wx.ID_OK:
			imgPath = dlg.GetFile()
			self.graphic.SetValue( imgPath )
		dlg.Destroy()

	def onOK( self, event ):
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan" )
	mainWin.Show()
	setGraphicDialog = SetGraphicDialog( mainWin, -1, "Set Graphic Dialog Test" )
	setGraphicDialog.ShowModal()
	app.MainLoop()
