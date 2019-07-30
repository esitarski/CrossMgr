from math import sqrt, log, fabs
from statistics import median
import random

def inv_cdf(mu, sigma, p):
	'''Inverse cumulative distribution function.  x : P(X <= x) = p
	Finds the value of the random variable such that the probability of the
	variable being less than or equal to that value equals the given probability.
	This function is also called the percent point function or quantile function.
	'''
	if (p <= 0.0 or p >= 1.0):
		raise ValueError('p must be in the range 0.0 < p < 1.0')
	if sigma <= 0.0:
		raise ValueError('cdf() not defined when sigma={} at or below zero'.format(sigma))

	# There is no closed-form solution to the inverse CDF for the normal
	# distribution, so we use a rational approximation instead:
	# Wichura, M.J. (1988). "Algorithm AS241: The Percentage Points of the
	# Normal Distribution".  Applied Statistics. Blackwell Publishing. 37
	# (3): 477–484. doi:10.2307/2347330. JSTOR 2347330.

	q = p - 0.5
	if fabs(q) <= 0.425:
		r = 0.180625 - q * q
		num = (((((((2.5090809287301226727e+3 * r +
					 3.3430575583588128105e+4) * r +
					 6.7265770927008700853e+4) * r +
					 4.5921953931549871457e+4) * r +
					 1.3731693765509461125e+4) * r +
					 1.9715909503065514427e+3) * r +
					 1.3314166789178437745e+2) * r +
					 3.3871328727963666080e+0) * q
		den = (((((((5.2264952788528545610e+3 * r +
					 2.8729085735721942674e+4) * r +
					 3.9307895800092710610e+4) * r +
					 2.1213794301586595867e+4) * r +
					 5.3941960214247511077e+3) * r +
					 6.8718700749205790830e+2) * r +
					 4.2313330701600911252e+1) * r +
					 1.0)
		x = num / den
		return mu + (x * sigma)
	r = p if q <= 0.0 else 1.0 - p
	r = sqrt(-log(r))
	if r <= 5.0:
		r = r - 1.6
		num = (((((((7.74545014278341407640e-4 * r +
					 2.27238449892691845833e-2) * r +
					 2.41780725177450611770e-1) * r +
					 1.27045825245236838258e+0) * r +
					 3.64784832476320460504e+0) * r +
					 5.76949722146069140550e+0) * r +
					 4.63033784615654529590e+0) * r +
					 1.42343711074968357734e+0)
		den = (((((((1.05075007164441684324e-9 * r +
					 5.47593808499534494600e-4) * r +
					 1.51986665636164571966e-2) * r +
					 1.48103976427480074590e-1) * r +
					 6.89767334985100004550e-1) * r +
					 1.67638483018380384940e+0) * r +
					 2.05319162663775882187e+0) * r +
					 1.0)
	else:
		r = r - 5.0
		num = (((((((2.01033439929228813265e-7 * r +
					 2.71155556874348757815e-5) * r +
					 1.24266094738807843860e-3) * r +
					 2.65321895265761230930e-2) * r +
					 2.96560571828504891230e-1) * r +
					 1.78482653991729133580e+0) * r +
					 5.46378491116411436990e+0) * r +
					 6.65790464350110377720e+0)
		den = (((((((2.04426310338993978564e-15 * r +
					 1.42151175831644588870e-7) * r +
					 1.84631831751005468180e-5) * r +
					 7.86869131145613259100e-4) * r +
					 1.48753612908506148525e-2) * r +
					 1.36929880922735805310e-1) * r +
					 5.99832206555887937690e-1) * r +
					 1.0)
	x = num / den
	if q < 0.0:
		x = -x
	return mu + (x * sigma)

class LapStats:
	pMin, pMax = 0.85, 1.20

	
	def __init__( self, lap_times ):
		self.set_lap_times( lap_times )
	
	def set_lap_times( self, lap_times ):
		if not lap_times:
			self.median = None
			self.mad = None
		else:
			self.median = median( lap_times )
			self.mad = median( [abs(v - self.median) for v in lap_times] )
	
	def probable_lap_range( self, laps, confidence=0.25 ):
		if self.median is None:
			return None, None
		
		# Combine the single lap distribution to a normal distribution over the given number of laps.
		# Scale mad to normal sigma with 1.4826.
		mu = self.median * laps
		sigma = self.mad * 1.4826 * sqrt(laps)
		if sigma < 0.00001:
			return mu * self.pMin, mu * self.pMax
		else:
			return inv_cdf(mu, sigma, 0.5-confidence/2.0), inv_cdf(mu, sigma, 0.5+confidence/2.0)
		
	def probable_lap_ranges( self, laps_max, confidence=0.25 ):
		lap_ranges = []
		for lap in range(2, laps_max):
			lo, hi = self.probable_lap_range(lap, confidence)
			if lap_ranges:
				lap_last, lo_last, hi_last = lap_ranges[-1]
				if hi_last > lo:
					hi_last = lo = (hi_last + lo) / 2.0
					lap_ranges[-1] = (lap_last, lo_last, hi_last)
			lap_ranges.append( (lap, lo, hi) )
		return lap_ranges

if __name__ == '__main__':
	random.seed( 17 )
	lap_times = [8*60 -30 + random.random()*60 for i in range(12)]
	s = LapStats( lap_times )
	print()
	print( s.median )
	for confidence in [0.25, 0.50, 0.75, 0.90, 0.95]:
		print()
		print( 'confidence:', confidence )
		for laps in range(1, 5):
			print( laps, s.probable_lap_range(laps, confidence) )
