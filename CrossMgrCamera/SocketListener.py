
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

def SocketListener( s, q ):
	while 1:
		client, addr = s.accept()
		for message in getDelimited( client, delimiter ):
			kwargs = json.loads( message )
			try:
				kwargs['time'] = datetime.datetime( *kwargs['time'] )
			except KeyError:
				pass
			q.put( kwargs )
		client.close()
