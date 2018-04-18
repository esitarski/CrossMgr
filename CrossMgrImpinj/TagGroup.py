
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
		
	def add( self, t, db ):
		self.reads.append( (datetimeToTr(t), db) )
		
	def replaceLast( self, t, db ):
		self.reads[-1] = (datetimeToTr(t), db)
	
	def isStray( self ):
		return self.reads[-1][0] != self.firstRead
	
	def getBestEstimate( self ):
		try:
			trEst = QuadRegExtreme( self.reads )
		except:
			trEst = self.reads[0][0]
		# If the estimate lies outside the data, return the first read.
		if not self.reads[0][0] <= trEst <= self.reads[-1][0]:
			trEst = self.reads[0][0]
		return trToDatetime( trEst )
	
class TagGroup( object ):
	'''
		Process groups of tag reads and return the best time estimated using quadratic regression.
		Stray reads are also detected if there is no quiet period for the tag.
		
		The first read time of a stray read is returned.
	'''
	def __init__( self ):
		self.tQuiet = 0.5		# Seconds of quiet after which the tag is considered read.
		self.tStray = 8.0		# Seconds of continuous reads for tag to be considered a stray.
		
		self.tagInfo = {}
		
	def add( self, tag, t, db ):
		try:
			tge = self.tagInfo[tag]
			if tge.isStray():
				tge.replaceLast( t, db )
			else:
				tge.add( t, db )
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
				if tge.reads[0][0] == tge.firstRead:
					reads.append( (tag, tge.getBestEstimate()) )
				toDelete.append( tag )
			elif tge.reads[-1][0] - self.tagFirstRead[tag] >= self.tStray:	# This is a stray.
				# Report the first read time of the stray if we have not done so.
				t = trToDatetime( tge.firstRead )
				if tge.reads[0][0] == tge.firstRead:
					reads.append( (tag, t) )
				strays.append( (tag, t) )
				del tge.reads[:-1]	# Cleanup old reads we don't need anymore.
				
		for tag in toDelete:
			del self.tagInfo[tag]
			
		return reads, strays
		
if __name__ == '__main__':
	tg = TagGroup()
	t = datetime.now()
	delta = timedelta( seconds=0.01 )
	for i in xrange(-10, 10):
		tg.add( '111', t + i*delta, 1000-i**2/3.0 + 5*(random.random()-0.5) )
		tg.add( '222', t - timedelta(seconds=10) + i*delta, 1000-i**2 + 5*(random.random()-0.5) )
	sleep( 1.0 )
	print t
	reads, strays = tg.getReadsStrays()
	for tag, t in reads:
		print t, tag
