import datetime
import wx
import os
import re
import sys
import math
import socket

timeoutSecs = None

DEFAULT_HOST = '127.0.0.1'

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
	
def MessageOKCancel( parent, message, title = '', iconMask = wx.ICON_QUESTION):
	dlg = wx.MessageDialog(parent, message, title, wx.OK | wx.CANCEL | iconMask )
	response = dlg.ShowModal()
	dlg.Destroy()
	return True if response == wx.ID_OK else False
	
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

def formatTime( secs, highPrecision = False ):
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
	secs = secs % 60
	if highPrecision:
		decimal = '.%02d' % int( f * 100 )
	else:
		decimal = ''
	if hours > 0:
		return "{}{}:{:02d}:{:02d}{}".format(sign, hours, minutes, secs, decimal)
	else:
		return "{}{:02d}:{:02d}{}".format(sign, minutes, secs, decimal)

def formatTimeGap( secs, highPrecision = False ):
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
	secs = secs % 60
	if highPrecision:
		decimal = '.{:02d}'.format(int(f * 100))
	else:
		decimal = ''
	if hours > 0:
		return "{}{}h{}'{:02d}{}\"".format(sign, hours, minutes, secs, decimal)
	else:
		return "{}{}'{:02d}{}\"".format(sign, minutes, secs, decimal)

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
	"""
	Converts zero or a *postive* integer (or their string 
	representations) to an ordinal value.

	>>> for i in range(1,13):
	...	 ordinal(i)
	...	 
	'1st'
	'2nd'
	'3rd'
	'4th'
	'5th'
	'6th'
	'7th'
	'8th'
	'9th'
	'10th'
	'11th'
	'12th'

	>>> for i in (100, '111', '112',1011):
	...	 ordinal(i)
	...	 
	'100th'
	'111th'
	'112th'
	'1011th'

	"""
	try:
		value = int(value)
	except ValueError:
		return value

	if (value % 100)//10 != 1:
		return "{}{}".format(value, ['th','st','nd','rd','th','th','th','th','th','th'][value%10])
	return "{}{}".format(value, "th")
	
def getHomeDir():
	sp = wx.StandardPaths.Get()
	homedir = sp.GetUserDataDir()
	try:
		if os.path.basename(homedir) == '.CrossMgr':
			homedir = os.path.join( os.path.dirname(homedir), '.CrossMgrApp' )
	except Exception:
		pass
	if not os.path.exists(homedir):
		os.makedirs( homedir )
	return homedir

def getDocumentsDir():
	sp = wx.StandardPaths.Get()
	return sp.GetDocumentsDir()
	
#------------------------------------------------------------------------
if 'WXMAC' in wx.Platform:
	try:
		topdirName = os.environ['RESOURCEPATH']
	except Exception:
		topdirName = os.path.dirname(os.path.realpath(__file__))
	if os.path.isdir( os.path.join(topdirName, 'CrossMgrAlienImages') ):
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
	except Exception:
		dirName = os.path.dirname(os.path.abspath(sys.argv[0]))
	
	if os.path.basename(dirName) in ['library.zip', 'MainWin.exe', 'CrossMgrAlien.exe']:
		dirName = os.path.dirname(dirName)
	if 'CrossMgr?' in os.path.basename(dirName):
		dirName = os.path.dirname(dirName)
	if not os.path.isdir( os.path.join(dirName, 'CrossMgrAlienImages') ):
		dirName = os.path.dirname(dirName)

	if os.path.isdir( os.path.join(dirName, 'CrossMgrAlienImages') ):
		pass
	elif os.path.isdir( '/usr/local/CrossMgrAlienImages' ):
		dirName = '/usr/local'

imageFolder = os.path.join(dirName, 'CrossMgrAlienImages')
htmlFolder = os.path.join(dirName, 'CrossMgrHtml')
helpFolder = os.path.join(dirName, 'CrossMgrHtmlDoc')

def getDirName():		return dirName
def getImageFolder():	return imageFolder
def getHtmlFolder():	return htmlFolder
def getHelpFolder():	return helpFolder

#------------------------------------------------------------------------

def disable_stdout_buffering():
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w", 0)
		
def readDelimitedData( s, delim ):
	# Handle all the processing in bytes, convert to str on return.
	delim = delim.encode()
	buffer = s.recv( 4096 )
	while True:
		nl = buffer.find( delim )
		if nl >= 0:
			yield buffer[:nl].decode()
			buffer = buffer[nl+len(delim):]
		else:
			more = s.recv( 4096 )
			if more:
				buffer = buffer + more
			else:
				break
	yield buffer.decode()
		
#------------------------------------------------------------------------------------------------
reIP = re.compile( '^[0-9.]+$' )

def GetAllIps():
	addrInfo = socket.getaddrinfo( socket.gethostname(), None )
	ips = []
	for a in addrInfo:
		try:
			ip = a[4][0]
		except Exception:
			continue
		if reIP.search(ip):
			ips.append( ip )
	return ips
	
playBell = False
def Bell():
	if playBell:
		wx.Bell()
