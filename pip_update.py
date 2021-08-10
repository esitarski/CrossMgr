import re
import os
import sys
import shutil
import subprocess

def pip_update():
	# Check for Ubuntu and get the wxPython extras release version.
	UBUNTU_RELEASE = ''
	os_release_file = '/etc/os-release'
	if os.path.exists( os_release_file ):
		with open( os_release_file ) as f:
			for line in f:
				line = line.strip()
				if line.startswith('VERSION_ID'):
					UBUNTU_RELEASE = '.'.join(re.sub('[^0-9.]', '', line).split('.')[:2])
					break

	# Update all the requirements.
	fname = 'requirements.txt'
	with open(fname) as f:
		for package in f:
			package = package.strip()
			if UBUNTU_RELEASE and 'wxPython' in package:
				package = '-f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-{} wxPython'.format( UBUNTU_RELEASE )
			cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', *package.split()]
			print( ' '.join( cmd ) )
			subprocess.check_call( cmd )

def process_dependencies():
	# Process Dependencies in the subprojects.
	with os.scandir('.') as cur_dir:
		for f in cur_dir:
			if not f.is_dir():
				continue
			dep_name = os.path.join( f.path, 'Dependencies.py' )
			if os.path.exists( dep_name ):
				with open(dep_name) as dep_file:
					for entry in dep_file:
						entry = entry.strip().split()
						if len(entry) != 2 or entry[0] != 'import':
							continue
						py_file = entry[1] + '.py'
						cpy_args = [py_file, os.path.join(f.path, py_file)]
						print( 'cp', *cpy_args )
						shutil.copyfile( *cpy_args )

if __name__ == '__main__':
	#pip_update()
	process_dependencies()
