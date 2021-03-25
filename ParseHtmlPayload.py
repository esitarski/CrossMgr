import io
import os
import re
import json
import datetime

def ParseHtmlPayload( fname=None, content=None ):
	assert fname or content
	
	payloadStart = u"/* !!! payload begin !!! */"
	payloadEnd = u"/* !!! payload end !!! */"
	
	imgHeaderStart = u'id="idImgHeader" src='

	if not content:
		try:
			with io.open(fname) as f:
				content = f.read()
		except Exception as e:
			return {'success':False, 'error':e, 'payload':None}
	
	try:
		iStart = content.index( payloadStart )
	except ValueError as e:
		return {'success':False, 'error':e, 'payload':None}
	
	try:
		iEnd = content.index( payloadEnd, iStart + len(payloadStart) )
	except ValueError as e:
		return {'success':False, 'error':e, 'payload':None}

	contentStr = content[iStart:iEnd].split('=',1)[1].strip()
	if contentStr.endswith(';'):
		contentStr = contentStr[:-1]
	
	try:
		payload = json.loads( contentStr )
	except Exception as e:
		return {'success':False, 'error':e, 'payload':None}
	
	raceScheduledStart = None
	try:
		raceScheduledStart = datetime.datetime( *[int(f) for f in re.split('[^0-9]+', payload['raceScheduledStart'] )] )
	except KeyError:
		pass
	
	if not raceScheduledStart:
		try:
			raceScheduledStart = (
				datetime.datetime( *[int(f) for f in re.split('[^0-9]+', payload['raceDate'] )] ) +
				datetime.timedelta( seconds = payload['raceStartTime'] )
			)
		except Exception as e:
			pass
			
	if not raceScheduledStart:
		try:
			raceScheduledStart = datetime.datetime( *[int(f) for f in re.split('[^0-9]+', payload['raceDate'] )] )
		except Exception:
			raceScheduledStart = datetime.datetime.fromtimestamp(os.path.getmtime(fname))
	
	payload['raceScheduledStart'] = raceScheduledStart
	
	try:
		iStart = content.index( imgHeaderStart )
		iStart = content.index( '"', iStart + len(imgHeaderStart) ) + 1
		iEnd = content.index( '"', iStart )
		payload['logoSrc'] = content[iStart:iEnd]
	except ValueError as e:
		payload['logoSrc'] = None
	
	# Remove unneeded payload fields to save space.
	for key in ('riderDashboard', 'travelMap', 'virtualRideTemplate',
				'courseViewerTemplate', 'courseCoordinates', 'gpsPoints',
				'gpsTotalElevationGain', 'gpsAltigraph', 'gpsIsPointToPoint', 
				'flags', 'primes',):
		payload.pop( key, None )
	
	return {'success':True, 'error':None, 'payload':payload, 'content':content}
	
if __name__ == '__main__':
	htmlFile = os.path.join('Gemma', '2015-11-10-CXC Open BWomen-r2-.html')
	htmlFile = os.path.join('Larkin', '2015-06-12-Larkinville Challenge 5-r3-.html' )
	htmlFile = 'parseTest.html'
	result = ParseHtmlPayload( htmlFile )
	if result['success']:
		payload = result['payload']
		print(  payload['raceScheduledStart'] )
		catDetails = payload['catDetails']
		catDetails.sort( key=lambda c: (c['startOffset'], c['name']) )
		for c in catDetails:
			if c['name'] != 'All':
				print(  c['name'], c['startOffset'] )
		print( payload['logoSrc'] )
