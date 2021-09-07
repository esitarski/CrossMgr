import re
import os
import time
import math
import socket
import threading
import datetime
import random
import traceback
from collections import defaultdict
from six.moves.queue import Queue, Empty
from Utils import readDelimitedData, timeoutSecs, Bell

try:
	from pyllrp.pyllrp import *
except ImportError:
	from pyllrp import *
from TagGroup import TagGroup, QuadraticRegressionMethod, StrongestReadMethod, FirstReadMethod, MostReadsChoice, DBMaxChoice

getTimeNow = datetime.datetime.now
tOld = getTimeNow() - datetime.timedelta( days=200 )

HOME_DIR = os.path.expanduser("~")

ConnectionTimeoutSecondsDefault	= 3		# Interval for connection timeout
KeepaliveSecondsDefault			= 2		# Interval to request a Keepalive message
RepeatSecondsDefault			= 3		# Interval in which a tag is considered a repeat read.
ProcessingMethodDefault 		= QuadraticRegressionMethod
AntennaChoiceDefault			= MostReadsChoice
RemoveOutliersDefault           = True

ConnectionTimeoutSeconds	= ConnectionTimeoutSecondsDefault
KeepaliveSeconds			= KeepaliveSecondsDefault
RepeatSeconds				= RepeatSecondsDefault

ReconnectDelaySeconds		= 2		# Interval to wait before reattempting a connection
ReaderUpdateMessageSeconds	= 5		# Interval to print we are waiting for input.

TagPopulation = None		# Size of a group to read.
TagPopulationDefault = 4

ReceiverSensitivity = None
TransmitPower = None
	
InventorySession = 2		# LLRP inventory session.
TagTransitTime = None		# Time (seconds) expected for tag to cross read field.  Default=3

ProcessingMethod = ProcessingMethodDefault
AntennaChoice    = AntennaChoiceDefault
RemoveOutliers   = RemoveOutliersDefault

#------------------------------------------------------

ImpinjDebug = False
def GetAddRospecRSSIMessage( MessageID = None, ROSpecID = 123, inventoryParameterSpecID = 1234,
		antennas = None, modeIdentifiers = None, maxNumberOfAntennaSupported = None,
	):
	#-----------------------------------------------------------------------------
	# Create a read everything Operation Spec message
	#
	if not antennas:	# Default to all antennas if unspecified.
		antennas = [0]
	
	if maxNumberOfAntennaSupported:
		antennas = [a for a in antennas if a <= maxNumberOfAntennaSupported]
	
	if not modeIdentifiers:	# Default to ModeIndex=1000 as this is common.
		modeIdentifiers = [1000]
	
	# Pick a mode index from those available in the reader.
	for modeIndex in (0,1000):
		if modeIndex in modeIdentifiers:
			break
	else:
		modeIndex = modeIdentifiers[0]	# If we can't find the ones we are looking for, pick a valid one.
	
	rospecMessage = ADD_ROSPEC_Message( MessageID = MessageID, Parameters = [
		# Initialize to disabled.
		ROSpec_Parameter(
			ROSpecID = ROSpecID,
			CurrentState = ROSpecState.Disabled,
			Parameters = [
				ROBoundarySpec_Parameter(		# Configure boundary spec (start and stop triggers for the reader).
					Parameters = [
						# Start immediately.
						ROSpecStartTrigger_Parameter(ROSpecStartTriggerType = ROSpecStartTriggerType.Immediate),
						# No stop trigger.
						ROSpecStopTrigger_Parameter(ROSpecStopTriggerType = ROSpecStopTriggerType.Null),
					]
				),
				
				AISpec_Parameter(				# Antenna Inventory Spec (specifies which antennas and protocol to use).
					AntennaIDs = antennas,		# Use specified antennas.
					Parameters = [
						AISpecStopTrigger_Parameter(
							AISpecStopTriggerType = AISpecStopTriggerType.Null,
						),
						InventoryParameterSpec_Parameter(
							InventoryParameterSpecID = inventoryParameterSpecID,
							ProtocolID = AirProtocols.EPCGlobalClass1Gen2,
							Parameters = [
								AntennaConfiguration_Parameter(
									AntennaID = 0,	# All antennas
									Parameters = [
										C1G2InventoryCommand_Parameter(
											TagInventoryStateAware = False,
											Parameters = [
												C1G2RFControl_Parameter(
													ModeIndex = modeIndex,
													Tari = 0,
												),
												C1G2SingulationControl_Parameter(
													Session = 2,
													TagPopulation = 32,
													TagTransitTime = 0,
												)
											],
										),
									],
								),
							],
						),
					]
				),
				
				ROReportSpec_Parameter(			# Report spec (specifies what to send from the reader).
					ROReportTrigger = ROReportTriggerType.Upon_N_Tags_Or_End_Of_ROSpec,
					N = 1,
					Parameters = [
						TagReportContentSelector_Parameter(
							EnableAntennaID = True,
							EnableFirstSeenTimestamp = True,
							EnablePeakRSSI = True,
						),
					]
				),
			]
		)	# ROSpec_Parameter
	])	# ADD_ROSPEC_Message
	return rospecMessage
	
class Impinj:

	def __init__( self, dataQ, strayQ, messageQ, shutdownQ, impinjHost, impinjPort, antennaStr, statusCB ):
		self.impinjHost = impinjHost
		self.impinjPort = impinjPort
		self.statusCB = statusCB
		if not antennaStr:
			self.antennas = [0]
		else:
			self.antennas = [int(a) for a in antennaStr.split()]
		self.tagGroup = None
		self.tagGroupTimer = None
		self.dataQ = dataQ			# Queue to write tag reads.
		self.strayQ = strayQ		# Queue to write stray reads.
		self.messageQ = messageQ	# Queue to write operational messages.
		self.shutdownQ = shutdownQ	# Queue to listen for shutdown.
		self.logQ = Queue()
		self.rospecID = 123
		self.readerSocket = None
		self.timeCorrection = None	# Correction between the reader's time and the computer's time.
		self.connectedAntennas = []
		self.antennaReadCount = defaultdict(int)
		self.lastReadTime = {}
		self.start()
		
	def start( self ):
		# Create a log file name.
		tNow = getTimeNow()
		dataDir = os.path.join( HOME_DIR, 'ImpinjData' )
		if not os.path.isdir( dataDir ):
			os.makedirs( dataDir )
		self.fname = os.path.join( dataDir, tNow.strftime('Impinj-%Y-%m-%d-%H-%M-%S.txt') )
		
		# Create a log queue and start a thread to write the log.
		self.logQ.put( 'msg', 'Tag ID,Discover Time' )
		self.logFileThread = threading.Thread( target=self.handleLogFile )
		self.logFileThread.daemon = True
		self.logFileThread.start()
	
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
		self.messageQ.put( ('Impinj', 'Sending Message:\n{}\n'.format(message)) )
		try:
			message.send( self.readerSocket )
		except Exception as e:
			self.messageQ.put( ('Impinj', 'Send command fails: {}'.format(e)) )
			return False
			
		try:
			response = WaitForMessage( message.MessageID, self.readerSocket )
		except Exception as e:
			self.messageQ.put( ('Impinj', 'Get response fails: {}'.format(e)) )
			return False
			
		self.messageQ.put( ('Impinj', 'Received Response:\n{}\n'.format(response)) )
		return True, response
		
	def sendCommands( self ):
		self.connectedAntennas = []
		self.antennaReadCount = defaultdict(int)
		
		self.messageQ.put( ('Impinj', 'Connected to: ({}:{})'.format(self.impinjHost, self.impinjPort) ) )
		
		self.messageQ.put( ('Impinj', 'Waiting for READER_EVENT_NOTIFICATION...') )
		response = UnpackMessageFromSocket( self.readerSocket )
		self.messageQ.put( ('Impinj', '\nReceived Response:\n{}\n'.format(response)) )
		
		# Compute a correction between the reader's time and the computer's time.
		readerTime = response.getFirstParameterByClass(UTCTimestamp_Parameter).Microseconds
		readerTime = datetime.datetime.utcfromtimestamp( readerTime / 1000000.0 )
		self.timeCorrection = getTimeNow() - readerTime
		
		self.messageQ.put( ('Impinj', '\nReader time is {} seconds different from computer time\n'.format(self.timeCorrection.total_seconds())) )
		
		# Reset to factory defaults.
		success, response = self.sendCommand( SET_READER_CONFIG_Message(ResetToFactoryDefault = True) )
		if not success:
			return False
			
		# Get the connected antennas.
		self.getConnectedAntennas()
		
		# Configure a periodic Keepalive message.
		# Change receiver sensitivity (if specified).  This value is reader dependent.
		receiverSensitivityParameter = []
		if ReceiverSensitivity is not None:
			receiverSensitivityParameter.append(
				RFReceiver_Parameter( 
					ReceiverSensitivity = ReceiverSensitivity
				)
			)
		
		# Change transmit power (if specified).  This value is reader dependent.
		transmitPowerParameter = []
		if TransmitPower is not None:
			transmitPowerParameter.append(
				RFTransmitter_Parameter( 
					HopTableID = 1,
					ChannelIndex = 0,
					TransmitPower = TransmitPower,
				)
			)
		
		# Change Inventory Control (if specified).
		inventoryCommandParameter = []
		if any(v is not None for v in [InventorySession, TagPopulation, TagTransitTime]):
			inventoryCommandParameter.append(
				C1G2InventoryCommand_Parameter( Parameters = [
						C1G2SingulationControl_Parameter(
							Session = InventorySession or 0,
							TagPopulation = TagPopulation or TagPopulationDefault,
							TagTransitTime = (TagTransitTime or 3)*1000,
						),
					],
				)
			)
		
		success, response = self.sendCommand(
			SET_READER_CONFIG_Message( Parameters = [
					AntennaConfiguration_Parameter(
						AntennaID = 0,
						Parameters = receiverSensitivityParameter + transmitPowerParameter + inventoryCommandParameter,
					),
					KeepaliveSpec_Parameter(
						KeepaliveTriggerType = KeepaliveTriggerType.Periodic,
						PeriodicTriggerValue = int(KeepaliveSeconds*1000),
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
			
		# Get the C1G2UHFRFModeTable and extract available mode identifiers.
		modeIdentifiers = None
		maxNumberOfAntennaSupported = 4
		try:
			success, response = self.sendCommand(GET_READER_CAPABILITIES_Message(RequestedData = GetReaderCapabilitiesRequestedData.All))
			if success:
				modeIdentifiers = [e.ModeIdentifier for e in response.getFirstParameterByClass(C1G2UHFRFModeTable_Parameter).Parameters]
				gdc = response.getFirstParameterByClass(GeneralDeviceCapabilities_Parameter)
				maxNumberOfAntennaSupported = gdc.MaxNumberOfAntennaSupported
			else:
				self.messageQ.put( ('Impinj', 'GET_READER_CAPABILITIES fails.') )
		except Exception as e:
			self.messageQ.put( ('Impinj', 'GET_READER_CAPABILITIES Exception: {}:\n{}'.format(e, traceback.format_exc())) )
				
		# Configure our new rospec.
		if ProcessingMethod == FirstReadMethod:
			cmd = GetBasicAddRospecMessage(ROSpecID = self.rospecID, antennas = self.antennas)
		else:
			cmd = GetAddRospecRSSIMessage(
				ROSpecID = self.rospecID, antennas = self.antennas,
				modeIdentifiers=modeIdentifiers, maxNumberOfAntennaSupported=maxNumberOfAntennaSupported
			)
		success, response = self.sendCommand(cmd)
		if not success:
			return False
			
		# Enable our new rospec.
		success, response = self.sendCommand( ENABLE_ROSPEC_Message(ROSpecID = self.rospecID) )
		if not success:
			return False
		
		success = (success and isinstance(response, ENABLE_ROSPEC_RESPONSE_Message) and response.success())
		return success
	
	def getConnectedAntennas( self ):
		success, response = self.sendCommand( GET_READER_CONFIG_Message(RequestedData=GetReaderConfigRequestedData.AntennaProperties) )
		if success:
			self.connectedAntennas = [p.AntennaID for p in response.Parameters
				if isinstance(p, AntennaProperties_Parameter) and p.AntennaConnected and p.AntennaID <= 4]
		return success
		
	def reportTag( self, tagID, discoveryTime, sampleSize=1, antennaID=0, quadReg=False ):
		lrt = self.lastReadTime.get(tagID, tOld)
		if discoveryTime > lrt:
			self.lastReadTime[tagID] = discoveryTime
		
		if (discoveryTime - lrt).total_seconds() < RepeatSeconds:
			self.messageQ.put( (
				'Impinj',
				'Received {}.  tag={} Skipped (<{} secs ago).  {}'.format(self.tagCount, tagID, RepeatSeconds,
				discoveryTime.strftime('%H:%M:%S.%f')),
				self.antennaReadCount,
				)
			)
			return False
			
		self.dataQ.put( (tagID, discoveryTime) )
		
		self.logQ.put( (
				'log',
				'{},{}'.format(
					tagID,
					discoveryTime.strftime('%a %b %d %H:%M:%S.%f %Z %Y-%m-%d'),
				)
			)
		)
		
		self.messageQ.put( (
			'Impinj',
			'{} {}. {} - {}{}{}'.format(
					'QuadReg' if quadReg else 'FirstRead',
					self.tagCount,
					tagID,
					discoveryTime.strftime('%H:%M:%S.%f'),
					' samples={}'.format(sampleSize) if sampleSize > 1 else '',
					' antennaID={}'.format(antennaID) if antennaID else '',
			),
			self.antennaReadCount,
			)
		)
		Bell()
		return True
	
	def handleTagGroup( self ):
		if not self.tagGroup:
			return
		reads, strays = self.tagGroup.getReadsStrays( method=ProcessingMethod, antennaChoice=AntennaChoice )
		for tagID, discoveryTime, sampleSize, antennaID in reads:
			self.reportTag( tagID, discoveryTime, sampleSize, antennaID, True )
			
		self.strayQ.put( ('strays', strays) )
		self.tagGroupTimer = threading.Timer( 1.0, self.handleTagGroup )
		self.tagGroupTimer.start()
	
	def handleLogFile( self ):
		while True:
			msg = self.logQ.get()
			self.logQ.task_done()
			
			if msg[0] == 'shutdown':
				return
			try:
				pf = open( self.fname, 'a' )
			except Exception:
				continue
			
			pf.write( msg[1] if msg[1].endswith('\n') else msg[1] + '\n' )
			while True:
				try:
					msg = self.logQ.get( False )
				except Empty:
					break
				self.logQ.task_done()
				
				if msg[0] == 'shutdown':
					return
				pf.write( msg[1] if msg[1].endswith('\n') else msg[1] + '\n' )
			pf.close()
			time.sleep( 0.1 )
	
	def runServer( self ):
		self.messageQ.put( ('BackupFile', self.fname) )
		
		self.messageQ.put( ('Impinj', '*****************************************' ) )
		self.messageQ.put( ('Impinj', 'Reader Server Started: ({}:{})'.format(self.impinjHost, self.impinjPort) ) )
			
		# Create an old default time for last tag read.
		tOld = getTimeNow() - datetime.timedelta( days = 100 )
		utcfromtimestamp = datetime.datetime.utcfromtimestamp
		
		while self.checkKeepGoing():
			self.readerSocket = None	# Voodoo to ensure that the socket is reset properly.
			
			#------------------------------------------------------------
			# Connect Mode.
			#
			# Create a socket to connect to the reader.
			self.readerSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self.readerSocket.settimeout( ConnectionTimeoutSeconds )
			
			self.messageQ.put( ('Impinj', 'state', False) )
			self.messageQ.put( ('Impinj', '') )
			self.messageQ.put( ('Impinj', 'Trying to Connect to Reader: ({}:{})...'.format(self.impinjHost, self.impinjPort) ) )
			self.messageQ.put( ('Impinj', 'ConnectionTimeout={:.2f} seconds'.format(ConnectionTimeoutSeconds) ) )
			
			try:
				self.readerSocket.connect( (self.impinjHost, self.impinjPort) )
			except Exception as e:
				self.messageQ.put( ('Impinj', 'Reader Connection Failed: {}'.format(e) ) )
				self.readerSocket.close()
				self.messageQ.put( ('Impinj', 'Attempting Reconnect in {} seconds...'.format(ReconnectDelaySeconds)) )
				self.reconnectDelay()
				continue

			self.messageQ.put( ('Impinj', 'state', True) )
			
			#------------------------------------------------------------
			# Initialize the reader.
			#
			try:
				success = self.sendCommands()
			except Exception as e:
				self.messageQ.put( ('Impinj', 'Send Command Error={}'.format(e)) )
				success = False
				
			if not success:
				self.messageQ.put( ('Impinj', 'Reader Initialization Failed.') )
				self.messageQ.put( ('Impinj', 'Disconnecting Reader.' ) )
				self.messageQ.put( ('Impinj', 'state', False) )
				self.readerSocket.close()
				self.messageQ.put( ('Impinj', 'Attempting Reconnect in {} seconds...'.format(ReconnectDelaySeconds)) )
				self.reconnectDelay()
				self.statusCB()
				continue
				
			self.statusCB(
				connectedAntennas = self.connectedAntennas,
				timeCorrection = self.timeCorrection,
			)
			
			self.tagGroup = TagGroup()
			self.handleTagGroup()
				
			tUpdateLast = tKeepaliveLast = getTimeNow()
			tAntennaConnectedLast = tUpdateLast - datetime.timedelta( days=1 )	# Force the antenna status to be updated at start.
			self.tagCount = 0
			lastDiscoveryTime = None
			while self.checkKeepGoing():
			
				#------------------------------------------------------------
				# Read Mode.
				#
				
				t = getTimeNow()
					
				#------------------------------------------------------------
				# Check on the antenna connection status.
				#
				if (t - tAntennaConnectedLast).total_seconds() >= 10:
					try:
						GET_READER_CONFIG_Message(RequestedData=GetReaderConfigRequestedData.AntennaProperties).send( self.readerSocket )
						tAntennaConnectedLast = t
					except Exception as e:
						self.messageQ.put( ('Impinj', 'GET_READER_CONFIG send fails: {}'.format(e)) )
						self.readerSocket.close()
						self.messageQ.put( ('Impinj', 'Attempting Reconnect...') )
						break
				
				#------------------------------------------------------------
				# Messages from the reader.
				# Handle connection/timeout errors here.
				#
				try:
					response = UnpackMessageFromSocket( self.readerSocket )
				
				except socket.timeout:
					if (t - tKeepaliveLast).total_seconds() > KeepaliveSeconds * 2:
						self.messageQ.put( ('Impinj', 'Reader Connection Lost (missing Keepalive).') )
						self.readerSocket.close()
						self.messageQ.put( ('Impinj', 'Attempting Reconnect...') )
						break
					
					if (t - tUpdateLast).total_seconds() >= ReaderUpdateMessageSeconds:
						self.messageQ.put( ('Impinj', 'Listening for Impinj reader data...') )
						tUpdateLast = t
					continue
				
				except Exception as e:
					if (t - tKeepaliveLast).total_seconds() > KeepaliveSeconds * 2:
						self.messageQ.put( ('Impinj', 'Reader Connection Lost (Check your network adapter).') )
						self.readerSocket.close()
						self.messageQ.put( ('Impinj', 'Attempting Reconnect...') )
						break
					
					if (t - tUpdateLast).total_seconds() >= ReaderUpdateMessageSeconds:
						self.messageQ.put( ('Impinj', 'Listening for Impinj reader data...') )
						tUpdateLast = t
					continue
				
				#------------------------------------------------------------
				# Keepalive.
				#
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
					
				#------------------------------------------------------------
				# Reader config (to get antenna connection status).
				#
				if isinstance(response, GET_READER_CONFIG_RESPONSE_Message):
					self.connectedAntennas = sorted( p.AntennaID for p in response.Parameters
						if isinstance(p, AntennaProperties_Parameter) and p.AntennaConnected and p.AntennaID <= 4 )
					# self.messageQ.put( ('Impinj', 'Connected antennas: {}'.format(','.join(str(a) for a in self.connectedAntennas)) ) )
					self.statusCB(
						connectedAntennas = self.connectedAntennas,
						timeCorrection = self.timeCorrection,
					)
					continue
				
				#------------------------------------------------------------
				# Unexpected messages.
				#
				if not isinstance(response, RO_ACCESS_REPORT_Message):
					if not isinstance(response, READER_EVENT_NOTIFICATION_Message):
						self.messageQ.put( ('Impinj', 'Skipping: {}'.format(response.__class__.__name__)) )
					continue
				
				#------------------------------------------------------------
				# Tag read.
				#
				try:
					discoveryTime = utcfromtimestamp( tag['Timestamp'] / 1000000.0 )
					if ImpinjDebug and lastDiscoveryTime is not None:
						print( '{}            \r'.format( (discoveryTime - lastDiscoveryTime).total_seconds() ) )
					lastDiscoveryTime = discoveryTime
				except Exception:
					pass
				
				for tag in response.getTagData():
					self.tagCount += 1
					
					antennaID = tag['AntennaID']
					
					try:
						self.antennaReadCount[antennaID] += 1
					except Exception as e:
						self.messageQ.put( ('Impinj', 'Received {}.  Missing AntennaID.'.format(self.tagCount)) )
					
					try:
						tagID = tag['EPC']
					except Exception as e:
						self.messageQ.put( ('Impinj', 'Received {}.  Skipping: missing tagID.'.format(self.tagCount)) )
						continue
						
					try:
						tagID = HexFormatToStr( tagID )
					except Exception as e:
						self.messageQ.put( ('Impinj', 'Received {}.  Skipping: HexFormatToStr fails.  Error={}'.format(self.tagCount, e)) )
						continue
					
					try:
						discoveryTime = tag['Timestamp']		# In microseconds since Jan 1, 1970
					except Exception as e:
						self.messageQ.put( ('Impinj', 'Received {}.  Skipping: Missing Timestamp'.format(self.tagCount)) )
						continue
					
					peakRSSI = tag.get('PeakRSSI', None)		# -127..127 in db.
					
					# Convert discoveryTime to Python format and correct for reader time difference.
					discoveryTime = utcfromtimestamp( discoveryTime / 1000000.0 ) + self.timeCorrection
					
					if peakRSSI is not None:
						self.tagGroup.add( antennaID, tagID, discoveryTime, peakRSSI )
					else:
						self.reportTag( tagID, discoveryTime, antennaID=antennaID )
		
		# Cleanup.
		if self.readerSocket:
			try:
				response = self.sendCommand( CLOSE_CONNECTION_Message() )
			except socket.timeout:
				pass
			self.readerSocket.close()
			self.readerSocket = None
		
		self.logQ.put( ('shutdown',) )
		self.logFileThread.join()

		if self.tagGroupTimer:
			self.tagGroupTimer.cancel()
		
		return True
		
	def purgeDataQ( self ):
		while True:
			try:
				d = self.dataQ.get( False )
			except Empty:
				break

def ImpinjServer( dataQ, messageQ, strayQ, shutdownQ, impinjHost, impinjPort, antennaStr, statusCB=None ):
	impinj = Impinj(dataQ, messageQ, strayQ, shutdownQ, impinjHost, impinjPort, antennaStr, statusCB)
	impinj.runServer()
