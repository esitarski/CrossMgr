
import os
import math
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

def formatTime( secs, highPrecision = False ):
	if secs is None:
		secs = 0
	if secs < 0:
		sign = '-'
		secs = -secs
	else:
		sign = ''
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = int(secs // (60*60))
	minutes = int( (secs // 60) % 60 )
	secs = secs % 60
	if highPrecision:
		secStr = '{:05.2f}'.format( secs + f )
	else:
		secStr = '{:02d}'.format( secs )
	
	if hours > 0:
		return "{}{}:{:02d}:{}".format(sign, hours, minutes, secStr)
	if minutes > 0:
		return "{}{}:{}".format(sign, minutes, secStr)
	return "{}{}".format(sign, secStr)
	
def formatTimeGap( secs, highPrecision = False ):
	if secs is None:
		secs = 0
	if secs < 0:
		sign = '-'
		secs = -secs
	else:
		sign = ''
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = int(secs // (60*60))
	minutes = int( (secs // 60) % 60 )
	secs = secs % 60
	if highPrecision:
		decimal = '.%02d' % int( f * 100 )
	else:
		decimal = ''
	if hours > 0:
		return "%s%dh%d'%02d%s\"" % (sign, hours, minutes, secs, decimal)
	else:
		return "%s%d'%02d%s\"" % (sign, minutes, secs, decimal)

class RaceResult( object ):
	def __init__( self, firstName, lastName, license, team, categoryName, raceName, raceDate, raceFileName, bib, rank, raceOrganizer,
					raceURL = None, raceInSeries = None, tFinish = None, tProjected = None ):
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
		self.tProjected = tProjected if tProjected else tFinish
		
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
		
	if race.licenseLinkTemplate:
		SeriesModel.model.licenseLinkTemplate = race.licenseLinkTemplate
		
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
			
			raceNum = getattr(race, 'raceNum', '')
			if raceNum:
				info['raceName'] = u'{}-{}'.format(info['raceName'], raceNum)
				
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
			try:
				info['rank'] = toInt(rr.pos)
			except Exception as e:
				info['rank'] = 999999
				
			try:
				info['tFinish'] = rr.lastTime
			except Exception as e:
				info['tFinish'] = 1000.0*24.0*60.0*60.0
				
			try:
				info['tProjected'] = rr.projectedTime
			except AttributeError:
				info['tProjected'] = rr.lastTime
			raceResults.append( RaceResult(**info) )
		
	Model.race = None
	return True, 'success', raceResults
	
def GetCategoryResults( categoryName, raceResults, pointsForRank, useMostEventsCompleted=False, numPlacesTieBreaker=5 ):
	scoreByTime = SeriesModel.model.scoreByTime
	scoreByPercent = SeriesModel.model.scoreByPercent
	bestResultsToConsider = SeriesModel.model.bestResultsToConsider
	mustHaveCompleted = SeriesModel.model.mustHaveCompleted
	
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
	
	ignoreFormat = u'[{}**]'
	
	if scoreByTime:
		# Get the individual results for each rider, and the total time.
		riderResults = defaultdict( lambda : [(0,0)] * len(races) )
		riderFinishes = defaultdict( lambda : [None] * len(races) )
		riderTFinish = defaultdict( float )
		for rr in raceResults:
			try:
				tFinish = float(rr.tFinish)
			except ValueError:
				continue
			rider = (rr.full_name, rr.license)
			if rr.team and rr.team != u'0':
				riderTeam[rider] = rr.team
			riderResults[rider][raceSequence[rr.raceInSeries]] = (formatTime(tFinish, True), rr.rank)
			riderFinishes[rider][raceSequence[rr.raceInSeries]] = tFinish
			riderTFinish[rider] += tFinish
			riderPlaceCount[rider][rr.rank] += 1
			riderEventsCompleted[rider] += 1

		# Adjust for the best scores.
		if bestResultsToConsider > 0:
			for rider, finishes in riderFinishes.iteritems():
				times = [t for t in finishes if t is not None]
				if len(times) > bestResultsToConsider:
					times.sort()
					riderTFinish[rider] -= sum(times[bestResultsToConsider:])
					tBest = times[bestResultsToConsider-1]
					count = 0
					for r, t in enumerate(finishes):
						if t is None:
							continue
						if t <= tBest and count < bestResultsToConsider:
							count += 1
						else:
							v = riderResults[rider][r]
							riderResults[rider][r] = (ignoreFormat.format(v[0]), v[1])

		# Filter out minimal events completed.
		riderOrder = [rider for rider, results in riderResults.iteritems() if riderEventsCompleted[rider] >= mustHaveCompleted]
		
		# Sort by decreasing events completed, then increasing rider time.
		riderOrder.sort( key = lambda r: (-riderEventsCompleted[r], riderTFinish[r]) )
		
		# Compute the time gap.
		riderGap = {}
		if riderOrder:
			leader = riderOrder[0]
			leaderTFinish = riderTFinish[leader]
			leaderEventsCompleted = riderEventsCompleted[leader]
			riderGap = { r : riderTFinish[r] - leaderTFinish if riderEventsCompleted[r] == leaderEventsCompleted else None for r in riderOrder }
			riderGap = { r : formatTimeGap(gap) if gap else u'' for r, gap in riderGap.iteritems() }
		
		# List of:
		# lastName, firstName, license, team, tTotalFinish, [list of (points, position) for each race in series]
		categoryResult = [list(rider) + [riderTeam[rider], formatTime(riderTFinish[rider],True), riderGap[rider]] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races
	
	elif scoreByPercent:
		# Get the individual results for each rider, and the total points.
		percentFormat = u'{:.2f}'
		riderResults = defaultdict( lambda : [(0,0)] * len(races) )
		riderFinishes = defaultdict( lambda : [None] * len(races) )
		riderPercentTotal = defaultdict( float )
		
		raceLeader = { rr.raceInSeries: rr for rr in raceResults if rr.rank == 1 }
		
		for rr in raceResults:
			tFastest = raceLeader[rr.raceInSeries].tProjected
			
			try:
				tFinish = rr.tProjected
			except ValueError:
				continue
			rider = (rr.full_name, rr.license)
			if rr.team and rr.team != u'0':
				riderTeam[rider] = rr.team
			percent = min( 100.0, (tFastest / tFinish) * 100.0 if tFinish > 0.0 else 0.0 )
			riderResults[rider][raceSequence[rr.raceInSeries]] = (u'{}, {}'.format(percentFormat.format(percent), formatTime(tFinish, False)), rr.rank)
			riderFinishes[rider][raceSequence[rr.raceInSeries]] = percent
			riderPercentTotal[rider] += percent
			riderPlaceCount[rider][rr.rank] += 1
			riderEventsCompleted[rider] += 1

		# Adjust for the best scores.
		if bestResultsToConsider > 0:
			for rider, finishes in riderFinishes.iteritems():
				percents = [p for p in finishes if p is not None]
				if len(percents) > bestResultsToConsider:
					percents.sort( reverse=True )
					riderPercentTotal[rider] -= sum(percents[bestResultsToConsider:])
					pBest = percents[bestResultsToConsider-1]
					count = 0
					for r, p in enumerate(finishes):
						if p is None:
							continue
						if p >= pBest and count < bestResultsToConsider:
							count += 1
						else:
							v = riderResults[rider][r]
							riderResults[rider][r] = (ignoreFormat.format(v[0]), v[1])

		# Filter out minimal events completed.
		riderOrder = [rider for rider, results in riderResults.iteritems() if riderEventsCompleted[rider] >= mustHaveCompleted]
		
		# Sort by decreasing percent total.
		riderOrder.sort( key = lambda r: -riderPercentTotal[r] )
		
		# Compute the points gap.
		riderGap = {}
		if riderOrder:
			leader = riderOrder[0]
			leaderPercentTotal = riderPercentTotal[leader]
			riderGap = { r : leaderPercentTotal - riderPercentTotal[r] for r in riderOrder }
			riderGap = { r : percentFormat.format(gap) if gap else u'' for r, gap in riderGap.iteritems() }
					
		# List of:
		# lastName, firstName, license, team, totalPercent, [list of (percent, position) for each race in series]
		categoryResult = [list(rider) + [riderTeam[rider], percentFormat.format(riderPercentTotal[rider]), riderGap[rider]] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races
		
	else:
		# Get the individual results for each rider, and the total points.
		riderResults = defaultdict( lambda : [(0,0)] * len(races) )
		riderFinishes = defaultdict( lambda : [None] * len(races) )
		riderPoints = defaultdict( int )
		for rr in raceResults:
			rider = (rr.full_name, rr.license)
			if rr.team and rr.team != u'0':
				riderTeam[rider] = rr.team
			points = pointsForRank[rr.raceFileName][rr.rank]
			riderResults[rider][raceSequence[rr.raceInSeries]] = (points, rr.rank)
			riderFinishes[rider][raceSequence[rr.raceInSeries]] = points
			riderPoints[rider] += points
			riderPlaceCount[rider][rr.rank] += 1
			riderEventsCompleted[rider] += 1

		# Adjust for the best scores.
		if bestResultsToConsider > 0:
			for rider, finishes in riderFinishes.iteritems():
				points = [p for p in finishes if p is not None]
				if len(points) > bestResultsToConsider:
					points.sort( reverse=True )
					riderPoints[rider] -= sum(points[bestResultsToConsider:])
					pBest = points[bestResultsToConsider-1]
					count = 0
					for r, p in enumerate(finishes):
						if p is None:
							continue
						if p >= pBest and count < bestResultsToConsider:
							count += 1
						else:
							v = riderResults[rider][r]
							riderResults[rider][r] = (ignoreFormat.format(v[0]), v[1])

		# Filter out minimal events completed.
		riderOrder = [rider for rider, results in riderResults.iteritems() if riderEventsCompleted[rider] >= mustHaveCompleted]
		
		# Sort by rider points - greatest number of points first.  Break ties with place count, then
		# most recent result.
		riderOrder.sort(key = lambda r:	[riderPoints[r]] +
										([riderEventsCompleted[r]] if useMostEventsCompleted else []) +
										[riderPlaceCount[r][k] for k in xrange(1, numPlacesTieBreaker+1)] +
										[-rank for points, rank in reversed(riderResults[r])],
						reverse = True )
		
		# Compute the points gap.
		riderGap = {}
		if riderOrder:
			leader = riderOrder[0]
			leaderPoints = riderPoints[leader]
			riderGap = { r : leaderPoints - riderPoints[r] for r in riderOrder }
			riderGap = { r : unicode(gap) if gap else u'' for r, gap in riderGap.iteritems() }
		
		# List of:
		# lastName, firstName, license, team, points, [list of (points, position) for each race in series]
		categoryResult = [list(rider) + [riderTeam[rider], riderPoints[rider], riderGap[rider]] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races

def GetTotalUniqueParticipants( raceResults ):
	return len( set( (rr.full_name, rr.license) for rr in raceResults ) )
		
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
	
