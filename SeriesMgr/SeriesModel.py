import os
import re
import sys
import cgi
import copy
import operator
import functools
import datetime
import GetModelInfo
from FileTrie import FileTrie
from io import StringIO
import Utils

#----------------------------------------------------------------------
class memoize(object):
	"""Decorator that caches a function's return value each time it is called.
	If called later with the same arguments, the cached value is returned, and
	not re-evaluated.
	"""
   
	cache = {}
	
	@classmethod
	def clear( cls ):
		cls.cache = {}
   
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
		"""Return the function's docstring."""
		return self.func.__doc__
		
	def __get__(self, obj, objtype):
		"""Support instance methods."""
		return functools.partial(self.__call__, obj)

def RaceNameFromPath( p ):
	raceName = os.path.basename( p )
	raceName = os.path.splitext( raceName )[0]
	while raceName.endswith('-'):
		raceName = raceName[:-1]
	raceName = raceName.replace( '-', ' ' )
	raceName = raceName.replace( ' ', '-', 2 )
	return raceName

class PointStructure( object ):

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
		return self.dnfPoints if rank == 999999 else self.pointsForPlace.get( rank, self.participationPoints )
	
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
			except:
				continue
		self.pointsForPlace = dict( (i+1, v) for i, v in enumerate(sorted(values, reverse=True)) )
		
	def __repr__( self ):
		return u'({}: {} + {}, dnf={})'.format( self.name, self.getStr(), self.participationPoints, self.dnfPoints )

class Race( object ):
	grade = u'A'
	
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
		self.grade = grade or u'A'
		
	def getRaceName( self ):
		return RaceNameFromPath( self.fileName )
		
	def postReadFix( self ):
		if getattr( self, 'fname', None ):
			self.fileName = getattr(self, 'fname')
			delattr( self, 'fname' )
				
	def getFileName( self ):
		return self.fileName
		
	def __repr__( self ):
		return ', '.join( '{}={}'.format(a, repr(getattr(self, a))) for a in ['fileName', 'pointStructure'] )

class Category( object ):
	name = u''
	iSequence = 0
	publish = False
	teamN = 3
	useNthScore = False
	teamPublish = False
	
	def __init__( self, name, iSequence=0, publish=True, teamN=3, useNthScore=False, teamPublish=True ):
		self.name = name
		self.iSequence = iSequence
		self.publish = publish
		self.teamN = teamN
		self.useNthScore = useNthScore
		self.teamPublish = teamPublish
		
	def __eq__( self, other ):
		return self.__dict__ == other.__dict__
		
	def __ne__( self, other ):
		return self.__dict__ != other.__dict__
		
	def __repr__( self ):
		return 'Category(name="{}", iSequence={}, publish={}, teamN={}, useNthScore={}, teamPublish={})'.format(
			self.name, self.iSequence, self.publish, self.teamN, self.useNthScore, self.teamPublish
		)

class SeriesModel( object ):
	DefaultPointStructureName = 'Regular'
	useMostEventsCompleted = False
	scoreByTime = False
	scoreByPercent = False
	scoreByTrueSkill = False
	considerPrimePointsOrTimeBonus = True
	
	licenseLinkTemplate = u''	# Used to create an html link from the rider's license number in the html output.
	bestResultsToConsider = 0	# 0 == all
	mustHaveCompleted = 0		# Number of events to complete to be eligible for results.
	organizer = u''
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
	referenceLicenses = []
	referenceTeams = []
	aliasLookup = {}
	aliasLicenseLookup = {}
	aliasTeamLookup = {}

	ftpHost = ''
	ftpPath = ''
	ftpUser = ''
	ftpPassword = ''
	urlPath = ''
	
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
		
	def postReadFix( self ):
		memoize.clear()
		for r in self.races:
			r.postReadFix()
	
	def setPoints( self, pointsList ):
		oldPointsList = [(p.name, p.name, p.getStr(), u'{}'.format(p.participationPoints), u'{}'.format(p.dnfPoints))
			for p in self.pointStructures]
		if oldPointsList == pointsList:
			return
			
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
			
		for r in self.races:
			r.pointStructure = newPS.get( oldToNewName.get(r.pointStructure.name, ''), newPointStructures[0] )
			if r.teamPointStructure:
				r.teamPointStructure = newPS.get( oldToNewName.get(r.teamPointStructure.name, ''), None )
			
		self.pointStructures = newPointStructures
		self.setChanged()
	
	def setRaces( self, raceList ):
		if [(r.fileName, r.pointStructure.name, r.teamPointStructure.name if r.teamPointStructure else None, r.grade) for r in self.races] == raceList:
			return
		
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
		
	def setReferences( self, references ):
		dNew = dict( references )
		dExisting = dict( self.references )
		
		changed = (len(dNew) != len(dExisting))
		updated = False
		
		for name, aliases in dNew.items():
			if name not in dExisting:
				changed = True
				if aliases:
					updated = True
			elif aliases != dExisting[name]:
				changed = True
				updated = True
	
		for name, aliases in dExisting.items():
			if name not in dNew:
				changed = True
				if aliases:
					updated = True
				
		if changed:
			self.changed = changed
			self.references = references
			self.aliasLookup = {}
			for name, aliases in self.references:
				for alias in aliases:
					key = tuple( [Utils.removeDiacritic(n).lower() for n in alias] )
					self.aliasLookup[key] = name				
	
		#if updated:
		#	memoize.clear()
	
	def setReferenceLicenses( self, referenceLicenses ):
		dNew = dict( referenceLicenses )
		dExisting = dict( self.referenceLicenses )
		
		changed = (len(dNew) != len(dExisting))
		updated = False
		
		for name, aliases in dNew,items():
			if name not in dExisting:
				changed = True
				if aliases:
					updated = True
			elif aliases != dExisting[name]:
				changed = True
				updated = True
	
		for name, aliases in dExisting.items():
			if name not in dNew:
				changed = True
				if aliases:
					updated = True
				
		if changed:
			self.changed = changed
			self.referenceLicenses = referenceLicenses
			self.aliasLicenseLookup = {}
			for license, aliases in self.referenceLicenses:
				for alias in aliases:
					key = Utils.removeDiacritic(alias).upper()
					self.aliasLicenseLookup[key] = license				
	
		#if updated:
		#	memoize.clear()
	
	
	def setReferenceTeams( self, referenceTeams ):
		dNew = dict( referenceTeams )
		dExisting = dict( self.referenceTeams )
		
		changed = (len(dNew) != len(dExisting))
		updated = False
		
		for name, aliases in dNew.items():
			if name not in dExisting:
				changed = True
				if aliases:
					updated = True
			elif aliases != dExisting[name]:
				changed = True
				updated = True
	
		for name, aliases in dExisting.items():
			if name not in dNew:
				changed = True
				if aliases:
					updated = True
				
		if changed:
			self.changed = changed
			self.referenceTeams = referenceTeams
			self.aliasTeamLookup = {}
			for Team, aliases in self.referenceTeams:
				for alias in aliases:
					key = Utils.removeDiacritic(alias).upper()
					self.aliasTeamLookup[key] = Team				
	
		#if updated:
		#	memoize.clear()
	
	def getReferenceName( self, lastName, firstName ):
		key = (Utils.removeDiacritic(lastName).lower(), Utils.removeDiacritic(firstName).lower())
		try:
			return self.aliasLookup[key]
		except KeyError:
			self.aliasLookup[key] = (lastName, firstName)
			return lastName, firstName
	
	def getReferenceLicense( self, license ):
		key = Utils.removeDiacritic(license).upper()
		return self.aliasLicenseLookup.get( key, key )
	
	def getReferenceTeam( self, team ):
		key = Utils.removeDiacritic(team).upper()
		return self.aliasTeamLookup.get( key, team )
	
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
		
	def getMetaTags( self ):
		return (
			('author', 'Edward Sitarski'),
			('copyright', "Edward Sitarski, 2013-{}".format(datetime.datetime.now().year)),
			('description', 'Series: {}, Races: {}'.format(
					cgi.escape(self.name, quote=True),
					u';'.join('{}'.format(cgi.escape(n, quote=True)) for n in self.getRaceNames())
				)
			),
			('generator', "SeriesMgr"),
			('keywords', "CrossMgr, SeriesMgr, cycling, race, series, results"),
		)
	
	def clearCache( self ):
		memoize.clear()		
	
	@memoize
	def _extractAllRaceResultsCore( self ):
		raceResults = []
		oldErrors = self.errors
		self.errors = []
		for r in self.races:
			success, ex, results = GetModelInfo.ExtractRaceResults( r )
			if success:
				raceResults.extend( results )
			else:
				self.errors.append( (r, ex) )
		if oldErrors != self.errors:
			self.changed = True
		self.harmonizeCategorySequence( raceResults )
		return raceResults
	
	def extractAllRaceResults( self, adjustForUpgrades=True, isIndividual=True ):
		raceResults = self._extractAllRaceResultsCore()
		if adjustForUpgrades:
			raceResults = copy.deepcopy( raceResults )
			GetModelInfo.AdjustForUpgrades( raceResults )
		
		rt = { r.fileName for r in self.races
				if r.resultsType == Race.IndividualAndTeamResults or
					(isIndividual and r.resultsType == Race.IndividualResultsOnly) or
					(not isIndividual and r.resultsType == Race.TeamResultsOnly)
		}
		return [rr for rr in raceResults if rr.raceFileName in rt]
			
model = SeriesModel()
