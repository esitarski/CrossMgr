import wx
import math
import Model
import JChip
from ChipImport import ChipImportDialog
import datetime
combine = datetime.datetime.combine
import string

sepTrans = string.maketrans( '/-:', '   ' )
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
		errors.append( 'line %d: unrecognized input' % lineNo )
		return None, None
	
	if tag.startswith( 'Tag' ):
		return None, None		# Skip header row.
	
	tStrSave = tStr
	tag = tag.replace( ' ', '' )
	
	try:
		tStr = tStr.translate( sepTrans )
		weekDay, shortMonth, day, hour, minute, second = tStr.split()[:6]
		fract, second = math.modf( float(second) )
		microsecond = fract * 1000000.0
		t = combine( JChip.dateToday, datetime.time(hour=int(hour), minute=int(minute), second=int(second), microsecond=int(microsecond)) )
	except (IndexError, ValueError):
		errors.append( 'line %d: invalid time: "%s"' % (lineNo, tStrSave) )
		return None, None
		
	return tag, t

def ImpinjImportDialog( parent, id = wx.ID_ANY ):
	return ChipImportDialog( 'Impinj', parseTagTime, parent, id )
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	dlg = ImpinjImportDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

