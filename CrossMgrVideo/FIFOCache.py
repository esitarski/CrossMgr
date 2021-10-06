from collections import OrderedDict

class FIFOCacheSet(OrderedDict):
	def __init__( self, maxlen=64 ):
		super().__init__()
		self.maxlen = maxlen
		
	def add(self, key):
		self[key] = True
		self.move_to_end( key )		# Do this in case this item was already in the cache.
		while len(self) > self.maxlen:
			self.popitem( False )	# Pop from the front.

	def remove(self, key):
		del self[key]
		
	def discard(self, key):
		if key in self:
			del self[key]

class FIFOCacheDict( OrderedDict ):
	def __init__(self, maxlen):
		super().__init__()
		self.maxlen = maxlen

	def __setitem__(self, key, value):
		super().__setitem__( key, value )
		self.move_to_end( key )		# Set this item to MRU.
		while len(self) > self.maxlen:
			self.popitem( False )	# Pop from the front.

if __name__ == '__main__':
	s = FIFOCacheSet( 3 )
	for i in range(20):
		print( s )
		s.add( i )
		assert i in s
		print( s )
