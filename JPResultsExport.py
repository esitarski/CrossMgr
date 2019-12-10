from math import floor
import Model
import Utils
import datetime
from GetResults import GetResults, GetCategoryDetails
from FitSheetWrapper import FitSheetWrapperXLSX
from ReadSignOnSheet import SyncExcelLink
from UCIExcel import formatUciId

JPResultFields = '''
body_number	racer_code	family_name	first_name	team	uci_id	gender	birth_date	entry_status	rank	result_status	lap	goal_time	category_code
'''.split()

def toInt( n ):
	try:
		return int(n.split()[0])
	except:
		return n

def getStatusName( s ):
	if s == Model.Rider.Finisher:
		return 'FIN'
	if s == Model.Rider.DQ:
		return 'DSQ'
	return Model.Rider.statusNames[s]	
	
def JPResultsExport( workbook, sheet ):
	race = Model.race
	if not race:
		return
		
	SyncExcelLink( race )
	
	sheetFit = FitSheetWrapperXLSX( sheet )
	
	titleStyle = workbook.add_format({'bold':True})
	leftAlignStyle = workbook.add_format()
	rightAlignStyle = workbook.add_format({'align':'right'})
	timeStyle = workbook.add_format({'num_format':'hh:mm:ss', 'align':'right'})
	
	Finisher = Model.Rider.Finisher
	
	row = 0
	for cat in race.getCategories( startWaveOnly = False, uploadOnly = True ):
		results = GetResults( cat )
		if not results:
			continue
		
		gender = None
		
		for rr in results:
			if row == 0:
				for col, field in enumerate(JPResultFields):
					sheetFit.write( row, col, field, titleStyle, bold=True )
				row += 1
			
			try:
				finishTime = (rr.lastTime - rr.raceTimes[0]) if rr.status == Finisher else None
				if race.roadRaceFinishTimes:
					finishTime = floor(finishTime)[0]	# Truncate decimal seconds.
				finishTime /= (24.0*60.0*60.0)			# Convert to fraction of a day.
			except Exception as e:
				finishTime = None

			valueStyle = {
				'body_number':		( rr.num, rightAlignStyle ),
				'racer_code':		( getattr(rr, 'License', None), leftAlignStyle ),
				'family_name':		( getattr(rr, 'LastName', None), leftAlignStyle ),
				'first_name':		( getattr(rr, 'FirstName', None), leftAlignStyle ),
				'team':				( getattr(rr, 'Team', None), leftAlignStyle ),
				'uci_id':			( formatUciId(getattr(rr, 'UCIID', None)) if hasattr(rr, 'UCIID') else None, leftAlignStyle ),
				'gender':			( gender, leftAlignStyle ),
				'birth_date':		( getattr(rr, 'DateOfBirth', None), leftAlignStyle ),
				'entry_status':		( getattr(rr, 'EntryStatus', None), leftAlignStyle ),
				'rank':				( rr.pos if rr.status == Finisher else None, rightAlignStyle ),
				'result_status':	( getStatusName(rr.status), leftAlignStyle ),
				'lap':				( rr.laps if rr.status == Finisher else None, rightAlignStyle ),
				'goal_time':		( finishTime if rr.status == Finisher else None, timeStyle ),
				'category_code':	( cat.name, leftAlignStyle ),
			}

			for col, field in enumerate(JPResultFields):
				value, style = valueStyle[field]
				if value is not None:
					sheetFit.write( row, col, value, style )
			
			row += 1
