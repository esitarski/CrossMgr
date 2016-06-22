import random
import bisect
from Names import GetNameTeam

def SimulateData( riders=6000 ):
	# Generate random rider events.
	random.seed( 10101021 )

	raceMinutes = 8
	mean = 8*60.0 / 8	# Average lap time.
	var = mean/20.0		# Variance between riders.
	lapsTotal = int(raceMinutes * 60 / mean + 3)
	raceTime = mean * lapsTotal
	errorPercent = 1.0/25.0

	for nMid in (10,100,200,500,1000,2000,5000,10000,20000,50000):
		if nMid >= riders:
			break
	numStart = nMid - riders//2
	startOffset = 10

	lapTimes = []
	riderInfo = []
	for num in xrange(numStart,numStart+riders+1):
		t = 0
		if num < numStart + riders // 2:
			mu = random.normalvariate( mean, mean/20.0 )			# Rider's random average lap time.
			riderInfo.append( [num] + list(GetNameTeam(True)) )
		else:
			mu = random.normalvariate( mean * 1.15, mean/20.0 )		# These riders are slower, on average.
			riderInfo.append( [num] + list(GetNameTeam(False)) )
			t += startOffset										# Account for offset start.
		for laps in xrange(lapsTotal):
			t += random.normalvariate( mu, var/2.0 )	# Rider's lap time.
			if random.random() > errorPercent:		# Respect error rate.
				lapTimes.append( (t, num) )

	lapTimes.sort()
	
	# Get the times and leaders for each lap.
	leaderTimes = [lapTimes[0][0]]
	leaderNums  = [lapTimes[0][1]]
	numSeen = set()
	for t, n in lapTimes:
		if n in numSeen:
			leaderTimes.append( t )
			leaderNums.append( n )
			numSeen.clear()
		numSeen.add( n )
	
	# Find the leader's time after the end of the race.
	iLast = bisect.bisect_left( leaderTimes, raceMinutes * 60.0, hi = len(leaderTimes) - 1 )
	if leaderTimes[iLast] < raceMinutes * 60.0:
		iLast += 1
		
	# Trim out everything except next arrivals after the finish time.
	tLeaderLast = leaderTimes[iLast]
	numSeen = set()
	afterLeaderFinishEvents = [evt for evt in lapTimes if evt[0] >= tLeaderLast]
	lapTimes = [evt for evt in lapTimes if evt[0] < tLeaderLast]
	
	# Find the next unique arrival of all finishers.
	lastLapFinishers = []
	tStop = raceMinutes * 60.0
	numSeen = set()
	for t, n in afterLeaderFinishEvents:
		if n not in numSeen:
			numSeen.add( n )
			lastLapFinishers.append( (t, n) )
			
	lapTimes.extend( lastLapFinishers )
	categories = [
		{'name':'Junior', 'catStr':'{}-{}'.format(nMid-riders//2,nMid-1), 'startOffset':'00:00', 'distance':0.5, 'gender':'Men', 'numLaps':5},
		{'name':'Senior', 'catStr':'{}-{}'.format(nMid,nMid+riders//2), 'startOffset':'00:{:02d}'.format(startOffset), 'distance':0.5, 'gender':'Women', 'numLaps':4}
	]
	
	return {
		'raceMinutes':	raceMinutes,
		'lapTimes':		lapTimes,
		'categories':	categories,
		'riderInfo':	riderInfo,
	}

if __name__ == '__main__':
	print SimulateData()['riderInfo']

