from distutils.core import setup
import os
import shutil
import zipfile
import sys
import subprocess

if os.path.exists('build'):
	shutil.rmtree( 'build' )

# Copy all dependent files into this folder.
copyFiles = [
	"Model.py",
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
	"MatchingCategory.py",
	"ReadCategoriesFromExcel.py",
	"ReadPropertiesFromExcel.py",
	"scramble.py",
]

for f in copyFiles:
	shutil.copy( os.path.join( '..', f), f )
	
with open('Dependencies.py', 'w') as fp:
	for f in copyFiles:
		fp.write( 'import {}\n'.format(f[:-3]) )

#----------------------------------------------------------------------------------------------------

distDir = r'dist\SeriesMgr'
distDirParent = os.path.dirname(distDir)
if os.path.exists(distDirParent):
	shutil.rmtree( distDirParent )
if not os.path.exists( distDirParent ):
	os.makedirs( distDirParent )

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
	os.mkdir( destD )
	for i in os.listdir( d ):
		if i[-3:] != '.db':	# Ignore .db files.
			shutil.copy( os.path.join(d, i), os.path.join(destD,i) )
			
copyDir( 'CrossMgrImages' )
#copyDir( 'data' )
#copyDir( 'html' )

# Create the installer
inno = r'\Program Files\Inno Setup 5\ISCC.exe'
# Find the drive it is installed on.
for drive in ['C', 'D']:
	innoTest = drive + ':' + inno
	if os.path.exists( innoTest ):
		inno = innoTest
		break
cmd = '"' + inno + '" ' + 'SeriesMgr.iss'
print cmd
os.system( cmd )

# Create versioned executable.
from Version import AppVerName
vNum = AppVerName.split()[1]
vNum = vNum.replace( '.', '_' )
newExeName = 'SeriesMgr_Setup_v' + vNum + '.exe'

try:
	os.remove( 'install\\' + newExeName )
except:
	pass
	
shutil.copy( 'install\\SeriesMgr_Setup.exe', 'install\\' + newExeName )
print 'executable copied to: ' + newExeName

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
print 'executable compressed.'

shutil.copy( newExeName, r"c:\GoogleDrive\Downloads\Windows\SeriesMgr"  )

