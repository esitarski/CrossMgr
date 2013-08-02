
import Model
import SeriesModel
import Utils
import cPickle as pickle
import datetime
from collections import defaultdict
from ReadSignOnSheet	import GetExcelLink, ResetExcelLinkCache
from GetResults			import GetResults, GetCategoryDetails

class RaceResult( object ):
	def __init__( self, firstName, lastName, license, team, categoryName, raceName, raceDate, raceOrganizer, raceFName, bib, rank ):
		self.firstName = firstName
		self.lastName = lastName
		self.license = license
		self.team = team
		
		self.categoryName = categoryName
		
		self.raceName = raceName
		self.raceDate = raceDate
		self.raceOrganizer = raceOrganizer
		self.raceFName = raceFName
		
		self.bib = bib
		self.rank = rank
		
	def keySort( self ):
		fields = ['categoryName', 'lastName', 'firstName', 'license', 'raceDate', 'raceName']
		return tuple( getattr(self, a) for a in fields )
		
	def keyMatch( self ):
		fields = ['categoryName', 'lastName', 'firstName', 'license']
		return tuple( getattr(self, a) for a in fields )
		
	@property
	def full_name( self ):
		if self.lastName and self.firstName:
			return ', '.join( self.lastName.upper(), self.firstName )
		if self.lastName:
			return self.lastName.upper()
		return self.firstName

def ExtractRaceResults( fileName ):
	try:
		with open(fileName, 'rb') as fp, Model.LockRace() as race:
			race = pickle.load( fp )
			isFinished = race.isFinished()
			race.tagNums = None
			race.resetAllCaches()
			Model.setRace( race )
		
		ResetExcelLinkCache()
		Model.resetCache()

	except IOError as e:
		return False, e, []
		
	raceResults = []
	for category in race.getCategories():
		results = GetResults( category, True )
		for rr in results:
			if rr.status != Model.Rider.Finisher:
				continue
			info = {}
			for fTo, fFrom in [('firstName', 'FirstName'), ('lastName', 'LastName'), ('license', 'License'), ('team', 'Team')]:
				info[fTo] = getattr(rr, fFrom, '')
			info['categoryName'] = category.fullname
			
			for fTo, fFrom in [('raceName', 'name'), ('raceOrganizer', 'organizer')]:
				info[fTo] = getattr(race, fFrom, '')
			info['raceFName'] = fileName
			if race.startTime:
				info['raceDate'] = race.startTime
			else:
				try:
					d = race.date.replace('-', ' ').replace('/', ' ')
					fields = [int(v) for v in d.split()] + [int(v) for v in race.scheduledStart.split(':')]
					info['raceDate'] = datetime.datetime( *fields )
				except:
					info['raceDate'] = datetime.datetime.now()
			
			info['bib'] = int(rr.num)
			info['rank'] = int(rr.pos)
			raceResults.append( RaceResult(**info) )
		
	Model.race = None
	return True, 'success', raceResults
	
def GetCategoryResults( categoryName, raceResults, pointsForRank, numPlacesTieBreaker = 5 ):
	# Get all results for this category.
	raceResults = [rr for rr in raceResults if rr.categoryName == categoryName]
	if not raceResults:
		return [], []
	
	# Get all races for this category.
	races = set( (rr.raceDate, rr.raceName) for rr in raceResults )
	races = sorted( races )
	raceSequence = dict( (r, i) for i, r in enumerate(races) )
	
	# Get the individual results for each rider, and the total points.
	riderResults = defaultdict( lambda : [(0,0)] * len(races) )
	riderPoints = defaultdict( int )
	riderPlaceCount = defaultdict( lambda : defaultdict(int) )
	for rr in raceResults:
		rider = (rr.lastName, rr.firstName, rr.license)
		points = pointsForRank[rr.raceFName][rr.rank]
		riderResults[rider][raceSequence[(rr.raceDate, rr.raceName)]] = (points, rr.rank)
		riderPoints[rider] += points
		riderPlaceCount[rider][rr.rank] += 1

	# Sort by rider points - greatest number of points first.  Break ties with place count, then
	# most recent result.
	riderOrder = [rider for rider, results in riderResults.iteritems()]
	riderOrder.sort( key = lambda r:	[riderPoints[r]] +
										[riderPlaceCount[r][k] for k in xrange(1, numPlacesTieBreaker+1)] +
										[-rank for points, rank in reversed(riderResults[r])], reverse = True )
	
	# List of:
	# lastName, firstName, license, points, [list of (points, position) for each race in series]
	categoryResult = [list(rider) + [riderPoints[rider]] + [riderResults[rider]] for rider in riderOrder]
	return categoryResult, races

if __name__ == '__main__':
	files = [
		r'C:\Projects\CrossMgr\RacoonRally\2013-06-30-2013 Raccoon Rally Mountain Bike Race-r1-.cmn',
	]
	raceResults = []
	for f in files:
		status, err, rr = ExtractRaceResults( f )
		if not status:
			continue
		raceResults.extend( rr )
	
	categories = set( rr.categoryName for rr in raceResults )
	categories = sorted( categories )
		
	pointsForRank = defaultdict( int )
	for i in xrange(250):
		pointsForRank[i+1] = 250 - i
		
	pointsForRank = { files[0]: pointsForRank }
		
	for c in categories:
		categoryResult, races = GetCategoryResults( c, raceResults, pointsForRank )
		print '--------------------------------------------------------'
		print c
		print
		for rr in categoryResult:
			print rr[0], rr[1], rr[2], rr[3], rr[4]
		print races
	#print raceResults
	