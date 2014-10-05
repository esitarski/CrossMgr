import wx
import sys
import os
import re
import time
import math
import datetime

HOST = 'localhost'
PORT = 54111

now = datetime.datetime.now

import sys
import threading
import socket
import atexit
import time
import threading
from Queue import Queue
from Queue import Empty

import Utils
from SocketListener import SocketListener
from PhotoWriter import PhotoWriter
from FrameCircBuf import FrameCircBuf
from AddPhotoHeader import AddPhotoHeader, PilImageToWxImage
from ScaledImage import ScaledImage
from VideoCapture import Device

from Version import AppVerName

def setFont( font, w ):
	w.SetFont( font )
	return w

def formatTime( secs ):
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
	secs = secs % 60 + f
	return "%s%02d:%02d:%06.3f" % (sign, hours, minutes, secs)
	
def fileFormatTime( secs ):
	return formatTime(secs).replace(':', '-').replace('.', '-')
	
fileFormat = 'bib-%04d-time-%s-%d.jpg'
def GetPhotoFName( dirName, bib, raceSeconds, i ):
	return os.path.join( dirName, fileFormat % (bib if bib else 0, fileFormatTime(raceSeconds), i+1 ) )

class MessageManager( object ):
	MessagesMax = 400	# Maximum number of messages before we start throwing some away.

	def __init__( self, messageList ):
		self.messageList = messageList
		self.messageList.Bind( wx.EVT_RIGHT_DOWN, self.skip )
		self.messageList.SetDoubleBuffered( True )
		self.clear()
		
	def skip(self, evt):
		return
		
	def write( self, message ):
		if len(self.messages) >= self.MessagesMax:
			self.messages = self.messages[int(self.MessagesMax):]
			s = '\n'.join( self.messages )
			self.messageList.ChangeValue( s + '\n' )
		self.messages.append( message )
		self.messageList.AppendText( message + '\n' )
		
	def clear( self ):
		self.messages = []
		self.messageList.ChangeValue( '' )
		self.messageList.SetInsertionPointEnd()

class ConfigDialog( wx.Dialog ):
	def __init__( self, parent, cameraDeviceNum=0, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, title=_('CrossMgr Camera Configuration') )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.title = wx.StaticText( self, label='CrossMgr Camera Configuration' )
		self.title.SetFont( wx.FontFromPixelSize( wx.Size(0,24), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL ) )
		self.explanation = [
			'Check that the USB Webcam is plugged in.',
			'Check the Camera Device (usually 0).',
		]
		pfgs = wx.FlexGridSizer( rows=0, cols=2, vgap=4, hgap=8 )
		
		pfgs.Add( wx.StaticText(self, label='Camera Device'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.cameraDevice = wx.Choice( self, choices=[unicode(i) for i in xrange(8)] )
		self.cameraDevice.SetSelection( cameraDeviceNum )
		pfgs.Add( self.cameraDevice )
		
		sizer.Add( self.title, flag=wx.ALL, border=4 )
		for i, e in enumerate(self.explanation):
			sizer.Add( wx.StaticText( self, label=u'{}. {}'.format(i+1, e) ),
				flag=wx.LEFT|wx.RIGHT|(wx.TOP if i == 0 else 0)|(wx.BOTTOM if i == len(self.explanation) else 0), border=4,
			)
		sizer.AddSpacer( 8 )
		sizer.Add( pfgs, flag=wx.ALL, border=4 )
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.okBtn, border = 4, flag=wx.ALL )
		self.okBtn.SetDefault()
		hs.AddStretchSpacer()
		hs.Add( self.cancelBtn, border = 4, flag=wx.ALL )
		
		sizer.AddSpacer( 8 )
		sizer.Add( hs, flag=wx.EXPAND )
		
		self.SetSizerAndFit( sizer )
		
	def GetCameraDeviceNum( self ):
		return self.cameraDevice.GetSelection()

	def onOK( self, event ):
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
	
class MainWin( wx.Frame ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(1000,800) ):
		wx.Frame.__init__(self, parent, id, title, size=size)
		
		self.fps = 25
		self.frameDelay = 1.0 / self.fps
		self.bufferSecs = 8
		
		self.tFrameCount = self.tLaunch = self.tLast = now()
		self.frameCount = 0
		self.frameCountUpdate = self.fps * 2
		self.fpsActual = 0.0
		self.fpt = datetime.timedelta(0)
		
		self.fcb = FrameCircBuf( self.bufferSecs * self.fps )
		
		self.config = wx.Config(appName="CrossMgrCamera",
						vendorName="SmartCyclingSolutions",
						style=wx.CONFIG_USE_LOCAL_FILE)
		
		self.requestQ = Queue()
		self.writerQ = Queue()
		self.messageQ = Queue()
		
		self.SetBackgroundColour( wx.Colour(232,232,232) )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.primaryImage = ScaledImage( self, style=wx.BORDER_SUNKEN )
		self.beforeImage = ScaledImage( self, style=wx.BORDER_SUNKEN )
		self.afterImage = ScaledImage( self, style=wx.BORDER_SUNKEN )
		
		#------------------------------------------------------------------------------------------------
		self.controlPanel = wx.Panel( self )
		self.controlPanel.SetDoubleBuffered(True)
		
		phSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.messagesText = wx.TextCtrl( self.controlPanel, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(350,480) )
		self.messageManager = MessageManager( self.messagesText )
		phSizer.Add( self.messagesText, proportion=1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		pfgs = wx.FlexGridSizer( rows=0, cols=3, vgap=4, hgap=8 )
		
		pfgs.Add( wx.StaticText(self.controlPanel, label='Camera Device'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.cameraDevice = wx.Choice( self.controlPanel, choices=[unicode(i) for i in xrange(8)] )
		pfgs.Add( self.cameraDevice )
		pfgs.Add( wx.StaticText(self.controlPanel), flag=wx.ALIGN_CENTRE_VERTICAL )
		
		pfgs.Add( wx.StaticText(self.controlPanel, label='Target Frames'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.frameProcessingTime = wx.StaticText(self.controlPanel, label=u'{:.3f}'.format(self.fps))
		pfgs.Add( self.frameProcessingTime, flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		pfgs.Add( wx.StaticText(self.controlPanel, label='per sec'), flag=wx.ALIGN_CENTRE_VERTICAL )
		
		pfgs.Add( wx.StaticText(self.controlPanel, label='Actual Frames'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.framesPerSecond = wx.StaticText(self.controlPanel, label='25.000')
		pfgs.Add( self.framesPerSecond, flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		pfgs.Add( wx.StaticText(self.controlPanel, label='per sec'), flag=wx.ALIGN_CENTRE_VERTICAL )
		
		pfgs.Add( wx.StaticText(self.controlPanel, label='Available Time Per Frame'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.availableMsPerFrame = wx.StaticText(self.controlPanel, label=u'{:.0f}'.format(1000.0*self.frameDelay))
		pfgs.Add( self.availableMsPerFrame, flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		pfgs.Add( wx.StaticText(self.controlPanel, label='ms'), flag=wx.ALIGN_CENTRE_VERTICAL )
		
		pfgs.Add( wx.StaticText(self.controlPanel, label='Actual Frame Processing'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.frameProcessingTime = wx.StaticText(self.controlPanel, label='20')
		pfgs.Add( self.frameProcessingTime, flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		pfgs.Add( wx.StaticText(self.controlPanel, label='ms'), flag=wx.ALIGN_CENTRE_VERTICAL )
		
		phSizer.Add( pfgs )
		
		self.controlPanel.SetSizerAndFit( phSizer )
		
		row1Sizer = wx.BoxSizer( wx.HORIZONTAL )
		row1Sizer.Add( self.primaryImage, flag=wx.ALL, border=4 )
		row1Sizer.Add( self.controlPanel, 1, flag=wx.ALL, border=4 )
		mainSizer.Add( row1Sizer )
		
		row2Sizer = wx.BoxSizer( wx.HORIZONTAL )
		row2Sizer.Add( self.beforeImage, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4 )
		row2Sizer.Add( self.afterImage, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4 )
		mainSizer.Add( row2Sizer )
		
		#------------------------------------------------------------------------------------------------
		# Create a timer to update the frame loop.
		#
		self.timer = wx.Timer()
		self.timer.Bind( wx.EVT_TIMER, self.frameLoop )
		
		self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

		self.readOptions()
		self.SetSizerAndFit( mainSizer )
		
		# Start the message reporting thread so we can see what is going on.
		self.messageThread = threading.Thread( target=self.showMessages )
		self.messageThread.daemon = True
		self.messageThread.start()
		
		self.grabFrameOK = False
		
		# Start the frame loop.
		ms = int(1000 * self.frameDelay * 0.80)
		self.timer.Start( ms, False )
		
	def Start( self ):
		self.messageQ.put( ('', '************************************************') )
		self.messageQ.put( ('started',now().strftime('%Y/%m/%d %H:%M:%S')) )
		self.startSocket()
		self.startThreads()
		self.startCamera()
		
	def showMessages( self ):
		while 1:
			message = self.messageQ.get()
			assert len(message) == 2, 'Incorrect message length'
			cmd, info = message
			wx.CallAfter( self.messageManager.write, '{}:  {}'.format(cmd, info) if cmd else info )
		
	def startSocket( self ):
		try:
			self.listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.listenerSocket.bind((HOST, PORT))
			self.listenerSocket.listen(5)
			self.messageQ.put( ('socket', 'Listening on {}.{}'.format(HOST,PORT)) )
			return True
		except Exception as e:
			self.messageQ.put( ('socket', 'Failed to connect: {}'.format(e)) )
			return False
		
	def startCamera( self ):
		self.camera = None
		try:
			self.camera = Device( max(self.cameraDevice.GetSelection(), 0) )
		except Exception as e:
			self.messageQ.put( ('camera', 'Error: {}'.format(e)) )
			return False
		
		self.messageQ.put( ('camera', 'Successfully Connected') )
		return True
	
	def startThreads( self ):
		self.grabFrameOK = False
		
		self.listenerThread = threading.Thread( target=SocketListener, args=(self.listenerSocket, self.requestQ) )
		self.listenerThread.daemon = True
		
		self.writerThread = threading.Thread( target=PhotoWriter, args=(self.writerQ, self.messageQ) )
		self.writerThread.daemon = True
		
		self.listenerThread.start()
		self.writerThread.start()
		
		self.fcb = FrameCircBuf( int(self.bufferSecs * self.fps) )
		
		self.grabFrameOK = True
		self.messageQ.put( ('threads', 'Successfully Launched') )
		return True
	
	def frameLoop( self, event=None ):
		if not self.grabFrameOK:
			return
			
		self.frameCount += 1
		tNow = now()
		
		# Compute frame rate statistics.
		if self.frameCount == self.frameCountUpdate:
			self.fpsActual = self.frameCount / (tNow - self.tFrameCount).total_seconds()
			self.frameCount = 0
			self.tFrameCount = tNow
			self.framesPerSecond.SetLabel( u'{:.3f}'.format(self.fpsActual) )
			self.availableMsPerFrame.SetLabel( u'{:.0f}'.format(1000.0/self.fpsActual) )
			self.frameProcessingTime.SetLabel( u'{:.0f}'.format(1000.0*self.fpt.total_seconds()) )
		
		try:
			image = self.camera.getImage()
		except Exception as e:
			self.messageQ.put( ('error', 'Webcam Failure: {}'.format(e) ) )
			self.grabFrameOK = False
			return
		
		image = AddPhotoHeader( PilImageToWxImage(image),
			time=tNow, raceSeconds=(tNow - self.tLaunch).total_seconds(),
			bib=999,
			firstNameTxt=u'Firstname', lastNameTxt=u'LASTNAME', teamTxt=u'Team',
			raceNameTxt='Racename'
		)
		self.primaryImage.SetImage( image )
		self.fcb.append( tNow, image )
		
		# Process save messages
		while 1:
			try:
				message = self.requestQ.get(False)
			except Empty:
				break
			
			times, frames = self.fcb.findBeforeAfter( message['time'], 1, 1 )
			for i, f in enumerate(frames):
				fname = GetPhotoFName( message['dirName'], message.get('bib',None), message.get('raceSeconds',None), i )
				image = AddPhotoHeader(
							f,
							message.get('bib', None),
							message.get('time', None),
							message.get('raceSeconds', None),
							message.get('firstName',u''),
							message.get('lastName',u''),
							message.get('team',u''),
							message.get('raceName',u'')
						)
				if i == 0:
					self.beforeImage.SetImage( image )
				else:
					self.afterImage.SetImage( image )
				self.writerQ.put( ('save', fname, image) )
				
			if (now() - tNow).total_seconds() > self.frameDelay / 2.0:
				break
				
		self.fpt = now() - tNow
		self.tLast = tNow
	
	def shutdown( self ):
		# Ensure that all images in the queue are saved.
		self.grabFrameOK = False
		if hasattr(self, 'writerThread'):
			self.writerQ.put( ('terminate', ) )
			self.writerThread.join()
	
	def resetCamera( self, event, confirm = True ):
		if confirm:
			dlg = wx.MessageDialog(self, 'Reset Camera?',
									'Confirm Reset',
									wx.OK | wx.CANCEL | wx.ICON_WARNING )
			ret = dlg.ShowModal()
			dlg.Destroy()
			if ret != wx.ID_OK:
				return
		
		self.reset.Enable( False )		# Prevent multiple clicks while shutting down.
		
		self.writeOptions()
		self.grabFrameOK = self.startCamera()
		
		self.reset.Enable( True )
		
	def setCameraDeviceNum( self, num ):
		self.cameraDevice.SetSelection( num )
		
	def onCloseWindow( self, event ):
		self.shutdown()
		wx.Exit()
		
	def writeOptions( self ):
		self.config.Write( 'CameraDevice', unicode(self.cameraDevice.GetSelection()) )
		self.config.Flush()
	
	def readOptions( self ):
		self.cameraDevice.SetSelection( int(self.config.Read('CameraDevice', '0')) )

def disable_stdout_buffering():
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w", 0)

redirectFileName = None
mainWin = None
def MainLoop():
	global mainWin, redirectFileName
	
	app = wx.App(False)
	app.SetAppName("CrossMgrCamera")

	mainWin = MainWin( None, title=AppVerName, size=(1300,864) )
	
	dataDir = Utils.getHomeDir()
	redirectFileName = os.path.join(dataDir, 'CrossMgrCamera.log')
	
	# Set up the log file.  Otherwise, show errors on the screen.
	if __name__ == '__main__':
		'''disable_stdout_buffering()'''
		pass
	else:
		try:
			logSize = os.path.getsize( redirectFileName )
			if logSize > 1000000:
				os.remove( redirectFileName )
		except:
			pass
	
		try:
			app.RedirectStdio( redirectFileName )
		except:
			pass
			
		try:
			with open(redirectFileName, 'a') as pf:
				pf.write( '********************************************\n' )
				pf.write( '%s: %s Started.\n' % (datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), AppVerName) )
		except:
			pass
	
	mainWin.Show()

	# Set the upper left icon.
	try:
		icon = wx.Icon( os.path.join(getImageFolder(), 'CrossMgrCamera.ico'), wx.BITMAP_TYPE_ICO )
		mainWin.SetIcon( icon )
	except:
		pass

	mainWin.Refresh()
	dlg = ConfigDialog( mainWin, mainWin.cameraDevice.GetSelection() )
	ret = dlg.ShowModal()
	cameraDeviceNum = dlg.GetCameraDeviceNum()
	dlg.Destroy()
	if ret != wx.ID_OK:
		wx.Exit()
		
	mainWin.cameraDevice.SetSelection( cameraDeviceNum )
	
	# Start processing events.
	mainWin.Start()
	app.MainLoop()

@atexit.register
def shutdown():
	if mainWin:
		mainWin.shutdown()
	
if __name__ == '__main__':
	MainLoop()
	
