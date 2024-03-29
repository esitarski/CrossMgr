from Database import GlobalDatabase
from queue import Empty

from MakeComposite import MakeComposite

def CompositeImage( qRequest, qReply ):
	
	while True:
		message = qRequest.get()
		
		# Skip all but the last message in case we fall behind.
		while True:
			if message[0] == 'terminate':
				return
			try:
				message = qRequest.get( False )
			except Empty:
				break
		
		fnameDB, tsLower, tsUpper, leftToRight, pixelsPerSec, scale = message[1:]
		tsJpgs = GlobalDatabase(fnameDB).getPhotos(tsLower, tsUpper)
		if not tsJpgs:
			qReply.put( ('composite', None, None, None) )
			continue

		qReply.put( ['composite'] + MakeComposite(tsJpgs, leftToRight, pixelsPerSec, scale) )
