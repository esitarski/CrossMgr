import re

#------------------------------------------------------------------------

class RangeCheck:
	def __init__( self, s = '' ):
		self.include = set()
		self.exclude = set()
		self.setRange( s )
		
	def setRange( self, s ):
		self.include = set()
		self.exclude = set()

		s = re.sub( r'[^\d,-]', '', s )
		s = re.sub( r'-+', '-', s )
		s = re.sub( r',+', ',', s )
		ranges = s.split( ',' )
		for r in ranges:
			try:
				if not r or r == '-':
					continue
				
				lohi = r.split( '-' )
				fields = len( lohi )
				if fields == 1:
					self.include.add( int(lohi[0]) )
				elif fields == 2:
					if lohi[0] == '':
						self.exclude.add( int(lohi[1]) )
					else:
						lo, hi = [int(n) for n in lohi]
						if lo < hi:
							self.include.update( range(lo, hi+1) )
				elif fields == 3:
					lo, hi = [int(n) for n in lohi[1:]]
					if lo < hi:
						self.exclude.update( range(lo, hi+1) )
				
			except Exception:
				pass
		
		self.exclude = self.exclude & self.include
		self.include = self.include.difference( self.exclude )
	
	def getNumericPrefix( self ):
		# If empty, return nothing.
		if not self.include:
			return ''
		
		# Find the longest prefix for all numbers.
		nLen = None
		prefix = None
		for n in self.include:
			s = '{}'.format(n)
			if prefix is None:					# Initialize the starting prefix.
				prefix = s
				nLen = len(s)
			elif len(s) != nLen:				# If all numbers are not the same length, return empty.
				return ''
			elif not s.startswith(prefix):
				i = 0
				while i < nLen and prefix[i] == s[i]:
					i += 1
				if i == 0:						# If no common prefix, return empty.
					return ''
				prefix = prefix[:i]
					
		return prefix
	
	def __contains__( self, n ):
		return n in self.include
	
	def __eq__( self, rc ):
		return self.include == rc.include
	
	def __str__( self ):
		ranges = []
		if self.include:
			elements = sorted( self.include | self.exclude )
			elements.append( elements[-1] )
			nFirst, nLast = None, None
			for n in elements:
				if nFirst is None:
					nFirst = n
					nLast = n
				elif n != nLast + 1:
					if nLast != nFirst:
						ranges.append( f'{nFirst}-{nLast}' )
					else:
						ranges.append( f'{nFirst}' )
					nFirst = n
				nLast = n
			
		if self.exclude:
			elements = sorted( self.exclude )
			elements.append( elements[-1] )
			nFirst, nLast = None, None
			for n in elements:
				if nFirst is None:
					nFirst = n
					nLast = n
				elif n != nLast + 1:
					if nLast != nFirst:
						ranges.append( f'-{nFirst}-{nLast}' )
					else:
						ranges.append( f'-{nFirst}' )
					nFirst = n
				nLast = n
		
		return ','.join( ranges )
		
	def __repr__( self ):
		return f'RangeCheck("{self.__str__()}")'
		
if __name__ == '__main__':
	r = RangeCheck( '--100-200-300,,,-,100-199,-120-130,asdfasdf,-161,-21' )
	print( r.include )
	print( r )
	print( repr(r) )
	print( 'prefix:', r.getNumericPrefix() )
	print( [i for i in range(300) if i in r] )
	
