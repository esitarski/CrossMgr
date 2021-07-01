import sys
import copy
import random
import datetime
import traceback
from operator import attrgetter

from collections import defaultdict
import Utils

QualifyingTimeDefault = 99*60*60

Sprint200mQualificationCompetitionTime = 60.0
SprintFinalCompetitionTime = 3*60.0

KeirinCompetitionTime = 5*60.0

class Rider:
	status = ''
	seeding_rank = 0
	uci_points = 0
	
	fields = { 'bib', 'first_name', 'last_name', 'team', 'team_code', 'uci_id', 'qualifying_time', 'uci_points', 'seeding_rank', 'status' }
	def __init__( self, bib,
			first_name = '', last_name = '', team = '', team_code = '', uci_id = '',
			qualifying_time = QualifyingTimeDefault,
			uci_points = 0,
			seeding_rank = 0,
			status = ''
		):
		self.bib = int(bib)
		self.first_name = first_name
		self.last_name = last_name
		self.team = team
		self.team_code = team_code
		self.uci_id = uci_id
		self.qualifying_time = float(qualifying_time)
		self.iSeeding = 0								# Actual value in the seeding list.
		self.uci_points = float(uci_points or 0)
		self.seeding_rank = int(seeding_rank or 0)
		self.status = status
	
	aliases = {
		'bib#':'bib',
		'bib_#':'bib',
		'#':'bib',
		'num':'bib',
		'bibnum':'bib',
		'bib_num':'bib',
		
		'name':'full_name',
		'rider_name':'full_name',
		
		'first':'first_name',
		'fname':'first_name',
		'firstname':'first_name',
		'rider_first':'first_name',
		
		'last':'last_name',
		'lname':'last_name',
		'lastname':'last_name',
		'rider_last':'last_name',
		
		'uciid':'uci_id',
		'rider_uciid':'uci_id',
		
		'ucipoints':'uci_points',
		'points':'uci_points',
		'rider_ucipoints':'uci_points',
		
		'qualifying':'qualifying_time',
		'time':'qualifying_time',
		'rider_time':'qualifying_time',
		
		'rank':'seeding_rank',
		
		'rider_team':'team',
		'teamcode':'team_code',
		
		'rider_status':'status',
	}
	aliases.update( {v:v for v in aliases.values()} )
	
	@staticmethod	
	def GetHeaderNameMap( headers ):
		header_map = {}
		for col, h in enumerate(headers):
			h = h.strip().lower().replace(' ', '_')
			h = Rider.aliases.get( h, h )
			if h in Rider.fields:
				header_map[h]  = col
		return header_map

	def isOpen( self ):
		return self.last_name == 'OPEN'
		
	def copyDataFields( self, r ):
		if r == self:
			return
			
		fields = ('first_name', 'last_name', 'team', 'team_code', 'uci_id', 'uci_points', 'seeding_rank')
		for attr in fields:
			setattr( self, attr, getattr(r, attr) )
		return self
		
	def key( self ):
		return tuple( getattr(self, a) for a in ('bib', 'first_name', 'last_name', 'team', 'team_code', 'uci_id', 'qualifying_time', 'uci_points', 'seeding_rank', ) )
	
	@staticmethod
	def getKeyQualifying( isKeirin ):
		if isKeirin:
			return attrgetter('status', 'iSeeding')
		else:
			return attrgetter('status', 'qualifying_time', 'iSeeding')
	
	@property
	def qualifying_time_text( self ):
		return Utils.SecondsToStr(self.qualifying_time) if self.qualifying_time < QualifyingTimeDefault else ''
		
	@property
	def uci_points_text( self ):
		return '{:.2f}'.format(self.uci_points) if self.uci_points else ''
		
	@property
	def full_name( self ):
		return ', '.join( n for n in [self.last_name.upper(), self.first_name] if n )
	
	@property
	def bib_full_name( self ):
		return '({}) {}'.format( self.bib, self.full_name ) if self.bib else self.full_name
	
	@property
	def short_name( self ):
		if self.last_name and self.first_name:
			return '{}, {}.'.format(self.last_name.upper(), self.first_name[:1])
		return self.last_name.upper() if self.last_name else self.first_name
	
	@property
	def bib_short_name( self ):
		return '{} {}'.format(self.bib, self.short_name)
	
	@property
	def long_name( self ):
		n = self.full_name
		return '{} ({})'.format(n, self.team) if self.team else n
		
	def __repr__( self ):
		return '{}'.format(self.bib)

#------------------------------------------------------------------------------------------------

class State:
	def __init__( self ):
		self.labels = {}		# Riders bound to competition labels.
		self.noncontinue = {}
		self.OpenRider = Rider( bib=0, last_name='OPEN', qualifying_time=QualifyingTimeDefault + 1.0 )
		
	def setQualifyingInfo( self, riders, competition ):
		riders = sorted(
			(r for r in riders if r.status != 'DNQ'),
			key = Rider.getKeyQualifying(competition.isKeirin),
		)[:competition.starters]
		
		self.labels = { 'N{}'.format(i):rider for i, rider in enumerate(riders,1) }
		
		# Initialize extra open spaces to make sure we have enough starters.
		self.labels.update( {'N{}'.format(i):self.OpenRider for i in range(len(riders)+1, 128)} )
		self.OpenRider.qualifying_time = QualifyingTimeDefault + 1.0

	def inContention( self, label ):
		return self.labels.get(label, None) != self.OpenRider and label not in self.noncontinue
		
	def canReassignStarters( self ):
		''' Check if no competitions have started and we can reasign starters. '''
		return all( label.startswith('N') for label in self.labels.keys() )
		
	def __repr__( self ):
		st = [(k,v) for k,v in self.labels.items() if not str(v).startswith('0')]
		return ','.join('{}:{}'.format(k,v) for k,v in st) if st else '<<< no state >>>'

#------------------------------------------------------------------------------------------------

class Start:
	placesTimestamp = None		# Timestamp when places were modified.
	
	finishCode = {
		'Inside':	1,
		'DNF':		2,
		'DNS':		3,
		'DQ':		4,
	}
	
	warning = set()
	
	def __init__( self, event, lastStart ):
		self.event = event
		self.lastStart = lastStart
		self.startPositions = []
		self.finishPositions = []	# id, including finishers, DNF and DNS.
		self.continuingPositions = []	# id, including finishers - no DNF and DNS.
		self.places = {}		# In the format of places[composition] = place, place in 1, 2, 3, 4, etc.
		self.times = {}			# In the format of times[1] = winner's time, times[2] = runner up's time, etc.
		self.relegated = set()	# Rider assigned a relegated position in this heat.
		self.inside = []		# Rider required to take inside position on next start.
		self.noncontinue = {}	# In the format of noncontinue[composition] = reason
		self.restartRequired = False
		self.canDrawLots = False

		remainingComposition = self.getRemainingComposition()
		
		if not lastStart:
			self.heat = 1
			self.firstStartInHeat = True
			self.startPositions = [c for c in remainingComposition]
			random.shuffle( self.startPositions )
			self.canDrawLots = True
		else:
			if lastStart.restartRequired:
				self.firstStartInHeat = False
				self.heat = lastStart.heat
				self.startPositions = [r for r in lastStart.inside] + \
						[c for c in lastStart.startPositions if c not in lastStart.inside]
				self.canDrawLots = False
			else:
				self.heat = lastStart.heat + 1
				self.firstStartInHeat = True
				if   self.heat == 2:
					# Find the non-restarted start of the heat.
					s = lastStart
					while s and not s.firstStartInHeat:
						s = s.lastStart
					self.startPositions = [r for r in lastStart.inside] + \
							[c for c in reversed(s.startPositions) if c not in lastStart.inside]
					self.canDrawLots = False
				elif self.heat == 3:
					if lastStart.inside:
						# Don't randomize the start positions again if the last run had a relegation.
						self.startPositions = [r for r in lastStart.inside] + \
								[c for c in lastStart.startPositions if c not in lastStart.inside]
						self.canDrawLots = False
					else:
						# Randomize the start positions again.
						self.startPositions = [c for c in remainingComposition]
						random.shuffle( self.startPositions )
						self.canDrawLots = True
				else:
					assert False, 'Cannot have more than 3 heats'
					
		state = event.competition.state
		self.startPositions = [c for c in self.startPositions if state.inContention(c)]
		if self.event.competition.isMTB:
			self.startPositions.sort( key=lambda c: state.labels[c].bib )

	def isHanging( self ):
		''' Check if there are no results, and this is not a restart.  If so, this start was interrupted and needs to be removed. '''
		if self.restartRequired:
			return False
		if self.places:
			return False
		return True
	
	def setStartPositions( self, startSequence ):
		''' startPositions is of the form [(bib, status), (bib, status), ...] '''
		state = self.event.competition.state
		
		remainingComposition = self.getRemainingComposition()
		bibToId = dict( (state.labels[c].bib, c) for c in remainingComposition )
		
		startIdPosition = { id : i+1000 for i, id in enumerate(self.startPositions) }
		for p, (bib, status) in enumerate(startSequence):
			id = bibToId[int(bib)]
			startIdPosition[id] = p
			if status:
				self.noncontinue[id] = status
			else:
				self.noncontinue.pop(id, None)
		
		self.startPositions = [id for p, id in sorted((p, id) for id, p in startIdPosition.items())]
	
	def setPlaces( self, places ):
		''' places is of the form [(bib, status, warning, relegation), (bib, status, warning, relegation), ...] '''
		state = self.event.competition.state
		
		remainingComposition = self.getRemainingComposition()
		bibToId = { state.labels[c].bib: c for c in remainingComposition }
		
		self.noncontinue = {}
		self.warning = set()
		self.places = {}
		self.finishPositions = []
		
		# Correct for status information.
		finishCode = self.finishCode
		statusPlaceId = []
		place = 0
		for bib, status, warning, relegation in places:
		
			id = bibToId[int(bib)]
			if finishCode.get(status,0) >= 2:
				self.noncontinue[id] = status
			
			if status == 'Inside':
				self.addInside( id ) 
			
			if finishCode.get(status,0) <= 3:
				place += 1
				statusPlaceId.append( (finishCode.get(status,0), place, id) )
				
			if ('{}'.format(warning)[:1] or '0') in '1TtYy':
				self.addWarning( id )
			
			if ('{}'.format(relegation)[:1] or '0') in '1TtYy':
				self.addRelegation( id )
			
		statusPlaceId.sort()
		
		self.places = { id : i+1 for i, (finishCode, place, id) in enumerate(statusPlaceId) if id not in self.noncontinue }
		self.finishPositions = [ id for (finishCode, place, id) in statusPlaceId ]
		self.continuingPositions = [ id for (finishCode, place, id) in statusPlaceId if id not in self.noncontinue ]
		
		self.placesTimestamp = datetime.datetime.now()
	
	def resetPlaces( self ):
		# Fix up data from previous versions.
		if hasattr(self, 'finishPositions'):
			return
		
		# Based on the known places and noncontinue status, set the places again so that the
		# additional data structures get initialized.
		state = self.event.competition.state
		OpenRider = state.OpenRider
		bibStatus = []
		for pos, id in sorted( (pos, id) for pos, id in self.places.items() ):
			try:
				bibStatus.append( (state.labels[id].bib, '') )
			except KeyError:
				pass
		for id, status in self.noncontinue.items():
			bibStatus.append( (state.labels[id].bib, status) )
		
		self.setPlaces( bibStatus )
	
	def setTimes( self, times ):
		''' times is of the form [(pos, t), (pos, t), ...] - missing pos have no time '''
		self.times = dict( times )
	
	def addRelegation( self, id ):
		if isinstance(self.relegated, list):
			self.relegated = set( self.relegated )
		self.relegated.add( id )
		
	def addInside( self, id ):
		self.inside.append( id )
		
	def addWarning( self, id ):
		self.warning.add( id )
		
	def getRemainingComposition( self ):
		state = self.event.competition.state
		return [c for c in self.event.composition if state.inContention(c)]
		
#------------------------------------------------------------------------------------------------

class Event:
	def __init__( self, rule, heatsMax=1 ):
		assert '->' in rule, 'Rule must contain ->'
		
		self.rule = rule.upper()
		rule = rule.replace( '->', ' -> ').replace('-',' ')
		
		fields = rule.split()
		iSep = fields.index( '>' )
		self.composition = fields[:iSep]
		self.winner = fields[iSep+1]	# Winner of competition.
		self.others = fields[iSep+2:]	# Other non-winners.
		
		# If "others" are incomplete, assume classification by TT time.
		self.others.extend( ['TT'] * (len(self.composition)-1 - len(self.others)) )
		
		assert len(self.composition) == len(self.others) + 1, 'Rule outputs cannot exceed inputs.'
			
		self.heatsMax = heatsMax	# Number of heats to decide the outcome.
		self.starts = []
		
		self.finishRiders, self.finishRiderPlace, self.finishRiderRank = [], {}, {}
		self.compositionRiders = []	# Input riders.
		
		# The following are convenience fields and are set by the competition.
		self.competition = None
		self.system = None
	
	@property
	def competitionTime( self ):
		if self.competition.isSprint:
			if self.competition.isKeirin:
				return KeirinCompetitionTime
			else:
				return (1 if self.heatsMax == 1 else 1.5) * SprintFinalCompetitionTime
		return None
	
	@property
	def isSemiFinal( self ):
		try:
			return self.competition.isMTB and self.system == self.competition.systems[-2]
		except IndexError:
			return False
	
	@property
	def isFinal( self ):
		try:
			return self.competition.isMTB and self.system == self.competition.systems[-1]
		except IndexError:
			return False
	
	@property
	def isSmallFinal( self ):
		try:
			return self.competition.isMTB and self.system == self.competition.systems[-1] and self == self.system.events[-2]
		except IndexError:
			return False
		
	@property
	def isBigFinal( self ):
		try:
			return self.competition.isMTB and self.system == self.competition.systems[-1] and self == self.system.events[-1]
		except IndexError:
			return False
		
	@property
	def output( self ):
		return [self.winner] + self.others
		
	def getHeat( self ):
		heats = sum( 1 for s in self.starts if not s.restartRequired )
		return min(heats, self.heatsMax)
	
	def getHeatPlaces( self, heat ):
		state = self.competition.state
		remainingComposition = [c for c in self.composition if state.inContention(c)]
		
		heatCur = 0
		for start in self.starts:
			if start.restartRequired:
				continue
			heatCur += 1
			if heatCur != heat:
				continue
			
			placeStatus = start.noncontinue.copy()
			for c in remainingComposition:
				if c not in placeStatus:
					placeStatus[c] = str(start.places.get(c, ''))
			heatPlaces = [placeStatus.get(c, '') for c in remainingComposition]
			heatPlaces = ['Win' if p == '1' else '-' for p in heatPlaces]
			return heatPlaces
			
		return [''] * len(remainingComposition)
	
	def __repr__( self ):
		state = self.competition.state
		remainingComposition = [c for c in self.composition if state.inContention(c)]
		remainingOthers = self.others[:len(remainingComposition)-1]
		def labName( id ):
			return '{}={:-12s}'.format(id, state.labels[id].full_name) if id in state.labels else '{}'.format(id)
		s = '{}, Heat {}/{}  Start {}:  {} => {} {}'.format(
			self.system.name,
			self.getHeat(), self.heatsMax, len(self.starts),
			' '.join(labName(c) for c in remainingComposition),
			labName(self.winner),
			' '.join(labName(c) for c in remainingOthers) )
		return s
	
	@property
	def multi_line_name( self ):
		return '{}\nHeat {}/{}'.format(self.system.name, self.getHeat(), self.heatsMax)
		
	@property
	def multi_line_bibs( self ):
		state = self.competition.state
		remainingComposition = [c for c in self.composition if state.inContention(c)]
		return '\n'.join((str(state.labels[c].bib)) for c in remainingComposition)
		
	@property
	def multi_line_rider_names( self ):
		state = self.competition.state
		remainingComposition = [c for c in self.composition if state.inContention(c)]
		return '\n'.join(state.labels[c].full_name for c in remainingComposition)
		
	@property
	def multi_line_rider_teams( self ):
		state = self.competition.state
		remainingComposition = [c for c in self.composition if state.inContention(c)]
		return '\n'.join(state.labels[c].team for c in remainingComposition)
		
	@property
	def multi_line_inlabels( self ):
		state = self.competition.state
		remainingComposition = [c for c in self.composition if state.inContention(c)]
		return '\n'.join( remainingComposition )
	
	@property
	def multi_line_outlabels( self ):
		state = self.competition.state
		remainingComposition = [c for c in self.composition if state.inContention(c)]
		outlabels = [self.winner]
		outlabels.extend( self.others[0:len(remainingComposition)-1] )
		return '\n'.join( outlabels )
	
	def getRepr( self ):
		return self.__repr__()
	
	def getStart( self ):
		if not self.canStart():
			return None
		self.starts.append( Start(self, self.starts[-1] if self.starts else None) )
		return self.starts[-1]
	
	def isFinished( self ):
		return self.winner in self.competition.state
	
	def canStart( self ):
		state = self.competition.state
		return  all(c in state.labels for c in self.composition) and \
				any(state.inContention(c) for c in self.composition) and \
				self.winner not in state.labels
	
	def setFinishRiders( self, places ):
		finishCode = Start.finishCode
		state = self.competition.state
		OpenRider = state.OpenRider
		noncontinue = state.noncontinue
		infoSort = []
		for place, id in enumerate(places):
			rider = state.labels.get(id, OpenRider)
			infoSort.append( (finishCode.get(noncontinue.get(id,''),0), place, rider.qualifying_time, rider, noncontinue.get(id,'')) )
		infoSort.sort()
		
		self.finishRiders = [rider for state, place, qualifying_time, rider, nc in infoSort]
		self.finishRiderRank = { rider: p+1 for p, (state, place, qualifying_time, rider, nc) in enumerate(infoSort) }
		self.finishRiderPlace = { rider: nc if nc else p+1 for p, (state, place, qualifying_time, rider, nc) in enumerate(infoSort) }
	
	def getCompositionRiders( self, places ):
		state = self.competition.state
		OpenRider = state.OpenRider
		return [state.labels.get(p,OpenRider) for p in places]
	
	def propagate( self ):
		if not self.canStart():
			#print( ', '.join(self.composition), 'Cannot start or already finished - nothing to propagate' )
			return False
		
		state = self.competition.state
		
		# Update all non-continuing riders into the competition state.
		for s in self.starts:
			s.resetPlaces()
			state.noncontinue.update( s.noncontinue )
		
		self.finishRiders, self.finishRiderPlace = [], {}
		self.compositionRiders = self.getCompositionRiders(self.composition)
		
		# Check for default winner(s).
		availableStarters = [c for c in self.composition if c not in state.noncontinue]
		
		# Single sprint case.
		if len(availableStarters) == 1:
			# Set the default winner.
			state.labels[self.winner] = state.labels[availableStarters[0]]
			self.setFinishRiders(self.composition)
			
			# Mark the "others" as open riders.
			for o in self.others:
				state.labels[o] = state.OpenRider
			return True
			
		# Check if we have a rider with a majority of wins in the heats.
		winCount = defaultdict( int )
		for s in self.starts:
			if s.restartRequired:
				continue
			
			winnerId = s.continuingPositions[0]
			winCount[winnerId] += 1
			if winCount[winnerId] < self.heatsMax - 1:
				continue
			
			# We have a winner of the event.  Propagate the results.
			state.labels[self.winner] = state.labels[winnerId]
			for o, c in zip(self.others, s.continuingPositions[1:]):
				state.labels[o] = state.labels[c]
				
			# Set any extra others to "OpenRider".
			for o in self.others[len(s.continuingPositions)-1:]:
				state.labels[o] = state.OpenRider
			
			# Create the list of finish positions to match the event finish.
			self.setFinishRiders( s.finishPositions if self.heatsMax == 1 else s.continuingPositions )
			return True
				
		return False

#------------------------------------------------------------------------------------------------

class Competition:
	def __init__( self, name, systems ):
		self.name = name
		self.systems = systems
		self.state = State()
		
		# Check that there are no repeated labels in the spec.
		inLabels = set()
		outLabels = set()
		self.starters = 0
		self.isMTB = 'MTB' in name
		self.isSprint = not self.isMTB
		self.isKeirin = self.isSprint and 'Keirin' in name
		
		byeEvents = set()
		byeOutcomeMap = {}
		
		ttCount = 0
		for iSystem, system in enumerate(self.systems):
			rrCount = 0
			for e in system.events:
				e.competition = self
				e.system = system
				
				# Assign unique outcomes for eliminated riders.
				if not self.isMTB:
					# If Track, non-winners in each round are ranked based on qualifying time only.
					for i, other in enumerate(e.others):
						if other == 'TT':
							ttCount += 1
							e.others[i] = '{}TT'.format(ttCount)			
				else:
					# If MTB, the non-winners get credit for the round and finish position.
					for i, other in enumerate(e.others):
						if other == 'TT':
							rrCount += 1
							e.others[i] = '{}RR_{}_{}'.format(rrCount, iSystem+1, i+2)	# Label is nnRR_ro_fo where nn=unique#, ro=round, fo=finishOrder
					
				
				# print( 'Event:', ' - '.join(e.composition), ' -> ', e.winner, e.others )
			
				for c in e.composition:
					assert c not in inLabels, '{}-{} c={}, outLabels={}'.format(e.competition.name, e.system.name, c, ','.join( sorted(outLabels) ))
					inLabels.add( c )
					if c.startswith('N'):
						self.starters += 1			
							
				assert e.winner not in outLabels, '{}-{} winner: {}, outLabels={}'.format(
					e.competition.name, e.system.name, e.winner, ','.join( sorted(outLabels) ))
				outLabels.add( e.winner )
				for c in e.others:
					assert c not in outLabels, '{}-{} other label: {} is already in outLabels={}'.format(
						e.competition.name, e.system.name, c, ','.join( outLabels ))
					outLabels.add( c )
				assert len(outLabels) <= len(inLabels), '{}-{} len(outLabels)={} exceeds len(inLabels)={}\n    {}\n    {}'.format(
						e.competition.name, e.system.name, len(outLabels), len(inLabels), ','.join(inLabels), ','.join(outLabels) )
						
				# Check if this is a bye Event.
				# We handle this by deleting the event and substituting the output value as the input in subsequent events.
				if not e.others:
					byeEvents.add( e )
					byeOutcomeMap[e.winner] = e.composition[0]
			
		assert self.starters != 0, '{}-{} No starters.  Check for missing N values'.format(
					e.competition.name, e.system.name )

		# Process Bye events (substitute outcome into composition of subsequent events, delete bye event).
		# Assign indexes to each component for sorting purposes.
		for j, system in enumerate(self.systems):
			system.i = j
			system.events = [e for e in system.events if e not in byeEvents]
			for k, event in enumerate(system.events):
				event.i = k
				event.composition = [byeOutcomeMap.get(c,c) for c in event.composition]
	
	def getRelegationsWarnings( self, bib, eventCur, before=False ):
		relegations = 0
		warnings = 0
		for system, event in self.allEvents():
			if before and event == eventCur:
				break
			for id in event.composition:
				try:
					if self.state.labels[id].bib == bib:
						for start in event.starts:
							if id in start.relegated:
								relegations += 1
							if id in start.warning:
								warnings += 1
				except KeyError:
					pass
			if event == eventCur:
				break
		return relegations, warnings
		
	def getRelegationsWarningsStr( self, bib, eventCur, before=False ):
		relegations, warnings = self.getRelegationsWarnings(bib, eventCur, before)
		s = []
		if warnings:
			s.append( '{} {}'.format(warnings, 'Warn') )
		if relegations:
			s.append( '{} {}'.format(relegations, 'Rel') )
		return ','.join( s )
	
	def canReassignStarters( self ):
		return self.state.canReassignStarters()
	
	def allEvents( self ):
		for system in self.systems:
			for event in system.events:
				yield system, event
	
	@property
	def competitionTime( self ):
		return None if not self.isSprint else sum( event.competitionTime for system, event in self.allEvents() )
	
	def reset( self ):
		for system, event in self.allEvents():
			for start in event.starts:
				start.resetPlaces()
	
	def __repr__( self ):
		out = ['***** {}'.format(self.name)]
		for s, e in self.allEvents():
			out.append( ' '.join( [s.name, '[{}]'.format(','.join(e.composition)), ' --> ', '[{}]'.format(','.join(e.output))] ) )
		return '\n'.join( out )
	
	def fixHangingStarts( self ):
		for s, e in self.allEvents():
			while e.starts and e.starts[-1].isHanging():
				del e.starts[-1]
	
	def getCanStart( self ):
		return [(s, e) for s, e in self.allEvents() if e.canStart()]
		
	def propagate( self ):
		while True:
			success = False
			for s, e in self.allEvents():
				success |= e.propagate()
			if not success:
				break
		labels = self.state.labels
		return [ labels.get('{}R'.format(r+1), None) for r in range(self.starters) ]

	def getRiderStates( self ):
		riderState = defaultdict( set )
		for id, reason in self.state.noncontinue.items():
			riderState[reason].add( self.state.labels[id] )
		DQs = riderState['DQ']
		DNSs = set( e for e in riderState['DNS'] if e not in DQs )
		DNFs = set( e for e in riderState['DNF'] if e not in DNSs and e not in DQs )
		return DQs, DNSs, DNFs
		
	def getResults( self ):
		DQs, DNSs, DNFs = self.getRiderStates()
		semiFinalRound, smallFinalRound, bigFinalRound = 60, 61, 62
		
		riders = { rider for label, rider in self.state.labels.items() if label.startswith('N') }
		
		Finisher, DNF, DNS, DQ = 1, 2, 3, 4
		riderStatus = { rider: (DQ if rider in DQs else DNS if rider in DNSs else DNF if rider in DNFs else Finisher) for rider in riders }
		statusText = {
			Finisher:	'Finisher',
			DNF:		'DNF',
			DNS:		'DNS',
			DQ:			'DQ',
		}
		
		if not self.isMTB:
			# Rank the rest of the riders based on their results in the competition.
			results = [None] * self.starters
			for i in range(self.starters):
				try:
					results[i] = self.state.labels['{}R'.format(i+1)]
				except KeyError:
					pass

			# Rank the remaining riders based on qualifying time (TT).
			iTT = self.starters
			tts = [rider for label, rider in self.state.labels.items() if label.endswith('TT')]
			tts.sort( key = lambda r: r.qualifying_time, reverse = True )	# Sort these in reverse as we assign them in from most to least.
			for rider in tts:
				iTT -= 1
				results[iTT] = rider
			results = [('Finisher', r) for r in results if not r or not r.isOpen()]
			
			# Purge unfillable spots from the results.
			for r in (DNFs | DNSs | DQs):
				try:
					results.remove( (statusText[Finisher], None) )
				except ValueError:
					break
			
			# Add the unclassifiable riders.
			for classification, s in (('DNF',DNFs), ('DNS',DNSs), ('DQ', DQs)):
				for r in sorted(s,  key = lambda r: r.qualifying_time):
					results.append( (classification, r) )
					
			# Purge empty results, except at the top.
			try:
				i = next( j for j, r in enumerate(results) if r[1] )	# Find first non-empty result.
				if i != 0:
					results[i:] = [r for r in results[i:] if r[1]]
			except StopIteration:
				pass
			
			# Assign classification for all finishers.
			results = [(p+1 if classification == 'Finisher' else classification, rider) for p, (classification, rider) in enumerate(results)]
			
			DNFs = set()
			DNSs = set()
		
		else:
			# Rank the rest of the riders based on their results also considering the result of their last round.
			abnormalFinishers = set()
			compResults = []
			for system in self.systems:
				for event in system.events:
					
					# Get the round of the event.
					round = 1
					if event.isSemiFinal:
						round = semiFinalRound
					elif event.isSmallFinal:
						round = smallFinalRound
					elif event.isBigFinal:
						round = bigFinalRound
					else:
						for id in event.output:
							if 'RR' in id:
								round = int(id.split('_')[-2])
								break
					
					# Rank the finishers.
					rank = 0
					for i, id in enumerate(event.output):
						try:
							rider = event.finishRiders[i]
						except IndexError:
							rider = None
						
						if rider in DQs:
							continue
						
						if id.endswith('R'):
							rank = int(id[:-1])
							isFinish = True
						else:
							try:
								rank = int(id.split('_')[-1])
							except ValueError:
								rank = i + 1
							isFinish = ('RR' in id)
							
						if (isFinish and riderStatus.get(rider,1) == 1) or (round >= 1 and riderStatus.get(rider,1) != 1):
							if riderStatus.get(rider,1) != 1:
								abnormalFinishers.add( rider )
							
							status = riderStatus.get(rider,1)
							statTxt = statusText[Finisher] if status != DQ and round > 1 else statusText[status]
							compResults.append( (
								-round, status, rank,
								rider.qualifying_time if rider else sys.float_info.max,
								rider.seeding_rank if rider else 9999999,
								rider.bib if rider else 999999,
								random.random(),		# Some insurance so that the sort does not fail.
								statusText[status],
								rider
							) )
			
			try:
				compResults.sort()
			except Exception as e:
				print( '****', self.name )
				raise e
				
			results = [rr[-2:] for rr in compResults]
			
			# Adjust the available finisher positions for the abnormal finishes.
			for i in range(len(abnormalFinishers)):
				try:
					results.remove( (statusText[Finisher], None) )
				except ValueError:
					break
				
			# Purge empty results, except at the top.
			try:
				i = next( j for j, r in enumerate(results) if r[1] )	# Find first non-empty result.
				if i != 0:
					results[i:] = [r for r in results[i:] if r[1]]
			except StopIteration:
				pass
			
			# Investigate later - should not have to do this!
			already_seen = set()
			results_non_duplicated = []
			for classification, rider in results:
				if not rider or rider not in already_seen:
					already_seen.add( rider )
					results_non_duplicated.append( (classification, rider) )
			results = results_non_duplicated
			
			# Assign classification for all finishers.
			results = [(p+1 if classification == 'Finisher' or rider in abnormalFinishers else classification, rider) for p, (classification, rider) in enumerate(results)]
				
			DNFs = set()
			DNSs = set()
		
		return (
			results,
			sorted(DNFs, key = lambda r: (r.qualifying_time, -r.uci_points, r.iSeeding)),
			sorted(DQs,  key = lambda r: (r.qualifying_time, -r.uci_points, r.iSeeding))
		)

class System:
	def __init__( self, name, events ):
		self.name = name
		self.events = events
	
	@property
	def competitionTime( self ):
		try:
			return sum( event.competitionTime for event in self.events )	
		except TypeError:
			return None

class Model:
	communique_start = 100
	modifier = 0

	def __init__( self ):
		self.competition_name = 'My Competition'
		self.date = datetime.date.today()
		self.category = 'My Category'
		self.track = 'My Track'
		self.organizer = 'My Organizer'
		self.chief_official = 'My Chief Official'
		self.competition = None
		self.riders = []
		self.changed = False
		self.showResults = 0
		self.communique_number = {}
	
	@property
	def competitionTime( self ):
		try:
			return self.competition.competitionTime + self.qualifyingCompetitionTime
		except TypeError:
			return None
			
	@property
	def qualifyingCompetitionTime( self ):
		return None if self.competition.isMTB else len(self.riders) * Sprint200mQualificationCompetitionTime
	
	@property
	def isKeirin( self ):
		return self.competition and self.competition.isKeirin
	
	def getProperties( self ):
		return { a : getattr(self, a) for a in ['competition_name', 'date', 'category', 'track', 'organizer', 'chief_official'] }

	def setProperties( self, properties ):
		for a, v in properties.items():
			setattr(self, a, v)
		
	def updateSeeding( self ):
		for iSeeding, rider in enumerate(self.riders, 1):
			rider.iSeeding = iSeeding
			
	def getDNQs( self ):
		riders = sorted( self.riders, key = lambda r: r.keyQualifying() )
		return riders[self.competition.starters:]
	
	def setQualifyingInfo( self ):
		self.updateSeeding()
		self.competition.state.setQualifyingInfo( self.riders, self.competition )
		
	def canReassignStarters( self ):
		return self.competition.state.canReassignStarters()
		
	def setChanged( self, changed=True ):
		self.changed = changed
		
	def setCompetition( self, competitionNew, modifier=0 ):
		if self.competition.name == competitionNew.name and self.modifier == modifier:
			return
		
		stateSave = self.competition.state
		self.competition = copy.deepcopy( competitionNew )
		self.competition.state = stateSave
		self.modifier = modifier
		if modifier:
			for system, event in self.competition.allEvents():
				if modifier == 3:
					event.heatsMax = 1
				elif modifier == 2:
					if '1/4' in system.name or '1/2' in system.name:
						event.heatsMax = 1
				elif modifier == 1:
					if '1/4' in system.name:
						event.heatsMax = 1

model = Model()

