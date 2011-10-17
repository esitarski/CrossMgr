
import sys
import time
import atexit
from multiprocessing import Process, Queue
from Queue import Empty

import Utils

q = None
streamer = None

def Server( q, fname ):
	while 1:
		# Wait for something to show up on the queue.
		messages = [q.get()]
		
		# Read all messages from the queue.
		while 1:
			try:
				m = q.get_nowait()
				messages.append( m )
			except Empty:
				break
		
		# Write all messages to the stream file.
		try:
			with open(fname, 'ab') as f:
				f.write( ''.join(messages) )
		except IOError:
			pass

def StopStreamer():
	global q
	global streamer

	# Terminate the server process if it is running.
	if streamer:
		time.sleep( 0.2 )
		streamer.terminate()
		
	streamer = None

def getFileName( fname = None ):
	if not fname:
		fname = Utils.getFileName()
	if not fname:
		fname = 'Race.cmn'
	if fname.endswith('.cmn'):
		fname = fname[:-4]
	return fname + 'Input.csv'
	
def DeleteStreamerFile( fname = None ):
	if not fname:
		fname = getFileName()
	try:
		os.remove( fname )
	except:
		pass

def StartStreamer( fname = None ):
	global q
	global streamer
	
	if not fname:
		fname = getFileName()
	
	StopStreamer()
	q = Queue()
	streamer = Process( target = Server, args=(q, fname) )
	streamer.start()

def write( message ):
	if not streamer:
		StartStreamer()
	if streamer:
		q.put( message )

DaySeconds = 24.0 * 60.0 * 60.0
	
def writeNumTime( num, t ):
	if not streamer:
		StartStreamer()

	# Convert race time to days for Excel.
	if streamer:
		q.put( '{:d},{:.15f}\n'.format(num, t / DaySeconds) )

def ReadStreamFile( fname = None ):
	if not fname:
		fname = getFileName()
		
	numTimes = []
	try:
		with open(fname, 'rb') as f:
			for line in f:
				line = line.strip()
				if not line or line[0] == '#':
					continue
				try:
					num, tStr = line.split(',')
					# Convert from days to race seconds.
					numTimes.append( (int(num), float(tStr) * DaySeconds) )
				except ValueError:
					pass
	except IOError:
		pass
	return numTimes
	
@atexit.register
def CleanupStreamer():
	if streamer:
		streamer.terminate()
	
if __name__ == '__main__':
	StartStreamer()
	count = 0
	for i in xrange(10):
		for j in xrange(5):
			writeNumTime( i+j, i )
		time.sleep( 1 )
	StopStreamer()
