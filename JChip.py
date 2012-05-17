from __future__ import print_function

import socket 
import sys
import time
import datetime
import atexit
import math
import subprocess
import re
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

def parseTime( tStr ):
	global dateToday
	hh, mm, ssmi = tStr.split(':')
	hh, mm, ssmi = int(hh), int(mm), float(ssmi)
	mi, ss = math.modf( ssmi )
	mi, ss = int(mi * 1000000.0), int(ss)
	return combine( dateToday, datetime.time(hour=hh, minute=mm, second=ss, microsecond=mi) )

def Server( q, HOST, PORT, startTime ):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	
	tSmall = datetime.timedelta( microseconds = 100 )
	
	lastTime = datetime.datetime.now()
	lastTag = ''
	while 1:
		s.listen(1)
		conn, addr = s.accept()
		
		q.put( ('connected', 'JChip receiver',) )
		q.put( ('waiting', 'for JChip receiver to respond',) )
		
		for line in socketByLine( conn ):
			if not line:
				continue
			try:
				if line[0] == 'D':
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
					if t < startTime:
						continue
						
					if t < lastTime and tag != lastTag:
						# We received two different tags at exactly the same time.
						# Add a small offset to the time so that we preserve the relative order.
						t += tSmall
					lastTime, lastTag = t, tag
					q.put( ('data', tag, t) )
				elif line[0] == 'N':
					q.put( ('name', line[5:].strip()) )
					
					cmd = 'S00000'
					q.put( ('transmitting', '%s command to JChip receiver' % cmd) )
					socketSend( conn, '%s%s' % (cmd, CR) )
				else:
					q.put( ('unknown', line ) )
			
			except (ValueError, KeyError, IndexError):
				q.put( ('exception', line ) )
				pass
				
		q.put( ('disconnected',) )
		
	print( 'closing...' )
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
	dateToday = datetime.date.today()
	
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
			elif m[0] == 'error':
				print( 'error: %s' % m[1] )
		sys.stdout.flush()
		
