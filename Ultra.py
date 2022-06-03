import socket
import sys
import time
import datetime
import datetime
now = datetime.datetime.now
import atexit
import subprocess
import threading
import re
import wx
import wx.lib.newevent
import Utils
import Model
from threading import Thread as Process
from queue import Queue, Empty
import JChip

ChipReaderEvent, EVT_CHIP_READER = JChip.ChipReaderEvent, JChip.EVT_CHIP_READER

readerEventWindow = None
def sendReaderEvent( tagTimes ):
	if tagTimes and readerEventWindow:
		wx.PostEvent( readerEventWindow, ChipReaderEvent(tagTimes = tagTimes) )

EOL = '\r'		# Ultra delimiter
len_EOL = len(EOL)

def parseTagTime( s ):
	_, ChipCode, Seconds, Milliseconds, _ = s.split(',', 4)
	t = datetime.datetime(1980, 1, 1) + datetime.timedelta( seconds=int(Seconds), milliseconds=int(Milliseconds) )
	return ChipCode, t

DEFAULT_PORT = 23
#DEFAULT_PORT = 8642
DEFAULT_HOST = '127.0.0.1'		# Port to connect to the Ultra receiver.

q = None
shutdownQ = None
listener = None

def socketSend( s, message ):
	sLen = 0
	while sLen < len(message):
		sLen += s.send( message[sLen:] )
		
def socketReadDelimited( s, delimiter=EOL ):
	buffer = s.recv( 4096 )
	while not buffer.endswith( delimiter ):
		more = s.recv( 4096 )
		if more:
			buffer += more
		else:
			break
	return buffer
	
def iterAdjacentIPs():
	''' Return ip addresses adjacent to the computer in an attempt to find the reader. '''
	ip = [int(i) for i in Utils.GetDefaultHost().split('.')]
	ipPrefix = '.'.join( '{}'.format(v) for v in ip[:-1] )
	ipLast = ip[-1]
	
	count = 0
	j = 0
	while 1:
		j = -j if j > 0 else -j + 1
		
		ipTest = ipLast + j
		if 0 <= ipTest < 256:
			yield '{}.{}'.format(ipPrefix, ipTest)
			count += 1
			if count >= 8:
				break
		
def AutoDetect( ultraPort=DEFAULT_PORT, callback=None ):
	for ultraHost in iterAdjacentIPs():
		if callback:
			if not callback( '{}:{}'.format(ultraHost,ultraPort) ):
				return None
		
		try:
			s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			s.settimeout( 0.5 )
			s.connect( (ultraHost, ultraPort) )
		except Exception as e:
			continue

		try:
			buffer = socketReadDelimited( s )
		except Exception as e:
			continue
			
		try:
			s.close()
		except Exception as e:
			pass
		
		if buffer.startswith('Connected'):
			return ultraHost
			
	return None
	
# if we get the same time, make sure we give it a small offset to make it unique, but preserve the order.
tSmall = datetime.timedelta( seconds = 0.000001 )

reNonDigit = re.compile( '[^0-9]+' )
def Server( q, shutdownQ, HOST, PORT, startTime ):
	global readerEventWindow
	
	if not readerEventWindow:
		readerEventWindow = Utils.mainWin
	
	timeoutSecs = 5
	delaySecs = 3
	
	readerTime = None
	readerComputerTimeDiff = None
	
	s = None
	passingsCur = 0
	status = None
	startOperation = None
	
	def qLog( category, message ):
		q.put( (category, message) )
		Utils.writeLog( 'Ultra: {}: {}'.format(category, message) )
	
	def keepGoing():
		try:
			shutdownQ.get_nowait()
		except Empty:
			return True
		return False
	
	def autoDetectCallback( m ):
		qLog( 'autodetect', '{} {}'.format(_('Checking'), m) )
		return keepGoing()
		
	def makeCall( s, message, getReply=True, comment='' ):
		cmd = message.split(';', 1)[0]
		buffer = None
		qLog( 'command', 'sending: {}{}'.format(message, ' ({})'.format(comment) if comment else '') )
		try:
			#socketSend( s, bytes('{}{}'.format(message,EOL)) )
			socketSend( s, bytes(message) )
			if getReply:
				buffer = socketReadDelimited( s )
		except Exception as e:
			qLog( 'connection', '{}: {}: "{}"'.format(cmd, _('Connection failed'), e) )
			raise ValueError
		
		return buffer
	
	while keepGoing():
		if s:
			try:
				s.shutdown( socket.SHUT_RDWR )
				s.close()
			except Exception as e:
				pass
			time.sleep( delaySecs )
		
		#-----------------------------------------------------------------------------------------------------
		qLog( 'connection', '{} {}:{}'.format(_('Attempting to connect to Ultra reader at'), HOST, PORT) )
		try:
			s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			s.settimeout( timeoutSecs )
			s.connect( (HOST, PORT) )
		except Exception as e:
			qLog( 'connection', '{}: {}'.format(_('Connection to Ultra reader failed'), e) )
			s, status, startOperation = None, None, None
			
			qLog( 'connection', '{}'.format(_('Attempting AutoDetect...')) )
			HOST_AUTO = AutoDetect( callback = autoDetectCallback )
			if HOST_AUTO:
				qLog( 'connection', '{}: {}'.format(_('AutoDetect Ultra at'), HOST_AUTO) )
				HOST = HOST_AUTO
			else:
				time.sleep( delaySecs )
			continue

		qLog( 'connection', '{} {}:{}'.format(_('connect to Ultra reader SUCCEEDS on'), HOST, PORT) )
		
		#-----------------------------------------------------------------------------------------------------
		try:
			makeCall( s, 'S', False, comment='stop reading' )
		except ValueError:
			continue
		
		#-----------------------------------------------------------------------------------------------------
		# Set the reader's time.
		# Wait for the boundary of a second.  This is the best synchronization we are going to get.
		time.sleep( (1000000 - now().microsecond) / 1000000.0 )
		try:
			buffer = makeCall( s, 't {}'.format( now().strftime('%H:%M:%S %d-%m-%Y') ), True, comment='set reader time' )
		except ValueError:
			continue
		readerComputerTimeDiff = datetime.timedelta( seconds=0 )
		
		#-----------------------------------------------------------------------------------------------------
		try:
			makeCall( s, 'R', False, comment='start reading' )
		except ValueError:
			continue
		
		lastVoltage = now()
		while keepGoing():
			try:
				buffer = socketReadDelimited( s )
			except socket.timeout:
				if (now() - lastVoltage).total_seconds() > 15:
					qLog( 'connection', _('Lost heartbeat.') )
				continue
			except Exception as e:
				qLog( 'connection', '{}: "{}"'.format(_('Connection failed'), e) )
				break

			tagTimes = []
			errors = []
			times = set()
			for message in buffer.split( EOL ):
				if not message:
					continue
				
				# Check for a heartbeat.
				if message.startswith( 'V=' ):
					lastVoltage = now()	# If so, reset the last heartbeat time.
					continue
				
				# Otherwise, assume this is a chip read.
				tag, t = parseTagTime( message )
				
				if tag is None or t is None:
					qLog( 'command', '{}: "{}"'.format(_('Unexpected reader message'), message) )
					continue
				
				t += readerComputerTimeDiff
				while t in times:	# Ensure no equal times.
					t += tSmall
				
				times.add( t )
				tagTimes.append( (tag, t) )
		
			sendReaderEvent( tagTimes )
			for tag, t in tagTimes:
				q.put( ('data', tag, t) )
	
	# Final cleanup.
	try:
		s.shutdown( socket.SHUT_RDWR )
		s.close()
	except Exception:
		pass
		
def GetData():
	data = []
	while 1:
		try:
			data.append( q.get_nowait() )
		except (Empty, AttributeError):
			break
	return data

def StopListener():
	global q
	global listener
	global shutdownQ
	
	# Terminate the server process if it is running.
	# Add a number of shutdown commands as we may check a number of times.
	if listener:
		for i in range(32):
			shutdownQ.put( 'shutdown' )
		listener.join()
	listener = None
	
	# Purge the queues.
	while q:
		try:
			q.get_nowait()
		except Empty:
			q = None
			break
	
	shutdownQ = None
	
def IsListening():
	return listener is not None

def StartListener( startTime=now(), HOST=None, PORT=None, test=False ):
	global q
	global shutdownQ
	global listener
	
	StopListener()
	
	if Model.race:
		HOST = (HOST or Model.race.chipReaderIpAddr)
		PORT = (PORT or Model.race.chipReaderPort)
	
	q = Queue()
	shutdownQ = Queue()
	listener = Process( target = Server, args=(q, shutdownQ, HOST, PORT, startTime) )
	listener.name = 'Ultra Listener'
	listener.daemon = True
	listener.start()
	
@atexit.register
def CleanupListener():
	global shutdownQ
	global listener
	if listener and listener.is_alive():
		shutdownQ.put( 'shutdown' )
		listener.join()
	listener = None
	
if __name__ == '__main__':
	def doTest():
		try:
			StartListener( HOST='127.0.0.1', PORT=DEFAULT_PORT )
			count = 0
			while 1:
				time.sleep( 1 )
				sys.stdout.write( '.' )
				messages = GetData()
				if messages:
					sys.stdout.write( '\n' )
				for m in messages:
					if m[0] == 'data':
						count += 1
						print( '{}: {}, {}'.format(count, m[1], m[2].time()) )
					else:
						print( 'other: {}, {}'.format(m[0], ', '.join('"{}"'.format(s) for s in m[1:])) )
				sys.stdout.flush()
		except KeyboardInterrupt:
			return
		
	t = threading.Thread( target=doTest )
	t.daemon = True
	t.run()
	
	time.sleep( 1000000 )

