import os
from html import escape
import copy
import operator
import functools
import datetime
import threading
from multiprocessing import Pool
import GetModelInfo
from FileTrie import FileTrie
from io import StringIO
import Utils
from RelativePath import FullToRelative, RelativeToFull

#----------------------------------------------------------------------
class memoize:
	"""Decorator that caches a function's return value each time it is called.
	If called later with the same arguments, the cached value is returned, and
	not re-evaluated.
	"""
   
	cache = {}
	
	@classmethod
	def clear( cls ):
		cls.cache.clear()
   
	def __init__(self, func):
		# print( 'memoize:', func.__name__ )
		self.func = func
		
	def __call__(self, *args):
		# print( self.func.__name__, args )
		try:
			return memoize.cache[self.func.__name__][args]
		except KeyError:
			value = self.func(*args)
			memoize.cache.setdefault(self.func.__name__, {})[args] = value
			return value
		except TypeError:
			# uncachable -- for instance, passing a list as an argument.
			# Better to not cache than to blow up entirely.
			return self.func(*args)
			
	def __repr__(self):
		# Return the function's docstring.
		return self.func.__doc__
		
	def __get__(self, obj, objtype):
		# Support instance methods.
		return functools.partial(self.__call__, obj)

def RaceNameFromPath( p, isUCIDataride=False ):
	if isUCIDataride:
		folderName = os.path.basename( os.path.dirname(p) )
		baseFileName = os.path.splitext( os.path.basename(p) )[0]
		raceName = '/'.join( folderName, baseFileName )
		return raceName
	else:
		raceName = os.path.basename( p )
		raceName = os.path.splitext( raceName )[0]
		while raceName.endswith('-'):
			raceName = raceName[:-1]
		raceName = raceName.replace( '-', ' ' )
		raceName = raceName.replace( ' ', '-' )
		return raceName

class PointStructure:

	participationPoints = 0
	dnfPoints = 0

	def __init__( self, name, pointsStr=None, participationPoints=0, dnfPoints=0 ):
		self.name = name
		if pointsStr is not None:
			self.setStr( pointsStr )
		else:
			self.setOCAOCup()
		self.participationPoints = participationPoints
		self.dnfPoints = dnfPoints
		
	def __getitem__( self, rank ):
		rank = int(rank)
		return self.dnfPoints if rank == rankDNF else self.pointsForPlace.get( rank, self.participationPoints )
	
	def __len__( self ):
		return len(self.pointsForPlace)
	
	def setUCIWorldTour( self ):
		self.pointsForPlace = { 1:100, 2:80, 3:70, 4:60, 5:50, 6:40, 7:30, 8:20, 9:10, 10:4 }
		
	def setOCAOCup( self ):
		self.pointsForPlace = { 1:25, 2:20, 3:16, 4:13, 5:11, 6:10, 7:9, 8:8, 9:7, 10:6, 11:5, 12:4, 13:3, 14:2, 15:1 }
	
	def getStr( self ):
		return ', '.join( '{}'.format(points) for points in sorted(self.pointsForPlace.values(), reverse=True) )
	
	def getHtml( self ):
		values = [(pos, points) for pos, points in self.pointsForPlace.items()]
		values.sort()
		
		html = StringIO()
		html.write( '<table class="points">\n' )
		html.write( '<tbody>\n' )
		
		pointsRange = []
		pointsForRange = []
		for i, (pos, points) in enumerate(values):
			if len(pointsRange) == i//10:
				lb, ub = i+1, min(i+10, len(values))
				if lb != ub:
					pointsRange.append( '{}-{}'.format(lb, ub) )
				else:
					pointsRange.append( '{}'.format(lb) )
					
				pointsForRange.append( [] )
			pointsForRange[-1].append( points )
			
		for i, (r, pfr) in enumerate(zip(pointsRange, pointsForRange)):
			html.write( '<tr{}>'.format(' class="odd"' if i & 1 else '') )
			html.write( '<td class="points-cell">{}:</td>'.format(r) )
			for p in pfr:
				html.write( '<td class="points-cell">{}</td>'.format(p) )
			html.write( '</tr>\n' )
			
		if self.participationPoints != 0:
			html.write( '<tr>' )
			html.write( '<td class="points-cell">Participation:</td>' )
			html.write( '<td class="points-cell">{}</td>'.format(self.participationPoints) )
			html.write( '</tr>\n' )
			
		if self.dnfPoints != 0:
			html.write( '<tr>' )
			html.write( '<td class="points-cell">DNF:</td>' )
			html.write( '<td class="points-cell">{}</td>'.format(self.dnfPoints) )
			html.write( '</tr>\n' )
			
		html.write( '</tbody>\n' )
		html.write( '</table>\n' )
		return html.getvalue()
	
	def setStr( self, s ):
		s = s.replace( ',', ' ' )
		values = []
		for v in s.split():
			try:
				values.append( int(v) )
			except Exception:
				continue
		self.pointsForPlace = dict( (i+1, v) for i, v in enumerate(sorted(values, reverse=True)) )
		
	def __repr__( self ):
		return '({}: {} + {}, dnf={})'.format( self.name, self.getStr(), self.participationPoints, self.dnfPoints )

class Race:
	grade = 'A'
	
	IndividualResultsOnly = 0
	TeamResultsOnly = 1
	IndividualAndTeamResults = 2
	resultsType = IndividualAndTeamResults
	
	pureTeam = False	# True if the results are by pure teams, that is, no individual results.
	teamPointStructure = None	# If specified, team points will be recomputed from the top individual results.
	
	def __init__( self, fileName, pointStructure, teamPointStructure=None, grade=None ):
		self.fileName = fileName
		self.pointStructure = pointStructure
		self.teamPointStructure = teamPointStructure
		self.grade = grade or 'A'
		
	def getRaceName( self ):
		return RaceNameFromPath( self.fileName )
		
	def postReadFix( self ):
		if getattr( self, 'fname', None ):
			self.fileName = getattr(self, 'fname')
			delattr( self, 'fname' )
				
	def getFileName( self ):
		return self.fileName
		
	def fullToRelative( self, source ):
		self.fileName = FullToRelative( source, self.fileName )
		
	def relativeToFull( self, source ):
		self.fileName = RelativeToFull( source, self.fileName )
		
	def __repr__( self ):
		return ', '.join( '{}={}'.format(a, repr(getattr(self, a))) for a in ['fileName', 'pointStructure'] )

class Category:
	name = ''
	longName = ''
	iSequence = 0

	publish = False					# If true, generate results for this category.
	pointStructure = None			# Override the pointStructure for this category.  If undefined, use the one from the Event.
	bestResultsToConsider = None	# Override the bestResultsToConsider for this category.
	mustHaveCompleted = None		# Override the mustHaveCompleted for this category.
	
	teamPublish = False				# If true, generate team results for this category.
	teamPointStructure = None		# Override the teamPointStructure for this category.  If undefined, use the one from the Event.
	useNthScore = False				# Flag indicating to use top Nth scoring team member.
	teamN = 3						# Top N team members to use.
	
	def __init__( self,
			name, longName='',
			iSequence=0,
			publish=True, pointStructure=None, bestResultsToConsider=None, mustHaveCompleted=None,
			teamPublish=True, teamPointStructure=None, useNthScore=False, teamN=3,
		):
		self.name = name
		self.longName = longName
		self.iSequence = iSequence
		
		self.publish = publish
		self.pointStructure = pointStructure
		self.bestResultsToConsider = bestResultsToConsider
		self.mustHaveCompleted = mustHaveCompleted

		self.teamPublish = teamPublish
		self.teamPointStructure = teamPointStructure
		self.useNthScore = useNthScore
		self.teamN = teamN		
		
	def __eq__( self, other ):
		return self.__dict__ == other.__dict__
		
	def __ne__( self, other ):
		return self.__dict__ != other.__dict__
		
	def __repr__( self ):
		return f'Category(name="{self.name}", iSequence={self.iSequence}, pointStructure={self.pointStructure.name if self.pointStructure else None}, publish={self.publish}, teamN={self.teamN}, useNthScore={self.useNthScore}, teamPublish={self.teamPublish})'
		
	def getName( self ):
		return self.longName or self.name

def nameToAliasKey( name ):
	no_accent_name = Utils.removeDiacritic( name )
	if len(no_accent_name) == len(name):
		return no_accent_name.lower()
	else:
		# If characters are lost, the name contains non-roman characters.  Just return what we have.
		return name.lower()

# "Special" rank codes.
rankDNF					= 999999
rankDidNotParticipate	= 9999999
rankUnknown				= 99999999

modelUpdateLock = threading.Lock()

class SeriesModel:
	DefaultPointStructureName = 'Regular'
	useMostEventsCompleted = False
	scoreByTime = False
	scoreByPercent = False
	scoreByTrueSkill = False
	considerPrimePointsOrTimeBonus = True
	scoreByPointsInput = False
	
	licenseLinkTemplate = ''	# Used to create an html link from the rider's license number in the html output.
	bestResultsToConsider = 0	# 0 == all
	mustHaveCompleted = 0		# Number of events to complete to be eligible for results.
	organizer = ''
	upgradePaths = []
	upgradeFactors = []
	showLastToFirst = True		# If True, show the latest races first in the output.
	postPublishCmd = ''
	
	categorySequence = {}
	categorySequencePrevious = {}
	categoryHide = set()
	categories = {}
	categoriesPrevious = {}
	
	references = []
	aliasLookup = {}

	referenceLicenses = []
	aliasLicenseLookup = {}

	referenceTeams = []
	aliasTeamLookup = {}

	referenceCategories = []	
	aliasCategoryLookup = {}

	ftpHost = ''
	ftpPath = ''
	ftpUser = ''
	ftpPassword = ''
	urlPath = ''
	
	graphicBase64 = None
	
	# Control how to identify riders: name, uciid or license.
	KeyByName, KeyByUciId, KeyByLicense = list(range(3))
	riderKey = KeyByName
	
	imageResource = None	# Display Logo (None uses default logo).  In base64.
	
	CategoryTeamResultsOnly, CombinedTeamResultsOnly, AllTeamResults = list( range(3) )
	teamResultsOption = CategoryTeamResultsOnly
	
	GreenTheme, RedTheme = list( range(2) )
	colorTheme = GreenTheme
	
	teamResultsNames = []
	
	@property
	def scoreByPoints( self ):
		return not (self.scoreByTime or self.scoreByPercent or self.scoreByTrueSkill)

	def __init__( self ):
		self.name = '<Series Name>'
		self.races = []
		self.pointStructures = [PointStructure(self.DefaultPointStructureName)]
		self.numPlacesTieBreaker = 5
		self.errors = []
		self.changed = False
		self.imageResource = None
		self.colorTheme = self.GreenTheme
		self.teamResultsList = []
		
	def postReadFix( self ):
		memoize.clear()
		for r in self.races:
			r.postReadFix()
	
	def setPoints( self, pointsList ):
		oldPointsList = [(p.name, p.name, p.getStr(), '{}'.format(p.participationPoints), '{}'.format(p.dnfPoints))
			for p in self.pointStructures]
		if oldPointsList == pointsList:
			return
			
		# Create new points structures, and create a mapping from the old names to the new names.
		newPointStructures = []
		oldToNewName = {}
		newPS = {}
		for name, oldName, points, participationPoints, dnfPoints in pointsList:
			name = name.strip()
			oldName = oldName.strip()
			points = points.strip()
			if not name or name in newPS:
				continue
			participationPoints = int(participationPoints or '0')
			dnfPoints = int(dnfPoints or '0')
			ps = PointStructure( name, points, participationPoints, dnfPoints )
			oldToNewName[oldName] = name
			newPS[name] = ps
			newPointStructures.append( ps )
			
		if not newPointStructures:
			newPointStructures = [PointStructure(self.DefaultPointStructureName)]
		
		# Correct the pointStructure pointers to point to the new structures.
		for r in self.races:
			r.pointStructure = newPS.get( oldToNewName.get(r.pointStructure.name, ''), newPointStructures[0] )
			if r.teamPointStructure:
				r.teamPointStructure = newPS.get( oldToNewName.get(r.teamPointStructure.name, ''), None )
			
		# Correct any category-specific points structures.
		for c in self.categories.values():
			if c.pointStructure:
				c.pointStructure = newPS.get( oldToNewName.get(c.pointStructure.name, ''), None )
			
		self.pointStructures = newPointStructures
		self.setChanged()
	
	def racesFullToRelative( self, source ):
		# source = os.path.abspath( source )
		# for r in self.races:
		#	r.fullToRelative( source )
		pass
	
	def racesRelativeToFull( self, source ):
		# source = os.path.abspath( source )
		# for r in self.races:
		#	r.relativeToFull( source )
		pass
	
	def setRaces( self, raceList ):
		if [(r.fileName, r.pointStructure.name, r.teamPointStructure.name if r.teamPointStructure else None, r.grade) for r in self.races] == raceList:
			return False
		
		self.setChanged()
		
		racesSeen = set()
		newRaces = []
		ps = { p.name:p for p in self.pointStructures }
		for fileName, pname, pteamname, grade in raceList:
			fileName = fileName.strip()
			if not fileName or fileName in racesSeen:
				continue
			racesSeen.add( fileName )
			
			pname = pname.strip()
			try:
				p = ps[pname]
			except KeyError:
				continue
			pt = ps.get( pteamname, None )
			newRaces.append( Race(fileName, p, pt, grade) )
			
		self.races = newRaces
		for i, r in enumerate(self.races):
			r.iSequence = i
		return True
		
	def setReferences( self, references ):
		dNew = dict( references )
		dExisting = dict( self.references )
		
		changed = (len(dNew) != len(dExisting))
		
		for name, aliases in dNew.items():
			if name not in dExisting:
				changed = True
			elif aliases != dExisting[name]:
				changed = True
	
		for name, aliases in dExisting.items():
			if name not in dNew:
				changed = True
				
		if changed:
			self.changed = changed
			self.references = references
			self.aliasLookup = {}
			for name, aliases in self.references:
				for alias in aliases:
					key = tuple( [nameToAliasKey(n) for n in alias] )
					self.aliasLookup[key] = name				
	
	def setReferenceLicenses( self, referenceLicenses ):
		dNew = dict( referenceLicenses )
		dExisting = dict( self.referenceLicenses )
		
		changed = (len(dNew) != len(dExisting))
		
		for name, aliases in dNew.items():
			if name not in dExisting:
				changed = True
			elif aliases != dExisting[name]:
				changed = True
	
		for name, aliases in dExisting.items():
			if name not in dNew:
				changed = True
				
		if changed:
			self.changed = changed
			self.referenceLicenses = referenceLicenses
			self.aliasLicenseLookup = {}
			for license, aliases in self.referenceLicenses:
				for alias in aliases:
					key = Utils.removeDiacritic(alias).upper()
					self.aliasLicenseLookup[key] = license				
		
	def setReferenceTeams( self, referenceTeams ):
		dNew = dict( referenceTeams )
		dExisting = dict( self.referenceTeams )
		
		changed = (len(dNew) != len(dExisting))
		
		for name, aliases in dNew.items():
			if name not in dExisting:
				changed = True
			elif aliases != dExisting[name]:
				changed = True
	
		for name, aliases in dExisting.items():
			if name not in dNew:
				changed = True
				
		if changed:
			self.changed = changed
			self.referenceTeams = referenceTeams
			self.aliasTeamLookup = {}
			for team, aliases in self.referenceTeams:
				for alias in aliases:
					key = nameToAliasKey( alias )
					self.aliasTeamLookup[key] = team				
	
	def setReferenceCategories( self, referenceCategories ):
		dNew = dict( referenceCategories )
		dExisting = dict( self.referenceCategories )
		
		changed = (len(dNew) != len(dExisting))
		
		for name, aliases in dNew.items():
			if name not in dExisting:
				changed = True
			elif aliases != dExisting[name]:
				changed = True
	
		for name, aliases in dExisting.items():
			if name not in dNew:
				changed = True
				
		if changed:
			self.changed = changed
			self.referenceCategories = referenceCategories
			self.aliasCategoryLookup = {}
			for category, aliases in self.referenceCategories:
				for alias in aliases:
					key = nameToAliasKey( alias )
					self.aliasCategoryLookup[key] = category				
	
	def getReferenceName( self, lastName, firstName ):
		key = (nameToAliasKey(lastName), nameToAliasKey(firstName))
		alias = self.aliasLookup.get( key, None )
		return alias if alias is not None else (lastName, firstName)
	
	def getReferenceLicense( self, license ):
		if license is None:
			return license
		key = Utils.removeDiacritic(license).upper()
		return self.aliasLicenseLookup.get( key, key )
	
	def getReferenceTeam( self, team ):
		if team is None:
			return team
		team = self.aliasTeamLookup.get( nameToAliasKey(team), team )
		if team.lower() in {'independent', 'ind.', 'ind', 'none', 'no team'}:
			return ''
		return team
	
	def getReferenceCategory( self, categoryName ):
		if categoryName is None:
			return categoryName
		# print( f'"{self.aliasCategoryLookup.get( nameToAliasKey(categoryName), categoryName )}"="{categoryName}"' )
		return self.aliasCategoryLookup.get( nameToAliasKey(categoryName), categoryName )
	
	def fixCategories( self ):
		categorySequence = getattr( self, 'categorySequence', None )
		if self.categorySequence or not isinstance(self.categories, dict):
			self.categories = {name:Category(name, i, name not in self.categoryHide) for name, i in categorySequence.items() }
			self.categorySequence = {}
			self.categoryHide = {}
	
	def setCategories( self, categoryList ):
		self.fixCategories()
		for i, c in enumerate(categoryList):
			c.iSequence = i
		
		categories = {c.name: c for c in categoryList}
		if self.categories != categories:
			self.categories = categories
			self.setChanged()
	
	def harmonizeCategorySequence( self, raceResults ):
		self.fixCategories()
		
		categoriesFromRaces = set(rr.categoryName for rr in raceResults)
		if not categoriesFromRaces:
			if self.categories:
				self.categories = {}
				self.setChanged()
			return
		
		categories = (self.categories or self.categoriesPrevious)
		categoryNamesCur = set( self.categories.keys() )
		categoryNamesNew = categoriesFromRaces - categoryNamesCur
		categoryNamesDel = categoryNamesCur - categoriesFromRaces

		categoryList = sorted( (c for c in categories.values() if c.name not in categoryNamesDel), key=operator.attrgetter('iSequence') )
		categoryList.extend( [Category(name) for name in sorted(categoryNamesNew)] )
		for i, c in enumerate(categoryList):
			c.iSequence = i
		
		categoriesNew = { c.name:c for c in categoryList }
		self.categoriesPrevious = categoriesNew
		if self.categories != categoriesNew:
			self.categories = categoriesNew
			self.setChanged()
			
	def getCategoriesSorted( self ):
		self.fixCategories()
		return sorted( self.categories.values(), key=operator.attrgetter('iSequence') )
		
	def getCategoriesSortedPublish( self ):
		self.fixCategories()
		return [c for c in self.getCategoriesSorted() if c.publish]
	
	def getCategoriesSortedTeamPublish( self ):
		self.fixCategories()
		return [c for c in self.getCategoriesSorted() if c.teamPublish]
	
	def getCategoryNamesSortedPublish( self ):
		return [c.name for c in self.getCategoriesSortedPublish()]
	
	def getCategoryNamesSortedTeamPublish( self ):
		return [c.name for c in self.getCategoriesSortedTeamPublish()]
	
	def getCategoryDisplayNames( self ):
		return {c.name:c.getName() for c in self.getCategoriesSorted()}
	
	def getTeamN( self, categoryName ):
		self.fixCategories()
		try:
			return self.categories[categoryName].teamN
		except KeyError:
			return 3
		
	def getUseNthScore( self, categoryName ):
		self.fixCategories()
		try:
			return self.categories[categoryName].useNthScore
		except KeyError:
			return False
	
	def setRootFolderWillSucceed( self, path ):
		ft = FileTrie()
		for top, directories, files in os.walk(path):
			for f in files:
				ft.add( os.path.join(top, f) )				
		return all( ft.best_match( r.fileName ) for r in self.races )
	
	def setRootFolder( self, path ):
		ft = FileTrie()
		for top, directories, files in os.walk(path):
			for f in files:
				ft.add( os.path.join(top, f) )
		
		success = False
		for r in self.races:
			m = ft.best_match( r.fileName )
			if m:
				r.fileName = m
				success = True
				self.setChanged()
		
		return success
	
	def setChanged( self, changed = True ):
		self.changed = changed
		if changed:
			memoize.clear()
	
	def addRace( self, name ):
		race = Race( name, self.pointStructures[0] )
		
		# Check if this race name matches an existing one and use the same pointsStructure.
		# This works for UCIDataride spreadsheets.
		for r in reversed(self.races):
			if r.getRaceName() == race.getRaceName():
				race.pointStructure = r.pointStructure
				race.teamPointStructure = r.teamPointStructure
				break
		
		self.races.append( race )
		self.setChanged()
		
	def removeRace( self, name ):
		raceCount = len(self.races)
		self.races = [r for r in self.races if r.fileName != name]
		if raceCount != len(self.races):
			self.setChanged()
			
	def removeAllRaces( self ):
		if self.races:
			self.races = []
			self.setChanged()
	
	def getRaceNames( self ):
		names = set()
		for r in self.races:
			names.add( os.path.splitext(os.path.basename(r.fileName))[0] )
		return sorted( names )
		
	def setTeamResultsNames( self, teamResultsNames ):
		teamResultsNames = sorted( set(n for n in map(operator.methodcaller('strip'), teamResultsNames) if n ) )
		if teamResultsNames != self.teamResultsNames:
			self.teamResultsNames = teamResultsNames
			self.setChanged()
			return True
		return False
		
	def getMetaTags( self ):
		return (
			('author', 'Edward Sitarski'),
			('copyright', "Edward Sitarski, 2013-{}".format(datetime.datetime.now().year)),
			('description', 'Series: {}, Races: {}'.format(
					escape(self.name, quote=True),
					';'.join('{}'.format(escape(n, quote=True)) for n in self.getRaceNames())
				)
			),
			('generator', "SeriesMgr"),
			('keywords', "CrossMgr, SeriesMgr, cycling, race, series, results"),
		)
	
	def clearCache( self ):
		memoize.clear()		
	
	@memoize
	def _extractAllRaceResultsCore( self ):
		with modelUpdateLock:	
			# Extract all race results in parallel.  Arguments are the race info and this series.
			if self.races:
				# p_results = map( GetModelInfo.ExtractRaceResults, [r.fileName for r in self.races] )
				with Pool() as p:
					p_results = p.map( GetModelInfo.ExtractRaceResults, [r.fileName for r in self.races] )
			else:
				p_results = []
			
			# Combine all results and record any errors.
			raceResults = []
			self.errors = []
			for ret, r in zip(p_results, self.races):
				# Set race attributes.
				for a in ('isUCIDataride', 'pureTeam', 'resultsType'):
					setattr( r, a, ret[a] )
				if ret['success']:
					for rr in ret['raceResults']:
						rr.raceInSeries = r
					raceResults.extend( ret['raceResults'] )
					if ret['licenseLinkTemplate']:
						self.licenseLinkTemplate = ret['licenseLinkTemplate']
				else:
					self.errors.append( (r, ret['explanation']) )
					
		return raceResults

	def extractAllRaceResults( self, adjustForUpgrades=True, isIndividual=True ):
		# Purge any existing key errors.
		oldErrors = self.errors
		keyErrorPrefix = '** '
		self.errors = [ (r,e) for r,e in self.errors if not e.startswith(keyErrorPrefix) ]

		# Get a copy of the potenially cached race results.  This will also reset self.errors.
		raceResults = copy.deepcopy( self._extractAllRaceResultsCore() )
		
		# Remove race results with missing keys.  Add corresponding errors to list.
		if self.riderKey == self.KeyByUciId:
			# If matching by UCI ID, remove all riders without a UCI ID and record those missing one as errors.
			self.errors.extend(
				(rr.raceInSeries, f'{keyErrorPrefix}Missing UCI ID: ({rr.categoryName}) {rr.lastName}, {rr.firstName}') for rr in raceResults if not rr.uci_id
			)
			raceResults = [rr for rr in raceResults if rr.uci_id]
		elif self.riderKey == self.KeyByLicense:
			# If matching by license, remove all riders without a license and record those missing one as errors.
			self.errors.extend(
				(rr.raceInSeries, f'{keyErrorPrefix}Missing License: ({rr.categoryName}) {rr.lastName}, {rr.firstName}') for rr in raceResults if not rr.license
			)
			raceResults = [rr for rr in raceResults if rr.license]

		# Set the change flag if the errors change.
		self.changed |= (oldErrors != self.errors)
		
		# Assign a sequence number to the races in the specified order.
		# Track the race filename so we can consolidate the race objects after the deep copy.
		raceFromFileName = {}
		for i, r in enumerate(self.races):
			r.iSequence = i
			raceFromFileName[r.fileName] = r
			
		# Try to fix missing teams based on the uciid.
		# Defaults to the most recent team.
		teamFromUCIID = { rr.uci_id:rr.team for rr in raceResults if rr.uci_id and rr.team }
		
		# Apply all aliases.
		for rr in raceResults:
			rr.categoryName = self.getReferenceCategory( rr.categoryName )
			rr.lastName, rr.firstName = self.getReferenceName( rr.lastName, rr.firstName )
			rr.license = self.getReferenceLicense( rr.license )
			if rr.uci_id and not rr.team:	# If we are missing the team, try to use a previously used team.
				rr.team = teamFromUCIID.get( rr.uci_id, '' )
			rr.team = self.getReferenceTeam( rr.team )
			rr.raceFileName = rr.raceInSeries.fileName
			rr.raceInSeries = raceFromFileName.get( rr.raceInSeries.fileName, rr.raceInSeries )	# Normalize the deepcopied raceInSeries.
		
		# Harmonize the categories *after* we have applied the category aliases.
		self.harmonizeCategorySequence( raceResults )
		
		if adjustForUpgrades:
			GetModelInfo.AdjustForUpgrades( raceResults )
			
		# Filter by configured races.
		rt = { r.fileName for r in self.races
				if r.resultsType == Race.IndividualAndTeamResults or
					(isIndividual and r.resultsType == Race.IndividualResultsOnly) or
					(not isIndividual and r.resultsType == Race.TeamResultsOnly)
		}
		return [rr for rr in raceResults if rr.raceFileName in rt]
			
model = SeriesModel()
