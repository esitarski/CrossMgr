import os
import math

try:
	from VideoCapture import Device
except:
	Device = None
	
camera = None

if Device:
	def TakePhoto( raceFileName, bib, raceSeconds ):
		global camera
		iSeconds = int(raceSeconds)
		hour = int(iSeconds / (60*60))
		minutes = int(iSeconds / 60) % 60
		seconds = iSeconds % 60
		decimals = int(math.modf(raceSeconds)[0] * 100)
		tStr = '%02d-%02d-%02d-%02d' % (hour, minutes, seconds, decimals)
	
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
			camera.saveSnapshot( fileName, timestamp=1, boldfont=1 )
		
	def SetCameraState( state = False ):
		global camera
		camera = None
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
	SetCameraState( True )
	import datetime
	for i in xrange(20):
		d = datetime.datetime.now()
		TakePhoto( 'test.cmn', 100, 129.676 + i )
		print 'Video Frame Capture Time', (datetime.datetime.now() - d).total_seconds()
