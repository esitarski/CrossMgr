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
	
	if heightPhoto == 0 or widthPhoto == 0:
		return None, None, None,
	
	# if there are 1,2 photos, show them all.
	if len(tsJpgs) <= 2:
		imgComposite = np.full((heightPhoto,widthPhoto*len(tsJpgs),3), 0xd3, np.uint8)
		for i in range(len(tsJpgs)):
			iImg = i if leftToRight else len(tsJpgs)-1-i
			xLeft = i*widthPhoto
			imgComposite[:,xLeft:xLeft+widthPhoto] = imgCur if iImg == 0 else jpegToFrame(tsJpgs[iImg][1])
		
		if scale != 1.0:
			imgComposite = cv2.resize(
				imgComposite, (0,0), fx=scale, fy=scale,
				interpolation=cv2.INTER_AREA if highQuality else cv2.INTER_LINEAR
			)
		return widthPhoto, heightPhoto, frameToBitmap(imgComposite)
	
	# Create a composite image from the photos.
	widthPhotoHalf = widthPhoto // 2
	extraSlice = (times[1] - times[0]) if leftToRight else (times[-1] - times[-2])
	widthComposite = int((times[-1] + extraSlice) * pixelsPerSec) + 1

	imgComposite = np.full((heightPhoto,widthComposite,3), 0xd3, np.uint8)
	
	if leftToRight:
		xLeftLast = widthComposite
		for i, t in enumerate(times):
			xLeft = widthComposite - int((t - extraSlice) * pixelsPerSec)
			dx = min( xLeftLast - xLeft, widthPhotoHalf )
			heightPhoto, widthPhoto, layers = imgCur.shape
			try:
				imgComposite[:,xLeft:xLeft+dx] = imgCur[:,widthPhotoHalf:widthPhotoHalf+dx]
			except ValueError as e:
				pass
			try:
				imgCur = jpegToFrame(tsJpgs[i+1][1])
			except IndexError:
				break
			xLeftLast = xLeft
	else:
		xRightLast = 0
		for i, t in enumerate(times):
			xRight = int((extraSlice + t) * pixelsPerSec)
			dx = min( xRight - xRightLast, widthPhotoHalf )
			try:
				imgComposite[:,xRight-dx:xRight] = imgCur[:,widthPhotoHalf-dx:widthPhotoHalf]
			except ValueError as e:
				pass
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
