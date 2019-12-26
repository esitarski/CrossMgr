import sys
import threading
import socket
import atexit
import time
from roundbutton import RoundButton
import Utils
from six.moves.queue import Queue, Empty
from threading import Thread as Process
from Alien import AlienServer
import Alien
from Alien2JChip import CrossMgrServer
from AutoDetect import AutoDetect, DefaultAlienCmdPort

import wx
import wx.adv
import wx.lib.masked        as masked
import wx.lib.intctrl		as intctrl
import sys
import os
import re
import datetime

if 'WXMAC' in wx.Platform:
	class IpAddrCtrl( wx.TextCtrl ):
		def GetAddress( self ):
			return self.GetValue()
else:
	IpAddrCtrl = masked.IpAddrCtrl

from Version import AppVerName

HeartbeatPort = 3988
CrossMgrPort = 53135
NotifyPort = CrossMgrPort + 1

clipboard_xpm = [
b"16 15 23 1",
b"+ c #769CDA",
b": c #DCE6F6",
b"X c #3365B7",
b"* c #FFFFFF",
b"o c #9AB6E4",
b"< c #EAF0FA",
b"# c #B1C7EB",
b". c #6992D7",
b"3 c #F7F9FD",
b", c #F0F5FC",
b"$ c #A8C0E8",
b"  c None",
b"- c #FDFEFF",
b"& c #C4D5F0",
b"1 c #E2EAF8",
b"O c #89A9DF",
b"= c #D2DFF4",
b"4 c #FAFCFE",
b"2 c #F5F8FD",
b"; c #DFE8F7",
b"% c #B8CCEC",
b"> c #E5EDF9",
b"@ c #648FD6",
b" .....XX        ",
b" .oO+@X#X       ",
b" .$oO+X##X      ",
b" .%$o........   ",
b" .&%$.*=&#o.-.  ",
b" .=&%.*;=&#.--. ",
b" .:=&.*>;=&.... ",
b" .>:=.*,>;=&#o. ",
b" .<1:.*2,>:=&#. ",
b" .2<1.*32,>:=&. ",
b" .32<.*432,>:=. ",
b" .32<.*-432,>:. ",
b" .....**-432,>. ",
b"     .***-432,. ",
b"     .......... "
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

class AdvancedSetup( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Advanced Setup",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		'''
		Alien.ConnectionTimeoutSeconds	= 1		# Interval for connection timeout
		Alien.KeepaliveSeconds			= 2		# Interval to request a Keepalive message
		Alien.RepeatSeconds			= 2		# Interval in which a tag is considered a repeat read.
		'''

		bs = wx.GridBagSizer(vgap=5, hgap=5)

		border = 8
		bs.Add( wx.StaticText(self, wx.ID_ANY, 'Advanced Reader Options:'), pos = (0,0), span=(1, 2), border = border, flag=wx.ALL )
		
		row = 1
		bs.Add( wx.StaticText(self, wx.ID_ANY, 'Repeat Seconds'), pos=(row, 0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.RepeatSeconds = intctrl.IntCtrl( self, wx.ID_ANY, min=1, max=120, limited = True,
			value = Alien.RepeatSeconds, size=(32,-1) )
		bs.Add( self.RepeatSeconds, pos=(row, 1), span=(1,1), border = border, flag=wx.TOP )
		bs.Add( wx.StaticText(self, wx.ID_ANY, 'interval in which multiple tag reads are considered "repeats" and not reported'), pos=(row, 2), span=(1,1), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL )

		row += 1
		self.playSoundsCheckbox = wx.CheckBox( self, wx.ID_ANY, 'Beep on Read' )
		self.playSoundsCheckbox.SetValue( Utils.playBell )
		bs.Add( self.playSoundsCheckbox, pos=(row, 0), span=(1,3), border = border, flag=wx.TOP|wx.LEFT|wx.RIGHT )
		
		row += 1
		self.restoreDefaultButton = wx.Button( self, wx.ID_ANY, 'Restore Defaults' )
		self.restoreDefaultButton.Bind( wx.EVT_BUTTON, self.onRestoreDefault )
		bs.Add( self.restoreDefaultButton, pos=(row, 0), span=(1,3), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER )
		
		row += 1
		bs.Add( wx.StaticText(self, wx.ID_ANY, 'Reminder: Press "Reset" for these changes to take effect.'), pos=(row, 0), span=(1,3), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT )
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		row += 1
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.okBtn, border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		hs.Add( self.cancelBtn, border = border, flag=wx.ALL )
		
		bs.Add( hs, pos=(row, 0), span=(1,3), flag=wx.ALIGN_RIGHT )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onRestoreDefault( self, event ):
		self.RepeatSeconds.SetValue( Alien.RepeatSecondsDefault )
		
	def onOK( self, event ):
		Alien.RepeatSeconds = self.RepeatSeconds.GetValue()
		Utils.playBell = self.playSoundsCheckbox.IsChecked()
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

def setFont( font, w ):
	w.SetFont( font )
	return w

class MainWin( wx.Frame ):
	def __init__( self, parent, id = wx.ID_ANY, title='', size=(200,200) ):
		wx.Frame.__init__(self, parent, id, title, size=size)

		dataDir = Utils.getHomeDir()
		configFileName = os.path.join(dataDir, 'CrossMgrAlien.cfg')
		self.config = wx.Config(appName="CrossMgrAlien",
						vendorName="SmartCyclingSolutions",
						localFilename=configFileName
						)

		ID_MENU_ADVANCECONFIG = wx.NewIdRef()
		ID_MENU_COPYLOGS = wx.NewIdRef()
		ID_MENU_AUTODETECT = wx.NewIdRef()
		self.menuBar = wx.MenuBar(wx.MB_DOCKABLE)
		if 'WXMAC' in wx.Platform:
			self.appleMenu = self.menuBar.OSXGetAppleMenu()
			self.appleMenu.SetTitle("CrossMgrAlien")

			self.appleMenu.Insert(0, wx.ID_ABOUT, "&About")

			self.Bind(wx.EVT_MENU, self.OnAboutBox, id=wx.ID_ABOUT)

			self.editMenu = wx.Menu()
			self.editMenu.Append(wx.MenuItem(self.editMenu, ID_MENU_ADVANCECONFIG,"A&dvanced Configuration"))
			self.editMenu.Append(wx.MenuItem(self.editMenu, ID_MENU_COPYLOGS,"&Copy Logs to Clipboard"))
			self.editMenu.Append(wx.MenuItem(self.editMenu, ID_MENU_AUTODETECT,"&Autodetect Reader"))

			self.Bind(wx.EVT_MENU, self.doAdvanced, id=ID_MENU_ADVANCECONFIG)
			self.Bind(wx.EVT_MENU, self.doCopyToClipboard, id=ID_MENU_COPYLOGS)
			self.Bind(wx.EVT_MENU, self.doAutoDetect, id=ID_MENU_AUTODETECT)
			self.menuBar.Append(self.editMenu, "&Edit")

		else:
			self.fileMenu = wx.Menu()
			self.fileMenu.Append(wx.MenuItem(self.fileMenu, ID_MENU_ADVANCECONFIG,"A&dvanced Configuration"))
			self.fileMenu.Append(wx.MenuItem(self.fileMenu, ID_MENU_COPYLOGS,"&Copy Logs to Clipboard"))
			self.fileMenu.Append(wx.MenuItem(self.fileMenu, ID_MENU_AUTODETECT,"&Autodetect Reader"))
			self.fileMenu.Append(wx.ID_EXIT)
			self.Bind(wx.EVT_MENU, self.doAdvanced, id=ID_MENU_ADVANCECONFIG)
			self.Bind(wx.EVT_MENU, self.doCopyToClipboard, id=ID_MENU_COPYLOGS)
			self.Bind(wx.EVT_MENU, self.doAutoDetect, id=ID_MENU_AUTODETECT)
			self.Bind(wx.EVT_MENU, self.onCloseWindow, id=wx.ID_EXIT)
			self.menuBar.Append(self.fileMenu, "&File")
			self.helpMenu = wx.Menu()
			self.helpMenu.Insert(0, wx.ID_ABOUT, "&About")
			self.Bind(wx.EVT_MENU, self.OnAboutBox, id=wx.ID_ABOUT)
			self.menuBar.Append(self.helpMenu, "&Help")

		self.SetMenuBar(self.menuBar)
		self.SetBackgroundColour( wx.Colour(232,232,232) )
		
		self.LightGreen = wx.Colour(153,255,153)
		self.LightRed = wx.Colour(255,153,153)
		
		font = self.GetFont()
		bigFont = wx.Font( font.GetPointSize() * 1.5, font.GetFamily(), font.GetStyle(), wx.FONTWEIGHT_BOLD )
		titleFont = wx.Font( bigFont.GetPointSize()*2.2, bigFont.GetFamily(), bigFont.GetStyle(), bigFont.GetWeight() )
		
		self.vbs = wx.BoxSizer( wx.VERTICAL )
		
		bs = wx.BoxSizer( wx.HORIZONTAL )
		
		self.reset = RoundButton(self, wx.ID_ANY, 'Reset', size=(80, 80))
		self.reset.SetBackgroundColour( wx.WHITE )
		self.reset.SetForegroundColour( wx.Colour(0,128,128) )
		self.reset.SetFontToFitLabel()	# Use the button's default font, but change the font size to fit the label.
		self.reset.Bind( wx.EVT_BUTTON, self.doReset )
		self.reset.Refresh()
		bs.Add( self.reset, border = 8, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.Add( setFont(titleFont,wx.StaticText(self, wx.ID_ANY, 'CrossMgrAlien')), border = 8, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.AddStretchSpacer()
		bitmap = wx.Bitmap( clipboard_xpm )
		self.copyToClipboard = wx.BitmapButton( self, wx.ID_ANY, bitmap )
		self.copyToClipboard.SetToolTip(wx.ToolTip('Copy Configuration and Logs to Clipboard...'))
		self.copyToClipboard.Bind( wx.EVT_BUTTON, self.doCopyToClipboard )
		bs.Add( self.copyToClipboard, border = 32, flag = wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.tStart = datetime.datetime.now()
		bs.Add( setFont(bigFont,wx.StaticText(self, wx.ID_ANY, 'Last Reset: {}'.format(self.tStart.strftime('%H:%M:%S')))), border = 10, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.runningTime = setFont(bigFont,wx.StaticText(self, wx.ID_ANY, '00:00:00' ))
		bs.Add( self.runningTime, border = 20, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.Add( setFont(bigFont,wx.StaticText(self, wx.ID_ANY, ' / ')), flag=wx.ALIGN_CENTER_VERTICAL )
		self.time = setFont(bigFont, wx.StaticText(self, wx.ID_ANY, '00:00:00' ))
		bs.Add( self.time, flag=wx.ALIGN_CENTER_VERTICAL )
		
		self.vbs.Add( bs, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		fgs = wx.FlexGridSizer( rows = 0, cols = 2, vgap = 4, hgap = 4 )
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
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( setFont(bigFont,wx.StaticText(self, wx.ID_ANY, 'Alien Configuration:')), flag=wx.ALIGN_CENTER_VERTICAL )
		self.autoDetectButton = wx.Button( self, wx.ID_ANY, 'Auto Detect' )
		self.autoDetectButton.Bind( wx.EVT_BUTTON, self.doAutoDetect )
		hs.Add( self.autoDetectButton, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border = 6 )
		
		self.advancedButton = wx.Button(self, wx.ID_ANY, 'Advanced...' )
		self.advancedButton.Bind( wx.EVT_BUTTON, self.doAdvanced )
		hs.Add( self.advancedButton, flag=wx.LEFT, border = 6 )
		
		gbs.Add( hs, pos=(iRow,0), span=(1,2), flag=wx.ALIGN_LEFT )
		iRow += 1
		
		gbs.Add( wx.StaticText(self, wx.ID_ANY, 'Antennas:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM )
		
		gs = wx.GridSizer( rows=0, cols=4, hgap=2, vgap=2 )
		self.antennas = []
		for i in range(4):
			gs.Add( wx.StaticText(self, wx.ID_ANY, '{}'.format(i)), flag=wx.ALIGN_CENTER )
		for i in range(4):
			cb = wx.CheckBox( self, wx.ID_ANY, '')
			if i < 2:
				cb.SetValue( True )
			cb.Bind( wx.EVT_CHECKBOX, lambda x: self.getAntennaStr() )
			gs.Add( cb, flag=wx.ALIGN_CENTER )
			self.antennas.append( cb )
		
		gbs.Add( gs, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		
		iRow += 1
		
		gbs.Add( wx.StaticText(self, wx.ID_ANY, 'Notify Address:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		
		hb = wx.BoxSizer( wx.HORIZONTAL )
		ips = Utils.GetAllIps()
		self.notifyHost = wx.Choice( self, choices = ips )
		hb.Add( self.notifyHost )
		hb.Add( wx.StaticText(self, label=' : {}'.format(NotifyPort) ), flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(iRow ,1), span=(1,1) )
		
		iRow += 1
		self.listenForHeartbeat = wx.CheckBox( self, label='Listen for Alien Heartbeat on Port: {}'.format(HeartbeatPort), style=wx.ALIGN_LEFT )
		self.listenForHeartbeat.SetValue( True )
		gbs.Add( self.listenForHeartbeat, pos=(iRow, 0), span=(1,2) )
		
		iRow += 1
		gbs.Add( wx.StaticText(self, label='Alien Cmd Address:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		hb = wx.BoxSizer( wx.HORIZONTAL )
		self.cmdHost = IpAddrCtrl( self, wx.ID_ANY, style = wx.TE_PROCESS_TAB )

		hb.Add( self.cmdHost )
		hb.Add( wx.StaticText(self,label=' : '), flag=wx.ALIGN_CENTER_VERTICAL )
		self.cmdPort = intctrl.IntCtrl( self, size=( 50, -1 ), min=0, max=999999 )
		hb.Add( self.cmdPort, flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		gbs.Add( wx.StaticText(self, label='Backup File:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT )
		self.backupFile = wx.StaticText( self, label='' )
		gbs.Add( self.backupFile, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		#------------------------------------------------------------------------------------------------
		# CrossMgr configuration.
		#
		gbs = wx.GridBagSizer( 4, 4 )
		fgs.Add( gbs, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		gbs.Add( setFont(bigFont,wx.StaticText(self, label='CrossMgr Configuration:')), pos=(0,0), span=(1,2), flag=wx.ALIGN_LEFT )
		gbs.Add( wx.StaticText(self, label='CrossMgr Address:'), pos=(1,0), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		
		hb = wx.BoxSizer( wx.HORIZONTAL )
		self.crossMgrHost = IpAddrCtrl( self, style = wx.TE_PROCESS_TAB )
		hb.Add( self.crossMgrHost, flag=wx.ALIGN_LEFT )
		hb.Add( wx.StaticText( self,label=' : 53135' ), flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(1,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		#------------------------------------------------------------------------------------------------
		# Add messages
		#
		self.alienMessagesText = wx.TextCtrl( self, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(-1,400) )
		fgs.Add( self.alienMessagesText, flag=wx.EXPAND, proportion=2 )
		self.alienMessages = MessageManager( self.alienMessagesText )
		
		self.crossMgrMessagesText = wx.TextCtrl( self, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(-1,400) )
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

	def OnAboutBox(self, e):
			description = """CrossMgrAlien is an Impinj interface to CrossMgr
	"""

			licence = """CrossMgrAlien is free software; you can redistribute 
	it and/or modify it under the terms of the GNU General Public License as 
	published by the Free Software Foundation; either version 2 of the License, 
	or (at your option) any later version.

	CrossMgrImpinj is distributed in the hope that it will be useful, 
	but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
	See the GNU General Public License for more details. You should have 
	received a copy of the GNU General Public License along with File Hunter; 
	if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
	Suite 330, Boston, MA  02111-1307  USA"""

			info = wx.adv.AboutDialogInfo()

			crossMgrPng = Utils.getImageFolder() + '/CrossMgrAlien.png'
			info.SetIcon(wx.Icon(crossMgrPng, wx.BITMAP_TYPE_PNG))
			info.SetName('CrossMgrAlien')
			info.SetVersion(AppVerName.split(' ')[1])
			info.SetDescription(description)
			info.SetCopyright('(C) 2020 Edward Sitarski')
			info.SetWebSite('http://www.sites.google.com/site/crossmgrsoftware/')
			info.SetLicence(licence)

			wx.adv.AboutBox(info, self)


	def start( self ):
		self.dataQ = Queue()
		self.messageQ = Queue()
		self.shutdownQ = Queue()	# Queue to tell the Alien monitor to shut down.
		
		self.alienProcess = Process( name='AlienProcess', target=AlienServer,
			args=(self.dataQ, self.messageQ, self.shutdownQ,
					self.getNotifyHost(), NotifyPort, HeartbeatPort, self.getAntennaStr(),
					self.listenForHeartbeat.GetValue(), self.cmdHost.GetAddress(), self.cmdPort.GetValue() ) )
		self.alienProcess.daemon = True
		
		self.crossMgrProcess = Process( name='CrossMgrProcess', target=CrossMgrServer,
			args=(self.dataQ, self.messageQ, self.shutdownQ, self.getCrossMgrHost(), CrossMgrPort) )
		self.crossMgrProcess.daemon = True
		
		self.alienProcess.start()
		self.crossMgrProcess.start()
	
	def doAdvanced( self, event ):
		dlg = AdvancedSetup( self )
		dlg.ShowModal()
		dlg.Destroy()
		self.writeOptions()
	
	def shutdown( self ):
		self.alienProcess = None
		self.crossMgrProcess = None
		self.messageQ = None
		self.dataQ = None
		self.shutdownQ = None
		
	def gracefulShutdown( self ):
		# Shutdown the CrossMgr process by sending it a shutdown command.
		if self.shutdownQ:
			self.shutdownQ.put( 'shutdown' )
			self.shutdownQ.put( 'shutdown' )
			self.shutdownQ.put( 'shutdown' )
		
		if self.dataQ:
			self.dataQ.put( 'shutdown' )
		
		if self.crossMgrProcess:
			self.crossMgrProcess.join()
		if self.alienProcess:
			self.alienProcess.join()
		
		self.crossMgrProcess = None
		self.alienProcess = None
	
	def doReset( self, event, confirm = True ):
		if confirm:
			dlg = wx.MessageDialog(self, 'Reset CrossMgrAlien Adapter?',
									'Confirm Reset',
									wx.OK | wx.CANCEL | wx.ICON_WARNING )
			ret = dlg.ShowModal()
			dlg.Destroy()
			if ret != wx.ID_OK:
				return
				
		self.reset.Enable( False )		# Prevent multiple clicks while shutting down.
		self.writeOptions()
		
		self.gracefulShutdown()
		
		self.alienMessages.clear()
		self.crossMgrMessages.clear()
		
		self.shutdown()
		self.reset.Enable( True )
		
		wx.CallAfter( self.start )
	
	def doAutoDetect( self, event ):
		wx.BeginBusyCursor()
		self.gracefulShutdown()
		self.shutdown()
		alienHost, crossmgrHost = AutoDetect()
		wx.EndBusyCursor()
		
		if alienHost and crossmgrHost:
			self.setNotifyHost( crossmgrHost ) # Assumes CrossMgr is on the same computer as CrossMgrAlien.
			
			self.cmdHost.SetValue( alienHost )
			self.cmdPort.SetValue( str(DefaultAlienCmdPort) )
			self.crossMgrHost.SetValue( crossmgrHost )
			
			self.listenForHeartbeat.SetValue( False )
		else:
			dlg = wx.MessageDialog(self, 'Auto Detect Failed.\nCheck that reader has power and is connected to the router.',
									'Auto Detect Failed',
									wx.OK | wx.ICON_INFORMATION )
			dlg.ShowModal()
			dlg.Destroy()
			
		self.doReset( event, False )
	
	def onCloseWindow( self, event ):
		wx.Exit()
		
	def doCopyToClipboard( self, event ):
		cc = [
			'Configuration: CrossMgrAlien',
			'    NotifyHost:    {}'.format(self.getNotifyHost()),
			'    NotifyPort:    {}'.format(NotifyPort),
			'    RunningTime:   {}'.format(self.runningTime.GetLabel()),
			'    Time:          {}'.format(self.time.GetLabel()),
			'    BackupFile:    {}'.format(self.backupFile.GetLabel()),
			'',
			'Configuration: Alien:',
			'    ListenForAlienHeartbeat: {}'.format('True' if self.listenForHeartbeat.GetValue() else 'False'),
			'    Antennas:      {}'.format(self.getAntennaStr()),
			'    HeartbeatPort: {}'.format(HeartbeatPort),
			'    AlienCmdHost:  {}'.format(self.cmdHost.GetAddress()),
			'    AlienCmdPort:  {}'.format(self.cmdPort.GetValue()),
			'',
			'    RepeatSeconds: {}'.format(Alien.RepeatSeconds),
			'',
			'Configuration: CrossMgr',
			'    CrossMgrHost:  {}'.format(self.getCrossMgrHost()),
			'    CrossMgrPort:  {}'.format(CrossMgrPort),
		]
		cc.append( '\nLog: Alien' )
		log = self.alienMessagesText.GetValue()
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

	def getNotifyHost( self ):
		s = self.notifyHost.GetSelection()
		return self.notifyHost.GetString(s) if s != wx.NOT_FOUND else None
	
	def setNotifyHost( self, notifyHost ):
		for i, s in enumerate(self.notifyHost.GetItems()):
			if s == notifyHost:
				self.notifyHost.SetSelection( i )
				return
		self.notifyHost.SetSelection( 0 )
	
	def getCrossMgrHost( self ):
		return self.crossMgrHost.GetAddress()
		
	def getAntennaStr( self ):
		s = []
		for i in range(4):
			if self.antennas[i].GetValue():
				s.append( '%d' % i )
		if not s:
			# Ensure that at least one antenna is selected.
			self.antennas[0].SetValue( True )
			s.append( '0' )
		return ' '.join( s )
		
	def setAntennaStr( self, s ):
		antennas = set( int(a) for a in s.split() )
		for i in range(4):
			self.antennas[i].SetValue( i in antennas )
	
	def writeOptions( self ):
		self.config.Write( 'CrossMgrHost', self.getCrossMgrHost() )
		self.config.Write( 'ListenForAlienHeartbeat', 'True' if self.listenForHeartbeat.GetValue() else 'False' )
		self.config.Write( 'AlienCmdAddr', self.cmdHost.GetAddress() )
		self.config.Write( 'AlienCmdPort', str(self.cmdPort.GetValue()) )
		self.config.Write( 'Antennas', self.getAntennaStr() )
		self.config.Write( 'RepeatSeconds', '{}'.format(Alien.RepeatSeconds) )
		self.config.Write( 'PlaySounds', '{}'.format(Utils.playBell) )
		s = self.notifyHost.GetSelection()
		if s != wx.NOT_FOUND:
			self.config.Write( 'NotifyHost', self.notifyHost.GetString(s) )
		self.config.Flush()
	
	def readOptions( self ):
		self.crossMgrHost.SetValue( self.config.Read('CrossMgrHost', Utils.DEFAULT_HOST) )
		self.listenForHeartbeat.SetValue( self.config.Read('ListenForAlienHeartbeat', 'True').upper()[:1] == 'T' )
		Utils.playBell = (self.config.Read('PlaySounds', 'True').upper()[:1] == 'T')
		self.cmdHost.SetValue( self.config.Read('AlienCmdAddr', '0.0.0.0') )
		self.cmdPort.SetValue( int(self.config.Read('AlienCmdPort', '0')) )
		self.setAntennaStr( self.config.Read('Antennas', '0 1') )
		Alien.RepeatSeconds = int(self.config.Read( 'RepeatSeconds', '{}'.format(Alien.RepeatSeconds)))
		notifyHost = self.config.Read('NotifyHost', Utils.DEFAULT_HOST)
		self.setNotifyHost( notifyHost )
	
	def updateMessages( self, event ):
		tNow = datetime.datetime.now()
		running = int((tNow - self.tStart).total_seconds())
		self.runningTime.SetLabel( '{:02d}:{:02d}:{:02d}'.format(running // (60*60), (running // 60) % 60, running % 60) )
		self.time.SetLabel( tNow.strftime('%H:%M:%S') )
		
		if not self.messageQ:
			return
			
		while 1:
			try:
				d = self.messageQ.get( False )
			except Empty:
				break
			message = ' '.join( str(x) for x in d[1:] )
			if   d[0] == 'Alien':
				if 'state' in d:
					self.alienMessages.messageList.SetBackgroundColour( self.LightGreen if d[2] else self.LightRed )
				else:
					self.alienMessages.write( message )
			elif d[0] == 'Alien2JChip':
				if 'state' in d:
					self.crossMgrMessages.messageList.SetBackgroundColour( self.LightGreen if d[2] else self.LightRed )
				else:
					self.crossMgrMessages.write( message )
			elif d[0] == 'CmdHost':
				cmdHost, cmdPort = d[1].split(':')
				self.cmdHost.SetValue( cmdHost )
				self.cmdPort.SetValue( int(cmdPort) )
			elif d[0] == 'BackupFile':
				self.backupFile.SetLabel( d[1] )

def disable_stdout_buffering():
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w")
		
mainWin = None
redirectFileName = None
def MainLoop():
	global mainWin, redirectFileName
	
	app = wx.App(False)
	app.SetAppName("CrossMgrAlien")

	mainWin = MainWin( None, title=AppVerName, size=(800,min(int(wx.GetDisplaySize()[1]*0.85),1000)) )
	
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
		
		try:
			with open(redirectFileName, 'a') as pf:
				pf.write( '********************************************\n' )
				pf.write( '{}: {} Started.\n'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), AppVerName) )
		except:
			pass
	
	mainWin.Show()

	# Set the upper left icon.
	try:
		icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'CrossMgrAlien.ico'), wx.BITMAP_TYPE_ICO )
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
	
