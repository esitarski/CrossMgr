import wx

def RescaleImage( image, width, height ):
	wImage = image.GetWidth()
	hImage = image.GetHeight()
	ratio = min( float(width) / float(wImage), float(height) / float(hImage) )
	return image.Copy().Rescale( int(wImage*ratio), int(hImage*ratio), wx.IMAGE_QUALITY_NORMAL ) if not (0.94 < ratio < 1.06) else image
	
class ScaledImage( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=(640,480), style=0 ):
		super(ScaledImage, self).__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		self.image = None
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
	
	def SetImage( self, image ):
		self.image = image
		self.Refresh()
		
	def GetImage( self ):
		return self.image
		
	def SetToEmpty( self ):
		width, height = self.GetSize()
		bitmap = wx.EmptyBitmapRGBA( width, height, 255, 255, 255, 0 )
		self.image = wx.ImageFromBitmap( bitmap )
		
	def SetTestImage( self ):
		# Return a test image.
		width, height = self.GetSize()
		bitmap = wx.EmptyBitmapRGBA( width, height, 255, 255, 255, 0 )
		dc = wx.MemoryDC()
		dc.SelectObject( bitmap )
		
		colours = [(255,255,255), (255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255), (0,0,0) ]
		for y, hCur in ((0, height*0.75), (height*0.75, height*0.25)):
			rWidth = int(float(width) / len(colours) + 0.5)
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
		
		self.SetImage( bitmap.ConvertToImage() )