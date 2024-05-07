import wx
import datetime
import Model
from ChipImport import ChipImportDialog

'''

#;ID;Date     ;Time        ;Extra Stuff
1;33;0000-00-00;00:00:02.773;6692;12;-68;09ca52

0 1  2          3            4    5   6
'''
def parseTagTime( line, lineNo, errors ):
	try:
		fields = line.split(';')
		tag = fields[1].strip().lstrip('0')		# ID
		dStr = fields[2]						# Date
		tStr = fields[3]						# Time
	except IndexError:
		errors.append( '{} {}: {}'.format(_('line'), lineNo, _('unrecognised input')) )
		return None, None

	secs = 0.0
	try:
		for f in tStr.split(':'):
			secs = secs * 60.0 + float(f.strip())
	except Exception as e:
		errors.append( '{} {}: {}: {}'.format( _('line'), lineNo, _('invalid time'), e) )
		return None, None

	try:
		year, month, day = [int(f.strip()) for f in dStr.split('-')]
		d = datetime.date( year, month, day )
	except Exception as e:
		errors.append( '{} {}: {}: {}'.format( _('line'), lineNo, _('invalid date'), e) )
		return None, None
		
	t = datetime.datetime.combine( d, datetime.time() ) + datetime.timedelta( seconds = secs )
		
	return tag, t
	
def RaceResultImportDialog( parent, id = wx.ID_ANY ):
	return ChipImportDialog( 'RaceResult', parseTagTime, parent, id )
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	with RaceResultImportDialog( mainWin ) as dlg:
		dlg.ShowModal()

