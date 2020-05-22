import sys
import six
import random
import operator
import itertools
from time import sleep
from datetime import datetime, timedelta
from six.moves.queue import Queue, Empty
from QuadReg import QuadRegExtreme, QuadRegRemoveOutliersRobust, QuadRegRemoveOutliersRansac, QuadReg

# Use a reference time to convert given times to float seconds.
tRef = datetime.now()

tQuiet = 0.4		# Seconds of quiet after which the tag is considered read.
tStray = 8.0		# Seconds of continuous reads for tag to be considered a stray.

def datetimeToTr( t ):
	return (t - tRef).total_seconds()

def trToDatetime( tr ):
	return tRef + timedelta(seconds=tr)

QuadraticRegressionMethod, StrongestReadMethod, FirstReadMethod = 0, 1, 2
MethodNames = ('Quad Regression', 'Strongest Read', 'First Read Time')

MostReadsChoice, DBMaxChoice = 0, 1
AntennaChoiceNames = ('Most Reads', 'Max Signal dB')
	
class AntennaReads( object ):
	__slots__ = ('firstRead', 'reads', 'trDbMax', 'dbMax')
	
	def __init__( self, tr, db ):
		self.firstRead = tr
		self.reads = [(tr, db)]
		self.trDbMax, self.dbMax = tr, db
	
	def add( self, tr, db ):
		if self.isStray:
			# if a stray, just replace the last entry.
			if len(self.reads) > 1:
				del self.reads[:-1]		
			self.reads[-1] = (tr, db)
		else:
			self.reads.append( (tr, db) )
			if db > self.dbMax:
				self.trDbMax, self.dbMax = tr, db
	
	@property
	def isStray( self ):
		return self.reads[-1][0] - self.firstRead > tStray
	
	@property
	def lastRead( self ):
		return self.reads[-1][0]
	
	@property
	def medianRead( self ):
		if (len(self.reads) & 1) == 1:
			return self.reads[len(reads)//2][0]
		else:
			iMid = len(self.reads)//2
			return (self.reads[iMid-1][0] + self.reads[iMid][0]) / 2.0
	
	def getBestEstimate( self, method=QuadraticRegressionMethod, removeOutliers=True ):
		if self.isStray:
			return self.firstRead, 1
		
		if method == QuadraticRegressionMethod and len(self.reads) >= 3:
			try:
				trEst, sampleSize = QuadRegExtreme(self.reads, QuadRegRemoveOutliersRansac if removeOutliers else QuadReg), len(self.reads)
			except Exception as e:
				# If error, return the strongest read.
				trEst, sampleSize = self.trDbMax, 1
			
			# If the estimate lies outside the data, return the strongest read.
			if not self.reads[0][0] <= trEst <= self.reads[-1][0]:
				trEst, sampleSize = self.trDbMax, 1
			return trEst, sampleSize
		
		else:	# method == StrongestReadMethod or len(self.reads) < 3
			return self.trDbMax, len(self.reads)
		
class TagGroupEntry( object ):
	__slots__ = ('antennaReads', 'firstReadMin', 'lastReadMax', 'isStray')
	
	def __init__( self, antenna, t, db ):
		self.antennaReads = [None, None, None, None]
		self.firstReadMin, self.lastReadMax = sys.float_info.max, -sys.float_info.max
		self.isStray = False
		self.add( antenna, t, db )
		
	def add( self, antenna, t, db ):
		tr = datetimeToTr(t)
		iAntenna = antenna - 1
		if not self.antennaReads[iAntenna]:
			self.antennaReads[iAntenna] = AntennaReads(tr, db)
		else:
			self.antennaReads[iAntenna].add( tr, db )
		
		if tr < self.firstReadMin: self.firstReadMin = tr
		if tr > self.lastReadMax:  self.lastReadMax = tr
	
	def setStray( self ):
		for ar in self.antennaReads:
			if ar:
				del ar.reads[:-1]	# Delete all but last read.
		self.isStray = True
	
	def getBestEstimate( self, method=QuadraticRegressionMethod, antennaChoice=MostReadsChoice, removeOutliers=True ):
		if self.isStray:
			return trToDatetime( self.firstReadMin ), 1, 0
		
		if method == QuadraticRegressionMethod:
			a, arBest = max(
				((a, ar) for a, ar in enumerate(self.antennaReads) if ar),
				key=((lambda x: (len(x[1].reads), x[1].dbMax)) if antennaChoice == MostReadsChoice else (lambda x: (x[1].dbMax, len(x[1].reads))))
			)
			tr, sampleSize = arBest.getBestEstimate( method, removeOutliers )
			return trToDatetime(tr), sampleSize, a+1
		
		else: # method == StrongestReadMethod:
			a, arBest = max( ((a, ar) for a, ar in enumerate(self.antennaReads) if ar), key=lambda x: x[1].dbMax )
			tr, sampleSize = arBest.trDbMax, len(arBest.reads)
			return trToDatetime(tr), sampleSize, a+1
		
	def __repr__( self ):
		return 'TagGroupEntry({},{})'.format(self.firstReadMin, self.lastReadMax)
	
class TagGroup( object ):
	'''
		Process groups of tag reads and return the best time estimated using quadratic regression.
		Stray reads are also detected if there is no quiet period for the tag.
		The first read time of each stray read is returned.
	'''
	def __init__( self ):
		self.q = Queue()
		self.tagInfo = {}
		
	def add( self, antenna, tag, t, db ):
		self.q.put((antenna, tag, t, db))

	def flush( self ):
		# Process all waiting reads.
		while 1:
			try:
				antenna, tag, t, db = self.q.get(False)
			except Empty:
				break
			try:
				self.tagInfo[tag].add( antenna, t, db )
			except KeyError:
				self.tagInfo[tag] = TagGroupEntry( antenna, t, db )
			self.q.task_done()
			
	def getReadsStrays( self, tNow=None, method=QuadraticRegressionMethod, antennaChoice=MostReadsChoice, removeOutliers=True ):
		'''
			Returns two lists:
				reads = [(tag1, t1, sampleSize1, antennaID1), (tag2, t2, sampleSize2, , antennaID2), ...]
				strays = [(tagA, tFirstReadA), (tagB, tFirstReadB), ...]
				
			Each stray will be reported as a read the first time it is detected.
		'''
		self.flush()
		
		trNow = datetimeToTr( tNow or datetime.now() )
		reads, strays = [], []
		toDelete = []
		
		for tag, tge in self.tagInfo.items():
			if trNow - tge.lastReadMax >= tQuiet:				# Tag has left read range.
				if not tge.isStray:
					t, sampleSize, antennaID = tge.getBestEstimate(method, antennaChoice, removeOutliers)
					reads.append( (tag, t, sampleSize, antennaID) )
				toDelete.append( tag )
			elif tge.lastReadMax - tge.firstReadMin >= tStray:	# This is a stray.
				t = trToDatetime( tge.firstReadMin )
				if not tge.isStray:
					tge.setStray()
					reads.append( (tag, t, 1, 0) )				# Report stray first read time.
				strays.append( (tag, t) )
				
		for tag in toDelete:
			del self.tagInfo[tag]
		
		reads.sort( key=operator.itemgetter(1,0))
		strays.sort( key=operator.itemgetter(1,0) )
		return reads, strays
	
if __name__ == '__main__':

	# method = StrongestReadMethod
	method = QuadraticRegressionMethod

	t = datetime.now()
	tFirst = None
	tg = TagGroup()
	data = '''10.16.21.147,82DD45F2339C3D0F556E5803,123414.636989,2,-61
10.16.21.147,82DD45F2339C3D0F556E5803,123414.676506,2,-55
10.16.21.147,82DD45F2339C3D0F556E5803,123414.711024,1,-49
10.16.21.147,82DD45F2339C3D0F556E5803,123414.738245,0,-42
10.16.21.147,82DD45F2339C3D0F556E5803,123414.767357,0,-39
10.16.21.147,82DD45F2339C3D0F556E5803,123414.799116,0,-39
10.16.21.147,82DD45F2339C3D0F556E5803,123414.831069,1,-41
10.16.21.147,82DD45F2339C3D0F556E5803,123414.858307,0,-42
10.16.21.147,82DD45F2339C3D0F556E5803,123414.897999,0,-48
10.16.21.147,82DD45F2339C3D0F556E5803,123414.927323,1,-55
10.16.21.147,82DD45F2339C3D0F556E5803,123414.983460,1,-66'''
	for line in data.split():
		fields = line.split(',')
		tCur = float(fields[2])
		if tFirst is None:
			tFirst = tCur
		db = int(fields[4])
		tg.add( 1, fields[1], t + timedelta( seconds=tCur - tFirst ), db  )
	reads, strays = tg.getReadsStrays( t + timedelta(seconds=5.0) )
	print( reads )
	
	def genReadProfile( tg, t, tag, antenna=1, yTop=-47, stddev=10.0 ):
		#pointCount = 15
		pointCount = 18
		xRange = 0.5
		yRange = 25
		
		yMult = yRange / ((pointCount/2.0) ** 2)
		tDelta = xRange / pointCount
		for i in range(pointCount):
			x = i - pointCount/2.0
			noise = random.normalvariate( 0.0, stddev )
			y = yTop - x * x * yMult
			# Report integer values, just like the reader would.
			tg.add( antenna, tag, t + timedelta( seconds=x*tDelta ), round(y+noise)  )
	
	t = datetime.now()
	for stddev in range(10+1):
		variance = 0.0
		samples = 1000
		for k in range(samples):
			tg = TagGroup()
			genReadProfile( tg, t, '111', stddev=float(stddev) )
			tg.flush()
			tEst, sampleSize, antennaID = tg.tagInfo['111'].getBestEstimate( method )
			variance += (t - tEst).total_seconds() ** 2
		print( '{},{}'.format( stddev, (variance / samples)**0.5 ) )
	
	print()
	tg = TagGroup()
	for antennaID in range(1,3):
		genReadProfile( tg, t, '111', antenna=antennaID, yTop=-47+antennaID )
		genReadProfile( tg, t-timedelta(seconds=3), '222', antenna=antennaID, yTop=-47+antennaID )
	sleep( 1.0 )
	print( t, t-timedelta(seconds=3) )
	reads, strays = tg.getReadsStrays(method=method)
	for tag, t, sampleSize, antennaID in reads:
		print( t, tag, sampleSize, antennaID )
