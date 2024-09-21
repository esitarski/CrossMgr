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
#     python3 crossmgr-install.py install
#
# This will download and install all CrossMgr programs and also create desktop shortcuts.
# It also creates a desktop shortcut to re-run the script.
# To upgrade to the latest CrossMgr, run the install from the desktop, or run this script again.
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
import re
import sys
import json
import shutil
import bisect
import zipfile
import argparse
import operator
import platform
import datetime
import subprocess
import contextlib
from collections import defaultdict
from html.parser import HTMLParser
import urllib.request

do_debug=False

zip_file_url = 'https://github.com/esitarski/CrossMgr/archive/refs/heads/master.zip'	# url of the CrossMgr source code zip file on github.

src_dir = 'CrossMgr-master'			# directory of the source code files.
env_dir = 'CrossMgr-env'			# directory of the python environment.
archive_dir = 'CrossMgr-archive'	# directory of previous releases.

wxpython_extras_url = 'https://extras.wxpython.org/wxPython4/extras/linux/gtk3/'

is_linux    = (platform.system() == 'Linux')
is_mac      = (platform.system() == 'Darwin')
is_windows  = (platform.system() == 'Windows')

@contextlib.contextmanager
def in_dir( x ):
	# Temporarily switch to another directory using a "with" statement.
	d = os.getcwd()
	os.chdir( x )
	try:
		yield
	finally:
		os.chdir( d )

def remove_ignore( file_name, show_error=False ):
	try:
		os.remove( file_name )
		return True
	except Exception as e:
		if show_error:
			print( f'remove error: {e}', flush=True )
		return False

def rmdir_ignore( d, show_error=False ):
	try:
		shutil.rmtree( d, ignore_errors=True )
		return True
	except Exception as e:
		if show_error:
			print( f'rmdir error: {e}', flush=True )
		return False

def get_install_dir():
	# Install into the user's home directory.
	# This is the only folder that is guaranteed that we can write to.
	return os.path.join(os.path.expanduser('~'), 'Projects', 'install') if do_debug else os.path.expanduser('~')

def dir_setup():
	os.chdir( get_install_dir() )

def src_download():
	# Pull the source and resources from github.
	zip_file_name = 'CrossMgrSrc.zip'
	
	print( f"Downloading CrossMgr source to: {os.path.abspath('.')}... ", end='', flush=True )
	urllib.request.urlretrieve( zip_file_url, filename=zip_file_name )
	print( 'Done.' )
	
	# Unzip everything to the new folder.
	print( f"Extracting CrossMgr source to: {os.path.abspath(os.path.join('.',src_dir))}... ", end='', flush=True )
	
	rmdir_ignore( src_dir, True )
	
	with zipfile.ZipFile( zip_file_name ) as z:
		z.extractall( '.' )
	
	remove_ignore( zip_file_name, True )

	print( 'Done.' )
	
def get_wxpython_versions():
	# Read the extras page.
	with urllib.request.urlopen(wxpython_extras_url) as request:
		contents = request.read().decode( encoding='utf8' )

	distro_versions = defaultdict( list )
	class DVHTMLParser(HTMLParser):
		def handle_starttag(self, tag, attrs):
			if tag != 'a':
				return
			attrs = {k:v for k,v in attrs}
			try:
				href = attrs['href']
			except KeyError:
				return
			if '-' not in href:
				return
			fields = href.split('-')
			if len(fields) != 2:
				return
			
			distro, version = fields
			if version.endswith('/'):
				version = version[:-1]
			distro_versions[distro].append( (float(version), version) )

	DVHTMLParser().feed( contents )
	for distro, versions in distro_versions.items():
		versions.sort( key = operator.itemgetter(0) )
	return distro_versions

def get_python_exe( env_dir ):
	# Get the path to python in the env.
	if is_windows:
		python_exe = os.path.abspath( os.path.join('.', env_dir, 'Scripts', 'python.exe') )
	else:
		python_exe = os.path.abspath( os.path.join('.', env_dir, 'bin', 'python3') )
	return python_exe

def env_setup( full=False ):	
	python_exe = get_python_exe( env_dir )

	# Create a local environment for Python.  Install all our dependencies here.
	if full or not os.path.isdir(env_dir) or not os.path.isfile(python_exe):
		print( f"Removing existing python environment {os.path.abspath(os.path.join('.',env_dir))}... ", end='', flush=True )
		try:
			shutil.rmtree( env_dir, ignore_errors=True )
		except Exception as e:
			print( f"Failure: {e}... ", end='', flush=True )
		print( 'Done.' )
		
		print( f"Creating python environment in {os.path.abspath(os.path.join('.',env_dir))}... ", end='', flush=True )
		subprocess.check_output( [sys.executable, '-m', 'venv', env_dir] )	# Call this with the script's python as we don't have an environment yet.
		print( 'Done.' )
	else:
		print( f"Using existing python environment {os.path.abspath(os.path.join('.',env_dir))}.", flush=True )

	print( "Updating python environment (takes a few minutes, especially on first install)... ", end='', flush=True )
	os.chdir( src_dir )
	
	# Upgrade pip first.
	subprocess.check_output( [python_exe, '-m', 'pip', 'install', '--upgrade', '--quiet', 'pip'] )
	
	if is_linux:
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
		
		# If this is an ubuntu flavor, use the ubuntu version.
		os_name = os_name.lower()
		if any( f in os_name for f in ('buntu', 'mint') ):
			os_name = 'ubuntu'
		wxpython_versions = get_wxpython_versions()

		# Check if this os is supported.
		if os_name not in wxpython_versions:
			print( f'\n***** CrossMgr is not supported on: {os_name}-{os_version} *****' )
			print( f'See {wxpython_extras_url} for supported Linux platforms and versions.' )
			uninstall()
			sys.exit( -1 )

		# Find the closest, lower version of wxPython.
		f_os_v = float( os_version )
		os_versions = wxpython_versions[os_name]
		f_v = [v[0] for v in os_versions]
		i = bisect.bisect_left( f_v, f_os_v, hi=len(f_v)-1 )
		if i and f_v[i] > f_os_v:
			i -= 1
		
		if os_version != os_versions[i][1]:
			print( f'\n***** Warning: CrossMgr is not supported on: {os_name}-{os_version} *****' )
			print( 'Using closest version: {os_name}-{os_versions[i][1]}' )
			print( 'This may not work!' )

		os_version = os_versions[i][1]
		
		# Get the name of the python extras url.
		url = f'{wxpython_extras_url}/{os_name}-{os_version}'
		
		# Install wxPyhon from the extras url.
		subprocess.check_output( [
			python_exe, '-m',
			'pip', 'install', '--upgrade', '--quiet', '-f', url, 'wxPython',
		], stderr=subprocess.DEVNULL )		# Hide stderr so we don't scare the user with DEPRECATED warnings.
	else:
		# If Windows or Mac, install mostly everything from regular pypi.
		with open('requirements.txt', encoding='utf8') as f_in, open('requirements_os.txt', 'w', encoding='utf8') as f_out:
			if is_windows:
				# Add winshell so we can do more with window shortcuts and suffix bindings.
				f_out.write( 'winshell\n' )
			
			for line in f_in:
				if 'pybabel' not in line:	# Skip pybabel.  Use polib instead to convert the .po files to .mo.
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
	context = {
		'pofiles': pofiles,
	}
	content = '\n'.join( [
		'import os',
		'import polib',
		f'context = {json.dumps(context)}',
		"for file in context['pofiles']:",
		"    po = polib.pofile(file)",
		"    po.save_as_mofile( os.path.splitext(file)[0] + '.mo' )",
	] )
	with open(po_to_mo_fname, 'w', encoding='utf8') as f:
		f.write( content )
	
	subprocess.check_output( [python_exe, po_to_mo_fname] )
	remove_ignore( po_to_mo_fname, True )
	print( 'Done.' )

	print( "Compiling all .py files... ", end='', flush=True )
	subprocess.check_output( [python_exe, '-m', 'compileall', '-q', ] )
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

def get_ico_file( pyw_file ):
	extension = {
		'Windows': 	'.ico',
		'Linux':	'.png',
		'Darwin':	'.icns',
	}
	fname = os.path.basename( pyw_file )
	basename = os.path.splitext( fname )[0]
	dirname = os.path.dirname( pyw_file )
	dirimages = os.path.join( dirname, basename + 'Images' )
	return os.path.join( dirimages, basename + extension.get(platform.system(), '.png') )
		
def make_file_associations( python_exe='', uninstall_assoc=False ):
	suffix_for_name = {
		'CrossMgr':		'.cmn',
		'SeriesMgr':	'.smn',
		'SprintMgr':	'.smr',
	}
	
	if is_windows:
		print( "{} file associations... ".format(['Making','Uninstalling'][uninstall_assoc]), end='', flush=True )

		python_launch_exe = python_exe.replace( 'python.exe', 'pythonw.exe' )

		assoc_fname = os.path.abspath( os.path.join('.', 'make_assoc_tmp.bat') )
		with open(assoc_fname, 'w', encoding='utf8') as f:
			for pyw in get_pyws():
				name = get_name( pyw )
				if name in suffix_for_name:
					if uninstall_assoc:
						f.write( f'assoc {suffix_for_name[name]}=\n' )
					else:
						f.write( f'assoc {suffix_for_name[name]}={name}\n' )
						f.write( f'ftype {name}="{python_launch_exe}" "{pyw}" "%1"\n' )
						f.write( fr'reg delete hkcr\{name}\DefaultIcon' + '\n' )
						f.write( fr'reg add hkcr\{name}\DefaultIcon /ve /d "{get_ico_file(pyw)}"' + '\n' )

		subprocess.check_output( [assoc_fname], shell=True, cwd=os.path.dirname(assoc_fname) )
		remove_ignore( assoc_fname )

		print( 'Done.' )
	elif is_mac:
		pass
	elif is_linux:
		pass

def make_shortcuts( python_exe ):
	print( "Making desktop shortcuts... ", end='', flush=True )
	
	if is_windows:
		python_launch_exe = python_exe.replace( 'python.exe', 'pythonw.exe' )
	else:
		python_launch_exe = python_exe

	pyws = sorted( get_pyws(), reverse=True )
	
	shortcuts_fname = os.path.abspath( os.path.join('.', 'make_shortcuts_tmp.py') )
	
	context = {
		'python_launch_exe': python_launch_exe,
		'shortcut_info': [ {
				'script':pyw,
				'icon':get_ico_file(pyw),
				'name':get_name(pyw)
			} for pyw in pyws
		],
	}
	contents = '\n'.join( [
		'from sys import exit',
		'from pyshortcuts import make_shortcut',
		f'context = {json.dumps(context)}',
		"for shortcut_args in context['shortcut_info']:",
		"    make_shortcut( terminal=False, startmenu=False, executable=context['python_launch_exe'], **shortcut_args )",
		"exit(0)",
	] )
	
	with open(shortcuts_fname, 'w', encoding='utf8') as f:
		f.write( contents )
	
	try:
		subprocess.check_output( [python_exe, shortcuts_fname] )
	except subprocess.CalledProcessError as e:
		print( 'Error:', e )
	finally:
		remove_ignore( shortcuts_fname )
	
	# Create a shortcut for this update script.
	# Remember, we are in the CrossMgr-master directory.
	context = {
		'python_exe': python_exe,	# Use the stock python, not the env python.
		'shortcut_args': {
			'script': __file__ + ' install',	# Add "install" command to the script.
			'icon': os.path.abspath( os.path.join('.', 'CrossMgrImages', 'CrossMgrDownload.ico' if is_windows else 'CrossMgrDownload.png') ),
			'name': 'Update CrossMgr',
		}
	}
	contents = '\n'.join( [
		'from sys import exit',
		'from pyshortcuts import make_shortcut',
		f'context = {json.dumps(context)}',
		"make_shortcut( terminal=True, startmenu=False, executable=context['python_exe'], **context['shortcut_args'] )",
		"exit(0)",
	] )
	
	with open(shortcuts_fname, 'w', encoding='utf8') as f:
		f.write( contents )
	
	try:
		subprocess.check_output( [python_exe, shortcuts_fname] )
	except subprocess.CalledProcessError as e:
		print( 'Error:', e )
	finally:
		remove_ignore( shortcuts_fname )
	
	print( 'Done.' )

re_timestamp = re.compile( r'(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2}\-\d{6})' )

def make_archive():
	install_dir = get_install_dir()
	timestamp = datetime.datetime.now().strftime( '%Y%m%dT%H%M%S-%f' )
	
	archive_dir_version = os.path.join( archive_dir, timestamp )
	src_dir_archive = os.path.join( archive_dir, timestamp, src_dir )
	env_dir_archive = os.path.join( archive_dir, timestamp, env_dir )
						
	with in_dir( install_dir ):
		if os.path.isdir(env_dir) and os.path.isdir(src_dir):
			print( f"Archiving current version to: {os.path.join(install_dir,archive_dir_version)}... ", end='', flush=True )
			
			if not os.path.isdir( archive_dir_version ):
				os.makedirs( archive_dir_version )
			
			# Move the src dir as we download it completely on install.
			rmdir_ignore( src_dir_archive )
			shutil.move( src_dir, src_dir_archive )
			
			# Copy the env dir as we incrementally update it on install.
			rmdir_ignore( env_dir_archive )
			shutil.copytree( env_dir, env_dir_archive )
			
			# Clean up excessive archive versions.
			with os.scandir( archive_dir ) as contents:
				dirs = sorted( (d.name for d in contents if d.is_dir() and re.fullmatch(re_timestamp, d.name)), reverse=True )
			for d in dirs[10:]:
				rmdir_ignore( os.path.join(archive_dir, d) )
				
			print( 'Done.' )

def restore_archive():
	install_dir = get_install_dir()
	with in_dir( get_install_dir() ):
		if not os.path.isdir( archive_dir ):
			print( "Archive directory does not exist." )
			return
		
		# Find the most recent archived version and restore it.
		with os.scandir( archive_dir ) as contents:
			dirs = sorted( (d.name for d in contents if d.is_dir() and re.fullmatch(re_timestamp, d.name)), reverse=True )
		if not dirs:
			print( "No previously archived version to restore." )
			return
		
		timestamp = dirs[0]
		archive_dir_version = os.path.join( archive_dir, timestamp )
		
		print( f"Restoring from archive {timestamp}... ", end='', flush=True )
		src_dir_archive = os.path.join( archive_dir_version, src_dir )
		env_dir_archive = os.path.join( archive_dir_version, env_dir )
		
		# Delete the current src and env.
		for d in (src_dir, env_dir):
			rmdir_ignore( d )

		# Restore src and env from the archive.
		# It is safe to move the files instead of copy as we don't need to preserve the archive after the restore.
		for d in (src_dir_archive, env_dir_archive):
			shutil.move( d, install_dir )
		
		# Cleanup the directories.
		rmdir_ignore( archive_dir_version )
		if not list( os.listdir(archive_dir) ):
			rmdir_ignore( archive_dir )
		# Check if the entire 
		print( 'Done.' )

def install( full=False ):
	dir_setup()
	make_archive()					# Make a copy of the existing install if it exists.
	src_download()
	python_exe = env_setup( full )
	fix_dependencies( python_exe )
	make_bin( python_exe )
	make_shortcuts( python_exe )
	make_file_associations( python_exe )

	print( "CrossMgr updated successfully." )
	print( "Check your desktop for shortcuts which allow you to run the CrossMgr applications." )
	print()
	print( "Additionally, there are scripts which will can run the programs." )
	bin_dir = os.path.abspath( os.path.join( '.', src_dir, 'bin') )
	print( f"These can be found in {bin_dir}." )
	print()
	print( 'Use these scripts to configure auto-launch for CrossMgr file extensions.' )
	print()
	print( 'Information about the CrossMgr suite of applications can be found at: https://github.com/esitarski/CrossMgr')
	print( 'The CrossMgr users group is here: https://groups.google.com/g/crossmgrsoftware' )
	print()
	print( 'Thank you for using CrossMgr.' )
	
def uninstall():
	install_dir = get_install_dir()
	home_dir = os.path.expanduser('~')
	
	cross_mgr_source_dir = os.path.join(install_dir, src_dir)
	if os.path.isdir( cross_mgr_source_dir ):
		# Get all pyw files from the src dir.
		with in_dir( cross_mgr_source_dir ):
			pyws = list( get_pyws() )
		pyws.append( 'Update CrossMgr.pyw' )	# Add the install shortcut itself.
	else:
		pyws = []
	
	make_file_associations( uninstall_assoc=True )
	
	print( "Removing CrossMgr desktop shortcuts... ", end='', flush=True )
	
	if not is_windows:
		desktop_dir = os.path.join( home_dir, 'Desktop' )
	else:
		# Get the desktop folder.  We have to call the python in the env to get winshell.
		python_exe = get_python_exe( os.path.join(install_dir, env_dir) )
		fname = os.path.join( install_dir, src_dir, 'get_desktop_tmp.py' )
		with open(fname, 'w', encoding='utf8') as f:
			f.write( 'import sys\n' )
			f.write( 'import winshell\n' )
			f.write( 'print( winshell.desktop() )\n' )
			f.write( 'sys.exit(0)\n' )
		try:
			desktop_dir = subprocess.check_output( [python_exe, fname], encoding='utf8' )
		except Exception as e:
			desktop_dir = None
		os.remove( fname )
		
	if desktop_dir is not None and os.path.isdir(desktop_dir):
		for pyw in pyws:
			fname = os.path.join( desktop_dir, get_name(pyw) ) + ('.lnk' if is_windows else '.desktop')
			if os.path.isfile(fname):
				remove_ignore( fname, True )
		print( 'Done.' )
	else:
		print( '\nError removing CrossMgr desktop shortcuts.  You must remove them manually.' )
	
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
	
	if os.path.isdir( os.path.join(install_dir, archive_dir) ):
		print( "Removing CrossMgr archive... ", end='', flush=True )
		rmdir_ignore( os.path.join(install_dir, archive_dir), True )
		print( 'Done.' )
	
	print( "Removing CrossMgr log files... ", end='', flush=True )
	pyws_set = set( pyws )
	for fn in os.listdir( home_dir ):
		fname = os.path.join( home_dir, fn )
		if fname.endswith('.log') and os.path.isfile(fname):
			pyw_log = os.path.splitext(os.path.basename(fname))[0] + '.pyw'
			if pyw_log in pyws_set:
				remove_ignore( fname, True )
	print( 'Done.' )

	
if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Installs/uninstalls all programs in the CrossMgr suite.',
		epilog='The install downloads and updates all CrossMgr programs and configures them to run in a local environment.  Requires internet access.'
	)
	subparsers = parser.add_subparsers( required=True, dest='sub_command' )	# dest specifies the attribute field of the subparser, in this case "sub_command".
	
	p_install = subparsers.add_parser(
		'install',
		help='Installs CrossMgr source and Python environment (default).'
	)
	p_install.add_argument(
		'-f', '--full',
		action='store_true',
		help="Forces a full install of the python environment.  Otherwise, the python environment is updated (faster).  Required if you upgrade your computer's python version."
	)	
	
	p_uninstall = subparsers.add_parser(
		'uninstall',
		help='Removes the CrossMgr source, Python environment and archive.'
	)
	
	p_restore = subparsers.add_parser(
		'restore',
		help="Restores to the last install (if available)."
	)

	dispatch = {
		'install':		lambda args: install( args.full ),
		'uninstall': 	lambda args: uninstall(),
		'restore':		lambda args: restore_archive(),
	}
	
	args = parser.parse_args()	
	dispatch[args.sub_command]( args )
