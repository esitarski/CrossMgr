from wx import BITMAP_TYPE_JPEG
import os
import io as StringIO

def PhotoWriter( qWriter, qMessage, qFTP ):
	keepGoing = True
	while keepGoing:
		message = qWriter.get()
		
		if message[0] == 'save':
			cmd, fname, image = message[:3]
			success, e = False, None
			for i in xrange(2):
				try:
					with open(fname, 'wb') as f:
						image.SaveFile( f, BITMAP_TYPE_JPEG )
					success = True
					break
				
				except Exception as e:
					pass
					
				# Check if the directory is missing and create it.
				if not os.path.exists( os.path.dirname(fname) ):
					try:
						os.mkdir( os.path.dirname(fname) )
					except Exception as e:
						break
				else:
					break
				
				success, e = False, None
		
			if success:
				qMessage.put( ('saved', '"{}"'.format(os.path.basename(fname))) )
				if len(message) > 3:
					ftpInfo = message[3]
					qFTP.put( ('save', fname, ftpInfo) )
			else:
				qMessage.put( ('save failure', '"{}": {}'.format(os.path.dirname(fname), e) ) )
				
		elif message[0] == 'terminate':
			keepGoing = False
		
		qWriter.task_done()
