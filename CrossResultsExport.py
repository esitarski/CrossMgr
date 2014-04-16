import csv
import math
import Utils
import datetime
import Model
from GetResults import GetResults, GetCategoryDetails
from ReadSignOnSheet import SyncExcelLink

CrossResultsFields = (
	('Place',		'pos'),
	('Time',		'lastTime'),
	('Last Name',	'LastName'),
	('First Name',	'FirstName'),
	('Team',		'Team'),
	('License',		'License'),
)
lenCrossResultsFields = len(CrossResultsFields)

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
		decimal = '.%02d' % int( f * 100 )
	else:
		decimal = ''
	return "%s%02d:%02d:%02d%s" % (sign, hours, minutes, secs, decimal)

def CrossResultsExport( fname ):
	race = Model.race
	if not race:
		return
	
	SyncExcelLink( race )
	
	hasField = [False] * len(CrossResultsFields)
	hasField[0] = True
	hasField[1] = True
	
	# Check for what fields are actually filled in.
	publishCategories = race.getCategories( startWaveOnly = False, uploadOnly = True )
	for cat in publishCategories:
		results = GetResults( cat, True )
		if not results:
			continue
		for rr in results:
			for i, (field, cmgrField) in enumerate(CrossResultsFields):
				if getattr(rr, cmgrField, None):
					hasField[i] = True
	
	if not hasField[2]:
		return False, _('"LastName" must be linked to a column in the Excel sheetl')
	
	# Filter the fields by what exists in the data.
	crossResultsFields = [CrossResultsFields[i][0] for i in xrange(len(hasField)) if hasField[i]]
	
	year, month, day = race.date.split( '-' )
	raceDate = datetime.date( year = int(year), month = int(month), day = int(day) ).strftime( '%m/%d/%Y' )
	
	def toInt( n ):
		try:
			return int(n.split()[0])
		except:
			return n

	with open(fname, 'w') as csvFile:
		csvWriter = csv.writer( csvFile, delimiter = ',', lineterminator = '\n' )
		csvWriter.writerow( crossResultsFields )
		
		for cat in publishCategories:
			results = GetResults( cat, True )
			if not results:
				continue
			
			csvWriter.writerow( [unicode(cat.fullname).encode('utf-8')] )
			
			for rr in results:
				try:
					finishTime = formatTime(rr.lastTime - rr.raceTimes[0]) if rr.status == Model.Rider.Finisher else ''
				except Exception as e:
					finishTime = ''
				
				dataRow = []
				for field in crossResultsFields:
					dataRow.append( {
						'Place':		lambda : 'DNP' if rr.pos in {'NP', 'OTL', 'PUL'} else toInt(rr.pos),
						'Time':			lambda : finishTime,
						'Last Name':	lambda : getattr(rr, 'LastName', ''),
						'First Name':	lambda : getattr(rr, 'FirstName', ''),
						'Team':			lambda : getattr(rr, 'Team', ''),
						'License':		lambda : getattr(rr, 'License', ''),
					}[field]() )
				
				csvWriter.writerow( [unicode(d).encode('utf-8') for d in dataRow] )
				
			csvWriter.writerow( [] )		# Blank line separates each category.
			
	return True, _('Success')
