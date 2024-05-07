import sys
import inspect
import threading
#import logging

class logging:
	@staticmethod
	def debug( msg ):
		print( msg, file=sys.stderr)

def format_frame( frame ):
	return '{}:{} {}'.format( *[str(getattr(frame, a)) for a in ('filename', 'lineno', 'function')] )

# Class to wrap Lock and simplify logging of lock usage
class Lock:
	"""
	Wraps a standard Lock, so that attempts to use the
	lock according to its API are logged for debugging purposes

	"""
	def __init__(self, name=None, log=None):
		self.lock = threading.Lock()
		self.do_init( name, log )
		self.log.debug("{0} created {1}".format(self.context(), self.name))

	def do_init( self, name=None, log=None ):
		self.name = str(name)
		self.log = log or logging

	def acquire(self, blocking=True):
		self.log.debug("{0} ---- trying to acquire {1}".format( self.context(), self.name))
		for f in self.print_stack():
			self.log.debug( f )
		ret = self.lock.acquire(blocking)
		if ret:
			self.log.debug("{0} **** acquired {1}".format(
				self.context(), self.name))
		else:
			self.log.debug("{0} **** non-blocking acquire of {1} lock failed".format(
				self.context(), self.name))
		return ret
		
	def print_stack( self ):
		stack = inspect.stack()
		return [format_frame(frame) for frame in reversed(stack)]
		
	def context( self ):
		return format_frame( inspect.stack()[3] )

	def release(self):
		self.log.debug("{0} vvvv releasing {1}".format(self.context(), self.name))
		self.lock.release()

	def __enter__(self):
		self.acquire()

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.release()
		return False # Do not swallow exceptions

class RLock(Lock):
	"""
	Wraps a standard RLock, so that attempts to use the
	lock according to its API are logged for debugging purposes

	"""
	def __init__(self, name=None, log=None):
		self.lock = threading.RLock()
		self.do_init( name, log )
		self.log.debug("{0} created {1}".format(self.context(), self.name))

