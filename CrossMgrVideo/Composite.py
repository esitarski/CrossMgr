import wx
import wx.lib.scrolledpanel as scrolled
import os
import sys
import cv2
import glob
from math import tan, radians
from datetime import datetime, timedelta

import CVUtil

class CompositeCtrl( wx.Control ):
	def __init__( self, parent, size=(600,600) ):
		super().__init__( parent, size=size )
		self.tsJpgs = []
		self.imagePixelsPerSeconds = 100
		self.leftToRight = True
		self.imageToScreenFactor = 1.0				# convert image coordinates to screen coordinates
		self.imageHeight = self.imageWidth = 600
		self.xVLeft = 0								# left side to show composite image (in image coordinates).
		self.compositeBitmap = None
		
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_ERASE_BACKGROUND, self.OnErase )

	def OnSize( self, event ):
		self.makeComposite()
		self.adjustScrollbar()
		self.Refresh()
		
	def OnErase( self, event ):
		pass
		
	def calculateCompositeBitmapWidth( self ):
		if not self.tsJpgs:
			self.imageToScreenFactor = 1.0
			return 128
			
		dt = (self.tsJpgs[-1][0] - self.tsJpgs[0][0]).total_seconds()
		
		self.imageWidth, self.imageHeight = CVUtil.getWidthHeight( self.tsJpgs[0][1] )
		
		self.compositeVBitmapWidth = round(dt * self.imagePixelsPerSecond + self.imageWidth * 2.5)
		self.imageToScreenFactor = self.GetSize()[1] / self.imageHeight
		self.compositeBitmap = None	
		
		return self.compositeVBitmapWidth

	def Set( self, tsJpgs, imagePixelsPerSecond=100, leftToRight=True ):
		self.tsJpgs = tsJpgs
		self.imagePixelsPerSecond = imagePixelsPerSecond
		self.leftToRight = leftToRight
		self.calculateCompositeBitmapWidth()
		
		self.xVLeft = 0
		self.makeComposite()
		self.adjustScrollbar()
		self.Refresh()
		
	def SetPixelsPerSecond( self, imagePixelsPerSecond ):
		self.imagePixelsPerSecond = imagePixelsPerSecond
		self.calculateCompositeBitmapWidth()
		self.makeComposite()
		self.adjustScrollbar()
		self.Refresh()
		
	def SetScrollbar( self, scrollbar ):
		self.scrollbar = scrollbar
		self.scrollbar.Bind( wx.EVT_SCROLL, self.onScroll )
		
	def onScroll( self, event ):
		self.SetXVLeft( event.GetPosition() / (self.imageToScreenFactor or 1.0) )

	def adjustScrollbar( self ):
		''' Set up a scrollbar in screen coordinates. '''
		if not self.scrollbar or not self.compositeBitmap:
			return
			
		screenWidth, screenHeight = self.GetSize()
		compositeWidth, compositeHeight = self.compositeBitmap.GetSize()
		
		pixRange = compositeWidth - screenWidth
		prevPositionRatio = self.scrollbar.GetThumbPosition() / (self.scrollbar.GetRange() or 1)
		
		self.scrollbar.SetScrollbar( round(prevPositionRatio * pixRange), screenWidth, pixRange, screenWidth )
		self.SetXVLeft( self.scrollbar.GetThumbPosition()  / (self.imageToScreenFactor or 1.0) )

	def SetXVLeft( self, xVLeft ):
		self.xVLeft = max( 0, xVLeft )
		self.Refresh()
		
	def SetTLeft( self, ts ):
		self.SetXVLeft( xVFromT(ts) )

	def xVFromT( self, t ):
		''' Returns x in image coordinates (not screen coordinates). '''
		if self.leftToRight:
			return self.imageWidth/2 + (self.tsJpgs[-1][0] - t).total_seconds() * self.imagePixelsPerSecond
		else:
			return self.imageWidth/2 + (t - self.tsJpgs[0][0]).total_seconds() * self.imagePixelsPerSecond
			
	def tFromXV( self, x ):
		x /= self.imageToScreenFactor	# Convert from screen to image coordinates.
		if self.leftToRight:
			return self.tsJpgs[-1][0] - timedelta( seconds=( (x - self.imageWidth/2) / self.imagePixelsPerSecond ) )
		else:
			return self.tsJpgs[0][0] + timedelta( seconds=( (x - self.imageWidth/2) / self.imagePixelsPerSecond ) )

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
		width, height = self.GetSize()
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
		xVFromT = self.xVFromT

		xImages = [round(xVFromT(ts)) for ts, jpg in reversed(self.tsJpgs)]

		first = True
		if self.leftToRight:
			xImages.append( round(xImages[-1] + widthDiv2) )	# Write a sentinel.

			for i, (ts, jpg) in enumerate(reversed(self.tsJpgs)):
				try:
					sourceDC.SelectObject(CVUtil.jpegToBitmap(jpg))
				except Exception as e:
					continue
				
				if first:
					first = False
					copyImage( sourceDC,
						0, 0, self.imageWidth, self.imageHeight,
						0, 0,
					)
				
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
				
				if first:
					first = False
					copyImage( sourceDC,
						0, 0, self.imageWidth, self.imageHeight,
						0, 0,
					)

				x = xImages[i]
				w = xImages[i] - xImages[i+1] + 1
								
				copyImage( sourceDC,
					0, 0, w, self.imageHeight,
					x - w, 0,
				)
				sourceDC.SelectObject(wx.NullBitmap)

	def OnPaint( self, event ):
		if not self.compositeBitmap:
			return
		
		dc = wx.PaintDC( self )
		sourceDC = wx.MemoryDC( self.compositeBitmap )

		width, height = self.GetSize()
		dc.Blit( 0, 0, width, height, sourceDC, round(self.xVLeft * self.imageToScreenFactor), 0 )

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
	
	viewS = fieldOfViewM / speedMPS										# Seconds for object to pass through field of view at given speed.
	pixelsPerSecond = frameWidthPixels / viewS							# Speed expressed in pixels/second.
	
	return pixelsPerSecond

class CompositePanel( wx.Panel):
	def __init__( self, parent ):
		super().__init__( parent )
		vs = wx.BoxSizer( wx.VERTICAL )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.composite = CompositeCtrl( self )
		hs.Add( self.composite, 1, flag=wx.EXPAND )
		self.speedScrollbar = wx.ScrollBar( self, style=wx.SB_VERTICAL )
		self.speedScrollbar.Bind( wx.EVT_SCROLL, self.onScrollSpeed )
		speedMax = 110	# k/h
		thumbSize = 10
		self.speedScrollbar.SetScrollbar( 50, thumbSize, speedMax, thumbSize )
		hs.Add( self.speedScrollbar, flag=wx.EXPAND )
		
		vs.Add( hs, 1, flag=wx.EXPAND )
		
		self.timeScrollbar = wx.ScrollBar( self, style=wx.SB_HORIZONTAL )
		self.composite.SetScrollbar( self.timeScrollbar )
		vs.Add( self.timeScrollbar, 0, flag=wx.EXPAND )
		self.SetSizer(vs)
		
	def onScrollSpeed( self, event ):
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
			frame = CVUtil.jpegToFrame( jpg )
			frame = cv2.flip( frame, 1 )
			jpg = CVUtil.frameToJPeg( frame )
			
		tsJpgs.append( (ts, jpg) )
	
	pixelsPerSecond = getPixelsPerSecond( frameWidthPixels=CVUtil.getWidthHeight(tsJpgs[0][1])[0], speedKMH=50 )
	#-------------------------------------------------------------------	
	displayWidth, displayHeight = wx.GetDisplaySize()
	
	width = round(displayWidth * 0.8)
	height = round(displayHeight * 0.8)
	
	mainWin = wx.Frame(None,title="Composite", size=(width, height))
	cp = CompositePanel( mainWin )
	
	cp.Set( tsJpgs, pixelsPerSecond, leftToRight=leftToRight )
	mainWin.Show()
	
	app.MainLoop()

