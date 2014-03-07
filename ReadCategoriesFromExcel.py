import Utils
import Model
from Excel import GetExcelReader

sheetName = '--CrossMgr_Categories'

Headers = [
	'Type',
	'Name',
	'Gender',
	'Numbers',
	'StartOffset',
	'RaceLaps',
	'RaceDistance',
	'RaceTime'
]

HeadersToCatFields = {
	'Type':			'catType',
	'Name':			'name',
	'Numbers':		'catStr',
	'StartOffset':	'startOffset',
	'RaceLaps':		'numLaps',
	'RaceDistance':	'distance',
	'RaceTime':		None,
}

assert len(Headers) == len(HeadersToCatFields)

def ReadCategoriesFromExcel( reader )
	race = Model.race
	if not race:
		return
		
	if sheetName not in reader.sheet_names():
		return False
	
	headerMap = {}
	categories = []
	for r, row in enumerate(reader.iter_list(sheetName)):
		# Since this is machine generated, assume the headers are in the first row.
		if not headerMap:
			headerSet = set( Headers )
			for c, v in enumerate(row):
				if v in headerSet:
					headerMap[v] = c
			continue
		
		for h, c in headerMap.iteritems():
			catField = HeadersToCatFields[h]
			if catField is None:
				continue
			catRow[catField] = row[headerMap[h]]
			
		catRow['startOffset'] = Utils.SecondsToStr( catRow['startOffset'] )
		categories.append( catRow )
	
	if categories:
		race.setCategories( categories )
