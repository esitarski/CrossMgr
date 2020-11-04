import sys
import collections
from netifaces import interfaces, ifaddresses, AF_INET

isWindows = sys.platform.startswith('win')

#------------------------------------------------------------------------
# Get resource directories.
#
import wx
import os
import io

import wx.lib.agw.genericmessagedialog

if 'WXMAC' in wx.Platform:
	try:
		topdirName = os.environ['RESOURCEPATH']
	except:
		topdirName = os.path.dirname(os.path.realpath(__file__))
	if os.path.isdir( os.path.join(topdirName, 'SeriesMgrImages') ):
		dirName = topdirName
	else:
		dirName = os.path.normpath(topdirName + '/../Resources/')
	if not os.path.isdir(dirName):
		dirName = os.path.normpath(topdirName + '/../../Resources/')
	if not os.path.isdir(dirName):
		raise Exception("Resource Directory does not exist:" + dirName)
		
	# Make message not have the standard python icon on Mac.
	wx.MessageDialog = wx.lib.agw.genericmessagedialog.GenericMessageDialog
		
else:
	try:
		dirName = os.path.dirname(os.path.abspath(__file__))
	except:
		dirName = os.path.dirname(os.path.abspath(sys.argv[0]))
	
	if os.path.basename(dirName) in ['library.zip', 'MainWin.exe', 'CrossMgr.exe', 'SeriesMgr.exe']:
		dirName = os.path.dirname(dirName)
	if 'CrossMgr?' in os.path.basename(dirName):
		dirName = os.path.dirname(dirName)
	if not os.path.isdir( os.path.join(dirName, 'SeriesMgrImages') ):
		dirName = os.path.dirname(dirName)

	if os.path.isdir( os.path.join(dirName, 'SeriesMgrImages') ):
		pass
	elif os.path.isdir( '/usr/local/SeriesMgrImages' ):
		dirName = '/usr/local'

imageFolder = os.path.join(dirName, 'SeriesMgrImages')
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
# First check enviroment variable.
lang = os.environ.get('CrossMgrLanguage', None)

# Then check default OS language.
import locale
if not lang:
	try:
		import ctypes
		windll = ctypes.windll.kernel32
		lang = locale.windows_locale[ windll.GetUserDefaultUILanguage() ]
	except:
		lang = locale.getdefaultlocale()[0]

# Finally, if that doesn't work, default to English.
lang = (lang or 'en')[:2]

#-----------------------------------------------------------------------
# Setup translation.
#
import sys
from Version import AppVerName
import gettext
initTranslationCalled = False
translate = None
import builtins
builtins.__dict__['_'] = translate = lambda s: s
def initTranslation():
	global initTranslationCalled
	global translate
	
	if not initTranslationCalled or (lang and not lang.startswith('en')):
		initTranslationCalled = True
		
		try:
			gettext.install('messages', os.path.join(dirName,'CrossMgrLocale'), unicode=1)
		except:
			gettext.install('messages', os.path.join(dirName,'CrossMgrLocale'))
		
		# Try to use a translation matching the user's language.
		try:
			translation = gettext.translation('messages', os.path.join(dirName,'CrossMgrLocale'), languages=[lang[:2]])
			translation.install()
			builtins.__dict__['_'] = translate = translation.ugettext
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
		self._Save = builtins.__dict__['_']
		builtins.__dict__['_'] = lambda x: x
	def __exit__(self, type, value, traceback):
		builtins.__dict__['_'] = self._Save

class UIBusy( object ):
	def __enter__(self):
		wx.BeginBusyCursor()
	
	def __exit__( self, type, value, traceback ):
		wx.EndBusyCursor()
		return False

def GetDateTimeToday():
	tQuery = datetime.datetime.now()
	return wx.DateTime.FromDMY( tQuery.day, tQuery.month-1, tQuery.year )

import wx.lib.agw.supertooltip as STT
def SetSuperTooltip( target, header, message ):
	tip = STT.SuperToolTip( header=header, message=message )
	tip.ApplyStyle("Outlook Green")
	tip.SetTarget( target )
	
#---------------------------------------------------------------------------
from contextlib import contextmanager

@contextmanager
def tag( buf, name, attrs = None ):
	if not attrs:
		attrs = {}
	if not isinstance(attrs, dict):
		attrs = { 'class': attrs }
	if attrs:
		buf.write( u'<{} {}>'.format(name, u' '.join(['{}="{}"'.format(attr, value) for attr, value in attrs.items()])) )
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

'''
import wx.lib.agw.genericmessagedialog
if 'WXMAC' in wx.Platform:
	# Error, Information and Question dialogs have no icons on the Mac.
	# Replace all message dialogs with generics dialogs.
	wx.MessageDialog = wx.lib.agw.genericmessagedialog.GenericMessageDialog
'''

# Fix up numeric keypad keys.
if 'WXMAC' in wx.Platform:
	wx.WXK_NUMPAD_ENTER = 13
	wx.WXK_NUMPAD_MULTIPLY = 42
	wx.WXK_NUMPAD_DIVIDE = 47
	wx.WXK_NUMPAD_EQUAL = 61
	wx.WXK_NUMPAD_ADD = 43
	wx.WXK_NUMPAD_SUBTRACT = 45
	
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
	ret = unicodedata.normalize('NFKD', u'{}'.format(s)).encode('ascii','ignore').decode()
	if ret.endswith( '.0' ):
		ret = ret[:-2]
	return ret

invalidFilenameChars = re.compile( "[^-_.() " + string.ascii_letters + string.digits + "]" )
def RemoveDisallowedFilenameChars( filename ):
	cleanedFilename = unicodedata.normalize('NFKD', u'{}'.format(filename).strip()).encode('ASCII', 'ignore').decode()
	cleanedFilename = cleanedFilename.replace( '/', '_' ).replace( '\\', '_' )
	return invalidFilenameChars.sub( '', cleanedFilename )

def RemoveDisallowedSheetChars( sheetName ):
	sheetName = unicodedata.normalize('NFKD', u'{}'.format(sheetName)).encode('ASCII', 'ignore').decode()
	return re.sub('[+!#$%&+~`".:;|\\\\/?*\[\] ]+', ' ', sheetName)[:31]		# four backslashes required to match one backslash in re.

class UniqueExcelSheetName():
	def __init__( self ):
		self.sheetNames = collections.defaultdict( int )
		
	def getSheetName( self, name ):
		sheetName = RemoveDisallowedSheetChars( name )
		while True:
			self.sheetNames[sheetName] += 1
			if self.sheetNames[sheetName] == 1:
				return sheetName
			suffix = '-{}'.format( sheetNameCount[sheetName] )
			sheetName = '{}{}'.format( sheetName[:31-len(suffix)], suffix )			
	
def removeDiacritic( s ):
	'''
	Accept a unicode string, and return a normal string
	without any diacritical marks.
	'''
	try:
		return unicodedata.normalize('NFKD', u'{}'.format(s)).encode('ASCII', 'ignore').decode()
	except:
		return s
	
def GetFileName( rDate, rName, rNum, rMemo ):
	return u'{}-{}-r{}-{}.cmn'.format(*[RemoveDisallowedFilenameChars(v) for v in (rDate, rName, rNum, rMemo)])
		
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
		soundCache[soundFile] = wx.adv.Sound( soundFile )
		return soundCache[soundFile].Play()
		
def PlaySound( soundFile ):
	if mainWin and not mainWin.playSounds:
		return True
	return Play( soundFile )

def GetSelectedRows( grid ):
	rows = []
	for row in range(grid.GetNumberRows()):
		if any(grid.IsInSelection(row, col) for col in range(grid.GetNumberCols())):
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
	for c in range(grid.GetNumberCols()):
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly()
		grid.SetColAttr( c, attr )

def SwapGridRows( grid, r, rTarget ):
	if r != rTarget and 0 <= r < grid.GetNumberRows() and 0 <= rTarget < grid.GetNumberRows():
		for c in range(grid.GetNumberCols()):
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
		r, g, b = [int(c, 16)<<4 for c in s]
	else:
		r, g, b = [int(s[i:i+2], 16) for i in range(0, 6, 2)]
	return wx.Colour(r, g, b)

epoch = datetime.datetime.utcfromtimestamp(0)
def millisFromEpoch( d = None ):
	d = d or datetime.datetime.now()
	return int((d - epoch).total_seconds() * 1000.0)

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
	if not isinstance(value, int):
		try:
			value = int(value)
		except ValueError:
			return u'{}'.format(value)
		
	if value == 999999:
		return translate(u'DNF')

	return {
		'fr': lambda v: '{}{}'.format(v, 'er' if v == 1 else 'e'),
		'en': lambda v: "{}{}".format(v, ['th','st','nd','rd','th','th','th','th','th','th'][v%10]) if (v % 100)//10 != 1 else "{}{}".format(value, "th"),
	}.get( lang[:2], lambda v: u'{}.\u00B0'.format(v) )( value )	# Default: show with a degree sign.

def getHomeDir( appName='CrossMgr' ):
	sp = wx.StandardPaths.Get()
	homedir = sp.GetUserDataDir()
	try:
		if os.path.basename(homedir) == '.{}'.format(appName):
			homedir = os.path.join( os.path.dirname(homedir), '.{}App'.format(appName) )
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
from Version import AppVerName
AppVer = 'v' + AppVerName.split(' ')[1]
def writeLog( message ):
	try:
		dt = datetime.datetime.now()
		dt = dt.replace( microsecond = 0 )
		msg = u'{} ({} {}) {}{}'.format(
			dt.isoformat(),
			AppVer,
			PlatformName,
			message,
			'\n' if not message or message[-1] != '\n' else '',
		)
		sys.stdout.write( removeDiacritic(msg) )
		sys.stdout.flush()
	except IOError:
		pass

def disable_stdout_buffering():
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w")

def logCall( f ):
	def _getstr( x ):
		return u'{}'.format(x) if not isinstance(x, wx.Object) else u'<<{}>>'.format(x.__class__.__name__)
	
	def new_f( *args, **kwargs ):
		parameters = [_getstr(a) for a in args] + [ u'{}={}'.format( key, _getstr(value) ) for key, value in kwargs.items() ]
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
	try:
		return mainWin.fileName
	except:
		return None
	
def getFileDir():
	try:
		return os.path.dirname(os.path.abspath(mainWin.fileName))
	except:
		return os.path.expanduser('~')
	
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
		menu.Delete( menu.FindItemByPosition(menu.GetMenuItemCount()-1) )
	
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
	
	try:
		raceTime = float(hour)*(60.0*60.0) + float(minute)*60.0 + float(second) + float(decimal)/(10**len(decimal))
	except:
		writeLog( 'ParsePhotoFName: raceTime fname="{}"'.format(fname) )
		logException( e, sys.exc_info() )
		raise
	
	try:
		count = int(fields[-1])
	except Exception as e:
		writeLog( 'ParsePhotoFName: count fname="{}"'.format(fname) )
		logException( e, sys.exc_info() )
		raise

	photoTime = datetime.datetime.fromtimestamp(int(fields[7], 36) / 10000.0) if len(fields) >= 9 else None
	return bib, raceTime, count, photoTime

invalidFNameChars = set( c for c in '<>:"/\\|?*' )
def ValidFilename( fname ):
	return ''.join( c for c in fname if c not in invalidFNameChars and ord(c) > 31 )

def GetDefaultHost():
	try:
		DEFAULT_HOST = '127.0.0.1'
		done = False
		for ifaceName in interfaces():
			if done == True:
				break
			ips = ifaddresses(ifaceName).setdefault(AF_INET)
			if (ips != None):
				for i in ips:
					currentaddress = str(i['addr'])
					# Only add real ips
					if (currentaddress.startswith('127') == False and currentaddress.startswith('169') == False):
						DEFAULT_HOST = currentaddress
						done = True
						break
	except:
		DEFAULT_HOST = '0.0.0.0'

	return DEFAULT_HOST
	
if sys.platform == 'darwin':
	webbrowser.register("chrome", None, webbrowser.MacOSXOSAScript('chrome'))

def LaunchApplication( fnames ):
	for fname in (fnames if isinstance(fnames, list) else [fnames]):
		if os.name == 'nt':							# Windows.
			subprocess.call(('cmd', '/C', 'start', '', fname))
		elif sys.platform.startswith('darwin'):
			subprocess.call(('open', fname))		# Apple
		else:
			subprocess.call(('xdg-open', fname))	# Linux

def BoldFromFont( font ):
	# pointSize, family, style, weight, underline=False, face="", encoding
	return wx.Font(
		font.GetPixelSize(),
		font.GetFamily(),
		font.GetStyle(),
		wx.FONTWEIGHT_BOLD,
		font.GetUnderlined(),
	)

def dict_compare(d_new, d_old):
	'''
		Returns three sets:
			added:		keys in d_new not in d_old
			removed:	keys in d_old not in d_new
			modified:	keys in d_new with different values than in d_old
	'''
	d_new_keys = set(d_new.keys())
	d_old_keys = set(d_old.keys())
	return {
		'r':list(d_old_keys - d_new_keys),
		'a':{o:d_new[o] for o in d_new_keys - d_old_keys},
		'm':{o:d_new[o] for o in d_new_keys.intersection(d_old_keys) if d_new[o] != d_old[o]},
	}

def GetContrastTextColour( backgroundColour ):
	r, g, b = backgroundColour.Get( False )
	yiq = ((r*299)+(g*587)+(b*114))/1000.0
	return  wx.BLACK if yiq >= 128.0 else wx.WHITE
	
def GetGoogleMapsApiKey():
	return 'AIzaSyD2sl2JTvnyMcsgWc3tTceWCYo3ZoyWdAI'

import json
def ToJson( v, separators=(',',':') ):
	''' Make sure we always return a unicode string. '''
	return json.dumps( v, separators=separators )

if __name__ == '__main__':
	initTranslation()
	app = wx.App(False)
	
	print( RemoveDisallowedSheetChars('Cat A/B') )
	print(  RemoveDisallowedFilenameChars('Cat A/B') )
	
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
		print(  'successfully opened: ' + fn )

cameraError = None
rfidReaderError = None
