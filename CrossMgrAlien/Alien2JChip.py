import re
import socket
import time
import threading
import datetime
from Queue import Empty
from Utils import readDelimitedData, timeoutSecs

#------------------------------------------------------------------------------	
# JChip delimiter (CR, **not** LF)
CR = chr( 0x0d )
		
#------------------------------------------------------------------------------	
# Function to format number, lap and time in JChip format
# Z413A35 10:11:16.4433 10  10000      C7
count = 0
def formatMessage( tag, t ):
	global count
	message = "DA%s %s 10  %05X      C7%s" % (
				tag,								# Tag code
				t.strftime('%H:%M:%S.%f'),			# hh:mm:ss.ff
				count,								# Data index number in hex.
				CR
			)
	count += 1
	return message

class Alien2JChip( object ):
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
			
	def runServer( self ):
		while self.checkKeepGoing():
			self.messageQ.put( ('Alien2JChip', 'Trying to connect to CrossMgr...') )
			sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

			#------------------------------------------------------------------------------	
			# Connect to the CrossMgr server.
			self.tagCount = 0
			while self.checkKeepGoing():
				try:
					sock.connect((self.crossMgrHost, self.crossMgrPort))
					break
				except socket.error:
					self.messageQ.put( ('Alien2JChip', 'CrossMgr Connection Failed.  Trying again in 5 seconds...') )
					for t in xrange(5):
						time.sleep( 1 )
						if not self.checkKeepGoing():
							break

			if not self.keepGoing:
				break
				
			#------------------------------------------------------------------------------	
			self.messageQ.put( ('Alien2JChip', 'CrossMgr Connection succeeded!' ) )
			self.messageQ.put( ('Alien2JChip', 'Sending identifier...') )
			sock.send("N0000ALIEN-DRIVER%s" % CR)

			#------------------------------------------------------------------------------	
			self.messageQ.put( ('Alien2JChip', 'Waiting for "get time" command from CrossMgr...') )
			while self.keepGoing:
				received = sock.recv(1)
				if received == 'G':
					while received[-1] != CR:
						received += sock.recv(1)
					self.messageQ.put( ('Alien2JChip', 'Received cmd: "%s" from CrossMgr' % received[:-1]) )
					break

			#------------------------------------------------------------------------------	
			if not self.keepGoing:
				break
				
			self.messageQ.put( ('Alien2JChip', 'Send gettime data...') )
			# format is GT0HHMMSShh<CR> where hh is 100's of a second.  The '0' (zero) after GT is the number of days running and is ignored by CrossMgr.
			dBase = datetime.datetime.now()
			message = 'GT0%02d%02d%02d%03d%s' % (dBase.hour, dBase.minute, dBase.second, int((dBase.microsecond / 1000000.0) * 1000.0), CR)
			self.messageQ.put( ('Alien2JChip', message[:-1]) )
			sock.send( message )

			#------------------------------------------------------------------------------	
			if not self.keepGoing:
				break

			self.messageQ.put( ('Alien2JChip', 'Waiting for send command from CrossMgr...') )
			while self.keepGoing:
				received = sock.recv(1)
				if received == 'S':
					while received[-1] != CR:
						received += sock.recv(1)
					self.messageQ.put( ('Alien2JChip', 'Received cmd: "%s" from CrossMgr' % received[:-1]) )
					break

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
					sock.send( message )
					self.tagCount += 1
					self.messageQ.put( ('Alien2JChip', 'Forwarded %d: %s' % (self.tagCount, message[:-1])) )
				except:
					self.alien.dataQ.put( d )
					self.messageQ.put( ('Alien2JChip', 'Lost CrossMgr Connection.  Attempting to reconnect...') )
					break
		
			sock.close()
			
def CrossMgrServer( dataQ, messageQ, shutdownQ, crossMgrHost, crossMgrPort ):
	alien2JChip = Alien2JChip( dataQ, messageQ, shutdownQ, crossMgrHost, crossMgrPort )
	alien2JChip.runServer()