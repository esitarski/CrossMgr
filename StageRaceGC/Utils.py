#-----------------------------------------------------------------------
# Set translation locale.
#
import wx
locale = wx.Locale()

from Version import AppVerName
import gettext
initTranslationCalled = False
def initTranslation():
	global initTranslationCalled
	if not initTranslationCalled:
		gettext.install(AppVerName.split(None, 1), './locale')
		initTranslationCalled = True
		
initTranslation()

try:
	from win32com.shell import shell, shellcon
except ImportError:
	pass
	
import os
import re
import sys
import math
import subprocess
import datetime
import platform
import traceback
import unicodedata

def removeDiacritic(input):
	'''
	Accept a unicode string, and return a normal string (bytes in Python 3)
	without any diacritical marks.
	'''
	if type(input) == str:
		return input
	else:
		return unicodedata.normalize('NFKD', input).encode('ASCII', 'ignore')
	
'''
wx.ICON_EXCLAMATION	Shows an exclamation mark icon.
wx.ICON_HAND	Shows an error icon.
wx.ICON_ERROR	Shows an error icon - the same as wxICON_HAND.
wx.ICON_QUESTION	Shows a question mark icon.
wx.ICON_INFORMATION	Shows an information (i) icon.
'''

def MessageOK( parent, message, title = '', iconMask = 0):
	dlg = wx.MessageDialog(parent, message, title, wx.OK | iconMask)
	dlg.ShowModal()
	dlg.Destroy()
	return True
	
def MessageOKCancel( parent, message, title = '', iconMask = 0):
	dlg = wx.MessageDialog(parent, message, title, wx.OK | wx.CANCEL | iconMask )
	response = dlg.ShowModal()
	dlg.Destroy()
	return True if response == wx.ID_OK else False
	
def MessageYesNoCancel( parent, message, title = '', iconMask = 0 ):
	dlg = wx.MessageDialog(parent, message, title, wx.YES_NO | wx.CANCEL | iconMask )
	response = dlg.ShowModal()
	dlg.Destroy()
	return response
	
def DeleteAllGridRows( grid ):
	if grid.GetNumberRows() > 0:
		grid.DeleteRows( 0, grid.GetNumberRows(), True )
		
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

try:
	dirName = os.path.dirname(os.path.abspath(__file__))
except:
	dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

if os.path.basename(dirName) == 'library.zip':
	dirName = os.path.dirname(dirName)
if not path.isdir( path.join(dirName, 'StageRaceGCImages') ):
	dirName = os.path.dirname( dirName )
	
imageFolder = os.path.join(dirName, 'StageRaceGCImages')
htmlDocFolder = os.path.join(dirName, 'StageRaceGCHtmlDoc')

PlatformName = platform.system()
def writeLog( message ):
	try:
		dt = datetime.datetime.now()
		dt = dt.replace( microsecond = 0 )
		msg = u'{} ({}) {}{}'.format(
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
	'''
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w", 0)
	'''
		
def logCall( f ):
	def _getstr( x ):
		return u'{}'.format(x) if not isinstance(x, wx.Object) else u'<<{}>>'.format(x.__class__.__name__)
	
	def new_f( *args, **kwargs ):
		parameters = [_getstr(a) for a in args] + [ '{}={}'.format( key, _getstr(value) ) for key, value in kwargs.items() ]
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

def fieldToHeader( f, multi_line=False ):
	if f == 'uci_id':
		return _('UCI ID')
	if f == 'uci_code':
		return _('UCI Code')
	if f.endswith('_name'):
		f = f[:-5]
	f = f.replace('_', u' ').replace('uci', 'UCI')
	s = ' '.join( w[0].upper() + w[1:] for w in f.split() )
	s = s.replace(' With ', ' with ').replace(' In ', ' in ').replace(' Of ', ' of ')
	s = s.replace( 'with Bonus', '-Bonus' ).replace( 'Plus Penalty', '+Penalty' ).replace( 'Plus Second', '+Second' )
	s = s.replace( 'Kom', 'KOM' )
	if multi_line:
		fields = s.split()
		if len(fields) == 2:
			s = '\n'.join( fields )
		elif len(fields) > 2:
			i = len(s) // 2
			dFirst = s[:i].rfind(' ')
			dLast = s[i:].find(' ')
			if dFirst > 0 or dLast > 0:
				if dLast < 0:
					dLast = 100000
				if i - dFirst < dLast:
					j = dFirst
				else:
					j = i + dLast
				s = s[:j] + '\n' + s[j+1:]
	return s

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

def StrToSeconds( str = '' ):
	secs = 0.0
	for f in str.split(':'):
		try:
			n = float(f)
		except ValueError:
			n = 0.0
		secs = secs * 60.0 + n
	return secs
	
lang = 'en'
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
	homedir = os.path.expanduser('~')
	return homedir

def getDirName():		return dirName
def getImageFolder():	return imageFolder
def getHtmlFolder():	return htmlFolder
def getHtmlDocFolder():	return htmlDocFolder

if sys.platform == 'darwin':
	webbrowser.register("chrome", None, webbrowser.MacOSXOSAScript('chrome'), -1)

def LaunchApplication( fnames ):
	for fname in (fnames if isinstance(fnames, list) else [fnames]):
		if os.name == 'nt':
			subprocess.call(('cmd', '/C', 'start', '', fname))
		elif sys.platform.startswith('darwin'):
			subprocess.call(('open', fname))
		else:
			subprocess.call(('xdg-open', fname))	# Linux
	
