import wx
import sys
import os
import re
import time
import math
import datetime
from datetime import timedelta

now = datetime.datetime.now

import sys
import threading
import socket
import atexit
import time
import threading
import platform
from Queue import Queue, Empty, Full

import Utils
from SocketListener import SocketListener
from PhotoWriter import PhotoWriter
from FTPWriter import FTPWriter
from PhotoRenamer import PhotoRenamer
from FrameCircBuf import FrameCircBuf
from AddPhotoHeader import AddPhotoHeader, PilImageToWxImage
from ScaledImage import ScaledImage
from GetPhotoFName import GetPhotoFName
from SaveImage import SaveImage

imageWidth, imageHeight = 640, 480

try:
	#from VideoCapture import Device
	from jaraco.video.capture_nofont import Device
except:
	if platform.system() == 'Windows':
		raise
	from PIL import Image, ImageDraw
	class Device( object ):
		def __init__( self, cameraDeviceNum = 0 ):
			self.cameraDeviceNum = cameraDeviceNum
			
		def getImage( self ):
			# Return a test image.
			image = Image.new('RGB', (imageWidth, imageHeight), (255,255,255))
			draw = ImageDraw.Draw( image )
			y1 = 0
			y2 = imageHeight
			colours = ((0,0,0), (255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255), (255,255,255))
			rWidth = int(float(imageWidth) / len(colours) + 0.5)
			for i, c in enumerate(colours):
				x1, x2 = rWidth * i, rWidth * (i+1)
				draw.rectangle( ((x1, y1), (x2, y2)), fill=c )
			return image

from Version import AppVerName

def setFont( font, w ):
	w.SetFont( font )
	return w

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

cameraResolution = (
	(160,120),
	(320,240),
	(424,240),
	(640,360),
	(640,480),
	(800,448),
	(960,544),
	(1280,720),
)
		
class ConfigDialog( wx.Dialog ):
	def __init__( self, parent, cameraDeviceNum=0, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, title=_('CrossMgr Camera Configuration') )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.title = wx.StaticText( self, label='CrossMgr Camera Configuration' )
		self.title.SetFont( wx.FontFromPixelSize( wx.Size(0,24), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL ) )
		self.explanation = [
			'Check that the USB Webcam is plugged in.',
			'Check the Camera Device (Usually 0 but could be 1, 2, etc.).',
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
		self.bufferSecs = 10
		
		self.tFrameCount = self.tLaunch = self.tLast = now()
		self.frameCount = 0
		self.frameCountUpdate = self.fps * 2
		self.fpsActual = 0.0
		self.fpt = timedelta(seconds=0)
		
		self.fcb = FrameCircBuf( self.bufferSecs * self.fps )
		
		self.config = wx.Config(appName="CrossMgrCamera",
						vendorName="SmartCyclingSolutions",
						style=wx.CONFIG_USE_LOCAL_FILE)
		
		self.requestQ = Queue()			# Select photos from photobuf.
		self.writerQ = Queue( 400 )		# Selected photos waiting to be written out.
		self.ftpQ = Queue()				# Photos waiting to be ftp'd.
		self.renamerQ = Queue()			# Photos waiting to be renamed and possibly ftp'd.
		self.messageQ = Queue()			# Collection point for all status/failure messages.
		
		self.SetBackgroundColour( wx.Colour(232,232,232) )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.primaryImage = ScaledImage( self, style=wx.BORDER_SUNKEN, size=(imageWidth, imageHeight) )
		self.beforeImage = ScaledImage( self, style=wx.BORDER_SUNKEN, size=(imageWidth, imageHeight) )
		self.afterImage = ScaledImage( self, style=wx.BORDER_SUNKEN, size=(imageWidth, imageHeight) )
		self.beforeAfterImages = [self.beforeImage, self.afterImage]
		
		#------------------------------------------------------------------------------------------------
		headerSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.logo = Utils.GetPngBitmap('CrossMgrHeader.png')
		headerSizer.Add( wx.StaticBitmap(self, bitmap=self.logo) )
		
		self.title = wx.StaticText(self, label='CrossMgr Camera\nVersion {}'.format(AppVerName.split()[1]), style=wx.ALIGN_RIGHT )
		self.title.SetFont( wx.FontFromPixelSize( wx.Size(0,28), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL ) )
		headerSizer.Add( self.title, flag=wx.ALL, border=10 )
		
		#------------------------------------------------------------------------------
		self.cameraDeviceLabel = wx.StaticText(self, label='Camera Device:')
		self.cameraDevice = wx.StaticText( self )
		boldFont = self.cameraDevice.GetFont()
		boldFont.SetWeight( wx.BOLD )
		self.cameraDevice.SetFont( boldFont )
		self.reset = wx.Button( self, label="Reset Camera" )
		self.reset.Bind( wx.EVT_BUTTON, self.resetCamera )
		cameraDeviceSizer = wx.BoxSizer( wx.HORIZONTAL )
		cameraDeviceSizer.Add( self.cameraDeviceLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		cameraDeviceSizer.Add( self.cameraDevice, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		cameraDeviceSizer.Add( self.reset, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )

		#------------------------------------------------------------------------------
		self.targetProcessingTimeLabel = wx.StaticText(self, label='Target Frames:')
		self.targetProcessingTime = wx.StaticText(self, label=u'{:.3f}'.format(self.fps))
		self.targetProcessingTime.SetFont( boldFont )
		self.targetProcessingTimeUnit = wx.StaticText(self, label='per sec')
		
		self.framesPerSecondLabel = wx.StaticText(self, label='Actual Frames:')
		self.framesPerSecond = wx.StaticText(self, label='25.000')
		self.framesPerSecond.SetFont( boldFont )
		self.framesPerSecondUnit = wx.StaticText(self, label='per sec')
		
		self.availableMsPerFrameLabel = wx.StaticText(self, label='Available Time Per Frame:')
		self.availableMsPerFrame = wx.StaticText(self, label=u'{:.0f}'.format(1000.0*self.frameDelay))
		self.availableMsPerFrame.SetFont( boldFont )
		self.availableMsPerFrameUnit = wx.StaticText(self, label='ms')
		
		self.frameProcessingTimeLabel = wx.StaticText(self, label='Actual Frame Processing:')
		self.frameProcessingTime = wx.StaticText(self, label='20')
		self.frameProcessingTime.SetFont( boldFont )
		self.frameProcessingTimeUnit = wx.StaticText(self, label='ms')
		
		pfgs = wx.FlexGridSizer( rows=0, cols=6, vgap=4, hgap=8 )
		fRight = wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT
		fLeft = wx.ALIGN_CENTRE_VERTICAL
		
		#------------------- Row 1 ------------------------------
		pfgs.Add( self.targetProcessingTimeLabel, flag=fRight )
		pfgs.Add( self.targetProcessingTime, flag=fRight )
		pfgs.Add( self.targetProcessingTimeUnit, flag=fLeft )
		pfgs.Add( self.availableMsPerFrameLabel, flag=fRight )
		pfgs.Add( self.availableMsPerFrame, flag=fRight )
		pfgs.Add( self.availableMsPerFrameUnit, flag=fLeft )
		
		#------------------- Row 2 ------------------------------
		pfgs.Add( self.framesPerSecondLabel, flag=fRight )
		pfgs.Add( self.framesPerSecond, flag=fRight )
		pfgs.Add( self.framesPerSecondUnit, flag=fLeft )
		pfgs.Add( self.frameProcessingTimeLabel, flag=fRight )
		pfgs.Add( self.frameProcessingTime, flag=fRight )
		pfgs.Add( self.frameProcessingTimeUnit, flag=fLeft )

		statsSizer = wx.BoxSizer( wx.VERTICAL )
		statsSizer.Add( cameraDeviceSizer )
		statsSizer.Add( pfgs, flag=wx.TOP, border=8 )
		headerSizer.Add( statsSizer, flag=wx.ALL, border=4 )
		mainSizer.Add( headerSizer )
		
		self.messagesText = wx.TextCtrl( self, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(350,imageHeight) )
		self.messageManager = MessageManager( self.messagesText )
		
		border = 2
		row1Sizer = wx.BoxSizer( wx.HORIZONTAL )
		row1Sizer.Add( self.primaryImage, flag=wx.ALL, border=border )
		row1Sizer.Add( self.messagesText, 1, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=border )
		mainSizer.Add( row1Sizer, 1, flag=wx.EXPAND )
		
		row2Sizer = wx.BoxSizer( wx.HORIZONTAL )
		row2Sizer.Add( self.beforeImage, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=border )
		row2Sizer.Add( self.afterImage, flag=wx.RIGHT|wx.BOTTOM, border=border )
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
		
		for i in [self.primaryImage, self.beforeImage, self.afterImage]:
			i.SetTestImage()
		
		# Start the frame loop.
		delayAdjustment = 0.80 if 'win' in sys.platform else 0.98
		ms = int(1000 * self.frameDelay * delayAdjustment)
		self.timer.Start( ms, False )
		
	def Start( self ):
		self.messageQ.put( ('', '************************************************') )
		self.messageQ.put( ('started', now().strftime('%Y/%m/%d %H:%M:%S')) )
		self.startThreads()
		self.startCamera()
		
	def showMessages( self ):
		while 1:
			message = self.messageQ.get()
			assert len(message) == 2, 'Incorrect message length'
			cmd, info = message
			wx.CallAfter( self.messageManager.write, '{}:  {}'.format(cmd, info) if cmd else info )
		
	def startCamera( self ):
		self.camera = None
		try:
			self.camera = Device( max(self.getCameraDeviceNum(), 0) )
		except Exception as e:
			self.messageQ.put( ('camera', 'Error: {}'.format(e)) )
			return False
		
		#self.camera.set_resolution( 640, 480 )
		self.messageQ.put( ('camera', 'Successfully Connected: Device: {}'.format(self.getCameraDeviceNum()) ) )
		for i in self.beforeAfterImages:
			i.SetTestImage()
		return True
	
	def startThreads( self ):
		self.grabFrameOK = False
		
		self.listenerThread = SocketListener( self.requestQ, self.messageQ )
		error = self.listenerThread.test()
		if error:
			wx.MessageBox('Socket Error:\n\n{}\n\nIs another CrossMgrVideo or CrossMgrCamera running on this computer?'.format(error),
				"Socket Error",
				wx.OK | wx.ICON_ERROR
			)
			wx.Exit()
				
		self.writerThread = threading.Thread( target=PhotoWriter, args=(self.writerQ, self.messageQ, self.ftpQ) )
		self.writerThread.daemon = True
		
		self.renamerThread = threading.Thread( target=PhotoRenamer, args=(self.renamerQ, self.writerQ, self.messageQ) )
		self.renamerThread.daemon = True
		
		self.ftpThread = threading.Thread( target=FTPWriter, args=(self.ftpQ, self.messageQ) )
		self.ftpThread.daemon = True
		
		self.fcb = FrameCircBuf( int(self.bufferSecs * self.fps) )
		
		self.listenerThread.start()
		self.writerThread.start()
		self.renamerThread.start()
		self.ftpThread.start()
		
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
		self.fcb.append( tNow, image )
		wx.CallAfter( self.primaryImage.SetImage, image )
		
		# Process any save messages
		while 1:
			try:
				message = self.requestQ.get(False)
			except Empty:
				break
			
			tSearch = message['time']
			advanceSeconds = message.get('advanceSeconds', 0.0)
			if advanceSeconds:
				tSearch += timedelta(seconds=advanceSeconds)
			times, frames = self.fcb.findBeforeAfter( tSearch, 1, 1 )
			if not frames:
				self.messageQ.put( ('error', 'No photos for {} at {}'.format(message.get('bib', None), message['time'].isoformat()) ) )
				
			lastImage = None
			for i, f in enumerate(frames):
				
				fname = GetPhotoFName( message['dirName'], message.get('bib',None), message.get('raceSeconds',None), i, times[i] )
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
				
				#if lastImage is not None and image.GetData() == lastImage.GetData():
				#	self.messageQ.put( ('duplicate', '"{}"'.format(os.path.basename(fname))) )
				#	continue
				
				wx.CallAfter( self.beforeAfterImages[i].SetImage, image )
				
				SaveImage( fname, image, message.get('ftpInfo', None), self.messageQ, self.writerQ )
				lastImage = image
				
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
	
	def resetCamera( self, event ):
		self.writeOptions()
		
		dlg = ConfigDialog( self, self.getCameraDeviceNum() )
		ret = dlg.ShowModal()
		cameraDeviceNum = dlg.GetCameraDeviceNum()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return
		
		self.setCameraDeviceNum( cameraDeviceNum )
		self.grabFrameOK = self.startCamera()
		
	def setCameraDeviceNum( self, num ):
		self.cameraDevice.SetLabel( unicode(num) )
		
	def getCameraDeviceNum( self ):
		return int(self.cameraDevice.GetLabel())
		
	def onCloseWindow( self, event ):
		self.shutdown()
		wx.Exit()
		
	def writeOptions( self ):
		self.config.Write( 'CameraDevice', self.cameraDevice.GetLabel() )
		self.config.Flush()
	
	def readOptions( self ):
		self.cameraDevice.SetLabel( self.config.Read('CameraDevice', u'0') )

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
	global mainWin, redirectFileName, imageWidth, imageHeight
	
	app = wx.App(False)
	app.SetAppName("CrossMgrCamera")

	displayWidth, displayHeight = wx.GetDisplaySize()
	if imageWidth*2 + 32 > displayWidth or imageHeight*2 + 32 > displayHeight:
		imageWidth /= 2
		imageHeight /= 2

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
		icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'CrossMgrCamera.ico'), wx.BITMAP_TYPE_ICO )
		mainWin.SetIcon( icon )
	except:
		pass

	mainWin.Refresh()
	dlg = ConfigDialog( mainWin, mainWin.getCameraDeviceNum() )
	ret = dlg.ShowModal()
	cameraDeviceNum = dlg.GetCameraDeviceNum()
	dlg.Destroy()
	if ret != wx.ID_OK:
		return
		
	mainWin.setCameraDeviceNum( cameraDeviceNum )
	
	# Start processing events.
	mainWin.Start()
	app.MainLoop()

@atexit.register
def shutdown():
	if mainWin:
		mainWin.shutdown()
	
if __name__ == '__main__':
	MainLoop()
	
