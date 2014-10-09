import os
import wx
import sys
import shutil

from GetResults import GetResultsCore
from SendPhotoRequests import getPhotoDirName, SendPhotoRequests, PhotoAcknowledge
import Utils
import Model

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
	return "{}{:02d}:{:02d}:{:06.3f}".format(sign, hours, minutes, secs)
	
def fileFormatTime( secs ):
	return formatTime(secs).replace(':', '-').replace('.', '-')

fileFormat = 'bib-%04d-time-%s-%d.jpg'
def GetPhotoFName( dirName, bib, raceSeconds, i ):
	return os.path.join( dirName, fileFormat % (bib if bib else 0, fileFormatTime(raceSeconds), i+1 ) )

photoFNameCache = set()
def updatePhotoFNameCache():
	global photoFNameCache
	
	photoFNameCache = set()
	
	race = Model.race
	if not race or not race.enableUSBCamera or not race.startTime:
		return
	
	fileName = Utils.getFileName()
	if not fileName:
		return
	
	try:
		photoFNameCache = { fname for fname in os.listdir(getPhotoDirName(fileName)) if fname.endswith('.jpg') and fname.startswith('bib') }
	except Exception as e:
		pass
		
def HasPhotoCache():
	global photoFNameCache
	return photoFNameCache
	
def hasPhoto( bib, t ):
	global photoFNameCache
	
	race = Model.race
	if not race or not race.enableUSBCamera or not race.startTime:
		return False
	fileName = Utils.getFileName()
	if not fileName:
		return False
	dirName = getPhotoDirName( fileName )
	return any( os.path.basename(GetPhotoFName(dirName, bib, t, i)) in photoFNameCache for i in xrange(2) )
	
def HasCamera():
	return PhotoAcknowledge()[0]

def okTakePhoto( num, t ):
	race = Model.race
	if not race or not race.enableUSBCamera or not race.isRunning():
		return False
	if not race.photosAtRaceEndOnly or race.isTimeTrial or num == 9999 or not t:
		return True
	
	results = GetResultsCore( race.getCategory(num) )
	if not results:
		return True
	
	rr = results[0]
	return getattr(rr,'raceTimes',None) and t > rr.raceTimes[-1] - 60.0

def DeletePhotos( raceFileName ):
	dirName = getPhotoDirName( raceFileName )
	try:
		shutil.rmtree( dirName, True )
	except Exception as e:
		logException( e, sys.exc_info() )
				
def TakePhoto( bib, raceSeconds, includeFTP=False ):
	return SendPhotoRequests( [(bib, raceSeconds)] )
