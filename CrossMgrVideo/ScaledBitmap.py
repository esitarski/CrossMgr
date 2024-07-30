import wx

contrastColour = wx.Colour( 255, 130, 0 )

def GetScaleRatio( wBitmap, hBitmap, width, height ):
	return min( float(width) / float(wBitmap), float(height) / float(hBitmap) )

def intervalsOverlap( a0, a1, b0, b1 ):
	return a0 <= b1 and b0 <= a1

class ScaledBitmap( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize, style=0, bitmap=None, drawFinishLine=False, inset=False, drawCallback=None ):
		super().__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_PAINT )
		self.bitmap = bitmap
		self.drawCallback = drawCallback
		self.drawFinishLine = drawFinishLine
		self.buttonDown = False
		self.backgroundBrush = wx.Brush( wx.Colour(0,0,0), wx.SOLID )
		self.resetMagRect()
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		if inset:
			self.Bind( wx.EVT_LEFT_DOWN, self.OnLeftDown )
			self.Bind( wx.EVT_MOTION, self.OnMotion )
			self.Bind( wx.EVT_LEFT_UP, self.OnLeftUp )
			self.Bind( wx.EVT_LEAVE_WINDOW, self.OnLeave )
	
	def resetMagRect( self ):
		# traceback.print_stack()
		self.xBegin = 0
		self.yBegin = 0
		self.xEnd = 0
		self.yEnd = 0		
		self.sourceRect = None
	
	def getMagRect( self ):
		return wx.Rect( min(self.xBegin, self.xEnd), min(self.yBegin, self.yEnd), abs(self.xEnd-self.xBegin), abs(self.yEnd-self.yBegin) )
	
	def GetSourceRect( self ):
		''' Returns the zoom rectangle in photo pixel coordinates. '''
		return self.sourceRect
		
	def SetSourceRect( self, rect ):
		''' Sets the zoom rectangle, given in photo pixel coordinates. '''
		if not rect or rect.IsEmpty() or not self.bitmap:
			return
		sourceBM = self.bitmap
		sourceWidth, sourceHeight = sourceBM.GetSize()
		width, height = self.GetSize()
		ratio = GetScaleRatio( sourceWidth, sourceHeight, width, height )
		destWidth, destHeight = int(sourceWidth * ratio), int(sourceHeight * ratio)
		xLeft, yTop = max(0, (width - destWidth)//2), max(0, (height - destHeight)//2)
		self.xBegin = xLeft + int(rect.GetX() * ratio)
		self.yBegin = yTop + int(rect.GetY() * ratio)
		self.xEnd = self.xBegin + int(rect.GetWidth() * ratio)
		self.yEnd = self.yBegin + int(rect.GetHeight() * ratio)
		self.Refresh()
	
	def OnSize( self, event ):
		self.Refresh()
	
	def OnLeftDown( self, event ):
		self.buttonDown = True
		self.xBegin, self.yBegin = event.GetX(), event.GetY()
		self.xEnd, self.yEnd = self.xBegin, self.yBegin
		self.SetCursor( wx.Cursor(wx.CURSOR_MAGNIFIER) )
		wx.CallAfter( self.Refresh )
		
	def OnMotion( self, event ):
		if self.buttonDown:
			self.xEnd, self.yEnd = event.GetX(), event.GetY()
			self.Refresh()
	
	def OnLeftUp( self, event ):
		self.SetCursor( wx.NullCursor )
		self.buttonDown = False
	
	def OnLeave( self, event ):
		if self.buttonDown:
			self.buttonDown = False
			self.SetCursor( wx.NullCursor )
	
	def getInsetRect( self, width, height, isWest, isNorth ):
		r = 0.75
		insetWidth = round(width*r)
		insetHeight = round(height*r)
		return wx.Rect( 0 if not isWest else width - insetWidth, 0 if not isNorth else height - insetHeight,
			insetWidth, insetHeight
		)
	
	def draw( self, dc, width, height ):
		dc.SetBackground( self.backgroundBrush )
		dc.Clear()
		
		self.sourceRect = None
		if not self.bitmap:
			return
		
		sourceBM = self.bitmap
		sourceWidth, sourceHeight = sourceBM.GetSize()
		ratio = GetScaleRatio( sourceWidth, sourceHeight, width, height )
		destWidth, destHeight = int(sourceWidth * ratio), int(sourceHeight * ratio)
		sourceDC = wx.MemoryDC( sourceBM )

		xLeft, yTop = max(0, (width - destWidth)//2), max(0, (height - destHeight)//2)
		dc.StretchBlit( xLeft, yTop, destWidth, destHeight, sourceDC, 0, 0, sourceWidth, sourceHeight )
		
		if self.drawFinishLine:
			dc.SetPen( wx.Pen(contrastColour, 1) )
			dc.DrawLine( width//2, 0, width//2, height )
		
		magnifyRect = self.getMagRect()
		if magnifyRect.IsEmpty():
			if self.drawCallback:
				self.drawCallback( dc, width, height )
			return
			
		sourceRect = wx.Rect( 0, 0, sourceWidth, sourceHeight )
		sourceRect.Intersect( wx.Rect( int((magnifyRect.GetX() - xLeft)/ratio), int((magnifyRect.GetY()-yTop)/ratio), int(magnifyRect.GetWidth()/ratio), int(magnifyRect.GetHeight()/ratio) ) )
		
		if sourceRect.IsEmpty():
			if self.drawCallback:
				self.drawCallback( dc, width, height )
			return
		self.sourceRect = sourceRect
			
		xCenter = sourceRect.GetX() + sourceRect.GetWidth() // 2
		yCenter = sourceRect.GetY() + sourceRect.GetHeight() // 2
		isWest = xCenter < self.bitmap.GetWidth()//2
		isNorth = yCenter < self.bitmap.GetHeight()//2
		insetRect = self.getInsetRect( width, height, isWest, isNorth )
		
		magRatio = GetScaleRatio( sourceRect.GetWidth(), sourceRect.GetHeight(), insetRect.GetWidth(), insetRect.GetHeight() )
		iWidth, iHeight = int(sourceRect.GetWidth() * magRatio), int(sourceRect.GetHeight() * magRatio)
		insetRect = wx.Rect(
			insetRect.GetX() + insetRect.GetWidth() - iWidth if insetRect.GetX() else 0,
			insetRect.GetY() + insetRect.GetHeight() - iHeight if insetRect.GetY() else 0,
			iWidth, iHeight
		)
		
		dc.StretchBlit( *(list(insetRect.Get()) + [sourceDC] + list(sourceRect.Get())) )
		
		dc.SetPen( wx.Pen(wx.Colour(200,200,0), 2) )
		dc.SetBrush( wx.TRANSPARENT_BRUSH )
		dc.DrawRectangle( insetRect )
		dc.DrawRectangle( magnifyRect )

		if intervalsOverlap(magnifyRect.GetLeft(), magnifyRect.GetRight(), insetRect.GetLeft(), insetRect.GetRight()):
			if not intervalsOverlap(magnifyRect.GetTop(), magnifyRect.GetBottom(), insetRect.GetTop(), insetRect.GetBottom() ):
				if isNorth:
					dc.DrawLine( magnifyRect.GetBottomLeft(), insetRect.GetTopLeft() )
					dc.DrawLine( magnifyRect.GetBottomRight(),insetRect.GetTopRight() )
				else:
					dc.DrawLine( magnifyRect.GetTopLeft(),    insetRect.GetBottomLeft() )
					dc.DrawLine( magnifyRect.GetTopRight(),   insetRect.GetBottomRight() )
		else:
			if isWest:
				dc.DrawLine( magnifyRect.GetTopRight(),   insetRect.GetTopLeft() )
				dc.DrawLine( magnifyRect.GetBottomRight(),insetRect.GetBottomLeft() )
			else:
				dc.DrawLine( magnifyRect.GetTopLeft(),    insetRect.GetTopRight() )
				dc.DrawLine( magnifyRect.GetBottomLeft(), insetRect.GetBottomRight() )

		if self.drawCallback:
			self.drawCallback( dc, width, height )
	
	def OnPaint( self, event=None ):
		width, height = self.GetSize()
		self.draw( wx.AutoBufferedPaintDC(self), width, height )
		
	def SetBitmap( self, bitmap ):
		if not bitmap:
			self.resetMagRect()
			self.SetTestBitmap()
			return
		
		assert isinstance(bitmap, wx.Bitmap)
		self.bitmap = bitmap
		self.Refresh()
		
	def GetBitmap( self ):
		return self.bitmap
		
	def GetDisplayBitmap( self ):
		width, height = self.GetSize()
		bitmap = wx.Bitmap( width*2, height*2 )
		self.xBegin *= 2
		self.yBegin *= 2
		self.xEnd *= 2
		self.yEnd *= 2
		dc = wx.MemoryDC( bitmap )
		self.draw( dc, width*2, height*2 )
		self.xBegin //= 2
		self.yBegin //= 2
		self.xEnd //= 2
		self.yEnd //= 2
		return bitmap
		
	def SetToEmpty( self ):
		width, height = self.GetSize()
		self.bitmap = wx.Bitmap( width, height )
		self.Refresh()
		
	def SetTestBitmap( self ):
		width, height = self.GetSize()
		self.bitmap = wx.Bitmap( width, height )
		dc = wx.MemoryDC()
		dc.SelectObject( self.bitmap )
		
		colours = (
			wx.Colour(255,255,255), wx.Colour(255,0,0), wx.Colour(0,255,0), wx.Colour(0,0,255),
			wx.Colour(255,255,0), wx.Colour(255,0,255), wx.Colour(0,255,255), wx.Colour(0,0,0),
		)
		rWidth = float(width) / len(colours)
		for row, (y, hCur) in enumerate(((0, int(height*0.75)), (int(height*0.75), int(height*0.25)))):
			for col, c in enumerate(colours if row == 0 else reversed(colours)):
				dc.SetBrush( wx.Brush(c, wx.SOLID) )
				dc.DrawRectangle( round(rWidth * col), y, round(rWidth+1), hCur )
		
		s = round(min(width, height) / 1.5)
		x = round((width-s) / 2)
		y = round((height-s) / 2)
		angle = 360.0 / len(colours)
		for i, c in enumerate(colours):
			dc.SetBrush( wx.Brush(c, wx.SOLID) )
			dc.DrawEllipticArc(x, y, s, s, angle*i, angle*(i+1))
		
		self.Refresh()
		
if __name__ == '__main__':
	app = wx.App(False)
	
	displayWidth, displayHeight = wx.GetDisplaySize()
	bitmapWidth, bitmapHeight = 640*2, 480*2
	if bitmapWidth*2 + 32 > displayWidth or bitmapHeight*2 + 32 > displayHeight:
		bitmapWidth //= 2
		bitmapHeight //= 2
	
	mainWin = wx.Frame(None,title="ScaledBitmap", size=(bitmapWidth,bitmapHeight))
	scaledBitmap = ScaledBitmap( mainWin, size=(bitmapWidth, bitmapHeight), inset=True )
	scaledBitmap.SetTestBitmap()
	# scaledBitmap.SetToEmpty()
	mainWin.Show()
	app.MainLoop()
