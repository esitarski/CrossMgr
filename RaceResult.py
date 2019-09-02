import socket 
import sys
import six
import time
import datetime
import atexit
import subprocess
import threading
import re
import wx
import wx.lib.newevent
import Utils
import Model
from threading import Thread as Process
from six.moves.queue import Queue, Empty
import JChip
from RaceResultImport import parseTagTime
from Utils import logCall, logException

ChipReaderEvent, EVT_CHIP_READER = JChip.ChipReaderEvent, JChip.EVT_CHIP_READER

readerEventWindow = None
def sendReaderEvent( tagTimes ):
	if tagTimes and readerEventWindow:
		wx.PostEvent( readerEventWindow, ChipReaderEvent(tagTimes = tagTimes) )

EOL = '\r\n'		# RaceResult delimiter
len_EOL = len(EOL)
EOL_encode = EOL.encode()

DEFAULT_PORT = 3601
DEFAULT_HOST = '127.0.0.1'		# Port to connect to the RaceResult receiver.

q = None
shutdownQ = None
listener = None

def socketSend( s, message ):	# Requires message to be a str.  Assumes message is delimited (if required).
	if not isinstance(message, bytes):
		message = message.encode()
	sLen = 0
	while sLen < len(message):
		sLen += s.send( message[sLen:] )
		
def socketReadDelimited( s, delimiter=EOL_encode ):
	if not isinstance(delimiter, bytes):
		delimiter = delimiter.encode()
	buffer = s.recv( 4096 )
	while not buffer.endswith( delimiter ):
		more = s.recv( 4096 )
		if more:
			buffer += more
		else:
			break
	return buffer.decode()		# returns an str.
	
def AutoDetect( raceResultPort=3601, callback=None ):
	''' Search ip addresses adjacent to the computer in an attempt to find the reader. '''
	ip = [int(i) for i in Utils.GetDefaultHost().split('.')]
	j = 0
	for i in range(14):
		j = -j if j > 0 else -j + 1
		
		ipTest = list( ip )
		ipTest[-1] += j
		if not (0 <= ipTest[-1] < 256):
			continue
			
		raceResultHost = '.'.join( '{}'.format(v) for v in ipTest )
		if callback:
			if not callback( '{}:{}'.format(raceResultHost,raceResultPort) ):
				return None
		
		try:
			s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			s.settimeout( 0.5 )
			s.connect( (raceResultHost, raceResultPort) )
		except Exception as e:
			continue

		cmd = 'GETSTATUS'
		try:
			socketSend( s, u'{}{}'.format(cmd, EOL) )
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
		
		if buffer.startswith( '{};'.format(cmd) ):
			return raceResultHost
			
	return None
	
# if we get the same time, make sure we give it a small offset to make it unique, but preserve the order.
tSmall = datetime.timedelta( seconds = 0.000001 )

statusFields = (
	'Date', 'Time', 'HasPower', 'Antennas', 'IsInTimingMode', 'FileNumber', 'GPSHasFix',
)
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
		Utils.writeLog( u'RaceResult: {}: {}'.format(category, message) )
	
	def keepGoing():
		try:
			shutdownQ.get_nowait()
		except Empty:
			return True
		return False
	
	def autoDetectCallback( m ):
		qLog( 'autodetect', u'{} {}'.format(_('Checking'), m) )
		return keepGoing()
		
	def makeCall( s, message ):
		cmd = message.split(';', 1)[0]
		qLog( 'command', u'sending: {}'.format(message) )
		try:
			socketSend( s, u'{}{}'.format(message,EOL) )
			buffer = socketReadDelimited( s )
		except Exception as e:
			qLog( 'connection', u'{}: {}: "{}"'.format(cmd, _('Connection failed'), e) )
			raise ValueError
		
		if not buffer.startswith( u'{};'.format(cmd) ):
			qLog( 'command', u'{}: {} "{}"'.format(cmd, _('Unexpected return'), buffer) )
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
		qLog( 'connection', u'{} {}:{}'.format(_('Attempting to connect to RaceResult reader at'), HOST, PORT) )
		try:
			s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			s.settimeout( timeoutSecs )
			s.connect( (HOST, PORT) )
		except Exception as e:
			qLog( 'connection', u'{}: {}'.format(_('Connection to RaceResult reader failed'), e) )
			s, status, startOperation = None, None, None
			
			qLog( 'connection', u'{}'.format(_('Attempting AutoDetect...')) )
			HOST_AUTO = AutoDetect( callback = autoDetectCallback )
			if HOST_AUTO:
				qLog( 'connection', u'{}: {}'.format(_('AutoDetect RaceResult at'), HOST_AUTO) )
				HOST = HOST_AUTO
			else:
				time.sleep( delaySecs )
			continue

		#-----------------------------------------------------------------------------------------------------
		crossMgrMinProtocol = (1,2)
		crossMgrMinProtocolStr = '.'.join('{}'.format(p) for p in crossMgrMinProtocol)
		try:
			buffer = makeCall( s, 'GETPROTOCOL' )
		except ValueError as e:
			logException( e, sys.exc_info() )
			continue
		
		current, minSupported, maxSupported = [f.strip() for f in buffer.strip().split(';')[1:]]
		
		if tuple(int(i) for i in maxSupported.split('.')) < crossMgrMinProtocol:
			qLog(
				'connection',
				u'{}. {} >={}. {} {}.'.format(
					_("RaceResult requires Firmware Upgrade"),
					_("CrossMgr requires PROTOCOL"), crossMgrMinProtocolStr,
					_("RaceResult supports"), maxSupported,
				)
			)
			time.sleep( delaySecs )
			continue
			
		try:
			buffer = makeCall( s, 'SETPROTOCOL;{}'.format(maxSupported) )
		except ValueError:
			continue
		
		qLog( 'status', u'{}'.format(buffer.strip()) )
		
		try:
			buffer = makeCall( s, 'GETSTATUS' )
		except ValueError:
			continue
		
		fields = [f.strip() for f in buffer.strip().split(';')]
		status = zip( statusFields, fields[1:] )
		for name, value in status:
			qLog( 'status', u'{}: {}'.format(name, value) )
		
		#-----------------------------------------------------------------------------------------------------
		try:
			buffer = makeCall( s, 'STOPOPERATION' )
		except ValueError:
			continue
		
		#-----------------------------------------------------------------------------------------------------
		try:
			buffer = makeCall( s, 'SETTIME;{}'.format(datetime.datetime.now().strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]) )
		except ValueError:
			continue
		
		#-----------------------------------------------------------------------------------------------------
		try:
			buffer = makeCall( s, 'STARTOPERATION' )
		except ValueError:
			continue
		qLog( 'status', u'{}'.format(buffer.strip()) )
		
		#-----------------------------------------------------------------------------------------------------
		try:
			buffer = makeCall( s, 'GETTIME' )
		except ValueError:
			continue
		
		try:
			dt = reNonDigit.sub(' ', buffer).strip()
			fields[-1] = (fields[-1] + '000000')[:6]	# Pad with zeros to convert to microseconds.
			readerTime = datetime.datetime( *[int(f) for f in dt.split()] )
			readerComputerTimeDiff = datetime.datetime.now() - readerTime
		except Exception as e:
			qLog( 'command', u'GETTIME: {} "{}" "{}"'.format(_('Unexpected return'), buffer, e) )
			continue
		
		while keepGoing():
			#-------------------------------------------------------------------------------------------------
			cmd = 'PASSINGS'
			try:
				socketSend( s, u'{}{}'.format(cmd, EOL) )
				buffer = socketReadDelimited( s )
				if buffer.startswith( '{};'.format(cmd) ):
					fields = buffer.split(';')
					try:
						passingsText = fields[1]
					except Exception as e:
						qLog( 'command', u'{}: {} "{}" "{}"'.format(cmd, _('Unexpected return'), buffer, e) )
						continue
					
					try:
						passingsNew = int( reNonDigit.sub(' ', passingsText).strip() )
					except Exception as e:
						qLog( 'command', u'{}: {} "{}" "{}"'.format(cmd, _('Unexpected return'), buffer, e) )
						continue
					
				else:
					qLog( 'command', u'{}: {} "{}"'.format(cmd, _('Unexpected return'), buffer) )
					continue
			except Exception as e:
				qLog( 'connection', u'{}: {}: "{}"'.format(cmd, _('Connection failed'), e) )
				break

			if passingsNew != passingsCur:
				if passingsNew < passingsCur:
					passingsCur = 0
					
				tagTimes = []
				errors = []
				times = set()
				
				passingsCount = passingsNew - passingsCur
				
				#---------------------------------------------------------------------------------------------
				cmd = '{}:{}'.format(passingsCur+1, passingsCount)	# Add one as the reader counts inclusively.
				qLog( 'command', u'sending: {} ({}+{}={} passings)'.format(cmd, passingsCur, passingsCount, passingsNew) )
				try:
					# Get the passing data.
					socketSend( s, u'{}{}'.format(cmd, EOL) )
				except Exception as e:
					qLog( 'connection', u'cmd={}: {}: "{}"'.format(cmd, _('Connection failed'), e) )
					break
				
				tagReadSuccess = False
				try:
					readAllPassings = False
					while not readAllPassings:
						response = socketReadDelimited( s )
						
						sStart = 0
						while 1:
							sEnd = response.find( EOL, sStart )
							if sEnd < 0:
								break
							if sEnd == sStart:		# An empty passing indicates this is the last one.
								readAllPassings = True
								break
							
							line = response[sStart:sEnd]
							sStart = sEnd + len_EOL
						
							tag, t = parseTagTime(line, passingsCur+len(tagTimes), errors)
							if tag is None or t is None:
								qLog( 'command', u'{}: {} "{}"'.format(cmd, _('Unexpected return'), line) )
								continue
							
							t += readerComputerTimeDiff
							while t in times:	# Ensure no equal times.
								t += tSmall
							
							times.add( t )
							tagTimes.append( (tag, t) )
					
					tagReadSuccess = True
				
				except Exception as e:
					qLog( 'connection', u'cmd={}: {}: "{}"'.format(cmd, _('Connection failed'), e) )
				
				sendReaderEvent( tagTimes )
				for tag, t in tagTimes:
					q.put( ('data', tag, t) )
				passingsCur += len(tagTimes)
				
				if not tagReadSuccess:
					break
			
			time.sleep( delaySecs )
	
	# Final cleanup.
	cmd = 'STOPOPERATION'
	try:
		socketSend( s, u'{}{}'.format(cmd, EOL) )
		buffer = socketReadDelimited( s )
		s.shutdown( socket.SHUT_RDWR )
		s.close()
	except:
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

def StartListener( startTime=datetime.datetime.now(), HOST=None, PORT=None ):
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
	listener.name = 'RaceResult Listener'
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
					elif m[0] == 'status':
						print( 'status: {}'.format(m[1]) )
					elif m[0] == 'passings':
						print( 'passings: {}'.format(m[1]) )
					elif m[0] == 'command':
						print( 'command: {}'.format(m[1]) )
					else:
						print( 'other: {}, {}'.format(m[0], ', '.join('"{}"'.format(s) for s in m[1:])) )
				sys.stdout.flush()
		except KeyboardInterrupt:
			return
		
	t = threading.Thread( target=doTest )
	t.daemon = True
	t.run()
	
	time.sleep( 1000000 )

