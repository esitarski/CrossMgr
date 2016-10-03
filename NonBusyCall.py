import wx
from datetime import datetime

class NonBusyCall( object ):
	def __init__( self, callable, args=(), kwargs={}, min_millis=1000, max_millis=5000  ):
		self.min_millis = min_millis
		self.max_millis = max_millis
		
		self.callable = callable
		self.args = args
		self.kwargs = kwargs
		
		self.tLastCall = None
		self.callLater = None
		
	def run( self ):
		self.tLastCall = datetime.now()
		self.callable( *self.args, **self.kwargs )
		self.callLater = None
		
	def __call__( self ):
		if self.callLater:
			if self.tLastCall and (datetime.now() - self.tLastCall).total_seconds() * 1000 > self.max_millis:
				return
			self.callLater.Stop()		
		self.callLater = wx.CallLater( self.min_millis, self.run )
