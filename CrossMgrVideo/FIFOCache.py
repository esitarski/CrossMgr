from collections import deque

class FIFOCacheSet:
	'''
		Cache that only keeps the most recent maxlen entries.
	'''
	def __init__( self, maxlen=64 ):
		self.maxlen = maxlen
		self.c = set()
		self.d = deque()
	
	def __contains__( self, e ):
		return e in self.c
		
	def clear( self ):
		self.c.clear()
		self.d.clear()
		
	def add( self, e ):
		if len(self.d) == self.maxlen:
			self.c.discard( self.d.popleft() )
		self.c.add( e )
		self.d.append( e )
		
if __name__ == '__main__':
	s = FIFOCacheSet( 5 )
	for i in range(20):
		s.add( i )
		assert i in s
		print( s.d, s.c )
