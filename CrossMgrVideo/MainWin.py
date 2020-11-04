import wx
import wx.adv
import wx.lib.mixins.listctrl as listmix
import wx.lib.intctrl
import sys
import os
import re
import six
import time
import math
import json
import threading
import socket
import atexit
import time
import platform
import webbrowser
from six.moves.queue import Queue, Empty
import CamServer
from roundbutton import RoundButton

from datetime import datetime, timedelta, time

now = datetime.now

import Utils
import CVUtil
from SocketListener import SocketListener
from MultiCast import multicast_group, multicast_port
from Database import Database, DBWriter
from ScaledBitmap import ScaledBitmap
from FinishStrip import FinishStripPanel
from ManageDatabase import ManageDatabase
from PhotoDialog import PhotoDialog
from Clock import Clock
from AddPhotoHeader import AddPhotoHeader
from Version import AppVerName
from AddExifToJpeg import AddExifToJpeg

imageWidth, imageHeight = 640, 480

tdCaptureBeforeDefault = timedelta(seconds=0.5)
tdCaptureAfterDefault = timedelta(seconds=2.0)

closeFinishThreshold = 3.0/30.0
closeColors = ('E50000','D1D200','00BF00')
def getCloseFinishBitmaps( size=(16,16) ):
	bm = []
	dc = wx.MemoryDC()
	for c in closeColors:
		bitmap = wx.Bitmap( *size )
		dc.SelectObject( bitmap )
		dc.SetPen( wx.Pen(wx.Colour(0,0,0), 1) )
		dc.SetBrush( wx.Brush(wx.Colour(*[int(c[i:i+2],16) for i in range(0,6,2)]) ) )
		dc.DrawRectangle( 0, 0, size[0]-1, size[1]-1 )
		dc.SelectObject( wx.NullBitmap )
		bm.append( bitmap )
	return bm

def setFont( font, w ):
	w.SetFont( font )
	return w

def OpenHelp():
	webbrowser.open( os.path.join(Utils.getHelpFolder(), 'QuickStart.html'), new=0, autoraise=1 )
	
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
			self.triggerDatesList.SetItem( i, 1, six.text_type(c) )
		
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
	'320x240',
	'640x480',
	'800x600',
	'1024x768',
	'1280x720',
	'1280x1024',
	'1920x1080',
	'1600x1200',
	'MAXxMAX',
)

def pixelsFromRes( res ):
	return tuple( (int(v) if v.isdigit() else 10000) for v in res.split('x') )

def getCameraResolutionChoice( resolution ):
	for i, res in enumerate(cameraResolutionChoices):
		if resolution == pixelsFromRes(res):
			return i
	return len(cameraResolutionChoices) - 1
	
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
		self.cameraDevice = wx.Choice( self, choices=['{}'.format(i) for i in range(8)] )
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
		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.helpBtn = wx.Button( self, wx.ID_HELP )
		self.Bind( wx.EVT_BUTTON, self.onHelp, self.helpBtn )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.okBtn, border=4, flag=wx.ALL )
		self.okBtn.SetDefault()
		hs.AddStretchSpacer()
		hs.Add( self.helpBtn, border=4, flag=wx.ALL )
		hs.Add( self.cancelBtn, border=4, flag=wx.ALL )
		
		sizer.AddSpacer( 8 )
		sizer.Add( hs, flag=wx.EXPAND )
		
		self.SetSizerAndFit( sizer )
		
	def GetCameraDeviceNum( self ):
		return self.cameraDevice.GetSelection()
		
	def GetCameraResolution( self ):
		return pixelsFromRes(cameraResolutionChoices[self.cameraResolution.GetSelection()])

	def GetFPS( self ):
		return self.fps.GetValue()
		
	def onHelp( self, event ):
		OpenHelp()

snapshotEnableColour = wx.Colour(0,0,100)
snapshotDisableColour = wx.Colour(100,100,0)
autoCaptureEnableColour = wx.Colour(100,0,100)
autoCaptureDisableColour = wx.Colour(100,100,0)
captureEnableColour = wx.Colour(0,100,0)
captureDisableColour = wx.Colour(100,0,0)
		
def CreateCaptureButtons( parent ):	
	snapshot = RoundButton( parent, label="SNAPSHOT", size=(90,90) )
	snapshot.SetBackgroundColour( wx.WHITE )
	snapshot.SetForegroundColour( snapshotEnableColour )
	snapshot.SetFontToFitLabel( wx.Font(wx.FontInfo(10).Bold()) )
	snapshot.SetToolTip( _('Record a Single Frame') )
	
	autoCapture = RoundButton( parent, label="AUTO\nCAPTURE", size=(90,90) )
	autoCapture.SetBackgroundColour( wx.WHITE )
	autoCapture.SetForegroundColour( autoCaptureEnableColour )
	autoCapture.SetFontToFitLabel( wx.Font(wx.FontInfo(10).Bold()) )
	autoCapture.SetToolTip( _('Capture Video for an Automatic Interval\nSet in "Config Auto Capture"') )
	
	capture = RoundButton( parent, label="CAPTURE", size=(90,90) )
	capture.SetBackgroundColour( wx.WHITE )
	capture.SetForegroundColour( captureEnableColour )
	capture.SetFontToFitLabel( wx.Font(wx.FontInfo(10).Bold()) )
	capture.SetToolTip( _('Capture Video\nwhile the Button is held down') )
		
	return snapshot, autoCapture, capture

class FocusDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id,
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX,
			title=_('CrossMgr Video Focus')
		)
		
		self.bitmapSz = None
		sizer = wx.BoxSizer( wx.VERTICAL )
		self.SetBackgroundColour( wx.Colour(232,232,232) )
				
		btnSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.logo = Utils.GetPngBitmap('CrossMgrHeader.png')
		
		self.title = wx.StaticText(self, label='CrossMgr Video\nFocus Window', style=wx.ALIGN_RIGHT )
		self.title.SetFont( wx.Font( (0,28), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ) )
		self.explain = wx.StaticText(self, label='Click and Drag to Zoom in Photo')
		self.snapshot, self.autoCapture, self.capture = CreateCaptureButtons( self )
		
		btnSizer.Add( wx.StaticBitmap(self, wx.ID_ANY, self.logo) )
		btnSizer.Add( self.title, flag=wx.ALL, border=10 )
		btnSizer.Add( self.explain, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=4 )
		btnSizer.AddStretchSpacer()
		btnSizer.Add( self.snapshot, flag=wx.ALL, border=4 )
		btnSizer.Add( self.autoCapture, flag=wx.ALL, border=4 )
		btnSizer.Add( self.capture, flag=wx.ALL, border=4 )
		
		sizer.Add( btnSizer, flag=wx.EXPAND )
		
		self.bitmap = ScaledBitmap( self, inset=True )
		sizer.Add( self.bitmap, 1, wx.EXPAND )
		self.SetSizerAndFit( sizer )
		
	def SetBitmap( self, bitmap ):
		sz = bitmap.GetSize()
		if sz != self.bitmapSz:
			if self.bitmapSz is None:
				r = wx.GetClientDisplayRect()
				dWidth, dHeight = r.GetWidth(), r.GetHeight()
				self.SetSize( (int(dWidth*0.85), int(dHeight*0.85)) )
			self.bitmapSz = sz
			self.SetTitle( u'{} {}x{}'.format( _('CrossMgr Video Focus'), *sz ) )
		return self.bitmap.SetBitmap( bitmap )

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
		btnSizer.Add( self.cancel, flag=wx.ALL, border=4 )
		
		sizer.Add( gs, flag=wx.ALL, border=4 )
		sizer.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border=4 )
		self.SetSizerAndFit( sizer )
	
	def set( self, db, triggerId ):
		self.db = db
		self.triggerId = triggerId
		ef = db.getTriggerEditFields( self.triggerId )
		ef = ef or ['' for f in Database.triggerEditFields]
		for e, v in zip(self.editFields, ef):
			e.SetValue( '{}'.format(v) )
	
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
		btnSizer.Add( self.cancel, flag=wx.ALL, border=4 )
		
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
		return [fixValue(e.GetValue()) for e in self.editFields]
		
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
		self.setFPS( 30 )
		self.xFinish = None
		
		self.tFrameCount = self.tLaunch = self.tLast = now()
		self.frameCount = 0
		self.fpt = timedelta(seconds=0)
		self.iTriggerSelect = None
		self.triggerInfo = None
		self.tsMax = None
		
		self.captureTimer = wx.CallLater( 10, self.stopCapture )
		
		self.tdCaptureBefore = tdCaptureBeforeDefault
		self.tdCaptureAfter = tdCaptureAfterDefault

		dataDir = Utils.getHomeDir()
		configFileName = os.path.join(dataDir, 'CrossMgrVideo.cfg')
		self.config = wx.Config(appName="CrossMgrVideo",
								vendorName="Edward.Sitarski@gmail.com",
								localFilename=configFileName
		)
		
		self.requestQ = Queue()		# Select photos from photobuf.
		self.dbWriterQ = Queue()	# Photos waiting to be written
		self.messageQ = Queue()		# Collection point for all status/failure messages.

		ID_MENU_RESETCAMERA = wx.NewIdRef()
		ID_MENU_FOCUS = wx.NewIdRef()
		ID_MENU_CONFIGAUTOCAPTURE = wx.NewIdRef()
		ID_MENU_MANAGEDATABASE = wx.NewIdRef()
		self.menuBar = wx.MenuBar(wx.MB_DOCKABLE)
		if 'WXMAC' in wx.Platform:
			self.appleMenu = self.menuBar.OSXGetAppleMenu()
			self.appleMenu.SetTitle("CrossMgrVideo")

			self.appleMenu.Insert(0, wx.ID_ABOUT, "&About")

			self.Bind(wx.EVT_MENU, self.OnAboutBox, id=wx.ID_ABOUT)

			self.editMenu = wx.Menu()
			self.editMenu.Append(wx.MenuItem(self.editMenu, ID_MENU_RESETCAMERA,"R&eset Camera"))
			self.editMenu.Append(wx.MenuItem(self.editMenu, ID_MENU_FOCUS,"&Focus"))
			self.editMenu.Append(wx.MenuItem(self.editMenu, ID_MENU_CONFIGAUTOCAPTURE,"&Configure Autocapture"))
			self.editMenu.Append(wx.MenuItem(self.editMenu, ID_MENU_MANAGEDATABASE,"&Manage Database"))

			self.Bind(wx.EVT_MENU, self.resetCamera, id=ID_MENU_RESETCAMERA)
			self.Bind(wx.EVT_MENU, self.onFocus, id=ID_MENU_FOCUS)
			self.Bind(wx.EVT_MENU, self.autoCaptureConfig, id=ID_MENU_CONFIGAUTOCAPTURE)
			self.Bind(wx.EVT_MENU, self.manageDatabase, id=ID_MENU_MANAGEDATABASE)
			self.menuBar.Append(self.editMenu, "&Edit")

		else:
			self.fileMenu = wx.Menu()
			self.fileMenu.Append(wx.MenuItem(self.fileMenu, ID_MENU_RESETCAMERA,"R&eset Camera"))
			self.fileMenu.Append(wx.MenuItem(self.fileMenu, ID_MENU_FOCUS,"&Focus"))
			self.fileMenu.Append(wx.MenuItem(self.fileMenu, ID_MENU_CONFIGAUTOCAPTURE,"&Configure Autocapture"))
			self.fileMenu.Append(wx.MenuItem(self.fileMenu, ID_MENU_MANAGEDATABASE,"&Manage Database"))
			self.fileMenu.Append(wx.ID_EXIT)
			self.Bind(wx.EVT_MENU, self.resetCamera, id=ID_MENU_RESETCAMERA)
			self.Bind(wx.EVT_MENU, self.onFocus, id=ID_MENU_FOCUS)
			self.Bind(wx.EVT_MENU, self.autoCaptureConfig, id=ID_MENU_CONFIGAUTOCAPTURE)
			self.Bind(wx.EVT_MENU, self.manageDatabase, id=ID_MENU_MANAGEDATABASE)
			self.Bind(wx.EVT_MENU, self.onCloseWindow, id=wx.ID_EXIT)
			self.menuBar.Append(self.fileMenu, "&File")
			self.helpMenu = wx.Menu()
			self.helpMenu.Insert(0, wx.ID_ABOUT, "&About")
			self.helpMenu.Insert(1, wx.ID_HELP, "&Help")
			self.Bind(wx.EVT_MENU, self.OnAboutBox, id=wx.ID_ABOUT)
			self.Bind(wx.EVT_MENU, self.onHelp, id=wx.ID_HELP)
			self.menuBar.Append(self.helpMenu, "&Help")

		self.SetMenuBar(self.menuBar)
		
		self.SetBackgroundColour( wx.Colour(232,232,232) )
		
		self.focusDialog = FocusDialog( self )
		self.photoDialog = PhotoDialog( self )
		self.autoCaptureDialog = AutoCaptureDialog( self )
		self.triggerDialog = TriggerDialog( self )
				
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		#------------------------------------------------------------------------------------------------
		headerSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.logo = Utils.GetPngBitmap('CrossMgrHeader.png')
		headerSizer.Add( wx.StaticBitmap(self, wx.ID_ANY, self.logo) )
		
		self.title = wx.StaticText(self, label='CrossMgr Video\nVersion {}'.format(AppVerName.split()[1]), style=wx.ALIGN_RIGHT )
		self.title.SetFont( wx.Font( (0,28), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ) )
		headerSizer.Add( self.title, flag=wx.ALL, border=10 )
		
		clock = Clock( self, size=(90,90) )
		clock.SetBackgroundColour( self.GetBackgroundColour() )
		clock.Start()

		headerSizer.Add( clock, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, border=4 )
		
		#------------------------------------------------------------------------------
		self.cameraDevice = wx.StaticText( self )
		self.cameraResolution = wx.StaticText( self )
		self.targetFPS = wx.StaticText( self, label='30 fps' )
		self.actualFPS = wx.StaticText( self, label='30.0 fps' )
		self.frameShape = (0,0,0)
		
		boldFont = self.cameraDevice.GetFont()
		boldFont.SetWeight( wx.BOLD )
		for w in (self.cameraDevice, self.cameraResolution, self.targetFPS, self.actualFPS):
			w.SetFont( boldFont )
		
		fgs = wx.FlexGridSizer( 2, 2, 2 )	# 2 Cols
		fgs.Add( wx.StaticText(self, label='Camera Device:'), flag=wx.ALIGN_RIGHT )
		fgs.Add( self.cameraDevice )
		
		fgs.Add( wx.StaticText(self, label='Resolution:'), flag=wx.ALIGN_RIGHT )
		fgs.Add( self.cameraResolution )
		
		fgs.Add( wx.StaticText(self, label='Target:'), flag=wx.ALIGN_RIGHT )
		fgs.Add( self.targetFPS, flag=wx.ALIGN_RIGHT )
		
		fgs.Add( wx.StaticText(self, label='Actual:'), flag=wx.ALIGN_RIGHT )
		fgs.Add( self.actualFPS, flag=wx.ALIGN_RIGHT )
		
		self.focus = wx.Button( self, label="Focus..." )
		self.focus.Bind( wx.EVT_BUTTON, self.onFocus )
		
		self.reset = wx.Button( self, label="Reset Camera" )
		self.reset.Bind( wx.EVT_BUTTON, self.resetCamera )
		
		self.manage = wx.Button( self, label="Manage Database" )
		self.manage.Bind( wx.EVT_BUTTON, self.manageDatabase )
		
		self.autoCaptureBtn = wx.Button( self, label="Config Auto Capture" )
		self.autoCaptureBtn.Bind( wx.EVT_BUTTON, self.autoCaptureConfig )
		
		self.help = wx.Button( self, wx.ID_HELP )
		self.help.Bind( wx.EVT_BUTTON, self.onHelp )
		
		self.snapshot, self.autoCapture, self.capture = CreateCaptureButtons( self )
		
		self.snapshot.Bind( wx.EVT_LEFT_DOWN, self.onStartSnapshot )
		self.focusDialog.snapshot.Bind( wx.EVT_LEFT_DOWN, self.onStartSnapshot )
		self.autoCapture.Bind( wx.EVT_LEFT_DOWN, self.onStartAutoCapture )
		self.focusDialog.autoCapture.Bind( wx.EVT_LEFT_DOWN, self.onStartAutoCapture )
		self.capture.Bind( wx.EVT_LEFT_DOWN, self.onStartCapture )
		self.capture.Bind( wx.EVT_LEFT_UP, self.onStopCapture )
		self.focusDialog.capture.Bind( wx.EVT_LEFT_DOWN, self.onStartCapture )
		self.focusDialog.capture.Bind( wx.EVT_LEFT_UP, self.onStopCapture )
		
		headerSizer.Add( fgs, flag=wx.ALIGN_CENTER_VERTICAL )
		
		fgs = wx.FlexGridSizer( rows=2, cols=0, hgap=8, vgap=4 )
		
		fgs.Add( self.focus, flag=wx.EXPAND )
		fgs.Add( self.reset, flag=wx.EXPAND )
		fgs.Add( self.manage, flag=wx.EXPAND )
		fgs.Add( self.autoCaptureBtn, flag=wx.EXPAND )
		fgs.Add( self.help, flag=wx.EXPAND )
		
		headerSizer.Add( fgs, flag=wx.ALIGN_CENTRE|wx.LEFT, border=4 )
		headerSizer.AddStretchSpacer()
		
		headerSizer.Add( self.snapshot, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		headerSizer.Add( self.autoCapture, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		headerSizer.Add( self.capture, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT|wx.RIGHT, border=8 )

		#------------------------------------------------------------------------------
		mainSizer.Add( headerSizer, flag=wx.EXPAND )
		
		#------------------------------------------------------------------------------------------------
		self.finishStrip = FinishStripPanel( self, size=(-1,wx.GetDisplaySize()[1]//2) )
		self.finishStrip.finish.Bind( wx.EVT_RIGHT_DOWN, self.onRightClick )
		
		self.primaryBitmap = ScaledBitmap( self, style=wx.BORDER_SUNKEN, size=(int(imageWidth*0.75), int(imageHeight*0.75)) )
		self.primaryBitmap.SetTestBitmap()
		self.primaryBitmap.Bind( wx.EVT_LEFT_UP, self.onFocus )
		self.primaryBitmap.Bind( wx.EVT_RIGHT_UP, self.onFocus )
		
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
		
		self.publishPhotos = wx.Button( self, label="Publish Photos" )
		self.publishPhotos.SetToolTip( "Write a JPG for each Trigger into a Folder" )
		self.publishPhotos.Bind( wx.EVT_BUTTON, self.onPublishPhotos )
		hsDate.Add( self.publishPhotos, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=32 )
		
		self.tsQueryLower = datetime(tQuery.year, tQuery.month, tQuery.day)
		self.tsQueryUpper = self.tsQueryLower + timedelta(days=1)
		self.bibQuery = None
		
		self.triggerList = AutoWidthListCtrl( self, style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_SORT_ASCENDING|wx.LC_HRULES )
		
		self.il = wx.ImageList(16, 16)
		self.sm_close = []
		for bm in getCloseFinishBitmaps():
			self.sm_close.append( self.il.Add(bm) )
		self.sm_up = self.il.Add( Utils.GetPngBitmap('SmallUpArrow.png'))
		self.sm_up = self.il.Add( Utils.GetPngBitmap('SmallUpArrow.png'))
		self.sm_dn = self.il.Add( Utils.GetPngBitmap('SmallDownArrow.png'))
		self.triggerList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		self.fieldCol = {f:c for c, f in enumerate('ts bib name team wave race_name note kmh mph frames'.split())}
		headers = ['Time', 'Bib', 'Name', 'Team', 'Wave', 'Race', 'Note', 'km/h', 'mph', 'Frames']
		for i, h in enumerate(headers):
			self.triggerList.InsertColumn(
				i, h,
				wx.LIST_FORMAT_RIGHT if h in ('Bib','km/h','mph','Frames') else wx.LIST_FORMAT_LEFT
			)
		self.itemDataMap = {}
		
		self.triggerList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.onTriggerSelected )
		self.triggerList.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.onTriggerEdit )
		self.triggerList.Bind( wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onTriggerRightClick )
		#self.triggerList.Bind( wx.EVT_LIST_DELETE_ITEM, self.onTriggerDelete )
		
		vsTriggers = wx.BoxSizer( wx.VERTICAL )
		vsTriggers.Add( hsDate )
		vsTriggers.Add( self.triggerList, 1, flag=wx.EXPAND|wx.TOP, border=2)
		
		#------------------------------------------------------------------------------------------------
		mainSizer.Add( self.finishStrip, 1, flag=wx.EXPAND )
		
		border=2
		row1Sizer = wx.BoxSizer( wx.HORIZONTAL )
		row1Sizer.Add( self.primaryBitmap, flag=wx.ALL, border=border )
		row1Sizer.Add( vsTriggers, 1, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.EXPAND, border=border )
		mainSizer.Add( row1Sizer, flag=wx.EXPAND )
				
		self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

		self.readOptions()
		self.updateFPS( int(float(self.targetFPS.GetLabel().split()[0])) )
		self.updateAutoCaptureLabel()
		self.SetSizerAndFit( mainSizer )
		
		# Add joystick capture.  Trigger capture while button 1 on the joystick is pressed.
		self.capturing = False
		self.joystick = wx.adv.Joystick()
		self.joystick.SetCapture( self )
		self.Bind(wx.EVT_JOY_BUTTON_DOWN, self.OnJoystickButton)
		self.Bind(wx.EVT_JOY_BUTTON_UP, self.OnJoystickButton)
		
		# Add keyboard accellerators.

		idStartAutoCapture = wx.NewId()
		idToggleCapture = wx.NewId()
		
		entries = [wx.AcceleratorEntry()]
		entries[0].Set(wx.ACCEL_CTRL, ord('A'), idStartAutoCapture)

		self.Bind(wx.EVT_MENU, self.onStartAutoCaptureAccel, id=idStartAutoCapture)		
		self.SetAcceleratorTable( wx.AcceleratorTable(entries) )

		# Start the message reporting thread so we can see what is going on.
		self.messageThread = threading.Thread( target=self.showMessages )
		self.messageThread.daemon = True
		self.messageThread.start()
		
		wx.CallLater( 300, self.refreshTriggers )
	
	def OnAboutBox(self, e):
			description = """CrossMgrVideo is an Impinj interface to CrossMgr
	"""

			licence = """CrossMgrVideo free software; you can redistribute 
	it and/or modify it under the terms of the GNU General Public License as 
	published by the Free Software Foundation; either version 2 of the License, 
	or (at your option) any later version.

	CrossMgrImpinj is distributed in the hope that it will be useful, 
	but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
	See the GNU General Public License for more details. You should have 
	received a copy of the GNU General Public License along with File Hunter; 
	if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
	Suite 330, Boston, MA  02111-1307  USA"""

			info = wx.adv.AboutDialogInfo()

			crossMgrPng = Utils.getImageFolder() + '/CrossMgrVideo.png'
			info.SetIcon(wx.Icon(crossMgrPng, wx.BITMAP_TYPE_PNG))
			info.SetName('CrossMgrVideo')
			info.SetVersion(AppVerName.split(' ')[1])
			info.SetDescription(description)
			info.SetCopyright('(C) 2020 Edward Sitarski')
			info.SetWebSite('http://www.sites.google.com/site/crossmgrsoftware/')
			info.SetLicence(licence)

			wx.adv.AboutBox(info, self)

	def onHelp( self, event ):
		OpenHelp()
	
	def setFPS( self, fps ):
		self.fps = int(fps if fps > 0 else 30)
		self.frameDelay = 1.0 / self.fps
		self.frameCountUpdate = int(self.fps * 2)
	
	def updateFPS( self, fps ):
		self.setFPS( fps )
		self.targetFPS.SetLabel( u'{} fps'.format(self.fps) )

	def updateActualFPS( self, actualFPS ):
		self.actualFPS.SetLabel( '{:.1f} fps'.format(actualFPS) )

	def updateAutoCaptureLabel( self ):
		def f( n ):
			s = '{:0.1f}'.format( n )
			return s[:-2] if s.endswith('.0') else s
		
		label = u'\n'.join( [u'AUTO',u'CAPTURE',u'{} .. {}'.format(f(-self.tdCaptureBefore.total_seconds()), f(self.tdCaptureAfter.total_seconds()))] )
		for btn in (self.autoCapture, self.focusDialog.autoCapture):
			btn.SetLabel( label )
			btn.SetFontToFitLabel()
			wx.CallAfter( btn.Refresh )

	def setQueryDate( self, d ):
		self.tsQueryLower = d
		self.tsQueryUpper = self.tsQueryLower + timedelta( days=1 )
		self.refreshTriggers( True )
		wx.CallAfter( self.date.SetValue, wx.DateTime(d.day, d.month-1, d.year) )
		
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
		
	def onPublishPhotos( self, event ):
		with wx.DirDialog(self, 'Folder to write Photos') as dlg:
			if dlg.ShowModal() == wx.ID_OK:				
				def write_photos( dirname, infoList, dbFName, fps ):
					db = Database( dbFName, initTables=False, fps=fps )
					for info in infoList:
						tsBest, jpgBest = db.getPhotoClosest( info['ts'] )
						if jpgBest is None:
							continue
						args = {k:info[k] for k in ('ts', 'first_name', 'last_name', 'team', 'race_name', 'kmh')}
						try:
							args['raceSeconds'] = (info['ts'] - info['ts_start']).total_seconds()
						except:
							args['raceSeconds'] = None
						jpg = CVUtil.bitmapToJPeg( AddPhotoHeader(CVUtil.jpegToBitmap(jpgBest), **args) )
						fname = Utils.RemoveDisallowedFilenameChars( '{:04d}-{}-{},{}.jpg'.format(
								info['bib'],
								info['ts'].strftime('%Y%m%dT%H%M%S'),
								info['last_name'],
								info['first_name'],
							)
						)
						comment = json.dumps( {k:info[k] for k in ('bib', 'first_name', 'last_name', 'team', 'race_name')} )
						try:
							with open(os.path.join(dirname, fname), 'wb') as f:
								f.write( AddExifToJpeg(jpg, info['ts'], comment) )
						except:
							pass
				
				# Start a thread so we don't slow down the main capture loop.
				args = (
					dlg.GetPath(),
					list( self.getTriggerInfo(row) for row in range(self.triggerList.GetItemCount()) ),
					self.db.fname,
					self.db.fps,
				)
				threading.Thread( target=write_photos, args=args, name='write_photos', daemon=True ).start()
				
	def GetListCtrl( self ):
		return self.triggerList
	
	def GetSortImages(self):
		return (self.sm_dn, self.sm_up)
	
	def getItemData( self, i ):
		data = self.triggerList.GetItemData( i )
		return self.itemDataMap[data]
	
	def getTriggerRowFromID( self, id ):
		for row in range(self.triggerList.GetItemCount()-1, -1, -1):
			if self.itemDataMap[row][0] == id:
				return row
		return None

	def updateTriggerRow( self, row, fields ):
		if 'last_name' in fields and 'first_name' in fields:
			fields['name'] = u', '.join( n for n in (fields['last_name'], fields['first_name']) if n )
		for k, v in fields.items():
			if k in self.fieldCol:
				if k == 'bib':
					v = u'{:>6}'.format(v)
				elif k == 'frames':
					v = '{}'.format(v) if v else u''
				else:
					v = '{}'.format(v)
				self.triggerList.SetItem( row, self.fieldCol[k], v )
				
	def updateTriggerRowID( self, id, fields ):
		row = self.getTriggerRowFromID( id )
		if row is not None:
			self.updateTriggerRow( row, fields )
	
	def getTriggerInfo( self, row ):
		data = self.itemDataMap[self.triggerList.GetItemData(row)]
		return {
			a:data[i] for i, a in enumerate((
				'id','ts','s_before','s_after','ts_start',
				'bib','name','team','wave','race_name',
				'first_name','last_name','note','kmh','frames'))
		}
	
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
			self.tsMax = triggers[-1][1] # id,ts,s_before,s_after,ts_start,bib,first_name,last_name,team,wave,race_name,note,kmh,frames
		
		zeroFrames, tsLower, tsUpper = [], datetime.max, datetime.min
		for i, (id,ts,s_before,s_after,ts_start,bib,first_name,last_name,team,wave,race_name,note,kmh,frames) in enumerate(triggers):
			if s_before == 0.0 and s_after == 0.0:
				s_before,s_after = tdCaptureBeforeDefault.total_seconds(),tdCaptureAfterDefault.total_seconds()
			
			dtFinish = (ts-tsPrev).total_seconds()
			itemImage = self.sm_close[min(len(self.sm_close)-1, int(len(self.sm_close) * dtFinish / closeFinishThreshold))]		
			row = self.triggerList.InsertItem( 999999, ts.strftime('%H:%M:%S.%f')[:-3], itemImage )
			
			if not frames:
				tsLower = min( tsLower, ts-timedelta(seconds=s_before) )
				tsU = ts + timedelta(seconds=s_after)
				tsUpper = max( tsUpper,tsU )
				zeroFrames.append( (row, id, tsU) )
			
			kmh_text, mph_text = (u'{:.2f}'.format(kmh), u'{:.2f}'.format(kmh * 0.621371)) if kmh else (u'', u'')
			fields = {
				'bib':			bib,
				'last_name':	last_name,
				'first_name':	first_name,
				'team':			team,
				'wave':			wave,
				'race_name':	race_name,
				'note':			note,
				'kmh':			kmh_text,
				'mph':			mph_text,
				'frames':		frames,
			}
			self.updateTriggerRow( row, fields )
			
			self.triggerList.SetItemData( row, row )
			self.itemDataMap[row] = (id,ts,s_before,s_after,ts_start,bib,fields['name'],team,wave,race_name,first_name,last_name,note,kmh,frames)
			tsPrev = ts
		
		if zeroFrames:
			counts = self.db.getTriggerPhotoCounts( tsLower, tsUpper )
			values = {'frames':0}
			for row, id, tsU in zeroFrames:
				values['frames'] = counts[id]
				self.updateTriggerRow( row, values )
				# Don't update the trigger if the number of frames is possibly not known yet.
				if (tNow - tsU).total_seconds() < 5.0*60.0:
					del counts[id]
			self.db.updateTriggerPhotoCounts( counts )
			
		for i in range(self.triggerList.GetColumnCount()):
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

	def updateSnapshot( self, t, f ):
		self.snapshotCount = getattr(self, 'snapshotCount', 0) + 1
		self.dbWriterQ.put( ('photo', t, f) )
		self.dbWriterQ.put( (
			'trigger',
			t,
			0.00001,		# s_before
			0.00001,		# s_after
			t,
			self.snapshotCount,	# bib
			u'', 			# first_name
			u'Snapshot',	# last_name
			u'',			# team
			u'',			# save
			u'',			# race_name
		) )
		self.doUpdateAutoCapture( t, self.snapshotCount, [self.snapshot, self.focusDialog.snapshot], snapshotEnableColour )
		
	def onStartSnapshot( self, event ):
		event.GetEventObject().SetForegroundColour( snapshotDisableColour )
		wx.CallAfter( event.GetEventObject().Refresh )
		self.camInQ.put( {'cmd':'snapshot'} )
		
	def doUpdateAutoCapture( self, tStartCapture, count, btn, colour ):
		self.dbWriterQ.put( ('flush',) )
		self.dbWriterQ.join()
		triggers = self.db.getTriggers( tStartCapture, tStartCapture, count )
		if triggers:
			id = triggers[0][0]
			self.db.initCaptureTriggerData( id )
			self.refreshTriggers( iTriggerRow=999999, replace=True )
			self.showLastTrigger()
			self.onTriggerSelected( iTriggerSelect=self.triggerList.GetItemCount()-1 )
		for b in (btn if isinstance(btn, list) else [btn]):
			b.SetForegroundColour( colour )
			wx.CallAfter( b.Refresh )

	def onStartAutoCaptureAccel( self, event ):
		event.SetEventObject( self.autoCapture )
		self.onStartAutoCapture( event )

	def onStartAutoCapture( self, event ):
		tNow = now()
		
		event.GetEventObject().SetForegroundColour( autoCaptureDisableColour )
		wx.CallAfter( event.GetEventObject().Refresh )
		
		self.autoCaptureCount = getattr(self, 'autoCaptureCount', 0) + 1
		s_before, s_after = self.tdCaptureBefore.total_seconds(), self.tdCaptureAfter.total_seconds()
		self.requestQ.put( {
				'time':tNow,
				's_before':s_before,
				's_after':s_after,
				'ts_start':tNow,
				'bib':self.autoCaptureCount,
				'last_name':u'Auto',
			}
		)
		
		wx.CallLater( int(CamServer.EstimateQuerySeconds(tNow, s_before, s_after, self.fps)*1000.0) + 80,
			self.doUpdateAutoCapture, tNow, self.autoCaptureCount, self.autoCapture, autoCaptureEnableColour
		)
		
	def onToggleCapture( self, event ):
		self.capturing ^= True

		event.SetEventObject( self.capture )
		if self.capturing:
			self.onStartCapture( event )
		else:
			self.onStopCapture( event )

	def OnJoystickButton( self, event ):
		startCaptureBtn	= event.ButtonIsDown( wx.JOY_BUTTON1 )
		autoCaptureBtn	= event.ButtonIsDown( wx.JOY_BUTTON2 )

		if startCaptureBtn:
			if not self.capturing:
				self.capturing = True
				event.SetEventObject( self.capture )
				self.onStartCapture( event )
			return
			
		if not startCaptureBtn:
			if self.capturing:
				self.capturing = False
				event.SetEventObject( self.capture )
				self.onStopCapture( event )

		if autoCaptureBtn:
			event.SetEventObject( self.autoCapture )
			self.onStartAutoCapture( event )
	
	def onStartCapture( self, event ):
		tNow = self.tStartCapture = now()
		
		event.GetEventObject().SetForegroundColour( captureDisableColour )
		wx.CallAfter( event.GetEventObject().Refresh )
		wx.BeginBusyCursor()
		
		self.captureCount = getattr(self, 'captureCount', 0) + 1
		self.requestQ.put( {
				'time':tNow,
				's_before':0.0,
				's_after':self.tdCaptureAfter.total_seconds(),
				'ts_start':tNow,
				'bib':self.captureCount,
				'last_name':u'Capture',
			}
		)
		self.camInQ.put( {'cmd':'start_capture', 'tStart':tNow-self.tdCaptureBefore} )
	
	def showLastTrigger( self ):
		iTriggerRow = self.triggerList.GetItemCount() - 1
		if iTriggerRow < 0:
			return
		self.triggerList.EnsureVisible( iTriggerRow )
		for r in range(self.triggerList.GetItemCount()-1):
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
			self.db.initCaptureTriggerData( id )
			self.refreshTriggers( iTriggerRow=999999, replace=True )
		
		self.showLastTrigger()
		
		wx.EndBusyCursor()
		event.GetEventObject().SetForegroundColour( captureEnableColour )
		wx.CallAfter( event.GetEventObject().Refresh )
		
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
			self.tdCaptureBefore = timedelta(seconds=s_before) if s_before is not None else tdCaptureBeforeDefault
			self.tdCaptureAfter  = timedelta(seconds=s_after)  if s_after  is not None else tdCaptureAfterDefault
			self.writeOptions()
			self.updateAutoCaptureLabel()
 		
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
		self.photoDialog.set( self.finishStrip.finish.getIJpg(self.xFinish), self.triggerInfo, self.finishStrip.GetTsJpgs(), self.fps,
			self.doTriggerEdit
		)
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
		self.triggerInfo = self.getTriggerInfo( self.iTriggerSelect )
		self.ts = self.triggerInfo['ts']
		s_before, s_after = abs(self.triggerInfo['s_before']), abs(self.triggerInfo['s_after'])
		if s_before == 0.0 and s_after == 0.0:
			s_before, s_after = tdCaptureBeforeDefault.total_seconds(), tdCaptureAfterDefault.total_seconds()
		
		# Update the screen in the background so we don't freeze the UI.
		def updateFS( triggerInfo ):
			self.ts = triggerInfo['ts']
			self.tsJpg = self.db.clone().getPhotos( self.ts - timedelta(seconds=s_before), self.ts + timedelta(seconds=s_after) )
			triggerInfo['frames'] = len(self.tsJpg)
			wx.CallAfter( self.finishStrip.SetTsJpgs, self.tsJpg, self.ts, triggerInfo )
			
		threading.Thread( target=updateFS, args=(self.triggerInfo,) ).start()
	
	def onTriggerRightClick( self, event ):
		self.iTriggerSelect = event.Index
		if not hasattr(self, "triggerDeleteID"):
			self.triggerDeleteID = wx.NewId()
			self.triggerEditID = wx.NewId()
			self.Bind(wx.EVT_MENU, lambda event: self.doTriggerDelete(), id=self.triggerDeleteID)
			self.Bind(wx.EVT_MENU, lambda event: self.doTriggerEdit(),   id=self.triggerEditID)

		menu = wx.Menu()
		menu.Append(self.triggerEditID,   "Edit...")
		menu.Append(self.triggerDeleteID, "Delete...")

		self.PopupMenu(menu)
		menu.Destroy()
		
	def doTriggerDelete( self, confirm=True ):
		triggerInfo = self.getTriggerInfo( self.iTriggerSelect )
		message = u', '.join( f for f in (triggerInfo['ts'].strftime('%H:%M:%S.%f')[:-3], '{}'.format(triggerInfo['bib']),
			triggerInfo['name'], triggerInfo['team'], triggerInfo['wave'], triggerInfo['race_name']) if f )
		if not confirm or wx.MessageDialog( self, u'{}:\n\n{}'.format(u'Confirm Delete', message), u'Confirm Delete',
				style=wx.OK|wx.CANCEL|wx.ICON_QUESTION ).ShowModal() == wx.ID_OK:		
			self.db.deleteTrigger( triggerInfo['id'], self.tdCaptureBefore.total_seconds(), self.tdCaptureAfter.total_seconds() )
			self.refreshTriggers( replace=True, iTriggerRow=self.iTriggerSelect )
	
	def onTriggerDelete( self, event ):
		self.iTriggerSelect = event.Index
		self.doTriggerDelete()
		
	def doTriggerEdit( self ):
		data = self.itemDataMap[self.triggerList.GetItemData(self.iTriggerSelect)]
		self.triggerDialog.set( self.db, data[0] )
		self.triggerDialog.CenterOnParent()
		if self.triggerDialog.ShowModal() == wx.ID_OK:
			row = self.iTriggerSelect
			fields = {f:v for f, v in zip(Database.triggerEditFields,self.triggerDialog.get())}
			self.updateTriggerRow( row, fields )
			self.triggerInfo.update( fields )
		return self.triggerInfo
	
	def onTriggerEdit( self, event ):
		self.iTriggerSelect = event.Index
		self.doTriggerEdit()
	
	def showMessages( self ):
		while 1:
			message = self.messageQ.get()
			assert len(message) == 2, 'Incorrect message length'
			cmd, info = message
			print( 'Message:', '{}:  {}'.format(cmd, info) if cmd else info )
			#wx.CallAfter( self.messageManager.write, '{}:  {}'.format(cmd, info) if cmd else info )
	
	def delayRefreshTriggers( self ):
		if not hasattr(self, 'refreshTimer') or not self.refreshTimer.IsRunning():
			self.resetTimer = wx.CallLater( 1000, self.refreshTriggers )

	def startThreads( self ):
		self.grabFrameOK = False
		
		self.listenerThread = SocketListener( self.requestQ, self.messageQ )
		error = self.listenerThread.test()
		if error:
			wx.MessageBox('Socket Error:\n\n"{}" group={}, port={}\n\nIs another CrossMgrVideo or CrossMgrCamera running on this computer?'.format(
					error,
					multicast_group, multicast_port,
				),
				"Socket Error",
				wx.OK | wx.ICON_ERROR
			)
			# wx.Exit()
		
		self.camInQ, self.camReader = CamServer.getCamServer( self.getCameraInfo() )
		self.cameraThread = threading.Thread( target=self.processCamera )
		self.cameraThread.daemon = True
		
		self.eventThread = threading.Thread( target=self.processRequests )
		self.eventThread.daemon = True
		
		self.dbWriterThread = threading.Thread( target=DBWriter, args=(self.dbWriterQ, lambda: wx.CallAfter(self.delayRefreshTriggers), self.db.fname) )
		self.dbWriterThread.daemon = True
		
		self.cameraThread.start()
		self.eventThread.start()
		self.dbWriterThread.start()
		self.listenerThread.start()
		
		self.grabFrameOK = True
		self.messageQ.put( ('threads', 'Successfully Launched') )
		
		self.primaryFreq = 5
		self.camInQ.put( {'cmd':'send_update', 'name':'primary', 'freq':self.primaryFreq} )
		return True
	
	def stopCapture( self ):
		self.dbWriterQ.put( ('flush',) )
	
	def processCamera( self ):
		lastFrame = None
		lastPrimaryTime = now()
		primaryCount = 0
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
						wx.CallAfter( self.primaryBitmap.SetBitmap, CVUtil.frameToBitmap(lastFrame) )
						
						primaryCount += self.primaryFreq
						primaryTime = now()
						primaryDelta = (primaryTime - lastPrimaryTime).total_seconds()
						if primaryDelta > 2.5:
							wx.CallAfter( self.updateActualFPS, primaryCount / primaryDelta )
							lastPrimaryTime = primaryTime
							primaryCount = 0
							
					elif name == 'focus':
						if self.focusDialog.IsShown():
							wx.CallAfter( self.focusDialog.SetBitmap, CVUtil.frameToBitmap(lastFrame) )
						else:
							self.camInQ.put( {'cmd':'cancel_update', 'name':'focus'} )
					
					if lastFrame.shape != self.frameShape:
						self.frameShape = lastFrame.shape
						wx.CallAfter( self.setCameraResolution, self.frameShape[1], self.frameShape[0] )
			
			elif cmd == 'snapshot':
				lastFrame = lastFrame if msg['frame'] is None else msg['frame']
				wx.CallAfter( self.updateSnapshot,  msg['ts'], lastFrame )
			elif cmd == 'terminate':
				break
		
	def processRequests( self ):
		def refresh():
			self.dbWriterQ.put( ('flush',) )
	
		while 1:
			msg = self.requestQ.get()
			
			tSearch = msg['time']
			advanceSeconds = msg.get('advanceSeconds', 0.0)
			tSearch += timedelta(seconds=advanceSeconds)
			
			# Record this trigger.
			self.dbWriterQ.put( (
				'trigger',
				tSearch - timedelta(seconds=advanceSeconds),
				msg.get('s_before', self.tdCaptureBefore.total_seconds()),	# Use the configured capture interval, not the default.
				msg.get('s_after', self.tdCaptureAfter.total_seconds()),
				msg.get('ts_start', None) or now(),
				msg.get('bib', 99999),
				msg.get('first_name',u'') or msg.get('firstName',u''),
				msg.get('last_name',u'') or msg.get('lastName',u''),
				msg.get('team',u''),
				msg.get('wave',u''),
				msg.get('race_name',u'') or msg.get('raceName',u''),
			) )
			# Record the video frames for the trigger.
			tStart, tEnd = tSearch-self.tdCaptureBefore, tSearch+self.tdCaptureAfter
			self.camInQ.put( { 'cmd':'query', 'tStart':tStart, 'tEnd':tEnd,} )
			wx.CallAfter( wx.CallLater, max(100, int(100+1000*(tEnd-now()).total_seconds())), refresh )
	
	def shutdown( self ):
		# Ensure that all images in the queue are saved.
		if hasattr(self, 'dbWriterThread'):
			if hasattr(self, 'camInQ' ):
				self.camInQ.put( {'cmd':'terminate'} )
			self.dbWriterQ.put( ('terminate', ) )
			self.dbWriterThread.join( 2.0 )
			
	def setDBName( self, dbName ):
		if dbName != self.db.fname:
			if hasattr(self, 'dbWriterThread'):
				self.dbWriterQ.put( ('terminate', ) )
				self.dbWriterThread.join()
			try:
				self.db = Database( dbName )
			except:
				self.db = Database()
			
			self.dbWriterQ = Queue()
			self.dbWriterThread = threading.Thread( target=DBWriter, args=(self.dbWriterQ, lambda: wx.CallAfter(self.delayRefreshTriggers), self.db.fname) )
			self.dbWriterThread.daemon = True
			self.dbWriterThread.start()
	
	def resetCamera( self, event=None ):
		dlg = ConfigDialog( self, self.getCameraDeviceNum(), self.fps, self.getCameraResolution() )
		ret = dlg.ShowModal()
		cameraDeviceNum = dlg.GetCameraDeviceNum()
		cameraResolution = dlg.GetCameraResolution()
		fps = dlg.GetFPS()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return False
		
		info = {'usb':cameraDeviceNum, 'fps':fps, 'width':cameraResolution[0], 'height':cameraResolution[1]}
		self.camInQ.put( {'cmd':'cam_info', 'info':info} )			

		self.setCameraDeviceNum( cameraDeviceNum )
		self.updateFPS( fps )		
		self.GetSizer().Layout()

		self.writeOptions()
		return True
	
	def manageDatabase( self, event ):
		trigFirst, trigLast = self.db.getTimestampRange()
		dlg = ManageDatabase( self, self.db.getsize(), self.db.fname, trigFirst, trigLast, title='Manage Database' )
		if dlg.ShowModal() == wx.ID_OK:
			work = wx.BusyCursor()
			tsLower, tsUpper, vacuum, dbName = dlg.GetValues()
			self.setDBName( dbName )
			if tsUpper:
				tsUpper = datetime.combine( tsUpper, time(23,59,59,999999) )
			self.db.cleanBetween( tsLower, tsUpper )
			if vacuum:
				self.db.vacuum()
			wx.CallAfter( self.finishStrip.Clear )
			wx.CallAfter( self.refreshTriggers, True )
		dlg.Destroy()
	
	def setCameraDeviceNum( self, num ):
		self.cameraDevice.SetLabel( '{}'.format(num) )
		
	def setCameraResolution( self, width, height ):
		self.cameraResolution.SetLabel( u'{}x{}'.format(width, height) )
			
	def getCameraDeviceNum( self ):
		return int(self.cameraDevice.GetLabel())
		
	def getCameraFPS( self ):
		return int(float(self.targetFPS.GetLabel().split()[0]))
		
	def getCameraResolution( self ):
		try:
			return pixelsFromRes( self.cameraResolution.GetLabel() )
		except:
			return 640, 480
		
	def onCloseWindow( self, event ):
		self.shutdown()
		wx.Exit()
		
	def writeOptions( self ):
		self.config.Write( 'DBName', self.db.fname )
		self.config.Write( 'CameraDevice', self.cameraDevice.GetLabel() )
		self.config.Write( 'CameraResolution', self.cameraResolution.GetLabel() )
		self.config.Write( 'FPS', self.targetFPS.GetLabel() )
		self.config.Write( 'SecondsBefore', '{:.3f}'.format(self.tdCaptureBefore.total_seconds()) )
		self.config.Write( 'SecondsAfter', '{:.3f}'.format(self.tdCaptureAfter.total_seconds()) )
		self.config.Flush()
	
	def readOptions( self ):
		self.setDBName( self.config.Read('DBName', '') )
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

	# Start processing events.
	mainWin.Start()
	wx.CallLater( 200, mainWin.resetCamera )
	app.MainLoop()

@atexit.register
def shutdown():
	if mainWin:
		mainWin.shutdown()
	
if __name__ == '__main__':
	MainLoop()
	
