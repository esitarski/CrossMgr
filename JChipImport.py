import wx
import Model
import JChip
from ChipImport import ChipImportDialog

def parseTagTime( line, lineNo, errors ):
	try:
		fields = line.split()
		tag = fields[0][1:]
		tStr = fields[1]
	except IndexError:
		errors.append( 'line %d: unrecognized input' % lineNo )
		return None, None
	
	try:
		t = JChip.parseTime(tStr)
	except (IndexError, ValueError):
		errors.append( 'line %d: invalid time: "%s"' % (lineNo, tStr) )
		return None, None
		
	return tag, t
	
def JChipImportDialog( parent, id = wx.ID_ANY ):
	return ChipImportDialog( 'JChip', parseTagTime, parent, id )

if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	dlg = JChipImportDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

