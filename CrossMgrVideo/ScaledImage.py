import wx

contrastColour = wx.Colour( 255, 130, 0 )

def RescaleImage( image, width, height, imageQuality=wx.IMAGE_QUALITY_NORMAL ):
	wImage = image.GetWidth()
	hImage = image.GetHeight()
	ratio = min( float(width) / float(wImage), float(height) / float(hImage) )
	return image.Copy().Rescale( int(wImage*ratio), int(hImage*ratio), imageQuality ) if not (0.94 < ratio < 1.06) else image
	
class ScaledImage( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=(640,480), style=0, drawFinishLine=False ):
		super(ScaledImage, self).__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		self.image = None
		self.drawFinishLine = drawFinishLine
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		
	def OnPaint( self, event=None ):
		dc = wx.AutoBufferedPaintDC( self )
		dc.SetBackground( wx.WHITE_BRUSH )
		dc.Clear()
		
		width, height = self.GetSizeTuple()
		try:
			bitmap = wx.BitmapFromImage( RescaleImage(self.image, width, height) )
		except Exception as e:
			return
		
		dc.DrawBitmap( bitmap, max(0,(width - bitmap.GetWidth())//2), max(0,(height - bitmap.GetHeight())//2) )
		
		if self.drawFinishLine:
			dc.SetPen( wx.Pen(contrastColour, 1) )
			dc.DrawLine( width//2, 0, width//2, height )
	
	def SetImage( self, image ):
		self.image = image
		self.Refresh()
		
	def GetImage( self ):
		return self.image
		
	def SetToEmpty( self ):
		width, height = self.GetSize()
		bitmap = wx.EmptyBitmapRGBA( width, height, 255, 255, 255, 0 )
		self.image = wx.ImageFromBitmap( bitmap )
		
	def SetTile( self, tile ):
		width, height = self.GetSize()
		bitmap = wx.EmptyBitmap( width, height )
		dc = wx.MemoryDC()
		dc.SelectObject( bitmap )
		
		wTile = tile.GetWidth()
		hTile = tile.GetHeight()
		for y in xrange( 0, height, hTile ):
			for x in xrange( 0, width, wTile ):
				dc.DrawBitmap( tile, x, y )
		self.SetImage( bitmap.ConvertToImage() )
		
	def SetTestImage( self ):
		# Return a test image.
		width, height = self.GetSize()
		bitmap = wx.EmptyBitmap( width, height )
		dc = wx.MemoryDC()
		dc.SelectObject( bitmap )
		
		colours = [(255,255,255), (255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255), (0,0,0) ]
		rWidth = int(float(width) / len(colours) + 0.5)
		for y, hCur in ((0, height*0.75), (height*0.75, height*0.25)):
			for i, c in enumerate(colours):
				dc.SetBrush( wx.Brush(wx.Colour(*c), wx.SOLID) )
				dc.DrawRectangle( rWidth * i, y, rWidth+1, hCur )
			colours.reverse()
		
		s = min(width, height) / 1.5
		x = (width-s) / 2
		y = (height-s) / 2
		angle = 360.0 / len(colours)
		for i, c in enumerate(colours):
			dc.SetBrush( wx.Brush(wx.Colour(*c), wx.SOLID) )
			dc.DrawEllipticArc(x, y, s, s, angle*i, angle*(i+1))
		
		dc.SelectObject( wx.NullBitmap )
		self.SetImage( bitmap.ConvertToImage() )
		
if __name__ == '__main__':
	app = wx.App(False)
	
	displayWidth, displayHeight = wx.GetDisplaySize()
	imageWidth, imageHeight = 640, 480
	if imageWidth*2 + 32 > displayWidth or imageHeight*2 + 32 > displayHeight:
		imageWidth /= 2
		imageHeight /= 2
	
	mainWin = wx.Frame(None,title="ScaledImage", size=(imageWidth,imageHeight))
	scaledImage = ScaledImage( mainWin, size=(imageWidth, imageHeight) )
	scaledImage.SetTestImage()
	# scaledImage.SetToEmpty()
	mainWin.Show()
	app.MainLoop()
