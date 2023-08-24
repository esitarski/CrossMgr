import os
import sys
import datetime
import platform
import Version
from getuser import lookup_username

def getInfo():
	app = Version.AppVerName.split()[0]
	uname = platform.uname()
	try:
		user = lookup_username()
	except Exception:
		user = ''
	info = {
		'{}_AppVersion'.format(app):	Version.AppVerName,
		'{}_Timestamp'.format(app):		datetime.datetime.now(),
		'{}_User'.format(app):			os.path.basename(user),
		'{}_Python'.format(app):		sys.version.replace('\n', ' '),
	}
	info.update( {'{}_{}'.format(app, a.capitalize()): getattr(uname, a)
		for a in ('system', 'release', 'version', 'machine', 'processor') if getattr(uname, a, '') } )
	return info

def AddExcelInfo( wb ):
	for k,v in getInfo().items():
		wb.set_custom_property( k, v )

if __name__ == '__main__':
	for k, v in getInfo().items():
		print( k, v )
