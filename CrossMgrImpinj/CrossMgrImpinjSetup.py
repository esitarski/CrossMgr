from distutils.core import setup
import os
import io
import six
import shutil
import zipfile
import datetime
import subprocess

if os.path.exists('build'):
	shutil.rmtree( 'build' )

distDir = r'dist\CrossMgrImpinj'
distDirParent = os.path.dirname(distDir)
if os.path.exists(distDirParent):
	shutil.rmtree( distDirParent )
if not os.path.exists( distDirParent ):
	os.makedirs( distDirParent )

gds = [
	r"c:\GoogleDrive\Downloads\Windows",
	r"C:\Users\edwar\Google Drive\Downloads\Windows",
	r"C:\Users\Edward Sitarski\Google Drive\Downloads\Windows",
]
for googleDrive in gds:
	if os.path.exists(googleDrive):
		break
googleDrive = os.path.join( googleDrive, 'CrossMgrImpinj' )
	
subprocess.call( [
	'pyinstaller',
	
	'CrossMgrImpinj.pyw',
	'--icon=' + os.path.join('CrossMgrImpinjImages','CrossMgrImpinj.ico'),
	'--clean',
	'--windowed',
	'--noconfirm',
	
	'--hidden-import=numpy',
	
	'--exclude-module=tcl',
	'--exclude-module=tk',
	'--exclude-module=Tkinter',
	'--exclude-module=_tkinter',
] )

# Copy additional dlls to distribution folder.
wxHome = r'C:\Python27\Lib\site-packages\wx-2.8-msw-ansi\wx'
try:
	shutil.copy( os.path.join(wxHome, 'MSVCP71.dll'), distDir )
except:
	pass
try:
	shutil.copy( os.path.join(wxHome, 'gdiplus.dll'), distDir )
except:
	pass

# Add images to the distribution folder.

def copyDir( d ):
	destD = os.path.join(distDir, d)
	if os.path.exists( destD ):
		shutil.rmtree( destD )
	os.mkdir( destD )
	for i in os.listdir( d ):
		if i[-3:] != '.db':	# Ignore .db files.
			shutil.copy( os.path.join(d, i), os.path.join(destD,i) )
			
copyDir( 'CrossMgrImpinjImages' )

# Create the installer
inno = r'\Program Files (x86)\Inno Setup 5\ISCC.exe'
# Find the drive it is installed on.
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
	with io.open('inno_setup.txt', 'w') as f:
		for k, v in six.iteritems(setup):
			f.write( '{}={}\n'.format(k,v) )
make_inno_version()
cmd = '"' + inno + '" ' + 'CrossMgrImpinj.iss'
six.print_( cmd )
os.system( cmd )

# Create versioned executable.
from Version import AppVerName
vNum = AppVerName.split()[1]
vNum = vNum.replace( '.', '_' )
newExeName = 'CrossMgrImpinj_Setup_v' + vNum + '.exe'

try:
	os.remove( os.path.join('install', newExeName ) )
except:
	pass
	
shutil.copy( os.path.join('install', 'CrossMgrImpinj_Setup.exe'), os.path.join('install', newExeName) )
six.print_(  'executable copied to: ' + newExeName )

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
six.print_(  'executable compressed.' )

shutil.copy( newZipName, googleDrive  )
shutil.copy( '../CrossMgrImpinjReadme.pdf', googleDrive  )

from virus_total_apis import PublicApi as VirusTotalPublicApi
API_KEY = '64b7960464d4dbeed26ffa51cb2d3d2588cb95b1ab52fafd82fb8a5820b44779'
vt = VirusTotalPublicApi(API_KEY)
six.print_( 'VirusTotal Scan' )
vt.scan_file( os.path.abspath(newExeName) )


