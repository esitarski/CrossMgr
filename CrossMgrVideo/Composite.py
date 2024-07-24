import wx
import os
import cv2
import glob
from math import tan, radians
from datetime import datetime, timedelta

import Utils
import CVUtil

def formatTime( ts ):
	return ts.strftime('%H:%M:%S.%f')[:-3]
	
def formatSeconds( secs ):
	return '{:+.3f}'.format( secs )
	
def getPixelsPerSecond( frameWidthPixels=1920, finishWidthM=8, cameraDistanceFromEdgeM=1, lensAngle=84, speedKMH=50 ):
	'''
		Calculate pixels per second given:
		
			frameWidthPixels:			width of photo image (pixels).  default=1920 pixels
			finishWidthM:				width of finish (m).			default=8 meters
			cameraDistanceFromEdgeM:	distance from edge of road (m)	default=1 meters
			lensAngle:					angle of webcam lens			default=84 degrees
			speedKMH:					speed of passing object (kmh)	default=50 km/h
	'''
	speedMPS = speedKMH / 3.6											# convert to meters/second
	
	finishCenterM = finishWidthM/2.0 + cameraDistanceFromEdgeM			# Distance camera from center of finish line.
	fieldOfViewM = 2.0 * finishCenterM * tan( radians(lensAngle/2.0) )	# Horizontal distance of camera field of view (distance to enter and exit the frame).
	
	viewS = fieldOfViewM / (speedMPS or 1.0)							# Seconds for object to pass through field of view at given speed.
	pixelsPerSecond = frameWidthPixels / viewS							# Speed expressed in pixels/second.
	
	return pixelsPerSecond

class CompositeCtrl( wx.Control ):
	def __init__( self, parent, size=(600,600) ):
		super().__init__( parent, size=size )
		
		self.tsJpgs = []
		self.iJpg = 0								# Index of the inset image.
		
		self.imagePixelsPerSecond = 100
		self.leftToRight = True
		self.imageToScreenFactor = 1.0				# convert image coordinates to screen coordinates
		self.imageHeight = self.imageWidth = 600
		self.xVLeft = 0								# left side to show composite image (in image coordinates).
		
		self.xClickLeft = 0							# Last left mouse click.
		self.xVLeftClick = 0
		
		self.Set( None )
		
		self.insetMagnification = 0.5
		
		self.filterContrast  = False
		self.filterSharpen   = False
		self.filterGrayscale = False
		
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_ERASE_BACKGROUND, self.OnErase )
		
		self.Bind( wx.EVT_LEFT_DOWN, self.OnLeftDown )
		self.Bind( wx.EVT_MOTION, self.OnMotion )

	def isValid( self ):
		return len(self.tsJpgs) >= 2

	def OnSize( self, event ):
		if self.isValid():
			self.makeComposite()
			self.Refresh()
		
	def OnErase( self, event ):
		pass
		
	def tsFromPointer( self, xPointer ):
		xV = self.xVLeft + xPointer / self.imageToScreenFactor
		return self.tsFromXV( xV )
		
	def OnLeftDown( self, event ):
		if self.isValid():
			self.currentTS = self.tsFromPointer( event.GetX() )
			self.xVLeftClick = self.xVLeft
			self.xClickLeft = event.GetX()
			self.Refresh()
			event.Skip()
		
	def OnMotion( self, event ):
		if not self.isValid():
			return

		self.pointerTS = self.insetTS = self.tsFromPointer( event.GetX() )
		if event.Dragging() :
			if event.LeftIsDown() and self.scrollbar:
				dx = self.xClickLeft - event.GetX()
				xV = self.xVLeftClick + dx / self.imageToScreenFactor
				xSMax = self.scrollbar.GetRange() - self.scrollbar.GetThumbSize()
				xS = min( xSMax, round(xV * self.imageToScreenFactor) )
				if 0 <= xS < xSMax:
					self.scrollbar.SetThumbPosition( xS )
					self.xVLeft = round(xV)
		self.Refresh()
				
	def calculateCompositeBitmapWidth( self ):
		self.compositeBitmap = None	
		self.pointerTS = None		# On-screen reference line

		if not self.isValid():
			self.imageToScreenFactor = 1.0
			self.compositeVBitmapWidth = 1024
			self.imageWidth, self.imageHeight = 1024, 1024
			
		dt = max( 1.0/30.0, (self.tsJpgs[-1][0] - self.tsJpgs[0][0]).total_seconds() )
		
		self.imageWidth, self.imageHeight = CVUtil.getWidthHeight( self.tsJpgs[0][1] )
		self.imageToScreenFactor = self.GetClientSize()[1] / self.imageHeight
		
		self.compositeVBitmapWidth = round(dt * self.imagePixelsPerSecond)
		
		return self.compositeVBitmapWidth

	def Set( self, tsJpgs, imagePixelsPerSecond=None, leftToRight=None, triggerTS=None, insetMagnification=None ):
		self.tsJpgs = tsJpgs or []
		self.iJpg = 0
		
		if len(self.tsJpgs) < 2:
			self.pointerTS = None
			self.insetTS   = None
			self.triggerTS = None
			self.currentTS = None
			self.compositeBitmap = None
			return
		
		self.imagePixelsPerSecond = (imagePixelsPerSecond if imagePixelsPerSecond is not None
			else getPixelsPerSecond( frameWidthPixels=CVUtil.getWidthHeight(tsJpgs[0][1])[0], speedKMH=50 )
		)
		if leftToRight is not None:
			self.leftToRight = leftToRight
		
		self.calculateCompositeBitmapWidth()
		
		self.pointerTS = None		# timestamp of the pointer
		self.currentTS = None		# timestamp of the set position
		self.insetTS   = triggerTS or tsJpgs[-1][0]	# timestamp of the photo inset
		if insetMagnification is not None:
			self.SetInsetMagnification( insetMagnification )
		
		self.xVLeft = 0
		self.makeComposite()
		self.SetTriggerTS( triggerTS )	# Also does a Refresh.
		
	def SetLeftToRight( self, leftToRight=True ):
		self.leftToRight = leftToRight
		self.makeComposite()
		self.Refresh()
		
	def SetFilters( self, contrast=None, sharpen=None, grayscale=None ):
		if contrast is not None:
			self.filterContrast = contrast
		if sharpen is not None:
			self.filterSharpen = sharpen
		if grayscale is not None:
			self.filterGrayscale = grayscale
		self.makeComposite()		
		self.Refresh()
		
	def SetTriggerTS( self, triggerTS ):
		self.triggerTS = triggerTS
		if triggerTS and self.isValid():
			# Center the composite view on the trigger.
			self.currentTS = triggerTS
			screenWidth, screenHeight = self.GetClientSize()
			self.xVLeft = round(
				min(
					max( 0, self.xVFromTS( triggerTS ) - (screenWidth/2) / self.imageToScreenFactor ),
					(self.compositeBitmap.GetWidth() - screenWidth) / self.imageToScreenFactor
				)
			)
			if self.scrollbar:
				wx.CallAfter( self.scrollbar.SetThumbPosition, round(self.xVLeft * self.imageToScreenFactor) )
		self.Refresh()
		
	def SetPixelsPerSecond( self, imagePixelsPerSecond ):
		self.imagePixelsPerSecond = imagePixelsPerSecond
		self.calculateCompositeBitmapWidth()
		self.makeComposite()
		self.Refresh()
		
	def SetScrollbar( self, scrollbar ):
		self.scrollbar = scrollbar
		self.scrollbar.Bind( wx.EVT_SCROLL, self.onScroll )
		
	def onScroll( self, event ):
		self.SetXLeft( event.GetPosition() )
		
	def GetInsetMagnification( self ):
		return self.insetMagnification

	def SetInsetMagnification( self, insetMagnification ):
		self.insetMagnification = max( 0.1, min(1.0, insetMagnification) )
		self.Refresh()

	def adjustScrollbar( self ):
		''' Set up a scrollbar in screen coordinates. '''
		if not self.scrollbar or not self.isValid() or not self.compositeBitmap:
			return
			
		screenWidth, screenHeight = self.GetClientSize()
		compositeWidth, compositeHeight = self.compositeBitmap.GetSize()
		
		pixRange = compositeWidth
		prevPositionRatio = self.scrollbar.GetThumbPosition() / (self.scrollbar.GetRange() or 1)
		
		self.scrollbar.SetScrollbar( round(prevPositionRatio * pixRange), screenWidth, pixRange, screenWidth )
		self.SetXVLeft( self.scrollbar.GetThumbPosition()  / (self.imageToScreenFactor or 1.0) )

	def SetXLeft( self, xLeft ):
		# Set scroll in screen coordinates.
		self.xVLeft = xLeft / (self.imageToScreenFactor or 1.0)
		self.Refresh()

	def SetXVLeft( self, xVLeft ):
		# Set scroll in image coordinates.
		self.xVLeft = max( 0, xVLeft )
		self.Refresh()
		
	def SetTLeft( self, ts ):
		# Set scroll position by time.
		self.SetXVLeft( self.xVFromTS(ts) )

	def xVFromTS( self, t ):
		''' Returns x in image coordinates (not screen coordinates). '''
		if self.leftToRight:
			return (self.tsJpgs[-1][0] - t).total_seconds() * self.imagePixelsPerSecond
		else:
			return (t - self.tsJpgs[0][0]).total_seconds() * self.imagePixelsPerSecond
			
	def tsFromXV( self, xv ):
		''' Returns t from image coordinates (not screen coordinates). '''
		if self.leftToRight:
			return self.tsJpgs[-1][0] - timedelta( seconds=xv/self.imagePixelsPerSecond )
		else:
			return self.tsJpgs[0][0] + timedelta( seconds=xv/self.imagePixelsPerSecond )

	def makeComposite( self ):
		'''
			Make a composite bitmap.
			The idea here is to create a composite bitmap that can be simply blit'ed to the screen (fast).
			The height of the bitmap is the same of the screen, and the width is a long as necessary for all the images.
			
			We have to deal with 2 coordinate systems:  image and screen.
			Images coordinates have a "V" and are in image coordinates.
			Image coordinates are converted to screen coordinates by multipying by self.imageToScreenFactor.
		'''
		if not self.isValid():
			self.compositeBitmap = None
			return
		
		self.calculateCompositeBitmapWidth()
		width, height = self.GetClientSize()
		f = self.imageToScreenFactor
		
		# Make sure we don't exceed the maximum bitmap size.
		MaxBitmapSize = 32768
		bitmapWidth = round(self.compositeVBitmapWidth * f)
		if bitmapWidth > MaxBitmapSize:
			dt = max( 1.0/30.0, (self.tsJpgs[-1][0] - self.tsJpgs[0][0]).total_seconds() )
			bitmapWidth = MaxBitmapSize
			self.imagePixelsPerSecond = bitmapWidth / dt
			self.compositeVBitmapWidth = round( bitmapWidth / f )
		
		try:
			self.compositeBitmap = wx.Bitmap( bitmapWidth, height )
			dc = wx.MemoryDC( self.compositeBitmap )
		except Exception as e:
			print( e )
			return
		
		def copyImage(	sourceDC,
						sourceX, sourceY, sourceW, sourceH,
						destX,   destY ):
			# Transform to screen coordinates.
			dc.StretchBlit(
				round(destX*f),   round(destY*f),   round(sourceW*f),   round(sourceH*f),
				sourceDC,
				sourceX, sourceY, sourceW, sourceH,
			)
		
		sourceDC = wx.MemoryDC()
		PS = self.imagePixelsPerSecond
		widthDiv2 = self.imageWidth // 2
		xVFromTS = self.xVFromTS

		# Precompute the x offsets of the images.
		xImages = [round(xVFromTS(ts)) for ts, jpg in reversed(self.tsJpgs)]

		if self.leftToRight:
			xImages.append( round(xImages[-1] + widthDiv2) )	# Write a sentinel.

			for i, (ts, jpg) in enumerate(reversed(self.tsJpgs)):
				try:
					sourceDC.SelectObject(CVUtil.jpegToBitmap(jpg))
				except Exception as e:
					continue
				
				x = xImages[i]
				w = xImages[i+1] - xImages[i] + 1
				
				copyImage( sourceDC,
					self.imageWidth - w, 0, w, self.imageHeight,
					x, 0,
				)
				sourceDC.SelectObject(wx.NullBitmap)
		else:
			xImages.append( round(xImages[-1] - widthDiv2) )	# Write a sentinel.

			for i, (ts, jpg) in enumerate(reversed(self.tsJpgs)):
				try:
					sourceDC.SelectObject(CVUtil.jpegToBitmap(jpg))
				except Exception as e:
					continue
				
				x = xImages[i]
				w = xImages[i] - xImages[i+1] + 1
								
				copyImage( sourceDC,
					0, 0, w, self.imageHeight,
					x - w, 0,
				)
				sourceDC.SelectObject(wx.NullBitmap)

		if self.filterContrast or self.filterSharpen or self.filterGrayscale:
			self.compositeBitmap = CVUtil.frameToBitmap( self.filterFrame(CVUtil.bitmapToFrame( self.compositeBitmap )) )

		self.adjustScrollbar()
		
	def filterFrame( self, frame ):
		if self.filterContrast:
			frame = CVUtil.adjustContrastFrame( frame )
		if self.filterSharpen:
			frame = CVUtil.sharpenFrame( frame )
		if self.filterGrayscale:
			frame = CVUtil.grayscaleFrame( frame )
		return frame

	def setClosestPhoto( self, ts ):
		self.iJpg = 0
		if len(self.tsJpgs) <= 1:
			return self.iJpg
		
		iLeft, iRight = 0, len(self.tsJpgs)
		while iRight - iLeft > 1:
			iMid = (iLeft + iRight) >> 1
			if ts < self.tsJpgs[iMid][0]:
				iRight = iMid
			else:
				iLeft = iMid
		
		tBest = abs( (self.tsJpgs[self.iJpg][0] - ts).total_seconds() ) 
		for i in range(max(0, iLeft-1), min(len(self.tsJpgs), iLeft+1)):
			tCur = abs( (self.tsJpgs[i][0] - ts).total_seconds() )
			if tCur < tBest:
				tBest = tCur
				self.iJpg = i
		
		return self.iJpg

	def OnPaint( self, event ):
		dc = wx.BufferedPaintDC( self )
		
		width, height = self.GetClientSize()
		
		def clear():
			dc.SetBrush( wx.BLACK_BRUSH )
			dc.SetPen( wx.TRANSPARENT_PEN )
			dc.DrawRectangle( 0, 0, width, height )

		if not self.isValid():
			clear()
			return
		
		compositeWidth, compositeHeight = self.compositeBitmap.GetSize()
		if compositeWidth < width:
			clear()
		
		try:
			dc.Blit( 0, 0, min(compositeWidth, width), height, wx.MemoryDC(self.compositeBitmap), round(self.xVLeft * self.imageToScreenFactor), 0 )
		except Exception as e:
			# print( e )
			pass
		
		# Draw the photo inset.
		if self.insetTS is not None:
			# Find the closest photo centered on the time.
			ts = self.insetTS + timedelta( seconds = (-1.0 if self.leftToRight else 1.0) * (self.imageWidth / (2 * self.imagePixelsPerSecond) ) )
			
			jpgBest = self.tsJpgs[self.setClosestPhoto(ts)][1]
					
			if jpgBest is not None:
				bm = CVUtil.frameToBitmap( self.filterFrame(CVUtil.jpegToFrame(jpgBest)) )
				lineWidth = 2
				destHeight = round(height * self.insetMagnification)
				destWidth = round((destHeight / bm.GetHeight()) * bm.GetWidth())
				destX = width - destWidth - lineWidth*2
				destY = 0
				dc.SetPen( wx.Pen(wx.Colour(255,255,0)) )
				dc.SetBrush( wx.TRANSPARENT_BRUSH )
				dc.DrawRectangle( destX, destY, destWidth+lineWidth*2, destHeight+lineWidth*2 )
				dc.StretchBlit( destX+lineWidth, destY+lineWidth, destWidth, destHeight,
					wx.MemoryDC(bm), 0, 0, bm.GetWidth(), bm.GetHeight()
				)
		
		# Draw the indicator lines.
		fontSize = max( 16, height//40 )
		lineHeight = round( fontSize * 1.25 )
		dc.SetFont( wx.Font(wx.FontInfo(fontSize)) )
		
		tsLeft = self.tsFromXV( self.xVLeft )
		tsRight = self.tsFromXV( self.xVLeft + width / self.imageToScreenFactor )
		
		def drawIndicatorLine( x, colour, text, textAtTop=True ):
			if not 0 <= x < width:
				return
			
			dc.SetPen( wx.Pen(colour) )
			dc.DrawLine( x, 0, x, height )
			
			dc.SetTextForeground( colour )
			xText = x + fontSize // 2
			yText = fontSize//2 if textAtTop else round( height - (len(text)+1) * lineHeight)
			for textCur in text:
				if textCur:
					tWidth, tHeight = dc.GetTextExtent( textCur )
					dc.DrawText( textCur, xText, yText )
				yText += lineHeight
		
		if self.pointerTS:
			text = [formatTime( self.pointerTS )]
			if self.triggerTS:
				text.append( '{} TRG'.format( formatSeconds( (self.pointerTS - self.triggerTS).total_seconds()) ) )
			if self.currentTS:
				text.append( '{} CUR'.format( formatSeconds( (self.pointerTS - self.currentTS).total_seconds()) ) )
			x = round( (self.xVFromTS( self.pointerTS ) - self.xVLeft) * self.imageToScreenFactor )
			drawIndicatorLine( x, wx.Colour(255,255,0), text, True )
			
		if self.triggerTS:
			text = ['TRG {}'.format(formatTime(self.triggerTS))]
			x = round( (self.xVFromTS(self.triggerTS) - self.xVLeft) * self.imageToScreenFactor )
			drawIndicatorLine( x, wx.Colour(0,0,255), text, False )
		
		if self.currentTS:
			text = [formatTime( self.currentTS )]
			if self.triggerTS:
				text.append( '{} TRG'.format( formatSeconds( (self.currentTS - self.triggerTS).total_seconds()) ) )
			text.append( '' )	# Blank line to give room for triggerTS line.
			x = round( (self.xVFromTS(self.currentTS) - self.xVLeft) * self.imageToScreenFactor )
			drawIndicatorLine( x, wx.Colour(255,69,0), text, False )

class CompositePanel( wx.Panel):
	def __init__( self, parent ):
		super().__init__( parent )
		
		self.composite = CompositeCtrl( self )
		
		self.leftToRight = wx.Choice( self, choices=('\u27F6 Left to Right', '\u27F5 Right to Left') )
		self.leftToRight.SetSelection( 0 )
		self.leftToRight.Bind( wx.EVT_CHOICE, self.onLeftToRight )
		
		self.trig = wx.BitmapButton(self, bitmap=Utils.getBitmap('center-icon.png') )
		self.trig.SetToolTip( wx.ToolTip('Recenter on Trigger Time') )
		self.trig.Bind( wx.EVT_BUTTON, lambda e: self.composite.SetTriggerTS(self.composite.triggerTS) )
		
		self.contrast  = wx.ToggleButton( self, label=('Contrast') )
		self.sharpen   = wx.ToggleButton( self, label=('Sharpen') )
		self.grayscale = wx.ToggleButton( self, label=('Grayscale') )
		
		self.contrast.Bind(		wx.EVT_TOGGLEBUTTON, lambda e: self.composite.SetFilters(contrast=e.IsChecked()) )
		self.sharpen.Bind(		wx.EVT_TOGGLEBUTTON, lambda e: self.composite.SetFilters(sharpen=e.IsChecked()) )
		self.grayscale.Bind(	wx.EVT_TOGGLEBUTTON, lambda e: self.composite.SetFilters(grayscale=e.IsChecked()) )
		
		self.timeScrollbar = wx.ScrollBar( self, style=wx.SB_HORIZONTAL )
		self.composite.SetScrollbar( self.timeScrollbar )
		self.composite.Bind( wx.EVT_MOUSEWHEEL, self.onCompositeWheel )
		
		self.speedScrollbar = wx.ScrollBar( self, style=wx.SB_VERTICAL )		
		speedMax = 110	# km/h
		thumbSize = 10
		self.speedScrollbar.SetScrollbar( 50, thumbSize, speedMax, thumbSize )
		self.speedScrollbar.Bind( wx.EVT_SCROLL, self.onScrollSpeed )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.composite, 1, flag=wx.EXPAND )
		hs.Add( self.speedScrollbar, 0, flag=wx.EXPAND )
		
		vs.Add( hs, 1, flag=wx.EXPAND )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.leftToRight, flag=wx.LEFT, border=2 )
		hs.Add( self.trig, flag=wx.LEFT, border=2 )
		hs.Add( self.contrast, flag=wx.LEFT, border=6 )
		hs.Add( self.sharpen, flag=wx.LEFT, border=2 )
		hs.Add( self.grayscale, flag=wx.LEFT, border=2 )
		hs.Add( self.timeScrollbar, 1, flag=wx.EXPAND, border=2 )
		
		vs.Add( hs, 0, flag=wx.EXPAND|wx.ALL, border=2 )
				
		self.SetSizer( vs )
		
	def onLeftToRight( self, event ):
		self.composite.SetLeftToRight( self.leftToRight.GetSelection() == 0 )
		
	def onCompositeWheel( self, event ):
		rot = event.GetWheelRotation()
		
		if event.ControlDown():
			self.composite.SetInsetMagnification( self.composite.GetInsetMagnification() + (0.1 if rot > 0 else -0.1) )
		elif event.ShiftDown():
			pass
		else:		
			ssb = self.speedScrollbar
			if rot < 0:
				ssb.SetThumbPosition( max(0, ssb.GetThumbPosition() - 1) )
			else:
				ssb.SetThumbPosition( min(ssb.GetRange() - ssb.GetThumbSize(), ssb.GetThumbPosition() + 1) )
			wx.CallAfter( self.onScrollSpeed )
		
	def onScrollSpeed( self, event=None ):
		if self.composite.tsJpgs:
			self.composite.SetPixelsPerSecond( getPixelsPerSecond(
					frameWidthPixels=self.composite.imageWidth,
					speedKMH=self.speedScrollbar.GetThumbPosition()
				)
			)

	def Set( self, *args, **kwargs ):
		self.composite.Set( *args, **kwargs )
		
	def GetTsJpgs( self ):
		return self.composite.tsJpgs
		
	def getIJpg( self ):
		return self.composite.iJpg
		
	def Clear( self ):
		self.composite.Set( None )
		
	def GetZoomMagnification( self ):
		return self.composite.GetInsetMagnification()
		
	def SetZoomMagnification( self, magnification ):
		self.composite.SetInsetMagnification( magnification )

if __name__ == '__main__':
	app = wx.App(False)

	leftToRight = True
	now = datetime.now()
	fps = 30.0
	spf = 1.0 / fps
	tsJpgs = []
	for i, f in enumerate(sorted(glob.glob( os.path.join('frames', 'out-*.jpg') ))):
		ts = now + timedelta( seconds=i*spf )
		with open(f, 'rb') as pf:
			jpg = pf.read()
		
		if not leftToRight:
			jpg = CVUtil.frameToJPeg( cv2.flip( CVUtil.jpegToFrame(jpg), 1 ) )
			
		tsJpgs.append( (ts, jpg) )
	
	pixelsPerSecond = getPixelsPerSecond( frameWidthPixels=CVUtil.getWidthHeight(tsJpgs[0][1])[0], speedKMH=50 )
	#-------------------------------------------------------------------	
	displayWidth, displayHeight = wx.GetDisplaySize()
	
	width = round(displayWidth * 0.8)
	height = round(displayHeight * 0.8)
	
	mainWin = wx.Frame(None,title="Composite", size=(width, height))
	cp = CompositePanel( mainWin )
	
	triggerTS = tsJpgs[0][0] + timedelta( seconds=(tsJpgs[-1][0] - tsJpgs[0][0]).total_seconds()/2)
	cp.Set( tsJpgs, pixelsPerSecond, leftToRight=True, triggerTS = triggerTS )
	mainWin.Show()
	
	app.MainLoop()

