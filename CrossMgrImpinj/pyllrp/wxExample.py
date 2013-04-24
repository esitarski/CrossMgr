import wx
import wx.lib.masked			as masked
import wx.lib.intctrl			as intctrl

import os
import sys
import time
import atexit
import datetime
from Queue import Queue, Empty

#-------------------------------------------------------------------
# A simple wxPython app to monitor messages from a LLRP reader.
#
# A Queue is used to collect asynchronous messages from the reader.
# Every second, the UI checks the queue and redraws the screen.
#
# There are at least two other methods in wxPython.
#
# The first is to use wx.CallAfter.  This puts a function call on
# the wxPython queue in a thread-safe way that will get called when
# control passes back to the wxPython event loop.
#
# See http://wiki.wxpython.org/CallAfter
#
# Another way to do this is with a custom event.  You send the custom
# event to a window from the reader monitoring thread, then you Bind an
# event handler to it.
#
# See http://wiki.wxpython.org/CustomEventClasses
# and http://www.blog.pythonlibrary.org/2010/05/22/wxpython-and-threads/

#-------------------------------------------------------------------
# If we are running from the development folder, change to a local search path.
if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == 'pyllrp':
	from pyllrp import *
	from LLRPConnection import LLRPConnection
else:
	from pyllrp.pyllrp import *
	from pyllrp.LLRPConnection import LLRPConnection

ReaderHostNamePrefix = 'SpeedwayR-'
ReaderHostNameSuffix = '.local'
ReaderInboundPort = 5084

class MessageManager( object ):
	''' Manage messages shown in a text ctrl. '''
	MessagesMax = 400	# Maximum number of messages before we start throwing some away.

	def __init__( self, messageList ):
		self.messageList = messageList
		self.messageList.Bind( wx.EVT_RIGHT_DOWN, lambda e: None )	# Disable default right button action.
		self.messageList.SetDoubleBuffered( True )					# Stop screen flicker.
		self.clear()
		
	def write( self, message ):
		if len(self.messages) >= self.MessagesMax:
			self.messages = self.messages[int(self.MessagesMax):]
			s = '\n'.join( self.messages )
			self.messageList.ChangeValue( s + '\n' )
		self.messages.append( message )
		self.messageList.AppendText( message + '\n' )
		
	def clear( self ):
		self.messages = []
		self.messageList.ChangeValue( '' )
		self.messageList.SetInsertionPointEnd()

def setFont( font, w ):
	w.SetFont( font )
	return w
	
class MainWin( wx.Frame ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(200,200) ):
		wx.Frame.__init__(self, parent, id, title, size=size)

		self.config = wx.Config(appName="wxExample",
						vendorName="Edward Sitarski",
						style=wx.CONFIG_USE_LOCAL_FILE)
						
		self.SetBackgroundColour( wx.Colour(232,232,232) )
		
		font = self.GetFont()
		bigFont = wx.Font( font.GetPointSize() * 1.5, font.GetFamily(), font.GetStyle(), wx.FONTWEIGHT_BOLD )
		italicFont = wx.Font( bigFont.GetPointSize()*2.2, bigFont.GetFamily(), wx.FONTSTYLE_ITALIC, bigFont.GetWeight() )
		
		self.vbs = wx.BoxSizer( wx.VERTICAL )
		
		self.vbs.Add( setFont(italicFont,wx.StaticText(self, wx.ID_ANY, 'wxExample LLRP Reader Demo')), border = 8, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		
		self.reset = setFont( bigFont, wx.Button(self, wx.ID_ANY, 'Reset') )
		self.reset.Bind( wx.EVT_BUTTON, self.doReset )
		self.vbs.Add( self.reset, border = 8, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		
		#------------------------------------------------------------------------------------------------
		# Reader configuration ui.
		#
		gbs = wx.GridBagSizer( 4, 4 )
		self.vbs.Add( gbs, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		iRow = 0
		gbs.Add( setFont(bigFont,wx.StaticText(self, wx.ID_ANY, 'Reader Configuration:')), pos=(iRow,0), span=(1,2), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		self.useHostName = wx.RadioButton( self, wx.ID_ANY, 'Host Name:', style=wx.wx.RB_GROUP )
		gbs.Add( self.useHostName, pos=(iRow,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( wx.StaticText(self, wx.ID_ANY, ReaderHostNamePrefix), flag=wx.ALIGN_CENTER_VERTICAL )
		self.readerHostName = masked.TextCtrl( self, wx.ID_ANY,
							mask         = 'NN-NN-NN',
							defaultValue = '00-00-00',
							useFixedWidthFont = True,
							size=(80, -1),
						)
		hb.Add( self.readerHostName )
		hb.Add( wx.StaticText(self, wx.ID_ANY, ReaderHostNameSuffix), flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		self.useStaticAddress = wx.RadioButton( self, wx.ID_ANY, 'IP:' )
		gbs.Add( self.useStaticAddress, pos=(iRow,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		self.readerHost = masked.IpAddrCtrl( self, wx.ID_ANY, style = wx.TE_PROCESS_TAB )
		gbs.Add( self.readerHost, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		self.useHostName.SetValue( True )
		self.useStaticAddress.SetValue( False )
		
		#------------------------------------------------------------------------------------------------
		# Add messages
		#
		self.readerMessagesText = wx.TextCtrl( self, wx.ID_ANY, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(-1,400) )
		self.vbs.Add( self.readerMessagesText, flag=wx.EXPAND, proportion=1 )
		self.readerMessages = MessageManager( self.readerMessagesText )
		
		#------------------------------------------------------------------------------------------------
		# Create a timer to check the message queue.
		#
		self.timer = wx.Timer()
		self.timer.Bind( wx.EVT_TIMER, self.updateMessages )
		self.timer.Start( 1000, False )
		
		self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

		self.readOptions()
		self.SetSizer( self.vbs )
		self.start()
	
	def start( self ):
		self.dataQ = Queue()	# Queue to put messages from the reaader.
		
		rospecID = 123					# Arbitrary rospecID.
		inventoryParameterSpecID = 1234	# Arbitrary inventory parameter spec id.

		# Create a reader connection.
		self.conn = LLRPConnection()

		# Add a callback so we can print the tags.
		self.conn.addHandler( RO_ACCESS_REPORT_Message, self.accessReportHandler )

		# Add a default callback so we can see what else comes from the reader.
		self.conn.addHandler( 'default', self.defaultHandler )

		self.readerMessages.write( 'Connecting to the reader at %s...\n' % datetime.datetime.now() )
		try:
			response = self.conn.connect( self.getReaderHost() )
		except Exception as e:
			self.readerMessages.write( 'Connection to reader failed.\nException:\n%s\n\nCheck address and/or network connection and press Reset.' % e )
			return

		# Compute a correction between the reader's time and the computer's time.
		readerTime = response.getFirstParameterByClass(UTCTimestamp_Parameter).Microseconds
		readerTime = datetime.datetime.utcfromtimestamp( readerTime / 1000000.0 )
		self.timeCorrection = datetime.datetime.now() - readerTime

		self.readerMessages.write( 'Disabling all rospecs...' )
		response = self.conn.transact( DISABLE_ROSPEC_Message(ROSpecID = 0) )

		self.readerMessages.write( 'Delete our old rospec (if it exists).' )
		response = self.conn.transact( DELETE_ROSPEC_Message(ROSpecID = rospecID) )

		self.readerMessages.write( 'Create an rospec that reports every read as soon as it happens.' )
		response = self.conn.transact(
			ADD_ROSPEC_Message( Parameters = [
				ROSpec_Parameter(
					ROSpecID = rospecID,
					CurrentState = ROSpecState.Disabled,
					Parameters = [
						ROBoundarySpec_Parameter(		# Configure boundary spec (start and stop triggers for the reader).
							Parameters = [
								ROSpecStartTrigger_Parameter(ROSpecStartTriggerType = ROSpecStartTriggerType.Immediate),
								ROSpecStopTrigger_Parameter(ROSpecStopTriggerType = ROSpecStopTriggerType.Null),
							]
						), # end ROBoundarySpec
						AISpec_Parameter(				# Antenna Inventory Spec (specifies which antennas and protocol to use)
							AntennaIDs = [0],			# Use all antennas.
							Parameters = [
								AISpecStopTrigger_Parameter( AISpecStopTriggerType = AISpecStopTriggerType.Null ),
								InventoryParameterSpec_Parameter(
									InventoryParameterSpecID = inventoryParameterSpecID,
									ProtocolID = AirProtocols.EPCGlobalClass1Gen2,
								),
							]
						), # end AISpec
						ROReportSpec_Parameter(			# Report spec (specified how often and what to send from the reader)
							ROReportTrigger = ROReportTriggerType.Upon_N_Tags_Or_End_Of_ROSpec,
							N = 1,						# N = 1 --> update on each read.
							Parameters = [
								TagReportContentSelector_Parameter(
									EnableAntennaID = True,
									EnableFirstSeenTimestamp = True,
								),
							]
						), # end ROReportSpec
					]
				), # end ROSpec_Parameter
			])	# end ADD_ROSPEC_Message
		)
		if not response.success():
			self.readerMessages.write( 'ADD_ROSPEC failed.  response:\n%s' % response)
			return

		self.readerMessages.write( 'And enable it...' )
		response = self.conn.transact( ENABLE_ROSPEC_Message(ROSpecID = rospecID) )
		if not response.success():
			self.readerMessages.write( 'ENABLE_ROSPEC failed.  response:\n%s' % response)
			return

		self.readerMessages.write( 'Start thread to listen to the reader...' )
		self.readerMessages.write( 'Listening for reader events...')
		self.conn.startListener()
	
	def gracefulShutdown( self ):
		if self.conn:
			if self.conn.isListening():
				self.conn.stopListener()
			self.conn = None
		self.dataQ = None
	
	def updateMessages( self, event ):
		''' Write all the accumulated reader messages to the screen. '''
		while 1:
			try:
				d = self.dataQ.get( False )
			except Empty:
				break
			message = ' '.join( str(x) for x in d[1:] )
			if d[0] == 'Reader':
				self.readerMessages.write( message )

	def doReset( self, event ):
		self.writeOptions()
		self.gracefulShutdown()
		self.readerMessages.clear()
		wx.CallAfter( self.start )
	
	def onCloseWindow( self, event ):
		self.gracefulShutdown()
		wx.Exit()
		
	def getReaderHost( self ):
		if self.useHostName.GetValue():
			return ReaderHostNamePrefix + self.readerHostName.GetValue() + ReaderHostNameSuffix
		else:
			return self.readerHost.GetAddress()
	
	def writeOptions( self ):
		self.config.Write( 'UseHostName', 'True' if self.useHostName.GetValue() else 'False' )
		self.config.Write( 'ReaderHostName', ReaderHostNamePrefix + self.readerHostName.GetValue() + ReaderHostNameSuffix )
		self.config.Write( 'ReaderAddr', self.readerHost.GetAddress() )
		self.config.Write( 'ReaderPort', str(ReaderInboundPort) )
	
	def readOptions( self ):
		useHostName = (self.config.Read('UseHostName', 'True').upper()[:1] == 'T')
		self.useHostName.SetValue( useHostName )
		self.useStaticAddress.SetValue( not useHostName )
		self.readerHostName.SetValue( self.config.Read(
				'ReaderHostName',
				ReaderHostNamePrefix + '00-00-00' + ReaderHostNameSuffix)[len(ReaderHostNamePrefix):-len(ReaderHostNameSuffix)] )
		self.readerHost.SetValue( self.config.Read('ReaderAddr', '0.0.0.0') )
	
	def defaultHandler( self, message ):
		''' Write to a queue so we can process it later. '''
		self.dataQ.put( ('Reader', ('Unexpected message:\n', message) ) )
	
	def accessReportHandler( self, accessReport ):
		''' Write the access report to a queue so we can process it later. '''
		''' We also could send these directly as a custom event. '''
		for tag in accessReport.getTagData():
			tagID = HexFormatToInt( tag['EPC'] )
			discoveryTime = tag['Timestamp']		# In microseconds since Jan 1, 1970
			discoveryTime = datetime.datetime.utcfromtimestamp( discoveryTime / 1000000.0 ) + self.timeCorrection
			self.dataQ.put( ('Reader', (tagID, discoveryTime.strftime('%Y-%m-%d %H:%M:%S.%f'))) )
	
mainWin = None
def MainLoop():
	global mainWin
	app = wx.PySimpleApp()
	app.SetAppName("wxExample RRLP Reader")
	mainWin = MainWin( None, title='wxExample RRLP Reader', size=(800,1000) )
	mainWin.Show()
	app.MainLoop()

@atexit.register
def shutdown():
	if mainWin:
		mainWin.gracefulShutdown()
	
if __name__ == '__main__':
	MainLoop()
	