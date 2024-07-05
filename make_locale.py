import os
import glob
import shutil
import subprocess

cmd = ['pybabel']

CrossMgrLocale = 'CrossMgrLocale'

languages = ('fr', 'es', 'it')
for lang in languages:
	dir = os.path.join(CrossMgrLocale,lang,'LC_MESSAGES')
	try:
		os.makedirs( dir )
	except OSError:
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
subprocess.run( cmd + ["extract", "-o", pot, dir] )

shutil.rmtree( dir )

with open(pot, 'r', encoding='utf8') as f:
	contents = f.read()
contents = contents.replace( 'locale_src/', '' )
with open(pot, 'w', encoding='utf8') as f:
	f.write( contents )

for lang in languages:
	#-----------------------------------------------------------------------
	# Create/Merge translation file.
	#
	po = os.path.join(CrossMgrLocale, lang, 'LC_MESSAGES', 'messages.po')

	if os.path.exists( po ):
		subprocess.run( cmd + ["update", "-d", CrossMgrLocale, "-i", pot] )
	else:
		subprocess.run( cmd + ["init", "-d", CrossMgrLocale, "-l", lang, "-i", pot] )
		
	#-----------------------------------------------------------------------
	# Compile the translation file.
	#
	subprocess.run( cmd + ["compile", "-f", "-d", CrossMgrLocale, "-l", lang, "-i", po] )
