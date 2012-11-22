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
from multiprocessing import Process, Queue
from Utils import readDelimitedData, timeoutSecs
import cStringIO as StringIO

HOME_DIR = os.path.expanduser("~")

cmdStr = '''
alien
password

set Time = {time}
set TagListMillis = ON
set PersistTime = 2
set HeartbeatTime = 15
	
AutoModeReset
set AutoAction = Acquire
set AutoStopTimer = 0
set AutoTruePause = 0 
set AutoFalsePause = 0
set AutoStartTrigger = 0,0
	
set NotifyAddress = {notifyHost}:{notifyPort}
set NotifyKeepAliveTime = 30
set NotifyHeader = On
set NotifyQueueLimit = 1000
set NotifyInclude = Tags
set NotifyRetryPause = 10
set NotifyRetryCount = -1
set NotifyFormat = XML
set NotifyTrigger = Add

set Function = Reader

set NotifyMode = ON
set AutoMode = ON
'''

extraCmds = '''
Info network
Info time
Info taglist
Info automode
Info notify
'''

initCmds = [f for f in (f.strip() for f in cmdStr.split('\n')) if f]
del cmdStr

reDateSplit = re.compile( '[/ :]' )

class Alien( object ):
	CmdDelim = '\r\n'
	ReaderDelim = '\r\n\0'

	def __init__( self, dataQ, messageQ, shutdownQ, notifyHost, notifyPort, heartbeatPort ):
		self.notifyHost = notifyHost
		self.notifyPort = notifyPort
		self.heartbeatPort = heartbeatPort
		self.dataQ = dataQ
		self.messageQ = messageQ
		self.shutdownQ = shutdownQ
		self.start()
		
	def start( self ):
		tNow = datetime.datetime.now()
		dataDir = os.path.join( HOME_DIR, 'AlienData' )
		if not os.path.isdir( dataDir ):
			os.makedirs( dataDir )
		self.fname = os.path.join( dataDir, tNow.strftime('Alien-%Y-%m-%d-%H-%M-%S.txt') )
	
		self.keepGoing = True
		self.cmdHost, self.cmdPort = None, None
		
		self.alienInfo = None
		self.tagCount = 0
		
	#-------------------------------------------------------------------------
	
	def checkKeepGoing( self ):
		if not self.keepGoing:
			return False
			
		try:
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
		cmdSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		cmdSocket.connect( (self.cmdHost, self.cmdPort) )
		
		cmdContext = {
				'notifyHost':	self.notifyHost,
				'notifyPort':	self.notifyPort,
		}
		
		for c in initCmds:
			cmdContext['time'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
			cmd = c.format( **cmdContext )
			self.messageQ.put( ('Alien', cmd) )
			cmdSocket.sendall( '%s%s' % (cmd, self.CmdDelim) )
			response = self.getResponse( cmdSocket )
			self.messageQ.put( ('Alien', '>>>> %s' % self.stripReaderDelim(response) ) )
			
		'''
		cmdContext['time'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
		bigCmd = self.CmdDelim.join( initCmds ).format( **cmdContext ) + self.CmdDelim
		cmdSocket.sendall( bigCmd )
		'''
		
		cmdSocket.close()
			
	def runServer( self ):
		self.messageQ.put( ('BackupFile', self.fname) )

		while self.checkKeepGoing():
			#---------------------------------------------------------------------------
			# Wait for the heartbeat and the connection info.
			#
			self.messageQ.put( ('Alien', 'Waiting for Alien heartbeat...') )
			heartbeatSocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
			heartbeatSocket.settimeout( 1 )
			heartbeatSocket.bind( (self.notifyHost, self.heartbeatPort) )
			#heartbeatSocket.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

			while self.checkKeepGoing():
				try:
					data, addr = heartbeatSocket.recvfrom( 2048 )
					break
				except socket.timeout:
					time.sleep( 1 )
					
			heartbeatSocket.close()
			
			if not self.keepGoing:
				break
								
			if data:
				while data and data[-1] == '\0':
					data = data[:-1]
			
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
			
			self.alienInfo = info
			self.cmdHost = info['IPAddress']
			self.cmdPort = int(info['CommandPort'])
			self.messageQ.put( ('Alien', 'Alien reader found.  Cmd Addr=%s:%d' % (self.cmdHost, self.cmdPort)) )
			self.messageQ.put( ('CmdAddr', '%s:%d' % (self.cmdHost, self.cmdPort)) )

			#---------------------------------------------------------------------------
			# Send the initialization commands to the reader.
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
							
						tagID = tagID.replace( ' ', '' )
						year, month, day, hour, minute, second = reDateSplit.split(discoveryTime)
						microsecond, second = math.modf( float(second) )
						microsecond *= 1000000
						discoveryTime = datetime.datetime( int(year), int(month), int(day), int(hour), int(minute), int(second), int(microsecond) )
						self.dataQ.put( (tagID, discoveryTime) )
						self.tagCount += 1
						m = '%016d %s' % (int(tagID), discoveryTime.strftime('%Y/%m/%d_%H:%M:%S.%f'))
						if pf:
							pf.write( '%d %s\n' % (self.tagCount, m) )
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
