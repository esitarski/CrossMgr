import wx
import io
import cv2
import six
import numpy as np
from LRUCache import LRUCache

def rescaleToRect( w_src, h_src, w_dest, h_dest ):
	scale = min( float(w_dest)/float(w_src), float(h_dest)/float(w_src) )
	return int(w_src * scale), int(h_src * scale)

def frameToBitmap( frame, w_req=None, h_req=None ):
	h_frame, w_frame, layers = frame.shape
	if w_req is not None:
		w_fix, h_fix = rescaleToRect( w_frame, h_frame, w_req, h_req )
		if w_fix != w_req or h_fix != h_req:
			frame = cv2.resize( frame, w_fix, h_fix )
			w_frame, h_frame = w_fix, h_fix
	return wx.Bitmap.FromBuffer(w_frame, h_frame, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

def frameToImage( frame, w_req=None, h_req=None ):
	h_frame, w_frame, layers = frame.shape
	if w_req is not None:
		w_fix, h_fix = rescaleToRect( w_frame, h_frame, w_req, h_req )
		if w_fix != w_req or h_fix != h_req:
			frame = cv2.resize( frame, w_fix, h_fix )
			w_frame, h_frame = w_fix, h_fix
	return wx.Image(w_frame, h_frame, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

def resizeFrame( frame, w_req, h_req ):
	h_frame, w_frame, layers = frame.shape
	w_fix, h_fix = rescaleToRect( w_frame, h_frame, w_req, h_req )
	if w_fix != w_req or h_fix != h_req:
		frame = cv2.resize( frame, w_fix, h_fix )
	return frame

jpegFramesCacheMax = 30*60
jpegFramesCache = LRUCache( jpegFramesCacheMax )
def frameToJPeg( frame ):
	jpeg = cv2.imencode('.jpg', frame)[1].tostring()
	jpegFramesCache[bytes(jpeg)] = frame
	return jpeg

def jpegToFrame( jpeg ):
	key = bytes( jpeg )
	if key in jpegFramesCache:
		return jpegFramesCache[key]
	frame = cv2.imdecode(np.frombuffer(jpeg, np.uint8), 1)
	jpegFramesCache[key] = frame
	return frame

def jpegToImage( jpeg ):
	return frameToImage(jpegToFrame(jpeg))
	
def jpegToBitmap( jpeg ):
	return frameToBitmap(jpegToFrame(jpeg))
	
def adjustGammaFrame( frame, gamma=1.0 ):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")

	# apply gamma correction using the lookup table
	return cv2.LUT(frame, table)

def adjustContrastFrame( frame ):
	frame_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
	# equalize the histogram of the Y channel
	frame_yuv[:,:,0] = cv2.equalizeHist(frame_yuv[:,:,0])
	# convert the YUV image back to RGB format
	return cv2.cvtColor(frame_yuv, cv2.COLOR_YUV2BGR)

StringIO = six.StringIO
def imageToFrame( image ):
	if six.PY2:
		s = StringIO()
		image.SaveFile( s, wx.BITMAP_TYPE_BMP )
		return cv2.imdecode( np.fromstring(s.getvalue(), dtype='B'), 1 )
	else:
		s = io.BytesIO()
		image.SaveFile( s, wx.BITMAP_TYPE_BMP )
		return cv2.imdecode( np.fromstring(s.getbuffer(), dtype='B'), 1 )

def bitmapToFrame( bitmap ):
	return imageToFrame( bitmap.ConvertToImage() )
	
def adjustGammaImage( image, gamma=1.0 ):
	return frameToImage( adjustGammaFrame(imageToFrame(image), gamma) )

def adjustContrastImage( image ):
	return frameToImage( adjustContrastFrame(imageToFrame(image)) )

def adjustContrastBitmap( bitmap ):
	return frameToBitmap( adjustContrastFrame(bitmapToFrame(bitmap)) )

if __name__ == '__main__':
	six.print_( rescaleToRect( 200, 100, 100, 50 ) )
	six.print_( rescaleToRect( 1080, 800, 640, 480 ) )
