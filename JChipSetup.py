import Model
import Utils
import JChip
from Utils				import logCall
import wx
import wx.lib.intctrl
import wx.lib.masked           as masked
import  wx.lib.mixins.listctrl  as  listmix
import socket

PORT = 53135

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
		
	return (True,)

def GetTagNums():
	race = Model.race
	if not race:
		return {}
		
	if not race.tagNums:
		# Get the linked external data.
		try:
			externalInfo = race.excelLink.read()
		except:
			externalInfo = {}
		
		# Associate Bib# and Tag from the external data.
		race.tagNums = {}
		for num, edata in externalInfo.iteritems():
			try:
				race.tagNums[edata['Tag']] = r.num
			except KeyError:
				pass
				
	return race.tagNums

class ListCtrlAutoWidth(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

#------------------------------------------------------------------------------------------------
class JChipSetupDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "JChip Setup",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
		
		self.timer = None
		self.receivedCount = 0
		
		self.enableJChipCheckBox = wx.CheckBox( self, -1, 'Read JChip Tags During Race.' )
		if Model.race:
			self.enableJChipCheckBox.SetValue( getattr(Model.race, 'enableJChipIntegration', False) )
		else:
			self.enableJChipCheckBox.Enable( False )
		
		self.ipaddrLabel = wx.StaticText( self, -1, 'Remote IP Address:' )
		self.ipaddr = masked.IpAddrCtrl( self, -1, style = wx.TE_PROCESS_TAB | wx.TE_READONLY )
		self.ipaddr.SetValue( socket.gethostbyname(socket.gethostname()) )
		ipWidth = self.ipaddr.GetSize().GetWidth()
		
		self.portLabel = wx.StaticText( self, -1, 'Remote Port:' )
		self.port = wx.lib.intctrl.IntCtrl( self, -1, min=1, max=65535, value=PORT, limited=True, size=(ipWidth,-1), style = wx.TE_READONLY )
		
		self.testJChip = wx.ToggleButton( self, -1, 'Start JChip Test' )
		self.Bind(wx.EVT_TOGGLEBUTTON, self.testJChipToggle, self.testJChip)
		
		self.testList = ListCtrlAutoWidth( self, -1, style=wx.LC_REPORT )
		self.testList.InsertColumn(0, "Messages Received:")
		self.testList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		
		self.okBtn = wx.Button( self, wx.ID_ANY, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_ANY, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		
		todoList = [
			'Make sure the JChip receiver is plugged into the network.',
			'Do a "Sync PC" on the JChip receiver to synchronize with your computer clock.',
			'Verify that the JChip has a "TCP Client" connection to the CrossMgr computer (see below).',
			'You must have the Sign-On Excel sheet ready and linked before your race.',
			'You must configure a "Tag" field in your Sign-On Excel Sheet.',
			'Run this test before each race.',
			'Make sure to set the "Read JChip Tags During Race" option.',
		]
		intro = 'CrossMgr supports the JChip tag reader.\n' \
				'For more details, consult the CrossMgr and JChip documentation.\n' \
				'\nChecklist:\n\n%s\n' % '\n'.join( '%d)  %s' % (i + 1, s) for i, s in enumerate(todoList) )
		
		border = 6
		row = 0
		bs.Add( wx.StaticText( self, -1, intro ),
				pos = (row, 0), span=(1, 2), border = border, flag = wx.GROW|wx.ALL|wx.ALIGN_LEFT )

		row += 1
		bs.Add( self.enableJChipCheckBox, pos=(row,0), span=(1, 2), border = border, flag=wx.GROW|wx.ALL|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, -1, 'JChip Receiver Configuration:' ),
				pos = (row, 0), span=(1, 2), border = border, flag = wx.GROW|wx.ALL|wx.ALIGN_LEFT )
				
		row += 1
		bs.Add( wx.StaticText( self, -1, 'Type:' ), pos=(row, 0), span=(1, 1), border = border,
			flag=wx.TOP|wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		bs.Add( wx.TextCtrl( self, -1, value='TCP Client', size=(ipWidth,-1), style = wx.TE_READONLY),
			pos=(row, 1), span=(1, 1), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( self.ipaddrLabel, pos=(row, 0), span=(1, 1), border = border,
			flag=wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		bs.Add( self.ipaddr, pos=(row, 1), span=(1, 1), border = border, flag=wx.RIGHT|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( self.portLabel, pos=(row, 0), span=(1, 1), border = border,
			flag=wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		bs.Add( self.port, pos=(row, 1), span=(1, 1), border = border, flag=wx.RIGHT|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, -1, 'See "7  Setting of Connections" in JChip "Control Panel Soft Manual" for more details.' ),
				pos = (row, 0), span=(1, 2), border = border, flag = wx.GROW|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ALIGN_LEFT )

		row += 1
		bs.Add( self.testJChip, pos=(row,0), span=(1, 2), border = border, flag=wx.GROW|wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTRE )
		
		row += 1
		height = 10
		bs.Add( self.testList, pos=(row,0), span=(height, 2), border = border, flag=wx.GROW|wx.RIGHT|wx.BOTTOM|wx.LEFT|wx.ALIGN_CENTRE )
		row += height - 1
		
		row += 1
		bs.Add( self.okBtn, pos=(row, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(row, 1), span=(1,1), border = border, flag=wx.ALL|wx.ALIGN_RIGHT )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def testJChipToggle( self, event ):
		if not JChip.listener:
			correct, reason = CheckExcelLink()
			explain = 	'CrossMgr will not be able to associate chip Tags with Bib numbers.\n' \
						'You may proceed with the test, but you need to fix the Excel sheet.\n\n' \
						'See documentation for more details.'
			if not correct:
				if not Utils.MessageOKCancel( self, 'Problems with Excel sheet.\n\n    Reason: %s\n\n%s' % (reason, explain),
									title = 'Excel Link Problem', iconMask = wx.ICON_WARNING ):
					self.testJChip.SetValue( False )
					return
			tagNums = GetTagNums()
			if correct and not tagNums:
				if not Utils.MessageOKCancel( self, 'All Tag entries in the Excel sheet are blank.\n\n%s' % explain,
									title = 'Excel Link Problem', iconMask = wx.ICON_WARNING ):
					self.testJChip.SetValue( False )
					return
			
			self.testList.DeleteAllItems()
			JChip.StartListener()
			
			self.appendMsg( 'listening for connection...' )
			
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
			self.testList.DeleteAllItems()
	
	def appendMsg( self, s ):
		self.testList.InsertStringItem( self.testList.GetItemCount(), s )
	
	def onTimerCallback( self, stat ):
		data = JChip.GetData()
		for d in data:
			if d[0] == 'data':
				self.receivedCount += 1
				ts = d[2].isoformat()
				if len(ts) == 8:
					ts += '.00'
				else:
					ts = ts[:-4]
				try:
					num = str(Model.race.tagNums[d[1]])
				except (AttributeError, ValueError, KeyError):
					num = 'not found'
				self.appendMsg( '%d: received: %s at %s, Bib#: %s' % (self.receivedCount, d[1], ts, num) )
			elif d[0] == 'connected':
				self.appendMsg( 'connected' )
			elif d[0] == 'disconnected':
				self.appendMsg( 'disconnected' )
				self.appendMsg( 'listening for connection...' )
			elif d[0] == 'name':
				self.appendMsg( 'accepted connection from: %s' % d[1] )
		if data:
			self.testList.EnsureVisible( self.testList.GetItemCount()-1 )
		self.timer.Restart( 1000, 'restarted' )
		
	def onOK( self, event ):
		if Model.race:
			Model.race.enableJChipIntegration = self.enableJChipCheckBox.GetValue()
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		if JChip.listener:
			self.testJChipToggle( event )
		self.EndModal( wx.ID_CANCEL )
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	mainWin.Show()
	dlg = JChipSetupDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

