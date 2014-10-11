from distutils.core import setup
import py2exe
import os
import shutil
import zipfile

# Update the minor version number.
#AppVerName="CrossMgr 1.87.x"
'''
with open('Version.py', 'r') as f:
	v = f.read().strip()
	i = v.rfind( ' ' )
	s = v[i+1:-1]
	vNums = s.split('.')
	if len(vNums) == 2:
		vNums.append( '0' )
	else:
		vNums[-1] = str(int(vNums[-1]) + 1)
	s = 'AppVerName="CrossMgr %s"\n' % ('.'.join(vNums))
with open('Version.py', 'w') as f:
	f.write( s )
'''

if os.path.exists('build'):
	shutil.rmtree( 'build' )


# Compile the help files
from helptxt.compile import CompileHelp
CompileHelp( 'helptxt' )

# Index the help files.
from HelpIndex import BuildHelpIndex
BuildHelpIndex()
	
distDir = 'dist'

# Cleanup existing dll, pyd and exe files.  The old ones may not be needed, so it is best to clean these up.
for f in os.listdir(distDir):
	if f.endswith('.dll') or f.endswith('.pyd') or f.endswith('.exe'):
		fname = os.path.join(distDir, f)
		os.remove( fname )

# Set up the py2exe configuration.
setup(	windows = [
			{
				'script': 'CrossMgr.pyw',
				'icon_resources': [(1, r'CrossMgrImages\CrossMgr.ico')],
			}
		],
		options = {
			'py2exe':{
					'includes': ['VideoCapture',],
			},
		},
	 )

# Copy additional dlls to distribution folder.
wxHome = r'C:\Python27\Lib\site-packages\wx-3.0-msw\wx'
try:
	shutil.copy( os.path.join(wxHome, 'MSVCP71.dll'), distDir )
except:
	pass
try:
	shutil.copy( os.path.join(wxHome, 'gdiplus.dll'), distDir )
except:
	pass

# Add images and reference data to the distribution folder.
def copyDir( d ):
	destD = os.path.join(distDir, d)
	if os.path.exists( destD ):
		shutil.rmtree( destD )
	os.mkdir( destD )
	for i in os.listdir( d ):
		if not i.endswith( '.db' ):	# Ignore .db files.
			shutil.copy( os.path.join(d, i), os.path.join(destD,i) )
			
for dir in ['CrossMgrImages', 'data', 'CrossMgrHtml', 'CrossMgrHtmlDoc', 'CrossMgrHelpIndex']: 
	copyDir( dir )

# Create the installer
inno = r'\Program Files\Inno Setup 5\ISCC.exe'
# Find the drive inno is installed on.
for drive in ['C', 'D']:
	innoTest = drive + ':' + inno
	if os.path.exists( innoTest ):
		inno = innoTest
		break
cmd = '"' + inno + '" ' + 'CrossMgr.iss'
print cmd
os.system( cmd )

# Create versioned executable.
from Version import AppVerName
vNum = AppVerName.split()[1]
vNum = vNum.replace( '.', '_' )
newExeName = 'CrossMgr_Setup_v' + vNum + '.exe'

try:
	os.remove( 'install\\' + newExeName )
except:
	pass
	
shutil.copy( 'install\\CrossMgr_Setup.exe', 'install\\' + newExeName )
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

shutil.copy( newZipName, r"c:\GoogleDrive\Downloads\Windows\CrossMgr"  )
