import wx
import sys
import traceback

class LogPrintStackStderr( wx.PyLog ):
	def doPrint( self, *args, **kwargs ):
		sys.stderr.write( u': '.join(u'{}'.format(a) for a in args) )
		sys.stderr.write( '\n' )
		for k, v in kwargs.iteritems():
			sys.stderr.write( u'{}: {}\n'.format(k,v) )
				
	def DoLogText( self, *args, **kwargs ):
		sys.stderr.write( '*' * 78 + '\n' )
		traceback.print_stack( file=sys.stderr )
		self.doPrint( *args, **kwargs )

	def DoLogRecord( self, *args, **kwargs ):
		sys.stderr.write( '*' * 78 + '\n' )
		traceback.print_stack( file=sys.stderr )
		self.doPrint( *args, **kwargs )
		
	def DoLogTextAtLevel( self, *args, **kwargs ):
		sys.stderr.write( '*' * 78 + '\n' )
		traceback.print_stack( file=sys.stderr )
		self.doPrint( *args, **kwargs )