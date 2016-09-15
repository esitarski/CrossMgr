import wx
import os
import sys
import glob
import math
import datetime
import cStringIO as StringIO
from bisect import bisect_left
from MakeComposite import MakeComposite

def _( s ):
	return s
	
def PilImageToWxImage(pil, alpha=False):
	"""Convert PIL Image to wx.Image."""
	image = wx.EmptyImage( *pil.size )
	image.SetData( pil.convert("RGB").tobytes() )

	if alpha and pilImage.mode[-1] == 'A':
		image.SetAlphaData(pil.convert("RGBA").tobytes()[3::4])

	return image

contrastColour = wx.Colour( 255, 130, 0 )

photoWidth = 640
photoHeight = 480

class FinishStrip( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize, style=0,
			fps=25,
			leftToRight=False, mouseWheelCallback = None ):
		super(FinishStrip, self).__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		
		self.fps = float(fps)
		self.scale = 1.0
		self.xTimeLine = None
		self.magnification = 2.0
		self.mouseWheelCallback = mouseWheelCallback
		
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_ERASE_BACKGROUND, self.OnErase )
		self.Bind( wx.EVT_LEFT_DOWN, self.OnLeftDown )
		self.Bind( wx.EVT_LEFT_UP, self.OnLeftUp )
		
		self.Bind( wx.EVT_ENTER_WINDOW, self.OnEnterWindow )
		self.Bind( wx.EVT_MOTION, self.OnMotion )
		self.Bind( wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow )
		self.Bind( wx.EVT_MOUSEWHEEL, self.OnMouseWheel )
		self.xMotionLast = None
		self.yMotionLast = None
		
		self.compositeBitmap = None
		self.tsFirst = datetime.datetime.now()
		self.tsJpgs = []
		self.photoWidth = self.photoHeight = None

		self.times = []
		self.jpg = {}
		self.zoomBitmap = {}
		
		self.leftToRight = leftToRight
		self.tDrawStart = 0.0
		self.pixelsPerSec = 25
		
		self.tDrawStartCallback = None
		self.jpgWidth = self.jpgHeight = None
		
		tMin, tMax = self.GetTimeMinMax()
		if tMin is not None:
			self.tDrawStart = tMin
		
	def formatTime( self, t ):
		return (self.tsFirst + datetime.timedelta(seconds=t)).strftime('%H:%M:%S.%f'[:-3])
		
	@property
	def scaledPixelsPerSec( self ):
		return self.pixelsPerSec * self.scale
	
	def SetLeftToRight( self, leftToRight=True ):
		self.leftToRight = leftToRight
		self.refreshCompositeBitmap()
		wx.CallAfter( self.Refresh )
		
	def SetPixelsPerSec( self, pixelsPerSec ):
		self.pixelsPerSec = pixelsPerSec
		self.refreshCompositeBitmap()
		wx.CallAfter( self.Refresh )

	def prefetchZoomBitmap( self, t=None ):
		if not self.times:
			return
		if not t:
			t = self.tDrawStart
		if t is None:
			return
		for i in xrange(bisect_left(self.times, t, hi=len(self.times)-1), -1, -1):
			tbm = self.times[i]
			if tbm not in self.zoomBitmap:
				image = wx.ImageFromStream( StringIO.StringIO(self.jpg[tbm]), wx.BITMAP_TYPE_JPEG )
				image.Rescale( int(photoWidth*self.magnification), int(photoHeight*self.magnification), wx.IMAGE_QUALITY_HIGH )
				self.zoomBitmap[tbm] = image.ConvertToBitmap()
				wx.CallLater( 150, self.prefetchZoomBitmap, tbm )
				break
		
	def SetDrawStartTime( self, tDrawStart ):
		self.tDrawStart = tDrawStart
		wx.CallAfter( self.prefetchZoomBitmap )
		wx.CallAfter( self.Refresh )
		
	def SetScale( self, scale ):
		self.scale = scale
		self.refreshCompositeBitmap()
		wx.CallAfter( self.Refresh )
		
	def GetTimeMinMax( self ):
		return (self.times[0], self.times[-1]) if self.times else (None, None)
		
	def GetTimePhotos( self ):
		return self.times
	
	def SetTsJpgs( self, tsJpgs ):
		self.zoomBitmap = {}
		
		if not tsJpgs:
			self.compositeBitmap = None
			self.tsFirst = datetime.datetime.now()
			self.tsJpgs = []
			return
		
		self.tsFirst = tsJpgs[0][0]
		self.tsJpgs = tsJpgs
		self.times = []
		self.jpg = {}
		for ts, jpg in tsJpgs:
			t = (ts-self.tsFirst).total_seconds()
			self.times.append( t )
			self.jpg[t] = jpg
					
		image = wx.ImageFromStream( StringIO.StringIO(tsJpgs[0][1]), wx.BITMAP_TYPE_JPEG )
		self.jpgWidth, self.jpgHeight = image.GetSize()
		self.scale = min( 1.0, float(self.GetSize()[1]) / float(self.jpgHeight) )
		if self.scale != 1.0:
			image.Rescale( int(image.GetWidth()*self.scale), int(image.GetHeight()*self.scale), wx.IMAGE_QUALITY_HIGH )
			self.zoomBitmap[0.0] = image.ConvertToBitmap()
		
		self.refreshCompositeBitmap()
	
	def refreshCompositeBitmap( self ):
		self.photoWidth, self.photoHeight, self.compositeBitmap = MakeComposite(self.tsJpgs, self.leftToRight, self.pixelsPerSec, self.scale)
		if self.compositeBitmap:
			self.compositeBitmap = wx.BitmapFromImage( PilImageToWxImage(self.compositeBitmap) )
		self.zoomBitmap = {}
		
	def OnErase( self, event ):
		pass
	
	def OnSize( self, event ):
		if self.jpgHeight is not None:
			self.scale = min( 1.0, float(event.GetSize()[1]) / float(self.jpgHeight) )
			self.refreshCompositeBitmap()
		wx.CallAfter( self.Refresh )
		event.Skip()
		
	def getXTimeLine( self ):
		winWidth, winHeight = self.GetClientSize()
		winWidthHalf = winWidth // 2
		return min( winWidth, self.xTimeLine if self.xTimeLine is not None else winWidthHalf )
		
	def OnLeftDown( self, event ):
		self.xDragLast = event.GetX()
		self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
		event.Skip()
		
	def OnLeftUp( self, event ):
		x, y = event.GetX(), event.GetY()
		self.tDrawStart += (x - self.getXTimeLine()) / float(self.scaledPixelsPerSec) * (-1.0 if self.leftToRight else 1.0)
		self.xTimeLine = x
		wx.CallAfter( self.OnLeaveWindow )
		wx.CallAfter( self.Refresh )
		if self.tDrawStartCallback:
			wx.CallAfter( self.tDrawStartCallback, self.tDrawStart )
		self.SetCursor( wx.NullCursor )
		
	def OnMouseWheel( self, event ):
		if event.ControlDown() and not event.ShiftDown():
			magnificationSave = self.magnification
			magFactor = 0.90
			if event.GetWheelRotation() < 0:
				self.magnification /= magFactor
			else:
				self.magnification *= magFactor
			
			self.magnification = min( 5.0, max(1.0, self.magnification) )
			if self.magnification != magnificationSave:
				self.zoomBitmap = {}
				wx.CallAfter( self.drawZoomPhoto, event.GetX(), event.GetY() )
		
		if self.mouseWheelCallback:
			self.mouseWheelCallback( event )
		
	def drawXorLine( self, x, y ):
		if x is None or not self.times:
			return
		
		dc = wx.ClientDC( self )
		dc.SetLogicalFunction( wx.XOR )
		
		dc.SetPen( wx.WHITE_PEN )
		winWidth, winHeight = self.GetClientSize()
		winWidthHalf = winWidth // 2
		
		xTimeLine = self.getXTimeLine()
		
		t = self.tDrawStart + (x - xTimeLine) / float(self.scaledPixelsPerSec) * (-1.0 if self.leftToRight else 1.0)
		
		text = self.formatTime( t )
		fontHeight = max(5, winHeight//20)
		font = wx.FontFromPixelSize(
			wx.Size(0,fontHeight),
			wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD
		)
		dc.SetFont( font )
		tWidth, tHeight = dc.GetTextExtent( text )
		border = int(tHeight / 3)
		
		bm = wx.BitmapFromImage( wx.EmptyImage(tWidth, tHeight) )
		memDC = wx.MemoryDC( bm )
		memDC.SetBackground( wx.BLACK_BRUSH )
		memDC.Clear()
		memDC.SetFont( font )
		memDC.SetTextForeground( wx.WHITE )
		memDC.DrawText( text, 0, 0 )
		bmMask = wx.BitmapFromImage( bm.ConvertToImage() )
		bm.SetMask( wx.Mask(bmMask, wx.BLACK) )
		dc.Blit( x+border, y - tHeight, tWidth, tHeight, memDC, 0, 0, useMask=True, rop=wx.XOR )
		dc.DrawLine( x, 0, x, winHeight )

	def drawZoomPhoto( self, x, y ):
		if not self.times or not self.photoWidth:
			return
			
		dc = wx.ClientDC( self )
		winWidth, winHeight = self.GetClientSize()
		
		photoWidth, photoHeight = self.photoWidth, self.photoHeight
		widthView, heightView = int(winHeight*0.95), int(winHeight*0.95)
		
		widthMagnified, heightMagnified = int(photoWidth * self.magnification), int(photoHeight * self.magnification)
		
		xTimeLine = self.getXTimeLine()
		
		leftToRightSign = (1,-1)[int(self.leftToRight)]
		xEdge = x + (photoWidth * leftToRightSign)//2
		t = self.tDrawStart + (xEdge - xTimeLine) / float(self.scaledPixelsPerSec) * leftToRightSign
		
		tbm = self.times[bisect_left(self.times, t, hi=len(self.times)-1)]
		
		penWidth = 2
		
		try:
			bm = self.zoomBitmap[tbm]
		except KeyError:
			image = wx.ImageFromStream( StringIO.StringIO(self.jpg[tbm]), wx.BITMAP_TYPE_JPEG )
			image.Rescale( int(photoWidth*self.magnification), int(photoHeight*self.magnification), wx.IMAGE_QUALITY_HIGH )
			bm = self.zoomBitmap[tbm] = image.ConvertToBitmap()
		
		mx, my = int(x * self.magnification), int(y * self.magnification / self.scale)
		
		if self.leftToRight:
			xViewPos, yViewPos = penWidth//2, penWidth//2
		else:
			xViewPos, yViewPos = winWidth - widthView - penWidth//2, penWidth//2
		
		memDC = wx.MemoryDC( bm )
		dc.Blit( xViewPos, yViewPos, widthView, heightView, memDC,
			max( 0, min(mx - widthView//2, widthMagnified - widthView) ),
			max( 0, min(my - heightView//2, heightMagnified - heightView) ),
		)
		memDC.SelectObject( wx.NullBitmap )
		
		dc.SetBrush( wx.TRANSPARENT_BRUSH )
		dc.SetPen( wx.Pen(wx.Colour(255,255,0), penWidth) )
		dc.DrawRectangle( xViewPos, yViewPos, widthView, heightView )
		
	def OnEnterWindow( self, event ):
		pass
		
	def OnMotion( self, event ):		
		x, y, dragging = event.GetX(), event.GetY(), event.Dragging()
		
		winWidth, winHeight = self.GetClientSize()
		self.drawXorLine( self.xMotionLast, self.yMotionLast )
		self.xMotionLast = x
		self.yMotionLast = y
		self.drawXorLine( self.xMotionLast, self.yMotionLast )
		
		if dragging and hasattr(self, 'xDragLast'):
			dx = -(x - self.xDragLast)
			self.tDrawStart += float(dx) / float(self.scaledPixelsPerSec)
			self.xDragLast = x
			wx.CallAfter( self.Refresh )
		else:
			self.drawZoomPhoto( x, y )
		
	def OnLeaveWindow( self, event=None ):
		self.drawXorLine( self.xMotionLast, self.yMotionLast )
		wx.CallAfter( self.Refresh )
		self.xMotionLast = None
		
	def draw( self, dc ):
		dc.SetBackground( wx.Brush(wx.Colour(128,128,150)) )
		dc.Clear()
		
		self.xMotionLast = None
		if not self.compositeBitmap:
			return
		
		winWidth, winHeight = self.GetClientSize()
		
		xTimeLine = self.getXTimeLine()
		
		compositeDC = wx.MemoryDC( self.compositeBitmap )
		xStart = int(self.tDrawStart * self.scaledPixelsPerSec)
		dc.Blit(
			0, 0, winWidth, self.photoHeight,
			compositeDC,
			xStart, 0,
		)
		compositeDC.SelectObject( wx.NullBitmap )
		
		# Draw the current time at the timeline.
		gc = wx.GraphicsContext.Create( dc )
		
		gc.SetPen( wx.Pen(contrastColour, 1) )
		gc.StrokeLine( xTimeLine, 0, xTimeLine, winHeight )
		
		text = self.formatTime( self.tDrawStart )
		fontHeight = max(5, winHeight//20)
		font = wx.FontFromPixelSize(
			wx.Size(0,fontHeight),
			wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL
		)
		gc.SetFont( font, wx.BLACK )
		tWidth, tHeight = gc.GetTextExtent( text )
		border = int(tHeight / 3)
		
		gc.SetPen( wx.Pen(wx.Colour(64,64,64), 1) )
		gc.SetBrush( wx.Brush(wx.Colour(200,200,200)) )
		rect = wx.Rect( xTimeLine - tWidth//2 - border, 0, tWidth + border*2, tHeight + border*2 )
		gc.DrawRoundedRectangle( rect.GetLeft(), rect.GetTop(), rect.GetWidth(), rect.GetHeight(), border*1.5 )
		rect.SetTop( winHeight - tHeight - border )
		gc.DrawRoundedRectangle( rect.GetLeft(), rect.GetTop(), rect.GetWidth(), rect.GetHeight(), border*1.5 )
		
		gc.DrawText( text, xTimeLine - tWidth//2, border )
		gc.DrawText( text, xTimeLine - tWidth//2, winHeight - tHeight - border/2 )
	
	def OnPaint( self, event=None ):
		self.draw( wx.PaintDC(self) )
		
	def GetBitmap( self ):
		return self.compositeBitmap if self.compositeBitmap else None

class FinishStripPanel( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize, style=0, fps=25.0 ):
		super(FinishStripPanel, self).__init__( parent, id, size=size, style=style )
		
		self.fps = fps
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		displayWidth, displayHeight = wx.GetDisplaySize()
	
		self.leftToRight = True
		self.finish = FinishStrip( self, size=(0, 480), leftToRight=self.leftToRight, mouseWheelCallback=self.onMouseWheel )
		self.finish.tDrawStartCallback = self.tDrawStartCallback
		
		self.timeSlider = wx.Slider( self, style=wx.SL_HORIZONTAL, minValue=0, maxValue=displayWidth )
		self.timeSlider.SetPageSize( 1 )
		self.timeSlider.Bind( wx.EVT_SCROLL, self.onChangeTime )
		
		minPixelsPerSecond, maxPixelsPerSecond = self.getSpeedPixelsPerSecondMinMax()
		self.stretchSlider = wx.Slider( self, style=wx.SL_HORIZONTAL, minValue=minPixelsPerSecond, maxValue=maxPixelsPerSecond )
		self.stretchSlider.SetPageSize( 1 )
		self.stretchSlider.Bind( wx.EVT_SCROLL, self.onChangeSpeed )
		
		self.zoomSlider = wx.Slider( self, style=wx.SL_HORIZONTAL|wx.SL_INVERSE, minValue=20, maxValue=100 )
		self.zoomSlider.Bind( wx.EVT_SCROLL_CHANGED, self.onChangeScale )
		self.zoomSlider.SetValue( 100 )
		
		self.direction = wx.RadioBox( self,
			label=_('Finish Direction'),
			choices=[_('Right to Left'), _('Left to Right')],
			majorDimension=1,
			style=wx.RA_SPECIFY_ROWS
		)
		self.direction.SetSelection( 1 if self.leftToRight else 0 )
		self.direction.Bind( wx.EVT_RADIOBOX, self.onDirection )

		self.copyToClipboard = wx.Button( self, label=_('Copy to Clipboard') )
		self.copyToClipboard.Bind( wx.EVT_BUTTON, self.onCopyToClipboard )
		
		self.save = wx.Button( self, label=u'{}...'.format(_('Save')) )
		self.save.Bind( wx.EVT_BUTTON, self.onSave )
		
		fgs = wx.FlexGridSizer( cols=2, vgap=0, hgap=0 )
		
		fgs.Add( wx.StaticText(self, label=u'{}'.format(_('Click and Drag for Time'))), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.timeSlider, flag=wx.EXPAND )
		
		fgs.Add( wx.StaticText(self, label=u'{}'.format(_('Mousewheel to Stretch'))), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.stretchSlider, flag=wx.EXPAND )
		
		fgs.Add( wx.StaticText(self, label=u'{}:'.format(_('Ctrl+Mousewheel to Zoom'))), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.zoomSlider, flag=wx.EXPAND )
		
		fgs.AddGrowableCol( 1, 1 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.direction )
		hs.AddSpacer( 16 )
		hs.Add( self.copyToClipboard, flag=wx.ALIGN_CENTRE_VERTICAL )
		hs.AddSpacer( 4 )
		hs.Add( self.save, flag=wx.ALIGN_CENTRE_VERTICAL )
		
		vs.Add( self.finish, 1, flag=wx.EXPAND )
		vs.Add( fgs, flag=wx.EXPAND|wx.ALL, border=4 )
		vs.Add( hs, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.SetSizer( vs )
		wx.CallAfter( self.initUI )
		
	def initUI( self ):
		self.finish.SetPixelsPerSec( self.stretchSlider.GetMin() )
		
	def getSpeedPixelsPerSecondMinMax( self ):
		frameTime = 1.0 / self.fps
		
		viewWidth = 4.0			# meters seen in the finish line with the finish camera
		widthPix = photoWidth	# width of the photo
		
		minMax = []
		for speedKMH in (0.0, 80.0):			# Speed of the target (km/h)
			speedMPS = speedKMH / 3.6			# Convert to m/s
			d = speedMPS * frameTime			# Distance the target moves between each frame at speed.
			pixels = widthPix * d / viewWidth	# Pixels the target moves between each frame at that speed.
			pixelsPerSecond = max(300, pixels * self.fps)
			minMax.append( int(pixelsPerSecond) )
		
		return minMax

	def onCopyToClipboard( self, event ):
		bm = self.finish.GetBitmap()
		if not bm:
			wx.MessageBox( _('Nothing to Copy'), _('Nothing to Copy') )
			return
			
		if wx.TheClipboard.Open():
			bitmapData = wx.BitmapDataObject()
			bitmapData.SetBitmap( bm )
			wx.TheClipboard.SetData( bitmapData )
			wx.TheClipboard.Flush() 
			wx.TheClipboard.Close()
			wx.MessageBox( _('Successfully copied to clipboard'), _('Success') )
		else:
			wx.MessageBox( _('Unable to open the clipboard'), _('Error') )

	def onSave( self, event ):
		dlg = wx.FileDialog(
			self,
			message=_('Save Finish as'),
			wildcard=u"PNG {} (*.png)|*.png".format(_("files")),
			defaultDir=os.path.dirname( Utils.getFileName() or '.' ),
			defaultFile=os.path.splitext( os.path.basename(Utils.getFileName() or _('Default.cmn')) )[0] + u'_Finish.png',
			style=wx.SAVE,
		)
		if dlg.ShowModal() == wx.ID_OK:
			fname = dlg.GetPath()
			bm = self.finish.GetBitmap()
			image = wx.ImageFromBitmap( bm )
			image.SaveFile( fname, wx.BITMAP_TYPE_PNG )
		dlg.Destroy()

	def onDirection( self, event ):
		self.SetLeftToRight( event.GetInt() == 1 ) 
		event.Skip()
		
	def onChangeSpeed( self, event=None ):
		self.SetPixelsPerSec( self.stretchSlider.GetValue(), False )
		if event:
			event.Skip()
	
	def onChangeScale( self, event ):
		scale = float(event.GetPosition()) / 100.0
		self.finish.SetScale( scale )
		event.Skip()
	
	def onMouseWheel( self, event ):
		if event.ControlDown() or event.ShiftDown():
			return
		speedFactor = 0.90
		if event.GetWheelRotation() > 0:
			v = self.stretchSlider.GetValue() / speedFactor
		else:
			v = self.stretchSlider.GetValue() * speedFactor
		self.stretchSlider.SetValue( max(self.stretchSlider.GetMin(), min(self.stretchSlider.GetMax(), v) ) )
		wx.CallAfter( self.onChangeSpeed )
	
	def getPhotoTimeMinMax( self ):
		tMin, tMax = self.finish.GetTimeMinMax()
		# Widen the range so we can see a few seconds before and after.
		if tMin is not None:
			tMin -= 0.1
			tMax += 0.1
		return tMin, tMax
		
	def onChangeTime( self, event ):
		r = float(event.GetPosition()) / float(event.GetEventObject().GetMax())
		tMin, tMax = self.getPhotoTimeMinMax()
		if tMin is not None:
			self.finish.SetDrawStartTime( tMin + (tMax - tMin) * r )
		event.Skip()
				
	def tDrawStartCallback( self, tDrawStart ):
		tMin, tMax = self.getPhotoTimeMinMax()
		if tMin is not None:
			vMin, vMax = self.timeSlider.GetMin(), self.timeSlider.GetMax()
			self.timeSlider.SetValue( int((tDrawStart - tMin) * float(vMax - vMin) / float(tMax - tMin)) )
			
	def SetLeftToRight( self, leftToRight ):
		self.leftToRight = leftToRight
		self.finish.SetLeftToRight( self.leftToRight )
		self.direction.SetSelection( 1 if self.leftToRight else 0 )
		
	def GetLeftToRight( self ):
		return self.leftToRight
		
	def SetPixelsPerSec( self, pixelsPerSec, setSliderValue=True ):
		self.finish.SetPixelsPerSec( pixelsPerSec )
		if setSliderValue:
			self.stretchSlider.SetValue( pixelsPerSec )
	
	def GetPixelsPerSec( self ):
		return self.stretchSlider.GetValue()
		
	def SetT( self, t ):
		tMin, tMax = self.getPhotoTimeMinMax()
		if tMin is None or tMax is None:
			return
		t = min(max(t, tMin), tMax)
		vMin, vMax = self.timeSlider.GetMin(), self.timeSlider.GetMax()
		self.timeSlider.SetValue( int((t - tMin) * float(vMax - vMin) / float(tMax - tMin)) )
		self.finish.SetDrawStartTime( t )
		
	def SetTsJpgs( self, tsJpgs, ts ):
		self.finish.SetTsJpgs( tsJpgs )
		if ts and self.finish.tsFirst:
			self.SetT( (ts-self.finish.tsFirst).total_seconds() )

class FinishStripDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX,
			dir=None, fps=25.0, leftToRight=True, pixelsPerSec=None ):
			
		if size == wx.DefaultSize:
			displayWidth, displayHeight = wx.GetDisplaySize()
			width = int(displayWidth * 0.9)
			height = 780
			size = wx.Size( width, height )

		super(FinishStripDialog, self).__init__( parent, id, size=size, style=style, title=_('Finish Strip') )
		
		self.panel = FinishStripPanel( self, fps=fps )
		
		self.okButton = wx.Button( self, wx.ID_OK )
		self.okButton.SetDefault()
		
		vs = wx.BoxSizer( wx.VERTICAL )
		vs.Add( self.panel, flag=wx.EXPAND )
		vs.Add( self.okButton, flag=wx.ALIGN_CENTRE|wx.ALL, border=4 )
		self.SetSizer( vs )
		
		self.panel.SetLeftToRight( leftToRight )
		if pixelsPerSec is not None:
			self.panel.SetPixelsPerSec( pixelsPerSec )
	
	def SetT( self, t ):
		self.panel.SetT( t )

	def GetAttrs( self ):
		return {
			'fps': self.panel.fps,
			'leftToRight': self.panel.GetLeftToRight(),
			'pixelsPerSec': self.panel.GetPixelsPerSec(),
		}

if __name__ == '__main__':
	app = wx.App(False)
	
	displayWidth, displayHeight = wx.GetDisplaySize()
	
	width = int(displayWidth * 0.9)
	height = 780
	
	mainWin = wx.Frame(None,title="FinishStrip", size=(width, height))
	fs = FinishStripPanel( mainWin )
	mainWin.Show()
	
	#fsd = FinishStripDialog( mainWin )
	#fsd.ShowModal()
	
	app.MainLoop()
