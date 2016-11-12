import threading
import datetime
from MultiCast import MultiCastReceiver

now = datetime.datetime.now
minDelay = 0.2

class SocketListener( MultiCastReceiver ):
	def __init__( self, qRequest, qMessage ):
		self.qRequest = qRequest
		self.qMessage = qMessage
		
		super( SocketListener, self ).__init__( self.triggerCallback, name='CrossMgrVideoReceiver' )
	
	def triggerCallback( self, info ):
		info['time'] = info['ts'] - datetime.timedelta( seconds=info['correction_secs'] )
		
		dt = (now() - info['time']).total_seconds() - info.get('advanceSeconds',0.0)
		if dt < minDelay:
			threading.Timer( dt + minDelay/2, self.qRequest.put, (info,) ).start()
		else:
			self.qRequest.put( info )
