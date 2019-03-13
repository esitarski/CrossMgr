import os
import wx
import six
import Utils
import base64

srcPrefix = "data:image/png;base64,"

try:
	# Python 2
	import cStringIO as StringIO
	def toBufFromImage( image ):
		ss = StringIO.StringIO()
		image.SaveFile( ss, wx.BITMAP_TYPE_PNG )
		return srcPrefix + base64.b64encode(ss.getvalue())
	
	def toImageFromBuf( buf ):
		return wx.Image( StringIO.StringIO(base64.b64decode(buf[len(srcPrefix):])), wx.BITMAP_TYPE_PNG )

except:
	# Python 3
	from io import BytesIO
	def toBufFromImage( image ):
		ss = BytesIO()
		image.SaveFile( ss, wx.BITMAP_TYPE_PNG )
		return srcPrefix + base64.b64encode(ss.getbuffer()).decode()
	
	def toImageFromBuf( buf ):
		return wx.Image( BytesIO(base64.b64decode(buf[len(srcPrefix):])), wx.BITMAP_TYPE_PNG )

def toBufFromBitmap( bitmap ):
	return toBufFromImage( wx.Image(bitmap) )

def toBufFromFile( fname, type=wx.BITMAP_TYPE_ANY ):
	return toBufFromImage( wx.Image(fname, type) )

def toBitmapFromBuf( buf ):
	return wx.Bitmap( toImageFromBuf(buf) )

if __name__ == '__main__':
	app = wx.App(False)
	image = wx.Image( os.path.join(Utils.getImageFolder(), 'CrossMgr.png'), wx.BITMAP_TYPE_PNG )
	buf1 = toBufFromImage( image )
	buf2 = toBufFromImage( toImageFromBuf(buf1) )
	buf3 = toBufFromFile( os.path.join(Utils.getImageFolder(), 'CrossMgr.png'), wx.BITMAP_TYPE_PNG )
	assert buf1 == buf2
	assert buf2 == buf3
	six.print_( len(buf1), len(buf2), len(buf3) )
	six.print_( Utils.ToJson(buf1) )
	img = toImageFromBuf( buf1 )
	bmp = toBitmapFromBuf( buf2 )
