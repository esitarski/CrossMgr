import re
import sys
import Utils
import Model
import scramble

sheetName = '--CrossMgr-Properties'

def ReadPropertiesFromExcel( reader ):
	race = Model.race
	if not race or sheetName not in reader.sheet_names():
		return False
			
	HeadersFields = (
		('Event Name',		'name', 			's'),
		('Event Organizer',	'organizer',	 	's'),
		('Event City',		'city',				's'),
		('Event StateProv',	'stateProv',		's'),
		('Event Country',	'country',			's'),
		('Event Date',		'date',				's'),
		('Scheduled Start',	'scheduledStart',	's'),
		('TimeZone',		'timezone',			's'),
		('Race Discipline',	'discipline',		's'),
		('Race Number',		'raceNum',			'n'),
		('Enable RFID',		'enableJChipIntegration',	'b'),
		('Distance Unit',	'distanceUnit',		's'),
		('Time Trial',		'isTimeTrial',		'b'),
		('RFID Option',		'__rfidOption__',	'n'),
		
		('FTP Host',		'ftpHost',			's'),
		('FTP User',		'ftpUser',			's'),
		('FTP Password',	'ftpPassword',		's'),
		('FTP Path',		'ftpPath',			's'),
		('FTP Upload During Race',	'ftpUploadDuringRace',	'b'),
		
		('GATrackingID',	'gaTrackingID',		's'),
		('Road Race Finish Times',	'roadRaceFinishTimes',	'b'),
		('Estimate Laps Down Finish Time',	'estimateLapsDownFinishTime',	'b'),
		('No Data DNS',		'setNoDataDNS',		'b'),
		('Chip Reader Type','chipReaderType',	'n'),
		('Win and Out',		'winAndOut',		'b'),
		('Event Long Name',	'longName', 		's'),
		('Email',			'email', 			's'),
	)

	AttributeFromHeader = { h: a for h, a, t in HeadersFields }
	FieldType = { a: t for h, a, t in HeadersFields }
	HeaderSet = set( h for h, a, t in HeadersFields )

	reStartDate = re.compile( '^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$' )
	reStartTime = re.compile( '^[0-2][0-9]:[0-9][0-9]$' )

	headerMap = {}
	for r, row in enumerate(reader.iter_list(sheetName)):
		# Since this is machine generated, assume the headers are always in the first row.
		if r == 0:
			for c, v in enumerate(row):
				if v in HeaderSet:
					headerMap[v] = c
			continue
		
		for h, c in headerMap.items():
			a = AttributeFromHeader[h]
			
			v = row[c]
			t = FieldType[a]
			if t == 's':
				v = '{}'.format(v)
			elif t == 'b':
				v = bool(v)
			elif t == 'n':
				try:
					v = int(v)
				except ValueError:
					v = 1
			
			if a == 'distanceUnit':
				v = 1 if v and v.lower().startswith('m') else 0
			elif a == 'date':
				if not reStartDate.match(v or ''):
					v = None
			elif a == 'scheduledStart':
				if not reStartTime.match(v or ''):
					v = None
			elif a == '__rfidOption__':
				if v == 0:		# Manual start.
					race.resetStartClockOnFirstTag = False
					race.skipFirstTagRead = False
				elif v == 1:	# Automatic start.
					race.resetStartClockOnFirstTag = True
					race.skipFirstTagRead = False
				elif v == 2:	# Manual start with first read skip.
					race.resetStartClockOnFirstTag = False
					race.skipFirstTagRead = True
				v = None
			elif a == 'ftpPassword':
				try:
					v = scramble.decode( v )
				except Exception as e:
					Utils.logException( e, sys.exc_info() )
					continue
			
			if v != u'' and v is not None:
				setattr( race, a, v )
		
		return True
		
	return False
