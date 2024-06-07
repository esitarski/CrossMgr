import os
from io import BytesIO
import sys
import getpass
import datetime
import platform
import piexif
import piexif.helper
import Version
import Utils

zeroth_ifd_common = {
	piexif.ImageIFD.Artist: 			getpass.getuser(),
	piexif.ImageIFD.Software:			Version.AppVerName,
}
try:
	zeroth_ifd_common[piexif.ImageIFD.HostComputer] = platform.uname()[1]
except Exception:
	pass

def AddExifToJpeg( jpeg, ts, comment ):
	zeroth_ifd = zeroth_ifd_common.copy()
	zeroth_ifd[piexif.ImageIFD.DateTime] = datetime.datetime.now().strftime('%Y:%m:%d %H:%M:%S')
	
	exif_ifd = {
		piexif.ExifIFD.DateTimeOriginal:	ts.strftime('%Y:%m:%d %H:%M:%S'),
		piexif.ExifIFD.UserComment:			piexif.helper.UserComment.dump(comment, 'unicode'),
	}
	exif_dict = {"0th":zeroth_ifd, "Exif":exif_ifd,}
	
	output = BytesIO()
	piexif.insert( piexif.dump(exif_dict), jpeg, output )
	return output.getbuffer()

if __name__ == '__main__':
	fname = os.path.join( 'photos', '0001-20190209T094625-Capture.jpg' )
	with open(fname, 'rb', encoding='utf8') as f:
		jpeg = f.read()
	fnameOut = os.path.splitext(fname)[0] + '-exif.jpg'
	with open(fnameOut, 'wb', encoding='utf8') as f:
		f.write( AddExifToJpeg( jpeg, datetime.datetime.now(), 'This is a comment' ) )
