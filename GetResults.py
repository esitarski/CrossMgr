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
		
def GetResults( catName = 'All', getExternalData = False ):
	
	riderResults = []
	with Model.LockRace() as race:
		if not race:
			return []
		
		category = race.categories.get( catName, None )
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
			return []
		
		highPrecision = Utils.highPrecisionTimes()
		isTimeTrial = getattr( race, 'isTimeTrial', False )
		for rider in race.riders.itervalues():
			riderCategory = race.getCategory( rider.num )
			if (category and riderCategory != category) or riderCategory not in categoryWinningTime:
				continue
			
			riderTimes = rider.interpolate()
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
								riderCategory.name,
								[times[i] - times[i-1] for i in xrange(1, len(times))],
								times,
								interp )
			
			if isTimeTrial:
				rr.startTime = getattr( rider, 'startTime', None )
				if rr.status == Model.Rider.Finisher:
					try:
						rr.finishTime = rr.startTime + rr.lastTime
					except (TypeError, AttributeError):
						pass
			
			# Compute the speeds for the rider.
			if getattr(riderCategory, 'distance', None):
				distance = getattr(riderCategory, 'distance')
				if riderCategory.distanceIsByLap:
					riderDistance = distance * len(rr.lapTimes)
					rr.lapSpeeds = [1000.0 if t <= 0.0 else (distance / (t / (60.0*60.0))) for t in rr.lapTimes]
					# Ensure that the race speeds are always consistent with the lap times.
					raceSpeeds = []
					if rr.lapSpeeds:
						speedCur = 0.0
						for i, s in enumerate(rr.lapSpeeds):
							speedCur += s
							raceSpeeds.append( speedCur / (i+1) )
					rr.raceSpeeds = raceSpeeds
					if rr.lapSpeeds:
						speed = sum(rr.lapSpeeds) / len(rr.lapSpeeds)
						rr.speed = '%.2f %s' % (speed, ['km/h', 'mph'][getattr(race, 'distanceUnit', 0)] )
				else:	# Distance is by entire race.
					riderDistance = distance
					# Only add the rider speed if the rider finished.
					if lastTime and rider.status == Model.Rider.Finisher:
						speed = riderDistance / (lastTime / (60.0*60.0))
						rr.speed = '%.2f %s' % (speed, ['km/h', 'mph'][getattr(race, 'distanceUnit', 0)] )
						
			riderResults.append( rr )
		
		if not riderResults:
			return []
			
		riderResults.sort( key = lambda x: (statusSortSeq[x.status], -x.laps, x.lastTime) )
		
		# Get the linked external data.
		externalFields = []
		externalInfo = None
		if getExternalData:
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
				externalInfo = None
		
		# Add external data.
		# Add the position (or status, if not a Finisher).
		# Fill in the gap field (include laps down if appropriate).
		leader = riderResults[0]
		for pos, rr in enumerate(riderResults):
			for f in externalFields:
				try:
					setattr( rr, f, externalInfo[rr.num][f] )
				except KeyError:
					setattr( rr, f, '' )
					
			if rr.status != Model.Rider.Finisher:
				rr.pos = Model.Rider.statusNames[rr.status]
				continue
				
			rr.pos = str(pos+1)
			
			if rr.laps != leader.laps:
				if rr.lastTime > leader.lastTime:
					lapsDown = leader.laps - rr.laps
					rr.gap = '%d %s' % (lapsDown, 'laps' if lapsDown > 1 else 'lap')
			elif rr != leader:
				rr.gap = Utils.formatTimeGap( TimeDifference(rr.lastTime, leader.lastTime, highPrecision), highPrecision )
		
	# Return the final results.
	return riderResults
		
def GetCategoryDetails():
	results = GetResults()
	catDetails = {}
	if not results:
		return catDetails
		
	with Model.LockRace() as race:
		if not race:
			return catDetails
		for rr in results:
			if not rr.lapTimes:
				continue
			cat = race.getCategory( rr.num )
			info = catDetails.get( cat.name, {} )
			if info.get('laps', 0) < len(rr.lapTimes):
				info['laps'] = len(rr.lapTimes)
				if getattr(cat, 'distance', None):
					if getattr(cat, 'distanceType', Model.Category.DistanceByLap) == Model.Category.DistanceByLap:
						info['lapDistance'] = cat.distance
						info['raceDistance'] = cat.distance * info['laps']
					else:
						info['raceDistance'] = cat.distance
				info['distanceUnit'] = race.distanceUnitStr
				catDetails[cat.name] = info
	
	return catDetails