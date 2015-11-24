import sys
import collections

#-----------------------------------------------------------------------
# Fix named tuple pickle issue.
#
def _fix_issue_18015(collections):
	try:
		template = collections._class_template
	except AttributeError:
		# prior to 2.7.4 _class_template didn't exists
		return
	if not isinstance(template, basestring):
		return  # strange
	if "__dict__" in template or "__getstate__" in template:
		return  # already patched
	lines = template.splitlines()
	indent = -1
	for i,l in enumerate(lines):
		if indent < 0:
			indent = l.find('def _asdict')
			continue
		if l.startswith(' '*indent + 'def '):
			lines.insert(i, ' '*indent + 'def __getstate__(self): pass')
			lines.insert(i, ' '*indent + '__dict__ = _property(_asdict)')
			break
	collections._class_template = '''\n'''.join(lines)
    
if sys.version_info[:3] == (2,7,5):
	_fix_issue_18015(collections)

#-----------------------------------------------------------------------
# Attempt to import windows libraries.
#
try:
	from win32com.shell import shell, shellcon
except ImportError:
	pass
	
try:
	import win32api,win32process,win32con
except:
	pass

try:
	sys.getwindowsversion()
	isWindows = True
except:
	isWindows = False

#------------------------------------------------------------------------
# Get resource directories.
#
import wx
import os

if 'WXMAC' in wx.Platform:
	try:
		dirName = os.environ['RESOURCEPATH']
	except:
		dirName = os.path.dirname(os.path.abspath(__file__))
	if not os.path.isdir( os.path.join(dirName, 'CrossMgrImages') ):
		dirName = '/System/Library/Frameworks/Python.framework/Versions/2.7'
else:
	try:
		dirName = os.path.dirname(os.path.abspath(__file__))
	except:
		dirName = os.path.dirname(os.path.abspath(sys.argv[0]))
	
	if os.path.basename(dirName) in ['library.zip', 'MainWin.exe', 'CrossMgr.exe']:
		dirName = os.path.dirname(dirName)
	if 'CrossMgr?' in os.path.basename(dirName):
		dirName = os.path.dirname(dirName)
	if not os.path.isdir( os.path.join(dirName, 'CrossMgrImages') ):
		dirName = os.path.dirname(dirName)

	if os.path.isdir( os.path.join(dirName, 'CrossMgrImages') ):
		pass
	elif os.path.isdir( '/usr/local/CrossMgrImages' ):
		dirName = '/usr/local'

imageFolder = os.path.join(dirName, 'CrossMgrImages')
htmlFolder = os.path.join(dirName, 'CrossMgrHtml')
helpFolder = os.path.join(dirName, 'CrossMgrHtmlDoc')
helpIndexFolder = os.path.join(dirName, 'CrossMgrHelpIndex')

def getDirName():		return dirName
def getImageFolder():	return imageFolder
def getHtmlFolder():	return htmlFolder
def getHelpFolder():	return helpFolder
def getHelpIndexFolder(): return helpIndexFolder

#-----------------------------------------------------------------------
# Get the user's default language.
#
import locale
lang = 'en'
try:
	import ctypes
	windll = ctypes.windll.kernel32
	lang = locale.windows_locale[ windll.GetUserDefaultUILanguage() ]
except:
	lang = locale.getdefaultlocale()[0]

try:
	lang = os.environ['CrossMgrLanguage']
except:
	pass

#-----------------------------------------------------------------------
# Setup translation.
#
import sys
from Version import AppVerName
import gettext
import __builtin__
initTranslationCalled = False
def initTranslation():
	global lang
	global initTranslationCalled
	
	if not initTranslationCalled or (lang and not lang.startswith('en')):
		initTranslationCalled = True
		
		gettext.install('messages', os.path.join(dirName,'CrossMgrLocale'), unicode=1)
		
		# Try to use a translation matching the user's language.
		try:
			translation = gettext.translation('messages', os.path.join(dirName,'CrossMgrLocale'), languages=[lang[:2]])
			translation.install()
			__builtin__.__dict__['_'] = translation.ugettext
		except:
			pass
		
		extra_fields = {
			_('Search'),
			_('Finisher'), _('DNF'), _('PUL'), _('DNS'), _('DQ'), _('OTL'), _('NP'),
		}
		
initTranslation()

class SuspendTranslation( object ):
	''' Temporarily suspend translation. '''
	def __enter__(self):
		self._Save = __builtin__.__dict__['_']
		__builtin__.__dict__['_'] = lambda x: x
	def __exit__(self, type, value, traceback):
		__builtin__.__dict__['_'] = self._Save

class UIBusy( object ):
	def __enter__(self):
		wx.BeginBusyCursor()
	
	def __exit__( self, type, value, traceback ):
		wx.EndBusyCursor()
		return False

#-----------------------------------------------------------------------
# Monkey-patch font function so we always fetch a nicer font face.
#
if 'WXMAC' not in wx.Platform:
	FontFace = 'Arial'
	FontFromPixelSize = wx.FontFromPixelSize
	def FontFromPixelSizeFontFace( *args, **kwargs ):
		if 'face' not in kwargs:
			kwargs['face'] = FontFace
		return FontFromPixelSize( *args, **kwargs )
	wx.FontFromPixelSize = FontFromPixelSizeFontFace

	Font = wx.Font
	def FontFontFace( *args, **kwargs ):
		if 'face' not in kwargs:
			kwargs['face'] = FontFace
		try:
			return Font( *args, **kwargs )
		except:
			pass
		del kwargs['face']
		return Font( *args, **kwargs )
	wx.Font = FontFontFace

#---------------------------------------------------------------------------
from contextlib import contextmanager

@contextmanager
def tag( buf, name, attrs = None ):
	if not attrs:
		attrs = {}
	if not isinstance(attrs, dict):
		attrs = { 'class': attrs }
	if attrs:
		buf.write( u'<{} {}>'.format(name, u' '.join(['{}="{}"'.format(attr, value) for attr, value in attrs.iteritems()])) )
	else:
		buf.write( u'<{}>'.format(name) )
	yield
	buf.write( '</{}>\n'.format(name) )

#-----------------------------------------------------------------------
# Now, get all the required modules required for the common functions.
#
import datetime
import re
import math
import string
import subprocess
import platform
import unicodedata
import webbrowser
import traceback
import socket
import wx.grid		as gridlib

import wx.lib.agw.genericmessagedialog
if 'WXMAC' in wx.Platform:
	# wx.DC.GetMultiLineTextExtent does not work on the Mac.
	# Replace it with our own function.
	def GetMultiLineTextExtent( dc, text, font = None ):
		textWidth, textHeight, lineHeight = 0, 0, None
		for line in text.split('\n'):
			lineWidth, lineHeight = dc.GetFullTextExtent( line, font )[:2]
			textWidth = max( textWidth, lineWidth )
			textHeight += lineHeight
		if lineHeight is None:
			lineHeight = dc.GetFullTextExtent( '000Yy', font )[1]
		return textWidth, textHeight, lineHeight
	
	wx.DC.GetMultiLineTextExtent = GetMultiLineTextExtent

	# Error, Information and Question dialogs have no icons on the Mac.
	# Replace all message dialogs with generics dialogs.
	wx.MessageDialog = wx.lib.agw.genericmessagedialog.GenericMessageDialog

# Fix up numeric keypad keys.
if 'WXMAC' in wx.Platform:
	wx.WXK_NUMPAD_ENTER = 13
	wx.WXK_NUMPAD_MULTIPLY = 42
	wx.WXK_NUMPAD_DIVIDE = 47
	wx.WXK_NUMPAD_EQUAL = 61
	wx.WXK_NUMPAD_ADD = 43
	wx.WXK_NUMPAD_SUBTRACT = 45
	
def HighPriority():
	""" Set the priority of the process to the highest level."""
	if isWindows:
		# Based on:
		#   "Recipe 496767: Set Process Priority In Windows" on ActiveState
		#   http://code.activestate.com/recipes/496767/
		pid = win32api.GetCurrentProcessId()
		handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
		win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS)
	else:
		os.nice( -os.nice(0) )

def stripLeadingZeros( s ):
	return s.lstrip('0')
	
def plat_ind_basename( s ):
	try:
		return s[s.rindex('/')+1:]
	except:
		try:
			return s[s.rindex('\\')+1:]
		except:
			return s
	
def toAscii( s ):
	if s is None or s == '':
		return ''
	ret = unicodedata.normalize('NFKD', s).encode('ascii','ignore') if type(s) == unicode else str(s)
	if ret.endswith( '.0' ):
		ret = ret[:-2]
	return ret

validFilenameChars = set( c for c in ("-_.() %s%s" % (string.ascii_letters, string.digits)) )
def RemoveDisallowedFilenameChars( filename ):
	cleanedFilename = unicodedata.normalize('NFKD', unicode(filename)).encode('ASCII', 'ignore')
	cleanedFilename = cleanedFilename.replace( '/', '_' )
	return ''.join(c for c in cleanedFilename if c in validFilenameChars)

def removeDiacritic(input):
	'''
	Accept a unicode string, and return a normal string (bytes in Python 3)
	without any diacritical marks.
	'''
	if type(input) == str:
		return input
	else:
		return unicodedata.normalize('NFKD', input).encode('ASCII', 'ignore')
	
soundCache = {}
def Play( soundFile ):
	global soundCache
	soundFile = os.path.join( getImageFolder(), soundFile )
	
	if sys.platform.startswith('linux'):
		try:
			subprocess.Popen(['aplay', '-q', soundFile])
		except:
			pass
		return True
		
	try:
		return soundCache[soundFile].Play()
	except:
		soundCache[soundFile] = wx.Sound( soundFile )
		return soundCache[soundFile].Play()
		
def PlaySound( soundFile ):
	if mainWin and not mainWin.playSounds:
		return True
	return Play( soundFile )

def GetSelectedRows( grid ):
	rows = []
	for row in xrange(grid.GetNumberRows()):
		if any(grid.IsInSelection(row, col) for col in xrange(grid.GetNumberCols())):
			rows.append( row )
	return rows

def GetListCtrlSelectedItems( listCtrl ):
	selection = []
	index = listCtrl.GetFirstSelected()
	while index >= 0:
		selection.append( index )
		index = listCtrl.GetNextSelected(index)
	return selection

'''
wx.ICON_EXCLAMATION	Shows an exclamation mark icon.
wx.ICON_HAND	Shows an error icon.
wx.ICON_ERROR	Shows an error icon - the same as wxICON_HAND.
wx.ICON_QUESTION	Shows a question mark icon.
wx.ICON_INFORMATION	Shows an information (i) icon.
'''

def MessageOK( parent, message, title = u'', iconMask = wx.ICON_INFORMATION, pos = wx.DefaultPosition ):
	dlg = wx.MessageDialog(parent, message, title, wx.OK|iconMask, pos=pos)
	dlg.ShowModal()
	dlg.Destroy()
	return True
	
def MessageOKCancel( parent, message, title = u'', iconMask = wx.ICON_QUESTION):
	dlg = wx.MessageDialog(parent, message, title, wx.OK|wx.CANCEL|iconMask )
	response = dlg.ShowModal()
	dlg.Destroy()
	return response == wx.ID_OK
	
def MessageYesNo( parent, message, title = u'', iconMask = wx.ICON_QUESTION):
	dlg = wx.MessageDialog(parent, message, title, wx.YES|wx.NO|iconMask )
	response = dlg.ShowModal()
	dlg.Destroy()
	return response == wx.ID_YES
	
def MessageYesNoCancel( parent, message, title = u'', iconMask = wx.ICON_QUESTION):
	dlg = wx.MessageDialog(parent, message, title, wx.YES|wx.NO|wx.CANCEL|iconMask )
	response = dlg.ShowModal()
	dlg.Destroy()
	return response
	
def SetValue( st, value ):
	if st.GetValue() != value:
		st.SetValue( value )
		return True
	return False

def SetLabel( st, label ):
	if st.GetLabel() != label:
		st.SetLabel( label )
		return True
	return False

def MakeGridReadOnly( grid ):
	for c in xrange(grid.GetNumberCols()):
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly()
		grid.SetColAttr( c, attr )

def SwapGridRows( grid, r, rTarget ):
	if r != rTarget and 0 <= r < grid.GetNumberRows() and 0 <= rTarget < grid.GetNumberRows():
		for c in xrange(grid.GetNumberCols()):
			vSave = grid.GetCellValue( rTarget, c )
			grid.SetCellValue( rTarget, c, grid.GetCellValue(r,c) )
			grid.SetCellValue( r, c, vSave )
		
def AdjustGridSize( grid, rowsRequired = None, colsRequired = None ):
	# print( 'AdjustGridSize: rowsRequired=', rowsRequired, ' colsRequired=', colsRequired )

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

def colorFromStr( s ):
	assert s[:1] == '#', 'Invalid colour string'
	s = s.lstrip('#')
	assert len(s) in (3, 6), 'Invalid colour string'
	if len(s) == 3:
		r, g, b = [int(c, 16) for c in s]
	else:
		r, g, b = [int(s[i:i+2], 16) for i in xrange(0, 6, 2)]
	return wx.Colour(r, g, b)

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
		return "{}{:0{hourWidth}d}:{:02d}:{}".format(sign, hours, minutes, secStr, hourWidth=2 if twoDigitHours else 0)
	else:
		if forceMinutes or minutes > 0:
			return "{}{:0{minuteWidth}d}:{}".format(sign, minutes, secStr, minuteWidth=2 if twoDigitMinutes else 0)
		else:
			return "{}{}".format(
				sign,
				secStr if twoDigitSeconds else (secStr.lstrip('0') if not secStr.startswith('00') else secStr[1:])
			)

def formatTimeGap( secs, highPrecision=False, separateWithQuotes=True, forceHours=False ):
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
	if highPrecision:
		secStr = '{:05.2f}'.format( secs )
	else:
		secStr = '{:02d}'.format( int(secs) )	# Truncate fractional seconds.
	if secStr == '60' or secStr == '60.00':
		secStr = '00.00' if highPrecision else '00'
		minutes += 1
		if minutes == 60:
			minutes = 0
			hours += 1
	
	if separateWithQuotes:
		if forceHours or hours > 0:
			return "{}{}h{}'{}\"".format(sign, hours, minutes, secStr)
		else:
			return "{}{}'{}\"".format(sign, minutes, secStr)
	else:
		if forceHours or hours > 0:
			return "{}{}:{:02d}:{}".format(sign, hours, minutes, secStr)
		else:
			return "{}{:02d}:{}".format(sign, minutes, secStr)

def formatTimeCompressed( secs, highPrecision = False ):
	f = formatTime( secs, highPrecision )
	if f[0] == '0':
		return f[1:]
	return f
		
def formatDate( date ):
	y, m, d = date.split('-')
	d = datetime.date( int(y,10), int(m,10), int(d,10) )
	return d.strftime( '%B %d, %Y' )
		
def StrToSeconds( str = '' ):
	secs = 0.0
	for f in str.split(':'):
		try:
			n = float(f)
		except ValueError:
			n = 0.0
		secs = secs * 60.0 + n
	return secs
	
def SecondsToStr( secs = 0 ):
	secs = int(secs)
	return '{:02d}:{:02d}:{:02d}'.format(secs // (60*60), (secs // 60)%60, secs % 60)

def SecondsToMMSS( secs = 0 ):
	secs = int(secs)
	return '{:02d}:{:02d}'.format((secs // 60)%60, secs % 60)

def ordinal( value ):
	try:
		value = int(value)
	except ValueError:
		return u'{}'.format(value)

	return {
		'fr': lambda v: '{}{}'.format(v, 'er' if v == 1 else 'e'),
		'es': lambda v: u'{}.\u00B0'.format(v),
		'en': lambda v: "{}{}".format(v, ['th','st','nd','rd','th','th','th','th','th','th'][v%10]) if (v % 100)//10 != 1 else "{}{}".format(value, "th"),
	}.get( lang[:2], lambda v: '{}'.format(v) )( value )

def getHomeDir():
	sp = wx.StandardPaths.Get()
	homedir = sp.GetUserDataDir()
	try:
		if os.path.basename(homedir) == '.CrossMgr':
			homedir = os.path.join( os.path.dirname(homedir), '.CrossMgrApp' )
	except:
		pass
	if not os.path.exists(homedir):
		os.makedirs( homedir )
	return homedir

def getDocumentsDir():
	sp = wx.StandardPaths.Get()
	dd = sp.GetDocumentsDir()
	if not os.path.exists(dd):
		os.makedirs( dd )
	return dd
	
#------------------------------------------------------------------------
# Use Firefox to display the help if we can find it.
for firefoxProg in ['/usr/bin/firefox', '']:
	if os.path.exists(firefoxProg) and os.access(firefoxProg, os.X_OK):
		break

if 'WXMAC' in wx.Platform:
	def showHelp( url ):
		url = os.path.join( getHelpFolder(), url )
		os.system( 'open -a Safari %s' % url.split('#')[0] )
elif firefoxProg:
	def showHelp( url ):
		url = os.path.join( getHelpFolder(), url )
		os.system( '"%s" "file://%s" &' % (firefoxProg, url) )
else:
	def showHelp( url ):
		url = os.path.join( getHelpFolder(), url )
		webbrowser.open( url, new = 0, autoraise = True )

#------------------------------------------------------------------------

reSpace = re.compile(r'\s')
def approximateMatch( s1, s2 ):
	s1 = removeDiacritic(reSpace.sub('', s1).lower())
	s2 = removeDiacritic(reSpace.sub('', s2).lower())
	if s1[-1:].isdigit():
		return 1.2 if s1 == s2 else 0.0
	if s1.startswith(s2) or s2.startswith(s1):
		return 1.1
	return len(set(s1) & set(s2)) / float(len(s1) + len(s2))
	
#------------------------------------------------------------------------
PlatformName = platform.system()
def writeLog( message ):
	try:
		dt = datetime.datetime.now()
		dt = dt.replace( microsecond = 0 )
		sys.stdout.write( '{} ({}) {}{}'.format(dt.isoformat(), PlatformName, message, '\n' if not message or message[-1] != '\n' else '' ) )
		sys.stdout.flush()
	except IOError:
		pass

def disable_stdout_buffering():
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w", 0)

def logCall( f ):
	def _getstr( x ):
		return u'{}'.format(x) if not isinstance(x, wx.Object) else u'<<{}>>'.format(x.__class__.__name__)
	
	def new_f( *args, **kwargs ):
		parameters = [_getstr(a) for a in args] + [ u'{}={}'.format( key, _getstr(value) ) for key, value in kwargs.iteritems() ]
		writeLog( 'call: {}({})'.format(f.__name__, removeDiacritic(u', '.join(parameters))) )
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

def refreshForecastHistory():
	if mainWin is not None:
		mainWin.forecastHistory.refresh()

def updateUndoStatus():
	if mainWin is not None:
		mainWin.updateUndoStatus()

def writeRace():
	if mainWin is not None:
		mainWin.writeRace()
		
def writeConfig( key, value ):
	try:
		return mainWin.config.Write( key, value )
	except:
		pass

def readConfig( key, defaultVal ):
	try:
		return mainWin.config.Read( key, defaultVal )
	except:
		return None
	
def getFileName():
	return mainWin.fileName if mainWin is not None else None
	
def isMainWin():
	return mainWin is not None

def hasTrailingSeparator( menu ):
	itemCount = menu.GetMenuItemCount()
	return itemCount > 0 and menu.FindItemByPosition(itemCount-1).IsSeparator()
	
def addMissingSeparator( menu ):
	if not hasTrailingSeparator(menu):
		menu.AppendSeparator()
	
def deleteTrailingSeparators( menu ):
	while hasTrailingSeparator(menu):
		menu.DeleteItem( menu.FindItemByPosition(menu.GetMenuItemCount()-1) )
	
def AlignHorizontalScroll( gFrom, gTo ): 
	xFrom, yFrom = gFrom.GetViewStart()
	xTo,   yTo   = gTo.GetViewStart()
	gTo.Scroll( xFrom, yTo )
	
def AlignVerticalScroll( gFrom, gTo ): 
	xFrom, yFrom = gFrom.GetViewStart()
	xTo,   yTo   = gTo.GetViewStart()
	gTo.Scroll( xTo, yFrom )

def LayoutChildResize( child ):
	parent = child.GetParent()
	while parent:
		parent.Layout()
		if parent.IsTopLevel():
			break
		parent = parent.GetParent()
		
def GetPngBitmap( fname ):
	return wx.Bitmap( os.path.join(imageFolder, fname), wx.BITMAP_TYPE_PNG )
			
def CombineFirstLastName( firstName, lastName ):
	if lastName:
		if firstName:
			return '%s, %s' % (lastName, firstName)
		else:
			return lastName
	else:
		return firstName

def ParsePhotoFName( fname ):
	fname = os.path.splitext(os.path.basename(fname))[0]
	fields = fname.split( '-' )
	
	bib = int(fields[1])
	hour, minute, second, decimal = fields[3:7]
	raceTime = float(hour)*(60.0*60.0) + float(minute)*60.0 + float(second) + float(decimal)/(10**len(decimal))
	count = int(fields[-1])
	photoTime = datetime.datetime.fromtimestamp(int(fields[7], 36) / 10000.0) if len(fields) >= 9 else None
	return bib, raceTime, count, photoTime

invalidFNameChars = set( c for c in '<>:"/\\|?*' )
def ValidFilename( fname ):
	return ''.join( c for c in fname if c not in invalidFNameChars and ord(c) > 31 )

def GetDefaultHost():
	DEFAULT_HOST = socket.gethostbyname(socket.gethostname())
	if DEFAULT_HOST in ('127.0.0.1', '127.0.1.1'):
		reSplit = re.compile('[: \t]+')
		try:
			co = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE)
			ifconfig = co.stdout.read()
			for line in ifconfig.split('\n'):
				line = line.strip()
				try:
					if line.startswith('inet addr:'):
						fields = reSplit.split( line )
						addr = fields[2]
						if addr != '127.0.0.1':
							DEFAULT_HOST = addr
							break
				except:
					pass
		except:
			pass
	return DEFAULT_HOST	

if __name__ == '__main__':
	initTranslation()
	app = wx.App(False)
	
	MessageOK( None, 'Test', 'Test', wx.ICON_INFORMATION )
	MessageOKCancel( None, 'Test', 'Test' )
	MessageYesNo( None, 'Test', 'Test' )
	MessageYesNoCancel( None, 'Test', 'Test' )
	
	disable_stdout_buffering()
	try:
		a = 5 / 0
	except Exception as e:
		logException( e, sys.exc_info() )
		
	wx.Exit()
	
	hd = getHomeDir()
	fn = os.path.join(hd, 'Test.txt')
	with open( fn, 'w' ) as fp:
		print 'successfully opened: ' + fn

cameraError = None
rfidReaderError = None
