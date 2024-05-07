def InSortedIntervalList( A, value ):
	lenA = len(A)
	low = 0
	high = lenA - 1
	while low <= high:
		mid = (low + high) // 2
		if A[mid][0] > value:
			high = mid - 1
		elif A[mid][1] < value:
			low = mid + 1
		else:
			return True
	return 0 <= low < lenA and A[low][0] <= value <= A[low][1]

if __name__ == '__main__':
	a = ((1,1), (3,5), (10,20), (40,50))
	assert InSortedIntervalList( a, 1 )
	assert not InSortedIntervalList( a, 2 )
	assert not InSortedIntervalList( a, 7 )
	assert InSortedIntervalList( a, 15 )
	assert InSortedIntervalList( a, 20 )
	assert InSortedIntervalList( a, 40 )
	assert not InSortedIntervalList( a, 51 )
	assert not InSortedIntervalList( a, 0 )
