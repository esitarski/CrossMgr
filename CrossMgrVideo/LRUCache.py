from collections import OrderedDict

class LRUCache( OrderedDict ):
	def __init__(self, maxlen):
		super().__init__()
		self.maxlen = maxlen

	def __getitem__(self, key):
		# Move the item to the end to reset the MRU (most recently used).
		self.move_to_end( key )
		return super().__getitem__(key)

	def get( self, key, default=None ):
		if key in self:
			# Call our own getitem to reset the MRU.
			return self.__getitem__(key)
		return default

	def __setitem__(self, key, value):
		if key not in self:
			# Add this key:value to the dict.
			# Reset the MRU.
			super().__setitem__( key, value )
			
			# If we are full, remove the LRU elements.
			while len(self) > self.maxlen:
				# Delete LRU items from the front.
				# We can't call popitem().
				# It calls __getitem__, and that calls move_to_end(), which messes up popitem().
				# So we use next(iter(self)).
				del self[next(iter(self))]
		else:
			# Replace the existing value with the new one and MRU it.
			super().__setitem__( key, value )
			self.move_to_end( key )
		
if __name__ == '__main__':
	s = LRUCache( 3 )
	for i in range(20):
		print( i, s, s.get(i) )
		s[i] = i
		assert i in s
		print( i, s, s.get(i) )

