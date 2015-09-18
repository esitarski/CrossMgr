from __future__ import print_function

import socket 
import sys
import time
import datetime
import atexit
import re
import wx
import wx.lib.newevent
import Utils
import Model
from threading import Thread as Process
from Queue import Queue
from Queue import Empty
import JChip
from RaceResultImport import parseTagTime

ChipReaderEvent, EVT_CHIP_READER = JChip.ChipReaderEvent, JChip.EVT_CHIP_READER

readerEventWindow = None
def sendReaderEvent( tagTimes ):
	if tagTimes and readerEventWindow:
		wx.PostEvent( readerEventWindow, ChipReaderEvent(tagTimes = tagTimes) )

EOL = chr( '\r\n' )	# RaceResult delimiter
len_EOL = len(EOL)

DEFAULT_PORT = 3601
DEFAULT_HOST = '0.0.0.0'		# Listen to all available network cards on this computer.

q = None
shutdownQ = None
listener = None

def socketSend( s, message ):
	sLen = 0
	while sLen < len(message):
		sLen += s.send( message[sLen:] )
		
def socketByLine( s ):
	buffer = s.recv( 4096 )
	while 1:
		nl = buffer.find( EOL )
		if nl >= 0:
			yield buffer[:nl+len_EOL]
			buffer = buffer[nl+len_EOL:]
		else:
			more = s.recv( 4096 )
			if more:
				buffer = buffer + more
			else:
				break
	if buffer:
		yield buffer

def socketReceiveLine( s ):
	buffer = s.recv( 4096 )
	while 1:
		nl = buffer.find( EOL )
		if nl < 0:
			more = s.recv( 4096 )
			if more:
				buffer = buffer + more
			else:
				break
	return buffer
		
# if we get the same time, make sure we give it a small offset to make it unique, but preserve the order.
tSmall = datetime.timedelta( seconds = 0.000001 )

reNonDigit = re.compile( '[^0-9]+' )
def Server( q, shutdownQ, HOST, PORT, startTime ):
	global readerEventWindow
	
	if not readerEventWindow:
		readerEventWindow = Utils.mainWin
	
	readerTime = None
	tAdjust = None
	timeoutSecs = 5
	delaySecs = 3
	passingsCur = 0
	status = None
	
	def qLog( category, message ):
		q.put( (category, message) )
		Utils.writeLog( u'RaceResult: {}: {}'.format(category, message) )
	
	def keepGoing():
		try:
			# Check if we have been told to shutdown.
			shutdownQ.get_nowait()
			return False
		except Empty:
			return True
	
	s = None
	while keepGoing():
		if s:
			try:
				s.shutdown( socket.SHUT_RDWR )
				s.close()
				time.sleep( delaySecs )
			except Exception as e:
				pass
			s = None
		
		try:
			s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			s.connect( (HOST, PORT) )
			s.settimeout( timoutSecs )
		except Exception as e:
			qLog( ('connection', u'{}: {}'.format(_('Connection to RaceResult reader failed'), e)) )
			continue

		try:
			if status is None:
				socketSend( s, bytes('GETSTATUS{}'.format(EOL)) )
				buffer = socketReceiveLine( s )
				if buffer.startswith( 'GETSTATUS;' ):
					fields = [f.strip() for f in buffer.strip().split(';')]
					status = zip( [
							'Date', 'Time', 'HasPower', 'Antennas', 'IsInTimingMode',
							'FileNumber', 'GPSHasFix', 'Latitude', 'Longitude', 'LongInd', 'ReaderIsHealthy', 'ActiveExtConnected',
							'Channel', 'LoopID', 'LoopPower', 'LoopConnected', 'LoopUnderPower', 'Temperature',
							], fields[1:] )
					for name, value in status:
						qLog( ('status', u'{}: {}'.format(name, value)) )
				else:
					qLog( ('command', u'GETSTATUS: {} "{}"'.format(_('Unexpected return'), buffer)) )
					continue
		except Exceptions as e:
			qLog( ('connection', u'GETSTATUS: {}: "{}"'.format(_('Connection failed'), e)) )
			continue

		try:
			# Check if we have the reader time.
			if readerTime is None:
				socketSend( s, bytes('GETTIME{}'.format(EOL)) )
				buffer = socketReceiveLine( s )
				if buffer.startswith( 'GETTIME;' ):
					dt = reNonDigit.sub(' ', buffer).strip()
					fields[-1] = fields[-1].ljust(6-len(fields[-1]))	# Add zeros to convert to microseconds.
					readerTime = datetime.datetime( *[int(f) for f in dt.split()] )
					tAdjust = datetime.datetime.now() - readerTime
				else:
					qLog( ('command', u'GETTIME: {} "{}"'.format(_('Unexpected return'), buffer)) )
					continue
		except Exceptions as e:
			qLog( ('connection', u'GETTIME: {}: "{}"'.format(_('Connection failed'), e)) )
			continue
					
		try:
			# Get the current number of passings.
			socketSend( s, bytes('PASSINGS{}'.format(EOL)) )
			buffer = socketReceiveLine( s )
			if buffer.startswith( 'PASSINGS;' ):
				passingsNew = int( reNonDigit.sub(' ', buffer).strip() )
			else:
				qLog( ('command', u'PASSINGS: {} "{}"'.format(_('Unexpected return'), buffer)) )
				continue
		except Exception as e:
			qLog( ('connection', u'PASSINGS: {}: "{}"'.format(_('Connection failed'), e)) )
			continue

		if passingsNew == passingsCur:
			continue	# Nothing to do
			
		if passingsNew < passingsCur:
			passingsCur = 0
		try:
			# Get the passing data.
			socketSend( s, bytes('{}:{}{}'.format(passingsCur, passingsNew - passingsCur, EOL)) )
			errors = []
			tagTimes = []
			for i, line in enumerate(socketByLine(s))):
				tag, t = parseTagTime(line, passingsCur+i+1, errors)
				if tag and t:
					t += tAdjust
					if tagTimes and tagTimes[-1][-1] == t:	# Ensure that there are no equal times.
						t += i * tSmall
					if t >= startTime:
						tagTimes.append( (tag, t) )
					
			sendReaderEvent( tagTimes )
			passingsCur = passingsNew
		except Exception as e:
			qLog( ('connection', u'DATA: {}: "{}"'.format(_('Connection failed'), e)) )
			continue
				
	# Final cleanup.		
	try:
		s.shutdown( socket.SHUT_RDWR )
		s.close()
	except:
		pass

def StopListener():
	global q
	global listener
	global shutdownQ

	# Terminate the server process if it is running.
	if listener:
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
		
def StartListener( startTime = datetime.datetime.now(),
					HOST = DEFAULT_HOST, PORT = DEFAULT_PORT ):
	global q
	global shutdownQ
	global listener
	global dateToday
	dateToday = startTime.date()
	
	StopListener()
	
	q = Queue()
	shutdownQ = Queue()
	listener = Process( target = Server, args=(q, shutdownQ, HOST, PORT, startTime) )
	listener.name = 'RaceResult Listener'
	listener.daemon = True
	listener.start()
	
@atexit.register
def Cleanuplistener():
	global shutdownQ
	global listener
	if listener and listener.is_alive():
		shutdownQ.put( 'shutdown' )
		listener.join()
	listener = None
	
if __name__ == '__main__':
	StartListener()
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
				print( '%d: %s, %s' % (count, m[1], m[2].time()) )
			elif m[0] == 'name':
				print( 'receiver name="%s"' % m[1] )
			elif m[0] == 'connected':
				print( 'connected' )
			elif m[0] == 'disconnected':
				print( 'disconnected' )
			else:
				print( 'other: %s, %s' % (m[0], ', '.join('"%s"' % '{}'.format(s) for s in m[1:])) )
		sys.stdout.flush()
		
