import os
import wx
import sys
import math
import shutil
import datetime
from wx.lib.agw.aui import LightColour

import Utils
import Model
from GetResults import GetResultsCore
from Utils import logException
from PIL import Image

from Version import AppVerName
try:
	from VideoCapture import Device
except:
	Device = None
	
class dotdict( object ):
	pass

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
	secs = secs % 60 + f
	return "%s%02d:%02d:%06.3f" % (sign, hours, minutes, secs)
	
def fileFormatTime( secs ):
	return formatTime(secs).replace(':', '-').replace('.', '-')
	
def HasPhotoFinish():
	return Device is not None

def PilImageToWxImage( pil ):
	image = wx.EmptyImage( *pil.size )
	image.SetData( pil.convert('RGB').tostring() )
	return image

#--------------------------------------------------------------------------------------

camera = None
photoCache = set()		# Cache of all photo file names.

def okTakePhoto( num, t ):
	race = Model.race
	if not race or not getattr(race, 'enableUSBCamera', False):
		return False
	if not race.photosAtRaceEndOnly or not race.isRunning() or getattr(race, 'isTimeTrial', False) or num == 9999 or not t:
		return True
	
	getCategory = race.getCategory
	category = getCategory( num )
	try:
		rr = next(rr for rr in GetResultsCore(None) if getCategory(rr.num) == category)
	except StopIteration:
		return False
	
	return rr.raceTimes and t > rr.raceTimes[-1] - 60.0

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

drawResources = None		# Cached resource for drawing the photo header.
def setDrawResources( dc, w, h ):
	global drawResources
	drawResources = dotdict()
	
	fontHeight = int(h/36.0)
	fontFace = 'Arial'
	
	drawResources.bibFontSize = fontHeight * 1.5
	drawResources.bibFont = wx.FontFromPixelSize(
		wx.Size(0, drawResources.bibFontSize),
		wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD,
		face=fontFace,
	)
	
	dc.SetFont( drawResources.bibFont )
	drawResources.bibWidth, drawResources.bibHeight = dc.GetTextExtent( u' 9999' )
	drawResources.bibTextColour = wx.Colour(0,0,200)
	drawResources.bibSpaceWidth = dc.GetTextExtent( u'9999' )[0] / 4
	
	drawResources.nameFontSize = drawResources.bibFontSize
	drawResources.nameFont = wx.FontFromPixelSize(
		wx.Size(0, drawResources.nameFontSize),
		wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL,
		face=fontFace,
	)
	drawResources.nameTextColour = drawResources.bibTextColour
	
	drawResources.fontSize = fontHeight * 1.0
	drawResources.font = wx.FontFromPixelSize(
		wx.Size(0, drawResources.fontSize),
		wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL,
		face=fontFace,
	)
	dc.SetFont( drawResources.font )
	drawResources.spaceWidth = dc.GetTextExtent( u'9999' )[0] / 4
	
	drawResources.smallFontSize = drawResources.fontSize * 0.9
	drawResources.smallFont = wx.FontFromPixelSize(
		wx.Size(0, drawResources.smallFontSize),
		wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL,
		face=fontFace,
	)
	drawResources.fontColour = wx.BLACK
	dc.SetFont( drawResources.font )
	drawResources.fontHeight = dc.GetTextExtent( u'ATWgjjy' )[1]
	
	bitmapHeight = drawResources.bibHeight * 2.5
	
	bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'CrossMgrHeader.png'), wx.BITMAP_TYPE_PNG )
	scaleMult = float(bitmapHeight) / float(bitmap.GetHeight())
	
	image = bitmap.ConvertToImage()
	drawResources.bitmapWidth, drawResources.bitmapHeight = int(image.GetWidth() * scaleMult), int(image.GetHeight() * scaleMult)
	image.Rescale( drawResources.bitmapWidth, drawResources.bitmapHeight, wx.IMAGE_QUALITY_HIGH )
	
	drawResources.bitmap = image.ConvertToBitmap()
	
	drawResources.fadeDark = wx.Colour(114+80,119+80,168+80)
	drawResources.fadeLight = LightColour( drawResources.fadeDark, 50 )
	drawResources.borderColour = wx.Colour( 71+50, 75+50, 122+50 )

def AddPhotoHeader( bib, raceSeconds, cameraImage, nameTxt=u'', teamTxt=u'' ):
	global drawResources
	
	race = Model.race
	bitmap = wx.BitmapFromImage( PilImageToWxImage(cameraImage) )
	
	w, h = bitmap.GetSize()
	dcMemory = wx.MemoryDC( bitmap )
	dc = wx.GCDC( dcMemory )
	
	if not drawResources:
		setDrawResources( dc, w, h )
	
	bibTxt = u''
	timeTxt = u''
	raceNameTxt = u''
	if bib:
		bibTxt = u'{}'.format(bib)
		
		try:
			riderInfo = race.excelLink.read()[int(bib)]
		except:
			if bib == 9999:
				if race:
					riderInfo = {
						'LastName':		race.name,
						'FirstName':	race.city,
						'Team':			datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
					}
				else:
					riderInfo = {
						'LastName':		'CameraTest',
						'Team':			datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
					}
			else:
				riderInfo = {}
		
		if not nameTxt:
			nameTxt = u' '.join( [n for n in [riderInfo.get('FirstName',u''), riderInfo.get('LastName',u'')] if n] )
		if not teamTxt:
			teamTxt = riderInfo.get('Team', u'')

		if bib != 9999:
			timeTxt = _('{}  {}').format(
				formatTime(raceSeconds),
				datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
			)
	else:
		timeTxt = _('{}  {}').format(
			formatTime(raceSeconds),
			datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		)
		
	if timeTxt.startswith('0'):
		timeTxt = timeTxt[1:]
	
	frameWidth = 4
	borderWidth = 1
	
	bitmapWidth = drawResources.bitmapWidth
	bitmapHeight = drawResources.bitmapHeight
	bibSpaceWidth = drawResources.bibSpaceWidth
	spaceWidth = drawResources.spaceWidth
	xText, yText = bitmapWidth, 0
	
	if race:
		raceNameTxt = race.name
	
	x = borderWidth
	y = borderWidth
	
	def shadedRect( x, y, w, h ):
		highlightTop = int(h/4.0)
		dc.GradientFillLinear( wx.Rect(0, y, w, highlightTop),
			drawResources.fadeDark, drawResources.fadeLight, wx.SOUTH )
		dc.GradientFillLinear( wx.Rect(0, y+highlightTop, w, h-highlightTop),
			drawResources.fadeDark, drawResources.fadeLight, wx.NORTH )
	
	def textInRect( txt, x, y, width, height, font=None, colour=None, alignment=wx.ALIGN_CENTER|wx.ALIGN_CENTRE_VERTICAL ):
		if font:
			dc.SetFont( font )
		if colour:
			dc.SetTextForeground( colour )
		dc.DrawLabel( txt, wx.Rect(x, y, width, height), alignment )
	
	lineHeight = int(drawResources.bibHeight * 1.15 + 0.5)
	x += xText + frameWidth + bibSpaceWidth
	
	dc.SetPen( wx.Pen(drawResources.borderColour, borderWidth) )
	
	shadedRect( x, y, w, lineHeight )

	dc.DrawLine( 0, 0, w, 0 )
	dc.DrawLine( xText, lineHeight, w, lineHeight )
	
	# Draw the bib.
	dc.SetFont( drawResources.bibFont )
	tWidth = dc.GetTextExtent( bibTxt )[0]
	textInRect( bibTxt, x, y, tWidth, lineHeight, drawResources.bibFont, drawResources.bibTextColour )

	# Draw the name and team.
	x += tWidth + spaceWidth
	textInRect( nameTxt, x, y, dc.GetTextExtent(nameTxt)[0], lineHeight, drawResources.nameFont, drawResources.bibTextColour )
	x += dc.GetTextExtent(nameTxt)[0] + spaceWidth
	remainingWidth = w - x - spaceWidth - borderWidth
	dc.SetFont( drawResources.font )
	teamTxtWidth = dc.GetTextExtent(teamTxt)[0]
	if teamTxtWidth < remainingWidth:
		textInRect( teamTxt, x, y, remainingWidth, lineHeight, drawResources.font, wx.BLACK, alignment=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
	
	y += lineHeight
	
	lineHeight = drawResources.fontHeight * 1.15
	shadedRect( 0, y, w, lineHeight )
	dc.DrawLine( 0, y+lineHeight, w, y+lineHeight )
	
	# Draw the time, race time and raceName.
	dc.SetFont( drawResources.font )
	x = borderWidth
	x += xText + frameWidth + bibSpaceWidth
	textInRect( timeTxt, x, y, w-x, lineHeight, drawResources.font, wx.BLACK, alignment=wx.ALIGN_LEFT|wx.ALIGN_CENTRE_VERTICAL )
	x += dc.GetTextExtent(timeTxt)[0] + spaceWidth
	remainingWidth = w - x - spaceWidth - borderWidth
	raceNameTxtWidth = dc.GetTextExtent(raceNameTxt)[0]
	if raceNameTxtWidth < remainingWidth:
		textInRect( raceNameTxt, x, y, remainingWidth, lineHeight, drawResources.font, wx.BLACK, alignment=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
	
	dc.DrawBitmap( drawResources.bitmap, frameWidth, frameWidth )
	
	dc.SetBrush( wx.TRANSPARENT_BRUSH )
	
	frameHalf = frameWidth / 2
	dc.SetPen( wx.Pen(drawResources.borderColour, frameWidth) )
	dc.DrawRectangle( frameHalf, frameHalf, bitmapWidth+frameHalf, bitmapHeight+frameHalf )
	dc.SetPen( wx.Pen(wx.WHITE, frameHalf) )
	dc.DrawRectangle( frameHalf, frameHalf, bitmapWidth+frameHalf, bitmapHeight+frameHalf )
	
	dc.SetPen( wx.Pen(drawResources.borderColour, 1) )
	dc.DrawLine( w-1, 0, w-1, y+lineHeight )
	
	return wx.ImageFromBitmap( bitmap )

def SavePhoto( fileName, bib, raceSeconds, cameraImage ):
	global photoCache
	
	Utils.cameraError = None

	# Check if the folder exists before trying to write to it.
	# Otherwise the SaveFile will raise an error dialog, which we don't want.
	if not os.path.isdir( os.path.dirname(fileName) ):
		try:
			os.mkdir( os.path.dirname(fileName) )
		except Exception as e:
			Utils.cameraError = e
			logException( e, sys.exc_info() )
			return 0
	
	# Try to save the file.
	image = AddPhotoHeader( bib, raceSeconds, cameraImage )
	
	try:
		image.SaveFile( fileName, wx.BITMAP_TYPE_JPEG )
		photoCache.add( os.path.basename(fileName) )
		return 1
	except Exception as e:
		Utils.cameraError = e
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
	
	def SnapPhoto():
		global camera
		Utils.cameraError = None
		
		# Open the camera if it is not open yet.
		if camera is None:
			SetCameraState( True )
			if not camera:
				Utils.cameraError = 'TakePhoto: SetCameraState fails'
				Utils.writeLog( Utils.cameraError )
				return None
		
		return camera.getImage()
	
	def TakePhoto( raceFileName, bib, raceSeconds ):
		
		cameraImage = SnapPhoto()
		if not cameraImage:
			return 0
		
		if Model.race:
			updateLatency( Model.race.curRaceTime() - raceSeconds )
			
		# Get the directory to write the photo in.
		dirName = getPhotoDirName( raceFileName )
		fname = GetPhotoFName( bib, raceSeconds )
		fileName = os.path.join( dirName, fname )
		
		ret = SavePhoto( fileName, bib, raceSeconds, cameraImage )
		return ret
		
	def SetCameraState( state = False ):
		global camera, drawResources
		Utils.cameraError = None
		camera = None
		drawResources = None
		if state:
			Utils.FixPILSearchPath()
			try:
				camera = Device( max((Model.race.cameraDevice if Model.race else 0) or 0, 0) )
			except Exception as e:
				logException( e, sys.exc_info() )
				Utils.cameraError = 'SetCameraState: {}'.format(e)
				camera = None
		return camera
else:
	def SnapPhoto():
		Utils.cameraError = 'SnapPhoto: Camera not supported on this platform.'
		Utils.writeLog( Utils.cameraError )
		return 0
	def TakePhoto( raceFileName, bib, raceSeconds ):
		Utils.cameraError = 'TakePhoto: Camera not supported on this platform.'
		Utils.writeLog( Utils.cameraError )
		return 0
	def SetCameraState( state ):
		Utils.cameraError = 'SetCameraState: Camera not supported on this platform.'
		Utils.writeLog( Utils.cameraError )
		return None
	def AddBibToPhoto( raceFileName, bib, raceSeconds ):
		Utils.cameraError = 'AddBibToPhoto: Camera not supported on this platform.'
		Utils.writeLog( Utils.cameraError )
		return None

if __name__ == '__main__':	
	race = Model.newRace()
	race._populate()

	app = wx.App(False)
	app.SetAppName("CrossMgr")
	Utils.disable_stdout_buffering()
	
	mainWin = wx.Frame(None,title="CrossMan", size=(850,650))
	bitmap = wx.StaticBitmap( mainWin, size=(800,600) )
	pimage = Image.new('RGB', (800,600), 'grey')
	img = AddPhotoHeader( 151, 631, pimage, nameTxt='Davide FRATTINI', teamTxt='UNITEDHEALTHCARE PRO CYCLING TEAM' )
	bitmap.SetBitmap( wx.BitmapFromImage(img) )

	vs = wx.BoxSizer( wx.VERTICAL )
	vs.Add( bitmap )
	mainWin.SetSizer( vs )
	
	mainWin.Show( True )
	app.MainLoop()
	
	'''
	SetCameraState( True )
	for i in xrange(5):
		d = datetime.datetime.now()
		TakePhoto( 'test.cmn', 100, 129.676 + i )
		print 'Video Frame Capture Time', (datetime.datetime.now() - d).total_seconds()
	'''
	

