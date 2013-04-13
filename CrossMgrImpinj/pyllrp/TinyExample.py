#!/usr/bin/env python
import sys
import os

# If we are running from the development folder, change to a local search path.
if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == 'pyllrp':
	from pyllrp import *
	from LLRPConnection import LLRPConnection
else:
	from pyllrp.pyllrp import *
	from pyllrp.LLRPConnection import LLRPConnection

import time
import datetime
import socket

# Change to the hostname or IP address of the reader.
host = '192.168.10.102'

timeCorrection = None
def AccessReportHandler( accessReport ):
	for tag in accessReport.getTagData():
		tagID = HexFormatToInt( tag['EPC'] )
		discoveryTime = tag['Timestamp']		# In microseconds since Jan 1, 1970
		discoveryTime = datetime.datetime.utcfromtimestamp( discoveryTime / 1000000.0 ) + timeCorrection
		print tagID, discoveryTime

def DefaultHandler( message ):
	print 'Unknown Message:'
	print message

#-----------------------------------------------------------------------------------------

def TinyExampleTest():
	global timeCorrection
	
	rospecID = 123					# Arbitrary rospecID.
	inventoryParameterSpecID = 1234	# Arbitrary inventory parameter spec id.

	# Create a reader connection.
	conn = LLRPConnection()

	# Add a callback so we can print the tags.
	conn.addHandler( RO_ACCESS_REPORT_Message, AccessReportHandler )

	# Add a default callback so we can see what else comes from the reader.
	conn.addHandler( 'default', DefaultHandler )

	# Connect to the reader.
	try:
		response = conn.connect( host )
	except socket.timeout:
		print '**** Connect timed out.  Check reader hostname and connection. ****'
		raise
	print response

	# Compute a correction between the reader's time and the computer's time.
	readerTime = response.getFirstParameterByClass(UTCTimestamp_Parameter).Microseconds
	readerTime = datetime.datetime.utcfromtimestamp( readerTime / 1000000.0 )
	timeCorrection = datetime.datetime.now() - readerTime
	print 'Reader timestamp is:', readerTime
	print timeCorrection, timeCorrection.total_seconds()

	# Disable all the rospecs.  This command may fail so we ignore the response.
	response = conn.transact( DISABLE_ROSPEC_Message(ROSpecID = 0) )

	# Delete our old rospec if it exists.  This command might fail so we ignore the return.
	response = conn.transact( DELETE_ROSPEC_Message(ROSpecID = rospecID) )
	#print response

	# Create an rospec that reports every read as soon as it happens.
	response = conn.transact(
		ADD_ROSPEC_Message( Parameters = [
			ROSpec_Parameter(
				ROSpecID = rospecID,
				CurrentState = ROSpecState.Disabled,
				Parameters = [
					ROBoundarySpec_Parameter(		# Configure boundary spec (start and stop triggers for the reader).
						Parameters = [
							ROSpecStartTrigger_Parameter(ROSpecStartTriggerType = ROSpecStartTriggerType.Immediate),
							ROSpecStopTrigger_Parameter(ROSpecStopTriggerType = ROSpecStopTriggerType.Null),
						]
					), # ROBoundarySpec
					AISpec_Parameter(				# Antenna Inventory Spec (specifies which antennas and protocol to use)
						AntennaIDs = [0],			# Use all antennas.
						Parameters = [
							AISpecStopTrigger_Parameter( AISpecStopTriggerType = AISpecStopTriggerType.Null ),
							InventoryParameterSpec_Parameter(
								InventoryParameterSpecID = inventoryParameterSpecID,
								ProtocolID = AirProtocols.EPCGlobalClass1Gen2,
							),
						]
					), # AISpec
					ROReportSpec_Parameter(			# Report spec (specified how often and what to send from the reader)
						ROReportTrigger = ROReportTriggerType.Upon_N_Tags_Or_End_Of_ROSpec,
						N = 1,						# N = 1 --> update on each read.
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

	# And enable it...
	response = conn.transact( ENABLE_ROSPEC_Message(ROSpecID = rospecID) )
	#print response
	assert response.success()

	# Start thread to listen to the reader for a while.
	print 'Listen to the connection for about 5 seconds...'
	conn.startListener()
	time.sleep( 5 )			# Wait for some reads (we could be doing something else here too).
	conn.stopListener()

	print 'Shutting down the connection...'
	response = conn.disconnect()
	print response

if __name__ == '__main__':
	TinyExampleTest()
