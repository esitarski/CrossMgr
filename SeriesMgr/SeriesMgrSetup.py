from distutils.core import setup
import py2exe
import os
import shutil
import zipfile
import sys

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
	"arial10.py",
	"GetResults.py",
	"FitSheetWrapper.py",
	"ReadSignOnSheet.py",
	"ReadCategoriesFromExcel.py",
	"ReadPropertiesFromExcel.py",
]

for f in copyFiles:
	shutil.copy( os.path.join( '..', f), f )
	
with open('Dependencies.py', 'w') as fp:
	for f in copyFiles:
		fp.write( 'import {}\n'.format(f[:-3]) )

#----------------------------------------------------------------------------------------------------

distDir = 'dist'

# Cleanup existing dll, pyd and exe files.  The old ones may not be needed, so it is best to clean these up.
for f in os.listdir(distDir):
	if f.endswith('.dll') or f.endswith('.pyd') or f.endswith('.exe'):
		fileName = os.path.join(distDir, f)
		print 'deleting:', fileName
		os.remove( fileName )
		
setup( windows=
			[
				{
					'script': 'SeriesMgr.pyw',
					'icon_resources': [(1, r'CrossMgrImages\SeriesMgr.ico')]
				}
			]
	 )

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

# Create comprssed executable.
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
