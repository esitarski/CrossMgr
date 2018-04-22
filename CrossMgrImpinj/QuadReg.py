import numpy as np

def QuadReg( data ):
	if len(data) < 3:
		raise ValueError( 'data must have >= 3 values' )
	return np.polyfit( np.array( [d[0] for d in data], 'd'), np.array( [d[1] for d in data], 'd'), 2 )
	
def QuadRegExtreme( data ):
	a, b, c = QuadReg( data )
	if a >= 0.0:
		raise ValueError( 'quadratic opens up' )
	return -b / (2.0 * a)

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
			points.append( (float(fields[1]), -float(fields[2])) )
	print points
	print QuadReg( points ), QuadRegExtreme( points )
	
