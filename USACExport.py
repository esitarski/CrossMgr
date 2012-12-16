import wx
import os
import xlwt
import Model
from ExportGrid import ExportGrid
from FitSheetWrapper import FitSheetWrapper

# Map the USAC header to our headers.
USACCrossMgr = (
	('rider place',			'Pos'),
	('race gender',			'Gender'),
	('race discipline',		'Cyclo-cross'),
	('race category',		'Category'),
	('rider last name',		'Last Name'),
	('rider first name',	'First Name'),
	('rider team',			'Team'),
	('rider license #',		'License'),
	('time',				'Time'),
)
# Map our headers back to USAC headers.
USACHeaderMapping = dict( e for e in USACCrossMgr )
HeaderToUSAC = dict( (v, k) for k, v in USACHeaderMapping.iteritems() )

rightJustify = set( ['rider place', 'time'] )

def USACExport( sheet ):
	''' Combine results for all categories into one big spreadsheet. '''
	exportGrid = ExportGrid()
	exportGrid.setResultsOneList( None, True )
	
	if not exportGrid.colnames:
		self.clearGrid()
		return
		
	with Model.LockRace() as race:
		try:
			externalFields = race.excelLink.getFields()
			externalInfo = race.excelLink.read()
		except:
			externalFields = []
			externalInfo = {}
		raceDiscipline = getattr( race, 'discipline', 'Cyclo-cross' )
	
	headerColMap = dict( (HeaderToUSAC[colName], c) for c, colName in enumerate(exportGrid.colnames) if colName in HeaderToUSAC )
	exportHeaders = set( headerColMap.keys() )
	exportHeaders.add( 'race discipline' )		# Taken from the race properties.
	exportHeaders.add( 'race gender' )			# Taken from the spreadsheet.
	exportHeaders.add( 'race category' )		# Taken from the category.

	titleStyle = xlwt.XFStyle()
	titleStyle.font.bold = True
	titleStyle.font.height += titleStyle.font.height / 2

	sheetFit = FitSheetWrapper( sheet )
	
	rowTop = 0
	for cat in Model.race.getCategories():
		exportGrid = ExportGrid()
		exportGrid.setResultsOneList( cat, True )
		if not exportGrid.colnames:
			continue
			
		dataRows = len(exportGrid.data[0])
		
		fixedValues = {
			'race discipline':		raceDiscipline,
			'race gender':			getattr( cat, 'gender', 'Open' ),
			'race category':		cat.name,
		}
		
		col = 0
		for header, cmHeader in USACCrossMgr:
			if header not in exportHeaders:
				continue
			
			row = rowTop
			if rowTop == 0:
				headerStyle = xlwt.XFStyle()
				headerStyle.borders.bottom = xlwt.Borders.MEDIUM
				headerStyle.font.bold = True
				headerStyle.alignment.horz = xlwt.Alignment.HORZ_LEFT
				headerStyle.alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
				sheetFit.write( row, col, header, headerStyle, bold=True )
				row += 1
				
			style = xlwt.XFStyle()
			style.alignment.horz = xlwt.Alignment.HORZ_LEFT if header not in rightJustify else xlwt.Alignment.HORZ_RIGHT
			
			for i in xrange(dataRows):
				v = fixedValues.get( header, None )
				if v is None:
					v = exportGrid.data[headerColMap[header]][i]
					if header == 'time':
						v = v.strip()
						try:		# Strip off decimals on the time.
							v = v[:v.rindex('.')]
						except ValueError:
							pass
					elif header == 'rider place':
						if v in {'NP', 'OTL', 'PUL'}:	# Normalize all CrossMgr statuses to USAC DNP.
							v = 'DNP'
				sheetFit.write( row, col, v, style )
				row += 1
			col += 1
			
		if rowTop == 0:
			rowTop = 1
		rowTop += len(exportGrid.data[0])