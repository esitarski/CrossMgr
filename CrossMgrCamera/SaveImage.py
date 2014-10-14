
def SaveImage( fname, image, ftpInfo, qMessage, qWriter ):
	if ftpInfo:
		writerMessage = ('save', fname, image, ftpInfo)
	else:
		writerMessage = ('save', fname, image)
	
	try:
		qWriter.put( writerMessage, False )
	except Full:
		qMessage.put( ('error', 'Photo write queue full.  Missed {}.'.format(fname)) )
