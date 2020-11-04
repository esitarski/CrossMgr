import wx
import os
import time
import subprocess
from AddPhotoHeader import AddPhotoHeader
from ScaledBitmap import ScaledBitmap, GetScaleRatio
from ComputeSpeed import ComputeSpeed
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
		wx.Printout.__init__(self)
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
			wx.MessageBox( u'\n\n'.join( [_("There was a printer problem."), _("Check your printer setup.")] ), _("Printer Error"))
	else:
		printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )

	printout.Destroy()	

photoHeaderState = True
class PhotoDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize,
		style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX ):
			
		super().__init__( parent, id, size=size, style=style, title=_('Photo: ***Left-click and Drag in the Photo to Zoom***') )
		
		self.clear()
		
		vs = wx.BoxSizer( wx.VERTICAL )
		self.scaledBitmap = ScaledBitmap( self, inset=True )
		vs.Add( self.scaledBitmap, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.scaledBitmap.Bind( wx.EVT_MOUSEWHEEL, self.onMouseWheel )
		self.scaledBitmap.Bind( wx.EVT_KEY_DOWN, self.onKeyDown )
		
		btnsizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.timestamp = wx.StaticText(self, label='00:00:00.000')
		self.timestamp.SetFont( wx.Font( (0,24), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ) )
		btnsizer.Add( self.timestamp, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)
		
		self.playerRewind = wx.Button( self, style=wx.BU_EXACTFIT, label=u'\u23EA' )
		self.playerRewind.Bind( wx.EVT_BUTTON, lambda e: self.playRewind() )
		self.playerReverse = wx.Button( self, style=wx.BU_EXACTFIT, label=u'\u25C0' )
		self.playerReverse.Bind( wx.EVT_BUTTON, lambda e: self.playReverse() )
		self.playerForward = wx.Button( self, style=wx.BU_EXACTFIT, label=u'\u25B6' )
		self.playerForward.Bind( wx.EVT_BUTTON, lambda e: self.play() )
		self.playerStop = wx.Button( self, style=wx.BU_EXACTFIT, label=u'\u25A0' )
		self.playerStop.Bind( wx.EVT_BUTTON, lambda e: self.playStop() )		
		self.playerForwardToEnd = wx.Button( self, style=wx.BU_EXACTFIT, label=u'\u23E9' )
		self.playerForwardToEnd.Bind( wx.EVT_BUTTON, lambda e: self.playForwardToEnd() )
		
		self.frameLeft = wx.Button( self, style=wx.BU_EXACTFIT, label=u'\u25C1' )
		self.frameLeft.Bind( wx.EVT_BUTTON, lambda e: self.changeFrame(-1) )
		self.frameRight = wx.Button( self, style=wx.BU_EXACTFIT, label=u'\u25B7' )
		self.frameRight.Bind( wx.EVT_BUTTON, lambda e: self.changeFrame(1) )
				
		btnsizer.Add( self.playerRewind, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)
		btnsizer.Add( self.playerReverse, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=0)
		btnsizer.Add( self.playerForward, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=0)
		btnsizer.Add( self.playerStop, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=0)
		btnsizer.Add( self.playerForwardToEnd, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=0)
		btnsizer.Add( self.frameLeft, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4)
		btnsizer.Add( self.frameRight, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=0)
		btnsizer.Add( wx.StaticText(self, label='or Mousewheel'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=2 )
        
		self.photoHeader = wx.CheckBox(self, label='Header')
		self.photoHeader.SetValue( photoHeaderState )
		self.photoHeader.Bind( wx.EVT_CHECKBOX, self.onPhotoHeader )
		btnsizer.Add(self.photoHeader, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=8)
		
		self.contrast = wx.ToggleButton( self, label='Contrast', style=wx.BU_EXACTFIT)
		self.contrast.Bind( wx.EVT_TOGGLEBUTTON, self.onContrast )
		btnsizer.Add(self.contrast, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4)		

		btn = wx.BitmapButton(self, wx.ID_PRINT, bitmap=Utils.getBitmap('print.png'))
		btn.SetToolTip( wx.ToolTip('Print Photo') )
		btn.SetDefault()
		btn.Bind( wx.EVT_BUTTON, self.onPrint )
		btnsizer.Add(btn, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=8)
		
		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('edit_icon.png'))
		btn.SetToolTip( wx.ToolTip('Edit Trigger Info') )
		btn.Bind( wx.EVT_BUTTON, self.onEdit )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('copy-to-clipboard.png'))
		btn.SetToolTip( wx.ToolTip('Copy Photo to Clipboard') )
		btn.Bind( wx.EVT_BUTTON, self.onCopyToClipboard )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

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
		
		btnsizer.AddStretchSpacer()

		btn = wx.BitmapButton(self, wx.ID_CLOSE, bitmap=Utils.getBitmap('close-window.png'))
		btn.SetToolTip( wx.ToolTip('Close') )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)
		btn.Bind( wx.EVT_BUTTON, self.onClose )

		vs.Add( btnsizer, flag=wx.ALL|wx.EXPAND, border=5 )

		self.SetSizer(vs)
		vs.Fit(self)

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
		
		self.kmh = triggerInfo.get('kmh',0.0) or 0.0
		self.mps = self.kmh / 3.6
		self.mph = self.kmh * 0.621371
		self.pps = 2000.0
		
		self.scaledBitmap.SetBitmap( self.getPhoto() )
		
		sz = self.scaledBitmap.GetBitmap().GetSize()
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
		
		w, h = self.GetSize()
		if w < wSize[0] or h < wSize[1]:
			self.SetSize( wSize )
		self.timestamp.SetLabel( self.ts.strftime('%H:%M:%S.%f')[:-3] )
	
	def changeFrame( self, frameDir ):
		if self.iJpg is None:
			return
		if frameDir < 0:
			self.iJpg = max(0, self.iJpg-1 )
		elif frameDir > 0:
			self.iJpg = min(len(self.tsJpg)-1, self.iJpg+1 )
		else:
			self.iJpg = 0
		self.set( self.iJpg, self.triggerInfo, self.tsJpg, self.fps, self.editCB )
		self.Refresh()
	
	def onMouseWheel( self, event ):
		self.changeFrame( event.GetWheelRotation() )
	
	def onKeyDown( self, event ):
		self.changeFrame( -1 if event.ShiftDown() else 1 )
	
	def playNextFrame( self ):
		if self.keepPlayingForward:
			self.changeFrame( 1 )
			if self.iJpg < len(self.tsJpg)-1:
				wx.CallLater( int((self.tsJpg[self.iJpg+1][0] - self.tsJpg[self.iJpg][0]).total_seconds()*1000.0), self.playNextFrame )
	
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
		
	def clear( self ):
		self.playStop()
		self.iJpg = None
		self.triggerInfo = None
		self.tsJpg = None
		self.fps = None
		self.editCB = None
	
	def onEdit( self, event ):
		if self.editCB:
			self.triggerInfo = self.editCB()
			self.Refresh()
	
	def onContrast( self, event ):
		self.scaledBitmap.SetBitmap( CVUtil.adjustContrastBitmap(self.getPhoto()) if self.contrast.GetValue() else self.getPhoto() )
	
	def onBrightness( self, event ):
		pass
	
	def onPhotoHeader( self, event=None ):
		global photoHeaderState
		photoHeaderState = self.photoHeader.GetValue()
		self.scaledBitmap.SetBitmap(self.getPhoto())
	
	def addPhotoHeaderToBitmap( self, bitmap ):
		if not photoHeaderState:
			return bitmap
		
		return AddPhotoHeader(
			bitmap,
			ts=self.triggerInfo['ts'],
			bib=self.triggerInfo['bib'],
			first_name=self.triggerInfo['first_name'],
			last_name=self.triggerInfo['last_name'],
			team=self.triggerInfo['team'],
			race_name=self.triggerInfo['race_name'],
			kmh=self.kmh,
			mph=self.mph,
		)
		
	def getPhoto( self ):
		if self.jpg is None:
			return None
		return self.addPhotoHeaderToBitmap( CVUtil.jpegToBitmap(self.jpg) )
		
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
