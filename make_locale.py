import os
import subprocess
import errno
import glob
import shutil
import io

cmd = ['pybabel']

try:
	os.makedirs( os.path.join('locale','fr','LC_MESSAGES') )
except OSError as e:
	if not os.path.join('locale','fr','LC_MESSAGES'):
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

pot = os.path.join("locale", "messages.pot")
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
po = 'locale/fr/LC_MESSAGES/messages.po'
if os.path.exists( po ):
	subprocess.call( cmd + ["update", "-d", "locale", "-i", pot] )
else:
	subprocess.call( cmd + ["init", "-d", "locale", "-l", "fr", "-i", pot] )
	
#-----------------------------------------------------------------------
# Compile the translation file.
#
subprocess.call( cmd + ["compile", "-d", "locale", "-i", po] )
