import wx
import random
import math
from math import radians, degrees, sin, cos, asin, sqrt, atan2, exp, modf, pi
import bisect
import sys
import six
import datetime
import os
import re
import io
import cgi
import getpass
import socket
from Version import AppVerName
from Animation import GetLapRatio
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
	scale = (normLen / 2.0) / sqrt( dx**2 + dy**2 )
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

	lat1 = radians(lat1)
	lat2 = radians(lat2)

	diffLong = math.radians(lon2 - lon1)

	x = sin(diffLong) * cos(lat2)
	y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(diffLong))

	initial_bearing = atan2(x, y)

	# Now we have the initial bearing but math.atan2 return values
	# from -180 to + 180 which is not what we want for a compass bearing
	# The solution is to normalize the initial bearing as shown below
	initial_bearing = degrees(initial_bearing)
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

def LatLonElesToGpsPoints( latLonEles, useTimes = False, isPointToPoint = False ):
	hasTimes = useTimes
	latMin, lonMin = 1000.0, 1000.0
	for latLonEle in latLonEles:
		if latLonEle.t is None:
			hasTimes = False
		if latLonEle.lat < latMin:
			latMin = latLonEle.lat
		if latLonEle.lon < lonMin:
			lonMin = latLonEle.lon

	gpsPoints = []
	dCum = 0.0
	for i in six.moves.range(len(latLonEles) - (1 if isPointToPoint else 0)):
		p, pNext = latLonEles[i], latLonEles[(i+1) % len(latLonEles)]
		if hasTimes:
			if pNext.t > p.t:
				gad = (pNext.t - p.t).total_seconds()
			else:
				# Estimate the last time difference based on the speed of the last segment.
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
	
def ParseGpxFile( fname, useTimes = False, isPointToPoint = False ):
	points = GpxParse( fname )
	
	latLonEles = []
	
	for p in points:
		lat, lon, ele, t = p['lat'], p['lon'], p.get('ele',0.0), p.get('time', None)
		
		# Skip consecutive duplicate points.
		try:
			if latLonEles[-1].lat == lat and latLonEles[-1].lon == lon:
				continue
		except IndexError:
			pass
		
		latLonEles.append( LatLonEle(lat, lon, ele, t) )
	
	return latLonEles

def createAppendChild( doc, parent, name, textAttr={} ):
	child = doc.createElement( name )
	parent.appendChild( child )
	for k, v in six.iteritems(textAttr):
		attr = doc.createElement( k )
		if isinstance(v, float) and modf(v)[0] == 0.0:
			v = int(v)
		attr.appendChild( doc.createTextNode( '{:.6f}'.format(v) if isinstance(v, float) else '{}'.format(v) ) )
		child.appendChild( attr )
	return child
	
def createAppendTextChild( doc, parent, text ):
	child = doc.createTextNode( text )
	parent.appendChild( child )
	return child

def CreateGPX( courseName, gpsPoints ):
	''' Create a GPX file from the gpsPoints list. '''

	doc = xml.dom.minidom.Document()
	gpx = createAppendChild( doc, doc, 'gpx' )
	gpx.attributes['creator'] = AppVerName + ' http://sites.google.com/site/crossmgrsoftware/'
	gpx.attributes['xmlns'] ="http://www.topografix.com/GPX/1/0"
	gpx.attributes['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
	gpx.attributes['xsi:schemaLocation'] = "http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd"
	
	gpx.appendChild( doc.createComment( u'\n'.join( [
		'',
		'DO NOT EDIT!',
		'',
		u'This file was created automatically by {}.'.format(AppVerName),
		'',
		'For more information, see http://sites.google.com/site/crossmgrsoftware',
		'',
		'Created:  {}'.format(datetime.datetime.now().strftime( '%Y-%m-%d %H:%M:%S' )),
		'User:     {}'.format(cgi.escape(getpass.getuser())),
		'Computer: {}'.format(cgi.escape(socket.gethostname())),
		'', ] )
	) )
	
	trk = createAppendChild( doc, gpx, 'trk', {
		'name': courseName,
	} )
	trkseg = createAppendChild( doc, trk, 'trkseg' )
	for p in gpsPoints:
		trkpt = createAppendChild( doc, trkseg, 'trkpt' )
		trkpt.attributes['lat'] = '{}'.format(p.lat)
		trkpt.attributes['lon'] = '{}'.format(p.lon)
		if p.ele:
			ele = createAppendChild( doc, trkpt, 'ele' )
			createAppendTextChild( doc, ele, '{}'.format(p.ele) )
	
	return doc
	
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
		self.totalElevationGain = 0.0
		self.isPointToPoint = False
		self.cache = {}
		
	def computeSummary( self ):
		lenGpsPoints = len(self.gpsPoints)
		length = 0.0
		totalElevationGain = 0.0
		self.isPointToPoint = getattr( self, 'isPointToPoint', False )
		for i in six.moves.range(lenGpsPoints - (1 if self.isPointToPoint else 0)):
			pCur, pNext = self.gpsPoints[i], self.gpsPoints[(i + 1) % lenGpsPoints]
			length += GreatCircleDistance3D( pCur.lat, pCur.lon, pCur.ele, pNext.lat, pNext.lon, pNext.ele )
			totalElevationGain += max(0.0, pNext.ele - pCur.ele)
		self.length = length
		self.totalElevationGain = totalElevationGain
	
	def setPoints( self, gpsPoints, isPointToPoint = False ):
		self.gpsPoints = gpsPoints
		self.isPointToPoint = isPointToPoint

		self.xMax = max( p.x for p in self.gpsPoints )
		self.yMax = max( p.y for p in self.gpsPoints )
		dCum = 0.0
		self.cumDistance = []
		for p in self.gpsPoints:
			self.cumDistance.append( dCum )
			dCum += p.d
		self.distanceTotal = dCum
		self.computeSummary()
	
	def read( self, fname, useTimes = False, isPointToPoint = False ):
		self.isPointToPoint = isPointToPoint
		latLonEles = ParseGpxFile( fname, useTimes=useTimes, isPointToPoint=isPointToPoint )
		gpsPoints = LatLonElesToGpsPoints( latLonEles, useTimes=useTimes, isPointToPoint=isPointToPoint )
		self.setPoints( gpsPoints, isPointToPoint=isPointToPoint )
		
	def getGPX( self, courseName ):
		return CreateGPX( courseName, self.gpsPoints )
	
	def writeGPXFile( self, fname ):
		with io.open( fname, 'w') as fp:
			self.getGPX( os.path.splitext(os.path.basename(fname))[0] ).writexml(fp, indent="", addindent=" ", newl="\n", encoding='utf-8')
	
	def readElevation( self, fname ):
		header = None
		distance, elevation = [], []
		iDistance, iElevation =  None, None
		with io.open(fname, 'r') as fp:
			for line in fp:
				fields = [f.strip() for f in line.split(',')]
				if not header:
					header = fields
					for i, h in enumerate(header):
						h = h.lower()
						if h.startswith('distance'):
							iDistance = i
						elif h.startswith('elevation'):
							iElevation = i
					assert iDistance is not None and iElevation is not None, 'Invalid header in file.'
				else:
					distance.append( float(fields[iDistance]) )
					elevation.append( float(fields[iElevation]) )
		if len(elevation) < 2:
			return
			
		lenGpsPoints = len(self.gpsPoints)
		length = 0.0
		for i in six.moves.range(lenGpsPoints-1):
			pCur, pNext = self.gpsPoints[i], self.gpsPoints[(i + 1) % lenGpsPoints]
			length += GreatCircleDistance( pCur.lat, pCur.lon, pNext.lat, pNext.lon )
			
		distanceMult = distance[-1] / length
		
		# Update the known GPS points with the proportional elevation.
		length = 0.0
		iSearch = 0
		for i in six.moves.range(lenGpsPoints):
			pCur, pNext = self.gpsPoints[i], self.gpsPoints[(i + 1) % lenGpsPoints]
			
			d = min( length * distanceMult, distance[-1] )
			for iSearch in six.moves.range(iSearch, len(elevation) - 2):
				if distance[iSearch] <= d < distance[iSearch+1]:
					break
			deltaDistance = max( distance[iSearch+1] - distance[iSearch], 0.000001 )
			ele = elevation[iSearch] + (elevation[iSearch+1] - elevation[iSearch]) * \
						(d - distance[iSearch]) / deltaDistance
			self.gpsPoints[i] = pCur._replace( ele = ele )
			length += GreatCircleDistance( pCur.lat, pCur.lon, pNext.lat, pNext.lon )
			
		self.computeSummary()
	
	def getXYTrack( self ):
		x, yBottom, mult = self.x, self.yBottom, self.mult
		return [(p.x * mult + x, yBottom - p.y * mult) for p in self.gpsPoints]

	def asExportJson( self ):
		return [ [int(getattr(p, a)*10.0) for a in ('x', 'y', 'd')] for p in self.gpsPoints ]
		
	def getAltigraph( self ):
		if not self.gpsPoints or all( p.ele == 0.0 for p in self.gpsPoints ):
			return []
		altigraph = [(0.0, self.gpsPoints[0].ele)]
		p = self.gpsPoints
		for i in six.moves.range(1, len(p)):
			altigraph.append( (altigraph[-1][0] + GreatCircleDistance(p[i-1].lat, p[i-1].lon, p[i].lat, p[i].lon), p[i].ele) )
		altigraph.append( (altigraph[-1][0] + GreatCircleDistance(p[-1].lat, p[-1].lon, p[0].lat, p[0].lon), p[0].ele) )
		return altigraph
		
	def isClockwise( self ):
		if not self.gpsPoints:
			return False
		p = self.gpsPoints
		return sum( (p[j].x - p[j-1].x) * (p[j].y + p[j-1].y) for j in six.moves.range(len(self.gpsPoints)) ) > 0.0
		
	def reverse( self ):
		''' Reverse the points in the track.  Make sure the distance to the next point and cumDistance is correct. '''
		self.cumDistance = []
		gpsPointsReversed = []
		dCum = 0.0
		for i in six.moves.range(len(self.gpsPoints)-1, -1, -1):
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
		
	def asKmlTour( self, raceName=None, speedKMH=None ):
		race = raceName or 'Race'
		speed = (speedKMH or 35.0) * (1000.0 / (60.0*60.0))

		doc = xml.dom.minidom.Document()
		kml = createAppendChild( doc, doc, 'kml' )
		kml.attributes['xmlns'] = "http://www.opengis.net/kml/2.2"
		kml.attributes['xmlns:gx'] = "http://www.google.com/kml/ext/2.2"
		
		kml.appendChild( doc.createComment( '\n'.join( [
			'',
			'DO NOT EDIT!',
			'',
			'This file was created automatically by CrossMgr.',
			'',
			'Is shows a fly-through of the actual bicycle race course.',
			'For more information, see http://sites.google.com/site/crossmgrsoftware',
			'',
			'Created:  {}'.format(datetime.datetime.now().strftime( '%Y/%m/%d %H:%M:%S' )),
			'User:     {}'.format(cgi.escape(getpass.getuser())),
			'Computer: {}'.format(cgi.escape(socket.gethostname())),
			'', ] )
		) )
		
		Document = createAppendChild( doc, kml, 'Document', {
			'open': 1,
			'name': raceName,
		} )
		
		# Define some styles.
		Style = createAppendChild( doc, Document, 'Style' )
		Style.attributes['id'] = 'thickBlueLine'
		LineStyle = createAppendChild( doc, Style, 'LineStyle', {
			'width': 5,
			'color': '#7fff0000',	# aabbggrr
		} )
		
		# Define an flying tour around the course.
		Tour = createAppendChild( doc, Document, 'gx:Tour', {
			'name': '{}: Tour'.format(race),
		} )
		
		Playlist = createAppendChild( doc, Tour, 'gx:Playlist' )

		def fly( doc, PlayList, p, mode, duration, heading ):
			FlyTo = createAppendChild( doc, Playlist, 'gx:FlyTo', {
				'gx:duration': duration,
				'gx:flyToMode': mode,
			} )	
			Camera = createAppendChild( doc, FlyTo, 'Camera', {
				'latitude': p.lat,
				'longitude': p.lon,
				'altitude': 2,
				'altitudeMode': 'relativeToGround',
				'heading': heading,
				'tilt': 80,
			} )
			
		# Fly to the starting point.
		p, pNext = self.gpsPoints[:2]
		fly( doc, Playlist, p, 'bounce', 3, CompassBearing(p.lat, p.lon, pNext.lat, pNext.lon) )
		
		# Follow the path through all the points.
		lenGpsPoints = len(self.gpsPoints)
		for i in six.moves.range(1, lenGpsPoints + (0 if self.isPointToPoint else 1)):
			pPrev, p = self.gpsPoints[i-1], self.gpsPoints[i%lenGpsPoints]			
			fly(doc, Playlist, p, 'smooth',
				GreatCircleDistance(pPrev.lat, pPrev.lon, p.lat, p.lon) / speed,
				CompassBearing(pPrev.lat, pPrev.lon, p.lat, p.lon)
			)
		
		if self.isPointToPoint:
			# Marker for the start line.
			Placemark = createAppendChild( doc, Document, 'Placemark', {'name': '{}: Start Line'.format(race)} )
			createAppendChild( doc, Placemark, 'Point', {
				'coordinates': '{},{}'.format(self.gpsPoints[0].lon, self.gpsPoints[0].lat)
			} )
			pFinish = self.gpsPoints[-1]
		else:
			pFinish = self.gpsPoints[0]
		
		# Marker for the finish line.
		Placemark = createAppendChild( doc, Document, 'Placemark', {'name': '{}: Finish Line'.format(race)} )
		createAppendChild( doc, Placemark, 'Point', {'coordinates': '{},{}'.format(pFinish.lon, pFinish.lat)} )
		
		# Path for the course.
		Placemark = createAppendChild( doc, Document, 'Placemark', {
			'name': '{}: Course'.format(race),
			'styleUrl': '#thickBlueLine',
		} )
		coords = ['']
		for i in six.moves.range(lenGpsPoints + (0 if self.isPointToPoint else 1)):
			p = self.gpsPoints[i % lenGpsPoints]
			coords.append( '{},{}'.format(p.lon, p.lat) )
		coords.append('')
		LineString = createAppendChild( doc, Placemark, 'LineString', {
			'tessellate': 1,
			'altitudeMode': 'clampToGround',
			'coordinates': '\n'.join(coords),
		} )
		
		ret = doc.toprettyxml( indent=' ' )
		doc.unlink()
		return ret
		
	def getXY( self, lap, id = None ):
		# Find the segment at this distance in the lap.
		lap = modf(lap)[0]								# Get fraction of lap.
		lapDistance = lap * self.distanceTotal			# Get distance traveled in the lap.
		
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
	def totalElevationGainM( self ):
		try:
			return self.totalElevationGain
		except AttributeError:
			self.totalElevationGain = sum( max(0.0, self.gpsPoints[i].ele - self.gpsPoints[i-1].ele) for i in six.moves.range(len(self.gpsPoints)) )
			return self.totalElevationGain
		
	@property
	def totalElevationGainFt( self ):
		return self.totalElevationGainM * 3.28084
		
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
		
shapes = [ [(cos(a), -sin(a)) \
					for a in (q*(2.0*pi/i)+pi/2.0+(2.0*pi/(i*2.0) if i % 2 == 0 else 0)\
						for q in six.moves.range(i))] for i in six.moves.range(3,9)]
def DrawShape( dc, num, x, y, radius ):
	dc.DrawPolygon( [ wx.Point(p*radius+x, q*radius+y) for p,q in shapes[num % len(shapes)] ] )
	
class GeoAnimation(wx.Control):
	topFewCount = 5
	infoLines = 1

	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="GeoAnimation"):
		wx.Control.__init__(self, parent, id, pos, size, style, validator, name)
		self.SetBackgroundColour('white')
		self.data = {}
		self.categoryDetails = {}
		self.t = 0
		self.tMax = None
		self.tDelta = 1
		self.r = 100	# Radius of the turns of the fictional track.
		self.laneMax = 8
		
		self.geoTrack = None
		self.compassLocation = ''
		self.widthLast = -1
		self.heightLast = -1
		
		self.xBanner = 300
		self.tBannerLast = None
		
		self.course = 'geo'
		self.units = 'km'
		
		self.framesPerSecond = 32
		self.lapCur = 0
		self.iLapDistance = 0
		
		self.tLast = datetime.datetime.now()
		self.speedup = 1.0
		
		self.suspendGeoAnimation = False
		self.numsToWatch = set()
		
		self.checkeredFlag = wx.Bitmap(os.path.join(Utils.getImageFolder(), 'CheckeredFlag.png'), wx.BITMAP_TYPE_PNG)	
		
		trackRGB = [int('7FE57F'[i:i+2],16) for i in six.moves.range(0, 6, 2)]
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
		self.trackColour = wx.Colour( *[int('7FE57F'[i:i+2],16) for i in six.moves.range(0, 6, 2)] )
		
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
		
	def SetGeoTrack( self, geoTrack ):
		if self.geoTrack != geoTrack:
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
			for num, info in six.iteritems(self.data):
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
		for num, info in six.iteritems(self.data):
			info['iLast'] = 1
			if info['status'] == 'Finisher' and info['raceTimes']:
				info['finishTime'] = info['raceTimes'][-1]
			else:
				info['finishTime'] = info['lastTime']
				
		# Get the units.
		for num, info in six.iteritems(self.data):
			if info['status'] == 'Finisher':
				try:
					self.units = 'miles' if 'mph' in info['speed'] else 'km'
				except KeyError:
					self.units = 'km'
				break
				
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
					
				position, num, name = u'{}'.format(bi[1]), u'{}'.format(bi[0]), self.getShortName(bi[0])
				
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
			
		avePoints = 1
		isPointToPoint = getattr(self.geoTrack, 'isPointToPoint', False)
		
		self.r = int(width / 4)
		if self.r * 2 > height:
			self.r = int(height / 2)
		self.r -= (self.r & 1)			# Make sure that r is an even number.
		
		r = self.r
		
		# Get the fonts if needed.
		if self.rLast != r:
			tHeight = int(r / 8.0)
			self.numberFont	= wx.Font( (0,tHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
			self.timeFont = self.numberFont
			self.highlightFont = wx.Font( (0,tHeight * 1.6), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
			
			self.positionFont = wx.Font( (0,tHeight*0.85*0.7), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
			self.bibFont = wx.Font( (0,tHeight*0.85), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD )
			self.nameFont = wx.Font((0,tHeight*0.85), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD )
			
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
		if width != self.widthLast or height != self.heightLast:
			self.widthLast, self.heightLast = width, height
			locations = ['NE', 'SE', 'NW', 'SW', ]
			compassWidth, compassHeight = width * 0.25, height * 0.25
			inCountBest = len(drawPoints) + 1
			self.compassLocation = locations[0]
			for loc in locations:
				xCompass = 0 if 'W' in loc else width - compassWidth
				yCompass = 0 if 'S' in loc else height - compassHeight
				inCount = sum( 1 for x, y in drawPoints
								if	xCompass <= x < xCompass + compassWidth and
									yCompass <= y < yCompass + compassHeight )
				if inCount < inCountBest:
					inCountBest = inCount
					self.compassLocation = loc
					if inCount == 0:
						break
		
		dc.SetPen( wx.Pen(wx.Colour(128,128,128), laneWidth * 1.25 + 2, wx.SOLID) )
		if isPointToPoint:
			dc.DrawLines( drawPoints )
		else:
			dc.DrawPolygon( drawPoints )
		
		dc.SetPen( wx.Pen(self.trackColour, laneWidth * 1.25, wx.SOLID) )
		if isPointToPoint:
			dc.DrawLines( drawPoints )
		else:
			dc.DrawPolygon( drawPoints )
		
		# Draw a centerline to show all the curves in the course.
		dc.SetPen( wx.Pen(wx.Colour(80,80,80), 1, wx.SOLID) )
		if isPointToPoint:
			dc.DrawLines( drawPoints )
		else:
			dc.DrawPolygon( drawPoints )
		
		# Draw a finish line.
		finishLineLength = laneWidth * 2
		if isPointToPoint:
			x1, y1, x2, y2 = LineNormal( drawPoints[-1][0], drawPoints[-1][1], drawPoints[-2][0], drawPoints[-2][1], laneWidth * 2 )
		else:
			x1, y1, x2, y2 = LineNormal( drawPoints[0][0], drawPoints[0][1], drawPoints[1][0], drawPoints[1][1], laneWidth * 2 )
		dc.SetPen( wx.Pen(wx.WHITE, laneWidth / 1.5, wx.SOLID) )
		dc.DrawLine( x1, y1, x2, y2 )
		dc.SetPen( wx.Pen(wx.BLACK, laneWidth / 5, wx.SOLID) )
		dc.DrawLine( x1, y1, x2, y2 )
		if isPointToPoint:
			x1, y1, x2, y2 = LineNormal( drawPoints[-1][0], drawPoints[-1][1], drawPoints[-2][0], drawPoints[-2][1], laneWidth * 4 )
		else:
			x1, y1, x2, y2 = LineNormal( drawPoints[0][0], drawPoints[0][1], drawPoints[1][0], drawPoints[1][1], laneWidth * 4 )
		dc.DrawBitmap( self.checkeredFlag, x2 - self.checkeredFlag.Width/2, y2 - self.checkeredFlag.Height/2, False )

		# Draw starting arrow showing direction.
		if not self.data and not isPointToPoint and len(drawPoints) > avePoints:
			x1, y1 = drawPoints[0][0], drawPoints[0][1]
			x2, y2 = drawPoints[1][0], drawPoints[1][1]
			a = atan2( y2-y1, x2-x1 )
			x2 = int(x1 + cos(a) * laneWidth*4)
			y2 = int(y1 + sin(a) * laneWidth*4)
			dc.SetPen( wx.Pen(wx.BLACK, laneWidth / 4, wx.SOLID) )
			dc.DrawLine( x1, y1, x2, y2 )
			a = atan2( y1-y2, x1-x2 )
			x1, y1 = x2, y2
			arrowLength = 1.25
			arrowAngle = 3.14159/8.0
			x2 = int(x1 + cos(a+arrowAngle) * laneWidth*arrowLength)
			y2 = int(y1 + sin(a+arrowAngle) * laneWidth*arrowLength)
			dc.DrawLine( x1, y1, x2, y2 )
			x2 = int(x1 + cos(a-arrowAngle) * laneWidth*arrowLength)
			y2 = int(y1 + sin(a-arrowAngle) * laneWidth*arrowLength)
			dc.DrawLine( x1, y1, x2, y2 )
			
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
			for num, d in six.iteritems(self.data):
				xypt = list(self.getRiderXYPT(num))
				xypt.insert( 0, num )
				riderXYPT.append( xypt )
			
			# Sort by reverse greatest distance, then by shortest time.
			# Do this so the leaders are drawn last.
			riderXYPT.sort( key=lambda x : ( x[3] if x[3] is not None else 0.0,
											-x[4] if x[4] is not None else 0.0) )
			
			topFew = {}
			for j, i in enumerate(six.moves.range(len(riderXYPT) - 1, max(-1,len(riderXYPT)-self.topFewCount-1), -1)):
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
						dc.DrawLabel('{}'.format(num), wx.Rect(x+numSize, y-numSize, numSize*2, numSize*2) )
				if i is not None:
					dc.SetPen( wx.BLACK_PEN )
					dc.SetFont( self.numberFont )
			
		# Convert topFew from dict to list.
		leaders = [0] * len(topFew)
		for num, position in six.iteritems(topFew):
			leaders[position] = num
		
		yTop = height - self.infoLines * tHeight
		
		tWidth, tHeight = dc.GetTextExtent( '999' )
		yCur = tHeight+textVSpace*1.6
		
		# Draw the race time
		secs = int( self.t )
		if secs < 60*60:
			tStr = '%d:%02d ' % ((secs / 60)%60, secs % 60 )
		else:
			tStr = '%d:%02d:%02d ' % (secs / (60*60), (secs / 60)%60, secs % 60 )
		tWidth = dc.GetTextExtent( tStr )[0]
		dc.DrawText( tStr, width - tWidth, yCur )
		yCur += tHeight
		
		# Draw the current lap
		dc.SetFont( self.timeFont )
		if self.lapCur and leaders:
			leaderRaceTimes = self.data[leaders[0]]['raceTimes']
			if leaderRaceTimes and leaderRaceTimes[0] < leaderRaceTimes[-1]:
				maxLaps = len(leaderRaceTimes) - 1
				self.iLapDistance, lapRatio = GetLapRatio( leaderRaceTimes, self.t, self.iLapDistance )
				lapRatio = int(lapRatio * 10.0) / 10.0		# Always round down, not to nearest decimal.
				text = [u'{:06.1f} {} {} '.format(self.iLapDistance + lapRatio, _('Laps of'), maxLaps),
						u'{:06.1f}  {}'.format(maxLaps - self.iLapDistance - lapRatio, _('Laps to go'))]
						
				cat = self.categoryDetails.get( self.data[leaders[0]].get('raceCat', None) )
				if cat:
					distanceCur, distanceRace = None, None
					
					if cat.get('lapDistance', None) is not None:
						text.append( '' )
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
						text.extend( [	u'{:05.1f} {} {} {:.1f}'.format(distanceCur, self.units, _('of'), distanceRace),
										u'{:05.1f} {} {}'.format(distanceRace - distanceCur, self.units, _('to go'))] )
								
				widthMax = max( dc.GetTextExtent(t)[0] for t in text )
				if 'N' in self.compassLocation:
					yCur = height - tHeight * (len(text) + 1)
				if 'E' in self.compassLocation:
					xCur = width - widthMax
				else:
					xCur = tHeight * 0.5
				for row, t in enumerate(text):
					yCur += tHeight
					if not t:
						continue
					tShow = t.lstrip('0')
					if tShow.startswith('.'):
						tShow = '0' + tShow
					dc.DrawText( tShow, xCur + dc.GetTextExtent('0' * (len(t) - len(tShow)))[0], yCur )
			
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
		if self.data:
			self.drawBanner( dc, width, height, tHeight, bannerItems )
		
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	fname = r'C:\Projects\CrossMgr\bugs\Stuart\20160419-glenlyon\2016-04-19-WTNC Glenlyon 710-r2-Course.gpx'
	six.print_( GpxHasTimes( fname ) )
	
	data = {}
	for num in six.moves.range(100,200):
		mean = random.normalvariate(6.0, 0.3)
		raceTimes = [0]
		for lap in six.moves.range( 4 ):
			raceTimes.append( raceTimes[-1] + random.normalvariate(mean, mean/20)*60.0 )
		data[num] = { 'raceTimes': raceTimes, 'lastTime': raceTimes[-1], 'flr': 1.0, 'status':'Finisher', 'speed':'32.7 km/h' }

	app = wx.App(False)
	mainWin = wx.Frame(None,title="GeoAnimation", size=(800,700))
	animation = GeoAnimation(mainWin)
	geoTrack = GeoTrack()
	geoTrack.read( fname )
	geoTrack.writeGPXFile( 'geotrack.gpx' )
	#sys.exit()
	
	#geoTrack.read( 'St._John__039_s_Cyclocross_course_v2.gpx' )
	#geoTrack.read( 'Camp Arrowhead mtb GPS course.gpx' )
	#geoTrack.read( 'Races/Midweek/Midweek_Learn_to_Race_and_Elite_Series_course.gpx' )
	#geoTrack.reverse()
	six.print_( 'Clockwise:', geoTrack.isClockwise() )
	
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
