import sys
import time
import socket
import random
import datetime
import calendar
from MainWin import ImpinjInboundPort
from LLRP.LLRP import *

#------------------------------------------------------------------------------	
# Create some random rider numbers.
random.seed( 10101010 )
seen = set()
nums = []
for i in xrange(25):
	while 1:
		x = random.randint(1,200)
		if x not in seen:
			seen.add( x )
			nums.append( x )
			break

#------------------------------------------------------------------------------	
# Create a Impinj-style numeric tag for each number.
tag = dict( (n, '000000000000%04d' % n) for n in nums )
	
#------------------------------------------------------------------------------	
# Write out as a .csv file.  To create an external data file suitable for linking
# with CrossMgr, open this file in Excel, then save it in .xls (or .xlsx) format.
# Then link to this sheet in CrossMgr through "DataMgmt|Link to External Excel File...".
with open('ImpinjTest.csv', 'w') as f:
	f.write( 'Bib#,Tag,dummy3,dummy4,dummy5\n' )
	for n in nums:
		f.write( '%d,%s\n' % (n, tag[n]) )

#------------------------------------------------------------------------------	
count = 0
MessageID = 10000
def formatMessage( n, lap, t ):
	global count, MessageID
	count += 1
	MessageID += 1
	ts = calendar.timegm(t.utctimetuple()) + t.microsecond / 1000000.0
	print 'timestamp:', ts
	message = RO_ACCESS_REPORT_Message( MessageID = MessageID, Parameters = [
			TagReportData_Parameter( Parameters = [
					EPCData_Parameter( EPC='%x' % n ),
					FirstSeenTimestampUTC_Parameter( int(ts * 1000000.0) ),
					TagSeenCount_Parameter( TagCount = count ),
				],
			),
		],
	)
	return message

# Generate some random lap times.
random.seed()
numLapTimes = []
mean = 60.0							# Average lap time.
varFactor = 9.0 * 4.0
var = mean / varFactor				# Variance between riders.
lapMax = 6
for n in nums:
	lapTime = random.normalvariate( mean, mean/(varFactor * 4.0) )
	for lap in xrange(0, lapMax+1):
		numLapTimes.append( (n, lap, lapTime*lap) )
numLapTimes.sort( key = lambda x: (x[1], x[2]) )	# Sort by lap, then race time.

def StartClient():
	print 'StartClient: Waiting for commands.'
	
	sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
	sock.bind( ('127.0.0.1', ImpinjInboundPort) )
	sock.listen( 5 )

	try:
		clientSocket, addr = sock.accept()
	except socket.error, e:
		print e
		raise
	
	while 1:
		message = UnpackMessageFromSocket( clientSocket )
		
		print 'Received:'
		print message
		
		if   isinstance( message, GET_SUPPORTED_VERSION_Message ):
			response = GET_SUPPORTED_VERSION_RESPONSE_Message( MessageID = message.MessageID, CurrentVersion = 1, SupportedVersion = 2, Parameters = [
						LLRPStatus_Parameter( StatusCode = StatusCode_M_Success, ErrorDescription = 'Success'),
					],
				)
				
		elif isinstance( message, SET_PROTOCOL_VERSION_Message ):
			response = SET_PROTOCOL_VERSION_RESPONSE_Message( MessageID = message.MessageID, Parameters = [
						LLRPStatus_Parameter( StatusCode = StatusCode_M_Success, ErrorDescription = 'Success'),
					],
				)
				
		elif isinstance( message, GET_READER_CAPABILITIES_Message ):
			response = GET_READER_CAPABILITIES_RESPONSE_Message( MessageID = message.MessageID, Parameters = [
						LLRPStatus_Parameter( StatusCode = StatusCode_M_Success, ErrorDescription = 'Success'),
						GeneralDeviceCapabilities_Parameter(	DeviceManufacturerName = 0xededed, 
																MaxNumberOfAntennaSupported = 4,
																CanSetAntennaProperties = True,
																HasUTCClockCapability = True,
																ReaderFirmwareVersion = 'ExtraFirm',
																ModelName = 0xdedede)
					],
				)
				
		elif isinstance( message, CLOSE_CONNECTION_Message ):
			response = CLOSE_CONNECTION_RESPONSE_Message( MessageID = message.MessageID, Parameters = [
						LLRPStatus_Parameter( StatusCode = StatusCode_M_Success, ErrorDescription = 'Success'),
					],
				)
				
		elif isinstance( message, DISABLE_ROSPEC_Message ):
			response = DISABLE_ROSPEC_RESPONSE_Message( MessageID = message.MessageID, Parameters = [
						LLRPStatus_Parameter( StatusCode = StatusCode_M_Success, ErrorDescription = 'Success'),
					],
				)
				
		elif isinstance( message, DELETE_ROSPEC_Message ):
			response = DELETE_ROSPEC_RESPONSE_Message( MessageID = message.MessageID, Parameters = [
						LLRPStatus_Parameter( StatusCode = StatusCode_M_Success, ErrorDescription = 'Success'),
					],
				)
				
		elif isinstance( message, ADD_ROSPEC_Message ):
			response = ADD_ROSPEC_RESPONSE_Message( MessageID = message.MessageID, Parameters = [
						LLRPStatus_Parameter( StatusCode = StatusCode_M_Success, ErrorDescription = 'Success'),
					],
				)
				
		elif isinstance( message, ENABLE_ROSPEC_Message ):
			response = ENABLE_ROSPEC_RESPONSE_Message( MessageID = message.MessageID, Parameters = [
						LLRPStatus_Parameter( StatusCode = StatusCode_M_Success, ErrorDescription = 'Success'),
					],
				)
				
		else:
			assert False, 'Unknown message.'
		
		print 'Response:'
		print response
		
		response.send( clientSocket )
		
		if message.Type == ENABLE_ROSPEC_Message.Type:
			break
	
	iMessage = 1
	dBase = datetime.datetime.now()
	#------------------------------------------------------------------------------	
	time.sleep( 1 )
	print 'Start sending data...'

	while iMessage < len(numLapTimes):
		#------------------------------------------------------------------------------	
		while iMessage < len(numLapTimes):
			n, lap, t = numLapTimes[iMessage]
			dt = t - numLapTimes[iMessage-1][2]
			
			time.sleep( dt )
			
			message = formatMessage( n, lap, dBase + datetime.timedelta(seconds = t) )
			sys.stdout.write( 'sending: %s\n' % message )
			message.send( clientSocket )
			iMessage += 1
			
	if clientSocket:
		clientSocket.close()
		
StartClient()
