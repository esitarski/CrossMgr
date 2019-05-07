#!/usr/bin/env python
#------------------------------------------------------------------------------	
# JChipFake.py: program for communicating with CrossMgr.
#
# Copyright (C) Edward Sitarski, 2017.
import re
import os
import six
import sys
import time
import socket
import datetime
import threading
from six.moves.queue import Queue, Empty

#------------------------------------------------------------------------------	
# CrossMgr's port.
DEFAULT_PORT = 53135
DEFAULT_HOST = '127.0.0.1'

#------------------------------------------------------------------------------	
# JChip delimiter (CR, **not** LF)
CR = u'\r'

class JChipFake( threading.Thread ):

	def __init__( self, q, host=DEFAULT_HOST, port=DEFAULT_PORT, connectionName='JChipFake', group=None, target=None, name=None ):
		super( JChipFake, self ).__init__( group=group, target=target, name=name )
		self.daemon = True
		
		self.q = q
		self.host = host
		self.port = port
		self.connectionName = connectionName
		self.count = 0
		self.sock = None

	def connect( self ):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout( 3.0 )

		six.print_( u'Trying to connect to CrossMgr...' )
		self.sock.connect((self.host, self.port))

		#------------------------------------------------------------------------------	
		six.print_( u'Connection succeeded!' )
		six.print_( u'Sending connection name...', self.connectionName )
		message = u"N0000{}{}".format(self.connectionName, CR)
		self.sock.send( message.encode() )

		#------------------------------------------------------------------------------	
		six.print_( u'Waiting for get time command...' )
		while 1:
			received = self.sock.recv(1) if six.PY2 else self.sock.recv(1).decode()
			if received == 'G':
				while received[-1] != CR:
					received += self.sock.recv(1).decode()
				six.print_( u'Received cmd: "%s" from CrossMgr' % received[:-1] )
				break

		#------------------------------------------------------------------------------	
		six.print_( 'Send gettime data...' )
		# format is GT0HHMMSShh<CR> where hh is 100's of a second.
		# The '0' (zero) after GT is the number of days running and is ignored by CrossMgr.
		# The date can be sent in the form date=YYYYMMDD.
		self.dBase = datetime.datetime.now()
		message = u'GT0%02d%02d%02d%02d date=%s%s' % (
			self.dBase.hour, self.dBase.minute, self.dBase.second, int((self.dBase.microsecond / 1000000.0) * 100.0),
			self.dBase.strftime('%Y%m%d'),
			CR
		)
		six.print_( message[:-1] )
		self.sock.send( message.encode() )

		#------------------------------------------------------------------------------	
		six.print_( u'Waiting for send command from CrossMgr...' )
		while 1:
			received = self.sock.recv(1) if six.PY2 else self.sock.recv(1).decode()
			if received == 'S':
				while received[-1] != CR:
					received += self.sock.recv(1).decode()
				six.print_( u'Received cmd: "%s" from CrossMgr' % received[:-1] )
				break

	#------------------------------------------------------------------------------	
	# Function to format tag and time in JChip format.
	# Parameter t must be a Python datetime.
	# eg. Z413A35 10:11:16.4433 10  10000      C7
	def formatMessage( self, tag, t ):
		message = u"DJ%s %s 10  %05X      C7 date=%s%s" % (
					tag,								# Tag code
					t.strftime('%H:%M:%S.%f'),			# hh:mm:ss.ff
					self.count,							# Data index number in hex.
					t.strftime('%Y%m%d'),
					CR
				)
		self.count += 1
		return message
		
	def run( self ):
		while 1:
			tag, t = q.get()
			while 1:
				if not self.sock:
					try:
						self.connect()
					except Exception as e:
						six.print_( u'connection error:', e )
						six.print_( u'waiting 5 seconds...' )
						time.sleep( 5 )
						self.sock = None
						continue
				
				message = self.formatMessage( tag, t )
				six.print_( u'sending:', message[:-1] )
				try:
					self.sock.send( message.encode() )
					break
				except Exception as e:
					six.print_( 'communication error:', e )
					self.sock = None	
		
if __name__ == '__main__':
	# Use a queue and thread so we won't lose drop reads if we have a communcation failure.
	q = Queue()
	sender = JChipFake( q, host=DEFAULT_HOST, connectionName='JChipFake' )
	sender.start()
	for i in six.moves.range(10,1000,10):
		q.put( (i, datetime.datetime.now()) )		# put tag (or bib) and datetime on queue to transmit (no wait).
		time.sleep( 1.5 )
	
