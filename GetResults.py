import Model
from bisect import bisect_left
from math import floor
import sys
import copy
import Utils
import itertools

from ReadSignOnSheet import IgnoreFields
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

class RiderResult( object ):
	def __init__( self, num, status, lastTime, raceCat, lapTimes, raceTimes, interp ):
		self.num		= num
		self.status		= status
		self.gap		= ''
		self.pos		= ''
		self.speed		= ''
		self.laps		= len(lapTimes)
		self.lastTime	= lastTime
		self.raceCat	= raceCat
		self.lapTimes	= lapTimes
		self.raceTimes	= raceTimes
		self.interp		= interp
		
	def __repr__( self ):
		return str(self.__dict__)
		
	def _getKey( self ):
		return (statusSortSeq[self.status], -self.laps, self.lastTime, getattr(self, 'startTime', 0.0) or 0.0, self.num)

DefaultSpeed = 0.00001
		
@Model.memoize
def GetResultsCore( category ):

	riderResults = []
	with Model.LockRace() as race:
		if not race:
			return tuple()
		
		isTimeTrial = getattr( race, 'isTimeTrial', False )
		allCategoriesFinishAfterFastestRidersLastLap = getattr( race, 'allCategoriesFinishAfterFastestRidersLastLap', False )
		
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
		
		# Get the race seconds.
		if race.numLaps:
			# If the number of laps is manually specified, find the category that results in the shortest race time with
			# the manually specified number of laps.
			raceSeconds = None
			for c, (times, nums) in race.getCategoryTimesNums().iteritems():
				if not times:
					continue
				try:
					if raceSeconds is None or times[race.numLaps] < raceSeconds:
						raceSeconds = times[race.numLaps] - 0.01
				except IndexError:
					pass
			if raceSeconds is None:
				raceSeconds = race.minutes * 60.0
		else:
			# Use the specified race time.
			raceSeconds = race.minutes * 60.0
		
		# Enforce All Categories Finish After Fastest Rider's Last Lap
		fastestRidersLastLapTime = None
		if allCategoriesFinishAfterFastestRidersLastLap:
			winningLapsMax = 0
			for c, (times, nums) in race.getCategoryTimesNums().iteritems():
				if not times:
					continue
				try:
					winningLaps = bisect_left( times, raceSeconds, hi=len(times)-1 )
					if winningLaps >= 2:
						lastLapTime = times[winningLaps] - times[winningLaps-1]
						if (times[winningLaps] - raceSeconds) > lastLapTime / 2.0:
							winningLaps -= 1
					if winningLaps >= winningLapsMax:
						winningLapsMax = winningLaps
						if fastestRidersLastLapTime is None or times[winningLaps] < fastestRidersLastLapTime:
							fastestRidersLastLapTime = times[winningLaps]
				except IndexError:
					pass
		
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
		
		highPrecision = Utils.highPrecisionTimes()
		for rider in race.riders.itervalues():
			riderCategory = race.getCategory( rider.num )
			if (category and riderCategory != category) or riderCategory not in categoryWinningTime:
				continue
			
			riderTimes = getRiderTimes( rider )
			times = [e.t for e in riderTimes]
			interp = [e.interp for e in riderTimes]
			
			if times:
				times[0] = min(riderCategory.getStartOffsetSecs(), times[1])
				if categoryWinningLaps.get(riderCategory, None) and getattr(riderCategory, 'lappedRidersMustContinue', False):
					laps = min( categoryWinningLaps[riderCategory], len(times)-1 )
				else:
					laps = bisect_left( times, categoryWinningTime[riderCategory], hi=len(times)-1 )
				# This is no longer necessary as we have a smarter ability to check for excess laps.
				#if fastestRidersLastLapTime is not None:
				#	while laps >= 1 and interp[laps] and times[laps] > fastestRidersLastLapTime:
				#		laps -= 1
				times = times[:laps+1]
				interp = interp[:laps+1]
			else:
				laps = 0
			lastTime = rider.tStatus
			if not lastTime:
				if times:
					lastTime = times[-1]
				else:
					lastTime = 0.0
			
			rr = RiderResult(	rider.num, rider.status, lastTime,
								riderCategory.fullname,
								[times[i] - times[i-1] for i in xrange(1, len(times))],
								times,
								interp )
			
			if isTimeTrial:
				rr.startTime = getattr( rider, 'firstTime', None )
				if rr.status == Model.Rider.Finisher:
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
					riderDistance = distance
					# Only add the rider speed if the rider finished.
					if lastTime and rider.status == Model.Rider.Finisher:
						tCur = lastTime - startOffset
						speed = DefaultSpeed if tCur <= 0.0 else riderDistance / (tCur / (60.0*60.0))
						rr.speed = '%.2f %s' % (speed, ['km/h', 'mph'][getattr(race, 'distanceUnit', 0)] )
						
			riderResults.append( rr )
		
		if not riderResults:
			return tuple()
			
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
		
			if rr.status != Model.Rider.Finisher:
				rr.pos = Model.Rider.statusNames[rr.status]
				continue
				
			rr.pos = '{}'.format(pos+1)
			
			if rr.laps != leader.laps:
				if rr.lastTime > leader.lastTime:
					lapsDown = leader.laps - rr.laps
					rr.gap = '-%d %s' % (lapsDown, _('laps') if lapsDown > 1 else _('lap'))
			elif rr != leader and not (isTimeTrial and rr.lastTime == leader.lastTime):
				rr.gap = Utils.formatTimeGap( TimeDifference(rr.lastTime, leader.lastTime, highPrecision), highPrecision )
				
		# Add stage race times and gaps.
		iTime = 0
		lastFullLapsTime = None
		for pos, rr in enumerate(riderResults):
			if rr.status != Model.Rider.Finisher or not rr.raceTimes:
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
				lapStart = 1 if len(rr.raceTimes) > 2 else 0
				raceTime = rr.raceTimes[rr.laps] - rr.raceTimes[lapStart]
				aveLapTime = raceTime / float(rr.laps - lapStart)
				lapsDown = leader.laps - rr.laps
				rr.stageRaceTime = max( lastFullLapsTime, floor(rr.raceTimes[-1] + lapsDown * aveLapTime) )
				rr.stageRaceGap = Utils.formatTimeGap( rr.stageRaceTime - leader.stageRaceTime, False ) if rr != leader else ''
		
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
			externalFields = race.excelLink.getFields()
			externalInfo = race.excelLink.read()
			for ignoreField in IgnoreFields:
				try:
					externalFields.remove( ignoreField )
				except ValueError:
					pass
		except:
			externalFields = []
			externalInfo = []
				
		for rr in riderResults:
			for f in externalFields:
				try:
					setattr( rr, f, externalInfo[rr.num][f] )
				except KeyError:
					setattr( rr, f, '' )
	
	return riderResults

def GetNonWaveCategoryResults( category ):
	race = Model.race
	if not race:
		return tuple()
	
	isTimeTrial = getattr( race, 'isTimeTrial', False )
	highPrecision = Utils.highPrecisionTimes()
	
	rrCache = {}
	riderResults = []
	for num in race.getRiderNums():
		if not race.inCategory(num, category):
			continue
		
		try:
			riderResults.append( copy.copy(rrCache[num]) )
		except KeyError:
			results = GetResults( race.getCategory(num), True )
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
	riderResults.sort( key = RiderResult._getKey )
	
	# Assign finish position and status.
	statusNames = Model.Rider.statusNames
	leader = riderResults[0] if riderResults else None
	leader.gap = ''
	for pos, rr in enumerate(riderResults):
		if rr.status == Model.Rider.Finisher:
			rr.pos = u'{}'.format( pos + 1 )
			if rr.laps != leader.laps:
				if rr.lastTime > leader.lastTime:
					lapsDown = leader.laps - rr.laps
					rr.gap = '-%d %s' % (lapsDown, _('laps') if lapsDown > 1 else _('lap'))
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
	
@Model.memoize
def GetCategoryDetails():
	results = GetResultsCore( None )
	if not results:
		return {}
		
	catDetails = []
	with Model.LockRace() as race:
		if not race:
			return catDetails
		
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
		for cat in race.getCategories( False ):
			results = GetResults( cat, True )
			if not results:
				continue
				
			info = dict(
					name		= cat.fullname,
					startOffset	= cat.getStartOffsetSecs() if cat.catType == cat.CatWave else 0.0,
					gender		= getattr( cat, 'gender', 'Open' ),
					catType		= ['StartWave', 'Component', 'Custom'][cat.catType],
					laps		= 0,
					pos			= [] )
			
			catDetails.append( info )
					
			for rr in results:
				info['pos'].append( rr.num )
				
				if info['laps'] < len(rr.lapTimes):
					waveCat = race.getCategory( rr.num )
					info['laps'] = len(rr.lapTimes)
					if getattr(waveCat, 'distance', None):
						if getattr(waveCat, 'distanceType', Model.Category.DistanceByLap) == Model.Category.DistanceByLap:
							info['lapDistance'] = waveCat.distance
							if getattr(waveCat, 'firstLapDistance', None):
								info['firstLapDistance'] = waveCat.firstLapDistance
							info['raceDistance'] = waveCat.getDistanceAtLap( info['laps'] )
						else:
							info['raceDistance'] = waveCat.distance
					info['distanceUnit'] = race.distanceUnitStr
					
	return catDetails