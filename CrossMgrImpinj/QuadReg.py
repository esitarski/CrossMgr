import numpy as np
import warnings
warnings.simplefilter('ignore', np.RankWarning)
import math
import operator
import itertools
from math import log

def QuadReg( data ):
	lenData = len(data)
	if lenData < 3:
		raise ValueError( 'data must have >= 3 values' )
	return np.polyfit( np.fromiter( (d[0] for d in data), np.float64, lenData), np.fromiter( (d[1] for d in data), np.float64, lenData), 2 )
	
def QuadRegRSS( data ):
	lenData = len(data)
	if lenData < 3:
		raise ValueError( 'data must have >= 3 values' )
	x = np.fromiter( (d[0] for d in data), np.float64, lenData )
	y = np.fromiter( (d[1] for d in data), np.float64, lenData )
	p = np.poly1d( np.polyfit(x, y, 2) )
	R = np.fromiter( (y[i] - p(v) for i, v in enumerate(x)), np.float64, lenData )
	return np.dot( R, R )

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
	p = np.poly1d( np.polyfit(x, y, 2) )
	R = np.fromiter( (y[i] - p(v) for i, v in enumerate(x)), np.float64, lenData )
	rmse = math.sqrt( np.dot(R,R) / (lenData-1) )	# dot(R,R) = sum of squares
	return max( ((i, abs(r/rmse)) for i, r in enumerate(R)), key=operator.itemgetter(1) )
	
def QuadRegRemoveOutliersRobust( data, returnDetails=False ):
	'''
		Return a Quadratic Regression ignoring outliers.
		
		Approach:
			1) Compute the QR with all data points.
			2) Compute the RMSE (Root Mean Square Error), an estimate of the standard deviation of the Residuals.
			3) Scale each point to a Standard Normal Distribution (Mean=0, Std=RMSE).  Mean is zero for best-fit residuals.
			4) Find the max point that exceeds a threshold distance from the mean (-1..1=68.25%, -2..2=95.44%, -3..3=99.74)
			5) If no such point exists, all the points used in the regression are within the threshold.  Return - no outliers.
			6) Otherwise, eliminate the outlier, compute the QR on the remaining points, go to (2)
			
		Discussion:
			Pros:
				This will return a quadratic best-fit using points that are "reasonably" for the fit.
			Cons:
				Like other outlier techniques, we can be "swamped" by outliers.
				And, the elimination threshold is somewhat arbitrary.  It can both accept outliers (false positives)
				and eliminate valid observations (false negatives) depending on the threshold.
				
				Also, O(N*k) where N is the sample size and k is the number of outliers.
			
			Conclusion:
				With RFID reads, we expect a few "wild" values.  The technique should work well for this case.
	'''
	lenData = len(data)
	if lenData < 3:
		raise ValueError( 'data must have >= 3 values' )
	
	zThreshold = 1.9
	
	x = np.fromiter( (d[0] for d in data), np.float64, lenData )
	y = np.fromiter( (d[1] for d in data), np.float64, lenData )
	
	abc = np.polyfit(x, y, 2)
	p = np.poly1d( abc )
	while len(x) > 3:
		R = np.fromiter( (y[i] - p(v) for i, v in enumerate(x)), np.float64, len(x) )	# Residuals from Best Fit.

		# Root mean square error.
		rmse = math.sqrt( np.dot(R,R) / (len(x)-1) )	# dot(R,R) = sum of squares
		iBest, zMax = None, zThreshold					# 2.0 = 95% of normal distribution within mean.
		for i, r in enumerate(R):
			z = abs(r/rmse)		# Scale residual to standard normal.  Mean is always zero for residuals.
			if z > zMax:
				iBest, zMax = i, z
		if iBest is None:
			break
			
		# Eliminate the maximum outlier found.
		x = np.delete( x, iBest )
		y = np.delete( y, iBest )
		abc = np.polyfit(x, y, 2)
		p = np.poly1d( abc )

	if returnDetails:
		inliers = tuple( zip(x, y) )
		inliersSet = set( inliers )
		outliers = tuple( d for d in data if d not in inliersSet )
		return abc, inliers, outliers
	
	return abc

def QuadRegRemoveOutliersRansac( data, returnDetails=False ):
	lenData = len(data)
	if lenData < 3:
		raise ValueError( 'data must have >= 3 values' )
		
	tMin = min( d[0] for d in data )
	tMax = max( d[0] for d in data )
	
	def modelValid( model ):
		if model[0] >= 0:
			return False	# Parabola cannot open up
		apexX = -model[1] / (2.0 * model[0])
		# Estimated point must be in time range, value at estimation must be reasonable db.
		return (tMin <= apexX <= tMax) and np.poly1d(model)(apexX) <= 0.0
	
	np.random.seed( 123456789 )
	# Number of points used to define a proposed model.
	n = max( lenData // 10, 3 )
	
	t = 4					# Distance from parabolic curve where a point is considered an inlier.
	
	bestErr = np.inf		# Best Sum of abs Residuals.
	bestModel = None		# Cooefs of the parabolic
	bestD = 0				# Best number of points within threshold distance of model.
	
	x = np.fromiter( (d[0] for d in data), np.float64, lenData )
	y = np.fromiter( (d[1] for d in data), np.float64, lenData )
	
	# Bias the sample to consider the strongest reads.
	indexes = sorted( list(xrange(lenData)), key=lambda i: data[i][1], reverse=True )
	indexes = np.fromiter( (i for i in indexes[:max(int(lenData*0.75), 6)]), int )
	
	P = 0.99		# Desired probability that we ahve found an uncontaminated model.
	K = np.inf		# Minimum number of samples required to find an uncontaminated model.
	samples = 0
	
	KBad = lenData * 2	# Max number of allowed bad samples (invalid models).
	samplesBad = 0
	
	while samples < K and samplesBad < KBad:
		np.random.shuffle( indexes )
		maybeInliers = np.resize( indexes, n )
		maybeModel = np.polyfit(x[maybeInliers], y[maybeInliers], 2)
		if not modelValid(maybeModel):
			samplesBad += 1
			continue
		
		samples += 1

		# Get all points within range of model.
		alsoInliers = np.abs(np.polyval(maybeModel, x)-y) < t
		curD = sum( alsoInliers )
		
		if curD >= bestD:
		
			betterModel = np.polyfit(x[alsoInliers], y[alsoInliers], 2)
			if not modelValid(betterModel):
				samplesBad += 1
				continue
			
			if curD > bestD:
				bestD = curD
				# Use adaptive estimation to update number of samples required to find
				# a sample model with uncontaminated points.
				if curD < lenData:
					w = float(curD) / float(lenData)
					K = 2.0 * log( 1.0 - P ) / log( 1.0 - w ** n)	# Multiply by 2 for extra safety.
				else:
					K = samples		# We have a model that includes all points - time to quit.
				
			thisErr = np.sum(np.abs(np.polyval(betterModel, x[alsoInliers])-y[alsoInliers]))
			if curD == bestD or thisErr < bestErr:
				bestModel = betterModel
				bestErr = thisErr
	
	if returnDetails:
		if bestModel is None:
			return None, None, None
		inliers = np.abs(np.polyval(bestModel, x)-y) < t
		inliers = tuple( zip(x[inliers], y[inliers]) )
		inliersSet = set( inliers )
		outliers = tuple( d for d in data if d not in inliersSet )
		return bestModel, inliers, outliers
		
	return bestModel
	
def QuadRegExtreme( data, f=QuadRegRemoveOutliersRansac ):
	a, b, c = f( data )
	if a >= 0.0:
		raise ValueError( 'invalid quadratic: cannot open up' )
	return -b / (2.0 * a)

'''
def QuadRegRemoveOutliersCooks( data ):
	lenData = len(data)
	if lenData < 4:
		raise ValueError( 'data must have >= 4 values' )
	
	k = 3.0		# Degrees of freedom.
		
	x = np.fromiter( (d[0] for d in data), np.float64, lenData )
	y = np.fromiter( (d[1] for d in data), np.float64, lenData )
	
	while len(x) >= 4:		
		# Compute the original best-fit.
		coefs = np.polyfit(x, y, 2)
		p = np.poly1d( coefs )
		lenX = len(x)

		# Get residuals.
		R = np.fromiter( (y[i] - p(v) for i, v in enumerate(x)), np.float64, len(x) )

		# Compute the leverage (scale the residuals to a standard normal distribution)..
		leverage = (R -  np.mean(R)) / np.std(R)
		
		# Compute the MSE (mean squared error) of the model.
		mse = np.doc(R,R) / lenX
		#DMax = 4.0 / (lenX - k)
		
		# Threshold for considering a point an outlier.
		DMax = 1.0
		
		outliers = []
		mask = np.ones( len(x), dtype=bool )	
		for i in xrange(len(x)):
			# Compute a best-fit without point i.
			mask[i] = False
			p_i = np.poly1d( np.polyfit(x[mask], y[mask], 2) )
			mask[i] = True
			
			# Compute Cook's Distance on removed point.
			print 'leverage', leverage[i], (leverage[i] / (1-leverage[i])**2)
			D = sum( (y[i] - p_i(v)) ** 2 for i, v in enumerate(x) ) / ((lenX+3.0) * mse) * (leverage[i] / (1-leverage[i])**2)
			print D, DMax
			if D > DMax:	# Classify as outlier if point exceeds threshold.
				outliers.append( i )
		
		print 'QuadRegRemoveOutliersCooks: outliers:', outliers
		if not outliers:
			return coefs
		
		# Eliminate outliers and continue.
		for i in outliers:
			mask[i] = False
		x = x[mask]
		y = y[mask]
	
	return np.polyfit(x, y, 2)
'''
	
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
	print QuadReg(points), QuadRegExtreme(points, QuadReg), QuadRegExtreme(points, QuadRegRemoveOutliersRobust)
	
