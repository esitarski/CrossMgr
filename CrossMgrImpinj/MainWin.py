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
import Impinj
from Impinj import ImpinjServer
from Impinj2JChip import CrossMgrServer
from AutoDetect import AutoDetect

import wx
import wx.lib.masked			as masked
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
	
class AdvancedSetup( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Advanced Setup",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		'''
		Impinj.TagPopulation			= None	# Size of a group to read.
		Impinj.ReceiverSensitivity		= None
		Impinj.TransmitPower			= None
		
		Impinj.ConnectionTimeoutSeconds	= 1		# Interval for connection timeout
		Impinj.KeepaliveSeconds			= 2		# Interval to request a Keepalive message
		Impinj.RepeatSeconds			= 2		# Interval in which a tag is considered a repeat read.
		'''

		bs = wx.GridBagSizer(vgap=5, hgap=5)
		
		row = 0

		border = 8
		bs.Add( wx.StaticText(self, label='Advanced Reader Options:'), pos = (0,0), span=(1, 2), border = border, flag=wx.ALL )
		
		row += 1
		bs.Add( wx.StaticText(self, label='Tag Population'), pos=(row, 0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.TagPopulation = intctrl.IntCtrl( self, min=0, max=500, limited = True, allow_none=True,
			value = Impinj.TagPopulation, size=(100,-1), style=wx.TE_RIGHT )
		bs.Add( self.TagPopulation, pos=(row, 1), span=(1,1), border = border, flag=wx.TOP )
		bs.Add( wx.StaticText(self, label='Expected number of tags in range of the antennas at the finish line.\nSuggestions: 4=TimeTrial/MTB, 16=Small Criterium/Road Race, 100=Large Criterium/Road Race.'), pos=(row, 2), span=(1,1), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL )

		row += 1
		bs.Add( wx.StaticLine(self), pos=(row, 0), span=(1, 3), flag=wx.EXPAND )

		row += 1
		bs.Add( wx.StaticText(self, label='Transmit Power'), pos=(row, 0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.TransmitPower = intctrl.IntCtrl( self, min=0, max=10000, limited = True, allow_none=True,
			value = Impinj.TransmitPower, size=(100,-1), style=wx.TE_RIGHT )
		bs.Add( self.TransmitPower, pos=(row, 1), span=(1,1), border = border, flag=wx.TOP )
		bs.Add( wx.StaticText(self, label='Check reader for details.  Leave blank for full power.'), pos=(row, 2), span=(1,1), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL )

		row += 1
		bs.Add( wx.StaticText(self, label='Receiver Sensitivity'), pos=(row, 0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.ReceiverSensitivity = intctrl.IntCtrl( self, min=0, max=500, limited = True, allow_none=True,
			value = Impinj.ReceiverSensitivity, size=(100,-1), style=wx.TE_RIGHT )
		bs.Add( self.ReceiverSensitivity, pos=(row, 1), span=(1,1), border = border, flag=wx.TOP )
		bs.Add( wx.StaticText(self, label='Check reader for details.  Leave blank for full sensitivity.'), pos=(row, 2), span=(1,1), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL )

		row += 1
		bs.Add( wx.StaticLine(self), pos=(row, 0), span=(1, 3), flag=wx.EXPAND )

		row += 1
		bs.Add( wx.StaticText(self, label='Connection Timeout Seconds'), pos=(row, 0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.ConnectionTimeoutSeconds = intctrl.IntCtrl( self, min=1, max=60, limited = True,
			value = Impinj.ConnectionTimeoutSeconds, size=(100,-1), style=wx.TE_RIGHT )
		bs.Add( self.ConnectionTimeoutSeconds, pos=(row, 1), span=(1,1), border = border, flag=wx.TOP )
		bs.Add( wx.StaticText(self, label='Maximum seconds to wait for a reader response.'), pos=(row, 2), span=(1,1), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL )
		
		row += 1
		bs.Add( wx.StaticText(self, label='Keepalive Seconds'), pos=(row, 0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.KeepaliveSeconds = intctrl.IntCtrl( self, min=1, max=60, limited = True,
			value = Impinj.KeepaliveSeconds, size=(100,-1), style=wx.TE_RIGHT )
		bs.Add( self.KeepaliveSeconds, pos=(row, 1), span=(1,1), border = border, flag=wx.TOP )
		bs.Add( wx.StaticText(self, label='Frequency of "heartbeat" messages indicating the reader is still connected.'), pos=(row, 2), span=(1,1), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL )

		row += 1
		bs.Add( wx.StaticText(self, label='Repeat Seconds'), pos=(row, 0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.RepeatSeconds = intctrl.IntCtrl( self, min=1, max=120, limited = True,
			value = Impinj.RepeatSeconds, size=(100,-1), style=wx.TE_RIGHT )
		bs.Add( self.RepeatSeconds, pos=(row, 1), span=(1,1), border = border, flag=wx.TOP )
		bs.Add( wx.StaticText(self, label='Interval in which multiple tag reads are considered "repeats" and not reported.'), pos=(row, 2), span=(1,1), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL )

		self.fields = [
			'ConnectionTimeoutSeconds', 'KeepaliveSeconds', 'RepeatSeconds',
			'TagPopulation', 'TransmitPower', 'ReceiverSensitivity',
		]
		
		row += 1
		bs.Add( wx.StaticLine(self), pos=(row, 0), span=(1, 3), flag=wx.EXPAND )

		row += 1
		self.playSoundsCheckbox = wx.CheckBox( self, label='Beep on Read' )
		self.playSoundsCheckbox.SetValue( Utils.playBell )
		bs.Add( self.playSoundsCheckbox, pos=(row, 1), span=(1,3), border = border, flag=wx.TOP|wx.LEFT|wx.RIGHT )
		
		row += 1
		bs.Add( wx.StaticLine(self), pos=(row, 0), span=(1, 3), flag=wx.EXPAND )

		row += 1
		self.restoreDefaultButton = wx.Button( self, label='Restore Defaults' )
		self.restoreDefaultButton.Bind( wx.EVT_BUTTON, self.onRestoreDefault )
		bs.Add( self.restoreDefaultButton, pos=(row, 0), span=(1,3), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER )
		
		row += 1
		bs.Add( wx.StaticText(self, label='Reminder: Press "Reset" for these changes to take effect.'), pos=(row, 0), span=(1,3), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT )
		
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
		for a in self.fields:
			try:
				getattr( self, a ).SetValue( getattr(Impinj, a + 'Default') )
			except AttributeError:
				getattr( self, a ).SetValue( None )
		
	def onOK( self, event ):
		for a in self.fields:
			setattr( Impinj, a, getattr(self, a).GetValue() )
		
		Utils.playBell = self.playSoundsCheckbox.IsChecked()
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
	
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
		
		self.reset = RoundButton(self, label='Reset', size=(80, 80))
		self.reset.SetBackgroundColour( wx.WHITE )
		self.reset.SetForegroundColour( wx.Colour(0,128,128) )
		self.reset.SetFontToFitLabel()	# Use the button's default font, but change the font size to fit the label.
		self.reset.Bind( wx.EVT_BUTTON, self.doReset )
		self.reset.Refresh()
		bs.Add( self.reset, border = 8, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.Add( setFont(italicFont,wx.StaticText(self, label='CrossMgrImpinj')), border = 8, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.AddStretchSpacer()
		bitmap = wx.BitmapFromXPMData( clipboard_xpm )
		self.copyToClipboard = wx.BitmapButton( self, bitmap=bitmap )
		self.copyToClipboard.SetToolTip(wx.ToolTip('Copy Configuration and Logs to Clipboard...'))
		self.copyToClipboard.Bind( wx.EVT_BUTTON, self.doCopyToClipboard )
		bs.Add( self.copyToClipboard, border = 32, flag = wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.tStart = datetime.datetime.now()
		bs.Add( setFont(bigFont,wx.StaticText(self, label='Last Reset: %s' % self.tStart.strftime('%H:%M:%S'))), border = 10, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.runningTime = setFont(bigFont,wx.StaticText(self, label='00:00:00' ))
		bs.Add( self.runningTime, border = 20, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL )
		bs.Add( setFont(bigFont,wx.StaticText(self, label=' / ')), flag=wx.ALIGN_CENTER_VERTICAL )
		self.time = setFont(bigFont, wx.StaticText(self, label='00:00:00' ))
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
		hb.Add( setFont(bigFont,wx.StaticText(self, label='Impinj Configuration:')), flag=wx.ALIGN_CENTER_VERTICAL )
		self.autoDetectButton = wx.Button(self, label='Auto Detect')
		self.autoDetectButton.Bind( wx.EVT_BUTTON, self.doAutoDetect )
		hb.Add( self.autoDetectButton, flag=wx.LEFT, border = 6 )
		
		self.advancedButton = wx.Button(self, label='Advanced...' )
		self.advancedButton.Bind( wx.EVT_BUTTON, self.doAdvanced )
		hb.Add( self.advancedButton, flag=wx.LEFT, border = 6 )
		
		gbs.Add( hb, pos=(iRow,0), span=(1,2), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		
		gs = wx.GridSizer( rows=0, cols=4, vgap=0, hgap=2 )
		self.antennaLabels = []
		self.antennas = []
		for i in xrange(4):
			self.antennaLabels.append( wx.StaticText(self, label='{}'.format(i+1), style=wx.ALIGN_CENTER) )
			gs.Add( self.antennaLabels[-1], flag=wx.ALIGN_CENTER|wx.EXPAND )
		for i in xrange(4):
			cb = wx.CheckBox( self, wx.ID_ANY, '')
			if i < 2:
				cb.SetValue( True )
			cb.Bind( wx.EVT_CHECKBOX, lambda x: self.getAntennaStr() )
			gs.Add( cb, flag=wx.ALIGN_CENTER )
			self.antennas.append( cb )
		
		gbs.Add( wx.StaticText(self, label='ANT Ports:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM )
		gbs.Add( gs, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		
		iRow += 1
		
		self.useHostName = wx.RadioButton( self, label='Host Name:', style=wx.wx.RB_GROUP )
		gbs.Add( self.useHostName, pos=(iRow,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( wx.StaticText(self, label=ImpinjHostNamePrefix), flag=wx.ALIGN_CENTER_VERTICAL )
		self.impinjHostName = masked.TextCtrl( self,
							mask         = 'NN-NN-NN',
							defaultValue = '00-00-00',
							useFixedWidthFont = True,
							size=(80, -1),
						)
		hb.Add( self.impinjHostName )
		hb.Add( wx.StaticText(self, label=ImpinjHostNameSuffix), flag=wx.ALIGN_CENTER_VERTICAL )
		hb.Add( wx.StaticText(self, label=' : ' + '{}'.format(ImpinjInboundPort)), flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		self.useStaticAddress = wx.RadioButton( self, label='IP:' )
		gbs.Add( self.useStaticAddress, pos=(iRow,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		hb = wx.BoxSizer( wx.HORIZONTAL )
		self.impinjHost = masked.IpAddrCtrl( self, style=wx.TE_PROCESS_TAB )
		hb.Add( self.impinjHost )
		hb.Add( wx.StaticText(self, label=' : ' + '{}'.format(ImpinjInboundPort)), flag=wx.ALIGN_CENTER_VERTICAL )

		gbs.Add( hb, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		self.useHostName.SetValue( True )
		self.useStaticAddress.SetValue( False )
		
		iRow += 1
		gbs.Add( wx.StaticText(self, label='ANT Reads:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT )
		self.antennaReadCount = wx.StaticText( self, label='1:0 0% | 2:0 0% | 3:0 0% | 4:0 0%               ' )
		gbs.Add( self.antennaReadCount, pos=(iRow,1), span=(1,2), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		gbs.Add( wx.StaticText(self, label='Backup File:'), pos=(iRow,0), span=(1,1), flag=wx.ALIGN_RIGHT )
		self.backupFile = wx.StaticText( self, label='                                                   ' )
		gbs.Add( self.backupFile, pos=(iRow,1), span=(1,2), flag=wx.ALIGN_LEFT )
		
		#------------------------------------------------------------------------------------------------
		# CrossMgr configuration.
		#
		gbs = wx.GridBagSizer( 4, 4 )
		fgs.Add( gbs, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		gbs.Add( setFont(bigFont,wx.StaticText(self, label='CrossMgr Configuration:')), pos=(0,0), span=(1,2), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( wx.StaticText(self, label='CrossMgr Address:'), pos=(1,0), span=(1,1), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		
		hb = wx.BoxSizer( wx.HORIZONTAL )
		self.crossMgrHost = masked.IpAddrCtrl( self, style = wx.TE_PROCESS_TAB )
		hb.Add( self.crossMgrHost, flag=wx.ALIGN_LEFT )
		hb.Add( wx.StaticText( self, label=' : 53135' ), flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(1,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		#------------------------------------------------------------------------------------------------
		# Add messages
		#
		self.impinjMessagesText = wx.TextCtrl( self, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL, size=(-1,400) )
		fgs.Add( self.impinjMessagesText, flag=wx.EXPAND, proportion=2 )
		self.impinjMessages = MessageManager( self.impinjMessagesText )
		
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
	
	def readerStatusCB( self, **kwargs ):
		# As this is called from another thread, make sure all UI updates are done from CallAfter.
		connectedAntennas = set(kwargs.get( 'connectedAntennas', [] ))
		for i in xrange(4):
			wx.CallAfter( self.antennaLabels[i].SetBackgroundColour, self.LightGreen if (i+1) in connectedAntennas else wx.NullColour  )
	
	def start( self ):
		self.dataQ = Queue()
		self.messageQ = Queue()
		self.shutdownQ = Queue()	# Queue to tell the Impinj monitor to shut down.
		self.readerStatusCB()
		
		if self.useHostName.GetValue():
			self.impinjProcess = Process(
				name='ImpinjProcess', target=ImpinjServer,
				args=(
					self.dataQ, self.messageQ, self.shutdownQ,
					ImpinjHostNamePrefix + self.impinjHostName.GetValue() + ImpinjHostNameSuffix, ImpinjInboundPort,
					self.getAntennaStr(),
					self.readerStatusCB,
				)
			)
		else:
			self.impinjProcess = Process(
				name='ImpinjProcess', target=ImpinjServer,
				args=(
					self.dataQ, self.messageQ, self.shutdownQ,
					self.impinjHost.GetAddress(), ImpinjInboundPort,
					self.getAntennaStr(),
					self.readerStatusCB,
				)
			)
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
		impinjHost, crossMgrHost = AutoDetect(ImpinjInboundPort)[0], '127.0.0.1'
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
	
	def doAdvanced( self, event ):
		dlg = AdvancedSetup( self )
		dlg.ShowModal()
		dlg.Destroy()
	
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
			''
			'    ConnectionTimeoutSeconds: {}'.format(Impinj.ConnectionTimeoutSeconds),
			'    KeepaliveSeconds:         {}'.format(Impinj.KeepaliveSeconds),
			'    RepeatSeconds:            {}'.format(Impinj.RepeatSeconds),
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
		selectedAntennas = [ i for i in xrange(4) if self.antennas[i].GetValue() ]
		# Ensure at least one antenna is selected.
		if not selectedAntennas:
			self.antennas[0].SetValue( True )
			selectedAntennas = [0]
		return ' '.join( '{}'.format(a+1) for a in selectedAntennas )
	
	def setAntennaStr( self, s ):
		antennas = set( int(a) for a in s.split() )
		for i in xrange(4):
			self.antennas[i].SetValue( (i+1) in antennas )
	
	def writeOptions( self ):
		self.config.Write( 'CrossMgrHost', self.getCrossMgrHost() )
		self.config.Write( 'UseHostName', 'True' if self.useHostName.GetValue() else 'False' )
		self.config.Write( 'ImpinjHostName', ImpinjHostNamePrefix + self.impinjHostName.GetValue() + ImpinjHostNameSuffix )
		self.config.Write( 'ImpinjAddr', self.impinjHost.GetAddress() )
		self.config.Write( 'ImpinjPort', '{}'.format(ImpinjInboundPort) )
		self.config.Write( 'Antennas', self.getAntennaStr() )
		
		self.config.Write( 'ConnectionTimeoutSeconds', '{}'.format(Impinj.ConnectionTimeoutSeconds) )
		self.config.Write( 'KeepaliveSeconds', '{}'.format(Impinj.KeepaliveSeconds) )
		self.config.Write( 'RepeatSeconds', '{}'.format(Impinj.RepeatSeconds) )
		self.config.Write( 'PlaySounds', '{}'.format(Utils.playBell) )
		
		self.config.Write( 'ReceiverSensitivity', '{}'.format(Impinj.ReceiverSensitivity or 0) )
		self.config.Write( 'TransmitPower', '{}'.format(Impinj.TransmitPower or 0) )
		self.config.Write( 'TagPopulation', '{}'.format(Impinj.TagPopulation or 0) )
		self.config.Write( 'TagTransitTime', '{}'.format(Impinj.TagTransitTime or 0) )

		self.config.Flush()
	
	def readOptions( self ):
		self.crossMgrHost.SetValue( self.config.Read('CrossMgrHost', Utils.DEFAULT_HOST) )
		useHostName = (self.config.Read('UseHostName', 'True').upper()[:1] == 'T')
		self.useHostName.SetValue( useHostName )
		self.useStaticAddress.SetValue( not useHostName )
		self.impinjHostName.SetValue( self.config.Read('ImpinjHostName', ImpinjHostNamePrefix + '00-00-00' + ImpinjHostNameSuffix)[len(ImpinjHostNamePrefix):-len(ImpinjHostNameSuffix)] )
		self.impinjHost.SetValue( self.config.Read('ImpinjAddr', '0.0.0.0') )
		self.setAntennaStr( self.config.Read('Antennas', '1 2 3 4') )
		Utils.playBell = (self.config.Read('PlaySounds', 'True').upper()[:1] == 'T')
		
		Impinj.ConnectionTimeoutSeconds = int(self.config.Read( 'ConnectionTimeoutSeconds',
												'{}'.format(Impinj.ConnectionTimeoutSeconds)))
		Impinj.KeepaliveSeconds = int(self.config.Read( 'KeepaliveSeconds',
												'{}'.format(Impinj.KeepaliveSeconds)))
		Impinj.RepeatSeconds = int(self.config.Read( 'RepeatSeconds',
												'{}'.format(Impinj.RepeatSeconds)))
												
		Impinj.ReceiverSensitivity = int(self.config.Read('ReceiverSensitivity', '0')) or None
		Impinj.TransmitPower = int(self.config.Read('TransmitPower', '0')) or None
		Impinj.TagPopulation = int(self.config.Read('TagPopulation', '0')) or None
		Impinj.TagTransitTime = int(self.config.Read('TagTransitTime', '0')) or None
	
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
			if isinstance(d[-1], dict):
				antennaReadCount = d[-1]
				d = d[:-1]
			else:
				antennaReadCount = None
			
			message = ' '.join( unicode(x) for x in d[1:] )
			if   d[0] == 'Impinj':
				if 'state' in d:
					self.impinjMessages.messageList.SetBackgroundColour( self.LightGreen if d[2] else self.LightRed )
				else:
					self.impinjMessages.write( message )
					if antennaReadCount is not None:
						total = max(1, sum( antennaReadCount[i] for i in xrange(1,4+1)) )
						self.antennaReadCount.SetLabel(' | '.join('{}:{} {:.1f}%'.format(i, antennaReadCount[i], antennaReadCount[i]*100.0/total) for i in xrange(1,4+1)) )
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
	
	app = wx.App(False)
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
		icon = wx.Icon( os.path.join(Utils.getImageFolder(), 'CrossMgrImpinj.ico'), wx.BITMAP_TYPE_ICO )
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
	
