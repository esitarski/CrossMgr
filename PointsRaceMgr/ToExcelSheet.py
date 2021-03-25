import Model
import xlwt
import re

labelStyle = xlwt.easyxf( "alignment: horizontal right;" )
fieldStyle = xlwt.easyxf( "alignment: horizontal right;" )
unitsStyle = xlwt.easyxf( "alignment: horizontal left;" )

def writeLabelField( ws, r, c, label, field, units = None ):
	ws.write( r, c    , label, labelStyle )
	ws.write( r, c + 1, field, fieldStyle )
	if units:
		ws.write( r, c + 2, units, unitsStyle )

def ToExcelSheet( ws ):
	race = Model.race
	maxSprints = race.getMaxSprints()
	
	fnt = xlwt.Font()
	fnt.name = 'Arial'
	fnt.bold = True
	fnt.height = int(fnt.height * 1.5)
	
	headerStyle = xlwt.XFStyle()
	headerStyle.font = fnt
	
	rowCur = 0
	ws.write_merge( rowCur, rowCur, 0, 8, race.name, headerStyle )
	rowCur += 2
	colCur = 2
	ws.write( rowCur, colCur, 'Category:', labelStyle )
	ws.write_merge( rowCur, rowCur, colCur + 1, colCur + 3, race.category, xlwt.easyxf(
															"font: name Arial, bold on;"
															) );
	if race.communique:
		ws.write( rowCur, 9    , u'Communiqu\u00E9:', labelStyle )
		ws.write( rowCur, 9 + 1, race.communique, unitsStyle )
		
	rowCur = 3
	writeLabelField( ws, rowCur, 2, 'Distance:', race.getDistance(), 'km' )
	rowCur += 1
	writeLabelField( ws, rowCur, 2, 'Sprint Every:', race.sprintEvery, 'laps' )
	rowCur += 1
	writeLabelField( ws, rowCur, 2, 'Course:', race.courseLength, ['m', 'km'][race.courseLengthUnit] )
	
	rowCur = 3
	if getattr(race, 'snowball', False):
		rowCur -= 1
		
	colCur = 7
	for f, span in [('Laps:',3), (race.laps,1)]:
		ws.write_merge( rowCur, rowCur, colCur, colCur + span - 1, f, labelStyle if f == 0 else fieldStyle )
		colCur += span
	rowCur += 1
	
	colCur = 7
	for f, span in [('Num Sprints:',3), (maxSprints,1)]:
		ws.write_merge( rowCur, rowCur, colCur, colCur + span - 1, f, labelStyle if f == 0 else fieldStyle )
		colCur += span
	rowCur += 1
	
	if getattr(race, 'snowball', False):
		colCur = 7
		for f, span in [('Snowball Points:',3), ('Yes',1)]:
			ws.write_merge( rowCur, rowCur, colCur, colCur + span - 1, f, labelStyle if f == 0 else fieldStyle )
			colCur += span
		rowCur += 1
	
	colCur = 7
	for f, span in [('Points for Lapping:',3), (race.pointsForLapping,1)]:
		ws.write_merge( rowCur, rowCur, colCur, colCur + span - 1, f, labelStyle if f == 0 else fieldStyle )
		colCur += span

	rowCur = 0
	colCur = 9
	for f, span in [('Date:',1), (race.date.isoformat()[2:],1)]:
		ws.write_merge( rowCur, rowCur, colCur, colCur + span - 1, f, labelStyle if f == 0 else fieldStyle )
		colCur += span

	#------------------------------------------------------------------------------------------
	maxPlace = race.getMaxPlace()
	
	styleTop = xlwt.easyxf(
		"alignment: horizontal center;"
		"borders: top thin, left thin, right thin;"
	)
	style = xlwt.easyxf(
		"alignment: horizontal center;"
		"borders: left thin, right thin;"
	)
	
	# Write the points for each placing.
	rowCur = 7
	for p in range(1, maxPlace):
		ws.write( rowCur + p - 1, 2, race.pointsForPlace[p], style if p != 1 else styleTop )
	styleTop = xlwt.easyxf(
		"alignment: horizontal center;"
		"borders: top thin, left thin, right medium;"
	)
	style = xlwt.easyxf(
		"alignment: horizontal center;"
		"borders: left thin, right medium;"
	)
	
	# Write the positions (1 .. maxPlace - 1).
	for p in range(1, maxPlace):
		ws.write( rowCur + p - 1, 3, p, style if p != 1 else styleTop )
		
	styleTop = xlwt.easyxf(
		"alignment: horizontal center;"
		"borders: top thin, left thin, right thin;"
	)
	style = xlwt.easyxf(
		"alignment: horizontal center;"
		"borders: left thin, right thin;"
	)
	for (sprint, place), num in race.sprintResults.items():
		if place < maxPlace:
			ws.write( rowCur + place - 1, sprint + 3, num, style if place != 1 else styleTop )
	for place in range(1, maxPlace):
		for sprint in range(1, maxSprints+1):
			if (sprint, place) not in race.sprintResults:
				ws.write( rowCur + place - 1, sprint + 3, '', style if place != 1 else styleTop )
		
	#------------------------------------------------------------------------------------------
	style = xlwt.easyxf(
		"font: name Arial, bold on;"
		"alignment: horizontal center;"
		"borders: top thin, bottom thin, left thin, right thin;"
	)

	styleTotal = xlwt.easyxf(
		"borders: top thin, bottom thin, left thin, right medium;"
	)
	styleBib = styleTotal
	styleRegular = xlwt.easyxf(
		"borders: top thin, bottom thin, left thin, right thin;"
	)

	rowCur += maxPlace - 1
	for c, lab in enumerate(['Rank', 'Bib', 'Name']):
		ws.write( rowCur, c, lab, style )
		
	style = xlwt.easyxf(
		"font: name Arial, bold on;"
		"alignment: horizontal center;"
		"borders: top thin, bottom thin, left thin, right medium;"
    )
	ws.write( rowCur, c+1, 'TOTAL', style )
	
	style = xlwt.easyxf(
		"font: name Arial, bold on;"
		"alignment: horizontal center;"
		"borders: top thin, bottom thin, left thin, right thin;"
    )
	for s in range(0, maxSprints):
		ws.write( rowCur, s + 4, 'Sp{}'.format(s + 1), style )
	
	colCur = maxSprints + 4
	if not race.pointsForLapping:
		ws.write( rowCur, colCur, 'Laps +/-', style )
		colCur += 1
	if race.pointsForLapping:
		ws.write( rowCur, colCur, 'Lap Pnts', style )
		colCur += 1
	if race.rankBy == race.RankByLapsPointsNumWins:
		ws.write( rowCur, colCur, 'Num Wins', style )
		colCur += 1
	if race.existingPoints:
		ws.write( rowCur, colCur, 'Existing Pnts', style )
		colCur += 1
	if race.finishOrder:
		ws.write( rowCur, colCur, 'Finish Order', style )
		colCur += 1
	
	rowCur += 1
	riderToRow = {}
	riders = race.getRiders()
	position = 1
	for r, rider in enumerate(riders):
		if (race.rankBy == 0 and rider.pointsTotal < 0) or (race.rankBy == 1 and rider.updown < 0):
			pass
		else:
			if r > 0:
				if not riders[r-1].tiedWith(rider):
					position = r + 1
			ws.write(	rowCur + r, 0,
						position if rider.status == Model.Rider.Finisher else Model.Rider.statusNames[rider.status],
						styleRegular )
		ws.write( rowCur + r, 1, rider.num, styleBib )
		ws.write( rowCur + r, 2, '', styleRegular )					# Name
		ws.write( rowCur + r, 3, rider.pointsTotal, styleTotal )
		
		colCur = maxSprints + 4
		if not race.pointsForLapping:
			ws.write( rowCur + r, colCur, rider.updown if rider.updown != 0 else '', styleRegular )
			colCur += 1
		if race.pointsForLapping:
			ws.write( rowCur + r, colCur, rider.updown * race.pointsForLapping if rider.updown != 0 else '', styleRegular )
			colCur += 1
		if race.rankBy == race.RankByLapsPointsNumWins:
			ws.write( rowCur + r, colCur, rider.numWins if rider.numWins > 0 else '', styleRegular )
			colCur += 1
		if race.existingPoints:
			ws.write( rowCur + r, colCur, rider.existingPoints if rider.existingPoints > 0 else '', styleRegular )
			colCur += 1
		if race.finishOrder:
			ws.write( rowCur + r, colCur, rider.finishOrder if rider.finishOrder < 1000 else '', styleRegular )
			colCur += 1
			
		riderToRow[rider.num] = r

	sprintNumPoints = {}
	for (sprint, place), num in race.sprintResults.items():
		if place < maxPlace and num in riderToRow:
			sprintNumPoints[(sprint, num)] = race.getSprintPoints(sprint, place)

	for sprint in range(1, maxSprints+1):
		for r, rider in enumerate(riders):
			ws.write( rowCur + r, sprint + 3, sprintNumPoints.get((sprint, rider.num)[0], ''), styleRegular )
			
	rowCur += len(riders) + 2
	for line in race.notes.split('\n'):
		ws.write( rowCur, 0, line, styleRegular )
		rowCur += 1

class PrintSheet:
	def __init__( self ):
		self.rows = []
		
	def write( self, row, col, value, style = None):
		try:
			r = self.rows[row]
		except IndexError:
			self.rows += [[] for i in range(row - len(self.rows) + 1)]
			r = self.rows[row]
			
		try:
			v = r[col]
		except IndexError:
			r += [None] * (col - len(r) + 1)
			v = r[col]
		assert v is None
		r[col] = value
		
	def write_merge( self, rowStart, rowEnd, colStart, colEnd, value, style = None ):
		for row in range(rowStart, rowEnd+1):
			for col in range(colStart, colEnd+1):
				if row == rowStart and col == colStart:
					self.write( row, col, u'{}'.format(value) )
				else:
					self.write( row, col, u'\t' )
			
if __name__ == '__main__':
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	race = Model.race
	xlFName = "Test.xls"
	wb = xlwt.Workbook()
	sheetCur = wb.add_sheet( re.sub('[:\\/?*\[\]]', ' ', race.name) )
	ToExcelSheet( sheetCur )
	wb.save( xlFName )
