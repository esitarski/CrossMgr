import os
import wx
import cStringIO as StringIO
import Utils
from GetPhotoFName import GetPhotoFName

def PhotoRenamer( qRenamer, qMessage, qFTP ):
	keepGoing = True
	while keepGoing:
		message = qRenamer.get()
		
		for i in xrange(2):
			fnameOld = GetPhotoFName( message['dirName'], 0, message.get('raceSeconds',None), i )
			fname = GetPhotoFName( message['dirName'], message.get('bib',None), message.get('raceSeconds',None), i )
			
			try:
				os.rename( fnameOld, fname )
			except Exception as e:
				qMessage.put( ('rename', 'file rename failed: "{}"'.format(os.path.basename(fname))) )
				continue
			
			try:
				image = wx.Image.LoadFile( fname, wx.BITMAP_TYPE_JPEG )
			except Exception as e:
				qMessage.put( ('rename', 'cannot load : "{}"'.format(os.path.basename(fname))) )
				continue
				
			image = AddPhotoHeader(
				image,
				message.get('bib', None),
				message.get('time', None),
				message.get('raceSeconds', None),
				message.get('firstName',u''),
				message.get('lastName',u''),
				message.get('team',u''),
				message.get('raceName',u'')
			)
			
			buf = StringIO.StringIO()
			image.SaveStream( wx.OutputStream(buf), wx.BITMAP_TYPE_JPEG )
			try:
				with open(fname, 'wb') as f:
					f.write( buf.getvalue() )
				qMessage.put( ('updated', '"{}"'.format(os.path.basename(fname))) )
			except Exception as e:
				qMessage.put( ('rename save failure', '"{}": {}'.format(os.path.basename(fname), e) ) )
				continue
				
			if 'ftpInfo' in message:
				qFTP.put( ('save', fname, message['ftpInfo']) )
	
		qRenamer.task_done()
