import wx
import os
import sys
import glob
import math
import datetime
import cStringIO as StringIO
from bisect import bisect_left
from MakeComposite import MakeComposite
from AddPhotoHeader import AddPhotoHeader
import Utils

def _( s ):
	return s
	
def PilImageToWxImage(pil, alpha=False):
	"""Convert PIL Image to wx.Image."""
	image = wx.Image( *pil.size )
	image.SetData( pil.convert("RGB").tobytes() )

	if alpha and pilImage.mode[-1] == 'A':
		image.SetAlphaData(pil.convert("RGBA").tobytes()[3::4])

	return image

contrastColour = wx.Colour( 255, 130, 0 )

class FinishStrip( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize, style=0,
			fps=25,
			leftToRight=False, mouseWheelCallback=None, scrollCallback=None ):
		super(FinishStrip, self).__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		
		self.SetMinSize( (wx.GetDisplaySize()[0]//4, wx.GetDisplaySize()[1]//4) )
		
		self.fps = float(fps)
		self.scale = 1.0
		self.magnification = 0.25
		self.mouseWheelCallback = mouseWheelCallback or (lambda event: None)
		self.scrollCallback = scrollCallback or (lambda position: None)
		
		self.imageQuality = wx.IMAGE_QUALITY_NORMAL
		
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
		self.xTime = None
		self.tsFirst = datetime.datetime.now()
		self.tsJpgs = []
		self.photoWidth, self.photoHeight = None, None
		self.jpgWidth, self.jpgHeight = 600, 480

		self.times = []
		self.jpg = {}
		self.zoomBitmap = {}
		
		self.leftToRight = leftToRight
		self.pixelsPerSec = 25
		
		self.bitmapLeft = 0
		self.tCursor = 0.0
		self.tMax = 0.0
		
	def formatTime( self, t ):
		return (self.tsFirst + datetime.timedelta(seconds=t)).strftime('%H:%M:%S.%f')[:-3]
		
	def SetImageQuality( self, iq ):
		self.imageQuality = iq
		self.zoomBitmap = {}
		self.prefetchZoomBitmap()
	
	def SetLeftToRight( self, leftToRight=True ):
		self.leftToRight = leftToRight
		self.refreshCompositeBitmap()
		wx.CallAfter( self.Refresh )
		
	def SetPixelsPerSec( self, pixelsPerSec ):
		self.pixelsPerSec = pixelsPerSec
		self.refreshCompositeBitmap()
		wx.CallAfter( self.Refresh )

	def prefetchZoomBitmap( self ):
		if not self.times:
			return
		
		iStart = bisect_left(self.times, self.tCursor, hi=len(self.times)-1)
		for i in xrange(iStart, -1, -1):
			tbm = self.times[i]
			if tbm not in self.zoomBitmap:
				self.getZoomBitmap( tbm )
				if self.tCursor - tbm < 0.25:
					wx.CallLater( 150, self.prefetchZoomBitmap )
				break
		
	def SetBitmapLeft( self, position ):
		self.bitmapLeft = position
		self.Refresh()
	
	def SetCursorTime( self, tCursor ):
		self.tCursor = tCursor
		wx.CallAfter( self.prefetchZoomBitmap )
		wx.CallAfter( self.Refresh )
		
	def GetTimeMinMax( self ):
		return (self.times[0], self.times[-1]) if self.times else (None, None)
		
	def GetTimePhotos( self ):
		return self.times
		
	def SetTsJpgs( self, tsJpgs ):
		self.zoomBitmap = {}
		self.tsJpgs = (tsJpgs or [])
		self.times = []
		self.jpg = {}
		self.scale = 1.0
		
		if not tsJpgs:
			self.tsFirst = datetime.datetime.now()
			self.compositeBitmap = None
			self.Refresh()
			return
		
		self.tsFirst = tsJpgs[0][0]
		for ts, jpg in tsJpgs:
			t = (ts-self.tsFirst).total_seconds()
			self.times.append( t )
			self.jpg[t] = jpg
		
		self.tMax = self.times[-1]
		
		image = wx.Image( StringIO.StringIO(tsJpgs[0][1]), wx.BITMAP_TYPE_JPEG )
		self.jpgWidth, self.jpgHeight = image.GetSize()
		self.scale = min( 1.0, float(self.GetSize()[1]) / float(self.jpgHeight) )
		if self.scale != 1.0:
			image.Rescale( int(image.GetWidth()*self.scale), int(image.GetHeight()*self.scale), self.imageQuality )

		self.refreshCompositeBitmap()
	
	def refreshCompositeBitmap( self ):
		wait = wx.BusyCursor()
		ts = datetime.datetime.now()
		self.photoWidth, self.photoHeight, self.compositeBitmap = MakeComposite(
			self.tsJpgs, self.leftToRight, self.pixelsPerSec, self.scale
		)
		print 'composite time:', (datetime.datetime.now() - ts).total_seconds()
		self.zoomBitmap = {}
		
	def OnErase( self, event ):
		pass
	
	def tFromX( self, x ):
		x += self.bitmapLeft
		t = x / (self.scale * self.pixelsPerSec)
		if self.leftToRight:
			t = self.tMax - t
		return t
		
	def xFromT( self, t ):
		if self.leftToRight:
			t = self.tMax - t
		return int(t * self.scale * self.pixelsPerSec) - self.bitmapLeft
		
	def SetT( self, t ):
		if not self.times:
			return
		self.tCursor = t
		x = self.xFromT( t )
		self.bitmapLeft = max(0, min(x, self.compositeBitmap.GetSize()[0] - self.GetClientSize()[0]))
		self.Refresh()
		self.scrollCallback( self.bitmapLeft )
	
	def drawXorLine( self, x, y ):
		if x is None or not self.times:
			return
		
		dc = wx.ClientDC( self )
		dc.SetLogicalFunction( wx.XOR )
		
		dc.SetPen( wx.WHITE_PEN )
		winWidth, winHeight = self.GetClientSize()
		
		text = self.formatTime( self.tFromX(x) )
		fontHeight = max(5, winHeight//20)
		font = wx.Font( (0,fontHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD )
		dc.SetFont( font )
		tWidth, tHeight = dc.GetTextExtent( text )
		border = int(tHeight / 3)
		
		bm = wx.Bitmap( tWidth, tHeight )
		memDC = wx.MemoryDC( bm )
		memDC.SetBackground( wx.BLACK_BRUSH )
		memDC.Clear()
		memDC.SetFont( font )
		memDC.SetTextForeground( wx.WHITE )
		memDC.DrawText( text, 0, 0 )
		bmMask = wx.Bitmap( bm.ConvertToImage() )
		bm.SetMask( wx.Mask(bmMask, wx.BLACK) )
		dc.Blit( x+border, y - tHeight, tWidth, tHeight, memDC, 0, 0, useMask=True, logicalFunc=wx.XOR )
		dc.DrawLine( x, 0, x, winHeight )

	def getZoomBitmap( self, tbm ):
		try:
			return self.zoomBitmap[tbm]
		except KeyError:
			image = wx.Image( StringIO.StringIO(self.jpg[tbm]), wx.BITMAP_TYPE_JPEG )
			image.Rescale( int(self.jpgWidth*self.magnification), int(self.jpgHeight*self.magnification), self.imageQuality )
			self.zoomBitmap[tbm] = image.ConvertToBitmap()
			return self.zoomBitmap[tbm]
	
	def getJpg( self, x ):
		if not self.times:
			return None
		return self.tsJpgs[bisect_left(self.times, self.tFromX(x), hi=len(self.times)-1)][1]
	
	def drawZoomPhoto( self, x, y ):
		if not self.times or not self.jpgWidth:
			return
			
		dc = wx.ClientDC( self )
		winWidth, winHeight = self.GetClientSize()
		
		jpgWidth, jpgHeight = self.jpgWidth, self.jpgHeight
		viewHeight = winHeight
		viewWidth = min(winWidth//2, int(viewHeight * float(jpgWidth)/float(jpgHeight)))
		
		tbm = self.times[bisect_left(self.times, self.tFromX(x), hi=len(self.times)-1)]
		bm = self.getZoomBitmap( tbm )
		bmWidth, bmHeight = bm.GetSize()
		
		viewWidth = min( viewWidth, bmWidth )
		viewHeight = min( viewHeight, bmHeight )
		
		penWidth = 2
		penWidthDiv2 = penWidth//2
		
		if not self.leftToRight:
			xViewPos, yViewPos = penWidthDiv2, penWidthDiv2
		else:
			xViewPos, yViewPos = winWidth - viewWidth + penWidthDiv2, penWidthDiv2
			
		if xViewPos <= x < xViewPos + viewWidth:
			if self.leftToRight:
				xViewPos, yViewPos = penWidthDiv2, penWidthDiv2
			else:
				xViewPos, yViewPos = winWidth - viewWidth + penWidthDiv2, penWidthDiv2
			
		ratioY = float(y) / float(winHeight)
		centerY = ratioY * bmHeight
		bmY = int(centerY - viewHeight//2)
		bmY = max( 0, min(bmY, bmHeight-viewHeight) )
		
		bmX = max( 0, (bmWidth - viewWidth) // 2 )
		
		if (xViewPos,viewWidth) != getattr(self,'zoomViewLast', (None,None)):
			self.zoomViewLast = (xViewPos,viewWidth)
			self.Refresh()
			wx.CallLater( 10, self.drawZoomPhoto, x, y )
			return
		
		memDC = wx.MemoryDC( bm )
		dc.Blit( xViewPos, yViewPos, viewWidth, viewHeight, memDC, bmX, bmY )
		memDC.SelectObject( wx.NullBitmap )
		
		dc.SetBrush( wx.TRANSPARENT_BRUSH )
		dc.SetPen( wx.Pen(wx.Colour(255,255,51), penWidth) )
		dc.DrawRectangle( xViewPos, yViewPos, viewWidth, viewHeight-penWidthDiv2 )
		
	def OnEnterWindow( self, event ):
		pass
		
	def OnSize( self, event ):
		if self.jpgHeight is not None:
			self.scale = min( 1.0, float(event.GetSize()[1]) / float(self.jpgHeight) )
			self.refreshCompositeBitmap()
		wx.CallAfter( self.Refresh )
		self.scrollCallback()
		event.Skip()
		
	def OnLeftDown( self, event ):
		self.xDragLast = event.GetX()
		self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
		event.Skip()
		
	def OnLeftUp( self, event ):
		self.tCursor = self.tFromX( event.GetX() )
		wx.CallAfter( self.prefetchZoomBitmap )
		wx.CallAfter( self.OnLeaveWindow )
		wx.CallAfter( self.Refresh )
		self.SetCursor( wx.NullCursor )
		event.Skip()
		
	def OnMouseWheel( self, event ):
		if event.ControlDown() and not event.ShiftDown():
			magnificationSave = self.magnification
			magFactor = 0.90
			if event.GetWheelRotation() < 0:
				self.magnification /= magFactor
			else:
				self.magnification *= magFactor
			
			self.magnification = min( 5.0, max(0.10, self.magnification) )
			if self.magnification != magnificationSave:
				self.zoomBitmap.clear()
				wx.CallAfter( self.drawZoomPhoto, event.GetX(), event.GetY() )
		else:
			self.mouseWheelCallback( event )
	
	def OnMotion( self, event ):		
		x, y, dragging = event.GetX(), event.GetY(), event.Dragging()
		
		winWidth, winHeight = self.GetClientSize()
		self.drawXorLine( self.xMotionLast, self.yMotionLast )
		self.xMotionLast = x
		self.yMotionLast = y
		self.drawXorLine( self.xMotionLast, self.yMotionLast )
		
		if dragging and hasattr(self, 'xDragLast'):
			dx = -(x - self.xDragLast)
			self.xDragLast = x
			self.tCursor = self.tFromX( x )
			bitmapLeft = max(0, min(self.compositeBitmap.GetSize()[0]-winWidth, self.bitmapLeft+dx)) 
			if bitmapLeft != self.bitmapLeft:
				self.bitmapLeft = bitmapLeft					
				wx.CallAfter( self.scrollCallback, self.bitmapLeft )
				wx.CallAfter( self.Refresh )
		else:
			self.drawZoomPhoto( x, y )
		
	def OnLeaveWindow( self, event=None ):
		self.drawXorLine( self.xMotionLast, self.yMotionLast )
		wx.CallAfter( self.Refresh )
		self.xMotionLast = None
		
	def draw( self, dc ):
		dc.SetBackground( wx.Brush(wx.BLACK, wx.SOLID) )
		dc.Clear()
	
		self.xMotionLast = None
		if not self.compositeBitmap:
			return
		
		winWidth, winHeight = self.GetClientSize()
		
		compositeDC = wx.MemoryDC( self.compositeBitmap )
		dc.Blit(
			0, 0, winWidth, self.photoHeight,
			compositeDC,
			self.bitmapLeft, 0,
		)
		compositeDC.SelectObject( wx.NullBitmap )
		
		xCursor = self.xFromT( self.tCursor )
		
		# Draw the current time at the timeline.
		gc = wx.GraphicsContext.Create( dc )
		
		gc.SetPen( wx.Pen(contrastColour, 1) )
		gc.StrokeLine( xCursor, 0, xCursor, winHeight )
		
		text = self.formatTime( self.tCursor )
		fontHeight = max(5, winHeight//20)
		font = wx.Font( (0,fontHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		gc.SetFont( font, wx.BLACK )
		tWidth, tHeight = gc.GetTextExtent( text )
		border = int(tHeight / 3)
		
		gc.SetPen( wx.Pen(wx.Colour(64,64,64), 1) )
		gc.SetBrush( wx.Brush(wx.Colour(200,200,200)) )
		rect = wx.Rect( xCursor - tWidth//2 - border, 0, tWidth + border*2, tHeight + border*2 )
		gc.DrawRoundedRectangle( rect.GetLeft(), rect.GetTop(), rect.GetWidth(), rect.GetHeight(), border*1.5 )
		rect.SetTop( winHeight - tHeight - border*2 )
		gc.DrawRoundedRectangle( rect.GetLeft(), rect.GetTop(), rect.GetWidth(), rect.GetHeight(), border*1.5 )
		
		gc.DrawText( text, xCursor - tWidth//2, border )
		gc.DrawText( text, xCursor - tWidth//2, winHeight - tHeight - border )
	
	def OnPaint( self, event=None ):
		self.draw( wx.PaintDC(self) )
		
	def GetBitmap( self ):
		return self.compositeBitmap if self.compositeBitmap else None

class FinishStripPanel( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize, style=0, fps=25.0 ):
		super(FinishStripPanel, self).__init__( parent, id, size=size, style=style )
		
		self.fps = fps
		self.info = {}
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		displayWidth, displayHeight = wx.GetDisplaySize()
	
		self.leftToRight = True
		self.imageQuality = wx.IMAGE_QUALITY_NORMAL
		self.finish = FinishStrip(
			self, leftToRight=self.leftToRight,
			mouseWheelCallback=self.onMouseWheel, scrollCallback=self.scrollCallback
		)
		
		self.timeScrollbar = wx.ScrollBar( self, style=wx.SB_HORIZONTAL )
		self.timeScrollbar.Bind( wx.EVT_SCROLL, self.onChangeTime )
		
		minPixelsPerSecond, maxPixelsPerSecond = self.getSpeedPixelsPerSecondMinMax()
		self.stretchSlider = wx.Slider( self, style=wx.SL_HORIZONTAL, minValue=minPixelsPerSecond, maxValue=maxPixelsPerSecond )
		self.stretchSlider.SetPageSize( 1 )
		self.stretchSlider.Bind( wx.EVT_SCROLL, self.onChangeSpeed )
		
		self.direction = wx.RadioBox( self,
			label=_('Finish Direction'),
			choices=[_('Right to Left'), _('Left to Right')],
			majorDimension=1,
			style=wx.RA_SPECIFY_ROWS
		)
		self.direction.SetSelection( 1 if self.leftToRight else 0 )
		self.direction.Bind( wx.EVT_RADIOBOX, self.onDirection )

		self.imageQualitySelect = wx.RadioBox( self,
			label=_('Zoom Image Quality'),
			choices=[_('Normal (faster)'), _('High (slower)')],
			majorDimension=1,
			style=wx.RA_SPECIFY_ROWS
		)
		self.imageQualitySelect.SetSelection( 1 if self.imageQuality == wx.IMAGE_QUALITY_HIGH else 0 )
		self.imageQualitySelect.Bind( wx.EVT_RADIOBOX, self.onImageQuality )

		self.copyToClipboard = wx.BitmapButton(self, bitmap=Utils.getBitmap('copy-to-clipboard.png'))
		self.copyToClipboard.SetToolTip( wx.ToolTip('Copy Finish Strip to Clipboard') )
		self.copyToClipboard.Bind( wx.EVT_BUTTON, self.onCopyToClipboard )
		
		fgs = wx.FlexGridSizer( cols=2, vgap=0, hgap=0 )
		fgs.Add( wx.StaticText(self, label=u'{}'.format(_('Stretch'))), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		fgs.Add( self.stretchSlider, flag=wx.EXPAND )
		
		fgs.AddGrowableCol( 1, 1 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.direction )
		hs.Add( self.imageQualitySelect, flag=wx.LEFT, border=16 )
		hs.Add( self.copyToClipboard, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )
		hs.Add( wx.StaticText(self, label=u'\n'.join([
					'To Pan: Click and Drag',
					'To Stretch: Mousewheel',
				])
			),
			flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16
		)
		hs.Add( wx.StaticText(self, label=u'\n'.join([
					'To Zoom: Ctrl+Mousewheel',
					'Show Photo: Right-click',
				])
			),
			flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16
		)
		vs.Add( self.finish, 1, flag=wx.EXPAND )
		vs.Add( self.timeScrollbar, flag=wx.EXPAND )
		vs.Add( fgs, flag=wx.EXPAND|wx.ALL, border=0 )
		vs.Add( hs, flag=wx.EXPAND|wx.ALL, border=0 )
		
		self.SetSizer( vs )
		wx.CallAfter( self.initUI )
		
	def initUI( self ):
		v = self.stretchSlider.GetMin()  + (self.stretchSlider.GetMax()-self.stretchSlider.GetMin()) // 3
		self.stretchSlider.SetValue( v )
		self.finish.SetPixelsPerSec( v )
		
	def getSpeedPixelsPerSecond( self, speedKMH ):
		frameTime = 1.0 / self.fps
		
		viewWidth = 4.0						# estimated meters seen in the finish line with the finish camera
		widthPix = self.finish.jpgWidth		# width of a frame
		
		speedMPS = speedKMH / 3.6			# Convert to m/s
		d = speedMPS * frameTime			# Distance the target moves between each frame at speed.
		pixels = widthPix * d / viewWidth	# Pixels the target moves between each frame at that speed.
		pixelsPerSecond = max(300, pixels * self.fps)
		return pixelsPerSecond
		
	def getSpeedPixelsPerSecondMinMax( self ):
		return [self.getSpeedPixelsPerSecond(speedKMH) for speedKMH in (0.0, 80.0)]

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

	def onDirection( self, event ):
		self.SetLeftToRight( event.GetInt() == 1 ) 
		event.Skip()
		
	def onImageQuality( self, event ):
		self.SetImageQuality( wx.IMAGE_QUALITY_HIGH if event.GetInt() == 1 else wx.IMAGE_QUALITY_NORMAL ) 
		event.Skip()
		
	def onChangeSpeed( self, event=None ):
		self.SetPixelsPerSec( self.stretchSlider.GetValue(), False )
		self.scrollCallback()
		if event:
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
		return self.finish.GetTimeMinMax()
	
	def scrollCallback( self, position=None ):
		if position is None:
			position = self.timeScrollbar.GetThumbPosition()
		
		bitmap = self.finish.GetBitmap()
		bmWidth =  bitmap.GetSize()[0] if bitmap else self.finish.GetClientSize()[0]
		
		range = bmWidth
		thumbSize = min( self.finish.GetClientSize()[0], range )
		pageSize = int(thumbSize * 0.95)
		position = max(0, min(position, range-thumbSize))
		self.timeScrollbar.SetScrollbar( position, thumbSize, range, pageSize, True )
			
	def onChangeTime( self, event ):
		self.finish.SetBitmapLeft( event.GetPosition() )
		event.Skip()
				
	def SetLeftToRight( self, leftToRight ):
		self.leftToRight = leftToRight
		self.finish.SetLeftToRight( self.leftToRight )
		self.direction.SetSelection( 1 if self.leftToRight else 0 )
		
	def SetImageQuality( self, iq ):
		self.imageQuality = iq
		self.finish.SetImageQuality( self.imageQuality )
		self.imageQualitySelect.SetSelection( 1 if self.imageQuality == wx.IMAGE_QUALITY_HIGH else 0 )
		
	def GetLeftToRight( self ):
		return self.leftToRight
		
	def SetPixelsPerSec( self, pixelsPerSec, setSliderValue=True ):
		self.finish.SetPixelsPerSec( pixelsPerSec )
		if setSliderValue:
			self.stretchSlider.SetValue( pixelsPerSec )
	
	def GetPixelsPerSec( self ):
		return self.stretchSlider.GetValue()
		
	def SetTsJpgs( self, tsJpgs, ts, info={} ):
		self.info = info
		self.finish.SetTsJpgs( tsJpgs )
		if ts and self.finish.tsFirst:
			self.finish.SetT( (ts-self.finish.tsFirst).total_seconds() )
		
		self.stretchSlider.SetRange( *self.getSpeedPixelsPerSecondMinMax() )
		self.scrollCallback()
		
	def GetTsJpgs( self ):
		return self.finish.tsJpgs
			
	def Clear( self ):
		self.info = {}
		self.finish.SetTsJpgs( [] )

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
	from Database import Database
	app = wx.App(False)
	
	displayWidth, displayHeight = wx.GetDisplaySize()
	
	width = int(displayWidth * 0.8)
	height = int(displayHeight * 0.8)
	
	mainWin = wx.Frame(None,title="FinishStrip", size=(width, height))
	fs = FinishStripPanel( mainWin )
	mainWin.Show()
	
	tsJpgs = Database().getLastPhotos( 90 )
	fs.SetTsJpgs( tsJpgs, tsJpgs[len(tsJpgs)//2][0], info={} )
	
	#fsd = FinishStripDialog( mainWin )
	#fsd.ShowModal()
	
	app.MainLoop()
