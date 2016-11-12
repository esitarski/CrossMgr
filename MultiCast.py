import socket
import struct
import sys
import time
import json
from Queue import Queue, Empty
from collections import deque
import threading
from datetime import datetime, timedelta

now = datetime.now

multicast_group = '225.3.14.15'
multicast_port = 10083

def makeJSONCompatible( info ):
	info = info.copy()
	v = info['ts']
	info['ts'] = [v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond]
	v = now()
	info['ts_sender'] = [v.year, v.month, v.day, v.hour, v.minute, v.second, v.microsecond]
	return info

class MultiCastSender( threading.Thread ):
	'''
		Thread to multicast messages written to an output queue.
		Also inventories receivers.
	'''
	def __init__( self, qIn=Queue(), receiverCallback=None, name='MultiCastSender' ):
		super( MultiCastSender, self ).__init__()
		
		self.name = name
		self.daemon = True
		self.hasReceivers = False
	
		self.qIn = qIn
		self.receiverCallback = receiverCallback or (lambda receivers: None)
		self.socket = None
	
	def put( self, message, cmd='trigger' ):
		self.qIn.put( (cmd, message) )
	
	def getReceivers( self, sock ):
		# Send our current time so the receivers can compute a clock correction.
		tNow = now()
		message = [
			'idrequest',
			{ 'ts_sender': [tNow.year, tNow.month, tNow.day, tNow.hour, tNow.minute, tNow.second, tNow.microsecond] }
		]
		sent = sock.sendto(json.dumps(message), (multicast_group, multicast_port))
		
		# Look for responses from all recipients
		receivers = []
		while 1:
			try:
				data, server = sock.recvfrom(4096)
			except socket.timeout:
				break
			
			try:
				response = json.loads( data )
			except Exception as e:
				continue
			
			if response[0] == 'idreply':
				response[1]['server'] = server
				response[1]['ts_receiver'] = datetime( *response[1]['ts_receiver'] )
				receivers.append( response[1] )
		
		return receivers

	def openSocket( self ):
		# Create the datagram socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		# Set a timeout so the socket does not block indefinitely when trying
		# to receive data.
		sock.settimeout(0.3)

		# Set the time-to-live for messages to 1 so they do not go past the
		# local network segment.
		ttl = struct.pack('b', 1)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
		return sock

	def run( self ):
		timeoutSecs = 5.0
		tLastReceiverQuery = now() - timedelta(seconds=timeoutSecs*2)
		keepGoing = True
		sock = None
		while keepGoing:
			message = None
			
			try:
				message = self.qIn.get( timeout=timeoutSecs )
			except Empty:
				pass

			if (now() - tLastReceiverQuery).total_seconds() >= timeoutSecs:
				sock = self.openSocket()
				receivers = self.getReceivers( sock )
				sock.close()
				sock = None
				self.hasReceivers = bool( receivers )
				self.receiverCallback( receivers )
				tLastReceiverQuery = now()
			
			if not message:
				continue
			
			# Clear all waiting messages.
			messages = [message]
			while 1:
				try:
					message = self.qIn.get( block=False )
					messages.append( message )
				except Empty:
					break
			
			# Broadcast all messages
			sock = self.openSocket()
			for message in messages:
				if message[0] == 'trigger':
					try:
						sent = sock.sendto(json.dumps([message[0], makeJSONCompatible(message[1])]), (multicast_group, multicast_port))
					except Exception as e:
						print e
						pass
				elif message[0] == 'terminate':
					keepGoing = False
					break
			sock.close()
			sock = None
		
		if sock:
			sock.close()

qTrigger = None
sender = None
def SendTrigger( message ):
	#
	# message is a tuple: (cmd, d)
	# d is an optional dict for the command.
	#
	# cmd can be:
	#
	# trigger    - broadcast the trigger
	# terminate  - stop the sender thread.
	#
	# if cmd = trigger, dict must contain d['ts'] which is the timestamp of the trigger.
	#
	global qTrigger, sender
	if not qTrigger:
		qTrigger = Queue()
		sender = MultiCastSender( qTrigger )
		sender.start()
	qTrigger.put( message )

#-----------------------------------------------------------------------

class MultiCastReceiver( threading.Thread ):
	
	def __init__( self, triggerCallback, messageQ = None, name='MultiCastReceiver' ):
		super( MultiCastReceiver, self ).__init__()
		
		self.triggerCallback = triggerCallback
		self.messageQ = messageQ
		self.name = name
		self.daemon = True
		
		self.recentCorrections = deque( maxlen=32 )
	
	def open( self ):
		server_address = ('', multicast_port)

		# Create the socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		# Bind to the server address
		sock.bind(server_address)

		# Tell the operating system to add the socket to the multicast group
		# on all interfaces.
		group = socket.inet_aton(multicast_group)
		mreq = struct.pack('4sL', group, socket.INADDR_ANY)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		return sock
		
	def test( self ):
		try:
			self.open().close()
			return None
		except Exception as e:
			return e
		
	def run( self ):
		now = datetime.now

		sock = self.open()
		while 1:
			data, address = sock.recvfrom(4096)
			tNow = now()
			
			try:
				message = json.loads( data )
			except Exception as e:
				continue
			
			if message[0] == 'trigger':
				message[1]['ts_receiver'] = tNow
				message[1]['ts'] = datetime( *message[1]['ts'] )
				message[1]['ts_sender'] = datetime( *message[1]['ts_sender'] )

				# Calculate a correction between the sender and the receiver.  Add it to the median list.
				self.recentCorrections.append( (message[1]['ts_receiver'] - message[1]['ts_sender']).total_seconds() )
				
				# Return the median of the last corrections (a more robust estimate of the clock difference to ignore network disruption).
				message[1]['correction_secs'] = sorted(self.recentCorrections)[len(self.recentCorrections)//2]
				
				self.triggerCallback( message[1] )
			
			elif message[0] == 'idrequest':
				# Calculate a correction between the sender and the receiver.  Add it to the median list.
				self.recentCorrections.append( (tNow - datetime( *message[1]['ts_sender'] )).total_seconds() )

				ts_receiver = [tNow.year, tNow.month, tNow.day, tNow.hour, tNow.minute, tNow.second, tNow.microsecond]
				sock.sendto( json.dumps(['idreply', {
					'hostname':socket.gethostname(),
					'name':self.name,
					'ts_receiver':ts_receiver,
					'correction_secs': sorted(self.recentCorrections)[len(self.recentCorrections)//2],
				}]), address )
			
			elif message[0] == 'terminate':
				break
			
		sock.close()

if __name__ == '__main__':
	if len(sys.argv) == 2 and sys.argv[1].startswith('-r'):
		# Receiver
		triggerQ = Queue()

		def triggerCallback( info ):
			triggerQ.put( info )
			
		def printQ():
			while 1:
				info = triggerQ.get()
				print info
				triggerQ.task_done()
				
		triggerPrinter = threading.Thread( target=printQ )
		triggerPrinter.daemon = True
		triggerPrinter.start()
		
		receiver = MultiCastReceiver( triggerCallback )
		receiver.start()
		receiver.join()
	else:
		# Sender
		def receiverCallback( receivers ):
			print 'receivers:'
			for r in receivers:
				print r
		
		for i in xrange(200):
			SendTrigger( ('trigger', {'bib':200+i, 'team':'MyTeam', 'ts':now()}) )
			time.sleep( 0.0001 if 10 < i < 20 else 1 )
		
		qTrigger.put( ('terminate',) )
		sender.join()

