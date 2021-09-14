import wx
import os
import imagebrowser
import Utils

#------------------------------------------------------------------------------------------------
class SetGraphicDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY, graphic = None ):
		super().__init__( parent, id, "Set Graphic",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		label = wx.StaticText( self, label = _('Graphic to be Displayed in Results (set to blank to use default graphic):') )
		mainSizer.Add( label, flag = wx.ALL, border = 4 )
		
		bhh = wx.BoxSizer( wx.HORIZONTAL )
		
		self.chooseButton = wx.Button( self, label = _('Choose...') )
		bhh.Add( self.chooseButton, flag = wx.ALL, border = 4 )
		self.Bind( wx.EVT_BUTTON, self.onChoose, self.chooseButton )

		self.graphic = wx.TextCtrl( self, size=(600,-1) )
		if graphic:
			self.graphic.SetValue( graphic )
		bhh.Add( self.graphic, flag = wx.ALL | wx.EXPAND, border = 4 )
		
		mainSizer.Add( bhh )
		
		btnSizer = self.CreateStdDialogButtonSizer( wx.OK|wx.CANCEL )
		if btnSizer:
			mainSizer.Add( btnSizer, flag = wx.EXPAND|wx.ALL, border = 4 )
		self.SetSizerAndFit( mainSizer )

	def GetValue( self ):
		return self.graphic.GetValue()
		
	def onChoose( self, event ):
		imgPath = self.GetValue()
		set_dir = os.path.dirname(imgPath)
		with imagebrowser.ImageDialog( self, set_dir = set_dir ) as dlg:
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
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="SprintMan" )
	mainWin.Show()
	setGraphicDialog = SetGraphicDialog( mainWin, -1, "Set Graphic Dialog Test" )
	setGraphicDialog.ShowModal()
	app.MainLoop()
