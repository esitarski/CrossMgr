import wx
import wx.lib.intctrl
import wx.lib.rcsizer  as rcs
import socket
import sys
import re
import datetime
import Model
import Utils
import JChip
import ChipReader
from JChip import EVT_CHIP_READER
import RaceResult
import Ultra
import HelpSearch
from ReadSignOnSheet import GetTagNums

HOST, PORT = JChip.DEFAULT_HOST, JChip.DEFAULT_PORT
 
def CheckExcelLink():
	race = Model.race
	if not race:
		return (False, 'No active race.')
	try:
		externalFields = race.excelLink.getFields()
	except (ValueError, AttributeError):
		return (False, 'Unconfigured.')
		
	if 'Tag' not in externalFields:
		return (False, '"Tag" column not specified.')
		
	return (True, 'Excel Link OK')

#------------------------------------------------------------------------------------------------
reIP = re.compile( '^[0-9.]+$' )

def GetAllIps():
	addrInfo = socket.getaddrinfo( socket.gethostname(), None )
	ips = set()
	for a in addrInfo:
		try:
			ip = a[4][0]
		except:
			continue
		if reIP.search(ip):
			ips.add( ip )
	return sorted( ips )

class JChipSetupDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, _("Chip Reader Setup"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
		
		self.timer = None
		self.receivedCount = 0
		self.refTime = None
		
		self.enableJChipCheckBox = wx.CheckBox( self, label = _('Accept RFID Reader Data During Race') )
		if Model.race:
			self.enableJChipCheckBox.SetValue( getattr(Model.race, 'enableJChipIntegration', False) )
		else:
			self.enableJChipCheckBox.Enable( False )
		
		self.testJChip = wx.ToggleButton( self, label = _('Start RFID Test') )
		self.testJChip.SetFont( wx.Font( (0,24), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ) )
		self.Bind(wx.EVT_TOGGLEBUTTON, self.testJChipToggle, self.testJChip)
		
		self.testList = wx.TextCtrl( self, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(-1,200) )
		self.testList.Bind( wx.EVT_RIGHT_DOWN, self.skip )
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		self.helpBtn = wx.Button( self, wx.ID_HELP )
		self.Bind( wx.EVT_BUTTON, lambda evt: HelpSearch.showHelp('Menu-ChipReader.html#chip-reader-setup'), self.helpBtn )
		
		self.Bind(EVT_CHIP_READER, self.handleChipReaderEvent)
		
		bs = wx.BoxSizer( wx.VERTICAL )
		
		todoList =  u'\n'.join( '%d)  %s' % (i + 1, s) for i, s in enumerate( [
			_('Make sure the RFID receiver is plugged into the network.'),
			_('If you are using Impinj/Alien, make sure the CrossMgrImpinj or CrossMgrAlien bridge programs are running.'),
			_('You must have the Sign-On Excel sheet ready and linked before your race.'),
			_('You must configure a "Tag" field in your Sign-On Excel Sheet.'),
			_('Run this test before each race.'),
		]) )
		intro = (u'\n'.join( [
				_('CrossMgr supports the JChip, RaceResult, Ultra, Impinj and Alien RFID readers.'),
				_('For more details, consult the documentation for your reader.'),
				] ) + u'\n' + _('Checklist:') + u'\n\n{}\n').format( todoList )
		
		border = 4
		bs.Add( wx.StaticText(self, label = intro), 0, wx.EXPAND|wx.ALL, border )

		bs.Add( self.enableJChipCheckBox, 0, wx.EXPAND|wx.ALL|wx.ALIGN_LEFT, border )
		
		#-------------------------------------------------------------------
		bs.AddSpacer( border )
		bs.Add( wx.StaticText( self, label = _('Reader Configuration:') ), 0, wx.EXPAND|wx.ALL, border )
		
		#-------------------------------------------------------------------
		rowColSizer = rcs.RowColSizer()
		bs.Add( rowColSizer, 0, wx.EXPAND|wx.ALL, border )
		
		row = 0
		rowColSizer.Add( wx.StaticText( self, label=u'{}:'.format(_('Reader Type')) ), row=row, col=0, border=border,
			flag=wx.TOP|wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.chipReaderType = wx.Choice( self, choices=[_('JChip/Impinj/Alien'), _('RaceResult'),  _('Ultra')] )
		self.chipReaderType.SetSelection( 0 )
		self.chipReaderType.Bind( wx.EVT_CHOICE, self.changechipReaderType )
		rowColSizer.Add( self.chipReaderType,
			row=row, col=1, border=border, flag=wx.EXPAND|wx.TOP|wx.RIGHT|wx.ALIGN_LEFT )
		
		row += 1
		sep = u'  -' + _('or') + u'-  '
		ips = sep.join( GetAllIps() )
		self.ipaddr = wx.TextCtrl( self, value = ips, style = wx.TE_READONLY, size=(240,-1) )
		self.autoDetect = wx.Button( self, label=_('AutoDetect') )
		self.autoDetect.Show( False )
		self.autoDetect.Bind( wx.EVT_BUTTON, self.doAutoDetect )
		
		iphs = wx.BoxSizer( wx.HORIZONTAL )
		iphs.Add( self.ipaddr, 1, flag=wx.EXPAND )
		iphs.Add( self.autoDetect, 0, flag=wx.LEFT, border=4 )
		
		rowColSizer.Add( wx.StaticText( self, label=_('Remote IP Address:') ),
						row=row, col=0, flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		rowColSizer.Add( iphs, row=row, col=1, border=border, flag=wx.EXPAND|wx.RIGHT|wx.ALIGN_LEFT )
		
		row += 1
		self.port = wx.lib.intctrl.IntCtrl( self, -1, min=1, max=65535, value=PORT,
											limited=True, style = wx.TE_READONLY )
		rowColSizer.Add( wx.StaticText(self, label = _('Remote Port:')), row=row, col=0,
						flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		rowColSizer.Add( self.port, row=row, col=1, border=border, flag=wx.EXPAND|wx.RIGHT|wx.ALIGN_LEFT )
		
		bs.Add( wx.StaticText( self, label = _('If using JChip, see "7  Setting of Connections" in JChip "Control Panel Soft Manual" for more details.') ),
				border=border, flag = wx.GROW|wx.ALL )
		#-------------------------------------------------------------------

		bs.Add( self.testJChip, 0, wx.ALIGN_CENTER|wx.ALL, border )
		bs.Add( wx.StaticText(self, label = _('Messages:')), 0, wx.EXPAND|wx.ALL, border=border )
		bs.Add( self.testList, 1, wx.EXPAND|wx.ALL, border )
		
		buttonBox = wx.BoxSizer( wx.HORIZONTAL )
		buttonBox.AddStretchSpacer()
		buttonBox.Add( self.okBtn, flag = wx.RIGHT, border=border )
		self.okBtn.SetDefault()
		buttonBox.Add( self.cancelBtn )
		buttonBox.Add( self.helpBtn )
		bs.Add( buttonBox, 0, wx.EXPAND | wx.ALL, border )
		
		self.stopTest()
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.update()
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )

	def skip(self, evt):
		return
		
	def commit( self ):
		race = Model.race
		if not race:
			return
		race.chipReaderType = max( 0, self.chipReaderType.GetSelection() )
		race.chipReaderIpAddr = self.ipaddr.GetValue()
		if race.chipReaderType == 1:
			Utils.writeConfig( 'RaceResultHost', race.chipReaderIpAddr )
		elif race.chipReaderType == 2:
			Utils.writeConfig( 'UltraHost', race.chipReaderIpAddr )
		race.chipReaderPort = self.port.GetValue()
		race.enableJChipIntegration = bool(self.enableJChipCheckBox.GetValue())
		ChipReader.chipReaderCur.reset( race.chipReaderType )

	def update( self ):
		race = Model.race
		if not race:
			return
		self.enableJChipCheckBox.SetValue( race.enableJChipIntegration )
		self.chipReaderType.SetSelection( max(0, race.chipReaderType) )
		self.ipaddr.SetValue( race.chipReaderIpAddr )
		self.port.SetValue( race.chipReaderPort )
		self.changechipReaderType()
		
	def changechipReaderType( self, event=None ):
		selection = self.chipReaderType.GetSelection()
		
		if selection == 0:	# JChip/CrossMgrImpinj/CrossMgrAlien
			self.port.SetValue( JChip.DEFAULT_PORT )
			self.port.SetEditable( False )
			self.ipaddr.SetValue( Utils.GetDefaultHost() )
			self.ipaddr.SetEditable( False )
			self.autoDetect.Show( False )
			
		elif selection == 1:	# RaceResult
			self.port.SetValue( RaceResult.DEFAULT_PORT )
			self.port.SetEditable( True )
			self.ipaddr.SetEditable( True )
			rfidReaderHost = Utils.readConfig( 'RfidReaderHost', None )
			if rfidReaderHost:
				try:
					self.ipaddr.SetValue( rfidReaderHost )
				except Exception as e:
					self.ipaddr.SetValue( Utils.GetDefaultHost() )
			self.autoDetect.Show( True )
		
		elif selection == 2:	# Ultra
			self.port.SetValue( Ultra.DEFAULT_PORT )
			self.port.SetEditable( True )
			self.ipaddr.SetEditable( True )
			rfidReaderHost = Utils.readConfig( 'RfidReaderHost', None )
			if rfidReaderHost:
				try:
					self.ipaddr.SetValue( rfidReaderHost )
				except Exception as e:
					self.ipaddr.SetValue( Utils.GetDefaultHost() )
			self.autoDetect.Show( True )
		
		self.Layout()
		self.Refresh()
	
	def doAutoDetect( self, event ):
		selection = self.chipReaderType.GetSelection()
		autoDetect = [RaceResult.AutoDetect, Ultra.AutoDetect][selection-1]
		
		def getHost():
			wait = wx.BusyCursor()
			try:
				return None, autoDetect(self.port.GetValue())
			except Exception as e:
				return e, None
		
		error, readerHost = getHost()
		if error:
			Utils.MessageOK(
				self,
				u'{}:\n\n{}'.format(_("AutoDetect Error"), error),
				_("AutoDetect Error"),
				wx.ICON_ERROR
			)
			return
		if not readerHost:
			Utils.MessageOK(
				self, u'{}:\n\n{}'.format(_("AutoDetect Failure"), _('Reader not found.')),
				_("AutoDetect Failure"),
				wx.ICON_ERROR
			)
			return
		self.ipaddr.SetValue( readerHost )
		
	def handleChipReaderEvent( self, event ):
		if not event.tagTimes:
			return
			
		tagNums = {}
		race = Model.race
		if race:
			if not getattr(race, 'enableUSBCamera', False):
				return
			tagNums = GetTagNums()
		
		tag, dt = event.tagTimes[-1]
		num = tagNums.get(tag, None)

	def testJChipToggle( self, event ):
		self.commit()
		
		if not Model.race:
			self.stopTest()
			Utils.MessageOK( self, _('No active race.  Cannot perform RFID test.  "New" or "Open" a race first.'), _('Cannot Perform RFID Test') )
			return
			
		if Model.race.isRunning():
			self.stopTest()
			Utils.MessageOK( self, _('Cannot perform RFID test while race is running.'), _('Cannot Perform RFID Test') )
			return

		if self.testJChip.GetValue():
			correct, reason = CheckExcelLink()
			explain = 	_('CrossMgr will not be able to associate chip Tags with Bib numbers.') + u'\n' + \
						_('You may proceed with the test, but you need to fix the Excel sheet.') + u'\n\n' + \
						_('See documentation for details.')
			if not correct:
				if not Utils.MessageOKCancel( self, (_('Problems with Excel sheet.') + u'\n\n    ' + _('Reason:') + u' {}\n\n{}').format(reason, explain),
									title = _('Excel Link Problem'), iconMask = wx.ICON_WARNING ):
					self.testJChip.SetValue( False )
					return
			tagNums = GetTagNums( True )
			if correct and not tagNums:
				if not Utils.MessageOKCancel( self, (_('All Tag entries in the Excel sheet are blank.') + u'\n\n{}').format(explain),
									title = _('Excel Link Problem'), iconMask = wx.ICON_WARNING ):
					self.testJChip.SetValue( False )
					return
			
			ChipReader.chipReaderCur.readerEventWindow = self
			
			self.testList.Clear()
			self.testJChip.SetLabel( 'Stop RFID Test' )
			self.testJChip.SetBackgroundColour( wx.Colour(255,128,128) )
			self.testJChip.SetValue( True )
			
			ChipReader.chipReaderCur.StartListener()
			
			self.appendMsg( 'listening for RFID connection...' )
			
			# Start a timer to monitor the receiver.
			self.receivedCount = 0
			self.timer = wx.CallLater( 1000, self.onTimerCallback, 'started' )
		else:
			self.stopTest()
	
	def appendMsg( self, s ):
		self.testList.AppendText( s + '\n' )
	
	def onTimerCallback( self, stat ):
		data = ChipReader.chipReaderCur.GetData()
		lastTag = None
		for d in data:
			if d[0] == 'data':
				self.receivedCount += 1
				ts = d[2].isoformat(' ')
				if len(ts) == 8:
					ts += '.00'
				else:
					ts = ts[:-2]
				try:
					num = '{}'.format(Model.race.tagNums[d[1]])
				except (AttributeError, ValueError, KeyError):
					num = 'not found'
				lastTag = d[1]
				self.appendMsg( '{}: tag={}, time={}, Bib={}'.format(self.receivedCount, d[1], ts, num) )
			elif d[0] == 'connected':
				self.appendMsg( '*******************************************' )
				self.appendMsg( '{}: {}'.format(d[0], ', '.join('{}'.format(s) for s in d[1:]) ) )
			elif d[0] == 'disconnected':
				self.appendMsg( d[0] )
				self.appendMsg( '' )
				self.appendMsg( _('listening for RFID connection...') )
			elif d[0] == 'name':
				self.appendMsg( u'{}: {}'.format(_('receiver name'), d[1]) )
			else:
				self.appendMsg( '{}: {}'.format(d[0], ', '.join('<<{}>>'.format(s) for s in d[1:]) ) )
		if data:
			self.testList.SetInsertionPointEnd()
		self.timer.Restart( 1000, 'restarted' )
		
		if lastTag and Utils.mainWin and getattr(Utils.mainWin, 'findDialog', None):
			if Utils.mainWin.findDialog.IsShown():
				Utils.mainWin.findDialog.refresh( lastTag )
	
	def stopTest( self ):
		ChipReader.chipReaderCur.StopListener()
		if self.timer:
			self.timer.Stop()
			self.timer = None
		self.testList.Clear()
		self.appendMsg( _('No test running.') )
		ChipReader.chipReaderCur.readerEventWindow = None
		self.testJChip.SetLabel( _('Start RFID Test') )
		self.testJChip.SetBackgroundColour( wx.NullColour )
		self.testJChip.SetValue( False )

	def onOK( self, event ):
		self.stopTest()
		self.commit()
		wx.CallAfter( Utils.refresh )
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.stopTest()
		self.EndModal( wx.ID_CANCEL )
		
if __name__ == '__main__':
	print GetAllIps()
	#sys.exit()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.race._populate()
	Model.race.finishRaceNow()
	Model.race.enableUSBCamera = True
	mainWin.Show()
	dlg = JChipSetupDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

