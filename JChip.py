import wx
import wx.lib.newevent
import os
import re

import sys
import time
import atexit
import select
import socket
import datetime

from threading import Thread as Process
from queue import Queue, Empty

import Utils
import Model

ChipReaderEvent, EVT_CHIP_READER = wx.lib.newevent.NewEvent()

stripLeadingZeros = Utils.stripLeadingZeros

readerEventWindow = None
def sendReaderEvent( tagTimes ):
	if tagTimes and readerEventWindow:
		wx.PostEvent( readerEventWindow, ChipReaderEvent(tagTimes = tagTimes) )

combine = datetime.datetime.combine
reTimeChars = re.compile( r'^\d\d:\d\d:\d\d\.\d+' )

CR = '\r'			# JChip delimiter
CRByte = b'\r'

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
DEFAULT_PORT = int(os.environ.get('JCHIP_REMOTE_PORT',53135))

q = None
shutdownQ = None
listener = None

# if we get the same time, make sure we give it a small offset to make it unique, but preserve the order.
tSmall = datetime.timedelta( seconds = 0.00001 )
tDay = datetime.timedelta( days = 1 )

def parseTime( tStr, day = 0 ):
	global dateToday
	global tLast
	global tSameCount
	
	hh, mm, ss = tStr.split(':')
	t = combine(dateToday, datetime.time()) + datetime.timedelta(
			seconds = (float(hh) * 60.0 * 60.0) + (float(mm)  * 60.0) + float(ss) )
	
	t += tDay * day
	
	if tLast is None:
		tLast = t - tSmall
	
	# Add a small offset to equal times so the order is preserved.
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
	r = []
	charsPerLine = 40
	for i in range(0, len(s), charsPerLine):
		line = s[i:i+charsPerLine]
		r.append( ''.join( '.{}'.format(c) for c in reUnprintable.sub('.', line)) )
		r.append( ''.join( '{:02x}'.format(ord(c)) for c in line ) )
	return '\n'.join( r )
	
def Server( q, shutdownQ, HOST, PORT, startTime ):
	global readerEventWindow
	
	if not readerEventWindow:
		readerEventWindow = Utils.mainWin
	
	#-----------------------------------------------------
	# Support multiple connections to a JChip client.
	# If we get a Address Already in use, we wait some time and try again
	#
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
	# Read and write buffers and state for JChip readers.
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
		except Exception as e:
			pass
		for state in [readerReadBytes, readerWriteBytes, readerName, readerComputerTimeDiff]:
			state.pop( s, None )
		s.close()
	
	def qLog( category, message ):
		q.put( (category, message) )
		Utils.writeLog( 'JChip: {}: {}'.format(category, message) )
	
	while inputs:
		# qLog( 'waiting', 'for communication' )
		readable, writable, exceptional = select.select( inputs, outputs, inputs, 2 )
		
		try:
			# Check if we have been told to shutdown.
			shutdownQ.get_nowait()
			break
		except Empty:
			pass

		# qLog( 'waiting', 'len(readable)=%d, len(writable)=%d, len(exceptional)=%d' % (len(readable), len(writable), len(exceptional) ) )
		#----------------------------------------------------------------------------------
		# Handle inputs.
		#
		for s in readable:
			if s is server:
				# This is the listener.  Accept the connection from a JChip reader.
				connCur, addr = s.accept()
				connCur.setblocking( 0 )
				inputs.append( connCur )
				readerReadBytes[connCur], readerWriteBytes[connCur] = b'', b''
				qLog( 'connection', 'established {}'.format(addr) )
				continue
			
			# This socket is a data socket.  Get the data.
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
			
			# Accumulate the data from this socket.
			readerReadBytes[s] += data
			if not readerReadBytes[s].endswith( CRByte ):
				continue	# Missing delimiter - need to get more data.
				
			# The buffer is delimited.  Decode from utf8.  Process the messages.
			tagTimes = []
			lines = readerReadBytes[s].decode().split( CR )
			readerReadBytes[s] = b''
			for line in lines:
				line = line.strip()
				if not line:
					continue
				try:
					if line.startswith( 'D' ):
						# The tag and time are always separated by at least one space.
						iSpace = line.find( ' ' )
						if iSpace < 0:
							qLog( 'error', line.strip() )
							continue
						tag = line[2:iSpace]	# Skip the D and first initial letter (always the same).
						
						# Find the first colon of the time and parse the time working backwards.
						iColon = line.find( ':' )
						if iColon < 0:
							qLog( 'error', line.strip() )
							continue
							
						m = reTimeChars.match( line[iColon-2:] )
						if not m:
							qLog( 'error', line.strip() )
							continue
						tStr = m.group(0)
						
						# Find the second field separated by a space after the time.
						# The second character of the field is the day count.
						iSecondField = line.find( ' ', iColon ) + 1
						if iSecondField >= 0:
							try:
								day = int(line[iSecondField+1:iSecondField+2])
							except Exception:
								day = 0
						
						try:
							iDate = line.index( 'date=' ) + 5
							YYYY, MM, DD = int(line[iDate:iDate+4]), int(line[iDate+4:iDate+6]), int(line[iDate+6:iDate+8])
							if Model.race and Model.race.isRunning():
								raceStartTime = Model.race.startTime
								startDate = datetime.date( raceStartTime.year, raceStartTime.month, raceStartTime.day )
								tagDate = datetime.date( YYYY, MM, DD )
								day = (tagDate - startDate).days
						except ValueError:
							pass
						
						t = parseTime( tStr, day )
						t += readerComputerTimeDiff.get(s, datetime.timedelta())
						
						tag = stripLeadingZeros(tag)
						q.put( ('data', tag, t) )
						tagTimes.append( (tag, t) )
						
					elif line.startswith( 'N' ):
						name = line[5:].strip()		# Skip the cmd and current number of recorded times.
						
						# Check if this reader is known to us already.
						# If so, the reader has dropped its previous connection and is reconnecting.
						# Close the previous connection as it is no longer needed.
						if name in nameReader:
							s_dropped = nameReader[name]
							qLog( 'transmitting', '"{}" is reconnecting'.format(readerName[s]) )
							closeReader( s_dropped )
						
						readerName[s] = name
						nameReader[name] = s
						q.put( ('name', name) )
						
						# Now, get the reader's current time.
						cmd = 'GT'
						qLog( 'transmitting', '{} command to "{}" (gettime)'.format(cmd, readerName[s]) )
						socketWrite( s, '{}{}'.format(cmd, CR) )
					
					elif line.startswith( 'GT' ):
						tNow = datetime.datetime.now()
						
						iStart = 3
						hh, mm, ss, hs = [int(line[i:i+2]) for i in range(iStart, iStart + 4 * 2, 2)]
						try:
							iDate = line.index( 'date=' ) + 5
							YYYY, MM, DD = int(line[iDate:iDate+4]), int(line[iDate+4:iDate+6]), int(line[iDate+6:iDate+8])
							tJChip = datetime.datetime( YYYY, MM, DD, hh, mm, ss, hs * 10000 )
						except ValueError:
							tJChip = datetime.datetime.combine( tNow.date(), datetime.time(hh, mm, ss, hs * 10000) )
						except Exception:
							tJChip = datetime.datetime.combine( tNow.date(), datetime.time(hh, mm, ss, hs * 10000) )
							
						readerComputerTimeDiff[s] = tNow - tJChip
						
						qLog( 'getTime', '({})={:02d}:{:02d}:{:02d}.{:02d}'.format(line[2:].strip(), hh,mm,ss,hs) )
						rtAdjust = readerComputerTimeDiff[s].total_seconds()
						if rtAdjust > 0:
							behindAhead = 'Behind'
						else:
							behindAhead = 'Ahead'
							rtAdjust *= -1
						qLog( 'timeAdjustment', 
								'"{}" is: {} {} (relative to computer)'.format(
									readerName.get(s, '<<unknown>>'),
									behindAhead,
									Utils.formatTime(rtAdjust, True)
								) )
						
						# Send command to start sending data.
						cmd = 'S0000'
						qLog( 'transmitting', '{} command to "{}" (start transmission)'.format(
							cmd, readerName.get(s, '<<unknown>>')) )
						socketWrite( s, '{}{}'.format(cmd, CR) )
					else:
						q.put( ('unknown', line ) )
						
				except (ValueError, KeyError, IndexError) as e:
					qLog( 'exception', '{}: {}'.format(line, e) )
					pass
			
			sendReaderEvent( tagTimes )
		#----------------------------------------------------------------------------------
		# Handle outputs.
		#
		for s in writable:
			# Write out the waiting data.
			# One call per command.
			# If we sent it all, remove it from the outputs list.
			try:
				buf = readerWriteBytes[s]
				buf = buf[:buf.find(CRByte)+1]
				readerWriteBytes[s] = readerWriteBytes[s][s.send(buf):]
			except Exception as e:
				qLog( 'exception', 'send error: {}'.format(e) )
				readerWriteBytes[s] = b''
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
	listener = Process( target = Server, args=(q, shutdownQ, HOST, PORT, startTime) )
	listener.name = 'JChip Listener'
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
		
