import wx
from ScaledBitmap import GetScaleRatio

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

class ScaledBitmapVerticalLines( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=(640,480), style=0, bitmap=None, numLines=2, colors=None ):
		super().__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		self.bitmap = bitmap
		self.verticalLines = [None for i in range(numLines)]
		self.iLineSelected = None
		self.ratio = None
		self.controlHeight = None
		self.doResize = False
		self.xCorrection = None
		self.yCur = None
		self.colors = colors or contrastColours
		self.backgroundBrush = wx.Brush( wx.Colour(232,232,232), wx.SOLID )
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_LEFT_DOWN, self.OnMouseDown )
		self.Bind( wx.EVT_LEFT_UP, self.OnMouseUp )
		self.Bind( wx.EVT_MOTION, self.OnMouseMotion )
	
	def OnMouseDown( self, event ):
		if not self.controlHeight:
			return
		width, height = self.GetSize()
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
			self.yCur = event.GetY()
			
			evt = VerticalLineEvent(EVT_VERTICAL_LINES_Type, self.GetId())
			evt.SetVerticalLines( self.verticalLines )
			self.GetEventHandler().ProcessEvent(evt)
			
			self.Refresh()
	
	def OnMouseUp( self, event ):
		self.iLineSelected = None
		self.yCur = None
		self.Refresh()
	
	def OnSize( self, event ):
		self.doResize = True
		self.Refresh()
	
	def OnPaint( self, event=None ):
		dc = wx.AutoBufferedPaintDC( self )
		dc.SetBackground( self.backgroundBrush )
		dc.Clear()
		
		if not self.bitmap:
			return
		
		if self.doResize:
			if not self.ratio:
				self.doResize = False
			else:
				self.verticalLines = [None if v is None else (v / self.ratio) for v in self.verticalLines]
		
		width, height = self.GetSize()
		bmWidth, bmHeight = self.bitmap.GetSize()
		self.controlHeight = 32
		bitmapHeight = height - self.controlHeight
		self.ratio = GetScaleRatio( bmWidth, bmHeight, width, bitmapHeight )
		
		if self.doResize:
			self.verticalLines = [None if v is None else int(v * self.ratio) for v in self.verticalLines]
			self.doResize = False
		
		dcSource = wx.MemoryDC( self.bitmap )
		dc.StretchBlit(
			0, 0, int(bmWidth*self.ratio), int(bmHeight*self.ratio),
			dcSource, 0, 0, bmWidth, bmHeight
		)
		
		lenColors = len(self.colors)
		if self.iLineSelected is not None and self.yCur is not None:
			dc.SetPen( wx.Pen(self.colors[self.iLineSelected%lenColors], 1) )
			dc.DrawLine( 0, self.yCur, width, self.yCur )
		
		for i, v in enumerate(self.verticalLines):
			if v is None:
				continue
			dc.SetPen( wx.Pen(self.colors[i%lenColors], 1) )
			dc.DrawLine( v, 0, v, height )
			x = v - self.controlHeight // 2
			dc.SetPen( wx.Pen(wx.BLACK, 1) )
			dc.SetBrush( wx.Brush(self.colors[i%lenColors]) )
			dc.DrawRectangle( x, height-self.controlHeight, self.controlHeight, self.controlHeight )
	
	def SetBitmap( self, bitmap ):
		self.bitmap = bitmap
		width, height = self.GetSize()
		dx = width / (len(self.verticalLines) + 1)
		self.verticalLines = [int(dx*(i+1)) for i in range(len(self.verticalLines))]
		self.doResize = False
		self.Refresh()
		
	def GetVerticalLines( self ):
		# Returned in bitmap pixels.
		return [None if (v is None or not self.ratio) else (v / self.ratio) for v in self.verticalLines]
		
	def SetLinePosition( self, i, v ):
		self.verticalLines[i] = v * self.ratio
		
	def GetBitmap( self ):
		return self.bitmap
		
	def SetToEmpty( self ):
		width, height = self.GetSize()
		self.bitmap = wx.Bitmap( width, height )
		dc = wx.MemoryDC( self.bitmap )
		dc.SetBackground( self.backgroundBrush )
		dc.Clear()
		self.Refresh()
		
	def SetTestBitmap( self ):
		width, height = self.GetSize()
		self.bitmap = wx.Bitmap( width, height )
		dc = wx.MemoryDC( self.bitmap )
		
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
		
		self.Refresh()
		
if __name__ == '__main__':
	app = wx.App(False)
	
	displayWidth, displayHeight = wx.GetDisplaySize()
	bitmapWidth, bitmapHeight = 640, 480
	if bitmapWidth*2 + 32 > displayWidth or bitmapHeight*2 + 32 > displayHeight:
		bitmapWidth /= 2
		bitmapHeight /= 2
	
	mainWin = wx.Frame(None,title="ScaledBitmapVerticalLines", size=(bitmapWidth,bitmapHeight))
	scaledBitmapVL = ScaledBitmapVerticalLines( mainWin, size=(bitmapWidth, bitmapHeight) )
	scaledBitmapVL.SetTestBitmap()
	mainWin.Show()
	app.MainLoop()
