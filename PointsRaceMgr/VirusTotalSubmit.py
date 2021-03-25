#!/usr/bin/env python3

import os
import sys
import argparse
try:
	from virus_total_apis import PublicApi as VirusTotalPublicApi
except:
	print( '**** virus_total_apis module not found.  Do "pip install virustotal-api"' )
	raise
	
API_KEY = '64b7960464d4dbeed26ffa51cb2d3d2588cb95b1ab52fafd82fb8a5820b44779'
vt = VirusTotalPublicApi( API_KEY )

parser = argparse.ArgumentParser(description='Submit executabes to virustotal.')
parser.add_argument('executables', type=str, nargs='+', help='executable files')
parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")

args = parser.parse_args()
for exe in args.executables:
	if args.verbose:         
		print( 'submitting "{}" to virustotal...'.format(exe) )
	if not os.path.exists(exe):
		raise ValueError('File not found: "{}"'.format(exe)) 
	vt.scan_file( exe )

sys.exit( 0 )
