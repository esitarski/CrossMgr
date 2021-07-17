import os
import pwd
import sys
import datetime
import platform
import Version

def get_user():
	try:
		return pwd.getpwuid( os.getuid() )[0]
	except Exception:
		return 'unknown'

def AddExcelInfo( wb ):
	app = Version.AppVerName.split[0]
	uname = platform.uname()
	set_custom_property = wb.set_custom_property
	set_custom_property('{}_AppVersion'.format(app),	Version.AppVerName)
	set_custom_property('{}_Timestamp'.format(app),		datetime.datetime.now() )
	set_custom_property('{}_User.format(app)',			get_user())
	set_custom_property('{}_Python.format(app)',		sys.version.replace('\n', ' '))
	for a in ('system', 'release', 'version', 'machine', 'processor'):
		set_custom_property( '{}_{}'.format(app, a.capitalize()), getattr(uname, a, ''))
