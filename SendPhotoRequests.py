import os
import json
import socket
import datetime
import Utils
import Model

HOST = 'localhost'
PORT = 54111

delimiter = '\n\n\n'

Fields = {'dirName', 'bib', 'time', 'raceSeconds', 'firstName', 'lastName', 'team', 'raceName', 'ftpHost', 'ftpUser', 'ftpPassword', 'ftpPhotoPath'}

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
	assert 'dirName' in kwargs, 'dirName is a required argument'
	messageArgs = {k : v if k != 'time' else [v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond]
			for k, v in kwargs.iteritems() if k in Fields }
	
	assert all( k in Fields for k in kwargs.iterkeys() ), 'unrecognized field(s): {}'.format(', '.join([k not in Fields for k in kwargs.iterkeys()]))
	messageArgs['cmd'] = cmd
	
	return json.dumps( messageArgs, separators=(',',':') )
	
def PhotoSendRequests( messages, cmd='photo' ):
	return sendMessages( [PhotoGetRequest(m, cmd) for m in messages] )
	
def getFtpInfo( race ):
	try:
		if race.ftpHost and race.ftpUser and race.ftpPassword and race.ftpPhotoPath:
			ftpInfo = {
				'host':			race.ftpHost,
				'user':			race.ftpUser,
				'password':		race.ftpPassword,
				'photoPath':	race.ftpPhotoPath,
			}
	except AttributeError:
		ftpInfo = None
	return ftpInfo
	
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

	ftpInfo = getFtpInfo(race)
		
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
