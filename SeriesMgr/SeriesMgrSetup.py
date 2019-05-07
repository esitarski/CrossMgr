from distutils.core import setup
import os
import six
import shutil
import zipfile
import sys
import datetime
import subprocess
import platform

# Copy all dependent files into this folder.
copyFiles = [
	"Model.py",
	"InSortedIntervalList.py",
	"minimal_intervals.py",
	"Utils.py",
	"rsonlite.py",
	"Checklist.py",
	"GpxParse.py",
	"GeoAnimation.py",
	"Animation.py",
	"GanttChart.py",
	"Excel.py",
	"arial10.py",
	"GetResults.py",
	"FitSheetWrapper.py",
	"ReadSignOnSheet.py",
	"HelpSearch.py",
	"MatchingCategory.py",
	"ModuleUnpickler.py",
	"BatchPublishAttrs.py",
	"ReadCategoriesFromExcel.py",
	"ReadPropertiesFromExcel.py",
	"ModuleUnpickler.py",
	"GetMatchingExcelFile.py",
	"SetGraphic.py",
	"imagebrowser.py",
	"scramble.py",
]

for f in copyFiles:
	shutil.copy( os.path.join( '..', f), f )
	
with open('Dependencies.py', 'w') as fp:
	for f in copyFiles:
		fp.write( 'import {}\n'.format(f[:-3]) )

if os.path.exists('build'):
	shutil.rmtree( 'build' )
	
if platform.platform() == 'Linux':
	sys.exit()

gds = [
	r"c:\GoogleDrive\Downloads\Windows",
	r"C:\Users\edwar\Google Drive\Downloads\Windows",
	r"C:\Users\Edward Sitarski\Google Drive\Downloads\Windows",
]
for googleDrive in gds:
	if os.path.exists(googleDrive):
		break
googleDrive = os.path.join( googleDrive, 'SeriesMgr' )

# Compile the help files
from helptxt.compile import CompileHelp
CompileHelp( 'helptxt' )

if 'win' not in sys.platform.lower():
	sys.exit()
	
#----------------------------------------------------------------------------------------------------

distDir = os.path.join('dist', 'SeriesMgr')
distDirParent = os.path.dirname(distDir)
if os.path.exists(distDirParent):
	shutil.rmtree( distDirParent )
if not os.path.exists( distDir ):
	os.makedirs( distDir )

subprocess.call( [
	'pyinstaller',
	
	'SeriesMgr.pyw',
	'--icon=CrossMgrImages\SeriesMgr.ico',
	'--clean',
	'--windowed',
	'--noconfirm',
	
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
	os.makedirs( destD )
	for i in os.listdir( d ):
		if i[-3:] != '.db':	# Ignore .db files.
			shutil.copy( os.path.join(d, i), os.path.join(destD,i) )
			
copyDir( 'CrossMgrImages' )
copyDir( 'SeriesMgrHtmlDoc' )
#copyDir( 'data' )

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
	with open('inno_setup.txt', 'w') as f:
		for k, v in six.iteritems(setup):
			f.write( '{}={}\n'.format(k,v) )
make_inno_version()
cmd = '"' + inno + '" ' + 'SeriesMgr.iss'
six.print_( cmd )
os.system( cmd )

# Create versioned executable.
from Version import AppVerName
vNum = AppVerName.split()[1].replace( '.', '_' )
newExeName = 'SeriesMgr_Setup_v' + vNum + '.exe'

try:
	os.remove( os.path.join('install',newExeName) )
except:
	pass
	
shutil.copy( os.path.join('install', 'SeriesMgr_Setup.exe'), os.path.join('install', newExeName) )
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
six.print_( 'executable compressed.' )

shutil.copy( newZipName, googleDrive  )

from virus_total_apis import PublicApi as VirusTotalPublicApi
API_KEY = '64b7960464d4dbeed26ffa51cb2d3d2588cb95b1ab52fafd82fb8a5820b44779'
vt = VirusTotalPublicApi(API_KEY)
six.print_( 'VirusTotal Scan' )
vt.scan_file( os.path.abspath(newExeName) )

