import re

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
				if len(lohi) == 1:
					self.include.add( int(lohi[0]) )
				elif len(lohi) == 2:
					if lohi[0] == '':
						self.exclude.add( int(lohi[1]) )
					else:
						lo, hi = [int(n) for n in lohi]
						self.include.update( xrange(lo, hi+1) )
			except:
				pass
		
		self.exclude = self.exclude & self.include
		self.include = self.include.difference( self.exclude )
		
	def __contains__( self, n ):
		return n in self.include
	
	def __eq__( self, rc ):
		return self.include == rc.include
	
	def __str__( self ):
		ranges = []
		if self.include:
			ranges = []
			inc = sorted( self.include | self.exclude )
			inc.append( inc[-1] )
			nFirst, nLast = -1, -1
			for n in inc:
				if nFirst < 0:
					nFirst = n
					nLast = n
				elif n != nLast + 1:
					if nLast != nFirst:
						ranges.append( '%d-%d' % (nFirst, nLast) )
					else:
						ranges.append( '%d' % nFirst )
					nFirst = n
				nLast = n
			
		ranges.extend( [str(-e) for e in sorted(self.exclude)] )
		
		return ','.join( ranges )
		
	def __repr__( self ):
		return 'RangeCheck("%s")' % self.__str__()
		
if __name__ == '__main__':
	r = RangeCheck( '--100-200-300,,,-,100-200,asdfasdf,81,-161,203,-21' )
	print r
	print repr(r)
	print [i for i in xrange(300) if i in r]
	