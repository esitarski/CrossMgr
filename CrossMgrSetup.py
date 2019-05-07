#from distutils.core import setup
import os
import io
import sys
import six
import shutil
import zipfile
import datetime
import subprocess

if os.path.exists('build'):
	shutil.rmtree( 'build' )

gds = [
	r"c:\GoogleDrive\Downloads\Windows",
	r"C:\Users\edwar\Google Drive\Downloads\Windows",
	r"C:\Users\Edward Sitarski\Google Drive\Downloads\Windows",
]
for googleDrive in gds:
	if os.path.exists(googleDrive):
		break
googleDrive = os.path.join( googleDrive, 'CrossMgr' )
	
# Compile the help files
from helptxt.compile import CompileHelp
CompileHelp( 'helptxt' )

# Index the help files.
from HelpIndex import BuildHelpIndex
BuildHelpIndex()

distDir = r'dist\CrossMgr'
distDirParent = os.path.dirname(distDir)
if os.path.exists(distDirParent):
	shutil.rmtree( distDirParent )
if not os.path.exists( distDirParent ):
	os.makedirs( distDirParent )

subprocess.call( [
	'pyinstaller',
	#'--debug',
	
	'CrossMgr.pyw',
	'--icon=CrossMgrImages\CrossMgr.ico',
	'--clean',
	'--windowed',
	'--noconfirm',
	
	'--exclude-module=tcl',
	'--exclude-module=tk',
	'--exclude-module=Tkinter',
	'--exclude-module=_tkinter',
] )

# Copy additional dlls to distribution folder.
# wxHome = r'C:\Python27\Lib\site-packages\wx-3.0-msw\wx'
# try:
	# shutil.copy( os.path.join(wxHome, 'MSVCP71.dll'), distDir )
# except:
	# pass
# try:
	# shutil.copy( os.path.join(wxHome, 'gdiplus.dll'), distDir )
# except:
	# pass

# Add images and reference data to the distribution folder.
def copyDir( d ):
	destD = os.path.join(distDir, d)
	if os.path.exists( destD ):
		shutil.rmtree( destD )
	shutil.copytree( d, destD, ignore=shutil.ignore_patterns('*.db') )
			
for dir in ['CrossMgrImages', 'data', 'CrossMgrHtml', 'CrossMgrHtmlDoc', 'CrossMgrHelpIndex']: 
	copyDir( dir )

# Copy the locale.
localeD = 'CrossMgrLocale'
destD = os.path.join(distDir, localeD)
if os.path.exists( destD ):
	shutil.rmtree( destD )
shutil.copytree( localeD, destD )

#-------------------------------
#sys.exit()

# Create the installer
inno = r'\Program Files (x86)\Inno Setup 5\ISCC.exe'
# Find the drive inno is installed on.
for drive in ['C', 'D']:
	innoTest = drive + ':' + inno
	if os.path.exists( innoTest ):
		inno = innoTest
		break

from Version import AppVerName
def make_inno_version():
	setup = {
		'AppName':				AppVerName.split()[0],
		'AppPublisher':			"Edward Sitarski",
		'AppContact':			"Edward Sitarski",
		'AppCopyright':			"Copyright (C) 2004-{} Edward Sitarski".format(datetime.date.today().year),
		'AppVerName':			AppVerName,
		'AppPublisherURL':		"http://www.sites.google.com/site/crossmgrsoftware/",
		'AppUpdatesURL':		"http://www.sites.google.com/site/crossmgrsoftware/downloads/",
		'VersionInfoVersion':	AppVerName.split()[1],
	}
	with io.open('inno_setup.txt', 'w', encoding='utf-8') as f:
		for k, v in six.iteritems(setup):
			f.write( '{}={}\n'.format(k,v) )
make_inno_version()

cmd = '"' + inno + '" ' + 'CrossMgr.iss'
six.print_( cmd )
subprocess.call( cmd, shell=True )

# Create versioned executable.
vNum = AppVerName.split()[1].replace( '.', '_' )
newExeName = 'CrossMgr_Setup_v' + vNum + '.exe'

try:
	os.remove( 'install\\' + newExeName )
except:
	pass

shutil.copy( 'install\\CrossMgr_Setup.exe', 'install\\' + newExeName )
six.print_( 'executable copied to: ' + newExeName )

# Create compressed executable.
os.chdir( 'install' )
newExeName = os.path.basename( newExeName )
newZipName = newExeName.replace( '.exe', '.zip' )

try:
	os.remove( newZipName )
except:
	pass

z = zipfile.ZipFile(newZipName, "w")
z.write( newExeName )
z.close()
six.print_( 'executable compressed to: ' + newZipName )

shutil.copy( newZipName, googleDrive  )

from virus_total_apis import PublicApi as VirusTotalPublicApi
API_KEY = '64b7960464d4dbeed26ffa51cb2d3d2588cb95b1ab52fafd82fb8a5820b44779'
vt = VirusTotalPublicApi(API_KEY)
six.print_( 'VirusTotal Scan' )
vt.scan_file( os.path.abspath(newExeName) )

os.chdir( '..' )
shutil.copy( os.path.join('helptxt', 'CrossMgrDocHtml.zip'), googleDrive )

