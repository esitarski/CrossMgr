import numpy as np
import operator

def QuadReg( data ):
	lenData = len(data)
	if lenData < 3:
		raise ValueError( 'data must have >= 3 values' )
	return np.polyfit( np.fromiter( (d[0] for d in data), np.float64, lenData), np.fromiter( (d[1] for d in data), np.float64, lenData), 2 )
	
def QuadRegExtreme( data ):
	a, b, c = QuadReg( data )
	if a >= 0.0:
		raise ValueError( 'invalid quadratic: cannot open up' )
	return -b / (2.0 * a)
	
def QuadRegRSS( data ):
	lenData = len(data)
	if lenData < 3:
		raise ValueError( 'data must have >= 3 values' )
	x = np.fromiter( (d[0] for d in data), np.float64, lenData )
	y = np.fromiter( (d[1] for d in data), np.float64, lenData )
	a, b, c = np.polyfit( x, y, 2 )
	e = np.fromiter( (v*v*a + v*b + c for v in x), np.float64, lenData )
	s = np.sum( (y-e)**2 )
	return s

def QuadRegRSE( data ):
	if len(data) <= 3:
		raise ValueError( 'data must have > 3 values' )
	return QuadRegRSS(data) / (len(data) - 3)

def QuadRegFindOutlier( data ):
	lenData = len(data)
	if lenData <= 3:
		raise ValueError( 'data must have >= 3 values' )
	x = np.fromiter( (d[0] for d in data), np.float64, lenData )
	y = np.fromiter( (d[1] for d in data), np.float64, lenData )
	a, b, c = np.polyfit( x, y, 2 )
	e = np.fromiter( (v*v*a + v*b + c for v in x), np.float64, lenData )
	R = y - e
	mean, std = np.mean(R), np.std(R)
	return max( ((i, abs(r-mean)/std) for i, r in enumerate(R)), key=operator.itemgetter(1) )
	
def QuadRegRemoveOutliers( data ):
	data = data[:]	# Make a copy of the data.
	lenData = len(data)
	if lenData <= 3:
		raise ValueError( 'data must have >= 3 values' )
	x = np.fromiter( (d[0] for d in data), np.float64, lenData )
	y = np.fromiter( (d[1] for d in data), np.float64, lenData )
	while 1:
		a, b, c = np.polyfit( x, y, 2 )
		e = np.fromiter( (v*v*a + v*b + c for v in x), np.float64, lenData )
		R = y - e
		mean, std = np.mean(R), np.std(R)
		i, zMax = max( ((i, abs(r-mean)/std) for i, r in enumerate(R)), key=operator.itemgetter(1) )
		if zMax < 1.8:
			break
		del data[i]
		x = np.delete( x, i )
		y = np.delete( y, i )
		lenData = len(data)
	return data
	
if __name__ == '__main__':
	data = '''i	Temperature	Yield
1	50	8.3
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
			points.append( (float(fields[1]), -float(fields[2])) )
	
	print points
	print QuadReg(points), QuadRegExtreme(points), QuadRegRSS(points), QuadRegFindOutlier(points)
	
	points = QuadRegRemoveOutliers( points )
	print points
	print QuadReg(points), QuadRegExtreme(points), QuadRegRSS(points), QuadRegFindOutlier(points)
	
