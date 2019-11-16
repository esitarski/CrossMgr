import wx
import datetime
import Utils
import Model
from ChipImport import ChipImportDialog

def parseTagTime( line, lineNo, errors ):
	line = line.strip()
	try:
		i = line.index( 'aa' )
	except ValueError:
		return None, None
	
	line = line[i:]
	if line.endswith( '\\' ):
		line = line[:-1]
	
	if line.endswith( 'LS' ):
		return None, None
	
	try:
		tag			= line[4:16]
		year		= line[20:22]
		month		= line[22:24]
		day			= line[24:26]
		hour		= line[26:28]
		minute		= line[28:30]
		second		= line[30:32]
		hundreths	= line[32:34]
	except IndexError:
		return None, None
	
	try:
		year		= 2000 + int(year)
		month		= int(month)
		day			= int(day)
		hour		= int(hour)
		minute		= int(minute)
		second		= int(second)
		hundreths	= int(hundreths)
	except ValueError:
		return None, None
	
	try:
		t = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=hundreths*10000)
	except Exception as e:
		errors.append( 'line: {}: Error: {}, line='.format( lineNo, e ) )
		return None, None
	
	return tag, t

def IpicoImportDialog( parent, id = wx.ID_ANY ):
	return ChipImportDialog( 'Ipico', parseTagTime, parent, id, fileSuffix = 'rtf' )
		
if __name__ == '__main__':
	errors = []
	for fname in ['Ipico/FS_LS.rtf']:
		with open(fname) as f:
			for i, line in enumerate(f):
				print( parseTagTime( line, i, errors ) )
			print( errors )

	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	dlg = IpicoImportDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

