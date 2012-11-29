from distutils.core import setup
import py2exe
import os
import shutil
import zipfile

distDir = 'dist'

# Cleanup existing dll, pyd and exe files.  The old ones may not be needed, so it is best to clean these up.
for f in os.listdir(distDir):
	if f.endswith('.dll') or f.endswith('.pyd') or f.endswith('.exe'):
		fname = os.path.join(distDir, f)
		print 'deleting:', fname
		os.remove( fname )
		
setup( windows=
			[
				{
					'script': 'CrossMgrAlien.pyw',
					'icon_resources': [(1, r'images\CrossMgrAlien.ico')]
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
			
copyDir( 'images' )

# Create the installer
inno = r'\Program Files\Inno Setup 5\ISCC.exe'
# Find the drive it is installed on.
for drive in ['C', 'D']:
	innoTest = drive + ':' + inno
	if os.path.exists( innoTest ):
		inno = innoTest
		break
cmd = '"' + inno + '" ' + 'CrossMgrAlien.iss'
print cmd
os.system( cmd )

# Create versioned executable.
from Version import AppVerName
vNum = AppVerName.split()[1]
vNum = vNum.replace( '.', '_' )
newExeName = 'CrossMgrAlien_Setup_v' + vNum + '.exe'

try:
	os.remove( 'install\\' + newExeName )
except:
	pass
	
shutil.copy( 'install\\CrossMgrAlien_Setup.exe', 'install\\' + newExeName )
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
