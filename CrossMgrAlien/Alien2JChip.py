import re
import os
import socket
import time
import threading
import datetime
from queue import Empty
from Utils import readDelimitedData, timeoutSecs

#------------------------------------------------------------------------------	
# JChip delimiter (CR, **not** LF)
CR = '\r'
bCR = b'\r'
		
#------------------------------------------------------------------------------	
# Function to format number, lap and time in JChip format
# Z413A35 10:11:16.4433 10  10000      C7
count = 0
def formatMessage( tagID, t ):
	global count
	message = "DA{} {} 10  {:05X}      C7 date={}{}".format(
				tagID.lstrip('0').upper(),			# Tag code as read, no leading zeros, upper case.
				t.strftime('%H:%M:%S.%f'),			# hh:mm:ss.ff
				count,								# Data index number in hex.
				t.strftime('%Y%m%d'),				# YYYYMMDD
				CR
			)
	count += 1
	return message

class Alien2JChip:
	def __init__( self, dataQ, messageQ, shutdownQ, crossMgrHost, crossMgrPort ):
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
			
	def getCmd( self, sock ):
		received = b''
		while self.keepGoing and received[-1:] != bCR:
			try:
				received += sock.recv(4096)
			except Exception as e:
				return received.decode(), e
		return received[:-1].decode(), None

	def runServer( self ):
		instance_name = '{}-{}'.format(socket.gethostname(), os.getpid())
		while self.checkKeepGoing():
			self.messageQ.put( ('Alien2JChip', 'state', False) )
			self.messageQ.put( ('Alien2JChip', 'Trying to connect to CrossMgr as "{}"...'.format(instance_name)) )

			#------------------------------------------------------------------------------
			# Connect to the CrossMgr server.
			self.tagCount = 0
			while self.checkKeepGoing():
				try:
					sock = None
					sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
					# Set the timeout with CrossMgr to 2 seconds.  If CrossMgr fails to respond within this time, re-establish the connection.
					sock.settimeout( 2.0 )				
					sock.connect((self.crossMgrHost, self.crossMgrPort))
					break
				except Exception as e:
					self.messageQ.put( ('Alien2JChip', 'CrossMgr Connection Failed ({}).'.format(e)) );
					self.messageQ.put( ('Alien2JChip', 'Trying "{}" again in 2 secs...'.format(instance_name)) )
					for t in range(2):
						time.sleep( 1 )
						if not self.checkKeepGoing():
							break

			if not self.keepGoing:
				break
				
			#------------------------------------------------------------------------------
			self.messageQ.put( ('Alien2JChip', 'state', True) )
			self.messageQ.put( ('Alien2JChip', 'CrossMgr Connection succeeded!' ) )
			self.messageQ.put( ('Alien2JChip', 'Sending identifier "{}"...'.format(instance_name)) )
			sock.sendall( "N0000{}{}".format(instance_name, CR).encode() )

			#------------------------------------------------------------------------------
			self.messageQ.put( ('Alien2JChip', 'Waiting for "get time" command from CrossMgr...') )
			success = True
			received, e = self.getCmd( sock )
			if not self.checkKeepGoing():
				break
			if e:
				self.messageQ.put( ('Alien2JChip', 'CrossMgr error: {}.'.format(e)) )
				sock.close()
				sock = None
				continue
			self.messageQ.put( ('Alien2JChip', 'Received: "{}" from CrossMgr'.format(received)) )
			if received != 'GT':
				self.messageQ.put( ('Alien2JChip', 'Incorrect command (expected GT).') )
				sock.close()
				sock = None
				continue
				
			self.messageQ.put( ('Alien2JChip', 'Send gettime data...') )
			# format is GT0HHMMSShh<CR> where hh is 100's of a second.  The '0' (zero) after GT is the number of days running and is ignored by CrossMgr.
			dBase = datetime.datetime.now()
			message = 'GT0{} date={}{}'.format(
				dBase.strftime('%H%M%S%f'),
				dBase.strftime('%Y%m%d'),
				CR)
			self.messageQ.put( ('Alien2JChip', message[:-1]) )
			try:
				sock.sendall( message.encode() )
			except Exception as e:
				self.messageQ.put( ('Alien2JChip', 'CrossMgr error: {}'.format(e)) )
				success = False

			#------------------------------------------------------------------------------	
			if not success:
				sock.close()
				sock = None
				continue
			
			if not self.keepGoing:
				break

			self.messageQ.put( ('Alien2JChip', 'Waiting for S0000 (send) command from CrossMgr...') )
			received, e = self.getCmd( sock )
			if not self.checkKeepGoing():
				break
			if e:
				self.messageQ.put( ('Alien2JChip', 'CrossMgr error: {}.'.format(e)) )
				sock.close()
				sock = None
				continue
			self.messageQ.put( ('Alien2JChip', 'Received: "{}" from CrossMgr'.format(received)) )
			if not received.startswith('S'):
				self.messageQ.put( ('Alien2JChip', 'Incorrect command (expected S0000).') )
				sock.close()
				sock = None
				continue

			#------------------------------------------------------------------------------	
			self.messageQ.put( ('Alien2JChip', 'Start sending data to CrossMgr...') )
			self.messageQ.put( ('Alien2JChip', 'Waiting for Alien reader data...') )
			while self.checkKeepGoing():
				# Get all the entries from the receiver and forward them to CrossMgr.
				d = self.dataQ.get()
				
				if d == 'shutdown':
					self.keepGoing = False
					break
				
				message = formatMessage( d[0], d[1] )
				try:
					sock.sendall( message.encode() )
					self.tagCount += 1
					self.messageQ.put( ('Alien2JChip', 'Forwarded {}: {}'.format(self.tagCount, message[:-1])) )
				except Exception as e:
					self.dataQ.put( d )	# Put the data back on the queue for resend.
					self.messageQ.put( ('Alien2JChip', 'Lost CrossMgr Connection ({}).  Attempting to reconnect...'.format(e)) )
					break
		
			sock.close()
			
def CrossMgrServer( dataQ, messageQ, shutdownQ, crossMgrHost, crossMgrPort ):
	alien2JChip = Alien2JChip( dataQ, messageQ, shutdownQ, crossMgrHost, crossMgrPort )
	alien2JChip.runServer()
