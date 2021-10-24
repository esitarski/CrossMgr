from collections import OrderedDict

class LRUCache( OrderedDict ):
	'''
		Items are set to MRU (Most Recently Used) on __setitem__ and __getitem__.
		A __contains__ call does not reset the item to MRU.
		__setitem__ is called by update() so this works correctly.
	'''
	def __init__(self, maxlen):
		super().__init__()
		self.maxlen = max( 1, maxlen )

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
		self.move_to_end( key )			# Set MRU if item is already in the cache.
		
		# If we are full, remove the LRU elements (the items on the front).
		# We can't call popitem().
		# It calls __getitem__, and that calls move_to_end(), which messes up popitem().
		# Use next(iter(self)) as it is safe.
		if len(self) > self.maxlen:
			try:
				del self[next(iter(self))]
			except Exception as e:
				pass

if __name__ == '__main__':
	s = LRUCache( 3 )
	for i in range(20):
		print( i, s, s.get(i) )
		s[i] = i
		assert i in s
		print( i, s, s.get(i) )

	s.update( {i:i for i in range(30,40)} )
	print( s )
