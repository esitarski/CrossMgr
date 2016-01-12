import os
import wx
import StringIO
import Utils
import base64
import json

srcPrefix = bytes("data:image/png;base64,")

def toBufFromImage( image ):
	stream = StringIO.StringIO()
	image.SaveStream( stream, wx.BITMAP_TYPE_PNG )
	return srcPrefix + base64.b64encode(stream.getvalue())

def toBufFromBitmap( bitmap ):
	return toBufFromImage( wx.ImageFromBitmap(bitmap) )

def toBufFromFile( fname, type=wx.BITMAP_TYPE_ANY ):
	return toBufFromImage( wx.Image(fname, type) )

def toImageFromBuf( buf ):
	return wx.ImageFromStream( StringIO.StringIO(base64.b64decode(buf[len(srcPrefix):])), wx.BITMAP_TYPE_PNG )

def toBitmapFromBuf( buf ):
	return wx.BitmapFromImage( toImageFromBuf(buf) )

if __name__ == '__main__':
	app = wx.App(False)
	image = wx.Image( os.path.join(Utils.getImageFolder(), 'CrossMgr.png'), wx.BITMAP_TYPE_PNG )
	buf1 = toBufFromImage( image )
	buf2 = toBufFromImage( toImageFromBuf(buf1) )
	buf3 = toBufFromFile( os.path.join(Utils.getImageFolder(), 'CrossMgr.png'), wx.BITMAP_TYPE_PNG )
	assert buf1 == buf2
	assert buf2 == buf3
	print len(buf1), len(buf2), len(buf3)
	print json.dumps( buf1 )
	img = toImageFromBuf( buf1 )
	bmp = toBitmapFromBuf( buf2 )
