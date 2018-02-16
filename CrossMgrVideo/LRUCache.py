import collections

class LRUCache( object ):
	def __init__(self, capacity):
		self.capacity = capacity
		self.cache = collections.OrderedDict()

	def __contains__( self, key ):
		return key in self.cache
		
	def __getitem__(self, key):
		# Reinsert to reset the insert order.
		value = self.cache.pop(key)
		self.cache[key] = value
		return value

	def __delitem__( self, key ):
		del self.cache[key]
		
	def __setitem__(self, key, value):
		if key in self.cache:
			self.cache.pop(key)
		elif len(self.cache) >= self.capacity:
			self.cache.popitem(False)
		self.cache[key] = value
