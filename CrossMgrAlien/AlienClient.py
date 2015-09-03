import sys
import time
import socket
import threading
import random
import datetime
from MainWin import HeartbeatPort, NotifyPort
from Utils import readDelimitedData
from AutoDetect import GetDefaultHost

DEFAULT_HOST = GetDefaultHost()

from xml.dom.minidom import parseString

CmdPort = 53161

testTags = '''e2001018860b01490700d128
e2001018860b01460700d11c
e2001018860b01470700d120
e2001018860b01520700d134
e2001018860b01570700d148
e2001018860b01500700d12c
e2001018860b01590700d150
e2001018860b01480700d124
e2001018860b01450700d118
e2001018860b01610700d158
e2001018860b01290700d0d8
e2001018860b01440700d114
e2001018860b01420700d10c
e2001018860b01400700d104
e2001018860b01430700d110
e2001018860b01380700d0fc
e2001018860b01410700d108
e2001018860b01390700d100
e2001018860b01370700d0f8
e2001018860b01530700d138'''.split()

alienOptions = {
	'readerName':	'Alien Client Test',
	'readerType':	'Python Emulator',
	'macAddress':	'01:02:03:04:05:06',
	'notifyHost':	DEFAULT_HOST,
	'cmdPort':		CmdPort
}

heartbeat = '''<Alien-RFID-Reader-Heartbeat>
 <ReaderName>{readerName}</ReaderName>
 <ReaderType>{readerType}</ReaderType>
 <IPAddress>{notifyHost}</IPAddress>
 <CommandPort>{cmdPort}</CommandPort>
 <HeartbeatTime>30</HeartbeatTime>
 <MACAddress>{macAddress}</MACAddress>
 <ReaderVersion>01.02.03.04</ReaderVersion>
</Alien-RFID-Reader-Heartbeat>'''.format( **alienOptions )

keepGoing = True
haveCommands = False

#------------------------------------------------------------------------------	
# JChip delimiter (CR, **not** LF)
CR = chr( 0x0d )

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
# Create a Alien-style numeric tag for each number.
tag = dict( (n, '000000000000%04d' % n) for n in nums )

# Add our special tags.
for i, n in enumerate(tag):
	try:
		tag[n] = testTags[i]
	except IndexError:
		break
	
#------------------------------------------------------------------------------	
# Write out as a .csv file.  To create an external data file suitable for linking
# with CrossMgr, open this file in Excel, then save it in .xls (or .xlsx) format.
# Then link to this sheet in CrossMgr through "DataMgmt|Link to External Excel File...".
with open('AlienTest.csv', 'w') as f:
	f.write( 'Bib#,Tag,dummy3,dummy4,dummy5\n' )
	for n in nums:
		f.write( '{},{}\n'.format(n, tag[n]) )

#------------------------------------------------------------------------------
		
def Heartbeat():
	print heartbeat
	address = (DEFAULT_HOST, HeartbeatPort)
	s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
	while keepGoing:
		print 'sending heartbeat...', address
		s.sendto( heartbeat, address )
		time.sleep( 5 )
		
intro = '''*****************************************************
*
* Alien Technology : RFID Reader Test (AlienClient.py)
*
*****************************************************

Username>\r\n\0'''

def MonitorCmds():
	global haveCommands
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.bind( (DEFAULT_HOST, CmdPort) )
	s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
	cmdCount = 0
	while 1:
		# Wait for a connection.
		s.listen( 5 )
		conn, addr = s.accept()
		
		conn.sendall( intro )
		
		for cmd in readDelimitedData( conn, '\n' ):
			if not cmd:
				continue
				
			if cmd.startswith( '\1' ):
				cmd = cmd[1:]
				
			cmd = cmd.strip()
			
			print 'cmd:', cmd
			if cmd.lower().startswith( 'set' ):
				eq = cmd.find( '=' )
				response = '{} = {}'.format(cmd[3:eq].strip(), cmd[eq+1:].strip())
			elif cmd.lower().startswith('get'):
				response = '{} = TestResponse cmdCount={}'.format(cmd.split()[1], cmdCount)
			elif cmd.endswith('?'):
				response = '{} = TestResponse cmdCount={}'.format(cmd[:-1], cmdCount)
			else:
				response = cmd
			conn.sendall( '{}\r\n\0'.format(response) )
		haveCommands = True
		cmdCount += 1

#----------------------------------------------------------------------------------

#------------------------------------------------------------------------------	
# Function to format number, lap and time in JChip-like format
# 01234567890123456 10:11:16.4433 10  10000      C7
#------------------------------------------------------------------------------	
count = 0
def formatMessage( n, lap, t ):
	global count
	message = '''<?xml version="1.0" encoding="UTF-8"?>
<Alien-RFID-Reader-Auto-Notification>
 <ReaderName>{readerName}</ReaderName>
 <ReaderType>{readerType}</ReaderType>
 <IPAddress>{notifyHost}</IPAddress>
 <CommandPort>{cmdPort}</CommandPort>
 <MACAddress>{macAddress}</MACAddress>
 <Time>{time}</Time>
 <Reason>TEST MESSAGE</Reason>
 <Alien-RFID-Tag-List>
   <Alien-RFID-Tag>
    <TagID>{tag}</TagID>
	<DiscoveryTime>{discoveryTime}</DiscoveryTime>
	<LastSeenTime>{lastSeenTime}</LastSeenTime>
	<Antenna>0</Antenna>
	<ReadCount>{readCount}</ReadCount>
	<Protocol>1</Protocol>
   </Alien-RFID-Tag>
 </Alien-RFID-Tag-List>
</Alien-RFID-Reader-Auto-Notification>\r\n\0'''

	tStr = t.strftime( '%Y/%m/%d %H:%M:%S.%f' )
	options = alienOptions
	options.update(
		{
			'tag':				tag[n],
			'time':				tStr,
			'discoveryTime':	tStr,
			'lastSeenTime':		tStr,
			'readCount':		count,
		}
	)
	count += 1
	
	s = message.format( **options )
	doc = parseString( s[:-3] )
	return message.format( **options )

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

def SendData():
	print 'SendData started.  Waiting for commands.'
	while not haveCommands:
		time.sleep( 5 )

	#------------------------------------------------------------------------------	
	# Connect to the CrossMgr server.
	iMessage = 1
	dBase = datetime.datetime.now()
	#------------------------------------------------------------------------------	
	time.sleep( 1 )
	print 'Start sending data...'

	while iMessage < len(numLapTimes):
		# Create a socket (SOCK_STREAM means a TCP socket)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print 'sending data to', DEFAULT_HOST, NotifyPort
		sock.connect((DEFAULT_HOST, NotifyPort))
		
		#------------------------------------------------------------------------------	
		while iMessage < len(numLapTimes):
			n, lap, t = numLapTimes[iMessage]
			dt = t - numLapTimes[iMessage-1][2]
			
			time.sleep( dt )
			
			message = formatMessage( n, lap, dBase + datetime.timedelta(seconds = t) )
			sys.stdout.write( 'sending: {}\n'.format(message[:-3]) )
			try:
				sock.send( message )
				sock.send( message )
				iMessage += 1
			except:
				print 'Send failed.  Attempting to reconnect...'
				sock.close()
				break
			
			# Simulate closing the connection.
			if iMessage % 10 == 0:
				sock.close()
				break
			
sendDataThread = threading.Thread( target = SendData )
sendDataThread.daemon = True
sendDataThread.start()

heartbeatThread = threading.Thread( target = Heartbeat )
heartbeatThread.daemon = True
heartbeatThread.start()

cmdsThread = threading.Thread( target = MonitorCmds )
cmdsThread.daemon = True
cmdsThread.start()

sendDataThread.join()

