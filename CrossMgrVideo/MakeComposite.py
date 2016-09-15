from datetime import datetime, timedelta
from PIL import Image
import cStringIO as StringIO

def scaledImageFromJpg( jpg, scale ):
	image = Image.open( StringIO.StringIO(jpg) )
	if scale != 1.0:
		width, height = image.size
		image = image.resize( (int(width*scale), int(height*scale)), Image.ANTIALIAS )
	return image
	
def MakeComposite( tsJpgs, leftToRight, pixelsPerSec, scale ):
	if not tsJpgs:
		return None, None, None

	tsFirst = tsJpgs[0][0]
	times = [(ts - tsFirst).total_seconds() for ts, jpg in tsJpgs]
	imgCur = scaledImageFromJpg(tsJpgs[0][1], scale)
	widthPhoto, heightPhoto = imgCur.size
	
	scaledPixelsPerSec = pixelsPerSec * scale
	widthComposite = int(times[-1] * scaledPixelsPerSec + widthPhoto) + 1

	imgComposite = Image.new( "RGB", (widthComposite, heightPhoto), '#d3d3d3' )
	
	if leftToRight:
		xLeftLast = widthComposite
		for i, t in enumerate(times):
			xLeft = widthComposite - widthPhoto - int(t * scaledPixelsPerSec)
			dx = min( xLeftLast - xLeft, widthPhoto )
			imgSlice = imgCur.crop( (0, 0, dx, heightPhoto) )
			imgComposite.paste( imgSlice, (xLeft, 0) )
			try:
				imgCur = scaledImageFromJpg(tsJpgs[i+1][1], scale)
			except IndexError:
				break
			xLeftLast = xLeft
	else:
		xRightLast = 0
		for i, t in enumerate(times):
			xRight = widthPhoto + int(t * scaledPixelsPerSec)
			dx = min( xRight - xRightLast, widthPhoto )
			imgSlice = imgCur.crop( (widthPhoto-dx, 0, widthPhoto, heightPhoto) )
			imgComposite.paste( imgSlice, (xRight-dx, 0) )
			try:
				imgCur = scaledImageFromJpg(tsJpgs[i+1][1], scale)
			except IndexError:
				break
			xRightLast = xRight
			
	return widthPhoto, heightPhoto, imgComposite
