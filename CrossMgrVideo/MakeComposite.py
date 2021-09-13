from datetime import datetime, timedelta
import cv2
import numpy as np
from CVUtil import frameToBitmap, jpegToFrame

def MakeComposite( tsJpgs, leftToRight, pixelsPerSec, scale, highQuality=False ):
	if not tsJpgs:
		return None, None, None
	
	# Create a composite at full size, then rescale at the end.
	tsFirst = tsJpgs[0][0]
	times = [(ts - tsFirst).total_seconds() for ts, jpg in tsJpgs]
	imgCur = jpegToFrame(tsJpgs[0][1])
	heightPhoto, widthPhoto, layers = imgCur.shape
	
	if len(tsJpgs) == 1:
		imgComposite = cv2.resize(
			imgCur, (0,0), fx=scale, fy=scale,
			interpolation=cv2.INTER_AREA if highQuality else cv2.INTER_LINEAR
		)
		return widthPhoto, heightPhoto, frameToBitmap(imgComposite)

	'''
	if False and len(tsJpgs) == 2:
		imgComposite = np.full((heightPhoto,widthPhoto*2,3), 0xd3, np.uint8)
		if leftToRight:
			for i in range(2):
				xLeft = i*widthPhoto
				imgComposite[:,xLeft:xLeft+widthPhoto] = imgCur
				try:
					imgCur = jpegToFrame(tsJpgs[i+1][1])
				except IndexError:
					break
		else:
			for i in range(2):
				xRight = (2-i)*widthPhoto
				imgComposite[:,xRight-widthPhoto:xRight] = imgCur
				try:
					imgCur = jpegToFrame(tsJpgs[i+1][1])
				except IndexError:
					break
		
		if scale != 1.0:
			imgComposite = cv2.resize(
				imgComposite, (0,0), fx=scale, fy=scale,
				interpolation=cv2.INTER_AREA if highQuality else cv2.INTER_LINEAR
			)
		return widthPhoto, heightPhoto, frameToBitmap(imgComposite)
	'''
	
	widthPhotoHalf = widthPhoto // 2
	extraSlice = int((times[1] - times[0]) if leftToRight else (times[-1] - times[-2]))
	widthComposite = int((times[-1] + extraSlice) * pixelsPerSec) + 1

	imgComposite = np.full((heightPhoto,widthComposite,3), 0xd3, np.uint8)
	
	if leftToRight:
		xLeftLast = widthComposite
		for i, t in enumerate(times):
			xLeft = widthComposite - extraSlice - int(t * pixelsPerSec)
			dx = min( xLeftLast - xLeft, widthPhotoHalf )
			imgComposite[:,xLeft:xLeft+dx] = imgCur[:,widthPhotoHalf:widthPhotoHalf+dx]
			try:
				imgCur = jpegToFrame(tsJpgs[i+1][1])
			except IndexError:
				break
			xLeftLast = xLeft
	else:
		xRightLast = 0
		for i, t in enumerate(times):
			xRight = extraSlice + int(t * pixelsPerSec)
			dx = min( xRight - xRightLast, widthPhotoHalf )
			imgComposite[:,xRight-dx:xRight] = imgCur[:,widthPhotoHalf-dx:widthPhotoHalf]
			try:
				imgCur = jpegToFrame(tsJpgs[i+1][1])
			except IndexError:
				break
			xRightLast = xRight
	
	# Rescale the composite once at the end.
	if scale != 1.0:
		imgComposite = cv2.resize(
			imgComposite, (0,0), fx=scale, fy=scale,
			interpolation=cv2.INTER_AREA if highQuality else cv2.INTER_LINEAR
		)
	return widthPhoto, heightPhoto, frameToBitmap(imgComposite)
#---------------------------------------------------------------------------------
'''

import wx
from datetime import datetime, timedelta
from PIL import Image
import cStringIO as StringIO

def MakeComposite( tsJpgs, leftToRight, pixelsPerSec, scale, highQuality=False ):
	if len(tsJpgs) < 2:
		return None, None, None

	# Create a composite at full size, then rescale at the end.
	tsFirst = tsJpgs[0][0]
	times = [(ts - tsFirst).total_seconds() for ts, jpg in tsJpgs]
	imgCur = Image.open( StringIO.StringIO(tsJpgs[0][1]) )
	widthPhoto, heightPhoto = imgCur.size
	widthPhotoHalf = widthPhoto // 2
	
	extraSlice = int((times[1] - times[0]) if leftToRight else (times[-1] - times[-2]))
	widthComposite = int((times[-1] + extraSlice)* pixelsPerSec) + 1

	imgComposite = Image.new( "RGB", (widthComposite, heightPhoto), '#d3d3d3' )
	
	if leftToRight:
		xLeftLast = widthComposite
		for i, t in enumerate(times):
			xLeft = widthComposite - extraSlice - int(t * pixelsPerSec)
			dx = min( xLeftLast - xLeft, widthPhotoHalf )
			imgSlice = imgCur.crop( (widthPhotoHalf, 0, widthPhotoHalf+dx, heightPhoto) )
			imgComposite.paste( imgSlice, (xLeft, 0) )
			try:
				imgCur = Image.open( StringIO.StringIO(tsJpgs[i+1][1]) )
			except IndexError:
				break
			xLeftLast = xLeft
	else:
		xRightLast = 0
		for i, t in enumerate(times):
			xRight = extraSlice + int(t * pixelsPerSec)
			dx = min( xRight - xRightLast, widthPhotoHalf )
			imgSlice = imgCur.crop( (widthPhotoHalf-dx, 0, widthPhotoHalf, heightPhoto) )
			imgComposite.paste( imgSlice, (xRight-dx, 0) )
			try:
				imgCur = Image.open( StringIO.StringIO(tsJpgs[i+1][1]) )
			except IndexError:
				break
			xRightLast = xRight
	
	# Rescale the composite once at the end.
	if scale != 1.0:
		width, height = imgComposite.size
		imgComposite = imgComposite.resize(
			(int(width*scale), int(height*scale)),
			Image.ANTIALIAS if highQuality else Image.BILINEAR
		)
	width, height = imgComposite.size
	return widthPhoto, heightPhoto, wx.Bitmap.FromBuffer(width, height, imgComposite.convert("RGB").tobytes())

#------------------------------------------------------------------------------------------------------------

import wx
from datetime import datetime, timedelta
import cStringIO as StringIO

def MakeComposite( tsJpgs, leftToRight, pixelsPerSec, scale, highQuality=False ):
	if len(tsJpgs) < 2:
		return None, None, None

	# Create a composite at full size, then rescale at the end.
	tsFirst = tsJpgs[0][0]
	times = [(ts - tsFirst).total_seconds() for ts, jpg in tsJpgs]
	bmpCur = wx.Image( StringIO.StringIO(tsJpgs[0][1]), wx.BITMAP_TYPE_JPEG ).ConvertToBitmap()
	widthPhoto, heightPhoto = bmpCur.GetWidth(), bmpCur.GetHeight()
	widthPhotoHalf = widthPhoto // 2
	
	extraSlice = int((times[1] - times[0]) if leftToRight else (times[-1] - times[-2]))
	widthComposite = int((times[-1] + extraSlice)* pixelsPerSec) + 1

	widthCompositeScale = int(widthComposite * scale)
	heightCompositeScale = int(widthPhoto * scale)
	bmpComposite = wx.Bitmap( widthCompositeScale, heightCompositeScale )
	
	dcDest = wx.MemoryDC( bmpComposite )
	dcDest.SetBackground( wx.Brush(wx.Colour(0xd3, 0xd3, 0xd3), wx.SOLID))
	dcDest.Clear()
	
	dcSrc = wx.MemoryDC()
	
	if leftToRight:
		xLeftLast = widthComposite
		for i, t in enumerate(times):
			xLeft = widthComposite - extraSlice - int(t * pixelsPerSec)
			dx = min( xLeftLast - xLeft, widthPhotoHalf )
			dcSrc.SelectObject( bmpCur )
			# imgComposite[:,xLeft:xLeft+dx] = imgCur[:,widthPhotoHalf:widthPhotoHalf+dx]
			dcDest.StretchBlit(
				int(xLeft*scale), 0, int(dx*scale), heightCompositeScale,
				dcSrc,
				widthPhotoHalf, 0, dx, heightPhoto
			)
			dcSrc.SelectObject( wx.NullBitmap )
			try:
				bmpCur = wx.Image( StringIO.StringIO(tsJpgs[i+1][1]), wx.BITMAP_TYPE_JPEG ).ConvertToBitmap()
			except IndexError:
				break
			xLeftLast = xLeft
	else:
		xRightLast = 0
		for i, t in enumerate(times):
			xRight = extraSlice + int(t * pixelsPerSec)
			dx = min( xRight - xRightLast, widthPhotoHalf )
			bmpSlice = bmpCur.crop( (widthPhotoHalf-dx, 0, widthPhotoHalf, heightPhoto) )
			dcSrc.SelectObject( bmpCur )
			# imgComposite[:,xRight-dx:xRight] = imgCur[:,widthPhotoHalf-dx:widthPhotoHalf]
			dcSrc.SelectObject( wx.NullBitmap )
			dcDest.StretchBlit(
				int((xRight-dx)*scale), 0, int(dx*scale), heightCompositeScale,
				dcSrc,
				widthPhotoHalf-dx, 0, dx, heightPhoto
			)
			try:
				bmpCur = wx.Image( StringIO.StringIO(tsJpgs[i+1][1]), wx.BITMAP_TYPE_JPEG ).ConvertToBitmap()
			except IndexError:
				break
			xRightLast = xRight
	
	return widthPhoto, heightPhoto, bmpComposite

'''
