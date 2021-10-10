import types
import datetime

class FrameCircBuf:
	def __init__( self, bufSize = 75 ):
		self.bufSize = bufSize
		self.tSet = set()		# Times in the circular buffer.
		self.reset( bufSize )
		
	def reset( self, bufSize = None ):
		if bufSize is not None:
			self.bufSize = bufSize
		self.clear()

	def clear( self ):
		t = datetime.datetime.now() - datetime.timedelta( seconds=10*60 )
		dt = datetime.timedelta( seconds = 0.001 )
		self.times = [t + dt*i for i in range(self.bufSize)]
		self.frames = [None] * self.bufSize
		self.tSet.clear()
		self.iStart = 0
		
	def getT( self, i ):
		return self.times[(i+self.iStart)%self.bufSize]
		
	def getFrame( self, i ):
		return self.frames[(i+self.iStart)%self.bufSize]

	def append( self, t, frame ):
		''' Replace the oldest frame and time. Ignore frames with a time we already have. '''
		if t not in self.tSet and frame is not None:
			iStart = self.iStart
			self.tSet.discard( self.times[iStart] )
			self.tSet.add( t )
			
			self.times[iStart] = t
			self.frames[iStart] = frame
			
			self.iStart = (iStart + 1) % self.bufSize

	def bisect_left( self, t ):
		iStart = self.iStart
		bufSize = self.bufSize
		iLeft, iRight = 0, bufSize
		times = self.times
		while iRight - iLeft > 1:
			iMid = (iRight + iLeft) >> 1
			if t < times[(iMid+iStart) % bufSize]:
				iRight = iMid
			else:
				iLeft = iMid
		return iLeft
		
	def getTimeFrames( self, tStart, tEnd, tsSeen ):
		bufSize = self.bufSize
		iStart = self.iStart
		
		times, frames = [], []
		if self.times[(iStart + bufSize-1) % bufSize] <= tEnd:
			# The last time in the circular buffer is within the time range.
			# Collect the buffer elements in reverse order.
			for j in range(bufSize-1, -1, -1):
				k = (j+iStart)%bufSize
				t = self.times[k]
				if t < tStart:
					break
				if t not in tsSeen:
					times.append( t )
					frames.append( self.frames[k] )
					tsSeen.add( t )
			
			times.reverse()		
			frames.reverse()
		else:	
			# Use binary search to find the start of the time range.
			# Collect the buffer elements in forward order.
			i = self.bisect_left( tStart )
			if i < bufSize:
				for j in range(i, bufSize):
					k = (j+iStart)%bufSize
					t = self.times[k]
					if t > tEnd:
						break
					if t not in tsSeen:
						times.append( t )
						frames.append( self.frames[k] )
						tsSeen.add( t )
		
		return times, frames
		
	def getTimeFramesClosest( self, t, closestFrames, tsSeen ):
		i = self.bisect_left( t )
		
		iStart = self.iStart
		bufSize = self.bufSize
		times, frames = [], []
		for j in range(max(0, i-2), min(bufSize, i+2)):
			k = (j+iStart)%bufSize
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
