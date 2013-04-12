import re
import os
import time
import math
import socket
import threading
import datetime
import random
from Queue import Empty
from Utils import readDelimitedData, timeoutSecs
import cStringIO as StringIO
from pyllrp.pyllrp import *

HOME_DIR = os.path.expanduser("~")

RepeatSeconds = 2	# Number of seconds that a tag is considered a repeat read.

class Impinj( object ):
	def __init__( self, dataQ, messageQ, shutdownQ, impinjHost, impinjPort ):
		self.impinjHost = impinjHost
		self.impinjPort = impinjPort
		self.dataQ = dataQ			# Queue to write tag reads.
		self.messageQ = messageQ	# Queue to write operational messages.
		self.shutdownQ = shutdownQ	# Queue to listen for shutdown.
		self.rospecID = 123
		self.readerSocket = None
		self.timeCorrection = None	# Correction between the reader's time and the computer's time.
		self.start()
		
	def start( self ):
		# Create a log file name.
		tNow = datetime.datetime.now()
		dataDir = os.path.join( HOME_DIR, 'ImpinjData' )
		if not os.path.isdir( dataDir ):
			os.makedirs( dataDir )
		self.fname = os.path.join( dataDir, tNow.strftime('Impinj-%Y-%m-%d-%H-%M-%S.txt') )
		with open(self.fname, 'w') as pf:
			pf.write( 'Tag ID, Discover Time, Count\n' )
	
		self.keepGoing = True
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
			
	#-------------------------------------------------------------------------
	
	def sendCommand( self, message ):
		self.messageQ.put( ('Impinj', '-----------------------------------------------------') )
		self.messageQ.put( ('Impinj', 'Sending Message:\n%s\n' % message) )
		message.send( self.readerSocket )
			
		success = True
		response = WaitForMessage( message.MessageID, GetResponseClass(message), self.readerSocket )
			
		self.messageQ.put( ('Impinj', 'Received Response:\n%s\n' % response) )
		return success, response
		
	def sendCommands( self ):
		self.messageQ.put( ('Impinj', 'Connected to: (%s:%d)' % (self.impinjHost, self.impinjPort) ) )
		
		self.messageQ.put( ('Impinj', 'Waiting for READER_EVENT_NOTIFICATION...') )
		response = UnpackMessageFromSocket( self.readerSocket )
		self.messageQ.put( ('Impinj', '\nReceived Response:\n%s\n' % response) )
		
		# Compute a correction between the reader's time and the computer's time.
		readerTime = response.getFirstParameterByClass(UTCTimestamp_Parameter).Microseconds
		readerTime = datetime.datetime.utcfromtimestamp( readerTime / 1000000.0 )
		self.timeCorrection = datetime.datetime.now() - readerTime
		
		self.messageQ.put( ('Impinj', '\nReader time is %f seconds different from computer time\n' % self.timeCorrection.total_seconds()) )
		
		# Reset to factory defaults.
		success, response = self.sendCommand( SET_READER_CONFIG_Message(ResetToFactoryDefault = True) )
		if not success:
			return False
		
		# Disable all rospecs in the reader.
		success, response = self.sendCommand( DISABLE_ROSPEC_Message(ROSpecID = 0) )
		if not success:
			return False
		
		# Delete our old rospec.
		success, response = self.sendCommand( DELETE_ROSPEC_Message(ROSpecID = self.rospecID) )
		if not success:
			return False
		
		# Configure our new rospec.
		success, response = self.sendCommand( GetBasicAddRospecMessage(ROSpecID = self.rospecID) )
		if not success:
			return False
		
		# Enable our new rospec.
		success, response = self.sendCommand( ENABLE_ROSPEC_Message(ROSpecID = self.rospecID) )
		if not success:
			return False
		
		success = (success and isinstance(response, ENABLE_ROSPEC_RESPONSE_Message) and response.success())
		return success
			
	def runServer( self ):
		self.messageQ.put( ('BackupFile', self.fname) )
		
		lastReadTime = {} 
		# Create an old default time.
		tOld = datetime.datetime.now() - datetime.timedelta( days = 100 )
		
		self.readerSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.readerSocket.settimeout( 5 )
		try:
			self.readerSocket.connect( (self.impinjHost, self.impinjPort) )
		except Exception as inst:
			self.messageQ.put( ('Impinj', 'Reader Connection Failed: (%s:%d)' % (self.impinjHost, self.impinjPort) ) )
			self.messageQ.put( ('Impinj', '%s' % inst ) )
			self.messageQ.put( ('Impinj', 'Check that the Reader is turned on and connected, and press Reset.') )
			self.readerSocket.close()
			return False

		if not self.sendCommands():
			self.messageQ.put( ('Impinj', 'Reader Connection Failed: (%s:%d)' % (self.impinjHost, self.impinjPort) ) )
			self.messageQ.put( ('Impinj', 'Check the Reader and press Reset.') )
			self.readerSocket.close()
			return False
		
		tUpdateLast = datetime.datetime.now()
		self.tagCount = 0
		while self.checkKeepGoing():
			
			try:
				response = UnpackMessageFromSocket( self.readerSocket )
			except socket.timeout:
				t = datetime.datetime.now()
				if (t - tUpdateLast).total_seconds() >= 5:
					self.messageQ.put( ('Impinj', 'Listening for Impinj reader data on (%s:%s)...' % (str(self.impinjHost), str(self.impinjPort))) )
					tUpdateLast = t
				continue
			
			if not isinstance(response, RO_ACCESS_REPORT_Message):
				continue
										
			# Open the log file.
			try:
				pf = open( self.fname, 'a' )
			except:
				pf = None
			
			for tag in response.getTagData():
				tagID = HexFormatToInt( tag['EPC'] )
				
				discoveryTime = tag['Timestamp']		# In microseconds since Jan 1, 1970
				readCount = tag['TagSeenCount']
				
				# Convert discoveryTime to Python format and correct for reader time difference.
				discoveryTime = datetime.datetime.utcfromtimestamp( discoveryTime / 1000000.0 ) + self.timeCorrection
				
				self.tagCount += 1
						
				# Convert tag and discovery Time
				discoveryTimeStr = discoveryTime.strftime('%Y/%m/%d_%H:%M:%S.%f')
				
				# Check if this read happend too soon after another read.
				LRT = lastReadTime.get( tagID, tOld )
				lastReadTime[tagID] = discoveryTime
				if (discoveryTime - LRT).total_seconds() < RepeatSeconds:
					self.messageQ.put( (
						'Impinj',
						'Received %d.  tag=%d Skipped (<%d secs ago).  time=%s' % (self.tagCount, tagID, RepeatSeconds, discoveryTimeStr)) )
					continue
				
				# Put this read on the queue for transmission to CrossMgr.
				self.dataQ.put( (tagID, discoveryTime) )

				# Write the entry to the log.
				if pf:
					# 									Thu Dec 04 10:14:49 PST
					pf.write( '%d,%s,%s\n' % (
								tagID,
								discoveryTime.strftime('%a %b %d %H:%M:%S.%f %Z %Y'),
								readCount) )
				self.messageQ.put( ('Impinj', 'Received %d. tag=%d, time=%s' % (self.tagCount, tagID, discoveryTimeStr)) )
			
			# Close the log file.
			if pf:
				pf.close()
			
		if self.readerSocket:
			try:
				response = self.sendCommand( CLOSE_CONNECTION_Message() )
			except socket.timeout:
				pass
			self.readerSocket.close()
			self.readerSocket = None
		return True
		
	def purgeDataQ( self ):
		while 1:
			try:
				d = self.dataQ.get( False )
			except Empty:
				break

def ImpinjServer( dataQ, messageQ, shutdownQ, impinjHost, impinjPort ):
	impinj = Impinj(dataQ, messageQ, shutdownQ, impinjHost, impinjPort)
	impinj.runServer()
