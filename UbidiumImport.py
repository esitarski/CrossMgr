import re
import csv
import math
import datetime

def to_datetime( s ):
	# Assume input of "YYYY-MM-DD HH:MM:SS.fff"
	fields = [v.lstrip('0') for v in re.split( '[- :]', s )]
	s_fract, s_int = math.modf( float(fields[-1]) )
	fields = [int(v) for v in fields[:-1]] + [s_int, int(s_fract * 1000000.0)]
	return datetime.datetime( *fields )

def UbidiumImport( fname ):
	# Ubidium header fields to read.
	fields = {
		'id',
		'time.local',
	}
	field_icol = {}
	
	tags, errors = [], []
	try:
		with open( fname, encoding='utf8' ) as csvfile:
			csvreader = csv.reader( csvfile, delimiter=';' )
			for irow, row in enumerate(csvreader,1):
				if not row:
					continue
				
				if not field_icol:
					# Get the header row.
					for icol, h in enumerate(row):
						if h in fields:
							field_icol[h] = icol
					# Check if all the header fields are present.
					if len(field_icol) != len(fields):
						return [], ['{}: {}'.format( _('Did Not Find Headers'), ','.join( f'"{f}"' for f in fields) )]
					continue
				
				# Check if id is present.
				try:
					id = row[field_icol['id']]
				except Exception:
					errors.append( '{} {}: {} {}'.format( _("Row"), irow, _("Error reading column"), field_icol['id'] ) )
					continue
					
				# Check if id is hex format.
				try:
					id = id.lstrip('0')
					int( id, 16 )
				except Exception:
					errors.append( '{} {}: {} "{}"'.format( _("Row"), irow, _('Invalid "id" (must be hex)'), id ) )
					continue						
				
				# Check if time.local is present.
				try:
					t = row[field_icol['time.local']]
				except Exception:
					errors.append( '{} {}: {}: {}'.format( _("Row"), irow, _("Error reading column"), field_icol['time.local'] ) )
					continue
				
				# Check if time.local is a valid time.
				try:
					dt = to_datetime( t )
				except Exception:
					errors.append( '{} {}: {} {}'.format( _('Row'), irow, _('Cannot parse "time.local"'), t ) )
					continue
				
				# Add tag and time.	
				tags.append( (id, dt) )
				
	except Exception as e:
		errors.append( '{}: {}'.format( _("File Open Error"), e) )

	return tags, errors
