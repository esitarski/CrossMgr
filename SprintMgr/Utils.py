#-----------------------------------------------------------------------
# Set translation locale.
#
import wx
import wx.lib.agw.genericmessagedialog
locale = wx.Locale()

from Version import AppVerName
import gettext
initTranslationCalled = False
def initTranslation():
	global initTranslationCalled
	if not initTranslationCalled:
		try:
			gettext.install(AppVerName.split()[0], './locale', unicode=True)
		except Exception:
			gettext.install(AppVerName.split()[0], './locale')
		initTranslationCalled = True
		
initTranslation()

FontFace = 'Arial'

try:
	from win32com.shell import shell, shellcon
except ImportError:
	pass
	
import os
import re
import sys
import math
import wx.grid		as gridlib
import unicodedata
import traceback
import platform
import datetime
import string

def removeDiacritic( s ):
	'''
	Accept a unicode string, and return a normal string
	without any diacritical marks.
	'''
	try:
		return unicodedata.normalize('NFKD', '{}'.format(s)).encode('ASCII', 'ignore').decode()
	except Exception:
		return s
	
invalidFilenameChars = re.compile( "[^-_.() " + string.ascii_letters + string.digits + "]" )
def RemoveDisallowedFilenameChars( filename ):
	cleanedFilename = unicodedata.normalize('NFKD', str(filename).strip()).encode('ASCII', 'ignore').decode()
	cleanedFilename = cleanedFilename.replace( '/', '_' ).replace( '\\', '_' )
	return invalidFilenameChars.sub( '', cleanedFilename )

def RemoveDisallowedSheetChars( sheetName ):
	sheetName = unicodedata.normalize('NFKD', str(sheetName)).encode('ASCII', 'ignore').decode()
	return re.sub('[+!#$%&+~`".:;|\\\\/?*\[\] ]+', ' ', sheetName)[:31]		# four backslashes required to match one backslash in re.
	
def ordinal( value ):
	try:
		value = int(value)
	except ValueError:
		return value

	if (value % 100)//10 != 1:
		return "{}{}".format(value, ['th','st','nd','rd','th','th','th','th','th','th'][value%10])
	return "{}{}".format(value, "th")
	
reSpace = re.compile(r'\s')
def approximateMatch( s1, s2 ):
	s1 = reSpace.sub( '', s1 ).lower()
	s2 = reSpace.sub( '', s2 ).lower()
	if s1 == 'lastname' and s2 == 'name':
		return 99.0
	if s1 == 'teamcode' and s2 == 'team':
		return 0.0
	if s1[-1].isdigit():
		return 1.2 if s1 == s2 else 0.0
	if s1.startswith(s2) or s2.startswith(s1):
		return 1.1
	return len(set(s1) & set(s2)) / float(len(s1) + len(s2))

GoodHighlightColour = wx.Colour( 0, 255, 0 )
BadHighlightColour = wx.Colour( 255, 255, 0 )
LightGrey = wx.Colour( 238, 238, 238 )
	
'''
wx.ICON_EXCLAMATION	Shows an exclamation mark icon.
wx.ICON_HAND	Shows an error icon.
wx.ICON_ERROR	Shows an error icon - the same as wxICON_HAND.
wx.ICON_QUESTION	Shows a question mark icon.
wx.ICON_INFORMATION	Shows an information (i) icon.
'''

def MessageOK( parent, message, title = '', iconMask = wx.ICON_INFORMATION, pos = wx.DefaultPosition ):
	dlg = wx.MessageDialog(parent, message, title, wx.OK | iconMask, pos)
	dlg.ShowModal()
	dlg.Destroy()
	return True
	
def MessageYesNo( parent, message, title = '', iconMask = wx.ICON_QUESTION):
	dlg = wx.MessageDialog(parent, message, title, wx.YES|wx.NO|iconMask )
	response = dlg.ShowModal()
	dlg.Destroy()
	return response == wx.ID_YES
	
def MessageOKCancel( parent, message, title = '', iconMask = wx.ICON_QUESTION ):
	dlg = wx.MessageDialog(parent, message, title, wx.OK | wx.CANCEL | iconMask )
	response = dlg.ShowModal()
	dlg.Destroy()
	return response == wx.ID_OK
	
def MessageYesNoCancel( parent, message, title = '', iconMask = wx.ICON_QUESTION ):
	dlg = wx.MessageDialog(parent, message, title, wx.YES_NO | wx.CANCEL | iconMask )
	response = dlg.ShowModal()
	dlg.Destroy()
	return response

class WriteCell:
	def __init__( self, grid, row, col = 0 ):
		self.grid = grid
		self.row = row
		self.col = col
	def __call__( self, value, horiz=None, vert=None ):
		self.grid.SetCellValue( self.row, self.col, value )
		if horiz is not None or vert is not None:
			self.grid.SetCellAlignment( self.row, self.col, horiz or wx.ALIGN_LEFT, vert or wx.ALIGN_TOP )
		self.col += 1
		
def SetValue( st, value ):
	if st.GetValue() != value:
		st.SetValue( value )

def SetLabel( st, label ):
	if st.GetLabel() != label:
		st.SetLabel( label )

def MakeGridReadOnly( grid ):
	attr = gridlib.GridCellAttr()
	attr.SetReadOnly()
	for c in range(grid.GetNumberCols()):
		grid.SetColAttr( c, attr )

def SetRowBackgroundColour( grid, row, colour ):
	for c in range(grid.GetNumberCols()):
		grid.SetCellBackgroundColour( row, c, colour )
		
def DeleteAllGridRows( grid ):
	if grid.GetNumberRows() > 0:
		grid.DeleteRows( 0, grid.GetNumberRows(), True )
		
def SwapGridRows( grid, r, rTarget ):
	if r != rTarget and 0 <= r < grid.GetNumberRows() and 0 <= rTarget < grid.GetNumberRows():
		for c in range(grid.GetNumberCols()):
			vSave = grid.GetCellValue( rTarget, c )
			grid.SetCellValue( rTarget, c, grid.GetCellValue(r,c) )
			grid.SetCellValue( r, c, vSave )
		
def AdjustGridSize( grid, rowsRequired = None, colsRequired = None ):
	# print 'AdjustGridSize: rowsRequired=', rowsRequired, ' colsRequired=', colsRequired

	if rowsRequired is not None:
		rowsRequired = int(rowsRequired)
		d = grid.GetNumberRows() - rowsRequired
		if d > 0:
			grid.DeleteRows( rowsRequired, d )
		elif d < 0:
			grid.AppendRows( -d )

	if colsRequired is not None:
		colsRequired = int(colsRequired)
		d = grid.GetNumberCols() - colsRequired
		if d > 0:
			grid.DeleteCols( colsRequired, d )
		elif d < 0:
			grid.AppendCols( -d )
			
def SetGridCellBackgroundColour( grid, colour=wx.WHITE ):
	for r in range(grid.GetNumberRows()):
		for c in range(grid.GetNumberCols()):
			grid.SetCellBackgroundColour( r, c, colour )

def ChangeFontInChildren(win, font):
	'''
	Set font in given window and all its descendants.
	@type win: L{wx.Window}
	@type font: L{wx.Font}
	'''
	try:
		win.SetFont( font )
	except Exception:
		pass # don't require all objects to support SetFont
	
	try:
		for child in win.GetChildren():
			ChangeFontInChildren( child, font )
	except Exception:
		pass
		
def formatTime( secs,
				highPrecision=False,	extraPrecision=False,
				forceHours=False, 		twoDigitHours=False,
				forceMinutes=True,		twoDigitMinutes=True,
				twoDigitSeconds=False ):
	if secs is None:
		secs = 0
	if secs < 0:
		sign = '-'
		secs = -secs
	else:
		sign = ''
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = int(secs // (60*60))
	minutes = int( (secs // 60) % 60 )
	secs = (secs % 60) + f
	if highPrecision or extraPrecision:
		if extraPrecision:
			secStr = '{:06.3f}'.format( secs )
		else:
			secStr = '{:05.2f}'.format( secs )
	else:
		secStr = '{:02.0f}'.format( secs )
	if secStr.startswith('60'):
		secStr = '00' + secStr[2:]
		minutes += 1
		if minutes == 60:
			minutes = 0
			hours += 1
	if forceHours or hours > 0:
		return '{}{:0{hourWidth}d}:{:02d}:{}'.format(sign, hours, minutes, secStr, hourWidth=2 if twoDigitHours else 0)
	else:
		if forceMinutes or minutes > 0:
			return '{}{:0{minuteWidth}d}:{}'.format(sign, minutes, secStr, minuteWidth=2 if twoDigitMinutes else 0)
		else:
			return '{}{}'.format(
				sign,
				secStr if twoDigitSeconds else (secStr.lstrip('0') if not secStr.startswith('00') else secStr[1:])
			)

def formatDate( date ):
	y, m, d = date.split('-')
	d = datetime.date( int(y,10), int(m,10), int(d,10) )
	return d.strftime('%B %d, %Y')

def StrToSeconds( s = '' ):
	secs = 0.0
	for f in s.strip().split(':'):
		if f:
			secs = secs * 60.0 + float(f)
		else:
			secs *= 60.0
	return secs
	
def SecondsToStr( secs, full = False ):
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = int(secs // (60*60))
	if hours > 99:
		hours = 99
	minutes = int( (secs // 60) % 60 )
	secs = secs % 60 + f
	if full:
		return "{:02d}:{:02d}:{:06.3f}".format(hours, minutes, secs)
	if hours != 0:
		return "{}:{:02d}:{:06.3f}".format(hours, minutes, secs)
	if minutes != 0:
		return "{}:{:06.3f}".format(minutes, secs)
	return "{:.3f}".format(secs)

def SecondsToMMSS( secs = 0 ):
	secs = int(secs+0.5)
	return '{:02d}:{:02d}'.format((secs // 60)%60, secs % 60)
	
def getHomeDir():
	try:
		homedir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
		homedir = os.path.join( homedir, 'SprintMgr' )
		if not os.path.exists(homedir):
			os.mkdir( homedir )
	except Exception:
		homedir = os.path.expanduser('~')
	return homedir

#------------------------------------------------------------------------
if 'MAC' in wx.Platform:
	# Make message not have the standard python icon on Mac.
	wx.MessageDialog = wx.lib.agw.genericmessagedialog.GenericMessageDialog

# Add access functions for all resource folders.
from GetFolder import GetFolders
globals().update( {'get' + folder[0].upper() + folder[1:]:lambda v=location: v for folder, location in GetFolders().items()} )
def getImageFile( fname, folder=getImageFolder() ):
	return os.path.join( folder, fname )

def AlignHorizontalScroll( gFrom, gTo ): 
	xFrom, yFrom = gFrom.GetViewStart()
	xTo,   yTo   = gTo.GetViewStart()
	gTo.Scroll( xFrom, yTo )

#------------------------------------------------------------------------

PlatformName = platform.system()
def writeLog( message ):
	try:
		dt = datetime.datetime.now()
		dt = dt.replace( microsecond = 0 )
		msg = '{} ({}) {}{}'.format(
			dt.isoformat(),
			PlatformName,
			message,
			'\n' if not message or message[-1] != '\n' else ''
		)
		sys.stdout.write( removeDiacritic(msg) )
		sys.stdout.flush()
	except IOError:
		pass
		
def disable_stdout_buffering():
	''' No longer necessary as all output to a tty will be flushed after newline. '''
	return None
		
def logCall( f ):
	def _getstr( x ):
		return '{}'.format(x) if not isinstance(x, wx.Object) else '<<{}>>'.format(x.__class__.__name__)
	
	def new_f( *args, **kwargs ):
		parameters = [_getstr(a) for a in args] + [ '{}={}'.format( key, _getstr(value) ) for key, value in kwargs.items() ]
		writeLog( 'call: {}({})'.format(f.__name__, removeDiacritic(', '.join(parameters))) )
		return f( *args, **kwargs)
	return new_f
	
def logException( e, exc_info ):
	eType, eValue, eTraceback = exc_info
	ex = traceback.format_exception( eType, eValue, eTraceback )
	writeLog( '**** Begin Exception ****' )
	for d in ex:
		for line in d.split( '\n' ):
			writeLog( line )
	writeLog( '**** End Exception ****' )
	
#------------------------------------------------------------------------

mainWin = None
def setMainWin( mw ):
	global mainWin
	mainWin = mw
	
def getMainWin():
	return mainWin

def refresh():
	if mainWin is not None:
		mainWin.refresh()

def writeRace():
	if mainWin is not None:
		mainWin.writeRace()
		
def setTitle():
	if mainWin:
		mainWin.setTitle()
	
def isMainWin():
	return mainWin is not None
	
if __name__ == '__main__':
	hd = getHomeDir()
	open( os.path.join(hd, 'Test.txt'), 'w' )
