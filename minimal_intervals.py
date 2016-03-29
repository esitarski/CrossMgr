
def minimal_intervals( numbers ):
	# Input: a list of sets of numbers
	# Output: a set of intervals expressed as [from,to] for each set that are non-intersecting.
	
	combineIntervalsTogether = True
	for n in numbers:
		if any( bib > 99999 for bib in n ):
			combineIntervalsTogether = False
			break
			
	intervals = []
	
	if combineIntervalsTogether:
		def testIntersection( intervalNums, n ):
			return all( nTest.isdisjoint(intervalNums) or n == nTest for nTest in numbers )
		
		for n in numbers:
			nums = sorted( n )
			intervalCur = []
			while nums:
				left, right = 0, len(nums)
				while right - left > 1:
					mid = left + (right - left) // 2
					if testIntersection( xrange(nums[0], nums[mid]+1), n ):
						left = mid
					else:
						right = mid
				intervalCur.append( (nums[0], nums[left]) )
				nums = nums[left+1:]
			
			intervals.append( intervalCur )
	else:
		for n in numbers:
			nums = sorted( n )
			intervalCur = []
			if nums:
				iBegin = 0
				for i in xrange(1, len(nums)):
					if nums[i] != nums[i-1] + 1:
						intervalCur.append( (nums[iBegin], nums[i-1]) )
						iBegin = i
				intervalCur.append( (nums[iBegin], nums[-1]) )
			intervals.append( intervalCur )

	return intervals
	
def interval_to_str( interval ):
	s = []
	for a, b in interval:
		if a == b:
			s.append( '{}'.format(a) )
		else:
			s.append( '{}-{}'.format(a, b) )
	return ','.join( s )
	
if __name__ == '__main__':
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
