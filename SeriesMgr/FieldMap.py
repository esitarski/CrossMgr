import unicodedata
from collections import defaultdict
import csv
import io

def remove_diacritic( s ):
	'''
	Accept a unicode string, and return a normal string
	without any diacritical marks.
	'''
	try:
		return unicodedata.normalize('NFKD', '{}'.format(s)).encode('ASCII', 'ignore').decode()
	except Exception:
		return s

def normalize( s ):
	return remove_diacritic( s.replace('.','').replace('_',' ').strip().lower() )
 
class FieldMap:
	def __init__( self ):
		self.reset()
		
	def reset( self ):
		self.name_to_col = {}
		self.alias_to_name = {}
		self.unmapped = set()
		self.aliases = {}
		self.description = {}
		 
	def set_aliases( self, name, aliases, description='' ):
		self.aliases[name] = tuple(aliases)
		for a in self.aliases[name]:
			self.alias_to_name[normalize(a)] = name
		self.description[name] = description

	def __delitem__( self, name ):
		for a in self.aliases[name]:
			self.alias_to_name.pop( normalize(a), None )
		self.name_to_col.pop( name, None )
		self.unmapped.discard( name )
		self.aliases.pop( name, None )
		self.description.pop( name, None )
		
	def get_aliases( self, name ):
		return self.aliases.get(name, tuple())
		
	def get_description( self, name ):
		return self.description.get(name, '')
			
	def set_headers( self, header ):
		self.name_to_col.clear()
		self.unmapped.clear()
		for i, h in enumerate(header):
			try:
				h = normalize( h )
			except Exception as e:
				continue
			
			try:
				name = self.alias_to_name[h]
			except KeyError:
				continue
			if name not in self.name_to_col:
				self.name_to_col[name] = i
			else:
				self.unmapped.add( h )
	
	def get_value( self, name, fields, default=None ):
		try:
			return fields[self.name_to_col[name]]
		except (KeyError, IndexError):
			return default
		
	def finder( self, fields ):
		return lambda name, default=None: self.get_value(name, fields, default)
			
	def __contains__( self, name ):
		return name in self.name_to_col
		
	def get_name_from_alias( self, alias ):
		try:
			alias = normalize( alias )
		except Exception as e:
			return None
		return None if alias in self.unmapped else self.alias_to_name.get(alias, None)
		
	def __repr__( self ):
		return repr(self.name_to_col)
		
	def summary( self ):
		name_aliases = defaultdict( list )
		for alias, name in self.alias_to_name.items():
			name_aliases[name].append( alias )
		
		s = io.StringIO()
		writer = csv.writer( s )
		writer.writerow( ['Field','Description','Accepted Column Names (upper/lower case, accents are ignored)'] )
		for name, aliases in sorted(name_aliases.items()):
			writer.writerow( [name, self.description[name]] + sorted(aliases) )
		return s.getvalue()

standard_field_aliases = (
	('pos',
		('Pos','Pos.','Rank', 'Rider Place','Place',),
		"Finish position",
	),
	('time',
		('Time','Tm.','Rider Time',),
		"Finish time",
	),
	('last_name',
		('LastName','Last Name','LName','Rider Last Name','Nom de famille'),
		"Participant's last name",
	),
	('first_name',
		('FirstName','First Name','FName','Rider First Name','Prénom'),
		"Participant's first name",
	),
	('name',
		('Name','Nom',),
		"Participant's name in \"LASTNAME, Firstname\" format",
	),
	('date_of_birth',
		('Date of Birth','DateOfBirth','Birthdate','DOB','Birth','Birthday','date de naissance'),
		"Date of birth",
	),
	('gender',
		('Gender', 'Rider Gender', 'Sex', 'Race Gender','Genre',),
		"Gender",
	),
	('team',
		('Team','Team Name','TeamName','Rider Team','Club','Club Name','ClubName','Rider Club','Rider Club/Team','Équipe','Affiliates',),
		"Team",
	),
	('discipline',
		('Discipline',),
		"Discipline",
	),
	('license_code',
		(
			'Lic', 'Lic #',
			'Lic Num', 'LicNum', 'Lic Number',
			'Lic Nums','LicNums','Lic Numbers',
			
			'License','License #', 
			'License Number','LicenseNumber',
			'License Numbers','LicenseNumbers',
			'License Num', 'LicenseNum',
			'License Nums','LicenseNums',
			'License Code','LicenseCode','LicenseCodes',
			
			'Licence','Licence #', 
			'Licence Number','LicenceNumber',
			'Licence Numbers','LicenceNumbers',
			'Licence Num', 'LicenceNum',
			'Licence Nums','LicenceNums',
			'Licence Code','LicenceCode','LicenceCodes',
			'Rider License #',
		),
		"License code (not UCI code)",
	),
	('uci_id',
		('UCI ID','UCIID',),
		"UCI ID of the form NNNNNNNNNNN",
	),
	('bib',
		('Bib','BibNum','Bib Num', 'Bib #', 'Bib#', 'Rider Bib #','Plate', 'Plate #', 'Plate#','Numéro','plaque'),
		"Bib number",
	),
	('paid',
		('Paid','Fee Paid',),
		"Paid",
	),
	('irm',
		('IRM',),
		"Dataride DNF/DNS/DSQ/LAP/REL status field",
	),
	('status',
		('Status','State'),
		"Status DNF/DNS/DSQ status field",
	),
	('result',
		('Result',),
		"Dataride Result (time)",
	),
	('email',
		('Email',),
		"Email",
	),
	('phone',
		('Phone','Telephone','Phone #','téléphone'),
		"Phone",
	),
	('city',
		('City','ville'),
		"City",
	),
	('state_prov',
		('State','Prov','Province','Stateprov','State Prov',),
		"State or Province",
	),
	('tag',
		('Tag','Chip','Chip ID','Chip Tag',),
		"Chip tag",
	),
	('note',
		('Note',),
		"Note about the participant",
	),
	('zip_postal',
		('ZipPostal','Zip','Postal','Zip Code','Postal Code','ZipCode','PostalCode',),
		"Postal or Zip code",
	),
	('category_code',
		('Race Category','RaceCategory','Race_Category','code de catégorie'),
		"Race Category",
	),
	('category_name',
		('Category','catégorie'),
		"Category Name",
	),
	('est_kmh',
		('Est kmh','Est. kmh','kmh',),
		"Estimated kmh (used for Time Trial Seeding)",
	),
	('est_mph',
		('Est mph','Est. mph','mph',),
		"Estimated mph (used for Time Trial Seeding)",
	),
	('seed_option',
		('Seed Option','SeedOption',),
		"Time Trial Seeding Option (value is 'early','late' or blank)",
	),
	('emergency_contact_name',
		('Emergency Contact','Emergency Contact Name','Emergency Name',),
		"Emergency Contact Name",
	),
	('emergency_contact_phone',
		('Emergency Phone','Emergency Contact Phone',),
		"Emergency Contact Phone",
	),
	('race_entered',
		('Race Entered','RaceEntered',),
		"Race Entered",
	),
	('role',
		('Role','rôle'),
		"Role",
	),
	('preregistered',
		('Preregistered', 'Prereg','préinscrit'),
		"Preregistered",
	),
	('waiver',
		('Waiver','renoncer'),
		"Waiver",
	),
	('laps',
		('Laps','tours'),
		"Laps",
	),
	('points',
		('Points',),
		"Points",
	),
)

def standard_field_map( exclude=None, only=None ):
	fm = FieldMap()
	for a in standard_field_aliases:
		fm.set_aliases( *a )
	if exclude:
		for f in exclude:
			del fm[f]
	if only:
		only_set = set( only )
		for f in list( fm.description.keys() ):
			if f not in only_set:
				del fm[f]
	return fm
	
if __name__ == '__main__':
	sfm = standard_field_map()
	headers = ('BibNum', 'Role', 'license', 'UCI Code', 'note', 'tag', 'Emergency Phone')
	sfm.set_headers( headers )
	del sfm['note']
	
	row = (133, 'Competitor', 'ABC123', 'CAN19900925', 'Awesome', '123456', '415-789-5432')
	v = sfm.finder( row )
	print( v('bib'), v('role'), v('license'), v('uci_code'), v('note'), v('tag'), v('emergency_contact_phone') )
	assert v('bib', None) == 133
	print( sfm.get_aliases( 'license_code' ) )

	sfm = standard_field_map( only=['pos', 'bib', 'license_code', 'uci_id', 'time', 'name', 'first_name', 'last_name', 'team', 'categoryName', 'laps', 'points', 'irm', 'status'] )
	with open('summary.csv', 'w', encoding='utf8') as f:
		f.write( sfm.summary() )
