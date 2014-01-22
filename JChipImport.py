import wx
import datetime
import Model
import JChip
from ChipImport import ChipImportDialog

def parseTagTime( line, lineNo, errors ):
	try:
		fields = line.split()
		tag = fields[0][1:]
		tStr = fields[1]
	except IndexError:
		errors.append( 'line {}: unrecognized input'.format(lineNo) )
		return None, None
	
	try:
		day = int(fields[2][1:2])
	except:
		day = 0
	
	try:
		t = JChip.parseTime(tStr, day)
	except (IndexError, ValueError):
		errors.append( 'line {}: invalid time: "{}"'.format(lineNo, tStr) )
		return None, None
	
	return tag, t
	
def JChipImportDialog( parent, id = wx.ID_ANY ):
	return ChipImportDialog( 'JChip', parseTagTime, parent, id )

if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	dlg = JChipImportDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

