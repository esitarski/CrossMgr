import io
from random import randint

def SetRangeMerge( sets ):
	'''
		sets consists of a list of either a python set (if mutable) or a frozenset (if immutable).
	'''
	if not sets:
		return []
	
	# Ensure that common elements override from the first set to the last set.
	numberSets  = [set(sets[0])]
	if isinstance(sets[0], frozenset):
		numberSets = frozenset( numberSets )
	previousElements = set(sets[0])
	for i in range(1, len(sets)):
		if isinstance(sets[i], frozenset):
			numberSets.append( sets[i] )
		else:
			numberSets.append( set(sets[i]) - previousElements )
		previousElements |= numberSets[-1]
		
	numberLists = [sorted(s) for s in numberSets]
	
	def inConflict( first, last, i ):
		rng = set( range(first, last+1) )
		for j, numSet in enumerate(numberSets):
			if j != i and rng & numSet:
				return True
		return False
	
	numberRanges = [[] for s in sets]
	for iNumberList, numberList in enumerate(numberLists):
		if isinstance(sets[iNumberList], frozenset):
			if sets[iNumberList]:
				# Represent consecutive numbers as ranges.
				numberRanges[iNumberList].append( (numberList[0], numberList[0]) )
				for n in numberList[1:]:
					if n == numberRanges[iNumberList][-1][1] + 1:
						numberRanges[iNumberList][-1] = (numberRanges[iNumberList][-1][0], n)
					else:
						numberRanges[iNumberList].append( (n,n) )
		else:
			# Build the largest ranges that don't conflict with number in any other group.
			iFirst = iLast = 0
			while iFirst < len(numberList):
				while iLast < len(numberList) and not inConflict(numberList[iFirst], numberList[iLast], iNumberList):
					iLast += 1
				numberRanges[iNumberList].append( (numberList[iFirst], numberList[iLast-1]) )
				iFirst = iLast
			
	return numberRanges
	
def RangeToStr( r ):
	return ','.join( str(first) if first == last else '{}-{}'.format(first, last) for first, last in r )
	
def RangeToSet( r ):
	return set().union( *[range(first, last+1) for first, last in r] ) if r else set()
	
if __name__ == '__main__':
	sets = [
		[randint(101,200) for i in range(50)],
		[randint(151,250) for i in range(50)],
		[randint(201,300) for i in range(50)],
		[randint(301,400) for i in range(50)],
	]
	for r in SetRangeMerge(sets) :
		print( RangeToStr(r) )
