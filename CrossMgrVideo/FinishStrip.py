import wx
import os
import io
import sys
import glob
import math
from time import sleep
import datetime
import platform
from bisect import bisect_left
from MakeComposite import MakeComposite
import Utils
import CVUtil

def _( s ):
	return s
	
def PilImageToWxImage(pil, alpha=False):
	"""Convert PIL Image to wx.Image."""
	image = wx.Image( pil.size[0], pil.size[1], pil.convert("RGB").tobytes() )

	if alpha and pil.mode[-1] == 'A':
		image.SetAlphaData(pil.convert("RGBA").tobytes()[3::4])

	return image

def imageFromJpeg( jpeg ):
	return wx.Image( io.BytesIO(jpeg), wx.BITMAP_TYPE_JPEG )

contrastColour = wx.Colour( 255, 130, 0 )

class FinishStrip( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize, style=0,
			fps=25,
			leftToRight=False, mouseWheelCallback=None, scrollCallback=None ):
		super().__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		
		self.SetMinSize( (wx.GetDisplaySize()[0]//4, wx.GetDisplaySize()[1]//4) )
		
		self.fps = float(fps)
		self.scale = 1.0
		self.magnification = 0.25
		self.mouseWheelCallback = mouseWheelCallback or (lambda event: None)
		self.scrollCallback = scrollCallback or (lambda position: None)
		self.drawingIsSafe = False	# True when it is safe to save the current window's background.
		self.xZoom = None
		
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
		
		self.leftToRight = leftToRight
		self.pixelsPerSec = 25
		
		self.bitmapLeft = 0
		self.tCursor = 0.0
		self.tMax = 0.0
		
		self.resetBmSave()
		
	def formatTime( self, t ):
		return (self.tsFirst + datetime.timedelta(seconds=t)).strftime('%H:%M:%S.%f')[:-3]
		
	def SetLeftToRight( self, leftToRight=True ):
		self.leftToRight = leftToRight
		self.refreshCompositeBitmap()
		wx.CallAfter( self.Refresh )
		
	def SetPixelsPerSec( self, pixelsPerSec ):
		self.pixelsPerSec = pixelsPerSec
		self.refreshCompositeBitmap()
		wx.CallAfter( self.Refresh )

	def SetBitmapLeft( self, position ):
		self.bitmapLeft = position
		self.Refresh()
	
	def SetCursorTime( self, tCursor ):
		self.tCursor = tCursor
		wx.CallAfter( self.Refresh )
		
	def GetTimeMinMax( self ):
		return (self.times[0], self.times[-1]) if self.times else (None, None)
		
	def GetTimePhotos( self ):
		return self.times
		
	def Clear( self ):
		self.SetTsJpgs( [] )
		
	def SetTsJpgs( self, tsJpgs, triggerTime=None ):
		self.resetBmSave()
		self.compositeBitmap = None
		self.drawingIsSafe = False
		
		self.tsJpgs = (tsJpgs or [])
		self.times = []
		self.jpg = {}
		self.scale = 1.0
		
		if not tsJpgs:
			self.tsFirst = datetime.datetime.now()
			self.triggerTime = 0.0
			self.Refresh()
			return
		
		self.tsFirst = tsJpgs[0][0]
		self.triggerTime = (triggerTime - self.tsFirst).total_seconds() if triggerTime else None
		for ts, jpg in tsJpgs:
			t = (ts-self.tsFirst).total_seconds()
			self.times.append( t )
			self.jpg[t] = jpg
		
		self.tMax = self.times[-1]
		
		image = imageFromJpeg( tsJpgs[0][1] )
		self.jpgWidth, self.jpgHeight = image.GetSize()
		self.scale = min( 1.0, float(self.GetSize()[1]) / float(self.jpgHeight) )
		if self.scale != 1.0:
			image.Rescale( int(image.GetWidth()*self.scale), int(image.GetHeight()*self.scale), wx.IMAGE_QUALITY_NORMAL )

		self.refreshCompositeBitmap()
		
	def refreshCompositeBitmap( self ):
		self.drawingIsSafe = False		# Turn off the drawingIfSafe flag as we are changing the underlying bitmap.
		self.photoWidth, self.photoHeight, self.compositeBitmap = MakeComposite(
			self.tsJpgs, self.leftToRight, self.pixelsPerSec, self.scale
		)
		
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
		
	def SetT( self, t = None ):
		if not self.times:
			return
		if t is None:
			 t = self.triggerTime
		self.tCursor = t
		x = self.xFromT( t )
		if self.compositeBitmap:
			self.bitmapLeft = max(0, min(x, self.compositeBitmap.GetSize()[0] - self.GetClientSize()[0]))
		self.drawingIsSafe = False
		self.Refresh()
		self.scrollCallback( self.bitmapLeft )
	
	def restoreBm( self ):
		if self.drawingIsSafe and self.bmSaveLast is not None:
			memDC = wx.MemoryDC( self.bmSaveLast )
			dc = wx.ClientDC( self )
			dc.Blit( self.bmSaveX, 0, self.bmSaveLast.GetWidth(), self.bmSaveLast.GetHeight(), memDC, 0, 0 )			
		self.resetBmSave()
		
	def resetBmSave( self ):
		self.bmSaveLast = self.bmSaveX = None
	
	def drawCurrentLine( self, x, y ):
		if not self.drawingIsSafe or x is None:
			self.resetBmSave()
			return
		
		# Restore the underlying bitmap.
		self.restoreBm()
		
		dc = wx.ClientDC( self )
		dc.SetBrush(wx.TRANSPARENT_BRUSH)
		
		winWidth, winHeight = self.GetClientSize()

		# Get the text dimensions of the current time.
		fontHeight = max(5, winHeight//20)
		font = wx.Font( (0,fontHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( font )
		
		tX = self.tFromX(x)
		
		text = []		
		text.append( self.formatTime(tX) )
		if self.triggerTime:
			text.append( '{:+.3f} TRG'.format(tX - self.triggerTime) )
		if self.tCursor:
			text.append( '{:+.3f} CUR'.format(tX - self.tCursor) )
			
		tWidth = tHeight = 0
		for t in text:
			tWidthCur, tHeightCur = dc.GetTextExtent( t )
			tWidth, tHeight = max( tWidth, tWidthCur ), max( tHeight, tHeightCur )
		
		border = tHeight // 3

		# Save the area under the time cursor before we draw.
		bm = self.bmSaveLast = wx.Bitmap( min(winWidth, tWidth + border * 2), winHeight )		
		overRightEdge = x + bm.GetWidth() > winWidth
		self.bmSaveX = (x - bm.GetWidth() + border) if overRightEdge else x - border
		
		memDC = wx.MemoryDC( bm )
		memDC.Blit( 0, 0, bm.GetWidth(), bm.GetHeight(), dc, self.bmSaveX, 0 )
		
		# Draw the time and delta information.
		dc.SetTextForeground( wx.WHITE )
		xText = x - tWidth - border if overRightEdge else x + border
		yText = y
		for t in text:
			dc.DrawText( t, xText, yText )
			yText += int(fontHeight*1.15)
		
		dc.SetPen( wx.WHITE_PEN )
		dc.DrawLine( x, 0, x, winHeight )

	def getIJpg( self, x ):
		return bisect_left(self.times, self.tFromX(x), hi=len(self.times)-1) if self.times else None

	def getJpg( self, x ):
		return self.tsJpgs[self.getIJpg(x)][1] if self.times else None
	
	def drawZoomPhoto( self, x, y ):
		if not self.drawingIsSafe or not self.jpgWidth:
			self.xZoom = None
			return
		self.xZoom = x
			
		dc = wx.ClientDC( self )
		winWidth, winHeight = self.GetClientSize()
		
		jpgWidth, jpgHeight = self.jpgWidth, self.jpgHeight
		viewHeight = winHeight
		viewWidth = min(winWidth//2, int(viewHeight * float(jpgWidth)/float(jpgHeight)))
		
		tbm = self.times[bisect_left(self.times, self.tFromX(x), hi=len(self.times)-1)]
		bm = CVUtil.jpegToImage( self.jpg[tbm] ).ConvertToBitmap()
		bmWidth, bmHeight = bm.GetSize()
		bmWidth = int(bmWidth * self.magnification)
		bmHeight = int(bmHeight * self.magnification)
		
		viewWidth = min( viewWidth, bmWidth )
		viewHeight = min( viewHeight, bmHeight )
		
		penWidth = 2
		penWidthDiv2 = penWidth//2
		
		if not self.leftToRight:
			xViewPos, yViewPos = penWidthDiv2, penWidthDiv2
		else:
			xViewPos, yViewPos = winWidth - viewWidth + penWidthDiv2, penWidthDiv2

		'''
		if xViewPos <= x < xViewPos + viewWidth:
			if self.leftToRight:
				xViewPos, yViewPos = penWidthDiv2, penWidthDiv2
			else:
				xViewPos, yViewPos = winWidth - viewWidth + penWidthDiv2, penWidthDiv2
		'''
			
		ratioY = float(y) / float(winHeight)
		centerY = ratioY * bmHeight
		bmY = int(centerY - viewHeight//2)
		bmY = max( 0, min(bmY, bmHeight-viewHeight) )
		
		bmX = max( 0, (bmWidth - viewWidth) // 2 )
		
		if (xViewPos,viewWidth) != getattr(self,'zoomViewLast', (None,None)):
			self.zoomViewLast = (xViewPos,viewWidth)
			self.Refresh()
		
		memDC = wx.MemoryDC( bm )
		dc.StretchBlit( xViewPos, yViewPos, viewWidth, viewHeight, memDC,
			int(bmX/self.magnification), int(bmY/self.magnification),
			int(viewWidth/self.magnification), int(viewHeight/self.magnification)
		)
		memDC.SelectObject( wx.NullBitmap )		
		
		# Display the times of the zoom photo.
		fontHeight = max(5, viewHeight//20)
		font = wx.Font( (0,fontHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )

		text = []
		text.append( self.formatTime(tbm) )
		if self.triggerTime:
			text.append( '{:+.3f} TRG'.format(tbm - self.triggerTime) )
		
		outlineColour = wx.Colour(255,255,51)
		if text:
			dc.SetFont( font )
			tWidth = tHeight = 0
			for t in text:
				tWidthCur, tHeightCur = dc.GetTextExtent( t )
				tWidth, tHeight = max( tWidth, tWidthCur ), max( tHeight, tHeightCur )
			
			border = fontHeight // 3
			lineHeight = int( tHeight * 1.15 )
			xText = xViewPos + border if self.leftToRight else xViewPos + viewWidth - tWidth - border
			yText = yViewPos + border
						
			dc.SetPen( wx.TRANSPARENT_PEN )
			dc.SetBrush( wx.BLACK_BRUSH )
			dc.DrawRectangle( xText - border, yText - border, tWidth + border*2, lineHeight * len(text) + border*2 )

			dc.SetTextForeground( wx.WHITE )
			dc.SetTextBackground( wx.BLACK )

			for t in text:
				dc.DrawText( t, xText, yText )	
				yText += int( tHeight * 1.15 )
			
		# Draw a border around the zoom photo.
		dc.SetBrush( wx.TRANSPARENT_BRUSH )
		dc.SetPen( wx.Pen(outlineColour, penWidth) )
		dc.DrawRectangle( xViewPos, yViewPos, viewWidth, viewHeight-penWidthDiv2 )
		
	def OnEnterWindow( self, event ):
		pass
		
	def OnSize( self, event ):
		self.resetBmSave()
		self.drawingIsSafe = False
		if self.jpgHeight is not None:
			self.scale = min( 1.0, float(event.GetSize()[1]) / float(self.jpgHeight) )
			self.refreshCompositeBitmap()
		wx.CallAfter( self.Refresh )
		self.scrollCallback()
		event.Skip()
		
	def OnLeftDown( self, event ):
		self.restoreBm()
		self.xDragLast = event.GetX()
		self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
		event.Skip()
		
	def OnLeftUp( self, event ):
		self.tCursor = self.tFromX( event.GetX() )
		wx.CallAfter( self.OnLeaveWindow )
		wx.CallAfter( self.Refresh )
		self.SetCursor( wx.NullCursor )
		event.Skip()
		
	def doZoom( self, dir=None, event=None, magnification=None ):
		assert dir is not None or magnification is not None

		self.restoreBm()
		magnificationSave = self.magnification
		if magnification is not None:
			self.magnification = magnification
		else:
			magFactor = 0.90
			if dir < 0:
				self.magnification /= magFactor
			else:
				self.magnification *= magFactor
		
		self.magnification = min( 10.0, max(0.10, self.magnification) )
		if self.magnification != magnificationSave:
			if event:
				x, y = event.GetX(), event.GetY()
			else:
				x, y = self.GetClientSize()[0]-4, 4
			for i in range(0,50,10):
				wx.CallLater( i*5, self.drawZoomPhoto, x, y )
	
	def OnMouseWheel( self, event ):
		if event.ControlDown() and not event.ShiftDown():
			self.doZoom( -event.GetWheelRotation(), event )
		else:
			self.mouseWheelCallback( event )
	
	def OnMotion( self, event ):		
		if not self.drawingIsSafe:
			self.resetBmSave()
			return
		
		x, y, dragging = event.GetX(), event.GetY(), event.Dragging()
		
		winWidth, winHeight = self.GetClientSize()
		self.xMotionLast, self.yMotionLast  = x, y
		
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
			self.drawCurrentLine( x, y )
			wx.CallAfter( self.drawZoomPhoto, x, y )
		
	def OnLeaveWindow( self, event=None ):
		self.restoreBm()
		self.xMotionLast = None
		
	def draw( self, dc, winWidth, winHeight ):
		dc.SetBackground( wx.Brush(wx.Colour(0xd3,0xd3,0xd3), wx.SOLID) )
		dc.Clear()
	
		self.xMotionLast = None
		if not self.compositeBitmap:
			return
		
		compositeDC = wx.MemoryDC( self.compositeBitmap )
		dc.Blit(
			0, 0, winWidth, self.photoHeight,
			compositeDC,
			self.bitmapLeft, 0,
		)
		compositeDC.SelectObject( wx.NullBitmap )
		
		# Draw the photo under the cursor.
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
		border = tHeight // 4
		
		# Draw the rounded rectangles around the current time.
		gc.SetPen( wx.Pen(wx.Colour(64,64,64), 1) )
		gc.SetBrush( wx.Brush(wx.Colour(200,200,200)) )
		rect = wx.Rect( xCursor - tWidth//2 - border, 0, tWidth + border*2, tHeight + border*2 )
		gc.DrawRoundedRectangle( rect.GetLeft(), rect.GetTop(), rect.GetWidth(), rect.GetHeight(), int(border*1.5) )
		rect.SetTop( winHeight - tHeight - border*2 )
		gc.DrawRoundedRectangle( rect.GetLeft(), rect.GetTop(), rect.GetWidth(), rect.GetHeight(), int(border*1.5) )
		
		# Draw the text on the top and the bottom.
		gc.DrawText( text, xCursor - tWidth//2, border )
		if self.triggerTime:
			text = '{:+.3f} TRG'.format( self.tCursor - self.triggerTime )
			tWidth, tHeight = gc.GetTextExtent( text )
		gc.DrawText( text, xCursor - tWidth//2, winHeight - tHeight - border )
		self.drawingIsSafe = True
	
	def OnPaint( self, event=None ):
		winWidth, winHeight = self.GetClientSize()
		self.draw( wx.BufferedPaintDC(self), winWidth, winHeight )
		
	def GetBitmap( self ):
		return self.compositeBitmap if self.compositeBitmap else None
		
	def GetZoomMagnification( self ):
		return self.magnification
		
	def SetZoomMagnification( self, magnification ):
		self.doZoom( 0, magnification=magnification )

class FinishStripPanel( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize, style=0, fps=25.0, photoViewCB=None ):
		super().__init__( parent, id, size=size, style=style )
		
		self.photoViewCB = photoViewCB
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
		
		self.zoomInButton = wx.BitmapButton( self, bitmap=Utils.getBitmap('Zoom-In-icon.png'))
		self.zoomInButton.Bind( wx.EVT_BUTTON, lambda event: self.finish.doZoom(-1) )
		self.zoomOutButton = wx.BitmapButton( self, bitmap=Utils.getBitmap('Zoom-Out-icon.png'))
		self.zoomOutButton.Bind( wx.EVT_BUTTON, lambda event: self.finish.doZoom(1) )
		zs = wx.BoxSizer( wx.HORIZONTAL )
		zs.Add( self.zoomInButton )
		zs.Add( self.zoomOutButton )
		
		self.direction = wx.RadioBox( self,
			label=_(''),
			choices=[_('Finish Right to Left'), _('Finish Left to Right')],
			majorDimension=1,
			style=wx.RA_SPECIFY_ROWS
		)
		self.direction.SetSelection( 1 if self.leftToRight else 0 )
		self.direction.Bind( wx.EVT_RADIOBOX, self.onDirection )

		self.recenter = wx.BitmapButton(self, bitmap=Utils.getBitmap('center-icon.png') )
		self.recenter.SetToolTip( wx.ToolTip('Recenter') )
		self.recenter.Bind( wx.EVT_BUTTON, self.onRecenter )
		
		self.photoView = wx.BitmapButton( self, bitmap=Utils.getBitmap('outline_photo_library_black_24dp.png') )
		self.photoView.SetToolTip( wx.ToolTip('Photo View') )
		self.photoView.Bind( wx.EVT_BUTTON, self.onPhotoView )
		
		self.copyToClipboard = wx.BitmapButton(self, bitmap=Utils.getBitmap('copy-to-clipboard.png'))
		self.copyToClipboard.SetToolTip( wx.ToolTip('Copy Finish Strip to Clipboard') )
		self.copyToClipboard.Bind( wx.EVT_BUTTON, self.onCopyToClipboard )
		
		szs = wx.BoxSizer( wx.HORIZONTAL )
		szs.Add( wx.StaticText(self, label='{}'.format(_('Stretch'))), flag=wx.ALIGN_CENTRE_VERTICAL )
		szs.Add( self.stretchSlider, 1, flag=wx.EXPAND )
		szs.Add( wx.StaticText(self, label='{}'.format(_('Zoom'))), flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=4 )
		szs.Add( zs )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.direction, flag=wx.ALIGN_CENTRE_VERTICAL )
		hs.Add( self.recenter, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )
		hs.Add( self.photoView, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=4 )
		hs.Add( self.copyToClipboard, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=4 )
		hs.Add( wx.StaticText(self, label='\n'.join([
					'Pan: Click and Drag',
					'Stretch: Mousewheel',
				])
			),
			flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16
		)
		hs.Add( wx.StaticText(self, label='\n'.join([
					'Zoom In: Ctrl+Mousewheel',
					'Show Frame: Right-click',
				])
			),
			flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16
		)
		
		self.frameCount = wx.StaticText( self, label='   Frames' )
		hs.Add( self.frameCount, flag=wx.LEFT|wx.ALIGN_CENTRE_VERTICAL, border=16 )
		
		vs.Add( self.finish, 1, flag=wx.EXPAND )
		vs.Add( self.timeScrollbar, flag=wx.EXPAND )
		vs.Add( szs, flag=wx.EXPAND|wx.ALL, border=0 )
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
		self.finish.SetTsJpgs( tsJpgs, ts )
		if ts and self.finish.tsFirst:
			self.finish.SetT( (ts-self.finish.tsFirst).total_seconds() )
		
		self.stretchSlider.SetRange( *self.getSpeedPixelsPerSecondMinMax() )
		self.scrollCallback()
		self.frameCount.SetLabel( '{} Frames'.format(len(tsJpgs)) if tsJpgs else '' )
		
	def GetTsJpgs( self ):
		return self.finish.tsJpgs
			
	def Clear( self ):
		self.info = {}
		self.finish.SetTsJpgs( [] )
		
	def onRecenter( self, event ):
		self.finish.SetT( None )
		
	def onPhotoView( self, event ):
		if self.photoViewCB:
			self.photoViewCB( self.finish.xZoom or 0 )
		
	def GetZoomMagnification( self ):
		return self.finish.GetZoomMagnification()
		
	def SetZoomMagnification( self, magnification ):
		self.finish.SetZoomMagnification( magnification )


class FinishStripDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize,
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX,
			dir=None, fps=25.0, leftToRight=True, pixelsPerSec=None ):
			
		if size == wx.DefaultSize:
			displayWidth, displayHeight = wx.GetDisplaySize()
			width = int(displayWidth * 0.9)
			height = 780
			size = wx.Size( width, height )

		super().__init__( parent, id, size=size, style=style, title=_('Finish Strip') )
		
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
	from Database import GlobalDatabase
	app = wx.App(False)
	
	displayWidth, displayHeight = wx.GetDisplaySize()
	
	width = round(displayWidth * 0.8)
	height = round(displayHeight * 0.8)
	
	mainWin = wx.Frame(None,title="FinishStrip", size=(width, height))
	fs = FinishStripPanel( mainWin )
	mainWin.Show()
	
	tsJpgs = GlobalDatabase().getLastPhotos( 90 )
	fs.SetTsJpgs( tsJpgs, tsJpgs[len(tsJpgs)//2][0], info={} )
	
	#fsd = FinishStripDialog( mainWin )
	#fsd.ShowModal()
	
	app.MainLoop()
