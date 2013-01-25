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
from xml.dom.minidom import parseString
from Queue import Empty
from Utils import readDelimitedData, timeoutSecs
import cStringIO as StringIO

HOME_DIR = os.path.expanduser("~")

#-------------------------------------------------------------------------
# Alien Reader Initialization Commands
#
cmdStr = '''
alien						# login
password					# default password

Function = Reader			# ensure we are not in programming mode

Clear TagList				# clear any old tags

Time = {time}				# the time of the reader to match the computer
TagListMillis = ON			# record tags times to milliseconds
PersistTime = 2				# hold on to a tag for 2 seconds before considering it new again
HeartbeatTime = 15			# send the heartbeat every 15 seconds rather than the default 30

TagStreamMode = OFF			# turn off tag streaming - we want a tag list
TagType = 16				# tell reader to default looking for Gen 2 tags

AcquireMode = Inventory		# resolve multiple tag reads rather than just reading the closest/strongest tag
# make the reader do some more work to try to resolve tags in a group
AcqC1Cycles = 5				# for Gen 1 tags
AcqG2Cycles = 5				# for Gen 2 tags

AntennaSeq = 0 1			# Cycle transmitting/receiving between antennas 0 and 1
RFModulation = STD			# Standard operating mode

# Auto Mode configuration.
AutoModeReset				# reset auto response state machine
AutoAction = Acquire		# reader to Acquire data, not report on pins
AutoStartTrigger = 0,0		# not triggered with pins states
AutoStopTimer = 0			# no waiting after work completed
AutoTruePause = 0 			# no waiting on trigger true
AutoFalsePause = 0			# no waiting on trigger false
AutoWorkOutput = 0			# don't change any pin status
AutoMode = ON				# start auto mode.

# Notify configuration.
NotifyMode = OFF			# turn off notify mode.
NotifyTrigger = Add			# trigger notify when tags are added to the list.
NotifyInclude = Tags		# notify for tags and not pin status, etc.
NotifyFormat = XML			# send message in XML format
NotifyHeader = ON			# include notify header on tag read messages
NotifyAddress = {notifyHost}:{notifyPort}	# address to send notify messages
NotifyKeepAliveTime = 30	# time to keep the connection open after a tag read (in case there is another read soon after)
NotifyQueueLimit = 1000		# failed notification messages to queue for later delivery (max=1000)
NotifyRetryPause = 10		# wait 10 seconds between failed notify attempts (time to reconnect the network)
NotifyRetryCount = -1		# no limit on retry attempts (if failure)
NotifyMode = ON				# start notify mode.

Save						# Save everything to flash memory in case of power failure.
'''

extraCmds = '''
Info network
Info time
Info taglist
Info automode
Info notify
'''

# Transform the cmd string into an array of Alien reader commands (strip out comments and blank lines).
initCmds = [f.strip() for f in cmdStr.split('\n')]
initCmds = [f.split('#')[0].strip() for f in cmdStr.split('\n') if f and not f.startswith('#')]

print '\n'.join(initCmds)
del cmdStr

reDateSplit = re.compile( '[/ :]' )		# Characters to split date/time fields.

class Alien( object ):
	CmdPrefix = chr(1)			# Causes Alien reader to suppress prompt on response.
	CmdDelim = '\r\n'			# Delimiter of Alien commands (sent to reader).
	ReaderDelim = '\r\n\0'		# Delimter of Alien reader responses (recieved from reader).

	def __init__( self, dataQ, messageQ, shutdownQ, notifyHost, notifyPort, heartbeatPort ):
		self.notifyHost = notifyHost
		self.notifyPort = notifyPort
		self.heartbeatPort = heartbeatPort
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
			pf.write( 'Tag ID, Discover Time, Antenna, Count\n' )
	
		self.keepGoing = True
		self.cmdHost, self.cmdPort = None, None
		
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
		return response[:-len(self.ReaderDelim)] if response.endswith(self.ReaderDelim) else response
	
	#-------------------------------------------------------------------------
	
	def sendCommands( self ):
		''' Send initialization commands to the Alien reader. '''
		cmdSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		cmdSocket.connect( (self.cmdHost, self.cmdPort) )
		
		cmdContext = {
				'notifyHost':	self.notifyHost,
				'notifyPort':	self.notifyPort,
		}
		
		for i, c in enumerate(initCmds):
			# Set time value if required.
			if '{time}' in c:
				cmdContext['time'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
			
			cmd = c.format( **cmdContext )											# Perform field substitutions.
			self.messageQ.put( ('Alien', cmd) )										# Write to the message queue.
			cmdSocket.sendall( '%s%s%s' % ('' if i < 2 else self.CmdPrefix, cmd, self.CmdDelim) )	# Send to Alien.
			response = self.getResponse( cmdSocket )								# Get the response.
			self.messageQ.put( ('Alien', '>>> %s' % self.stripReaderDelim(response) ) )
			
		cmdSocket.close()
			
	def runServer( self ):
		self.messageQ.put( ('BackupFile', self.fname) )

		while self.checkKeepGoing():
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
			if data:
				while data and data[-1] == '\0':
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
			self.messageQ.put( ('Alien', 'Alien reader found.  Cmd Addr=%s:%d' % (self.cmdHost, self.cmdPort)) )
			self.messageQ.put( ('CmdAddr', '%s:%d' % (self.cmdHost, self.cmdPort)) )

			#---------------------------------------------------------------------------
			# Send initialization commands to the reader.
			#
			self.messageQ.put( ('Alien', 'Sending Alien reader initialization commands...') )
			self.sendCommands()
			
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
					self.messageQ.put( ('Alien', 'Waiting for reader connection...') )
					try:
						readerSocket, addr = dataSocket.accept()
					except socket.timeout:
						continue	# Go back to the top of the loop.  This checks the keepGoing flag.
					readerSocket.settimeout( 1 )
			
				# Get the reader message.
				response = ''
				while not response.endswith( self.ReaderDelim ):
					try:
						more = readerSocket.recv( 4096 )
					except socket.timeout:
						if self.checkKeepGoing():
							continue
						break
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
							tagID = f.firstChild.nodeValue.strip()
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
						tagID = tagID.replace( ' ', '' )
						year, month, day, hour, minute, second = reDateSplit.split(discoveryTime)
						microsecond, second = math.modf( float(second) )
						microsecond *= 1000000
						discoveryTime = datetime.datetime( int(year), int(month), int(day), int(hour), int(minute), int(second), int(microsecond) )
						self.dataQ.put( (tagID, discoveryTime) )
						self.tagCount += 1
						
						# Format as CrossMgr message.
						m = '%016d %s' % (int(tagID), discoveryTime.strftime('%Y/%m/%d_%H:%M:%S.%f'))
						if pf:
							# 									Thu Dec 04 10:14:49 PST
							pf.write( '%s %s %s %s,%s,%s\n' % (
										tagID[0:4], tagID[4-8], tagID[8-12], tagID[12:],
										discoveryTime.strftime('%a %b %d %H:%M:%S.%f %Z %Y'),
										readCount) )
						self.messageQ.put( ('Alien', 'Received %d:' % self.tagCount, m) )
					
					# Close the log file.
					if pf:
						pf.close()
			
			if readerSocket:
				readerSocket.close()
			dataSocket.close()
		
	def purgeDataQ( self ):
		while 1:
			try:
				d = self.dataQ.get( False )
			except Empty:
				break

def AlienServer( dataQ, messageQ, shutdownQ, notifyHost, notifyPort, heartbeatPort ):
	alien = Alien(dataQ, messageQ, shutdownQ, notifyHost, notifyPort, heartbeatPort)
	alien.runServer()
