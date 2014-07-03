import wx
import math
import datetime

tCos60 = [math.cos((i/60.0)*2.0*math.pi-math.pi/2.0) for i in xrange(60)]
tSin60 = [math.sin((i/60.0)*2.0*math.pi-math.pi/2.0) for i in xrange(60)]

def GetCos( pos ):
	return math.cos(pos*2.0*math.pi-math.pi/2.0)
	
def GetSin( pos ):
	return math.sin(pos*2.0*math.pi-math.pi/2.0)

def GetPen( colour=wx.BLACK, cap=wx.CAP_ROUND, join=wx.JOIN_ROUND, width=1 ):
	pen = wx.Pen( colour, width )
	pen.SetCap( cap )
	pen.SetJoin( join )
	return pen

class Clock(wx.PyControl):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="Clock", checkFunc=None ):
		"""
		Default class constructor.

		@param parent: Parent window. Must not be None.
		@param id: StatusBar identifier. A value of -1 indicates a default value.
		@param pos: StatusBar position. If the position (-1, -1) is specified
					then a default position is chosen.
		@param style: not used
		@param validator: Window validator.
		@param name: Window name.
		"""

		# Ok, let's see why we have used wx.PyControl instead of wx.Control.
		# Basically, wx.PyControl is just like its wxWidgets counterparts
		# except that it allows some of the more common C++ virtual method
		# to be overridden in Python derived class. For StatusBar, we
		# basically need to override DoGetBestSize and AcceptsFocusFromKeyboard
		
		wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)
		
		self.timer = wx.Timer( self )
		self.Bind( wx.EVT_TIMER, self.onTimer )
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
		self.checkFunc = checkFunc if checkFunc else lambda: True
		self.tCur = datetime.datetime.now()
		wx.CallAfter( self.onTimer )
		
	def DoGetBestSize(self):
		return wx.Size(100, 100)

	def SetForegroundColour(self, colour):
		wx.PyControl.SetForegroundColour(self, colour)
		self.Refresh()

	def SetBackgroundColour(self, colour):
		wx.PyControl.SetBackgroundColour(self, colour)
		self.Refresh()
		
	def GetDefaultAttributes(self):
		"""
		Overridden base class virtual.  By default we should use
		the same font/colour attributes as the native wx.StaticText.
		"""
		return wx.StaticText.GetClassDefaultAttributes()

	def ShouldInheritColours(self):
		"""
		Overridden base class virtual.  If the parent has non-default
		colours then we want this control to inherit them.
		"""
		return True

	def onTimer( self, event=None):
		if not self.timer.IsRunning():
			self.tCur = datetime.datetime.now()
			self.Refresh()
			if self.checkFunc():
				self.timer.Start( 1001 - datetime.datetime.now().microsecond//1000, True )
	
	def Start( self ):
		self.onTimer()
	
	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def Draw(self, dc):
		t = self.tCur
		
		size = self.GetClientSize()
		width = size.width
		height = size.height
		radius = min(width, height) // 2 * 0.9
		xCenter, yCenter = width//2, height//2
		
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		ctx = wx.GraphicsContext_Create(dc)
		
		rOutside = radius * 0.98
		rOutTicks = rOutside
		rInMinuteTicks = rOutTicks * 0.95
		rInHourTicks = rOutTicks * 0.9
		rHour = radius * 0.6
		rMinute = (rInMinuteTicks + rInHourTicks) / 2
		rSecond = rMinute
		rBack = -radius * 0.1
		rDot = rSecond * 0.85
		dotSize = rDot * 0.08

		wMinuteTicks = radius * 0.03
		wHourTicks = wMinuteTicks * 2.0
		
		wHourHand = wHourTicks * 1.5
		wMinuteHand = wHourTicks
		wSecondHand = wMinuteHand / 2.0
		
		tCos60Local = tCos60
		tSin60Local = tSin60
		penSecond = ctx.CreatePen( GetPen(width=wMinuteTicks, cap=wx.wx.CAP_BUTT) )
		penHour = ctx.CreatePen( GetPen(width=wHourTicks, cap=wx.wx.CAP_BUTT) )
		
		#-----------------------------------------------------------------------------
		# Draw the metal ring
		#
		r = radius * 1.0/0.9
		def drawCircle( x, y, r ):
			ctx.DrawEllipse( x - r, y - r, r * 2, r * 2 )
		
		ctx.SetBrush( ctx.CreateRadialGradientBrush(
						xCenter, yCenter - r,
						xCenter, yCenter - r,
						r * 2,
						wx.WHITE, wx.Colour(33,33,33) ) )
		drawCircle( xCenter, yCenter, r )
		
		rSmaller = r * 0.90
		ctx.SetBrush( ctx.CreateRadialGradientBrush(
						xCenter, yCenter + rSmaller,
						xCenter, yCenter + rSmaller,
						rSmaller * 2,
						wx.WHITE, wx.Colour(33,33,33) ) )
		drawCircle( xCenter, yCenter, rSmaller )
		
		#-----------------------------------------------------------------------------
		# Draw the clock face.
		#
		ctx.SetPen( penSecond )
		ctx.SetBrush( ctx.CreateRadialGradientBrush(
			xCenter, yCenter-radius*0.6, xCenter, yCenter, rOutside,
			wx.Colour(252,252,252), wx.Colour(220,220,220) ) )
		ctx.DrawEllipse( xCenter - rOutside, yCenter - rOutside, rOutside*2, rOutside*2 )

		penCur = None
		for i in xrange(60):
			if i % 5 == 0:
				rIn = rInHourTicks
				pen = penHour
			else:
				rIn = rInMinuteTicks
				pen = penSecond
			if pen is not penCur:
				penCur = pen
				ctx.SetPen( pen )
			ctx.StrokeLine(
				xCenter + rIn * tCos60Local[i], yCenter + rIn * tSin60Local[i],
				xCenter + rOutTicks * tCos60Local[i], yCenter + rOutTicks * tSin60Local[i]
			)
			
		#-----------------------------------------------------------------------------
		# Draw the digital clock.
		#
		ctx.SetFont( ctx.CreateFont(wx.FFontFromPixelSize((0,radius*0.37), wx.DEFAULT), wx.Colour(100,100,100)) )
		tStr = u'{}:{:02d}:{:02d}'.format( t.hour, t.minute, t.second )
		w, h = ctx.GetTextExtent(tStr)
		ctx.DrawText( tStr, xCenter-w/2, yCenter+radius/2-h )
		
		#-----------------------------------------------------------------------------
		# Draw the hands.
		#
		secondPos = (t.second  + t.microsecond/1000000.0) / 60.0
		minutePos = (t.minute + secondPos) / 60.0
		hourPos = (t.hour % 12 + minutePos) / 12.0
		
		ctx.SetPen( ctx.CreatePen( GetPen(colour=wx.Colour(0,0,180,128), width=wHourHand) ) )
		cosCur = GetCos(hourPos)
		sinCur = GetSin(hourPos)
		ctx.StrokeLine(
			xCenter + rBack * cosCur, yCenter + rBack * sinCur,
			xCenter + rHour * cosCur, yCenter + rHour * sinCur
		)
		ctx.SetPen( ctx.CreatePen( GetPen(colour=wx.Colour(0,150,0,128), width=wMinuteHand) ) )
		cosCur = GetCos(minutePos)
		sinCur = GetSin(minutePos)
		ctx.StrokeLine(
			xCenter + rBack * cosCur,   yCenter + rBack * sinCur,
			xCenter + rMinute * cosCur, yCenter + rMinute * sinCur
		)
		
		ctx.SetPen( ctx.CreatePen( GetPen(colour=wx.RED,width=wSecondHand) ) )
		ctx.SetBrush( ctx.CreateBrush(wx.Brush(wx.RED)) )
		cosCur = GetCos(secondPos)
		sinCur = GetSin(secondPos)
		ctx.StrokeLine(
			xCenter + rDot * cosCur,    yCenter + rDot * sinCur,
			xCenter + rMinute * cosCur, yCenter + rMinute * sinCur
		)
		xDot = xCenter + rDot * cosCur
		yDot = yCenter + rDot * sinCur
		ctx.DrawEllipse( xDot - dotSize, yDot - dotSize, dotSize*2, dotSize*2 )
		
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="Clock", size=(600,400))
	Clock = Clock(mainWin)
	mainWin.Show()
	app.MainLoop()
