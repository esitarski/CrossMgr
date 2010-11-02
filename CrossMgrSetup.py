from distutils.core import setup
import py2exe
import os
import shutil

setup( windows=
			[
				{
					'script': 'CrossMgr.pyw',
					'icon_resources': [(1, r'images\CrossMgr.ico')]
				}
			]
	 )

distDir = 'dist'

# Copy additional dlls to distribution folder.
wxHome = r'C:\Python26\Lib\site-packages\wx-2.8-msw-ansi\wx'
shutil.copy( os.path.join(wxHome, 'MSVCP71.dll'), distDir )
shutil.copy( os.path.join(wxHome, 'gdiplus.dll'), distDir )

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
copyDir( 'data' )

# Create the installer
inno = r'\Program Files\Inno Setup 5\ISCC.exe'
# Find the drive it is installed on.
for drive in ['C', 'D']:
	innoTest = drive + ':' + inno
	if os.path.exists( innoTest ):
		inno = innoTest
		break
cmd = '"' + inno + '" ' + 'CrossMgr.iss'
print cmd
os.system( cmd )

import shutil
from Version import AppVerName
vNum = AppVerName.split()[1]
vNum = vNum.replace( '.', '_' )
newExeName = 'CrossMgr_Setup_v' + vNum + '.exe'
shutil.copy( 'install\\CrossMgr_Setup.exe', 'install\\' + newExeName )
print 'executable copied to: ' + newExeName
