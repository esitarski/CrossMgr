import sys
import time
import socket
import random
import datetime
import calendar
from MainWin import ImpinjInboundPort
from pyllrp.pyllrp import *

#------------------------------------------------------------------------------	
# Create some random rider numbers.
random.seed( 10101010 )
seen = set()
nums = []
for i in range(25):
	while True:
		x = random.randint(1,200)
		if x not in seen:
			seen.add( x )
			nums.append( x )
			break

#------------------------------------------------------------------------------	
# Create a Impinj-style numeric tag for each number.
tag = dict( (n, '000000000000%04d' % n) for n in nums )
	
def toHexFormat( tag ):
	s = str(tag)
	if len(s) & 1:		# Pad to an even number of chars.
		s = '0' + s
	b = []
	for i in range(0, len(s), 2):				# Convert pairs of decimals to hex.
		b.append( chr(int(s[i:i+2], 16)) )
	return bytes( ''.join(b) )

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
	print( 'timestamp:', ts )
	message = RO_ACCESS_REPORT_Message( MessageID = MessageID, Parameters = [
			TagReportData_Parameter( Parameters = [
					EPCData_Parameter( EPC=toHexFormat(n) ),
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
	for lap in range(0, lapMax+1):
		numLapTimes.append( (n, lap, lapTime*lap) )
numLapTimes.sort( key = lambda x: (x[1], x[2]) )	# Sort by lap, then race time.

def StartClient():
	print( 'StartClient: Setting up connection...' )
	
	sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
	sock.bind( ('127.0.0.1', ImpinjInboundPort) )
	sock.listen( 5 )

	try:
		clientSocket, addr = sock.accept()
	except socket.error as e:
		print( e )
		raise
	
	print( 'StatClient: Sending  event notification - everything is OK.' )
	ms = long((datetime.datetime.now() - datetime.datetime( 1970, 1, 1, 0, 0, 0 )).total_seconds() * 1000000)
	READER_EVENT_NOTIFICATION_Message( Parameters = [
			ReaderEventNotificationData_Parameter( Parameters = [
				UTCTimestamp_Parameter( ms ),
				ConnectionAttemptEvent_Parameter(Status = ConnectionAttemptStatusType.Success),
			] )
		]
	).send( clientSocket )
	
	print( 'StartClient: Waiting for commands.' )
	llrpSuccess = LLRPStatus_Parameter( StatusCode = StatusCode.M_Success, ErrorDescription = 'Success')
	while True:
		message = UnpackMessageFromSocket( clientSocket )
		
		print( 'Received:' )
		print( message )
		
		if isinstance( message, SET_READER_CONFIG_Message ):
			response = SET_READER_CONFIG_RESPONSE_Message( MessageID = message.MessageID, Parameters = [llrpSuccess] )
		elif isinstance( message, CLOSE_CONNECTION_Message ):
			response = CLOSE_CONNECTION_RESPONSE_Message( MessageID = message.MessageID, Parameters = [llrpSuccess] )
		elif isinstance( message, DISABLE_ROSPEC_Message ):
			response = DISABLE_ROSPEC_RESPONSE_Message( MessageID = message.MessageID, Parameters = [llrpSuccess] )
		elif isinstance( message, DELETE_ROSPEC_Message ):
			response = DELETE_ROSPEC_RESPONSE_Message( MessageID = message.MessageID, Parameters = [llrpSuccess] )
		elif isinstance( message, ADD_ROSPEC_Message ):
			response = ADD_ROSPEC_RESPONSE_Message( MessageID = message.MessageID, Parameters = [llrpSuccess] )
		elif isinstance( message, ENABLE_ROSPEC_Message ):
			response = ENABLE_ROSPEC_RESPONSE_Message( MessageID = message.MessageID, Parameters = [llrpSuccess] )
		else:
			assert False, 'Unknown message.'
		
		print( 'Response:' )
		print( response )
		
		response.send( clientSocket )
		
		if message.Type == ENABLE_ROSPEC_Message.Type:
			break
	
	iMessage = 1
	dBase = datetime.datetime.now()
	#------------------------------------------------------------------------------
	time.sleep( 1 )
	print( 'Start sending data...' )

	while iMessage < len(numLapTimes):
		#------------------------------------------------------------------------------
		while iMessage < len(numLapTimes):
			n, lap, t = numLapTimes[iMessage]
			dt = t - numLapTimes[iMessage-1][2]
			
			# Wait for the next event.  Make sure we send a KEEP_ALIVE every 2 seconds.
			for i in range(1000):
				if i >= dt:
					break
				time.sleep( min(2, dt - i) )
				KEEPALIVE_Message().send( clientSocket )
				response = UnpackMessageFromSocket( clientSocket )
				assert isinstance( response, KEEPALIVE_ACK_Message )
			
			message = formatMessage( n, lap, dBase + datetime.timedelta(seconds = t) )
			print( 'sending: %s\n' % message )
			message.send( clientSocket )
			iMessage += 1
			
	if clientSocket:
		clientSocket.close()
		
StartClient()
