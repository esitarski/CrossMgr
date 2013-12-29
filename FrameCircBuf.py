import types
import datetime

class PhotoCircBuf( object ):
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
			'def find( self, t ):',
			' iStart = self.iStart',
			' bufSize = self.bufSize',
			' times = self.times',
		]
		self._genFind( stmts, 1, 0, self.bufSize )
		print( '\n'.join(stmts) + '\n' )
		exec( '\n'.join(stmts) + '\n' )
		self.find = types.MethodType(find,self)

	def clear( self ):
		self.frames = [None for i in xrange(self.bufSize)]		

	def append( self, t, frame ):
		self.times[self.iStart] = t
		self.frames[self.iStart] = frame
		self.iStart = (0 if self.iStart == self.bufSize - 1 else self.iStart + 1)

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

	def getFrames( self, t, before = 0, after = 1 ):
		i = self.find( t )
		if self.times[i] < t:
			return [], []
			
		iStart = self.iStart
		times = self.times
		frames = self.frames
		bufSize = self.bufSize
		
		retTimes = []
		retFrames = []
		if  before != 0 and i != self.iStart:
			for b in xrange(1, before):
				k = (i-b) % bufSize
				retTimes.append( times[k] )
				retFrames.append( frames[k] )
				if k == self.iStart:
					break
			retTimes.reverse()
			retFrames.reverse()
		for a in xrange(0, after):
			k = (i+a) % bufSize
			if k == iStart:
				break
			retTimes.append( times[k] )
			retFrames.append( frames[k] )
		
		return retTimes, retFrames

	def loopFind( self, t ):
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
	pcb = PhotoCircBuf( bufSize )
	pcb.reset( 6*75 )
	
	for t in pcb.times:
		print t.strftime( '%H:%M:%S.%f' )
	print
	
	tSearch = datetime.datetime.now() - datetime.timedelta(seconds = 4)
	i = pcb.find( tSearch )
	print i, tSearch.strftime( '%H:%M:%S.%f' ), pcb.times[i].strftime( '%H:%M:%S.%f' )
	
	print 'getFrames'
	times, frames = pcb.getFrames( tSearch, 5, 5 )
	for t in times:
		print t.strftime( '%H:%M:%S.%f' )
	
	print 'Validation'
	tSearch = datetime.datetime.now()
	for i in xrange(300000):
		tSearchCur = tSearch - datetime.timedelta(seconds = i%bufSize)
		'''
		print i
		f1 = pcb.find( tSearchCur )
		f2 = pcb.loopFind( tSearchCur )
		print f1, f2
		print tSearchCur.strftime( '%H:%M:%S.%f' )
		print
		print pcb.times[0].strftime( '%H:%M:%S.%f' )
		print pcb.times[1].strftime( '%H:%M:%S.%f' )
		'''
		assert pcb.find( tSearchCur ) == pcb.loopFind( tSearchCur )
	
	print 'Performance'
	t = datetime.datetime.now()
	for i in xrange(300000):
		pcb.find( tSearch - datetime.timedelta(seconds = i%bufSize) )
	print datetime.datetime.now() - t
	
	t = datetime.datetime.now()
	for i in xrange(300000):
		pcb.loopFind( t - datetime.timedelta( seconds = i%bufSize ) )
	print datetime.datetime.now() - t
	
