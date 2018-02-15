'''
from datetime import datetime, timedelta
import cv2
import numpy as np
from CVUtil import frameToBitmap

def MakeComposite( tsJpgs, leftToRight, pixelsPerSec, scale, highQuality=False ):
	if len(tsJpgs) < 2:
		return None, None, None

	# Create a composite at full size, then rescale at the end.
	tsFirst = tsJpgs[0][0]
	times = [(ts - tsFirst).total_seconds() for ts, jpg in tsJpgs]
	imgCur = cv2.imdecode(np.frombuffer(tsJpgs[0][1], np.uint8), 1)
	heightPhoto, widthPhoto, layers = imgCur.shape
	widthPhotoHalf = widthPhoto // 2
	
	extraSlice = int((times[1] - times[0]) if leftToRight else (times[-1] - times[-2]))
	widthComposite = int((times[-1] + extraSlice)* pixelsPerSec) + 1

	imgComposite = np.full((heightPhoto,widthComposite,3), 0xd3, np.uint8)
	
	if leftToRight:
		xLeftLast = widthComposite
		for i, t in enumerate(times):
			xLeft = widthComposite - extraSlice - int(t * pixelsPerSec)
			dx = min( xLeftLast - xLeft, widthPhotoHalf )
			imgComposite[:,xLeft:xLeft+dx] = imgCur[:,widthPhotoHalf:widthPhotoHalf+dx]
			try:
				imgCur = cv2.imdecode(np.frombuffer(tsJpgs[i+1][1], np.uint8), 1)
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
				imgCur = cv2.imdecode(np.frombuffer(tsJpgs[i+1][1], np.uint8), 1)
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
