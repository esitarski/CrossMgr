import wx

contrastColour = wx.Colour( 255, 130, 0 )

def GetScaleRatio( wImage, hImage, width, height ):
	return min( float(width) / float(wImage), float(height) / float(hImage) )

def RescaleImage( image, width, height, imageQuality=wx.IMAGE_QUALITY_NORMAL ):
	wImage, hImage = image.GetWidth(), image.GetHeight()
	ratio = GetScaleRatio( wImage, hImage, width, height )
	return image.Scale( int(wImage*ratio), int(hImage*ratio), imageQuality )
	
class ScaledImage( wx.Panel ):
	NW, NE, SE, SW = (0,1,2,3)

	def __init__( self, parent, id=wx.ID_ANY, size=(640,480), style=0, image=None, drawFinishLine=False ):
		super(ScaledImage, self).__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		self.image = image
		self.drawFinishLine = drawFinishLine
		self.buttonDown = False
		self.resetMagRect()
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_LEFT_DOWN, self.OnLeftDown )
		self.Bind( wx.EVT_MOTION, self.OnMotion )
		self.Bind( wx.EVT_LEFT_UP, self.OnLeftUp )
	
	def resetMagRect( self ):
		self.xBegin = 0
		self.yBegin = 0
		self.xEnd = 0
		self.yEnd = 0		
	
	def getMagRect( self ):
		return wx.Rect( min(self.xBegin, self.xEnd), min(self.yBegin, self.yEnd), abs(self.xEnd-self.xBegin), abs(self.yEnd-self.yBegin) )
	
	def OnSize( self, event ):
		self.resetMagRect()
		self.Refresh()
	
	def OnLeftDown( self, event ):
		self.buttonDown = True
		self.xBegin, self.yBegin = event.GetX(), event.GetY()
		self.xEnd, self.yEnd = self.xBegin, self.yBegin
		wx.CallAfter( self.Refresh )
		
	def OnLeftUp( self, event ):
		self.buttonDown = False
		
	def OnMotion( self, event ):
		x, y, dragging = event.GetX(), event.GetY(), event.Dragging()
		if not self.buttonDown:
			return
		self.xEnd, self.yEnd = x, y
		wx.CallAfter( self.Refresh )
	
	def getInsetRect( self, isWest, isNorth ):
		width, height = self.GetSize()
		insetWidth = width//2
		insetHeight = height//2
		return wx.Rect( 0 if not isWest else width - insetWidth, 0 if not isNorth else height - insetHeight, insetWidth, insetHeight )
	
	def OnPaint( self, event=None ):
		dc = wx.AutoBufferedPaintDC( self )
		dc.SetBackground( wx.WHITE_BRUSH )
		dc.Clear()
		
		width, height = self.GetSize()
		try:
			bitmap = wx.Bitmap( RescaleImage(self.image, width, height) )
		except Exception as e:
			return
		
		xLeft, yTop = max(0, (width - bitmap.GetWidth())//2), max(0, (height - bitmap.GetHeight())//2)
		dc.DrawBitmap( bitmap, xLeft, yTop )
		
		if self.drawFinishLine:
			dc.SetPen( wx.Pen(contrastColour, 1) )
			dc.DrawLine( width//2, 0, width//2, height )
		
		magnifyRect = self.getMagRect()
		if magnifyRect.IsEmpty():
			return
			
		ratio = GetScaleRatio( self.image.GetWidth(), self.image.GetHeight(), width, height )
		sourceRect = wx.Rect( 0, 0, self.image.GetWidth(), self.image.GetHeight() )
		sourceRect.Intersect( wx.Rect( int((magnifyRect.GetX() - xLeft)/ratio), int(magnifyRect.GetY()-yTop)/ratio, magnifyRect.GetWidth()/ratio, magnifyRect.GetHeight()/ratio ) )
		
		if sourceRect.IsEmpty():
			return
			
		xCenter = sourceRect.GetX() + sourceRect.GetWidth() // 2
		yCenter = sourceRect.GetY() + sourceRect.GetHeight() // 2
		insetRect = self.getInsetRect( xCenter < self.image.GetWidth()//2, yCenter < self.image.GetHeight()//2 )
		
		magRatio = GetScaleRatio( sourceRect.GetWidth(), sourceRect.GetHeight(), insetRect.GetWidth(), insetRect.GetHeight() )
		iWidth, iHeight = int(sourceRect.GetWidth() * magRatio), int(sourceRect.GetHeight() * magRatio)
		insetRect = wx.Rect(
			insetRect.GetX() + insetRect.GetWidth() - iWidth if insetRect.GetX() else 0,
			insetRect.GetY() + insetRect.GetHeight() - iHeight if insetRect.GetY() else 0,
			iWidth, iHeight
		)
		
		dc.SetPen( wx.Pen(wx.Colour(200,200,200), 2) )
		dc.DrawLine( magnifyRect.GetBottomRight(), insetRect.GetBottomRight() )
		dc.DrawLine( magnifyRect.GetBottomLeft(),  insetRect.GetBottomLeft() )
		dc.DrawLine( magnifyRect.GetTopRight(),    insetRect.GetTopRight() )
		dc.DrawLine( magnifyRect.GetTopLeft(),     insetRect.GetTopLeft() )
		
		sourceBM = wx.Bitmap( self.image )
		sourceDC = wx.MemoryDC( sourceBM )
		dc.StretchBlit( *(list(insetRect.Get()) + [sourceDC] + list(sourceRect.Get())) )
		sourceDC.SelectObject( wx.NullBitmap )
		
		dc.SetBrush( wx.TRANSPARENT_BRUSH )
		dc.DrawRectangle( insetRect )
		dc.DrawRectangle( magnifyRect )
		
	def SetImage( self, image ):
		self.image = image
		self.resetMagRect()
		self.Refresh()
		
	def GetImage( self ):
		return self.image
		
	def SetToEmpty( self ):
		width, height = self.GetSize()
		bitmap = wx.Bitmap( width, height )
		self.resetMagRect()
		self.image = bitmap.ConvertToImage()
		
	def SetTile( self, tile ):
		width, height = self.GetSize()
		bitmap = wx.Bitmap( width, height )
		dc = wx.MemoryDC()
		dc.SelectObject( bitmap )
		
		wTile = tile.GetWidth()
		hTile = tile.GetHeight()
		for y in xrange( 0, height, hTile ):
			for x in xrange( 0, width, wTile ):
				dc.DrawBitmap( tile, x, y )
		self.SetImage( bitmap.ConvertToImage() )
		
	def SetTestImage( self ):
		width, height = self.GetSize()
		bitmap = wx.Bitmap( width, height )
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
	imageWidth, imageHeight = 640*2, 480*2
	if imageWidth*2 + 32 > displayWidth or imageHeight*2 + 32 > displayHeight:
		imageWidth /= 2
		imageHeight /= 2
	
	mainWin = wx.Frame(None,title="ScaledImage", size=(imageWidth,imageHeight))
	scaledImage = ScaledImage( mainWin, size=(imageWidth, imageHeight) )
	scaledImage.SetTestImage()
	# scaledImage.SetToEmpty()
	mainWin.Show()
	app.MainLoop()
