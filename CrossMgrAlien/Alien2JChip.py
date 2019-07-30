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
				tagID.lstrip('0').upper(),			# Tag code as read, no leading zeros, upper case.
				t.strftime('%H:%M:%S.%f'),			# hh:mm:ss.ff
				count,								# Data index number in hex.
				t.strftime('%Y%m%d'),				# YYYYMMDD
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
		instance_name = '{}-{}'.format(socket.gethostname(), os.getpid())
		while self.checkKeepGoing():
			self.messageQ.put( ('Alien2JChip', 'state', False) )
			self.messageQ.put( ('Alien2JChip', u'Trying to connect to CrossMgr as "{}"...'.format(instance_name)) )
			sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

			#------------------------------------------------------------------------------
			# Connect to the CrossMgr server.
			self.tagCount = 0
			while self.checkKeepGoing():
				try:
					sock.connect((self.crossMgrHost, self.crossMgrPort))
					break
				except socket.error:
					self.messageQ.put( ('Alien2JChip', u'CrossMgr Connection Failed.  Trying a "{}" again in 2 secs...'.format(instance_name)) )
					for t in range(2):
						time.sleep( 1 )
						if not self.checkKeepGoing():
							break

			if not self.keepGoing:
				break
				
			#------------------------------------------------------------------------------
			self.messageQ.put( ('Alien2JChip', 'state', True) )
			self.messageQ.put( ('Alien2JChip', u'CrossMgr Connection succeeded!' ) )
			self.messageQ.put( ('Alien2JChip', u'Sending identifier "{}"...'.format(instance_name)) )
			sock.send("N0000{}{}".format(instance_name, CR) )

			#------------------------------------------------------------------------------
			self.messageQ.put( ('Alien2JChip', 'Waiting for "get time" command from CrossMgr...') )
			success = True
			while self.keepGoing:
				try:
					received = sock.recv(1).decode()
				except Exception as e:
					self.messageQ.put( ('Alien2JChip', u'CrossMgr Communication Error: {}'.format(e)) )
					success = False
					break
				if received == 'G':
					while received[-1] != CR:
						received += sock.recv(1).decode()
					self.messageQ.put( ('Alien2JChip', u'Received cmd: "{}" from CrossMgr'.format(received[:-1])) )
					break

			#------------------------------------------------------------------------------
			if not success:
				sock.close()
				continue
			
			if not self.keepGoing:
				break
				
			self.messageQ.put( ('Alien2JChip', u'Send gettime data...') )
			# format is GT0HHMMSShh<CR> where hh is 100's of a second.  The '0' (zero) after GT is the number of days running and is ignored by CrossMgr.
			dBase = datetime.datetime.now()
			message = u'GT0{} date={}{}'.format(
				dBase.strftime('%H%M%S%f'),
				dBase.strftime('%Y%m%d'),
				CR)
			self.messageQ.put( ('Alien2JChip', message[:-1]) )
			try:
				sock.send( message.encode() )
			except Exception as e:
				self.messageQ.put( ('Alien2JChip', 'CrossMgr Communication Error: {}'.format(e)) )
				success = False

			#------------------------------------------------------------------------------	
			if not success:
				sock.close()
				continue
			
			if not self.keepGoing:
				break

			self.messageQ.put( ('Alien2JChip', 'Waiting for send command from CrossMgr...') )
			while self.keepGoing:
				received = sock.recv(1).decode()
				if received == 'S':
					while received[-1] != CR:
						received += sock.recv(1).decode()
					self.messageQ.put( ('Alien2JChip', 'Received cmd: "{}" from CrossMgr'.format(received[:-1])) )
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
					sock.send( message.encode() )
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
