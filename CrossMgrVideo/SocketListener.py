
import wx
import socket
import threading
import json
import datetime
import time

now = datetime.datetime.now
delimiter = '\n\n\n'
minDelay = 0.2

def postRequests( requests, qRequest, delay ):
	# If we process a message too early, it is possible that the before and after frame are
	# not processed yet and could be missed.
	# Or, if the photo request is in the future, we need to wait before we proess it.
	time.sleep( delay )
	for kwargs in requests:
		qRequest.put( kwargs )

def SocketListener( s, qRequest, qMessage ):
	messageStrs = []
	while 1:
		client, addr = s.accept()
		
		while 1:
			data = client.recv( 4096 )
			if not data:
				break
			messageStrs.append( data )
		client.close()
		
		messages = ''.join( messageStrs )
		del messageStrs[:]
		
		# Collect the photo messages.
		tNow = now()
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
			
			cmd = kwargs.get('cmd', None)
			dtMax = minDelay
			if cmd == 'photo':
				dt = (tNow - kwargs['time']).total_seconds() - kwargs.get('advanceSeconds',0.0)
				if dt < minDelay:
					requests.append( kwargs )
					dtMax = max(dtMax, -dt + minDelay if dt < 0 else minDelay)
				else:
					qRequest.put( kwargs )

		# Post the messages in a thread to add a delay.
		if requests:
			thread = threading.Thread( target=postRequests, args=(requests, qRequest, dtMax) )
			thread.daemon = True
			thread.name = 'PostRequestDelay'
			thread.start()
