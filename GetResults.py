import Model
from ReadSignOnSheet import IgnoreFields
statusSortSeq = Model.Rider.statusSortSeq

class RiderResult( object ):
	def __init__( self, num, status, lastTime, raceCat, lapTimes, raceTimes, interp ):
		self.num		= num
		self.status		= status
		self.gap		= ''
		self.pos		= ''
		self.laps		= len(lapTimes)
		self.lastTime	= lastTime
		self.raceCat	= raceCat
		self.lapTimes	= lapTimes
		self.raceTimes	= raceTimes
		self.interp		= interp
		
def GetResults( catName = 'All', getExternalData = False ):
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
				categoryWinningTime[c] = times[c.getNumLaps()]
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
		
		riderResults = []
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
			
			riderResults.append( RiderResult(rider.num, rider.status, lastTime,
									riderCategory.name,
									[times[i] - times[i-1] for i in xrange(1, len(times))],
									times,
									interp) )
		
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
				rr.gap = Utils.formatTimeGap( rr.lastTime - leader.lastTime )
		
		return riderResults
		
