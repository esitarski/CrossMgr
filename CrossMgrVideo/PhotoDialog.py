import wx
import subprocess
import cStringIO as StringIO
from AddPhotoHeader import AddPhotoHeader
from ScaledImage import ScaledImage, RescaleImage
from ComputeSpeed import ComputeSpeed
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

photoHeaderState = True
class PhotoDialog( wx.Dialog ):
	def __init__( self, parent, jpg, triggerInfo, tsJpg, fps=25, id=wx.ID_ANY, size=wx.DefaultSize,
		style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX ):
			
		super(PhotoDialog, self).__init__( parent, id, size=size, style=style, title=_('Photo') )
		
		self.jpg = jpg
		self.triggerInfo = triggerInfo
		self.tsJpg = tsJpg
		self.fps = fps
		
		vs = wx.BoxSizer( wx.VERTICAL )
		self.scaledImage = ScaledImage( self, image=self.getPhoto() )
		vs.Add( self.scaledImage, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		btnsizer = wx.BoxSizer( wx.HORIZONTAL )
        
		self.photoHeader = wx.CheckBox(self, label='Header')
		self.photoHeader.SetValue( photoHeaderState )
		self.photoHeader.Bind( wx.EVT_CHECKBOX, self.onPhotoHeader )
		btnsizer.Add(self.photoHeader, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4)

		btn = wx.Button(self, wx.ID_PRINT)
		btn.SetDefault()
		btn.Bind( wx.EVT_BUTTON, self.onPrint )
		btnsizer.Add(btn, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4)
		
		btn = wx.Button(self, label='Copy to Clipboard')
		btn.Bind( wx.EVT_BUTTON, self.onCopyToClipboard )
		btnsizer.Add(btn, flag=wx.LEFT, border=8)

		btn = wx.Button(self, label='Save as PNG...')
		btn.Bind( wx.EVT_BUTTON, self.onSavePng )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.Button(self, label='Save as Mpeg...')
		btn.Bind( wx.EVT_BUTTON, self.onSaveMPeg )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.Button(self, label='Save as Anim. Gif...')
		btn.Bind( wx.EVT_BUTTON, self.onSaveGif )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.Button(self, label='Speed')
		btn.Bind( wx.EVT_BUTTON, self.onGetSpeed )
		btnsizer.Add(btn, flag=wx.LEFT, border=4)

		btn = wx.Button(self, wx.ID_CLOSE)
		btnsizer.Add(btn, flag=wx.LEFT, border=4)
		btn.Bind( wx.EVT_BUTTON, self.onClose )

		vs.Add( btnsizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND|wx.ALIGN_CENTRE, border=5 )

		self.SetSizer(vs)
		vs.Fit(self)
	
	def onPhotoHeader( self, event ):
		global photoHeaderState
		photoHeaderState = self.photoHeader.GetValue()
		self.scaledImage.SetImage(self.getPhoto())
	
	def addPhotoHeaderToImage( self, image ):
		if not photoHeaderState:
			return image
		
		return AddPhotoHeader(
			wx.BitmapFromImage( image ),
			ts=self.triggerInfo['ts'],
			bib=self.triggerInfo['bib'],
			firstName=self.triggerInfo['firstName'],
			lastName=self.triggerInfo['lastName'],
			team=self.triggerInfo['team'],
			raceName=self.triggerInfo['raceName'],
		)
		
	def getPhoto( self ):
		if self.jpg is None:
			return None
		return self.addPhotoHeaderToImage( wx.ImageFromStream(StringIO.StringIO(self.jpg), wx.BITMAP_TYPE_JPEG) )
		
	def onClose( self, event ):
		self.EndModal( wx.ID_OK )
	
	def onGetSpeed( self, event ):
		tSearch = self.triggerInfo['ts']
		t1, image1, t2, image2 = None, None, None, None
		for i, (ts, jpg) in enumerate(self.tsJpg):
			if ts >= tSearch:
				t1 = ts
				image1 = wx.ImageFromStream( StringIO.StringIO(jpg), wx.BITMAP_TYPE_JPEG )
				iNext = min( len(self.tsJpg)-1, i + self.fps // 4 )
				t2 = self.tsJpg[iNext][0]
				image2 = wx.ImageFromStream( StringIO.StringIO(self.tsJpg[iNext][1]), wx.BITMAP_TYPE_JPEG )
				break
		
		computeSpeed = ComputeSpeed(self, size=image1.GetSize())
		computeSpeed.Show( image1, t1, image2, t2 )
	
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
		
	def onSavePng( self, event ):
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
			try:
				command = [
					Utils.getFFMegExe(),
					'-y', # (optional) overwrite output file if it exists
					'-f', 'rawvideo',
					'-vcodec','rawvideo',
					'-s', '{}x{}'.format(*self.scaledImage.GetImage().GetSize()), # size of one frame
					'-pix_fmt', 'rgb24',
					'-r', '{}'.format(self.fps), # frames per second
					'-i', '-', # The imput comes from a pipe
					'-an', # Tells FFMPEG not to expect any audio
					'-vcodec', 'mpeg1video',
					fd.GetPath(),
				]
				proc = subprocess.Popen( command, stdin=subprocess.PIPE, stderr=subprocess.PIPE )
				for ts, jpg in self.tsJpg:
					proc.stdin.write( self.addPhotoHeaderToImage(wx.ImageFromStream(StringIO.StringIO(jpg), wx.BITMAP_TYPE_JPEG)).GetData() )
				proc.terminate()
				wx.MessageBox( _('MPeg Save Successful'), _('Success') )
			except Exception as e:
				wx.MessageBox( _('MPeg Save Failed:\n\n{}').format(e), _('Save Failed') )
		fd.Destroy()

	def onSaveGif( self, event ):
		fd = wx.FileDialog( self, message='Save Animaged Gif', wildcard='*.gif', style=wx.FD_SAVE )
		if fd.ShowModal() == wx.ID_OK:
			try:
				command = [
					Utils.getFFMegExe(),
					'-y', # (optional) overwrite output file if it exists
					'-f', 'rawvideo',
					'-vcodec','rawvideo',
					'-s', '{}x{}'.format(*self.scaledImage.GetImage().GetSize()), # size of one frame
					'-pix_fmt', 'rgb24',
					'-r', '{}'.format(self.fps), # frames per second
					'-i', '-', # The imput comes from a pipe
					'-an', # Tells FFMPEG not to expect any audio
					fd.GetPath(),
				]
				proc = subprocess.Popen( command, stdin=subprocess.PIPE, stderr=subprocess.PIPE )
				for ts, jpg in self.tsJpg:
					proc.stdin.write(self.addPhotoHeaderToImage(wx.ImageFromStream(StringIO.StringIO(jpg), wx.BITMAP_TYPE_JPEG)).GetData() )
				images = None
				proc.terminate()
				wx.MessageBox( _('Gif Save Successful'), _('Success') )
			except Exception as e:
				wx.MessageBox( _('Gif Save Failed:\n\n{}').format(e), _('Save Failed') )
		fd.Destroy()
