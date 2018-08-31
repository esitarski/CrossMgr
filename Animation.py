import wx
import random
import math
import bisect
import datetime
import random
import Utils

shapes = [ [(math.cos(a), -math.sin(a)) \
					for a in (q*(2.0*math.pi/i)+math.pi/2.0+(2.0*math.pi/(i*2.0) if i % 2 == 0 else 0)\
						for q in xrange(i))] for i in xrange(3,9)]
def DrawShape( dc, num, x, y, radius ):
	dc.DrawPolygon( [ wx.Point(p*radius+x, q*radius+y) for p,q in shapes[num % len(shapes)] ] )

def GetLapRatio( leaderRaceTimes, tCur, iLapHint ):
	maxLaps = len(leaderRaceTimes) - 1
	if maxLaps < 1:
		return 0, 0.0
		
	if 0 <= iLapHint < maxLaps and \
			leaderRaceTimes[iLapHint] <= tCur < leaderRaceTimes[iLapHint+1]:
		lapRatio = (tCur - leaderRaceTimes[iLapHint]) / (leaderRaceTimes[iLapHint + 1] - leaderRaceTimes[iLapHint])
	elif tCur <= leaderRaceTimes[0]:
		iLapHint = 0
		lapRatio = 0.0
	elif tCur >= leaderRaceTimes[-1]:
		iLapHint = maxLaps - 1
		lapRatio = 1.0
	else:
		iLapHint = max( 0, min(maxLaps, iLapHint) )
		for iLapHint in xrange(iLapHint+1 if leaderRaceTimes[iLapHint] < tCur else 0, maxLaps):
			if leaderRaceTimes[iLapHint] <= tCur:
				break
		lapRatio = (tCur - leaderRaceTimes[iLapHint]) / (leaderRaceTimes[iLapHint + 1] - leaderRaceTimes[iLapHint])
	return iLapHint, lapRatio
	
class Animation(wx.Control):
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

		# Ok, let's see why we have used wx.Control instead of wx.Control.
		# Basically, wx.Control is just like its wxWidgets counterparts
		# except that it allows some of the more common C++ virtual method
		# to be overridden in Python derived class. For Animation, we
		# basically need to override DoGetBestSize and AcceptsFocusFromKeyboard
		
		wx.Control.__init__(self, parent, id, pos, size, style, validator, name)
		self.SetBackgroundColour('white')
		self.data = {}
		self.categoryDetails = {}
		self.t = 0
		self.tMax = None
		self.tDelta = 1
		self.r = 100	# Radius of the turns of the fictional track.
		self.laneMax = 8
		
		self.framesPerSecond = 32
		self.lapCur = 0
		self.iLapDistance = 0
		
		self.tLast = datetime.datetime.now()
		self.speedup = 1.0
		
		self.suspendAnimation = False
		self.numsToWatch = set()
		
		self.reverseDirection = False
		self.finishTop = False
		self.clockwise = False
		
		self.course = 'track'
		
		'''
		self.colours = [
			wx.Colour(255, 0, 0),
			wx.Colour(0, 0, 255),
			wx.Colour(255, 255, 0),
			wx.Colour(255, 0, 255),
			wx.Colour(0, 255, 255),
			wx.Colour(128, 0, 0),
			wx.Colour(0, 0, 128),
			wx.Colour(128, 128, 0),
			wx.Colour(128, 0, 128),
			wx.Colour(0, 128, 128),
			 ]
		self.colours = makeColourGradient(	1.666,	2.666,	3.666,
											  0,			  0,	  0,
											128,			127,
											241)
		'''
		
		trackRGB = [int('7FE57F'[i:i+2],16) for i in xrange(0, 6, 2)]
		self.trackColour = wx.Colour( *trackRGB )
		
		self.colours = []
		k = [0,32,64,128,128+32,128+64,255]
		for r in k:
			for g in k:
				for b in k:
					if  sum( abs(c - t) for c, t in zip([r,g,b],trackRGB) ) > 80 and \
						sum( c for c in [r,g,b] ) > 64:
						self.colours.append( wx.Colour(r, g, b) )
		random.seed( 1234 )
		random.shuffle( self.colours )
			 
		self.topThreeColours = [
			wx.Colour(255,215,0),
			wx.Colour(230,230,230),
			wx.Colour(205,133,63)
			]
		self.trackColour = wx.Colour( *[int('7FE57F'[i:i+2],16) for i in xrange(0, 6, 2)] )
		
		# Cache the fonts if the size does not change.
		self.numberFont	= None
		self.timeFont	= None
		self.highlightFont = None
		self.rLast = -1
			 
		self.timer = wx.Timer( self, id=wx.ID_ANY )
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
				try:
					tMax = max(tMax, info['raceTimes'][-1])
				except IndexError:
					pass
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

	def SetData( self, data, tCur = None, categoryDetails = None ):
		"""
		* data is a rider information indexed by number.  Info includes lap times and lastTime times.
		* lap times should include the start offset.
		Example:
			data = { 101: { raceTimes: [xx, yy, zz], lastTime: None }, 102 { raceTimes: [aa, bb], lastTime: cc} }
		"""
		self.data = data if data else {}
		self.categoryDetails = categoryDetails if categoryDetails else {}
		for num, info in self.data.iteritems():
			info['iLast'] = 1
			if info['status'] == 'Finisher' and info['raceTimes']:
				info['finishTime'] = info['raceTimes'][-1]
			else:
				info['finishTime'] = info['lastTime']
				
		# Get the units.
		for num, info in self.data.iteritems():
			if info['status'] == 'Finisher':
				try:
					self.units = 'miles' if 'mph' in info['speed'] else 'km'
				except KeyError:
					self.units = 'km'
				break
				
		if tCur is not None:
			self.t = tCur;
		self.Refresh()
	
	def SetOptions( self, reverseDirection = False, finishTop = False ):
		self.reverseDirection = reverseDirection
		self.finishTop = finishTop
		self.Refresh()
		
	def isClockwise( self ):
		return self.clockwise
		
	def setClockwise( self, clockwise = True ):
		if self.clockwise != clockwise:
			self.clockwise = clockwise
			if clockwise:
				self.reverseDirection = not self.finishTop
			else:
				self.reverseDirection = self.finishTop
			self.Refresh()
			
	def setFinishTop( self, finishTop = True ):
		if self.finishTop != finishTop:
			self.finishTop = finishTop
			self.reverseDirection = not self.reverseDirection
			self.Refresh()
	
	def getShortName( self, num ):
		try:
			info = self.data[num]
		except KeyError:
			return ''
		
		lastName = info.get('LastName',u'')
		firstName = info.get('FirstName',u'')
		if lastName:
			if firstName:
				return u'{}, {}.'.format(lastName, firstName[:1])
			else:
				return lastName
		return firstName
	
	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def getRiderPositionTime( self, num ):
		""" Returns the fraction of the lap covered by the rider and the time. """
		if num not in self.data:
			return (None, None)
		info = self.data[num]
		raceTimes = info['raceTimes']
		if not raceTimes or self.t < raceTimes[0] or len(raceTimes) < 2:
			return (None, None)

		tSearch = self.t
		finishTime = info['finishTime']
		if finishTime is not None and finishTime < self.t:
			if finishTime == raceTimes[-1]:
				return (len(raceTimes), finishTime)
			tSearch = finishTime
		
		if tSearch >= raceTimes[-1]:
			p = len(raceTimes) + float(tSearch - raceTimes[-1]) / float(raceTimes[-1] - raceTimes[-2])
		else:
			i = info['iLast']
			if not (raceTimes[i-1] < tSearch <= raceTimes[i]):
				i += 1
				if not (raceTimes[i-1] < tSearch <= raceTimes[i]):
					i = bisect.bisect_left( raceTimes, tSearch )
				info['iLast'] = i
				
			if i == 1:
				firstLapRatio = info['flr']
				p = float(tSearch - raceTimes[i-1]) / float(raceTimes[i] - raceTimes[i-1])
				p = 1.0 - firstLapRatio + p * firstLapRatio
				p -= math.floor(p) - 1.0
			else:
				p = i + float(tSearch - raceTimes[i-1]) / float(raceTimes[i] - raceTimes[i-1])
			
		return (p, tSearch)
	
	def getXYfromPosition( self, lane, position ):
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
			self.lapCur = max(self.lapCur, len(self.data[num]['raceTimes']))
			return (None, None, positionTime[0], positionTime[1])
		self.lapCur = max(self.lapCur, int(positionTime[0]))
		xypt = list(self.getXYfromPosition( lane, positionTime[0] ))
		if self.reverseDirection:
			xypt[0] = self.r * 4 - xypt[0]
		if self.finishTop:
			xypt[1] = self.r * 2 - xypt[1]
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
			self.numberFont = wx.Font( (0,tHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
			self.leaderFont = wx.Font( (0,tHeight * 0.9), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
			self.timeFont = self.numberFont
			self.highlightFont = wx.Font( (0,tHeight * 1.6), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
			self.rLast = r
			
		# Draw the track.
		dc.SetBrush( wx.Brush(self.trackColour, wx.SOLID) )
		dc.SetPen( wx.Pen(self.trackColour, 0, wx.SOLID) )
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
		
		# Draw the quarter lines.
		for p in [0.0, 0.25, 0.50, 0.75]:
			x1, y1 = self.getXYfromPosition(-1, p)
			x2, y2 = self.getXYfromPosition(self.laneMax+0.25, p)
			if self.reverseDirection:
				x1 = 4*r - x1
				x2 = 4*r - x2
			if self.finishTop:
				y1 = 2*r - y1
				y2 = 2*r - y2
			if p == 0.0:
				# Draw the Start/Finish line.
				dc.SetBrush( wx.WHITE_BRUSH )
				sfWidth = 8
				dc.DrawRectangle( x1 - sfWidth / 2, min(y1, y2), sfWidth, r )
				dc.SetPen( wx.Pen(wx.Colour(0,0,0), 2, wx.SOLID) )
			else:
				# Else, draw a regular quarter line on the course.
				dc.SetPen( wx.Pen(wx.Colour(64,64,64), 1, wx.SOLID) )
			dc.DrawLine( x1, y1, x2, y2 )
		
		# Draw the riders
		dc.SetFont( self.numberFont )
		dc.SetPen( wx.BLACK_PEN )
		numSize = (r/2)/self.laneMax
		self.lapCur = 0
		topThree = {}
		riderRadius = laneWidth * 0.75
		thickLine = r / 32
		highlightPen = wx.Pen( wx.Colour(255,255,255), thickLine * 1.0 )
		riderPosition = {}
		if self.data:
			riderXYPT = []
			for num, d in self.data.iteritems():
				xypt = list(self.getRiderXYPT(num, num % self.laneMax))
				xypt.insert( 0, num )
				riderXYPT.append( xypt )
			
			# Sort by reverse greatest distance, then by shortest time.
			# Do this so the leaders are drawn last.
			riderXYPT.sort( key=lambda x : ( x[3] if x[3] is not None else 0.0,
											-x[4] if x[4] is not None else 0.0) )
			
			topThree = {}
			for j, i in enumerate(xrange(len(riderXYPT) - 1, max(-1,len(riderXYPT)-4), -1)):
				topThree[riderXYPT[i][0]] = j
			
			numRiders = len(riderXYPT)
			for j, (num, x, y, position, time) in enumerate(riderXYPT):
				riderPosition[num] = numRiders - j
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
				DrawShape( dc, num, x, y, riderRadius )
				dc.DrawLabel(u'{}'.format(num), wx.Rect(x+numSize, y-numSize, numSize*2, numSize*2) )
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
			tLap = ''
			tDistance = ''
			if leaders:
				leaderRaceTimes = self.data[leaders[0]]['raceTimes']
				maxLaps = len(leaderRaceTimes) - 1
				self.iLapDistance, lapRatio = GetLapRatio( leaderRaceTimes, self.t, self.iLapDistance )
				lapRatio = int(lapRatio * 10.0) / 10.0		# Always round down, not to nearest decimal.
				tLap = u'{:05.1f} {} {},{:05.1f} {}'.format(	self.iLapDistance + lapRatio,
																_('Laps of'), maxLaps,
																maxLaps - self.iLapDistance - lapRatio, _('Laps to go') )
				cat = self.categoryDetails.get( self.data[leaders[0]].get('raceCat', None) )
				if cat:
					distanceCur, distanceRace = None, None
					
					if cat.get('lapDistance', None) is not None:
						flr = self.data[leaders[0]].get('flr', 1.0)
						distanceLap = cat['lapDistance']
						distanceRace = distanceLap * (flr + maxLaps-1)
						if self.iLapDistance == 0:
							distanceCur = lapRatio * (distanceLap * flr)
						else:
							distanceCur = distanceLap * (flr + self.iLapDistance - 1 + lapRatio)
					elif cat.get('raceDistance', None) is not None and leaderRaceTimes[0] != leaderRaceTimes[-1]:
						distanceRace = cat['raceDistance']
						distanceCur = (self.t - leaderRaceTimes[0]) / (leaderRaceTimes[-1] - leaderRaceTimes[0]) * distanceRace
						distanceCur = max( 0.0, min(distanceCur, distanceRace) )
						
					if distanceCur is not None:
						if distanceCur != distanceRace:
							distanceCur = int( distanceCur * 10.0 ) / 10.0
						tDistance = u'{:05.1f} {} {} {:.1f},{:05.2f} {} {}'.format(
											distanceCur, self.units,
											_('of'), distanceRace,
											distanceRace - distanceCur, self.units, _('to go')
										)
			
			tWidth, tHeight = dc.GetTextExtent( '999' )
			xRight  = 3*r + r/7
			table = []
			if tLap:
				table.append( tLap.split(',') )
			if tDistance:
				table.append( tDistance.split(',') )
			table = zip(*table)	# Transpose the table.  Nice!
			for col in xrange(len(table[0])-1, -1, -1):
				tWidth = max( dc.GetTextExtent(table[row][col])[0] for row in xrange(len(table)) )
				xRight -= tWidth
				yCur = r + r/2 - laneWidth - tHeight * 1.25 - tHeight
				for row in xrange(len(table)):
					t = table[row][col]
					tShow = t.lstrip('0')
					if tShow.startswith('.'):
						tShow = '0' + tShow
					dc.DrawText( tShow, xRight + dc.GetTextExtent('0' * (len(t) - len(tShow)))[0], yCur )
					yCur += tHeight
				xRight -= tHeight / 2.5

		# Draw the leader board.
		leaderHeader = u'{}:'.format(_('Leaders'))
		xLeft = int(r * 0.85)
		leaderWidth = 0
		if leaders:
			dc.SetFont( self.leaderFont )
			x = xLeft
			y = r / 2 + laneWidth * 1.5
			tWidth, tHeight = dc.GetTextExtent( leaderHeader )
			dc.DrawText( leaderHeader, x, y )
			leaderWidth = dc.GetTextExtent(leaderHeader)[0]
			y += tHeight
			thickLine = tHeight / 5
			riderRadius = tHeight / 3.5
			for i, num in enumerate(leaders):
				dc.SetPen( wx.Pen(backColour, 0) )
				dc.SetBrush( wx.Brush(self.trackColour, wx.SOLID) )
				dc.DrawRectangle( x - thickLine/4, y - thickLine/4, tHeight + thickLine/2, tHeight  + thickLine/2)
				
				dc.SetPen( wx.Pen(self.topThreeColours[i], thickLine) )
				dc.SetBrush( wx.Brush(self.colours[num % len(self.colours)], wx.SOLID) )
				DrawShape( dc, num, x + tHeight / 2, y + tHeight / 2, riderRadius )
				
				s = u'{} {}'.format(num, self.getShortName(num))
				tWidth, tHeight = dc.GetTextExtent( s )
				leaderWidth = max(tWidth, leaderWidth)
				dc.DrawText( s, x + tHeight * 1.2, y)
				y += tHeight

		# Draw the positions of the highlighted ridrs
		if self.numsToWatch:
			rp = []
			for n in self.numsToWatch:
				try:
					rp.append( (riderPosition[n], n) )
				except KeyError:
					pass
			rp.sort()
			
			colCount = 0
			tWidth, tHeight = dc.GetTextExtent(leaderHeader)
			spaceWidth, spaceHeight = dc.GetTextExtent(' ')
			x = xLeft + leaderWidth + spaceWidth
			yTop = r / 2 + laneWidth * 1.5+ tHeight
			y = yTop
			for i, (pos, num) in enumerate(rp):
				if i >= 4:
					break
				s = u'({}) {} {}'.format(Utils.ordinal(pos), num, self.getShortName(num) )
				dc.DrawText( s, x + tHeight * 1.2, y)
				y += tHeight
				if y > r * 1.5 - tHeight * 1.5:
					colCount += 1
					if colCount == 2:
						break
					y = yTop
					x += tWidth * 1.2
				
		# Draw the race time
		secs = int( self.t )
		if secs < 60*60:
			tStr = '{}:{:02d}'.format((secs / 60)%60, secs % 60 )
		else:
			tStr = '{}:{:02d}:{:02d}'.format(secs / (60*60), (secs / 60)%60, secs % 60 )
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
		raceTimes = [0]
		for lap in xrange( 5 ):
			raceTimes.append( raceTimes[-1] + random.normalvariate(mean, mean/20)*60.0 )
		data[num] = { 'raceTimes': raceTimes, 'lastTime': raceTimes[-1], 'status':'Finisher', 'speed':'32.7 km/h' , 'flr':1.0 }

	# import json
	# with open('race.json', 'w') as fp: fp.write( json.dumps(data, sort_keys=True, indent=4) )

	app = wx.App(False)
	mainWin = wx.Frame(None,title="Animation", size=(600,400))
	animation = Animation(mainWin)
	animation.SetData( data )
	animation.Animate( 2*60, 60*60 )
	mainWin.Show()
	app.MainLoop()
