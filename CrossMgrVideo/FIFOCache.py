from collections import OrderedDict

class FIFOCacheSet(OrderedDict):
	def __init__( self, maxlen, iterable=None ):
		self.maxlen = maxlen
		super().__init__()
		if iterable:
			self.__ior__( iterable )
		
	def __setitem__( self, key, value ):
		super().__setitem__( key, True )
		self.move_to_end( key )		# Set this item to MRU if it was already in the cache.
		if len(self) > self.maxlen:
			self.popitem( False )	# Pop from the front.		
		
	def add( self, key ):
		self[key] = True
		self.move_to_end( key )		# Set this item to MRU if it was already in the cache.
		if len(self) > self.maxlen:
			self.popitem( False )	# Pop from the front.

	def remove( self, key ):
		del self[key]
		
	def discard(self, key):
		if key in self:
			del self[key]
			
	def __ior__( self, s ):
		super().update( ((e,True) for e in s) )
		return self
		
	def __repr__( self ):
		return 'FIFOCachSet({},{})'.format( self.maxlen, list(super().keys()) )
			
	def update( self, iterable ):
		raise AttributeError( "'FIFOCachSet' has no attribute 'update'" )
			
	def items(self):
		raise AttributeError( "'FIFOCachSet' has no attribute 'items'" )

	def keys(self):
		raise AttributeError( "'FIFOCachSet' has no attribute 'keys'" )
		
	def values(self):
		raise AttributeError( "'FIFOCachSet' has no attribute 'values'" )

class FIFOCacheDict( OrderedDict ):
	def __init__(self, maxlen, *args, **kwargs):
		self.maxlen = maxlen
		super().__init__( *args, **kwargs )

	def __setitem__(self, key, value):
		super().__setitem__( key, value )
		self.move_to_end( key )		# Set this item to MRU if it was already in the cache.
		if len(self) > self.maxlen:
			self.popitem( False )	# Pop from the front.

if __name__ == '__main__':
	s = FIFOCacheSet( 3, (1000,2000,3000) )
	print( s )
	s |= (100, 200, 300)
	print( s )
	for i in range(20):
		print( s )
		s.add( i )
		assert i in s
		print( s )
