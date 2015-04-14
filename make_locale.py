import os
import subprocess
import glob

pygettext = "c:\Python27\Tools\i18n\pygettext.py"
if not os.path.exists(pygettext):
	pygettext = "\lib\python27\Tools\i18n\pygettext.py"
	
subprocess.call( ["python", pygettext, "-v", "-p", "locale", "-o" "CrossMgr.pot"] + glob.glob('*.py') )