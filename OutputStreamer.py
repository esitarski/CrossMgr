
import sys
import time
import atexit
import os
import datetime
import threading
from Queue import Queue, Empty

import Utils
import Model

q = None
streamer = None

terminateMessage = '<<<terminate>>>'

def Server( q, fname ):
	keepGoing = True
	while keepGoing:
		# Read all available messages from the queue.
		messages = []
		while 1:
			try:
				m = q.get( not messages )
				if m == terminateMessage:
					keepGoing = False
					q.task_done()
					break
				messages.append( m )
			except Empty:
				break
				
		# Write all messages to the stream file.
		if messages:
			try:
				with open(fname, 'ab') as f:
					f.write( ''.join(messages) )
				for m in messages:
					q.task_done()
			except IOError:
				pass

def StopStreamer():
	global q
	global streamer

	# Terminate the server process if it is running.
	if streamer:
		q.put( terminateMessage )
		
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
	streamer = threading.Thread( target = Server, args=(q, fname) )
	streamer.daemon = True
	streamer.name = 'OutputStreamer'
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
		with Model.LockRace() as race:
			if race and race.startTime:
				t = race.startTime
	if t is None:
		return
	if not streamer:
		StartStreamer()
	if streamer:
		q.put( 'start,%s\n' % t.isoformat() )

def writeRaceFinish( t = None ):
	if t is None:
		with Model.LockRace() as race:
			if race and race.finishTime:
				t = race.finishTime
	if t is None:
		return
		
	if not streamer:
		StartStreamer()
	if streamer:
		q.put( 'end,%s\n' % t.isoformat() )
		q.put( terminateMessage )

def writeNumTime( num, t ):
	if not streamer:
		StartStreamer()

	# Convert race time to days for Excel.
	if streamer:
		q.put( 'time,{:d},{:.15e}\n'.format(num, t / DaySeconds) )
		
def writeNumTimes( numTimes ):
	if not streamer:
		StartStreamer()

	# Convert race time to days for Excel.
	if streamer:
		for num, t in numTimes:
			q.put( 'time,{:d},{:.15e}\n'.format(num, t / DaySeconds) )
	else:
		print 'writeNumTimes failure:', numTimes


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
						timeStr = fields[2]
						if ':' in timeStr:
							t = Utils.StrToSeconds(timeStr)		# Convert from a time format.
						else:
							t = float(timeStr) * DaySeconds		# Convert from Excel format, (days to race seconds).
						numTimes.append( (int(fields[1]), t) )
					elif fields[0] == 'start':
						startTime = gt( fields[1] )
						endTime = None		# Reset the endTime and numTimes on start.
						numTimes = []
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
		q.put( terminateMessage )
		q.join()
	
if __name__ == '__main__':
	StartStreamer()
	count = 0
	for i in xrange(10):
		for j in xrange(5):
			writeNumTime( i+j, i )
		time.sleep( 1 )
	StopStreamer()
