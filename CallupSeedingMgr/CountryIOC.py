# -*- coding: utf-8 -*-

import os
import io
import json

from Utils import imageFolder, removeDiacritic

# from https://github.com/mledoze/countries
fname = os.path.join( imageFolder, 'countries.json' )
with io.open(fname, mode='r', encoding='utf8') as fp:
	country_info = json.loads( fp.read() )

uci_country_codes = {}
iso_uci_country_codes = {}
ison3_uci_country_codes = {}
ioc_country = {}
countries = []

country_short_forms = {
	'United States':	'USA',
}

for c in country_info:
	names = set()
	def scan( d ):
		for k, v in d.items():
			if isinstance(v, dict):
				scan( v )
			elif k in ('common', 'official'):
				names.add( v )
	scan( c['name'] )
	
	common_name = c['name']['common']
	ioc = c['cioc']
	isoa3 = c['cca3']
	ison3 = c['ccn3']
	
	for name in names:
		uci_country_codes[name.upper()] = ioc
	ioc_country[ioc] = country_short_forms.get( common_name, common_name )
	iso_uci_country_codes[isoa3] = ioc
	ison3_uci_country_codes[ison3] = ioc
	
	countries.append( name )
	
isoa3_uci_country_codes = iso_uci_country_codes

countries.sort()

uci_country_codes['USA'.upper()] = 'USA'
uci_country_codes['US'.upper()] = 'USA'
uci_country_codes['United States of America'.upper()] = 'USA'
uci_country_codes['American'.upper()] = 'USA'

uci_country_codes['Canadian'.upper()] = 'CAN'
uci_country_codes['Cdn'.upper()] = 'CAN'

uci_country_codes['The Netherlands'.upper()] = 'NED'
uci_country_codes['Dutch'.upper()] = 'NED'

uci_country_codes['Deutschland'.upper()] = 'GER'

uci_country_codes['Trinidad'.upper()] = 'TTO'
uci_country_codes['Tobago'.upper()] = 'TTO'

ioc_country.pop( '', None )
uci_country_codes.pop( '', None )
ison3_uci_country_codes.pop( '', None )

#-----------------------------------------------------------------------

uci_country_codes_set = set( n.upper() for n in uci_country_codes.values() )

country_info = None

def ioc_from_country( country ):
	return uci_country_codes.get(country.strip().upper(), None)

def ioc_from_code( code ):
	code = code[:3].upper()
	return code if code in uci_country_codes_set else ison3_uci_country_codes.get( code, None )

def country_from_ioc( ioc ):
	return ioc_country.get(removeDiacritic(ioc.strip()[:3]).upper(), None)

#-----------------------------------------------------------------------

provinces = '''
Alberta	AB
British Columbia	BC
Manitoba	MB
New Brunswick	NB
Newfoundland and Labrador	NL
Northwest Territories	NT
Nova Scotia	NS
Nunavut	NU
Ontario	ON
Prince Edward Island	PE
Quebec	QC
Saskatchewan	SK
Yukon	YT
'''

province_codes = {}
for line in provinces.split( '\n' ):
	line = line.strip()
	if not line:
		continue
	fields = line.split('\t')
	province_codes[fields[1].strip()] = fields[0].strip()

provinces = None

#-----------------------------------------------------------------------
