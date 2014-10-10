import os
import wx
import cStringIO as StringIO

def PhotoWriter( qWriter, qMessage, qFTP ):
	keepGoing = True
	while keepGoing:
		message = qWriter.get()
		if message[0] == 'save':
			success = False
			cmd, fname, image = message[:3]
			buf = StringIO.StringIO()
			image.SaveStream( wx.OutputStream(buf), wx.BITMAP_TYPE_JPEG )
			
			try:
				with open(fname, 'wb') as f:
					f.write( buf.getvalue() )
				qMessage.put( ('saved', '"{}"'.format(os.path.basename(fname))) )
				success = True
			
			except Exception as e:
				if not os.path.exists( os.path.dirname(fname) ):
					try:
						os.mkdir( os.path.dirname(fname) )
						with open(fname, 'wb') as f:
							f.write( buf.getvalue() )
						qMessage.put( ('mkdir', '"{}"'.format(os.path.dirname(fname))) )
						qMessage.put( ('saved', '"{}"'.format(os.path.basename(fname))) )
						success = True
					except Exception as e:
						qMessage.put( ('save failure', '"{}": {}'.format(os.path.basename(fname), e) ) )
		
			if success and len(message) > 3:
				ftpInfo = message[3]
				qFTP.put( ('save', fname, ftpInfo) )
				
		elif message[0] == 'terminate':
			keepGoing = False
		
		qWriter.task_done()
