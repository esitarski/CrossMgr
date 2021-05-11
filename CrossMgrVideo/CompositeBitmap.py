import wx
import io
from Database import GlobalDatabase
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
import io
StringIO = io.StringIO

def scaledBitmapfromJpg( jpg, scale ):
	image = wx.Image( StringIO(jpg) if six.PY2 else io.BytesIO(jpg) )
	width, height = image.size
	if self.scale != 1.0:
		image = image.resize( (int(width*scale), int(height*scale)), Image.ANTIALIAS )
	return image
	
def CompositeBitmap( qResult, fnameDB, tsLower, tsUpper, pixelsPerSec, scale ):
	tsJpgs = GlobalDatabase( fnameDB ).getPhotos( tsLower, tsUpper )
	if not tsJpgs:
		qResult.put( ('composite', None) )
		return
	
	tsFirst = tsJpgs[0][0]
	times = [(ts - tsFirst).total_seconds() for ts, jpg in tsJpgs]
	tJpg = {t:jpg for t, (ts, jpg) in zip(times, tsJpgs)}
	scaledBitmaps = {}
	def getScaledBitmap( t ):
		if t not in scaledBitmaps:
			scaledBitmaps[t] = scaledBitmapFromJpg(tJpg[t], scale)
		return scaledBitmaps[t]
	widthPhoto, heightPhoto = getScaledBitmap[times[0]].size
	
	scaledPixelsPerSec = pixelsPerSec * scale
	tMin, tMax = times[0], times[-1]
	widthComposite = (tMax-tMin) * scaledPixelsPerSec + widthPhoto

	composite = Image.new( "RGB", (widthComposite, heightPhoto), '#d3d3d3' )
	
	if self.leftToRight:
		xLeft = [int((t-tMin) * scaledPixelsPerSec) for t, bm in timeBitmaps]
		xLeft.append( widthComposite )
		for i, (t, bm) in enumerate(timeBitmaps):
			
			bitmapDC.SelectObject( bm )
			dc.Blit(
				xLeft[i], 0, xLeft[i+1] - xLeft[i], heightPhoto,
				bitmapDC,
				0, 0,
			)
			bitmapDC.SelectObject( wx.NullBitmap )
	else:
		xLeft = [int(widthComposite - widthPhoto - (t - tMin) * self.scaledPixelsPerSec) for t, bm in timeBitmaps]
		xLeft.append( -widthPhoto )
		for i, (t, bm) in enumerate(timeBitmaps):
			bitmapDC.SelectObject( bm )
			dx = xLeft[i] - xLeft[i+1]
			dc.Blit(
				xLeft[i] + widthPhoto - dx, 0, dx, heightPhoto,
				bitmapDC,
				widthPhoto - dx, 0,
			)
			bitmapDC.SelectObject( wx.NullBitmap )
	
	dc.SelectObject( wx.NullBitmap )
	self.compositeBM = bm
	return bm
