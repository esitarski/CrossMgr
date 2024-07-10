#-----------------------------------------------------------------------
# Installs all CrossMgr programs and creates desktop shortcuts.
# This is the easiest and fastest way to keep up with the latest version of CrossMgr.
# Works for Linux, Mac and Windows.
#
# Requires Python installed on your machine.
# If you are running Linux, Python is already installed.
#
# On Mac and Windows, you may need to install Python first if you don't already have it.
# See: www.python.org/downloads/ for details.
#
# When installing Python, if you get a prompt to modify your PATH, choose this option.
#
# You only need to install Python once.  You can the run crossmgr-install.py anytime you want.
# Once Python is installed, open a terminal/console/powershell window.
#
# Change to the directory where you downloaded this script (i.e. the Downloads directory).
# Make sure you have an internet connection.
#
# At the command line, enter:
#
#     python3 crossmgr-install.py
#
# This will download and install all CrossMgr programs and also create desktop shortcuts.
# It also creates an icon to re-run the script.
# To upgrade, just run the script again.
#
# For information about the script options (including uninstall), run the script with --help.
#
# For more information about CrossMgr, see https://github.com/esitarski/CrossMgr
#
# Advantages of this script:
#
# * No security or virus errors.
# * One step, quick install for all CrossMgr applications.  About 15Meg download for everything.
# * Smallest disk usage.  Rather than separately include the Python runtime in each exectuable
#   (like pyinstaller), the Python runtime is installed once and reused
#   by all executables.
#
# Edward Sitarski, 2024.
#

import os
import sys
import shutil
import zipfile
import argparse
import httplib2
import platform
import subprocess
import contextlib
import urllib.request

do_debug=False

zip_file_url = 'https://github.com/esitarski/CrossMgr/archive/refs/heads/master.zip'	# url of the CrossMgr source code zip file on github.

src_dir = 'CrossMgr-master'		# directory of the source code files.
env_dir = 'CrossMgrEnv'			# directory of the python environment.

@contextlib.contextmanager
def in_dir( x ):
	# Temporarily switch to another directory in a with statement.
	d = os.getcwd()
	os.chdir( x )
	try:
		yield
	finally:
		os.chdir( d )

def get_install_dir():
	# Install into the user's home directory.
	# This is the only folder that is guaranteed that we can write to.
	return os.path.join(os.path.expanduser('~'), 'Projects', 'install') if do_debug else os.path.expanduser('~')

def dir_setup():
	os.chdir( get_install_dir() )

def src_download():
	# Pull the entire source and resources from github.
	zip_file_name = 'CrossMgrSrc.zip'
	
	print( f"Downloading CrossMgr source to: {os.path.abspath(os.path.join('.',src_dir))}... ", end='', flush=True )
	urllib.request.urlretrieve( zip_file_url, filename=zip_file_name )

	# Remove the existing folder and replace its contents..
	try:
		shutil.rmtree( src_dir, ignore_errors=True )
	except Exception as e:
		pass
	
	# Unzip everything to the new folder.
	z = zipfile.ZipFile( zip_file_name )
	z.extractall( "." )
	print( 'Done.' )

def env_setup( full=False ):
	if full and os.path.isdir( env_dir ):
		print( f"Removing existing python environment {os.path.abspath(os.path.join('.',env_dir))}... ", end='', flush=True )
		try:
			shutil.rmtree( env_dir, ignore_errors=True )
		except Exception as e:
			print( f"Failure: {e}... ", end='', flush=True )
		print( 'Done.' )
	
	if not os.path.isdir( env_dir ):
		print( f"Creating python environment in {os.path.abspath(os.path.join('.',env_dir))}... ", end='', flush=True )
		subprocess.check_output( ['python3', '-m', 'venv', env_dir] )
		print( 'Done.' )
	
	# Get the path to the exe.
	python_exe = os.path.abspath( os.path.join('.', env_dir, 'bin', 'python3') )
	
	print( f"Updating python environment (this could take a few minutes): {os.path.abspath(os.path.join('.',env_dir))}... ", end='', flush=True )
	os.chdir( src_dir )
	if platform.system() == 'Linux':
		# Install wxPython from the "extras" folder.
		with open('requirements.txt', encoding='utf8') as f_in, open('requirements_os.txt', 'w', encoding='utf8') as f_out:
			for line in f_in:
				if 'wxPython' not in line and 'pybabel' not in line:
					f_out.write( line )

		# Install all the regular modules.
		subprocess.check_output( [python_exe, '-m', 'pip', 'install', '--upgrade', '--quiet', '-r', 'requirements_os.txt'] )

		# Get the name and version of this Linux so we can download it from the wxPython extras folder.
		os_name, os_version = None, None
		for line in subprocess.check_output( ['lsb_release', '-a'], stderr=subprocess.STDOUT, encoding='utf8' ).split('\n'):
			if line.startswith( 'Distributor ID:' ):
				os_name = line.split(':')[1].strip().lower()
			elif line.startswith( 'Release:' ):
				os_version = line.split(':')[1].strip().lower()
		
		# Get the name of the python extras url.
		url = f'https://extras.wxpython.org/wxPython4/extras/linux/gtk3/{os_name}-{os_version}'
		
		# Check if the version exists and fail if it doesn't.
		h = httplib2.Http()
		resp = h.request( url, 'HEAD' )
		if int(resp[0]['status']) >= 400:
			print( f'\nCrossMgr is not supported on {os_name} : {os_version}' )
			print( 'See https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ for supported Linux platforms and versions.' )
			uninstall()
			sys.exit( -1 )
		
		# Instally wxPyhon from the extras url.
		subprocess.check_output( [
			python_exe, '-m',
			'pip', 'install', '--upgrade', '-f', url, 'wxPython',
		] )
	else:
		# If Windows or Mac, install mostly everything from regular pypi.
		with open('requirements.txt', encoding='utf8') as f_in, open('requirements_os.txt', 'w', encoding='utf8') as f_out:
			for line in f_in:
				if 'pybabel' not in line:	# Skip pybabel as we don't need it.
					f_out.write( line )
		subprocess.check_output( [python_exe, '-m', 'pip', 'install', '--upgrade', '--quiet', '-r', 'requirements_os.txt'] )

	# Install polib and pyshortcuts for building the mo translation files and setting up the desktop shortcuts, respectively.
	subprocess.check_output( [python_exe, '-m', 'pip', 'install', '--upgrade', '--quiet', 'polib', 'pyshortcuts'] )
	print( 'Done.' )

	return python_exe

def fix_dependencies( python_exe ):
	print( "Fixing dependencies, building/indexing help files... ", end='', flush=True )

	pofiles = []
	for subdir, dirs, files in os.walk('.'):
		for fname in files:
			if (
				fname in ('UpdateDependencies.py', 'HelpIndex.py') or
				(fname == 'compile.py' and os.path.basename(subdir) == 'helptxt')
			):
				# Fix code dependencies and build help files.
				with in_dir( subdir ):
					subprocess.check_output( [python_exe, fname] )
			elif fname == 'Version.py':
				# Remove the "private" from the Version.
					with open(fname, encoding='utf8') as f:
						contents = f.read()
					with open(fname, 'w', encoding='utf8') as f:
						f.write( contents.replace( '-private', '' ) )
			elif fname.endswith( '.po' ):
				pofiles.append( os.path.abspath( os.path.join(subdir, fname)) )
	print( 'Done.' )

	# Write a python script to convert the po files to mo files with polib.
	# This is a big hackyt and I wish there was an easier way to...
	print( "Formatting translation files... ", end='', flush=True )
	po_to_mo_fname = 'po_to_mo_tmp.py'
	with open(po_to_mo_fname, 'w', encoding='utf8') as f:
		f.write( '\n'.join( [
				'import os',
				'import polib',
				"for file in ({}):",
				"    po = polib.pofile(file)",
				"    po.save_as_mofile( os.path.splitext(file)[0] + '.mo' )",
			] ).format( ','.join( f'"{po}"' for po in pofiles ) )
		)
	subprocess.check_output( [python_exe, po_to_mo_fname] )
	os.remove( po_to_mo_fname )
	print( 'Done.' )

	print( "Compiling all .py files... ", end='', flush=True )
	subprocess.check_output( [python_exe, '-m', 'compileall', '-qq', ] )
	print( 'Done.' )

def get_pyws():
	deprecated = ('CrossMgrCamera', 'CrossMgrAlien')
	
	# Return all the pyw files.
	for subdir, dirs, files in os.walk('.'):
		for fname in files:
			if fname.endswith('.pyw') and not any( d in fname for d in deprecated ):
				yield os.path.abspath( os.path.join(subdir, fname) )

def make_bin( python_exe ):
	# Make scripts in CrossMgr-master/bin
	# These scripts can be used to auto-launch from file extensions.
	
	bin_dir = 'bin'
	print( f"Making scripts in directory {os.path.abspath(os.path.join('.',bin_dir))}... ", end='', flush=True )

	try:
		os.mkdir( bin_dir )
	except Exception as e:
		pass

	is_windows = (platform.system() == 'Windows')
	
	home_dir = os.path.expanduser( '~' )
	
	pyws = sorted( get_pyws(), reverse=True )
	with in_dir( bin_dir ):
		for pyw in pyws:
			fbase = os.path.splitext(os.path.basename(pyw))[0]
			fname = fbase + ('.ps1' if is_windows else '.sh')
			with open( fname, 'w', encoding='utf8' ) as f:
				if not is_windows:
					# Create a bash shell script,
					f.write( '#!/usr/bin/env bash\n' )
					f.write( f'cd {home_dir}\n' )
					f.write( f'{python_exe} "{pyw}" "$@"\n' )
				
					# Make the script executable.
					mode = os.fstat( f.fileno() ).st_mode
					mode |= 0o111
					os.fchmod( f.fileno(), mode & 0o777 )
				else:
					# Create a powershell script.
					f.write( f'Start-Process -WorkingDirectory {home_dir} -FilePath "{python_exe}" -ArgumentList "{pyw}" $args\n' )
	
	print( 'Done.' )

def get_name( pyw_file ):
	return os.path.splitext( os.path.basename( pyw_file ) )[0]
		
def make_shortcuts( python_exe ):
	print( "Making desktop shortcuts... ", end='', flush=True )

	def get_ico_file( pyw_file ):
		fname = os.path.basename( pyw_file )
		basename = os.path.splitext( fname )[0]
		dirname = os.path.dirname( pyw_file )
		dirimages = os.path.join( dirname, basename + 'Images' )
		return os.path.join( dirimages, basename + '.ico' )
		
	pyws = sorted( get_pyws(), reverse=True )
	
	shortcuts_fname = 'make_shortcuts_tmp.py'
	
	script_info=tuple( (pyw, get_ico_file(pyw), get_name(pyw)) for pyw in pyws )
	with open(shortcuts_fname, 'w', encoding='utf8') as f:
		f.write( '\n'.join( [
				'from pyshortcuts import make_shortcut',
				"for script, ico, name in {script_info}:",
				"    make_shortcut( terminal=False, startmenu=False, executable='{python_exe}', icon=ico, script=script, name=name )",
			] ).format( python_exe=python_exe, script_info=script_info )
		)
	
	subprocess.check_output( [python_exe, shortcuts_fname] )
	os.remove( shortcuts_fname )
	
	# Create a shortcut for this update script.
	icon = os.path.abspath( os.path.join('.', src_dir, 'CrossMgrImages', 'CrossMgrDownload.png') )
	with open(shortcuts_fname, 'w', encoding='utf8') as f:
		f.write( '\n'.join( [
				'from pyshortcuts import make_shortcut',
				f"make_shortcut( terminal=True, startmenu=False, executable='python3', icon='{icon}', script='{__file__}', name='Update CrossMgr' )",
			] ).format( python_exe=python_exe, script_info=script_info )
		)
	
	subprocess.check_output( [python_exe, shortcuts_fname] )
	os.remove( shortcuts_fname )
	
	print( 'Done.' )

def install( full=False ):
	dir_setup()
	src_download()
	python_exe = env_setup( full )
	fix_dependencies( python_exe )
	make_bin( python_exe )
	make_shortcuts( python_exe )

	print( "CrossMgr updated." )
	print( "See the desktop shortcuts which allow you to run the CrossMgr executables." )
	print()
	print( "Additionally, there are scripts which will can run the executables." )
	bin_dir = os.path.abspath( os.path.join( '.', src_dir, 'bin') )
	print( f"These can be found in {bin_dir}." )
	print()
	print( 'Use these scripts to configure auto-launch for CrossMgr file extensions.' )
	print( 'Enjoy, and thank you for using CrossMgr!' )
	
def uninstall():
	install_dir = get_install_dir()
	
	with in_dir( os.path.join(install_dir, src_dir) ):
		pyws = list( get_pyws() )
	pyws.append( 'Update CrossMgr.pyw' )
	
	print( "Removing CrossMgr source... ", end='', flush=True )
	try:
		shutil.rmtree( os.path.join(install_dir, src_dir), ignore_errors=True )
	except Exception as e:
		print( 'Error: ', e )
	print( 'Done.' )

	print( "Removing CrossMgr python environment... ", end='', flush=True )
	try:
		shutil.rmtree( os.path.join(install_dir, env_dir), ignore_errors=True )
	except Exception as e:
		print( 'Error: ', e )
		
	print( 'Done.' )
	
	desktop_dir = os.path.join( os.path.expanduser('~'), 'Desktop' )
	if os.path.isdir(desktop_dir):
		print( "Removing desktop shortcuts... ", end='', flush=True )
		for pyw in pyws:
			fname = os.path.join( desktop_dir, get_name(pyw) ) + '.desktop'
			if os.path.isfile(fname):
				try:
					os.remove( fname )
				except Exception as e:
					print( 'Error: ', e )
		print( 'Done.' )
	else:
		print( 'Desktop shortcuts must be removed manually.' )
	
if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		prog='crossmgr-install',
		description='Installs all programs in the CrossMgr suite.',
		epilog='Downloads and updates all CrossMgr programs and configures them to run in a local environment.'
	)
	parser.add_argument( '-u', '--uninstall', action='store_true',
		help='Removes the CrossMgr source and Python environment.  Desktop shortcuts must be removed manually.'
	)
	parser.add_argument( '-f', '--full', action='store_true',
		help="Does a full install of the python environment.  Otherwise, an incremental update is done for speed.  Required if you upgrade your computer's python version."
	)
	args = parser.parse_args()
	
	if args.uninstall:
		uninstall()
	else:
		install( args.full )
