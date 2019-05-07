import wx
import six
from ScaledBitmap import ScaledBitmap

class FramesViewer( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, rows=5, cols=12, size=(640,480), style=0 ):
		super(FramesViewer, self).__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		
		self.scaledBitmaps = [ScaledBitmap(self, size=(64,48)) for i in six.moves.range(rows*cols)]
		for si in self.scaledBitmaps:
			si.SetTestBitmap()
			
		self.cols = cols
		self.rows = rows
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( sizer )
		
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.OnSize()
		
	def GetBitmapCount( self ):
		return len(self.scaledBitmaps)
				
	def SetBitmaps( self, images ):
		for i, si in enumerate(self.scaledBitmaps):
			try:
				si.SetBitmap( images[i] )
			except IndexError:
				si.SetTestBitmap()
				
	def OnSize( self, event = None ):
		widthWindow, heightWindow = self.GetClientSize()
		
		sep = 2
		width = int((widthWindow - (self.cols-1) * sep) / float(self.cols))
		height = int(width * 480.0 / 640.0)
		
		xMax = widthWindow - width/2
		x = 0
		y = 0
		for si in self.scaledBitmaps:
			si.SetSize( (width, height) )
			si.Move( (x, y) )
			x += width + sep
			if x > xMax:
				x = 0
				y += height
		self.GetSizer().Layout()
		
if __name__ == '__main__':
	import os
	import glob
	
	app = wx.App(False)
	
	displayWidth, displayHeight = wx.GetDisplaySize()
	imageWidth, imageHeight = int(displayWidth*6/8.0), int(displayHeight*6/8.0)
	
	mainWin = wx.Frame(None,title="FramesViewer", size=(imageWidth,imageHeight))
	fv = FramesViewer( mainWin )
	
	images = []
	for f in glob.glob( os.path.join('Test_Photos','*.jpg') ):
		images.append( wx.Bitmap(f, wx.BITMAP_TYPE_JPEG ) )
	images = images[-fv.GetBitmapCount():]
	fv.SetBitmaps( images )
	
	mainWin.Show()
	app.MainLoop()

