import csv
import Utils
import datetime
import Model
from GetResults import GetResults, GetCategoryDetails

CrossResultsFields = (
	('Place',		'pos'),
	('Time',		'lastTime'),
	('Last Name',	'LastName'),
	('First Name',	'FirstName'),
	('Team',		'Team'),
	('License',		'License'),
)
lenCrossResultsFields = len(CrossResultsFields)

def CrossResultsExport( fname ):
	race = Model.race
	if not race:
		return
	
	hasField = [False] * len(CrossResultsFields)
	hasField[0] = True
	hasField[1] = True
	
	# Check for what fields are actually filled in.
	for cat in race.getCategories():
		results = GetResults( cat, True )
		if not results:
			continue
		for rr in results:
			for i, (field, cmgrField) in enumerate(CrossResultsFields):
				if getattr(rr, cmgrField, None):
					hasField[i] = True
	
	if not hasField[2]:
		return False, _('"LastName" must be linked to a column in the Excel sheetl')
	
	# Filter the fields by what exists.
	crossResultsFields = [CrossResultsFields[i][0] for i in xrange(len(hasField)) if hasField[i]]
	
	year, month, day = race.date.split( '-' )
	raceDate = datetime.date( year = int(year), month = int(month), day = int(day) ).strftime( '%m/%d/%Y' )
	
	with open(fname, 'w') as csvFile:
		csvWriter = csv.writer( csvFile, delimiter = ',', lineterminator = '\n' )
		csvWriter.writerow( crossResultsFields )
		
		for cat in race.getCategories():
			results = GetResults( cat, True )
			if not results:
				continue
			
			csvWriter.writerow( [unicode(cat.fullname).encode('utf-8')] )
			
			for rr in results:
				dataRow = []
				for field in crossResultsFields:
					dataRow.append( {
						'Place':		lambda : 'DNP' if rr.pos in {'NP', 'OTL', 'PUL'} else rr.pos,
						'Time':			lambda : Utils.formatTime(rr.lastTime) if rr.lastTime else '',
						'Last Name':	lambda : getattr(rr, 'LastName', ''),
						'First Name':	lambda : getattr(rr, 'FirstName', ''),
						'Team':			lambda : getattr(rr, 'Team', ''),
						'License':		lambda : getattr(rr, 'License', ''),
					}[field]() )
				
				csvWriter.writerow( [unicode(d).encode('utf-8') for d in dataRow] )
				
			csvWriter.writerow( [] )		# Blank line separates each category.
			
	return True, _('Success')
