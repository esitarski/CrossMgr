import os
import json
import socket
import datetime
import Utils
import Model
from MultiCast import SendTrigger

def getPhotoDirName( raceFileName ):
	return os.path.join( os.path.dirname(raceFileName or '') or '.', os.path.splitext(raceFileName or '')[0] + '_Photos' )

def PhotoSendRequests( messages, cmd='trigger' ):
	for m in messages:
		SendTrigger( [cmd, m] )
	return True, ''
	
def getFtpInfo( race ):
	try:
		if race.ftpUploadPhotos:
			return {
				'host':			race.ftpHost,
				'user':			race.ftpUser,
				'password':		race.ftpPassword,
				'photoPath':	race.ftpPhotoPath,
			}
	except Exception as e:
		pass
	
	return None
	
def getRequest( race, dirName, bib, raceSeconds, externalInfo ):
	info = {
		'dirName':			dirName,
		'bib':				bib,
		'ts':				race.startTime + datetime.timedelta(seconds=raceSeconds),
		'raceSeconds':		raceSeconds,
		'raceName':			race.name,
		'advanceSeconds':	race.advancePhotoMilliseconds/1000.0,
	}
	category = race.getCategory( bib )
	info['wave'] = category.fullname if category else u''
	try:
		riderInfo = externalInfo[bib]
		for a, b in (('firstName', 'FirstName'), ('lastName','LastName'), ('team', 'Team')):
			try:
				info[a] = riderInfo[b]
			except KeyError:
				pass
	except KeyError:
		pass
	
	if race.isTimeTrial:
		rider = race.riders.get( bib, None )
		if rider and rider.firstTime is not None:
			info['ts_start'] = race.startTime + datetime.timedelta(seconds=rider.firstTime)
		else:
			info['ts_start'] = race.startTime
	else:
		info['ts_start'] = race.startTime + datetime.timedelta(seconds=race.categoryStartOffset(category))
	return info

def SendPhotoRequests( bibRaceSeconds, includeFTP=True ):
	if not bibRaceSeconds:
		return True, 'no requests'
	
	race = Model.race
	if not race or not race.startTime:
		return False, 'race not started'

	ftpInfo = getFtpInfo(race) if includeFTP else None
		
	try:
		externalInfo = race.excelLink.read( True )
	except Exception:
		externalInfo = {}
	
	dirName = getPhotoDirName( Utils.getFileName() )
	
	requests = []
	for bib, raceSeconds in bibRaceSeconds:
		request = getRequest( race, dirName, bib, raceSeconds, externalInfo )
		if ftpInfo is not None:
			request['ftpInfo'] = ftpInfo
		
		requests.append( request )
	
	return PhotoSendRequests( requests )

def SendRenameRequests( bibRaceSeconds ):
	# Fixlater - do something about video support for time trials?
	return
	
if __name__ == '__main__':
	print( getFtpInfo( None ) )
	
	race = Model.newRace()
	race._populate()

	print( getFtpInfo( race ) )
	
	race.ftpHost = 'ftpHost'
	race.ftpUser = 'ftpUser'
	race.ftpPassword = 'ftpPassword'
	race.ftpPhotoPath = 'ftpPhotoPath'
	print( getFtpInfo( race ) )
