#!/usr/bin/env python

import os
import sys
import shutil

def NeedsUpdating( srcFName, destFName ):
	try:
		srcStat = os.stat( srcFName )
		destStat = os.stat( destFName )
	except Exception:
		return True
	
	return srcStat.st_mtime > destStat.st_mtime or srcStat.st_size != destStat.st_size

def CopyMedia( src='.', dest=None ):
	extensions = set( ['.py', '.html', '.gif', '.png', '.iss', '.txt'] )
	
	if dest is None:
		try:
			media = os.listdir( '/media' )
			assert len(media) == 1, 'Missing, or more than one media'
			dest = os.path.join( '/media', media[0], os.path.basename(os.path.abspath(src)) )
		except Exception as e:
			print ( e )
			sys.exit( -1 )
	
	for path, dirs, files in os.walk(src):
		for d in dirs:
			srcDName = os.path.join(path, d)
			destDName = os.path.join( dest, srcDName[len(src)+1:] )
			if not os.path.isdir(destDName):
				os.makedirs( destDName )
		
		for f in files:
			if os.path.splitext(f)[1].lower() in extensions:
				srcFName = os.path.join(path, f)
				destFName = os.path.join( dest, srcFName[len(src)+1:] )
				if NeedsUpdating( srcFName, destFName ):
					print ( srcFName, destFName )
					try:
						shutil.copy( srcFName, destFName )
					except Exception as e:
						print ( e )

if __name__ == '__main__':
	CopyMedia()
