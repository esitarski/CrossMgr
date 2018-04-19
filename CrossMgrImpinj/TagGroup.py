
from datetime import datetime, timedelta
from QuadReg import QuadRegExtreme
from time import sleep
import random

# Use a reference time to convert given times to float seconds.
tRef = datetime.now()

def datetimeToTr( t ):
	return (t - tRef).total_seconds()

def trToDatetime( tr ):
	return tRef + timedelta(seconds=tr)

class TagGroupEntry( object ):
	__slots__ = ('firstRead', 'reads')
	
	def __init__( self, t, db ):
		self.firstRead = datetimeToTr( t )
		self.reads = [(self.firstRead, db)]
		
	def insert( self, t, db ):
		if self.reads[0][0] != self.firstRead:
			self.reads[-1] = (datetimeToTr(t), db)	# if a stray, replace the last entry.
		else:
			self.reads.append( (datetimeToTr(t), db) )
		
	def getBestEstimate( self ):
		try:
			trEst = QuadRegExtreme( self.reads )
		except Exception as e:
			# If error, return the first read.
			trEst = self.reads[0][0]
		
		# If the estimate lies outside the data, return the first read.
		if not self.reads[0][0] <= trEst <= self.reads[-1][0]:
			trEst = self.reads[0][0]
		return trToDatetime( trEst )
	
class TagGroup( object ):
	'''
		Process groups of tag reads and return the best time estimated using quadratic regression.
		Stray reads are also detected if there is no quiet period for the tag.
		The first read time of each stray read is returned.
	'''
	def __init__( self ):
		self.tQuiet = 0.5		# Seconds of quiet after which the tag is considered read.
		self.tStray = 8.0		# Seconds of continuous reads for tag to be considered a stray.
		
		self.tagInfo = {}
		
	def add( self, tag, t, db ):
		try:
			self.tagInfo[tag].insert( t, db )
		except KeyError:
			self.tagInfo[tag] = TagGroupEntry( t, db )

	def getReadsStrays( self, tNow=None ):
		'''
			Returns two lists:
				reads = [(tag1, t1), (tag2, t2), ...]
				strays = [(tagA, tFirstReadA), (tagB, tFirstReadB), ...]
				
			Each stray will be reported as a read the first time it is detected.
		'''
		trNow = datetimeToTr( tNow or datetime.now() )
		reads, strays = [], []
		toDelete = []
		for tag, tge in self.tagInfo.iteritems():
			if trNow - tge.reads[-1][0] >= self.tQuiet:			# Tag has left read range.
				if tge.reads[0][0] == tge.firstRead:			# Check if not a stray.
					reads.append( (tag, tge.getBestEstimate()) )
				toDelete.append( tag )
			elif tge.reads[-1][0] - self.tagFirstRead[tag] >= self.tStray:	# This is a stray.
				# Report the first read time of the stray if we have not done so.
				t = trToDatetime( tge.firstRead )
				if tge.reads[0][0] == tge.firstRead:
					reads.append( (tag, t) )
				strays.append( (tag, t) )
				del tge.reads[:-1]	# Cleanup any old reads we don't need anymore.
				
		for tag in toDelete:
			del self.tagInfo[tag]
			
		return reads, strays
	
from math import sqrt
if __name__ == '__main__':
	
	def genReadProfile( tg, t, tag, stddev=10.0 ):
		#pointCount = 15
		pointCount = 18
		xRange = 0.5
		yRange = 25
		yTop = -47
		
		yMult = yRange / ((pointCount/2.0) ** 2)
		tDelta = xRange / pointCount
		for i in xrange(pointCount):
			x = i - pointCount/2.0
			noise = random.normalvariate( 0.0, stddev )
			y = yTop - x * x * yMult
			# Report integer values, just like the reader would.
			tg.add( tag, t + timedelta( seconds=x*tDelta ), round(y+noise)  )
	
	t = datetime.now()
	for stddev in xrange(10+1):
		variance = 0.0
		samples = 1000
		for k in xrange(samples):
			tg = TagGroup()
			genReadProfile( tg, t, '111', float(stddev) )
			tEst = tg.tagInfo['111'].getBestEstimate()
			variance += (t - tEst).total_seconds() ** 2
		print '{},{}'.format( stddev, sqrt(variance / samples) )
	
	print
	tg = TagGroup()
	genReadProfile( tg, t, '111' )
	genReadProfile( tg, t-timedelta(seconds=3), '222' )
	sleep( 1.0 )
	print t, t-timedelta(seconds=3)
	reads, strays = tg.getReadsStrays()
	for tag, t in reads:
		print t, tag
