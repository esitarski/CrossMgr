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
		
		# Generate a search function for the buffer size.
		stmts = [
			'def _find( self, t ):',
			' iStart = self.iStart',
			' bufSize = self.bufSize',
			' times = self.times',
		]
		self._genFind( stmts, 1, 0, self.bufSize )
		#print( '\n'.join(stmts) + '\n' )
		exec( '\n'.join(stmts) + '\n' )
		self._find = types.MethodType(_find,self)

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

	def _genFind( self, stmts, level, left, right ):
		if right - left > 1:
			mid = (left + right) // 2
			stmts.append( '{}if times[({}+iStart)%bufSize] < t:'.format(' '*level, mid ) )
			self._genFind( stmts, level + 1, mid + 1, right )
			stmts.append( '{}else:'.format(' '*level ) )
			self._genFind( stmts, level + 1, left, mid )
		else:
			if left == self.bufSize:
				stmts.append( '{}return iStart'.format(' '*level) )
			else:
				stmts.append( '{}i = ({}+iStart)%bufSize'.format(' '*level, left) )
				stmts.append( '{}return i if t <= times[i] else (i+1)%bufSize '.format(' '*level) )

	def findBeforeAfter( self, t, before = 0, after = 1, window = 2.0 ):
		i = self._find( t )
		if self.times[i] < t:
			return [], []
			
		iStart = self.iStart
		times = self.times
		frames = self.frames
		bufSize = self.bufSize
		
		retTimes = []
		retFrames = []
		
		if before and i != iStart:
			for b in xrange(1, before+1):
				k = (i-b) % bufSize
				if abs(times[k] - t).total_seconds() <= window:
					retTimes.append( times[k] )
					retFrames.append( frames[k] )
				if k == iStart:
					break
			retTimes.reverse()
			retFrames.reverse()
			
		if after:
			if abs(times[i] - t).total_seconds() <= window:
				retTimes.append( times[i] )
				retFrames.append( frames[i] )
			for a in xrange(1, after):
				k = (i+a) % bufSize
				if k == iStart:
					break
				if abs(times[k] - t).total_seconds() <= window:
					retTimes.append( times[k] )
					retFrames.append( frames[k] )
		
		return retTimes, retFrames

	def _loopFind( self, t ):
		iStart = self.iStart
		bufSize = self.bufSize
		times = self.times
		
		left = 0
		right = bufSize
		while right - left > 1:
			mid = (right + left) // 2
			if times[(mid + iStart) % bufSize] < t:
				left = mid
			else:
				right = mid
		i = (left + iStart) % bufSize
		return i if left == bufSize or t <= times[i] else (i+1) % bufSize

if __name__ == '__main__':
	bufSize = 5*75
	fcb = FrameCircBuf( bufSize )
	fcb.reset( 5*25 )
	
	tStart = datetime.datetime.now()
	for i in xrange(fcb.bufSize):
		fcb.append( tStart + datetime.timedelta(seconds=i*1.0/25.0), None )
	
	for t in fcb.times:
		print((t-tStart).total_seconds())
	print()
	
	times, frames = fcb.findBeforeAfter( tStart + datetime.timedelta(seconds=2.01), 1, 1 )
	print([(t-tStart).total_seconds() for t in times])
	
	tSearch = datetime.datetime.now() - datetime.timedelta(seconds = 4)
	i = fcb._find( tSearch )
	print(i, tSearch.strftime( '%H:%M:%S.%f' ), fcb.times[i].strftime( '%H:%M:%S.%f' ))
	
	print('getFrames')
	times, frames = fcb.findBeforeAfter( tSearch, 1, 1 )
	for t in times:
		print(t.strftime( '%H:%M:%S.%f' ))
	
	
	print('Validation')
	tSearch = datetime.datetime.now()
	for i in xrange(300000):
		tSearchCur = tSearch - datetime.timedelta(seconds = i%bufSize)
		'''
		print i
		f1 = fcb._find( tSearchCur )
		f2 = fcb._loopFind( tSearchCur )
		print f1, f2
		print tSearchCur.strftime( '%H:%M:%S.%f' )
		print
		print fcb.times[0].strftime( '%H:%M:%S.%f' )
		print fcb.times[1].strftime( '%H:%M:%S.%f' )
		'''
		assert fcb._find( tSearchCur ) == fcb._loopFind( tSearchCur )
	
	print('Performance')
	t = datetime.datetime.now()
	for i in xrange(300000):
		fcb._find( tSearch - datetime.timedelta(seconds = i%bufSize) )
	print(datetime.datetime.now() - t)
	
	t = datetime.datetime.now()
	for i in xrange(300000):
		fcb._loopFind( t - datetime.timedelta( seconds = i%bufSize ) )
	print(datetime.datetime.now() - t)
	
