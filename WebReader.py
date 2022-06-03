import wx
import Utils
import Model

# Simple reader control functions as the messages come from the web server.

def StartListener( startTime=None, HOST=None, PORT=None, test=False ):
	# Messages come from the web server, so, nothing to do here.
	pass
	
data = []
def SetData( data_new ):
	global data
	data.extend( data_new )
	mainWin = Utils.getMainWin()
	if mainWin and Model.race and Model.race.isRunning():
		wx.CallAfter( mainWin.processJChipListener )
	
def GetData():
	global data
	data_ret = data
	data = []
	return data_ret

def StopListener():
	# Messages come from the web server, so, nothing to do here.
	pass
	
def CleanupListener():
	# Messages come from the web server, so, nothing to do here.
	pass

def IsListening():
	# Always true as the web server is always running.
	return True

