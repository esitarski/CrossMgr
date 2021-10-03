import wx
import os
import time
import bisect
import subprocess
from AddPhotoHeader import AddPhotoHeader
from ScaledBitmap import ScaledBitmap, GetScaleRatio
from ComputeSpeed import ComputeSpeed
from Database import GlobalDatabase
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

photoHeaderState = True
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
		self.frameBackward.Bind( wx.EVT_BUTTON, lambda e: self.changeFrame(-1) )
		self.frameForward = wx.BitmapButton( self, bitmap=Utils.getBitmap('plus.png') )
		self.frameForward.Bind( wx.EVT_BUTTON, lambda e: self.changeFrame(1) )
				
		self.playerRewind = wx.BitmapButton( self, bitmap=Utils.getBitmap('fast-backward.png') )
		self.playerRewind.Bind( wx.EVT_BUTTON, lambda e: self.playRewind() )
		self.playerReverse = wx.BitmapButton( self, bitmap=Utils.getBitmap('play-reverse.png') )
		self.playerReverse.Bind( wx.EVT_BUTTON, lambda e: self.playReverse() )
		self.playerStop = wx.BitmapButton( self, bitmap=Utils.getBitmap('stop.png') )
		self.playerStop.Bind( wx.EVT_BUTTON, lambda e: self.playStop() )		
		self.playerForward = wx.BitmapButton( self, bitmap=Utils.getBitmap('play.png') )
		self.playerForward.Bind( wx.EVT_BUTTON, lambda e: self.play() )
		self.playerForwardToEnd = wx.BitmapButton( self, bitmap=Utils.getBitmap('fast-forward.png') )
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
        
		self.photoHeader = wx.CheckBox(self, label='Header')
		self.photoHeader.SetValue( photoHeaderState )
		self.photoHeader.Bind( wx.EVT_CHECKBOX, self.onPhotoHeader )
		btnsizer.Add(self.photoHeader, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=8)
		
		self.contrast = wx.ToggleButton( self, label='Contrast')
		self.contrast.Bind( wx.EVT_TOGGLEBUTTON, self.onFilter )
		btnsizer.Add(self.contrast, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4)		

		self.sharpen = wx.ToggleButton( self, label='Sharpen')
		self.sharpen.Bind( wx.EVT_TOGGLEBUTTON, self.onFilter )
		btnsizer.Add(self.sharpen, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)		

		self.grayscale = wx.ToggleButton( self, label='Grayscale')
		self.grayscale.Bind( wx.EVT_TOGGLEBUTTON, self.onFilter )
		btnsizer.Add(self.grayscale, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)		

		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('edit_icon.png'))
		btn.SetToolTip( wx.ToolTip('Edit Trigger Info') )
		btn.Bind( wx.EVT_BUTTON, self.onEdit )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('clipboard-bw.png'))
		btn.SetToolTip( wx.ToolTip('Copy Photo to Clipboard') )
		btn.Bind( wx.EVT_BUTTON, self.onCopyToClipboard )
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

		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('speedometer.png'))
		btn.SetToolTip( wx.ToolTip('Get Speed') )
		btn.Bind( wx.EVT_BUTTON, self.onGetSpeed )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)
		
		btn = wx.Button( self, label="Restore View" )
		btn.SetToolTip( wx.ToolTip('Restore Zoom and Frame') )
		btn.Bind( wx.EVT_BUTTON, self.doRestoreView )
		btnsizer.Add(btn, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=8)
		
		btn = wx.Button( self, label="Save View" )
		btn.SetToolTip( wx.ToolTip('Save Zoom and Frame') )
		btn.Bind( wx.EVT_BUTTON, self.onSaveView )
		btnsizer.Add(btn, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=8)
		
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
		return None if self.iJpg is None else self.tsJpg[self.iJpg][1]

	@property
	def ts( self ):
		return None if self.iJpg is None else self.tsJpg[self.iJpg][0]
		
	def set( self, iJpg, triggerInfo, tsJpg, fps=25, editCB=None ):
		self.iJpg = iJpg
		self.triggerInfo = triggerInfo
		self.tsJpg = tsJpg
		self.fps = fps
		self.editCB = editCB
		
		self.kmh = (triggerInfo.get('kmh',0.0) or 0.0) if triggerInfo else 0.0
		self.mps = self.kmh / 3.6
		self.mph = self.kmh * 0.621371
		self.pps = 2000.0
		
		self.SetBitmap()
	
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
		if self.iJpg is not None:
			self.setFrameIndex( self.findFrameClosestToTrigger(), True )
	
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
			self.changeFrame( 1 )
			if self.iJpg < len(self.tsJpg)-1:
				wx.CallLater( int((self.tsJpg[self.iJpg+1][0] - self.tsJpg[self.iJpg][0]).total_seconds()*1000.0), self.playNextFrame )
			else:
				self.iJpg = 0
				wx.CallLater( 700, self.playNextFrame )
	
	def play( self ):
		self.playStop()
		if self.tsJpg:
			self.keepPlayingForward = True
			if self.iJpg < len(self.tsJpg)-1:
				wx.CallLater( int((self.tsJpg[self.iJpg+1][0] - self.tsJpg[self.iJpg][0]).total_seconds()*1000.0), self.playNextFrame )
		
	def playPrevFrame( self ):
		if self.keepPlayingReverse:
			self.changeFrame( -1 )
			if self.iJpg > 0:
				wx.CallLater( int((self.tsJpg[self.iJpg][0] - self.tsJpg[self.iJpg-1][0]).total_seconds()*1000.0), self.playPrevFrame )
			else:
				self.iJpg = len(self.tsJpg)
				wx.CallLater( 700, self.playPrevFrame )
	
	def playReverse( self ):
		self.playStop()
		if self.tsJpg:
			self.keepPlayingReverse = True
			if self.iJpg > 0:
				wx.CallLater( int((self.tsJpg[self.iJpg][0] - self.tsJpg[self.iJpg-1][0]).total_seconds()*1000.0), self.playPrevFrame )
		
	def playStop( self ):
		self.keepPlayingForward = self.keepPlayingReverse = False
		
	def playRewind( self ):
		self.playStop()
		self.changeFrame( 0 )		
		
	def playForwardToEnd( self ):
		self.playStop()
		if self.tsJpg:
			self.iJpg = len(self.tsJpg)
			self.changeFrame( 1 )
		
	def clear( self, playStop=True ):
		if playStop:
			self.playStop()
		self.iJpg = None
		self.triggerInfo = None
		self.tsJpg = None
		self.fps = None
		self.editCB = None
	
	def onEdit( self, event ):
		if self.editCB:
			self.triggerInfo = self.editCB()
			wx.CallAfter( self.SetBitmap )
			wx.CallAfter( self.Refresh )
			
	def GetZoomInfo( self ):
		r = self.scaledBitmap.GetSourceRect()
		if not r:
			return {}
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

	def SetBitmap( self ):
		self.scaledBitmap.SetBitmap( self.getPhoto() )
		
	def onBrightness( self, event ):
		pass
	
	def onPhotoHeader( self, event=None ):
		global photoHeaderState
		photoHeaderState = self.photoHeader.GetValue()
		self.SetBitmap()
	
	def addPhotoHeaderToBitmap( self, bitmap ):
		if not photoHeaderState:
			return bitmap
		
		return AddPhotoHeader(
			bitmap,
			ts				= self.triggerInfo['ts'],
			bib				= self.triggerInfo['bib'],
			first_name		= self.triggerInfo['first_name'],
			last_name		= self.triggerInfo['last_name'],
			team			= self.triggerInfo['team'],
			race_name		= self.triggerInfo['race_name'],
			kmh				= self.kmh,
			mph				= self.mph,
		)
		
	def getPhoto( self ):
		if self.jpg is None:
			return None

		frame = CVUtil.jpegToFrame(self.jpg)
		if self.contrast.GetValue():
			frame = CVUtil.adjustContrastFrame( frame )
		if self.sharpen.GetValue():
			frame = CVUtil.sharpenFrame( frame )
		if self.grayscale.GetValue():
			frame = CVUtil.grayscaleFrame( frame )
		
		return self.addPhotoHeaderToBitmap( CVUtil.frameToBitmap(frame) )
	
	def drawCallback( self, dc, width, height ):
		if self.jpg is None:
			return None

		# Add the frame timestamps and offset into.
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
		self.onPhotoHeader()
	
	def onPrint( self, event ):
		self.playStop()
		PrintPhoto( self, self.scaledBitmap.GetDisplayBitmap() )
		
	def onCopyToClipboard( self, event ):
		self.playStop()
		if wx.TheClipboard.Open():
			bmData = wx.BitmapDataObject()
			bmData.SetBitmap( self.scaledBitmap.GetDisplayBitmap() )
			wx.TheClipboard.SetData( bmData )
			wx.TheClipboard.Flush() 
			wx.TheClipboard.Close()
			wx.MessageBox( _('Successfully copied to clipboard'), _('Success') )
		else:
			wx.MessageBox( _('Unable to open the clipboard'), _('Error') )
		
	def onSavePng( self, event ):
		self.playStop()
		fd = wx.FileDialog( self, message='Save Photo', wildcard='*.png', style=wx.FD_SAVE )
		if fd.ShowModal() == wx.ID_OK:
			try:
				self.scaledBitmap.GetDisplayBitmap().SaveFile( fd.GetPath(), wx.BITMAP_TYPE_PNG )
				wx.MessageBox( _('Photo Save Successful'), _('Success') )
			except Exception as e:
				wx.MessageBox( _('Photo Save Failed:\n\n{}').format(e), _('Save Failed') )
		fd.Destroy()

	def onSaveMP4( self, event ):
		self.playStop()
		fd = wx.FileDialog( self, message='Save MP4', wildcard='*.mp4', style=wx.FD_SAVE )
		if fd.ShowModal() == wx.ID_OK:
			work = wx.BusyCursor()
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
		fd.Destroy()

	def onSaveGif( self, event ):
		self.playStop()
		fd = wx.FileDialog( self, message='Save Animated Gif', wildcard='*.gif', style=wx.FD_SAVE )
		if fd.ShowModal() == wx.ID_OK:
			work = wx.BusyCursor()
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
		fd.Destroy()

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

