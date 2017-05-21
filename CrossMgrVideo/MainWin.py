import wx
import wx.lib.mixins.listctrl as listmix
import wx.lib.intctrl
import sys
import os
import re
import time
import math
import threading
import socket
import atexit
import time
import platform
import cStringIO as StringIO
from Queue import Queue, Empty, Full

from datetime import datetime, timedelta

now = datetime.now

import Utils
from SocketListener import SocketListener
from Database import Database, DBWriter, DBReader
from FrameCircBuf import FrameCircBuf
from AddPhotoHeader import PilImageToWxImage
from ScaledImage import ScaledImage
from FinishStrip import FinishStripPanel
from ManageDatabase import ManageDatabase
from PhotoDialog import PhotoDialog

imageWidth, imageHeight = 640, 480

tdCaptureBefore = timedelta(seconds=0.5)
tdCaptureAfter = timedelta(seconds=3.5)

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

cameraResolutionChoices = (
	'640x480',
	'1280x720',
	'1280x1024',
	'1920x1080',
	'1600x1200',
)

def getCameraResolutionChoice( resolution ):
	res = '{}x{}'.format( *resolution )
	for i, c in enumerate(cameraResolutionChoices):
		if c == res:
			return i
	return 0
		
class ConfigDialog( wx.Dialog ):
	def __init__( self, parent, cameraDeviceNum=0, cameraResolution = (imageWidth,imageHeight), id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, title=_('CrossMgr Video Configuration') )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.title = wx.StaticText( self, label='CrossMgr Video Configuration' )
		self.title.SetFont( wx.FontFromPixelSize( wx.Size(0,24), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL ) )
		self.explanation = [
			'Check that the USB Webcam is plugged in.',
			'Check the Camera Device (Usually 0 but could be 1, 2, etc.).',
		]
		pfgs = wx.FlexGridSizer( rows=0, cols=2, vgap=4, hgap=8 )
		
		pfgs.Add( wx.StaticText(self, label='Camera Device'+':'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.cameraDevice = wx.Choice( self, choices=[unicode(i) for i in xrange(8)] )
		self.cameraDevice.SetSelection( cameraDeviceNum )
		pfgs.Add( self.cameraDevice )
		
		pfgs.Add( wx.StaticText(self, label='Camera Resolution'+':'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.cameraResolution = wx.Choice( self, choices=cameraResolutionChoices )
		self.cameraResolution.SetSelection( getCameraResolutionChoice(cameraResolution) )
		pfgs.Add( self.cameraResolution )
		
		pfgs.AddSpacer( 1 )
		pfgs.Add( wx.StaticText(self, label='Your camera may not support all resolutions.\nYour Camera may not support the required frame rate at high resolutions.\nCheck your Camera specs for details.'), flag=wx.RIGHT, border=4 )
		
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
		
	def GetCameraResolution( self ):
		return tuple(int(v) for v in cameraResolutionChoices[self.cameraResolution.GetSelection()].split('x'))

	def onOK( self, event ):
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
		
class FocusDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, title=_('CrossMgr Video Focus') )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.image = ScaledImage( self )
		self.image.Bind( wx.EVT_LEFT_UP, self.onOK )
		sizer.Add( self.image, 1, wx.EXPAND )
		self.SetSizerAndFit( sizer )
	
	def onOK( self, event ):
		self.EndModal( wx.ID_OK )		
	
	def SetImage( self, image ):
		sz = image.GetSize()
		if self.GetSize() != sz:
			self.SetSize( sz )
			self.SetTitle( u'{} {}x{}'.format( _('CrossMgr Video Focus'), *sz ) )
		return self.image.SetImage( image )

class AutoWidthListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID = wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

class MainWin( wx.Frame ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(1000,800) ):
		wx.Frame.__init__(self, parent, id, title, size=size)
		
		self.db = Database()
		
		self.fps = 25
		self.frameDelay = 1.0 / self.fps
		self.bufferSecs = 10
		self.xFinish = None
		
		self.tFrameCount = self.tLaunch = self.tLast = now()
		self.frameCount = 0
		self.frameCountUpdate = int(self.fps * 2)
		self.fpsActual = 0.0
		self.fpt = timedelta(seconds=0)
		self.iTriggerSelect = None
		self.triggerInfo = None
		
		self.captureTimer = wx.CallLater( 10, self.stopCapture )
		
		self.fcb = FrameCircBuf( self.bufferSecs * self.fps )
		
		self.config = wx.Config(appName="CrossMgrVideo",
						vendorName="SmartCyclingSolutions",
						style=wx.CONFIG_USE_LOCAL_FILE)
		
		self.requestQ = Queue()		# Select photos from photobuf.
		self.dbWriterQ = Queue()	# Photos waiting to be written
		self.dbReaderQ = Queue()	# Photos read as requested from user.
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
		self.cameraResolution = wx.StaticText( self )
		self.cameraResolution.SetFont( boldFont )
		self.reset = wx.Button( self, label="Reset Camera" )
		self.reset.Bind( wx.EVT_BUTTON, self.resetCamera )
		
		self.manage = wx.Button( self, label="Manage Database" )
		self.manage.Bind( wx.EVT_BUTTON, self.manageDatabase )
		
		self.test = wx.Button( self, label="Test" )
		self.test.Bind( wx.EVT_BUTTON, self.onTest )
		
		self.focus = wx.Button( self, label="Focus..." )
		self.focus.Bind( wx.EVT_BUTTON, self.onFocus )
		
		cameraDeviceSizer = wx.BoxSizer( wx.HORIZONTAL )
		cameraDeviceSizer.Add( self.cameraDeviceLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		cameraDeviceSizer.Add( self.cameraDevice, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		cameraDeviceSizer.Add( self.cameraResolution, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		cameraDeviceSizer.Add( self.reset, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=32 )
		cameraDeviceSizer.Add( self.manage, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )
		cameraDeviceSizer.Add( self.test, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )
		cameraDeviceSizer.Add( self.focus, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )

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
		
		self.frameProcessingTimeLabel = wx.StaticText(self, label='Frame Processing Time:')
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
		self.finishStrip = FinishStripPanel( self, size=(-1,wx.GetDisplaySize()[1]//2) )
		self.finishStrip.finish.Bind( wx.EVT_RIGHT_DOWN, self.onRightClick )
		
		self.primaryImage = ScaledImage( self, style=wx.BORDER_SUNKEN, size=(imageWidth, imageHeight) )
		self.primaryImage.SetTestImage()
		
		self.focusDialog = FocusDialog( self )
		
		hsDate = wx.BoxSizer( wx.HORIZONTAL )
		hsDate.Add( wx.StaticText(self, label='Show Triggers for'), flag=wx.ALIGN_CENTER_VERTICAL )
		tQuery = now()
		self.date = wx.DatePickerCtrl(
			self,
			dt=wx.DateTimeFromDMY( tQuery.day, tQuery.month-1, tQuery.year ),
			style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY
		)
		self.date.Bind( wx.EVT_DATE_CHANGED, self.onQueryDateChanged )
		hsDate.Add( self.date, flag=wx.LEFT, border=2 )
		
		hsDate.Add( wx.StaticText(self, label='Filter by Bib'), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=12 )
		self.bib = wx.lib.intctrl.IntCtrl( self, style=wx.TE_PROCESS_ENTER, size=(64,-1), min=1, allow_none=True, value=None )
		self.bib.Bind( wx.EVT_TEXT_ENTER, self.onQueryBibChanged )
		hsDate.Add( self.bib, flag=wx.LEFT, border=2 )
		
		self.tsQueryLower = datetime(tQuery.year, tQuery.month, tQuery.day)
		self.tsQueryUpper = self.tsQueryLower + timedelta(days=1)
		self.bibQuery = None
		
		self.triggerList = AutoWidthListCtrl( self, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_SORT_ASCENDING )
		
		self.il = wx.ImageList(16, 16)
		self.sm_check = self.il.Add( Utils.GetPngBitmap('check_icon.png'))
		self.sm_close = self.il.Add( Utils.GetPngBitmap('flame_icon.png'))
		self.sm_up = self.il.Add( Utils.GetPngBitmap('SmallUpArrow.png'))
		self.sm_dn = self.il.Add( Utils.GetPngBitmap('SmallDownArrow.png'))
		self.triggerList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		headers = ['Time', 'Bib', 'Name', 'Team', 'Wave', 'km/h', 'mph']
		for i, h in enumerate(headers):
			self.triggerList.InsertColumn(
				i, h,
				wx.LIST_FORMAT_RIGHT if h in ('Bib','km/h','mph') else wx.LIST_FORMAT_LEFT
			)
		self.itemDataMap = {}
		
		self.triggerList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.onTriggerSelected )
		
		self.messagesText = wx.TextCtrl( self, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(250,-1) )
		self.messageManager = MessageManager( self.messagesText )
		
		vsTriggers = wx.BoxSizer( wx.VERTICAL )
		vsTriggers.Add( hsDate )
		vsTriggers.Add( self.triggerList, 1, flag=wx.EXPAND|wx.TOP, border=2)
		
		#------------------------------------------------------------------------------------------------
		mainSizer.Add( self.finishStrip, 1, flag=wx.EXPAND )
		
		border = 2
		row1Sizer = wx.BoxSizer( wx.HORIZONTAL )
		row1Sizer.Add( self.primaryImage, flag=wx.ALL, border=border )
		row1Sizer.Add( vsTriggers, 1, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=border )
		row1Sizer.Add( self.messagesText, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=border )
		mainSizer.Add( row1Sizer, flag=wx.EXPAND )
		
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
		
		wx.CallLater( 300, self.refreshTriggers )
	
	def onQueryDateChanged( self, event ):
		v = self.date.GetValue()
		self.tsQueryLower = datetime( v.GetYear(), v.GetMonth() + 1, v.GetDay() )
		self.tsQueryUpper = self.tsQueryLower + timedelta( days=1 )
		self.refreshTriggers( True )
	
	def onQueryBibChanged( self, event ):
		self.bibQuery = self.bib.GetValue()
		self.refreshTriggers( True )
	
	def GetListCtrl( self ):
		return self.triggerList
	
	def GetSortImages(self):
		return (self.sm_dn, self.sm_up)
	
	def getItemData( self, i ):
		data = self.triggerList.GetItemData( i )
		return self.itemDataMap[data]
	
	def refreshTriggers( self, replace=False ):
		tNow = now()
		self.lastTriggerRefresh = tNow
		
		if replace:
			tsLower = self.tsQueryLower
			tsUpper = self.tsQueryUpper
			self.triggerList.DeleteAllItems()
			self.itemDataMap = {}
			self.tsMax = None
			self.iTriggerSelect = None
			self.triggerInfo = {}
		else:
			tsLower = (self.tsMax or datetime(tNow.year, tNow.month, tNow.day)) + timedelta(seconds=0.00001)
			tsUpper = tsLower + timedelta(days=1)

		triggers = self.db.getTriggers( tsLower, tsUpper, self.bibQuery )
		if not triggers:
			return
			
		tsPrev = (self.tsMax or datetime(2000,1,1))
		self.tsMax = triggers[-1][1] # id,ts,bib,first_name,last_name,team,wave,race_name,kmh
		
		for i, (id,ts,bib,first_name,last_name,team,wave,race_name,kmh) in enumerate(triggers):
			closeFinish = ((ts-tsPrev).total_seconds() < 0.3)
			row = self.triggerList.InsertImageStringItem( sys.maxint, ts.strftime('%H:%M:%S.%f')[:-3], self.sm_close if closeFinish else self.sm_check )
			if closeFinish and row > 0:
				self.triggerList.SetItemImage( row-1, self.sm_close )
			self.triggerList.SetStringItem( row, 1, u'{:>6}'.format(bib) )
			name = u', '.join( n for n in (last_name, first_name) if n )
			self.triggerList.SetStringItem( row, 2, name )
			self.triggerList.SetStringItem( row, 3, team )
			self.triggerList.SetStringItem( row, 4, wave )
			if kmh:
				mph = kmh * 0.621371
				kmh = u'{:.2f}'.format(kmh)
				mph = u'{:.2f}'.format(mph)
			else:
				kmh = mph = u''
			self.triggerList.SetStringItem( row, 5, kmh )
			self.triggerList.SetStringItem( row, 6, mph )
			
			self.triggerList.SetItemData( row, row )
			self.itemDataMap[row] = (id,ts,bib,name,team,wave,race_name,first_name,last_name,kmh)
			tsPrev = ts
			
		for i in xrange(5):
			self.triggerList.SetColumnWidth(i, wx.LIST_AUTOSIZE)

		self.triggerList.EnsureVisible( self.triggerList.GetItemCount() - 1 )

	def Start( self ):
		self.messageQ.put( ('', '************************************************') )
		self.messageQ.put( ('started', now().strftime('%Y/%m/%d %H:%M:%S')) )
		self.startThreads()
		self.startCamera()

	def onTest( self, event ):
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
		wx.CallLater( 500, self.dbWriterQ.put, ('flush',) )
		wx.CallLater( int(100+1000*int(tdCaptureBefore.total_seconds())), self.refreshTriggers )
	
	def onFocus( self, event ):
		self.focusDialog.Move((4,4))
		self.focusDialog.ShowModal()
	
	def onRightClick( self, event ):
		if not self.triggerInfo:
			return
		self.xFinish = event.GetX()
		pd = PhotoDialog( self, self.finishStrip.finish.getJpg(self.xFinish), self.triggerInfo, self.finishStrip.GetTsJpgs(), self.fps )
		pd.ShowModal()
		if pd.kmh:
			self.database.updateTriggerKMH( self.triggerInfo['id'], pd.kmh or 0.0 )
		pd.Destroy()

	def setFinishStripJpgs( self, jpgs ):
		self.tsJpg = jpgs
		wx.CallAfter( self.finishStrip.SetTsJpgs, self.tsJpg, self.ts, self.triggerInfo )

	def onTriggerSelected( self, event ):
		self.iTriggerSelect = event.m_itemIndex
		data = self.itemDataMap[self.triggerList.GetItemData(self.iTriggerSelect)]
		self.triggerInfo = {
			a:data[i] for i, a in enumerate(('id','ts','bib','name','team','wave','raceName','firstName','lastName','kmh'))
		}
		self.ts = self.triggerInfo['ts']
		self.dbReaderQ.put( ('getphotos', self.ts-tdCaptureBefore, self.ts+tdCaptureAfter) )
		
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
		
		try:
			self.camera.set_resolution( *self.getCameraResolution() )
			self.messageQ.put( ('camera', '{}x{} Supported'.format(*self.getCameraResolution())) )
		except Exception as e:
			self.messageQ.put( ('camera', '{}x{} Unsupported Resolution'.format(*self.getCameraResolution())) )
			
		self.messageQ.put( ('camera', 'Successfully Connected: Device: {}'.format(self.getCameraDeviceNum()) ) )
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
		
		self.dbWriterThread = threading.Thread( target=DBWriter, args=(self.dbWriterQ,) )
		self.dbWriterThread.daemon = True
		
		self.dbReaderThread = threading.Thread( target=DBReader, args=(self.dbReaderQ, self.setFinishStripJpgs) )
		self.dbReaderThread.daemon = True
		
		self.fcb = FrameCircBuf( int(self.bufferSecs * self.fps) )
		
		self.listenerThread.start()
		self.dbWriterThread.start()
		self.dbReaderThread.start()
		
		self.grabFrameOK = True
		self.messageQ.put( ('threads', 'Successfully Launched') )
		return True
	
	def stopCapture( self ):
		self.dbWriterQ.put( ('flush',) )
	
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
		
		# Add the image to the circular buffer.
		self.fcb.append( tNow, image )
		
		# Update the monitor screen.
		if self.frameCount & 3 == 0:
			wx.CallAfter( self.primaryImage.SetImage, image )
		if self.focusDialog.IsShown():
			wx.CallAfter( self.focusDialog.SetImage, image )
		
		# Record images if the timer is running.
		if self.captureTimer.IsRunning():
			self.dbWriterQ.put( ('photo', tNow, image) )
		
		# Periodically update events.
		if (tNow - self.lastTriggerRefresh).total_seconds() > 5.0:
			self.refreshTriggers()
			self.lastTriggerRefresh = tNow
			return
		
		# Process event messages
		while 1:
			try:
				message = self.requestQ.get(False)
			except Empty:
				break
			
			tSearch = message['time']
			advanceSeconds = message.get('advanceSeconds', 0.0)
			tSearch += timedelta(seconds=advanceSeconds)
			
			# Record this trigger.
			self.dbWriterQ.put( (
				'trigger',
				tSearch - timedelta(seconds=advanceSeconds),
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
						self.dbWriterQ.put( ('photo', t, f) )
			else:
				self.captureTimer.Stop()
			
			# Set a timer to stop recording after the capture window.
			millis = int((tSearch - now() + tdCaptureAfter).total_seconds() * 1000.0)
			if millis > 0:
				self.captureTimer.Start( millis )
			
			if (now() - tNow).total_seconds() > self.frameDelay / 2.0:
				break
				
		self.fpt = now() - tNow
		self.tLast = tNow
	
	def shutdown( self ):
		# Ensure that all images in the queue are saved.
		self.grabFrameOK = False
		if hasattr(self, 'dbWriterThread'):
			self.dbWriterQ.put( ('terminate', ) )
			self.dbWriterThread.join()
			self.dbReaderQ.put( ('terminate', ) )
			self.dbReaderThread.join()
	
	def resetCamera( self, event=None ):
		dlg = ConfigDialog( self, self.getCameraDeviceNum(), self.getCameraResolution() )
		ret = dlg.ShowModal()
		cameraDeviceNum = dlg.GetCameraDeviceNum()
		cameraResolution = dlg.GetCameraResolution()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return False
		
		self.setCameraDeviceNum( cameraDeviceNum )
		self.setCameraResolution( *cameraResolution )
		self.writeOptions()

		self.grabFrameOK = self.startCamera()
		return True
	
	def manageDatabase( self, event ):
		dlg = ManageDatabase( self, self.db.getsize(), self.db.fname, title='Manage Database' )
		if dlg.ShowModal() == wx.ID_OK:
			tsLower, tsUpper = dlg.GetDates()
			self.db.cleanBetween( tsLower, tsUpper )
			wx.CallAfter( self.finishStrip.Clear )
			wx.CallAfter( self.refreshTriggers, True )
		dlg.Destroy()
	
	def setCameraDeviceNum( self, num ):
		self.cameraDevice.SetLabel( unicode(num) )
		
	def setCameraResolution( self, width, height ):
		self.cameraResolution.SetLabel( u'{}x{}'.format(width, height) )
			
	def getCameraDeviceNum( self ):
		return int(self.cameraDevice.GetLabel())
		
	def getCameraResolution( self ):
		try:
			resolution = [int(v) for v in self.cameraResolution.GetLabel().split('x')]
			return resolution[0], resolution[1]
		except:
			return 640, 400
		
	def onCloseWindow( self, event ):
		self.shutdown()
		wx.Exit()
		
	def writeOptions( self ):
		self.config.Write( 'CameraDevice', self.cameraDevice.GetLabel() )
		self.config.Write( 'CameraResolution', self.cameraResolution.GetLabel() )
		self.config.Flush()
	
	def readOptions( self ):
		self.cameraDevice.SetLabel( self.config.Read('CameraDevice', u'0') )
		self.cameraResolution.SetLabel( self.config.Read('CameraResolution', u'640x400') )

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

	mainWin = MainWin( None, title=AppVerName, size=(1000,500) )
	
	dataDir = Utils.getHomeDir()
	redirectFileName = os.path.join(dataDir, 'CrossMgrVideo.log')
	
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
		icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'CrossMgrVideo.ico'), wx.BITMAP_TYPE_ICO )
		mainWin.SetIcon( icon )
	except:
		pass

	mainWin.Refresh()
	if not mainWin.resetCamera():
		return
	
	# Start processing events.
	mainWin.Start()
	app.MainLoop()

@atexit.register
def shutdown():
	if mainWin:
		mainWin.shutdown()
	
if __name__ == '__main__':
	MainLoop()
	
