import wx
import sys
import time
import socket
import datetime
import atexit
import re
import os
import select

from threading import Thread as Process
from queue import Queue, Empty

import Utils
from Utils import stripLeadingZeros
import Model
from JChip import ChipReaderEvent, EVT_CHIP_READER

readerEventWindow = None
def sendReaderEvent( tagTimes ):
	if tagTimes and readerEventWindow:
		wx.PostEvent( readerEventWindow, ChipReaderEvent(tagTimes = tagTimes) )

combine = datetime.datetime.combine
reTimeChars = re.compile( r'^\d\d:\d\d:\d\d\.\d+' )

dateToday = datetime.date.today()
tSameCount = 0
tLast = None

def reset( raceDate = None ):
	global dateToday
	global tSameCount
	global tLast
	
	dateToday = raceDate or datetime.date.today()
	tLast = None
	tSameCount = 0

DEFAULT_HOST = '0.0.0.0'		# Listen to all available network cards on this computer.
DEFAULT_PORT = int(os.environ.get('MYLAPS_PORT',3097))

q = None
shutdownQ = None
listener = None

# if we get the same time, make sure we give it a small offset to make it unique, but preserve the order.
tSmall = datetime.timedelta( seconds = 0.00001 )

def parseTime( tStr, dStr=None ):
	global dateToday
	global tLast
	global tSameCount
	
	if dStr:
		dToday = datetime.date( 2000 + int(dStr[:2]), int(dStr[2:4]), int(dStr[4:]) )
	else:
		dToday = dateToday
	
	hh, mm, ss = tStr.split(':')
	t = combine(dToday, datetime.time()) + datetime.timedelta(
			seconds = (float(hh) * 60.0 * 60.0) + (float(mm)  * 60.0) + float(ss) )
	
	if tLast is None:
		tLast = t - tSmall
	
	# Add a tiny offset to equal times so the order is preserved.
	if t == tLast:
		tSameCount += 1
	else:
		tSameCount = 0
		tLast = t
	
	return t + tSmall * tSameCount if tSameCount > 0 else t

def safeRemove( lst, x ):
	while True:
		try:
			lst.remove( x )
		except ValueError:
			return

def safeAppend( lst, x ):
	if x not in lst:
		lst.append( x )
		
reUnprintable = re.compile( r'[\x00-\x19\x7f-\xff]' )
def formatAscii( s ):
	if isinstance(s, bytes):
		s = s.decode()
	
	r = []
	charsPerLine = 40
	for i in range(0, len(s), charsPerLine):
		record = s[i:i+charsPerLine]
		r.append( ''.join( '.{}'.format(c) for c in reUnprintable.sub('.', record)) )
		r.append( ''.join( '{:02x}'.format(ord(c)) for c in record ) )
	return '\n'.join( r )

def parseRecord( record ):
	return dict( f.split('=',1) for f in record.split('|') if '=' in f )

def parseMessages( messages ):
	for m in messages:
		data = parseRecord( m )
		if data:
			yield data

def Server( q, shutdownQ, HOST, PORT, startTime, test ):
	# Ensure there are no reserved characters in the severName.
	serverName = 'CrossMgr-{}'.format( re.sub( '[@$|-]', '-', socket.gethostname()) )
	
	global readerEventWindow
	
	if not readerEventWindow:
		readerEventWindow = Utils.mainWin
	
	#-----------------------------------------------------
	# Support multiple connections to MyLaps clients.
	#
	# First open the server socket.
	while True:
		server = None
		server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.setblocking( 0 )
		try:
			server.bind((HOST, PORT))
		except IOError as e:
			if e.errno == 48:
				server = None
				time.sleep(2)
				continue
			else:
				raise e
		server.listen( 5 )
		break
	
	# List of ports for select.
	inputs = [server]
	outputs = []
	
	#
	# Read and write buffers and state for MyLaps readers.
	#
	readerReadBytes, readerWriteBytes, readerName, readerComputerTimeDiff, nameReader = {}, {}, {}, {}, {}
	
	def socketWrite( s, message ):
		if message:
			message = message.encode()
			readerWriteBytes[s] += message
			if s not in outputs:
				outputs.append( s )
	
	def closeReader( s ):
		safeRemove( inputs, s )
		safeRemove( outputs, s )
		try:
			del nameReader[readerName[s]]
		except ValueError:
			pass
		for state in [readerReadBytes, readerWriteBytes, readerName, readerComputerTimeDiff]:
			state.pop( s, None )
		s.close()
	
	def qLog( category, message ):
		q.put( (category, message) )
		Utils.writeLog( 'MyLaps: {}: {}'.format(category, message) )
	
	while inputs:
		# qLog( 'waiting', 'for communication' )
		readable, writable, exceptional = select.select( inputs, outputs, inputs, 2 )
		
		try:
			# Check if we have been told to shutdown.
			shutdownQ.get_nowait()
			break
		except Empty:
			pass

		# qLog( 'waiting', 'len(readable)={}, len(writable)={}, len(exceptional)={}'.format(len(readable), len(writable), len(exceptional) ) )
		#----------------------------------------------------------------------------------
		# Handle inputs.
		#
		for s in readable:
			if s is server:
				# This is the listener.  Accept a connection from a MyLaps reader.
				connCur, addr = s.accept()
				connCur.setblocking( 0 )
				inputs.append( connCur )
				readerReadBytes[connCur], readerWriteBytes[connCur] = b'', b''
				qLog( 'connection', 'established {}'.format(addr) )
				continue
			
			# This socket is a data socket.  Get the data.  Assume utf8 encoding.
			try:
				data = s.recv( 4096 )
			except Exception as e:
				qLog( 'connection', 'error: {}'.format(e) )
				data = None
			
			if not data:
				# No data - close this socket.
				qLog( 'connection', 'disconnected: {}'.format(readerName.get(s, '<unknown>')) )
				closeReader( s )
				continue
			
			# Accumulate the data.
			readerReadBytes[s] += data
			if not readerReadBytes[s].endswith(b'$'):
				continue	# Missing delimiter - need more data.
				
			# Process all delimited messages even if they come in the same buffer.
			tagTimes = []
			records = readerReadBytes[s].decode().split('$')
			readerReadBytes[s] = b''
			for record in records:
				record = record.strip()
				if not record:
					continue
				
				components	= record.split('@')
				reader  	= components[0]
				cmd			= components[1]
				
				try:
					if cmd == 'Passing':
						# Passing data from MyLaps.
						messageNumber	= components[-2]
						passings		= components[2:-2]
						
						for data in parseMessages(passings):
							try:
								tag		= stripLeadingZeros( data['c'] )
								t		= parseTime( data['t'], data['d'] )
								q.put( ('data', tag, t) )
								tagTimes.append( (tag, t) )
							except Exception as e:
								q.put( ('exception', '{}: {}'.format(e, data)) )		
					
						# Acknowledge that we received the passings so MyLaps doesn't retransmit them.
						socketWrite( s, '{}@AckPassing@{}@$'.format(serverName, messageNumber) )

					elif cmd == 'Pong':
						# The MyLaps client is connecting.  Acknowledge the connection and configure the info to receive.
						# Read parameters:    c=Chip Code|d=date|utc=milliseconds in UTC time
						# Device parameters:  time=time on the device in utc milliseconds.
						readerName[s]		= reader
						nameReader[reader]	= s
						
						# Acknowledge the Pong.
						# Return the chip, time and date for Passings.
						socketWrite( s, '{}@AckPong@Version2.1@c|t|d@$'.format(serverName) )
						
					elif cmd == 'Ping':
						# The MyLaps client is checking the connection.
						# Acknowledge the Ping.
						socketWrite( s, '{}@AckPing@$'.format(serverName) )
						
					elif cmd == 'Marker':
						messageNumber	= components[-2]
						markers			= components[2:-2]

						# Acknowledge the markers.
						socketWrite( s, '{}@AckMarker@{}@$'.format(serverName, messageNumber) )

						for data in parseMessages(markers):
							if data.get('mt', None) == 'Gunshot':
								startTimeNew = parseTime( data['t'] )
								q.put( ('marker', 'gunshot', startTimeNew) )
								race = Model.race
								if not test and race and not race.isFinished():
									race.startTime = startTimeNew
									race.setChanged()
									wx.CallLater( 1, Utils.refresh )
						
					else:
						q.put( ('unknown', record ) )
						
				except (ValueError, KeyError, IndexError) as e:
					qLog( 'exception', '{}: {}'.format(record, e) )
					pass
			
			sendReaderEvent( tagTimes )
		#----------------------------------------------------------------------------------
		# Handle outputs.
		#
		for s in writable:
			# Write out the waiting bytes.  If we sent it all, remove it from the outputs list.
			# Send each command in its own call.
			try:
				buf = readerWriteBytes[s]
				buf = buf[:buf.find(b'$')+1]
				readerWriteBytes[s] = readerWriteBytes[s][s.send(buf):]
			except Exception as e:
				qLog( 'exception', 'send error: {}'.format(e) )
				readerWriteBytes[s] = ''
			if not readerWriteBytes[s]:
				safeRemove( outputs, s )
			
		#----------------------------------------------------------------------------------
		# Handle exceptional list.
		#
		for s in exceptional:
			# Close the socket and remove its state.
			closeReader( s )
	
	server.close()

def GetData():
	data = []
	while True:
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
		
def StartListener( startTime = datetime.datetime.now(),
					HOST = DEFAULT_HOST, PORT = DEFAULT_PORT, test=False ):
	global q
	global shutdownQ
	global listener
	global dateToday
	dateToday = startTime.date()
	
	StopListener()
	
	q = Queue()
	shutdownQ = Queue()
	listener = Process( target = Server, args=(q, shutdownQ, HOST, PORT, startTime, test) )
	listener.name = 'MyLaps Listener'
	listener.daemon = True
	listener.start()
	
def IsListening():
	return listener is not None
	
@atexit.register
def CleanupListener():
	global shutdownQ
	global listener
	if listener and listener.is_alive():
		shutdownQ.put( 'shutdown' )
		listener.join()
	listener = None
	
if __name__ == '__main__':
	StartListener()
	
	count = 0
	for count in range(50):
		time.sleep( 1 )
		sys.stdout.write( '.' )
		messages = GetData()
		if messages:
			sys.stdout.write( '\n' )
		for m in messages:
			print( m )
		sys.stdout.flush()
	
	StopListener()
