import wx

EVT_VERTICAL_LINES_Type = wx.NewEventType()
EVT_VERTICAL_LINES = wx.PyEventBinder(EVT_VERTICAL_LINES_Type, 1)

#----------------------------------------------------------------------

class VerticalLineEvent(wx.PyCommandEvent):
	def __init__(self, evtType, id):
		wx.PyCommandEvent.__init__(self, evtType, id)
		self.verticalLines = []

	def SetVerticalLines(self, verticalLines):
		self.verticalLine = verticalLines

	def GetVerticalLines(self):
		return self.verticalLines

contrastColours = [
	wx.Colour(255,   0,   0), wx.Colour(  0, 255,   0), wx.Colour(  0,   0, 255),
	wx.Colour(  0, 255, 255), wx.Colour(255,   0, 255), wx.Colour(255, 255,   0),
	wx.Colour(  0,   0,   0), wx.Colour(255, 255, 255),
]

class ScaledImageVerticalLines( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=(640,480), style=0, image=None, numLines=2, colors=None ):
		super(ScaledImageVerticalLines, self).__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		self.image = image
		self.verticalLines = [None for i in xrange(numLines)]
		self.iLineSelected = None
		self.ratio = None
		self.controlHeight = None
		self.doResize = False
		self.xCorrection = None
		self.colors = colors or contrastColours
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_LEFT_DOWN, self.OnMouseDown )
		self.Bind( wx.EVT_LEFT_UP, self.OnMouseUp )
		self.Bind( wx.EVT_MOTION, self.OnMouseMotion )
	
	def rescaleImage( self, width, height ):
		imageQuality = wx.IMAGE_QUALITY_NORMAL
		
		wImage = self.image.GetWidth()
		hImage = self.image.GetHeight()
		self.ratio = min( float(width) / float(wImage), float(height) / float(hImage) )
		if 0.95 < self.ratio < 1.05:
			self.ratio = 1.0
		return (
			self.image.Copy().Rescale( int(wImage*self.ratio), int(hImage*self.ratio), imageQuality ) if not self.ratio == 1.0
			else self.image
		)
	
	def OnMouseDown( self, event ):
		if not self.controlHeight:
			return
		width, height = self.GetSizeTuple()
		y = height - self.controlHeight
		if event.GetY() < y:
			return
		x = event.GetX()
		dx = self.controlHeight // 2
		for i, v in enumerate(self.verticalLines):
			if v - dx <= x < v + dx:
				self.iLineSelected = i
				self.xCorrection = x - v
				break
		else:
			self.iLineSelected = None
	
	def OnMouseMotion( self, event ):
		if self.iLineSelected is not None:
			self.verticalLines[self.iLineSelected] = event.GetX() - self.xCorrection
			
			evt = VerticalLineEvent(EVT_VERTICAL_LINES_Type, self.GetId())
			evt.SetVerticalLines( self.verticalLines )
			self.GetEventHandler().ProcessEvent(evt)
			
			self.Refresh()
	
	def OnMouseUp( self, event ):
		self.iLineSelected = None
	
	def OnSize( self, event ):
		self.doResize = True
		self.Refresh()
	
	def OnPaint( self, event=None ):
		dc = wx.AutoBufferedPaintDC( self )
		dc.SetBackground( wx.WHITE_BRUSH )
		dc.Clear()
		
		if self.doResize:
			if not self.ratio:
				self.doResize = False
			else:
				self.verticalLines = [None if v is None else (v / self.ratio) for v in self.verticalLines]
		
		width, height = self.GetSize()
		self.controlHeight = 32
		bitmapHeight = height - self.controlHeight
		try:
			bitmap = wx.Bitmap( self.rescaleImage(width, bitmapHeight) )
		except Exception as e:
			print e
			return
		
		if self.doResize:
			self.verticalLines = [None if v is None else int(v * self.ratio) for v in self.verticalLines]
			self.doResize = False
		
		dc.DrawBitmap( bitmap, 0, 0 )
		
		lenColors = len(self.colors)
		for i, v in enumerate(self.verticalLines):
			dc.SetPen( wx.Pen(self.colors[i%lenColors], 1) )
			dc.DrawLine( v, 0, v, height )
			x = v - self.controlHeight // 2
			dc.SetPen( wx.Pen(wx.BLACK, 1) )
			dc.SetBrush( wx.Brush(self.colors[i%lenColors]) )
			dc.DrawRectangle( x, height-self.controlHeight, self.controlHeight, self.controlHeight )
	
	def SetImage( self, image ):
		self.image = image
		width, height = self.GetSize()
		dx = width / (len(self.verticalLines) + 1)
		self.verticalLines = [int(dx*(i+1)) for i in xrange(len(self.verticalLines))]
		self.doResize = False
		self.Refresh()
		
	def GetVerticalLines( self ):
		# Returned in image pixels.
		return [None if (v is None or not self.ratio) else (v / self.ratio) for v in self.verticalLines]
		
	def SetLinePosition( self, i, v ):
		self.verticalLines[i] = v * self.ratio
		
	def GetImage( self ):
		return self.image
		
	def SetToEmpty( self ):
		width, height = self.GetSize()
		bitmap = wx.EmptyBitmapRGBA( width, height, 255, 255, 255, 0 )
		self.image = wx.ImageFromBitmap( bitmap )
		
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
	imageWidth, imageHeight = 640, 480
	if imageWidth*2 + 32 > displayWidth or imageHeight*2 + 32 > displayHeight:
		imageWidth /= 2
		imageHeight /= 2
	
	mainWin = wx.Frame(None,title="ScaledImageVerticalLines", size=(imageWidth,imageHeight))
	scaledImageVL = ScaledImageVerticalLines( mainWin, size=(imageWidth, imageHeight) )
	scaledImageVL.SetTestImage()
	mainWin.Show()
	app.MainLoop()
