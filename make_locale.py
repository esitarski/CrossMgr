import os
import subprocess
import errno
import glob
import shutil
import io

cmd = ['pybabel']

CrossMgrLocale = 'CrossMgrLocale'

try:
	os.makedirs( os.path.join(CrossMgrLocale,'fr','LC_MESSAGES') )
except OSError as e:
	if not os.path.join(CrossMgrLocale,'fr','LC_MESSAGES'):
		raise

#-----------------------------------------------------------------------
# Extract the strings.
#
dir = 'locale_src'
try:
	shutil.rmtree( dir )
except:
	pass

os.makedirs( dir )
for f in glob.glob( '*.py' ):
	shutil.copy( f, dir )

pot = os.path.join(CrossMgrLocale, "messages.pot")
subprocess.call( cmd + ["extract", "-o", pot, dir] )

shutil.rmtree( dir )

with io.open(pot, 'r', encoding='utf-8') as f:
	contents = f.read()
contents = contents.replace( 'locale_src/', '' )
with io.open(pot, 'w', encoding='utf-8') as f:
	f.write( contents )

#-----------------------------------------------------------------------
# Create/Merge translation file.
#
po = os.path.join(CrossMgrLocale, 'fr', 'LC_MESSAGES', 'messages.po')
if os.path.exists( po ):
	subprocess.call( cmd + ["update", "-d", CrossMgrLocale, "-i", pot] )
else:
	subprocess.call( cmd + ["init", "-d", CrossMgrLocale, "-l", "fr", "-i", pot] )
	
#-----------------------------------------------------------------------
# Compile the translation file.
#
subprocess.call( cmd + ["compile", "-f", "-d", CrossMgrLocale, "-l", "fr", "-i", po] )
