import wx
import wx.lib.mixins.listctrl as listmix
import sys
import os
import re
import time
import math
from datetime import datetime, timedelta

HOST = 'localhost'
PORT = 54111

now = datetime.now

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
from Database import Database, DBWriter
from FrameCircBuf import FrameCircBuf
from AddPhotoHeader import PilImageToWxImage
from ScaledImage import ScaledImage
from FinishStrip import FinishStripPanel

imageWidth, imageHeight = 640, 480

tdCaptureBefore = timedelta(seconds=1.0)
tdCaptureAfter = timedelta(seconds=3.0)

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
			self.yLast = 0
			
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
			draw.rectangle( ((0, 0), (imageWidth-1, imageHeight-1)), outline=(255,255,0) )
			
			s = imageHeight // 10
			self.yLast += 4
			if not self.yLast <= imageHeight-s:
				self.yLast = 0
			x = 0
			draw.rectangle( ((x, self.yLast), (imageWidth, self.yLast+s)), fill=(128,128,128) )
			
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
		wx.Dialog.__init__( self, parent, id, title=_('CrossMgr Video Configuration') )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.title = wx.StaticText( self, label='CrossMgr Video Configuration' )
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
	
class AutoWidthListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID = wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

class MainWin( wx.Frame, listmix.ColumnSorterMixin ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(1000,800) ):
		wx.Frame.__init__(self, parent, id, title, size=size)
		
		self.db = Database()
		
		self.fps = 25
		self.frameDelay = 1.0 / self.fps
		self.bufferSecs = 10
		
		self.tFrameCount = self.tLaunch = self.tLast = now()
		self.frameCount = 0
		self.frameCountUpdate = self.fps * 2
		self.fpsActual = 0.0
		self.fpt = timedelta(seconds=0)
		
		self.captureTimer = wx.CallLater( 10, self.stopCapture )
		
		self.fcb = FrameCircBuf( self.bufferSecs * self.fps )
		
		self.config = wx.Config(appName="CrossMgrCamera",
						vendorName="SmartCyclingSolutions",
						style=wx.CONFIG_USE_LOCAL_FILE)
		
		self.requestQ = Queue()		# Select photos from photobuf.
		self.dbQ = Queue()			# Photos waiting to be renamed and possibly ftp'd.
		self.messageQ = Queue()		# Collection point for all status/failure messages.
		
		self.SetBackgroundColour( wx.Colour(232,232,232) )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		#------------------------------------------------------------------------------------------------
		headerSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.logo = Utils.GetPngBitmap('CrossMgrHeader.png')
		headerSizer.Add( wx.StaticBitmap(self, bitmap=self.logo) )
		
		self.title = wx.StaticText(self, label='CrossMgr Video\nVersion {}'.format(AppVerName.split()[1]), style=wx.ALIGN_RIGHT )
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
		
		self.test = wx.Button( self, label="Test" )
		self.test.Bind( wx.EVT_BUTTON, self.testEvent )
		
		cameraDeviceSizer = wx.BoxSizer( wx.HORIZONTAL )
		cameraDeviceSizer.Add( self.cameraDeviceLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		cameraDeviceSizer.Add( self.cameraDevice, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		cameraDeviceSizer.Add( self.reset, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		cameraDeviceSizer.Add( self.test, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )

		#------------------------------------------------------------------------------
		self.targetProcessingTimeLabel = wx.StaticText(self, label='Target Frames:')
		self.targetProcessingTime = wx.StaticText(self, label=u'{:.3f}'.format(self.fps))
		self.targetProcessingTime.SetFont( boldFont )
		self.targetProcessingTimeUnit = wx.StaticText(self, label='/ sec')
		
		self.framesPerSecondLabel = wx.StaticText(self, label='Actual Frames:')
		self.framesPerSecond = wx.StaticText(self, label='25.000')
		self.framesPerSecond.SetFont( boldFont )
		self.framesPerSecondUnit = wx.StaticText(self, label='/ sec')
		
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
		
		#------------------------------------------------------------------------------------------------
		self.finishStrip = FinishStripPanel( self, size=(-1,wx.GetDisplaySize()[1]/2) )
		
		self.primaryImage = ScaledImage( self, style=wx.BORDER_SUNKEN, size=(imageWidth, imageHeight) )
		self.primaryImage.SetTestImage()
		
		self.eventList = AutoWidthListCtrl( self, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_SORT_ASCENDING )
		
		self.il = wx.ImageList(16, 16)
		self.sm_rt = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallRightArrow.png'), wx.BITMAP_TYPE_PNG))
		self.sm_close = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallUpArrow.png'), wx.BITMAP_TYPE_PNG ))
		self.sm_up = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallUpArrow.png'), wx.BITMAP_TYPE_PNG))
		self.sm_dn = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallDownArrow.png'), wx.BITMAP_TYPE_PNG ))
		self.eventList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		headers = ['Time', 'Bib', 'Name', 'Team', 'Category']
		for i, h in enumerate(headers):
			self.eventList.InsertColumn(i, h, wx.LIST_FORMAT_RIGHT if h == 'Bib' else wx.LIST_FORMAT_LEFT)
		listmix.ColumnSorterMixin.__init__( self, len(headers) )
		self.itemDataMap = {}
		
		self.eventList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.onEventSelected )
		
		self.messagesText = wx.TextCtrl( self, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(250,-1) )
		self.messageManager = MessageManager( self.messagesText )
		
		#------------------------------------------------------------------------------------------------
		mainSizer.Add( self.finishStrip, flag=wx.EXPAND )
		
		border = 2
		row1Sizer = wx.BoxSizer( wx.HORIZONTAL )
		row1Sizer.Add( self.primaryImage, flag=wx.ALL, border=border )
		row1Sizer.Add( self.eventList, 1, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=border )
		row1Sizer.Add( self.messagesText, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=border )
		mainSizer.Add( row1Sizer, 1, flag=wx.EXPAND )
		
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
		self.tsMax = None
		
		# Start the frame loop.
		delayAdjustment = 0.80 if 'win' in sys.platform else 0.98
		ms = int(1000 * self.frameDelay * delayAdjustment)
		self.timer.Start( ms, False )
		
		wx.CallLater( 300, self.refreshEvents )
	
	def GetListCtrl( self ):
		return self.eventList
	
	def GetSortImages(self):
		return (self.sm_dn, self.sm_up)
	
	def refreshEvents( self, replace=False ):
		tNow = now()
		self.lastEventRefresh = tNow
		
		if replace:
			tsLower = datetime(tNow.year, tNow.month, tNow.day)
			tsUpper = tsLower + timedelta(days=1)
			self.eventList.DeleteAllItems()
			self.itemDataMap = {}
			self.tsMax = None
		else:
			tsLower = (self.tsMax or datetime(tNow.year, tNow.month, tNow.day)) + timedelta(seconds=0.00001)
			tsUpper = tsLower + timedelta(days=1)

		events = self.db.getEvents( tsLower, tsUpper )
		if not events:
			return
			
		tsPrev = (self.tsMax or datetime(2000,1,1))
		self.tsMax = events[-1][0]
		
		for i, (ts,bib,first_name,last_name,team,category,race_name) in enumerate(events):
			closeFinish = ((ts-tsPrev).total_seconds() < 0.3)
			row = self.eventList.InsertImageStringItem( sys.maxint, ts.strftime('%H:%M:%S.%f')[:-3], self.sm_close if closeFinish else self.sm_rt )
			self.eventList.SetStringItem( row, 1, unicode(bib) )
			name = u', '.join( n for n in (last_name, first_name) if n )
			self.eventList.SetStringItem( row, 2, name )
			self.eventList.SetStringItem( row, 3, team )
			self.eventList.SetStringItem( row, 4, category )
			
			self.eventList.SetItemData( row, row )
			self.itemDataMap[row] = (ts,bib,name,team,category)
			tsPrev = ts
			
		for i in xrange(5):
			self.eventList.SetColumnWidth(i, wx.LIST_AUTOSIZE)

		self.eventList.EnsureVisible( self.eventList.GetItemCount() - 1 )

	def Start( self ):
		self.messageQ.put( ('', '************************************************') )
		self.messageQ.put( ('started', now().strftime('%Y/%m/%d %H:%M:%S')) )
		self.startSocket()
		self.startThreads()
		self.startCamera()

	def testEvent( self, event ):
		self.testCount = getattr(self, 'testCount', 0) + 1
		self.requestQ.put( {
				'time':now(),
				'bib':self.testCount,
				'firstName':u'Test',
				'lastName':u'Test',
				'team':u'Test',
				'wave':u'Test',
				'raceName':u'Test',				
			}
		)
		wx.CallLater( 500, self.dbQ.put, ('flush',) )
		wx.CallLater( 1000, self.refreshEvents )
		wx.CallLater( 1500, lambda: self.eventList.Select(self.eventList.GetItemCount()-1) )
		
	def onEventSelected( self, event ):
		item = event.m_itemIndex
		data = self.eventList.GetItemData( item )
		ts = self.itemDataMap[data][0]
		self.finishStrip.SetTsJpgs( self.db.getPhotos(ts-tdCaptureAfter, ts+tdCaptureBefore), ts )
		
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
			self.camera = Device( max(self.getCameraDeviceNum(), 0) )
		except Exception as e:
			self.messageQ.put( ('camera', 'Error: {}'.format(e)) )
			return False
		
		#self.camera.set_resolution( 640, 480 )
		self.messageQ.put( ('camera', 'Successfully Connected: Device: {}'.format(self.getCameraDeviceNum()) ) )
		return True
	
	def startThreads( self ):
		self.grabFrameOK = False
		
		self.listenerThread = threading.Thread( target=SocketListener, args=(self.listenerSocket, self.requestQ, self.messageQ) )
		self.listenerThread.daemon = True
		
		self.dbThread = threading.Thread( target=DBWriter, args=(self.dbQ,) )
		self.dbThread.daemon = True
		
		self.fcb = FrameCircBuf( int(self.bufferSecs * self.fps) )
		
		self.listenerThread.start()
		self.dbThread.start()
		
		self.grabFrameOK = True
		self.messageQ.put( ('threads', 'Successfully Launched') )
		return True
	
	def stopCapture( self ):
		pass
	
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
		
		image = PilImageToWxImage( image )
		self.fcb.append( tNow, image )
		if self.frameCount & 1:
			wx.CallAfter( self.primaryImage.SetImage, image )
		
		# Record images as long as the timer is running.
		if self.captureTimer.IsRunning():
			self.dbQ.put( ('photo', tNow, image) )
			
		if (tNow - self.lastEventRefresh).total_seconds() > 5.0:
			self.refreshEvents()
			self.lastEventRefresh = tNow
			return
		
		# Process any event messages
		while 1:
			try:
				message = self.requestQ.get(False)
			except Empty:
				break
			
			tSearch = message['time']
			advanceSeconds = message.get('advanceSeconds', 0.0)
			if advanceSeconds:
				tSearch += timedelta(seconds=advanceSeconds)
			
			# Record this event.
			self.dbQ.put( (
				'event',
				tSearch,
				message.get('bib', 99999),
				message.get('firstName',u''),
				message.get('lastName',u''),
				message.get('team',u''),
				message.get('wave',u''),
				message.get('raceName',u'')
			) )

			# If we are not currently capturing, make sure we record past frames.
			if not self.captureTimer.IsRunning():
				times, frames = self.fcb.getBackFrames( tSearch - tdCaptureBefore )
				for t, f in zip(times, frames):
					if f:
						self.dbQ.put( ('photo', t, f) )
			else:
				self.captureTimer.Stop()
			
			# Set a timer to stop recording after the capture window.
			millis = int((tSearch + tdCaptureAfter - now()).total_seconds() * 1000.0)
			if millis > 0:
				self.captureTimer.Start( millis )
			
			if (now() - tNow).total_seconds() > self.frameDelay / 2.0:
				break
				
		self.fpt = now() - tNow
		self.tLast = tNow
	
	def shutdown( self ):
		# Ensure that all images in the queue are saved.
		self.grabFrameOK = False
		if hasattr(self, 'dbThread'):
			self.dbQ.put( ('terminate', ) )
			self.dbThread.join()
	
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
	app.SetAppName("CrossMgrVideo")

	displayWidth, displayHeight = wx.GetDisplaySize()
	if imageWidth*2 + 32 > displayWidth or imageHeight*2 + 32 > displayHeight:
		imageWidth /= 2
		imageHeight /= 2

	mainWin = MainWin( None, title=AppVerName, size=(1600,864) )
	
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
	
