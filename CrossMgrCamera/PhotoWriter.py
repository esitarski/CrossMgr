import os
import wx
import cStringIO as StringIO

def PhotoWriter( qWriter, qMessage ):
	keepGoing = True
	while keepGoing:
		message = qWriter.get()
		if message[0] == 'save':
			cmd, fname, image = message
			buf = StringIO.StringIO()
			image.SaveStream( wx.OutputStream(buf), wx.BITMAP_TYPE_JPEG )
			try:
				with open(fname, 'wb') as f:
					f.write( buf.getvalue() )
				qMessage.put( ('saved', '"{}"'.format(os.path.basename(fname))) )
			except Exception as e:
				qMessage.put( ('save failure', '"{}": {}'.format(os.path.basename(fname), e) ) )
		elif message[0] == 'terminate':
			keepGoing = False
		
		qWriter.task_done()
