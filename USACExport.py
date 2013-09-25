import wx
import os
import xlwt
import Model
import Utils
import datetime
from GetResults import GetResults
from FitSheetWrapper import FitSheetWrapper

USACFields = (
	'Race Date',
	'Race Gender',
	'Race Discipline',
	'Race Category',
	'Rider Bib #',
	'Rider Last Name',
	'Rider First Name',
	'Rider Team',
	'Rider License #',
	'Rider Place',
	'Rider Time',
)
lenUSACFields = len(USACFields)

def USACExport( sheet ):
	race = Model.race
	if not race:
		return
		
	raceDiscipline = getattr( race, 'discipline', 'Cyclo-cross' )
	if raceDiscipline.lower() in 'cyclocross':
		raceDiscipline = 'Cyclo-cross'

	sheetFit = FitSheetWrapper( sheet )
	
	titleStyle = xlwt.XFStyle()
	titleStyle.font.bold = True
	
	leftAlignStyle = xlwt.XFStyle()
	
	rightAlignStyle = xlwt.XFStyle()
	rightAlignStyle.alignment.horz = xlwt.Alignment.HORZ_RIGHT
	
	maxLaps = 0
	for cat in race.getCategories():
		results = GetResults( cat, True )
		for rr in results:
			maxLaps = max( maxLaps, rr.laps )
	if maxLaps == 1 or maxLaps > 99:
		maxLaps == 0
		
	def toInt( n ):
		try:
			return int(n)
		except:
			return n
			
	year, month, day = race.date.split( '-' )
	raceDate = datetime.date( year = int(year), month = int(month), day = int(day) ).strftime( '%m/%d/%Y' )
	
	row = 0
	for cat in race.getCategories():
		results = GetResults( cat, True )
		if not results:
			continue
		
		raceGender = getattr(cat, 'gender', 'Open')
		if raceGender == 'Open':
			raceGender = 'All'
		
		for rr in results:
			if row == 0:
				for col, field in enumerate(USACFields):
					sheetFit.write( row, col, field, titleStyle, bold=True )
				for i in xrange(maxLaps):
					sheetFit.write( row, lenUSACFields + i, 'Rider Lap {}'.format(i + 1), titleStyle, bold=True )
				row += 1
			
			for col, field in enumerate(USACFields):
				{
					'Race Date':		lambda : sheet.write( row, col, raceDate, rightAlignStyle ),
					'Race Gender':		lambda : sheetFit.write( row, col, raceGender, leftAlignStyle ),
					'Race Discipline':	lambda : sheetFit.write( row, col, raceDiscipline, leftAlignStyle ),
					'Race Category':	lambda : sheetFit.write( row, col, cat.name, leftAlignStyle ),
					'Rider Bib #':		lambda : sheetFit.write( row, col, rr.num, rightAlignStyle ),
					'Rider Last Name':	lambda : sheetFit.write( row, col, getattr(rr, 'LastName', ''), leftAlignStyle ),
					'Rider First Name':	lambda : sheetFit.write( row, col, getattr(rr, 'FirstName', ''), leftAlignStyle ),
					'Rider Team':		lambda : sheetFit.write( row, col, getattr(rr, 'Team', ''), leftAlignStyle ),
					'Rider License #':	lambda : sheetFit.write( row, col, getattr(rr, 'License', ''), leftAlignStyle ),
					'Rider Place':		lambda : sheetFit.write( row, col, 'DNP' if rr.pos in {'NP', 'OTL', 'PUL'} else toInt(rr.pos), rightAlignStyle ),
					'Rider Time':		lambda : sheetFit.write( row, col, Utils.formatTime(rr.lastTime) if rr.lastTime else '', rightAlignStyle ),
				}[field]()
			
			if maxLaps:
				for i, lapTime in enumerate(rr.lapTimes):
					sheetFit.write( row, lenUSACFields + i, Utils.formatTime(lapTime), rightAlignStyle )
			row += 1
