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
host = '192.168.10.101'

timeCorrection = None
def AccessReportHandler( accessReport ):
	for tag in accessReport.getTagData():
		tagID = HexFormatToInt( tag['EPC'] )
		
		discoveryTime = tag['Timestamp']		# In microseconds since Jan 1, 1970
		readCount = tag['TagSeenCount']
		
		# Decode tagID and discoveryTime.
		discoveryTime = datetime.datetime.utcfromtimestamp( discoveryTime / 1000000.0 ) + timeCorrection
		
		print tagID, discoveryTime

def DefaultHandler( message ):
	print 'Unknown Message:'
	print message

#-----------------------------------------------------------------------------------------

def TinyExampleTest():
	global timeCorrection
	
	rospecID = 123	# Arbitrary rospecID.

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

	# Disable all the rospecs.
	response = conn.transact( DISABLE_ROSPEC_Message(ROSpecID = 0) )
	#print response
	assert response.success()

	# Delete our old rospec if it exists.  This command might fail, so we don't check the return.
	response = conn.transact( DELETE_ROSPEC_Message(ROSpecID = rospecID) )
	#print response

	# Create a new rospec that reports every read as soon as it happens.
	response = conn.transact( GetBasicAddRospecMessage(ROSpecID = rospecID) )
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
