from __future__ import print_function

import socket 
import sys
import time
import datetime
import atexit
import math
import subprocess
import re
import wx
import wx.lib.newevent
import Utils
stripLeadingZeros = Utils.stripLeadingZeros
import select
from threading import Thread as Process
from Queue import Queue
from Queue import Empty

ChipReaderEvent, EVT_CHIP_READER = wx.lib.newevent.NewEvent()

readerEventWindow = None
def sendReaderEvent( tagTimes ):
	if tagTimes and readerEventWindow:
		wx.PostEvent( readerEventWindow, ChipReaderEvent(tagTimes = tagTimes) )

combine = datetime.datetime.combine
reTimeChars = re.compile( '^\d\d:\d\d:\d\d\.\d+' )

CR = chr( 0x0d )	# JChip delimiter

dateToday = datetime.date.today()
tSameCount = 0
tLast = None
dayCur = 0

def reset( raceDate = None ):
	global dateToday
	global tSameCount
	global tLast
	global dayCur
	
	dateToday = raceDate or datetime.date.today()
	tLast = None
	tSameCount = 0
	dayCur = 0

DEFAULT_PORT = 53135
DEFAULT_HOST = socket.gethostbyname(socket.gethostname())
if DEFAULT_HOST == '127.0.0.1':
	reSplit = re.compile('[: \t]+')
	try:
		co = subprocess.Popen(['ifconfig'], stdout = subprocess.PIPE)
		ifconfig = co.stdout.read()
		for line in ifconfig.split('\n'):
			line = line.strip()
			try:
				if line.startswith('inet addr:'):
					fields = reSplit.split( line )
					addr = fields[2]
					if addr != '127.0.0.1':
						DEFAULT_HOST = addr
						break
			except:
				pass
	except:
		pass

q = None
shutdownQ = None
listener = None

def socketSend( s, message ):
	sLen = 0
	while sLen < len(message):
		sLen += s.send( message[sLen:] )
		
def socketByLine(s):
	buffer = s.recv( 4096 )
	while 1:
		nl = buffer.find( CR )
		if nl >= 0:
			yield buffer[:nl+1]
			buffer = buffer[nl+1:]
		else:
			more = s.recv( 4096 )
			if more:
				buffer = buffer + more
			else:
				break
	if buffer:
		yield buffer

# if we get the same time, make sure we give it a small offset to make it unique, but preserve the order.
tSmall = datetime.timedelta( seconds = 0.00001 )

def parseTime( tStr ):
	global dateToday
	global tLast
	global tSameCount
	
	hh, mm, ssmi = tStr.split(':')
	
	hh, mm, ssmi = int(hh), int(mm), float(ssmi)
	mi, ss = math.modf( ssmi )
	mi, ss = int(mi * 1000000.0), int(ss)
	t = combine(dateToday, datetime.time()) + datetime.timedelta( seconds = (hh * 60.0 * 60.0) + (mm  * 60.0) + ss + mi / 1000000.0 )
	
	if tLast is None:
		tLast = t - tSmall
	
	'''
	t += datetime.timedelta( days = 1 ) * dayCur
	while t < tLast:
		t += datetime.timedelta( days = 1 )
		dayCur += 1
	'''
	
	# Add a small offset to equal times so the order is preserved.
	if t == tLast:
		tSameCount += 1
	else:
		tSameCount = 0
		tLast = t
	
	return t + tSmall * tSameCount if tSameCount > 0 else t

def safeRemove( lst, x ):
	while 1:
		try:
			lst.remove( x )
		except ValueError:
			return

def safeAppend( lst, x ):
	if x not in lst:
		lst.append( x )
		
readerComputerTimeDiff = None
def Server( q, shutdownQ, HOST, PORT, startTime ):
	global readerComputerTimeDiff
	global readerEventWindow
	readerComputerTimeDiff = None
	
	if not readerEventWindow:
		readerEventWindow = Utils.mainWin
	
	#-----------------------------------------------------
	# We support one connection to JChip.
	#
	connCur = None
	#
	# Read and write buffers for JChip reader.
	#
	readStr, writeStr = '', ''
	
	server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	server.setblocking( 0 )
	server.bind((HOST, PORT))
	server.listen( 5 )
	
	# List of ports for select.
	inputs = [server]
	outputs = []
	
	while inputs:
		# q.put( ('waiting', 'for communication' ) )
		readable, writable, exceptional = select.select( inputs, outputs, inputs, 2 )
		
		try:
			# Check if we have been told to shutdown.
			shutdownQ.get_nowait()
			break
		except Empty:
			pass

		# q.put( ('waiting', 'len(readable)=%d, len(writable)=%d, len(exceptional)=%d' % (len(readable), len(writable), len(exceptional) ) ) )
		#----------------------------------------------------------------------------------
		# Handle inputs.
		#
		for s in readable:
			if s is server:
				# This is the listener.  Accept the connection from JChip.
				if connCur:	# If we have an existing connection, close it and use the new one.
					safeRemove( outputs, connCur )
					safeRemove( inputs, connCur )
					connCur.close()
					connCur = None
					
				# Accept the new connection.
				connCur, addr = s.accept()
				connCur.setblocking( 0 )
				inputs.append( connCur )
				readStr, writeStr = '', ''
				q.put( ('connection', 'established {}'.format(addr) ) )
				continue
			
			# This socket is a data socket.  Get the data.
			try:
				data = s.recv( 4096 )
			except Exception as e:
				q.put( ('connection', 'error: %s' % e ) )
				data = None
			
			if not data:
				# No data - close socket and wait for a new connection.
				safeRemove( outputs, s )
				safeRemove( inputs, s )
				if s == connCur:
					connCur = None
					readStr, writeStr = '', ''
				s.close()
				q.put( ('connection', 'disconnected') )
				continue
			
			# Accumulate the data.
			readStr += data
			if not readStr.endswith( CR ):
				continue	# Missing delimiter - need to get more data.
				
			# The message is delimited.  Process the messages.
			tagTimes = []
			lines = readStr.split( CR )
			readStr = ''
			for line in lines:
				line = line.strip()
				if not line:
					continue
				try:
					if line.startswith( 'D' ):
						# The tag and time are always separated by at least one space.
						iSpace = line.find( ' ' )
						if iSpace < 0:
							q.put( ('error', line.strip() ) )
							continue
						tag = line[2:iSpace]	# Skip the D and first initial letter (always the same).
						
						# Find the first colon of the time and parse the time working backwards.
						iColon = line.find( ':' )
						if iColon < 0:
							q.put( ('error', line.strip() ) )
							continue
							
						m = reTimeChars.match( line[iColon-2:] )
						if not m:
							q.put( ('error', line.strip() ) )
							continue
						tStr = m.group(0)
						
						t = parseTime( tStr )
						t += readerComputerTimeDiff
						
						tag = stripLeadingZeros(tag)
						q.put( ('data', tag, t) )
						tagTimes.append( (tag, t) )
						
					elif line.startswith( 'N' ):
						q.put( ('name', line[5:].strip()) )
						
						# Get the reader's current time.
						cmd = 'GT'
						q.put( ('transmitting', '%s command to JChip receiver (gettime)' % cmd) )
						writeStr += '%s%s' % (cmd, CR)
						safeAppend( outputs, s )
					
					elif line.startswith( 'GT' ):
						tNow = datetime.datetime.now()
						
						iStart = 3
						hh, mm, ss, hs = [int(line[i:i+2]) for i in xrange(iStart, iStart + 4 * 2, 2)]
						tJChip = datetime.datetime.combine( tNow.date(), datetime.time(hh, mm, ss, hs * 10000) )
						readerComputerTimeDiff = tNow - tJChip
						
						q.put( ('getTime', '%s=%02d:%02d:%02d.%02d' % (line[2:].strip(), hh,mm,ss,hs)) )
						rtAdjust = readerComputerTimeDiff.total_seconds()
						if rtAdjust > 0:
							behindAhead = 'Behind'
						else:
							behindAhead = 'Ahead'
							rtAdjust *= -1
						q.put( ('timeAdjustment', 
								"JChip receiver's clock is: %s %s (relative to computer)" %
									(behindAhead, Utils.formatTime(rtAdjust, True))) )
						
						# Send command to start sending data.
						cmd = 'S0000'
						q.put( ('transmitting', '%s command to JChip receiver (start transmission)' % cmd) )
						writeStr += '%s%s' % (cmd, CR)
						safeAppend( outputs, s )
					else:
						q.put( ('unknown', line ) )
						
				except (ValueError, KeyError, IndexError):
					q.put( ('exception', line ) )
					pass
			
			sendReaderEvent( tagTimes )
		#----------------------------------------------------------------------------------
		# Handle outputs.
		#
		for s in writable:
			# Write out the waiting data.  If we sent it all, remove it from the outputs list.
			try:
				writeStr = writeStr[s.send(writeStr):]
			except Exception as e:
				q.put( ('exception', 'send error: %s' % e) )
				writeStr = ''
			if not writeStr:
				outputs.remove( s )
			
		#----------------------------------------------------------------------------------
		# Handle exceptional list.
		#
		for s in exceptional:
			# Close the socket.  Remove it from the inputs and outputs list.
			safeRemove( inputs, s )
			safeRemove( outputs, s )
			s.close()
			readStr, writeStr = '', ''
			
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
	listener.name = 'JChip Listener'
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
		