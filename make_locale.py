import os
import subprocess
import errno
import glob
import shutil
import io

cmd = ['pybabel']

CrossMgrLocale = 'CrossMgrLocale'

languages = ('fr', 'es', 'it')
for lang in languages:
	dir = os.path.join(CrossMgrLocale,lang,'LC_MESSAGES')
	try:
		os.makedirs( dir )
	except OSError as e:
		if not os.path.isdir( dir ):
			raise

#-----------------------------------------------------------------------
# Extract the strings.
#
dir = 'locale_src'
try:
	shutil.rmtree( dir )
except Exception:
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

for lang in languages:
	#-----------------------------------------------------------------------
	# Create/Merge translation file.
	#
	po = os.path.join(CrossMgrLocale, lang, 'LC_MESSAGES', 'messages.po')

	if os.path.exists( po ):
		subprocess.call( cmd + ["update", "-d", CrossMgrLocale, "-i", pot] )
	else:
		subprocess.call( cmd + ["init", "-d", CrossMgrLocale, "-l", lang, "-i", pot] )
		
	#-----------------------------------------------------------------------
	# Compile the translation file.
	#
	subprocess.call( cmd + ["compile", "-f", "-d", CrossMgrLocale, "-l", lang, "-i", po] )
