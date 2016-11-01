import Utils
import Model
import datetime
import threading
from time import sleep

now = datetime.datetime.now

class Playback( threading.Thread ):
	def __init__( self, bibTimes, updateFunc ):
		super( Playback, self ).__init__( name='Playback' )
		self.bibTimes = bibTimes
		self.updateFunc = updateFunc
		self.daemon = True
		self.keepGoing = True
		
	def run( self ):
		dStart = now()
		race = Model.race
		if race.enableJChipIntegration and race.resetStartClockOnFirstTag:
			for bib in set( bib for bib, t in self.bibTimes ):
				race.addTime( bib, 0.0 )
		for bib, t in self.bibTimes:
			while 1:
				tCur = (now() - dStart).total_seconds()
				if t > tCur:
					#print 'Playback: sleeping {} seconds'.format( t - tCur )
					sleep( t - tCur )
				else:
					break
			if Model.race != race or not self.keepGoing:
				break
			#print 'Playback: addTime({},{})'.format( bib, t )
			race.addTime( bib, t )
			self.updateFunc()
		
	def terminate( self ):
		self.keepGoing = False
	