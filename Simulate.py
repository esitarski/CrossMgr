
import random
import pyExcelerator as pyXL

def SimulateCategory( numStart, riders, factor = 1.0, errorRate = 0.0, raceTime = 60.0 * 60.0, offset = 0.0 ):
	
	mean = 5 * 60.0	* factor	# Average lap time.
	varFactor = 9.0
	var = mean/varFactor		# Variance between riders.
	
	lapTimes = []
	for num in xrange(numStart,numStart+riders):
		mu = random.normalvariate( mean, mean/(varFactor * 4.0) )			# Rider's random average lap time.
		t = offset
		lap = 0
		while t < raceTime * 2:
			lap += 1
			t += random.normalvariate( mu, var/2 )	# Rider's lap time.
			if random.random() > errorRate:			# Respect error rate.
				lapTimes.append( (num, t, lap) )
	
	return lapTimes

def Simulate():
	# Generate all the random rider events.
	random.seed( 0xeded )

	raceTime = 50.0 * 60.0
	
	wbProb = pyXL.Workbook()
	wbSol = pyXL.Workbook()
	for p in xrange(8):
		numCategories = 3
		numRiders = 20
		if p >= 5:
			numRiders = 25
		lapTimes = []
		for i in xrange(1, numCategories + 1):
			lapTimes.extend( SimulateCategory(i * 100, numRiders, 1.0 + i * 0.05, raceTime = raceTime, offset = (60.0 * (i-1)) ) )
			
		lapTimes.sort( key = lambda x : (x[1], -x[2]) )
		
		raceLaps = raceTime / (5*60.0)
		
		finish = []
		sheet = wbProb.add_sheet( 'Problem %d' % (p + 1) )
		rowStart = 3
		col = 0
		row = rowStart
		seen = set()
		sheet.write( 0, 0, 'Problem %d' % (p + 1) )
		sheet.write( 1, 0, 'Lap 1' )
		for num, t, lap in lapTimes:
			if num in seen:
				if col == raceLaps:
					continue
				finish = []
				col += 1
				row = rowStart
				seen = set()
				sheet.write( 1, col, 'Lap %d' % (col + 1) )
				
			sheet.write( row, col, num )
			finish.append( (num, t, lap) )
			row += 1
			seen.add( num )
		
		# Sort by laps, then time.
		finish.sort( key = lambda x : (-x[2], x[1]) )
		
		col = 0
		sheet = wbSol.add_sheet( 'Solution %d' % (p + 1) )
		sheet.write( 0, 0, 'Solution %d' % (p + 1) )
		for i in xrange(1, numCategories + 1):
			sheet.write( 1, col+1, "%d's" % (i * 100) )
			sheet.write( 1, col+2, "Laps" )
			row = rowStart
			for num, t, lap in (e for e in finish if i*100 <= e[0] < (i+1)*100 ):
				sheet.write( row, col, row - rowStart + 1 )
				sheet.write( row, col+1, num )
				sheet.write( row, col+2, lap )
				row += 1
			col += 4
	
	wbProb.save( 'CrossProblems.xls' )
	wbSol.save( 'CrossSolutions.xls' )

if __name__ == '__main__':
	Simulate()
