import wx
import random
import math
from math import radians, sin, cos, asin, sqrt, atan2, exp
import bisect
import copy
import sys
import datetime
import random
import os
from operator import itemgetter, attrgetter
from GanttChart import makePastelColours, makeColourGradient
import Utils
import xml.etree.ElementTree
import xml.etree.cElementTree
import xml.dom
import xml.dom.minidom
from xml.dom.minidom import parse
import collections

def LineNormal( x1, y1, x2, y2, normLen ):
	''' Returns the coords of a normal line passing through x1, y1 of length normLen. '''
	dx, dy = x2 - x1, y2 - y1
	scale = (normLen / 2.0) / math.sqrt( dx**2 + dy**2 )
	dx *= scale
	dy *= scale
	return x1 + dy, y1 - dx, x1 - dy, y1 + dx

def GreatCircleDistance( lat1, lon1, lat2, lon2 ):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) in meters.
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2.0 * asin(sqrt(max(a, 0.0))) 
    m = 6371000.0 * c
    return m

def GreatCircleDistance3D( lat1, lon1, ele1, lat2, lon2, ele2 ):
	d = GreatCircleDistance( lat1, lon1, lat2, lon2 )
	return sqrt( d ** 2 + (ele2 - ele1) ** 2 )
	
def GradeAdjustedDistance( lat1, lon1, ele1, lat2, lon2, ele2 ):
	d = GreatCircleDistance(lat1, lon1, lat2, lon2 )
	if not d:
		return 0.0
	a = atan2( ele2 - ele1, d )
	m = 2.0 / (1.0 + exp(-a * 2.5))		# Use a sigmoid curve to approximate the effect of grade on speed.
	return m * d

LatLonEle = collections.namedtuple('LatLonEle', ['lat','lon','ele'] )
GpsPoint = collections.namedtuple('GpsPoint', ['lat','lon','ele','x','y','d','dCum'] )

def triangle( t, a ):
	a = float(a)
	return (2 / a) * (t - a * int(t / a + 0.5)) * (-1 ** int(t / a + 0.5))

def ParseGpxFile( fname ):
	doc = parse( open(fname) )
	latMin, lonMin = 1000.0, 1000.0
	latLonEles = []
	for trkpt in doc.getElementsByTagName('trkpt'):
		try:
			lat = float( trkpt.getAttribute('lat') )
			lon = float( trkpt.getAttribute('lon') )
		except:
			continue
		
		latMin = min( latMin, lat )
		lonMin = min( lonMin, lon )

		ele = 0.0
		for e in trkpt.getElementsByTagName('ele'):
			ele = float( e.firstChild.nodeValue )
			
		latLonEles.append( LatLonEle(lat, lon, ele) )
		
	gpsPoints = []
	dCum = 0.0
	for i in xrange(len(latLonEles)):
		p, pNext = latLonEles[i], latLonEles[(i+1) % len(latLonEles)]
		gad = GradeAdjustedDistance( p.lat, p.lon, p.ele, pNext.lat, pNext.lon, pNext.ele )
		x = GreatCircleDistance( latMin, lonMin, latMin, p.lon )
		y = GreatCircleDistance( latMin, lonMin, p.lat, lonMin )
		gpsPoints.append( GpsPoint(p.lat, p.lon, p.ele, x, y, gad, dCum) )
		dCum += gad
	
	doc.unlink()
	return gpsPoints

class GeoTrack( object ):
	def __init__( self ):
		self.gpsPoints = []
		self.distanceTotal = 0.0
		self.cumDistance = []
		self.x = 0
		self.xMax = self.yMax = 0.0
		self.yBottom = 0
		self.mult = 1.0
		self.length = 0.0
		self.cache = {}
		
	def read( self, fname ):
		self.gpsPoints = ParseGpxFile( fname )
		self.xMax = max( p.x for p in self.gpsPoints )
		self.yMax = max( p.y for p in self.gpsPoints )
		dCum = 0.0
		self.cumDistance = []
		for p in self.gpsPoints:
			self.cumDistance.append( dCum )
			dCum += p.d
		self.distanceTotal = dCum
		
		lenGpsPoints = len(self.gpsPoints)
		length = 0.0
		for i in xrange(lenGpsPoints):
			pCur, pNext = self.gpsPoints[i], self.gpsPoints[(i + 1) % lenGpsPoints]
			length += GreatCircleDistance3D( pCur.lat, pCur.lon, pCur.ele, pNext.lat, pNext.lon, pNext.ele )
		self.length = length
			
	def getXYTrack( self ):
		x, yBottom, mult = self.x, self.yBottom, self.mult
		return [(p.x * mult + x, yBottom - p.y * mult) for p in self.gpsPoints]
		
	def asExportJson( self ):
		return [ [int(getattr(p, a)*10.0) for a in ('x', 'y', 'd')] for p in self.gpsPoints ]
		
	def getXY( self, lap, id = None ):
		# Find the segment at this distance in the lap.
		lap = math.modf(lap)[0]								# Get fraction of lap.
		lapDistance = lap * self.distanceTotal				# Get distance traveled in the lap.
		
		# Avoid the cost of the binary search by checking if the id request is still on the last segment.
		lenGpsPoints = len(self.gpsPoints)
		try:
			i = self.cache[id]
			pCur, pNext = self.gpsPoints[i], self.gpsPoints[(i + 1) % lenGpsPoints]
			if not (pCur.d <= lapDistance <= pNext.d):
				i = (i + 1) % lenGpsPoints
				pCur, pNext = pNext, self.gpsPoints[(i + 1) % lenGpsPoints]
				if not (pCur.d <= lapDistance <= pNext.d):
					i = None
		except (IndexError, KeyError):
			i = None
			
		if i is None:
			i = bisect.bisect_right( self.cumDistance, lapDistance )-1	# Find the closest point LE the lap distance.
			i = (i + lenGpsPoints) % lenGpsPoints
			pCur, pNext = self.gpsPoints[i], self.gpsPoints[(i + 1) % lenGpsPoints]
		
		self.cache[id] = i
		
		segDistance = lapDistance - self.cumDistance[i]
		segRatio = segDistance / pCur.d
		
		x, y = pCur.x + (pNext.x - pCur.x) * segRatio, pCur.y + (pNext.y - pCur.y) * segRatio
		return x * self.mult + self.x, self.yBottom - y * self.mult

	@property
	def lengthKm( self ):
		return self.length / 1000.0
		
	@property
	def lengthMiles( self ):
		return self.length * 0.621371/1000.0
		
	@property
	def numPoints( self ):
		return len(self.gpsPoints)
		
	def setDisplayRect( self, x, y, width, height ):
		if width <= 0 or height <= 0:
			self.mult = 1.0
			self.x = x
			self.yBottom = y + height
			return
		mult = min( width / self.xMax, height / self.yMax )
		w, h = self.xMax * mult, self.yMax * mult
		xBorder = (width - w) / 2.0
		yBorder = (height - h) / 2.0
		self.mult = mult
		self.x = xBorder + x
		self.yBottom = y + height
		
shapes = [ [(math.cos(a), -math.sin(a)) \
					for a in (q*(2.0*math.pi/i)+math.pi/2.0+(2.0*math.pi/(i*2.0) if i % 2 == 0 else 0)\
						for q in xrange(i))] for i in xrange(3,9)]
def DrawShape( dc, num, x, y, radius ):
	dc.DrawPolygon( [ wx.Point(p*radius+x, q*radius+y) for p,q in shapes[num % len(shapes)] ] )
	
class GeoAnimation(wx.PyControl):
	topFewCount = 5
	infoLines = topFewCount + 1

	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="GeoAnimation"):
		"""
		Default class constructor.

		@param parent: Parent window. Must not be None.
		@param id: GeoAnimation identifier. A value of -1 indicates a default value.
		@param pos: GeoAnimation position. If the position (-1, -1) is specified
					then a default position is chosen.
		@param size: GeoAnimation size. If the default size (-1, -1) is specified
					then a default size is chosen.
		@param style: not used
		@param validator: Window validator.
		@param name: Window name.
		"""

		wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)
		self.SetBackgroundColour('white')
		self.data = {}
		self.t = 0
		self.tMax = None
		self.tDelta = 1
		self.r = 100	# Radius of the turns of the fictional track.
		self.laneMax = 8
		
		self.course = 'geo'
		
		self.framesPerSecond = 32
		self.lapCur = 0
		
		self.tLast = datetime.datetime.now()
		self.speedup = 1.0
		
		self.suspendGeoAnimation = False
		self.numsToWatch = set()
		
		self.checkeredFlag = wx.Bitmap(os.path.join(Utils.getImageFolder(), 'CheckeredFlag.png'), wx.BITMAP_TYPE_PNG)	
		
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
			 
		self.topFewColours = [
			wx.Colour(255,215,0),
			wx.Colour(230,230,230),
			wx.Colour(205,133,63)
			]
		while len(self.topFewColours) < self.topFewCount:
			self.topFewColours.append( wx.Colour(200,200,200) )
		self.trackColour = wx.Colour( *[int('7FE57F'[i:i+2],16) for i in xrange(0, 6, 2)] )
		
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
		
	def SetGeoTrack( self, geoTrack ):
		self.geoTrack = geoTrack
		
	def SetOptions( self, *argc, **kwargs ):
		pass
		
	def DoGetBestSize(self):
		return wx.Size(400, 200)
	
	def _initGeoAnimation( self ):
		self.tLast = datetime.datetime.now()
		self.suspendGeoAnimation = False
	
	def Animate( self, tRunning, tMax = None, tCur = 0.001 ):
		self.StopAnimate();
		self._initGeoAnimation()
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
		self._initGeoAnimation()
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
		self.suspendGeoAnimation = True;
	
	def IsAnimating( self ):
		return not self.suspendGeoAnimation and self.timer.IsRunning()
	
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
			if self.suspendGeoAnimation or self.t >= self.tMax:
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
			data = { 101: { raceTimes: [xx, yy, zz], lastTime: None }, 102 { raceTimes: [aa, bb], lastTime: cc} }
		"""
		self.data = data if data else {}
		for num, info in self.data.iteritems():
			info['iLast'] = 1
		if tCur is not None:
			self.t = tCur;
		self.Refresh()
	
	def getShortName( self, num ):
		try:
			info = self.data[num]
		except KeyError:
			return ''
			
		lastName = info.get('LastName','')
		firstName = info.get('FirstName','')
		if lastName:
			if firstName:
				return '%s, %s.' % (lastName, firstName[:1])
			else:
				return lastName
		return firstName
	
	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		
	def getRiderPositionTime( self, num ):
		""" Returns the fraction of the lap covered by the rider and the time. """
		if num not in self.data:
			return (None, None)
		info = self.data[num]
		raceTimes = info['raceTimes']
		if not raceTimes or self.t < raceTimes[0] or len(raceTimes) < 2:
			return (None, None)

		tSearch = self.t
		lastTime = info['lastTime']
		if lastTime is not None and lastTime < self.t:
			if lastTime == raceTimes[-1]:
				return (len(raceTimes), lastTime)
			tSearch = lastTime
		
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
	
	def getRiderXYPT( self, num ):
		positionTime = self.getRiderPositionTime( num )
		if positionTime[0] is None:
			return None, None, None, None
		if self.data[num]['lastTime'] is not None and self.t >= self.data[num]['lastTime']:
			self.lapCur = max(self.lapCur, len(self.data[num]['raceTimes']))
			return (None, None, positionTime[0], positionTime[1])
		self.lapCur = max(self.lapCur, int(positionTime[0]))
		xy = self.geoTrack.getXY( positionTime[0], num )
		return xy[0], xy[1], positionTime[0], positionTime[1]
	
	def Draw(self, dc):
		size = self.GetClientSize()
		width = size.width
		height = size.height
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		if width < 80 or height < 80 or not self.geoTrack:
			return

		self.r = int(width / 4)
		if self.r * 2 > height:
			self.r = int(height / 2)
		self.r -= (self.r & 1)			# Make sure that r is an even number.
		
		r = self.r
		
		# Get the fonts if needed.
		if self.rLast != r:
			tHeight = int(r / 8.0)
			self.numberFont	= wx.FontFromPixelSize( wx.Size(0,tHeight), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )
			self.timeFont = self.numberFont
			self.highlightFont = wx.FontFromPixelSize( wx.Size(0,tHeight * 1.6), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )
			self.rLast = r
			
		tHeight = int(r / 8.0)
		laneWidth = (r/2) / self.laneMax
		
		border = laneWidth * 1.5 / 2
		trackWidth = width - border * 2
		trackHeight = height - tHeight * self.infoLines - border * 2
		self.geoTrack.setDisplayRect( border, border, trackWidth, trackHeight )
		
		# Draw the course.
		dc.SetBrush( wx.TRANSPARENT_BRUSH )
		
		drawPoints = self.geoTrack.getXYTrack()
		
		dc.SetPen( wx.Pen(wx.Colour(128,128,128), laneWidth * 1.25 + 2, wx.SOLID) )
		dc.DrawPolygon( drawPoints )
		
		dc.SetPen( wx.Pen(self.trackColour, laneWidth * 1.25, wx.SOLID) )
		dc.DrawPolygon( drawPoints )
		
		# Draw a centerline to show all the curves in the course.
		dc.SetPen( wx.Pen(wx.Colour(80,80,80), 1, wx.SOLID) )
		dc.DrawPolygon( drawPoints )
		
		# Draw a finish line.
		finishLineLength = laneWidth * 2
		x1, y1, x2, y2 = LineNormal( drawPoints[0][0], drawPoints[0][1], drawPoints[1][0], drawPoints[1][1], laneWidth * 2 )
		dc.SetPen( wx.Pen(wx.WHITE, laneWidth / 1.5, wx.SOLID) )
		dc.DrawLine( x1, y1, x2, y2 )
		dc.SetPen( wx.Pen(wx.BLACK, laneWidth / 5, wx.SOLID) )
		dc.DrawLine( x1, y1, x2, y2 )
		x1, y1, x2, y2 = LineNormal( drawPoints[0][0], drawPoints[0][1], drawPoints[1][0], drawPoints[1][1], laneWidth * 4 )
		dc.DrawBitmap( self.checkeredFlag, x2 - self.checkeredFlag.Width/2, y2 - self.checkeredFlag.Height/2, False )

		# Draw the riders
		dc.SetFont( self.numberFont )
		dc.SetPen( wx.BLACK_PEN )
		numSize = (r/2)/self.laneMax
		self.lapCur = 0
		topFew = {}
		riderRadius = laneWidth * 0.75
		thickLine = r / 32
		highlightPen = wx.Pen( wx.Colour(255,255,255), thickLine * 1.0 )
		riderPosition = {}
		if self.data:
			riderXYPT = []
			for num, d in self.data.iteritems():
				xypt = list(self.getRiderXYPT(num))
				xypt.insert( 0, num )
				riderXYPT.append( xypt )
			
			# Sort by reverse greatest distance, then by shortest time.
			# Do this so the leaders are drawn last.
			riderXYPT.sort( key=lambda x : ( x[3] if x[3] is not None else 0.0,
											-x[4] if x[4] is not None else 0.0) )
			
			topFew = {}
			for j, i in enumerate(xrange(len(riderXYPT) - 1, max(-1,len(riderXYPT)-self.topFewCount-1), -1)):
				topFew[riderXYPT[i][0]] = j
				
			numRiders = len(riderXYPT)
			for j, (num, x, y, position, time) in enumerate(riderXYPT):
				riderPosition[num] = numRiders - j
				if x is None:
					continue
					
				dc.SetBrush( wx.Brush(self.colours[num % len(self.colours)], wx.SOLID) )
				try:
					i = topFew[num]
					dc.SetPen( wx.Pen(self.topFewColours[i], thickLine) )
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
				if i is not None:
					dc.DrawLabel(str(num), wx.Rect(x+numSize, y-numSize, numSize*2, numSize*2) )
				if i is not None:
					dc.SetPen( wx.BLACK_PEN )
					dc.SetFont( self.numberFont )
			
		# Convert topFew from dict to list.
		leaders = [0] * len(topFew)
		for num, position in topFew.iteritems():
			leaders[position] = num
		
		yTop = height - self.infoLines * tHeight
		# Draw the current lap
		dc.SetFont( self.timeFont )
		if self.lapCur:
			if leaders:
				maxLaps = len(self.data[leaders[0]]['raceTimes'])
			else:
				maxLaps = 9999
			if self.lapCur > maxLaps:
				self.lapCur = maxLaps
			tStr = 'Laps Completed %d' % max(0, self.lapCur-1)
			tWidth, tHeight = dc.GetTextExtent( tStr )
			dc.DrawText( tStr, 4*r - tWidth - 8, height - tHeight*2 )

		# Draw the leader board.
		xLeft = 8
		leaderWidth = 0
		if leaders:
			x = xLeft
			y = yTop
			thickLine = tHeight / 5
			riderRadius = tHeight / 3.5
			for i, num in enumerate(leaders):
				dc.SetPen( wx.Pen(backColour, 0) )
				dc.SetBrush( wx.Brush(self.trackColour, wx.SOLID) )
				dc.DrawRectangle( x - thickLine/4, y - thickLine/4, tHeight + thickLine/2, tHeight  + thickLine/2)
				
				dc.SetPen( wx.Pen(self.topFewColours[i], thickLine) )
				dc.SetBrush( wx.Brush(self.colours[num % len(self.colours)], wx.SOLID) )
				DrawShape( dc, num, x + tHeight / 2, y + tHeight / 2, riderRadius )
				
				s = '%d %s' % (num, self.getShortName(num))
				tWidth, tHeight = dc.GetTextExtent( s )
				leaderWidth = max(tWidth, leaderWidth)
				dc.DrawText( s, x + tHeight * 1.2, y)
				y += tHeight

		# Draw the positions of the highlighted riders
		if self.numsToWatch:
			rp = []
			for n in self.numsToWatch:
				try:
					rp.append( (riderPosition[n], n) )
				except KeyError:
					pass
			rp.sort()
			
			colCount = 0
			tWidth, tHeight = dc.GetTextExtent( 'Leaders:' )
			spaceWidth, spaceHeight = dc.GetTextExtent(' ')
			x = xLeft + leaderWidth + spaceWidth
			y = yTop
			for i, (pos, num) in enumerate(rp):
				if i >= self.infoLines * 2:
					break
				s = '(%s) %d %s' % (Utils.ordinal(pos), num, self.getShortName(num) )
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
			tStr = '%d:%02d' % ((secs / 60)%60, secs % 60 )
		else:
			tStr = '%d:%02d:%02d' % (secs / (60*60), (secs / 60)%60, secs % 60 )
		tWidth, tHeight = dc.GetTextExtent( tStr )
		dc.DrawText( tStr, 4*r - tWidth - 8, height - tHeight )
		
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
		data[num] = { 'raceTimes': raceTimes, 'lastTime': raceTimes[-1], 'flr': 1.0 }

	# import json
	# with open('race.json', 'w') as fp: fp.write( json.dumps(data, sort_keys=True, indent=4) )

	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="GeoAnimation", size=(800,700))
	animation = GeoAnimation(mainWin)
	geoTrack = GeoTrack()
	geoTrack.read( 'EdgeField_Cyclocross_Course.gpx' )
	animation.SetGeoTrack( geoTrack )
	animation.SetData( data )
	animation.Animate( 2*60, 60*60 )
	mainWin.Show()
	app.MainLoop()
