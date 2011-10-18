
import sys
import time
import atexit
import os
import datetime
from multiprocessing import Process, Queue
from Queue import Empty

import Utils
import Model

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

def gt( dt_str ):
	dt, _, us = dt_str.partition(".")
	dt= datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
	us= int(us.rstrip("Z"), 10)
	return dt + datetime.timedelta(microseconds=us)

def writeRaceStart( t = None ):
	if t is None:
		if Model.race and Model.race.startTime:
			t = Model.race.startTime
	if t is None:
		return
	if not streamer:
		StartStreamer()
	if streamer:
		q.put( 'start,%s\n' % t.isoformat() )

def writeRaceFinish( t = None ):
	if t is None:
		if Model.race and Model.race.finishTime:
			t = Model.race.finishTime
	if t is None:
		return
	if not streamer:
		StartStreamer()
	if streamer:
		q.put( 'end,%s\n' % t.isoformat() )

def writeNumTime( num, t ):
	if not streamer:
		StartStreamer()

	# Convert race time to days for Excel.
	if streamer:
		q.put( 'time,{:d},{:.15e}\n'.format(num, t / DaySeconds) )

def ReadStreamFile( fname = None ):
	if not fname:
		fname = getFileName()
	
	startTime = None
	endTime = None
	numTimes = []
	try:
		with open(fname, 'rb') as f:
			for line in f:
				line = line.strip()
				if not line or line[0] == '#':
					continue
				try:
					fields = line.split(',')
					if fields[0] == 'time':
						# Convert from days to race seconds.
						numTimes.append( (int(fields[1]), float(fields[2]) * DaySeconds) )
					elif fields[0] == 'start':
						startTime = gt( fields[1] )
					elif fields[0] == 'end':
						endTime = gt( fields[1] )
				except (ValueError, IndexError):
					pass
	except IOError:
		pass
	if startTime is None and numTimes:
		startTime = datetime.datetime.now() - datetime.timedelta( seconds = numTimes[0][1] )
	return startTime, endTime, numTimes
	
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
