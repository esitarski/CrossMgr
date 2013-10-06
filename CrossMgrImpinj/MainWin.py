import sys
import threading
import socket
import atexit
import time
from roundbutton import RoundButton
import Utils
from Queue import Empty
from threading import Thread as Process
from Queue import Queue
from Impinj import ImpinjServer
from Impinj2JChip import CrossMgrServer
from AutoDetect import AutoDetect

import wx
import wx.lib.masked             as masked
import wx.lib.intctrl			as intctrl
import sys
import os
import re
import datetime

from Version import AppVerName

CrossMgrPort = 53135
ImpinjHostNamePrefix = 'SpeedwayR-'
ImpinjHostNameSuffix = '.local'
ImpinjInboundPort = 5084
#ImpinjInboundPort = 50840

clipboard_xpm = [
"16 15 23 1",
"+ c #769CDA",
": c #DCE6F6",
"X c #3365B7",
"* c #FFFFFF",
"o c #9AB6E4",
"< c #EAF0FA",
"# c #B1C7EB",
". c #6992D7",
"3 c #F7F9FD",
", c #F0F5FC",
"$ c #A8C0E8",
"  c None",
"- c #FDFEFF",
"& c #C4D5F0",
"1 c #E2EAF8",
"O c #89A9DF",
"= c #D2DFF4",
"4 c #FAFCFE",
"2 c #F5F8FD",
"; c #DFE8F7",
"% c #B8CCEC",
"> c #E5EDF9",
"@ c #648FD6",
" .....XX        ",
" .oO+@X#X       ",
" .$oO+X##X      ",
" .%$o........   ",
" .&%$.*=&#o.-.  ",
" .=&%.*;=&#.--. ",
" .:=&.*>;=&.... ",
" .>:=.*,>;=&#o. ",
" .<1:.*2,>:=&#. ",
" .2<1.*32,>:=&. ",
" .32<.*432,>:=. ",
" .32<.*-432,>:. ",
" .....**-432,>. ",
"     .***-432,. ",
"     .......... "
]


class MessageManager( object ):
	MessagesMax = 400	# Maximum number of messages before we start throwing some away.

	def __init__( self, messageList ):
		self.messageList = messageList
		self.messageList.Bind( wx.EVT_RIGHT_DOWN, self.skip )
		self.messageList.SetDoubleBuffered( True )
		self.clear()
		
	def skip(self, evt):
		return
		
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

		self.config = wx.Config(appName="CrossMgrImpinj",
						vendorName="SmartCyclingSolutions",
						style=wx.CONFIG_USE_LOCAL_FILE)
						
		self.SetBackgroundColour( wx.Colour(232,232,232) )
		
		self.LightGreen = wx.Colour(153,255,153)
		self.LightRed = wx.Colour(255,153,153)
		
		font = self.GetFont()
		bigFont = wx.Font( font.GetPointSize() * 1.5, font.GetFamily(), font.GetStyle(), wx.FONTWEIGHT_BOLD )
		italicFont = wx.Font( bigFont.GetPointSize()*2.2, bigFont.GetFamily(), wx.FONTSTYLE_ITALIC, bigFont.GetWeight() )
		
		self.vbs = wx.BoxSizer( wx.VERTICAL )
		
		bs = wx.BoxSizer( wx.HORIZONTAL )
		
		self.reset = RoundButton(self, wx.ID_ANY, 'Reset', size=(80, 80))
		self.reset.SetBackgroundColour( wx.WHITE )
		self.reset.SetForegroundColour( wx.Colour(0,128,128) )
		self.reset.SetFontToFitLabel()	# Use the button's default font, but change the font size to fit the label.
		self.reset.Bind( wx.EVT_BUTTON, self.doReset )
		self.reset.Refresh()
		bs.Add( self.reset, border = 8, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.Add( setFont(italicFont,wx.StaticText(self, wx.ID_ANY, 'CrossMgrImpinj')), border = 8, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.AddStretchSpacer()
		bitmap = wx.BitmapFromXPMData( clipboard_xpm )
		self.copyToClipboard = wx.BitmapButton( self, wx.ID_ANY, bitmap )
		self.copyToClipboard.SetToolTip(wx.ToolTip('Copy Configuration and Logs to Clipboard...'))
		self.copyToClipboard.Bind( wx.EVT_BUTTON, self.doCopyToClipboard )
		bs.Add( self.copyToClipboard, border = 32, flag = wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.tStart = datetime.datetime.now()
		bs.Add( setFont(bigFont,wx.StaticText(self, wx.ID_ANY, 'Last Reset: %s' % self.tStart.strftime('%H:%M:%S'))), border = 10, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.runningTime = setFont(bigFont,wx.StaticText(self, wx.ID_ANY, '00:00:00' ))
		bs.Add( self.runningTime, border = 20, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.Add( setFont(bigFont,wx.StaticText(self, wx.ID_ANY, ' / ')), flag=wx.ALIGN_CENTER_VERTICAL )
		self.time = setFont(bigFont, wx.StaticText(self, wx.ID_ANY, '00:00:00' ))
		bs.Add( self.time, flag=wx.ALIGN_CENTER_VERTICAL )
		
		self.vbs.Add( bs, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		fgs = wx.FlexGridSizer( rows = 2, cols = 2, vgap = 4, hgap = 4 )
		fgs.AddGrowableRow( 1 )
		fgs.AddGrowableCol( 0 )
		fgs.AddGrowableCol( 1 )
		fgs.SetFlexibleDirection( wx.BOTH )
		
		self.vbs.Add( fgs, flag=wx.EXPAND, proportion=5 )
		
		#------------------------------------------------------------------------------------------------
		# Impinj configuration.
		#
		gbs = wx.GridBagSizer( 4, 4 )
		fgs.Add( gbs, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		iRow = 0
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( setFont(bigFont,wx.StaticText(self, wx.ID_ANY, 'Impinj Configuration:')), flag=wx.ALIGN_CENTER_VERTICAL )
		self.autoDetectButton = wx.Button(self, wx.ID_ANY, 'Auto Detect')
		self.autoDetectButton.Bind( wx.EVT_BUTTON, self.doAutoDetect )
		hb.Add( self.autoDetectButton, flag=wx.LEFT, border = 6 )
		gbs.Add( hb, pos=(iRow,0), span=(1,2), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		
		gs = wx.GridSizer( 1, 4, 2, 2 )
		self.antennas = []
		for i in xrange(4):
			gs.Add( wx.StaticText(self, wx.ID_ANY, '%d' % (i+1)), flag=wx.ALIGN_CENTER )
		for i in xrange(4):
			cb = wx.CheckBox( self, wx.ID_ANY, '')
			if i < 2:
				cb.SetValue( True )
			cb.Bind( wx.EVT_CHECKBOX, lambda x: self.getAntennaStr() )
			gs.Add( cb, flag=wx.ALIGN_CENTER )
			self.antennas.append( cb )
		
		gbs.Add( wx.StaticText(self, wx.ID_ANY, 'ANT Ports:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM )
		gbs.Add( gs, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		
		iRow += 1
		
		self.useHostName = wx.RadioButton( self, wx.ID_ANY, 'Host Name:', style=wx.wx.RB_GROUP )
		gbs.Add( self.useHostName, pos=(iRow,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( wx.StaticText(self, wx.ID_ANY, ImpinjHostNamePrefix), flag=wx.ALIGN_CENTER_VERTICAL )
		self.impinjHostName = masked.TextCtrl( self, wx.ID_ANY,
							mask         = 'NN-NN-NN',
							defaultValue = '00-00-00',
							useFixedWidthFont = True,
							size=(80, -1),
						)
		hb.Add( self.impinjHostName )
		hb.Add( wx.StaticText(self, wx.ID_ANY, ImpinjHostNameSuffix), flag=wx.ALIGN_CENTER_VERTICAL )
		hb.Add( wx.StaticText(self, wx.ID_ANY, ' : ' + '{}'.format(ImpinjInboundPort)), flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		self.useStaticAddress = wx.RadioButton( self, wx.ID_ANY, 'IP:' )
		gbs.Add( self.useStaticAddress, pos=(iRow,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		hb = wx.BoxSizer( wx.HORIZONTAL )
		self.impinjHost = masked.IpAddrCtrl( self, wx.ID_ANY, style = wx.TE_PROCESS_TAB )
		hb.Add( self.impinjHost )
		hb.Add( wx.StaticText(self, wx.ID_ANY, ' : ' + '{}'.format(ImpinjInboundPort)), flag=wx.ALIGN_CENTER_VERTICAL )

		gbs.Add( hb, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		self.useHostName.SetValue( True )
		self.useStaticAddress.SetValue( False )
		
		iRow += 1
		gbs.Add( wx.StaticText(self, wx.ID_ANY, 'Backup File:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT )
		self.backupFile = wx.StaticText( self, wx.ID_ANY, '' )
		gbs.Add( self.backupFile, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		#------------------------------------------------------------------------------------------------
		# CrossMgr configuration.
		#
		gbs = wx.GridBagSizer( 4, 4 )
		fgs.Add( gbs, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		gbs.Add( setFont(bigFont,wx.StaticText(self, wx.ID_ANY, 'CrossMgr Configuration:')), pos=(0,0), span=(1,2), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( wx.StaticText(self, wx.ID_ANY, 'CrossMgr Address:'), pos=(1,0), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		
		hb = wx.BoxSizer( wx.HORIZONTAL )
		self.crossMgrHost = masked.IpAddrCtrl( self, wx.ID_ANY, style = wx.TE_PROCESS_TAB )
		hb.Add( self.crossMgrHost, flag=wx.ALIGN_LEFT )
		hb.Add( wx.StaticText( self, wx.ID_ANY, ' : 53135' ), flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(1,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		#------------------------------------------------------------------------------------------------
		# Add messages
		#
		self.impinjMessagesText = wx.TextCtrl( self, wx.ID_ANY, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(-1,400) )
		fgs.Add( self.impinjMessagesText, flag=wx.EXPAND, proportion=2 )
		self.impinjMessages = MessageManager( self.impinjMessagesText )
		
		self.crossMgrMessagesText = wx.TextCtrl( self, wx.ID_ANY, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(-1,400) )
		fgs.Add( self.crossMgrMessagesText, flag=wx.EXPAND, proportion=2 )
		self.crossMgrMessages = MessageManager( self.crossMgrMessagesText )
		self.fgs = fgs
		
		#------------------------------------------------------------------------------------------------
		# Create a timer to update the messages.
		#
		self.timer = wx.Timer()
		self.timer.Bind( wx.EVT_TIMER, self.updateMessages )
		self.timer.Start( 1000, False )
		
		self.Bind(wx.EVT_CLOSE, self.onCloseWindow)

		self.readOptions()
		
		self.SetSizer( self.vbs )
		self.start()
	
	def start( self ):
		self.dataQ = Queue()
		self.messageQ = Queue()
		self.shutdownQ = Queue()	# Queue to tell the Impinj monitor to shut down.
		
		if self.useHostName.GetValue():
			self.impinjProcess = Process( name='ImpinjProcess', target=ImpinjServer,
				args=(self.dataQ, self.messageQ, self.shutdownQ,
						ImpinjHostNamePrefix + self.impinjHostName.GetValue() + ImpinjHostNameSuffix, ImpinjInboundPort,
						self.getAntennaStr() ) )
		else:
			self.impinjProcess = Process( name='ImpinjProcess', target=ImpinjServer,
				args=(self.dataQ, self.messageQ, self.shutdownQ,
						self.impinjHost.GetAddress(), ImpinjInboundPort, self.getAntennaStr() ) )
		self.impinjProcess.daemon = True
		
		self.crossMgrProcess = Process( name='CrossMgrProcess', target=CrossMgrServer,
			args=(self.dataQ, self.messageQ, self.shutdownQ, self.getCrossMgrHost(), CrossMgrPort) )
		self.crossMgrProcess.daemon = True
		
		self.impinjProcess.start()
		self.crossMgrProcess.start()
	
	def shutdown( self ):
		self.impinjProcess = None
		self.crossMgrProcess = None
		self.messageQ = None
		self.dataQ = None
		self.shutdownQ = None
	
	def doReset( self, event, confirm = True ):
		if confirm:
			dlg = wx.MessageDialog(self, 'Reset CrossMgrImpinj Adapter?',
									'Confirm Reset',
									wx.OK | wx.CANCEL | wx.ICON_WARNING )
			ret = dlg.ShowModal()
			dlg.Destroy()
			if ret != wx.ID_OK:
				return
		
		self.reset.Enable( False )		# Prevent multiple clicks while shutting down.
		self.writeOptions()
		
		self.gracefulShutdown()
		
		self.impinjMessages.clear()
		self.crossMgrMessages.clear()
		self.shutdown()
		
		self.reset.Enable( True )
		
		wx.CallAfter( self.start )
		
	def doAutoDetect( self, event ):
		wx.BeginBusyCursor()
		self.gracefulShutdown()
		self.shutdown()
		impinjHost, crossMgrHost = AutoDetect( ImpinjInboundPort )
		wx.EndBusyCursor()
		
		if impinjHost and crossMgrHost:
			self.useStaticAddress.SetValue( True )
			self.useHostName.SetValue( False )
			
			self.impinjHost.SetValue( impinjHost )
			self.crossMgrHost.SetValue( crossMgrHost )
		else:
			dlg = wx.MessageDialog(self, 'Auto Detect Failed.\nCheck that reader has power and is connected to the router.',
									'Auto Detect Failed',
									wx.OK | wx.ICON_INFORMATION )
			dlg.ShowModal()
			dlg.Destroy()
			
		self.doReset( event, False )
	
	def gracefulShutdown( self ):
		# Shutdown the CrossMgr process by sending it a shutdown command.
		if self.shutdownQ:
			self.shutdownQ.put( 'shutdown' )
			self.shutdownQ.put( 'shutdown' )
			self.shutdownQ.put( 'shutdown' )
		if self.dataQ:
			self.dataQ.put( 'shutdown' )
			self.dataQ.put( 'shutdown' )
		
		if self.crossMgrProcess:
			self.crossMgrProcess.join()
		if self.impinjProcess:
			self.impinjProcess.join()
		
		self.crossMgrProcess = None
		self.impinjProcess = None
	
	def onCloseWindow( self, event ):
		self.gracefulShutdown()
		wx.Exit()
		
	def doCopyToClipboard( self, event ):
		cc = [
			'Configuration: CrossMgrImpinj',
			'    RunningTime:   {}'.format(self.runningTime.GetLabel()),
			'    Time:          {}'.format(self.time.GetLabel()),
			'    BackupFile:    {}'.format(self.backupFile.GetLabel()),
			'',
			'Configuration: Impinj:',
			'    Use Host Name: {}'.format('True' if self.useHostName.GetValue() else 'False'),
			'    HostName:      {}'.format((ImpinjHostNamePrefix + self.impinjHostName.GetValue()) + ImpinjHostNameSuffix),
			'    ImpinjHost:    {}'.format(self.impinjHost.GetAddress()),
			'    ImpinjPort:    {}'.format(ImpinjInboundPort),
			'',
			'Configuration: CrossMgr',
			'    CrossMgrHost:  {}'.format(self.getCrossMgrHost()),
			'    CrossMgrPort:  {}'.format(CrossMgrPort),
		]
		cc.append( '\nLog: Impinj' )
		log = self.impinjMessagesText.GetValue()
		cc.extend( ['    ' + line for line in log.split('\n')] )
		
		cc.append( '\nLog: CrossMgr' )
		log = self.crossMgrMessagesText.GetValue()
		cc.extend( ['    ' + line for line in log.split('\n')] )
		
		cc.append( '\nLog: Application\n' )
		try:
			with open(redirectFileName, 'r') as fp:
				for line in fp:
					cc.append( line )
		except:
			pass
		
		if wx.TheClipboard.Open():
			do = wx.TextDataObject()
			do.SetText( '\n'.join(cc) )
			wx.TheClipboard.SetData(do)
			wx.TheClipboard.Close()
			dlg = wx.MessageDialog(self, 'Configuration and Logs copied to the Clipboard.',
									'Copy to Clipboard Succeeded',
									wx.OK | wx.ICON_INFORMATION )
			ret = dlg.ShowModal()
			dlg.Destroy()
		else:
			# oops... something went wrong!
			wx.MessageBox("Unable to open the clipboard", "Error")

	def getCrossMgrHost( self ):
		return self.crossMgrHost.GetAddress()
		
	def getAntennaStr( self ):
		s = []
		for i in xrange(4):
			if self.antennas[i].GetValue():
				s.append( '%d' % (i + 1) )
		if not s:
			# Ensure that at least one antenna is selected.
			self.antennas[0].SetValue( True )
			s.append( '1' )
		return ' '.join( s )
		
	def setAntennaStr( self, s ):
		antennas = set( int(a) for a in s.split() )
		for i in xrange(4):
			self.antennas[i].SetValue( (i+1) in antennas )
	
	def writeOptions( self ):
		self.config.Write( 'CrossMgrHost', self.getCrossMgrHost() )
		self.config.Write( 'UseHostName', 'True' if self.useHostName.GetValue() else 'False' )
		self.config.Write( 'ImpinjHostName', ImpinjHostNamePrefix + self.impinjHostName.GetValue() + ImpinjHostNameSuffix )
		self.config.Write( 'ImpinjAddr', self.impinjHost.GetAddress() )
		self.config.Write( 'ImpinjPort', str(ImpinjInboundPort) )
		self.config.Write( 'Antennas', self.getAntennaStr() )
	
	def readOptions( self ):
		self.crossMgrHost.SetValue( self.config.Read('CrossMgrHost', Utils.DEFAULT_HOST) )
		useHostName = (self.config.Read('UseHostName', 'True').upper()[:1] == 'T')
		self.useHostName.SetValue( useHostName )
		self.useStaticAddress.SetValue( not useHostName )
		self.impinjHostName.SetValue( self.config.Read('ImpinjHostName', ImpinjHostNamePrefix + '00-00-00' + ImpinjHostNameSuffix)[len(ImpinjHostNamePrefix):-len(ImpinjHostNameSuffix)] )
		self.impinjHost.SetValue( self.config.Read('ImpinjAddr', '0.0.0.0') )
		self.setAntennaStr( self.config.Read('Antennas', '1 2 3 4') )
	
	def updateMessages( self, event ):
		tNow = datetime.datetime.now()
		running = int((tNow - self.tStart).total_seconds())
		self.runningTime.SetLabel( '%02d:%02d:%02d' % (running // (60*60), (running // 60) % 60, running % 60) )
		self.time.SetLabel( tNow.strftime('%H:%M:%S') )
		
		if not self.messageQ:
			return
		while 1:
			try:
				d = self.messageQ.get( False )
			except Empty:
				break
			message = ' '.join( str(x) for x in d[1:] )
			if   d[0] == 'Impinj':
				if 'state' in d:
					self.impinjMessages.messageList.SetBackgroundColour( self.LightGreen if d[2] else self.LightRed )
				else:
					self.impinjMessages.write( message )
			elif d[0] == 'Impinj2JChip':
				if 'state' in d:
					self.crossMgrMessages.messageList.SetBackgroundColour( self.LightGreen if d[2] else self.LightRed )
				else:
					self.crossMgrMessages.write( message )
			elif d[0] == 'BackupFile':
				self.backupFile.SetLabel( os.path.basename(d[1]) )

def disable_stdout_buffering():
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w", 0)

redirectFileName = None
mainWin = None
def MainLoop():
	global mainWin, redirectFileName
	
	app = wx.PySimpleApp()
	app.SetAppName("CrossMgrImpinj")

	mainWin = MainWin( None, title=AppVerName, size=(800,1000) )
	
	dataDir = Utils.getHomeDir()
	redirectFileName = os.path.join(dataDir, 'CrossMgrImpinj.log')
	
	# Set up the log file.  Otherwise, show errors on the screen.
	if __name__ == '__main__':
		disable_stdout_buffering()
	else:
		try:
			logSize = os.path.getsize( redirectFileName )
			if logSize > 1000000:
				os.remove( redirectFileName )
		except:
			pass
	
		try:
			app.RedirectStdio( redirectFileName )
		except:
			pass
			
		try:
			with open(redirectFileName, 'a') as pf:
				pf.write( '********************************************\n' )
				pf.write( '%s: %s Started.\n' % (datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), AppVerName) )
		except:
			pass
	
	mainWin.Show()

	# Set the upper left icon.
	try:
		icon = wx.Icon( os.path.join(getImageFolder(), 'CrossMgrImpinj.ico'), wx.BITMAP_TYPE_ICO )
		mainWin.SetIcon( icon )
	except:
		pass

	# Start processing events.
	mainWin.Refresh()
	app.MainLoop()

@atexit.register
def shutdown():
	if mainWin:
		mainWin.shutdown()
	
if __name__ == '__main__':
	MainLoop()
	