import unicodedata

def remove_diacritic( s ):
	'''
	Accept a unicode string, and return a normal string
	without any diacritical marks.
	'''
	try:
		return unicodedata.normalize('NFKD', u'{}'.format(s)).encode('ASCII', 'ignore').decode()
	except:
		return s

def normalize( s ):
	return remove_diacritic( s.replace('.','').replace('_',' ').strip().lower() )
 
class FieldMap( object ):
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
			del self.alias_to_name[normalize(a)]
		del self.aliases[name]
		del self.description[name]
		
	def get_aliases( self, name ):
		return self.aliases.get(name, tuple())
		
	def get_description( self, name ):
		return self.description.get(name, '')
			
	def set_headers( self, header ):
		self.name_to_col = {}
		self.unmapped = set()
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
		('LastName','Last Name','LName','Rider Last Name',),
		"Participant's last name",
	),
	('first_name',
		('FirstName','First Name','FName','Rider First Name',),
		"Participant's first name",
	),
	('name',
		('Name',),
		"Participant's name",
	),
	('date_of_birth',
		('Date of Birth','DateOfBirth','Birthdate','DOB','Birth','Birthday',),
		"Date of birth",
	),
	('gender',
		('Gender', 'Rider Gender', 'Sex', 'Race Gender',),
		"Gender",
	),
	('team',
		('Team','Team Name','TeamName','Rider Team','Club','Club Name','ClubName','Rider Club','Rider Club/Team',),
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
		('Bib','BibNum','Bib Num', 'Bib #', 'Bib#', 'Rider Bib #',),
		"Bib number",
	),
	('paid',
		('Paid','Fee Paid',),
		"Paid",
	),
	('email',
		('Email',),
		"Email",
	),
	('phone',
		('Phone','Telephone','Phone #',),
		"Phone",
	),
	('city',
		('City',),
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
		('Race Category','RaceCategory','Race_Category',),
		"Race Category",
	),
	('category_name',
		('Category',),
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
		('Role',),
		"Role",
	),
	('preregistered',
		('Preregistered', 'Prereg',),
		"Preregistered",
	),
	('waiver',
		('Waiver',),
		"Waiver",
	),
	('laps',
		('Laps',),
		"Laps",
	),
)

def standard_field_map( exclude = [] ):
	fm = FieldMap()
	for a in standard_field_aliases:
		fm.set_aliases( *a )
	for e in exclude:
		del fm[e]
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
