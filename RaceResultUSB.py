from __future__ import print_function

import socket
import six
import sys
import time
import datetime
import atexit
import subprocess
import threading
import re
import wx
import wx.lib.newevent
import serial
import Utils
import Model
from threading import Thread as Process
from six.moves.queue import Queue, Empty
import JChip

ChipReaderEvent, EVT_CHIP_READER = JChip.ChipReaderEvent, JChip.EVT_CHIP_READER

readerEventWindow = None
def sendReaderEvent( tagTimes ):
	if tagTimes and readerEventWindow:
		wx.PostEvent( readerEventWindow, ChipReaderEvent(tagTimes = tagTimes) )

EOL = bytes('\n')		# RaceResult USB delimiter
len_EOL = len(EOL)

q = None
shutdownQ = None
listener = None

def readResponse( s ):
	time.sleep( 0.1 )
	response = []
	while 1:
		c = s.read( 1 )
		if not c:
			raise ValueError
		if c == '\n' and response[-1] == '\n':
			return b''.join( response )
		response.append( c )

def AutoDetect( callback=None ):
	for comport in serial.tools.list_ports.comports():
		if comport.pid == 403 and comport.vid == 6001:
			found = re.search( r'(\d+)$', comport.name )
			if found:
				return int(found.group(1))
	return None
	
# if we get the same time, make sure we give it a small offset to make it unique, but preserve the order.
tSmall = datetime.timedelta( seconds = 0.000001 )

reNonDigit = re.compile( '[^0-9]+' )
def Server( q, shutdownQ, comPort, startTime ):
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
	
	def autoDetectCallback( com ):
		qLog( 'autodetect', '{}{}...'.format(_('Checking COM'), com) )
		return keepGoing()
		
	def makeCall( s, message ):
		if not message.endswith(EOL):
			message += EOL
		cmd = message.split(';', 1)[0]
		qLog( 'command', u'sending: {}'.format(message) )
		try:
			bMsg = bytes(message.encode())
			bytesWritten = s.write( bMsg )
			if bytesWritten != len(bMsg):
				qLog( 'connection', u'{}: {}: "{}"'.format(cmd, _('Connection failed'), _('Write length error')) )
				raise ValueError
			s.flush()
			buffer = readResponse( s )
		except Exception as e:
			qLog( 'connection', u'{}: {}: "{}"'.format(cmd, _('Connection failed'), e) )
			raise ValueError
		
		if not buffer.startswith( '{};00'.format(cmd) ):
			qLog( 'command', u'{}: {} "{}"'.format(cmd, _('Command failed'), buffer) )
			raise ValueError
		
		return buffer[buffer.index(EOL)+1:]		# Strip off the cmd repeat and return code.
		
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
	def querySystemInfo( s ):
		for i in systemInfo:
			ret = makeCall( s, 'INFOGET;{:2x}'.format(i[0]) )
			param, value = ret.strip().split(';')
			value = int(value, 16)
			try:
				format = i[3]
				if format & signed:
					if value >> (i[2]-1):
						value -= (1<<i[2])
				if format & percent:
					value = '{}%'.format(value)
			except IndexError:
				pass
			qLog( 'status', u'{}={}'.format(i[1], value) )
	
	beaconFields = (
		('decoderID', 4),
		('loopstatus', 1, (
				'OK',
				'Unplugged/Broken Cable',
				'Underpower',
				'Overvoltage',
			)
		),
		('mode', 2),
		('loopData', 2),
		('loopPower', 2),
		('channel', 1),
		('loopID', 1),
		('powerstatus', 1, (
				'12V',
				'USB',
				'Battery',
			)
		),
		('voltageAndBattery', 2),
	)
	def parseBeacon( buf ):
		beacon = []
		dataFields = buf.split(';', len(beaconFields)+1 )
		for data, info in zip(dataFields, beaconFields):
			try:
				v = int(data, 16)
			except ValueError:
				v = data
			try:
				v = info[2][v]
			except IndexError:
				pass
			if info[0] == 'voltageAndBattery':
				if beacon['powerstatus'] == 'Battery':
					v = '{}hrs'.format( v )
				else:
					v = '{:.1f}V'.format( v / 10.0 )
			beacon.append( (info[0], v) )
		return beacon
	
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
	)
	def parseTagTime( line, lineNo, errors ):
		fields = line.split(';', len(passingInfo)+1)
		info = {key: fields[i] if type is None else int(fields[i], 16)
			for i, (key, type) in enumerate(passingInfo) }
		return info['transponder-id'], timestampToDateTime(info['timestamp'])
	
	while keepGoing():
		if s:
			try:
				s.close()
			except Exception as e:
				pass
			time.sleep( delaySecs )
		
		#-----------------------------------------------------------------------------------------------------
		qLog( 'connection', u'{}{}'.format(_('Attempting to connect to RaceResult reader on COM'), comPort) )
		try:
			s = serial.Serial( port='COM{}'.format(comPort), baudrate=19200,
				timeout=timeoutSecs, write_timeout=timeoutSecs )
			s.open()
		except Exception as e:
			qLog( 'connection', u'{}: {}'.format(_('Connection to RaceResult reader failed'), e) )
			s, status, startOperation = None, None, None
			
			qLog( 'connection', u'{}'.format(_('Attempting AutoDetect...')) )
			comPortAuto = AutoDetect( callback = autoDetectCallback )
			if comPortAuto is not None:
				qLog( 'connection', u'{}{}'.format(_('AutoDetect RaceResult at COM'), comPort) )
				comPort = comPortAuto
			else:
				time.sleep( delaySecs )
			continue

		#-----------------------------------------------------------------------------------------------------
		# Enable ASCII mode.
		try:
			ret = makeCall( s, 'ASCII' )
		except ValueError:
			continue
		time.sleep( 0.2 )
		s.reset_input_buffer()
			
		#-----------------------------------------------------------------------------------------------------
		# Switch to timing mode.
		try:
			ret = makeCall( s, 'CONFSET;05;06' )
		except ValueError:
			continue
		
		#-----------------------------------------------------------------------------------------------------
		# Report on system info.
		try:
			querySystemInfo( s )
		except:
			continue
		
		#-----------------------------------------------------------------------------------------------------
		# Display a warning if the loop id is not zero (as recommended)
		try:
			ret = makeCall( s, 'CONFGET;07' )
		except ValueError:
			continue
		loopID = int(ret.strip(), 16)
		if loopID != 0:
			qLog( 'reader', u'{} "{}"'.format(_('Warning: Loop ID != 0'), loopID) )			
				
		#-----------------------------------------------------------------------------------------------------
		# Get the epoch reference.
		try:
			ret = makeCall( s, 'EPOCHREFGET' )
		except ValueError:
			continue
		fields = ret.strip().split(';')
		ref_epoch, ref_timestamp = int(fields[0], 16), int(fields[1], 16)
		
		# If the epoch reference is zero, the box has been rebooted.
		# Set it to the computer's time.
		if ref_epoch == 0 and ref_timestamp == 0:
			try:
				ret = makeCall( s, 'EPOCHREFSET;{:08x}'.format(int(time.time())) )
			except ValueError:
				continue
			fields = ret.strip().split(';')
			ref_epoch, ref_timestamp = int(fields[0], 16), int(fields[1], 16)
		
		# Check if the reader has been on for two days and we need to readjust the epoch to avoid overflow.
		# This will also update any internal times still in the reader's buffer.
		try:
			ret = makeCall( s, 'TIMESTAMPGET' )
		except ValueError:
			continue
		cur_timestamp = int(ret.strip(), 16)
		
		if cur_timestamp > 44236800:
			try:
				ret = makeCall( s, 'EPOCHREFADJ1D' )
			except ValueError:
				continue
			fields = ret.strip().split(';')
			ref_epoch, ref_timestamp = int(fields[0], 16), int(fields[1], 16)			
		
			# Get another timestamp based on the adjusted epoch.
			try:
				ret = makeCall( s, 'TIMESTAMPGET' )
			except ValueError:
				continue
			cur_timestamp = int(ret.strip(), 16)
		
		# Compute a correction between the reader's time and the computer's time.
		readerComputerTimeDiff = datetime.datetime.now() - timestampToDateTime(cur_timestamp)
		
		# Main loop to query passings.
		tagTimes, errors, times = [], [], set()
		while keepGoing():
			
			count = 64			
			while count == 64:
				cmd = 'PASSINGGET;{:08x}'.format( passingsCur )
				try:
					ret = makeCall( cmd )
				except Exception as e:
					qLog( 'connection', u'{}: {}: "{}"'.format(cmd, _('Connection failed'), e) )
					break

				lines = ret.split( EOL )
				count = int( lines[0].split(';')[1], 16 )
			
				for i in six.moves.range( count ):
					line = lines[i+1]
					if not line:
						continue
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
					
			if tagTimes:
				sendReaderEvent( tagTimes )
				for tag, t in tagTimes:
					q.put( ('data', tag, t) )
				tagTimes, errors, times = [], [], set()
			
			time.sleep( delaySecs )
	
	# Final cleanup.
	try:
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
		for i in six.moves.range(32):
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

def StartListener( startTime=datetime.datetime.now(), comPort=1, HOST=None, PORT=None ): # HOST, PORT not used.
	global q
	global shutdownQ
	global listener
	
	StopListener()

	if Model.race:
		comPort = (comPort or getattr(Model.race, 'comPort', 1))
	
	q = Queue()
	shutdownQ = Queue()
	listener = Process( target = Server, args=(q, shutdownQ, comPort, startTime) )
	listener.name = 'RaceResultUSB Listener'
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
			StartListener( comPort=1 )
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

