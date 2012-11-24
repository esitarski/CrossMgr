import wx
import Model
import JChip
from ChipImport import ChipImportDialog
import calendar
import string

sepTrans = string.maketrans( '/-:', '   ' )
def parseTagTime( line, lineNo, errors ):
	try:
		tag, tStr, antenna, readCount = line.split(',')
	except IndexError:
		errors.append( 'line %d: unrecognized input' % lineNo )
		return None, None
	
	if tag.startswith( 'Tag' ):
		return None, None		# Skip header row.
		
	tag = tag.replace( ' ', '' )
	
	try:
		tStr = tStr.translate( sepTrans )
		weekDay, shortMonth, day, hour, minute, second, tzone, year = tStr.split()
		
		# We only want the time.
		fract, second = math.fmod( second )
		microsecond = fract * 1000000.0
		t = combine( JChip.dateToday, datetime.time(minute=int(minute), second=int(second), microsecond=int(microsecond)) )
	except (IndexError, ValueError):
		errors.append( 'line %d: invalid time' % lineNo )
		return None, None
		
	return tag, t

def AlienImportDialog( parent, id = wx.ID_ANY ):
	return ChipImportDialog( 'Alien', parseTagTime, parent, id )
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	dlg = AlienImportDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

