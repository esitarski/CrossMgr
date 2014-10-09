import os
import wx
import sys
import shutil

from GetResults import GetResultsCore
from SendPhotoRequests import getPhotoDirName, SendPhotoRequests, PhotoAcknowledge
import Utils
import Model

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
