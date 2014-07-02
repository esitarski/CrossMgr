import wx
import math
import datetime

tCos300 = [math.cos((i/300.0)*2.0*math.pi-math.pi/2.0) for i in xrange(300)]
tSin300 = [math.sin((i/300.0)*2.0*math.pi-math.pi/2.0) for i in xrange(300)]

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
				name="Clock", checkFunc = None ):
		"""
		Default class constructor.

		@param parent: Parent window. Must not be None.
		@param id: StatusBar identifier. A value of -1 indicates a default value.
		@param pos: StatusBar position. If the position (-1, -1) is specified
					then a default position is chosen.
		@param size: StatusBar size. If the default size (-1, -1) is specified
					then a default size is chosen.
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
		self.SetBackgroundColour('white')
		
		self.timer = wx.Timer( self )
		self.Bind( wx.EVT_TIMER, self.onTimer )
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
		self.checkFunc = checkFunc
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
		radius = min(width, height) // 2
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
		
		penSecond = ctx.CreatePen( GetPen(width=wMinuteTicks, cap=wx.wx.CAP_BUTT) )
		penHour = ctx.CreatePen( GetPen(width=wHourTicks, cap=wx.wx.CAP_BUTT) )
		penCur = None
		for i in xrange(0, 300, 5):
			if i % 25 == 0:
				rIn = rInHourTicks
				pen = penHour
			else:
				rIn = rInMinuteTicks
				pen = penSecond
			if pen is not penCur:
				penCur = pen
				ctx.SetPen( pen )
			ctx.StrokeLine(
				xCenter + rIn * tCos300[i], yCenter - rIn * tSin300[i],
				xCenter + rOutTicks * tCos300[i], yCenter - rOutTicks * tSin300[i]
			)
			
		ctx.SetPen( penSecond )
		ctx.DrawEllipse( xCenter - rOutside, yCenter - rOutside, rOutside*2, rOutside*2 )
		
		fHour = (t.hour % 12) / 12.0
		fMinute = t.minute / 60.0
		fSecond = (t.second  + t.microsecond/1000000.0) / 60.0
		
		hourPos = (fHour + fMinute/60.0 + fSecond/(60.0*60.0))
		minutePos = (fMinute + fSecond/60.0)
		secondPos = fSecond
		
		ctx.SetPen( ctx.CreatePen( GetPen(colour=wx.Colour(0,0,180,128), width=wHourHand) ) )
		ctx.StrokeLine(
			xCenter + rBack * GetCos(hourPos), yCenter + rBack * GetSin(hourPos),
			xCenter + rHour * GetCos(hourPos), yCenter + rHour * GetSin(hourPos)
		)
		ctx.SetPen( ctx.CreatePen( GetPen(colour=wx.Colour(0,180,0,128), width=wMinuteHand) ) )
		ctx.StrokeLine(
			xCenter + rBack * GetCos(minutePos), yCenter + rBack * GetSin(minutePos),
			xCenter + rMinute * GetCos(minutePos), yCenter + rMinute * GetSin(minutePos)
		)
		
		ctx.SetPen( ctx.CreatePen( GetPen(colour=wx.RED,width=wSecondHand) ) )
		ctx.SetBrush( ctx.CreateBrush(wx.Brush(wx.RED)) )
		ctx.StrokeLine(
			xCenter + rBack * GetCos(secondPos), yCenter + rBack * GetSin(secondPos),
			xCenter + rMinute * GetCos(secondPos), yCenter + rMinute * GetSin(secondPos)
		)
		xDot = xCenter + rDot * GetCos(secondPos)
		yDot = yCenter + rDot * GetSin(secondPos)
		ctx.DrawEllipse( xDot - dotSize, yDot - dotSize, dotSize*2, dotSize*2 )
		
		ctx.SetFont( ctx.CreateFont(wx.FFontFromPixelSize((0,radius/3), wx.DEFAULT) ) )
		ctx.SetBrush( ctx.CreateBrush(wx.Brush(wx.BLACK)) )
		tStr = unicode(t.strftime('%H:%M:%S'))
		w, h = ctx.GetTextExtent(tStr)
		ctx.DrawText( tStr, xCenter-w/2, yCenter+radius/2-h )
		
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
