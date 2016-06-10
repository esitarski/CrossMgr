from __future__ import print_function

import socket 
import sys
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
from Queue import Queue
from Queue import Empty
import JChip

ChipReaderEvent, EVT_CHIP_READER = JChip.ChipReaderEvent, JChip.EVT_CHIP_READER

readerEventWindow = None
def sendReaderEvent( tagTimes ):
	if tagTimes and readerEventWindow:
		wx.PostEvent( readerEventWindow, ChipReaderEvent(tagTimes = tagTimes) )

EOL = bytes('\r\n')		# RaceResult delimiter
len_EOL = len(EOL)

DEFAULT_PORT = 3601
DEFAULT_HOST = '127.0.0.1'		# Port to connect to the RaceResult receiver.

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
	
def AutoDetect( raceResultPort=3601, callback=None ):
	''' Search ip addresses adjacent to the computer in an attempt to find the reader. '''
	ip = [int(i) for i in Utils.GetDefaultHost().split('.')]
	j = 0
	for i in xrange(14):
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
			socketSend( s, bytes('{}{}'.format(cmd, EOL)) )
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

statusFields = [
	'Date', 'Time', 'HasPower', 'Antennas', 'IsInTimingMode',
	'FileNumber', 'GPSHasFix', 'Latitude', 'Longitude', 'LongInd', 'ReaderIsHealthy', 'ActiveExtConnected',
	'Channel', 'LoopID', 'LoopPower', 'LoopConnected', 'LoopUnderPower', 'Temperature',
]
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
		qLog( 'autodetect', '{} {}'.format(_('Checking'), m) )
		return keepGoing()
		
	def makeCall( s, message ):
		cmd = message.split(';', 1)[0]
		qLog( 'command', u'sending: {}'.format(message) )
		try:
			socketSend( s, bytes('{}{}'.format(message,EOL)) )
			buffer = socketReadDelimited( s )
		except Exception as e:
			qLog( 'connection', u'{}: {}: "{}"'.format(cmd, _('Connection failed'), e) )
			raise ValueError
		
		if not buffer.startswith( '{};00'.format(cmd) ):
			qLog( 'command', u'{}: {} "{}"'.format(cmd, _('Unexpected return'), buffer) )
			raise ValueError
		
		return buffer[buffer.index(EOL)+1:]		# Strip off the return code.
		
	signed = 2
	percent = 1
	systemInfo = (
		(0x01, 'decoder id', 16),
		(0x02, 'firmware version', 8),
		(0x03, 'hardware version', 8),
		(0x04, 'box type', 8),
		(0x05, 'battery voltage', 8),
		(0x06, 'batter hours left', 8),
		(0x07, 'battery state', 8),
		(0x08, 'battery fillstate', 8, percent),
		(0x09, 'internal temperature', 8, signed),
		(0x0a, 'supply voltage', 8),
		(0x0b, 'loop status', 8),
	)
	def querySystemsystemInfo( s ):
		for i in systemInfo:
			ret = makeCall( s, 'systemInfoGET;{:2x}{}'.format(i[0], EOL) )
			param, value = ret.strip().split(';')
			value = int(value, 16)
			try:
				format = i[3]
				if format & signed:
					maxPos = (1<<i[2]) - 1
					if value > maxPos:
						value -= (maxPos + 1)
				if format & percent:
					value = '{}%'.format(value)
			except IndexError:
				pass
			qLog( 'status', u'{}={}'.format(i[1], value) )
	
	ref_epoch, ref_timestamp = 0, 0
	def timestampToDateTime( timestamp ):
		#ticks_since_epoch = timestamp - ref_timestamp         # this value is in 1/256s
		#seconds_since_epoch = ticks_since_epoch % 256
		#epoch_now_seconds = ref_epoch + seconds_since_epoch
		#epoch_now_additional_ticks = ticks_since_epoch - seconds_since_epoch * 256
		#seconds = epoch_now_seconds + epoch_now_additional_ticks / 256.0
		
		seconds = ref_epoch + (timestamp - ref_timestamp) / 256.0
		return datetime.datetime(1970,1,1) + datetime.timedelta( seconds=seconds )
		
	passingInfo = (
		('transponder-id', None),
		('passing-counter', 4),
		('timestamp', 8),
		('detection-counter', 2),
	)
	def parseTagTime( line, lineNo, errors ):
		fields = lines.split(';', len(passingInfo)+1)
		info = {key: fields[i] if type is None else int(fields[i], 16)
			for i, (key, type) in enumerate(passingInfo) }
		return info['transponder-id'], timestampToDateTime(info['timestamp'])
	
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
		try:
			querySystemInfo( s )
		except:
			continue
		
		#-----------------------------------------------------------------------------------------------------
		try:
			ret = makeCall( s, 'EPOCHREFGET{}'.format(EOL) )
		except ValueError:
			continue
		fields = ret.strip().split(';')
		ref_epoch, ref_timestamp = int(fields[0], 16), int(fields[1], 16)
		
		if ref_epoch == 0 and ref_timestamp == 0:
			try:
				ret = makeCall( s, 'EPOCHREFSET;{:8x}{}'.format(int(time.time()), EOL) )
			except ValueError:
				continue
			ref_epoch, ref_timestamp = int(fields[0], 16), int(fields[1], 16)
		
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
			
			tagTimes = []
			errors = []
			times = set()				
			while 1:
				cmd = 'PASSINGGET;{:08x}{}'.format( passingsCur, EOL )
				try:
					ret = makeCall( cmd )
				except Exception as e:
					qLog( 'connection', u'{}: {}: "{}"'.format(cmd, _('Connection failed'), e) )
					break

				lines = ret.split( EOL )
				count = int( lines[0].split(';')[1], 16 )
				if count == 0:
					break
			
				for i in xrange( count ):
					line = lines[i+1]
					tag, t = parseTagTime(line, passingsCur+i, errors)
					if tag is None or t is None:
						qLog( 'command', u'{}: {} "{}"'.format(cmd, _('Unexpected return'), line) )
						continue
					
					
					t += readerComputerTimeDiff
					while t in times:	# Ensure no equal times.
						t += tSmall
					
					times.add( t )
					tagTimes.append( (tag, t) )
					
				passingsCur += count
				
				if count != 64:
					break
					
			if tagTimes:
				sendReaderEvent( tagTimes )
				for tag, t in tagTimes:
					q.put( ('data', tag, t) )
				passingsCur += len(tagTimes)				
			
			time.sleep( delaySecs )
	
	# Final cleanup.
	cmd = 'STOPOPERATION'
	try:
		socketSend( s, '{}{}'.format(cmd, EOL) )
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
		for i in xrange(32):
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

