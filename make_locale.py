import os
import subprocess
import glob
import errno

pygettext = "c:\Python27\Tools\i18n\pygettext.py"
if not os.path.exists(pygettext):
	pygettext = "\lib\python27\Tools\i18n\pygettext.py"

try:
	os.makedirs( 'locale' )
except OSError as e:
	if not os.path.isdir('locale'):
		raise

subprocess.call( ["python", pygettext, "-v", "-p", "locale", "-o" "CrossMgr.pot"] + glob.glob('*.py') )