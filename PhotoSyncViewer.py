import wx
import os
import sys
import Model
import Utils
import PhotoFinish
import VideoBuffer

def getRiderName( info ):
	lastName = info.get('LastName','')
	firstName = info.get('FirstName','')
	if lastName:
		if firstName:
			return '%s, %s' % (lastName, firstName)
		else:
			return lastName
	return firstName
	
def getTitle( num, t ):
	if not num:
		return ''
		
	try:
		externalInfo = Model.race.excelLink.read()
	except:
		name = str(num)
	else:
		info = externalInfo.get(num, {})
		name = getRiderName( info )
		if info.get('Team', ''):
			name = '%d: %s  (%s)' % (num, name, info.get('Team', '').strip())
			
	name = '%s - %s' % (name, Utils.formatTime(t, True))
	return name

def RescaleImage( image, width, height ):
	bWidth, bHeight = image.GetWidth(), image.GetHeight()
	# Keep the same aspect ratio.
	ar = float(bHeight) / float(bWidth)
	if width * ar > height:
		width = height / ar
	image.Rescale( int(width), int(height), wx.IMAGE_QUALITY_NORMAL )
	return image
	
def RescaleBitmap( dc, bitmap, width, height ):
	bWidth, bHeight = bitmap.GetWidth(), bitmap.GetHeight()
	# Keep the same aspect ratio.
	ar = float(bHeight) / float(bWidth)
	if width * ar > height:
		width = height / ar
	image = bitmap.ConvertToImage()
	image.Rescale( int(width), int(height), wx.IMAGE_QUALITY_HIGH )
	if dc.GetDepth() == 8:
		image = image.ConvertToGreyscale()
	return image.ConvertToBitmap( dc.GetDepth() )
	
class PhotoSyncViewerDialog( wx.Dialog ):
	def __init__(
			self, parent, ID, title='Photo Sync Previewer', size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER ):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		pre = wx.PreDialog()
		#pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)
		
		self.timeFrames = []

		self.vbs = wx.BoxSizer(wx.VERTICAL)
		
		self.title = wx.StaticText( self, wx.ID_ANY, '', style=wx.ALIGN_LEFT )
		self.title.SetFont( wx.FontFromPixelSize( wx.Size(0,24), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL ) )
		
		self.captureButton = wx.ToggleButton( self, wx.ID_ANY, 'Reset Photo Capture' )
		self.captureButton.Bind( wx.EVT_TOGGLEBUTTON, self.OnCapture )
		self.captureCount = 0
		
		self.scrolledWindow = wx.ScrolledWindow( self, wx.ID_ANY )
		self.numPhotoSeries = 4
		self.numPhotos = 18
		self.iSeries = 0
		self.photoWidth, self.photoHeight = int(2 * 320 / 4), int(2 * 240 / 4)
		self.hgap = 4
		gs = wx.FlexGridSizer( rows = 2 * self.numPhotoSeries, cols = self.numPhotos, hgap = self.hgap, vgap = 4 )
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'CrossMgrSplash.png'), wx.BITMAP_TYPE_PNG )
		self.bitmap = RescaleBitmap( wx.WindowDC(self), bitmap, self.photoWidth, self.photoHeight )
		
		self.photoBitmaps = [[wx.BitmapButton(
									self.scrolledWindow, wx.ID_ANY,
									bitmap=self.bitmap, size=(self.photoWidth+4,self.photoHeight+4),
									style=wx.BU_AUTODRAW)
								for i in xrange(self.numPhotos)] for s in xrange(self.numPhotoSeries)]
		self.photoLabels = [[wx.StaticText(self.scrolledWindow, wx.ID_ANY, style=wx.ALIGN_CENTRE) for i in xrange(self.numPhotos)]
								for s in xrange(self.numPhotoSeries)]
		self.titles = [''] * self.numPhotoSeries
		for s in xrange(self.numPhotoSeries):
			for i, p in enumerate(self.photoLabels[s]):
				p.SetLabel( str(i) )
			for i, w in enumerate(self.photoBitmaps[s]):
				w.Bind( wx.EVT_BUTTON, lambda event, s = s, i = i: self.OnBitmapButton(event, s, i) )
				w.Bind( wx.EVT_MOTION, lambda event, s = s, i = i: self.OnMouseMove(event, s, i) )
			gs.AddMany( (w,0,) for w in self.photoBitmaps[s] )
			gs.AddMany( (w,1,wx.ALIGN_CENTER_HORIZONTAL) for w in self.photoLabels[s] )
		
		self.scrolledWindow.SetSizer( gs )
		self.scrolledWindow.Fit()
		width, height = self.scrolledWindow.GetBestSize()
		self.scrolledWindow.SetVirtualSize( (width, height) )
		self.scrolledWindow.SetScrollRate( 20, 20 )
		self.scrolledWindow.SetScrollbars( 1, 1, width, height )
		
		wx.CallAfter( self.ScrollToPicture, self.numPhotos // 2 )
		
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( self.title, 1, flag=wx.ALL, border = 2 )
		hb.Add( self.captureButton, 0, flag=wx.ALL|wx.ALIGN_RIGHT, border = 2 )
		self.vbs.Add( hb, 0, wx.EXPAND )
		self.vbs.Add( self.scrolledWindow, 1, wx.EXPAND )
		
		self.SetSizer( self.vbs )
		
		displayWidth, displayHeight = wx.GetDisplaySize()
		self.SetSize( (int(displayWidth * 0.75), min(height + 80, int(wx.GetDisplaySize()[1] * 0.9))) )
		self.vbs.Layout()
		
		self.clear()

	def OnCapture( self, event ):
		if self.captureButton.GetValue():
			self.reset()
			
	def reset( self ):
		self.captureCount = 0
		self.iSeries = 0
		self.captureButton.SetValue( True )
		self.clear()
		
	def OnMouseMove( self, event, s, i ):
		self.title.SetLabel( self.titles[s] )
		
	def OnBitmapButton( self, event, s, i ):
		label = self.photoLabels[s][i].GetLabel()
		fields = label.split()
		if len(fields) < 1:
			return
		milliseconds = fields[0]
		if milliseconds and Model.race:
			Model.race.advancePhotoMilliseconds = int( milliseconds )
			Utils.MessageOK( self, _('Advance/Delay Photo Milliseconds set to {}').format(milliseconds), 'Advance/Delay Milliseconds' )
		
	def OnClose( self, event ):
		self.Show( False )
		
	def ScrollToPicture( self, iPicture ):
		xScroll = 0
		for i, b in enumerate(self.photoBitmaps[self.iSeries]):
			if i == iPicture:
				break
			xScroll += b.GetSize().GetWidth() + self.hgap
		self.scrolledWindow.Scroll( xScroll / self.scrolledWindow.GetScrollPixelsPerUnit()[0], -1 )
			
	def clear( self ):
		self.timeFrames = []
		self.titles = [''] * self.numPhotoSeries
		for s in xrange(self.numPhotoSeries):
			for w in self.photoBitmaps[s]:
				w.SetBitmapLabel( self.bitmap )
			for w in self.photoLabels[s]:
				w.SetLabel( '' )
		
	def refresh( self, videoBuffer, t, num = None ):
		if not videoBuffer:
			for s in xrange(self.len(self.photoLabels)):
				for i in xrange(len(self.photoLabels[s])):
					self.photoBitmaps[s][i].SetBitmapLabel( self.bitmap )
					self.photoLabels[s][i].SetLabel( '' )
			return
	
		if not self.captureButton.GetValue():
			return
	
		timeFrames = videoBuffer.findBeforeAfter( t, self.numPhotos // 2, self.numPhotos // 2 )
		deltaMS = [int((tFrame - t) * 1000.0) for tFrame, frame in timeFrames]
		
		if len(timeFrames) < self.numPhotos:
			d = self.numPhotos - len(timeFrames)
			timeFrames = ([(None, None)] * d) + timeFrames
			deltaMS = ([None] * d) + deltaMS
		
		photoLabels = self.photoLabels[self.iSeries]
		photoBitmaps = self.photoBitmaps[self.iSeries]
		
		deltaMin = sys.float_info.max
		iMin = 0
		dc = wx.WindowDC( self )
		for i, (tFrame, frame) in enumerate(timeFrames):
			if deltaMS[i] is not None and abs(deltaMS[i]) < deltaMin:
				deltaMin = abs(deltaMS[i])
				iMin = i
			if deltaMS[i] is None:
				photoLabels[i].SetLabel( '' )
				photoBitmaps[i].SetBitmapLabel( wx.NullBitmap )
			else:
				photoLabels[i].SetLabel( str(deltaMS[i]) + ' ms')
				image = PhotoFinish.PilImageToWxImage( frame )
				image = RescaleImage( image, self.photoWidth, self.photoHeight )
				bitmap = image.ConvertToBitmap( dc.GetDepth() )
				photoBitmaps[i].SetBitmapLabel( bitmap )

		self.titles[self.iSeries] = getTitle( num, t )
		self.title.SetLabel( self.titles[self.iSeries] )
		
		self.Refresh()
		
		self.iSeries = (self.iSeries + 1) % self.numPhotoSeries
		
		self.captureCount += 1
		if self.captureCount >= self.numPhotoSeries:
			self.captureButton.SetValue( False )
				
photoSyncViewer = None
def PhotoSyncViewerShow( parent ):
	global photoSyncViewer
	if not photoSyncViewer:
		photoSyncViewer = PhotoSyncViewerDialog( parent, wx.ID_ANY, "Photo Sync Viewer" )
	photoSyncViewer.reset()
	photoSyncViewer.Show( True )
	
def PhotoSyncViewerIsShown():
	global photoSyncViewer
	return photoSyncViewer and photoSyncViewer.IsShown()
	
def PhotoSyncViewerHide():
	if not photoSyncViewer:
		return
	photoSyncViewer.Show( False )
	photoSyncViewer.clear()

def StartPhotoSyncViewer( parent ):
	PhotoSyncViewerShow( parent )
	
def Shutdown():
	PhotoSyncViewerHide()

if __name__ == '__main__':
	import time
	import datetime
	import shutil
	
	race = Model.newRace()
	race._populate()

	app = wx.PySimpleApp()
	
	dirName = 'VideoBufferTest_Photos'
	if os.path.isdir(dirName):
		shutil.rmtree( dirName, True )
	os.mkdir( dirName )
	
	tRef = datetime.datetime.now()
	camera = PhotoFinish.SetCameraState( True )
	vb = VideoBuffer.VideoBuffer( camera, tRef, dirName )
	vb.start()
	time.sleep( 1.0 )
	
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	mainWin.Show()
	photoSyncDialog = PhotoSyncViewerDialog( mainWin, wx.ID_ANY, "PhotoSyncViewer", size=(600,400) )
	def doRefresh( bib ):
		t = (datetime.datetime.now() - tRef).total_seconds()
		wx.CallLater( 300, photoSyncDialog.refresh, vb, t, bib )
		
	photoSyncDialog.Show()
	photoSyncDialog.reset()
	bib = 100
	for d in xrange(0, 1000*60, 1000):
		wx.CallLater( d, doRefresh, bib )
		bib += 1
	app.MainLoop()
