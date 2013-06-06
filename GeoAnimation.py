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
import re
import cgi
import getpass
import socket
from operator import itemgetter, attrgetter
from GanttChart import makePastelColours, makeColourGradient
import Utils
import xml.etree.ElementTree
import xml.etree.cElementTree
import xml.dom
import xml.dom.minidom
from GpxParse import GpxParse
import collections
import zipfile

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

LatLonEle = collections.namedtuple('LatLonEle', ['lat','lon','ele', 't'] )
GpsPoint = collections.namedtuple('GpsPoint', ['lat','lon','ele','x','y','d','dCum'] )

def triangle( t, a ):
	a = float(a)
	return (2 / a) * (t - a * int(t / a + 0.5)) * (-1 ** int(t / a + 0.5))
	
def CompassBearing(lat1, lon1, lat2, lon2):
	"""
	Calculates the bearing between two points.
	"""

	lat1 = math.radians(lat1)
	lat2 = math.radians(lat2)

	diffLong = math.radians(lon2 - lon1)

	x = math.sin(diffLong) * math.cos(lat2)
	y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))

	initial_bearing = math.atan2(x, y)

	# Now we have the initial bearing but math.atan2 return values
	# from -180 to + 180 which is not what we want for a compass bearing
	# The solution is to normalize the initial bearing as shown below
	initial_bearing = math.degrees(initial_bearing)
	compass_bearing = (initial_bearing + 360) % 360

	return compass_bearing
	
reGpxTime = re.compile( '[^0-9+]' )

def GpxHasTimes( fname ):
	''' Check that the gpx file contains valid times. '''
	points = GpxParse( fname )
	tLast = None
	for p in points:
		try:
			t = p['time']
		except KeyError:
			return False
		if tLast is not None and tLast > t:
			return False
		tLast = t
	return True
	
def ParseGpxFile( fname, useTimes = False ):
	points = GpxParse( fname )
	
	latMin, lonMin = 1000.0, 1000.0
	latLonEles = []
	
	hasTimes = True
	for p in points:
		lat, lon, ele, t = p['lat'], p['lon'], p.get('ele',0.0), p.get('time', None)
		
		latMin = min( latMin, lat )
		lonMin = min( lonMin, lon )

		latLonEles.append( LatLonEle(lat, lon, ele, t) )
		if t is None:
			hasTimes = False
		
	gpsPoints = []
	dCum = 0.0
	for i in xrange(len(latLonEles)):
		p, pNext = latLonEles[i], latLonEles[(i+1) % len(latLonEles)]
		if hasTimes and useTimes:
			if pNext.t > p.t:
				gad = (pNext.t - p.t).total_seconds()
			else:
				# Estimate the last time difference based on the speed as the last segment.
				pPrev = latLonEles[(i+len(latLonEles)-1)%len(latLonEles)]
				d = GreatCircleDistance( pPrev.lat, pPrev.lon, p.lat, p.lon )
				t = (p.t - pPrev.t).total_seconds()
				if t > 0:
					s = d / t
					gad = GreatCircleDistance( p.lat, p.lon, pNext.lat, pNext.lon ) / s
				else:
					gad = 0.0
		else:
			gad = GradeAdjustedDistance( p.lat, p.lon, p.ele, pNext.lat, pNext.lon, pNext.ele )
		x = GreatCircleDistance( latMin, lonMin, latMin, p.lon )
		y = GreatCircleDistance( latMin, lonMin, p.lat, lonMin )
		if gad > 0.0:
			gpsPoints.append( GpsPoint(p.lat, p.lon, p.ele, x, y, gad, dCum) )
			dCum += gad
	
	return gpsPoints

def createAppendChild( doc, parent, name ):
	child = doc.createElement( name )
	parent.appendChild( child )
	return child
	
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
		
	def read( self, fname, useTimes = False ):
		self.gpsPoints = ParseGpxFile( fname, useTimes )
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
		
	def isClockwise( self ):
		if not self.gpsPoints:
			return False
		p = self.gpsPoints
		return sum( (p[j].x - p[j-1].x) * (p[j].y + p[j-1].y) for j in xrange(len(self.gpsPoints)) ) > 0.0
		
	def reverse( self ):
		''' Reverse the points in the track.  Make sure the distance to the next point and cumDistance is correct. '''
		self.cumDistance = []
		gpsPointsReversed = []
		dCum = 0.0
		for i in xrange(len(self.gpsPoints)-1, -1, -1):
			p = self.gpsPoints[i]
			pPrev = self.gpsPoints[i-1 if i > 0 else len(self.gpsPoints)-1]
			gpsPointsReversed.append( GpsPoint(p.lat, p.lon, p.ele, p.x, p.y, pPrev.d, dCum) )
			self.cumDistance.append( dCum )
			dCum += pPrev.d
		self.gpsPoints = gpsPointsReversed
	
	def setClockwise( self, clockwise = True ):
		if self.isClockwise() != clockwise:
			self.reverse()
	
	def asCoordinates( self ):
		coordinates = []
		for p in self.gpsPoints:
			coordinates.append( p.lon )
			coordinates.append( p.lat )
		return coordinates
		
	def asKmlTour( self, raceName = None, speedKMH = None, dateTime = None ):
		race = raceName if raceName is not None else 'Race'
		speed = (speedKMH if speedKMH is not None else 35.0) * (1000.0 / (60.0*60.0))
		if dateTime is None:
			dt = datetime.datetime.now().replace( hour = 11, minute = 0, second = 0 )
			dateTimeStr = dt.strftime( '%Y-%m-%dT%H:%M:%S%z' )
		else:
			dateTimeStr = dateTime.strftime( '%Y-%m-%dT%H:%M:%S%z' )

		doc = xml.dom.minidom.Document()
		kml = createAppendChild( doc, doc, 'kml' )
		kml.attributes['xmlns'] ="http://www.opengis.net/kml/2.2"
		kml.attributes['xmlns:gx'] = "http://www.google.com/kml/ext/2.2"
		
		kml.appendChild( doc.createComment( '\n'.join( [
			'',
			'DO NOT EDIT!',
			'',
			'This file was created automatically by CrossMgr.',
			'',
			'Is shows a fly-through of an actual bicycle race course.',
			'For more information, see http://sites.google.com/site/crossmgrsoftware',
			'',
			'Created:  %s' % datetime.datetime.now().strftime( '%Y/%m/%d %H:%M:%S' ),
			'User:     %s' % cgi.escape(getpass.getuser()),
			'Computer: %s' % cgi.escape(socket.gethostname()),
			'', ] )
		) )
		
		Document = createAppendChild( doc, kml, 'Document' )
		
		name = createAppendChild( doc, Document, 'name' )
		name.appendChild( doc.createTextNode(raceName) )
		
		# Define some styles.
		'''
		Style = createAppendChild( doc, Document, 'Style' )
		Style.attributes['id'] = 'thickBlueLine'
		LineStyle = createAppendChild( doc, Style, 'LineStyle' )
		#createAppendChild( doc, LineStyle, 'width' ).appendChild( doc.createTextNode('5') )
		createAppendChild( doc, LineStyle, 'color' ).appendChild( doc.createTextNode('#000000ffff') )
		PolyStyle = createAppendChild( doc, Style, 'PolyStyle' )
		createAppendChild( doc, PolyStyle, 'color' ).appendChild( doc.createTextNode('#000000ffff') )
		'''
		
		# Define an flying tour around the course.
		Tour = createAppendChild( doc, Document, 'gx:Tour' )
		createAppendChild( doc, Tour, 'name' ).appendChild( doc.createTextNode('%s: Virtual Tour' % race) )
		
		Playlist = createAppendChild( doc, Tour, 'gx:Playlist' )

		for i, p in enumerate(self.gpsPoints):
			pNext = self.gpsPoints[ (i + 1) % len(self.gpsPoints) ]
			
			FlyTo = createAppendChild( doc, Playlist, 'gx:FlyTo' )
			duration = createAppendChild( doc, FlyTo, 'gx:duration' )
			
			if i == 0:
				duration.appendChild( doc.createTextNode('3.0') )
				createAppendChild( doc, FlyTo, 'gx:flyToMode' ).appendChild( doc.createTextNode('bounce') )
			else:
				distance = GreatCircleDistance( p.lat, p.lon, pNext.lat, pNext.lon )
				duration.appendChild( doc.createTextNode(str(distance / speed)) )
				createAppendChild( doc, FlyTo, 'gx:flyToMode' ).appendChild( doc.createTextNode('smooth') )
				
			Camera = createAppendChild( doc, FlyTo, 'Camera' )
			heading = CompassBearing( p.lat, p.lon, pNext.lat, pNext.lon )
			
			createAppendChild( doc, Camera, 'latitude' ).appendChild( doc.createTextNode(str(p.lat)) )
			createAppendChild( doc, Camera, 'longitude' ).appendChild( doc.createTextNode(str(p.lon)) )
			createAppendChild( doc, Camera, 'altitude' ).appendChild( doc.createTextNode(str(2.0)) )
			createAppendChild( doc, Camera, 'altitudeMode' ).appendChild( doc.createTextNode('relativeToGround') )
			createAppendChild( doc, Camera, 'heading' ).appendChild( doc.createTextNode(str(heading)) )
			createAppendChild( doc, Camera, 'tilt' ).appendChild( doc.createTextNode(str(80.0)) )
			
		# Define a marker for the finish line.
		Placemark = createAppendChild( doc, Document, 'Placemark' )
		createAppendChild( doc, Placemark, 'name' ).appendChild( doc.createTextNode('%s: Finish Line' % race) )
		Point = createAppendChild( doc, Placemark, 'Point' )
		coordinates = createAppendChild( doc, Point, 'coordinates' )
		coordinates.appendChild( doc.createTextNode('%f,%f' % (self.gpsPoints[0].lon, self.gpsPoints[0].lat)) )
		
		# Define a closed path for the course.
		Placemark = createAppendChild( doc, Document, 'Placemark' )
		createAppendChild( doc, Placemark, 'name' ).appendChild( doc.createTextNode('%s: Course' % race) )
		# createAppendChild( doc, Placemark, 'styleUrl' ).appendChild( doc.createTextNode('#thickBlueLine') )
		LineString = createAppendChild( doc, Placemark, 'LineString' )
		createAppendChild( doc, LineString, 'tessellate' ).appendChild( doc.createTextNode('1') )
		createAppendChild( doc, LineString, 'altitudeMode' ).appendChild( doc.createTextNode('relativeToGround') )
		coordinates = createAppendChild( doc, LineString, 'coordinates' )
		coords = []
		for i in xrange(len(self.gpsPoints)+1):
			p = self.gpsPoints[i % len(self.gpsPoints)]
			coords.append( '%f,%f,%f' % (p.lon, p.lat, 1.0) )
		coordinates.appendChild( doc.createTextNode('\n'.join(coords)) )
		
		ret = doc.toprettyxml( indent = '  ' )
		text_re = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)    
		ret = text_re.sub('>\g<1></', ret)
		doc.unlink()
		return ret
		
	def getXY( self, lap, id = None ):
		# Find the segment at this distance in the lap.
		lap = math.modf(lap)[0]								# Get fraction of lap.
		lapDistance = lap * self.distanceTotal				# Get distance traveled in the lap.
		
		# Avoid the cost of the binary search by checking if the id request is still on the last segment.
		lenGpsPoints = len(self.gpsPoints)
		try:
			i = self.cache[id]
			pCur = self.gpsPoints[i]
			if not (pCur.dCum <= lapDistance <= pCur.dCum + pCur.d):
				i = (i + 1) % lenGpsPoints
				pCur = self.gpsPoints[i]
				if not (pCur.dCum <= lapDistance <= pCur.dCum + pCur.d):
					i = None
		except (IndexError, KeyError):
			i = None
			
		if i is None:
			# Find the closest point LT the lap distance.
			i = bisect.bisect_right( self.cumDistance, lapDistance )
			i %= lenGpsPoints
			if self.cumDistance[i] > lapDistance:
				i -= 1
		
		self.cache[id] = i
		pCur, pNext = self.gpsPoints[i], self.gpsPoints[(i + 1) % lenGpsPoints]
		
		segDistance = lapDistance - self.cumDistance[i]
		segRatio = 0.0 if pCur.d <= 0.0 else segDistance / pCur.d
		
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
	infoLines = 1

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
		
		self.xBanner = 300
		self.tBannerLast = None
		
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
			self.timer.Stop()
		self.tBannerLast = None
	
	def SetNumsToWatch( self, numsToWatch ):
		self.numsToWatch = numsToWatch
		self.Refresh()
	
	def SuspendAnimate( self ):
		self.suspendGeoAnimation = True
	
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
			if info['status'] == 'Finisher' and info['raceTimes']:
				info['finishTime'] = info['raceTimes'][-1]
			else:
				info['finishTime'] = info['lastTime']
		if tCur is not None:
			self.t = tCur;
		self.tBannerLast = None
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
	
	def getRiderXYPT( self, num ):
		positionTime = self.getRiderPositionTime( num )
		if positionTime[0] is None:
			return None, None, None, None
		if self.data[num]['finishTime'] is not None and self.t >= self.data[num]['finishTime']:
			self.lapCur = max(self.lapCur, len(self.data[num]['raceTimes']))
			return (None, None, positionTime[0], positionTime[1])
		self.lapCur = max(self.lapCur, int(positionTime[0]))
		xy = self.geoTrack.getXY( positionTime[0], num )
		return xy[0], xy[1], positionTime[0], positionTime[1]
	
	def drawBanner( self, dc, width, height, tHeight, bannerItems ):
		blue = wx.Colour(0, 0, 200)
		dc.SetPen( wx.Pen(blue) )
		dc.SetBrush( wx.Brush(blue, wx.SOLID) )
		dc.DrawRectangle( 0, 0, width, tHeight*1.1 )
		if not bannerItems:
			return
		
		y = tHeight * 0.1
		tHeight *= 0.85
		x = self.xBanner
		while x < width:
			for bi in bannerItems:
				if x >= width:
					break
					
				position, num, name = str(bi[1]), str(bi[0]), self.getShortName(bi[0])
				
				if position == '1':
					x += tHeight / 2
					tWidth = self.checkeredFlag.Width
					if x + tWidth > 0 and x < width:
						dc.DrawBitmap( self.checkeredFlag, x, y, False )
					x += tWidth + tHeight / 2
				
				dc.SetFont( self.positionFont )
				tWidth = dc.GetTextExtent( position )[0]
				if x + tWidth > 0 and x < width:
					dc.SetTextForeground( wx.WHITE )
					dc.DrawText( position, x, y )
				x += tWidth + tHeight / 4

				dc.SetFont( self.bibFont )
				tWidth = dc.GetTextExtent(num)[0]
				if x + tWidth > 0 and x < width:
					dc.SetTextForeground( 'YELLOW' )
					dc.DrawText(num, x, y )
				x += tWidth + tHeight / 3
				
				dc.SetFont( self.nameFont )
				tWidth = dc.GetTextExtent(name)[0]
				if x + tWidth > 0 and x < width:
					dc.SetTextForeground( wx.WHITE )
					dc.DrawText(name, x, y )
				x += tWidth + tHeight
			if x < 0:
				self.xBanner = x
		
		tBanner = datetime.datetime.now()
		if self.tBannerLast is None:
			self.tBannerLast = tBanner
		self.xBanner -= 64.0 * (tBanner - self.tBannerLast).total_seconds()
		self.tBannerLast = tBanner
	
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
			
			self.positionFont = wx.FontFromPixelSize( wx.Size(0,tHeight*0.85*0.7), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )
			self.bibFont = wx.FontFromPixelSize( wx.Size(0,tHeight*0.85), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD )
			self.nameFont = wx.FontFromPixelSize( wx.Size(0,tHeight*0.85), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD )
			
			self.rLast = r
			
		tHeight = int(r / 8.0)
		textVSpace = tHeight*0.2
		laneWidth = (r/2) / self.laneMax
		
		border = laneWidth * 1.5 / 2
		trackWidth = width - border * 2
		topMargin = border + tHeight + textVSpace
		trackHeight = height - topMargin - border
		self.geoTrack.setDisplayRect( border, topMargin, trackWidth, trackHeight )
		
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
		riderRadius = laneWidth * 0.5
		thickLine = r / 32
		highlightPen = wx.Pen( wx.WHITE, thickLine * 1.0 )
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
					if not self.numsToWatch or num in self.numsToWatch:
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
		tStr = ''
		dc.SetFont( self.timeFont )
		if self.lapCur:
			if leaders:
				maxLaps = len(self.data[leaders[0]]['raceTimes'])
			else:
				maxLaps = 9999
			if self.lapCur > maxLaps:
				self.lapCur = maxLaps
			tStr = 'Laps Completed %d   ' % max(0, self.lapCur-1)

		# Draw the race time
		secs = int( self.t )
		if secs < 60*60:
			tStr += '%d:%02d ' % ((secs / 60)%60, secs % 60 )
		else:
			tStr += '%d:%02d:%02d ' % (secs / (60*60), (secs / 60)%60, secs % 60 )
		tWidth = dc.GetTextExtent( tStr )[0]
		dc.DrawText( tStr, width - tWidth, tHeight+textVSpace*1.6 )
			
		# Draw the leader board.
		bannerItems = []
		for i, leader in enumerate(leaders):
			bannerItems.append( (leaders[i], i+1) )
		if self.numsToWatch:
			rp = []
			for n in self.numsToWatch:
				try:
					p = riderPosition[n]
					rp.append( (p, n) )
				except KeyError:
					pass
			rp.sort()
			for w in rp:
				bannerItems.append( (w[1], w[0]) )
		self.drawBanner( dc, width, height, tHeight, bannerItems )
		
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	print GpxHasTimes( 'ParkAvenue/ParkAveOneLap.gpx' )
	
	data = {}
	for num in xrange(100,200):
		mean = random.normalvariate(6.0, 0.3)
		raceTimes = [0]
		for lap in xrange( 4 ):
			raceTimes.append( raceTimes[-1] + random.normalvariate(mean, mean/20)*60.0 )
		data[num] = { 'raceTimes': raceTimes, 'lastTime': raceTimes[-1], 'flr': 1.0, 'status':'Finisher' }

	# import json
	# with open('race.json', 'w') as fp: fp.write( json.dumps(data, sort_keys=True, indent=4) )

	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="GeoAnimation", size=(800,700))
	animation = GeoAnimation(mainWin)
	geoTrack = GeoTrack()
	#geoTrack.read( 'EdgeField_Cyclocross_Course.gpx' )
	#geoTrack.read( 'St._John__039_s_Cyclocross_course_v2.gpx' )
	geoTrack.read( 'Camp Arrowhead mtb GPS course.gpx' )
	#geoTrack.read( 'Races/Midweek/Midweek_Learn_to_Race_and_Elite_Series_course.gpx' )
	#geoTrack.reverse()
	print 'Clockwise:', geoTrack.isClockwise()
	
	zf = zipfile.ZipFile( 'track.kmz', 'w', zipfile.ZIP_DEFLATED )
	zf.writestr( 'track.kml', geoTrack.asKmlTour('Race Track') )
	zf.close()
	
	with open('track.kml', 'w') as f:
		f.write( geoTrack.asKmlTour('Race Track') )
		
	#sys.exit()
		
	animation.SetGeoTrack( geoTrack )
	animation.SetData( data )
	animation.Animate( 2*60, 60*60 )
	mainWin.Show()
	app.MainLoop()
