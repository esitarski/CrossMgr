import wx
import wx.grid as gridlib
import wx.lib.agw.floatspin as FS
import os
import io
import re
import sys
import base64
import SeriesModel
import Utils

def fileToResource( fname ):
	# Get the file type.
	ext = os.path.splitext( fname )[1:].lower()
	# Convert the file contents to base64.
	with open(fname, 'rb') as f:
		b64 = base64.encode( f.read() )
	return 'data:image/{};base64,{}'.format( ext, b64.decode('utf-9') )
	
ext_to_bmp_type = {
	'bmp': wx.BITMAP_TYPE_BMP, # Load a Windows bitmap file.
	'gif': wx.BITMAP_TYPE_GIF, # Load a GIF bitmap file.
	'jpeg': wx.BITMAP_TYPE_JPEG, # Load a JPEG bitmap file.
	'jpg': wx.BITMAP_TYPE_JPEG, # Load a JPEG bitmap file.
	'png': wx.BITMAP_TYPE_PNG, # Load a PNG bitmap file.
}
	
def resourceToImage( imageResource ):
	header, data = imageResource.split( ';', 1 )
	bitmap_type = ext_to_bmp_type[header.split( '/', 1 )[1]]
	b64 = base64.decode( data.split( ',', 1 )[1] )
	return wx.Image( io.BytesIO(b64), bitmap_type )

def getBitmap( model ):
	if model.imageResource is None:
		image = wx.Image( os.path.join(Utils.getImageFolder(), 'SeriesMgr128.png') )
	else:
		image = resourceToImage( model.imageResource )
	return wx.Bitmap( image )

def getImageResource( model ):
	if model.imageResource:
		return model.imageResource
	else:
		return fileToResource( os.path.join(Utils.getImageFolder(), 'SeriesMgr128.png') )

class Options(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		sizer = wx.BoxSizer(wx.VERTICAL)

		#--------------------------------------------------------------------------
		box = wx.StaticBox( self, -1, _("Output Options") )
		bsizer = wx.StaticBoxSizer( box, wx.VERTICAL )
		
		self.showLastToFirst = wx.CheckBox( self, label=_("Show Race Results in Last-to-First Order") )
		self.showLastToFirst.SetValue( True )
		bsizer.Add( self.showLastToFirst, 1, flag=wx.EXPAND )
		
		sizer.Add(bsizer, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		#--------------------------------------------------------------------------
		box = wx.StaticBox( self, -1, _("Input Key Options") )
		bsizer = wx.StaticBoxSizer( box, wx.VERTICAL )
		
		self.riderKey = wx.Choice( self, choices=[
				_("Use First and Last Name to match participants"),
				_("Use UCI ID to match participants"),
				_("Use License to match participants"),
			]
		)
		self.riderKey.SetSelection( SeriesModel.SeriesModel.KeyByName )
		bsizer.Add( self.riderKey )
		bsizer.Add( wx.StaticText(self, label='''
The CrossMgr or Spreadsheet results must include the fields you are using to match.
If you have missing UCI ID or License fields, the safest option is to match
using First and Last Name.'''
		))
		
		sizer.Add(bsizer, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		sizer.Add( wx.StaticLine(self), flag=wx.TOP|wx.BOTTOM, border = 4 )
		
		#--------------------------------------------------------------------------
		box = wx.StaticBox( self, -1, _("Team Results Option") )
		bsizer = wx.StaticBoxSizer( box, wx.VERTICAL )
		
		self.teamResultsOption = wx.Choice( self, choices=[
				_("Show Team Results by Category Only"),
				_("Show Combined Category Team Results Only"),
				_("Show Combined and Category Team Results"),
			]
		)
		self.teamResultsOption.SetSelection( 0 )
		bsizer.Add( self.teamResultsOption )
		
		sizer.Add(bsizer, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		#--------------------------------------------------------------------------

		box = wx.StaticBox( self, -1, _("HTML Color Theme") )
		bsizer = wx.StaticBoxSizer( box, wx.VERTICAL )
		
		self.colorTheme = wx.Choice( self, choices=[
				_("Green"),
				_("Red"),
			]
		)
		self.colorTheme.SetSelection( 0 )
		bsizer.Add( self.colorTheme )
		
		sizer.Add(bsizer, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		#--------------------------------------------------------------------------
		
		self.SetSizer( sizer )
						
	def refresh( self ):
		model = SeriesModel.model
		self.showLastToFirst.SetValue( model.showLastToFirst )
		self.riderKey.SetSelection( model.riderKey )
		self.teamResultsOption.SetSelection( model.teamResultsOption )
		self.colorTheme.SetSelection( model.colorTheme )
	
	def commit( self ):
		model = SeriesModel.model
		av = (
			('showLastToFirst',		self.showLastToFirst.GetValue()),
			('riderKey',			self.riderKey.GetSelection()),
			('teamResultsOption',	self.teamResultsOption.GetSelection()),
			('colorTheme',			self.colorTheme.GetSelection()),
		)
		
		for a, v in av:
			if getattr(model, a) != v:
				setattr( model, a, v )
				model.changed = True
		
########################################################################

class OptionsFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		wx.Frame.__init__(self, None, title="Options Test", size=(800,600) )
		self.panel = Options(self)
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	frame = OptionsFrame()
	frame.panel.refresh()
	app.MainLoop()
