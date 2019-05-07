import six
import collections

class LRUCache( object ):
	def __init__(self, capacity):
		self.capacity = capacity
		self.cache = collections.OrderedDict()

	def __getitem__(self, key):
		# Reinsert to reset the insert order.
		value = self.cache.pop(key)
		self.cache[key] = value
		return value

	def __setitem__(self, key, value):
		if key in self.cache:
			self.cache.pop(key)
		elif len(self.cache) >= self.capacity:
			self.cache.popitem(False)
		self.cache[key] = value
		
	def __contains__( self, key ):
		return key in self.cache
		
	def __delitem__( self, key ):
		del self.cache[key]
		
	def __len__( self ):
		return len( self.cache )
		
	def __getattr__( self, name ):
		return getattr(self.cache, name)

if __name__ == '__main__':
	lru = LRUCache( 20 )
	for i in six.moves.range(30):
		lru[i] = i
	assert len(lru) == 20
	assert sorted( lru.values() ) == list( v for v in six.moves.range(10,30))
	keys = list( lru.keys() )
	six.print_( keys )
	values = list( lru.values() )
	six.print_( values )
