import types
import datetime
from bisect import bisect_left

class CircAsFlat:
	__slots__ = ('arr', 'iStart', 'iMax')

	def __init__( self, arr, iStart, iMax ):
		self.arr = arr
		self.iStart = iStart
		self.iMax = iMax
		
	def __getitem__( self, i ):
		return self.arr[(i + self.iStart) % self.iMax]
		
	def __len__( self ):
		return self.iMax

class FrameCircBuf:
	def __init__( self, bufSize = 75 ):
		self.bufSize = bufSize
		self.reset( bufSize )
		
	def reset( self, bufSize = None ):
		if bufSize is None:
			bufSize = self.bufSize
		t = datetime.datetime.now() - datetime.timedelta( seconds = bufSize )
		dt = datetime.timedelta( seconds = 0.001 )
		times = []
		for i in range(bufSize):
			times.append( t )
			t += dt
		self.iStart = 0
		self.times = times
		self.bufSize = bufSize
		self.clear()

	def clear( self ):
		self.frames = [None for i in range(self.bufSize)]
		self.tSet = set()	# Set of times in the circular buffer.
		
	def getT( self, i ):
		return self.times[(i+self.iStart)%self.bufSize]
		
	def getFrame( self, i ):
		return self.frames[(i+self.iStart)%self.bufSize]

	def append( self, t, frame ):
		''' Replace the oldest frame and time. '''
		if frame is not None and t not in self.tSet:
			iStart = self.iStart
			self.tSet.discard( self.times[iStart] )
			self.times[iStart] = t
			self.tSet.add( t )
			
			self.frames[iStart] = frame
			self.iStart = (iStart + 1) % self.bufSize

	def getTimeFrames( self, tStart, tEnd, tsSeen ):
		iStart = self.iStart
		bufSize = self.bufSize
		
		i = bisect_left( CircAsFlat(self.times, iStart, bufSize), tStart )
		if i >= bufSize:
			return [], []
		times, frames = [], []
		for j in range(i, bufSize):
			k = (j+iStart)%bufSize
			t = self.times[k]
			if t > tEnd:
				break
			if t not in tsSeen and self.frames[k] is not None:
				times.append( t )
				frames.append( self.frames[k] )
				tsSeen.add( t )
		return times, frames
		
	def getTimeFramesClosest( self, t, closestFrames, tsSeen ):
		iStart = self.iStart
		bufSize = self.bufSize
		
		i = bisect_left( CircAsFlat(self.times, iStart, bufSize), t )
		times, frames = [], []
		for j in range(max(0, i-2), min(bufSize, i+2)):
			k = (j+iStart)%bufSize
			if self.frames[k] is not None:
				times.append( self.times[k] )
				frames.append( self.frames[k] )
		
		tsClosest = set( sorted(times, key=lambda tFrame: abs(t-tFrame))[:closestFrames] )
		timesRet, framesRet = [], []
		for time, frame in zip(times, frames):
			if time in tsClosest and time not in tsSeen:
				timesRet.append( time )
				framesRet.append( frame )
				tsSeen.add( time )
		return timesRet, framesRet
		
if __name__ == '__main__':
	bufSize = 5*75
	fcb = FrameCircBuf( bufSize )
	fcb.reset( 5*25 )
	
	tStart = datetime.datetime.now()
	for i in range(fcb.bufSize):
		fcb.append( tStart + datetime.timedelta(seconds=i*1.0/25.0), None )
	
	for t in fcb.times:
		print( (t-tStart).total_seconds() )
	print()
