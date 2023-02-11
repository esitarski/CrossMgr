import threading
import datetime
from MultiCast import MultiCastReceiver

now = datetime.datetime.now
minDelay = 1.0/30.0

def putTrigger( qRequest, info ):
	info['time'] = info['ts'] + datetime.timedelta( seconds=info.get('correction_secs', 0.0) )
	
	# Ensure that any timestamps in the future are delayed until they are in the past.
	dt = (now() - info['time']).total_seconds() - info.get('advanceSeconds',0.0)
	if dt <= minDelay:
		threading.Timer( minDelay, qRequest.put, (info,) ).start()
	else:
		qRequest.put( info )

class SocketListener( MultiCastReceiver ):
	def __init__( self, qRequest, qMessage ):
		self.qRequest = qRequest
		self.qMessage = qMessage
				
		super().__init__( self.triggerCallback, name='CrossMgrVideoListener' )
	
	def triggerCallback( self, info ):
		putTrigger( self.qRequest, info )
