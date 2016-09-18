import wx
import subprocess
import cStringIO as StringIO
from ScaledImage import ScaledImage, RescaleImage
import Utils

def _( x ):
	return x

class PhotoPrintout( wx.Printout ):
	def __init__(self, image):
		wx.Printout.__init__(self)
		self.image = image

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
		image = RescaleImage( self.image, drawWidth, drawHeight, wx.IMAGE_QUALITY_HIGH )
		bitmap = wx.BitmapFromImage( image )
		dcBitmap = wx.MemoryDC( bitmap )
		
		dc.Blit( border, border, image.GetSize()[0], image.GetSize()[1], dcBitmap, 0, 0 )
		
		dcBitmap.SelectObject( wx.NullBitmap )
		return True

def PrintPhoto( parent, image ):
	printData = wx.PrintData()
	printData.SetPaperId(wx.PAPER_LETTER)
	printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
	printData.SetOrientation(wx.LANDSCAPE)
	
	pdd = wx.PrintDialogData(printData)
	pdd.SetAllPages( True )
	pdd.EnableSelection( False )
	pdd.EnablePageNumbers( False )
	pdd.EnableHelp( False )
	pdd.EnablePrintToFile( False )
	
	printer = wx.Printer(pdd)
	printout = PhotoPrintout( image )

	if not printer.Print(parent, printout, True):
		if printer.GetLastError() == wx.PRINTER_ERROR:
			wx.MessageBox( u'\n\n'.join( [_("There was a printer problem."), _("Check your printer setup.")] ), _("Printer Error"))
	else:
		printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )

	printout.Destroy()	


class PhotoDialog( wx.Dialog ):
	def __init__( self, parent, photoImage, tsJpg, id=wx.ID_ANY, size=wx.DefaultSize,
		style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX ):
			
		super(PhotoDialog, self).__init__( parent, id, size=size, style=style, title=_('Photo') )
		
		self.tsJpg = tsJpg
		
		vs = wx.BoxSizer( wx.VERTICAL )
		self.scaledImage = ScaledImage( self, image=photoImage )
		vs.Add( self.scaledImage, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		btnsizer = wx.WrapSizer()
        
		btn = wx.Button(self, wx.ID_PRINT)
		btn.SetDefault()
		btn.Bind( wx.EVT_BUTTON, self.onPrint )
		btnsizer.Add(btn)

		btn = wx.Button(self, label='Copy to Clipboard')
		btn.Bind( wx.EVT_BUTTON, self.onCopyToClipboard )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.Button(self, label='Save Photo...')
		btn.Bind( wx.EVT_BUTTON, self.onSavePhoto )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.Button(self, label='Save mpeg...')
		btn.Bind( wx.EVT_BUTTON, self.onSaveMPeg )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.Button(self, wx.ID_CLOSE)
		btnsizer.Add(btn, flag=wx.LEFT, border=4)
		btn.Bind( wx.EVT_BUTTON, self.onClose )

		vs.Add( btnsizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND|wx.ALIGN_CENTRE, border=5 )

		self.SetSizer(vs)
		vs.Fit(self)
	
	def onClose( self, event ):
		self.EndModal( wx.ID_OK )
	
	def onPrint( self, event ):
		PrintPhoto( self, self.scaledImage.GetImage() )
		
	def onCopyToClipboard( self, event ):
		if wx.TheClipboard.Open():
			bmData = wx.BitmapDataObject()
			bmData.SetBitmap( wx.BitmapFromImage(self.scaledImage.GetImage()) )
			wx.TheClipboard.SetData( bmData )
			wx.TheClipboard.Flush() 
			wx.TheClipboard.Close()
			wx.MessageBox( _('Successfully copied to clipboard'), _('Success') )
		else:
			wx.MessageBox( _('Unable to open the clipboard'), _('Error') )
		
	def onSavePhoto( self, event ):
		fd = wx.FileDialog( self, message='Save Photo', wildcard='*.png', style=wx.FD_SAVE )
		if fd.ShowModal() == wx.ID_OK:
			try:
				self.scaledImage.GetImage().SaveFile( fd.GetPath(), wx.BITMAP_TYPE_PNG )
				wx.MessageBox( _('Photo Save Successful'), _('Success') )
			except Exception as e:
				wx.MessageBox( _('Photo Save Failed:\n\n{}').format(e), _('Save Failed') )
		fd.Destroy()

	def onSaveMPeg( self, event ):
		fd = wx.FileDialog( self, message='Save MPeg', wildcard='*.mpeg', style=wx.FD_SAVE )
		if fd.ShowModal() == wx.ID_OK:
			image = wx.ImageFromStream( StringIO.StringIO(self.tsJpg[0][1]), wx.BITMAP_TYPE_JPEG )
			try:
				command = [
					Utils.getFFMegExe(),
					'-y', # (optional) overwrite output file if it exists
					'-f', 'rawvideo',
					'-vcodec','rawvideo',
					'-s', '{}x{}'.format(*image.GetSize()), # size of one frame
					'-pix_fmt', 'rgb24',
					'-r', '25', # frames per second
					'-i', '-', # The imput comes from a pipe
					'-an', # Tells FFMPEG not to expect any audio
					'-vcodec', 'mpeg1video',
					fd.GetPath(),
				]
				proc = subprocess.Popen( command, stdin=subprocess.PIPE, stderr=subprocess.PIPE )
				for ts, jpg in self.tsJpg:
					image = wx.ImageFromStream( StringIO.StringIO(jpg), wx.BITMAP_TYPE_JPEG )
					proc.stdin.write( image.GetData() )
				proc.terminate()
				wx.MessageBox( _('MPeg Save Successful'), _('Success') )
			except Exception as e:
				wx.MessageBox( _('MPeg Save Failed:\n\n{}').format(e), _('Save Failed') )
		fd.Destroy()
