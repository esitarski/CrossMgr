import wx
import cv2

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
	
def frameToJPeg( frame ):
	return cv2.imencode('.jpg', frame)[1].tostring()

if __name__ == '__main__':
	print rescaleToRect( 200, 100, 100, 50 )
	print rescaleToRect( 1080, 800, 640, 480 )