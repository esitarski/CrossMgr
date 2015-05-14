import Model
from bisect import bisect_left
from math import floor
import sys
import copy
import Utils
import itertools

from ReadSignOnSheet import IgnoreFields, SyncExcelLink
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
		# Check if swapping the last times would result in race times out of order.
		with Model.LockRace() as race:
			e1 = race.getRider(num).interpolate()
			e2 = race.getRider(numAdjacent).interpolate()
		if e1[laps].interp or e2[laps].interp:
			return False
		rt1 = [e.t for e in e1]
		rt2 = [e.t for e in e2]
		rt1[laps], rt2[laps] = rt2[laps], rt1[laps]
		if 	all( x < y for x, y in itertools.izip(rt1, rt1[1:]) ) and \
			all( x < y for x, y in itertools.izip(rt2, rt2[1:]) ):
			return True
	except (IndexError, ValueError, KeyError):
		pass
	return False

def toInt( n ):
	try:
		return int(n.split()[0])
	except:
		return 99999
	
class RiderResult( object ):
	def __init__( self, num, status, lastTime, raceCat, lapTimes, raceTimes, interp ):
		self.num		= num
		self.status		= status
		self.gap		= ''
		self.pos		= ''
		self.speed		= ''
		self.laps		= len(lapTimes)
		self.lastTime	= lastTime
		self.lastTimeOrig = lastTime
		self.raceCat	= raceCat
		self.lapTimes	= lapTimes
		self.raceTimes	= raceTimes
		self.interp		= interp
		
	def full_name( self ):
		names = []
		try:
			names.append( self.LastName.upper() )
		except AttributeError:
			pass
		try:
			names.append( self.FirstName )
		except AttributeError:
			pass
		return u', '.join( names )
		
	def __repr__( self ):
		return str(self.__dict__)
		
	def _getKey( self ):
		return (statusSortSeq[self.status], -self.laps, self.lastTime, getattr(self, 'startTime', 0.0) or 0.0, self.num)
		
	def _getComponentKey( self ):
		return (statusSortSeq[self.status], toInt(self.pos), self.lastTime, getattr(self, 'startTime', 0.0) or 0.0, self.num)

DefaultSpeed = 0.00001

@Model.memoize
def GetResultsCore( category ):
	Finisher = Model.Rider.Finisher
	PUL = Model.Rider.Pulled
	NP = Model.Rider.NP
	rankStatus = { Finisher, PUL }
	
	riderResults = []
	with Model.LockRace() as race:
		if not race:
			return tuple()
		
		isTimeTrial = getattr( race, 'isTimeTrial', False )
		allCategoriesFinishAfterFastestRidersLastLap = race.allCategoriesFinishAfterFastestRidersLastLap
		raceStartSeconds = (
			race.startTime.hour*60.0*60.0 + race.startTime.minute*60.0 + race.startTime.second + race.startTime.microsecond / 1000000.0 if race.startTime
			else Utils.StrToSeconds(race.scheduledStart) * 60.0
		)
		
		allRiderTimes = {}
		entries = race.interpolate()
		
		# Group finish times are defined as times which are separated from the previous time by at least 1 second.
		groupFinishTimes = [0 if not entries else floor(entries[0].t)]
		groupFinishTimes.extend( [floor(entries[i].t) for i in xrange(1, len(entries)) if entries[i].t - entries[i-1].t >= 1.0] )
		groupFinishTimes.append( sys.float_info.max )
		groupFinishTimes.append( sys.float_info.max )
		groupFinishTimes.append( sys.float_info.max )
		groupFinishTimes.append( sys.float_info.max )
		groupFinishTimes.append( sys.float_info.max )
		
		for e in entries:
			try:
				allRiderTimes[e.num].append( e )
			except KeyError:
				allRiderTimes[e.num] = [e]
		
		def getRiderTimes( rider ):
			try:
				return allRiderTimes[rider.num]
			except KeyError:
				return tuple()
		
		startOffset = category.getStartOffsetSecs() if category else 0.0
		
		raceSeconds = race.minutes * 60.0
		
		# Enforce All Categories Finish After Fastest Rider's Last Lap
		fastestRidersLastLapTime = None
		if allCategoriesFinishAfterFastestRidersLastLap:
			resultBest = (0, sys.float_info.max)
			for c, (times, nums) in race.getCategoryTimesNums().iteritems():
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
		for c, (times, nums) in race.getCategoryTimesNums().iteritems():
			if category and c != category:
				continue
			
			# If the category num laps is specified, use that.
			if c.getNumLaps():
				categoryWinningLaps[c] = c.getNumLaps()
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
							winner = race[nums[winningLaps]]
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
		for rider in race.riders.itervalues():
			riderCategory = getCategory( rider.num )
			if (category and riderCategory != category) or riderCategory not in categoryWinningTime:
				continue
			
			cutoffTime = categoryWinningTime.get(riderCategory, raceSeconds)
			
			riderTimes = getRiderTimes( rider )
			times = [e.t for e in riderTimes]
			interp = [e.interp for e in riderTimes]
			
			if len(times) >= 2:
				times[0] = min(riderCategory.getStartOffsetSecs(), times[1])
				if categoryWinningLaps.get(riderCategory, None) and getattr(riderCategory, 'lappedRidersMustContinue', False):
					laps = min( categoryWinningLaps[riderCategory], len(times)-1 )
				else:
					laps = bisect_left( times, cutoffTime, hi=len(times)-1 )
				
				times = times[:laps+1]
				interp = interp[:laps+1]
			else:
				laps = 0
				times = []
				interp = []
			
			lastTime = rider.tStatus
			if not lastTime:
				if times:
					lastTime = times[-1]
				else:
					lastTime = 0.0
			
			status = Finisher if rider.status in rankStatus else rider.status
			if isTimeTrial and not lastTime and rider.status == Finisher:
				status = NP
			rr = RiderResult(	rider.num, status, lastTime,
								riderCategory.fullname,
								[times[i] - times[i-1] for i in xrange(1, len(times))],
								times,
								interp )
			
			if isTimeTrial:
				rr.startTime = getattr( rider, 'firstTime', None )
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
			if getattr(riderCategory, 'distance', None):
				distance = getattr(riderCategory, 'distance')
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
						rr.speed = '%.2f %s' % (raceSpeeds[-1], ['km/h', 'mph'][getattr(race, 'distanceUnit', 0)] )
					rr.raceSpeeds = raceSpeeds
				else:	# Distance is by entire race.
					if rider.status == Finisher and rr.raceTimes:
						riderDistance = distance
						try:
							tCur = rr.raceTimes[-1] - rr.raceTimes[0]
							speed = DefaultSpeed if tCur <= 0.0 else riderDistance / (tCur / (60.0*60.0))
						except IndexError as e:
							speed = DefaultSpeed
						rr.speed = '%.2f %s' % (speed, ['km/h', 'mph'][getattr(race, 'distanceUnit', 0)] )
						
			riderResults.append( rr )
		
		if not riderResults:
			return tuple()
		
		if race.isRunning():
			def overlap(start1, end1, start2, end2):
				"""Does the range (start1, end1) overlap with (start2, end2)?"""
				return end1 >= start2 and end2 >= start1
				
			# Sequence the riders based on the last lap time, not the projected winner of the race.
			t = race.curRaceTime()
			statusLapsTimeBest = (99, 0, 24*60*60*200)
			rrLeader = None
			for rr in riderResults:
				if not rr.raceTimes:
					continue
				iT = bisect_left( rr.raceTimes, t )
				try:
					if rr.raceTimes[iT] != t:
						iT -= 1
				except IndexError:
					iT -= 1
				
				iT = max( iT, 0 )
				statusLapsTime = (statusSortSeq[rr.status], -iT, rr.raceTimes[iT])
				if statusLapsTime < statusLapsTimeBest:
					statusLapsTimeBest = statusLapsTime
					rrLeader = rr
			
			lapBest = -statusLapsTimeBest[1]
			
			tLapStartBest = rrLeader.raceTimes[lapBest]
			try:
				tLapEndBest = rrLeader.raceTimes[lapBest+1]
			except IndexError:
				tLapEndBest = None
			
			for rr in riderResults:
				if rr.raceTimes:
					try:
						rr.lastTime = rr.raceTimes[lapBest]
						rr.laps = min( rr.laps, lapBest )
						
						# Check for laps down.
						if tLapEndBest is not None and rr.laps == lapBest:
							for iLapCur in xrange(lapBest, -1, -1):
								if overlap(tLapStartBest, tLapEndBest, rr.raceTimes[iLapCur], rr.raceTimes[iLapCur+1]):
									rr.laps = iLapCur
									break
					except IndexError:
						pass
		
		riderResults.sort( key = RiderResult._getKey )
		
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
				
			rr.pos = u'{}'.format(pos+1)
			
			# if gapValue is negative, it means laps down.  Otherwise, it is seconds.
			rr.gapValue = 0
			if rr.laps != leader.laps:
				lapsDown = leader.laps - rr.laps
				rr.gap = u'-{} {}'.format(lapsDown, _('lap') if lapsDown == 1 else _('laps'))
				rr.gapValue = -lapsDown
			elif rr != leader and not (isTimeTrial and rr.lastTime == leader.lastTime):
				rr.gap = Utils.formatTimeGap( TimeDifference(rr.lastTime, leader.lastTime, highPrecision), highPrecision )
				rr.gapValue = rr.lastTime - leader.lastTime
				
		# Add stage race times and gaps.
		iTime = 0
		lastFullLapsTime = 60.0
		for pos, rr in enumerate(riderResults):
			rr.projectedTime = rr.lastTime
			if rr.status != Finisher or not rr.raceTimes:
				rr.stageRaceTime = floor(rr.lastTime)
				rr.stageRaceGap = rr.gap
			elif rr.laps == leader.laps:
				if not (groupFinishTimes[iTime] <= rr.lastTime < groupFinishTimes[iTime+1]):
					iTime += 1
					if not (groupFinishTimes[iTime] <= rr.lastTime < groupFinishTimes[iTime+1]):
						iTime = bisect_left( groupFinishTimes, rr.lastTime, 0, len(groupFinishTimes) - 1 )
						if groupFinishTimes[iTime] > rr.lastTime:
							iTime -= 1
				rr.stageRaceTime = groupFinishTimes[iTime]
				rr.stageRaceGap = Utils.formatTimeGap( rr.stageRaceTime - leader.stageRaceTime, False )
				lastFullLapsTime = rr.stageRaceTime + 60.0
			else:
				# Compute a projected finish time.  Try to skip the first lap in the calculation.
				if len(rr.raceTimes) > 1:
					lapStart = min( len(rr.raceTimes), 1 if len(rr.raceTimes) > 2 else 0 )
					raceTime = rr.raceTimes[rr.laps] - rr.raceTimes[lapStart]
					aveLapTime = raceTime / (float(rr.laps - lapStart) if rr.laps - lapStart > 0 else 0.000001)
					lapsDown = leader.laps - rr.laps
					rr.projectedTime = rr.raceTimes[-1] + lapsDown * aveLapTime
					rr.stageRaceTime = max( lastFullLapsTime, floor(rr.projectedTime) )
					rr.stageRaceGap = Utils.formatTimeGap( rr.stageRaceTime - leader.stageRaceTime, False ) if rr != leader else ''
				else:
					rr.stageRaceTime = rr.projectedTime = 5 * 24.0 * 60.0 * 60.0
				rr.stageRaceGap = Utils.formatTimeGap( rr.stageRaceTime - leader.stageRaceTime, False ) if rr != leader else ''
		
		if isTimeTrial:
			for rr in riderResults:
				rider = race[rr.num]
				if rider.status == Finisher and hasattr(rider, 'ttPenalty'):
					rr.ttPenalty = getattr(rider, 'ttPenalty')
					rr.ttNote = getattr(rider, 'ttNote', u'')
		
		# Fix relegations.
		if any( race[rr.num].isRelegated() for rr in riderResults ):
			relegatedResults = {}
			relegated = set()
			maxRelegatedPosition = 0
			for rr in riderResults:
				rider = race[rr.num]
				if rider.isRelegated():
					rr.relegated = True
					relegated.add( rr )
					relegatedPosition = rider.relegatedPosition
					while relegatedResults.get(relegatedPosition-1, None) is not None:
						relegatedPosition += 1
					relegatedResults[relegatedPosition-1] = rr
					maxRelegatedPosition = max( maxRelegatedPosition, relegatedPosition )
				
			posCur = 0
			doneFinishers = False
			for rr in riderResults:
				if rr not in relegated:
					if not doneFinishers and rr.status != Finisher:
						doneFinishers = True
						posCur = maxRelegatedPosition
					while relegatedResults.get(posCur, None) is not None:
						posCur += 1
					relegatedResults[posCur] = rr
					posCur += 1
			
			riderResults = [v[1] for v in sorted(relegatedResults.iteritems(), key = lambda x: x[0])]
			for pos, rr in enumerate(riderResults):
				if rr.status != Finisher:
					break
				rr.pos = u'{} {}'.format(pos+1, _('REL')) if rr in relegated else pos + 1
		
		'''
		for rr in riderResults:
			rr.lastTime = rr.stageRaceTime
			rr.gap = rr.stageRaceGap
		'''
	
	return tuple(riderResults)

def GetResults( category, getExternalData = False ):
	if category and category.catType != Model.Category.CatWave:
		return GetNonWaveCategoryResults( category )

	riderResults = GetResultsCore( category )
	if not getExternalData or not riderResults:
		return riderResults
	
	# Add the linked external data.
	with Model.LockRace() as race:
		try:
			excelLink = race.excelLink
			externalFields = excelLink.getFields()
			externalInfo = excelLink.read()
			for ignoreField in IgnoreFields:
				try:
					externalFields.remove( ignoreField )
				except ValueError:
					pass
		except:
			excelLink = None
			externalFields = []
			externalInfo = {}
				
		for rr in riderResults:
			for f in externalFields:
				try:
					setattr( rr, f, externalInfo[rr.num][f] )
				except KeyError:
					setattr( rr, f, '' )
	
	if excelLink and excelLink.hasField( 'Factor' ):
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
			except:
				startOffset = 0.0
				
			try:
				ttPenalty = rr.ttPenalty
			except:
				ttPenalty = 0.0
			
			# Adjust the true ride time by the factor (subtract the start offset and any penalties, add them back later).
			rr.lastTime = startOffset + ttPenalty + max(0.0, rr.lastTimeOrig - startOffset - ttPenalty) * factor
			
		riderResults.sort( key=RiderResult._getKey )
	
		# Assign finish position.
		statusNames = Model.Rider.statusNames
		for pos, rr in enumerate(riderResults):
			if rr.status == Model.Rider.Finisher:
				rr.pos = u'{}'.format( pos + 1 ) if not getattr(rr, 'relegated', False) else u'{} {}'.format( pos + 1, _('REL') )
			else:
				rr.pos = statusNames[rr.status]
		
		riderResults = tuple( riderResults )
	
	return riderResults

def GetNonWaveCategoryResults( category ):
	race = Model.race
	if not race:
		return tuple()
	
	isTimeTrial = getattr( race, 'isTimeTrial', False )
	highPrecision = Model.highPrecisionTimes()
	
	rrCache = {}
	riderResults = []

	getCategory = race.getCategory
	for num in race.getRiderNums():
		if not race.inCategory(num, category):
			continue
		
		try:
			riderResults.append( copy.copy(rrCache[num]) )
		except KeyError:
			results = GetResults( getCategory(num), True )
			rrCache.update( { (rr.num, rr) for rr in results } )
			try:
				riderResults.append( copy.copy(rrCache[num]) )
			except KeyError:
				continue
		
		# Remove the start offset from the race times and finish times.
		rr = riderResults[-1]
		try:
			startOffset = rr.raceTimes[0]
		except:
			startOffset = 0.0
			
		try:
			rr.lastTime = max( 0.0, rr.lastTime - startOffset )
		except:
			pass
			
		rr.raceTimes = [t - startOffset for t in rr.raceTimes]
	
	# Sort the new results.
	riderResults.sort( key = (RiderResult._getComponentKey if category.catType == Model.Category.CatComponent else RiderResult._getKey) )
	
	# Assign finish position, gaps and status.
	statusNames = Model.Rider.statusNames
	leader = riderResults[0] if riderResults else None
	if leader:
		leader.gap = ''
		for pos, rr in enumerate(riderResults):
			if rr.status == Model.Rider.Finisher:
				rr.pos = u'{}'.format( pos + 1 ) if not getattr(rr, 'relegated', False) else u'{} {}'.format(pos + 1, _('REL'))
				if rr.laps != leader.laps:
					if rr.lastTime > leader.lastTime:
						lapsDown = leader.laps - rr.laps
						rr.gap = u'-{} {}'.format(lapsDown, _('laps') if lapsDown > 1 else _('lap'))
				elif rr != leader and not (isTimeTrial and rr.lastTime == leader.lastTime):
					rr.gap = Utils.formatTimeGap( TimeDifference(rr.lastTime, leader.lastTime, highPrecision), highPrecision )
			else:
				rr.pos = statusNames[rr.status]
	
	return tuple(riderResults)
	
@Model.memoize
def GetLastFinisherTime():
	results = GetResultsCore( None )
	finisher = Model.Rider.Finisher
	try:
		return max( r.lastTime for r in results if r.status == finisher )
	except:
		return 0.0
	
def GetLeaderFinishTime():
	results = GetResultsCore( None )
	if results and results[0].status == Model.Rider.Finisher:
		return results[0].lastTime
	else:
		return 0.0

def UnstartedRaceDataProlog( getExternalData = True ):
	tempNums = set()
	externalInfo = None
	
	with Model.LockRace() as race:
		if race and getExternalData and race.isUnstarted():
			try:
				externalInfo = race.excelLink.read()
			except:
				pass
		
		# Add all numbers from the spreadsheet if they are not already in the race.
		# Default the status to NP.
		if externalInfo:
			for num, info in externalInfo.iteritems():
				if num not in race.riders and any(info.get(f, None) for f in ['LastName', 'FirstName', 'Team', 'License']):
					rider = race.getRider( num )
					rider.status = Model.Rider.NP
					tempNums.add( num )
			race.resetCache()
	
	return tempNums
	
def UnstartedRaceDataEpilog( tempNums ):
	# Remove all temporary numbers.
	race = Model.race
	if race and tempNums:
		for num in tempNums:
			race.deleteRider( num )
		race.resetCache()

class UnstartedRaceWrapper( object ):
	count = 0	# Ensure that we can nest calls without problems.
	
	def __init__(self,  getExternalData = True):
		self.getExternalData = getExternalData
		
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
	for rr in GetResults( None ):
		for lap, t in enumerate(rr.raceTimes):
			i1 = lapNote.get((rr.num, lap), u'')
			i2 = numTimeInfo.getInfoStr(rr.num, t)
			if i1 or i2:
				details[u'{},{}'.format(rr.num, lap)] = [i1, i2]
				
	return details

@Model.memoize
def GetCategoryDetails( ignoreEmptyCategories = True ):
	if not Model.race:
		return []

	SyncExcelLink( Model.race )
	
	tempNums = UnstartedRaceDataProlog()
	unstarted = Model.race.isUnstarted()

	results = GetResultsCore( None )
	
	catDetails = []
	with Model.LockRace() as race:
	
		# Create a custom category for all riders.
		info = dict(
				name			= 'All',
				startOffset		= 0,
				gender			= 'Open',
				catType			= 'Custom',
				laps			= 0,
				pos				= [rr.num for rr in results] )
		catDetails.append( info )
		
		# Add the remainder of the categories.
		lastWaveLaps = 0
		lastWaveCat = None
		lastWaveStartOffset = 0
		for cat in race.getCategories( False ):
			results = GetResults( cat, True )
			if ignoreEmptyCategories and not results:
				continue
			
			if cat.catType == cat.CatWave:
				lastWaveLaps = cat.getNumLaps()
				lastWaveCat = cat
				lastWaveStartOffset = cat.getStartOffsetSecs()
				
			info = dict(
					name		= cat.fullname,
					startOffset	= lastWaveStartOffset if cat.catType == cat.CatWave or cat.catType == cat.CatComponent else 0.0,
					gender		= getattr( cat, 'gender', 'Open' ),
					catType		= ['Start Wave', 'Component', 'Custom'][cat.catType],
					laps		= lastWaveLaps if unstarted else 0,
					pos			= [] )
			
			catDetails.append( info )
					
			for rr in results:
				info['pos'].append( rr.num )
				if rr.status == Model.Rider.Finisher:
					info['laps'] = max( info['laps'], len(rr.lapTimes) )
			
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
