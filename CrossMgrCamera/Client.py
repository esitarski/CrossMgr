import os
import json
import socket
import random
import time
import datetime
import shutil

from MainWin import HOST, PORT

delimeter = '\n\n\n'

Fields = {'dirName', 'bib', 'time', 'raceSeconds', 'firstName', 'lastName', 'team', 'raceName'}

def PhotoSendMessage( **kwargs ):
	assert 'dirName' in kwargs, 'dirName is a required argument'
	messageArgs = {}
	for k, v in kwargs.iteritems():
		assert k in Fields, 'unrecognized argument: {}'.format(key)
		messageArgs[k] = v if k != 'time' else [v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond]
	
	message = json.dumps( messageArgs, separators=(',',':') )
	print message
	
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))
		s.sendall( message + delimeter )
	except Exception as e:
		return False, e
	
	return True, None

if __name__ == '__main__':
	now = datetime.datetime.now
	choice = random.choice

	tStart = now()

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

	dirName = 'Test_Photos'
	
	# Cleanup the photo directory.
	if os.path.exists(dirName):
		shutil.rmtree( dirName )
	os.mkdir( dirName )
	
	while 1:
		for i in xrange(random.randint(0, 5)):
			tNow = now()
			success, error = PhotoSendMessage(
				dirName = dirName,
				bib = int(199*random.random()+1),
				time = tNow,
				raceSeconds = (tNow - tStart).total_seconds(),
				firstName = choice(firstNames),
				lastName = choice(lastNames),
				team = choice(teams),
				raceName = u'Client Race Test'
			)
			if not success:
				print error
		time.sleep( random.random() * 2 )