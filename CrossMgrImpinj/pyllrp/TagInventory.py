#!/usr/bin/env python
import os
import sys
import time
import socket
import datetime
from pyllrp import *
from LLRPConnector import LLRPConnector

class TagInventory( object ):
	roSpecID = 123					# Arbitrary roSpecID.
	inventoryParameterSpecID = 1234	# Arbitrary inventory parameter spec id.
	readWaitMilliseconds = 100

	def __init__( self, host = '192.168.10.102', defaultAntennas = None, transmitPower = None ):
		self.host = host
		self.connector = None
		self.resetTagInventory()
		self.defaultAntennas = defaultAntennas
		self.transmitPower = transmitPower
		
	def resetTagInventory( self ):
		self.tagInventory = set()
		self.otherMessages = []

	def AccessReportHandler( self, connector, accessReport ):
		for tag in accessReport.getTagData():
			tagID = HexFormatToStr( tag['EPC'] )
			discoveryTime = self.connector.tagTimeToComputerTime( tag['Timestamp'] )
			self.tagInventory.add( tagID )

	def DefaultHandler( self, connector, message ):
		self.otherMessages.append( message )

	def Connect( self ):
		# Create the reader connection.
		self.connector = LLRPConnector()

		# Connect to the reader.
		try:
			response = self.connector.connect( self.host )
		except socket.timeout:
			raise
			
		# Reset to factory defaults.
		response = self.connector.transact( SET_READER_CONFIG_Message(ResetToFactoryDefault = True) )
		assert response.success(), 'SET_READER_CONFIG ResetToFactorDefault fails\n{}'.format(response)

		transmitPowerParameter = []
		
		# Change transmit power (if specified).  This value is RFID reader dependent.
		if self.transmitPower is not None:
			transmitPowerParameter.append(
				RFTransmitter_Parameter( 
					HopTableID = 1,
					ChannelIndex = 0,
					TransmitPower = self.transmitPower,
				)
			)
		
		message = SET_READER_CONFIG_Message( Parameters = [
				AntennaConfiguration_Parameter( AntennaID = 0, Parameters =
					transmitPowerParameter + [
					C1G2InventoryCommand_Parameter( Parameters = [
						C1G2SingulationControl_Parameter(
							Session = 0,
							TagPopulation = 100,
							TagTransitTime = 3000,
						),
					] ),
				] ),
			] )
		
		response = self.connector.transact( message )
		assert response.success(), 'SET_READER_CONFIG Configuration fails:\n{}'.format(response)
		
	def Disconnect( self ):
		response = self.connector.disconnect()
		self.connector = None

	def GetROSpec( self, antennas = None ):
		if antennas is not None:
			if isinstance(antennas, (int, long)):
				antennas = [antennas]
		else:
			antennas = [0]
	
		# Create an rospec that reports reads.
		return ADD_ROSPEC_Message( Parameters = [
				ROSpec_Parameter(
					ROSpecID = self.roSpecID,
					CurrentState = ROSpecState.Disabled,
					Parameters = [
						ROBoundarySpec_Parameter(		# Configure boundary spec (start and stop triggers for the reader).
							Parameters = [
								ROSpecStartTrigger_Parameter(ROSpecStartTriggerType = ROSpecStartTriggerType.Immediate),
								ROSpecStopTrigger_Parameter(ROSpecStopTriggerType = ROSpecStopTriggerType.Null),
							]
						), # ROBoundarySpec
						AISpec_Parameter(				# Antenna Inventory Spec (specifies which antennas and protocol to use)
							AntennaIDs = antennas,
							Parameters = [
								AISpecStopTrigger_Parameter(
									AISpecStopTriggerType = AISpecStopTriggerType.Tag_Observation,
									Parameters = [
										TagObservationTrigger_Parameter(
											TriggerType = TagObservationTriggerType.N_Attempts_To_See_All_Tags_In_FOV_Or_Timeout,
											NumberOfAttempts = 10,
											Timeout = self.readWaitMilliseconds,
										),
									]
								),
								InventoryParameterSpec_Parameter(
									InventoryParameterSpecID = self.inventoryParameterSpecID,
									ProtocolID = AirProtocols.EPCGlobalClass1Gen2,
								),
							]
						), # AISpec
						ROReportSpec_Parameter(			# Report spec (specifies how often and what to send from the reader)
							ROReportTrigger = ROReportTriggerType.Upon_N_Tags_Or_End_Of_ROSpec,
							N = 10000,
							Parameters = [
								TagReportContentSelector_Parameter(
									EnableAntennaID = True,
									EnableFirstSeenTimestamp = True,
								),
							]
						), # ROReportSpec
					]
				), # ROSpec_Parameter
			]
		)	# ADD_ROSPEC_Message

	def _prolog( self, antennas = None ):
		# Disable all the rospecs.  This command may fail so we ignore the response.
		response = self.connector.transact( DISABLE_ROSPEC_Message(ROSpecID = 0) )
		# Delete our old rospec if it exists.  This command might fail so we ignore the response.
		response = self.connector.transact( DELETE_ROSPEC_Message(ROSpecID = self.roSpecID) )

		# Add callbacks so we can record the tag reads and any other messages from the reader.
		self.resetTagInventory()
		self.connector.addHandler( RO_ACCESS_REPORT_Message, self.AccessReportHandler )
		self.connector.addHandler( 'default', self.DefaultHandler )

		# Add and enable our ROSpec
		response = self.connector.transact( self.GetROSpec(antennas) )
		assert response.success(), 'Add ROSpec Fails\n{}'.format(response)
		
	def _execute( self ):
		response = self.connector.transact( ENABLE_ROSPEC_Message(ROSpecID = self.roSpecID) )
		assert response.success(), 'Enable ROSpec Fails\n{}'.format(response)
		
		# Wait for the reader to do its work.
		time.sleep( (1.5*self.readWaitMilliseconds) / 1000.0 )
		
		response = self.connector.transact( DISABLE_ROSPEC_Message(ROSpecID = self.roSpecID) )
		assert response.success(), 'Disable ROSpec Fails\n{}'.format(response)
		
	def _epilog( self ):
		# Cleanup.
		response = self.connector.transact( DELETE_ROSPEC_Message(ROSpecID = self.roSpecID) )
		assert response.success(), 'Delete ROSpec Fails\n{}'.format(response)
		self.connector.removeAllHandlers()
		
	def GetTagInventory( self, antennas = None ):
		self._prolog( antennas if antennas is not None else self.defaultAntennas )
		self._execute()
		self._epilog()
		return self.tagInventory, self.otherMessages

if __name__ == '__main__':
	'''Read a tag inventory from the reader and shutdown.'''
	host = '192.168.10.101'
	ti = TagInventory( host )
	ti.Connect()
	tagInventory, otherMessages = ti.GetTagInventory()
	print '\n'.join( tagInventory )
	ti.Disconnect()
	
	for p in xrange(1, 100, 10):
		ti = TagInventory( host, transmitPower = p )
		ti.Connect()
		tagInventory, otherMessages = ti.GetTagInventory()
		print '\n'.join( tagInventory )
		ti.Disconnect()
