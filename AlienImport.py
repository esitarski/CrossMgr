import wx
import math
import Utils
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
		year, month, day, hour, minute, second = tStr.split()
		fract, second = math.modf( float(second) )
		microsecond = fract * 1000000.0
		t = combine( JChip.dateToday, datetime.time(hour=int(hour), minute=int(minute), second=int(second), microsecond=int(microsecond)) )
		return t
	except (IndexError, ValueError):
		return None

def parseTagTime( line, lineNo, errors ):
	if 'Tag:' in line:
		tag, tStr = None, None
		for f in line.split(','):
			key, data = [kv.strip() for kv in f.split(':', 1)]
			if key == 'Tag':
				tag = data
			elif key == 'Disc':
				tStr = data
			if tag and tStr:
				break
			
		if not tag or not tStr:
			errors.append( _('line {}: unrecognized input').format(lineNo) )
			return None, None
			
		tag = tag.replace( ' ', '' )
		t = timeFromStr( tStr )
		return tag, t

	try:
		tag, tStr, antenna, readCount = line.split(',')
	except (IndexError, ValueError):
		errors.append( _('line {}: unrecognized input').format(lineNo) )
		return None, None
	
	if tag.startswith( 'Tag' ):
		return None, None		# Skip header row.
		
	tStrSave = tStr
	tag = tag.replace( ' ', '' )
	
	tFields = tStr.split()
	
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
		errors.append( _('line {}: invalid time: "{}"').format(lineNo, tStrSave) )
		return None, None
	
	return tag, t

def AlienImportDialog( parent, id = wx.ID_ANY ):
	return ChipImportDialog( 'Alien', parseTagTime, parent, id )
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	dlg = AlienImportDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

