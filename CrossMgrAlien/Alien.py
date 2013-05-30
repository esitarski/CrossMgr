import re
import os
import time
import math
import socket
import threading
import datetime
import xml
import xml.etree.ElementTree
import xml.etree.cElementTree
import xml.dom
import xml.dom.minidom
import unicodedata
from xml.dom.minidom import parseString
from Queue import Empty
from Utils import readDelimitedData, timeoutSecs
import cStringIO as StringIO

HOME_DIR = os.path.expanduser("~")

RepeatSeconds = 2	# Number of seconds that a tag is considered a repeat read.

#-------------------------------------------------------------------------
# Alien Reader Initialization Commands
#
cmdStr = '''
alien							# default username
password						# default password

get ReaderName					# Do not change.  Use this to check if the login succeeded.  

# Turn off Auto and Notify Mode.
set AutoMode = OFF				# turn off auto mode.
set NotifyMode = OFF			# turn off notify mode.

clear TagList					# clear any old tags

set Function = Reader			# ensure we are not in programming mode

set Time = {time}				# the time of the reader to match the computer
set TagListMillis = ON			# record tags times to milliseconds
set PersistTime = -1				# hold on to a tag for 2 seconds before considering it new again

set TagStreamMode = OFF			# turn off tag streaming - we want a tag list
set TagType = 16				# tell reader to default looking for Gen 2 tags

set AcquireMode = Inventory		# resolve multiple tag reads rather than just reading the closest/strongest tag
set AcqG2Q = 5					# tell the reader to expect a larger group of tags in each read cycle (2^5 = 32)
set AcqG2Cycles = 8				# set the outer loop to make the reader work harder to get reads

set AntennaSequence = {antennas}	# Set which antennas to use based on user indication.
set RFModulation = STD			# Standard operating mode

# Notify configuration.
set NotifyTrigger = Add			# trigger notify when tags are added to the list.
set NotifyInclude = Tags		# notify for tags and not pin status, etc.
set NotifyFormat = XML			# send message in XML format
set NotifyHeader = ON			# include notify header on tag read messages
set NotifyAddress = {notifyHost}:{notifyPort}	# address to send notify messages
set NotifyKeepAliveTime = 30	# time to keep the connection open after a tag read (in case there is another read soon after)
set NotifyQueueLimit = 1000		# failed notification messages to queue for later delivery (max=1000)
set NotifyRetryPause = 10		# wait 10 seconds between failed notify attempts (time to reconnect the network)
set NotifyRetryCount = -1		# no limit on retry attempts (if failure)
set NotifyMode = ON				# start notify mode.

# Auto Mode configuration.
AutoModeReset					# reset auto response state machine
set AutoWaitOutput = 0			# don't change any pin states while waiting
set AutoStartTrigger = 0,0		# not triggered with pin states - start now.
set AutoStartPause = 0			# no waiting after trigger.
set AutoAction = Acquire		# reader to Acquire data, not report on input/output pins
set AutoWorkOutput = 0			# don't change any pin states when we start work.
set AutoStopTimer = 0			# no waiting after work completed
set AutoTrueOutput = 0			# don't change pin states on true
set AutoTruePause = 0			# no waiting on trigger true
set AutoStopPause = 0			# no waiting 
set AutoFalseOutput = 0			# don't change pin states on false
set AutoFalsePause = 0			# no waiting on trigger false
set AutoMode = ON				# start auto mode.

Save							# save everything to flash memory in case of power failure.

Quit							# Close the interface.
'''

# Transform the cmd string into an array of Alien reader commands (strip out comments and blank lines).
initCmds = [f.split('#')[0].strip() for f in cmdStr.split('\n') if f and not f.startswith('#')]
initCmds = [c for c in initCmds if c]	# Remove empty commands.
del cmdStr

#print '\n'.join(initCmds)

reDateSplit = re.compile( '[/ :]' )		# Characters to split date/time fields.

def removeDiacritic( input ):
	'''
	Accept a unicode string, and return a normal string (bytes in Python 3)
	without any diacritical marks.
	'''
	if type(input) == str:
		return input
	else:
		return unicodedata.normalize('NFKD', input).encode('ASCII', 'ignore')

class Alien( object ):
	CmdPrefix = chr(1)			# Causes Alien reader to suppress prompt on response.
	CmdDelim = '\n'				# Delimiter of Alien commands (sent to reader).
	ReaderDelim = '\0'			# Delimiter of Alien reader responses (received from reader).

	def __init__( self, dataQ, messageQ, shutdownQ, notifyHost, notifyPort, heartbeatPort, antennas,
				listenForHeartbeat = False, cmdHost = '', cmdPort = 0 ):
		self.notifyHost = notifyHost
		self.notifyPort = notifyPort
		self.heartbeatPort = heartbeatPort
		self.listenForHeartbeat = listenForHeartbeat
		self.antennas = antennas
		self.cmdHost = cmdHost
		self.cmdPort = cmdPort
		self.dataQ = dataQ			# Queue to write tag reads.
		self.messageQ = messageQ	# Queue to write operational messages.
		self.shutdownQ = shutdownQ	# Queue to listen for shutdown.
		self.start()
		
	def start( self ):
		# Create a log file name.
		tNow = datetime.datetime.now()
		dataDir = os.path.join( HOME_DIR, 'AlienData' )
		if not os.path.isdir( dataDir ):
			os.makedirs( dataDir )
		self.fname = os.path.join( dataDir, tNow.strftime('Alien-%Y-%m-%d-%H-%M-%S.txt') )
		with open(self.fname, 'w') as pf:
			pf.write( 'Tag ID, Discover Time, Count\n' )
	
		self.keepGoing = True
		
		self.alienInfo = None
		self.tagCount = 0
		
	#-------------------------------------------------------------------------
	
	def checkKeepGoing( self ):
		if not self.keepGoing:
			return False
			
		try:
			# Check the shutdown queue for a message.  If there is one, shutdown.
			d = self.shutdownQ.get( False )
			self.keepGoing = False
			return False
		except Empty:
			return True
			
	def getResponse( self, conn ):
		# Read delimited data from the reader
		response = ''
		while not response.endswith( self.ReaderDelim ):
			more = conn.recv( 4096 )
			if not more:
				break
			response += more
		return response
	
	def stripReaderDelim( self, response ):
		return (response[:-len(self.ReaderDelim)] if response.endswith(self.ReaderDelim) else response).strip()
	
	#-------------------------------------------------------------------------
	
	def sendCommands( self ):
		''' Send initialization commands to the Alien reader. '''
		self.messageQ.put( ('Alien', 'Sending initialization commands to the Alien reader...') )
		cmdSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		try:
			cmdSocket.connect( (self.cmdHost, int(self.cmdPort)) )
		except Exception as inst:
			self.messageQ.put( ('Alien', 'Reader Connection Failed: CmdAddr=%s:%d' % (self.cmdHost, self.cmdPort) ) )
			self.messageQ.put( ('Alien', '%s' % inst ) )
			self.messageQ.put( ('Alien', 'Check that the Reader is turned on and connected, and press Reset.') )
			cmdSocket.close()
			return False
		
		# Read the header from the reader.
		response = self.getResponse( cmdSocket )								# Get the response.
		self.messageQ.put( ('Alien', self.stripReaderDelim(response) ) )
		
		cmdContext = {
				'notifyHost':	self.notifyHost,
				'notifyPort':	self.notifyPort,
				'antennas':		self.antennas,
		}
		
		success = True
		for i, c in enumerate(initCmds):
			if '{time}' in c:
				cmdContext['time'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
			
			cmd = c.format( **cmdContext )											# Perform field substitutions.
			self.messageQ.put( ('Alien', 'Sending Command: "%s"' % cmd) )			# Write to the message queue.
			# Send cmd.  Prefix with 0x01 if not username or password.
			cmdSocket.sendall( '%s%s%s' % ('' if i < 2 else self.CmdPrefix, cmd, self.CmdDelim) )
			response = self.getResponse( cmdSocket )								# Get the response.
			self.messageQ.put( ('Alien', 'Reader Response: "%s"' % self.stripReaderDelim(response) ) )
			
			# Check if we could successfully get the ReaderName from the #2 command.  If so, the login was successful.
			# If the login fails, the reader just returns nothing.
			if i == 2 and not response.lower().startswith('ReaderName'.lower()):
				self.messageQ.put( ('Alien', 'Error: "%s" command fails.' % initCmds[2]) )
				self.messageQ.put( ('Alien', 'Most likely cause:  Reader Login Failed.') )
				self.messageQ.put( ('Alien', 'Check that the reader accepts Username=%s and Password=%d' % (initCmds[0], initCmds[1]) ) )
				self.messageQ.put( ('Alien', 'Aborting.') )
				success = False
				break
			
		cmdSocket.close()
		return success
			
	def runServer( self ):
		self.messageQ.put( ('BackupFile', self.fname) )
		
		lastReadTime = {} 
		# Create an old default time.
		tOld = datetime.datetime.now() - datetime.timedelta( days = 100 )

		while self.checkKeepGoing():
			if self.listenForHeartbeat:
				#---------------------------------------------------------------------------
				# Wait for the heartbeat (contains the connection info).
				#
				self.messageQ.put( ('Alien', 'Waiting for Alien heartbeat...') )
				heartbeatSocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
				heartbeatSocket.settimeout( 1 )
				heartbeatSocket.bind( (self.notifyHost, self.heartbeatPort) )
				#heartbeatSocket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

				#---------------------------------------------------------------------------
				# Get heartbeat message.
				#
				while self.checkKeepGoing():
					try:
						data, addr = heartbeatSocket.recvfrom( 2048 )
						break
					except socket.timeout:
						time.sleep( 1 )
						
				heartbeatSocket.close()
				
				if not self.keepGoing:
					break
				
				#---------------------------------------------------------------------------
				# Strip terminating null (if present).
				#
				while data.endswith( chr(0) ):
					data = data[:-1]
				
				#---------------------------------------------------------------------------
				# Parse heartbeat message XML.
				#
				try:
					doc = parseString( data.strip() )
				except xml.parsers.expat.ExpatError, e:
					self.messageQ.put( ('Alien', 'Heartbeat Syntax error:', e) )
					self.messageQ.put( ('Alien', data) )
					continue
				except:
					self.messageQ.put( ('Alien', 'Heartbeat Syntax error') )
					self.messageQ.put( ('Alien', data) )
					continue
				
				#---------------------------------------------------------------------------
				# Extract heartbeat info.
				#
				info = {}
				for h in doc.getElementsByTagName( 'Alien-RFID-Reader-Heartbeat' ):
					for c in h.childNodes:
						if c.nodeType == c.ELEMENT_NODE:
							info[c.tagName] = c.firstChild.nodeValue.strip()
					break
					
				self.messageQ.put( ('Alien', 'Successfully Received Heartbeat Info:') )
				self.messageQ.put( ('Alien', '**********************************************') )
				self.messageQ.put( ('Alien', data) )
				self.messageQ.put( ('Alien', '**********************************************') )
				
				#---------------------------------------------------------------------------
				# Save info especially connection details.
				#
				self.alienInfo = info
				self.cmdHost = info['IPAddress']
				self.cmdPort = int(info['CommandPort'])
				
			self.messageQ.put( ('Alien', 'Alien reader.  CmdAddr=%s:%d' % (self.cmdHost, self.cmdPort)) )
			self.messageQ.put( ('CmdHost', '%s:%d' % (self.cmdHost, self.cmdPort)) )

			#---------------------------------------------------------------------------
			# Send initialization commands to the reader.
			#
			if not self.sendCommands():
				return
			
			self.tagCount = 0
			self.messageQ.put( ('Alien', 'Listening for Alien reader data on (%s:%s)...' % (str(self.notifyHost), str(self.notifyPort))) )
			dataSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			dataSocket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
			dataSocket.bind( (self.notifyHost, self.notifyPort) )
			dataSocket.listen( 5 )
			dataSocket.settimeout( 2 )
			
			#---------------------------------------------------------------------------
			# Main Loop for receiving reader messages.
			#
			readerSocket = None
			while self.checkKeepGoing():
			
				# Wait for a connection from the reader if we do not already have one.
				if not readerSocket:
					self.messageQ.put( ('Alien', 'Waiting for reader to send tag info...') )
					try:
						readerSocket, addr = dataSocket.accept()
					except socket.timeout:
						continue	# Go back to the top of the loop.  This checks the keepGoing flag.
					readerSocket.settimeout( 1 )	# Set timeout to 1 second so we can check whether to keep going.
			
				# Get the reader message.
				response = ''
				while not response.endswith( self.ReaderDelim ):
					try:
						more = readerSocket.recv( 4096 )
					except socket.timeout:
						if self.checkKeepGoing():
							continue
						break
					except Exception as inst:
						self.messageQ.put( ('Alien', 'Reader Data Connection Failed:' ) )
						self.messageQ.put( ('Alien', '%s' % inst ) )
						readerSocket.close()
						return False
						
					if not more:
						self.messageQ.put( ('Alien', 'Reader disconnected itself.') )
						readerSocket.close()
						readerSocket = None
						break
					response += more
					
				if not self.checkKeepGoing():
					break
				
				# Process the reader message.  There may be multiple notifications in the same response.
				for data in response.split( self.ReaderDelim ):
					if not data:
						continue
						
					try:
						doc = parseString( data )
					except xml.parsers.expat.ExpatError, e:
						self.messageQ.put( ('Alien', 'Message Syntax error:', e) )
						self.messageQ.put( ('Alien', data) )
						continue
					except:
						self.messageQ.put( ('Alien', 'Message Syntax error') )
						self.messageQ.put( ('Alien', data) )
						continue
						
					# Open the log file.
					try:
						pf = open( self.fname, 'a' )
					except:
						pf = None

					# Process each tag message.
					for t in doc.getElementsByTagName( 'Alien-RFID-Tag' ):
						tagID = None
						for f in t.getElementsByTagName( 'TagID' ):
							tagID = removeDiacritic(f.firstChild.nodeValue.strip())
							break
						if not tagID:
							self.messageQ.put( ('Alien', 'Missing TagID', data) )
							continue
							
						discoveryTime = None
						for f in t.getElementsByTagName( 'DiscoveryTime' ):
							discoveryTime = f.firstChild.nodeValue.strip()
							break
						if not discoveryTime:
							self.messageQ.put( ('Alien', 'Missing DiscoveryTime', data) )
							continue
							
						readCount = None
						for f in t.getElementsByTagName( 'ReadCount' ):
							readCount = f.firstChild.nodeValue.strip()
							break
						if not readCount:
							self.messageQ.put( ('Alien', 'Missing ReadCount', data) )
							continue
							
						# Decode tagID and discoveryTime.
						tagID = tagID.replace(' ', '').lstrip( '0' )
						year, month, day, hour, minute, second = reDateSplit.split(discoveryTime)
						microsecond, second = math.modf( float(second) )
						microsecond *= 1000000
						discoveryTime = datetime.datetime( int(year), int(month), int(day), int(hour), int(minute), int(second), int(microsecond) )
						
						self.tagCount += 1
						
						discoveryTimeStr = discoveryTime.strftime('%Y/%m/%d_%H:%M:%S.%f')
						
						# Check if this read happend too soon after another read.
						LRT = lastReadTime.get( tagID, tOld )
						lastReadTime[tagID] = discoveryTime
						if (discoveryTime - LRT).total_seconds() < RepeatSeconds:
							self.messageQ.put( (
								'Alien',
								'Received %d.  tag=%s Skipped (<%d secs ago).  time=%s' % (self.tagCount, tagID, RepeatSeconds, discoveryTimeStr)) )
							continue
						
						# Put this read on the queue for transmission to CrossMgr.
						self.dataQ.put( (tagID, discoveryTime) )

						# Write the entry to the log.
						if pf:
							# 									Thu Dec 04 10:14:49 PST
							pf.write( '%s,%s,%s\n' % (
										tagID,					# Keep tag in same format as read.
										discoveryTime.strftime('%a %b %d %H:%M:%S.%f %Z %Y'),
										readCount) )
						self.messageQ.put( ('Alien', 'Received %d. tag=%s, time=%s' % (self.tagCount, tagID, discoveryTimeStr)) )
					
					# Close the log file.
					if pf:
						pf.close()
			
			if readerSocket:
				readerSocket.close()
			dataSocket.close()
			return True
		
	def purgeDataQ( self ):
		while 1:
			try:
				d = self.dataQ.get( False )
			except Empty:
				break

def AlienServer( dataQ, messageQ, shutdownQ, notifyHost, notifyPort, heartbeatPort, antennas,
				listenForHeartbeat = False, cmdHost = '', cmdPort = 0 ):
	alien = Alien(dataQ, messageQ, shutdownQ, notifyHost, notifyPort, heartbeatPort, antennas,
					listenForHeartbeat, cmdHost, cmdPort)
	alien.runServer()
