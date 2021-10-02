import wx
import wx.lib.scrolledpanel as scrolled
import os
import sys
import cv2
import glob
from math import tan, radians
from datetime import datetime, timedelta

import CVUtil

def formatTime( ts ):
	return ts.strftime('%H:%M:%S.%f')[:-3]
	
def formatSeconds( secs ):
	return '{:+.3f}'.format( secs )

class CompositeCtrl( wx.Control ):
	def __init__( self, parent, size=(600,600) ):
		super().__init__( parent, size=size )
		self.tsJpgs = []
		self.imagePixelsPerSecond = 100
		self.leftToRight = True
		self.imageToScreenFactor = 1.0				# convert image coordinates to screen coordinates
		self.imageHeight = self.imageWidth = 600
		self.xVLeft = 0								# left side to show composite image (in image coordinates).
		self.compositeBitmap = None
		
		self.pointerTS = None
		self.currentTS = None
		self.triggerTS = None
		
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_ERASE_BACKGROUND, self.OnErase )
		
		self.Bind( wx.EVT_MOTION, self.OnMotion )
		self.Bind( wx.EVT_LEFT_DOWN, self.OnLeft )

	def OnSize( self, event ):
		self.makeComposite()
		self.Refresh()
		
	def OnErase( self, event ):
		pass
		
	def tsFromPointer( self, xPointer ):
		xV = self.xVLeft + xPointer / self.imageToScreenFactor
		return self.tsFromXV( xV )
		
	def OnLeft( self, event ):
		if not self.compositeBitmap:
			return
		self.currentTS = self.tsFromPointer( event.GetX() )
		self.Refresh()
		event.Skip()
		
	def OnMotion( self, event ):
		if not self.compositeBitmap:
			return
		self.pointerTS = self.tsFromPointer( event.GetX() )
		self.Refresh()
				
	def calculateCompositeBitmapWidth( self ):
		if not self.tsJpgs:
			self.imageToScreenFactor = 1.0
			return 128
			
		dt = (self.tsJpgs[-1][0] - self.tsJpgs[0][0]).total_seconds()
		
		self.imageWidth, self.imageHeight = CVUtil.getWidthHeight( self.tsJpgs[0][1] )
		
		self.compositeVBitmapWidth = round(dt * self.imagePixelsPerSecond)
		self.imageToScreenFactor = self.GetClientSize()[1] / self.imageHeight
		self.compositeBitmap = None	
		self.pointerTS = None		# On-screen reference
		
		return self.compositeVBitmapWidth

	def Set( self, tsJpgs, imagePixelsPerSecond=100, leftToRight=True, triggerTS=None ):
		if not tsJpgs:
			self.pointerTS = None
			self.triggerTS = None
			self.currentTS = None
			self.compositeBitmap = None
		
		self.tsJpgs = tsJpgs
		self.imagePixelsPerSecond = imagePixelsPerSecond
		self.leftToRight = leftToRight
		
		self.pointerTS = None		# timestamp of the current pointer
		self.currentTS = None		# timestamp of the current set position
		
		self.calculateCompositeBitmapWidth()
		
		self.xVLeft = 0
		self.makeComposite()
		self.SetTriggerTS( triggerTS )	# Also does a Refresh.
		
	def SetLeftToRight( self, leftToRight=True ):
		self.leftToRight = leftToRight
		self.makeComposite()	
		
	def SetTriggerTS( self, triggerTS ):
		self.triggerTS = triggerTS
		if triggerTS and self.compositeBitmap:
			# Center the composite view on the trigger.
			self.currentTS = triggerTS
			screenWidth, screenHeight = self.GetClientSize()
			self.xVLeft = max( 0, self.xVFromTS( triggerTS ) - screenWidth / self.imageToScreenFactor )
			if self.scrollbar:
				self.scrollbar.SetThumbPosition( round(self.xVLeft * self.imageToScreenFactor) )
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

	def adjustScrollbar( self ):
		''' Set up a scrollbar in screen coordinates. '''
		if not self.scrollbar or not self.compositeBitmap:
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
		self.SetXVLeft( xVFromTS(ts) )

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
		self.calculateCompositeBitmapWidth()
		width, height = self.GetClientSize()
		f = self.imageToScreenFactor
		self.compositeBitmap = wx.Bitmap( round(self.compositeVBitmapWidth * f), height )
		dc = wx.MemoryDC( self.compositeBitmap )
		
		if not self.tsJpgs:
			dc.SetBackground( wx.Brush(wx.Colour(200,200,200)) )
			dc.Clear()
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

		self.adjustScrollbar()

	def OnPaint( self, event ):
		dc = wx.PaintDC( self )

		if not self.compositeBitmap:
			dc.SetBackground( wx.BLACK_BRUSH )
			dc.Clear()
			return
		
		width, height = self.GetClientSize()
		if self.compositeBitmap.GetSize()[0] < width:
			dc.SetBackground( wx.BLACK_BRUSH )
			dc.Clear()
		
		dc.Blit( 0, 0, width, height, wx.MemoryDC(self.compositeBitmap), round(self.xVLeft * self.imageToScreenFactor), 0 )
		
		# Draw the indicator lines.
		fontSize = max( 16, height//40 )
		lineHeight = round( fontSize * 1.2 )
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
			x = round( (self.xVFromTS( self.triggerTS ) - self.xVLeft) * self.imageToScreenFactor )
			drawIndicatorLine( x, wx.Colour(0,0,255), text, False )
		
		if self.currentTS:
			text = [formatTime( self.currentTS )]
			if self.triggerTS:
				text.append( '{} TRG'.format( formatSeconds( (self.currentTS - self.triggerTS).total_seconds()) ) )
			text.append( '' )	# Blank line to give room for triggerTS line.
			x = round( (self.xVFromTS( self.currentTS ) - self.xVLeft) * self.imageToScreenFactor )
			drawIndicatorLine( x, wx.Colour(255,0,0), text, False )

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

class CompositePanel( wx.Panel):
	def __init__( self, parent ):
		super().__init__( parent )
		
		self.composite = CompositeCtrl( self )
		
		self.leftToRight = wx.Choice( self, choices=('\u27F6 Left to Right', '\u27F5 Right to Left') )
		self.leftToRight.SetSelection( 0 )
		self.leftToRight.Bind( wx.EVT_CHOICE, self.onLeftToRight )
		
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
		hs.Add( self.leftToRight, flag=wx.ALL, border=4 )
		hs.Add( self.timeScrollbar, 1, wx.EXPAND )
		
		vs.Add( hs, 0, flag=wx.EXPAND )
				
		self.SetSizer( vs )
		
	def onLeftToRight( self, event ):
		self.composite.SetLeftToRight( self.leftToRight.GetSelection() == 0 )
		
	def onCompositeWheel( self, event ):
		rot = event.GetWheelRotation()
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
	cp.Set( tsJpgs, pixelsPerSecond, leftToRight=leftToRight, triggerTS = triggerTS )
	mainWin.Show()
	
	app.MainLoop()

