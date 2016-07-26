
import wx
import wx.lib.intctrl
import wx.lib.masked
import wx.lib.agw.hyperlink as hl
import re
import os
import sys
import time
import datetime
import traceback

sys.path.append( '../CrossMgrImpinj/pyllrp' )

import Utils
from Version import AppVerName
import Images

from pyllrp import *
from pyllrp.TagInventory import TagInventory
from pyllrp.TagWriter import TagWriter

from AutoDetect import AutoDetect

ImpinjHostNamePrefix = 'SpeedwayR-'
ImpinjHostNameSuffix = '.local'
ImpinjInboundPort = 5084

def toInt( s, d = 1 ):
	try:
		n = int(s)
	except ValueError:
		n = d
	return n

class TemplateValidator(wx.PyValidator):
	validChars = set( '0123456789ABCDEF#' )

	def __init__( self ):
		wx.PyValidator.__init__(self)
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
		super( MainWin, self ).__init__( parent, id, title = title, size = size )
		
		self.SetTitle( AppVerName )
		
		self.successBitmap = wx.BitmapFromXPMData( Images.success_xpm )
		self.attemptBitmap = wx.BitmapFromXPMData( Images.attempt_xpm )
		self.errorBitmap = wx.BitmapFromXPMData( Images.error_xpm )
		
		self.config = wx.Config(appName="CrossMgrReadWrite",
						vendorName="SmartCyclingSolutions",
						style=wx.CONFIG_USE_LOCAL_FILE)
		
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
		
		self.useHostName = wx.RadioButton( self, label = 'Host Name:', style=wx.wx.RB_GROUP )
		gbs.Add( self.useHostName, pos=(iRow,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( wx.StaticText(self, label = ImpinjHostNamePrefix), flag=wx.ALIGN_CENTER_VERTICAL )
		self.impinjHostName = wx.lib.masked.TextCtrl( self, wx.ID_ANY,
							mask         = 'NN-NN-NN',
							defaultValue = '00-00-00',
							useFixedWidthFont = True,
							size=(80, -1),
						)
		hb.Add( self.impinjHostName )
		hb.Add( wx.StaticText(self, label = ImpinjHostNameSuffix), flag=wx.ALIGN_CENTER_VERTICAL )
		hb.Add( wx.StaticText(self, label = ' : ' + '{}'.format(ImpinjInboundPort)), flag=wx.ALIGN_CENTER_VERTICAL )
		gbs.Add( hb, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		
		iRow += 1
		self.useStaticAddress = wx.RadioButton( self, wx.ID_ANY, 'IP:' )
		gbs.Add( self.useStaticAddress, pos=(iRow,0), span=(1,1), flag=wx.ALIGN_CENTER_VERTICAL )
		hb = wx.BoxSizer( wx.HORIZONTAL )
		self.impinjHost = wx.lib.masked.IpAddrCtrl( self, style = wx.TE_PROCESS_TAB )
		hb.Add( self.impinjHost )
		hb.Add( wx.StaticText(self, label = ' : ' + '{}'.format(ImpinjInboundPort)), flag=wx.ALIGN_CENTER_VERTICAL )

		gbs.Add( hb, pos=(iRow,1), span=(1,1), flag=wx.ALIGN_LEFT )
		iRow += 1
		
		gbs.Add( wx.StaticLine(self, style=wx.LI_HORIZONTAL), pos=(iRow,0), span=(1,2) )
		iRow += 1
		
		self.autoDetectButton = wx.Button(self, wx.ID_ANY, 'Auto Detect Reader')
		self.autoDetectButton.Bind( wx.EVT_BUTTON, self.doAutoDetect )
		gbs.Add( self.autoDetectButton, pos=(iRow,0), span=(1,2), flag=wx.ALIGN_RIGHT )
		iRow += 1
		
		self.useHostName.SetValue( True )
		self.useStaticAddress.SetValue( False )
		
		statusVS = wx.BoxSizer( wx.VERTICAL )
		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.statusBitmap = wx.StaticBitmap( self, bitmap = self.attemptBitmap )
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
		
		self.writeButton = wx.Button( self, label = 'Write' )
		self.writeButton.Bind( wx.EVT_BUTTON, self.onWriteButton )
		
		readTags = wx.StaticBox( self, label = 'Read Tags' )
		vs2 = wx.StaticBoxSizer( readTags, wx.VERTICAL )
		self.tags = wx.TextCtrl( self, style = wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_PROCESS_ENTER )
		self.readButton = wx.Button( self, label = 'Read' )
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
		vs1.Add( self.writeButton, flag = wx.EXPAND|wx.ALL|wx.ALIGN_BOTTOM, border = border )
		
		vs2.Add( self.tags, 1, flag = wx.EXPAND|wx.ALL, border = border )
		vs2.Add( self.readButton, flag = wx.EXPAND|wx.ALL, border = border )
		
		hs.Add( vs1, 1, flag = wx.EXPAND|wx.ALL, border = border )
		hs.Add( vs2, 1, flag = wx.EXPAND|wx.ALL, border = border )
		
		hsTitle = wx.BoxSizer( wx.HORIZONTAL )
		hsTitle.Add( self.title )
		hsTitle.AddStretchSpacer()
		hsTitle.Add( self.url, flag = wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		vsMain.Add( hsTitle, flag = wx.ALL|wx.EXPAND, border = border )
		vsMain.Add( impinjConfigurationSizer, flag = wx.ALL|wx.EXPAND, border = border )
		vsMain.Add( hs, 1, flag = wx.EXPAND )
		
		self.sb = self.CreateStatusBar()
		
		self.getWriteValue()
		self.setWriteSuccess( False )
		
		self.SetSizer( vsMain )
		self.readOptions()
		
		self.Bind( wx.EVT_CLOSE, self.onClose )
		
		wx.CallAfter( self.doReset )
	
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
		
	def doReset( self, event = None ):
		self.shutdown()
		self.setStatus( self.StatusAttempt )
		self.tagWriter = TagWriter( self.getHost() )
		
		try:
			self.tagWriter.Connect()
		except Exception as e:
			self.setStatus( self.StatusError )
			Utils.MessageOK( self, 'Reader Connection Fails: {}\n\nCheck the reader connection and configuration.\nThen press "Reset Connection"'.format(e),
							'Reader Connection Fails' )
			self.tagWriter = None
			return
			
		self.setStatus( self.StatusSuccess )
	
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
	
	def readOptions( self ):
		self.template.SetValue( self.config.Read('Template', '#AA{}'.format(datetime.datetime.now().year % 100)) )
		self.number.SetValue( toInt(self.config.Read('Number', '1')) )
		self.increment.SetValue( toInt(self.config.Read('Increment', '1')) )
		
		useHostName = (self.config.Read('UseHostName', 'True').upper()[:1] == 'T')
		self.useHostName.SetValue( useHostName )
		self.useStaticAddress.SetValue( not useHostName )
		self.impinjHostName.SetValue( self.config.Read('ImpinjHostName', ImpinjHostNamePrefix + '00-00-00' + ImpinjHostNameSuffix)[len(ImpinjHostNamePrefix):-len(ImpinjHostNameSuffix)] )
		self.impinjHost.SetValue( self.config.Read('ImpinjAddr', '0.0.0.0') )
		
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
			self.statusLabel.SetLabel( '' )
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
			host = ImpinjHostNamePrefix + self.impinjHostName.GetValue() + ImpinjHostNameSuffix
		else:
			host = self.impinjHost.GetAddress()
		return host
	
	def onWriteButton( self, event ):
		if not self.tagWriter:
			Utils.MessageOK( self, 'Reader not connected.\n\nSet reader connection parameters and press "Reset Connection".', 'Reader Not Connected' )
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
		busy = wx.BusyCursor()
			
		wx.CallAfter( self.writeOptions )
		
		self.tags.SetBackgroundColour( wx.WHITE )
		
		tagInventory = None
		try:
			tagInventory, otherMessages = self.tagWriter.GetTagInventory()
			tagInventory = [(t or '0') for t in sorted(tagInventory, key = lambda x: int(x,16))]
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
		
if __name__ == '__main__':
	app = wx.App( False )
	app.SetAppName( 'TagReadWrite' )
	
	dataDir = Utils.getHomeDir()
	redirectFileName = os.path.join(dataDir, 'TagReadWrite.log')
	
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
			pf.write( '%s: %s Started.\n' % (datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), AppVerName) )
	except:
		pass
	
	mainWin = MainWin( None )
	mainWin.Show()
	app.MainLoop()

		
