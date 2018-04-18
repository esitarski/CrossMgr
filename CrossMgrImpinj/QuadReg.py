def QuadReg( points ):
	n = len( points )
	s1 = s2 = s3 = s4 = s5 = s6 = s7 = 0.0
	for x, y in points:
		s1 += x
		s2 += x * x
		s3 += x * x * x
		s4 += x * x * x * x
		s5 += y
		s6 += x * y
		s7 += x * x * y
		
	denom = (n  * (s2 * s4 - s3 * s3) -
		s1 * (s1 * s4 - s2 * s3) +
		s2 * (s1 * s3 - s2 * s2) )
		
	if denom < 0.0000001:
		raise ValueError( 'denom too small' )
		   
	a1 = (s5 * (s2 * s4 - s3 * s3) -
		s6 * (s1 * s4 - s2 * s3) +
		s7 * (s1 * s3 - s2 * s2)) / denom
	a2 = (n  * (s6 * s4 - s3 * s7) -
		s1 * (s5 * s4 - s7 * s2) +
		s2 * (s5 * s3 - s6 * s2)) / denom
	a3 = (n  * (s2 * s7 - s6 * s3) -
		s1 * (s1 * s7 - s5 * s3) +
		s2 * (s1 * s6 - s5 * s2)) / denom
	return a3, a2, a1
	
def QuadRegExtreme( points ):
	n = len( points )
	s1 = s2 = s3 = s4 = s5 = s6 = s7 = 0.0
	for x, y in points:
		s1 += x
		s2 += x * x
		s3 += x * x * x
		s4 += x * x * x * x
		s5 += y
		s6 += x * y
		s7 += x * x * y
	
	return -(n  * (s6 * s4 - s3 * s7) -
		s1 * (s5 * s4 - s7 * s2) +
		s2 * (s5 * s3 - s6 * s2)) / (2.0 * (
		n  * (s2 * s7 - s6 * s3) -
		s1 * (s1 * s7 - s5 * s3) +
		s2 * (s1 * s6 - s5 * s2)))

if __name__ == '__main__':
	data = '''i	Temperature	Yield
1	50	3.3
2	50	2.8
3	50	2.9
4	70	2.3
5	70	2.6
6	70	2.1
7	80	2.5
8	80	2.9
9	80	2.4
10	90	3.0
11	90	3.1
12	90	2.8
13	100	3.3
14	100	3.5
15	100	3.0'''
	points = []
	for line in data.split('\n'):
		if not line.startswith('i'):
			fields = line.split()
			points.append( (float(fields[1]), float(fields[2])) )
	print points
	print QuadReg( points ), QuadRegExtreme( points )
	