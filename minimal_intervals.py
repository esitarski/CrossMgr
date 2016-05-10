def set_to_intervals( s ):
	if not s:
		return []
	
	all_nums = sorted( s )
	nBegin = nLast = all_nums.pop( 0 )
	
	intervals = []
	for n in all_nums:
		if n != nLast + 1:
			intervals.append( (nBegin, nLast) )
			nBegin = n
		nLast = n

	intervals.append( (nBegin, nLast) )		
	return intervals
	
def minimal_intervals( numbers ):
	# Input: a list of sets of numbers
	# Output: a set of intervals expressed as [from,to] for each set that are non-intersecting.
	
	if not numbers:
		return []
	if len(numbers) == 1:
		return [set_to_intervals(numbers[0])]
	
	combineIntervalsTogether = True
	for n in numbers:
		if any( bib > 99999 for bib in n ):
			combineIntervalsTogether = False
			break
			
	intervals = []
	
	if combineIntervalsTogether:
		for j, n in enumerate(numbers):
			if not n:
				intervals.append( [] )
				continue
			
			other_nums = set.union( *[nn for k, nn in enumerate(numbers) if k != j] )
			
			nums = sorted( n )
			intervalCur = []			
			nRange = [nums[0], nums[0]]
			for i in xrange(1, len(nums)):
				if other_nums.isdisjoint( xrange(nums[i-1], nums[i]+1) ):
					nRange[1] = nums[i]
				else:
					if intervalCur and intervalCur[-1][1]+1 == nRange[0]:
						intervalCur[-1] = ( intervalCur[-1][0], nRange[1] )
					else:
						intervalCur.append( tuple(nRange) )
					nRange = [nums[i], nums[i]]
			intervalCur.append( tuple(nRange) )
			
			intervals.append( intervalCur )
	else:
		intervals = [set_to_intervals(n) for n in numbers]

	return intervals
	
def interval_to_str( intervals ):
	return ','.join( '{}'.format(a) if a == b else '{}-{}'.format(a, b) for a, b in intervals )
	
if __name__ == '__main__':
	for i in minimal_intervals( [
					set( xrange(1,99+1) ),
					set( xrange(1,10+1) ),
					set( xrange(10,19+1) ),
					set( xrange(20,29+1) ),
				]
			):
		print interval_to_str( i )
	
	print '-------------------------'
	
	for i in minimal_intervals( [
					set( [0, 1, 2] ),
					set( [1, 2] ),
					set( x*3 for x in [1,2,3,4,5,7] ),
					set( x*3 for x in [6,8,9,10,11] ),
				]
			):
		print interval_to_str( i )
	
	print '-------------------------'
	
	for i in minimal_intervals( [
					set( 1000000 + x for x in [0, 1, 2] ),
					set( 1000000 + x for x in [1, 2] ),
					set( 1000000 + x*3 for x in [1,2,3,4,5,7] ),
					set( 1000000 + x*3 for x in [6,8,9,10,11] ),
				]
			):
		print interval_to_str( i )
