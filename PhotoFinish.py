import os
import wx
import sys
import math
import shutil
import datetime
import Utils
import Model
from Utils import logException

from Version import AppVerName
try:
	from VideoCapture import Device
except:
	Device = None

def formatTime( secs ):
	if secs is None:
		secs = 0
	if secs < 0:
		sign = '-'
		secs = -secs
	else:
		sign = ''
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = int(secs // (60*60))
	minutes = int( (secs // 60) % 60 )
	secs = secs % 60
	decimal = int( f * 1000.0 )
	return "%s%02d:%02d:%02d.%03d" % (sign, hours, minutes, secs, decimal)

def fileFormatTime( secs ):
	return formatTime(secs).replace(':', '-').replace('.', '-')
	
def HasPhotoFinish():
	return Device is not Null

def PilImageToWxImage( pil ):
	image = wx.EmptyImage( *pil.size )
	image.SetData( pil.convert('RGB').tostring() )
	return image

#--------------------------------------------------------------------------------------
	
camera = None
font = None
brandingBitmap = None
photoCache = set()		# Cache of all photo file names.

def getPhotoDirName( raceFileName ):
	fileName, fileExtension = os.path.splitext( raceFileName )
	# Get the directory to write the photo in.
	dirName = os.path.dirname( raceFileName )
	if not dirName:
		dirName = '.'
	dirName = os.path.join( dirName, fileName + '_Photos' )
	return dirName
	
def DeletePhotos( raceFileName ):
	dirName = getPhotoDirName( raceFileName )
	try:
		shutil.rmtree( dirName, True )
	except Exception as e:
		logException( e, sys.exc_info() )
				
def ResetPhotoInfoCache( raceFileName ):
	global photoCache
	photoCache = set()
	dir = getPhotoDirName( raceFileName )
	if not os.path.isdir(dir):
		return
	photoCache = set( file for file in os.listdir(dir) if file.startswith('bib') and file.endswith('.jpg') )
	
def hasPhoto( bib, raceSeconds ):
	fname = GetPhotoFName(bib, raceSeconds)
	if fname in photoCache:
		return True
	fnameBase = os.path.splitext( fname )[0]
	return any( ('%s-%d.jpg' % (fnameBase, i)) in photoCache for i in xrange(1, 4) )

fileFormat = 'bib-%04d-time-%s.jpg'
def GetPhotoFName( bib, raceSeconds ):
	return fileFormat % (bib if bib else 0, fileFormatTime(raceSeconds) )

latencies = []
sumLatencies = 0.0
iLatency = 0
iLatencyMax = 10

def updateLatency( latency ):
	global sumLatencies, iLatency
	# Update the response statistics.
	if len(latencies) < iLatencyMax:
		latencies.append( latency )
	else:
		sumLatencies -= latencies[iLatency]
		latencies[iLatency] = latency
	sumLatencies += latency
	iLatency = (iLatency + 1) % iLatencyMax

def getAverageLatency():
	return sumLatencies / float(len(latencies))

def SavePhoto( fileName, bib, raceSeconds, cameraImage ):
	global font, brandingBitmap, photoCache
	bitmap = wx.BitmapFromImage( PilImageToWxImage(cameraImage) )
	
	w, h = bitmap.GetSize()
	dc = wx.MemoryDC( bitmap )
	fontHeight = h//32
	if not font:
		font = wx.FontFromPixelSize( wx.Size(0,fontHeight), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD )
		
		brandingHeight = fontHeight * 2.3
		brandingBitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'CrossMgrHeader.png'), wx.BITMAP_TYPE_PNG )
		scaleMult = float(brandingHeight) / float(brandingBitmap.GetHeight())
		
		brandingImage = brandingBitmap.ConvertToImage()
		brandingImage.Rescale( int(brandingImage.GetWidth() * scaleMult), int(brandingImage.GetHeight() * scaleMult), wx.IMAGE_QUALITY_HIGH )
		brandingBitmap = brandingImage.ConvertToBitmap( dc.GetDepth() )
	
	txt = []
	if bib:
		try:
			riderInfo = Model.race.excelLink.read()[int(bib)]
		except:
			riderInfo = {}
		riderName = ', '.join( [n for n in [riderInfo.get('LastName',''), riderInfo.get('FirstName','')] if n] )
		if riderName:
			team = riderInfo.get('Team', '')
			if team:
				txt.append( '  %s    (%s)' % (riderName, team) )
			else:
				txt.append( '  %s' % riderName )

		txt.append( '  Bib: %d    RaceTime: %s    %s' % (
			bib, formatTime(raceSeconds), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) )
	else:
		txt.append( '  RaceTime: %s    %s' % (
			formatTime(raceSeconds), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) )
	
	bitmapHeight = brandingBitmap.GetHeight()
	xText, yText = brandingBitmap.GetWidth(), int(fontHeight*0.14)
	
	dc.SetFont( font )
	dc.SetPen( wx.BLACK_PEN )
	dc.SetBrush( wx.WHITE_BRUSH )
	dc.DrawRectangle( 0, 0, w, bitmapHeight+1 )
	dc.GradientFillLinear( wx.Rect(int(w/2), 0, int(w/2), bitmapHeight), wx.WHITE, wx.Colour(200,200,200), wx.EAST )
	
	dc.DrawBitmap( brandingBitmap, 0, 0 )
	
	lineHeight = int(fontHeight*1.07)
	dc.SetTextForeground( wx.BLACK )
	for t in txt:
		dc.DrawText( t, xText, yText )
		yText += lineHeight
		
	dc.DrawText( AppVerName, w - dc.GetTextExtent(AppVerName)[0] - fontHeight*.25, yText - lineHeight )
	
	dc.DrawLine( xText, 0, xText, bitmapHeight )
	
	dc.SetBrush( wx.Brush(wx.WHITE, wx.TRANSPARENT) )
	dc.DrawRectangle( 0, 0, w, bitmapHeight+1 )
	
	dc.SelectObject( wx.NullBitmap )
	image = wx.ImageFromBitmap( bitmap )
	
	# Check if the folder exists before trying to write to it.
	# Otherwise the SaveFile will raise an error dialog, which we don't want.
	if not os.path.isdir( os.path.dirname(fileName) ):
		try:
			os.mkdir( os.path.dirname(fileName) )
		except Exception as e:
			logException( e, sys.exc_info() )
			return 0
	
	# Try to save the file.
	try:
		image.SaveFile( fileName, wx.BITMAP_TYPE_JPEG )
		photoCache.add( os.path.basename(fileName) )
		return 1
	except Exception as e:
		logException( e, sys.exc_info() )
		return 0

if Device:
	def AddBibToPhoto( raceFileName, bib, raceSeconds ):
		dirName = getPhotoDirName( raceFileName )
		
		fnameOld = GetPhotoFName( None, raceSeconds )
		fnameNew = GetPhotoFName( bib, raceSeconds )
		
		fileNameOld = os.path.join( dirName, fnameOld )
		fileNameNew = os.path.join( dirName, fnameNew )
		try:
			os.rename( fileNameOld, fileNameNew )
		except Exception as e:
			logException( e, sys.exc_info() )
			
	def TakePhoto( raceFileName, bib, raceSeconds ):
		global camera, font
		
		# Open the camera if it is not open yet.
		if camera is None:
			SetCameraState( True )
			Utils.writeLog( 'TakePhoto: SetCameraState fails' )
			if not camera:
				return 0
		
		# Take the picture as quickly as possible.
		cameraImage = camera.getImage()
		if Model.race:
			updateLatency( Model.race.curRaceTime() - raceSeconds )
			
		# Get the directory to write the photo in.
		dirName = getPhotoDirName( raceFileName )
		fname = GetPhotoFName( bib, raceSeconds )
		fileName = os.path.join( dirName, fname )
		
		ret = SavePhoto( fileName, bib, raceSeconds, cameraImage )
		return ret
		
	def SetCameraState( state = False ):
		global camera, font
		camera = None
		font = None
		if state:
			Utils.FixPILSearchPath()
			try:
				camera = Device()
			except Exceptione as e:
				logException( e, sys.exc_info() )
				camera = None
		return camera
else:
	def TakePhoto( raceFileName, bib, raceSeconds ):
		Utils.writeLog( 'TakePhoto: Missing Device' )
		return 0
	def SetCameraState( state ):
		Utils.writeLog( 'SetCameraState: Missing Device' )
		return None
	def AddBibToPhoto( raceFileName, bib, raceSeconds ):
		Utils.writeLog(  'AddBibToPhoto: Missing Device' )
		return None

if __name__ == '__main__':
	app = wx.PySimpleApp()
	app.SetAppName("CrossMgr")
	Utils.disable_stdout_buffering()
	
	SetCameraState( True )
	import datetime
	for i in xrange(5):
		d = datetime.datetime.now()
		TakePhoto( 'test.cmn', 100, 129.676 + i )
		print 'Video Frame Capture Time', (datetime.datetime.now() - d).total_seconds()

