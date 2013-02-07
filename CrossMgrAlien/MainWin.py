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
from Alien import AlienServer
from Alien2JChip import CrossMgrServer

import wx
import wx.lib.masked             as masked
import wx.lib.intctrl			as intctrl
import sys
import os
import re
import datetime

from Version import AppVerName

HeartbeatPort = 3988
CrossMgrPort = 53135
NotifyPort = CrossMgrPort + 1

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

		self.config = wx.Config(appName="CrossMgrAlien",
						vendorName="SmartCyclingSolutions",
						style=wx.CONFIG_USE_LOCAL_FILE)
						
		self.SetBackgroundColour( wx.Colour(232,232,232) )
		
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
		bs.Add( setFont(italicFont,wx.StaticText(self, wx.ID_ANY, 'CrossMgrAlien')), border = 8, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.AddStretchSpacer()
		self.tStart = datetime.datetime.now()
		bs.Add( setFont(bigFont,wx.StaticText(self, wx.ID_ANY, 'Last Reset: %s' % self.tStart.strftime('%H:%M:%S'))), border = 32, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
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
		# Alien configuration.
		#
		gbs = wx.GridBagSizer( 4, 4 )
		fgs.Add( gbs, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		iRow = 0
		gbs.Add( setFont(bigFont,wx.StaticText(self, wx.ID_ANY, 'Alien Configuration:')), pos=(iRow,0), span=(1,2), flag=wx.ALIGN_LEFT )
		iRow += 1
		gbs.Add( wx.StaticText(self, wx.ID_ANY, 'Notify Address:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		
		hb = wx.BoxSizer( wx.HORIZONTAL )
		ips = Utils.GetAllIps()
		self.notifyHost = wx.Choice( self, wx.ID_ANY, choices = ips )
		hb.Add( self.notifyHost )
		hb.Add( wx.StaticText(self, wx.ID_ANY, ' : %d' % NotifyPort ), flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(iRow ,1), span=(1,1) )
		
		iRow += 1
		self.listenForHeartbeat = wx.CheckBox( self, wx.ID_ANY, 'Listen for Alien Heartbeat', style=wx.ALIGN_LEFT )
		self.listenForHeartbeat.SetValue( True )
		gbs.Add( self.listenForHeartbeat, pos=(iRow, 1), span=(1,1) )
		
		iRow += 1
		gbs.Add( wx.StaticText(self, wx.ID_ANY, 'Heartbeat Port:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT )
		self.heartbeatPort = wx.StaticText( self, wx.ID_ANY, '3988' )
		gbs.Add( self.heartbeatPort, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		gbs.Add( wx.StaticText(self, wx.ID_ANY, 'Cmd Address:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT )
		hb = wx.BoxSizer( wx.HORIZONTAL )
		self.cmdHost = masked.IpAddrCtrl( self, wx.ID_ANY, style = wx.TE_PROCESS_TAB )
		hb.Add( self.cmdHost )
		hb.Add( wx.StaticText(self, wx.ID_ANY, ' : '), flag=wx.ALIGN_CENTER_VERTICAL )
		self.cmdPort = intctrl.IntCtrl( self, size=( 50, -1 ), min=0, max=999999 )
		hb.Add( self.cmdPort, flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		gbs.Add( wx.StaticText(self, wx.ID_ANY, 'Backup File:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT )
		self.backupFile = wx.StaticText( self, wx.ID_ANY, '' )
		gbs.Add( self.backupFile, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		#------------------------------------------------------------------------------------------------
		# CrossMgr configuration.
		#
		gbs = wx.GridBagSizer( 4, 4 )
		fgs.Add( gbs, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		gbs.Add( setFont(bigFont,wx.StaticText(self, wx.ID_ANY, 'CrossMgr Configuration:')), pos=(0,0), span=(1,2), flag=wx.ALIGN_LEFT )
		gbs.Add( wx.StaticText(self, wx.ID_ANY, 'CrossMgr Address:'), pos=(1,0), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		
		hb = wx.BoxSizer( wx.HORIZONTAL )
		self.crossMgrHost = masked.IpAddrCtrl( self, wx.ID_ANY, style = wx.TE_PROCESS_TAB )
		hb.Add( self.crossMgrHost, flag=wx.ALIGN_LEFT )
		hb.Add( wx.StaticText( self, wx.ID_ANY, ' : 53135' ), flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(1,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		#------------------------------------------------------------------------------------------------
		# Add messages
		#
		self.alienMessagesText = wx.TextCtrl( self, wx.ID_ANY, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(-1,400) )
		fgs.Add( self.alienMessagesText, flag=wx.EXPAND, proportion=2 )
		self.alienMessages = MessageManager( self.alienMessagesText )
		
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
		self.shutdownQ = Queue()	# Queue to tell the Alien monitor to shut down.
		
		self.alienProcess = Process( name='AlienProcess', target=AlienServer,
			args=(self.dataQ, self.messageQ, self.shutdownQ,
					self.getNotifyHost(), NotifyPort, HeartbeatPort,
					self.listenForHeartbeat.GetValue(), self.cmdHost.GetAddress(), self.cmdPort.GetValue() ) )
		self.alienProcess.daemon = True
		
		self.crossMgrProcess = Process( name='CrossMgrProcess', target=CrossMgrServer,
			args=(self.dataQ, self.messageQ, self.shutdownQ, self.getCrossMgrHost(), CrossMgrPort) )
		self.crossMgrProcess.daemon = True
		
		self.alienProcess.start()
		self.crossMgrProcess.start()
	
	def shutdown( self ):
		self.alienProcess = None
		self.crossMgrProcess = None
		self.messageQ = None
		self.dataQ = None
		self.shutdownQ = None
	
	def doReset( self, event ):
		dlg = wx.MessageDialog(self, 'Reset CrossMgrAlien Adapter?',
								'Confirm Reset',
								wx.OK | wx.CANCEL | wx.ICON_WARNING )
		ret = dlg.ShowModal()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return
		self.writeOptions()
		
		# Shutdown the CrossMgr process by sending it a shutdown command.
		self.shutdownQ.put( 'shutdown' )
		self.shutdownQ.put( 'shutdown' )
		self.shutdownQ.put( 'shutdown' )
		self.dataQ.put( 'shutdown' )
		
		self.crossMgrProcess.join()
		self.alienProcess.join()
		
		self.crossMgrProcess = None
		self.alienProcess = None
		
		self.alienMessages.clear()
		self.crossMgrMessages.clear()
		self.shutdown()
		wx.CallAfter( self.start )
	
	def onCloseWindow( self, event ):
		wx.Exit()

	def getNotifyHost( self ):
		s = self.notifyHost.GetSelection()
		return self.notifyHost.GetString(s) if s != wx.NOT_FOUND else None
	
	def getCrossMgrHost( self ):
		return self.crossMgrHost.GetAddress()
	
	def writeOptions( self ):
		self.config.Write( 'CrossMgrHost', self.getCrossMgrHost() )
		self.config.Write( 'ListenForAlienHeartbeat', str(self.listenForHeartbeat.GetValue()) )
		self.config.Write( 'AlienCmdAddr', self.cmdHost.GetAddress() )
		self.config.Write( 'AlienCmdPort', str(self.cmdPort.GetValue()) )
		s = self.notifyHost.GetSelection()
		if s != wx.NOT_FOUND:
			self.config.Write( 'NotifyHost', self.notifyHost.GetString(s) )
	
	def readOptions( self ):
		self.crossMgrHost.SetValue( self.config.Read('CrossMgrHost', Utils.DEFAULT_HOST) )
		self.listenForHeartbeat.SetValue( self.config.Read('ListenForAlienHeartbeat', 'True').upper() == 'T' )
		self.cmdHost.SetValue( self.config.Read('AlienCmdAddr', '0.0.0.0') )
		self.cmdPort.SetValue( int(self.config.Read('AlienCmdPort', '0')) )
		notifyHost = self.config.Read('NotifyHost', Utils.DEFAULT_HOST)
		for i, s in enumerate(self.notifyHost.GetItems()):
			if s == notifyHost:
				self.notifyHost.SetSelection( i )
				return
		self.notifyHost.SetSelection( 0 )
	
	def updateMessages( self, event ):
		tNow = datetime.datetime.now()
		running = int((tNow - self.tStart).total_seconds())
		self.runningTime.SetLabel( '%02d:%02d:%02d' % (running // (60*60), (running // 60) % 60, running % 60) )
		self.time.SetLabel( tNow.strftime('%H:%M:%S') )
		while 1:
			try:
				d = self.messageQ.get( False )
			except Empty:
				break
			message = ' '.join( str(x) for x in d[1:] )
			if   d[0] == 'Alien':
				self.alienMessages.write( message )
			elif d[0] == 'Alien2JChip':
				self.crossMgrMessages.write( message )
			elif d[0] == 'CmdAddr':
				cmdHost, cmdPort = d[1].split(':')
				self.cmdHost.SetValue( cmdHost )
				self.cmdPort.SetValue( int(cmdPort) )
			elif d[0] == 'BackupFile':
				self.backupFile.SetLabel( os.path.basename(d[1]) )

def disable_stdout_buffering():
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w", 0)
		
mainWin = None
def MainLoop():
	global mainWin
	
	app = wx.PySimpleApp()
	app.SetAppName("CrossMgrAlien")

	mainWin = MainWin( None, title=AppVerName, size=(800,600) )
	
	dataDir = Utils.getHomeDir()
	redirectFileName = os.path.join(dataDir, 'CrossMgrAlien.log')
			
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
	
	mainWin.Show()

	# Set the upper left icon.
	try:
		icon = wx.Icon( os.path.join(getImageFolder(), 'CrossMgrAlien.ico'), wx.BITMAP_TYPE_ICO )
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