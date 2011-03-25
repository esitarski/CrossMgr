import wx
import random
import math
import bisect
import copy
import sys
import datetime

class Animation(wx.PyControl):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="Animation"):
		"""
		Default class constructor.

		@param parent: Parent window. Must not be None.
		@param id: Animation identifier. A value of -1 indicates a default value.
		@param pos: Animation position. If the position (-1, -1) is specified
					then a default position is chosen.
		@param size: Animation size. If the default size (-1, -1) is specified
					then a default size is chosen.
		@param style: not used
		@param validator: Window validator.
		@param name: Window name.
		"""

		# Ok, let's see why we have used wx.PyControl instead of wx.Control.
		# Basically, wx.PyControl is just like its wxWidgets counterparts
		# except that it allows some of the more common C++ virtual method
		# to be overridden in Python derived class. For Animation, we
		# basically need to override DoGetBestSize and AcceptsFocusFromKeyboard
		
		wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)
		self.SetBackgroundColour('white')
		self.data = None
		self.t = 0
		self.tDelta = 1
		self.r = 100	# Radius of the turns of the fictional track.
		self.laneMax = 8
		
		self.framesPerSecond = 32
		
		self.tLast = datetime.datetime.now()
		self.speedup = 1.0
		
		self.colours = [
			wx.Colour(255, 0, 0),
			wx.Colour(0, 0, 255),
			wx.Colour(255, 255, 0),
			wx.Colour(255, 0, 255),
			wx.Colour(0, 255, 255),
			 ]
			 
		self.numberFont	= wx.Font( 10, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )
		self.timeFont	= wx.Font( 14, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )

		self.timer = wx.Timer( self, id=wx.NewId())
		self.Bind( wx.EVT_TIMER, self.NextFrame, self.timer )
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
	def DoGetBestSize(self):
		return wx.Size(100, 50)
	
	def _initAnimation( self ):
		self.tLast = datetime.datetime.now()
	
	def Animate( self, tRunning, tMax = None, tCur = 0 ):
		self.StopAnimate();
		self._initAnimation()
		self.t = tCur
		if not self.data:
			return
		if tMax is None:
			tMax = 0
			for num, info in self.data.iteritems():
				tMax = max(tMax, info['lapTimes'][-1])
		self.speedup = float(tMax) / float(tRunning)
		self.tMax = tMax
		self.timer.Start( 1000.0/self.framesPerSecond, False )
	
	def StartAnimateRealtime( self ):
		self.StopAnimate();
		self._initAnimation()
		self.speedup = 1.0
		self.tMax = 999999
		self.timer.Start( 1000.0/self.framesPerSecond, False )
	
	def StopAnimate( self ):
		if self.timer.IsRunning():
			self.timer.Stop();
			
	def IsAnimating( self ):
		return self.timer.IsRunning()
	
	def SetTime( self, t ):
		self.t = t
		self.Refresh()
	
	def NextFrame( self, event ):
		if event.GetId() == self.timer.GetId():
			tNow = datetime.datetime.now()
			tDelta = tNow - self.tLast
			self.tLast = tNow
			secsDelta = tDelta.seconds + tDelta.microseconds / 1000000.0
			self.SetTime( self.t + secsDelta * self.speedup )
			if self.t >= self.tMax:
				self.StopAnimate()

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

	def SetData( self, data, tCur = None ):
		"""
		* data is a rider information indexed by number.  Info includes lap times and lastTime times.
		* lap times should include the start offset.
		Example:
			data = { 101: { lapTimes: [xx, yy, zz], lastTime: None }, 102 { lapTimes: [aa, bb], lastTime: cc} }
		"""
		self.data = data if data else None
		if tCur is not None:
			self.t = tCur;
		self.Refresh()
	
	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		
	def getRiderPosition( self, rider ):
		""" Returns the fraction of the lap covered by the rider. """
		if rider not in self.data:
			return None
		if self.data[rider]['lastTime'] is not None and self.t >= self.data[rider]['lastTime']:
			return None
		lapTimes = self.data[rider]['lapTimes']
		if not lapTimes or self.t <= lapTimes[0]:
			return None
		if self.t >= lapTimes[-1]:
			p = len(lapTimes) + float(self.t - lapTimes[-1]) / float(lapTimes[-1] - lapTimes[-2])
		else:
			i = bisect.bisect_left( lapTimes, self.t )
			p = i + float(self.t - lapTimes[i-1]) / float(lapTimes[i] - lapTimes[i-1])
		return p
	
	def getRiderXY( self, num, lane ):
		position = self.getRiderPosition( num )
		if position is None:
			return None
		position -= int(position)
		
		r = self.r
		curveLength = (r/2) * math.pi
		trackLength = 4*r + 2 * curveLength
		laneLength = (r/2) * (lane / float(self.laneMax))
		riderLength = trackLength * position
		
		if riderLength <= r/2:
			# rider is on starting straight
			return (2*r + r/2.0 + riderLength, r + r/2.0 + laneLength )
			
		riderLength -= r/2
		if riderLength <= curveLength:
			# rider is on 1st curve
			a = math.pi * riderLength / curveLength
			rd = r/2 + laneLength
			return (3*r + rd*math.sin(a), r + rd*math.cos(a))

		riderLength -= curveLength
		if riderLength <= 2*r:
			# rider is on back straight
			return (3*r - riderLength, r/2 - laneLength)
			
		riderLength -= 2*r
		if riderLength <= curveLength:
			# rider is on back curve
			a = math.pi * (1.0 + riderLength / curveLength)
			rd = r/2 + laneLength
			return (r + rd*math.sin(a), r + rd*math.cos(a) )
			
		riderLength -= curveLength
		# rider is on finishing straight
		return (r + riderLength, r + r/2 + laneLength)
	
	def Draw(self, dc):
		size = self.GetClientSize()
		width = size.width
		height = size.height
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		if width < 80 or height < 80:
			return

		self.r = int(width / 4)
		if self.r * 2 > height:
			self.r = int(height / 2)
		self.r -= (self.r & 1)			# Make sure that r is an even number.
		
		r = self.r
		# Draw the track.
		trackColour = wx.Colour(0,255,0)
		dc.SetBrush( wx.Brush(trackColour, wx.SOLID) )
		dc.SetPen( wx.Pen(trackColour, 0, wx.SOLID) )
		dc.DrawCircle( r, r, r )
		dc.DrawCircle( 3*r, r, r )
		dc.DrawRectangle( r, 0, 2*r, 2*r + 2 )
		
		# Draw the negative space.
		laneWidth = (r/2) / self.laneMax
		dc.SetBrush( backBrush )
		dc.SetPen( wx.Pen(backColour, 0, wx.SOLID) )
		dc.DrawCircle( r, r, r/2 - laneWidth )
		dc.DrawCircle( 3*r, r, r/2 - laneWidth )
		dc.DrawRectangle( r, r/2 + laneWidth, 2*r, r - 2*laneWidth + 1 )
		
		# Draw the Start/Finish line.
		dc.SetPen( wx.Pen(wx.Colour(0,0,0), 2, wx.SOLID) )
		dc.DrawLine( 2*r + r/2, r + r/2 - laneWidth - 1, 2*r + r/2, 2*r + 2)
		
		# Draw the race time
		dc.SetFont( self.timeFont )
		secs = int( self.t )
		if secs < 60*60:
			tStr = '%d:%02d' % ((secs / 60)%60, secs % 60 )
		else:
			tStr = '%d:%02d:%02d' % (secs / (60*60), (secs / 60)%60, secs % 60 )
		tWidth, tHeight = dc.GetTextExtent( tStr )
		dc.DrawText( tStr, 4*r - tWidth, 2*r - tHeight )
		
		# Draw the riders
		dc.SetFont( self.numberFont )
		dc.SetPen( wx.BLACK_PEN )
		numSize = (r/2)/self.laneMax
		if self.data:
			for num, d in self.data.iteritems():
				xy = self.getRiderXY( num, num % self.laneMax )
				if xy is not None:
					dc.SetBrush( wx.Brush(self.colours[num % len(self.colours)], wx.SOLID) )
					dc.DrawCirclePoint( xy, laneWidth )
					dc.DrawLabel(str(num), wx.Rect(xy[0]+numSize, xy[1]-numSize, numSize*2, numSize*2) )
		
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="Animation", size=(600,400))
	Animation = Animation(mainWin)
	data = {}
	for num in xrange(100,130):
		mean = random.normalvariate(6.0, 0.3)
		lapTimes = [0]
		for lap in xrange( 15 ):
			lapTimes.append( lapTimes[-1] + random.normalvariate(mean, mean/20)*60.0 )
		data[num] = { 'lapTimes': lapTimes, 'lastTime': None }
	Animation.SetData( data )
	Animation.Animate( 1*60, 60*60 )
	mainWin.Show()
	app.MainLoop()
