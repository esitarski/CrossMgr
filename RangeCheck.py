from __future__ import print_function
import re
import six

#------------------------------------------------------------------------

class RangeCheck( object ):
	def __init__( self, s = '' ):
		self.include = set()
		self.exclude = set()
		self.setRange( s )
		
	def setRange( self, s ):
		self.include = set()
		self.exclude = set()

		s = re.sub( '[^\d,-]', '', s )
		s = re.sub( '-+', '-', s )
		s = re.sub( ',+', ',', s )
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
							self.include.update( six.moves.range(lo, hi+1) )
				elif fields == 3:
					lo, hi = [int(n) for n in lohi[1:]]
					if lo < hi:
						self.exclude.update( six.moves.range(lo, hi+1) )
				
			except:
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
						ranges.append( '%d-%d' % (nFirst, nLast) )
					else:
						ranges.append( '%d' % nFirst )
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
						ranges.append( '-%d-%d' % (nFirst, nLast) )
					else:
						ranges.append( '-%d' % nFirst )
					nFirst = n
				nLast = n
		
		return ','.join( ranges )
		
	def __repr__( self ):
		return 'RangeCheck("%s")' % self.__str__()
		
if __name__ == '__main__':
	r = RangeCheck( '--100-200-300,,,-,100-199,-120-130,asdfasdf,-161,-21' )
	six.print_( r.include )
	six.print_( r )
	six.print_( repr(r) )
	six.print_( 'prefix:', r.getNumericPrefix() )
	six.print_( [i for i in six.moves.range(300) if i in r] )
	
