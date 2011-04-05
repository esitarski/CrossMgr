import wx
import random
import math
import bisect
import copy
import sys
import datetime
from operator import itemgetter, attrgetter

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
		self.tMax = None
		self.tDelta = 1
		self.r = 100	# Radius of the turns of the fictional track.
		self.laneMax = 8
		
		self.framesPerSecond = 32
		self.lapCur = 0
		
		self.tLast = datetime.datetime.now()
		self.speedup = 1.0
		
		self.suspendAnimation = False
		self.numsToWatch = set()
		
		self.colours = [
			wx.Colour(255, 0, 0),
			wx.Colour(0, 0, 255),
			wx.Colour(255, 255, 0),
			wx.Colour(255, 0, 255),
			wx.Colour(0, 255, 255),
			 ]
			 
		self.topThreeColours = [
			wx.Colour(255,215,0),
			wx.Colour(230,230,230),
			wx.Colour(205,133,63)
			]
		
		# Cache the fonts if the size does not change.
		self.numberFont	= None
		self.timeFont	= None
		self.highlightFont = None
		self.rLast = -1
			 
		self.timer = wx.Timer( self, id=wx.NewId())
		self.Bind( wx.EVT_TIMER, self.NextFrame, self.timer )
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
	def DoGetBestSize(self):
		return wx.Size(400, 200)
	
	def _initAnimation( self ):
		self.tLast = datetime.datetime.now()
		self.suspendAnimation = False
	
	def Animate( self, tRunning, tMax = None, tCur = 0.001 ):
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
	
	def SetNumsToWatch( self, numsToWatch ):
		self.numsToWatch = numsToWatch
		self.Refresh()
	
	def SuspendAnimate( self ):
		self.suspendAnimation = True;
	
	def IsAnimating( self ):
		return not self.suspendAnimation and self.timer.IsRunning()
	
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
			if self.suspendAnimation or self.t >= self.tMax:
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
		
	def getRiderPositionTime( self, num ):
		""" Returns the fraction of the lap covered by the rider and the time. """
		if num not in self.data:
			return (None, None)
		lapTimes = self.data[num]['lapTimes']
		if not lapTimes or self.t < lapTimes[0]:
			return (None, None)

		tSearch = self.t
		lastTime = self.data[num]['lastTime']
		if lastTime is not None and lastTime < self.t:
			if lastTime == lapTimes[-1]:
				return (len(lapTimes), lastTime)
			tSearch = lastTime
			
		if tSearch >= lapTimes[-1]:
			p = len(lapTimes) + float(tSearch - lapTimes[-1]) / float(lapTimes[-1] - lapTimes[-2])
		else:
			i = bisect.bisect_left( lapTimes, tSearch )
			p = i + float(tSearch - lapTimes[i-1]) / float(lapTimes[i] - lapTimes[i-1])
			
		return (p, tSearch)
	
	def getXYfromPosition( self, lane, position ):
		positionSave = position
		position -= int(position)
		
		r = self.r
		curveLength = (r/2.0) * math.pi
		trackLength = 4*r + 2 * curveLength
		laneWidth = (r/2.0) / self.laneMax
		laneLength = lane * laneWidth
		riderLength = trackLength * position
		
		if riderLength <= r/2:
			# rider is on starting straight
			return (2*r + r/2.0 + riderLength, r + r/2.0 + laneLength )
			
		riderLength -= r/2
		if riderLength <= curveLength:
			# rider is on 1st curve
			a = math.pi * riderLength / curveLength
			rd = r/2 + laneLength
			return (3*r + rd*math.sin(a), r + rd*math.cos(a) )

		riderLength -= curveLength
		if riderLength <= 2*r:
			# rider is on back straight
			return (3*r - riderLength, r/2 - laneLength )
			
		riderLength -= 2*r
		if riderLength <= curveLength:
			# rider is on back curve
			a = math.pi * (1.0 + riderLength / curveLength)
			rd = r/2 + laneLength
			return (r + rd*math.sin(a), r + rd*math.cos(a) )
			
		riderLength -= curveLength
		# rider is on finishing straight
		return (r + riderLength, r + r/2 + laneLength )
	
	def getRiderXYPT( self, num, lane ):
		positionTime = self.getRiderPositionTime( num )
		if positionTime[0] is None:
			return (None, None, None, None)
		if self.data[num]['lastTime'] is not None and self.t >= self.data[num]['lastTime']:
			self.lapCur = max(self.lapCur, len(self.data[num]['lapTimes']))
			return (None, None, positionTime[0], positionTime[1])
		self.lapCur = max(self.lapCur, int(positionTime[0]))
		xypt = list(self.getXYfromPosition( lane, positionTime[0] ))
		xypt.extend( positionTime )
		return tuple( xypt )
	
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
		
		# Get the fonts if needed.
		if self.rLast != r:
			tHeight = r / 8.0
			self.numberFont	= wx.FontFromPixelSize( wx.Size(0,tHeight), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )
			self.timeFont = self.numberFont
			self.highlightFont = wx.FontFromPixelSize( wx.Size(0,tHeight * 1.6), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )
			self.rLast = r
			
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
		dc.SetPen( wx.Pen(wx.Colour(0,0,0), 3, wx.SOLID) )
		dc.DrawLine( 2*r + r/2, r + r/2 - laneWidth - 1, 2*r + r/2, 2*r + 2)

		# Draw the quarter lines.
		dc.SetPen( wx.Pen(wx.Colour(64,64,64), 1, wx.SOLID) )
		for p in [0.25, 0.50, 0.75]:
			x1, y1 = self.getXYfromPosition(-1, p)
			x2, y2 = self.getXYfromPosition(self.laneMax+0.25, p)
			dc.DrawLine( x1, y1, x2, y2 )
		
		# Draw the riders
		dc.SetFont( self.numberFont )
		dc.SetPen( wx.BLACK_PEN )
		numSize = (r/2)/self.laneMax
		self.lapCur = 0
		topThree = {}
		riderRadius = laneWidth * 0.75
		thickLine = r / 24
		highlightPen = wx.Pen( wx.Colour(255,255,255), thickLine * 1.5 )
		if self.data:
			riderXYPT = []
			for num, d in self.data.iteritems():
				xypt = list(self.getRiderXYPT( num, num % self.laneMax ))
				xypt.insert( 0, num )
				riderXYPT.append( xypt )
			
			# Sort by reverse greatest distance, then by shortest time.
			# Do this so the leaders are drawn last.
			riderXYPT.sort( cmp=lambda x,y: -cmp((-x[3], x[4]), (-y[3], y[4]) ) )
			
			topThree = {}
			for j, i in enumerate(xrange(len(riderXYPT) - 1, max(-1,len(riderXYPT)-4), -1)):
				topThree[riderXYPT[i][0]] = j
				
			for num, x, y, position, time in riderXYPT:
				if x is None:
					continue
				dc.SetBrush( wx.Brush(self.colours[num % len(self.colours)], wx.SOLID) )
				try:
					i = topThree[num]
					dc.SetPen( wx.Pen(self.topThreeColours[i], thickLine) )
					if num in self.numsToWatch:
						dc.SetFont( self.highlightFont )
				except KeyError:
					if num in self.numsToWatch:
						dc.SetFont( self.highlightFont )
						dc.SetPen( highlightPen )
						i = 9999
					else:
						i = None
				dc.DrawCircle( x, y, riderRadius )
				dc.DrawLabel(str(num), wx.Rect(x+numSize, y-numSize, numSize*2, numSize*2) )
				if i is not None:
					dc.SetPen( wx.BLACK_PEN )
					dc.SetFont( self.numberFont )
			
		# Convert topThree from dict to list.
		leaders = [0] * len(topThree)
		for num, position in topThree.iteritems():
			leaders[position] = num
			
		# Draw the current lap
		dc.SetFont( self.timeFont )
		if self.lapCur:
			if leaders:
				maxLaps = len(self.data[leaders[0]]['lapTimes'])
			else:
				maxLaps = 9999
			if self.lapCur > maxLaps:
				self.lapCur = maxLaps
			tStr = 'Lap %d' % self.lapCur
			tWidth, tHeight = dc.GetTextExtent( tStr )
			dc.DrawText( tStr, 2*r + r/2 - tWidth, r + r/2 - laneWidth - tHeight * 1.5 )

		# Draw the leader board.
		if leaders:
			x = r
			y = r / 2 + laneWidth * 1.5
			tWidth, tHeight = dc.GetTextExtent( 'Leaders:' )
			dc.DrawText( 'Leaders:', x, y )
			y += tHeight
			thickLine = tHeight / 5
			riderRadius = tHeight / 3.5
			for i, num in enumerate(leaders):
				dc.SetPen( wx.Pen(backColour, 0) )
				dc.SetBrush( wx.Brush(trackColour, wx.SOLID) )
				dc.DrawRectangle( x - thickLine/4, y - thickLine/4, tHeight + thickLine/2, tHeight  + thickLine/2)
				
				dc.SetPen( wx.Pen(self.topThreeColours[i], thickLine) )
				dc.SetBrush( wx.Brush(self.colours[num % len(self.colours)], wx.SOLID) )
				dc.DrawCircle( x + tHeight / 2, y + tHeight / 2, riderRadius )
				
				s = '%d' % num
				dc.DrawText( s, x + tHeight * 1.2, y)
				y += tHeight
			
		# Draw the race time
		secs = int( self.t )
		if secs < 60*60:
			tStr = '%d:%02d' % ((secs / 60)%60, secs % 60 )
		else:
			tStr = '%d:%02d:%02d' % (secs / (60*60), (secs / 60)%60, secs % 60 )
		tWidth, tHeight = dc.GetTextExtent( tStr )
		dc.DrawText( tStr, 4*r - tWidth, 2*r - tHeight )
		
		
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	data = {}
	for num in xrange(100,200):
		mean = random.normalvariate(6.0, 0.3)
		lapTimes = [0]
		for lap in xrange( 5 ):
			lapTimes.append( lapTimes[-1] + random.normalvariate(mean, mean/20)*60.0 )
		data[num] = { 'lapTimes': lapTimes, 'lastTime': lapTimes[-1] }

	# import json
	# open('race.json', 'w').write( json.dumps(data, sort_keys=True, indent=4) )

	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="Animation", size=(600,400))
	Animation = Animation(mainWin)
	Animation.SetData( data )
	Animation.Animate( 1*60, 60*60 )
	mainWin.Show()
	app.MainLoop()
