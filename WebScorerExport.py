import io
import math
import Utils
import datetime
import Model
from GetResults import GetResults, GetCategoryDetails
from ReadSignOnSheet import SyncExcelLink

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

def formatTimeGap( secs ):
	return Utils.formatTimeGap(
		secs,
		highPrecision=True,
		forceHours=True,
		separateWithQuotes=True,
	)

def WebScorerExport( fname ):
	race = Model.race
	if not race:
		return
	
	SyncExcelLink( race )
	
	hasField = [False] * len(WebScorerFields)
	hasField[0] = True
	hasField[1] = True
	
	# Check for what fields are actually filled in.
	publishCategories = race.getCategories( startWaveOnly = False, uploadOnly = True )
	for cat in publishCategories:
		results = GetResults( cat )
		if not results:
			continue
		for rr in results:
			for i, (field, cmgrField) in enumerate(WebScorerFields):
				if getattr(rr, cmgrField, None):
					hasField[i] = True
	
	if not hasField[2]:
		return False, _('LastName must be linked to a column in the Excel sheet.')
	
	catDetails = dict( (cd['name'], cd) for cd in GetCategoryDetails() )
	
	# Filter the fields by what exists in the data.
	webScorerFields = [WebScorerFields[i][0] for i in range(len(hasField)) if hasField[i]]
	webScorerToCrossMgr = dict( (ws, cm) for ws, cm in WebScorerFields )
	
	hasDistance = False
	maxLaps = 0
	for cat in publishCategories:
		results = GetResults( cat )
		if not results:
			continue
		cd = catDetails[cat.fullname]
		if cd.get('raceDistance', None):
			hasDistance = True
		maxLaps = max( maxLaps, max(rr.laps for rr in results) )
		
	if maxLaps == 1 or maxLaps > 99:
		maxLaps = 0
		
	webScorerCategoryFields = [f for f in WebScorerCategoryFields if (hasDistance or f != 'Distance')]
	
	colNames = webScorerFields + webScorerCategoryFields + [u'{} {}'.format(_('Lap'), i+1) for i in range(maxLaps)]
	
	def toInt( n ):
		try:
			return int(n.split()[0])
		except:
			return n
	
	with io.open(fname, 'w', encoding = 'utf-16') as txtFile:
		txtFile.write( u'{}\n'.format( u'\t'.join('{}'.format(c) for c in colNames) ) )
		
		for cat in publishCategories:
			results = GetResults( cat )
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
				
				try:
					finishTime = formatTimeGap(rr.lastTime - rr.raceTimes[0]) if rr.status == Model.Rider.Finisher else ''
				except Exception as e:
					finishTime = ''
				
				# Rider Fields.
				for field in webScorerFields:
					if field == 'Place':
						dataRow.append( 'DNP' if rr.pos in {'NP', 'OTL', 'PUL'} else toInt(rr.pos) )
					elif field == 'Time':
						dataRow.append( finishTime )
					else:
						dataRow.append( getattr(rr, webScorerToCrossMgr[field], '') )

				# Category Fields.
				dataRow.append( cat.name )
				if hasDistance:
					dataRow.append( distance )
				dataRow.append( gender )
					
				# Lap Times.
				for i in range(maxLaps):
					try:
						lapTime = formatTimeGap(rr.lapTimes[i])
					except IndexError:
						lapTime = ''
					dataRow.append( lapTime )
				
				txtFile.write( u'{}\n'.format( u'\t'.join('{}'.format(d).strip().replace(u'\t','    ') for d in dataRow) ) )
				
	return True, _('Success')
