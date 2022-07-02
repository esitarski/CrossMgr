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
		try:
			gettext.install(AppVerName.split(None, 1), './locale', unicode=True)
		except:
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
import platform
import datetime
import traceback
import subprocess
import unicodedata

def removeDiacritic( s ):
	'''
	Accept a unicode string, and return a normal string
	without any diacritical marks.
	'''
	try:
		return unicodedata.normalize('NFKD', '{}'.format(s)).encode('ASCII', 'ignore').decode()
	except:
		return s
		
'''
wx.ICON_EXCLAMATION	Shows an exclamation mark icon.
wx.ICON_HAND	Shows an error icon.
wx.ICON_ERROR	Shows an error icon - the same as wxICON_HAND.
wx.ICON_QUESTION	Shows a question mark icon.
wx.ICON_INFORMATION	Shows an information (i) icon.
'''

def MessageOK( parent, message, title = '', iconMask = 0 ):
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

if 'WXMAC' in wx.Platform:
	try:
		topdirName = os.environ['RESOURCEPATH']
	except:
		topdirName = os.path.dirname(os.path.realpath(__file__))
	if os.path.isdir( os.path.join(topdirName, 'images') ):
		dirName = topdirName
	else:
		dirName = os.path.normpath(topdirName + '/../Resources/')
	if not os.path.isdir(dirName):
		dirName = os.path.normpath(topdirName + '/../../Resources/')
	if not os.path.isdir(dirName):
		raise Exception("Resource Directory does not exist:" + dirName)
		
else:
	try:
		dirName = os.path.dirname(os.path.abspath(__file__))
	except:
		dirName = os.path.dirname(os.path.abspath(sys.argv[0]))
	
	if os.path.basename(dirName) in ['library.zip', 'MainWin.exe', 'CrossMgrCallUpSeedingMgr.exe']:
		dirName = os.path.dirname(dirName)
	if 'CrossMgrSeedingMgr?' in os.path.basename(dirName):
		dirName = os.path.dirname(dirName)
	if not os.path.isdir( os.path.join(dirName, 'images') ):
		dirName = os.path.dirname(dirName)

	if os.path.isdir( os.path.join(dirName, 'images') ):
		pass
	elif os.path.isdir( '/usr/local/images' ):
		dirName = '/usr/local'

imageFolder = os.path.join(dirName, 'images')
htmlFolder = os.path.join(dirName, 'html')
htmlDocFolder = os.path.join(dirName, 'htmldoc')

import webbrowser
if 'WXMAC' in wx.Platform:
	webbrowser.register("chrome", None, webbrowser.MacOSXOSAScript('chrome'))

def LaunchApplication( fnames ):
	for fname in (fnames if isinstance(fnames, list) else [fnames]):
		if os.name == 'nt':
			subprocess.call(('cmd', '/C', 'start', '', fname))
		elif sys.platform.startswith('darwin'):
			subprocess.call(('open', fname))
		else:
			subprocess.call(('xdg-open', fname))	# Linux

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
	sys.stdout = os.fdopen(fileno, "w")
		
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
	

def getHomeDir():
	homedir = os.path.expanduser('~')
	return homedir

def getDirName():		return dirName
def getImageFolder():	return imageFolder
def getHtmlFolder():	return htmlFolder
def getHtmlDocFolder():	return htmlDocFolder

