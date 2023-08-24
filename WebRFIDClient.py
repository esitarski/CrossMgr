import sys
import json
import time
import random
import datetime
import requests

import Utils

url = 'http://192.168.2.17:8765/'

def epochTime():
	return (datetime.datetime.now() - datetime.datetime(1970, 1, 1, 0, 0, 0, 0)).total_seconds()

def AutoDetect( webServerPort=8765, callback=None ):
	''' Try to find the CrossMgr computer on a small LAN network. '''
	ip = [int(i) for i in Utils.GetDefaultHost().split('.')]
	
	j = 0
	for i in range(15):
		ipTest = ip[:]
		ipTest[-1] += j
		if not (0 <= ipTest[-1] < 256):
			continue
			
		webServerHost = '.'.join( '{}'.format(v) for v in ipTest )
		if callback:
			if not callback( '{}:{}'.format(webServerHost,webServerPort) ):
				return None
		
		identity = requests.get( '{}/{}'.format(webServerHost, 'identity.js') )
		if identity.status_code == 200:
			return webServerHost + '/'

		j = -j if j > 0 else -j + 1		
			
	return None

def get_time_correction( url ):
	# Christian's algorithm (https://en.wikipedia.org/wiki/Cristian%27s_algorithm).
	# Use best latency to estimate round-trip time and get a better estimate of the time differences between two computers.
	round_trip_min = sys.float_info.max
	correction = None
	for i in range(21):	
		r = requests.get(
			'{}{}'.format(url, 'servertimestamp.js'),
			params = { 'clientTime': epochTime() }
		)
		t_response = epochTime()
		response = r.json()
		round_trip = t_response - response['clientTime']
		if round_trip < round_trip_min:
			round_trip_min = round_trip
			correction = response['serverTime'] - response['clientTime'] - round_trip_min/2.0
		time.sleep( random.random()/100.0 )
	return datetime.timedelta( seconds=correction )

message = {
	'reader_id': 10,
	'data': [
		{"tag": 'ABCDEF0123456790',"t": datetime.datetime.now() },
		{"tag": 'ABCDEF0123456791',"t": datetime.datetime.now() },
		{"tag": 'ABCDEF0123456792',"t": datetime.datetime.now() },
		{"tag": 'ABCDEF0123456793',"t": datetime.datetime.now() },
		{"tag": 'ABCDEF0123456795',"t": datetime.datetime.now() },
		{"tag": 'ABCDEF0123456796',"t": datetime.datetime.now() },
	]
}

class DateTimeEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, datetime.datetime):
			return o.isoformat( timespec='milliseconds' )

		return json.JSONEncoder.default(self, o)
		
# Show the identity of the server.
identity = requests.get( '{}{}'.format(url, 'identity.js') )
print( identity.json() )

# Get a time correction between the client and the server.
correction = get_time_correction( url )
print( 'correction', correction )

for m in message['data']:
	m['t'] += correction

r = requests.post(
	'{}{}'.format( url, 'rfid.js' ),
	data=json.dumps(message, cls=DateTimeEncoder),
	headers={'Content-Type': 'application/json'}
)

print( r.text )
