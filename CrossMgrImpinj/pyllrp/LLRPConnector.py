#!/usr/bin/env python
from pyllrp import *
from Queue import Queue, Empty
import socket
import datetime
import threading

class LLRPConnector( object ):
	#--------------------------------------------------------------------------
	#
	# A simple LLRP reader connection manager.
	#
	# Supports connecting to the reader, transacting commands, message handlers,
	# and asynchronous/synchronous monitoring of the reader socket.
	#
	def __init__( self ):
		self.TimeoutSecs = 6		# Time for the reader to respond.
		self._reset()
		self.handlers = {}
		
	def _reset( self ):
		''' Reset all internal fields. '''
		self.host = None
		self.port = None
		self.readerSocket = None
		self.thread = None
		self.shutdownQ = None		# Used to shutdown the thread.
		self.keepGoing = False
		self.timeCorrection = None
	
	def connect( self, host, port = 5084 ):
		''' Connect to a reader. '''
		self._reset()
		self.readerSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		
		# Set a timeout for the socket.  This is also the maximum time it will take to shut down the listener.
		self.readerSocket.settimeout( self.TimeoutSecs )
		self.readerSocket.connect( (host, port) )
		tNow = datetime.datetime.now()	# Get the time here to minimize latency.
		
		self.host = host
		self.port = port
		
		# Expecting READER_EVENT_NOTIFICATION message.
		response = UnpackMessageFromSocket( self.readerSocket )
		
		# Check if the connection succeeded.
		connectionAttemptEvent = response.getFirstParameterByClass(ConnectionAttemptEvent_Parameter)
		if connectionAttemptEvent and connectionAttemptEvent.Status != ConnectionAttemptStatusType.Success:
			self.disconnect()
			raise EnvironmentError(
				connectionAttemptEvent.Status,
				ConnectionAttemptStatusType.getName(connectionAttemptEvent.Status).replace('_',' ')
			)
		
		self.keepGoing = True
		
		# Compute a correction between the reader's time and the computer's time.
		self.timeCorrection = None
		try:
			microseconds = response.getFirstParameterByClass(UTCTimestamp_Parameter).Microseconds
			readerTime = datetime.datetime.utcfromtimestamp( microseconds / 1000000.0 )
			self.timeCorrection = tNow - readerTime
		except Exception as e:
			self.disconnect()
			raise ValueError('Missing Timestamp: ' + response.__repr__())

		return response
		
	def tagTimeToComputerTime( self, tagTime ):
		# Time is in microseconds from Jan 1, 1970.
		return datetime.datetime.utcfromtimestamp( tagTime / 1000000.0 ) + self.timeCorrection
	
	def disconnect( self ):
		''' Disconnect from a reader.  Also stops the listener. '''
		self.timeCorrection = None
		if not self.readerSocket:
			return None
		
		if self.isListening():
			self.stopListener()
		
		# Send the reader a disconnect message.
		response = None
		try:
			response = self.transact( CLOSE_CONNECTION_Message() )
		except:
			pass
		
		self.readerSocket.close()
		self.readerSocket = None
		return response
		
	def addHandler( self, messageClass, handlerFunc ):
		''' Add a handler for a specific message type. '''
		''' Support multiple handlers for the same message type. '''
		self.handlers.setdefault( messageClass, [] ).append( handlerFunc )
		
	def removeHandler( self, messageClass, handlerFunc = None ):
		''' Remove a handler for a specific message type from the reader.
			If handlerFunc is None, all handlers for the given messageClass will be removed.
			If handlerFunc is not None, only the specific handler is removed.
		'''
		if handlerFunc is None:
			try:
				del self.handlers[messageClass]
			except KeyError:
				pass
		else:
			while 1:
				try:
					self.handlers[messageClass].remove( handlerFunc )
				except (KeyError, ValueError):
					break
					
	def removeAllHandlers( self ):
		self.handlers = {}
	
	def transact( self, message ):
		''' Send a message to the reader and wait for the response. '''
		assert not self.isListening(), 'Cannot perform transact() while listen thread is active.  Stop it first with stopListener().'
		message.send( self.readerSocket )
		response = WaitForMessage( message.MessageID, self.readerSocket, self.callHandler )
		return response
		
	def checkKeepGoing( self ):
		''' Check if we should continue the reader thread. '''
		if not self.keepGoing:
			return False
			
		try:
			# Check the shutdown queue for a message.  If there is one, shutdown.
			d = self.shutdownQ.get( False )
			self.shutdownQ.task_done()
			self.keepGoing = False
			return False
		except (AttributeError, Empty):
			return True
	
	def callHandler( self, message ):
		''' Call all the handlers for this message. '''
		for cb in (self.handlers.get(message.__class__, None) or self.handlers.get('default', [])):
			cb( self, message )
	
	def listen( self ):
		''' Listen for messages from the reader. '''
		# Calling this by itself will block.
		# Recommended usage is to use startListener and stopListener.
		while self.checkKeepGoing():
			try:
				response = UnpackMessageFromSocket( self.readerSocket )
			except socket.timeout:
				continue
			self.callHandler( response )
				
	def startListener( self ):
		''' Starts a thread to listen to the reader. '''
		assert self.readerSocket, 'Cannot start listener without a successful connection.'
		assert not self.thread, 'Listener is already running.  Stop it first with stopListener().'
		self.shutdownQ = Queue()
		self.keepGoing = True
		self.thread = threading.Thread( target = self.listen, name='LLRP Listener' )
		self.thread.daemon = True
		self.thread.start()
	
	def stopListener( self ):
		''' Stops the thread listening to the reader. '''
		self.shutdownQ.put( 'Shutdown' )
		self.thread.join()					# Wait for the thread to terminate.
		self.shutdownQ = None
		self.thread = None
	
	def isListening( self ):
		return self.thread and self.thread.is_alive()
		
