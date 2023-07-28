#!/usr/bin/env python
import os
import argparse
import subprocess
import compileall
import platform

is_windows = (platform.system() == 'Windows')

dependencies = [
	'requests',
	'waitress',
	'xlsxwriter',
	'pygments',
	'xlrd',
	'pytz',
	'fpdf',
	'natural-keys',
	'xlwt',
	'whoosh',
	'qrcode',
	'tornado',
	'ftputil'
]

uninstall_dependencies = [
	'south',
]

def update_dependencies( upgrade ):
	print( 'Updating Dependencies...' )
	
	pip = 'C:/Python27/Scripts/pip.exe'
	if os.path.isfile(pip):
		print( 'Found "pip" at "{}".'.format(pip) )
	else:
		pip = 'pip'
	
	for d in dependencies:
		args = [pip, 'install', d]
		if upgrade:
			args.append('--upgrade')
		print( ' '.join(args) )
		subprocess.call( args )

	for d in uninstall_dependencies:
		args = [pip, 'uninstall', d]
		print( ' '.join(args) )
		subprocess.call( args )

	print( 'Removing old compiled files...' )
	for root, dirs, files in os.walk( '.' ):
		for f in files:
			fname = os.path.join( root, f )
			if os.path.splitext(fname)[1] == '.pyc':
				os.remove( fname )
	
	print( 'Pre-compiling source code...' )
	compileall.compile_dir( '.', quiet=True )

if __name__ == '__main__':
	parser = argparse.ArgumentParser( description='Update CrossMgr Dependencies' )
	parser.add_argument(
		'--upgrade',
		action='store_true',
		default=False,
	)
	
	args = parser.parse_args()
	update_dependencies( args.upgrade )
