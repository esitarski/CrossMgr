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
		self.imageToScreenFactor = 1.0
		self.imageHeight = self.imageWidth = 600
		self.xLeft = 0
		self.compositeBitmap = None
		
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_ERASE_BACKGROUND, self.OnErase )

	def OnSize( self, event ):
		self.makeComposite()
		self.Refresh()
		
	def OnErase( self, event ):
		pass
		
	def calculateCompositeBitmapWidth( self ):
		if not self.tsJpgs:
			self.imageToScreenFactor = 1.0
			return 128
			
		dt = (self.tsJpgs[-1][0] - self.tsJpgs[0][0]).total_seconds()
		
		self.imageWidth, self.imageHeight = CVUtil.getWidthHeight( self.tsJpgs[0][1] )
		
		self.compositeVBitmapWidth = round(dt * self.imagePixelsPerSecond + self.imageWidth)
		self.imageToScreenFactor = self.GetSize()[1] / self.imageHeight		
		
		return self.compositeVBitmapWidth

	def set( self, tsJpgs, imagePixelsPerSecond=100, leftToRight=True ):
		self.tsJpgs = tsJpgs
		self.imagePixelsPerSecond = imagePixelsPerSecond
		self.leftToRight = leftToRight
		self.calculateCompositeBitmapWidth()
		
		self.xLeft = 0
		self.makeComposite()
		self.Refresh()
		
	def setPixelsPerSecond( self, imagePixelsPerSecond ):
		self.imagePixelsPerSecond = imagePixelsPerSecond
		self.calculateCompositeBitmapWidth()
		self.makeComposite()
		self.Refresh()

	def SetXLeft( self, xLeft ):
		self.xLeft = xLeft
		self.Refresh()
		
	def SetTLeft( self, ts ):
		self.SetXLeft( xFromT(ts) )

	def xFromT( self, t ):
		''' Returns x in image coordinates (not screen coordinates). '''
		if self.leftToRight:
			return self.imageWidth/2 + (self.tsJpgs[-1][0] - t).total_seconds() * self.imagePixelsPerSecond
		else:
			return self.imageWidth/2 + (t - self.tsJpgs[0][0]).total_seconds() * self.imagePixelsPerSecond
			
	def tFromX( self, x ):
		x /= self.imageToScreenFactor	# Convert from screen to image coordinates.
		if self.leftToRight:
			return self.tsJpgs[-1][0] - timedelta( seconds=( (x - self.imageWidth/2) / self.imagePixelsPerSecond ) )
		else:
			return self.tsJpgs[0][0] + timedelta( seconds=( (x - self.imageWidth/2) / self.imagePixelsPerSecond ) )

	def makeComposite( self ):
		'''
			Make a composite bitmap in screen height coordinates.
		'''
		width, height = self.GetSize()
		f = self.imageToScreenFactor
		self.compositeBitmap = wx.Bitmap( round(self.compositeVBitmapWidth * f)+1, height )
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
		xFromT = self.xFromT

		first = True
		if self.leftToRight:
			for ts, jpg in reversed( self.tsJpgs ):
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
					
				x, w = xFromT( ts ), widthDiv2
				
				copyImage( sourceDC,
					self.imageWidth - w, 0, w, self.imageHeight,
					x, 0,
				)
				sourceDC.SelectObject(wx.NullBitmap)
		else:
			for ts, jpg in reversed( self.tsJpgs ):
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

				x, w = xFromT( ts ), widthDiv2
				
				copyImage( sourceDC,
					0, 0, self.imageWidth, self.imageHeight,
					x - widthDiv2, 0,
				)
				sourceDC.SelectObject(wx.NullBitmap)

	def OnPaint( self, event ):
		if not self.compositeBitmap:
			return
		
		dc = wx.PaintDC( self )
		sourceDC = wx.MemoryDC( self.compositeBitmap )

		width, height = self.GetSize()
		dc.Blit( 0, 0, width, height, sourceDC, round(self.xLeft * self.imageToScreenFactor), 0 )

def getPixelsPerSecond( frameWidthPixels=1920, finishWidthM=8, cameraDistanceFromEdgeM=1, lensAngle=84, speedKMH=50 ):
	'''
		Calculate pixels per second given:
		
			frameWidthPixels:			width of photo image (pixels)
			finishWidthM:				width of finish (m)
			cameraDistanceFromEdgeM:	distance from edge of road (m)
			lensAngle:					angle of webcam lens
			speedKMH:					speed of passing object (kmh)
	'''
	speedMPS = speedKMH / 3.6
	
	finishCenterM = finishWidthM/2.0 + cameraDistanceFromEdgeM
	viewLengthM = 2.0 * finishCenterM * tan( radians(lensAngle/2.0) )
	
	viewS = viewLengthM / speedMPS
	pixelsPerSecond = frameWidthPixels / viewS
	
	return pixelsPerSecond

class CompositePanel( wx.Panel):
	def __init__( self, parent ):
		super().__init__( parent )
		vs = wx.BoxSizer( wx.VERTICAL )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.composite = CompositeCtrl( self )
		hs.Add( self.composite, 1, flag=wx.EXPAND )
		self.speedScrollBar = wx.ScrollBar( self, style=wx.SB_VERTICAL )
		self.speedScrollBar.Bind( wx.EVT_SCROLL, self.onScrollSpeed )
		speedMax = 100
		thumbSize = 10
		self.speedScrollBar.SetScrollbar( 50, thumbSize, speedMax, thumbSize )
		hs.Add( self.speedScrollBar, flag=wx.EXPAND )
		
		vs.Add( hs, 1, flag=wx.EXPAND )
		
		self.timeScrollBar = wx.ScrollBar( self, style=wx.SB_HORIZONTAL )
		self.timeScrollBar.Bind( wx.EVT_SCROLL, self.onScrollTime )
		vs.Add( self.timeScrollBar, 0, flag=wx.EXPAND )
		self.SetSizer(vs)
		
	def onScrollTime( self, event ):
		self.composite.SetXLeft( event.GetPosition() )
	
	def fixTimeScollbar( self, position=0 ):
		width, height = self.GetSize()
		widthComposite = self.composite.compositeVBitmapWidth
		thumbSize = round(width * width/widthComposite)
		self.timeScrollBar.SetScrollbar( position, thumbSize, widthComposite - self.composite.imageWidth*2, thumbSize )
	
	def onScrollSpeed( self, event ):
		if self.composite.tsJpgs:
			self.composite.setPixelsPerSecond( getPixelsPerSecond(
					frameWidthPixels=self.composite.imageWidth,
					speedKMH=self.speedScrollBar.GetThumbPosition()
				)
			)
			self.fixTimeScollbar( self.timeScrollBar.GetThumbPosition() )
		
	def set( self, *args, **kwargs ):
		self.composite.set( *args, **kwargs )
		self.fixTimeScollbar()

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
	
	cp.set( tsJpgs, pixelsPerSecond, leftToRight=leftToRight )
	mainWin.Show()
	
	app.MainLoop()

