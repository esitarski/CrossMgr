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

def sendMessages( messages ):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))
		s.sendall( delimiter.join(messages) )
	except Exception as e:
		return False, e
	
	return True, None

def PhotoGetRequest( kwargs ):
	assert 'dirName' in kwargs, 'dirName is a required argument'
	messageArgs = {k : v if k != 'time' else [v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond]
			for k, v in kwargs.iteritems() if k in Fields }
	
	assert all( k in Fields for k in kwargs.iterkeys() ), 'unrecognized field(s): {}'.format(', '.join([k not in Fields for k in kwargs.iterkeys()]))
	messageArgs['cmd'] = 'photo'
	
	return json.dumps( messageArgs, separators=(',',':') )
	
def PhotoSendRequests( messages ):
	return sendMessages( [PhotoGetRequest(m) for m in messages] )

def PhotoAcknowledge():
	return sendMessage( [json.dumps( {'cmd':'ack'}, separators=(',',':') )] )

def SendPhotoRequests( bibRaceSeconds ):
	race = Model.race
	if not race or not race.startTime:
		return

	fileName = Utils.getFileName()
	dirName = os.path.join( os.path.dirname(fileName), os.path.splitext(fileName)[0] + '_Photos' )
	
	try:
		excelLink = race.excelLink
		externalInfo = excelLink.read( True )
	except:
		externalInfo = {}
		
	ftpHost			= getattr( race, 'ftpHost', '' )
	ftpUser			= getattr( race, 'ftpUser', '' )
	ftpPassword		= getattr( race, 'ftpPassword', '' )
	ftpPhotoPath	= getattr( race, 'ftpPhotoPath', '' )
	if ftpHost and ftpUser and ftpPassword and ftpPhotoPath:
		ftpInfo = {
			'host':			ftpHost,
			'user':			ftpUser,
			'password':		ftpPassword,
			'photoPath':	ftpPhotoPath,
		}
	else:
		ftpInfo = None
	
	requests = []
	for bib, raceSeconds in bibRaceSeconds:
		request = {
			'dirName':		dirName,
			'bib':			bib,
			'time':			race.startTime + datetime.timedelta(seconds=raceSeconds),
			'raceSeconds':	raceSeconds,
			'raceName':		race.name,
			'firstName':	externalInfo[bib].get('FirstName',''),
			'lastName':		externalInfo[bib].get('LastName',''),
			'team':			externalInfo[bib].get('Team',''),
		}
		if ftpInfo is not None:
			request['ftpInfo'] = ftpInfo
		
		requests.append( request )
	success, error = PhotoSendRequests( requests )
