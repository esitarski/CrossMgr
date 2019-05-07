#!/usr/bin/env python
import os
import six
import sys
import time
import socket
import datetime

from .pyllrp import *
from .TagInventory import TagInventory

#-----------------------------------------------------------------------------------------

def TinyExampleTest( conn ):
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
	assert response.success()

	# And enable it...
	response = conn.transact( ENABLE_ROSPEC_Message(ROSpecID = rospecID) )
	assert response.success()

	# Start thread to listen to the reader for a while.
	six.print_( 'Listen to the connection for a few seconds...\n' )
	conn.startListener()
	time.sleep( 2 )			# Wait for some reads (we could be doing something else here too).
	conn.stopListener()

	six.print_( 'Shutting down the connection...\n' )
	response = conn.disconnect()
	six.print_( response )

if __name__ == '__main__':
	'''Read a tag inventory from the reader and shutdown.'''
	host = '192.168.0.101'
	ti = TagInventory( host )
	ti.Connect()
	tagInventory = ti.GetTagInventory()
	for t in tagInventory:
		six.print_( t )
	ti.Disconnect()
	
	''' Test that we can connect at different power levels. '''
	for p in [1,5,10,20,30,40,50,60,70,80]:
		six.print_( 'power={}'.format(p) )
		ti = TagInventory( host, transmitPower = p )
		ti.Connect()
		tagInventory = ti.GetTagInventory()
		for t in tagInventory:
			six.print_( t )
		ti.Disconnect()
