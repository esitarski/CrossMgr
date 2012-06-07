from __future__ import print_function

import socket 
import sys
import time
import datetime
import atexit
import math
import subprocess
import re
import Utils
from multiprocessing import Process, Queue
from Queue import Empty

combine = datetime.datetime.combine
reTimeChars = re.compile( '^\d\d:\d\d:\d\d\.\d+' )

CR = chr( 0x0d )	# JChip delimiter
dateToday = datetime.date.today()

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
tSameCount = 0
tLast = None

def parseTime( tStr ):
	global dateToday
	global tLast
	global tSameCount
	
	hh, mm, ssmi = tStr.split(':')
	
	hh, mm, ssmi = int(hh), int(mm), float(ssmi)
	mi, ss = math.modf( ssmi )
	mi, ss = int(mi * 1000000.0), int(ss)
	t = combine( dateToday, datetime.time(hour=hh, minute=mm, second=ss, microsecond=mi) )
	
	# Add a small offset to equal times so the order is preserved.
	if t == tLast:
		tSameCount += 1
	else:
		tSameCount = 0
		tLast = t
	
	return t + tSmall * tSameCount if tSameCount > 0 else t

def Server( q, HOST, PORT, startTime ):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	
	readerComputerTimeDiff = None
	while 1:
		s.listen(1)
		conn, addr = s.accept()
		
		q.put( ('connected', 'JChip receiver',) )
		q.put( ('waiting', 'for JChip receiver to respond',) )
		
		for line in socketByLine( conn ):
			if not line:
				continue
			try:
				if line.startswith( 'D' ):
					tag = line[2:2+6]	# Skip the initial letter (always the same).
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
						
					q.put( ('data', tag, t) )
					
				elif line.startswith( 'N' ):
					q.put( ('name', line[5:].strip()) )
					
					# Get the reader's current time.
					cmd = 'GT'
					q.put( ('transmitting', '%s command to JChip receiver (gettime)' % cmd) )
					socketSend( conn, '%s%s' % (cmd, CR) )
				
				elif line.startswith( 'GT' ):
					tNow = datetime.datetime.now()
					
					iStart = 3
					hh, mm, ss, hs = [int(line[i:i+2]) for i in xrange(iStart, iStart + 4 * 2, 2)]
					tJChip = datetime.datetime.combine( tNow.date(), datetime.time(hh, mm, ss, hs * 10000) )
					readerComputerTimeDiff = tNow - tJChip
					
					q.put( ('getTime', '%s=%02d:%02d:%02d.%02d' % (line[2:].strip(), hh,mm,ss,hs)) )
					q.put( ('timeAdjustment', 
							'JChip time will be adjusted by %s to match computer' %
								Utils.formatTime(readerComputerTimeDiff.total_seconds(), True)) )
					
					# Send command to start sending data.
					cmd = 'S0000'
					q.put( ('transmitting', '%s command to JChip receiver (start transmission)' % cmd) )
					socketSend( conn, '%s%s' % (cmd, CR) )
				else:
					q.put( ('unknown', line[:-1] ) )
			
			except (ValueError, KeyError, IndexError):
				q.put( ('exception', line ) )
				pass
				
		q.put( ('disconnected',) )
		
	s.close()

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

	# Terminate the server process if it is running.
	if listener:
		listener.terminate()
	listener = None
	
	# Purge the queue.
	if q:
		while 1:
			try:
				q.get_nowait()
			except Empty:
				break
			
		q = None
		
def StartListener( startTime = datetime.datetime.now(),
					HOST = DEFAULT_HOST, PORT = DEFAULT_PORT ):
	global q
	global listener
	global dateToday
	dateToday = startTime.date()
	
	StopListener()
	
	q = Queue()
	listener = Process( target = Server, args=(q, HOST, PORT, startTime) )
	listener.start()
	
@atexit.register
def Cleanuplistener():
	if listener:
		listener.terminate()
	
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
				print( 'other: %s, %s' % (m[0], ', '.join('"%s"' % str(s) for s in m[1:])) )
		sys.stdout.flush()
		
