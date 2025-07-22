import os
import sys
import datetime

import wx
import wx.lib.masked			as masked
import wx.adv

import asyncio
from wxasync import AsyncBind, WxAsyncApp, StartCoroutine, AsyncShowDialogModal

import Utils
import Ubidium
from Ubidium import UbidiumServer
import Ubidium2JChip
from Ubidium2JChip import CrossMgrServer
from roundbutton import RoundButton

from Version import AppVerName

CrossMgrPort = 53135
UbidiumInboundPort = 443

if 'WXMSW' in wx.Platform:
	IpAddrCtrl = masked.IpAddrCtrl
else:
	class IpAddrCtrl( wx.TextCtrl ):
		def GetAddress( self ):
			ipaddress = self.GetValue()
			return ipaddress.strip()

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

class MessageManager:
	MessagesMax = 400	# Maximum number of messages before we start throwing some away.

	def __init__( self, messageList ):
		self.messageList = messageList
		self.messageList.SetDoubleBuffered( True )
		AsyncBind( wx.EVT_RIGHT_DOWN, self.skip, self.messageList )
		self.clear()
		
	async def skip(self, evt):
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

		dataDir = Utils.getHomeDir()
		configFileName = os.path.join(dataDir, 'CrossMgrUbidium.cfg')
		self.config = wx.Config(
			appName="CrossMgrUbidium",
			vendorName="SmartCyclingSolutions",
			localFilename=configFileName
		)
		
		ID_MENU_COPYLOGS = wx.NewIdRef()
		self.menuBar = wx.MenuBar(wx.MB_DOCKABLE)
		if 'WXMAC' in wx.Platform:
			self.appleMenu = self.menuBar.OSXGetAppleMenu()
			self.appleMenu.SetTitle("CrossMgrUbidium")

			item = self.appleMenu.Insert(0, wx.ID_ABOUT, "&About")

			self.Bind(wx.EVT_MENU, self.OnAboutBox, item)

			self.editMenu = wx.Menu()
			item = self.editMenu.Append(wx.MenuItem(self.editMenu, ID_MENU_COPYLOGS,"&Copy Logs to Clipboard"))

			self.Bind( wx.EVT_MENU, self.doCopyToClipboard, self.editMenu, item )
			self.menuBar.Append(self.editMenu, "&Edit")

		else:
			self.fileMenu = wx.Menu()
			item = self.fileMenu.Append(wx.MenuItem(self.fileMenu, ID_MENU_COPYLOGS,"&Copy Logs to Clipboard"))
			self.Bind( wx.EVT_MENU, self.doCopyToClipboard, item )
			item = self.fileMenu.Append(wx.ID_EXIT)
			self.Bind( wx.EVT_MENU, self.onCloseWindow, item )
			self.menuBar.Append(self.fileMenu, "&File")
			self.helpMenu = wx.Menu()
			item = self.helpMenu.Insert(0, wx.ID_ABOUT, "&About")
			self.Bind( wx.EVT_MENU, self.OnAboutBox, item )
			self.menuBar.Append(self.helpMenu, "&Help")

		self.SetMenuBar( self.menuBar )
		
		self.LightGreen = wx.Colour(153,255,153)
		self.LightRed = wx.Colour(255,153,153)
		
		font = self.GetFont()
		bigFont = wx.Font( wx.FontInfo(int(font.GetPointSize() * 1.2)).Bold() )
		titleFont = wx.Font( wx.FontInfo(int(font.GetPointSize() * 2.2)).Bold() )
		
		vbs = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( vbs )
		
		bs = wx.BoxSizer( wx.HORIZONTAL )
		
		self.reset = RoundButton(self, label='Reset', size=(80, 80))
		#self.reset.SetBackgroundColour( wx.WHITE )
		self.reset.SetForegroundColour( wx.Colour(0,128,128) )
		self.reset.SetFontToFitLabel()	# Use the button's default font, but change the font size to fit the label.
		AsyncBind( wx.EVT_BUTTON, self.doReset, self.reset )
		self.reset.Refresh()
		bs.Add( self.reset, border = 8, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.Add( setFont(titleFont,wx.StaticText(self, label='CrossMgrUbidium')), border = 8, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.AddStretchSpacer()
		bitmap = wx.Bitmap( clipboard_xpm )
		self.copyToClipboard = wx.BitmapButton( self, bitmap=bitmap )
		self.copyToClipboard.SetToolTip(wx.ToolTip('Copy Configuration and Logs to Clipboard...'))
		self.copyToClipboard.Bind( wx.EVT_BUTTON, self.doCopyToClipboard )
		bs.Add( self.copyToClipboard, border = 32, flag = wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.tStart = datetime.datetime.now()
		bs.Add( setFont(bigFont,wx.StaticText(self, label='Last Reset: {}'.format(self.tStart.strftime('%H:%M:%S')))), border=10, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.runningTime = setFont(bigFont,wx.StaticText(self, label='00:00:00' ))
		bs.Add( self.runningTime, border = 20, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.Add( setFont(bigFont,wx.StaticText(self, label=' / ')), flag=wx.ALIGN_CENTER_VERTICAL )
		self.time = setFont(bigFont, wx.StaticText(self, label='00:00:00' ))
		bs.Add( self.time, flag=wx.ALIGN_CENTER_VERTICAL )
		
		vbs.Add( bs, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		fgs = wx.FlexGridSizer( rows = 2, cols = 2, vgap = 4, hgap = 4 )
		fgs.AddGrowableRow( 1 )
		fgs.AddGrowableCol( 0 )
		fgs.AddGrowableCol( 1 )
		fgs.SetFlexibleDirection( wx.BOTH )
		
		vbs.Add( fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		#------------------------------------------------------------------------------------------------
		# Ubidium configuration.
		#
		ucs = wx.BoxSizer( wx.VERTICAL )
		fgs.Add( ucs, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		ucs.Add( setFont(bigFont,wx.StaticText(self, label='Ubidium Configuration:')) )
		hh = wx.BoxSizer( wx.HORIZONTAL )
		hh.Add( wx.StaticText(self, label='Ubidium Inbound Port:'), flag=wx.ALIGN_CENTER_VERTICAL )
		hh.Add( wx.StaticText( self, label=f'{UbidiumInboundPort}' ), flag=wx.ALIGN_CENTER_VERTICAL )
		ucs.Add( hh, flag=wx.ALL, border=4 )
		
		hh = wx.BoxSizer( wx.HORIZONTAL )
		hh.Add( wx.StaticText(self, label='Backup File:') )
		self.backupFile = wx.StaticText( self, label='<<< Waiting for Ubidium Backup File >>>            ' )
		hh.Add( self.backupFile )
		ucs.Add( hh, flag=wx.ALL, border=4 )
		
		#------------------------------------------------------------------------------------------------
		# CrossMgr configuration.
		#
		cmcs = wx.BoxSizer( wx.VERTICAL )
		fgs.Add( cmcs, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		cmcs.Add( setFont(bigFont,wx.StaticText(self, label='CrossMgr Configuration:')) )
		hh = wx.BoxSizer( wx.HORIZONTAL )
		hh.Add( wx.StaticText(self, label='CrossMgr Address:'), flag=wx.ALIGN_CENTER_VERTICAL )
		self.crossMgrHost = IpAddrCtrl( self, style = wx.TE_PROCESS_TAB )
		hh.Add( self.crossMgrHost, flag=wx.ALIGN_LEFT )
		hh.Add( wx.StaticText( self, label=' : 53135' ), flag=wx.ALIGN_CENTER_VERTICAL )
		cmcs.Add( hh, flag=wx.ALL, border=4 )
		
		#------------------------------------------------------------------------------------------------
		# Add messages
		#
		self.ubidiumMessagesText = wx.TextCtrl( self, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(-1,400) )
		fgs.Add( self.ubidiumMessagesText, flag=wx.EXPAND, proportion=2 )
		self.ubidiumMessages = MessageManager( self.ubidiumMessagesText )
		
		self.crossMgrMessagesText = wx.TextCtrl( self, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(-1,400) )
		fgs.Add( self.crossMgrMessagesText, flag=wx.EXPAND, proportion=2 )
		self.crossMgrMessages = MessageManager( self.crossMgrMessagesText )
		self.fgs = fgs
		
		self.Bind( wx.EVT_CLOSE, self.onCloseWindow )
		self.SetSizer( vbs )
		
		self.readOptions()
		StartCoroutine( self.start, self )		

	def OnAboutBox(self, e):
			description = """CrossMgrUbidium is an Ubidium interface to CrossMgr
	"""

			licence = """CrossMgrUbidium is free software; you can redistribute 
	it and/or modify it under the terms of the GNU General Public License as 
	published by the Free Software Foundation; either version 2 of the License, 
	or (at your option) any later version.

	CrossMgrUbidium is distributed in the hope that it will be useful, 
	but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
	See the GNU General Public License for more details. You should have 
	received a copy of the GNU General Public License along with File Hunter; 
	if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
	Suite 330, Boston, MA  02111-1307  USA"""

			info = wx.adv.AboutDialogInfo()

			crossMgrPng = os.path.join( Utils.getImageFolder(), 'CrossMgrUbidium.png' )
			info.SetIcon(wx.Icon(crossMgrPng, wx.BITMAP_TYPE_PNG))
			info.SetName('CrossMgrUbidium')
			info.SetVersion(AppVerName.split(' ')[1])
			info.SetDescription(description)
			info.SetCopyright('(C) 2025 Edward Sitarski')
			info.SetWebSite('https://github.com/esitarski/CrossMgr')
			info.SetLicence(licence)

			wx.adv.AboutBox(info, self)

	def readerStatusCB( self ):
		return

	async def start( self ):
		if not hasattr(self, 'dataQ') or not self.dataQ:
			self.dataQ = asyncio.Queue()
			self.messageQ = asyncio.Queue()
			#------------------------------------------------------------------------------------------------
			# Create a timer to update the messages.
			#		
			StartCoroutine( self.updateMessages, self )		

		self.readerStatusCB()
		
		await UbidiumServer( self.dataQ, self.messageQ, None, None )
		CrossMgrServer(self.dataQ, self.messageQ, self.getCrossMgrHost(), CrossMgrPort )
	
	def shutdown( self ):
		if hasattr(self, 'dataQ'):
			delattr( self, 'dataQ' )
			delattr( self, 'messageQ' )
	
	async def doReset( self, event, confirm = True ):
		if confirm:
			dlg = wx.MessageDialog(self, 'Reset CrossMgrUbidium Adapter?',
									'Confirm Reset',
									wx.OK | wx.CANCEL | wx.ICON_WARNING )
			ret = dlg.ShowModal()
			dlg.Destroy()
			if ret != wx.ID_OK:
				return
		
		self.reset.Enable( False )		# Prevent multiple clicks while shutting down.
		self.writeOptions()
		
		await self.gracefulShutdown()
		
		self.ubidiumMessages.clear()
		self.crossMgrMessages.clear()
		self.shutdown()
		
		self.reset.Enable( True )
		
		await self.start()
		
	async def gracefulShutdown( self ):
		# Shutdown the async processes.
		Ubidium2JChip.Shutdown()
		await self.dataQ.put( 'shutdown' )
		await self.messageQ.put( 'shutdown' )
		await Ubidium.Shutdown()
	
	def onCloseWindow( self, event ):
		self.gracefulShutdown()
		wx.Exit()
		
	def doCopyToClipboard( self, event ):
		cc = [
			AppVerName,
			'Configuration: CrossMgrUbidium',
			f'    RunningTime:   {self.runningTime.GetLabel()}',
			f'    Time:          {self.time.GetLabel()}',
			f'    BackupFile:    {self.backupFile.GetLabel()}',
			'',
			'Configuration: Ubidium:',
			f'    UbidiumPort:   {UbidiumInboundPort}',
			'',
			'Configuration: CrossMgr',
			f'    CrossMgrHost:  {self.getCrossMgrHost()}',
			f'    CrossMgrPort:  {CrossMgrPort}',
		]
		cc.append( '\nLog: Ubidium' )
		log = self.ubidiumMessagesText.GetValue()
		cc.extend( ['    ' + line for line in log.split('\n')] )
		
		cc.append( '\nLog: CrossMgr' )
		log = self.crossMgrMessagesText.GetValue()
		cc.extend( ['    ' + line for line in log.split('\n')] )
		
		cc.append( '\nLog: Application\n' )
		try:
			with open(redirectFileName, 'r', encoding='utf8') as fp:
				for line in fp:
					cc.append( line )
		except Exception:
			pass
		
		if wx.TheClipboard.Open():
			do = wx.TextDataObject()
			do.SetText( '\n'.join(cc) )
			wx.TheClipboard.SetData(do)
			wx.TheClipboard.Close()
			with wx.MessageDialog(self, 'Configuration and Logs copied to the Clipboard.',
									'Copy to Clipboard Succeeded',
									wx.OK | wx.ICON_INFORMATION ) as dlg:
				dlg.ShowModal()
		else:
			with wx.MessageDialog(self, 'Cannot Open Clipboard.',
									'Cannot Open Clipboard.',
									wx.OK | wx.ICON_INFORMATION ) as dlg:
				dlg.ShowModal()

	def getCrossMgrHost( self ):
		return self.crossMgrHost.GetAddress()
		
	def writeOptions( self ):
		self.config.Write( 'CrossMgrHost', self.getCrossMgrHost() )
		#self.config.Write( 'UseHostName', 'True' if self.useHostName.GetValue() else 'False' )
		
		self.config.Write( 'PlaySounds', f'{Utils.playBell}' )

		self.config.Flush()
	
	def readOptions( self ):
		self.crossMgrHost.SetValue( self.config.Read('CrossMgrHost', Utils.DEFAULT_HOST) )
		Utils.playBell = (self.config.Read('PlaySounds', 'True').upper()[:1] == 'T')
			
	async def updateMessages( self ):
		while True:
			await asyncio.sleep( 1.0 )
			
			tNow = datetime.datetime.now()
			running = int((tNow - self.tStart).total_seconds())
			self.runningTime.SetLabel( '{:02d}:{:02d}:{:02d}'.format(running // (60*60), (running // 60) % 60, running % 60) )
			self.time.SetLabel( tNow.strftime('%H:%M:%S') )
			
			while True:
				try:
					d = self.messageQ.get_nowait()
				except asyncio.QueueEmpty:
					break
				
				self.messageQ.task_done()
				message = ' '.join( f'{x}' for x in d[1:] )
				if   d[0] == 'Ubidium':
					if 'state' in d:
						self.ubidiumMessages.messageList.SetForegroundColour( wx.BLACK if d[2] else wx.BLACK )
						self.ubidiumMessages.messageList.SetBackgroundColour( self.LightGreen if d[2] else self.LightRed )
					else:
						self.ubidiumMessages.write( message )
				elif d[0] == 'Ubidium2JChip':
					if 'state' in d:
						self.crossMgrMessages.messageList.SetForegroundColour( wx.BLACK if d[2] else wx.BLACK )
						self.crossMgrMessages.messageList.SetBackgroundColour( self.LightGreen if d[2] else self.LightRed )
					else:
						self.crossMgrMessages.write( message )
				elif d[0] == 'BackupFile':
					self.backupFile.SetLabel( d[1] )

def disable_stdout_buffering():
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w")

redirectFileName = None
mainWin = None

async def MainLoop():
	global mainWin, redirectFileName
	
	app = WxAsyncApp()
	app.SetAppName("CrossMgrUbidium")

	mainWin = MainWin( None, title=AppVerName, size=(800,min(int(wx.GetDisplaySize()[1]*0.85),1000)) )
	
	dataDir = Utils.getHomeDir()
	redirectFileName = os.path.join(dataDir, 'CrossMgrUbidium.log')
	
	# Set up the log file.  Otherwise, show errors on the screen.
	if __name__ == '__main__':
		disable_stdout_buffering()
	else:
		try:
			logSize = os.path.getsize( redirectFileName )
			if logSize > 1000000:
				os.remove( redirectFileName )
		except Exception:
			pass
	
		try:
			app.RedirectStdio( redirectFileName )
		except Exception:
			pass
			
		try:
			with open(redirectFileName, 'a', encoding='utf8') as pf:
				pf.write( '********************************************\n' )
				pf.write( '{}: {} Started.\n'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), AppVerName) )
		except Exception:
			pass
	
	mainWin.Show()

	# Set the upper left icon.
	try:
		icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'CrossMgrUbidium.ico'), wx.BITMAP_TYPE_ICO )
		mainWin.SetIcon( icon )
	except Exception:
		pass

	# Start processing events.
	await app.MainLoop()

if __name__ == '__main__':
	asyncio.run( MainLoop() )
	
