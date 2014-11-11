import os
import json
import socket
import datetime
import Utils
import Model

HOST = 'localhost'
PORT = 54111

delimiter = '\n\n\n'

def getPhotoDirName( raceFileName ):
	return os.path.join( os.path.dirname(raceFileName) or '.', os.path.splitext(raceFileName)[0] + '_Photos' )

def sendMessages( messages ):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))
		s.sendall( delimiter.join(messages) )
		s.close()
	except Exception as e:
		return False, e
	
	return True, None

def PhotoGetRequest( kwargs, cmd ):
	messageArgs = { k : v if k != 'time' else [v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond]
			for k, v in kwargs.iteritems() }
	messageArgs['cmd'] = cmd	
	return json.dumps( messageArgs, separators=(',',':') )
	
def PhotoSendRequests( messages, cmd='photo' ):
	return sendMessages( [PhotoGetRequest(m, cmd) for m in messages] )
	
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
		'dirName':		dirName,
		'bib':			bib,
		'time':			race.startTime + datetime.timedelta(seconds=raceSeconds),
		'raceSeconds':	raceSeconds,
		'raceName':		race.name,
	}
	try:
		riderInfo = externalInfo[bib]
		for a, b in (('firstName', 'FirstName'), ('lastName','LastName'), ('team', 'Team')):
			try:
				info[a] = riderInfo[b]
			except KeyError:
				pass
	except KeyError:
		pass
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
	except:
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
	if not bibRaceSeconds:
		return True, 'no requests'
	
	race = Model.race
	if not race or not race.startTime:
		return False, 'race not started'

	ftpInfo = getFtpInfo( race )
		
	try:
		externalInfo = race.excelLink.read( True )
	except:
		externalInfo = {}
	
	dirName = getPhotoDirName( Utils.getFileName() )
	
	requests = []
	for bib, raceSeconds in bibRaceSeconds:
		request = getRequest( race, dirName, bib, raceSeconds, externalInfo )
		if ftpInfo is not None:
			request['ftpInfo'] = ftpInfo
		
		requests.append( request )
	
	return PhotoSendRequests( requests, 'rename' )
	
def PhotoAcknowledge():
	return sendMessages( [json.dumps( {'cmd':'ack'}, separators=(',',':') )] )
	
if __name__ == '__main__':
	print getFtpInfo( None )
	
	race = Model.newRace()
	race._populate()

	print getFtpInfo( race )
	
	race.ftpHost = 'ftpHost'
	race.ftpUser = 'ftpUser'
	race.ftpPassword = 'ftpPassword'
	race.ftpPhotoPath = 'ftpPhotoPath'
	print getFtpInfo( race )
