import os
import wx
import sys
import math
import datetime
from Version import AppVerName

try:
	from VideoCapture import Device
except:
	Device = None

def PilImageToWxImage( myPilImage, copyAlpha=True ) :

	hasAlpha = myPilImage.mode[ -1 ] == 'A'
	if copyAlpha and hasAlpha :  # Make sure there is an alpha layer copy.

		myWxImage = wx.EmptyImage( *myPilImage.size )
		myPilImageCopyRGBA = myPilImage.copy()
		myPilImageCopyRGB = myPilImageCopyRGBA.convert( 'RGB' )    # RGBA --> RGB
		myPilImageRgbData =myPilImageCopyRGB.tostring()
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

if Device:
	def TakePhoto( raceFileName, bib, raceSeconds ):
		global camera, font
		iSeconds = int(raceSeconds)
		hours = int(iSeconds / (60*60))
		minutes = int(iSeconds / 60) % 60
		seconds = iSeconds % 60
		decimals = int(math.modf(raceSeconds)[0] * 100)
		tStr = '%02d-%02d-%02d-%02d' % (hours, minutes, seconds, decimals)
	
		fileName, fileExtension = os.path.splitext( raceFileName )
		
		# Get the directory to write the photo in.
		dirName = os.path.dirname( raceFileName )
		if not dirName:
			dirName = '.'
		dirName = os.path.join( dirName, fileName + '_Photos' )
		if not os.path.isdir( dirName ):
			try:
				os.mkdir( dirName )
			except:
				return
		
		# Get the filename for the photo.
		fileName = os.path.join( dirName, 'bib-%04d-time-%s.jpg' % (bib, tStr) )
		
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
			#camera.saveSnapshot( fileName, timestamp=1, boldfont=1 )
		
	def SetCameraState( state = False ):
		global camera, font
		camera = None
		font = None
		
		if state:
			try:
				camera = Device()
			except:
				pass
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
