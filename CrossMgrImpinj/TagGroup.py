
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

class TagGroup( object ):
	'''
		Process groups of tag reads and return the best time estimated using quadratic regression.
		Stray reads are also detected if there is no quiet period for the tag.
		
		The first read time of a stray read is returned.
	'''
	def __init__( self ):
		self.tQuiet = 0.5		# Seconds of quiet after which the tag is considered read.
		self.tStray = 5.0		# Seconds after the tag is considered a stray.
		
		self.tagReads = {}
		self.tagFirstRead = {}
		
	def add( self, tag, t, db ):
		tr = datetimeToTr( t )
		if tag in self.tagReads:
			self.tagReads[tag].append( (tr, db) )
		else:
			self.tagFirstRead[tag] = tr
			self.tagReads[tag] = [(tr, db)]

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
		for tag, tagReads in self.tagReads.iteritems():
			if trNow - tagReads[0][0] >= self.tQuiet:			# This tag read group has ended.
				if tagReads[0][0] == self.tagFirstRead[tag]:
					tEst = QuadRegExtreme(tagReads)
					# Check that the estimated time is within the read range.
					# If not, return the first read.
					if not tagReads[0][0] <= tEst <= tagReads[-1][0]:
						tEst = tagReads[0][0]
					reads.append( (tag, trToDatetime(tEst)) )
				toDelete.append( tag )
			elif tagReads[-1][0] - self.tagFirstRead[tag] >= self.tStray:	# This is a stray.
				# Report the first read time of the stray if we have not done so.
				if tagReads[0][0] == self.tagFirstRead[tag]:
					reads.append( (tag, trToDatetime(tagReads[0][0])) )
				strays.append( (tag, trToDatetime(self.tagFirstRead[tag])) )
				del tagReads[0:len(reads)-1]	# Cleanup reads we don't need anymore.
				
		for tag in toDelete:
			del self.tagReads[tag]
			del self.tagFirstRead[tag]
			
		return reads, strays
		
if __name__ == '__main__':
	tg = TagGroup()
	t = datetime.now()
	delta = timedelta( seconds=0.01 )
	for i in xrange(-10, 10):
		tg.add( '111', t + i*delta, 1000-i**2 + 5*(random.random()-0.5) )
		tg.add( '222', t - timedelta(seconds=10) + i*delta, 1000-i**2 + 5*(random.random()-0.5) )
	sleep( 1.0 )
	print t, tg.getReadsStrays()
