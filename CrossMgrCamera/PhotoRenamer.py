import os
import wx
import cStringIO as StringIO
import Utils
from GetPhotoFName import GetPhotoFName
from AddPhotoHeader import AddPhotoHeader
from SaveImage import SaveImage

def doRename( fname, message, qMessage, qWriter ):
	# This has to be its own function as we have to make the wx.ImageFromStream call on the main thread.
	try:
		with open(fname, 'rb') as f:
			image = wx.ImageFromStream( f, wx.BITMAP_TYPE_JPEG )
	except Exception as e:
		qMessage.put( ('rename', 'cannot load : "{}": {}'.format(os.path.basename(fname), e)) )
		return
		
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
	
	qMessage.put( ('renamed', '"{}"'.format(os.path.basename(fname)) ) )
	SaveImage( fname, image, message.get('ftpInfo', None), qMessage, qWriter )

def PhotoRenamer( qRenamer, qWriter, qMessage ):
	keepGoing = True
	while keepGoing:
		message = qRenamer.get()
		
		for i in xrange(2):
			fnameOld = GetPhotoFName( message['dirName'], 0, message.get('raceSeconds',None), i )
			fname = GetPhotoFName( message['dirName'], message.get('bib',None), message.get('raceSeconds',None), i )
			
			try:
				os.rename( fnameOld, fname )
			except Exception as e:
				wx.CallAfter( qMessage.put, ('failed rename', '"{}": {}'.format(os.path.basename(fname), e)) )
				continue
				
			wx.CallAfter( doRename, fname, message, qMessage, qWriter )
	
		qRenamer.task_done()
