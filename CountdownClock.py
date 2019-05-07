import wx
import six
import math
import datetime
import wx.lib.newevent

CountdownEvent, EVT_COUNTDOWN = wx.lib.newevent.NewEvent()

tCos60 = [math.cos((i/60.0)*2.0*math.pi-math.pi/2.0) for i in six.moves.range(60)]
tSin60 = [math.sin((i/60.0)*2.0*math.pi-math.pi/2.0) for i in six.moves.range(60)]

def GetCos( pos ):
	return math.cos(pos*2.0*math.pi-math.pi/2.0)
	
def GetSin( pos ):
	return math.sin(pos*2.0*math.pi-math.pi/2.0)

def GetPen( colour=wx.BLACK, cap=wx.CAP_ROUND, join=wx.JOIN_ROUND, width=1 ):
	pen = wx.Pen( colour, width )
	pen.SetCap( cap )
	pen.SetJoin( join )
	return pen

class CountdownClock(wx.Control):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="CountdownClock", tFuture = None ):
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

		# Ok, let's see why we have used wx.Control instead of wx.Control.
		# Basically, wx.Control is just like its wxWidgets counterparts
		# except that it allows some of the more common C++ virtual method
		# to be overridden in Python derived class. For StatusBar, we
		# basically need to override DoGetBestSize and AcceptsFocusFromKeyboard
		
		wx.Control.__init__(self, parent, id, pos, size, style, validator, name)
		
		self.timer = wx.Timer( self )
		self.Bind( wx.EVT_TIMER, self.onTimer )
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
		self.owner = parent
		self.initialSize = size
		
		self.tFuture = None
		wx.CallAfter( self.Start, tFuture )
		
	def DoGetBestSize(self):
		return wx.Size(100, 100) if self.initialSize is wx.DefaultSize else self.initialSize

	def SetForegroundColour(self, colour):
		wx.Control.SetForegroundColour(self, colour)
		self.Refresh()

	def SetBackgroundColour(self, colour):
		wx.Control.SetBackgroundColour(self, colour)
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
		if self.tFuture is None:
			self.Refresh()
			return
		
		if not self.timer.IsRunning():
			self.tCur = datetime.datetime.now()
			self.Refresh()
			if self.tCur >= self.tFuture:
				if self.owner:
					wx.PostEvent( self.owner, CountdownEvent(tFuture=self.tFuture) )
				return
			self.timer.Start( 1000 - datetime.datetime.now().microsecond//1000, True )
	
	def Stop( self ):
		if self.timer.IsRunning():
			self.timer.Stop()
	
	def Start( self, tFuture ):
		self.tFuture = tFuture
		self.onTimer()
	
	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def Draw(self, dc):
		size = self.GetClientSize()
		width = size.width
		height = size.height
		middle = min(width, height) // 2
		radius = middle * 0.9
		xCenter, yCenter = width//2, height//2
		
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		ctx = wx.GraphicsContext.Create(dc)
		
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
		penSecond = ctx.CreatePen( GetPen(width=wMinuteTicks, cap=wx.CAP_BUTT) )
		penHour = ctx.CreatePen( GetPen(width=wHourTicks, cap=wx.CAP_BUTT) )
		
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
		# Draw the CountdownClock face.
		#
		ctx.SetPen( penSecond )
		ctx.SetBrush( ctx.CreateRadialGradientBrush(
			xCenter, yCenter-radius*0.6, xCenter, yCenter, rOutside,
			wx.Colour(252,252,252), wx.Colour(220,220,220) ) )
		ctx.DrawEllipse( xCenter - rOutside, yCenter - rOutside, rOutside*2, rOutside*2 )

		penCur = None
		for i in six.moves.range(60):
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
			
		
		if self.tFuture is None:
			return
			
		dt = self.tFuture - self.tCur
		dSeconds = dt.total_seconds()

		#-----------------------------------------------------------------------------
		# Draw the digital CountdownClock.
		#
		tt = int(max(dSeconds,0.0) + 0.999)
		hour = tt // 3600
		minute = (tt // 60) % 60
		second = tt % 60
		
		ctx.SetFont( ctx.CreateFont(
			wx.Font(
				(0,radius*0.37),
				wx.FONTFAMILY_SWISS,
				wx.FONTSTYLE_NORMAL,
				wx.FONTWEIGHT_NORMAL,
			),
			wx.Colour(100,100,100)) )
		tStr = u'{}:{:02d}:{:02d}'.format( hour, minute, second )
		w, h = ctx.GetTextExtent(u'00:00:00'[:len(tStr)])
		ctx.DrawText( tStr, xCenter-w/2, yCenter+radius/2-h )
		
		#-----------------------------------------------------------------------------
		# Draw the hands.
		#
		tt = int(max(dSeconds,0.0))
		hour = tt // 3600
		minute = (tt // 60) % 60
		second = tt % 60
		secondPos = (second  + math.modf(dSeconds)[0]) / 60.0
		minutePos = (minute + secondPos) / 60.0
		hourPos = (hour % 12 + minutePos) / 12.0
		
		if hour > 1.0:
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
	mainWin = wx.Frame(None,title="CountdownClock", size=(600,400))
	
	tFuture = datetime.datetime.now() + datetime.timedelta(seconds=20)
	tFuture = datetime.datetime( tFuture.year, tFuture.month, tFuture.day, tFuture.hour, tFuture.minute, tFuture.second )
	countdownClock = CountdownClock( mainWin, tFuture=tFuture )
	
	mainWin.Show()
	app.MainLoop()
