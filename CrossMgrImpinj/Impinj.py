import re
import os
import time
import math
import socket
import threading
import datetime
import random
from Queue import Empty
from Utils import readDelimitedData, timeoutSecs, Bell
import cStringIO as StringIO
try:
	from pyllrp.pyllrp import *
except ImportError:
	from pyllrp import *

getTimeNow = datetime.datetime.now

HOME_DIR = os.path.expanduser("~")

ConnectionTimeoutSecondsDefault	= 3		# Interval for connection timeout
KeepaliveSecondsDefault			= 2		# Interval to request a Keepalive message
RepeatSecondsDefault			= 2		# Interval in which a tag is considered a repeat read.

ConnectionTimeoutSeconds	= ConnectionTimeoutSecondsDefault
KeepaliveSeconds			= KeepaliveSecondsDefault
RepeatSeconds				= RepeatSecondsDefault

ReconnectDelaySeconds		= 2		# Interval to wait before reattempting a connection
ReaderUpdateMessageSeconds	= 5		# Interval to print we are waiting for input.

class Impinj( object ):

	receiverSensitivity = None
	transmitPower = None
	
	inventorySession = 2		# LLRP inventory session.
	tagPopulation = None		# Size of a group to read.  Default=100
	tagTransitTime = None		# Time (milliseconds) expected for tag to cross read field.  Default=3000

	def __init__( self, dataQ, messageQ, shutdownQ, impinjHost, impinjPort, antennaStr ):
		self.impinjHost = impinjHost
		self.impinjPort = impinjPort
		if not antennaStr:
			self.antennas = [0]
		else:
			self.antennas = [int(a) for a in antennaStr.split()]
		self.dataQ = dataQ			# Queue to write tag reads.
		self.messageQ = messageQ	# Queue to write operational messages.
		self.shutdownQ = shutdownQ	# Queue to listen for shutdown.
		self.rospecID = 123
		self.readerSocket = None
		self.timeCorrection = None	# Correction between the reader's time and the computer's time.
		self.start()
		
	def start( self ):
		# Create a log file name.
		tNow = getTimeNow()
		dataDir = os.path.join( HOME_DIR, 'ImpinjData' )
		if not os.path.isdir( dataDir ):
			os.makedirs( dataDir )
		self.fname = os.path.join( dataDir, tNow.strftime('Impinj-%Y-%m-%d-%H-%M-%S.txt') )
		with open(self.fname, 'w') as pf:
			pf.write( 'Tag ID, Discover Time\n' )
	
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
			
			
	def reconnectDelay( self ):
		if self.checkKeepGoing():
			time.sleep( ReconnectDelaySeconds )
		
	#-------------------------------------------------------------------------
	
	def sendCommand( self, message ):
		self.messageQ.put( ('Impinj', '-----------------------------------------------------') )
		self.messageQ.put( ('Impinj', 'Sending Message:\n%s\n' % message) )
		try:
			message.send( self.readerSocket )
		except Exception as e:
			self.messageQ.put( ('Impinj', 'Send command fails: %s' % e) )
			return False
			
		try:
			response = WaitForMessage( message.MessageID, self.readerSocket )
		except Exception as e:
			self.messageQ.put( ('Impinj', 'Get response fails: %s' % e) )
			return False
			
		self.messageQ.put( ('Impinj', 'Received Response:\n%s\n' % response) )
		return True, response
		
	def sendCommands( self ):
		self.messageQ.put( ('Impinj', 'Connected to: (%s:%d)' % (self.impinjHost, self.impinjPort) ) )
		
		self.messageQ.put( ('Impinj', 'Waiting for READER_EVENT_NOTIFICATION...') )
		response = UnpackMessageFromSocket( self.readerSocket )
		self.messageQ.put( ('Impinj', '\nReceived Response:\n%s\n' % response) )
		
		# Compute a correction between the reader's time and the computer's time.
		readerTime = response.getFirstParameterByClass(UTCTimestamp_Parameter).Microseconds
		readerTime = datetime.datetime.utcfromtimestamp( readerTime / 1000000.0 )
		self.timeCorrection = getTimeNow() - readerTime
		
		self.messageQ.put( ('Impinj', '\nReader time is %f seconds different from computer time\n' % self.timeCorrection.total_seconds()) )
		
		# Reset to factory defaults.
		success, response = self.sendCommand( SET_READER_CONFIG_Message(ResetToFactoryDefault = True) )
		if not success:
			return False
		
		# Configure a period Keepalive message.
		if True:
			success, response = self.sendCommand( SET_READER_CONFIG_Message(Parameters = [
					KeepaliveSpec_Parameter(	KeepaliveTriggerType = KeepaliveTriggerType.Periodic,
												PeriodicTriggerValue = int(KeepaliveSeconds*1000)
					),
			] ) )
		else:
			# Change receiver sensitivity (if specified).  This value is RFID reader dependent.
			receiverSensitivityParameter = []
			if self.receiverSensitivity is not None:
				receiverSensitivityParameter.append(
					RFReceiver_Parameter( 
						ReceiverSensitivity = self.receiverSensitivity
					)
				)
			
			# Change transmit power (if specified).  This value is RFID reader dependent.
			transmitPowerParameter = []
			if self.transmitPower is not None:
				transmitPowerParameter.append(
					RFTransmitter_Parameter( 
						HopTableID = 1,
						ChannelIndex = 0,
						TransmitPower = self.transmitPower,
					)
				)
			
			# Change Invnetory Control (if specifield).
			inventoryCommandParameter = []
			if any(v is not None for v in [self.inventorySession, self.tagPopulation, self.tagTransitTime]):
				inventoryCommandParameter.append(
					C1G2InventoryCommand_Parameter( Parameters = [
							C1G2SingulationControl_Parameter(
								Session = self.inventorySession or 0,
								TagPopulation = self.tagPopulation or 100,
								TagTransitTime = self.tagTransitTime or 3000,
							),
						],
					)
				)
			
			success, response = self.sendCommand( SET_READER_CONFIG_Message(Parameters = [
					KeepaliveSpec_Parameter( KeepaliveTriggerType = KeepaliveTriggerType.Periodic, PeriodicTriggerValue = int(KeepaliveSeconds*1000),),
						AntennaConfiguration_Parameter(
							AntennaID = 0,
							Parameters = receiverSensitivityParameter + transmitPowerParameter + inventoryCommandParameter
						),
					],
				),
			)
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
		success, response = self.sendCommand( GetBasicAddRospecMessage(ROSpecID = self.rospecID, antennas = self.antennas) )
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
		
		self.messageQ.put( ('Impinj', '*****************************************' ) )
		self.messageQ.put( ('Impinj', 'Reader Server Started: (%s:%d)' % (self.impinjHost, self.impinjPort) ) )
			
		# Create an old default time for last tag read.
		tOld = getTimeNow() - datetime.timedelta( days = 100 )
		
		while self.checkKeepGoing():
			#------------------------------------------------------------
			# Connect Mode.
			#
			lastReadTime = {}			# Lookup for last tag read times.
			
			# Create a socket to connect to the reader.
			self.readerSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self.readerSocket.settimeout( ConnectionTimeoutSeconds )
			
			self.messageQ.put( ('Impinj', 'state', False) )
			self.messageQ.put( ('Impinj', '') )
			self.messageQ.put( ('Impinj', 'Trying to Connect to Reader: (%s:%d)...' % (self.impinjHost, self.impinjPort) ) )
			self.messageQ.put( ('Impinj', 'ConnectionTimeout={:.2f} seconds'.format(ConnectionTimeoutSeconds) ) )
			
			try:
				self.readerSocket.connect( (self.impinjHost, self.impinjPort) )
			except Exception as e:
				self.messageQ.put( ('Impinj', 'Reader Connection Failed: %s' % e ) )
				self.readerSocket.close()
				self.messageQ.put( ('Impinj', 'Attempting Reconnect in %d seconds...' % ReconnectDelaySeconds) )
				self.reconnectDelay()
				continue

			self.messageQ.put( ('Impinj', 'state', True) )
			
			try:
				success = self.sendCommands()
			except Exception as e:
				self.messageQ.put( ('Impinj', 'Send Command Error=%s' % e) )
				success = False
				
			if not success:
				self.messageQ.put( ('Impinj', 'Reader Initialization Failed.') )
				self.messageQ.put( ('Impinj', 'Disconnecting Reader.' ) )
				self.messageQ.put( ('Impinj', 'state', False) )
				self.readerSocket.close()
				self.messageQ.put( ('Impinj', 'Attempting Reconnect in %d seconds...' % ReconnectDelaySeconds) )
				self.reconnectDelay()
				continue
			
			tUpdateLast = tKeepaliveLast = getTimeNow()
			self.tagCount = 0
			while self.checkKeepGoing():
				#------------------------------------------------------------
				# Read Mode.
				#
				try:
					response = UnpackMessageFromSocket( self.readerSocket )
				except socket.timeout:
					t = getTimeNow()
					
					if (t - tKeepaliveLast).total_seconds() > KeepaliveSeconds * 2:
						self.messageQ.put( ('Impinj', 'Reader Connection Lost (missing Keepalive).') )
						self.readerSocket.close()
						self.messageQ.put( ('Impinj', 'Attempting Reconnect...') )
						break
					
					if (t - tUpdateLast).total_seconds() >= ReaderUpdateMessageSeconds:
						self.messageQ.put( ('Impinj', 'Listening for Impinj reader data...') )
						tUpdateLast = t
					continue
				
				if isinstance(response, KEEPALIVE_Message):
					# Respond to the KEEP_ALIVE message with KEEP_ALIVE_ACK.
					try:
						KEEPALIVE_ACK_Message().send( self.readerSocket )
					except socket.timeout:
						self.messageQ.put( ('Impinj', 'Reader Connection Lost (Keepalive_Ack timeout).') )
						self.readerSocket.close()
						self.messageQ.put( ('Impinj', 'Attempting Reconnect...') )
						break
						
					tKeepaliveLast = getTimeNow()
					continue
				
				if not isinstance(response, RO_ACCESS_REPORT_Message):
					if not isinstance(response, READER_EVENT_NOTIFICATION_Message):
						self.messageQ.put( ('Impinj', 'Skipping: %s' % response.__class__.__name__) )
					continue
				
				Bell()
				
				# Open the log file.
				try:
					pf = open( self.fname, 'a' )
				except:
					pf = None
				
				for tag in response.getTagData():
					self.tagCount += 1
					
					try:
						tagID = tag['EPC']
					except Exception as e:
						self.messageQ.put( ('Impinj', 'Received %d.  Skipping: missing tagID.' % self.tagCount) )
						continue
						
					if isinstance( tagID, (int, long) ):
						tagID = str(tagID)
					else:
						try:
							tagID = HexFormatToStr( tagID )
						except Exception as e:
							self.messageQ.put( ('Impinj', 'Received {}.  Skipping: HexFormatToStr fails.  Error={}'.format(self.tagCount, e)) )
							continue
					
					try:
						discoveryTime = tag['Timestamp']		# In microseconds since Jan 1, 1970
					except Exception as e:
						self.messageQ.put( ('Impinj', 'Received %d.  Skipping: Missing Timestamp' % self.tagCount) )
						continue
						
					# Convert discoveryTime to Python format and correct for reader time difference.
					discoveryTime = datetime.datetime.utcfromtimestamp( discoveryTime / 1000000.0 ) + self.timeCorrection
					
					# Convert tag and discovery Time
					discoveryTimeStr = discoveryTime.strftime('%Y/%m/%d_%H:%M:%S.%f')
					
					# Check if this read happened too soon after another read.
					LRT = lastReadTime.get( tagID, tOld )
					lastReadTime[tagID] = discoveryTime
					if (discoveryTime - LRT).total_seconds() < RepeatSeconds:
						self.messageQ.put( (
							'Impinj',
							'Received {}.  tag={} Skipped (<{} secs ago).  time={}'.format(self.tagCount, tagID, RepeatSeconds, discoveryTimeStr)) )
						continue
					
					# Put this read on the queue for transmission to CrossMgr.
					self.dataQ.put( (tagID, discoveryTime) )

					# Write the entry to the log.
					if pf:
						# 									Thu Dec 04 10:14:49 PST 2014
						pf.write( '{},{}\n'.format(
									tagID,
									discoveryTime.strftime('%a %b %d %H:%M:%S.%f %Z %Y-%m-%d')) )
					self.messageQ.put( ('Impinj', 'Received {}. tag={}, time={}'.format(self.tagCount, tagID, discoveryTimeStr)) )
				
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

def ImpinjServer( dataQ, messageQ, shutdownQ, impinjHost, impinjPort, antennaStr ):
	impinj = Impinj(dataQ, messageQ, shutdownQ, impinjHost, impinjPort, antennaStr)
	impinj.runServer()
