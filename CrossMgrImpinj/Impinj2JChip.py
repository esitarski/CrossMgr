import re
import os
import six
import socket
import time
import threading
import datetime
from six.moves.queue import Empty
from Utils import readDelimitedData, timeoutSecs

#------------------------------------------------------------------------------	
# JChip delimiter (CR, **not** LF)
CR = u'\r'
		
#------------------------------------------------------------------------------	
# Function to format number, lap and time in JChip format
# Z413A35 10:11:16.4433 10  10000      C7
count = 0
def formatMessage( tagID, t ):
	global count
	message = u"DA{} {} 10  {:05X}      C7 date={}{}".format(
				tagID,								# Tag code in decimal, no leading zeros.
				t.strftime('%H:%M:%S.%f'),			# hh:mm:ss.ff
				count,								# Data index number in hex.
				t.strftime('%Y%m%d'),				# YYYYMMDD
				CR
			)
	count += 1
	return message

class Impinj2JChip( object ):
	def __init__( self, dataQ, messageQ, shutdownQ, crossMgrHost, crossMgrPort ):
		''' Queues:
				dataQ:		tag/timestamp data to be written out to CrossMgr.
				messageQ:	queue to write status messages.
				shutdownQ:	queue to receive shutdown message to stop gracefully.
		'''
		self.dataQ = dataQ
		self.messageQ = messageQ
		self.shutdownQ = shutdownQ
		self.crossMgrHost = crossMgrHost
		self.crossMgrPort = crossMgrPort
		self.keepGoing = True
		self.tagCount = 0
	
	def shutdown( self ):
		self.keepGoing = False
		
	def checkKeepGoing( self ):
		if not self.keepGoing:
			return False
			
		try:
			d = self.shutdownQ.get( False )
			self.keepGoing = False
			return False
		except Empty:
			return True
			
	def runServer( self ):
		instance_name = u'{}-{}'.format(socket.gethostname(), os.getpid())
		while self.checkKeepGoing():
			self.messageQ.put( ('Impinj2JChip', 'state', False) )
			self.messageQ.put( ('Impinj2JChip', u'Trying to connect to CrossMgr as "{}"...'.format(instance_name)) )
			sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

			#------------------------------------------------------------------------------	
			# Connect to the CrossMgr server.
			self.tagCount = 0
			while self.checkKeepGoing():
				try:
					sock.connect((self.crossMgrHost, self.crossMgrPort))
					break
				except socket.error:
					self.messageQ.put( ('Impinj2JChip', u'CrossMgr Connection Failed.  Trying as "{}" in 2 sec...'.format(instance_name)) )
					for t in six.moves.range(2):
						time.sleep( 1 )
						if not self.checkKeepGoing():
							break

			if not self.keepGoing:
				break
				
			# Set the timeout with CrossMgr to 2 seconds.  If CrossMgr fails to respond within this time, re-establish the connection.
			sock.settimeout( 2.0 )
				
			#------------------------------------------------------------------------------
			self.messageQ.put( ('Impinj2JChip', u'state', True) )
			self.messageQ.put( ('Impinj2JChip', u'******************************' ) )
			self.messageQ.put( ('Impinj2JChip', u'CrossMgr Connection succeeded!' ) )
			self.messageQ.put( ('Impinj2JChip', u'Sending identifier "{}"...'.format(instance_name)) )
			try:
				sock.send(u"N0000{}{}".format(instance_name, CR).encode())
			except socket.timeout:
				self.messageQ.put( ('Impinj2JChip', 'CrossMgr connection timed out [1].') )
				sock.close()
				continue

			#------------------------------------------------------------------------------	
			self.messageQ.put( ('Impinj2JChip', 'Waiting for "get time" command from CrossMgr...') )
			reconnect = False
			while self.keepGoing:
			
				# Expect a 'G' command from CrossMgr (GetTime).
				try:
					received = sock.recv(1).decode()
				except socket.timeout:
					reconnect = True
					break
				
				# Ugly way to get the cmd.
				if received == u'G':
					while received[-1] != CR:
						try:
							received += sock.recv(1).decode()
						except socket.timeout:
							reconnect = True
							break
					if not reconnect:
						self.messageQ.put( ('Impinj2JChip', u'Received cmd: "%s" from CrossMgr' % received[:-1]) )
					break
					
			if reconnect:
				self.messageQ.put( ('Impinj2JChip', u'CrossMgr connection timed out [2].') )
				sock.close()
				continue

			#------------------------------------------------------------------------------	
			if not self.keepGoing:
				break
			
			# Send 'GT' (GetTime response to CrossMgr).
			self.messageQ.put( ('Impinj2JChip', u'Send gettime data...') )
			# format is GT0HHMMSShh<CR> where hh is 100's of a second.  The '0' (zero) after GT is the number of days running, ignored by CrossMgr.
			dBase = datetime.datetime.now()
			message = u'GT0{} date={}{}'.format(
				dBase.strftime('%H%M%S%f'),
				dBase.strftime('%Y%m%d'),
				CR)
			self.messageQ.put( ('Impinj2JChip', message[:-1]) )
			try:
				sock.send( message.encode() )
			except socket.timeout:
				self.messageQ.put( ('Impinj2JChip', u'CrossMgr connection timed out [3].') )
				sock.close()
				continue

			#------------------------------------------------------------------------------	
			if not self.keepGoing:
				break

			# Expect a "Send" command from CrossMgr.
			self.messageQ.put( ('Impinj2JChip', u'Waiting for send command from CrossMgr...') )
			while self.keepGoing:
				try:
					received = sock.recv(1).decode()
				except socket.timeout:
					reconnect = True
					break
					
				# Ugly way to get the cmd.
				if received == 'S':
					while received[-1] != CR:
						try:
							received += sock.recv(1).decode()
						except socket.timeout:
							reconnect = True
							break
					if not reconnect:
						self.messageQ.put( ('Impinj2JChip', u'Received cmd: "%s" from CrossMgr' % received[:-1]) )
					break

			if reconnect:
				self.messageQ.put( ('Impinj2JChip', u'CrossMgr connection timed out [4].') )
				sock.close()
				continue

			#------------------------------------------------------------------------------
			# Enter "Send" mode - keep sending data until we get a shutdown.
			# If the connection fails, return to the outer loop to re-establish a connection.
			#
			self.messageQ.put( ('Impinj2JChip', u'Start sending data to CrossMgr...') )
			self.messageQ.put( ('Impinj2JChip', u'Waiting for Impinj reader data...') )
			while self.checkKeepGoing():
				# Get all the entries from the receiver and forward them to CrossMgr.
				d = self.dataQ.get()
				
				if d == 'shutdown':
					self.keepGoing = False
					break
				
				# Expect message if the form [tag, time].
				message = formatMessage( d[0], d[1] )
				try:
					sock.send( message.encode() )
					self.tagCount += 1
					self.messageQ.put( ('Impinj2JChip', u'Forwarded %d: %s' % (self.tagCount, message[:-1])) )
				except:
					self.dataQ.put( d )	# Put the data back on the queue for resend.
					self.messageQ.put( ('Impinj2JChip', u'Lost CrossMgr Connection.  Attempting to reconnect...') )
					break
		
			sock.close()
			
def CrossMgrServer( dataQ, messageQ, shutdownQ, crossMgrHost, crossMgrPort ):
	impinj2JChip = Impinj2JChip( dataQ, messageQ, shutdownQ, crossMgrHost, crossMgrPort )
	impinj2JChip.runServer()
