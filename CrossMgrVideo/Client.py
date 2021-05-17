import os
import json
import socket
import random
import time
import datetime
import shutil

from MainWin import HOST, PORT

delimiter = '\n\n\n'

Fields = {'dirName', 'bib', 'time', 'raceSeconds', 'first_name', 'last_name', 'team', 'race_name'}

def sendMessages( messages ):
	if messages:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST, PORT))
			s.sendall( delimiter.join(messages).encode() )
		except Exception as e:
			return False, e
	
	return True, None

def PhotoGetRequest( kwargs, cmd ):
	assert 'dirName' in kwargs, 'dirName is a required argument'
	messageArgs = {k : v if k != 'time' else [v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond]
			for k, v in kwargs.items() if k in Fields }
	
	assert all( k in Fields for k in kwargs.keys() ), 'unrecognized field(s): {}'.format(', '.join([k not in Fields for k in kwargs.keys()]))
	messageArgs['cmd'] = cmd
	
	return json.dumps( messageArgs, separators=(',',':') )
	
def PhotoSendRequests( messages, cmd='photo' ):
	return sendMessages( [PhotoGetRequest(m, cmd) for m in messages] )

def PhotoAcknowledge():
	return sendMessages( [json.dumps( {'cmd':'ack'}, separators=(',',':') )] )
	
if __name__ == '__main__':
	now = datetime.datetime.now
	choice = random.choice

	tStart = now()
	time.sleep( 0.5 )

	first_names = 'Liam	Ethan	Jacob	Lucas	Benjamin'.split()
	last_names = 'SMITH JOHNSON WILLIAMS JONES BROWN'.split()
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
	
	for q in range(1000):
		requests = []
		for i in range(random.randint(1, 2)):
			tNow = now()
			requests.append( {
					'dirName':		dirName,
					'bib':			0,
					'time':			tNow,
					'raceSeconds':	(tNow - tStart).total_seconds(),
					'race_name':	'Client Race Test',
				}
			)
		success, error = PhotoSendRequests( requests, 'photo' )
		if not success:
			print( error )
		time.sleep( random.random() * 2 )
		for request in requests:
			request.update( {
				'bib':			int(199*random.random()+1),
				'first_name':	choice(first_names),
				'last_name':		choice(last_names),
				'team':			choice(teams),
			} )
		success, error = PhotoSendRequests( requests, 'rename' )
		if not success:
			print( error )
		time.sleep( random.random() * 2 )
	
	while True:
		requests = []
		for i in range(random.randint(0, 5)):
			tNow = now()
			requests.append( {
					'dirName':		dirName,
					'bib':			int(199*random.random()+1),
					'time':			tNow,
					'raceSeconds':	(tNow - tStart).total_seconds(),
					'race_name':	'Client Race Test',
					'first_name':	choice(first_names),
					'last_name':		choice(last_names),
					'team':			choice(teams),
				}
			)
		success, error = PhotoSendRequests( requests )
		if not success:
			print( error )
		time.sleep( random.random() * 2 )
