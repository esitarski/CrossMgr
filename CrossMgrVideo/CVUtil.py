import wx
import io
import cv2
import numpy as np
import simplejpeg
from LRUCache import LRUCache

jpegFramesCache = LRUCache( 20*30 )		# For performance, cache the last few seconds of jpegs to frame conversions.
def resetCache():
	jpegFramesCache.clear()

def rescaleToRect( w_src, h_src, w_dest, h_dest ):
	scale = min( float(w_dest)/float(w_src), float(h_dest)/float(w_src) )
	return int(w_src * scale), int(h_src * scale)

def frameToWidthHeight( frame ):
	return frame.shape[:2][::-1]
	
def getWidthHeight( o ):
	if isinstance(o, (wx.Image, wx.Bitmap)):
		return o.GetWidth(), o.GetHeight()
	if isinstance(o, np.ndarray):
		if o.shape[0] != 1:
			return frameToWidthHeight( o )
		return frameToWidthHeight( jpegToFrame(o.tobytes()) )	# Assume single-dimension np is encoded as jpeg.
	if isinstance(o, bytes):			# Assume a jpg.
		return frameToWidthHeight( jpegToFrame(o) )
	raise TypeError( 'Unknown object type' )

def isJpegBuf( buf ):
	return isinstance(buf, bytes) and buf[:2] == b'\xff\xd8' and buf[-2:] == b'\xff\xd9'	# Check for jpeg magic values.

def toFrame( o, updateCache=True ):
	'''
		Transform the given object into an opencv numpy frame.
		Specifically, a numpy ndarray of dimension 2 in BGR format.
	'''
	if isinstance(o, np.ndarray):
		if o.shape[0] != 1:
			return o
		try:
			return jpegToFrame( o.tobytes(), updateCache )	# Assume single-dimension np is encoded as jpeg.
		except Exception as e:
			#print( 'Conversion failure.  o.shape=', o.shape )
			return None
	if isJpegBuf( o ):
		return jpegToFrame( o, updateCache )
	if isinstance( o, wx.Bitmap ):
		return bitmapToFrame( o )
	if isinstance( o, wx.Image ):
		return imageToFrame( o )
	if o is None:
		return o
	raise TypeError( 'Unknown object type' )

def toJpeg( o ):
	if isinstance(o, np.ndarray):
		if o.shape[0] == 1:
			b = o.tobytes()
			if isJpegBuf( b ):
				return b
			return None
		if len(o.shape) != 3 or o.shape[2] != 3:	# Check for height, width, and 3 colors.
			return None
		return simplejpeg.encode_jpeg( o, colorspace='BGR' )
	if isinstance(o, bytes) or o is None:
		return o
	raise TypeError( 'Unknown object type' )

def frameToBitmap( frame, w_req=None, h_req=None ):
	h_frame, w_frame = frame.shape[0], frame.shape[1]
	if w_req is not None:
		w_fix, h_fix = rescaleToRect( w_frame, h_frame, w_req, h_req )
		if w_fix != w_req or h_fix != h_req:
			frame = cv2.resize( frame, w_fix, h_fix )
			w_frame, h_frame = w_fix, h_fix
	return wx.Bitmap.FromBuffer(w_frame, h_frame, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

def frameToImage( frame, w_req=None, h_req=None ):
	h_frame, w_frame = frame.shape[0], frame.shape[1]
	if w_req is not None:
		w_fix, h_fix = rescaleToRect( w_frame, h_frame, w_req, h_req )
		if w_fix != w_req or h_fix != h_req:
			frame = cv2.resize( frame, w_fix, h_fix )
			w_frame, h_frame = w_fix, h_fix
	return wx.Image(w_frame, h_frame, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

def resizeFrame( frame, w_req, h_req ):
	h_frame, w_frame = frame.shape[0], frame.shape[1]
	w_fix, h_fix = rescaleToRect( w_frame, h_frame, w_req, h_req )
	if w_fix != w_req or h_fix != h_req:
		frame = cv2.resize( frame, w_fix, h_fix )
	return frame

def frameToJPeg( frame ):
	if frame.shape[0] == 1:		# If this is already encoded, just convert to bytes.
		return frame.tobytes()
	# jpeg = cv2.imencode('.jpg', frame)[1].tobytes()
	jpeg = simplejpeg.encode_jpeg( image=frame, colorspace='BGR' )
	jpegFramesCache[jpeg] = frame
	return jpeg

def jpegToFrame( jpeg, updateCache=True ):
	if jpeg in jpegFramesCache:
		return jpegFramesCache[jpeg]
	# frame = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
	assert isJpegBuf(jpeg), 'Corrupt JPEG data'
	frame = simplejpeg.decode_jpeg( data=jpeg, colorspace='BGR' )
	if updateCache:
		jpegFramesCache[jpeg] = frame
	return frame

def jpegToImage( jpeg ):
	return frameToImage(jpegToFrame(jpeg))
	
def jpegToBitmap( jpeg ):
	return frameToBitmap(jpegToFrame(jpeg))
	
def adjustContrastFrame( frame ):
	frame_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
	# equalize the histogram of the Y channel
	frame_yuv[:,:,0] = cv2.equalizeHist(frame_yuv[:,:,0])
	# convert the YUV image back to BGR format
	return cv2.cvtColor(frame_yuv, cv2.COLOR_YUV2BGR)

def sharpenFrame( frame ):
	return cv2.filter2D(frame,-1,np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]))
	
def grayscaleFrame( frame ):
	return cv2.cvtColor( frame, cv2.COLOR_BGR2GRAY )

def imageToFrame( image ):
	s = io.BytesIO()
	image.SaveFile( s, wx.BITMAP_TYPE_BMP )
	return cv2.imdecode( np.frombuffer(s.getvalue(), dtype='B'), cv2.IMREAD_COLOR )

def bitmapToFrame( bitmap ):
	return imageToFrame( bitmap.ConvertToImage() )
	
def bitmapToJPeg( bitmap ):
	return frameToJPeg(bitmapToFrame(bitmap))
	
def adjustContrastImage( image ):
	return frameToImage( adjustContrastFrame(imageToFrame(image)) )

def adjustContrastBitmap( bitmap ):
	return frameToBitmap( adjustContrastFrame(bitmapToFrame(bitmap)) )

if __name__ == '__main__':
	print ( rescaleToRect( 200, 100, 100, 50 ) )
	print ( rescaleToRect( 1080, 800, 640, 480 ) )
