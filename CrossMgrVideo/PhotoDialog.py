import wx
import os
import subprocess
import cStringIO as StringIO
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
			
		super(PhotoDialog, self).__init__( parent, id, size=size, style=style, title=_('Photo') )
		
		self.clear()
		
		vs = wx.BoxSizer( wx.VERTICAL )
		self.scaledBitmap = ScaledBitmap( self, inset=True )
		vs.Add( self.scaledBitmap, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		btnsizer = wx.BoxSizer( wx.HORIZONTAL )
        
		self.photoHeader = wx.CheckBox(self, label='Header')
		self.photoHeader.SetValue( photoHeaderState )
		self.photoHeader.Bind( wx.EVT_CHECKBOX, self.onPhotoHeader )
		btnsizer.Add(self.photoHeader, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4)
		
		self.contrast = wx.ToggleButton( self, label='Contrast')
		self.contrast.Bind( wx.EVT_TOGGLEBUTTON, self.onContrast )
		btnsizer.Add(self.contrast, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4)		

		btn = wx.BitmapButton(self, wx.ID_PRINT, bitmap=Utils.getBitmap('print.png'))
		btn.SetToolTip( wx.ToolTip('Print Photo') )
		btn.SetDefault()
		btn.Bind( wx.EVT_BUTTON, self.onPrint )
		btnsizer.Add(btn, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=32)
		
		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('copy-to-clipboard.png'))
		btn.SetToolTip( wx.ToolTip('Copy Photo to Clipboard') )
		btn.Bind( wx.EVT_BUTTON, self.onCopyToClipboard )
		btnsizer.Add(btn, flag=wx.LEFT, border=32)

		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('png.png'))
		btn.SetToolTip( wx.ToolTip('Save Photo as PNG file') )
		btn.Bind( wx.EVT_BUTTON, self.onSavePng )
		btnsizer.Add(btn, flag=wx.LEFT, border=32)

		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('mpg.png'))
		btn.SetToolTip( wx.ToolTip('Save Sequence as Mpeg') )
		btn.Bind( wx.EVT_BUTTON, self.onSaveMPeg )
		btnsizer.Add(btn, flag=wx.LEFT, border=32)

		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('gif.png'))
		btn.SetToolTip( wx.ToolTip('Save Sequence as Animated Gif') )
		btn.Bind( wx.EVT_BUTTON, self.onSaveGif )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.BitmapButton(self, bitmap=Utils.getBitmap('speedometer.png'))
		btn.SetToolTip( wx.ToolTip('Get Speed') )
		btn.Bind( wx.EVT_BUTTON, self.onGetSpeed )
		btnsizer.Add(btn, flag=wx.LEFT, border=32)
		
		self.speedFrames = wx.Choice(self, choices=['Use 1 Frame', 'Use 2 Frames', 'Use 3 Frames', 'Use 4 Frames'] )
		self.speedFrames.SetSelection( 1 )
		btnsizer.Add(self.speedFrames, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=2)
		
		btnsizer.AddStretchSpacer()

		btn = wx.BitmapButton(self, wx.ID_CLOSE, bitmap=Utils.getBitmap('close-window.png'))
		btn.SetToolTip( wx.ToolTip('Close') )
		btnsizer.Add(btn, flag=wx.LEFT|wx.ALIGN_RIGHT, border=4)
		btn.Bind( wx.EVT_BUTTON, self.onClose )

		vs.Add( btnsizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND|wx.ALIGN_CENTRE, border=5 )

		self.SetSizer(vs)
		vs.Fit(self)

	def set( self, jpg, triggerInfo, tsJpg, fps=25 ):
		self.jpg = jpg
		self.triggerInfo = triggerInfo
		self.tsJpg = tsJpg
		self.fps = fps
		
		self.kmh = triggerInfo['kmh'] or 0.0
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
		if self.GetSize() != wSize:
			self.SetSize( wSize )
	
	def clear( self ):
		self.jpg = None
		self.triggerInfo = None
		self.tsJpg = None
		self.fps = None
	
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
			firstName=self.triggerInfo['firstName'],
			lastName=self.triggerInfo['lastName'],
			team=self.triggerInfo['team'],
			raceName=self.triggerInfo['raceName'],
			kmh=self.kmh,
			mph=self.mph,
		)
		
	def getPhoto( self ):
		if self.jpg is None:
			return None
		return self.addPhotoHeaderToBitmap( CVUtil.jpegToBitmap(self.jpg) )
		
	def onClose( self, event ):
		self.EndModal( wx.ID_OK )
	
	def onGetSpeed( self, event ):
		t1, bitmap1, t2, bitmap2 = None, None, None, None
		speedFrames = self.speedFrames.GetSelection() + 1
		i1, i2 = len(self.tsJpg)-(speedFrames+1), len(self.tsJpg)-1
		
		for i, (ts, jpg) in enumerate(self.tsJpg):
			if jpg == self.jpg:
				if i == 0:
					i1, i2 = 0, speedFrames
				else:
					i1, i2  = i-speedFrames, i
				break
		
		i1 = min( max(0, i1), len(self.tsJpg)-1 )
		i2 = min( max(0, i2), len(self.tsJpg)-1 )
		if i1 == i2:
			return
		
		t1 = self.tsJpg[i1][0]
		bitmap1 = CVUtil.jpegToBitmap(self.tsJpg[i1][1])
		t2 = self.tsJpg[i2][0]
		bitmap2 = CVUtil.jpegToBitmap(self.tsJpg[i2][1])
				
		computeSpeed = ComputeSpeed( self, size=self.GetSize() )
		self.mps, self.kmh, self.mph, self.pps = computeSpeed.Show( bitmap1, t1, bitmap2, t2, self.triggerInfo['ts_start'] )
		self.onPhotoHeader()
	
	def onPrint( self, event ):
		PrintPhoto( self, self.scaledBitmap.GetDisplayBitmap() )
		
	def onCopyToClipboard( self, event ):
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
		fd = wx.FileDialog( self, message='Save Photo', wildcard='*.png', style=wx.FD_SAVE )
		if fd.ShowModal() == wx.ID_OK:
			try:
				self.scaledBitmap.GetDisplayBitmap().SaveFile( fd.GetPath(), wx.BITMAP_TYPE_PNG )
				wx.MessageBox( _('Photo Save Successful'), _('Success') )
			except Exception as e:
				wx.MessageBox( _('Photo Save Failed:\n\n{}').format(e), _('Save Failed') )
		fd.Destroy()

	def onSaveMPeg( self, event ):
		fd = wx.FileDialog( self, message='Save MPeg', wildcard='*.mpeg', style=wx.FD_SAVE )
		if fd.ShowModal() == wx.ID_OK:
			work = wx.BusyCursor()
			try:
				command = [
					Utils.getFFMegExe(),
					Utils.getFFMegExe(),
					'-y', # (optional) overwrite output file if it exists
					'-f', 'image2pipe',
					'-r', '{}'.format(self.fps), # frames per second
					'-i', '-', # The input comes from a pipe
					'-an', # Tells FFMPEG not to expect any audio
					'-filter:v', 'setpts=5.0*PTS',	# Slow down the output.
					'-vcodec', 'mpeg2video',
					fd.GetPath(),
				]
				proc = subprocess.Popen( command, stdin=subprocess.PIPE, stderr=subprocess.PIPE )
				for i, (ts, jpg) in enumerate(self.tsJpg):
					print 'photo', i
					proc.stdin.write( jpg )
				proc.stdin.close()
				proc.terminate()
				wx.MessageBox( _('MPeg Save Successful'), _('Success') )
			except Exception as e:
				wx.MessageBox( _('MPeg Save Failed:\n\n{}').format(e), _('Save Failed') )
		fd.Destroy()

	def onSaveGif( self, event ):
		fd = wx.FileDialog( self, message='Save Animated Gif', wildcard='*.gif', style=wx.FD_SAVE )
		if fd.ShowModal() == wx.ID_OK:
			work = wx.BusyCursor()
			try:
				command = [
					Utils.getFFMegExe(),
					'-y', # (optional) overwrite output file if it exists
					'-f', 'image2pipe',
					'-r', '{}'.format(self.fps), # frames per second
					'-i', '-', # The input comes from a pipe
					'-an', # Tells FFMPEG not to expect any audio
					fd.GetPath(),
				]
				proc = subprocess.Popen( command, stdin=subprocess.PIPE, stderr=subprocess.PIPE )
				for i, (ts, jpg) in enumerate(self.tsJpg):
					print 'photo', i
					proc.stdin.write( jpg )
				print 'Closing stdin'
				proc.stdin.close()
				print 'Teminating proc'
				proc.terminate()
				wx.MessageBox( _('Gif Save Successful'), _('Success') )
			except Exception as e:
				wx.MessageBox( _('Gif Save Failed:\n\n{}').format(e), _('Save Failed') )
		fd.Destroy()
