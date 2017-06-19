import os
import math
import cPickle as pickle
import datetime
import operator
from collections import defaultdict

import trueskill

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
from Excel				import GetExcelReader
from FieldMap			import standard_field_map, standard_field_aliases

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

def safe_upper( f ):
	try:
		return f.upper()
	except:
		return f

class RaceResult( object ):
	rankDNF = 999999
	
	def __init__( self, firstName, lastName, license, team, categoryName, raceName, raceDate, raceFileName, bib, rank, raceOrganizer,
					raceURL=None, raceInSeries=None, tFinish=None, tProjected=None, primePoints=0, timeBonus=0, laps=1 ):
		self.firstName = unicode(firstName or u'')
		self.lastName = unicode(lastName or u'')
		
		self.license = (license or u'')
		if isinstance(self.license, float) and int(self.license) == self.license:
			self.license = int(self.license)
		self.license = unicode(self.license)
		
		self.team = unicode(team or u'')
		
		self.categoryName = unicode(categoryName or u'')
		
		self.raceName = unicode(raceName)
		self.raceDate = raceDate
		self.raceOrganizer = raceOrganizer
		self.raceFileName = raceFileName
		self.raceURL = raceURL
		self.raceInSeries = raceInSeries
		
		self.bib = bib
		self.rank = rank
		self.primePoints = primePoints
		self.timeBonus = timeBonus
		self.laps = laps
		
		self.tFinish = tFinish
		self.tProjected = tProjected if tProjected else tFinish
		
		self.upgradeFactor = 1
		self.upgradeResult = False
			
	def keySort( self ):
		fields = ['categoryName', 'lastName', 'firstName', 'license', 'raceDate', 'raceName']
		return tuple( safe_upper(getattr(self, a)) for a in fields )
		
	def keyMatch( self ):
		fields = ['categoryName', 'lastName', 'firstName', 'license']
		return tuple( safe_upper(getattr(self, a)) for a in fields )
		
	def key( self ):
		return (Utils.removeDiacritic(self.full_name.upper()), Utils.removeDiacritic(self.license))
		
	@property
	def full_name( self ):
		return u', '.join( [name for name in [self.lastName.upper(), self.firstName] if name] )
		
	def __unicode__( self ):
		return u', '.join( u'{}'.format(p) for p in [self.full_name, self.license, self.categoryName, self.raceName, self.raceDate] if p )

def ExtractRaceResults( r ):
	if os.path.splitext(r.fileName)[1] == '.cmn':
		return ExtractRaceResultsCrossMgr( r )
	else:
		return ExtractRaceResultsExcel( r )

def toInt( n ):
	if n == 'DNF':
		return RaceResult.rankDNF
	try:
		return int(n.split()[0])
	except:
		return n

def ExtractRaceResultsExcel( raceInSeries ):
	getReferenceName = SeriesModel.model.getReferenceName
	getReferenceLicense = SeriesModel.model.getReferenceLicense
	
	excel = GetExcelReader( raceInSeries.fileName )
	raceName = os.path.splitext(os.path.basename(raceInSeries.fileName))[0]
	raceResults = []
	
	# Search for a "Pos" field to indicate the start of the data.
	for sfa in standard_field_aliases:
		if sfa[0] == 'pos':
			posHeader = set( a.lower() for a in sfa[1] )
			break
	for sheetName in excel.sheet_names():
		fm = None
		categoryNameSheet = sheetName.strip()
		for row in excel.iter_list(sheetName):
			if fm:
				f = fm.finder( row )
				info = {
					'raceDate':		None,
					'raceFileName':	raceInSeries.fileName,
					'raceName':		raceName,
					'raceOrganizer': u'',
					'raceInSeries': raceInSeries,					
					'bib': 			f('bib',99999),
					'rank':			f('pos',''),
					'tFinish':		f('time',0.0),
					'firstName':	unicode(f('first_name',u'')).strip(),
					'lastName'	:	unicode(f('last_name',u'')).strip(),
					'license':		unicode(f('license_code',u'')).strip(),
					'team':			unicode(f('team',u'')).strip(),
					'categoryName': f('category_code',None),
					'laps':			f('laps',1),
				}
				
				info['rank'] = unicode(info['rank']).strip()
				if not info['rank']:	# If missing rank, assume end of input.
					break
				
				if info['categoryName'] is None:
					info['categoryName'] = categoryNameSheet
				info['categoryName'] = unicode(info['categoryName']).strip()
				
				try:
					info['rank'] = toInt(info['rank'])
				except ValueError:
					pass
					
				if not isinstance(info['rank'], (long,int)):
					continue

				# Check for comma-separated name.
				name = unicode(f('name', u'')).strip()
				if name and not info['firstName'] and not info['lastName']:
					try:
						info['lastName'], info['firstName'] = name.split(',',1)
					except:
						pass
				
				if not info['firstName'] and not info['lastName']:
					continue
				
				info['lastName'], info['firstName'] = getReferenceName(info['lastName'], info['firstName'])
				info['license'] = getReferenceLicense(info['license'])
				
				# If there is a bib it must be numeric.
				try:
					info['bib'] = int(unicode(info['bib']).strip())
				except ValueError:
					continue
					
				info['tFinish'] = (info['tFinish'] or 0.0)
				if isinstance(info['tFinish'], basestring) and ':' in info['tFinish']:
					info['tFinish'] = Utils.StrToSeconds( info['tFinish'].strip() )
				else:
					try:
						info['tFinish'] = float( info['tFinish'] ) * 24.0 * 60.0 * 60.0	# Convert Excel day number to seconds.
					except Exception as e:
						info['tFinish'] = 0.0
				
				raceResults.append( RaceResult(**info) )
				
			elif any( unicode(r).strip().lower() in posHeader for r in row ):
				fm = standard_field_map()
				fm.set_headers( row )

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
	
	getReferenceName = SeriesModel.model.getReferenceName
	getReferenceLicense = SeriesModel.model.getReferenceLicense
	
	Finisher = Model.Rider.Finisher
	DNF = Model.Rider.DNF
	acceptedStatus = { Finisher, DNF }
	raceURL = getattr( race, 'urlFull', None )
	
	racePrimes = getattr( race, 'primes', None )
	primePoints = defaultdict( int )
	timeBonus = defaultdict( float )
	if racePrimes:
		for p in racePrimes:
			primePoints[p['winnerBib']] += p.get('points', 0)
			timeBonus[p['winnerBib']] += p.get('timeBonus', 0.0)
	
	raceResults = []
	for category in race.getCategories( startWaveOnly=False ):
		if not category.seriesFlag:
			continue
		
		results = GetResults( category )
		
		for pos, rr in enumerate(results,1):
			if rr.status not in acceptedStatus:
				continue
			info = {
				'raceURL':		raceURL,
				'raceInSeries':	raceInSeries,
			}
			for fTo, fFrom in [('firstName', 'FirstName'), ('lastName', 'LastName'), ('license', 'License'), ('team', 'Team')]:
				info[fTo] = getattr(rr, fFrom, '')
				
			if not info['firstName'] and not info['lastName']:
				continue				

			info['categoryName'] = category.fullname
			info['lastName'], info['firstName'] = getReferenceName(info['lastName'], info['firstName'])
			info['license'] = getReferenceLicense(info['license'])
			info['laps'] = rr.laps
			
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
			info['rank'] = RaceResult.rankDNF if rr.status == DNF else pos
				
			info['tFinish'] = getattr(rr, '_lastTimeOrig', None) or getattr(rr,'lastTime', 1000.0*24.0*60.0*60.0)
			
			try:
				info['tProjected'] = rr.projectedTime
			except AttributeError:
				info['tProjected'] = rr.lastTime
				
			info['primePoints'] = primePoints.get(rr.num, 0)
			info['timeBonus'] = timeBonus.get(rr.num, 0.0)
			
			raceResults.append( RaceResult(**info) )
		
	Model.race = None
	return True, 'success', raceResults

def AdjustForUpgrades( raceResults ):
	upgradePaths = []
	for path in SeriesModel.model.upgradePaths:
		upgradePaths.append( [p.strip() for p in path.split(',')] )
	upgradeFactors = SeriesModel.model.upgradeFactors
	
	competitionCategories = defaultdict( lambda: defaultdict(list) )
	for rr in raceResults:
		competitionCategories[rr.key()][rr.categoryName].append( rr )
	
	for key, categories in competitionCategories.iteritems():
		if len(categories) == 1:
			continue
		
		for i, path in enumerate(upgradePaths):
			upgradeCategories = { cName: rrs for cName, rrs in categories.iteritems() if cName in path }
			if len(upgradeCategories) <= 1:
				continue
			
			try:
				upgradeFactor = upgradeFactors[i]
			except:
				upgradeFactor = 0.5
			
			categoryPosition = {}
			highestCategoryPosition, highestCategoryName = -1, None
			for cName in upgradeCategories.iterkeys():
				pos = path.index( cName )
				categoryPosition[cName] = pos
				if pos > highestCategoryPosition:
					highestCategoryPosition, highestCategoryName = pos, cName
			
			for cName, rrs in upgradeCategories.iteritems():
				for rr in rrs:
					if rr.categoryName != highestCategoryName:
						rr.categoryName = highestCategoryName
						rr.upgradeFactor = upgradeFactor ** (highestCategoryPosition - categoryPosition[cName])
						rr.upgradeResult = True
		
			break

def GetPotentialDuplicateFullNames( riderNameLicense ):
	nameLicense = defaultdict( list )
	for (full_name, license) in riderNameLicense.itervalues():
		nameLicense[full_name].append( license )
	
	return {full_name for full_name, licenses in nameLicense.iteritems() if len(licenses) > 1}
			
def GetCategoryResults( categoryName, raceResults, pointsForRank, useMostEventsCompleted=False, numPlacesTieBreaker=5 ):
	scoreByTime = SeriesModel.model.scoreByTime
	scoreByPercent = SeriesModel.model.scoreByPercent
	scoreByTrueSkill = SeriesModel.model.scoreByTrueSkill
	bestResultsToConsider = SeriesModel.model.bestResultsToConsider
	mustHaveCompleted = SeriesModel.model.mustHaveCompleted
	showLastToFirst = SeriesModel.model.showLastToFirst
	considerPrimePointsOrTimeBonus = SeriesModel.model.considerPrimePointsOrTimeBonus
	
	# Get all results for this category.
	raceResults = [rr for rr in raceResults if rr.categoryName == categoryName]
	if not raceResults:
		return [], [], set()
		
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
	riderUpgrades = defaultdict( lambda : [False] * len(races) )
	riderNameLicense = {}
	
	def asInt( v ):
		return int(v) if int(v) == v else v
	
	ignoreFormat = u'[{}**]'
	upgradeFormat = u'{} pre-upg'
	
	def FixUpgradeFormat( riderUpgrades, riderResults ):
		# Format upgrades so they are visible in the results.
		for rider, upgrades in riderUpgrades.iteritems():
			for i, u in enumerate(upgrades):
				if u:
					v = riderResults[rider][i]
					riderResults[rider][i] = tuple([upgradeFormat.format(v[0] if v[0] else '')] + list(v[1:]))
	
	riderResults = defaultdict( lambda : [(0,0,0,0)] * len(races) )
	riderFinishes = defaultdict( lambda : [None] * len(races) )
	if scoreByTime:
	
		raceLeader = { rr.raceInSeries: rr for rr in raceResults if rr.rank == 1 }
		
		# Get the individual results for each rider, and the total time.  Do not consider DNF riders as they have invalid times.
		raceResults = [rr for rr in raceResults if rr.rank != RaceResult.rankDNF]
		
		riderTFinish = defaultdict( float )
		for rr in raceResults:
			try:
				leader = raceLeader[rr.raceInSeries]
				if rr.laps != leader.laps:
					continue
			except KeyError:
				continue

			try:
				tFinish = float(rr.tFinish - (rr.timeBonus if considerPrimePointsOrTimeBonus else 0.0))
			except ValueError:
				continue
			rider = rr.key()
			riderNameLicense[rider] = (rr.full_name, rr.license)
			if rr.team and rr.team != u'0':
				riderTeam[rider] = rr.team
			riderResults[rider][raceSequence[rr.raceInSeries]] = (
				formatTime(tFinish, True), rr.rank, 0, rr.timeBonus if considerPrimePointsOrTimeBonus else 0.0
			)
			riderFinishes[rider][raceSequence[rr.raceInSeries]] = tFinish
			riderTFinish[rider] += tFinish
			riderUpgrades[rider][raceSequence[rr.raceInSeries]] = rr.upgradeResult
			riderPlaceCount[rider][rr.rank] += 1
			riderEventsCompleted[rider] += 1

		# Adjust for the best times.
		if bestResultsToConsider > 0:
			for rider, finishes in riderFinishes.iteritems():
				iTimes = [(i, t) for i, t in enumerate(finishes) if t is not None]
				if len(iTimes) > bestResultsToConsider:
					iTimes.sort( key=operator.itemgetter(1, 0) )
					for i, t in iTimes[bestResultsToConsider:]:
						riderTFinish[rider] -= t
						v = riderResults[rider][i]
						riderResults[rider][i] = tuple([ignoreFormat.format(v[0])] + list(v[1:]))
					riderEventsCompleted[rider] = bestResultsToConsider

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
		categoryResult = [list(riderNameLicense[rider]) + [riderTeam[rider], formatTime(riderTFinish[rider],True), riderGap[rider]] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races, GetPotentialDuplicateFullNames(riderNameLicense)
	
	elif scoreByPercent:
		# Get the individual results for each rider as a percentage of the winner's time.  Ignore DNF riders.
		raceResults = [rr for rr in raceResults if rr.rank != RaceResult.rankDNF]

		percentFormat = u'{:.2f}'
		riderPercentTotal = defaultdict( float )
		
		raceLeader = { rr.raceInSeries: rr for rr in raceResults if rr.rank == 1 }
		
		for rr in raceResults:
			try:
				leader = raceLeader[rr.raceInSeries]
				if rr.laps != leader.laps:
					continue
			except KeyError:
				continue

			tFastest = leader.tProjected
			try:
				tFinish = rr.tProjected
			except ValueError:
				continue
			rider = rr.key()
			riderNameLicense[rider] = (rr.full_name, rr.license)
			if rr.team and rr.team != u'0':
				riderTeam[rider] = rr.team
			percent = min( 100.0, (tFastest / tFinish) * 100.0 if tFinish > 0.0 else 0.0 ) * (rr.upgradeFactor if rr.upgradeResult else 1)
			riderResults[rider][raceSequence[rr.raceInSeries]] = (
				u'{}, {}'.format(percentFormat.format(percent), formatTime(tFinish, False)), rr.rank, 0, 0
			)
			riderFinishes[rider][raceSequence[rr.raceInSeries]] = percent
			riderPercentTotal[rider] += percent
			riderUpgrades[rider][raceSequence[rr.raceInSeries]] = rr.upgradeResult
			riderPlaceCount[rider][rr.rank] += 1
			riderEventsCompleted[rider] += 1

		# Adjust for the best percents.
		if bestResultsToConsider > 0:
			for rider, finishes in riderFinishes.iteritems():
				iPercents = [(i, p) for i, p in enumerate(finishes) if p is not None]
				if len(iPercents) > bestResultsToConsider:
					iPercents.sort( key=lambda x: (-x[1], x[0]) )
					for i, p in iPercents[bestResultsToConsider:]:
						riderPercentTotal[rider] -= p
						v = riderResults[rider][i]
						riderResults[rider][i] = tuple([ignoreFormat.format(v[0])] + list(v[1:]))

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
		categoryResult = [list(riderNameLicense[rider]) + [riderTeam[rider], percentFormat.format(riderPercentTotal[rider]), riderGap[rider]] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races, GetPotentialDuplicateFullNames(riderNameLicense)
	
	elif scoreByTrueSkill:
		# Get an intial Rating for all riders.
		tsEnv = trueskill.TrueSkill( draw_probability=0.0 )
		
		sigmaMultiple = 3.0
		
		def formatRating( rating ):
			return u'{:0.2f} ({:0.2f},{:0.2f})'.format(
				rating.mu-sigmaMultiple*rating.sigma,
				rating.mu,
				rating.sigma
			)
	
		# Get the individual results for each rider, and the total points.
		riderRating = {}
		riderPoints = defaultdict( int )
		for rr in raceResults:
			rider = rr.key()
			riderNameLicense[rider] = (rr.full_name, rr.license)
			if rr.team and rr.team != u'0':
				riderTeam[rider] = rr.team
			if rr.rank != RaceResult.rankDNF:
				riderResults[rider][raceSequence[rr.raceInSeries]] = (0, rr.rank, 0, 0)
				riderFinishes[rider][raceSequence[rr.raceInSeries]] = rr.rank
				riderPlaceCount[rider][rr.rank] += 1

		riderRating = { rider:tsEnv.Rating() for rider in riderResults.iterkeys() }
		for iRace in xrange(len(races)):
			# Get the riders that participated in this race.
			riderRank = sorted(
				((rider, finishes[iRace]) for rider, finishes in riderFinishes.iteritems() if finishes[iRace] is not None),
				key=operator.itemgetter(1)
			)
			
			if len(riderRank) <= 1:
				continue
			
			# Update the ratings based on this race's outcome.
			# The TrueSkill rate function requires each rating to be a list even if there is only one.
			ratingNew = tsEnv.rate( [[riderRating[rider]] for rider, rank in riderRank] )
			riderRating.update( {rider:rating[0] for (rider, rank), rating in zip(riderRank, ratingNew)} )
			
			# Update the partial results.
			for rider, rank in riderRank:
				rating = riderRating[rider]
				riderResults[rider][iRace] = (formatRating(rating), rank, 0, 0)

		# Assign rider points based on mu-3*sigma.
		riderPoints = { rider:rating.mu-sigmaMultiple*rating.sigma for rider, rating in riderRating.iteritems() }
		
		# Sort by rider points - greatest number of points first.
		riderOrder = sorted( riderPoints.iterkeys(), key=lambda r: riderPoints[r], reverse=True )

		# Compute the points gap.
		riderGap = {}
		if riderOrder:
			leader = riderOrder[0]
			leaderPoints = riderPoints[leader]
			riderGap = { r : leaderPoints - riderPoints[r] for r in riderOrder }
			riderGap = { r : u'{:0.2f}'.format(gap) if gap else u'' for r, gap in riderGap.iteritems() }
		
		riderPoints = { rider:formatRating(riderRating[rider]) for rider, points in riderPoints.iteritems() }
		
		# Reverse the race order if required.
		if showLastToFirst:
			races.reverse()
			for results in riderResults.itervalues():
				results.reverse()
		
		# List of:
		# lastName, firstName, license, team, points, [list of (points, position) for each race in series]
		categoryResult = [list(riderNameLicense[rider]) + [riderTeam[rider], riderPoints[rider], riderGap[rider]] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races, GetPotentialDuplicateFullNames(riderNameLicense)
		
	else: # Score by points.
		# Get the individual results for each rider, and the total points.
		riderPoints = defaultdict( int )
		for rr in raceResults:
			rider = rr.key()
			riderNameLicense[rider] = (rr.full_name, rr.license)
			if rr.team and rr.team != u'0':
				riderTeam[rider] = rr.team
			primePoints = rr.primePoints if considerPrimePointsOrTimeBonus else 0
			earnedPoints = pointsForRank[rr.raceFileName][rr.rank] + primePoints
			points = asInt( earnedPoints * rr.upgradeFactor )
			riderResults[rider][raceSequence[rr.raceInSeries]] = (points, rr.rank, primePoints, 0)
			riderFinishes[rider][raceSequence[rr.raceInSeries]] = points
			riderPoints[rider] += points
			riderPoints[rider] = asInt( riderPoints[rider] )
			riderUpgrades[rider][raceSequence[rr.raceInSeries]] = rr.upgradeResult
			riderPlaceCount[rider][rr.rank] += 1
			riderEventsCompleted[rider] += 1

		# Adjust for the best scores.
		if bestResultsToConsider > 0:
			for rider, finishes in riderFinishes.iteritems():
				iPoints = [(i, p) for i, p in enumerate(finishes) if p is not None]
				if len(iPoints) > bestResultsToConsider:
					iPoints.sort( key=lambda x: (-x[1], x[0]) )
					for i, p in iPoints[bestResultsToConsider:]:
						riderPoints[rider] -= p
						v = riderResults[rider][i]
						riderResults[rider][i] = tuple([ignoreFormat.format(v[0] if v[0] else '')] + list(v[1:]))

		FixUpgradeFormat( riderUpgrades, riderResults )

		# Filter out minimal events completed.
		riderOrder = [rider for rider, results in riderResults.iteritems() if riderEventsCompleted[rider] >= mustHaveCompleted]
		
		# Sort by rider points - greatest number of points first.  Break ties with place count, then
		# most recent result.
		rankDNF = RaceResult.rankDNF
		riderOrder.sort(
			key = lambda r:	[-riderPoints[r]] +
							([-riderEventsCompleted[r]] if useMostEventsCompleted else []) +
							[-riderPlaceCount[r][k] for k in xrange(1, numPlacesTieBreaker+1)] +
							[rank if rank>0 else rankDNF for points, rank, primePoints, timeBonus in reversed(riderResults[r])]
		)
		
		# Compute the points gap.
		riderGap = {}
		if riderOrder:
			leader = riderOrder[0]
			leaderPoints = riderPoints[leader]
			riderGap = { r : leaderPoints - riderPoints[r] for r in riderOrder }
			riderGap = { r : unicode(gap) if gap else u'' for r, gap in riderGap.iteritems() }
		
		# Reverse the race order if required for display.
		if showLastToFirst:
			races.reverse()
			for results in riderResults.itervalues():
				results.reverse()
		
		# List of:
		# lastName, firstName, license, team, points, [list of (points, position) for each race in series]
		categoryResult = [list(riderNameLicense[rider]) + [riderTeam[rider], riderPoints[rider], riderGap[rider]] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races, GetPotentialDuplicateFullNames(riderNameLicense)

def GetTotalUniqueParticipants( raceResults ):
	return len( set( rr.key() for rr in raceResults ) )
	
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
		categoryResult, races, potentialDuplicates = GetCategoryResults( c, raceResults, pointsForRank )
		print '--------------------------------------------------------'
		print c
		print
		for rr in categoryResult:
			print rr[0], rr[1], rr[2], rr[3], rr[4]
		print races
	#print raceResults
	
