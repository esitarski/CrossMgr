import wx
import Model
from ChipImport import ChipImportDialog
import string

def parseTagTime( line, lineNo, errors ):
	try:
		fields = line.split(';' if ';' in line else ',')
		msg = fields[0]
		if msg != '$P':
			return None, None
		tag = fields[2]
		tStr = fields[5]
	except IndexError:
		errors.append( 'line %d: unrecognized input' % lineNo )
		return None, None
	
	try:
		secs = int(tStr) / 1000.0	# Convert from 1000's of a second.
	except ValueError:
		errors.append( 'line %d: invalid time' % lineNo )
		return None, None
	else:
		t = datetime.datetime.combine( JChip.dateToday, datetime.time() ) + datetime.timedelta( seconds = secs )
		
	return tag, t
	
def OrionImportDialog( parent, id = wx.ID_ANY ):
	return ChipImportDialog( 'Orion', parseTagTime, parent, id )
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	dlg = OrionImportDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

