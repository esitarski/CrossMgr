
import Model
import Utils
import cPickle as pickle
from collections import defaultdict
from ReadSignOnSheet	import GetExcelLink, ResetExcelLinkCache
from GetResults			import GetResults, GetCategoryDetails

class RaceResult( object ):
	def __init__( self, firstName, lastName, license, team, categoryName, raceName, raceDate, raceOrganizer, bib, rank ):
		self.firstName = firstName
		self.lastName = lastName
		self.license = license
		self.team = team
		self.categoryName = categoryName
		self.raceName = raceName
		self.raceDate = raceDate
		self.raceOrganizer = raceOrganizer
		self.bib = bib
		self.rank = rank
		
	def keySort( self ):
		fields = ['categoryName', 'lastName', 'firstName', 'license', 'raceDate', 'raceName']
		return tuple( getattr(self, a) for a in fields )
		
	def keyMatch( self ):
		fields = ['categoryName', 'lastName', 'firstName', 'license']
		return tuple( getattr(self, a) for a in fields )

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
			info['raceName'] = race.name
			info['raceDate'] = race.date
			info['raceOrganizer'] = race.organizer
			info['bib'] = int(rr.num)
			info['rank'] = int(rr.pos)
			raceResults.append( RaceResult(**info) )
		
	Model.race = None
	return True, '', raceResults
	
def GetCategoryResults( categoryName, raceResults, pointsForRank ):
	mostPointsFirst = (pointsForRank[1] > pointsForRank[2])

	# Get all results for this category.
	raceResults = [rr for rr in raceResults if rr.categoryName == categoryName]
	
	# Get all races for this category.
	races = set( (rr.raceDate, rr.raceName) for rr in raceResults )
	races = sorted( races )
	raceSequence = dict( (r, i) for i, r in enumerate(races) )
	
	# Get the individual results for each rider, and the total points.
	riderResults = defaultdict( lambda : [(0,0)] * len(races) )
	riderPoints = defaultdict( int )
	for rr in raceResults:
		rider = (rr.lastName, rr.firstName, rr.license)
		points = pointsForRank[rr.rank]
		riderResults[rider][raceSequence[(rr.raceDate, rr.raceName)]] = (points, rr.rank)
		riderPoints[rider] += points

	# If not most points first, remove any riders that did not participate in all races.
	if not mostPointsFirst:
		toDelete = set()
		for rr in raceResults:
			if (0, 0) in riderResults:
				toDelete.add( tt )
		for rr in toDelete:
			del raceResults[rr]
		
	# Sort by rider points - greatest number of points first.  Break ties with most recent results.
	riderOrder = [rider for rider, results in riderResults.iteritems()]
	riderOrder.sort( key = lambda r: [riderPoints[r]] + riderResults[r][::-1], reverse = mostPointsFirst )
	
	# List of:
	# lastName, firstName, license, points, [list of (points, position) for each race]
	categoryResult = [list(rider) + [riderPoints[rider]] + [riderResults[rider]] for rider in riderOrder]
	return categoryResult, races
	
	
if __name__ == '__main__':
	files = [
		r'D:\Projects\CrossMgr\RacoonRally\2013-06-30-2013 Raccoon Rally Mountain Bike Race-r1-.cmn',
	]
	raceResults = []
	for f in files:
		status, err, rr = ExtractRaceResults( f )
		if not status:
			continue
		raceResults.extend( rr )
	
	categories = set( rr.categoryName for rr in raceResults )
	categories = sorted( categories )
	for c in categories:
		print c
		
	pointsForRank = defaultdict( int )
	for i in xrange(25):
		pointsForRank[i] = 26 - i
		
	for c in categories:
		categoryResult, races = GetCategoryResults( c, raceResults, pointsForRank )
		for rr in categoryResult:
			print rr[0], rr[1], rr[2], rr[3], rr[4]
	#print raceResults
	