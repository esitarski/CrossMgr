import os
import re
import platform

if platform.system() == 'Windows':
	class filesystem_str( str ):
		"""Case insensitive with respect to hashes and comparisons """
		#--Hash/Compare
		def __hash__(self):		return hash(self.lower())
		def __eq__(self, other):
			if isinstance(other, str):
				return self.lower() == other.lower()
			return NotImplemented
		def __ne__(self, other): return not (self == other)
		def __lt__(self, other):
			if isinstance(other, str):
				return self.lower() < other.lower()
			return NotImplemented
		def __ge__(self, other): return not (self < other)
		def __gt__(self, other):
			if isinstance(other, str):
				return self.lower() > other.lower()
			return NotImplemented
		def __le__(self, other): return not (self > other)
else:
	filesystem_str = str

class FileTrie:
	'''
		Find corresponding files in a new directory folder.
		Handles cases where the file names are the same but in different
		directories as long as the overall path is unique.
	'''
	def __init__( self ):
		self.node = {}

	def add( self, p ):
		node = self.node
		p = re.sub( r'[\\/]+', '/', p )
		for c in reversed(re.split( r'[\\/]', p)):
			c = filesystem_str( c )
			if c not in node:
				node[c] = {}
			node = node[c]
				
	def best_match( self, p ):
		path = []
		node = self.node
		p = re.sub( r'[\\/]+', '/', p )
		for c in reversed(re.split( r'[\\/]', p)):
			c = filesystem_str( c )
			try:
				node = node[c]
				path.append( c )
			except KeyError:
				break
		
		while node:
			if len(node) > 1:
				return None
			k, v = next(iter(node.items()))
			path.append( k )
			node = v
		
		path.reverse()
		
		if path:
			if re.match( '^[a-zA-Z]:$', path[0] ):	# Add absolution path to drive.
				path[0] += '\\'
			elif not path[0]:						# Ensure absolution paths are created correctly on linux in python 3.
				path[0] = os.sep

		return os.path.join( *path )

if __name__ == '__main__':
	ft = FileTrie()
	for i in range(5):
		ft.add( r'c:\Projects\CrossMgr\SeriesMgr\test{}'.format(i) ) 
	ft.add( r'c:\Projects\CrossMgr\CrossMgrImpinj\test{}'.format(0) ) 
	print( ft.best_match( '/home/Projects/CrossMgr/SeriesMgr/test2' ) )
	print( ft.best_match( '/home/Projects/CrossMgr/CrossMgrImpinj/test0' ) )
	print( ft.best_match( 'test4' ) )
	print( ft.best_match( 'test0' ) )
	print( '****done****' )
