#!/usr/bin/env python
import os
import sys
import time
import socket
import datetime

# If we are running from the development folder, change to a local search path.
if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == 'pyllrp':
	from pyllrp import *
	from LLRPConnection import LLRPConnection
else:
	from pyllrp.pyllrp import *
	from pyllrp.LLRPConnection import LLRPConnection

class TagInventory( object ):
	rospecID = 123					# Arbitrary rospecID.
	inventoryParameterSpecID = 1234	# Arbitrary inventory parameter spec id.

	def __init__( self, host = '192.168.10.102' ):
		self.host = host
		self.timeCorrection = None
		self.conn = None
		self.tagInventory = set()

	def AccessReportHandler( self, accessReport ):
		for tag in accessReport.getTagData():
			tagID = HexFormatToStr( tag['EPC'] )
			discoveryTime = tag['Timestamp']		# In microseconds since Jan 1, 1970
			discoveryTime = datetime.datetime.utcfromtimestamp( discoveryTime / 1000000.0 ) + self.timeCorrection
			print tagID, discoveryTime
			self.tagInventory.add( tagID )

	def DefaultHandler( self, message ):
		print 'Unknown Message:'
		print message

	def Connect( self ):
		# Create the reader connection.
		self.conn = LLRPConnection()

		# Add a callback so we can record the tag reads.
		self.conn.addHandler( RO_ACCESS_REPORT_Message, self.AccessReportHandler )

		# Add a default callback so we can see what else comes from the reader.
		self.conn.addHandler( 'default', self.DefaultHandler )

		# Connect to the reader.
		try:
			response = self.conn.connect( self.host )
		except socket.timeout:
			print '**** Connect timed out.  Check reader hostname and connection. ****'
			raise
		print response

		# Compute a correction between the reader's time and the computer's time.
		readerTime = response.getFirstParameterByClass(UTCTimestamp_Parameter).Microseconds
		readerTime = datetime.datetime.utcfromtimestamp( readerTime / 1000000.0 )
		self.timeCorrection = datetime.datetime.now() - readerTime
		print 'Reader timestamp is:', readerTime
		print self.timeCorrection, self.timeCorrection.total_seconds()

		# Disable all the rospecs.  This command may fail so we ignore the response.
		response = self.conn.transact( DISABLE_ROSPEC_Message(ROSpecID = 0) )

		# Delete our old rospec if it exists.  This command might fail so we ignore the return.
		response = self.conn.transact( DELETE_ROSPEC_Message(ROSpecID = self.rospecID) )
		#print response
		
	def Disconnect( self ):
		print 'Shutting down the connection...'
		response = self.conn.disconnect()
		print response
		self.conn = None

	def SetROSpec( self ):
		# Create an rospec that reports reads.
		response = self.conn.transact(
			ADD_ROSPEC_Message( Parameters = [
				ROSpec_Parameter(
					ROSpecID = self.rospecID,
					CurrentState = ROSpecState.Disabled,
					Parameters = [
						ROBoundarySpec_Parameter(		# Configure boundary spec (start and stop triggers for the reader).
							Parameters = [
								ROSpecStartTrigger_Parameter(ROSpecStartTriggerType = ROSpecStartTriggerType.Immediate),
								ROSpecStopTrigger_Parameter(
									ROSpecStopTriggerType = ROSpecStopTriggerType.Duration,
									DurationTriggerValue = 500
								),
							]
						), # ROBoundarySpec
						AISpec_Parameter(				# Antenna Inventory Spec (specifies which antennas and protocol to use)
							AntennaIDs = [0],			# Use all antennas.
							Parameters = [
								AISpecStopTrigger_Parameter( AISpecStopTriggerType = AISpecStopTriggerType.Null ),
								InventoryParameterSpec_Parameter(
									InventoryParameterSpecID = self.inventoryParameterSpecID,
									ProtocolID = AirProtocols.EPCGlobalClass1Gen2,
								),
							]
						), # AISpec
						ROReportSpec_Parameter(			# Report spec (specified how often and what to send from the reader)
							ROReportTrigger = ROReportTriggerType.Upon_N_Tags_Or_End_Of_ROSpec,
							N = 100,
							Parameters = [
								TagReportContentSelector_Parameter(
									EnableAntennaID = True,
									EnableFirstSeenTimestamp = True,
								),
							]
						), # ROReportSpec
					]
				), # ROSpec_Parameter
			])	# ADD_ROSPEC_Message
		)
		#print response
		assert response.success()

	def GetTagInventory( self ):
		# Enable our ROSpec
		response = self.conn.transact( ENABLE_ROSPEC_Message(ROSpecID = self.rospecID) )
		assert response.success()

		self.tagInventory = set()
		
		# Start thread to listen to the reader for a while.
		print 'Listen to the connection...'
		self.conn.startListener()
		time.sleep( 0.6 )			# Wait for some reads.
		self.conn.stopListener()
		
		response = self.conn.transact( DISABLE_ROSPEC_Message(ROSpecID = self.rospecID) )
		assert response.success()
		
		return self.tagInventory

if __name__ == '__main__':
	'''Read a tag inventory from the reader and shutdown.'''
	host = '192.168.10.102'
	ti = TagInventory( host )
	ti.Connect()
	ti.SetROSpec()
	tagInventory = ti.GetTagInventory()
	for t in tagInventory:
		print t
	ti.Disconnect()