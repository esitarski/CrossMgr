import Utils
import Model

sheetName = '--CrossMgr-Categories'

def ReadCategoriesFromExcel( reader, raceHasStartTime=False ):
	race = Model.race
	if not race or sheetName not in reader.sheet_names():
		return False
		
	HeadersFields = (
		('Category Type',	'catType'),
		('Name',			'name'),
		('Gender',			'gender'),
		('Numbers',			'catStr'),
		('Start Offset',	'startOffset'),
		('Race Laps',		'numLaps'),
		('Race Distance',	'distance'),
		('Race Minutes',	None),
		('Publish',			'publishFlag'),
		('Upload',			'uploadFlag'),
		('Series',			'seriesFlag'),
	)
	# List of fields not to update if the race is underway.
	# These are left under CrossMgr control.
	ignoreFields = ['startOffset', 'numLaps', 'raceMinutes', 'distance'] if raceHasStartTime else []

	HeadersToFields = dict( (k, v) for k, v in HeadersFields )
	HeaderSet = set( k for k, v in HeadersFields )

	# If the course is defined, default the Categories to the course length.
	if race.geoTrack:
		distance = race.geoTrack.lengthKm if race.distanceUnit == race.UnitKm else race.geoTrack.lengthMiles
	else:
		distance = None
		
	raceMinutesMax = -1
	headerMap = {}
	categories = []
	for r, row in enumerate(reader.iter_list(sheetName)):
		# Since this is machine generated, assume the headers are in the first row.
		if not headerMap:
			for c, v in enumerate(row):
				if v in HeaderSet:
					headerMap[v] = c
			continue
		
		catRow = {}
		for h, c in headerMap.items():
			catField = HeadersToFields[h]
			if h == 'Race Minutes' and row[c]:
				try:
					raceMinutes = int(row[c])
					raceMinutesMax = max( raceMinutesMax, raceMinutes )
					catRow['raceMinutes'] = raceMinutes
				except ValueError:
					pass
			elif h == 'Race Distance' and not row[c] and distance:
				catRow['distance'] = distance
			if catField is not None:
				catRow[catField] = row[c]
		
		for f in ignoreFields:
			cateRow.pop( f, None )
		
		categories.append( catRow )
	
	if categories:
		try:
			race.setCategories( race.mergeExistingCategoryAttributes(categories) )
			race.adjustAllCategoryWaveNumbers()
			if raceMinutesMax > 0:
				if raceHasStartTime:
					if raceMinutesMax > race.minutes:
						race.minutes = raceMinutesMax
				else:
					race.minutes = raceMinutesMax
			return True
		except Exception as e:
			Utils.writeLog( 'ReadCategoriesFromExcel: error: {}'.format(e) )
			return False
	else:
		return False
