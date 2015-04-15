import os
import subprocess
import glob
import errno

pygettext = r"c:\Python27\Tools\i18n\pygettext.py"
if os.path.exists(pygettext):
	cmd = ['python', pygettext]
else:
	cmd = ['pygettext']

try:
	os.makedirs( 'locale' )
except OSError as e:
	if not os.path.isdir('locale'):
		raise

subprocess.call( cmd + ["-v", "-p", "locale", "-o" "CrossMgr.pot"] + glob.glob('*.py') )
