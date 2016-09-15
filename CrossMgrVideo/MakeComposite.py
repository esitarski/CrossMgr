from datetime import datetime, timedelta
from PIL import Image
import cStringIO as StringIO

def MakeComposite( tsJpgs, leftToRight, pixelsPerSec, scale ):
	if not tsJpgs:
		return None, None, None

	tsFirst = tsJpgs[0][0]
	times = [(ts - tsFirst).total_seconds() for ts, jpg in tsJpgs]
	imgCur = Image.open( StringIO.StringIO(tsJpgs[0][1]) )
	widthPhoto, heightPhoto = imgCur.size
	
	widthComposite = int(times[-1] * pixelsPerSec + widthPhoto) + 1

	imgComposite = Image.new( "RGB", (widthComposite, heightPhoto), '#d3d3d3' )
	
	if leftToRight:
		xLeftLast = widthComposite
		for i, t in enumerate(times):
			xLeft = widthComposite - widthPhoto - int(t * pixelsPerSec)
			dx = min( xLeftLast - xLeft, widthPhoto )
			imgSlice = imgCur.crop( (0, 0, dx, heightPhoto) )
			imgComposite.paste( imgSlice, (xLeft, 0) )
			try:
				imgCur = Image.open( StringIO.StringIO(tsJpgs[i+1][1] ) )
			except IndexError:
				break
			xLeftLast = xLeft
	else:
		xRightLast = 0
		for i, t in enumerate(times):
			xRight = widthPhoto + int(t * pixelsPerSec)
			dx = min( xRight - xRightLast, widthPhoto )
			imgSlice = imgCur.crop( (widthPhoto-dx, 0, widthPhoto, heightPhoto) )
			imgComposite.paste( imgSlice, (xRight-dx, 0) )
			try:
				imgCur = Image.open( StringIO.StringIO(tsJpgs[i+1][1] ) )
			except IndexError:
				break
			xRightLast = xRight
			
	if scale != 1.0:
		width, height = imgComposite.size
		imgComposite = imgComposite.resize( (int(width*scale), int(height*scale)), Image.ANTIALIAS )
	return widthPhoto, heightPhoto, imgComposite
