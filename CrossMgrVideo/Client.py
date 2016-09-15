import os
import json
import socket
import random
import time
import datetime
import shutil

from MainWin import HOST, PORT

delimiter = '\n\n\n'

Fields = {'dirName', 'bib', 'time', 'raceSeconds', 'firstName', 'lastName', 'team', 'raceName'}

def sendMessages( messages ):
	if messages:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST, PORT))
			s.sendall( delimiter.join(messages) )
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

def PhotoAcknowledge():
	return sendMessage( [json.dumps( {'cmd':'ack'}, separators=(',',':') )] )
	
if __name__ == '__main__':
	now = datetime.datetime.now
	choice = random.choice

	tStart = now()
	time.sleep( 0.5 )

	firstNames = 'Liam	Ethan	Jacob	Lucas	Benjamin'.split()
	lastNames = 'SMITH JOHNSON WILLIAMS JONES BROWN'.split()
	teams = '''AG2R La Mondiale
Astana Pro Team
Belkin Pro Cycling Team
BMC Racing Team
Cannondale
FDJ.fr
Garmin Sharp
Lampre-Merida
Lotto Belisol
Movistar Team
Omega Pharma - Quick-Step Cycling Team
Orica GreenEdge
Team Europcar
Team Giant-Shimano
Team Katusha
Team Sky
Tinkoff-Saxo
Trek Factory Racing'''.split( '\n' )

	dirName = os.path.join( os.path.dirname(os.path.realpath(__file__)), 'Test_Photos' )
	
	# Cleanup the photo directory.
	if os.path.exists(dirName):
		shutil.rmtree( dirName )
	os.mkdir( dirName )
	
	for q in xrange(1000):
		requests = []
		for i in xrange(random.randint(1, 2)):
			tNow = now()
			requests.append( {
					'dirName':		dirName,
					'bib':			0,
					'time':			tNow,
					'raceSeconds':	(tNow - tStart).total_seconds(),
					'raceName':		u'Client Race Test',
				}
			)
		success, error = PhotoSendRequests( requests, 'photo' )
		if not success:
			print error
		time.sleep( random.random() * 2 )
		for request in requests:
			request.update( {
				'bib':			int(199*random.random()+1),
				'firstName':	choice(firstNames),
				'lastName':		choice(lastNames),
				'team':			choice(teams),
			} )
		success, error = PhotoSendRequests( requests, 'rename' )
		if not success:
			print error
		time.sleep( random.random() * 2 )
	
	while 1:
		requests = []
		for i in xrange(random.randint(0, 5)):
			tNow = now()
			requests.append( {
					'dirName':		dirName,
					'bib':			int(199*random.random()+1),
					'time':			tNow,
					'raceSeconds':	(tNow - tStart).total_seconds(),
					'raceName':		u'Client Race Test',
					'firstName':	choice(firstNames),
					'lastName':		choice(lastNames),
					'team':			choice(teams),
				}
			)
		success, error = PhotoSendRequests( requests )
		if not success:
			print error
		time.sleep( random.random() * 2 )
