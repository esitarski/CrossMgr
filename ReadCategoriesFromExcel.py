import Utils
import Model

sheetName = '--CrossMgr-Categories'

def ReadCategoriesFromExcel( reader ):
	race = Model.race
	if not race:
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
	)

	HeadersToFields = dict( (k, v) for k, v in HeadersFields )
	HeaderSet = set( k for k, v in HeadersFields )

	if sheetName not in reader.sheet_names():
		return False
	
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
		for h, c in headerMap.iteritems():
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
		
		categories.append( catRow )
	
	if categories:
		try:
			race.setCategories( race.mergeExistingCategoryAttributes(categories) )
			race.adjustAllCategoryWaveNumbers()
			if raceMinutesMax > 0:
				race.minutes = raceMinutesMax
			return True
		except Exception as e:
			Utils.writeLog( 'ReadCategoriesFromExcel: error: {}'.format(e) )
			return False
	else:
		return False
