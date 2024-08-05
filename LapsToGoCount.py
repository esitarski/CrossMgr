from collections import defaultdict
from bisect import bisect_right

import Model
from GetResults import GetResults

def LapsToGoCount( t=None ):
	# Returns a dict indexed by category with a list of (lapsToGo, count).
	ltgc = defaultdict( list )
	
	race = Model.race
	if not race or race.isUnstarted() or race.isFinished():
		return ltgc

	if not t:
		t = race.curRaceTime()

	Finisher = Model.Rider.Finisher
	lapsToGoCount = defaultdict( int )
	for category in race.getCategories():
		for rr in GetResults(category):
			if rr.status != Finisher or not rr.raceTimes:
				break
			try:
				tSearch = race.riders[rr.num].raceTimeToRiderTime( t )
			except KeyError:
				continue
			
			if rr.raceTimes[-1] <= tSearch or not (lap := bisect_right(rr.raceTimes, tSearch) ):
				continue
			
			lapsToGoCount[len(rr.raceTimes) - lap] += 1
		
		if lapsToGoCount:
			ltgc[category] = sorted( lapsToGoCount.items(), reverse=True )
			lapsToGoCount.clear()
		
	return ltgc
