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
	return '%02d:%02d:%02d' % (secs // (60*60), (secs // 60)%60, secs % 60)

def SecondsToMMSS( secs = 0 ):
	secs = int(secs)
	return '%02d:%02d' % ((secs // 60)%60, secs % 60)

def getHomeDir():
	sp = wx.StandardPaths.Get()
	homedir = sp.GetUserDataDir()
	try:
		if os.path.basename(homedir) == '.CrossMgrImpinj':
			homedir = os.path.join( os.path.dirname(homedir), '.CrossMgrImpinjApp' )
	except:
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

	if os.path.basename(dirName) == 'library.zip':
		dirName = os.path.dirname(dirName)
	if 'CrossMgrImpinj?' in os.path.basename(dirName):
		dirName = os.path.dirname(dirName)

	if os.path.isdir( os.path.join(dirName, 'CrossMgrImpinjImages') ):
		pass
	elif os.path.isdir( '/usr/local/CrossMgrImpinjImages' ):
		dirName = '/usr/local'

imageFolder = os.path.join(dirName, 'CrossMgrImpinjImages')
htmlFolder = os.path.join(dirName, 'CrossMgrHtml')
helpFolder = os.path.join(dirName, 'CrossMgrHtmlDoc')

def getDirName():		return dirName
def getImageFolder():	return imageFolder
def getHtmlFolder():	return htmlFolder
def getHelpFolder():	return helpFolder

#------------------------------------------------------------------------
playBell = False
def Bell():
	if playBell:
		wx.CallAfter( wx.Bell )
		
#------------------------------------------------------------------------
def disable_stdout_buffering():
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w", 0)
		
def readDelimitedData( s, delim ):
	buffer = s.recv( 4096 )
	while 1:
		nl = buffer.find( delim )
		if nl >= 0:
			yield buffer[:nl]
			buffer = buffer[nl+len(delim):]
		else:
			more = s.recv( 4096 )
			if more:
				buffer = buffer + more
			else:
				break
	yield buffer
		
#------------------------------------------------------------------------------------------------
reIP = re.compile( '^[0-9.]+$' )

def GetAllIps():
	addrInfo = socket.getaddrinfo( socket.gethostname(), None )
	ips = []
	for a in addrInfo:
		try:
			ip = a[4][0]
		except:
			continue
		if reIP.search(ip):
			ips.append( ip )
	return ips