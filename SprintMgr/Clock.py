import wx
from math import cos, sin, pi
import datetime

now = datetime.datetime.now

tCos60 = [cos((i/60.0)*2.0*pi-pi/2.0) for i in range(60)]
tSin60 = [sin((i/60.0)*2.0*pi-pi/2.0) for i in range(60)]

def GetCosSin( pos ):
	a = pos*2.0*pi-pi/2.0
	return cos(a), sin(a)

def GetPen( colour=wx.BLACK, cap=wx.CAP_ROUND, join=wx.JOIN_ROUND, width=1 ):
	pen = wx.Pen( colour, int(width) )
	pen.SetCap( cap )
	pen.SetJoin( join )
	return pen

class Clock(wx.Control):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="Clock", checkFunc=None, tCur=None ):
		# If tCur is given, the clock will statically show that time with no update.

		wx.Control.__init__(self, parent, id, pos, size, style, validator, name)
		
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
		self.initialSize = size
		
		self.checkFunc = checkFunc if checkFunc else lambda: True
		self.timer = None
		self.SetTCur( tCur )
		
	def DoGetBestSize(self):
		return wx.Size(100, 100) if self.initialSize is wx.DefaultSize else self.initialSize

	def SetForegroundColour(self, colour):
		wx.Control.SetForegroundColour(self, colour)
		self.Refresh()

	def SetBackgroundColour(self, colour):
		wx.Control.SetBackgroundColour(self, colour)
		self.Refresh()
		
	def GetDefaultAttributes(self):
		return wx.StaticText.GetClassDefaultAttributes()

	def ShouldInheritColours(self):
		return True
		
	def SetTCur( self, tCur=None ):
		self.tCur = tCur or now()
		if tCur is None:
			self.timer = wx.CallLater( 10, self.onTimer )
		else:
			if self.timer and self.timer.IsRunning():
				self.timer.Stop()
			self.timer = None
			self.Refresh()

	def onTimer( self, event=None ):
		try:
			self.tCur = now()
			self.Refresh()
			
			# Schedule the next update.
			if self.checkFunc():
				delay = 1001 - now().microsecond//1000
				if self.timer is None:
					self.timer = wx.CallLater( delay, self.onTimer )
				else:
					if self.timer.IsRunning():
						self.timer.Stop()
					self.timer.Start( delay, True )			
		except Exception:
			pass
	
	def Start( self ):
		self.onTimer()
		
	def OnPaint(self, event):
		if self.IsShown():
			dc = wx.BufferedPaintDC( self )
			self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def Draw(self, dc):
		t = self.tCur
		
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
		# Draw the clock face.
		#
		ctx.SetPen( penSecond )
		ctx.SetBrush( ctx.CreateRadialGradientBrush(
			xCenter, yCenter-radius*0.6, xCenter, yCenter, rOutside,
			wx.Colour(252,252,252), wx.Colour(220,220,220) ) )
		ctx.DrawEllipse( xCenter - rOutside, yCenter - rOutside, rOutside*2, rOutside*2 )

		penCur = None
		for i in range(60):
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
		ctx.SetFont( ctx.CreateFont(
				wx.Font(
					(0,int(max(1,radius*0.37))),
					wx.FONTFAMILY_SWISS,
					wx.FONTSTYLE_NORMAL,
					wx.FONTWEIGHT_NORMAL,
				),
				wx.Colour(100,100,100)) )
		tStr = u'{}:{:02d}:{:02d}'.format( t.hour, t.minute, t.second )
		w, h = ctx.GetTextExtent(u'00:00:00'[:len(tStr)])
		ctx.DrawText( tStr, xCenter-w/2, yCenter+radius/2-h )
		
		#-----------------------------------------------------------------------------
		# Draw the hands.
		#
		secondPos = (t.second  + t.microsecond/1000000.0) / 60.0
		minutePos = (t.minute + secondPos) / 60.0
		hourPos = (t.hour % 12 + minutePos) / 12.0
		
		ctx.SetPen( ctx.CreatePen( GetPen(colour=wx.Colour(0,0,180,128), width=wHourHand) ) )
		cosCur, sinCur = GetCosSin(hourPos)
		ctx.StrokeLine(
			xCenter + rBack * cosCur, yCenter + rBack * sinCur,
			xCenter + rHour * cosCur, yCenter + rHour * sinCur
		)
		ctx.SetPen( ctx.CreatePen( GetPen(colour=wx.Colour(0,150,0,128), width=wMinuteHand) ) )
		cosCur, sinCur = GetCosSin(minutePos)
		ctx.StrokeLine(
			xCenter + rBack * cosCur,   yCenter + rBack * sinCur,
			xCenter + rMinute * cosCur, yCenter + rMinute * sinCur
		)
		
		ctx.SetPen( ctx.CreatePen( GetPen(colour=wx.RED,width=wSecondHand) ) )
		ctx.SetBrush( ctx.CreateBrush(wx.Brush(wx.RED)) )
		cosCur, sinCur = GetCosSin(secondPos)
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
	Clock = Clock(mainWin, tCur=now())
	mainWin.Show()
	wx.CallLater( 5000, Clock.Start )
	app.MainLoop()
