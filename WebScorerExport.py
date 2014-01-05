import io
import math
import Utils
import datetime
import Model
from GetResults import GetResults, GetCategoryDetails

WebScorerFields = (
	('Place',		'pos'),
	('Bib',			'num'),
	('Last name',	'LastName'),
	('First name',	'FirstName'),
	('Team name',	'Team'),
	('Age',			'Age'),
	('Time',		'lastTime'),
)

WebScorerCategoryFields = (
	'Category',
	'Distance',
	'Gender',
)

def formatTime( secs ):
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
	decimal = '.%03d' % int( f * 1000 )
	return "%s%02d:%02d:%02d%s" % (sign, hours, minutes, secs, decimal)

def WebScorerExport( fname ):
	race = Model.race
	if not race:
		return
	
	hasField = [False] * len(WebScorerFields)
	hasField[0] = True
	hasField[1] = True
	
	# Check for what fields are actually filled in.
	publishCategories = race.getCategories( startWaveOnly = False, uploadOnly = True )
	for cat in publishCategories:
		results = GetResults( cat, True )
		if not results:
			continue
		for rr in results:
			for i, (field, cmgrField) in enumerate(WebScorerFields):
				if getattr(rr, cmgrField, None):
					hasField[i] = True
	
	if not hasField[2]:
		return False, _('"LastName" must be linked to a column in the Excel sheetl')
	
	catDetails = dict( (cd['name'], cd) for cd in GetCategoryDetails() )
	
	# Filter the fields by what exists in the data.
	webScorerFields = [WebScorerFields[i][0] for i in xrange(len(hasField)) if hasField[i]]
	webScorerToCrossMgr = dict( (ws, cm) for ws, cm in WebScorerFields )
	
	hasDistance = False
	maxLaps = 0
	for cat in publishCategories:
		results = GetResults( cat, True )
		if not results:
			continue
		cd = catDetails[cat.fullname]
		if cd.get('raceDistance', None):
			hasDistance = True
		for rr in results:
			maxLaps = max( maxLaps, rr.laps )
	if maxLaps == 1 or maxLaps > 99:
		maxLaps = 0
		
	webScorerCategoryFields = [f for f in WebScorerCategoryFields if (hasDistance or f != 'Distance')]
	
	colNames = webScorerFields + webScorerCategoryFields + [u'Lap {}'.format(i+1) for i in xrange(maxLaps)]
	
	with io.open(fname, 'w', encoding = 'utf-16') as txtFile:
		txtFile.write( u'{}\n'.format( u'\t'.join(unicode(c) for c in colNames) ) )
		
		for cat in publishCategories:
			results = GetResults( cat, True )
			if not results:
				continue
			
			cd = catDetails[cat.fullname]
			raceDistance = cd.get('raceDistance', '')
			raceDistanceType = cd.get('distanceUnit', '')
			if raceDistance:
				distance = u'{:.2f} {}'.format( raceDistance, raceDistanceType )
			else:
				distance = u''
				
			if cat.gender.startswith( 'M' ):
				gender = 'M'
			elif cat.gender.startswith( 'W' ):
				gender = 'F'
			else:
				gender = ''
			
			for rr in results:
				dataRow = []
				
				# Rider Fields.
				for field in webScorerFields:
					if field == 'Place':
						dataRow.append( 'DNP' if rr.pos in {'NP', 'OTL', 'PUL'} else rr.pos )
					elif field == 'Time':
						dataRow.append( formatTime(rr.lastTime) if rr.lastTime else '' )
					else:
						dataRow.append( getattr(rr, webScorerToCrossMgr[field], '') )

				# Category Fields.
				dataRow.append( cat.name )
				if hasDistance:
					dataRow.append( distance )
				dataRow.append( gender )
					
				# Lap Times.
				for i in xrange(maxLaps):
					try:
						lapTime = formatTime(rr.lapTimes[i])
					except IndexError:
						lapTime = ''
					dataRow.append( lapTime )
				
				txtFile.write( u'{}\n'.format( u'\t'.join(unicode(d).strip().replace(u'\t','    ') for d in dataRow) ) )
				
	return True, _('Success')
