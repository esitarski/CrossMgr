import Model
import Utils
import JChip
from Utils				import logCall, stripLeadingZeros
import wx
import wx.lib.intctrl
import wx.lib.masked           as masked
import  wx.lib.mixins.listctrl  as  listmix
import  wx.lib.rcsizer  as rcs
import socket
import sys
import re

PORT, HOST = JChip.DEFAULT_PORT, JChip.DEFAULT_HOST

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

def GetTagNums( forceUpdate = False ):
	race = Model.race
	if not race:
		return {}
		
	# Get the linked external data.
	try:
		excelLink = race.excelLink
	except:
		race.tagNums = {}
	else:
		try:
			externalInfo = excelLink.read()
		except:
			race.tagNums = {}
		else:
			if excelLink.readFromFile or not getattr(race, 'tagNums', None) or forceUpdate:
				race.tagNums = {}
				for tagName in ['Tag', 'Tag2']:
					if excelLink.hasField( tagName ):
						tn = {}
						for num, edata in externalInfo.iteritems():
							try:
								tag = edata[tagName].lstrip('0')
							except (KeyError, ValueError):
								continue
							if tag:
								tn[tag] = num
						race.tagNums.update( tn )
	return race.tagNums

#------------------------------------------------------------------------------------------------
reIP = re.compile( '^[0-9.]+$' )

def GetAllIps():
	addrInfo = socket.getaddrinfo( socket.gethostname(), None )
	ips = []
	for a in addrInfo:
		try:
			ip = a[4][0]
		except:
			continue
		if reIP.search(ip):
			ips.append( ip )
	return ips

class JChipSetupDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "JChip Setup",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
		
		self.timer = None
		self.receivedCount = 0
		
		self.enableJChipCheckBox = wx.CheckBox( self, -1, 'Accept JChip Data During Race' )
		if Model.race:
			self.enableJChipCheckBox.SetValue( getattr(Model.race, 'enableJChipIntegration', False) )
		else:
			self.enableJChipCheckBox.Enable( False )
		
		self.testJChip = wx.ToggleButton( self, wx.ID_ANY, 'Start JChip Test' )
		self.Bind(wx.EVT_TOGGLEBUTTON, self.testJChipToggle, self.testJChip)
		if Model.race and Model.race.isRunning():
			self.testJChip.Enable( False )
		
		self.testList = wx.TextCtrl( self, wx.ID_ANY, style=wx.TE_READONLY|wx.TE_MULTILINE, size=(-1,200) )
		self.testList.Bind( wx.EVT_RIGHT_DOWN, self.skip )
		
		self.okBtn = wx.Button( self, wx.ID_ANY, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_ANY, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		self.helpBtn = wx.Button( self, wx.ID_ANY, '&Help' )
		self.Bind( wx.EVT_BUTTON, lambda evt: Utils.showHelp('Menu-ChipReader.html#jchip-setup'), self.helpBtn )
		
		bs = wx.BoxSizer( wx.VERTICAL )
		
		todoList = [
			'Make sure the JChip receiver is plugged into the network.',
			'Do a "Sync PC" on the JChip receiver to synchronize with your computer clock.',
			'Verify that the JChip has a "TCP Client" connection to the CrossMgr computer (see below).',
			'You must have the Sign-On Excel sheet ready and linked before your race.',
			'You must configure a "Tag" field in your Sign-On Excel Sheet.',
			'Run this test before each race.',
		]
		intro = 'CrossMgr supports the JChip tag reader.\n' \
				'For more details, consult the CrossMgr and JChip documentation.\n' \
				'\nChecklist:\n\n%s\n' % '\n'.join( '%d)  %s' % (i + 1, s) for i, s in enumerate(todoList) )
		
		border = 4
		bs.Add( wx.StaticText(self, -1, intro), 0, wx.EXPAND|wx.ALL, border )

		bs.Add( self.enableJChipCheckBox, 0, wx.EXPAND|wx.ALL|wx.ALIGN_LEFT, border )
		
		#-------------------------------------------------------------------
		bs.AddSpacer( border )
		bs.Add( wx.StaticText( self, -1, 'JChip Configuration:' ), 0, wx.EXPAND|wx.ALL, border )
		
		#-------------------------------------------------------------------
		rowColSizer = rcs.RowColSizer()
		bs.Add( rowColSizer, 0, wx.EXPAND|wx.ALL, border )
		
		row = 0
		rowColSizer.Add( wx.StaticText( self, -1, 'Type:' ), row=row, col=0, border = border,
			flag=wx.TOP|wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		rowColSizer.Add( wx.TextCtrl( self, -1, value='TCP Client', style = wx.TE_READONLY),
			row=row, col=1, border = border, flag=wx.EXPAND|wx.TOP|wx.RIGHT|wx.ALIGN_LEFT )
		
		row += 1
		#self.ipaddr = masked.IpAddrCtrl( self, -1, style = wx.TE_PROCESS_TAB | wx.TE_READONLY )
		#self.ipaddr.SetValue( HOST )
		ips = GetAllIps()
		self.ipaddr = wx.Choice( self, wx.ID_ANY, choices = ips )
		for i, ip in enumerate(ips):
			if ip == HOST:
				self.ipaddr.SetSelection( i )
				break
		self.ipaddr.Bind( wx.EVT_CHOICE, self.onIpAddrSelect )
		
		rowColSizer.Add( wx.StaticText( self, -1, 'Remote IP Address:' ),
						row=row, col=0, flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		rowColSizer.Add( self.ipaddr, row=row, col=1, border = border, flag=wx.EXPAND|wx.RIGHT|wx.ALIGN_LEFT )
		
		row += 1
		self.port = wx.lib.intctrl.IntCtrl( self, -1, min=1, max=65535, value=PORT,
											limited=True, style = wx.TE_READONLY )
		rowColSizer.Add( wx.StaticText(self, -1, 'Remote Port:'), row=row, col=0,
						flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		rowColSizer.Add( self.port, row=row, col=1, border = border, flag=wx.EXPAND|wx.RIGHT|wx.ALIGN_LEFT )
		
		bs.Add( wx.StaticText( self, -1, 'See "7  Setting of Connections" in JChip "Control Panel Soft Manual" for more details.' ),
				border = border, flag = wx.GROW|wx.ALL )
		#-------------------------------------------------------------------

		bs.Add( self.testJChip, 0, wx.EXPAND|wx.ALL, border )
		bs.Add( wx.StaticText(self, wx.ID_ANY, 'Messages:'), 0, wx.EXPAND|wx.ALL, border = border )
		bs.Add( self.testList, 1, wx.EXPAND|wx.ALL, border )
		
		buttonBox = wx.BoxSizer( wx.HORIZONTAL )
		buttonBox.AddStretchSpacer()
		buttonBox.Add( self.okBtn, flag = wx.RIGHT, border = border )
		self.okBtn.SetDefault()
		buttonBox.Add( self.cancelBtn )
		buttonBox.Add( self.helpBtn )
		bs.Add( buttonBox, 0, wx.EXPAND | wx.ALL, border )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def skip(self, evt):
		return
	
	def onIpAddrSelect( self, event ):
		running = bool( JChip.listener )
		if running:
			JChip.StopListener()
			if self.timer:
				self.timer.Stop()
				self.timer = None
			wx.Sleep( 2 )	# Give everthing a chance to shut down.
			
		global HOST
		HOST = JChip.DEFAULT_HOST = self.ipaddr.GetStringSelection()
		
		if running:
			self.appendMsg( 'restarting JChip listener (%s)...' % HOST )
			JChip.StartListener()
			self.appendMsg( 'listening for JChip connection...' )
			
			# Start a timer to monitor the receiver.
			self.receivedCount = 0
			self.timer = wx.CallLater( 1000, self.onTimerCallback, 'started' )
	
	def testJChipToggle( self, event ):
		if not JChip.listener:
			correct, reason = CheckExcelLink()
			explain = 	'CrossMgr will not be able to associate chip Tags with Bib numbers.\n' \
						'You may proceed with the test, but you need to fix the Excel sheet.\n\n' \
						'See documentation for details.'
			if not correct:
				if not Utils.MessageOKCancel( self, 'Problems with Excel sheet.\n\n    Reason: %s\n\n%s' % (reason, explain),
									title = 'Excel Link Problem', iconMask = wx.ICON_WARNING ):
					self.testJChip.SetValue( False )
					return
			tagNums = GetTagNums( True )
			if correct and not tagNums:
				if not Utils.MessageOKCancel( self, 'All Tag entries in the Excel sheet are blank.\n\n%s' % explain,
									title = 'Excel Link Problem', iconMask = wx.ICON_WARNING ):
					self.testJChip.SetValue( False )
					return
			
			self.testList.Clear()
			JChip.StartListener()
			
			self.appendMsg( 'listening for JChip connection...' )
			
			self.testJChip.SetLabel( 'Stop JChip Test' )
			self.testJChip.SetValue( True )
			
			# Start a timer to monitor the receiver.
			self.receivedCount = 0
			self.timer = wx.CallLater( 1000, self.onTimerCallback, 'started' )
		else:
			# Stop the listener.
			JChip.StopListener()
			
			# Stop the timer sampling the reader.
			if self.timer:
				self.timer.Stop()
				self.timer = None
			
			self.testJChip.SetLabel( 'Start JChip Test' )
			self.testJChip.SetValue( False )
			self.testList.Clear()
	
	def appendMsg( self, s ):
		self.testList.AppendText( s + '\n' )
	
	def onTimerCallback( self, stat ):
		data = JChip.GetData()
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
					num = str(Model.race.tagNums[d[1]])
				except (AttributeError, ValueError, KeyError):
					num = 'not found'
				lastTag = d[1]
				self.appendMsg( '%d: tag=%s, time=%s, Bib=%s' % (self.receivedCount, d[1], ts, num) )
			elif d[0] == 'connected':
				self.appendMsg( '*******************************************' )
				self.appendMsg( '%s: %s' % (d[0], ', '.join('%s' % str(s) for s in d[1:]) ) )
			elif d[0] == 'disconnected':
				self.appendMsg( d[0] )
				self.appendMsg( '' )
				self.appendMsg( 'listening for JChip connection...' )
			elif d[0] == 'name':
				self.appendMsg( 'receiver name: %s' % d[1] )
			else:
				self.appendMsg( '%s: %s' % (d[0], ', '.join('<<%s>>' % str(s) for s in d[1:]) ) )
		if data:
			self.testList.SetInsertionPointEnd()
		self.timer.Restart( 1000, 'restarted' )
		
		if lastTag and Utils.mainWin and getattr(Utils.mainWin, 'findDialog', None):
			if Utils.mainWin.findDialog.IsShown():
				Utils.mainWin.findDialog.refresh( lastTag )
		
	def onOK( self, event ):
		if Model.race:
			Model.race.enableJChipIntegration = bool(self.enableJChipCheckBox.GetValue())
		wx.CallAfter( Utils.refresh )
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		if JChip.listener:
			self.testJChipToggle( event )
		self.EndModal( wx.ID_CANCEL )
		
if __name__ == '__main__':
	print GetAllIps()
	#sys.exit()
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.race._populate()
	Model.race.finishRaceNow()
	mainWin.Show()
	dlg = JChipSetupDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

