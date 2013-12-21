#!/usr/bin/env python
import os
import sys
import time
import socket
import datetime

# If we are running from the development folder, change to a local search path.
if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == 'pyllrp':
	from TagInventory import TagInventory
else:
	from pyllrp.TagInventory import TagInventory

#-----------------------------------------------------------------------------------------

def TinyExampleTest():
	rospecID = 123					# Arbitrary rospecID.
	inventoryParameterSpecID = 1234	# Arbitrary inventory parameter spec id.

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
	print 'Listen to the connection for a few seconds...'
	conn.startListener()
	time.sleep( 2 )			# Wait for some reads (we could be doing something else here too).
	conn.stopListener()

	print 'Shutting down the connection...'
	response = conn.disconnect()
	print response

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