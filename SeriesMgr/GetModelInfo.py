import os
import re
import math
import pickle
import datetime
import operator
import itertools
from collections import defaultdict, namedtuple

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
from GetMatchingExcelFile import GetMatchingExcelFile

class DeepDict(defaultdict):
	def __call__(self):
		return DeepDict(self.default_factory)

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
		decimal = '.{:02d}'.format( int( f * 100 ) )
	else:
		decimal = ''
	if hours > 0:
		return "{}{}h{}'{:02d}{}\"".format(sign, hours, minutes, secs, decimal)
	else:
		return "{}{}'{:02d}{}\"".format(sign, minutes, secs, decimal)

def safe_upper( f ):
	try:
		return f.upper()
	except:
		return f

def fix_uci_id( uci_id ):
	uci_id = str(uci_id or '').strip()
	if uci_id.endswith('.0'):	# Correct if the uci_id is a floating point number.
		uci_id = uci_id[-2:]
	uci_id = re.sub( '[^0-9]', '', uci_id )
	return uci_id
	'''
	# Check for valid UCI id.
	if len(uci_id) == 11 and sum( int(d) for d in uci_id[:9] ) % 97 == int(uci_id[9:]):
		return uci_id
	return None
	'''

class RaceResult:
	def __init__( self, firstName, lastName, license, team, categoryName, raceName, raceDate, raceFileName, bib, rank, raceOrganizer,
					raceURL=None, raceInSeries=None, tFinish=None, tProjected=None, primePoints=0, timeBonus=0, laps=1, pointsInput=None, uci_id=None ):
		self.firstName = str(firstName or '')
		self.lastName = str(lastName or '')
		
		self.license = (license or '')
		if isinstance(self.license, float) and int(self.license) == self.license:
			self.license = int(self.license)
		self.license = str(self.license)
		self.uci_id = fix_uci_id( uci_id )
		
		self.team = str(team or '')
		
		self.categoryName = str(categoryName or '')
		
		self.raceName = str(raceName)
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
		self.pointsInput = pointsInput
		
		self.tFinish = tFinish
		self.tProjected = tProjected if tProjected else tFinish
		
		self.upgradeFactor = 1
		self.upgradeResult = False
	
	@property
	def teamIsValid( self ):
		return self.team and self.team.lower() not in {'0', '0.0', 'no team', 'no-team', 'independent', 'independant', 'none'}
	
	'''
	def keySort( self ):
		if SeriesModel.model.uciIdKey:
			fields = 'categoryName', 'lastName', 'firstName', 'uci_id', 'raceDate', 'raceName'
		else:
			fields = 'categoryName', 'lastName', 'firstName', 'license', 'raceDate', 'raceName'
		return tuple( safe_upper(getattr(self, a)) for a in fields )
		
	def keyMatch( self ):
		if SeriesModel.model.uciIdKey:
			fields = 'categoryName', 'lastName', 'firstName', 'uci_id'
		else:
			fields = 'categoryName', 'lastName', 'firstName', 'license'
		return tuple( safe_upper(getattr(self, a)) for a in fields )
	'''
		
	def key( self ):
		if SeriesModel.model.riderKey == SeriesModel.SeriesModel.KeyByUciId:
			return self.uci_id
		elif SeriesModel.model.riderKey == SeriesModel.SeriesModel.KeyByLicense:
			return self.license
		else:
			k = self.full_name.upper()
			s = Utils.removeDiacritic(k)		# If the full name has characters that have no ascii representation, return it as-is.
			return (s if len(s) == len(k) else k, Utils.removeDiacritic(self.license))
		
	def keyTeam( self ):
		k = self.team.upper()
		s = Utils.removeDiacritic(k)
		return s if len(s) == len(k) else k		# If the team name has characters that have no ascii representation, return it as-is.
		
	@property
	def full_name( self ):
		return ', '.join( [name for name in [self.lastName.upper(), self.firstName] if name] )
		
	def __repr__( self ):
		return ', '.join( '{}'.format(p) for p in [self.full_name, self.license, self.categoryName, self.raceName, self.raceDate] if p )

def ExtractRaceResults( r, seriesModel ):
	if os.path.splitext(r.fileName)[1] == '.cmn':
		return ExtractRaceResultsCrossMgr( r, seriesModel )
	else:
		return ExtractRaceResultsExcel( r, seriesModel )

def toInt( n ):
	if n == 'DNF':
		return SeriesModel.rankDNF
	try:
		return int(n.split()[0])
	except:
		return n

def ExtractRaceResultsExcel( raceInSeries, seriesModel ):
	ret = { 'success':True, 'explanation':'success', 'raceResults':[], 'licenseLinkTemplate':None }
	
	if not os.path.exists( raceInSeries.getFileName() ):
		ret['success'] = False
		ret['explanation'] = 'File not found'
		return ret
	
	raceName = os.path.splitext(os.path.basename(raceInSeries.getFileName()))[0]
	raceResults = []
	
	# Search for a "Pos" field to indicate the start of the data.
	for sfa in standard_field_aliases:
		if sfa[0] == 'pos':
			posHeader = set( a.lower() for a in sfa[1] )
			break
	
	# Check if this is a UCI Dataride spreadsheet
	folderName = os.path.basename( os.path.dirname(raceInSeries.getFileName()) )
	baseFileName = os.path.splitext( os.path.basename( raceInSeries.getFileName() ) )[0]
	
	excel = GetExcelReader( raceInSeries.getFileName() )
	uciDatarideSheets = {'General', 'Reference', 'Country Reference'}
	isUCIDataride = any( (s.strip() in uciDatarideSheets) for s in excel.sheet_names() )
	if isUCIDataride:
		uciCategoryName = baseFileName	# Category name is the directory.
		raceName = folderName			# Race name is the base file name.
		raceInSeries.isUCIDataride = isUCIDataride
	else:
		uciCategoryName = None
		
	for sheetName in excel.sheet_names():
		hasPointsInput, defaultPointsInput = False, None
		fm = None
		categoryNameSheet = sheetName.strip()
		if isUCIDataride:
			if categoryNameSheet in uciDatarideSheets:
				continue
			categoryNameSheet = uciCategoryName
		
		for row in excel.iter_list(sheetName):
			if fm:
				f = fm.finder( row )
				info = {
					'raceDate':		None,
					'raceFileName':	raceInSeries.getFileName(),
					'raceName':		raceName,
					'raceOrganizer': '',
					'raceInSeries': raceInSeries,					
					'bib': 			f('bib',99999),
					'rank':			f('pos',''),
					'tFinish':		f('time',0.0) or f('result',0.0),
					'firstName':	str(f('first_name','')).strip(),
					'lastName'	:	str(f('last_name','')).strip(),
					'license':		str(f('license_code','')).strip(),
					'uci_id':		f('uci_id',''),
					'team':			str(f('team','')).strip(),
					'categoryName': f('category_code',None),
					'laps':			f('laps',1),
					'pointsInput':	f('points',defaultPointsInput),
					'irm':			f('irm',None),
				}
				
				info['rank'] = str(info['rank']).strip()
				
				# Handle the status in the irm column.
				if not info['rank'] and info['irm'] in {'DQ', 'DSQ', 'DNS', 'DNF'}:
					info['rank'] = info['irm']
				info.pop('irm', None)
				
				if not info['rank']:	# If missing rank, assume end of input.
					break
				
				isUSAC = False
				if info['categoryName'] is None:
					if isUCIDataride:
						info['categoryName'] = uciCategoryName
					elif sheetName == 'Results' and 'irm' in fm:
						info['categoryName'] = folderName			# Case of Dataride Results-only sheet.
					else:
						# Hack for USAC cycling input spreadsheet.
						cn = str(f('category_name','')).strip()
						if cn and categoryNameSheet.startswith('Sheet'):
							isUSAC = True
							g = str(f('gender', '')).strip()
							if g and cn.startswith('CAT') and not (cn.endswith(' F') or cn.endswith(' M')):
								cn += ' ({})'.format( 'Women' if g.upper() in 'FW' else 'Men' )
							info['categoryName'] = cn
						else:
							info['categoryName'] = categoryNameSheet
				info['categoryName'] = str(info['categoryName']).strip()
				
				try:
					info['rank'] = toInt(info['rank'])
				except ValueError:
					pass
				
				# Handle DNF status by assigning special rank.
				if info['rank'] == 'DNF':
					info['rank'] = SeriesModel.rankDNF
					
				# For all other status, ignore the result.
				if not isinstance(info['rank'], int):
					continue

				if isUSAC and info['rank'] >= 999:
					info['rank'] = SeriesModel.rankDNF
					
				# Check for comma-separated name.
				name = str(f('name', '')).strip()
				if name and not info['firstName'] and not info['lastName']:
					try:
						info['lastName'], info['firstName'] = name.split(',',1)
					except:
						pass
				
				if not info['firstName'] and not info['lastName']:
					continue
				
				if info['team'] == 'None':
					info['team'] = ''
				
				# If there is a bib it must be numeric.
				try:
					info['bib'] = int(str(info['bib']).strip())
				except ValueError:
					continue
					
				info['tFinish'] = (info['tFinish'] or 0.0)
				if isinstance(info['tFinish'], str) and ':' in info['tFinish']:
					info['tFinish'] = Utils.StrToSeconds( info['tFinish'].strip() )
				else:
					try:
						info['tFinish'] = float( info['tFinish'] ) * 24.0 * 60.0 * 60.0	# Convert Excel day number to seconds.
					except Exception as e:
						info['tFinish'] = 0.0
				
				raceResults.append( RaceResult(**info) )
				
			elif any( str(r).strip().lower() in posHeader for r in row ):
				fm = standard_field_map()
				fm.set_headers( row )
				
				# Check if this spreadsheet has points.
				if 'points' in fm:
					hasPointsInput, defaultPointsInput = True, 0
				
				# Check if this is a team-only sheet.
				raceInSeries.pureTeam = ('team' in fm and not any(n in fm for n in ('name', 'last_name', 'first_name', 'license')))
				raceInSeries.resultsType = SeriesModel.Race.TeamResultsOnly if raceInSeries.pureTeam else SeriesModel.Race.IndividualAndTeamResults

	ret['raceResults'] = raceResults
	return ret

def FixExcelSheetLocal( fileName, race ):
	# Check if we have a missing spreadsheet, but can find one in the same folder as the race.
	if getattr(race, 'excelLink', None):
		excelLink = race.excelLink
		if excelLink.fileName and not os.path.isfile(excelLink.fileName):
			newFileName = GetMatchingExcelFile( fileName, excelLink.fileName )
			if newFileName:
				race.excelLink.fileName = newFileName

def ExtractRaceResultsCrossMgr( raceInSeries, seriesModel ):
	ret = { 'success':True, 'explanation':'success', 'raceResults':[], 'licenseLinkTemplate':None }
	
	fileName = raceInSeries.getFileName()
	try:
		with open(fileName, 'rb') as fp, Model.LockRace() as race:
			race = pickle.load( fp, encoding='latin1', errors='replace' )
			FixExcelSheetLocal( fileName, race )
			isFinished = race.isFinished()
			race.tagNums = None
			race.resetAllCaches()
			Model.setRace( race )
		
		ResetExcelLinkCache()
		Model.resetCache()

	except IOError as e:
		ret['success'] = False
		ret['explanation'] = e
		return ret
	
	race = Model.race
	if not HasExcelLink(race):	# Force a refresh of the Excel link before reading the categories.
		pass
		
	if race.licenseLinkTemplate:
		ret['licenseLinkTemplate'] = race.licenseLinkTemplate
	
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
			for fTo, fFrom in [('firstName', 'FirstName'), ('lastName', 'LastName'), ('license', 'License'), ('uci_id', 'UCIID'), ('team', 'Team')]:
				info[fTo] = getattr(rr, fFrom, '')
				
			if not info['firstName'] and not info['lastName']:
				continue				

			info['categoryName'] = category.fullname
			info['laps'] = rr.laps
			
			for fTo, fFrom in [('raceName', 'name'), ('raceOrganizer', 'organizer')]:
				info[fTo] = getattr(race, fFrom, '')
			
			raceNum = getattr(race, 'raceNum', '')
			if raceNum:
				info['raceName'] = '{}-{}'.format(info['raceName'], raceNum)
				
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
			info['rank'] = SeriesModel.rankDNF if rr.status == DNF else pos
			
			if hasattr(rr, '_lastTimeOrig') or hasattr(rr, 'lastTime'):
				info['tFinish'] = getattr(rr, '_lastTimeOrig', None) or getattr(rr,'lastTime')
				if rr.raceTimes:
					#info['tFinish'] = max( 0.0, info['tFinish'] - rr.raceTimes[0] )
					info['tFinish'] = max( 0.0, rr.raceTimes[-1] - rr.raceTimes[0] )
			else:
				info['tFinish'] = 1000.0*24.0*60.0*60.0
			
			try:
				info['tProjected'] = rr.projectedTime
				if rr.raceTimes:
					info['tProjected'] = max( 0.0, info['tProjected'] - rr.raceTimes[0] )				
			except AttributeError:
				info['tProjected'] = info['tFinish']
			
			info['primePoints'] = primePoints.get(rr.num, 0)
			info['timeBonus'] = timeBonus.get(rr.num, 0.0)
			
			raceResults.append( RaceResult(**info) )
		
	Model.race = None
	ret['raceResults'] = raceResults
	return ret

def AdjustForUpgrades( raceResults ):
	upgradePaths = []
	for path in SeriesModel.model.upgradePaths:
		upgradePaths.append( [p.strip() for p in path.split(',')] )
	upgradeFactors = SeriesModel.model.upgradeFactors
	
	competitionCategories = defaultdict( lambda: defaultdict(list) )
	for rr in raceResults:
		competitionCategories[rr.key()][rr.categoryName].append( rr )
	
	for key, categories in competitionCategories.items():
		if len(categories) == 1:
			continue
		
		for i, path in enumerate(upgradePaths):
			upgradeCategories = { cName: rrs for cName, rrs in categories.items() if cName in path }
			if len(upgradeCategories) <= 1:
				continue
			
			try:
				upgradeFactor = upgradeFactors[i]
			except:
				upgradeFactor = 0.5
			
			categoryPosition = {}
			highestCategoryPosition, highestCategoryName = -1, None
			for cName in upgradeCategories.keys():
				pos = path.index( cName )
				categoryPosition[cName] = pos
				if pos > highestCategoryPosition:
					highestCategoryPosition, highestCategoryName = pos, cName
			
			for cName, rrs in upgradeCategories.items():
				for rr in rrs:
					if rr.categoryName != highestCategoryName:
						rr.categoryName = highestCategoryName
						rr.upgradeFactor = upgradeFactor ** (highestCategoryPosition - categoryPosition[cName])
						rr.upgradeResult = True
		
			break

def GetPotentialDuplicateFullNames( riderNameLicenseUCIID ):
	nameLicenseUCIID = defaultdict( list )
	for (full_name, license, uci_id) in riderNameLicenseUCIID.values():
		nameLicenseUCIID[full_name].append( license or uci_id )
	
	return {full_name for full_name, entries in nameLicenseUCIID.items() if len(entries) > 1}
			
def GetCategoryResults( categoryName, raceResults, useMostEventsCompleted=False, numPlacesTieBreaker=5, bestResultsToConsider=None, mustHaveCompleted=None ):
	model = SeriesModel.model
	
	scoreByTime						= model.scoreByTime
	scoreByPercent					= model.scoreByPercent
	scoreByTrueSkill				= model.scoreByTrueSkill
	showLastToFirst					= model.showLastToFirst
	considerPrimePointsOrTimeBonus	= model.considerPrimePointsOrTimeBonus
	scoreByPointsInput				= model.scoreByPointsInput
	bestResultsToConsider			= (bestResultsToConsider or 0)
	mustHaveCompleted				= (mustHaveCompleted or 0)
	
	# Get all results for this category.
	raceResults = [rr for rr in raceResults if rr.categoryName == categoryName]
	if not raceResults:
		return [], [], set()
		
	# Create a map for race filenames to grade.
	raceGrade = { race.getFileName():race.grade for race in model.races }
	gradesUsed = sorted( set(race.grade for race in model.races) )
		
	# Assign a sequence number to the races in the specified order.
	for i, r in enumerate(model.races):
		r.iSequence = i
		
	# Get all races for this category.
	races = set( (rr.raceDate, rr.raceName, rr.raceURL, rr.raceInSeries) for rr in raceResults )
	races = sorted( races, key = lambda r: getattr(r[3], 'iSequence', 0) )
	raceSequence = dict( (r[3], i) for i, r in enumerate(races) )
	
	riderEventsCompleted = defaultdict( int )
	riderPlaceCount = defaultdict( lambda : defaultdict(int) )		# Indexed by (grade, rank).
	riderTeam = defaultdict( lambda : '' )
	riderUpgrades = defaultdict( lambda : [False] * len(races) )
	riderNameLicenseUCIID = {}
	
	def asInt( v ):
		return int(v) if int(v) == v else v
	
	ignoreFormat = '[{}**]'
	upgradeFormat = '{} pre-upg'
	
	def FixUpgradeFormat( riderUpgrades, riderResults ):
		# Format upgrades so they are visible in the results.
		for rider, upgrades in riderUpgrades.items():
			for i, u in enumerate(upgrades):
				if u:
					v = riderResults[rider][i]
					riderResults[rider][i] = tuple([upgradeFormat.format(v[0] if v[0] else '')] + list(v[1:]))
	
	riderResults = defaultdict( lambda : [(0,SeriesModel.rankDidNotParticipate,0,0)] * len(races) )	# (points, rr.rank, primePoints, 0) for each result.
	riderFinishes = defaultdict( lambda : [None] * len(races) )
	if scoreByTime:
	
		raceLeader = { rr.raceInSeries: rr for rr in raceResults if rr.rank == 1 }
		
		# Get the individual results for each rider, and the total time.  Do not consider DNF riders as they have invalid times.
		raceResults = [rr for rr in raceResults if rr.rank != SeriesModel.rankDNF]
		
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
			riderNameLicenseUCIID[rider] = (rr.full_name, rr.license, rr.uci_id)
			if rr.team and rr.team != '0':
				riderTeam[rider] = rr.team
			riderResults[rider][raceSequence[rr.raceInSeries]] = (
				formatTime(tFinish, True), rr.rank, 0, rr.timeBonus if considerPrimePointsOrTimeBonus else 0.0
			)
			riderFinishes[rider][raceSequence[rr.raceInSeries]] = tFinish
			riderTFinish[rider] += tFinish
			riderUpgrades[rider][raceSequence[rr.raceInSeries]] = rr.upgradeResult
			riderPlaceCount[rider][(raceGrade[rr.raceFileName],rr.rank)] += 1
			riderEventsCompleted[rider] += 1

		# Adjust for the best times.
		if bestResultsToConsider > 0:
			for rider, finishes in riderFinishes.items():
				iTimes = [(i, t) for i, t in enumerate(finishes) if t is not None]
				if len(iTimes) > bestResultsToConsider:
					iTimes.sort( key=operator.itemgetter(1, 0) )
					for i, t in iTimes[bestResultsToConsider:]:
						riderTFinish[rider] -= t
						v = riderResults[rider][i]
						riderResults[rider][i] = tuple([ignoreFormat.format(v[0])] + list(v[1:]))
					riderEventsCompleted[rider] = bestResultsToConsider

		# Filter out minimal events completed.
		riderOrder = [rider for rider, results in riderResults.items() if riderEventsCompleted[rider] >= mustHaveCompleted]
		
		# Sort by decreasing events completed, then increasing rider time.
		riderOrder.sort( key = lambda r: (-riderEventsCompleted[r], riderTFinish[r]) )
		
		# Compute the time gap.
		riderGap = {}
		if riderOrder:
			leader = riderOrder[0]
			leaderTFinish = riderTFinish[leader]
			leaderEventsCompleted = riderEventsCompleted[leader]
			riderGap = { r : riderTFinish[r] - leaderTFinish if riderEventsCompleted[r] == leaderEventsCompleted else None for r in riderOrder }
			riderGap = { r : formatTimeGap(gap) if gap else '' for r, gap in riderGap.items() }
		
		# List of:
		# lastName, firstName, license, team, tTotalFinish, [list of (points, position) for each race in series]
		categoryResult = [list(riderNameLicenseUCIID[rider]) + [riderTeam[rider], formatTime(riderTFinish[rider],True), riderGap[rider]] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races, GetPotentialDuplicateFullNames(riderNameLicenseUCIID)
	
	elif scoreByPercent:
		# Get the individual results for each rider as a percentage of the winner's time.  Ignore DNF riders.
		raceResults = [rr for rr in raceResults if rr.rank != SeriesModel.rankDNF]

		percentFormat = '{:.2f}'
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
			riderNameLicenseUCIID[rider] = (rr.full_name, rr.license, rr.uci_id)
			if rr.team and rr.team != '0':
				riderTeam[rider] = rr.team
			percent = min( 100.0, (tFastest / tFinish) * 100.0 if tFinish > 0.0 else 0.0 ) * (rr.upgradeFactor if rr.upgradeResult else 1)
			riderResults[rider][raceSequence[rr.raceInSeries]] = (
				'{}, {}'.format(percentFormat.format(percent), formatTime(tFinish, False)), rr.rank, 0, 0
			)
			riderFinishes[rider][raceSequence[rr.raceInSeries]] = percent
			riderPercentTotal[rider] += percent
			riderUpgrades[rider][raceSequence[rr.raceInSeries]] = rr.upgradeResult
			riderPlaceCount[rider][(raceGrade[rr.raceFileName],rr.rank)]
			riderEventsCompleted[rider] += 1

		# Adjust for the best percents.
		if bestResultsToConsider > 0:
			for rider, finishes in riderFinishes.items():
				iPercents = [(i, p) for i, p in enumerate(finishes) if p is not None]
				if len(iPercents) > bestResultsToConsider:
					iPercents.sort( key=lambda x: (-x[1], x[0]) )
					for i, p in iPercents[bestResultsToConsider:]:
						riderPercentTotal[rider] -= p
						v = riderResults[rider][i]
						riderResults[rider][i] = tuple([ignoreFormat.format(v[0])] + list(v[1:]))

		# Filter out minimal events completed.
		riderOrder = [rider for rider, results in riderResults.items() if riderEventsCompleted[rider] >= mustHaveCompleted]
		
		# Sort by decreasing percent total.
		riderOrder.sort( key = lambda r: -riderPercentTotal[r] )
		
		# Compute the gap.
		riderGap = {}
		if riderOrder:
			leader = riderOrder[0]
			leaderPercentTotal = riderPercentTotal[leader]
			riderGap = { r : leaderPercentTotal - riderPercentTotal[r] for r in riderOrder }
			riderGap = { r : percentFormat.format(gap) if gap else '' for r, gap in riderGap.items() }
					
		# List of:
		# lastName, firstName, license, team, totalPercent, [list of (percent, position) for each race in series]
		categoryResult = [list(riderNameLicenseUCIID[rider]) + [riderTeam[rider], percentFormat.format(riderPercentTotal[rider]), riderGap[rider]] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races, GetPotentialDuplicateFullNames(riderNameLicenseUCIID)
	
	elif scoreByTrueSkill:
		# Get an initial Rating for all riders.
		tsEnv = trueskill.TrueSkill( draw_probability=0.0 )
		
		sigmaMultiple = 3.0
		
		def formatRating( rating ):
			return '{:0.2f} ({:0.2f},{:0.2f})'.format(
				rating.mu-sigmaMultiple*rating.sigma,
				rating.mu,
				rating.sigma
			)
	
		# Get the individual results for each rider, and the total points.
		riderRating = {}
		riderPoints = defaultdict( int )
		for rr in raceResults:
			rider = rr.key()
			riderNameLicenseUCIID[rider] = (rr.full_name, rr.license, rr.uci_id)
			if rr.team and rr.team != '0':
				riderTeam[rider] = rr.team
			if rr.rank != SeriesModel.rankDNF:
				riderResults[rider][raceSequence[rr.raceInSeries]] = (0, rr.rank, 0, 0)
				riderFinishes[rider][raceSequence[rr.raceInSeries]] = rr.rank
				riderPlaceCount[rider][(raceGrade[rr.raceFileName],rr.rank)]

		riderRating = { rider:tsEnv.Rating() for rider in riderResults.keys() }
		for iRace in range(len(races)):
			# Get the riders that participated in this race.
			riderRank = sorted(
				((rider, finishes[iRace]) for rider, finishes in riderFinishes.items() if finishes[iRace] is not None),
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
		riderPoints = { rider:rating.mu-sigmaMultiple*rating.sigma for rider, rating in riderRating.items() }
		
		# Sort by rider points - greatest number of points first.
		riderOrder = sorted( riderPoints.keys(), key=lambda r: riderPoints[r], reverse=True )

		# Compute the gap.
		riderGap = {}
		if riderOrder:
			leader = riderOrder[0]
			leaderPoints = riderPoints[leader]
			riderGap = { r : leaderPoints - riderPoints[r] for r in riderOrder }
			riderGap = { r : '{:0.2f}'.format(gap) if gap else '' for r, gap in riderGap.items() }
		
		riderPoints = { rider:formatRating(riderRating[rider]) for rider, points in riderPoints.items() }
		
		# Reverse the race order if required.
		if showLastToFirst:
			races.reverse()
			for results in riderResults.values():
				results.reverse()
		
		# List of:
		# lastName, firstName, license, team, points, [list of (points, position) for each race in series]
		categoryResult = [list(riderNameLicenseUCIID[rider]) + [riderTeam[rider], riderPoints[rider], riderGap[rider]] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races, GetPotentialDuplicateFullNames(riderNameLicenseUCIID)
		
	else: # Score by points.
		# Get the individual results for each rider, and the total points.
		
		pointStructureFromRaceFileName = { r.fileName:r.pointStructure for r in model.races }	
		def getPointStructure( raceFileName, categoryName ):
			return model.categories[categoryName].pointStructure or pointStructureFromRaceFileName[raceFileName]
					
		riderPoints = defaultdict( int )
		for rr in raceResults:
			rider = rr.key()
			riderNameLicenseUCIID[rider] = (rr.full_name, rr.license, rr.uci_id)
			if rr.team and rr.team != '0':
				riderTeam[rider] = rr.team
			primePoints = rr.primePoints if considerPrimePointsOrTimeBonus else 0
			earnedPoints = getPointStructure(rr.raceFileName, categoryName)[rr.rank] + primePoints
			points = asInt( earnedPoints * rr.upgradeFactor )
			riderResults[rider][raceSequence[rr.raceInSeries]] = (points, rr.rank, primePoints, 0)
			riderFinishes[rider][raceSequence[rr.raceInSeries]] = points
			riderPoints[rider] += points
			riderPoints[rider] = asInt( riderPoints[rider] )
			riderUpgrades[rider][raceSequence[rr.raceInSeries]] = rr.upgradeResult
			riderPlaceCount[rider][(raceGrade[rr.raceFileName],rr.rank)] += 1
			riderEventsCompleted[rider] += 1

		# Apply scoring by points input if set in the last race.
		# Used for scoring Omniums.
		if scoreByPointsInput:
			hasPointsInput = set()	# Keep track of the riders with points.
			for rr in raceResults:
				rider = rr.key()
				if rr.pointsInput is not None:
					riderPoints[rider] = rr.pointsInput or 0
					hasPointsInput.add( rider )
			if hasPointsInput:	# If some of the riders have points.
				# For all riders without points (presumably DNF'd or DQ'd in earlier events).
				for rider in list(riderPoints.keys()):
					if rider not in hasPointsInput:
						riderPoints[rider] = 0

		# Adjust for the best scores.
		if bestResultsToConsider > 0:
			for rider, finishes in riderFinishes.items():
				iPoints = [(i, p) for i, p in enumerate(finishes) if p is not None]
				if len(iPoints) > bestResultsToConsider:
					iPoints.sort( key=lambda x: (-x[1], x[0]) )
					for i, p in iPoints[bestResultsToConsider:]:
						riderPoints[rider] -= p
						v = riderResults[rider][i]
						riderResults[rider][i] = tuple([ignoreFormat.format(v[0] if v[0] else '')] + list(v[1:]))

		FixUpgradeFormat( riderUpgrades, riderResults )

		# Filter out minimal events completed.
		riderOrder = [rider for rider, results in riderResults.items() if riderEventsCompleted[rider] >= mustHaveCompleted]
		
		# Sort by rider points - greatest number of points first.  Break ties with place count, then most recent result.
		rankDNF = SeriesModel.rankDNF
		riderOrder.sort(
			key = lambda r:	[-riderPoints[r]] +
							([-riderEventsCompleted[r]] if useMostEventsCompleted else []) +
							[-riderPlaceCount[r][(g,k)] for g,k in itertools.product(gradesUsed, range(1, numPlacesTieBreaker+1))] +
							[rank if rank>0 else rankDNF for points, rank, primePoints, timeBonus in reversed(riderResults[r])]
		)
		
		# Compute the points gap.
		riderGap = {}
		if riderOrder:
			leader = riderOrder[0]
			leaderPoints = riderPoints[leader]
			riderGap = { r : leaderPoints - riderPoints[r] for r in riderOrder }
			riderGap = { r : str(gap) if gap else '' for r, gap in riderGap.items() }
		
		# Reverse the race order if required for display.
		if showLastToFirst:
			races.reverse()
			for results in riderResults.values():
				results.reverse()
		
		# List of:
		# lastName, firstName, license, team, points, [list of (points, position) for each race in series]
		categoryResult = [list(riderNameLicenseUCIID[rider]) + [riderTeam[rider], riderPoints[rider], riderGap[rider]] + [riderResults[rider]] for rider in riderOrder]
		return categoryResult, races, GetPotentialDuplicateFullNames(riderNameLicenseUCIID)

#------------------------------------------------------------------------------------------------

RaceTuple = namedtuple('RaceTuple', ['date', 'name', 'url', 'raceInSeries'] )
ResultTuple = namedtuple('ResultTuple', ['points', 'time', 'rank', 'primePoints', 'timeBonus', 'rr'] )

def GetAllCategoryResultsTeam( raceResults ):
	model = SeriesModel.model
	showLastToFirst = model.showLastToFirst
	considerPrimePointsOrTimeBonus = model.considerPrimePointsOrTimeBonus
	
	# Filter results just for teams on the list, or valid team names (exclude missing team, independent, etc.)
	trn = set( model.teamResultsNames )
	raceResults = [rr for rr in raceResults if ((rr.team in trn) if trn else rr.teamIsValid)]
	if not raceResults:
		return [], []
		
	# Get all races for this category.
	raceNameSequence = {rr.raceName:rr.raceInSeries.iSequence for rr in raceResults}
	raceNames = sorted( set( rr.raceName for rr in raceResults ), key=lambda name: raceNameSequence[name], reverse=True )
	raceNameIndex = { rn:i for i, rn in enumerate(raceNames) }
	raceNameToRaceTuple = {}
	for rr in raceResults:
		if rr.raceName not in raceNameToRaceTuple:
			raceNameToRaceTuple[rr.raceName] = RaceTuple(None, rr.raceName, None, rr.raceInSeries)
	
	def asInt( v ):
		return int(v) if int(v) == v else v

	# Get the specific pointStructure as a function of the raceName and categoryName.
	# If no pointStructure is specified by category, use the race one as a default.
	pointStructureFromRaceFileName = { r.fileName:r.pointStructure for r in model.races }	
	def getPointStructure( raceFileName, categoryName ):
		return model.categories[categoryName].pointStructure or pointStructureFromRaceFileName[raceFileName]
		
	# Get the best points result by raceName, keyTeam and categoryName.
	teamName = {}
	
	bestResultsByTeamRaceCategory = defaultdict( lambda:defaultdict( lambda:defaultdict(int) ) )
	teamResultsPoints = defaultdict( lambda: [0] * len(raceNames)  )
	for rr in raceResults:
		if trn and rr.team not in trn:	# Skip teams not included in the Team Results Names list.
			continue
		
		primePoints = rr.primePoints if considerPrimePointsOrTimeBonus else 0
		earnedPoints = getPointStructure(rr.raceFileName, rr.categoryName)[rr.rank] + primePoints
		pointsNew = asInt( earnedPoints )
		
		pointsCur = bestResultsByTeamRaceCategory[rr.keyTeam()][rr.raceName][rr.categoryName]
		if pointsNew > pointsCur:
			bestResultsByTeamRaceCategory[rr.keyTeam()][rr.raceName][rr.categoryName] = pointsNew
			teamResultsPoints[rr.keyTeam()][raceNameIndex[rr.raceName]] += pointsNew - pointsCur
		teamName[rr.keyTeam()] = rr.team
	
	# Get the total results by keyTeam for all races.
	teamPoints = {}
	for keyTeam, bestResultsByRace in teamResultsPoints.items():
		teamPoints[keyTeam] = sum( bestResultsByRace )
	
	# Transform into a list of keyTeam, pointsTotal sorted by decreasing points.
	# Break ties with most recent results.
	teamOrder = [
		keyTeam for keyTeam, totalPoints in sorted(teamPoints.items(), key=lambda e: [e[1]] + teamResultsPoints[e[0]], reverse=True)
	]
	
	# Compute the points gap.
	teamGap = {}
	if teamOrder:
		leader = teamOrder[0]
		leaderPoints = teamPoints[leader]
		teamGap = { t : leaderPoints - teamPoints[t] for t in teamOrder }
		teamGap = { t : str(gap) if gap else '' for t, gap in teamGap.items() }
	
	# Reverse the race order if required for display.
	if not showLastToFirst:
		raceNames.reverse()
	
	# List of:
	# team, points, gap, [list of teamResultsPoints for each race in series]
	# Note: only the team results are returned - the individual results are not included.
	categoryResult = [
		[teamName[t], teamPoints[t], teamGap[t]] + [[(teamResultsPoints[t][raceNameIndex[rn]], []) for rn in raceNames]]
		for t in teamOrder
	]
	
	return categoryResult, [raceNameToRaceTuple[rn] for rn in raceNames]

def GetCategoryResultsTeam( categoryName, raceResults, useMostEventsCompleted=False, numPlacesTieBreaker=5 ):
	
	# If this is a combined result, return that.
	if SeriesModel.model.scoreByPoints and not categoryName:
		return GetAllCategoryResultsTeam( raceResults )
	
	model = SeriesModel.model
	
	scoreByPoints = model.scoreByPoints
	scoreByTime = model.scoreByTime
	
	teamResultsN = model.getTeamN( categoryName )
	useNthScore = model.getUseNthScore( categoryName )
	
	showLastToFirst = model.showLastToFirst
	considerPrimePointsOrTimeBonus = model.considerPrimePointsOrTimeBonus
	
	# Get all results for this category and valid teams.
	trn = set( model.teamResultsNames )	
	raceResults = [rr for rr in raceResults if rr.categoryName == categoryName and ((rr.team in trn) if trn else rr.teamIsValid)]
	if not raceResults or not(scoreByPoints or scoreByTime):
		return [], []
		
	# Create a map for race filenames to grade.
	raceGrade = { race.getFileName():race.grade for race in model.races }
	gradesUsed = sorted( set(race.grade for race in model.races) )
	pureTeam = { race.getFileName() for race in model.races if race.pureTeam }
		
	# Get all races for this category.
	races = set( RaceTuple(rr.raceDate, rr.raceName, rr.raceURL, rr.raceInSeries) for rr in raceResults )
	races = sorted( races, key = lambda r: getattr(r[3], 'iSequence', 0) )
	raceSequence = dict( (r.raceInSeries, i) for i, r in enumerate(races) )
	
	def asInt( v ):
		return int(v) if int(v) == v else v
	
	# Get the results for each team for each event.
	teamName = {}
	resultsByTeam = {r.raceInSeries:defaultdict(list) for r in races}
	for rr in raceResults:
		resultsByTeam[rr.raceInSeries][rr.keyTeam()].append( rr )
		teamName[rr.keyTeam()] = rr.team
	
	teamResults = {r.raceInSeries:defaultdict(list) for r in races}
	teamResultsPoints = {r.raceInSeries:defaultdict(int) for r in races}
	teamEventsCompleted = defaultdict( int )
	teamPlaceCount = defaultdict( lambda : defaultdict(int) )
	teamRanks = defaultdict( lambda : defaultdict(int) )
	
	if scoreByPoints:
		# Get the specific pointStructure as a function of the raceName and categoryName.
		# If no pointStructure is specified by category, use the race one as a default.
		pointStructureFromRaceFileName = { r.fileName:r.pointStructure for r in model.races }
		def getPointStructure( raceFileName, categoryName ):
			return model.categories[categoryName].pointStructure or pointStructureFromRaceFileName[raceFileName]
			
		teamPointStructureFromRaceFileName = { r.fileName:r.teamPointStructure for r in model.races }
		def getTeamPointStructure( raceFileName, categoryName ):
			return model.categories[categoryName].teamPointStructure or teamPointStructureFromRaceFileName[raceFileName]
		
		# Get the individual results for each rider, and the total points.
		teamPoints = defaultdict( int )
		for raceInSeries, teamParticipants in resultsByTeam.items():
			pointsStructure = getPointStructure( raceInSeries.fileName, categoryName )
			
			for team, rrs in teamParticipants.items():
				for rr in rrs:
					rider = rr.key()
					primePoints = rr.primePoints if considerPrimePointsOrTimeBonus else 0
					earnedPoints = pointsStructure[rr.rank] + primePoints
					points = asInt( earnedPoints )
					teamResults[raceInSeries][team].append( ResultTuple(points, rr.tFinish, rr.rank, primePoints, 0, rr) )

				teamResults[raceInSeries][team].sort( key=lambda rt: (-rt.points, rt.rank) )
				# Record best scores only.
				teamResults[raceInSeries][team] = teamResults[raceInSeries][team][:teamResultsN]
				teamResultsPoints[raceInSeries][team] += sum( rt.points for rt in teamResults[raceInSeries][team] )
				teamPoints[team] += sum( rt.points for rt in teamResults[raceInSeries][team] )
				teamEventsCompleted[team] += 1
			
			# Rank teams by sum of individual points.  Use individual rank to break ties.
			tr = sorted(
				teamResultsPoints[raceInSeries].keys(),
				key = lambda t: (-teamResultsPoints[raceInSeries][t],) + tuple(rt.rank for rt in teamResults[raceInSeries][t])
			)
			
			# Correct the earned team points based on the team points structure, not the sum of the individual points.
			teamPointStructure = getTeamPointStructure( raceInSeries.getFileName(), categoryName )
			if teamPointStructure:
				def getTeamPointsForRank(team, rank):
					return teamPointStructure[rank]
			else:
				def getTeamPointsForRank(team, rank):
					return teamResultsPoints[raceInSeries][team]
				
			# Get the points for the team rank as specified.  Adjust race results and total.
			for rank, t in enumerate(tr, 1):
				newTeamPoints = getTeamPointsForRank(t, rank)
				teamPoints[t] += newTeamPoints - teamResultsPoints[raceInSeries][t]
				teamResultsPoints[raceInSeries][t] = newTeamPoints
				teamPlaceCount[t][(raceGrade[raceInSeries.getFileName()],rank)] += 1
				teamRanks[raceInSeries][t] = rank

		# Sort by team points - greatest number of points first.  Break ties with the number of place count by race grade, then the last result.
		rankDNF = SeriesModel.rankDNF
		teamOrder = list( teamName.keys() )
		def getBestResults( t ):
			return [-teamResultsPoints[r.raceInSeries][t] for r in reversed(races)]
		
		teamOrder.sort(
			key = lambda t:	[-teamPoints[t]] +
							([-teamEventsCompleted[t]] if useMostEventsCompleted else []) +
							[-teamPlaceCount[t][(g,k)] for g,k in itertools.product(gradesUsed,range(1, numPlacesTieBreaker+1))] +
							getBestResults(t)
		)
		
		# Compute the points gap.
		teamGap = {}
		if teamOrder:
			leader = teamOrder[0]
			leaderPoints = teamPoints[leader]
			teamGap = { t : leaderPoints - teamPoints[t] for t in teamOrder }
			teamGap = { t : str(gap) if gap else '' for t, gap in teamGap.items() }
		
		# Reverse the race order if required for display.
		if showLastToFirst:
			races.reverse()
		
		# List of:
		# team, points, gap, [list of teamResultsPoints for each race in series]
		# Note: only the team results are returned - the individual results are not returned.
		categoryResult = [
			[teamName[t], teamPoints[t], teamGap[t]] + [[(teamResultsPoints[r.raceInSeries][t], teamRanks[r.raceInSeries][t]) for r in races]]
			for t in teamOrder
		]
		return categoryResult, races
		
	elif scoreByTime:
	
		# Score by time.
		# Get the individual results for each rider, and the total time.
		teamTime = defaultdict( int )
		for raceInSeries, teamParticipants in resultsByTeam.items():
			for team, rrs in teamParticipants.items():
				for rr in rrs:
					if rr.rank == SeriesModel.rankDNF:
						continue
					rider = rr.key()
					timeBonus = rr.timeBonus if considerPrimePointsOrTimeBonus else 0
					time = rr.tFinish - timeBonus
					teamResults[raceInSeries][team].append( ResultTuple(0, rr.tFinish, rr.rank, 0, timeBonus, rr) )

				if len(teamResults[raceInSeries][team]) < teamResultsN and raceInSeries.getFileName() not in pureTeam:
					teamResults[raceInSeries][team] = []
					continue
				
				teamResults[raceInSeries][team].sort( key=operator.attrgetter('time', 'rank') )
				
				if useNthScore and raceInSeries.getFileName() not in pureTeam:
					teamResults[raceInSeries][team] = teamResults[raceInSeries][team][teamResultsN-1:teamResultsN]
				else:
					# Record best scores only.
					teamResults[raceInSeries][team] = teamResults[raceInSeries][team][:teamResultsN]
				
				teamTime[team] += sum( rt.time for rt in teamResults[raceInSeries][team] )
				teamEventsCompleted[team] += 1

		# Sort by team time - least time first
		rankDNF = SeriesModel.rankDNF
		teamOrder = list( tn for tn in teamName.keys() if teamTime.get(tn,None) )
		def getBestResults( t ):
			results = []
			for r in reversed(races):
				tr = teamResults[r.raceInSeries][t]
				results.append( tr[0].rank if tr else rankDNF )
			return results
		
		teamOrder.sort(
			key = lambda t:	[-teamEventsCompleted[t], teamTime[t]] + getBestResults( t )
		)
		
		def formatEventCount( count ):
			if not count:
				return ''
			if count < -1:
				return '{} events'.format( count )
			else:
				return '{} event'.format( count )
		
		# Compute the time gap.
		teamGap = {}
		if teamOrder:
			leader = teamOrder[0]
			leaderTime = teamTime[leader]
			leaderEventsCompleted = teamEventsCompleted[leader]
			teamGap = { t : teamTime[t] - leaderTime if teamEventsCompleted[t] == leaderEventsCompleted
					else teamEventsCompleted[t] - leaderEventsCompleted
				for t in teamOrder }
			teamGap = { t : Utils.formatTime(gap) if gap > 0.0 else formatEventCount(gap) for t, gap in teamGap.items() }
		
		# Reverse the race order if required for display.
		if showLastToFirst:
			races.reverse()
		
		# List of:
		# team, points, gap, [list of ResultTuple for each race in series]
		categoryResult = [[teamName[t], Utils.formatTime(teamTime[t]), teamGap[t]] + [[teamResults[r.raceInSeries][t] for r in races]] for t in teamOrder]		
		return categoryResult, races
		
	return [], []

def GetTotalUniqueParticipants( raceResults ):
	return len( set( rr.key() for rr in raceResults ) )
	
def GetTotalUniqueTeams( raceResults ):
	return len( set( rr.keyTeam() for rr in raceResults if rr.teamIsValid ) )
	
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
	for i in range(250):
		pointsForRank[i+1] = 250 - i
		
	pointsForRank = { files[0]: pointsForRank }
	
	for c in categories:
		categoryResult, races, potentialDuplicates = GetCategoryResults( c, raceResults, pointsForRank )
		print ( '--------------------------------------------------------' )
		print ( c )
		print ( '' )
		for rr in categoryResult:
			print( rr[0:5] )
		print ( races )
	#print ( raceResults )
	
