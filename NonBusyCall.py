import wx
from datetime import datetime, timedelta

now = datetime.now

class NonBusyCall:
	def __init__( self, callable, args=(), kwargs={}, min_millis=1000, max_millis=3000  ):
		self.min_millis = min_millis
		self.max_millis = max_millis
		
		self.callable = callable
		self.args = args
		self.kwargs = kwargs
		
		self.tLastCall = now() - timedelta( seconds=max_millis/1000.0 )
		self.callLater = None
		
	def run_callable( self ):
		self.tLastCall = now()
		self.callable( *self.args, **self.kwargs )
		self.callLater = None
		
	def __call__( self ):
		tNow = now()
		last_call_millis = (tNow - self.tLastCall).total_seconds()*1000.0
		if last_call_millis >= self.max_millis:
			if self.callLater:
				self.callLater.Stop()
				self.callLater = None
			self.tLastCall = tNow
			self.callable( *self.args, **self.kwargs )
			return		
		if self.callLater:
			self.callLater.Stop()		
		self.callLater = wx.CallLater( self.min_millis, self.run_callable )
