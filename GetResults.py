import Model
from bisect import bisect_left
from math import floor
import re
import sys
import copy
import Utils
import itertools
import operator
from datetime import timedelta, datetime
from collections import deque, defaultdict

from ReadSignOnSheet import IgnoreFields, NumericFields, SyncExcelLink
from SetNoDataDNS import SetNoDataDNS
statusSortSeq = Model.Rider.statusSortSeq

def TimeDifference( a, b, highPrecision = False ):
	if highPrecision:
		a *= 100.0
		b *= 100.0
	t = int(a) - int(b)
	if highPrecision:
		t /= 100.0
	return t

def RidersCanSwap( riderResults, num, numAdjacent ):
	try:
		rr1 = riderResults[num]
		rr2 = riderResults[numAdjacent]
		if (rr1.status != Model.Rider.Finisher or
			rr2.status != Model.Rider.Finisher or
			rr1.laps != rr2.laps ):
			return False
		laps = rr1.laps
		if rr1.interp[laps] or rr2.interp[laps]:
			return False
		rt1, rt2 = rr1.raceTimes[:], rr2.raceTimes[:]
		rt1[laps], rt2[laps] = rt2[laps], rt1[laps]
		if 	all( x < y for x, y in zip(rt1, rt1[1:]) ) and \
			all( x < y for x, y in zip(rt2, rt2[1:]) ):
			return True
	except (IndexError, ValueError, KeyError):
		pass
	return False

def toInt( n ):
	try:
		return int(n.split()[0])
	except Exception:
		return 99999
	
class RiderResult:
	# By default, all the fields in this structure are used as attributes.
	# Except fields that start with '_', or fields that are in "ignoreAttr", which is used by a number of functions to extract attributes.
	# Make sure that all local functions start with '_' to avoid them being picked up as attributes.
	
	def __init__( self, num, status, lastTime, raceCat, lapTimes, raceTimes, interp ):
		self.num		= num
		self.status		= status
		self.gap		= ''
		self.pos		= ''
		self.speed		= ''
		self.laps		= len(lapTimes)
		self.lastTime	= lastTime
		self.lastTimeOrig = lastTime
		self._lastTimeOrig = lastTime		# Keep an internal copy of the original last time for checking close finishes.
		self.raceCat	= raceCat
		self.lapTimes	= lapTimes
		self.raceTimes	= raceTimes
		self.interp		= interp
		self.lastInterp = False
		
	def _getExpectedLapChar( self, t ):
		if self.status == Model.Rider.Finisher:
			try:
				if self.raceTimes[-2] <= t:
					return '🏁 '
				if self.raceTimes[-3] <= t:
					return '🔔 '
			except Exception:
				pass
		return ''
		
	def _getRecordedLapChar( self, t ):
		if self.status == Model.Rider.Finisher:
			try:
				if self.raceTimes[-1] <= t:
					return '🏁 '
				if self.raceTimes[-2] <= t:
					return '🔔 '
			except Exception:
				pass
		return ''
		
	_reMissingName = re.compile( '^, |, $' )
	def full_name( self ):
		return self._reMissingName.sub( '', '{}, {}'.format(getattr(self, 'LastName', ''), getattr(self,'FirstName', '')), 1 )
		
	_reMissingShortName = re.compile( '^, |, $' )
	def short_name( self, maxLen=20 ):
		lastName = getattr(self, 'LastName', '')
		if len(lastName) + 3 >= maxLen:
			return lastName
		firstName = getattr(self,'FirstName', '')
		if not lastName:
			return firstName
		if len(lastName) + len(firstName) + 3 <= maxLen:
			return self._reMissingShortName.sub( '', '{}, {}'.format(lastName, firstName), 1 )
		return self._reMissingShortName.sub( '', '{}, {}.'.format(lastName, firstName[:1]), 1 )
		
	def __repr__( self ):
		return str(self.__dict__)
		
	def _getKey( self ):
		return (statusSortSeq[self.status], -self.laps, self.lastTime, getattr(self, 'startTime', 0.0) or 0.0, self.num)
		
	def _getRunningKey( self ):
		self.lastInterp = (self.laps and self.interp[self.laps] and self.status == Model.Rider.Finisher)
		return (
			statusSortSeq[self.status], -self.laps,
			statusSortSeq[Model.Rider.DNF if self.lastInterp else self.status],
			self.lastTime, getattr(self, 'startTime', 0.0) or 0.0,
			self.num
		)
	
	def _getWinAndOutKey( self ):
		k = self._getKey()
		laps = -k[1]
		if laps == 0:
			laps = 999999
		return (k[0], laps,) + k[2:]		# Sort by increasing lap count.
		
	def _getComponentKey( self ):
		return (statusSortSeq[self.status], toInt(self.pos), self.lastTime, getattr(self, 'startTime', 0.0) or 0.0, self.num)
	
	def _getWinAndOutComponentKey( self ):
		return (statusSortSeq[self.status], self.laps if self.laps else 999999, toInt(self.pos), self.lastTime, getattr(self, 'startTime', 0.0) or 0.0, self.num)
		
	def _setLapsDown( self, lapsDown ):
		self.gap = '-{} {}'.format(lapsDown, _('lap') if lapsDown == 1 else _('laps'))
		self.gapValue = -lapsDown

def assignFinishPositions( riderResults ):
	Finisher = Model.Rider.Finisher
	statusNames = Model.Rider.statusNames
	for pos, rr in enumerate(riderResults):
		if rr.status != Finisher:
			rr.pos = statusNames[rr.status]
		else:
			rr.pos = '{}'.format(pos+1)

DefaultSpeed = 0.00001

def FixRelegations( riderResults ):
	race = Model.race
	riders = race.riders
	
	relegated = []
	nonRelegated = deque()
	nonFinishers = []
	
	Finisher = Model.Rider.Finisher
	for i, rr in enumerate(riderResults):
		if rr.status == Finisher:
			rider = riders[rr.num]
			if rider.relegatedPosition:
				relegated.append( (rider.relegatedPosition, i, rr) )
			else:
				nonRelegated.append( rr )
		else:
			nonFinishers = riderResults[i:]
			break

	relegated.sort()
	relegated = deque( relegated )

	riderResultsNew = []
	while nonRelegated or relegated:
		if nonRelegated and (not relegated or relegated[0][0] > len(riderResultsNew)+1):
			riderResultsNew.append( nonRelegated.popleft() )
		else:
			riderResultsNew.append( relegated.popleft()[-1] )
	riderResultsNew.extend( nonFinishers )
		
	riderResults[:] = riderResultsNew

def getPulledCmpTuple( rr, rider, winnerLaps, decreasingLapsToGo=True ):
	f = 1 if decreasingLapsToGo else -1
	if rider.pulledLapsToGo:
		lapsToGo = rider.pulledLapsToGo
	else:
		try:
			lapsToGo = winnerLaps - (len(rr.lapTimes) + int(rider.tStatus - rr.raceLaps[-1] > 20.0))
		except Exception:
			lapsToGo = winnerLaps
	return (lapsToGo*f, (rider.pulledSequence if rider.pulledSequence is not None else 9999999), rr.raceTimes[-1] if rr.raceTimes else 24.0*60*60*300, rr.num, rr)
	
def FixPulled( riderResults, race, category ):
	if not race.useTableToPullRiders or (race.isTimeTrial or race.winAndOut):
		return
	
	catPull = defaultdict( list )
	catWinnerLaps = {}
	setPull = set()
	Finisher, Pulled = Model.Rider.Finisher, Model.Rider.Pulled
	hasPulledSequence = 0
	for rr in riderResults:
		category = race.getCategory(rr.num)
		if not category:
			continue
		if category not in catWinnerLaps:
			catWinnerLaps[category] = race.getNumLapsFromCategory(category)
		rider = race.riders[rr.num]
		if rider.status == Pulled:
			catPull[category].append( rr )
			setPull.add( rr.num )
			hasPulledSequence += int(rider.pulledSequence is not None)
	
	if not catPull or not hasPulledSequence:
		return
	
	pullSort = []
	for cat, winnerLaps in catWinnerLaps.items():
		if not winnerLaps:
			continue
		for rr in catPull[cat]:
			rider = race.riders[rr.num]
			pullSort.append( getPulledCmpTuple(rr, rider, winnerLaps) )
			
			pulledLapsToGo = abs(pullSort[-1][0])
			rr._setLapsDown( pulledLapsToGo )
			
			lapsCompleted = max( 0, winnerLaps - pulledLapsToGo )
			del rr.raceTimes[((lapsCompleted+1) if lapsCompleted else 0):]
			del rr.lapTimes[lapsCompleted:]
			rr.lastTime = rr.lastTimeOrig = rr._lastTimeOrig = rr.raceTimes[-1] if rr.raceTimes else 0.0

	pullSort.sort()
	
	riderResultsNew, nonFinishers = [], []
	for rr in riderResults:
		if rr.num not in setPull:
			if rr.status == Finisher:
				riderResultsNew.append( rr )
			else:
				nonFinishers.append( rr )
	
	riderResultsNew.extend( v[-1] for v in pullSort )
	riderResultsNew.extend( nonFinishers)
	
	riderResults[:] = riderResultsNew

def _GetResultsCore( category ):
	Finisher = Model.Rider.Finisher
	PUL = Model.Rider.Pulled
	NP = Model.Rider.NP
	rankStatus = { Finisher, PUL }
	
	riderResults = []
	race = Model.race
	if not race:
		return tuple()
	
	isRunning = race.isRunning()
	isTimeTrial = race.isTimeTrial
	
	SetNoDataDNS()
	
	roadRaceFinishTimes = race.roadRaceFinishTimes
	estimateLapsDownFinishTime = race.estimateLapsDownFinishTime
	allCategoriesFinishAfterFastestRidersLastLap = race.allCategoriesFinishAfterFastestRidersLastLap
	winAndOut = race.winAndOut
	riders = race.riders
	raceStartSeconds = (
		race.startTime.hour*60.0*60.0 + race.startTime.minute*60.0 + race.startTime.second + race.startTime.microsecond / 1000000.0 if race.startTime
		else Utils.StrToSeconds(race.scheduledStart) * 60.0
	)
	
	entries = race.interpolate()
	
	# Group finish times are defined as times which are separated from the previous time by at least 1 second.
	groupFinishTimes = [0 if not entries else floor(entries[0].t)]
	if roadRaceFinishTimes and not isTimeTrial:
		groupFinishTimes.extend( [floor(entries[i].t) for i in range(1, len(entries)) if entries[i].t - entries[i-1].t >= 1.0] )
		groupFinishTimes.extend( [sys.float_info.max] * 5 )
	
	allRiderTimes = defaultdict( list )
	for e in entries:
		allRiderTimes[e.num].append( e )
	
	startOffset = category.getStartOffsetSecs() if category else 0.0
	raceSeconds = race.minutes * 60.0
	
	# Enforce All Categories Finish After Fastest Rider's Last Lap
	fastestRidersLastLapTime = None
	if allCategoriesFinishAfterFastestRidersLastLap and not isTimeTrial:
		resultBest = (0, sys.float_info.max)
		for c, (times, nums) in race.getCategoryTimesNums().items():
			if not times:
				continue
			try:
				winningLaps = bisect_left( times, raceSeconds, hi=len(times)-1 )
				if winningLaps >= 2:
					lastLapTime = times[winningLaps] - times[winningLaps-1]
					if (times[winningLaps] - raceSeconds) > lastLapTime / 2.0:
						winningLaps -= 1
				resultBest = min( resultBest, (-winningLaps, times[winningLaps] - 0.01) )
			except IndexError:
				pass
		fastestRidersLastLapTime = resultBest[1] if resultBest[0] != 0 else None
				
	# Get the number of race laps for each category.
	categoryWinningTime, categoryWinningLaps = {}, {}
	for c, (times, nums) in race.getCategoryTimesNums().items():
		if category and c != category:
			continue
		
		# If the category num laps is specified, use that.
		if race.getNumLapsFromCategory(c):
			categoryWinningLaps[c] = race.getNumLapsFromCategory(c)
			categoryWinningTime[c] = times[min(len(times)-1, categoryWinningLaps[c])]
		else:
			# Otherwise, set the number of laps by the winner's time closest to the race finish time.
			try:
				if fastestRidersLastLapTime is not None:
					winningLaps = bisect_left( times, fastestRidersLastLapTime, hi=len(times)-1 )
					categoryWinningTime[c] = fastestRidersLastLapTime
					categoryWinningLaps[c] = winningLaps
				else:
					winningLaps = bisect_left( times, raceSeconds, hi=len(times)-1 )
					if winningLaps >= 2:
						winner = riders[nums[winningLaps]]
						entries = winner.interpolate()
						if entries[winningLaps].interp:
							lastLapTime = times[winningLaps] - times[winningLaps-1]
							if (times[winningLaps] - raceSeconds) > lastLapTime / 2.0:
								winningLaps -= 1
					categoryWinningTime[c] = times[winningLaps]
					categoryWinningLaps[c] = winningLaps
			except IndexError:
				categoryWinningTime[c] = raceSeconds
				categoryWinningLaps[c] = None
	
	highPrecision = Model.highPrecisionTimes()
	getCategory = race.getCategory
	for rider in list(race.riders.values()):
		riderCategory = getCategory( rider.num )
		
		if category and riderCategory != category:
			continue
		if not riderCategory:
			continue
		
		cutoffTime = categoryWinningTime.get(riderCategory, raceSeconds)
		
		riderTimes = allRiderTimes[rider.num]
		times = [e.t for e in riderTimes]
		interp = [e.interp for e in riderTimes]
		
		if len(times) >= 2:
			times[0] = min(riderCategory.getStartOffsetSecs() if riderCategory else 0, times[1])
			if isTimeTrial or riderCategory and categoryWinningLaps.get(riderCategory, None) and riderCategory.lappedRidersMustContinue:
				laps = min( categoryWinningLaps[riderCategory], len(times)-1 )
			else:
				laps = bisect_left( times, cutoffTime, hi=len(times)-1 )
			
			del times[laps+1:]
			del interp[laps+1:]
		else:
			laps = 0
			times.clear()
			interp.clear()

		# Apply the early bell time.  Early bell time signifies the beginning of the last lap for all riders.
		if riderCategory.earlyBellTime and not race.isTimeTrial and times:
			try:
				# While a not-last lap starts after earlyBellTime, delete the last lap.
				while times[-3] >= riderCategory.earlyBellTime:	# This is confusing.  Don't change it!
					times.pop()
					interp.pop()
					laps -= 1
			except IndexError:
				pass
		
		# Get the last time on record for the rider.
		lastTime = rider.tStatus
		if not lastTime:
			lastTime = times[-1] if times else 0.0
		
		status = Finisher if rider.status in rankStatus else rider.status
		if isTimeTrial and not lastTime and rider.status == Finisher:
			status = NP
		rr = RiderResult(	rider.num, status, lastTime,
							riderCategory.fullname,
							[times[i] - times[i-1] for i in range(1, len(times))],
							times,
							interp )
		
		if isTimeTrial:
			rr.startTime = rider.firstTime
			rr.clockStartTime = rr.startTime + raceStartSeconds if rr.startTime is not None else None
			if rr.status == Finisher:
				try:
					if rr.lastTime > 0:
						rr.finishTime = rr.startTime + rr.lastTime
				except (TypeError, AttributeError):
					pass
					
			try:
				rr.lastTime += getattr(rider, 'ttPenalty', 0.0)
			except (TypeError, AttributeError):
				pass
		
		# Compute the speeds for the rider.
		if riderCategory.distance:
			distance = riderCategory.distance
			if riderCategory.distanceIsByLap:
				riderDistance = riderCategory.getDistanceAtLap(len(rr.lapTimes))
				rr.lapSpeeds = [DefaultSpeed if t <= 0.0 else (riderCategory.getLapDistance(i+1) / (t / (60.0*60.0))) for i, t in enumerate(rr.lapTimes)]
				# Ensure that the race speeds are always consistent with the lap times.
				raceSpeeds = []
				if rr.lapSpeeds:
					tCur = 0.0
					for i, t in enumerate(rr.lapTimes):
						tCur += t
						raceSpeeds.append( DefaultSpeed if tCur <= 0.0 else (riderCategory.getDistanceAtLap(i+1) / (tCur / (60.0*60.0))) )
					rr.speed = '{:.2f} {}'.format(raceSpeeds[-1], ['km/h', 'mph'][race.distanceUnit] )
				rr.raceSpeeds = raceSpeeds
			else:	# Distance is by entire race.
				if rider.status == Finisher and rr.raceTimes:
					riderDistance = distance
					try:
						tCur = rr.raceTimes[-1] - rr.raceTimes[0]
						speed = DefaultSpeed if tCur <= 0.0 else riderDistance / (tCur / (60.0*60.0))
					except IndexError as e:
						speed = DefaultSpeed
					rr.speed = '{:.2f} {}'.format(speed, ['km/h', 'mph'][race.distanceUnit] )
					
		riderResults.append( rr )
	
	if not riderResults:
		return tuple()
	
	if isRunning:
		# Sequence the riders based on the last lap time, not the projected winner of the race.
		t = race.curRaceTime()
		statusLapsTimeBest = (999, 0, 24*60*60*200)
		rrLeader = None
		for rr in riderResults:
			if not rr.raceTimes or not rr.status == Finisher:
				continue
			iT = bisect_left( rr.raceTimes, t )
			try:
				if rr.raceTimes[iT] != t:
					iT -= 1
			except IndexError:
				iT -= 1
			
			if iT > 0:
				statusLapsTime = (statusSortSeq[rr.status], -iT, rr.raceTimes[iT])
				if statusLapsTime < statusLapsTimeBest:
					statusLapsTimeBest = statusLapsTime
					rrLeader = rr
		
		if rrLeader:
			tBest = statusLapsTimeBest[2]
			for rr in riderResults:
				if not rr.raceTimes or not rr.status == Finisher:
					continue
				iT = bisect_left( rr.raceTimes, tBest )
				if 0 < iT < len(rr.raceTimes):
					rr.laps = iT
					rr.lastTime = rr.raceTimes[iT]
					rr.lastTimeOrig = rr.lastTime
	
	riderResults.sort( key=RiderResult._getRunningKey if isRunning else RiderResult._getKey )
	
	relegatedNums = { rr.num for rr in riderResults if race.riders[rr.num].isRelegated() }
	if relegatedNums:
		FixRelegations( riderResults )
	
	# Add the position (or status, if not a Finisher).
	# Fill in the gap field (include laps down if appropriate).
	leader = riderResults[0]
	leaderRaceTimes = len( leader.raceTimes )
	leaderLapTimes = len( leader.lapTimes )
	for pos, rr in enumerate(riderResults):
	
		if len(rr.raceTimes) > leaderRaceTimes:
			rr.raceTimes = rr.raceTimes[:leaderRaceTimes]
		if len(rr.lapTimes) > leaderLapTimes:
			rr.lapTimes = rr.lapTimes[:leaderLapTimes]
			rr.laps = leader.laps
	
		if rr.status != Finisher:
			rr.pos = Model.Rider.statusNames[rr.status]
			continue
			
		rr.pos = '{}{}'.format(pos+1, ' '+_('REL') if rr.num in relegatedNums else '')
		
		# if gapValue is negative, it is laps down.  Otherwise, it is seconds.
		rr.gapValue = 0
		if rr.laps < leader.laps:
			rr._setLapsDown( leader.laps - rr.laps )
		elif (winAndOut or rr != leader) and not (isTimeTrial and rr.lastTime == leader.lastTime):
			rr.gap = (
				Utils.formatTimeGap( TimeDifference(rr.lastTime, leader.lastTime, highPrecision), highPrecision )
					if leader.lastTime < rr.lastTime else ''
			)
			rr.gapValue = max(0.0, rr.lastTime - leader.lastTime)

	FixPulled( riderResults, race, category )
	
	# Compute road race times and gaps.
	if roadRaceFinishTimes and not isTimeTrial:
		iTime = 0
		lastFullLapsTime = 60.0
		for pos, rr in enumerate(riderResults):
			rr.projectedTime = rr.lastTime
			if rr.status != Finisher or not rr.raceTimes:
				rr.roadRaceLastTime = floor(rr.lastTime)
				rr.roadRaceGap = rr.gap.split('.')[0]
				rr.roadRaceGapValue = 0
			elif rr.laps == leader.laps:
				if not (groupFinishTimes[iTime] <= rr.lastTime < groupFinishTimes[iTime+1]):
					iTime += 1
					if not (groupFinishTimes[iTime] <= rr.lastTime < groupFinishTimes[iTime+1]):
						iTime = bisect_left( groupFinishTimes, rr.lastTime, 0, len(groupFinishTimes) - 1 )
						if groupFinishTimes[iTime] > rr.lastTime:
							iTime -= 1
				rr.roadRaceLastTime = groupFinishTimes[iTime]
				rr.roadRaceGapValue = rr.roadRaceLastTime - leader.roadRaceLastTime
				rr.roadRaceGap = Utils.formatTimeGap( rr.roadRaceGapValue, False )
				lastFullLapsTime = rr.roadRaceLastTime + 60.0
			else:
				if estimateLapsDownFinishTime:
					# Compute a projected finish time.  Use the median lap time.  Disregard the first lap.
					lapTimes = sorted( rr.lapTimes[1:] if len(rr.lapTimes) > 1 else rr.lapTimes )
					if lapTimes:
						lapTimesLen = len(lapTimes)
						medianLapTime = lapTimes[lapTimesLen//2] if lapTimesLen&1 else (lapTimes[lapTimesLen//2-1] + lapTimes[lapTimesLen//2]) / 2.0
						rr.projectedTime = rr.raceTimes[-1] + (leader.laps - rr.laps) * medianLapTime
						rr.roadRaceLastTime = max( lastFullLapsTime, floor(rr.projectedTime) )
					else:
						rr.roadRaceLastTime = rr.projectedTime = 5 * 24.0 * 60.0 * 60.0
					rr.roadRaceGapValue = rr.roadRaceLastTime - leader.roadRaceLastTime
					rr.roadRaceGap = Utils.formatTimeGap( rr.roadRaceGapValue, False ) if rr != leader else ''
				else:
					rr.roadRaceLastTime = floor(rr.lastTime)
					rr.roadRaceGap = rr.gap.split('.')[0]
					rr.roadRaceGapValue = rr.gapValue				
	
	if isTimeTrial:
		for rr in riderResults:
			rider = riders[rr.num]
			if rider.status == Finisher and hasattr(rider, 'ttPenalty'):
				rr.ttPenalty = getattr(rider, 'ttPenalty')
				rr.ttNote = getattr(rider, 'ttNote', '')
	elif winAndOut:
		riderResults.sort( key=RiderResult._getWinAndOutKey )
		assignFinishPositions( riderResults )
		
	if roadRaceFinishTimes and estimateLapsDownFinishTime and not isTimeTrial:
		for rr in riderResults:
			rr.lastTime = rr.lastTimeOrig = rr.roadRaceLastTime
			rr.gap = rr.roadRaceGap
			rr.gapValue = rr.roadRaceGapValue
			del rr.roadRaceLastTime
			del rr.roadRaceGap
			del rr.roadRaceGapValue
	
	return tuple(riderResults)
	
def GetNonWaveCategoryResults( category ):
	race = Model.race
	if not race:
		return tuple()
	
	isTimeTrial = race.isTimeTrial
	winAndOut = race.winAndOut
	highPrecision = Model.highPrecisionTimes()
	
	rrCache = {}
	riderResults = []

	getCategory = race.getCategory
	for num in race.getRiderNums():
		if not race.inCategory(num, category):
			continue
		
		try:
			rrFound = rrCache[num]
		except KeyError:
			rrCache.update( { rr.num: rr for rr in GetResults(getCategory(num)) } )
			rrFound = rrCache.get( num, None )
				
		if not rrFound:
			continue
		
		riderResults.append( copy.deepcopy(rrFound) )
		
		# Remove the start offset from the race times and finish times.
		rr = riderResults[-1]
		try:
			startOffset = rr.raceTimes[0]
		except Exception:
			startOffset = 0.0
			
		try:
			rr.lastTime = max( 0.0, rr.lastTime - startOffset )
		except Exception:
			pass
			
		rr.raceTimes = [t - startOffset for t in rr.raceTimes]
	
	# Sort the new results.
	if winAndOut:	# Make sure we forward-sort the results.  This is required as we assign gaps/pos below and we do not want to use the winAndOut position.
		riderResults.sort( key = RiderResult._getKey )
	else:
		riderResults.sort( key = RiderResult._getComponentKey if category.catType == Model.Category.CatComponent else RiderResult._getKey )
	
	# Assign finish position, gaps and status.
	statusNames = Model.Rider.statusNames
	leader = riderResults[0] if riderResults else None
	
	Finisher = Model.Rider.Finisher
	if leader:
		leader.gap = ''
		leader.gapValue = 0
		for pos, rr in enumerate(riderResults):
			rr.gap = ''
			rr.gapValue = 0
			if rr.status == Finisher:
				rr.pos = '{}'.format( pos + 1 ) if not getattr(rr, 'relegated', False) else '{} {}'.format(pos + 1, _('REL'))
				if rr.laps != leader.laps:
					lapsDown = leader.laps - rr.laps
					rr.gap = '-{} {}'.format(lapsDown, _('laps') if lapsDown > 1 else _('lap'))
					rr.gapValue = -lapsDown
				elif (rr != leader or winAndOut) and not (isTimeTrial and rr.lastTime == leader.lastTime):
					rr.gap = Utils.formatTimeGap( TimeDifference(rr.lastTime, leader.lastTime, highPrecision), highPrecision )
					rr.gapValue = rr.lastTime - leader.lastTime
			else:
				rr.pos = statusNames[rr.status]
	
	if winAndOut:
		riderResults.sort( key =
			RiderResult._getWinAndOutComponentKey if category.catType == Model.Category.CatComponent else RiderResult._getWinAndOutKey
		)
		assignFinishPositions( riderResults )
	
	return tuple(riderResults)

@Model.memoize
def GetResultsWithData( category ):
	CatWave =  Model.Category.CatWave
	if category and category.catType != CatWave:
		return GetNonWaveCategoryResults( category )

	# If there is only one category in the race, use that category instead of None.
	# This eliminates computing results twice.
	race = Model.race
	if category is None:
		singleCategory = None
		for c in race.categories.values():
			if c.active and c.catType == CatWave:
				if not singleCategory:
					singleCategory = c
				else:
					singleCategory = None
					break
		if singleCategory:
			return GetResults( singleCategory )

	riderResults = _GetResultsCore( category )
	
	# Add the linked external data.
	try:
		excelLink = race.excelLink
		externalInfo = excelLink.read()
		ignoreFields = set(IgnoreFields)
		externalFields = [f for f in excelLink.getFields() if f not in ignoreFields]
	except Exception:
		excelLink = None
		externalFields = []
		externalInfo = {}
			
	if not excelLink or not riderResults:
		return riderResults
	
	for rr in riderResults:
		for f in externalFields:
			try:
				v = externalInfo[rr.num][f]
				if f in NumericFields:
					v = float(v)
					if float(v) == int(v):
						v = int(v)
				else:
					v = '{}'.format(v)
				setattr( rr, f, v )
			except (KeyError, ValueError):
				setattr( rr, f, '' )
	
	if excelLink and excelLink.hasField('Factor'):
		riderResults = [copy.copy(rr) for rr in riderResults]
		for rr in riderResults:
			try:
				factor = float(externalInfo[rr.num]['Factor'])
			except Exception as e:
				factor = 1.0
		
			if factor > 1.0:
				factor /= 100.0
			elif factor <= 0.0:
				factor = 1.0
			rr.factor = factor * 100.0
			
			try:
				startOffset = rr.raceTimes[0]
			except Exception:
				startOffset = 0.0
				
			try:
				ttPenalty = rr.ttPenalty
			except Exception:
				ttPenalty = 0.0
			
			# Adjust the true ride time by the factor (subtract the start offset and any penalties, add them back later).
			rr.lastTime = startOffset + ttPenalty + max(0.0, rr.lastTimeOrig - startOffset - ttPenalty) * factor
			
		riderResults.sort( key = RiderResult._getWinAndOutKey if race.winAndOut else RiderResult._getKey )
		assignFinishPositions( riderResults )
		FixRelegations( riderResults )
		riderResults = tuple( riderResults )
	
	return riderResults

def GetResults( category ):
	# If the spreadsheet changed, clear the cache to update the results with new data.
	try:
		excelLink = Model.race.excelLink
		externalInfo = excelLink.read()
		if excelLink.readFromFile:
			Model.resetCache()
	except Exception as e:
		pass
		
	return GetResultsWithData( category )

@Model.memoize
def GetEntries( category ):
	results = GetResultsWithData( category )
	Entry = Model.Entry
	return sorted(
		itertools.chain.from_iterable(
			((Entry(r.num, lap, t, r.interp[lap]) for lap, t in enumerate(r.raceTimes))
				for r in results )
		),
		key=Entry.key
	)

def GetEntriesForNum( category, num ):
	results = GetResultsWithData( category )
	Entry = Model.Entry
	for r in results:
		if r.num == num:
			return [Entry(r.num, lap, t, r.interp[lap]) for lap, t in enumerate(r.raceTimes)]
	return []
	
@Model.memoize
def GetLastRider( category ):
	race = Model.race
	if not race or race.isUnstarted() or race.isTimeTrial:
		return None
	
	categories = [category] if category else race.getCategories( startWaveOnly=True )
	finisher = Model.Rider.Finisher
	rrLast = None
	for c in categories:
		for rr in GetResultsWithData( c ):
			if rr.status == finisher and rr._lastTimeOrig:
				if rrLast is None or rrLast._lastTimeOrig <= rr._lastTimeOrig:
					rrLast = rr
	return rrLast

@Model.memoize
def GetLastFinisherTime():
	results = GetResultsWithData( None )
	finisher = Model.Rider.Finisher
	try:
		return max( r.lastTime for r in results if r.status == finisher )
	except Exception:
		return 0.0
	
def GetLeaderFinishTime():
	results = GetResultsWithData( None )
	if results and results[0].status == Model.Rider.Finisher:
		return results[0].lastTime
	else:
		return 0.0

def GetETA( category ):
	race = Model.race
	if not race or not race.isRunning():
		return None
	results = GetResultsWithData( category )
	if not results:
		return None
	rr = results[0]
	if rr.status != Model.Rider.Finisher or not rr.raceTimes:
		return None
	offsetSecs = category.getStartOffsetSecs() if category else 0.0
	tSearch = race.curRaceTime() - offsetSecs
	if tSearch > rr.raceTimes[-1]:
		return None
		
	lap = bisect_left( rr.raceTimes, tSearch )
	try:
		return race.startTime + timedelta(seconds=rr.raceTimes[lap] + offsetSecs)
	except IndexError:
		return None

def GetLeaderTime( category ):
	race = Model.race
	if not race or not race.isRunning():
		return None
	results = GetResultsWithData( category )
	if not results:
		return None
	rr = results[0]
	if rr.status != Model.Rider.Finisher or not rr.raceTimes:
		return None
	offsetSecs = category.getStartOffsetSecs() if category else 0.0
	tSearch = race.curRaceTime() - offsetSecs
	if tSearch > rr.raceTimes[-1]:
		return None
		
	lap = bisect_left( rr.raceTimes, tSearch )
	try:
		return offsetSecs + rr.raceTimes[lap-1]
	except IndexError:
		return None

def UnstartedRaceDataProlog( getExternalData = True ):
	tempNums = set()
	externalInfo = None
	
	with Model.LockRace() as race:
		if race and getExternalData and race.isUnstarted():
			try:
				externalInfo = race.excelLink.read()
			except Exception:
				externalInfo = {}
		
		# Add all numbers from the spreadsheet if they are not already in the race.
		# Default the status to NP.
		if externalInfo:
			for num, info in externalInfo.items():
				if num not in race.riders and any(info.get(f, None) for f in ['LastName', 'FirstName', 'Team', 'License']):
					rider = race.getRider( num )
					rider.status = Model.Rider.NP
					tempNums.add( num )
			race.resetAllCaches()
	
	return tempNums
	
def UnstartedRaceDataEpilog( tempNums ):
	# Remove all temporary numbers.
	race = Model.race
	if race and tempNums:
		for num in tempNums:
			race.deleteRider( num )
		race.resetAllCaches()

class UnstartedRaceWrapper:
	count = 0	# Ensure that we can nest calls without problems.
	
	def __init__(self,  getExternalData = True):
		self.getExternalData = getExternalData
		self.tempNums = set()
		
	def __enter__( self ):
		UnstartedRaceWrapper.count += 1
		if UnstartedRaceWrapper.count == 1:
			self.tempNums = UnstartedRaceDataProlog( self.getExternalData )
	
	def __exit__(self, type, value, traceback):
		if UnstartedRaceWrapper.count == 1:
			UnstartedRaceDataEpilog( self.tempNums )
		UnstartedRaceWrapper.count -= 1

@Model.memoize
def GetLapDetails():
	details = {}
	
	race = Model.race
	if not race:
		return details

	numTimeInfo = race.numTimeInfo
	lapNote = getattr(race, 'lapNote', {})
	for rr in GetResultsWithData( None ):
		for lap, t in enumerate(rr.raceTimes):
			i1 = lapNote.get((rr.num, lap), '')
			i2 = numTimeInfo.getInfoStr(rr.num, t)
			if i1 or i2:
				details['{},{}'.format(rr.num, lap)] = [i1, i2]
				
	return details

@Model.memoize
def GetCategoryDetails( ignoreEmptyCategories=True, publishOnly=False ):
	if not Model.race:
		return []

	tempNums = UnstartedRaceDataProlog()
	unstarted = Model.race.isUnstarted()

	results = GetResults( None )
	
	catDetails = []
	race = Model.race
	
	DNS = Model.Rider.DNS
	Finisher = Model.Rider.Finisher
	
	# Create a custom category for all riders.
	info = {
		'name'			: 'All',
		'startOffset'	: 0,
		'gender'		: 'Open',
		'catType'		: 'Custom',
		'laps'			: 0,
		'pos'			: [rr.num for rr in results],
		'gapValue'		: [getattr(rr, 'gapValue', 0) for rr in results],
		'iSort'			: 0,
	}
	catDetails.append( info )
	
	# Add the remainder of the categories.
	lastWaveLaps = 0
	lastWaveCat = None
	lastWaveStartOffset = 0
	for iSort, cat in enumerate(race.getCategories( startWaveOnly=False, publishOnly=publishOnly ), 1):
		results = GetResults( cat )
		if ignoreEmptyCategories and not results:
			continue
		
		if cat.catType == cat.CatWave:
			lastWaveLaps = race.getNumLapsFromCategory(cat)
			lastWaveCat = cat
			lastWaveStartOffset = cat.getStartOffsetSecs()
			
		info = {
			'name'			: cat.fullname,
			'startOffset'	: lastWaveStartOffset if cat.catType == cat.CatWave or cat.catType == cat.CatComponent else 0.0,
			'gender'		: getattr( cat, 'gender', 'Open' ),
			'catType'		: ['Start Wave', 'Component', 'Custom'][cat.catType],
			'laps'			: lastWaveLaps if unstarted else 0,
			'pos'			: [rr.num for rr in results],
			'starters'		: sum( 1 for rr in results if rr.status != DNS ),
			'finishers'		: sum( 1 for rr in results if rr.status == Finisher ),
			'gapValue'		: [getattr(rr, 'gapValue', 0) for rr in results],
			'iSort'			: iSort,
		}
		
		try:
			info['laps'] = max( info['laps'], max(len(rr.lapTimes) for rr in results if rr.status == Model.Rider.Finisher) )
		except ValueError:
			pass
		
		catDetails.append( info )
		
		waveCat = lastWaveCat
		if waveCat:
			if getattr(waveCat, 'distance', None):
				if getattr(waveCat, 'distanceType', Model.Category.DistanceByLap) == Model.Category.DistanceByLap:
					info['lapDistance'] = waveCat.distance
					if getattr(waveCat, 'firstLapDistance', None):
						info['firstLapDistance'] = waveCat.firstLapDistance
					info['raceDistance'] = waveCat.getDistanceAtLap( info['laps'] )
				else:
					info['raceDistance'] = waveCat.distance
		info['distanceUnit'] = race.distanceUnitStr
	
	# Cleanup.
	UnstartedRaceDataEpilog( tempNums )

	return catDetails

def GetAnimationData( category=None, getExternalData=False ):
	animationData = {}
	ignoreFields = {'pos', 'num', 'gap', 'gapValue', 'laps', 'lapTimes', 'full_name', 'short_name'}
	statusNames = Model.Rider.statusNames
	
	with UnstartedRaceWrapper( getExternalData ):
		with Model.LockRace() as race:
			riders = race.riders
			for cat in ([category] if category else race.getCategories()):
				results = GetResults( cat )
				
				for rr in results:
					info = {
						'flr': race.getCategory(rr.num).firstLapRatio,
						'relegated': riders[rr.num].isRelegated(),
					}
					bestLaps = race.getNumBestLaps( rr.num )
					for a in dir(rr):
						if a.startswith('_') or a in ignoreFields:
							continue
						if a == 'raceTimes':
							info['raceTimes'] = getattr(rr, a)
							if bestLaps is not None and len(info['raceTimes']) > bestLaps:
								info['raceTimes'] = info['raceTimes'][:bestLaps+1]
						elif a == 'status':
							info['status'] = statusNames[getattr(rr, a)]
						elif a == 'lastTime':
							try:
								info[a] = rr.raceTimes[-1]
							except IndexError:
								info[a] = rr.lastTime
						else:
							info[a] = getattr( rr, a )
					
					if race.isTimeTrial:
						info['startTime'] = race.riders[rr.num].firstTime
					animationData[rr.num] = info
		
	return animationData

def GetRaceName():
	return Model.race.getFileName()[:-4] if Model.race else None

versionCountStart = 10000
versionCount = versionCountStart
resultsBaseline = { 'cmd': 'baseline', 'categoryDetails':{}, 'info':{}, 'reference':{} }
def getReferenceInfo():
	global versionCount
	race = Model.race
	tLastRaceTime = race.lastRaceTime() if race else 0.0;
	tNow = datetime.now()	
	return {
		'versionCount': versionCount,
		'raceName': GetRaceName(),
		'raceIsRunning': race.isRunning() if race else False,
		'raceIsUnstarted': race.isUnstarted() if race else False,
		'raceIsFinished': race.isFinished() if race else False,
		'isTimeTrial': race.isTimeTrial if race else False,
		'winAndOut': race.winAndOut if race else False,
		'timestamp': [tNow.ctime(), tLastRaceTime],
		'tNow': tNow.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
		'raceTimeZone': race.timezone if race else '',
		'curRaceTime': race.curRaceTime() if race and race.isRunning() else 0.0,
	}

def ResetVersionRAM():
	global versionCountStart, versionCount
	# If we decrease the versionCountStart, nothing can have a version + 1.
	versionCountStart -= 100
	if versionCountStart <= 0:
		versionCountStart = 10000
	versionCount = versionCountStart
	
def GetResultsRAM():
	global versionCount, resultsBaseline
	
	race = Model.race
	if not race:
		return None
	
	categoryDetails = { c['name']:c for c in GetCategoryDetails(True, True) }
	info = GetAnimationData( None, True )
	raceName = GetRaceName()
	
	if (	resultsBaseline['info'] == info and
			resultsBaseline['categoryDetails'] == categoryDetails and
			resultsBaseline['reference'].get('raceIsRunning',None) == race.isRunning() and
			resultsBaseline['reference'].get('raceIsUnstarted',None) == race.isUnstarted() and
			resultsBaseline['reference'].get('raceName',None) == raceName and
			resultsBaseline['reference'].get('raceStartTime',None) == race.startTime
		):
		return None

	versionCount += 1
	resultsBaseline['reference'] = getReferenceInfo()

	ram = {
		'cmd':			'ram',
		'categoryRAM':	Utils.dict_compare( categoryDetails, resultsBaseline['categoryDetails'] ),
		'infoRAM':		Utils.dict_compare( info, resultsBaseline['info'] ),
		'reference':    resultsBaseline['reference'],
	}
	
	resultsBaseline['categoryDetails'] = categoryDetails
	resultsBaseline['info'] = info	
	return ram
	
def GetResultsBaseline():
	resultsBaseline['reference'] = getReferenceInfo()
	return resultsBaseline
	
@Model.memoize
def GetResultMap( category ):
	return {rr.num:rr for rr in GetResults(category)} 
	
def IsRiderFinished( bib, t ):
	race = Model.race
	if not race:
		return False
	category = race.getCategory( bib )
	if category is None:
		return False
	results = GetResults( category )
	if not results or results[0].status != Model.Rider.Finisher or results[0].laps != race.getNumLapsFromCategory( category ):
		return False
	
	rr = GetResultMap( category ).get( bib, None )
	return rr and rr.status == Model.Rider.Finisher and rr.raceTimes and rr.raceTimes[-1] == t

def IsRiderOnCourse( bib, tRace=None, rr=None ):
	race = Model.race
	if not race or not race.isRunning():
		return False
	
	rider = race.riders.get( bib, None )
	if not rider:
		return False
	
	category = race.getCategory( bib )
	if category is None:						# The rider must be in a category to be counted.
		return False

	if rr is None:
		rr = GetResultMap( category ).get( bib, None )
	
	tRace = tRace or race.curRaceTime()
	if race.isTimeTrial:
		if rider.firstTime is None or rider.firstTime > tRace:	# The rider didn't start yet.
			return False
		if not rr.lapTimes:										# Rider started but nothing recorded yet.
			return True
	
	Finisher = Model.Rider.Finisher
	
	results = GetResults( category )
	if not results or results[0].status != Finisher:
		return False							# No category leader.
		
	if rr is None or rr.status != Finisher:
		return False							# If the rider doesn't have a result, or is DNF or DQ, skip.
		
	if rr.interp and rr.interp[-1]:				# If the last time is estimated, rider is still on course.
		return True
			
	return False

def RidersOnCourseCount():
	race = Model.race
	if not race or not race.isRunning():
		return 0
	
	Finisher = Model.Rider.Finisher
	tRace = race.curRaceTime()
	count = 0
	for bib, rider in race.riders.items():
		if race.isTimeTrial:
			if rider.firstTime is None or rider.firstTime > tRace:		# The rider didn't start yet.
				continue
		
		category = race.getCategory( bib )
		if category is None:					# The rider must be in a category
			continue
		results = GetResults( category )
		if not results or results[0].status != Finisher:
			continue							# There must be a category leader.
			
		rr = GetResultMap( category ).get( bib, None )
		if rr is None or rr.status != Finisher:
			continue							# If the rider doesn't have a result, or has DNF or DQ, skip.
			
		if rr.raceTimes:
			if rr.lastInterp:					# If the last time is estimated, assume the rider is on course.
				continue

			lastTime = rr.raceTimes[-1]
			if race.isTimeTrial:
				lastTime += race.startTime
			if lastTime > tRace:
				count += 1						# The rider's last time is after the current race time.  Therefore, the rider is on course.
		
	return count
