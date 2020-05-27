
import wx
import wx.adv
import wx.lib.intctrl
import wx.lib.masked			as masked
import wx.lib.agw.hyperlink as hl
import re
import os
import sys
import time
import datetime
import traceback

import Utils
from Version import AppVerName
import Images

from pyllrp import *
from pyllrp.TagInventory import TagInventory
from TagWriterCustom import TagWriterCustom
from AdvancedDialog import AdvancedDialog

from AutoDetect import AutoDetect

ImpinjHostNamePrefix = 'SpeedwayR-'
ImpinjHostNameSuffix = '.local'
ImpinjInboundPort = 5084

if 'WXMSW' in wx.Platform:
	IpAddrCtrl = masked.IpAddrCtrl
else:
	class IpAddrCtrl( wx.TextCtrl ):
		def GetAddress( self ):
			ipaddress = self.GetValue()
			return ipaddress.strip()

def toInt( s, d = 1 ):
	try:
		n = int(s)
	except ValueError:
		n = d
	return n

class TemplateValidator(wx.Validator):
	validChars = set( '0123456789ABCDEF#' )

	def __init__( self ):
		wx.Validator.__init__(self)
		self.Bind(wx.EVT_CHAR, self.OnChar)

	def Clone(self):
		return TemplateValidator()

	def Validate(self, win):
		tc = self.GetWindow()
		val = tc.GetValue()
		return all( x in self.validChars for x in val )

	def OnChar(self, event):
		key = event.GetKeyCode()

		if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
			event.Skip()
			return

		if chr(key) in self.validChars:
			event.Skip()
			return
			
		if not wx.Validator_IsSilent():
			wx.Bell()

class MainWin( wx.Frame ):
	EPCHexCharsMax = 24
	
	StatusError, StatusSuccess, StatusAttempt = [0, 1, 2]

	def __init__( self, parent, id = wx.ID_ANY, title = '', size = (550, 480) ):
		super().__init__( parent, id, title = title, size = size )
		
		self.SetTitle( AppVerName )
		
		self.successBitmap = wx.Bitmap( Images.success_xpm )
		self.attemptBitmap = wx.Bitmap( Images.attempt_xpm )
		self.errorBitmap = wx.Bitmap( Images.error_xpm )
		
		dataDir = Utils.getHomeDir()
		configFileName = os.path.join(dataDir, 'TagReadWrite.cfg')
		self.config = wx.Config(appName="TagReadWrite",
						vendorName="SmartCyclingSolutions",
						localFilename=configFileName
		)
		
		ID_MENU_ADVANCECONFIG = wx.NewIdRef()
		ID_MENU_COPYLOGS = wx.NewIdRef()
		ID_MENU_AUTODETECT = wx.NewIdRef()
		self.menuBar = wx.MenuBar(wx.MB_DOCKABLE)
		if 'WXMAC' in wx.Platform:
			self.appleMenu = self.menuBar.OSXGetAppleMenu()
			self.appleMenu.SetTitle("CrossMgrImpinj")

			self.appleMenu.Insert(0, wx.ID_ABOUT, "&About")

			self.Bind(wx.EVT_MENU, self.OnAboutBox, id=wx.ID_ABOUT)

			self.editMenu = wx.Menu()
			self.editMenu.Append(wx.MenuItem(self.editMenu, ID_MENU_AUTODETECT,"&Autodetect Reader"))

			self.Bind(wx.EVT_MENU, self.doAutoDetect, id=ID_MENU_AUTODETECT)
			self.menuBar.Append(self.editMenu, "&Edit")

		else:
			self.fileMenu = wx.Menu()
			self.fileMenu.Append(wx.MenuItem(self.fileMenu, ID_MENU_AUTODETECT,"&Autodetect Reader"))
			self.fileMenu.Append(wx.ID_EXIT)
			self.Bind(wx.EVT_MENU, self.doAutoDetect, id=ID_MENU_AUTODETECT)
			self.Bind(wx.EVT_MENU, self.onClose, id=wx.ID_EXIT)
			self.menuBar.Append(self.fileMenu, "&File")
			self.helpMenu = wx.Menu()
			self.helpMenu.Insert(0, wx.ID_ABOUT, "&About")
			self.Bind(wx.EVT_MENU, self.OnAboutBox, id=wx.ID_ABOUT)
			self.menuBar.Append(self.helpMenu, "&Help")

		self.SetMenuBar(self.menuBar)

		self.tagWriter = None
		
		self.backgroundColour = wx.Colour(232,232,232)
		self.SetBackgroundColour( self.backgroundColour )
		self.LightGreen = wx.Colour(153,255,153)
		self.LightRed = wx.Colour(255,153,153)
		
		vsMain = wx.BoxSizer( wx.VERTICAL )
		
		self.title = wx.StaticText( self, label = 'CrossMgr Impinj Tag Read/Write' )
		self.title.SetFont( wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD) )
		
		self.url = hl.HyperLinkCtrl( self, label = 'Powered by CrossMgr', URL = 'http://sites.google.com/site/crossmgrsoftware' )
		self.url.SetBackgroundColour( self.backgroundColour )
		
		#-------------------------------------------------------------------------------------------------
		# Impinj configuration.
		#		
		impinjConfiguration = wx.StaticBox( self, label = 'Impinj Configuration' )
		impinjConfigurationSizer = wx.StaticBoxSizer( impinjConfiguration, wx.HORIZONTAL )
		gbs = wx.GridBagSizer( 4, 4 )
		impinjConfigurationSizer.Add( gbs, flag = wx.ALL, border = 4 )
		
		iRow = 0
		
		self.useHostName = wx.RadioButton( self, label = 'Host Name:', style=wx.RB_GROUP )
		gbs.Add( self.useHostName, pos=(iRow,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( wx.StaticText(self, label = ImpinjHostNamePrefix), flag=wx.ALIGN_CENTER_VERTICAL )
		if 'WXMAC' in wx.Platform:
			self.impinjHostName = masked.TextCtrl( self,
								defaultValue = '00-00-00',
								useFixedWidthFont = True,
								size=(100,-1),
							)
		else:
			self.impinjHostName = masked.TextCtrl( self,
								mask         = 'NN-NN-NN',
								defaultValue = '00-00-00',
								useFixedWidthFont = True,
								size=(100,-1),
							)
		hb.Add( self.impinjHostName )
		hb.Add( wx.StaticText(self, label = ImpinjHostNameSuffix), flag=wx.ALIGN_CENTER_VERTICAL )
		hb.Add( wx.StaticText(self, label = ' : ' + '{}'.format(ImpinjInboundPort)), flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		self.useStaticAddress = wx.RadioButton( self, label='IP:' )
		gbs.Add( self.useStaticAddress, pos=(iRow,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		hb = wx.BoxSizer( wx.HORIZONTAL )
		self.impinjHost = IpAddrCtrl( self, style = wx.TE_PROCESS_TAB, size=(120,-1) )
		hb.Add( self.impinjHost )
		hb.Add( wx.StaticText(self, label = ' : ' + '{}'.format(ImpinjInboundPort)), flag=wx.ALIGN_CENTER_VERTICAL )

		gbs.Add( hb, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		iRow += 1
		
		gbs.Add( wx.StaticLine(self, style=wx.LI_HORIZONTAL), pos=(iRow,0), span=(1,2) )
		iRow += 1
		
		self.autoDetectButton = wx.Button(self, label='Auto Detect Reader')
		self.autoDetectButton.Bind( wx.EVT_BUTTON, self.doAutoDetect )
		gbs.Add( self.autoDetectButton, pos=(iRow,0), span=(1,2), flag=wx.ALIGN_RIGHT )
		iRow += 1

		fgs = wx.FlexGridSizer( 2, 3, 2, 2 )
		fgs.Add( wx.StaticText(self, label='Transmit Power:') )
		self.transmitPower_dBm = wx.StaticText( self, label='Max', size=(40,-1), style=wx.ALIGN_RIGHT )
		fgs.Add( self.transmitPower_dBm, flag=wx.LEFT, border=2 )
		fgs.Add( wx.StaticText(self, label='dBm'), flag=wx.LEFT, border=2 )

		fgs.Add( wx.StaticText(self, label='Receive Sensitivity:') )
		self.receiveSensitivity_dB = wx.StaticText( self, label='Max', size=(40,-1), style=wx.ALIGN_RIGHT )
		fgs.Add( self.receiveSensitivity_dB, flag=wx.LEFT, border=2 )
		fgs.Add( wx.StaticText(self, label='dB'), flag=wx.LEFT, border=2 )		
		
		gbs.Add( fgs, pos=(iRow,0), span=(2,1) )

		advancedButton = wx.Button( self, label="Advanced..." )
		advancedButton.Bind( wx.EVT_BUTTON, self.doAdvancedButton )
		gbs.Add( advancedButton, pos=(iRow, 1), span=(2,1) )

		iRow += 2

		self.disconnectButton = wx.Button(self, label='Disconnect')
		self.disconnectButton.Bind( wx.EVT_BUTTON, self.doDisconnect )
		gbs.Add( self.disconnectButton, pos=(iRow,0), span=(1,2), flag=wx.ALIGN_RIGHT )
		iRow += 1
		
		self.useHostName.SetValue( True )
		self.useStaticAddress.SetValue( False )
		
		statusVS = wx.BoxSizer( wx.VERTICAL )
		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.statusBitmap = wx.StaticBitmap( self, wx.ID_ANY, self.attemptBitmap )
		self.statusLabel = wx.StaticText( self, label = 'Connecting...' )
		hs.Add( self.statusBitmap )
		hs.Add( self.statusLabel, flag = wx.ALIGN_CENTRE_VERTICAL )

		self.resetButton = wx.Button( self, label = 'Reset Connection' )
		self.resetButton.Bind( wx.EVT_BUTTON, self.doReset )
		
		statusVS.Add( hs, flag = wx.ALL|wx.ALIGN_CENTRE, border = 4 )
		statusVS.Add( self.resetButton, flag = wx.ALL|wx.ALIGN_CENTRE, border = 4 )
		
		impinjConfigurationSizer.Add( statusVS, 1, flag = wx.EXPAND|wx.ALL, border = 4 )
		
		#-------------------------------------------------------------------------------------------------
		
		writeTags = wx.StaticBox( self, label = 'Write Tags' )
		vs1 = wx.StaticBoxSizer( writeTags, wx.VERTICAL )

		self.templateLabel = wx.StaticText( self, label = 'Template (0-9A-F, #### for number):' )
		self.template = wx.TextCtrl( self, validator = TemplateValidator() )
		self.template.SetMaxLength( self.EPCHexCharsMax )
		self.template.Bind( wx.EVT_TEXT, self.onTextChange )
		
		self.numberLabel = wx.StaticText( self, label = 'Number:' )
		self.number = wx.lib.intctrl.IntCtrl( self, min = 1, max = 99999999, allow_none = True, limited = True, value = 1 )
		self.number.Bind( wx.EVT_TEXT, self.onTextChange )
		
		self.incrementLabel = wx.StaticText( self, label = 'Increment by:' )
		self.increment = wx.lib.intctrl.IntCtrl( self, min = 0, max = 99999999, limited = True, value = 1 )
		
		self.valueLabel = wx.StaticText( self, label = 'Next Value to Write:' )
		self.value = wx.TextCtrl( self, style = wx.TE_READONLY )
		self.value.SetMaxLength( self.EPCHexCharsMax )
		self.value.SetBackgroundColour( wx.Colour(235,235,235) )
		
		self.writeSuccess = wx.Gauge( self, style = wx.GA_HORIZONTAL, range = 100 )
		
		self.writeButton = wx.Button( self, label = 'Write (F1 or Space)' )
		self.writeButton.Enabled = False
		self.writeButton.Bind( wx.EVT_BUTTON, self.onWriteButton )
		
		readTags = wx.StaticBox( self, label = 'Read Tags' )
		vs2 = wx.StaticBoxSizer( readTags, wx.VERTICAL )
		self.tags = wx.TextCtrl( self, style = wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_PROCESS_ENTER )
		self.readButton = wx.Button( self, label = 'Read (F2)' )
		self.readButton.Enabled = False
		self.readButton.Bind( wx.EVT_BUTTON, self.onReadButton )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		
		labelBorderOptions = wx.TOP | wx.LEFT | wx.RIGHT
		valueBorderOptions = wx.BOTTOM | wx.LEFT | wx.RIGHT
		border = 2
		
		vs1.Add( self.templateLabel, flag = labelBorderOptions, border = border )
		vs1.Add( self.template, flag = wx.EXPAND|valueBorderOptions, border = border )
		vs1.Add( self.numberLabel, flag = labelBorderOptions, border = border )
		vs1.Add( self.number, flag = wx.EXPAND|valueBorderOptions, border = border )
		vs1.Add( self.incrementLabel, flag = labelBorderOptions, border = border )
		vs1.Add( self.increment, flag = wx.EXPAND|valueBorderOptions, border = border )
		vs1.Add( self.valueLabel, flag = labelBorderOptions, border = border )
		vs1.Add( self.value, flag = wx.EXPAND|valueBorderOptions, border = border )
		vs1.Add( self.writeSuccess, 0, flag = wx.EXPAND|wx.ALL, border = border )
		vs1.AddStretchSpacer()
		vs1.Add( self.writeButton, flag = wx.EXPAND|wx.ALL, border = border )
		
		vs2.Add( self.tags, 1, flag = wx.EXPAND|wx.ALL, border = border )
		vs2.Add( self.readButton, flag = wx.EXPAND|wx.ALL, border = border )
		
		hs.Add( vs1, 1, flag = wx.EXPAND|wx.ALL, border = border )
		hs.Add( vs2, 1, flag = wx.EXPAND|wx.ALL, border = border )
		
		hsTitle = wx.BoxSizer( wx.HORIZONTAL )
		hsTitle.Add( self.title )
		hsTitle.AddStretchSpacer()
		hsTitle.Add( self.url, flag = wx.ALIGN_CENTRE_VERTICAL )
		vsMain.Add( hsTitle, flag = wx.ALL|wx.EXPAND, border = border )
		vsMain.Add( impinjConfigurationSizer, flag = wx.ALL|wx.EXPAND, border = border )
		vsMain.Add( hs, 1, flag = wx.EXPAND )
		
		self.sb = self.CreateStatusBar()
		
		self.getWriteValue()
		self.setWriteSuccess( False )
		
		self.SetSizer( vsMain )
		self.readOptions()
		
		self.Bind( wx.EVT_CLOSE, self.onClose )
		
		self.idWrite, self.idRead = self.writeButton.GetId(), self.readButton.GetId()
		self.Bind(wx.EVT_MENU, self.onWriteButton, id=self.idWrite)
		self.Bind(wx.EVT_MENU, self.onReadButton, id=self.idRead)
		wx.CallAfter( self.doReset )

	def EnableAccelerator(self):
		accelTable = wx.AcceleratorTable([
			(wx.ACCEL_NORMAL, wx.WXK_F1, self.idWrite ),
			(wx.ACCEL_NORMAL, wx.WXK_SPACE, self.idWrite ),
			(wx.ACCEL_NORMAL, wx.WXK_F2, self.idRead ),
		])
		self.SetAcceleratorTable(accelTable)
		self.readButton.Enabled = True
		self.writeButton.Enabled = True
		self.useHostName.Enabled = False
		self.impinjHostName.Enabled = False
		self.impinjHost.Enabled = False
		self.useStaticAddress.Enabled = False

	def DisableAccelerator(self):
		accelTable = wx.AcceleratorTable([
		])
		self.SetAcceleratorTable(accelTable)
		self.readButton.Enabled = False
		self.writeButton.Enabled = False
		self.useHostName.Enabled = True
		self.impinjHostName.Enabled = True
		self.impinjHost.Enabled = True
		self.useStaticAddress.Enabled = True

	def OnAboutBox(self, e):
			description = """TagReadWrite is an Impinj Tag Writer for CrossMgr
	"""

			licence = """TagReadWrite free software; you can redistribute 
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

			crossMgrPng = Utils.getImageFolder() + '/TagReadWrite.png'
			info.SetIcon(wx.Icon(crossMgrPng, wx.BITMAP_TYPE_PNG))
			info.SetName('TagReadWrite')
			info.SetVersion(AppVerName.split(' ')[1])
			info.SetDescription(description)
			info.SetCopyright('(C) 2020 Edward Sitarski')
			info.SetWebSite('http://www.sites.google.com/site/crossmgrsoftware/')
			info.SetLicence(licence)

			wx.adv.AboutBox(info, self)

	def setWriteSuccess( self, success ):
		self.writeSuccess.SetValue( 100 if success else 0 )
	
	reTemplate = re.compile( u'#+' )
	def getFormatStr( self ):
		template = self.template.GetValue()
		if u'#' not in template:
			template = u'#' + template
		
		while 1:
			m = self.reTemplate.search( template )
			if not m:
				break
			template = template[:m.start(0)] + u'{{n:0{}d}}'.format(len(m.group(0))) + template[m.end(0):]
			
		return template
	
	def onClose( self, event ):
		self.shutdown()
		self.Destroy()
	
	def shutdown( self ):
		if self.tagWriter:
			try:
				self.tagWriter.Disconnect()
			except Exception as e:
				pass
		self.tagWriter = None
		self.DisableAccelerator()
		
	def doAdvancedButton( self, event = None ):
		if not self.tagWriter:
			with wx.MessageDialog(self, "You must be connected to an RFID reader.", "Error: not connected to Reader") as md:
				md.ShowModal()
			return
			
		with AdvancedDialog(
				self,
				receive_sensitivity_table=self.tagWriter.receive_sensitivity_table, receive_dB=self.receiveSensitivity_dB.GetLabel(),
				transmit_power_table=self.tagWriter.transmit_power_table, transmit_dBm=self.transmitPower_dBm.GetLabel(),
			) as advDlg:
			if advDlg.ShowModal() == wx.ID_OK:
				r, t = advDlg.get()
				self.receiveSensitivity_dB.SetLabel(r)
				self.transmitPower_dBm.SetLabel(t)
				self.doReset()	

	def doDisconnect(self, event = None ):
		self.shutdown()
		self.setStatus( self.StatusAttempt )

	def doReset( self, event = None ):
		self.shutdown()
		self.setStatus( self.StatusAttempt )
		
		self.tagWriter = TagWriterCustom( self.getHost() )
		try:
			self.tagWriter.Connect( self.receiveSensitivity_dB.GetLabel(), self.transmitPower_dBm.GetLabel() )
		except Exception as e:
			self.DisableAccelerator()
			self.setStatus( self.StatusError )
			Utils.MessageOK( self, 'Reader Connection Fails to "{}": {}\n\nCheck the reader connection and configuration.\nThen press "Reset Connection"'.format(self.getHost(), e),
							'Reader Connection Fails' )
			self.tagWriter = None
			return

		self.setStatus( self.StatusSuccess )
		self.writeOptions()
		self.EnableAccelerator()
	
	def onTextChange( self, event ):
		self.getWriteValue()
	
	def autoDetectCallback( self, addr ):
		self.sb.SetStatusText( 'Trying Reader at: {}...'.format(addr) )
	
	def doAutoDetect( self, event ):
		wx.BeginBusyCursor()
		self.shutdown()
		impinjHost = AutoDetect( ImpinjInboundPort, self.autoDetectCallback )
		wx.EndBusyCursor()
		
		if impinjHost:
			self.useStaticAddress.SetValue( True )
			self.useHostName.SetValue( False )
			
			self.impinjHost.SetValue( impinjHost )
			self.doReset()
			self.writeOptions()
			wx.Bell()
		else:
			dlg = wx.MessageDialog(self, 'Auto Detect Failed.\nCheck that reader has power and is connected to the router.',
									'Auto Detect Failed',
									wx.OK | wx.ICON_INFORMATION )
			dlg.ShowModal()
			dlg.Destroy()
	
	def writeOptions( self ):
		self.config.Write( 'Template', self.template.GetValue() )
		self.config.Write( 'Number', '{}'.format(self.number.GetValue()) )
		self.config.Write( 'Increment', '{}'.format(self.increment.GetValue()) )
		
		self.config.Write( 'UseHostName', 'True' if self.useHostName.GetValue() else 'False' )
		self.config.Write( 'ImpinjHostName', ImpinjHostNamePrefix + self.impinjHostName.GetValue() + ImpinjHostNameSuffix )
		self.config.Write( 'ImpinjAddr', self.impinjHost.GetAddress() )
		self.config.Write( 'ImpinjPort', '{}'.format(ImpinjInboundPort) )

		self.config.Write( 'ReceiveSensitivity_dB', '{}'.format(self.receiveSensitivity_dB.GetLabel()) )
		self.config.Write( 'TransmitPower_dBm', '{}'.format(self.transmitPower_dBm.GetLabel()) )
	
	def readOptions( self ):
		self.template.SetValue( self.config.Read('Template', '#AA{}'.format(datetime.datetime.now().year % 100)) )
		self.number.SetValue( toInt(self.config.Read('Number', '1')) )
		self.increment.SetValue( toInt(self.config.Read('Increment', '1')) )
		
		useHostName = (self.config.Read('UseHostName', 'True').upper()[:1] == 'T')
		self.useHostName.SetValue( useHostName )
		self.useStaticAddress.SetValue( not useHostName )
		self.impinjHostName.SetValue( self.config.Read('ImpinjHostName', ImpinjHostNamePrefix + '00-00-00' + ImpinjHostNameSuffix)[len(ImpinjHostNamePrefix):-len(ImpinjHostNameSuffix)] )
		self.impinjHost.SetValue( self.config.Read('ImpinjAddr', '0.0.0.0') )
		
		self.receiveSensitivity_dB.SetLabel( self.config.Read('ReceiveSensitivity_dB', 'Max') )
		self.transmitPower_dBm.SetLabel( self.config.Read('TransmitPower_dBm', 'Max') )
	
	def getWriteValue( self ):
		f = self.getFormatStr().format( n = int(self.number.GetValue() or 0) ).lstrip('0')
		if not f:
			f = '0'
		f = f[:self.EPCHexCharsMax]
		self.value.SetValue( f )
		return f
		
	def setStatus( self, status ):
		if status == self.StatusAttempt:
			self.statusBitmap.SetBitmap( self.attemptBitmap )
			self.statusLabel.SetLabel( 'Not Connected' )
			self.sb.SetStatusText( 'Not Connected' )
		elif status == self.StatusSuccess:
			self.statusBitmap.SetBitmap( self.successBitmap )
			self.statusLabel.SetLabel( 'Connected' )
			self.sb.SetStatusText( 'Connected' )
		else:
			self.statusBitmap.SetBitmap( self.errorBitmap )
			self.statusLabel.SetLabel( 'Connection Failed' )
			self.sb.SetStatusText( 'Connection Failed' )
			
		self.statusBitmap.Hide()
		self.statusLabel.Hide()
		self.statusBitmap.Show()
		self.statusLabel.Show()
		
	def getHost( self ):
		if self.useHostName.GetValue():
			host = ImpinjHostNamePrefix + self.impinjHostName.GetValue().strip() + ImpinjHostNameSuffix
		else:
			host = self.impinjHost.GetAddress()
		return host
	
	def onWriteButton( self, event ):
		if not self.tagWriter:
			Utils.MessageOK( self, 'Reader not connected.\n\nSet reader connection parameters and press "Reset Connection".', 'Reader Not Connected' )
			return
		
		busy = wx.BusyCursor()
		wx.CallAfter( self.writeOptions )
		
		self.setWriteSuccess( False )
		
		writeValue = self.getWriteValue()
		
		try:
			self.tagWriter.WriteTag( '', writeValue )
		except Exception as e:
			Utils.MessageOK( self, 'Write Fails: {}\n\nCheck the reader connection.\n\n{}'.format(e, traceback.format_exc()),
							'Write Fails' )
		
		self.setWriteSuccess( True )
		wx.CallLater( 50, self.onReadButton, None )
		
	def onReadButton( self, event ):
		if not self.tagWriter:
			Utils.MessageOK( self,  u'Reader not connected.\n\nSet reader connection parameters and press "Reset Connection".',
									u'Reader Not Connected' )
			return
		
		busy = wx.BusyCursor()
			
		wx.CallAfter( self.writeOptions )
		
		self.tags.SetBackgroundColour( wx.WHITE )
		
		tagInventory = None
		try:
			tagInventory, otherMessages = self.tagWriter.GetTagInventory()
			tagDetail = { t['Tag']:t for t in self.tagWriter.tagDetail }
			tagInventory = ['{}, PeakRSSI={}db, ANT={}'.format(t or '0', tagDetail[t].get('PeakRSSI',''), tagDetail[t].get('AntennaID',''))
				for t in sorted(tagInventory, key = lambda x: int(x,16))]
			self.tags.SetValue( '\n'.join(tagInventory) )
		except Exception as e:
			Utils.MessageOK( self, 'Read Fails: {}\n\nCheck the reader connection.\n\n{}'.format(e, traceback.format_exc()),
							'Read Fails' )
		
		if event is None:
			# This read follows a write.
			# Check that the tag read matches the tag wrote.
			if len(tagInventory) == 1 and self.getWriteValue() == tagInventory[0]:
				self.number.SetValue( self.number.GetValue() + self.increment.GetValue() )
				self.getWriteValue()
				
				self.tags.SetBackgroundColour( self.LightGreen )
				self.setWriteSuccess( True )
				wx.Bell()
			else:
				self.tags.SetBackgroundColour( self.LightRed )
				self.setWriteSuccess( False )
		else:
			if tagInventory:
				self.tags.SetBackgroundColour( self.LightGreen )
		
def Launch( doRedirect = False ):
	app = wx.App( False )
	app.SetAppName( 'TagReadWrite' )
	
	if doRedirect:
		dataDir = Utils.getHomeDir()
		redirectFileName = os.path.join(dataDir, 'TagReadWrite.log')
		print ( '"{}"'.format( redirectFileName ) )
		
		# Set up the log file.  Otherwise, show errors on the screen.
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
	
	mainWin = MainWin( None )
	mainWin.Show()
	app.MainLoop()
		
if __name__ == '__main__':
	Launch()
