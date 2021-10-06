from collections import OrderedDict

class LRUCache( OrderedDict ):
	'''
		An item is set to MRU (Most Recently Used) when it is inserted,
		or when its value is changed.
		Notes: __contains__ does not reset to MRU.
	'''
	def __init__(self, maxlen):
		super().__init__()
		self.maxlen = maxlen

	def __getitem__(self, key):
		# Move the item to the end to reset to MRU (most recently used).
		self.move_to_end( key )
		return super().__getitem__(key)

	def get( self, key, default=None ):
		if key in self:
			# Call our own getitem to reset to MRU.
			return self.__getitem__(key)
		return default

	def __setitem__(self, key, value):
		# Add this key:value to the dict.
		super().__setitem__( key, value )
		self.move_to_end( key )			# Set MRU if item already in the cache.
		
		# If we are full, remove the LRU elements.
		while len(self) > self.maxlen:
			# Delete LRU items from the front.
			# We can't call popitem().
			# It calls __getitem__, and that calls move_to_end(), which messes up popitem().
			# So we use next(iter(self)).
			del self[next(iter(self))]
		
if __name__ == '__main__':
	s = LRUCache( 3 )
	for i in range(20):
		print( i, s, s.get(i) )
		s[i] = i
		assert i in s
		print( i, s, s.get(i) )

	print( '************' )
	s[21] = 21
