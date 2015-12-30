import io
import os
import re
import json
import datetime

def ParseHtmlPayload( fname ):
	payloadStart = u"/* !!! payload begin !!! */"
	payloadEnd = u"/* !!! payload end !!! */"

	try:
		with io.open(fname, encoding='utf-8') as f:
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
		except:
			raceScheduledStart = datetime.fromtimestamp(os.path.getmtime(fname))
	
	payload['raceScheduledStart'] = raceScheduledStart
	return {'success':True, 'error':None, 'payload':payload}
	
if __name__ == '__main__':
	result = ParseHtmlPayload( os.path.join('Gemma', '2015-11-10-CXC Open BWomen-r2-.html') )
	if result['success']:
		payload = result['payload']
		print payload['raceScheduledStart']
		catDetails = payload['catDetails']
		catDetails.sort( key=lambda c: (c['startOffset'], c['name']) )
		for c in catDetails:
			if c['name'] != 'All':
				print c['name'], c['startOffset']