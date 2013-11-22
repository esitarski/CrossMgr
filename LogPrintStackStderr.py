import wx
import sys
import datetime
import traceback

class LogPrintStackStderr( wx.PyLog ):
	def logHeader( self ):
		sys.stderr.write( '*' * 78 + '\n' )
		sys.stderr.write( '* wxPython Exception: {}\n'.format( datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') ) )
		sys.stderr.write( '*' * 78 + '\n' )

	def doPrint( self, *args, **kwargs ):
		sys.stderr.write( u': '.join(u'{}'.format(a) for a in args) )
		sys.stderr.write( '\n' )
		for k, v in kwargs.iteritems():
			sys.stderr.write( u'{}: {}\n'.format(k,v) )
				
	def DoLogText( self, *args, **kwargs ):
		self.logHeader()
		traceback.print_stack( file=sys.stderr )
		self.doPrint( *args, **kwargs )

	def DoLogString( self, *args, **kwargs ):
		self.logHeader()
		traceback.print_stack( file=sys.stderr )
		self.doPrint( *args, **kwargs )
	
	def DoLogRecord( self, *args, **kwargs ):
		self.logHeader()
		traceback.print_stack( file=sys.stderr )
		self.doPrint( *args, **kwargs )
		
	def DoLogTextAtLevel( self, *args, **kwargs ):
		self.logHeader()
		traceback.print_stack( file=sys.stderr )
		self.doPrint( *args, **kwargs )
		
if __name__ == '__main__':
	app = wx.App( False )
	wx.Log.SetActiveTarget( LogPrintStackStderr() )
	bitmap = wx.Bitmap( 'NonExistentFile.png' )