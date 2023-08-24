import wx
import io
import re
import Model
from ChipImport import ChipImportDialog
import datetime

def parseTagTime( line, lineNo, errors ):
	fields = [f.strip() for f in line.split(',')]
	if not fields:
		return None, None
	if fields[0] == 'Tag':
		return None, None
	
	try:
		tag = fields[0].replace( ' ', '' )
		tStr = re.sub( '[^0-9]', ' ', fields[1] ).strip()
		hh, mm, ss, mss, year, mon, day = tStr.split()[1:]	# Skip the day of the month number.
		mss += '0' * max(0, 6-len(mss))
		t = datetime.datetime( int(year), int(mon), int(day), int(hh), int(mm), int(ss), int(mss) )
		return tag, t
	except Exception:
		errors.append( '{} {}: {}'.format(_('line'), lineNo, _('unrecognised input')) )
		return None, None

def AlienImportDialog( parent, id = wx.ID_ANY ):
	return ChipImportDialog( 'Alien', parseTagTime, parent, id )
		
if __name__ == '__main__':
	errors = []
	with io.open(r"C:\Users\edwar\Downloads\Alien-2017-05-10-18-37-51.txt",'r',encoding='utf-8') as f:
		for lineno, line in enumerate(f,1):
			print( parseTagTime( line, lineno, errors ) )
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	with AlienImportDialog(mainWin) as dlg:
		dlg.ShowModal()

