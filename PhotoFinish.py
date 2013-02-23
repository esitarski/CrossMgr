import os
import wx
import sys
import math
import datetime
import Utils
from Version import AppVerName

sys.path.append( Utils.dirName )	# Required for PIL to find the font files.

#import Image	# Required for VideoCapture (PIL library)
#import VideoCapture
#from VideoCapture import Device

try:
	from VideoCapture import Device
except:
	Device = None

def HasPhotoFinish():
	return Device is not Null

def PilImageToWxImage( myPilImage, copyAlpha=True ) :
	hasAlpha = myPilImage.mode[ -1 ] == 'A'
	if copyAlpha and hasAlpha :  # Make sure there is an alpha layer copy.

		myWxImage = wx.EmptyImage( *myPilImage.size )
		myPilImageCopyRGBA = myPilImage.copy()
		myPilImageCopyRGB = myPilImageCopyRGBA.convert( 'RGB' )    # RGBA --> RGB
		myPilImageRgbData = myPilImageCopyRGB.tostring()
		myWxImage.SetData( myPilImageRgbData )
		myWxImage.SetAlphaData( myPilImageCopyRGBA.tostring()[3::4] )  # Create layer and insert alpha values.

	else :    # The resulting image will not have alpha.

		myWxImage = wx.EmptyImage( *myPilImage.size )
		myPilImageCopy = myPilImage.copy()
		myPilImageCopyRGB = myPilImageCopy.convert( 'RGB' )    # Discard any alpha from the PIL image.
		myPilImageRgbData =myPilImageCopyRGB.tostring()
		myWxImage.SetData( myPilImageRgbData )

	return myWxImage
	
#--------------------------------------------------------------------------------------
	
camera = None
font = None
photoCache = set()		# Cache of all photo file names.

fileFormat = 'bib-%04d-time-%02d-%02d-%02d-%02d.jpg'

def getPhotoDirName( raceFileName ):
	fileName, fileExtension = os.path.splitext( raceFileName )
	# Get the directory to write the photo in.
	dirName = os.path.dirname( raceFileName )
	if not dirName:
		dirName = '.'
	dirName = os.path.join( dirName, fileName + '_Photos' )
	return dirName

def ResetPhotoInfoCache( raceFileName ):
	global photoCache
	photoCache = set()
	dir = getPhotoDirName( raceFileName )
	if not os.path.isdir(dir):
		return
	photoCache = set( file for file in os.listdir(dir) if file.startswith('bib') and file.endswith('.jpg') )
	
def hasPhoto( bib, raceSeconds ):
	iSeconds = int(raceSeconds)
	tStr = fileFormat % (bib, int(iSeconds / (60*60)), int(iSeconds / 60) % 60, iSeconds % 60, int(math.modf(raceSeconds)[0] * 100))
	return tStr in photoCache
	
if Device:
	def TakePhoto( raceFileName, bib, raceSeconds ):
		global camera, font
		
		# Get the directory to write the photo in.
		dirName = getPhotoDirName( raceFileName )
		if not os.path.isdir( dirName ):
			try:
				os.mkdir( dirName )
			except:
				return
		
		iSeconds = int(raceSeconds)
		hours = int(iSeconds / (60*60))
		minutes = int(iSeconds / 60) % 60
		seconds = iSeconds % 60
		decimals = int(math.modf(raceSeconds)[0] * 100)
	
		# Get the filename for the photo.
		fname = fileFormat % (bib, hours, minutes, seconds, decimals)
		fileName = os.path.join( dirName, fname )
		
		# Write the photo.
		if camera is None:
			SetCameraState( True )
		if camera:
			bitmap = wx.BitmapFromImage( PilImageToWxImage(camera.getImage()) )
			w, h = bitmap.GetSize()
			dc = wx.MemoryDC( bitmap )
			dc.SetTextForeground( wx.WHITE )
			fontHeight = h//25
			if not font:
				font = wx.FontFromPixelSize( wx.Size(0,fontHeight), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )
			txt = 'Bib: %d  RaceTime: %02d:%02d:%02d.%02d  %s  %s' % (
				bib, hours, minutes, seconds, decimals, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), AppVerName)
			dc.SetFont( font )
			dc.DrawText( txt, fontHeight * 0.5, h - fontHeight*1.25 )
			wx.ImageFromBitmap(bitmap).SaveFile( fileName, wx.BITMAP_TYPE_JPEG )
			photoCache.Add( fname )		# Add the photo to the cache.
		
	def SetCameraState( state = False ):
		global camera, font
		camera = None
		font = None
		if state:
			try:
				camera = Device()
			except:
				camera = None
else:
	def TakePhoto( raceFileName, bib, raceSeconds ):
		pass
	def SetCameraState( state ):
		pass

if __name__ == '__main__':
	app = wx.App()
	SetCameraState( True )
	import datetime
	for i in xrange(5):
		d = datetime.datetime.now()
		TakePhoto( 'test.cmn', 100, 129.676 + i )
		print 'Video Frame Capture Time', (datetime.datetime.now() - d).total_seconds()
