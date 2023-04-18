import wx
import os
import re
import time
import datetime
import bisect
import threading
from ScaledBitmap import ScaledBitmap, GetScaleRatio
from ComputeSpeed import ComputeSpeed
from Database import GlobalDatabase
from AddPhotoHeader import AddPhotoHeader
import Utils
import CVUtil

def _( x ):
	return x
	
def RescaleBitmap( bitmap, width, height ):
	wBitmap, hBitmap = bitmap.GetSize()
	ratio = GetScaleRatio( wBitmap, hBitmap, width, height )
	wBM, hBM = int(wBitmap * ratio), int(hBitmap * ratio)
	bm = wx.Bitmap( wBM, hBM )
	
	sourceDC = wx.MemoryDC( bitmap )
	
	destDC = wx.MemoryDC( bm )
	destDC.SetBrush( wx.Brush( wx.Colour(232,232,232), wx.SOLID ) )
	destDC.Clear()
	
	xLeft, yTop = (wBM - wBitmap) // 2, (hBM - hBitmap) // 2
	destDC.StretchBlit( xLeft, yTop, wBM, hBM, sourceDC, 0, 0, wBitmap, hBitmap )
	return bm
	
class PhotoPrintout( wx.Printout ):
	def __init__(self, bitmap):
		super().__init__()
		self.bitmap = bitmap

	def HasPage(self, page):
		return page == 1

	def GetPageInfo(self):
		return (1,1,1,1)

	def OnPrintPage(self, page):
		dc = self.GetDC()
		dc.SetBackground( wx.Brush(wx.WHITE, wx.SOLID) )
		dc.Clear()
		
		width, height = dc.GetSize()
		shrink = 0.9
		drawWidth, drawHeight = int(width*shrink), int(height*shrink)
		border = (width-drawWidth)//2
		bitmap = RescaleBitmap( self.bitmap, drawWidth, drawHeight )
		dcBitmap = wx.MemoryDC( bitmap )
		
		dc.Blit( border, border, bitmap.GetSize()[0], bitmap.GetSize()[1], dcBitmap, 0, 0 )
		return True

def PrintPhoto( parent, bitmap ):
	printData = wx.PrintData()
	printData.SetPaperId(wx.PAPER_LETTER)
	printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
	printData.SetOrientation(wx.LANDSCAPE)
	
	pdd = wx.PrintDialogData(printData)
	pdd.EnableSelection( False )
	pdd.EnablePageNumbers( False )
	pdd.EnableHelp( False )
	pdd.EnablePrintToFile( False )
	
	printer = wx.Printer(pdd)
	printout = PhotoPrintout( bitmap )

	if not printer.Print(parent, printout, True):
		if printer.GetLastError() == wx.PRINTER_ERROR:
			wx.MessageBox( '\n\n'.join( [_("There was a printer problem."), _("Check your printer setup.")] ), _("Printer Error"))
	else:
		printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )

	printout.Destroy()	

class PhotoPanel( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize, style=0, isDialog=False ):
			
		super().__init__( parent, id, size=size, style=style )
		
		self.clear( False )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		self.scaledBitmap = ScaledBitmap( self, inset=True, drawCallback=self.drawCallback )
		vs.Add( self.scaledBitmap, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.scaledBitmap.Bind( wx.EVT_MOUSEWHEEL, self.onMouseWheel )
		self.scaledBitmap.Bind( wx.EVT_KEY_DOWN, self.onKeyDown )
		
		btnsizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.recenter = wx.BitmapButton(self, bitmap=Utils.getBitmap('center-icon.png'))
		self.recenter.SetToolTip( wx.ToolTip('Recenter') )
		self.recenter.Bind( wx.EVT_BUTTON, self.onRecenter )

		self.frameBackward = wx.BitmapButton( self, bitmap=Utils.getBitmap('minus.png') )
		self.frameBackward.SetToolTip( wx.ToolTip('-1 Frame') )
		self.frameBackward.Bind( wx.EVT_BUTTON, lambda e: self.changeFrame(-1) )
		self.frameForward = wx.BitmapButton( self, bitmap=Utils.getBitmap('plus.png') )
		self.frameForward.SetToolTip( wx.ToolTip('+1 Frame') )
		self.frameForward.Bind( wx.EVT_BUTTON, lambda e: self.changeFrame(1) )
				
		self.playerRewind = wx.BitmapButton( self, bitmap=Utils.getBitmap('fast-backward.png') )
		self.playerRewind.SetToolTip( wx.ToolTip('To Beginning') )
		self.playerRewind.Bind( wx.EVT_BUTTON, lambda e: self.playRewind() )
		self.playerReverse = wx.BitmapButton( self, bitmap=Utils.getBitmap('play-reverse.png') )
		self.playerReverse.SetToolTip( wx.ToolTip('Play Backward') )
		self.playerReverse.Bind( wx.EVT_BUTTON, lambda e: self.playReverse() )
		self.playerStop = wx.BitmapButton( self, bitmap=Utils.getBitmap('stop.png') )
		self.playerStop.SetToolTip( wx.ToolTip('Stop Play') )
		self.playerStop.Bind( wx.EVT_BUTTON, lambda e: self.playStop() )		
		self.playerForward = wx.BitmapButton( self, bitmap=Utils.getBitmap('play.png') )
		self.playerForward.SetToolTip( wx.ToolTip('Play Forward') )
		self.playerForward.Bind( wx.EVT_BUTTON, lambda e: self.play() )
		self.playerForwardToEnd = wx.BitmapButton( self, bitmap=Utils.getBitmap('fast-forward.png') )
		self.playerForwardToEnd.SetToolTip( wx.ToolTip('To End') )
		self.playerForwardToEnd.Bind( wx.EVT_BUTTON, lambda e: self.playForwardToEnd() )
		
		btnsizer.Add( self.recenter, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)
		btnsizer.Add( self.frameBackward, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4)
		btnsizer.Add( self.frameForward, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=0)
		btnsizer.Add( self.playerRewind, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=8)
		btnsizer.Add( self.playerReverse, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=0)
		btnsizer.Add( self.playerStop, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=0)
		btnsizer.Add( self.playerForward, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=0)
		btnsizer.Add( self.playerForwardToEnd, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=0)
		btnsizer.Add( wx.StaticText(self, label='or Mousewheel'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=2 )
        
		self.contrast = wx.ToggleButton( self, label='Contrast')
		self.contrast.Bind( wx.EVT_TOGGLEBUTTON, self.onFilter )
		btnsizer.Add(self.contrast, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4)		

		self.sharpen = wx.ToggleButton( self, label='Sharpen')
		self.sharpen.Bind( wx.EVT_TOGGLEBUTTON, self.onFilter )
		btnsizer.Add(self.sharpen, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)		

		#btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('edit_icon.png'))
		btn = wx.Button( self, label='Edit Info' )
		btn.SetToolTip( wx.ToolTip('Edit Trigger Info') )
		btn.Bind( wx.EVT_BUTTON, self.onEdit )
		btnsizer.Add(btn, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16)

		#---------------------------------------------------------------
		self.exportViewMenu = wx.Menu()
		item = self.exportViewMenu.Append(wx.ID_ANY, 'to File...', 'Save to File')
		self.Bind(wx.EVT_MENU, self.onExportPng, item)
		item = self.exportViewMenu.Append(wx.ID_ANY, 'to Clipboard...', 'Save to Clipboard')
		self.Bind(wx.EVT_MENU, self.onExportClipboard, item)
		
		btn = wx.Button( self, label='Export View' )
		btn.SetToolTip( wx.ToolTip('Export current view (includes zoom)') )
		btn.Bind( wx.EVT_BUTTON, self.onExportView )
		btnsizer.Add(btn, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16)

		self.savePhotoMenu = wx.Menu()
		item = self.savePhotoMenu.Append(wx.ID_ANY, 'to File...', 'Save to File')
		self.Bind(wx.EVT_MENU, self.onSaveJpg, item)
		item = self.savePhotoMenu.Append(wx.ID_ANY, 'to Clipboard...', 'Save to Clipboard')
		self.Bind(wx.EVT_MENU, self.onSaveClipboard, item)
		
		btn = wx.Button( self, label='Save Photo' )
		btn.SetToolTip( wx.ToolTip('Save current photo only') )
		btn.Bind( wx.EVT_BUTTON, self.onSavePhoto )
		btnsizer.Add(btn, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4)
		#---------------------------------------------------------------


		'''
		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('clipboard-bw.png'))
		btn.SetToolTip( wx.ToolTip('Copy Photo to Clipboard') )
		btn.Bind( wx.EVT_BUTTON, self.onCopyClipboard )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.BitmapButton(self, wx.ID_PRINT, bitmap=Utils.getBitmap('print.png'))
		btn.SetToolTip( wx.ToolTip('Print Photo') )
		btn.SetDefault()
		btn.Bind( wx.EVT_BUTTON, self.onPrint )
		btnsizer.Add(btn, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=8)
		
		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('png.png'))
		btn.SetToolTip( wx.ToolTip('Save Photo as PNG file') )
		btn.Bind( wx.EVT_BUTTON, self.onSavePng )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('mpg.png'))
		btn.SetToolTip( wx.ToolTip('Save Sequence as Mp4') )
		btn.Bind( wx.EVT_BUTTON, self.onSaveMP4 )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('gif.png'))
		btn.SetToolTip( wx.ToolTip('Save Sequence as Animated Gif') )
		btn.Bind( wx.EVT_BUTTON, self.onSaveGif )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)
		'''

		self.restoreViewBtn = btn = wx.BitmapButton( self, bitmap=Utils.getBitmap('upload.png') )
		btn.SetToolTip( wx.ToolTip('Restore View from Database') )
		btn.Bind( wx.EVT_BUTTON, self.doRestoreView )
		btnsizer.Add(btn, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=16)
		
		btn = wx.BitmapButton( self, bitmap=Utils.getBitmap('download.png') )
		btn.SetToolTip( wx.ToolTip('Save View to Database') )
		btn.Bind( wx.EVT_BUTTON, self.onSaveView )
		btnsizer.Add(btn, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=4)
		
		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('speedometer.png'))
		btn.SetToolTip( wx.ToolTip('Get Speed') )
		btn.Bind( wx.EVT_BUTTON, self.onGetSpeed )
		btnsizer.Add(btn, flag=wx.LEFT, border=16)
		
		if isDialog:
			btnsizer.AddStretchSpacer()
			btn = wx.BitmapButton(self, wx.ID_CLOSE, bitmap=Utils.getBitmap('close-window.png'))
			btn.SetToolTip( wx.ToolTip('Close') )
			btnsizer.Add(btn, flag=wx.LEFT, border=4)
			btn.Bind( wx.EVT_BUTTON, self.onClose )

		vs.Add( btnsizer, flag=wx.ALL|wx.EXPAND, border=5 )
		
		self.SetSizer(vs)

	@property
	def jpg( self ):
		if self.iJpg is None or not self.tsJpg:
			return None
		self.iJpg = max( 0, min( len(self.tsJpg)-1, self.iJpg ) )
		return self.tsJpg[self.iJpg][1]

	@property
	def ts( self ):
		return None if self.iJpg is None else self.tsJpg[self.iJpg][0]
		
	def set( self, iJpg, triggerInfo, tsJpg, fps=25, editCB=None, updateCB=None ):
		self.iJpg = max( 0, min(iJpg or 0, (len(tsJpg)-1) if tsJpg else 0) )
		self.triggerInfo = triggerInfo or {}
		self.tsJpg = tsJpg
		self.fps = fps
		self.editCB = editCB
		self.updateCB = updateCB or (lambda update: None)
		
		self.restoreViewBtn.Enable( self.triggerInfo.get('zoom_frame',-1) >= 0 )
		
		self.kmh = (triggerInfo.get('kmh',0.0) or 0.0) if triggerInfo else 0.0
		if isinstance(self.kmh, str):
			self.kmh = float( '0' + re.sub('[^0-9.]', '', self.kmh) )
		self.mps = self.kmh / 3.6
		self.mph = self.kmh * 0.621371
		self.pps = 2000.0
		
		self.tsPreview = None
		
		self.SetBitmap()
		
	def setPreview( self, bitmap=None, ts=None ):
		if not bitmap:
			return
		self.clear()
		self.scaledBitmap.SetBitmap( bitmap )
		self.tsPreview = ts
	
	def setFrameIndex( self, i ):
		self.iJpg = max( 0, min(i, len(self.tsJpg)-1) )
		self.SetBitmap()
		
	def findFrameClosestToTrigger( self ):
		# Clever way to bisect list of sorted tuples.
		ts = self.triggerInfo['ts']
		iJpgClosest = bisect.bisect_left( self.tsJpg, (ts, ), hi=len(self.tsJpg)-1 )
		
		# Find the closest photo to the trigger time.
		for i in range(max(0, iJpgClosest-1), min(iJpgClosest+2, len(self.tsJpg)) ):
			if abs((self.tsJpg[i][0] - ts).total_seconds()) < abs((self.tsJpg[iJpgClosest][0] - ts).total_seconds()):
				iJpgClosest = i
		
		return iJpgClosest
	
	def onRecenter( self, event=None ):
		# Set to the photo closest to the trigger time.
		if self.iJpg is not None and self.triggerInfo:
			self.setFrameIndex( self.findFrameClosestToTrigger() )
	
	def changeFrame( self, frameDir ):
		if self.tsJpg and self.iJpg is not None:
			if frameDir == 0:
				self.setFrameIndex( 0 )
			else:
				self.setFrameIndex( self.iJpg + (1 if frameDir > 0 else -1) )
		
	def onFilter( self, event ):
		self.SetBitmap()
	
	def onMouseWheel( self, event ):
		self.changeFrame( -event.GetWheelRotation() )
		event.Skip()
	
	def onKeyDown( self, event ):
		self.changeFrame( -1 if event.ShiftDown() else 1 )
	
	def playNextFrame( self ):
		if self.keepPlayingForward:
			if self.iJpg < len(self.tsJpg)-1:
				wx.CallLater( int((self.tsJpg[self.iJpg+1][0] - self.tsJpg[self.iJpg][0]).total_seconds()*1000.0), lambda: (self.changeFrame(1) or self.playNextFrame()) )
			else:
				self.setFrameIndex( 0 )
				wx.CallLater( 700, self.playNextFrame )
	
	def play( self ):
		self.playStop()
		if self.tsJpg:
			self.keepPlayingForward = True
			self.playNextFrame()
		
	def playPrevFrame( self ):
		if self.keepPlayingReverse:
			if self.iJpg > 0:
				wx.CallLater( int((self.tsJpg[self.iJpg][0] - self.tsJpg[self.iJpg-1][0]).total_seconds()*1000.0), lambda: (self.changeFrame(-1) or self.playPrevFrame()) )
			else:
				self.setFrameIndex( len(self.tsJpg)-1 )
				wx.CallLater( 700, self.playPrevFrame )
	
	def playReverse( self ):
		self.playStop()
		if self.tsJpg:
			self.keepPlayingReverse = True
			self.playPrevFrame()
		
	def playStop( self ):
		self.keepPlayingForward = self.keepPlayingReverse = False
		
	def playRewind( self ):
		self.playStop()
		self.changeFrame( 0 )		
		
	def playForwardToEnd( self ):
		self.playStop()
		if self.tsJpg:
			self.iJpg = len(self.tsJpg) - 1
			self.changeFrame( 1 )
		
	def clear( self, playStop=True ):
		if playStop:
			self.playStop()
		self.iJpg = None
		self.triggerInfo = {}
		self.tsJpg = None
		self.fps = None
		self.editCB = None
		self.tsPreview = None
	
	def onEdit( self, event ):
		if self.editCB and self.triggerInfo:
			self.triggerInfo.update( self.editCB() )
			wx.CallAfter( self.SetBitmap )
			wx.CallAfter( self.Refresh )
			wx.CallAfter( self.updateCB, self.triggerInfo )
			
	def GetZoomInfo( self ):
		r = self.scaledBitmap.GetSourceRect()
		if not r:
			r = wx.Rect( 0, 0, 0, 0 )
		return {
			'zoom_frame':	self.iJpg,
			'zoom_x':		r.GetX(),
			'zoom_y':		r.GetY(),
			'zoom_width':	r.GetWidth(),
			'zoom_height':	r.GetHeight(),
		}
		
	def SetZoomInfo( self, zinfo ):
		if not self.tsJpg:
			return
		if 'zoom_frame' in zinfo:
			frame = zinfo['zoom_frame']
			self.iJpg = min( max(0, self.findFrameClosestToTrigger() if frame < 0 else frame), len(self.tsJpg)-1 )
		self.scaledBitmap.SetSourceRect( wx.Rect( *[zinfo.get(f, 0) for f in ('zoom_x','zoom_y','zoom_width','zoom_height')] ) )
		self.SetBitmap()
	
	#-------------------------------------------------------------------
	def getDefaultFilename( self, suffix, label=None ):
		if not suffix.startswith('.'):
			suffix = '.' + suffix
		
		defaultFile = '{} {}-{:04d}-{}'.format(
			self.triggerInfo.get('first_name',''),
			self.triggerInfo.get('last_name',''),
			self.triggerInfo.get('bib',0),
			self.triggerInfo.get('ts', datetime.datetime.now()).strftime('%Y%m%d-%H%M%S-%f')[:-3],
		)
		if label:
			defaultFile += '-' + label
		return Utils.RemoveDisallowedFilenameChars( defaultFile ) + suffix
	
	#-------------------------------------------------------------------
	def onExportClipboard( self, event ):
		self.playStop()
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData( wx.BitmapDataObject(self.scaledBitmap.GetDisplayBitmap()) )
			wx.TheClipboard.Flush() 
			wx.TheClipboard.Close()
			wx.MessageBox( _('Successfully exported to clipboard'), _('Success') )
		else:
			wx.MessageBox( _('Unable to open the clipboard'), _('Error') )
	
	def onExportPng( self, event ):
		self.playStop()
		with wx.FileDialog( self, message='Export View', wildcard='*.png', style=wx.FD_SAVE, defaultFile=self.getDefaultFilename('.png', 'View') ) as fd:
			if fd.ShowModal() == wx.ID_OK:
				try:
					self.scaledBitmap.GetDisplayBitmap().SaveFile( fd.GetPath(), wx.BITMAP_TYPE_PNG )
					wx.MessageBox( _('View Export Successful'), _('Success') )
				except Exception as e:
					wx.MessageBox( _('View Export Failed:\n\n{}').format(e), _('Export Failed') )

	def onExportView( self, event ):
		self.playStop()
		if not self.triggerInfo:
			return
		self.PopupMenu(self.exportViewMenu)
	
	#-------------------------------------------------------------------
	def onSaveClipboard( self, event ):
		self.playStop()
		bitmap = self.getPhotoWithHeader()		
		if bitmap is None:
			wx.MessageBox( _('No photo to save'), _('Error') )
			return
		
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData( wx.BitmapDataObject(bitmap) )
			wx.TheClipboard.Flush() 
			wx.TheClipboard.Close()
			wx.MessageBox( _('Successfully exported to clipboard'), _('Success') )
		else:
			wx.MessageBox( _('Unable to open the clipboard'), _('Error') )
	
	def onSaveJpg( self, event ):
		self.playStop()
		bitmap = self.getPhotoWithHeader()		
		if bitmap is None:
			wx.MessageBox( _('No photo to save'), _('Error') )
			return
			
		with wx.FileDialog( self, message='Export View', wildcard='*.jpeg', style=wx.FD_SAVE, defaultFile=self.getDefaultFilename('.jpeg') ) as fd:
			if fd.ShowModal() == wx.ID_OK:
				try:
					bitmap.SaveFile( fd.GetPath(), wx.BITMAP_TYPE_JPEG )
					wx.MessageBox( _('Photo Save Successful'), _('Success') )
				except Exception as e:
					wx.MessageBox( _('Photo Save Failed:\n\n{}').format(e), _('Export Failed') )
		
	def onSavePhoto( self, event ):
		self.playStop()
		if not self.triggerInfo:
			return
		self.PopupMenu(self.savePhotoMenu)
	
	#-------------------------------------------------------------------
	def doRestoreView( self, event=None ):
		if self.triggerInfo:
			# Refresh the record from the database.
			self.triggerInfo.update( GlobalDatabase().getTriggerFields(self.triggerInfo['id'], ('zoom_frame','zoom_x','zoom_y','zoom_width','zoom_height')) )
			self.SetZoomInfo( self.triggerInfo )
		
	def onSaveView( self, event ):
		if self.triggerInfo:
			zinfo = self.GetZoomInfo() 
			if zinfo:
				self.triggerInfo.update( zinfo )
				GlobalDatabase().updateTriggerRecord( self.triggerInfo['id'], zinfo )
				self.restoreViewBtn.Enable( self.triggerInfo.get('zoom_frame',-1) >= 0 )

	def SetBitmap( self ):
		self.scaledBitmap.SetBitmap( self.getPhoto() )
		
	#-------------------------------------------------------------------
	def onBrightness( self, event ):
		pass
	
	def getPhoto( self ):
		if self.jpg is None:
			return None

		frame = CVUtil.jpegToFrame(self.jpg)
		if self.contrast.GetValue():
			frame = CVUtil.adjustContrastFrame( frame )
		if self.sharpen.GetValue():
			frame = CVUtil.sharpenFrame( frame )
		
		return CVUtil.frameToBitmap(frame)
	
	def getPhotoData( self ):
		if not self.triggerInfo:
			return {}
		photoData = {f:self.triggerInfo[f] for f in ('bib', 'ts', 'first_name', 'last_name', 'team', 'race_name', 'kmh', 'mph') if f in self.triggerInfo}
		try:
			photoData['raceSeconds'] = (self.triggerInfo['ts'] - self.triggerInfo['ts_start']).total_seconds()
		except Exception as e:
			pass
		return photoData
	
	def getPhotoWithHeader( self ):
		if not self.triggerInfo:
			return None
		return AddPhotoHeader( self.getPhoto(), **self.getPhotoData() )
	
	#-------------------------------------------------------------------
	def drawCallback( self, dc, width, height ):
		if self.jpg is None and self.tsPreview is None:
			return None

		# Add the frame timestamps and offset into.
		if self.tsPreview:
			text = [ 'CAPTURING...' ]
			tsCur = self.tsPreview
		else:
			text = []
			tsCur = self.tsJpg[self.iJpg][0]
			try:
				tsTrigger = self.triggerInfo['ts']
				text.append( '{:+.3f} TRG'.format( (tsCur - tsTrigger).total_seconds() ) )
			except Exception as e:
				pass
		
		text.append( tsCur.strftime('%H:%M:%S.%f')[:-3] )

		fontHeight = max( 8, height // 25 )
		dc.SetFont( wx.Font( wx.FontInfo(fontHeight) ) )
		dc.SetTextForeground( wx.Colour(255,255,0) )
		lineHeight = round(fontHeight * 1.5)
		xText = fontHeight
		yText = fontHeight
		for textCur in text:
			dc.DrawText( textCur, xText, yText )
			yText += lineHeight
	
	def onClose( self, event ):
		self.playStop()
		self.EndModal( wx.ID_OK )
	
	def onGetSpeed( self, event ):
		self.playStop()

		t1, bitmap1, t2, bitmap2 = None, None, None, None
		speedFrames = 2
		
		if self.iJpg == 0:
			i1, i2 = 0, speedFrames
		else:
			i1, i2  = self.iJpg-speedFrames, self.iJpg
		
		i1 = min( max(0, i1), len(self.tsJpg)-1 )
		i2 = min( max(0, i2), len(self.tsJpg)-1 )
		if i1 == i2:
			return
		
		computeSpeed = ComputeSpeed( self, size=self.GetSize() )
		self.mps, self.kmh, self.mph, self.pps = computeSpeed.Show( self.tsJpg, i1, i2, self.triggerInfo['ts_start'] )
		if self.kmh is not None:
			self.triggerInfo.update( {'kmh':'{:.2f}'.format(self.kmh), 'mph':'{:.2f}'.format(self.mph)} )
			GlobalDatabase().updateTriggerRecord( self.triggerInfo['id'], {'kmh': self.kmh} )
			wx.CallAfter( self.updateCB, self.triggerInfo )
	
	def onPrint( self, event ):
		self.playStop()
		PrintPhoto( self, self.scaledBitmap.GetDisplayBitmap() )
	
	def onSaveMP4( self, event ):
		if not self.triggerInfo:
			return
		
		self.playStop()
		with wx.FileDialog( self, message='Save MP4', wildcard='*.mp4', style=wx.FD_SAVE, defaultFile=self.getDefaultFilename('.mp4') ) as fd:
			if fd.ShowModal() != wx.ID_OK:
				return
			fname = fd.GetPath()

		def writePhotos( fname, photoData, tsJpg ):
			# Find the most likely fps.
			tDiff = []
			for i in range(len(tsJpg)-1):
				tDiff.append( (tsJpg[i+1][0] - tsJpg[i][0]).total_seconds() )
			if not tDiff:
				return
			tDiff.sort()
			fps = round(1.0 / tDiff[len(tDiff)//2])
			
			width, height = CVUtil.getWidthHeight( AddPhotoHeader(CVUtil.jpegToBitmap(tsJpg[0][1], **photoData)) )
			fourcc = cv2.VideoWriter_fourcc(*'mp4v')
			out = cv2.VideoWriter(fname, fourcc, fps, (width, height))
			for ts, jpg in tsJpg:
				out.write( CVUtil.toFrame(AddPhotoHeader(CVUtil.jpegToBitmap(jpg, **photoData))) )
			out.release()
							
		threading.Thread( target=writePhotos, args=(fname, self.getPhotoData(), self.tsJpgs,), daemon=True ).start()
	
	'''
			with wx.BusyCursor():
				try:
					# ffmpeg -i animated.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" video.mp4
					command = [
						Utils.getFFMegExe(),
						'-nostats', '-loglevel', '0',	# silence ffmpeg output
						'-y', # (optional) overwrite output file if it exists
						'-f', 'image2pipe',
						'-r', '{}'.format(self.fps), # frames per second
						'-i', '-', # The input comes from a pipe
						'-an', # Tells FFMPEG not to expect any audio
						'-movflags', 'faststart',
						'-pix_fmt', 'yuv420p',
						'-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
						fd.GetPath(),
					]
					proc = subprocess.Popen( command, stdin=subprocess.PIPE, bufsize=-1 )
					for i, (ts, jpg) in enumerate(self.tsJpg):
						proc.stdin.write( jpg )
					proc.stdin.close()
					proc.wait()
					
					wx.MessageBox( _('MP4 Save Successful'), _('Success') )
				except Exception as e:
					wx.MessageBox( _('MP4 Save Failed:\n\n{}').format(e), _('Save Failed') )
	'''
	'''
	def onSaveGif( self, event ):
		self.playStop()
		with wx.FileDialog( self, message='Save Animated Gif', wildcard='*.gif', style=wx.FD_SAVE, defaultFile=self.getDefaultFilename('.gif') ) as fd:
			if fd.ShowModal() == wx.ID_OK:
				with wx.BusyCursor():
					try:
						command = [
							Utils.getFFMegExe(),
							'-nostats', '-loglevel', '0',	# silence ffmpeg output
							'-y', # (optional) overwrite output file if it exists
							'-f', 'image2pipe',
							'-r', '{}'.format(self.fps), # frames per second
							'-i', '-', # The input comes from a pipe
							'-an', # Tells FFMPEG not to expect any audio
							fd.GetPath(),
						]
						proc = subprocess.Popen( command, stdin=subprocess.PIPE, bufsize=-1 )
						for i, (ts, jpg) in enumerate(self.tsJpg):
							proc.stdin.write( jpg )
						proc.stdin.close()
						proc.wait()
						wx.MessageBox( _('Gif Save Successful'), _('Success') )
					except Exception as e:
						wx.MessageBox( _('Gif Save Failed:\n\n{}').format(e), _('Save Failed') )
	'''

class PhotoDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, size=(500,500),
		style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX ):
			
		super().__init__( parent, id, size=size, style=style, title=_('Photo: *** Left-click and Drag in the Photo to Zoom In ***') )
		
		vs = wx.BoxSizer( wx.VERTICAL )

		self.panel = PhotoPanel( self, isDialog=True )
		vs.Add( self.panel, 1, flag=wx.ALL|wx.EXPAND )
		
		self.SetSizer( vs )
		
	def set( self, *args, **kwargs ):
		self.panel.set( *args, **kwargs )

