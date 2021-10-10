import wx
import wx.adv
import wx.lib.mixins.listctrl as listmix
import wx.lib.intctrl
import os
import re
import sys
import cv2
import sys
import time
import math
import json
import time
import socket
import atexit
import base64
import random
import platform
import tempfile
import threading
import webbrowser
import platform
import pickle
import gzip
import sqlite3
import numpy as np
from queue import Queue, Empty

from datetime import datetime, timedelta, time

now = datetime.now

import Utils
import CVUtil
import CamServer
from Clock import Clock
from SocketListener import SocketListener
from MultiCast import multicast_group, multicast_port
from Database import GlobalDatabase, DBWriter, Database, BulkInsertDBRows
from ScaledBitmap import ScaledBitmap
from Composite import CompositePanel
from ManageDatabase import ManageDatabase
from PhotoDialog import PhotoPanel
from AddPhotoHeader import AddPhotoHeader
from AddExifToJpeg import AddExifToJpeg
from PublishPhotoOptions import PublishPhotoOptionsDialog
from roundbutton import RoundButton
from GetMyIP import GetMyIP
from FIFOCache import FIFOCacheSet
from Version import AppVerName
import WebServer

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
	
def getInfo():
	app = AppVerName.split()[0]
	uname = platform.uname()
	info = {
		'{}_AppVersion'.format(app):	AppVerName,
		'{}_Timestamp'.format(app):		datetime.now(),
		'{}_User'.format(app):			os.path.basename(os.path.expanduser("~")),
		'{}_Python'.format(app):		sys.version.replace('\n', ' '),
	}
	info.update( {'{}_{}'.format(app, a.capitalize()): getattr(uname, a)
		for a in ('system', 'release', 'version', 'machine', 'processor') if getattr(uname, a, '') } )
	return info

from CalendarHeatmap import CalendarHeatmap
class DateSelectDialog( wx.Dialog ):
	def __init__( self, parent, triggerDates, id=wx.ID_ANY, ):
		super().__init__( parent, id, title=_("Date Select") )
		
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
			self.triggerDatesList.SetItem( i, 1, str(c) )
		
		if self.triggerDates:
			self.triggerDatesList.Select( 0 )
			self.chm.SetDate( self.triggerDates[0][0] )
		
		self.triggerDatesList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.onItemSelect )
		self.triggerDatesList.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivate )
		
		btnSizer = self.CreateSeparatedButtonSizer( wx.OK|wx.CANCEL )
		
		sizer.Add( self.chm, flag=wx.ALL, border=4 )
		sizer.Add( self.triggerDatesList, flag=wx.ALL, border=4 )
		if btnSizer:
			sizer.Add( btnSizer, flag=wx.EXPAND|wx.ALL, border=4 )
		
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

FOURCC_DEFAULT = 'MJPG'

class ConfigDialog( wx.Dialog ):
	def __init__( self, parent, usb=0, fps=30, width=imageWidth, height=imageHeight, fourcc='', availableCameraUsb=None, id=wx.ID_ANY ):
		super().__init__( parent, id, title=_('CrossMgr Video Configuration') )
		
		fps = int( fps )
		availableCameraUsb = availableCameraUsb or []
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.title = wx.StaticText( self, label='CrossMgr Video Configuration' )
		self.title.SetFont( wx.Font( (0,24), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ) )
		pfgs = wx.FlexGridSizer( rows=0, cols=2, vgap=4, hgap=8 )
		
		pfgs.Add( wx.StaticText(self, label='Camera USB'+':'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.usb = wx.Choice( self, choices=['{}'.format(i) for i in range(16)] )
		self.usb.SetSelection( usb )
		hs.Add( self.usb )
		hs.Add( wx.StaticText(self, label='cameras detected on {}'.format(availableCameraUsb)), flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		pfgs.Add( hs )
		
		pfgs.Add( wx.StaticText(self, label='Camera Resolution'+':'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.cameraResolution = wx.Choice( self, choices=cameraResolutionChoices )
		self.cameraResolution.SetSelection( getCameraResolutionChoice((width, height)) )
		pfgs.Add( self.cameraResolution )
		
		pfgs.Add( wx.StaticText(self, label='Frames per second'+':'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.fps = wx.lib.intctrl.IntCtrl( self, value=fps, min=10, max=1000 )
		pfgs.Add( self.fps )
		
		pfgs.Add( wx.StaticText(self, label='FourCC'+':'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.fourccChoices = ['', FOURCC_DEFAULT]
		self.fourcc = wx.Choice( self, choices=self.fourccChoices )
		self.fourcc.SetSelection( self.fourccChoices.index(fourcc if fourcc in self.fourccChoices else FOURCC_DEFAULT) )
		pfgs.Add( self.fourcc )
		
		pfgs.AddSpacer( 1 )
		pfgs.Add( wx.StaticText(self, label='\n'.join([
				'After pressing Apply, check the "Actual" fps on the main screen.',
				'The camera may not support the frame rate at the desired resolution,',
				'or may lower the frame rate in low light.',
				"If your fps is low or your camera doesn't work, try FourCC={}.".format(FOURCC_DEFAULT),
			])), flag=wx.RIGHT, border=4 )
		
		sizer.Add( self.title, flag=wx.ALL, border=4 )
		sizer.AddSpacer( 8 )
		sizer.Add( pfgs, flag=wx.ALL, border=4 )
		
		btnSizer = self.CreateButtonSizer( wx.OK|wx.APPLY|wx.CANCEL|wx.HELP )
		self.Bind( wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_APPLY), id=wx.ID_APPLY )
		self.Bind( wx.EVT_BUTTON, lambda event: OpenHelp(), id=wx.ID_HELP )
		
		if btnSizer:
			sizer.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border=8 )
		
		self.SetSizerAndFit( sizer )
		
	def GetValues( self ):
		width, height = pixelsFromRes(cameraResolutionChoices[self.cameraResolution.GetSelection()])
		return {
			'usb':			self.usb.GetSelection(),
			'width':		width,
			'height':		height,
			'fps':			self.fps.GetValue(),
			'fourcc':		self.fourccChoices[self.fourcc.GetSelection()],
		}

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
		super().__init__( parent, id,
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
		self.explain = wx.StaticText(self, label='Click and Drag to Zoom In')
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
			self.SetTitle( '{} {}x{}'.format( _('CrossMgr Video Focus'), *sz ) )
		return self.bitmap.SetBitmap( bitmap )
		
	def SetTestBitmap( self ):
		self.bitmap.SetTestBitmap()

class TriggerDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY ):
		super().__init__( parent, id, title=_('CrossMgr Video Trigger Editor') )
		
		self.db = None
		self.triggerId = None
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		gs = wx.FlexGridSizer( 2, 2, 4 )
		gs.AddGrowableCol( 1 )
		fieldNames = [h.replace('_', ' ').title() for h in GlobalDatabase().triggerEditFields]
		self.editFields = []
		for f in fieldNames:
			gs.Add( wx.StaticText(self, label=f), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			e = wx.TextCtrl(self, size=(500,-1) )
			gs.Add( e )
			self.editFields.append(e)
		
		btnSizer = self.CreateButtonSizer( wx.OK|wx.CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onOK, id=wx.ID_OK )
		
		sizer.Add( gs, flag=wx.ALL, border=4 )
		if btnSizer:
			sizer.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border=4 )
		self.SetSizerAndFit( sizer )
	
	def set( self, db, triggerId ):
		self.db = db
		self.triggerId = triggerId
		ef = db.getTriggerEditFields( triggerId )
		for e, f in zip(self.editFields, Database.triggerEditFields):
			e.SetValue( '{}'.format(ef.get(f,'') or '') )
	
	def get( self ):
		values = {}
		for f, e in zip(Database.triggerEditFields, self.editFields):
			v = e.GetValue()
			if f == 'bib':
				try:
					v = int(v)
				except Exception:
					v = 99999
			values[f] = v
		return values
	
	def commit( self ):
		self.db.setTriggerEditFields( self.triggerId, **self.get() )
	
	def onOK( self, event ):
		self.commit()
		self.EndModal( wx.ID_OK )
		
class AutoCaptureDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY ):
		super().__init__( parent, id, title=_('CrossMgr Video Auto Capture') )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		sizer.Add( wx.StaticText(self, label="Configure what to Capture on each Trigger"), flag=wx.ALL, border=8 )

		gs = wx.FlexGridSizer( 2, 2, 4 )
		gs.AddGrowableCol( 1 )
		
		gs.Add( wx.StaticText(self, label="Capture"), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.closestFrames = wx.Choice( self, choices=('by Seconds', 'Closest Frame to Trigger', 'Closest 2 Frames to Trigger') )
		self.closestFrames.Bind( wx.EVT_CHOICE, self.onChoice )
		gs.Add( self.closestFrames )
		
		fieldNames = ('Capture Seconds Before Trigger', 'Capture Seconds After Trigger')
		self.labelFields = []
		self.editFields = []
		for f in fieldNames:
			self.labelFields.append( wx.StaticText(self, label=f) )
			gs.Add( self.labelFields[-1], flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			self.editFields.append( wx.TextCtrl(self, size=(60,-1) ) )
			gs.Add( self.editFields[-1] )
			
		sizer.Add( gs, flag=wx.ALL, border=4 )
		
		btnSizer = self.CreateButtonSizer( wx.OK|wx.CANCEL )		
		if btnSizer:
			sizer.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border=4 )
		
		self.SetSizerAndFit( sizer )
	
	def onChoice( self, event=None ):
		enable = (self.closestFrames.GetSelection() == 0)
		for w in (self.labelFields + self.editFields):
			w.Enable( enable )
	
	def set( self, s_before, s_after, closestFrames=0 ):
		for w, v in zip( self.editFields, (s_before, s_after) ):
			w.SetValue( '{:.3f}'.format(v) )
		self.closestFrames.SetSelection( closestFrames )
		self.onChoice()
	
	def get( self ):
		def fixValue( v ):
			try:
				return abs(float(v))
			except Exception:
				return None
		return [fixValue(e.GetValue()) for e in self.editFields] + [self.closestFrames.GetSelection()]
		
class AutoWidthListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID = wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

class MainWin( wx.Frame ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(1000,800) ):
		super().__init__( parent, id, title, size=size )
		
		self.db = GlobalDatabase()
		
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
		self.availableCameraUsb = []
		
		self.tdCaptureBefore = tdCaptureBeforeDefault
		self.tdCaptureAfter = tdCaptureAfterDefault
		self.closestFrames = 0

		dataDir = Utils.getHomeDir()
		configFileName = os.path.join(dataDir, 'CrossMgrVideo.cfg')
		self.config = wx.Config(appName="CrossMgrVideo",
								vendorName="Edward.Sitarski@gmail.com",
								localFilename=configFileName
		)
		
		self.requestQ = Queue()		# Select photos from photobuf.
		self.dbWriterQ = Queue()	# Photos waiting to be written
		self.messageQ = Queue()		# Collection point for all status/failure messages.
		
		#-------------------------------------------

		self.menuBar = wx.MenuBar(wx.MB_DOCKABLE)
		if 'WXMAC' in wx.Platform:
			self.appleMenu = self.menuBar.OSXGetAppleMenu()
			self.appleMenu.SetTitle("CrossMgrVideo")
			self.appleMenu.Insert(0, wx.ID_ABOUT, "&About")
			self.Bind(wx.EVT_MENU, self.OnAboutBox, id=wx.ID_ABOUT)
		else:
			self.fileMenu = wx.Menu()
			item = self.fileMenu.Append( wx.ID_EXIT, "Exit", "Exit CrossMgrVideo" )
			self.Bind(wx.EVT_MENU, self.onCloseWindow, id=wx.ID_EXIT)
			self.menuBar.Append(self.fileMenu, "&File")

		#-------------------------------------------
		self.toolsMenu = wx.Menu()
		
		item = self.toolsMenu.Append( wx.ID_ANY, "R&eset Camera", "Reset the camera configuration" )
		self.Bind(wx.EVT_MENU, self.resetCamera, item )
		
		item = self.toolsMenu.Append( wx.ID_ANY, "&Focus", "Large window to focus the camera" )
		self.Bind(wx.EVT_MENU, self.onFocus, item )

		item = self.toolsMenu.Append( wx.ID_ANY, "&Configure Autocapture", "Configure Autocapture parameters" )
		self.Bind(wx.EVT_MENU, self.autoCaptureConfig, item )

		item = self.toolsMenu.Append( wx.ID_ANY, "&Manage Database", "Manage the database" )
		self.Bind(wx.EVT_MENU, self.manageDatabase, item )
		
		self.toolsMenu.AppendSeparator()
		item = self.toolsMenu.Append( wx.ID_ANY, "Copy &Log File to Clipboard", "Copy Log File to Clipboard" )
		self.Bind(wx.EVT_MENU, self.copyLogFileToClipboard, item )

		self.toolsMenu.AppendSeparator()
		item = self.toolsMenu.Append( wx.ID_ANY, "Export Photos...", "Export all photos and triggers for the current day." )
		self.Bind(wx.EVT_MENU, self.exportDB, item )

		item = self.toolsMenu.Append( wx.ID_ANY, "Import Photos...", "Import all photos and triggers for a day." )
		self.Bind(wx.EVT_MENU, self.importDB, item )

		self.menuBar.Append(self.toolsMenu, "&Tools")

		#-------------------------------------------
		if 'WXMAC' not in wx.Platform:
			self.helpMenu = wx.Menu()
			item = self.helpMenu.Append( wx.ID_ABOUT, "&About", "About CrossMgrVideo" )
			self.Bind(wx.EVT_MENU, self.OnAboutBox, item )
			
			item = self.helpMenu.Append( wx.ID_HELP, "&Help", "CrossMgrVideo QuickHelp" )
			self.Bind(wx.EVT_MENU, self.onHelp, item )

			self.menuBar.Append(self.helpMenu, "Help")
		#-------------------------------------------

		self.SetMenuBar( self.menuBar )
		
		self.SetBackgroundColour( wx.Colour(232,232,232) )
		
		self.focusDialog = FocusDialog( self )
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
		self.usb = wx.StaticText( self )
		self.cameraResolution = wx.StaticText( self )
		self.targetFPS = wx.StaticText( self, label='30 fps' )
		self.actualFPS = wx.StaticText( self, label='30.0 fps' )
		self.fourcc = wx.StaticText( self, label=FOURCC_DEFAULT )
		
		boldFont = self.usb.GetFont()
		boldFont.SetWeight( wx.BOLD )
		for w in (self.usb, self.cameraResolution, self.targetFPS, self.actualFPS, self.fourcc):
			w.SetFont( boldFont )
		
		fgs = wx.FlexGridSizer( 2, 2, 2 )	# 2 Cols
		fgs.Add( wx.StaticText(self, label='Camera USB:'), flag=wx.ALIGN_RIGHT )
		fgs.Add( self.usb )
		
		fgs.Add( wx.StaticText(self, label='Resolution:'), flag=wx.ALIGN_RIGHT )
		fgs.Add( self.cameraResolution, flag=wx.ALIGN_RIGHT )
		
		fgs.Add( wx.StaticText(self, label='FourCC:'), flag=wx.ALIGN_RIGHT )
		fgs.Add( self.fourcc, flag=wx.ALIGN_RIGHT )
		
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
		
		self.webBtn = wx.Button( self, label="Web Page" )
		self.webBtn.Bind( wx.EVT_BUTTON, self.onWeb )
		
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
		fgs.Add( self.webBtn, flag=wx.EXPAND )
		fgs.Add( self.help, flag=wx.EXPAND )
		
		headerSizer.Add( fgs, flag=wx.ALIGN_CENTRE|wx.LEFT, border=4 )
		headerSizer.AddStretchSpacer()
		
		headerSizer.Add( self.snapshot, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		headerSizer.Add( self.autoCapture, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=8 )
		headerSizer.Add( self.capture, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT|wx.RIGHT, border=8 )

		#------------------------------------------------------------------------------
		mainSizer.Add( headerSizer, flag=wx.EXPAND )
		
		#------------------------------------------------------------------------------------------------
		self.notebook = wx.Notebook( self, size=(-1,wx.GetDisplaySize()[1]//2), style=wx.NB_BOTTOM )
		self.notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onNotebook )
		
		self.photoPanel = PhotoPanel( self.notebook )
		self.finishStrip = CompositePanel( self.notebook )
		
		self.notebook.AddPage(self.photoPanel, "Images")
		self.notebook.AddPage(self.finishStrip, "Finish Strip")
		
		self.primaryBitmap = ScaledBitmap( self, style=wx.BORDER_SUNKEN, size=(int(imageWidth*0.4), int(imageHeight*0.4)) )
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
		
		self.publishWebPage = wx.Button( self, label="Photo Web Page" )
		self.publishWebPage.SetToolTip( "Write a JPG for each Trigger and create a Web Page" )
		self.publishWebPage.Bind( wx.EVT_BUTTON, self.onPublishWebPage )
		hsDate.Add( self.publishWebPage, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=32 )
		
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
		formatRightHeaders = {'Bib','km/h','mph','Frames'}
		for i, h in enumerate(headers):
			self.triggerList.InsertColumn(
				i, h,
				wx.LIST_FORMAT_RIGHT if h in formatRightHeaders else wx.LIST_FORMAT_LEFT
			)
		self.iNoteCol = self.fieldCol['note']
		self.itemDataMap = {}
		
		self.triggerList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.onTriggerSelected )
		self.triggerList.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.onTriggerEdit )
		self.triggerList.Bind( wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onTriggerRightClick )
		#self.triggerList.Bind( wx.EVT_LIST_DELETE_ITEM, self.onTriggerDelete )
		
		vsTriggers = wx.BoxSizer( wx.VERTICAL )
		vsTriggers.Add( hsDate )
		vsTriggers.Add( self.triggerList, 1, flag=wx.EXPAND|wx.TOP, border=2)
		
		#------------------------------------------------------------------------------------------------
		mainSizer.Add( self.notebook, 1, flag=wx.EXPAND )
		
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

		idStartAutoCapture = wx.NewIdRef()
		idToggleCapture = wx.NewIdRef()
		
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
		
	def onWeb( self, event ):
		dateStrInitial = self.date.GetValue().Format('%Y-%m-%d')
		url = '{}:{}?date={}'.format( GetMyIP(), WebServer.PORT_NUMBER, dateStrInitial )
		webbrowser.open( url, new=0, autoraise=1 )
		
	def exportDB( self, event ):
		fname = os.path.join( os.path.expanduser("~"), 'CrossMgrVideo-{}.gz'.format(self.tsQueryUpper.strftime('%Y-%m-%d')) )
		with wx.MessageDialog( self,
				'Export all photos for this day.\n\n\tPhotos will be exported to:\n\n"{}"'.format(fname),
				'Photo Export',
				style=wx.OK|wx.CANCEL|wx.ICON_INFORMATION ) as dlg:
			if dlg.ShowModal() != wx.ID_OK:
				return		
		
		fname = os.path.join( os.path.expanduser("~"), 'CrossMgrVideo-{}.gz'.format(self.tsQueryUpper.strftime('%Y-%m-%d')) )
		if os.path.exists(fname):
			os.remove( fname )

		progress = wx.ProgressDialog( 'Export Progress', 'Initializing...' )
		progress.SetRange( 1 )
		progress.Show()
		wx.Yield()

		db = GlobalDatabase()
		
		triggerFields = [f for f in db.triggerFieldsAll if f != 'id']
		photoFields = ['ts', 'jpg']

		with gzip.open( fname, 'wb' ) as f:
			# Write out some info as a file header.
			pickle.dump( getInfo(), f, -1 )
			
			# Write out the fields we are using.
			pickle.dump( triggerFields, f, -1 )
			pickle.dump( photoFields, f, -1 )
			
			#-----------------------------------------------------------
			triggerTS = [row[0] for row in db.runQuery( 'SELECT ts FROM trigger WHERE ts BETWEEN ? and ? ORDER BY ts', (self.tsQueryLower, self.tsQueryUpper))]
			
			progress.SetRange( len(triggerTS) )
			progress.Update( 0, 'Exporting triggers...' )
			wx.Yield()
			
			pickle.dump( triggerTS, f, -1 )
			with db.dbLock, db.conn:
				for count, row in enumerate(db.conn.execute( 'SELECT {} FROM trigger WHERE ts BETWEEN ? AND ? ORDER BY ts'.format(','.join(triggerFields)), (self.tsQueryLower, self.tsQueryUpper) )):
					obj = {f:v for f,v in zip(triggerFields, row)}
					pickle.dump( obj, f, -1 )
					if count % 25 == 0:
						progress.Update( count, 'Exporting triggers ({}/{} {:.1f}%)...'.format(count, len(triggerTS), 100*count/max(1,len(photoTS))) )
						wx.Yield()
		
			#-----------------------------------------------------------
			# Purge duplicates.
			photoTS = sorted(set(row[0] for row in db.runQuery( 'SELECT ts FROM photo WHERE ts BETWEEN ? and ?', (self.tsQueryLower, self.tsQueryUpper))))
			
			progress.SetRange( len(photoTS) )
			progress.Update( 0, 'Exporting Photos...' )
			wx.Yield()
			
			pickle.dump( photoTS, f, -1 )
			with db.dbLock, db.conn:
				tsSeen = set()
				count = 0
				for row in db.conn.execute( 'SELECT {} FROM photo WHERE ts BETWEEN ? AND ? ORDER BY ts'.format(','.join(photoFields)), (self.tsQueryLower, self.tsQueryUpper) ):
					if row[0] not in tsSeen:
						tsSeen.add( row[0] )
						obj = {f:v for f,v in zip(photoFields, row)}
						pickle.dump( obj, f, -1 )
						if count % 25 == 0:
							progress.Update( count, 'Exporting Photos ({}/{} {:.1f}%) ...'.format(count, len(photoTS), 100*count/max(1,len(photoTS)) ) )
							wx.Yield()
						count += 1
				
		progress.Destroy()
	
	def importDB( self, event ):
		with wx.FileDialog(self, "Open CrossMgrVideo Import file", wildcard="Files (*.gz)|*.gz",
						   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return
			fname = fileDialog.GetPath()

		# Check if the import file is valid.
		try:
			with gzip.open( fname, 'rb' ) as f:
				info = pickle.load( f )
				app = AppVerName.split()[0]
				key = '{}_AppVersion'.format(app)
				assert key in info
		except Exception as e:
			with wx.MessageDialog( self, 'Exception: {}'.format(e), 'Improper File', style=wx.OK|wx.ICON_ERROR ) as dlg:
				dlg.ShowModal()
				return
	
		progress = wx.ProgressDialog( 'Import Progress', 'Initializing...' )
		progress.SetRange( 1 )
		progress.Show()
		wx.Yield()
		
		def getUpdateCB( msg ):
			def updateCB( count, total ):
				progress.Update( count, msg.format(count, total, 100*count/max(1,total)) )
				wx.Yield()
			return updateCB

		db = GlobalDatabase()
		
		with gzip.open( fname, 'rb' ) as f:
			info = pickle.load( f )

			# Read the fields used to write the export file.
			triggerFields = pickle.load( f )
			photoFields = pickle.load( f )
			
			# For compatability, ensure there are no unexpected import fields.
			triggerFieldsSet = set( f for f in db.triggerFieldsAll if f != 'id' )
			triggerFields = [f for f in triggerFields if f in triggerFieldsSet]

			
			#-----------------------------------------------------------
			triggerTS = pickle.load( f )
			
			progress.SetRange( len(triggerTS) )
			progress.Update( 0, 'Removing exisiting triggers...' )
			wx.Yield()
			
			db.deleteTss( 'trigger', triggerTS, getUpdateCB('Removing exisiting triggers ({}/{})...') )
			
			progress.Update( 0, 'Importing triggers...' )
			wx.Yield()
			
			with BulkInsertDBRows( 'trigger', triggerFields, db ) as bid:
				for count in range(len(triggerTS)):
					obj = pickle.load( f )
					bid.append( [obj[f] for f in triggerFields] )
					if count % 25 == 0:
						progress.Update( count, 'Importing Triggers ({}/{} {:.1f}%)...'.format(count, len(triggerTS)) )
						wx.Yield()
		
			#-----------------------------------------------------------
			photoTS = pickle.load( f )
			print( photoTS )
			
			progress.SetRange( len(photoTS) )
			progress.Update( 0, 'Removing exisiting photos...' )
			wx.Yield()
			
			db.deleteTss( 'photo', photoTS, getUpdateCB('Removing exisiting photos ({}/{})...')  )
			
			progress.Update( 0, 'Importing photos...' )
			wx.Yield()

			with BulkInsertDBRows( 'photo', photoFields, db ) as bid:
				for count in range(len(photoTS)):
					obj = pickle.load( f )
					obj['jpg'] = sqlite3.Binary( obj['jpg'] )
					bid.append( [obj[f] for f in photoFields] )
					if count % 25 == 0:
						progress.Update( count, 'Importing Photos ({}/{} {:.1f}%) ...'.format(count, len(photoTS)) )
						wx.Yield()
				
		progress.Destroy()
		self.refreshTriggers( replace=True )
	
	def setFPS( self, fps ):
		self.fps = int(fps if fps > 0 else 30)
		self.frameDelay = 1.0 / self.fps
		self.frameCountUpdate = int(self.fps * 2)
	
	def updateFPS( self, fps ):
		self.setFPS( fps )
		self.targetFPS.SetLabel( '{} fps'.format(self.fps) )

	def updateActualFPS( self, actualFPS ):
		self.actualFPS.SetLabel( '{:.1f} fps'.format(actualFPS) )
		
	def updateCameraUsb( self, availableCameraUsb ):
		self.availableCameraUsb = availableCameraUsb

	def updateAutoCaptureLabel( self ):
		def f( n ):
			s = '{:0.1f}'.format( n )
			return s[:-2] if s.endswith('.0') else s
		
		if self.closestFrames:
			label = '\n'.join( ['AUTO','CAPTURE','CLOSEST {}'.format(self.closestFrames)] )
		else:
			label = '\n'.join( ['AUTO','CAPTURE','{} .. {}'.format(f(-self.tdCaptureBefore.total_seconds()), f(self.tdCaptureAfter.total_seconds()))] )
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

	def copyLogFileToClipboard( self, event ):
		logFileName = getLogFileName()
		try:
			with open(logFileName) as f:
				logData = f.read()
		except IOError:
			with wx.MessageDialog(self, "Unable to open log file.", "Error", style=wx.OK|wx.ICON_ERROR) as dlg:
				dlg.ShowModal()
			return
			
		logData = logData.split( '\n' )
		logData = logData[-1000:]
		logData = '\n'.join( logData )
		
		dataObj = wx.TextDataObject()
		dataObj.SetText( logData )
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData( dataObj )
			wx.TheClipboard.Close()
			with wx.MessageDialog(self, '\n\n'.join( ("Log file copied to clipboard.", "You can now paste it into an email.") ), "Success", style=wx.OK) as dlg:
				dlg.ShowModal()
		else:
			with wx.MessageDialog(self, "Unable to open the clipboard.", "Error", style=wx.OK|wx.ICON_ERROR) as dlg:
				dlg.ShowModal()

	def onQueryDateChanged( self, event ):
		v = self.date.GetValue()
		self.setQueryDate( datetime( v.GetYear(), v.GetMonth() + 1, v.GetDay() ) )
	
	def onQueryBibChanged( self, event ):
		self.bibQuery = self.bib.GetValue()
		self.refreshTriggers( True )
		
	def filterLastBibWave( self, infoList):
		''' Filter out all photos but the last by bib and wave. '''
		seen = set()
		infoListNew = []
		for info in reversed(infoList):
			key = (info['bib'], info['wave'])
			if key not in seen:
				seen.add( key )
				infoListNew.append( info )
		infoListNew.reverse()
		return infoListNew
		
	def refreshPhotoPanel( self ):
		self.photoPanel.playStop()
		self.photoPanel.set( self.finishStrip.getIJpg(), self.triggerInfo, self.finishStrip.GetTsJpgs(), self.fps, editCB=self.doTriggerEdit )
		wx.CallAfter( self.photoPanel.doRestoreView, self.triggerInfo )
		
	def onNotebook( self, event ):
		self.refreshPhotoPanel()
		
	def onPublishPhotos( self, event ):
		infoList = [self.getTriggerInfo(row) for row in range(self.triggerList.GetItemCount())]
		if not infoList:
			with wx.MessageDialog( self,
					"Please select a date with videos.",
					"Nothing to Publish",
					style=wx.OK ) as dlg:
				dlg.ShowModal()
				return
				
		if not hasattr(self, 'publishPhotoOptionsPhotoDialog'):
			self.publishPhotoOptionsPhotoDialog = PublishPhotoOptionsDialog( self, webPublish=False )
		if self.publishPhotoOptionsPhotoDialog.ShowModal() != wx.ID_OK:
			return
		values = self.publishPhotoOptionsPhotoDialog.GetValues()
		dirname = values['dirname']
		if not dirname:
			return
		if values['lastBibWaveOnly']:
			infoList = self.filterLastBibWave( infoList )
			
		def write_photos( dirname, infoList, dbFName, fps ):
			for info in infoList:
				tsBest, jpgBest = GlobalDatabase(dbFName).getPhotoClosest( info['ts'] )
				if jpgBest is None:
					continue
				args = {k:info[k] for k in ('ts', 'bib', 'first_name', 'last_name', 'team', 'race_name', 'kmh')}
				try:
					args['raceSeconds'] = (info['ts'] - info['ts_start']).total_seconds()
				except Exception:
					args['raceSeconds'] = None
				if isinstance(args['kmh'], str):
					args['kmh'] = float( '0' + re.sub( '[^0-9.]', '', args['kmh'] ) )
					
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
				except Exception:
					pass
		
		# Write in a thread so we don't slow down the main capture loop.
		args = (
			dirname,
			infoList,
			self.db.fname,
			self.db.fps,
		)
		threading.Thread( target=write_photos, args=args, name='write_photos', daemon=True ).start()
	
	def onPublishWebPage( self, event ):
		infoList = [self.getTriggerInfo(row) for row in range(self.triggerList.GetItemCount())]
		if not infoList:
			with wx.MessageDialog( self,
					"Please select a date with videos.",
					"Nothing to Publish",
					style=wx.OK ) as dlg:
				dlg.ShowModal()
				return
				
		if not hasattr(self, 'publishPhotoOptionsWebDialog'):
			self.publishPhotoOptionsWebDialog = PublishPhotoOptionsDialog( self, webPublish=True )
		if self.publishPhotoOptionsWebDialog.ShowModal() != wx.ID_OK:
			return
		values = self.publishPhotoOptionsWebDialog.GetValues()
		dirname = values['dirname']
		if not dirname:
			return
		singleFile = (values['htmlOption'] == 1)
		
		if values['lastBibWaveOnly']:
			infoList = self.filterLastBibWave( infoList )
			
		class DateTimeEncoder( json.JSONEncoder ):
			def default(self, o):
				if isinstance(o, datetime):
					return o.isoformat()
				return json.JSONEncoder.default(self, o)
		
		def publish_web_photos( dirname, infoList, dbFName, fps, singleFile ):
			if not infoList:
				return
			
			dateStr = infoList[0]['ts'].strftime('%Y-%m-%d')
			fname = os.path.join( dirname, '{}-index.html'.format(dateStr) )
			ftemplate = os.path.join( Utils.getHtmlFolder(), 'PhotoPage.html' )
			
			with open(fname, 'w') as fOut, open(ftemplate) as fIn:
				for line in fIn:
					
					lineStrip = line.strip()
					if lineStrip == '<script src="ScaledBitmap.js"></script>':
						fOut.write( '<script>\n' )
						with open( os.path.join(Utils.getHtmlFolder(), 'ScaledBitmap.js') ) as fsb:
							fOut.write( fsb.read() )
						fOut.write( '\n</script>\n' )
						continue
					
					if not lineStrip.startswith( 'var photo_info' ):
						fOut.write( line )
						continue
						
					# Write out all the photo info.
					fOut.write( 'var photo_info = [\n' )
					for iInfo, info in enumerate(infoList):
						tsBest, jpgBest = GlobalDatabase(dbFName).getPhotoClosest( info['ts'] )
						if jpgBest is None:
							continue
						args = {k:info[k] for k in ('ts', 'bib', 'first_name', 'last_name', 'team', 'race_name', 'kmh')}
						try:
							args['raceSeconds'] = (info['ts'] - info['ts_start']).total_seconds()
						except Exception:
							args['raceSeconds'] = None
						if isinstance(args['kmh'], str):
							args['kmh'] = float( '0' + re.sub( '[^0-9.]', '', args['kmh'] ) )

						comment = json.dumps( {k:info[k] for k in ('bib', 'first_name', 'last_name', 'team', 'race_name')} )
						jpg = CVUtil.bitmapToJPeg( AddPhotoHeader(CVUtil.jpegToBitmap(jpgBest), **args) )
						jpg = AddExifToJpeg( jpg, info['ts'], comment )

						if iInfo:
							fOut.write( ',\n' )
						
						if singleFile:
							args['photo'] = 'data:image/jpeg;base64,{}'.format( base64.standard_b64encode(jpg).decode() )
						else:
							photo_fname = '{}-{:06X}.jpeg'.format(dateStr, iInfo)
							with open(os.path.join(os.path.dirname(fname), photo_fname), 'wb') as fPhoto:
								fPhoto.write( jpg )
							args['photo'] = './{}'.format( photo_fname )
						
						json.dump( args, fOut, cls=DateTimeEncoder )
					
					fOut.write( '];\n' )
					
			webbrowser.open( fname, new=0, autoraise=1 )

		# Write in a thread so we don't slow down the main capture loop.
		args = (
			dirname,
			infoList,
			self.db.fname,
			self.db.fps,
			singleFile,
		)
		threading.Thread( target=publish_web_photos, args=args, name='publish_web', daemon=True ).start()
		# write_photos( *args )
	
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
			fields['name'] = ', '.join( n for n in (fields['last_name'], fields['first_name']) if n )
		for k, v in fields.items():
			if k in self.fieldCol:
				if k == 'bib':
					v = '{:>6}'.format(v)
				elif k == 'frames':
					v = '{}'.format(v) if v else ''
				else:
					v = '{}'.format(v) if v is not None else ''
				self.triggerList.SetItem( row, self.fieldCol[k], v )

	def updateTriggerColumnWidths( self ):
		for c in range(self.triggerList.GetColumnCount()):
			self.triggerList.SetColumnWidth(c, wx.LIST_AUTOSIZE_USEHEADER if c != self.iNoteCol else 100 )
				
	def updateTriggerRowID( self, id, fields ):
		row = self.getTriggerRowFromID( id )
		if row is not None:
			self.updateTriggerRow( row, fields )
	
	def getTriggerInfo( self, row ):
		return self.itemDataMap[self.triggerList.GetItemData(row)]
	
	def refreshTriggers( self, replace=False, iTriggerRow=None ):
		tNow = now()
		self.lastTriggerRefresh = tNow
		self.finishStrip.Set( None )
		
		# replace = True
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

		tsPrev = (self.tsMax or datetime(2000,1,1))
		
		triggers = self.db.getTriggers( tsLower, tsUpper, self.bibQuery )			
		if triggers:
			self.tsMax = triggers[-1].ts
		
		zeroFrames, tsLower, tsUpper = [], datetime.max, datetime.min
		for i, trig in enumerate(triggers):
			if not trig.closest_frames and trig.s_before == 0.0 and trig.s_after == 0.0:
				trig = trig._replace( s_before=tdCaptureBeforeDefault.total_seconds(), s_after=tdCaptureAfterDefault.total_seconds() )
			
			dtFinish = (trig.ts-tsPrev).total_seconds()
			itemImage = self.sm_close[min(len(self.sm_close)-1, int(len(self.sm_close) * dtFinish / closeFinishThreshold))]		
			row = self.triggerList.InsertItem( 999999, trig.ts.strftime('%H:%M:%S.%f')[:-3], itemImage )
			
			if not trig.closest_frames and not trig.frames:
				tsLower = min( tsLower, trig.ts-timedelta(seconds=trig.s_before) )
				tsU = trig.ts + timedelta(seconds=trig.s_after)
				tsUpper = max( tsUpper, tsU )
				zeroFrames.append( (row, trig.id, tsU) )
			
			fields = trig._asdict()
			fields['kmh'], fields['mph'] = ('{:.2f}'.format(trig.kmh), '{:.2f}'.format(trig.kmh * 0.621371)) if trig.kmh else ('', '')
			fields['frames'] = max(trig.frames, trig.closest_frames)
			self.updateTriggerRow( row, fields )
			
			self.triggerList.SetItemData( row, row )
			self.itemDataMap[row] = fields
			tsPrev = trig.ts
		
		if zeroFrames:
			counts = GlobalDatabase().getTriggerPhotoCounts( tsLower, tsUpper )
			values = {'frames':0}
			for row, id, tsU in zeroFrames:
				values['frames'] = counts[id]
				self.updateTriggerRow( row, values )
				# Don't update the trigger if the number of frames is possibly not known yet.
				if (tNow - tsU).total_seconds() < 5.0*60.0:
					del counts[id]
			GlobalDatabase().updateTriggerPhotoCounts( counts )
		
		self.updateTriggerColumnWidths()

		if self.triggerList.GetItemCount() >= 1:
			if iTriggerRow is not None:
				iTriggerRow = min( max(0, iTriggerRow), self.triggerList.GetItemCount()-1 )
				self.triggerList.EnsureVisible( iTriggerRow )
				self.triggerList.Select( iTriggerRow )
			else:
				self.triggerList.EnsureVisible( self.triggerList.GetItemCount()-1 )
				
		self.onTriggerSelected( self, iTriggerSelect=0 )

	def Start( self ):
		self.messageQ.put( ('', '************************************************') )
		self.messageQ.put( ('started', now().strftime('%Y/%m/%d %H:%M:%S')) )
		self.startThreads()

	def updateSnapshot( self, t, f ):
		self.snapshotCount = getattr(self, 'snapshotCount', 0) + 1
		self.dbWriterQ.put( ('photo', t, f) )
		self.dbWriterQ.put( (
			'trigger',
			{
				'ts':				t,
				's_before':			0.0,
				's_after':			0.0,
				'closest_frames':	1,
				'ts_start':			t,
				'bib':				self.snapshotCount,
				'first_name':		'',
				'last_name':		'Snapshot',
				'team':				'',
				'wave':				'',
				'race_name':		'',
			}
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
			id = triggers[0].id
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
				'time':				tNow,
				's_before':			s_before,
				's_after':			s_after,
				'closest_frames':	self.closestFrames,
				'ts_start':			tNow,
				'bib':				self.autoCaptureCount,
				'last_name':		'Auto',
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
		wx.BeginBusyCursor()
		tNow = self.tStartCapture = now()
		
		event.GetEventObject().SetForegroundColour( captureDisableColour )
		wx.CallAfter( event.GetEventObject().Refresh )
		
		self.captureCount = getattr(self, 'captureCount', 0) + 1
		self.requestQ.put( {
				'time':				tNow,
				's_before':			0.0,
				's_after':			self.tdCaptureAfter.total_seconds(),
				'closest_frames':	0,
				'ts_start':			tNow,
				'bib':				self.captureCount,
				'last_name':		'Capture',
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
			id = triggers[0].id
			self.db.updateTriggerBeforeAfter(
				id,
				0.0,
				(now() - self.tStartCapture).total_seconds()
			)
			self.db.initCaptureTriggerData( id )
			self.refreshTriggers( iTriggerRow=999999, replace=True )
		
		self.showLastTrigger()
		
		event.GetEventObject().SetForegroundColour( captureEnableColour )
		wx.CallAfter( event.GetEventObject().Refresh )
		wx.EndBusyCursor()
		
		def updateFS():
			# Wait for all the photos to be written.
			self.dbWriterQ.put( ('flush',) )
			self.dbWriterQ.join()
			# Update the finish strip.
			wx.CallAfter( self.onTriggerSelected, iTriggerSelect=self.triggerList.GetItemCount() - 1 )

		threading.Thread( target=updateFS ).start()

	def autoCaptureConfig( self, event ):
		self.autoCaptureDialog.set( self.tdCaptureBefore.total_seconds(), self.tdCaptureAfter.total_seconds(), self.closestFrames )
		if self.autoCaptureDialog.ShowModal() == wx.ID_OK:
			s_before, s_after, closestFrames = self.autoCaptureDialog.get()
			self.tdCaptureBefore = timedelta(seconds=s_before) if s_before is not None else tdCaptureBeforeDefault
			self.tdCaptureAfter  = timedelta(seconds=s_after)  if s_after  is not None else tdCaptureAfterDefault
			self.closestFrames = closestFrames
			self.writeOptions()
			self.updateAutoCaptureLabel()
 		
	def onFocus( self, event ):
		if self.focusDialog.IsShown():
			return
		self.focusDialog.Move((4,4))
		self.camInQ.put( {'cmd':'send_update', 'name':'focus', 'freq':1} )
		self.focusDialog.Show()
	
	def onTriggerSelected( self, event=None, iTriggerSelect=None ):
		self.iTriggerSelect = event.Index if iTriggerSelect is None else iTriggerSelect
		
		if self.iTriggerSelect >= self.triggerList.GetItemCount():
			self.ts = None
			self.tsJpg = []
			self.finishStrip.Set( self.tsJpg )
			self.refreshPhotoPanel()
			return
		
		self.finishStrip.Set( None )	# Clear the current finish strip so nothing gets updated.
		self.refreshPhotoPanel()
		triggerInfo = self.triggerInfo = self.getTriggerInfo( self.iTriggerSelect )
		self.ts = self.triggerInfo['ts']
		s_before, s_after = abs(self.triggerInfo['s_before']), abs(self.triggerInfo['s_after'])
		if s_before == 0.0 and s_after == 0.0:
			s_before, s_after = tdCaptureBeforeDefault.total_seconds(), tdCaptureAfterDefault.total_seconds()
		
		self.ts = triggerInfo['ts']
		if triggerInfo['closest_frames']:
			self.tsJpg = GlobalDatabase().getPhotosClosest( self.ts, triggerInfo['closest_frames'] )
		else:
			self.tsJpg = GlobalDatabase().getPhotos( self.ts - timedelta(seconds=s_before), self.ts + timedelta(seconds=s_after) )
		triggerInfo['frames'] = len(self.tsJpg)
		self.finishStrip.Set( self.tsJpg, leftToRight=[None, True, False][triggerInfo.get('finish_direction', 0)], triggerTS=triggerInfo['ts'] )
		self.refreshPhotoPanel()
	
	def onTriggerRightClick( self, event ):
		self.iTriggerSelect = event.Index
		if self.iTriggerSelect < 0:
			self.iTriggerSelect = 0
			return
		
		self.triggerList.Select( self.iTriggerSelect )
		
		if not hasattr(self, "triggerDeleteID"):
			self.triggerDeleteID = wx.NewIdRef()
			self.triggerEditID = wx.NewIdRef()
			self.Bind(wx.EVT_MENU, lambda event: self.doTriggerDelete(), id=self.triggerDeleteID)
			self.Bind(wx.EVT_MENU, lambda event: self.doTriggerEdit(),   id=self.triggerEditID)

		menu = wx.Menu()
		menu.Append(self.triggerEditID,   "Edit...")
		menu.Append(self.triggerDeleteID, "Delete...")

		self.PopupMenu(menu)
		menu.Destroy()
		
	def doTriggerDelete( self, confirm=True ):
		triggerInfo = self.getTriggerInfo( self.iTriggerSelect )
		message = ', '.join( f for f in (triggerInfo['ts'].strftime('%H:%M:%S.%f')[:-3], '{}'.format(triggerInfo['bib']),
			triggerInfo['name'], triggerInfo['team'], triggerInfo['wave'], triggerInfo['race_name']) if f )
		if not confirm or wx.MessageDialog( self, '{}:\n\n{}'.format('Confirm Delete', message), 'Confirm Delete',
				style=wx.OK|wx.CANCEL|wx.ICON_QUESTION ).ShowModal() == wx.ID_OK:		
			self.db.deleteTrigger( triggerInfo['id'], self.tdCaptureBefore.total_seconds(), self.tdCaptureAfter.total_seconds() )
			self.refreshTriggers( replace=True, iTriggerRow=self.iTriggerSelect )
	
	def onTriggerDelete( self, event ):
		self.iTriggerSelect = event.Index
		self.doTriggerDelete()
		
	def doTriggerEdit( self ):
		data = self.itemDataMap[self.triggerList.GetItemData(self.iTriggerSelect)]
		self.triggerDialog.set( self.db, data['id'] )
		self.triggerDialog.CenterOnParent()
		if self.triggerDialog.ShowModal() == wx.ID_OK:
			row = self.iTriggerSelect
			fields = self.triggerDialog.get()
			self.updateTriggerRow( row, fields )
			self.updateTriggerColumnWidths()
			self.triggerInfo.update( fields )
		return self.triggerInfo
	
	def onTriggerEdit( self, event ):
		self.iTriggerSelect = event.Index
		self.doTriggerEdit()
	
	def showMessages( self ):
		while True:
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
		lastPrimaryTime = now()
		primaryCount = 0
		
		#---------------------------------------------------------------
		def responseHandler( msg ):
			for t, f in msg['ts_frames']:
				self.dbWriterQ.put( ('photo', t, f) )
		
		#---------------------------------------------------------------
		def updateHandler( msg ):
			nonlocal lastPrimaryTime, primaryCount
			
			name, lastFrame = msg['name'], CVUtil.toFrame(msg['frame'])
			if name == 'primary':
				if lastFrame is None:
					wx.CallAfter( self.primaryBitmap.SetTestBitmap )
				else:
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
					if lastFrame is None:
						wx.CallAfter( self.focusDialog.SetTestBitmap )
					else:
						wx.CallAfter( self.focusDialog.SetBitmap, CVUtil.frameToBitmap(lastFrame) )
				else:
					self.camInQ.put( {'cmd':'cancel_update', 'name':'focus'} )

		#---------------------------------------------------------------
		def focusHandler( msg ):
			if self.focusDialog.IsShown():
				if lastFrame is None:
					wx.CallAfter( self.focusDialog.SetTestBitmap )
				else:
					wx.CallAfter( self.focusDialog.SetBitmap, CVUtil.frameToBitmap(lastFrame) )
			else:
				self.camInQ.put( {'cmd':'cancel_update', 'name':'focus'} )

		#---------------------------------------------------------------
		def infoHandler( msg ):
			vals = {name:update_value for name, property_index, call_status, update_value in msg['retvals']}
			wx.CallAfter( self.setCameraResolution, int(vals['frame_width']), int(vals['frame_height']) )
			
		#---------------------------------------------------------------
		def cameraUsbHandler( msg ):
			wx.CallAfter( self.updateCameraUsb, msg['usb'] )
			
		#---------------------------------------------------------------
		def snapshotHandler( msg ):
			lastFrame = lastFrame if msg['frame'] is None else msg['frame']
			wx.CallAfter( self.updateSnapshot,  msg['ts'], lastFrame )

		handlers = {
			'response':		responseHandler,
			'update':		updateHandler,
			'focus':		focusHandler,
			'info':			infoHandler,
			'cameraUsb':	cameraUsbHandler,
			'snapshot':		snapshotHandler,
		}
		
		while True:
			try:
				msg = self.camReader.recv()
			except EOFError:
				break
				
			try:
				handler = handlers[msg['cmd']]
			except KeyError:
				if msg['cmd'] == 'terminate':
					break
				continue
				
			handler( msg )
		
	def processRequests( self ):
		def refresh():
			self.dbWriterQ.put( ('flush',) )
	
		while True:
			msg = self.requestQ.get()	# Blocking get.
			
			tSearch = msg['time']
			advanceSeconds = msg.get('advanceSeconds', 0.0)
			tSearch += timedelta(seconds=advanceSeconds)
			
			# Record this trigger.
			self.dbWriterQ.put( (
					'trigger',
					{
						'ts':				tSearch - timedelta(seconds=advanceSeconds),
						's_before':			msg.get('s_before', self.tdCaptureBefore.total_seconds()),	# Use the configured capture interval, not the default.
						's_after':			msg.get('s_after', self.tdCaptureAfter.total_seconds()),
						'ts_start':			msg.get('ts_start', None) or now(),
						'closest_frames':	msg.get('closest_frames', self.closestFrames),
						'bib':				msg.get('bib', 99999),
						'first_name':		msg.get('first_name','') or msg.get('firstName',''),
						'last_name':		msg.get('last_name','') or msg.get('lastName',''),
						'team':				msg.get('team',''),
						'wave':				msg.get('wave',''),
						'race_name':		msg.get('race_name','') or msg.get('raceName',''),
					}
				)
			)
			# Record the video frames for the trigger.
			tStart, tEnd = tSearch-self.tdCaptureBefore, tSearch+self.tdCaptureAfter
			if self.closestFrames:
				self.camInQ.put( {'cmd':'query_closest', 't':tSearch, 'closest_frames':self.closestFrames} )
			else:
				self.camInQ.put( {'cmd':'query', 'tStart':tStart, 'tEnd':tEnd} )
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
				self.db = GlobalDatabase( dbName )
			except Exception:
				self.db = GlobalDatabase()
			
			self.dbWriterQ = Queue()
			self.dbWriterThread = threading.Thread( target=DBWriter, args=(self.dbWriterQ, lambda: wx.CallAfter(self.delayRefreshTriggers), self.db.fname) )
			self.dbWriterThread.daemon = True
			self.dbWriterThread.start()
	
	def resetCamera( self, event=None ):
		status = False
		while True:
			width, height = self.getCameraResolution()
			info = {'usb':self.getUsb(), 'fps':self.fps, 'width':width, 'height':height, 'fourcc':self.fourcc.GetLabel(), 'availableCameraUsb':self.availableCameraUsb}
			with ConfigDialog( self, **info ) as dlg:
				ret = dlg.ShowModal()
				if ret == wx.ID_CANCEL:
					return status
				info = dlg.GetValues()

			self.camInQ.put( {'cmd':'cam_info', 'info':info} )			

			self.setUsb( info['usb'] )
			self.setCameraResolution( info['width'], info['height'] )
			self.updateFPS( info['fps'] )
			self.fourcc.SetLabel( info['fourcc'] )
			
			self.GetSizer().Layout()

			self.writeOptions()
			
			status = True
			if ret == wx.ID_OK:
				return status
				
		return status
	
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
				GlobalDatabase().vacuum()
			wx.CallAfter( self.finishStrip.Clear )
			wx.CallAfter( self.refreshTriggers, True )
		dlg.Destroy()
	
	def setUsb( self, num ):
		self.usb.SetLabel( '{} {}'.format(num, self.availableCameraUsb) )
		
	def getUsb( self ):
		return int(self.usb.GetLabel().split()[0])
		
	def setCameraResolution( self, width, height ):
		self.cameraResolution.SetLabel( '{}x{}'.format(width if width < 5000 else 'MAX', height if height < 5000 else 'MAX') )
			
	def getCameraFPS( self ):
		return int(float(self.targetFPS.GetLabel().split()[0]))
		
	def getCameraResolution( self ):
		try:
			return pixelsFromRes( self.cameraResolution.GetLabel() )
		except Exception:
			return 640, 480
	
	def getFourCC( self ):
		return self.fourcc.GetLabel()
	
	def onCloseWindow( self, event ):
		self.writeOptions()
		self.shutdown()
		wx.Exit()
		
	def writeOptions( self ):
		self.config.Write( 'DBName', self.db.fname )
		self.config.Write( 'CameraDevice', str(self.getUsb()) )
		self.config.Write( 'CameraResolution', self.cameraResolution.GetLabel() )
		self.config.Write( 'FPS', self.targetFPS.GetLabel() )
		self.config.Write( 'FourCC', self.fourcc.GetLabel() )
		self.config.Write( 'SecondsBefore', '{:.3f}'.format(self.tdCaptureBefore.total_seconds()) )
		self.config.Write( 'SecondsAfter', '{:.3f}'.format(self.tdCaptureAfter.total_seconds()) )
		self.config.WriteFloat( 'ZoomMagnification', self.finishStrip.GetZoomMagnification() )
		self.config.WriteInt( 'ClosestFrames', self.closestFrames )
		self.config.Flush()
	
	def readOptions( self ):
		self.setDBName( self.config.Read('DBName', '') )
		self.setUsb( self.config.Read('CameraDevice', '0') )
		self.cameraResolution.SetLabel( self.config.Read('CameraResolution', '640x480') )
		self.targetFPS.SetLabel( self.config.Read('FPS', '30.000') )
		self.fourcc.SetLabel( self.config.Read('FourCC', FOURCC_DEFAULT) )
		s_before = self.config.Read('SecondsBefore', '0.5')
		s_after = self.config.Read('SecondsAfter', '2.0')
		try:
			self.tdCaptureBefore = timedelta(seconds=abs(float(s_before)))
		except Exception:
			pass
		try:
			self.tdCaptureAfter = timedelta(seconds=abs(float(s_after)))
		except Exception:
			pass
		self.finishStrip.SetZoomMagnification( self.config.ReadFloat('ZoomMagnification', 0.5) )
		self.closestFrames = self.config.ReadInt( 'ClosestFrames', 0 )
		
	def getCameraInfo( self ):
		width, height = self.getCameraResolution()
		return {'usb':self.getUsb(), 'fps':self.getCameraFPS(), 'width':width, 'height':height, 'fourcc':self.getFourCC()}

def disable_stdout_buffering():
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w", 0)
	
def getLogFileName():
	return os.path.join(Utils.getHomeDir(), 'CrossMgrVideo.log')

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
	redirectFileName = getLogFileName()
	
	# Set up the log file.  Otherwise, show errors on the screen.
	if __name__ == '__main__':
		'''disable_stdout_buffering()'''
		pass
	else:
		try:
			logSize = os.path.getsize( redirectFileName )
			if logSize > 1000000:
				os.remove( redirectFileName )
		except Exception:
			pass
	
		try:
			app.RedirectStdio( redirectFileName )
		except Exception:
			pass
			
		try:
			with open(redirectFileName, 'a') as pf:
				pf.write( '********************************************\n' )
				pf.write( '{}: {} Started.\n'.format(now().strftime('%Y-%m-%d_%H:%M:%S'), AppVerName) )
		except Exception:
			pass
	
	mainWin.Show()

	# Set the upper left icon.
	try:
		icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'CrossMgrVideo.ico'), wx.BITMAP_TYPE_ICO )
		mainWin.SetIcon( icon )
	except Exception:
		pass

	# Start processing events.
	mainWin.Start()
	wx.CallLater( 1500, mainWin.resetCamera )
	app.MainLoop()

@atexit.register
def shutdown():
	if mainWin:
		mainWin.shutdown()
	
if __name__ == '__main__':
	MainLoop()
	
