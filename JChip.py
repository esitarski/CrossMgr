
import socket 
import sys
import time
import datetime
import atexit
from multiprocessing import Process, Queue
from Queue import Empty

q = None
listener = None

def socketSend( s, message ):
	sLen = 0
	while sLen < len(message):
		sLen += s.send( message[sLen:] )

def socketByLine(s):
	buffer = s.recv( 4096 )
	while 1:
		nl = buffer.find( '\n' )
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
		
def Server( q, HOST, PORT ):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	
	lastTime = datetime.time()
	lastTag = ''
	while 1:
		s.listen(1)
		conn, addr = s.accept()
		
		q.put( ('connected',) )
		
		# Send the command to start sending data.
		socketSend( conn, 'S00000\n' )
			
		for line in socketByLine( conn ):
			if not line:
				continue
			if line[0] == 'D':
				u = line.find( '_' )
				if u > 0:
					tag = line[u-6:u]
					tStr = line[u+1:u+1+11]
					hh, mm, ss = tStr.split(':')
					hh = int(hh)
					mm = int(mm)
					ss = float(ss)
					mi = int((ss - int(ss)) * 1000000)
					ss = int(ss)
					t = datetime.time( hour=hh, minute=mm, second=ss, microsecond=mi )
					if t == lastTime and tag != lastTag:
						# We received two different tags at exactly the same time.
						# Add a small offset to the time so that we preserve the relative order.
						dFull = datetime.datetime.combine( datetime.date(2011,9,27), lastTime )
						dFull += datetime.timedelta( microseconds = 100 )
						t = dFull.time()
					lastTime, lastTag = t, tag
					q.put( ('data', tag, t) )
			elif line[0] == 'N':
				q.put( ('name', line[5:].strip()) )
				
		q.put( ('disconnected',) )
		
	print 'closing...'
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
		
def StartListener( HOST = socket.gethostbyname(socket.gethostname()), PORT = 53135 ):
	global q
	global listener
	
	StopListener()
		
	q = Queue()
	listener = Process( target = Server, args=(q, HOST, PORT) )
	listener.start()
	
@atexit.register
def Cleanuplistener():
	if listener:
		listener.terminate()
	
if __name__ == '__main__':
	StartListener()
	count = 0
	while 1:
		print 'polling queue...'
		time.sleep( 1 )
		messages = GetData()
		for m in messages:
			if m[0] == 'data':
				count += 1
				print '%d: %d, %s' % (count, m[1], m[2])
			elif m[0] == 'name':
				print 'receiver name="%s"' % m[1]
			elif m[0] == 'connected':
				print 'connected'
			elif m[0] == 'disconnected':
				print 'disconnected'
		
