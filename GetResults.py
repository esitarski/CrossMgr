import Model
import bisect
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

DefaultSpeed = 0.00001
		
@Model.memoize
def GetResultsCore( category ):
	
	riderResults = []
	with Model.LockRace() as race:
		if not race:
			return tuple()
			
		allRiderTimes = {}
		for e in race.interpolate():
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
			
		# Get the number of race laps for each category.
		raceNumLaps = (race.numLaps or 1000)
		categoryWinningTime = {}
		for c, (times, nums) in race.getCategoryTimesNums().iteritems():
			if not times or (category and c != category):
				continue
				
			# If the category num laps is specified, use that.
			if c.getNumLaps():
				categoryWinningTime[c] = times[min(len(times)-1, c.getNumLaps())]
			else:
				# Otherwise, set the number of laps by the winner's time closest to the race finish time.
				try:
					winningLaps = bisect.bisect_left( times, race.minutes * 60.0, hi=len(times)-1 )
					if winningLaps > raceNumLaps:
						winningLaps = raceNumLaps
					elif winningLaps >= 2:
						winner = race[nums[winningLaps]]
						entries = winner.interpolate()
						if entries[winningLaps].interp:
							lastLapTime = times[winningLaps] - times[winningLaps-1]
							if (times[winningLaps] - race.minutes * 60.0) > lastLapTime / 2.0:
								winningLaps -= 1
					categoryWinningTime[c] = times[winningLaps]
				except IndexError:
					categoryWinningTime[c] = race.minutes * 60.0
		
		if not categoryWinningTime:
			return tuple()
		
		highPrecision = Utils.highPrecisionTimes()
		isTimeTrial = getattr( race, 'isTimeTrial', False )
		for rider in race.riders.itervalues():
			riderCategory = race.getCategory( rider.num )
			if (category and riderCategory != category) or riderCategory not in categoryWinningTime:
				continue
			
			riderTimes = getRiderTimes( rider )
			times = [e.t for e in riderTimes]
			interp = [e.interp for e in riderTimes]
			
			if times:
				times[0] = min(riderCategory.getStartOffsetSecs(), times[1])
				laps = bisect.bisect_left( times, categoryWinningTime[riderCategory], hi=len(times)-1 )
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
			
		riderResults.sort( key = lambda x: (statusSortSeq[x.status], -x.laps, x.lastTime) )
		
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
				
			rr.pos = str(pos+1)
			
			if rr.laps != leader.laps:
				if rr.lastTime > leader.lastTime:
					lapsDown = leader.laps - rr.laps
					rr.gap = '%d %s' % (lapsDown, 'laps' if lapsDown > 1 else 'lap')
			elif rr != leader and not (isTimeTrial and rr.lastTime == leader.lastTime):
				rr.gap = Utils.formatTimeGap( TimeDifference(rr.lastTime, leader.lastTime, highPrecision), highPrecision )
		
	return tuple(riderResults)

def GetResults( category, getExternalData = False ):
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
			return riderResults
				
		for rr in riderResults:
			for f in externalFields:
				try:
					setattr( rr, f, externalInfo[rr.num][f] )
				except KeyError:
					setattr( rr, f, '' )
		
	return riderResults

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
		
	catDetails = {}
	with Model.LockRace() as race:
		if not race:
			return catDetails
		for rr in results:
			if not rr.lapTimes:
				continue
			cat = race.getCategory( rr.num )
			info = catDetails.get( cat.fullname, {} )
			if not info:
				info['startOffset'] = cat.getStartOffsetSecs()
				info['gender'] = getattr( cat, 'gender', 'Open' )
				
			if info.get('laps', 0) < len(rr.lapTimes):
				info['laps'] = len(rr.lapTimes)
				if getattr(cat, 'distance', None):
					if getattr(cat, 'distanceType', Model.Category.DistanceByLap) == Model.Category.DistanceByLap:
						info['lapDistance'] = cat.distance
						if getattr(cat, 'firstLapDistance', None):
							info['firstLapDistance'] = cat.firstLapDistance
						info['raceDistance'] = cat.getDistanceAtLap( info['laps'] )
					else:
						info['raceDistance'] = cat.distance
				info['distanceUnit'] = race.distanceUnitStr
				catDetails[cat.fullname] = info
	
	return catDetails