import os
import wx
import sys
import math
import shutil

from GetResults import GetResultsCore
from SendPhotoRequests import getPhotoDirName, SendPhotoRequests, PhotoAcknowledge
import Utils
import Model

def formatTime( secs ):
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = secs // (60*60)
	minutes = (secs // 60) % 60
	secStr = '{:06.3f}'.format( secs%60 + f ).replace('.', '-')
	return "{:02d}-{:02d}-{}".format(hours, minutes, secStr)

def GetPhotoFName( dirName, bib, raceSeconds, i ):
	return os.path.join(dirName, 'bib-{:04d}-time-{}-{}.jpg'.format(int(bib or 0), formatTime(raceSeconds or 0), i+1))

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
		print e
		
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
	return 2 if SendPhotoRequests( [(bib, raceSeconds)] )[0] else 0
