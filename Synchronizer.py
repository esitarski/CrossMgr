import wx
import sys
import threading
import traceback
import Utils

class Synchronizer( object ):
	def __init__( self, func, *args, **kwargs ):
		super( Synchronizer, self ).__init__()
		
		self.func = func
		self.args = args
		self.kwargs = kwargs
		self._sync = threading.Semaphore(0)
	
	def _ASyncWrapper( self ):
		''' This runs in the main gui thread. '''
		try:
			self.result = self.func( *self.args, **self.kwargs )
		except Exception as e:
			traceback.print_exc()
			self.exception = e
			Utils.logException( e, sys.exc_info )
		self._sync.release()
	
	def Run( self ):
		''' Call from background thread. '''
		assert not wx.IsMainThread(), 'Deadlock'
		wx.CallAfter( self._ASyncWrapper )
		self._sync.acquire()
		try:
			return self.result
		except AttributeError:
			raise self.exception

def syncfunc( func ):
	''' Decorator to synchronize a function call from a worker thread to the wx GUI thread. '''
	def syncwrap( *args, **kwargs ):
		if wx.IsMainThread():
			return self.func( *args, **kwargs )
		else:
			sync = Synchronizer( func, *args, **kwargs )
			return sync.Run()
	
	syncwrap.__name__ = func.__name__
	syncwrap.__doc__ = func.__doc__
	return syncwrap
	
def synchronized( lock ):
	""" Synchronization decorator. """

	def wrap( f ):
		def newFunction(*args, **kwargs):
			lock.acquire()
			try:
				return f(*args, **kwargs)
			finally:
				lock.release()
		return newFunction
	return wrap
