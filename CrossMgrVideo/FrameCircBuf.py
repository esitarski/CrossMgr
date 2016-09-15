import types
import datetime

class FrameCircBuf( object ):
	def __init__( self, bufSize = 75 ):
		self.reset( bufSize )
		
	def reset( self, bufSize = None ):
		if bufSize is None:
			bufSize = self.bufSize
		t = datetime.datetime.now() - datetime.timedelta( seconds = bufSize )
		dt = datetime.timedelta( seconds = 1 )
		times = []
		for i in xrange(bufSize):
			times.append( t )
			t += dt
		self.iStart = 0
		self.times = times
		self.frames = [None for i in xrange(bufSize)]
		self.bufSize = bufSize

	def clear( self ):
		self.frames = [None for i in xrange(self.bufSize)]
		
	def getT( self, i ):
		return self.times[(i+self.iStart)%self.bufSize]
		
	def getFrame( self, i ):
		return self.frames[(i+self.iStart)%self.bufSize]

	def append( self, t, frame ):
		''' Replace the oldest frame and time. '''
		iStart = self.iStart
		self.times[iStart] = t
		self.frames[iStart] = frame
		self.iStart = (iStart + 1) % self.bufSize

	def getBackFrames( self, t ):
		iStart = self.iStart
		times = self.times
		frames = self.frames
		bufSize = self.bufSize
		bufSizeMinus1 = bufSize - 1
		
		retTimes = []
		retFrames = []
		
		iPrev = iStart
		while 1:
			iPrev = (iPrev + bufSizeMinus1) % bufSize
			if iPrev == iStart or times[iPrev] < t:
				break
			retTimes.append( times[iPrev] )
			retFrames.append( frames[iPrev] )
		
		retTimes.reverse()
		retFrames.reverse()
		return retTimes, retFrames
		
if __name__ == '__main__':
	bufSize = 5*75
	fcb = FrameCircBuf( bufSize )
	fcb.reset( 5*25 )
	
	tStart = datetime.datetime.now()
	for i in xrange(fcb.bufSize):
		fcb.append( tStart + datetime.timedelta(seconds=i*1.0/25.0), None )
	
	for t in fcb.times:
		print (t-tStart).total_seconds()
	print
