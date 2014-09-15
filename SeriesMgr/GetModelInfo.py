
import os
import cPickle as pickle
import datetime
from collections import defaultdict

import Model
import GpxParse
import GeoAnimation
import Animation
import GanttChart
import ReadSignOnSheet
import SeriesModel
import Utils
from ReadSignOnSheet	import GetExcelLink, ResetExcelLinkCache, HasExcelLink
from GetResults			import GetResults, GetCategoryDetails

class RaceResult( object ):
	def __init__( self, firstName, lastName, license, team, categoryName, raceName, raceDate, raceFileName, bib, rank, raceOrganizer,
					raceURL = None, raceInSeries = None, tFinish = None ):
		self.firstName = (firstName or u'')
		self.lastName = (lastName or u'')
		self.license = (license or u'')
		self.team = (team or u'')
		
		self.categoryName = (categoryName or u'')
		
		self.raceName = raceName
		self.raceDate = raceDate
		self.raceOrganizer = raceOrganizer
		self.raceFileName = raceFileName
		self.raceURL = raceURL
		self.raceInSeries = raceInSeries
		
		self.bib = bib
		self.rank = rank
		
		self.tFinish = tFinish
		
	def keySort( self ):
		fields = ['categoryName', 'lastName', 'firstName', 'license', 'raceDate', 'raceName']
		return tuple( getattr(self, a) for a in fields )
		
	def keyMatch( self ):
		fields = ['categoryName', 'lastName', 'firstName', 'license']
		return tuple( getattr(self, a) for a in fields )
		
	@property
	def full_name( self ):
		return u', '.join( [name for name in [self.lastName.upper(), self.firstName] if name] )

def ExtractRaceResults( r ):
	if os.path.splitext(r.fileName)[1] == '.cmn':
		return ExtractRaceResultsCrossMgr( r )
	else:
		return ExtractRaceResultsExcel( r )

def toInt( n ):
	try:
		return int(n.split()[0])
	except:
		return n

def ExtractRaceResultsExcel( raceInSeries ):
	excelLink = raceInSeries.excelLink
	if not excelLink:
		return False, 'Missing Excel Link Definition', []

	try:
		data = excelLink.read()
	except Exception as e:
		return False, e, []
	
	raceFileName =  u'{}:{}'.format( excelLink.fileName, excelLink.sheetName )
	raceName = u'{}:{}'.format(	os.path.basename(os.path.splitext(excelLink.fileName)[0]), excelLink.sheetName )
	raceResults = []
	for d in data:
		info = {'raceDate':		None,
				'raceFileName':	raceFileName,
				'raceName':		raceName,
				'raceOrganizer': '',
				'raceInSeries': raceInSeries,
		}
		for fTo, fFrom in [
				('bib', 'Bib#'),
				('rank', 'Pos'), ('tFinish', 'Time'),
				('firstName', 'FirstName'), ('lastName', 'LastName'), ('license', 'License'),
				('team', 'Team'), ('categoryName', 'Category')]:
			info[fTo] = d.get( fFrom, u'' )
		
		if not info['categoryName']:
			continue
		
		try:
			info['rank'] = toInt(info['rank'])
		except ValueError:
			continue
		
		try:
			info['bib'] = int(info['bib'])
		except ValueError:
			pass
		
		info['tFinish'] = (info['tFinish'] or 0.0)
		if isinstance( info['tFinish'], basestring ) and ':' in info['tFinish']:
			info['tFinish'] = Utils.StrToSeconds( info['tFinish'] )
		else:
			try:
				info['tFinish'] = float( info['tFinish'] ) * 24.0 * 60.0 * 60.0	# Convert Excel day number to seconds.
			except Exception as e:
				info['tFinish'] = 0.0
		
		raceResults.append( RaceResult(**info) )
	
	return True, 'success', raceResults

def ExtractRaceResultsCrossMgr( raceInSeries ):
	fileName = raceInSeries.fileName
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
	
	race = Model.race
	if not HasExcelLink(race):	# Force a refresh of the Excel link before reading the categories.
		pass
		
	raceURL = getattr( race, 'urlFull', None )
	raceResults = []
	for category in race.getCategories( startWaveOnly=False ):
		if not category.seriesFlag:
			continue
		
		results = GetResults( category, True )
		
		for rr in results:
			if rr.status != Model.Rider.Finisher:
				continue
			info = {
				'raceURL':		raceURL,
				'raceInSeries':	raceInSeries,
			}
			for fTo, fFrom in [('firstName', 'FirstName'), ('lastName', 'LastName'), ('license', 'License'), ('team', 'Team')]:
				info[fTo] = getattr(rr, fFrom, '')
			info['categoryName'] = category.fullname
			
			for fTo, fFrom in [('raceName', 'name'), ('raceOrganizer', 'organizer')]:
				info[fTo] = getattr(race, fFrom, '')
			info['raceFileName'] = fileName
			if race.startTime:
				info['raceDate'] = race.startTime
			else:
				try:
					d = race.date.replace('-', ' ').replace('/', ' ')
					fields = [int(v) for v in d.split()] + [int(v) for v in race.scheduledStart.split(':')]
					info['raceDate'] = datetime.datetime( *fields )
				except:
					info['raceDate'] = None
			
			info['bib'] = int(rr.num)
			info['rank'] = toInt(rr.pos)
			info['tFinish'] = rr.lastTime
			raceResults.append( RaceResult(**info) )
		
	Model.race = None
	return True, 'success', raceResults
	
def GetCategoryResults( categoryName, raceResults, pointsForRank, useMostEventsCompleted=False, numPlacesTieBreaker=5 ):
	scoreByTime = SeriesModel.model.scoreByTime
	
	# Get all results for this category.
	raceResults = [rr for rr in raceResults if rr.categoryName == categoryName]
	if not raceResults:
		return [], []
	
	# Assign a sequence number to the races in the specified order.
	for i, r in enumerate(SeriesModel.model.races):
		r.iSequence = i
		
	# Get all races for this category.
	races = set( (rr.raceDate, rr.raceName, rr.raceURL, rr.raceInSeries) for rr in raceResults )
	races = sorted( races, key = lambda r: r[3].iSequence )
	raceSequence = dict( (r[3], i) for i, r in enumerate(races) )
	
	riderEventsCompleted = defaultdict( int )
	riderPlaceCount = defaultdict( lambda : defaultdict(int) )
	riderTeam = defaultdict( lambda : u'' )
	
	if scoreByTime:
		# Get the individual results for each rider, and the total points.
		riderResults = defaultdict( lambda : [(0,0)] * len(races) )
		riderTFinish = defaultdict( float )
		for rr in raceResults:
			try:
				tFinish = float(rr.tFinish)
			except ValueError:
				continue
			rider = (rr.full_name, rr.license)
			if rr.team and rr.team != u'0':
				riderTeam[rider] = rr.team
			riderResults[rider][raceSequence[rr.raceInSeries]] = (Utils.formatTime(tFinish, True), rr.rank)
			riderTFinish[rider] += tFinish
			riderPlaceCount[rider][rr.rank] += 1
			riderEventsCompleted[rider] += 1

		# Sort by decreasing events completed, then increasing rider time.
		riderOrder = [rider for rider, results in riderResults.iteritems()]
		riderOrder.sort( key = lambda r: (-riderEventsCompleted[r], riderTFinish[r]) )
		
		# List of:
		# lastName, firstName, license, team, tTotalFinish, [list of (points, position) for each race in series]
		categoryResult = [list(rider) + [riderTeam[rider], Utils.formatTime(riderTFinish[rider], True)] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races
	else:
		# Get the individual results for each rider, and the total points.
		riderResults = defaultdict( lambda : [(0,0)] * len(races) )
		riderPoints = defaultdict( int )
		for rr in raceResults:
			rider = (rr.full_name, rr.license)
			if rr.team and rr.team != u'0':
				riderTeam[rider] = rr.team
			points = pointsForRank[rr.raceFileName][rr.rank]
			riderResults[rider][raceSequence[rr.raceInSeries]] = (points, rr.rank)
			riderPoints[rider] += points
			riderPlaceCount[rider][rr.rank] += 1
			riderEventsCompleted[rider] += 1

		# Sort by rider points - greatest number of points first.  Break ties with place count, then
		# most recent result.
		riderOrder = [rider for rider, results in riderResults.iteritems()]
		riderOrder.sort(key = lambda r:	[riderPoints[r]] +
										([riderEventsCompleted[r]] if useMostEventsCompleted else []) +
										[riderPlaceCount[r][k] for k in xrange(1, numPlacesTieBreaker+1)] +
										[-rank for points, rank in reversed(riderResults[r])],
						reverse = True )
		
		# List of:
		# lastName, firstName, license, team, points, [list of (points, position) for each race in series]
		categoryResult = [list(rider) + [riderTeam[rider], riderPoints[rider]] + [riderResults[rider]] for rider in riderOrder]
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
	
