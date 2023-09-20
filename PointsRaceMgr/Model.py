import re
import random
import operator
import itertools
import datetime
import sys
from collections import namedtuple

#------------------------------------------------------------------------------
# Define a global current race.
race = None

def getRace():
	global race
	return race

def newRace():
	global race
	race = Race()
	return race

def setRace( r ):
	global race
	race = r

def fixBibsNML( bibs, bibsNML, isFinish=False ):
	bibsNMLSet = set( bibsNML )
	bibsNew = [b for b in bibs if b not in bibsNMLSet]
	if isFinish:
		bibsNew.extend( bibsNML )
	return bibsNew
	
#------------------------------------------------------------------------------------------------------------------
class Rider:
	Finisher, DNF, DNS, DSQ, PUL = tuple( range(5) )
	statusNames = ('Finisher', 'DNF', 'DNS', 'DSQ')
	statusSortSeq = {
		'Finisher':1,	Finisher:1,
	  'DNF':2,		DNF:2,
	  'DNS':3,		DNS:3,
	  'DSQ':4,		DSQ:4,
	  'PUL':5,		PUL:5,
	}
	pullSequence = 0	# Sequence that this rider was pulled.
	
	def __init__( self, num ):
		self.num = num
		self.reset()
		
	def reset( self ):
		self.pointsTotal = 0
		self.sprintPlacePoints = {}
		self.sprintsTotal = 0
		self.lapsTotal = 0
		self.updown = 0
		self.numWins = 0
		self.existingPoints = 0
		self.finishOrder = 1000
		self.pullSequence = 0
		self.status = Rider.Finisher
		
	def addSprintResult( self, sprint, place, bibs ):
		points, place, tie = race.getSprintPoints(sprint, place, bibs)
		if points > 0:
			self.pointsTotal += points
			self.sprintsTotal += points
			self.sprintPlacePoints[sprint] = (place, points, tie)
		
		if place == 1:
			self.numWins += 1

		if sprint == race.getNumSprints():
			self.finishOrder = place
	
	def addUpDown( self, updown ):
		assert updown == -1 or updown == 1
		self.updown += updown
		self.pointsTotal += race.pointsForLapping * updown
		self.lapsTotal += race.pointsForLapping * updown

	def addExistingPoints( self, existingPoints ):
		if existingPoints == int(existingPoints):
			existingPoints = int(existingPoints)
		self.existingPoints += existingPoints
		self.pointsTotal += existingPoints
		
	def getKey( self ):
		if   race.rankBy == race.RankByPoints:
			return (Rider.statusSortSeq[self.status], -self.pointsTotal, self.finishOrder, self.num)
		elif race.rankBy == race.RankByLapsPoints:
			return (Rider.statusSortSeq[self.status], -self.updown, -self.pointsTotal, self.finishOrder, self.num)
		else:	# race.RankByLapsPointsNumWins
			return (Rider.statusSortSeq[self.status], -self.updown, -self.pointsTotal, -self.numWins, self.finishOrder, self.num)

	def tiedWith( s, r ):
		return s.getKey()[:-1] == r.getKey()[:-1]	# Use all scoring criteria except bib number.
	
	@property
	def pulled( self ):
		return self.pullSequence != 0
	
	def __repr__( self ):
		return "Rider( {}, {}, {}, {}, {} )".format(
			self.num, self.pointsTotal, self.updown, self.numWins,
			self.statusNames[self.status]
		)
		
class RiderInfo:
	FieldNames  = ('bib', 'existing_points', 'last_name', 'first_name', 'team', 'team_code', 'license', 'nation_code', 'uci_id')
	HeaderNames = ('Bib', 'Existing\nPoints', 'Last Name', 'First Name', 'Team', 'Team Code', 'License', 'Nat Code', 'UCI ID')

	def __init__( self, bib, last_name='', first_name='', team='', team_code='', license='', uci_id='', nation_code='', existing_points=0.0, status=Rider.Finisher ):
		self.bib = int(bib)
		self.last_name = last_name
		self.first_name = first_name
		self.team = team
		self.team_code = team_code
		self.license = license
		self.uci_id = uci_id
		self.nation_code = nation_code
		try:
			self.existing_points = float(existing_points)
		except:
			self.existing_points = 0.0
		
		self.status = status
		if isinstance(existing_points, str):
			for s, statusName in enumerate(Rider.statusNames):
				if existing_points.lower() == statusName.lower():
					self.status = s
					break
			if existing_points.lower() == 'DQ'.lower():
				self.status = Rider.DSQ

	def __eq__( self, ri ):
		return all(getattr(self,a) == getattr(ri,a) for a in self.FieldNames)
		
	def __repr__( self ):
		return 'RiderInfo({})'.format(','.join('{}="{}"'.format(a,getattr(self,a)) for a in self.FieldNames))

class GetRank:
	def __init__( self ):
		self.rankLast, self.rrLast = None, None
	
	def __call__( self, rank, rr ):
		if rr.status == Rider.PUL:
			self.rankLast, self.rrLast = rank, rr
			return 'PUL {}'.format(rank)
		elif rr.status != Rider.Finisher:
			return Rider.statusNames[rr.status]
		elif self.rrLast and self.rrLast.tiedWith(rr):
			return '{}'.format(self.rankLast)
		else:
			self.rankLast, self.rrLast = rank, rr
			return '{}'.format(rank)
		
class RaceEvent:
	DNS, DNF, PUL, DSQ, LapUp, LapDown, Sprint, Finish, Break, Chase, OTB, NML, Compact = tuple( range(13) )
	
	Events = (
		('Sp', Sprint),
		('+ Lap', LapUp),
		('- Lap', LapDown),
		('DNF', DNF),
		('Finish', Finish),
		('PUL', PUL),
		('DNS', DNS),
		('DSQ', DSQ),
	)

	States = (
		('Break', Break),
		('Chase', Chase),
		('OTB', OTB),
		('NML', NML),
		('CMPCT', Compact),
	)
	EventName = {v:n for n,v in Events}
	EventName.update( {v:n for n,v in States} )
	
	@staticmethod
	def getCleanBibs( bibs ):
		if isinstance( bibs, str ):
			bibs = bibs.replace( '-', '=' )			# accept the minus char for the equal char as those keys are next to each other on the keyboard.
			bibs = re.sub( r'[^\d=]', ' ', bibs)	# replace all non-digit/equals with space.
			bibs = bibs.replace('=', ' - ')			# replace all equal signs with dashes separated by spaces.
			bibs = re.sub( r'- +(\d)' , lambda m: '-' + m.group(1), bibs )		# remove spaces between dashes and numbers to form negative numbers.
			biblist = []
			for v in bibs.split():
				try:
					biblist.append( int(v) )
				except:
					continue
			bibs = biblist
				
		seen = set()
		nonDupBibs = []
		for b in bibs:
			if abs(b) not in seen:
				seen.add( abs(b) )
				nonDupBibs.append( b )

		# Negative bibs indicate a tie with the preceeding position.  eg. 10 -20 30 40 means 1st place: 10, 20; 3rd place 30, 4th place 40.
		if nonDupBibs:
			nonDupBibs[0] = abs(nonDupBibs[0])
		return nonDupBibs
	
	def __init__( self, eventType=Sprint, bibs=[] ):
		if not isinstance(eventType, int):
			for n, v in self.Events:
				if eventType.startswith(n):
					eventType = v
					break
			else:
				eventType = self.Sprint
		
		self.eventType = eventType
		self.setBibs( bibs )

	def setBibs( self, bibs ):
		self.bibs = RaceEvent.getCleanBibs( bibs )
		if self.eventType not in (self.Sprint, self.Finish):
			self.bibs = [abs(bib) for bib in self.bibs]

	def bibStr( self ):
		return ','.join( '{}'.format(b) for b in self.bibs).replace(',-', '=')

	@staticmethod
	def isStateEvent( eventType ):
		return eventType >= RaceEvent.Break

	def isState( self ):
		return RaceEvent.isStateEvent( self.eventType )
	
	@property
	def eventTypeName( self ):
		return self.EventName[self.eventType]
			
	def __eq__( s, t ):
		return s.eventType == t.eventType and s.bibs == t.bibs
		
	def __repr__( self ):
		return 'RaceEvent( eventType={}, bibs=[{}] )'.format( self.eventType, self.bibStr() )
		
class Race:
	RankByPoints = 0
	RankByLapsPoints = 1
	RankByLapsPointsNumWins = 2

	pointsForPlaceDefault = {
		1 : 5,
		2 : 3,
		3 : 2,
		4 : 1,
	}
	startLaps = 0
	
	def __init__( self ):
		self.reset()

	def reset( self ):
		self.name = '<RaceName>'
		self.communique = ''
		self.category = '<Category>'
		self.notes = ''
		self.sprintEvery = 10
		self.courseLength = 250.0
		self.courseLengthUnit = 0	# 0 = Meters, 1 = Km
		self.laps = 160
		self.rankBy = Race.RankByPoints		# 0 = Points only, 1 = Distance, then points, 2 = 
		self.date = datetime.date.today()
		self.pointsForLapping = 20
		self.doublePointsForLastSprint = True
		self.doublePointsOnSprint = set()		# set other sprints to double points on.
		self.snowball = False
		self.pointsForPlace = Race.pointsForPlaceDefault.copy()

		self.events = []
		self.riders = {}
		self.riderInfo = []
		
		self.sprintCount = 0

		self.isChangedFlag = True
	
	def getRaceType( self ):
		if self.snowball:
			return 'Snowball Race'
		
		if (	self.rankBy == Race.RankByPoints and
				self.pointsForLapping == 20 and
				self.doublePointsForLastSprint == True
			):
			return 'Points Race' if len(self.pointsForPlace) > 1 else 'Tempo Race'
		
		return ''
	
	def getDistance( self ):	# Always return in km
		return self.courseLength * self.laps / (1000.0 if self.courseLengthUnit == 0 else 1.0)
	
	def newNext( self ):
		self.events = []
		self.riderInfo = []
		self.isChangedFlag = True
	
	def getDistanceStr( self ):
		d = self.courseLength * self.laps
		if d - int(d) < 0.001:
			return '{:,}'.format(int(d)) + ['m','km'][self.courseLengthUnit]
		else:
			return '{:,.2f}'.format(d) + ['m','km'][self.courseLengthUnit]
	
	def setattr( self, attr, v ):
		if getattr(self, attr, None) != v:
			setattr( self, attr, v )
			self.setChanged()
			return True
		else:
			return False
	
	def getNumSprints( self ):
		try:
			numSprints = max(0, self.laps - self.startLaps) // self.sprintEvery
		except:
			numSprints = 0
		return numSprints
	
	def getSprintCount( self ):
		Sprint = RaceEvent.Sprint
		return sum( 1 for e in self.events if e.eventType == Sprint )
	
	def isDoublePoints( self, sprint ):
		if not hasattr(self, 'doublePointsOnSprint'):
			self.doublePointsOnSprint = set()
		return sprint in self.doublePointsOnSprint or (self.doublePointsForLastSprint and sprint == self.getNumSprints())
	
	def getSprintLabel( self, sprint ):
		if self.isDoublePoints(sprint):
			return 'Sp{} \u00D72'.format(sprint)
		return 'Sp{}'.format(sprint)
	
	def getMaxPlace( self ):
		maxPlace = 2
		for place, points in self.pointsForPlace.items():
			if points >= 0:
				maxPlace = max( maxPlace, place )
		return maxPlace
	
	def getRider( self, bib ):
		bib = abs(bib)
		try:
			return self.riders[bib]
		except KeyError:
			self.riders[bib] = Rider( bib )
			return self.riders[bib]
			
	def getSprintPoints( self, sprint, place, bibs=None ):
		# Adjust the place if there is a tie.
		while place > 1:
			try:
				bib = bibs[place-1]
			except IndexException:
				break
			if bib < 0:		# If the bib number is negative, tie with the previous position.
				place -= 1
			else:
				break
		
		# If this is a tie, the following bib will be negative.
		try:
			tie = (bibs[place] < 0)
		except:
			tie = False
		
		points = self.pointsForPlace.get(place,0)
		if self.snowball:
			points *= sprint
		if self.isDoublePoints(sprint):
			points *= 2
		return points, place, tie
	
	def cleanNonFinishers( self, bibs ):
		# Remove any non-finishers from this sprint (mistakes).
		bibs = [b for b in bibs if self.getRider(b).status == Rider.Finisher]
		if bibs:	# Ensure that the first bib is not a "tie".
			bibs[0] = abs(bibs[0])
		return bibs
	
	def processEvents( self ):
		Finisher = Rider.Finisher

		self.riders = {}
		self.isFinished = False
		
		for info in self.riderInfo:
			r = self.getRider(info.bib)
			r.addExistingPoints( info.existing_points )
			r.status = info.status
		
		numSprints = self.getNumSprints()
		self.sprintCount = 0
		pullSequenceCur = 0
		for iEvent, e in enumerate(self.events):
			
			# Ensure the eventType matches the number of sprints.
			if e.eventType == RaceEvent.Finish and self.sprintCount != numSprints-1:
				e.eventType = RaceEvent.Sprint
			elif e.eventType == RaceEvent.Sprint and self.sprintCount == numSprints-1:
				e.eventType = RaceEvent.Finish
				
			if e.eventType == RaceEvent.Sprint:
				self.sprintCount += 1
				bibs = self.cleanNonFinishers( e.bibs )
				for place, b in enumerate(bibs, 1):
					self.getRider(b).addSprintResult( self.sprintCount, place, bibs )
			
			elif e.eventType == RaceEvent.Finish:
				self.isFinished = True
				self.sprintCount += 1
				if iEvent != len(self.events)-1 and self.events[iEvent+1].eventType == RaceEvent.NML:
					bibs = fixBibsNML( self.cleanNonFinishers(e.bibs), self.cleanNonFinishers(self.events[iEvent+1].bibs), True )
				else:
					bibs = self.cleanNonFinishers( e.bibs )
				
				for place, b in enumerate(bibs, 1):
					# addSprintResult also updates the finishOrder and processes ties.
					self.getRider(b).addSprintResult( self.sprintCount, place, bibs )
				
			elif e.eventType == RaceEvent.LapUp:
				for b in self.cleanNonFinishers(e.bibs):
					self.getRider(b).addUpDown(1)
			elif e.eventType == RaceEvent.LapDown:
				for b in self.cleanNonFinishers(e.bibs):
					self.getRider(b).addUpDown(-1)

			elif e.eventType == RaceEvent.DNF:
				for b in e.bibs:
					self.getRider(b).status = Rider.DNF
			elif e.eventType == RaceEvent.DNS:
				for b in e.bibs:
					self.getRider(b).status = Rider.DNS
			elif e.eventType == RaceEvent.PUL:
				pullSequenceCur += 1
				for b in e.bibs:
					self.getRider(b).pullSequence = pullSequenceCur
			elif e.eventType == RaceEvent.DSQ:
				for b in e.bibs:
					self.getRider(b).status = Rider.DSQ

		# Post-process pulled riders.  Put them in reverse pull order in the finish order.
		# Of course, points, +/- laps, etc. will be taken into account before finish order.
		pulled = []
		non_pulled_finishers = []
		for r in self.riders.values():
			if r.status == Finisher:
				if r.pulled:
					pulled.append( r )
				else:
					non_pulled_finishers.append( r )
		
		finishOrderMax = len(non_pulled_finishers)
		if pulled:
			# Fix up the existing finish order.
			for r in non_pulled_finishers:
				if r.finishOrder >= 1000:
					r.finishOrder = finishOrderMax
			
			pulled.sort( key=operator.attrgetter('pullSequence'), reverse=True )
			for place, r in enumerate(pulled, finishOrderMax+1):
				r.finishOrder = place
			# Adjust the pull order for ties.
			for rPrev, rNext in itertools.pairwise(pulled):
				if rNext.pullSequence == rPrev.pullSequence:
					rNext.finishOrder = rPrev.finishOrder
		
	def isChanged( self ):
		return self.isChangedFlag

	def setChanged( self, changed = True ):
		self.isChangedFlag = changed
		#traceback.print_stack()
	
	def getRiders( self ):
		self.processEvents()
		return sorted( self.riders.values(), key=operator.methodcaller('getKey') )
		
	def setRiderInfo( self, riderInfo ):
		self.isChangedFlag |= (self.riderInfo != riderInfo)
		self.riderInfo = riderInfo

	def setEvents( self, events ):
		self.isChangedFlag |= (self.events != events)
		self.events = events
		
	def _populate( self ):
		self.reset()
		self.events.append( RaceEvent(RaceEvent.DNS, [41,42]) )
		random.seed( 0xed )
		bibs = list( range(10,34) )
		self.events.append( RaceEvent(RaceEvent.Break, bibs=[13,14]) )
		self.events.append( RaceEvent(RaceEvent.LapUp, bibs=[13,14]) )
		self.events.append( RaceEvent(RaceEvent.OTB, bibs=[14,15]) )
		self.events.append( RaceEvent(RaceEvent.LapDown, bibs=[14,15]) )
		self.events.append( RaceEvent(RaceEvent.Compact, bibs=[]) )
		
		def addTies( bibList ):
			bibList = ','.join( '{}'.format(b*random.choice([-1,1,1,1])) for b in bibList )	# 0.2 probability of ties.
			return bibList.replace( '-,', '=')
		
		for lap in range(50,-1,-10):
			random.shuffle( bibs )
			self.events.append( RaceEvent(bibs=addTies(bibs[:5])) )
		self.events.append( RaceEvent(RaceEvent.DNF, [51,52]) )
		self.events.append( RaceEvent(RaceEvent.DSQ, [61,62]) )
		random.shuffle( bibs )
		self.events.append( RaceEvent(RaceEvent.Finish, addTies(bibs)) )
		self.setChanged()

if __name__ == '__main__':
	r = newRace()
	r._populate()
