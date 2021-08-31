import wx

class PublishPhotoOptionsDialog( wx.Dialog ):
	def __init__( self, parent, webPublish, id=wx.ID_ANY ):
		super().__init__( parent, id, title='CrossMgr Video Photo Publish' )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		explainText = []
		explainText.append( "Write Photos to a folder." )
		if webPublish:
			explainText.append( "Also make a nice .html navigation file." )
		explainText.append( "Make sure you have a separate folder ready for all the files (create one if necessary)." )

		self.explain = wx.StaticText( self, label='\n'.join(explainText) )
		sizer.Add( self.explain, flag=wx.ALL, border=4 )
		
		self.directoryText = wx.StaticText( self, label="Folder for files" )
		self.directory = wx.DirPickerCtrl( self, style=wx.DIRP_DIR_MUST_EXIST )
		
		pfgs = wx.FlexGridSizer( rows=0, cols=2, vgap=4, hgap=8 )
		pfgs.Add( self.directoryText, flag=wx.ALIGN_CENTRE_VERTICAL )
		pfgs.Add( self.directory, 1, flag=wx.EXPAND )
		sizer.Add( pfgs, flag=wx.ALL|wx.EXPAND, border=8 )
		
		choices = (
			'All Laps: Output a Photo for each Trigger',
			'Finishes Only: Output the Last Photo for each Bib/Wave',
		)
		self.lastBibWaveOnlyBox = wx.RadioBox( self, label="Photo Output", choices=choices, majorDimension=len(choices), style=wx.RA_SPECIFY_ROWS )
		self.lastBibWaveOnlyBox.SetSelection( 1 )
		sizer.Add( self.lastBibWaveOnlyBox, flag=wx.ALL|wx.EXPAND, border=8 )
		
		if webPublish:
			choices = (
				'Recommended: .html page links to photos in seperate .jpeg files (requires uploading all the .jpeg and .html files to your web server)',
				'Not Recommended: .html page embeds photos (one single .html file, but huge and inefficient)',
			)
			self.webPageGeneration = wx.RadioBox( self, label="Web Page Generation", choices=choices, majorDimension=len(choices), style=wx.RA_SPECIFY_ROWS )
			self.webPageGeneration.SetSelection( 0 )
			sizer.Add( self.webPageGeneration, flag=wx.ALL|wx.EXPAND, border=8 )
		
		btnSizer = self.CreateButtonSizer( wx.OK|wx.CANCEL )
		wx.FindWindowById( wx.ID_OK, self ).SetDefault()
		
		sizer.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border=8 )
		
		self.SetSizerAndFit( sizer )
		
	def GetValues( self ):
		values = {
			'dirname': self.directory.GetPath(),
			'lastBibWaveOnly': self.lastBibWaveOnlyBox.GetSelection(),
		}
		if hasattr(self, 'webPageGeneration'):
			values['htmlOption'] = self.webPageGeneration.GetSelection()
		return values

if __name__ == '__main__':
	app = wx.App(False)
	
	with PublishPhotoOptionsDialog(None, webPublish=True) as dlg:
		if dlg.ShowModal() == wx.ID_OK:
			print( dlg.GetValues() )
		
	app.MainLoop()
