
import wx
import socket
import json
import datetime

delimiter = '\n\n\n'

def getDelimited( s, delimeter ):
	r = ''
	while not r.endswith(delimiter):
		r += s.recv(4096)
	for m in r.split(delimiter):
		if m:
			yield m

def SocketListener( s, q, qMessage ):
	while 1:
		client, addr = s.accept()
		for message in getDelimited( client, delimiter ):
		
			try:
				kwargs = json.loads( message )
			except Exception as e:
				qMessage.put( ('error', 'Bad message format: "{}": {}'.format(message, e)) )
				
			try:
				kwargs['time'] = datetime.datetime( *kwargs['time'] )
			except KeyError:
				pass
			except Exception as e:
				qMessage.put( ('error', 'Bad time format: "{}": {}'.format(kwargs['time'], e)) )
				
			q.put( kwargs )
		client.close()
