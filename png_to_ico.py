import os
import sys
from PIL import Image

def fname_ico_from_png( pngfile ):
	return os.path.splitext(pngfile)[0] + '.ico'

def png_to_ico( pngfile, icofile=None ):
	img = Image.open( pngfile )
	if icofile is None:
		icofile = fname_ico_from_png( pngfile )
	img.save( icofile, format='ICO' )
	
if __name__ == '__main__':
	import argparse
	
	parser = argparse.ArgumentParser(
		description="Convert a png file into a ico file",
	)
	parser.add_argument( 'imagefile' )
	parser.add_argument( '-f', '--force', action='store_true' )
	
	args = parser.parse_args()
	if not os.path.isfile( args.imagefile ):
		print( f'File: "{args.imagefile}" not found.' )
		sys.exit( -1 )
	if os.path.splitext( args.imagefile )[1] != '.png':
		print( f'File: "{args.imagefile}" must be a png file.' )
		sys.exit( -1 )
	
	icofile = fname_ico_from_png( args.imagefile )
	if not args.force and os.path.isfile(icofile):
		print( f'File: "{icofile}" exists.  To replace it, use the -f option.' )
		sys.exit( -1 )
		
	png_to_ico( args.imagefile, icofile )
