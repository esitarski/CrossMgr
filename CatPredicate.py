import re
import ReadSignOnSheet
import itertools

def SetToIntervals( s ):
	if not s:
		return []
	seq = sorted( s )
	intervals = [(seq[0], seq[0])]
	for num in itertools.islice(seq, 1, len(seq)):
		if num <= intervals[-1][1]:
			pass
		elif num == intervals[-1][1] + 1:
			intervals[-1] = (intervals[-1][0], num)
		else:
			intervals.append( (num, num) )
	return intervals
	
def IntervalsToSet( intervals ):
	ret = set()
	for i in intervals:
		ret.update( xrange(i[0], i[1]+1) )
	return ret

class CategoryPredicate( object ):
	def __init__( self ):
		# None == ignore
		self.numberSet = None
		self.genderMatch = None
		self.ageRange = None
		self.categoryMatch = None
		
		self.intervals = []
		self.exclude = set()
		
	def match( self, info ):
		isMatch = True
		if isMatch and info.get('Bib#', -1) in self.exclude:
			isMatch = False
		if isMatch and self.intervals is not None:
			num = info.get('Bib#', -1)
			isMatch = False
			for i in self.intervals:
				if i[0] <= num <= i[1]:
					isMatch = True
					break
		if isMatch and self.genderMatch is not None:
			isMatch = (info.get('Gender',ReadSignOnSheet.ExcelLink.OpenCode) == self.genderMatch)
		if isMatch and self.categoryMatch is not None:
			catMatch = info.get('Category','').lower()
			isMatch = False
			for c in self.categoryMatch:
				if catMatch == c.lower():
					isMatch = True
					break
		if isMatch and self.ageRange is not None:
			isMatch = (self.ageRange[0] <= info.get('Age', -1) <= self.ageRange[1])
		return isMatch
		
	badRangeCharsRE = re.compile( '[^0-9,\-]' )
	nonDigits = re.compile( '[^0-9]' )

	def _getStr( self ):
		s = [str(i[0]) if i[0] == i[1] else '%d-%d' % i for i in self.intervals]
		s.extend( ['-{}'.format(i[0]) if i[0] == i[1] else '-{}-{}'.format(*i) for i in SetToIntervals(self.exclude)] )
		s = ','.join( s )
		
		if self.genderMatch is not None:
			s += ';Gender=' + ['Open', 'Men', 'Women'][self.genderMatch]
			
		if self.categoryMatch is not None:
			s += ';Category={' + '|'.join(self.categoryMatch) + '}'
			
		if self.ageRange is not None:
			s += ';Age=[{}..{}]'.format( self.ageRange[0], self.ageRange[1] )
		
	def _setStr( self, sIn ):
		self.genderMatch = None
		self.categoryMatch = None
		self.ageRange = None
		
		for s in sIn.split(';'):
			s = s.strip()
			if s.startswith( 'Gender=' ):
				f = s.split('=', 1)[1].strip()
				genderFirstChar = f[1:]
				if genderFirstChar in 'MH':
					self.genderMatch = 1
				elif genderFirstchar in 'WFL':
					self.genderMatch = 2
				else:
					self.genderMatch = 0
			elif s.startswith( 'Category=' ):
				f = s.split('=', 1)[1].strip()
				f = f[1:-1]		# Remove braces.
				cats = f.split('|')
				self.categoryMatch = [c.strip() for c in cats]
				if not self.categoryMatch:
					self.categoryMatch = None
			elif s.startswith( 'Age=' ):
				self.ageRange = []
				f = s.split('=')[1].strip()
				for r in f.split( '..' ):
					r = self.nonDigits.sub( '', r )
					try:
						self.ageRange.append( int(r) )
					except Exception as e:
						self.ageRange = None
						break
				if self.ageRange is not None:
					if len(self.ageRange) != 2:
						self.ageRange = None
					else:
						self.ageRange = self.ageRange[:2]
			else:
				s = self.badRangeCharsRE.sub( '', str(s) )
				self.intervals = []
				self.exclude = set()
				for f in s.split(','):
					if not f:
						continue
					
					try:
						if f.startswith('-'):				# Check for exclusion.
							f = f[1:]
							isExclusion = True
						else:
							isExclusion = False
							
						bounds = [int(b) for b in f.split('-') if b]
						if not bounds:
							continue

						if len(bounds) > 2:					# Fix numbers not in proper x-y range format.
							del bounds[2:]
						elif len(bounds) == 1:
							bounds.append( bounds[0] )
							
						bounds[0] = min(bounds[0], 99999)	# Keep the numbers in a reasonable range to avoid crashing.
						bounds[1] = min(bounds[1], 99999)
						
						if bounds[0] > bounds[1]:			# Swap the range if out of order.
							bounds[0], bounds[1] = bounds[1], bounds[0]
							
						if isExclusion:
							self.exclude.update( xrange(bounds[0], bounds[1]+1) )
						else:
							self.intervals.append( tuple(bounds) )
							
					except Exception as e:
						# Ignore any parsing errors.
						print( e )
						pass
						
				self.intervals.sort()

	predicate = property(_getStr, _setStr)
		
	def set( self, numberRange = None, genderMatch = None, categoryMatch = None, ageRange = None ):
		pass