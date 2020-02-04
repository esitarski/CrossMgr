import wx
import sys
import math
import Utils
import Model
import JChip
from ChipImport import ChipImportDialog
import datetime
combine = datetime.datetime.combine

sepTrans = str.maketrans( '/-:', '   ' )
def timeFromStr( tStr ):
	try:
		tStr = tStr.translate( sepTrans )
		hour, minute, second = tStr.split()[-3:]
		fract, second = math.modf( float(second) )
		microsecond = fract * 1000000.0
		t = combine( JChip.dateToday, datetime.time(hour=int(hour), minute=int(minute), second=int(second), microsecond=int(microsecond)) )
		return t
	except (IndexError, ValueError):
		return None

def parseTagTime( line, lineNo, errors ):
	try:
		tag, tStr = line.split(',')[:2]
	except (IndexError, ValueError):
		errors.append( u'{}: {} {}'.format(_('line'), lineNo, _('unrecognised input')) )
		return None, None
	
	if tag.startswith( 'Tag' ):
		return None, None		# Skip header row.
	
	tStrSave = tStr
	tag = tag.replace( ' ', '' )
	
	tStr = tStr.translate( sepTrans ).strip()
	tFields = tStr.split()
	
	try:
		year, month, day, hour, minute = [int(f) for f in tFields[:-1]]
		fract, second = math.modf( float(tFields[-1]) )
		microsecond = int(fract * 1000000.0)
		second = int(second)
		return tag, datetime.datetime( year, month, day, hour, minute, second, microsecond )
	
	except:
	
		# Get the date (if present).
		tDate = JChip.dateToday
		try:
			yyyy, mm, dd = [int(v) for v in tFields[-3:]]
			if 1900 <= yyyy <= 3000 and 1 <= mm <= 12 and 1 <= dd <= 31:
				tDate = datetime.date( yyyy, mm, dd )
		except (IndexError, ValueError):
			pass
		
		# Get the time.
		try:
			hour, minute, second = tFields[3:6]
			fract, second = math.modf( float(second) )
			microsecond = fract * 1000000.0
			t = combine( tDate, datetime.time(hour=int(hour), minute=int(minute), second=int(second), microsecond=int(microsecond)) )
		except (IndexError, ValueError):
			errors.append( u'{}: {}  {}: "{}"'.format( _('line'), lineNo, _('invalid time'), tStrSave) )
			return None, None
	
	return tag, t

def ImpinjImportDialog( parent, id = wx.ID_ANY ):
	return ChipImportDialog( 'Impinj', parseTagTime, parent, id )
		
if __name__ == '__main__':
	data = '''Tag,Timestamp
AAABBB,	2016-09-11 09:15:34.305
AAADDD,	  2016-10-11 23:15:34.305
'''
	data = '''s
20200201FC000004,Sat Feb 01 14:11:29.139089  2020-02-01
20200201FC000021,Sat Feb 01 14:11:29.516689  2020-02-01
20200201FC000004,Sat Feb 01 14:11:35.530523  2020-02-01
20200201FC000004,Sat Feb 01 14:11:42.412994  2020-02-01
20200201FC000047,Sat Feb 01 14:11:43.256820  2020-02-01
20200201FC000044,Sat Feb 01 14:11:44.576765  2020-02-01
10522C54AFCC0DA3F415C69A,Sat Feb 01 14:11:44.671056  2020-02-01
20200201FC000043,Sat Feb 01 14:11:45.535942  2020-02-01
20200201FC000057,Sat Feb 01 14:11:46.125401  2020-02-01
20200201FC000003,Sat Feb 01 14:11:46.783155  2020-02-01
20200201FC000021,Sat Feb 01 14:11:49.850968  2020-02-01
20200201FC000004,Sat Feb 01 14:11:59.852483  2020-02-01
20200201FC000047,Sat Feb 01 14:12:00.111699  2020-02-01
20200201FC000044,Sat Feb 01 14:12:00.432677  2020-02-01
10522C54AFCC0DA3F415C69A,Sat Feb 01 14:12:00.638752  2020-02-01
20200201FC000043,Sat Feb 01 14:12:01.199199  2020-02-01
20200201FC000057,Sat Feb 01 14:12:01.508610  2020-02-01
20200201FC000003,Sat Feb 01 14:12:02.413108  2020-02-01
20200201FC000004,Sat Feb 01 14:12:11.202626  2020-02-01
20200201FC000047,Sat Feb 01 14:12:11.415818  2020-02-01
20200201FC000044,Sat Feb 01 14:12:11.577448  2020-02-01
10522C54AFCC0DA3F415C69A,Sat Feb 01 14:12:11.782115  2020-02-01'''

	errors = []
	for lineNo, line in enumerate(data.split('\n'), 1):
		print( parseTagTime(line, lineNo, errors) )
	#sys.exit()
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	dlg = ImpinjImportDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

