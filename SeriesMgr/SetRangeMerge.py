from random import randint

def SetRangeMerge( sets ):
	'''
		The sets parameter is a list of either a python set (if mutable) or a frozenset (if immutable).\
		Immutable sets correspond to Wave categories with no Components.
		Elements in the sets must be numbers.
	'''
	if not sets:
		return []
	
	# Ensure that shared elements are matched in sequence from the first set to last set.
	numberSets = []
	previousElements = set()
	for s in sets:
		numberSets.append( s - previousElements )
		previousElements |= numberSets[-1]
	
	def inConflict( first, last, i ):
		''' Check if the proposed range is in conflict with any other set. '''
		rngSet = set( range(first, last+1) )
		return not all( j == i or rngSet.isdisjoint(numSet) for j, numSet in enumerate(numberSets) )
	
	numberRanges = []
	for iNumberSet, numberSet in enumerate(numberSets):
		numberRange = []
		if isinstance(sets[iNumberSet], frozenset):
			# For frozen sets, just convert consecutive numbers to ranges.  Don't check between sets.
			numberList = sorted( sets[iNumberSet] )
			if numberList:
				numberRange.append( (numberList[0], numberList[0]) )
				for n in numberList[1:]:
					if n == numberRange[-1][1] + 1:
						numberRange[-1] = (numberRange[-1][0], n)
					else:
						numberRange.append( (n,n) )
		else:
			# Build the largest ranges that don't conflict with any other set.
			numberList = sorted( numberSet )
			iFirst = iLast = 0
			while iFirst < len(numberList):
				while iLast < len(numberList) and not inConflict(numberList[iFirst], numberList[iLast], iNumberSet):
					iLast += 1
				numberRange.append( (numberList[iFirst], numberList[iLast-1]) )
				iFirst = iLast
		numberRanges.append( numberRange )
			
	return numberRanges
	
def RangeToStr( r ):
	return ','.join( str(first) if first == last else '{}-{}'.format(first, last) for first, last in r )
	
def RangeToSet( r ):
	return set().union( *[range(first, last+1) for first, last in r] ) if r else set()
	
if __name__ == '__main__':
	sets = [
		set(randint(101,200) for i in range(50)),
		frozenset(randint(151,250) for i in range(50)),
		set(randint(201,300) for i in range(50)),
		set(randint(301,400) for i in range(50)),
		set(randint(401,500) for i in range(50)),
	]
	for r in SetRangeMerge(sets) :
		print( RangeToStr(r) )
