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

photoCache = set()
def updatePhotoFNameCache():
	global photoCache
	
	photoCache = set()
	
	race = Model.race
	if not race or not race.enableUSBCamera or not race.startTime:
		return
	
	photoDir = getPhotoDirName( Utils.getFileName() )
	try:
		photoCache = { fname[:-6] for fname in os.listdir(photoDir) if fname.startswith('bib') and fname.endswith('.jpg')  }
	except Exception as e:
		pass
		
def HasPhotoCache():
	global photoCache
	return photoCache
	
def hasPhoto( bib, t ):
	global photoCache
	
	race = Model.race
	if not photoCache or not race or not race.enableUSBCamera or not race.startTime:
		return False
		
	try:
		return os.path.basename(GetPhotoFName(getPhotoDirName(Utils.getFileName()), bib, t, 0))[:-6] in photoCache
	except Exception as e:
		return False
	
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
