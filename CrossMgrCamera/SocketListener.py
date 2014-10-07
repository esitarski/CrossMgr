
import wx
import socket
import threading
import json
import datetime
import time

delimiter = '\n\n\n'

def postRequests( requests, qRequest ):
	# Wait for some frames to accumulate.
	time.sleep( 0.2 )
	
	# Now, post all the messages
	for kwargs in requests:
		qRequest.put( kwargs )

def SocketListener( s, qRequest, qMessage ):
	while 1:
		client, addr = s.accept()
		
		messages = ''
		while 1:
			data = client.recv( 4096 )
			if not data:
				break
			messages += data
		client.close()
		
		# Collect the messages.
		requests = []
		for message in messages.split( delimiter ):
			if not message:
				continue
			
			try:
				kwargs = json.loads( message )
			except Exception as e:
				qMessage.put( ('error', 'Bad request format: "{}": {}'.format(message, e)) )
				continue
				
			try:
				kwargs['time'] = datetime.datetime( *kwargs['time'] )
			except KeyError:
				pass
			except Exception as e:
				qMessage.put( ('error', 'Bad time format: "{}": {}'.format(kwargs['time'], e)) )
				continue
			
			if kwargs.get('cmd', None) == 'photo':
				requests.append( kwargs )

		# Post the messages in a thread so we can add a delay.
		thread = threading.Thread( target=postRequests, args=(requests, qRequest) )
		thread.daemon = True
		thread.start()
