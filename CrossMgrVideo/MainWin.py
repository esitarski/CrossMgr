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
from Queue import Queue, Empty
import CamServer
from roundbutton import RoundButton

from datetime import datetime, timedelta, time

now = datetime.now

import Utils
import CVUtil
from SocketListener import SocketListener
from Database import Database, DBWriter, DBReader
from ScaledImage import ScaledImage
from FinishStrip import FinishStripPanel
from ManageDatabase import ManageDatabase
from PhotoDialog import PhotoDialog
from Version import AppVerName

imageWidth, imageHeight = 640, 480

closeFinishThreshold = 3.0/30.0
closeColors = ('E50000','D1D200','00BF00')
def getCloseFinishBitmaps( size=(16,16) ):
	bm = []
	dc = wx.MemoryDC()
	for c in closeColors:
		bitmap = wx.Bitmap( *size )
		dc.SelectObject( bitmap )
		dc.SetPen( wx.Pen(wx.Colour(0,0,0), 1) )
		dc.SetBrush( wx.Brush(wx.Colour(*[int(c[i:i+2],16) for i in xrange(0,6,2)]) ) )
		dc.DrawRectangle( 0, 0, size[0]-1, size[1]-1 )
		dc.SelectObject( wx.NullBitmap )
		bm.append( bitmap )
	return bm

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

from CalendarHeatmap import CalendarHeatmap
class DateSelectDialog( wx.Dialog ):
	def __init__( self, parent, triggerDates, id=wx.ID_ANY, ):
		wx.Dialog.__init__( self, parent, id, title=_("Date Select") )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		self.dateSelect = None
		
		self.triggerDates = triggerDates
		
		self.chm = CalendarHeatmap( self, dates=self.triggerDates )
		self.chm.Bind( wx.EVT_BUTTON, self.onCHMSelect )
		self.chm.Bind( wx.EVT_COMMAND_LEFT_DCLICK, self.onCHMChoose )
		
		self.triggerDatesList = wx.ListCtrl( self, style=wx.LC_REPORT|wx.LC_SINGLE_SEL, size=(-1,230) )
		
		self.triggerDatesList.InsertColumn( 0, 'Date' )
		self.triggerDatesList.InsertColumn( 1, 'Entries', format=wx.LIST_FORMAT_CENTRE, width=wx.LIST_AUTOSIZE_USEHEADER )
		for i, (d, c) in enumerate(triggerDates):
			self.triggerDatesList.InsertItem( i, d.strftime('%Y-%m-%d') )
			self.triggerDatesList.SetItem( i, 1, unicode(c) )
		
		if self.triggerDates:
			self.triggerDatesList.Select( 0 )
			self.chm.SetDate( self.triggerDates[0][0] )
		
		self.triggerDatesList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.onItemSelect )
		self.triggerDatesList.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivate )
		
		btns = self.CreateSeparatedButtonSizer( wx.OK|wx.CANCEL )
		self.ok = wx.FindWindowById(wx.ID_OK, self)
		self.cancel = wx.FindWindowById(wx.ID_CANCEL, self )		
		
		sizer.Add( self.chm, flag=wx.ALL, border=4 )
		sizer.Add( self.triggerDatesList, flag=wx.ALL, border=4 )
		
		sizer.Add( btns, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.SetSizer( sizer )
		wx.CallAfter( self.Fit )

	def onCHMSelect( self, event ):
		dSelect = event.GetDate()
		for i, (d, c) in enumerate(self.triggerDates):
			if d == dSelect:
				self.triggerDatesList.Select( i )
				break
		
	def onCHMChoose( self, event ):
		self.onCHMSelect( event )
		self.dateSelect = event.GetDate()
		self.EndModal( wx.ID_OK )	
		
	def onItemSelect( self, event ):
		self.dateSelect = self.triggerDates[event.GetIndex()][0]
		self.chm.SetDate( self.dateSelect )
		
	def onItemActivate( self, event ):
		self.onItemSelect( event )
		self.EndModal( wx.ID_OK )	
		
	def GetDate( self ):
		return self.dateSelect

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
	def __init__( self, parent, cameraDeviceNum=0, fps=30, cameraResolution=(imageWidth,imageHeight), id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, title=_('CrossMgr Video Configuration') )
		
		fps = int( fps )
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.title = wx.StaticText( self, label='CrossMgr Video Configuration' )
		self.title.SetFont( wx.Font( (0,24), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ) )
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
		
		pfgs.Add( wx.StaticText(self, label='Frames per second'+':'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.fps = wx.lib.intctrl.IntCtrl( self, value=fps, min=10, max=1000 )
		pfgs.Add( self.fps )
		
		pfgs.AddSpacer( 1 )
		pfgs.Add( wx.StaticText(self, label='\n'.join([
				'Your camera may not support all resolutions.',
				'Your Camera/Computer may not support the frame rate in low light.',
				'Check that the "Frame Processing Time" does not exceed the "Available Time Per Frame".',
				'If so, you will have to choose a lower Frames Per Second".',
			])), flag=wx.RIGHT, border=4 )
		
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

	def GetFPS( self ):
		return self.fps.GetValue()
		
	def onOK( self, event ):
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
		
class FocusDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, title=_('CrossMgr Video Focus') )
		
		self.imageSz = None
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.image = ScaledImage( self )
		self.image.Bind( wx.EVT_LEFT_UP, self.onOK )
		sizer.Add( self.image, 1, wx.EXPAND )
		self.SetSizerAndFit( sizer )
	
	def onOK( self, event ):
		self.EndModal( wx.ID_OK )
	
	def SetImage( self, image ):
		sz = image.GetSize()
		if sz != self.imageSz:
			self.imageSz = sz
			iWidth, iHeight = sz
			r = wx.GetClientDisplayRect()
			dWidth, dHeight = r.GetWidth(), r.GetHeight()
			if iWidth > dWidth or iHeight > dHeight:
				if float(iHeight)/float(iWidth) < float(dHeight)/float(dWidth):
					wSize = (dWidth, int(iHeight * float(dWidth)/float(iWidth)))
				else:
					wSize = (int(iWidth * float(dHeight)/float(iHeight)), dHeight)
			else:
				wSize = sz
			self.SetSize( wSize )
			self.SetTitle( u'{} {}x{}'.format( _('CrossMgr Video Focus'), *sz ) )
		
		return self.image.SetImage( image )

class TriggerDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, title=_('CrossMgr Video Trigger Editor') )
		
		self.db = None
		self.triggerId = None
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		gs = wx.FlexGridSizer( 2, 2, 4 )
		gs.AddGrowableCol( 1 )
		fieldNames = [h.replace('_', ' ').title() for h in Database.triggerEditFields]
		self.editFields = []
		for f in fieldNames:
			gs.Add( wx.StaticText(self, label=f), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			e = wx.TextCtrl(self, size=(500,-1) )
			gs.Add( e )
			self.editFields.append(e)
		btnSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.ok = wx.Button( self, wx.ID_OK )
		self.ok.Bind( wx.EVT_BUTTON, self.onOK )
		self.cancel = wx.Button( self, wx.ID_CANCEL )
		btnSizer.Add( self.ok, flag=wx.ALL, border=4 )
		btnSizer.AddStretchSpacer()
		btnSizer.Add( self.cancel, flag=wx.ALL|wx.ALIGN_RIGHT, border=4 )
		
		sizer.Add( gs, flag=wx.ALL, border=4 )
		sizer.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border=4 )
		self.SetSizerAndFit( sizer )
	
	def set( self, db, triggerId ):
		self.db = db
		self.triggerId = triggerId
		ef = db.getTriggerEditFields( self.triggerId )
		ef = ef or ['' for f in Database.triggerEditFields]
		for e, v in zip(self.editFields, ef):
			e.SetValue( unicode(v) )
	
	def get( self ):
		values = []
		for f, e in zip(Database.triggerEditFields, self.editFields):
			v = e.GetValue()
			if f == 'bib':
				try:
					v = int(v)
				except:
					v = 99999
			values.append( v )
		return values
	
	def commit( self ):
		self.db.setTriggerEditFields( self.triggerId, *self.get() )
	
	def onOK( self, event ):
		self.commit()
		self.EndModal( wx.ID_OK )
		
class AutoCaptureDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, title=_('CrossMgr Video Auto Capture') )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		gs = wx.FlexGridSizer( 2, 2, 4 )
		gs.AddGrowableCol( 1 )
		fieldNames = ['Seconds Before', 'Seconds After']
		self.editFields = []
		for f in fieldNames:
			gs.Add( wx.StaticText(self, label=f), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			e = wx.TextCtrl(self, size=(60,-1) )
			gs.Add( e )
			self.editFields.append(e)
		btnSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.ok = wx.Button( self, wx.ID_OK )
		self.cancel = wx.Button( self, wx.ID_CANCEL )
		btnSizer.Add( self.ok, flag=wx.ALL, border=4 )
		btnSizer.AddStretchSpacer()
		btnSizer.Add( self.cancel, flag=wx.ALL|wx.ALIGN_RIGHT, border=4 )
		
		sizer.Add( gs, flag=wx.ALL, border=4 )
		sizer.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border=4 )
		self.SetSizerAndFit( sizer )
	
	def set( self, s_before, s_after ):
		self.editFields[0].SetValue( '{:.2f}'.format(s_before) )
		self.editFields[1].SetValue( '{:.2f}'.format(s_after) )
	
	def get( self ):
		def fixValue( v ):
			try:
				return abs(float(v))
			except:
				return None
		return [fixValue(e.GetValue()) for e in seld.editFields]
		
class AutoWidthListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID = wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

class MainWin( wx.Frame ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(1000,800) ):
		wx.Frame.__init__(self, parent, id, title, size=size)
		
		self.db = Database()
		
		self.bufferSecs = 10
		self.setFPS( 25 )
		self.xFinish = None
		
		self.tFrameCount = self.tLaunch = self.tLast = now()
		self.frameCount = 0
		self.fpsActual = 0.0
		self.fpt = timedelta(seconds=0)
		self.iTriggerSelect = None
		self.triggerInfo = None
		self.tsMax = None
		
		self.captureTimer = wx.CallLater( 10, self.stopCapture )
		
		self.tdCaptureBefore = timedelta(seconds=0.5)
		self.tdCaptureAfter = timedelta(seconds=2.0)

		self.config = wx.Config(appName="CrossMgrVideo",
						vendorName="SmartCyclingSolutions",
						#style=wx.CONFIG_USE_LOCAL_FILE
		)
		
		self.requestQ = Queue()		# Select photos from photobuf.
		self.dbWriterQ = Queue()	# Photos waiting to be written
		self.messageQ = Queue()		# Collection point for all status/failure messages.
		
		self.SetBackgroundColour( wx.Colour(232,232,232) )
		
		self.triggerDialog = TriggerDialog( self )
		self.photoDialog = PhotoDialog( self )
		self.autoCaptureDialog = AutoCaptureDialog( self )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		#------------------------------------------------------------------------------------------------
		headerSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.logo = Utils.GetPngBitmap('CrossMgrHeader.png')
		headerSizer.Add( wx.StaticBitmap(self, wx.ID_ANY, self.logo) )
		
		self.title = wx.StaticText(self, label='CrossMgr Video\nVersion {}'.format(AppVerName.split()[1]), style=wx.ALIGN_RIGHT )
		self.title.SetFont( wx.Font( (0,28), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ) )
		headerSizer.Add( self.title, flag=wx.ALL, border=10 )
		
		#------------------------------------------------------------------------------
		self.cameraDeviceLabel = wx.StaticText(self, label='Camera Device:')
		self.cameraDevice = wx.StaticText( self )
		boldFont = self.cameraDevice.GetFont()
		boldFont.SetWeight( wx.BOLD )
		self.cameraDevice.SetFont( boldFont )
		self.cameraResolution = wx.StaticText( self )
		self.cameraResolution.SetFont( boldFont )
		self.targetFPS = wx.StaticText( self )
		self.targetFPSLabel = wx.StaticText( self, label='fps' )
		
		self.focus = wx.Button( self, label="Focus..." )
		self.focus.Bind( wx.EVT_BUTTON, self.onFocus )
		
		self.reset = wx.Button( self, label="Reset Camera" )
		self.reset.Bind( wx.EVT_BUTTON, self.resetCamera )
		
		self.manage = wx.Button( self, label="Manage Database" )
		self.manage.Bind( wx.EVT_BUTTON, self.manageDatabase )
		
		self.autoCaptureBtn = wx.Button( self, label="Config Auto Capture" )
		self.autoCaptureBtn.Bind( wx.EVT_BUTTON, self.autoCaptureConfig )
		
		self.autoCaptureEnableColour = wx.Colour(100,0,100)
		self.autoCaptureDisableColour = wx.Colour(100,0,0)
		
		self.autoCapture = RoundButton( self, label="AUTO\nCAPTURE", size=(90,90) )
		self.autoCapture.SetBackgroundColour( wx.WHITE )
		self.autoCapture.SetForegroundColour( self.autoCaptureEnableColour )
		self.autoCapture.SetFontToFitLabel( wx.Font(wx.FontInfo(10).Bold()) )
		self.autoCapture.Bind( wx.EVT_LEFT_DOWN, self.onStartAutoCapture )
		self.autoCapture.Bind( wx.EVT_LEFT_UP, self.onStopAutoCapture )
		
		self.captureEnableColour = wx.Colour(0,100,0)
		self.captureDisableColour = wx.Colour(100,0,0)
		
		self.capture = RoundButton( self, label="CAPTURE", size=(90,90) )
		self.capture.SetBackgroundColour( wx.WHITE )
		self.capture.SetForegroundColour( self.captureEnableColour )
		self.capture.SetFontToFitLabel( wx.Font(wx.FontInfo(10).Bold()) )
		self.capture.Bind( wx.EVT_LEFT_DOWN, self.onStartCapture )
		self.capture.Bind( wx.EVT_LEFT_UP, self.onStopCapture )
		
		headerSizer.Add( self.cameraDeviceLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		headerSizer.Add( self.cameraDevice, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		headerSizer.Add( self.cameraResolution, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		headerSizer.Add( self.targetFPS, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		headerSizer.Add( self.targetFPSLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=2 )
		headerSizer.Add( self.focus, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )
		headerSizer.Add( self.reset, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=32 )
		headerSizer.Add( self.manage, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )
		headerSizer.Add( self.autoCaptureBtn, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )
		headerSizer.AddStretchSpacer()
		headerSizer.Add( self.autoCapture, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		headerSizer.Add( self.capture, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT|wx.RIGHT, border=8 )

		#------------------------------------------------------------------------------
		mainSizer.Add( headerSizer, flag=wx.EXPAND )
		
		#------------------------------------------------------------------------------------------------
		self.finishStrip = FinishStripPanel( self, size=(-1,wx.GetDisplaySize()[1]//2) )
		self.finishStrip.finish.Bind( wx.EVT_RIGHT_DOWN, self.onRightClick )
		
		self.primaryImage = ScaledImage( self, style=wx.BORDER_SUNKEN, size=(imageWidth, imageHeight) )
		self.primaryImage.SetTestImage()
		self.primaryImage.Bind( wx.EVT_LEFT_UP, self.onFocus )
		
		self.focusDialog = FocusDialog( self )
		
		hsDate = wx.BoxSizer( wx.HORIZONTAL )
		hsDate.Add( wx.StaticText(self, label='Show Triggers for'), flag=wx.ALIGN_CENTER_VERTICAL )
		tQuery = now()
		self.date = wx.adv.DatePickerCtrl(
			self,
			dt=wx.DateTime.FromDMY( tQuery.day, tQuery.month-1, tQuery.year ),
			style=wx.adv.DP_DROPDOWN|wx.adv.DP_SHOWCENTURY
		)
		self.date.Bind( wx.adv.EVT_DATE_CHANGED, self.onQueryDateChanged )
		hsDate.Add( self.date, flag=wx.LEFT, border=2 )
		
		self.dateSelect = wx.Button( self, label='Select Date' )
		hsDate.Add( self.dateSelect, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2 )
		self.dateSelect.Bind( wx.EVT_BUTTON, self.onDateSelect )
		
		hsDate.Add( wx.StaticText(self, label='Filter by Bib'), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=12 )
		self.bib = wx.lib.intctrl.IntCtrl( self, style=wx.TE_PROCESS_ENTER, size=(64,-1), min=1, allow_none=True, value=None )
		self.bib.Bind( wx.EVT_TEXT_ENTER, self.onQueryBibChanged )
		hsDate.Add( self.bib, flag=wx.LEFT, border=2 )
		
		self.tsQueryLower = datetime(tQuery.year, tQuery.month, tQuery.day)
		self.tsQueryUpper = self.tsQueryLower + timedelta(days=1)
		self.bibQuery = None
		
		self.triggerList = AutoWidthListCtrl( self, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_SORT_ASCENDING )
		
		self.il = wx.ImageList(16, 16)
		self.sm_close = []
		for bm in getCloseFinishBitmaps():
			self.sm_close.append( self.il.Add(bm) )
		self.sm_up = self.il.Add( Utils.GetPngBitmap('SmallUpArrow.png'))
		self.sm_up = self.il.Add( Utils.GetPngBitmap('SmallUpArrow.png'))
		self.sm_dn = self.il.Add( Utils.GetPngBitmap('SmallDownArrow.png'))
		self.triggerList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		headers = ['Time', 'Bib', 'Name', 'Team', 'Wave', 'Race', 'km/h', 'mph']
		for i, h in enumerate(headers):
			self.triggerList.InsertColumn(
				i, h,
				wx.LIST_FORMAT_RIGHT if h in ('Bib','km/h','mph') else wx.LIST_FORMAT_LEFT
			)
		self.itemDataMap = {}
		
		self.triggerList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.onTriggerSelected )
		self.triggerList.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.onTriggerEdit )
		self.triggerList.Bind( wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onTriggerRightClick )
		#self.triggerList.Bind( wx.EVT_LIST_DELETE_ITEM, self.onTriggerDelete )
		
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
				
		self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

		self.readOptions()
		self.updateFPS( int(float(self.targetFPS.GetLabel())) )
		self.SetSizerAndFit( mainSizer )
		
		# Start the message reporting thread so we can see what is going on.
		self.messageThread = threading.Thread( target=self.showMessages )
		self.messageThread.daemon = True
		self.messageThread.start()
		
		wx.CallLater( 300, self.refreshTriggers )
	
	def setFPS( self, fps ):
		self.fps = int(fps if fps > 0 else 30)
		self.frameDelay = 1.0 / self.fps
		self.frameCountUpdate = int(self.fps * 2)
	
	def updateFPS( self, fps ):
		self.setFPS( fps )
		self.targetFPS.SetLabel( u'{}'.format(self.fps) )
	
	def setQueryDate( self, d ):
		self.tsQueryLower = d
		self.tsQueryUpper = self.tsQueryLower + timedelta( days=1 )
		self.refreshTriggers( True )
		
	def onDateSelect( self, event ):
		triggerDates = self.db.getTriggerDates()
		triggerDates.sort( reverse=True )
		with DateSelectDialog( self, triggerDates ) as dlg:
			if dlg.ShowModal() == wx.ID_OK and dlg.GetDate():
				self.setQueryDate( dlg.GetDate() )
			
	def onQueryDateChanged( self, event ):
		v = self.date.GetValue()
		self.setQueryDate( datetime( v.GetYear(), v.GetMonth() + 1, v.GetDay() ) )
	
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
	
	def refreshTriggers( self, replace=False, iTriggerRow=None ):
		tNow = now()
		self.lastTriggerRefresh = tNow
		
		# replace = True
		if replace:
			tsLower = self.tsQueryLower
			tsUpper = self.tsQueryUpper
			self.triggerList.DeleteAllItems()
			self.itemDataMap = {}
			self.tsMax = None
			self.iTriggerSelect = None
			self.triggerInfo = {}
			self.finishStrip.SetTsJpgs( None, None )
		else:
			tsLower = (self.tsMax or datetime(tNow.year, tNow.month, tNow.day)) + timedelta(seconds=0.00001)
			tsUpper = tsLower + timedelta(days=1)

		triggers = self.db.getTriggers( tsLower, tsUpper, self.bibQuery )
			
		tsPrev = (self.tsMax or datetime(2000,1,1))
		if triggers:
			self.tsMax = triggers[-1][1] # id,ts,s_before,s_after,ts_start,bib,first_name,last_name,team,wave,race_name,kmh
		
		for i, (id,ts,s_before,s_after,ts_start,bib,first_name,last_name,team,wave,race_name,kmh) in enumerate(triggers):
			dtFinish = (ts-tsPrev).total_seconds()
			itemImage = self.sm_close[min(len(self.sm_close)-1, int(len(self.sm_close) * dtFinish / closeFinishThreshold))]		
			row = self.triggerList.InsertItem( sys.maxint, ts.strftime('%H:%M:%S.%f')[:-3], itemImage )
			self.triggerList.SetItem( row, 1, u'{:>6}'.format(bib) )
			name = u', '.join( n for n in (last_name, first_name) if n )
			self.triggerList.SetItem( row, 2, name )
			self.triggerList.SetItem( row, 3, team )
			self.triggerList.SetItem( row, 4, wave )
			self.triggerList.SetItem( row, 5, race_name )
			if kmh:
				kmh_text, mph_text = u'{:.2f}'.format(kmh), u'{:.2f}'.format(kmh * 0.621371)
			else:
				kmh_text = mph_text = u''
			self.triggerList.SetItem( row, 6, kmh_text )
			self.triggerList.SetItem( row, 7, mph_text )
			
			self.triggerList.SetItemData( row, row )
			self.itemDataMap[row] = (id,ts,s_before,s_after,ts_start,bib,name,team,wave,race_name,first_name,last_name,kmh)
			tsPrev = ts
			
		for i in xrange(5):
			self.triggerList.SetColumnWidth(i, wx.LIST_AUTOSIZE)

		if iTriggerRow is not None:
			iTriggerRow = min( max(0, iTriggerRow), self.triggerList.GetItemCount()-1 )
			self.triggerList.EnsureVisible( iTriggerRow )
			self.triggerList.Select( iTriggerRow )
		else:
			if self.triggerList.GetItemCount() >= 1:
				self.triggerList.EnsureVisible( self.triggerList.GetItemCount()-1 )

	def Start( self ):
		self.messageQ.put( ('', '************************************************') )
		self.messageQ.put( ('started', now().strftime('%Y/%m/%d %H:%M:%S')) )
		self.startThreads()

	def onStartAutoCapture( self, event ):
		tNow = now()
		
		self.autoCapture.SetForegroundColour( self.autoCaptureDisableColour )
		wx.CallAfter( self.autoCapture.Refresh )
		wx.BeginBusyCursor()
		
		self.autoCaptureCount = getattr(self, 'autoCaptureCount', 0) + 1
		self.requestQ.put( {
				'time':tNow,
				's_before':self.tdCaptureBefore.total_seconds(),
				's_after':self.tdCaptureAfter.total_seconds(),
				'ts_start':tNow,
				'bib':self.autoCaptureCount,
				'lastName':u'Event',
			}
		)
		
		def doUpdateAutoCapture( tStartCapture, autoCaptureCount ):
			self.dbWriterQ.put( ('flush',) )
			self.dbWriterQ.join()
			triggers = self.db.getTriggers( tStartCapture, tStartCapture, autoCaptureCount )
			if triggers:
				id = triggers[0][0]
				self.db.initCaptureTriggerData( id, tStartCapture )
				self.refreshTriggers( iTriggerRow=999999 )
				self.onTriggerSelected( iTriggerSelect=self.triggerList.GetItemCount()-1 )

		wx.CallLater( int(self.tdCaptureAfter.total_seconds()*1000.0) + 100, doUpdateAutoCapture, tNow, self.autoCaptureCount )
		
	def onStopAutoCapture( self, event ):
		wx.EndBusyCursor()
		self.autoCapture.SetForegroundColour( self.autoCaptureEnableColour )
		self.autoCapture.Refresh()		
		
	def onStartCapture( self, event ):
		tNow = now()
		
		self.capture.SetForegroundColour( self.captureDisableColour )
		wx.CallAfter( self.capture.Refresh )
		wx.BeginBusyCursor()
		
		self.captureCount = getattr(self, 'captureCount', 0) + 1
		self.requestQ.put( {
				'time':tNow,
				's_before':0.0,
				's_after':self.tdCaptureAfter.total_seconds(),
				'ts_start':tNow,
				'bib':self.captureCount,
				'lastName':u'Capture',
			}
		)
		self.tStartCapture = tNow
		self.camInQ.put( {'cmd':'start_capture', 'tStart':tNow-self.tdCaptureBefore} )
	
	def showLastTrigger( self ):
		iTriggerRow = self.triggerList.GetItemCount() - 1
		if iTriggerRow < 0:
			return
		self.triggerList.EnsureVisible( iTriggerRow )
		for r in xrange(self.triggerList.GetItemCount()):
			self.triggerList.Select(r, 0)
		self.triggerList.Select( iTriggerRow )		
	
	def onStopCapture( self, event ):
		self.camInQ.put( {'cmd':'stop_capture'} )
		triggers = self.db.getTriggers( self.tStartCapture, self.tStartCapture, self.captureCount )
		if triggers:
			id = triggers[0][0]
			self.db.updateTriggerBeforeAfter(
				id,
				0.0,
				(now() - self.tStartCapture).total_seconds()
			)
			self.db.initCaptureTriggerData( id, self.tStartCapture )
			self.refreshTriggers( iTriggerRow=999999 )
		
		self.showLastTrigger()
		
		wx.EndBusyCursor()
		self.capture.SetForegroundColour( self.captureEnableColour )
		self.capture.Refresh()		
		
		def updateFS():
			# Wait for all the photos to be written.
			self.dbWriterQ.put( ('flush',) )
			self.dbWriterQ.join()
			# Update the finish strip.
			wx.CallAfter( self.onTriggerSelected, iTriggerSelect=self.triggerList.GetItemCount() - 1 )

		threading.Thread( target=updateFS ).start()

	def autoCaptureConfig( self, event ):
		self.autoCaptureDialog.set( self.tdCaptureBefore.total_seconds(), self.tdCaptureAfter.total_seconds() )
		if self.autoCaptureDialog.ShowModal() == wx.ID_OK:
			s_before, s_after = self.autoCaptureDialog.get()
			self.tdCaptureBefore = timedelta( seconds=s_before if s_before else 0.5 )
			self.tdCaptureAfter = timedelta( seconds=s_after if s_after else 2.0 )
			self.writeOptions()
		
	def onFocus( self, event ):
		if self.focusDialog.IsShown():
			return
		self.focusDialog.Move((4,4))
		self.camInQ.put( {'cmd':'send_update', 'name':'focus', 'freq':1} )
		self.focusDialog.Show()
	
	def onRightClick( self, event ):
		if not self.triggerInfo:
			return
		
		self.xFinish = event.GetX()
		self.photoDialog.set( self.finishStrip.finish.getJpg(self.xFinish), self.triggerInfo, self.finishStrip.GetTsJpgs(), self.fps )
		self.photoDialog.CenterOnParent()
		self.photoDialog.Move( self.photoDialog.GetScreenPosition().x, 0 )
		self.photoDialog.ShowModal()
		if self.triggerInfo['kmh'] != (self.photoDialog.kmh or 0.0):
			self.db.updateTriggerKMH( self.triggerInfo['id'], self.photoDialog.kmh or 0.0 )
			self.refreshTriggers( replace=True, iTriggerRow=self.iTriggerSelect )
		self.photoDialog.clear()

	def onTriggerSelected( self, event=None, iTriggerSelect=None ):
		self.iTriggerSelect = event.Index if iTriggerSelect is None else iTriggerSelect
		if self.iTriggerSelect >= self.triggerList.GetItemCount():
			self.ts = None
			self.tsJpg = []
			self.finishStrip.SetTsJpgs( self.tsJpg, self.ts, {} )
			return
		
		data = self.itemDataMap[self.triggerList.GetItemData(self.iTriggerSelect)]
		self.triggerInfo = {
			a:data[i] for i, a in enumerate((
				'id','ts','s_before','s_after','ts_start',
				'bib','name','team','wave','raceName',
				'firstName','lastName','kmh'))
		}
		self.ts = self.triggerInfo['ts']
		s_before = max( self.triggerInfo['s_before'] or 0.0, self.tdCaptureBefore.total_seconds() )
		s_after = max( self.triggerInfo['s_after'] or 0.0, self.tdCaptureAfter.total_seconds() )
		
		# Update the screen in the background so we don't freeze the UI.
		def updateFS():
			self.tsJpg = self.db.clone().getPhotos(
				self.ts - timedelta(seconds=s_before), self.ts + timedelta(seconds=s_after)
			)
			wx.CallAfter( self.finishStrip.SetTsJpgs, self.tsJpg, self.ts, self.triggerInfo )
			
		threading.Thread( target=updateFS ).start()
	
	def onTriggerEdit( self, event ):
		self.iTriggerSelect = event.Index
		data = self.itemDataMap[self.triggerList.GetItemData(self.iTriggerSelect)]
		self.triggerDialog.set( self.db, data[0] )
		self.triggerDialog.CenterOnParent()
		if self.triggerDialog.ShowModal() == wx.ID_OK:
			row = event.Index
			fields = {f:v for f, v in zip(Database.triggerEditFields,self.triggerDialog.get())}
			self.triggerList.SetItem( row, 1, u'{:>6}'.format(fields['bib']) )
			name = u', '.join( n for n in (fields['last_name'], fields['first_name']) if n )
			self.triggerList.SetItem( row, 2, name )
			self.triggerList.SetItem( row, 3, fields['team'] )
			self.triggerList.SetItem( row, 4, fields['wave'] )
			self.triggerList.SetItem( row, 5, fields['race_name'] )
	
	def onTriggerRightClick( self, event ):
		self.iTriggerSelect = event.Index
		if not hasattr(self, "triggerDeleteID"):
			self.triggerDeleteID = wx.NewId()
			self.Bind(wx.EVT_MENU, lambda event: self.doTriggerDelete(), id=self.triggerDeleteID)

		menu = wx.Menu()
		menu.Append(self.triggerDeleteID, "Delete...")

		self.PopupMenu(menu)
		menu.Destroy()

	def doTriggerDelete( self ):
		data = self.itemDataMap[self.triggerList.GetItemData(self.iTriggerSelect)]
		self.db.deleteTrigger( data[0], self.tdCaptureBefore.total_seconds(), self.tdCaptureAfter.total_seconds() )
		self.refreshTriggers( replace=True, iTriggerRow=self.iTriggerSelect )
	
	def onTriggerDelete( self, event ):
		self.iTriggerSelect = event.Index
		self.doTriggerDelete()
		
	def showMessages( self ):
		while 1:
			message = self.messageQ.get()
			assert len(message) == 2, 'Incorrect message length'
			cmd, info = message
			wx.CallAfter( self.messageManager.write, '{}:  {}'.format(cmd, info) if cmd else info )
		
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
		
		self.camInQ, self.camReader = CamServer.getCamServer( self.getCameraInfo() )
		self.cameraThread = threading.Thread( target=self.processCamera )
		self.cameraThread.daemon = True
		
		self.eventThread = threading.Thread( target=self.processRequests )
		self.eventThread.daemon = True
		
		self.dbWriterThread = threading.Thread( target=DBWriter, args=(self.dbWriterQ,) )
		self.dbWriterThread.daemon = True
		
		self.cameraThread.start()
		self.eventThread.start()
		self.dbWriterThread.start()
		
		self.grabFrameOK = True
		self.messageQ.put( ('threads', 'Successfully Launched') )
		
		self.camInQ.put( {'cmd':'send_update', 'name':'primary', 'freq':5} )
		return True
	
	def stopCapture( self ):
		self.dbWriterQ.put( ('flush',) )
	
	def processCamera( self ):
		lastFrame = None
		while 1:
			try:
				msg = self.camReader.recv()
			except EOFError:
				break
			
			cmd = msg['cmd']
			if cmd == 'response':
				for t, f in msg['ts_frames']:
					self.dbWriterQ.put( ('photo', t, f) )
					lastFrame = f
			elif cmd == 'update':
				name, lastFrame = msg['name'], lastFrame if msg['frame'] is None else msg['frame']
				if lastFrame is not None:
					if name == 'primary':
						wx.CallAfter( self.primaryImage.SetImage, CVUtil.frameToImage(lastFrame) )
					elif name == 'focus':
						if self.focusDialog.IsShown():
							wx.CallAfter( self.focusDialog.SetImage, CVUtil.frameToImage(lastFrame) )
						else:
							self.camInQ.put( {'cmd':'cancel_update', 'name':'focus'} )
			elif cmd == 'terminate':
				break
		
	def processRequests( self ):
		def refresh():
			self.dbWriterQ.put( ('flush',) )
			wx.CallLater( 300, self.refreshTriggers )
	
		while 1:
			msg = self.requestQ.get()
			
			tSearch = msg['time']
			advanceSeconds = msg.get('advanceSeconds', 0.0)
			tSearch += timedelta(seconds=advanceSeconds)
			
			# Record this trigger.
			self.dbWriterQ.put( (
				'trigger',
				tSearch - timedelta(seconds=advanceSeconds),
				msg.get('s_before', self.tdCaptureBefore.total_seconds()),
				msg.get('s_after', self.tdCaptureAfter.total_seconds()),
				msg.get('ts_start', None) or now(),
				msg.get('bib', 99999),
				msg.get('firstName',u''),
				msg.get('lastName',u''),
				msg.get('team',u''),
				msg.get('wave',u''),
				msg.get('raceName',u'')
			) )
			# Record the video frames for the trigger.
			tStart, tEnd = tSearch-self.tdCaptureBefore, tSearch+self.tdCaptureAfter
			self.camInQ.put( { 'cmd':'query', 'tStart':tStart, 'tEnd':tEnd,} )
			wx.CallAfter( wx.CallLater, max(100, int(100+1000*(tEnd-now()).total_seconds())), refresh )
	
	def shutdown( self ):
		# Ensure that all images in the queue are saved.
		if hasattr(self, 'dbWriterThread'):
			self.camInQ.put( {'cmd':'terminate'} )
			self.dbWriterQ.put( ('terminate', ) )
			self.dbWriterThread.join()
	
	def resetCamera( self, event=None ):
		dlg = ConfigDialog( self, self.getCameraDeviceNum(), self.fps, self.getCameraResolution() )
		ret = dlg.ShowModal()
		cameraDeviceNum = dlg.GetCameraDeviceNum()
		cameraResolution = dlg.GetCameraResolution()
		fps = dlg.GetFPS()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return False
		
		self.setCameraDeviceNum( cameraDeviceNum )
		self.setCameraResolution( *cameraResolution )
		self.updateFPS( fps )
		self.writeOptions()
		
		if hasattr(self, 'camInQ'):
			self.camInQ.put( {'cmd':'cam_info', 'info':self.getCameraInfo(),} )
		return True
	
	def manageDatabase( self, event ):
		trigFirst, trigLast = self.db.getTimestampRange()
		dlg = ManageDatabase( self, self.db.getsize(), self.db.fname, trigFirst, trigLast, title='Manage Database' )
		if dlg.ShowModal() == wx.ID_OK:
			work = wx.BusyCursor()
			tsLower, tsUpper, vacuum = dlg.GetValues()
			if tsUpper:
				tsUpper = datetime.combine( tsUpper, time(23,59,59,999999) )
			self.db.cleanBetween( tsLower, tsUpper )
			if vacuum:
				self.db.vacuum()
			wx.CallAfter( self.finishStrip.Clear )
			wx.CallAfter( self.refreshTriggers, True )
		dlg.Destroy()
	
	def setCameraDeviceNum( self, num ):
		self.cameraDevice.SetLabel( unicode(num) )
		
	def setCameraResolution( self, width, height ):
		self.cameraResolution.SetLabel( u'{}x{}'.format(width, height) )
			
	def getCameraDeviceNum( self ):
		return int(self.cameraDevice.GetLabel())
		
	def getCameraFPS( self ):
		return int(float(self.targetFPS.GetLabel()))
		
	def getCameraResolution( self ):
		try:
			resolution = [int(v) for v in self.cameraResolution.GetLabel().split('x')]
			return resolution[0], resolution[1]
		except:
			return 640, 480
		
	def onCloseWindow( self, event ):
		self.shutdown()
		wx.Exit()
		
	def writeOptions( self ):
		self.config.Write( 'CameraDevice', self.cameraDevice.GetLabel() )
		self.config.Write( 'CameraResolution', self.cameraResolution.GetLabel() )
		self.config.Write( 'FPS', self.targetFPS.GetLabel() )
		self.config.Write( 'SecondsBefore', '{:.3f}'.format(self.tdCaptureBefore.total_seconds()) )
		self.config.Write( 'SecondsAfter', '{:.3f}'.format(self.tdCaptureAfter.total_seconds()) )
		self.config.Flush()
	
	def readOptions( self ):
		self.cameraDevice.SetLabel( self.config.Read('CameraDevice', u'0') )
		self.cameraResolution.SetLabel( self.config.Read('CameraResolution', u'640x480') )
		self.targetFPS.SetLabel( self.config.Read('FPS', u'30.000') )
		s_before = self.config.Read('SecondsBefore', u'0.5')
		s_after = self.config.Read('SecondsAfter', u'2.0')
		try:
			self.tdCaptureBefore = timedelta(seconds=abs(float(s_before)))
		except:
			pass
		try:
			self.tdCaptureAfter = timedelta(seconds=abs(float(s_after)))
		except:
			pass
		
	def getCameraInfo( self ):
		width, height = self.getCameraResolution()
		return {'usb':self.getCameraDeviceNum(), 'fps':self.getCameraFPS(), 'width':width, 'height':height}

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
				pf.write( '{}: {} Started.\n'.format(now().strftime('%Y-%m-%d_%H:%M:%S'), AppVerName) )
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
	
