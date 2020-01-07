import wx
import wx.lib.mixins.listctrl as listmix
import threading
import datetime
import Utils

class AutoWidthListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID = wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

class BackgroundJobMgr( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY, style=0 ):
		super(BackgroundJobMgr, self).__init__( parent, id, _('Background Job Mgr'),
						style=style|wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL|wx.RESIZE_BORDER )
		self.jobList = AutoWidthListCtrl( self, style = wx.LC_REPORT|wx.LC_HRULES )
		for col, (k, name, align) in enumerate((
				('name', 		_('Name'),		wx.LIST_FORMAT_LEFT),
				('status', 		_('Status'),	wx.LIST_FORMAT_LEFT),
				('message',		_('Message'),	wx.LIST_FORMAT_LEFT),
				('start',		_('Start'),		wx.LIST_FORMAT_LEFT),
				('end',			_('End'),		wx.LIST_FORMAT_LEFT),
				('dur',			_('Dur'),		wx.LIST_FORMAT_RIGHT),
				('id',			_('ID'),		wx.LIST_FORMAT_LEFT),
			)):
			self.jobList.AppendColumn( name, align )
			setattr( self, k + 'Col', col )
		
		self.okButton = wx.Button( self, id=wx.ID_OK )
		self.okButton.Bind( wx.EVT_BUTTON, self.onOK )
		
		buttonSizer = wx.StdDialogButtonSizer()
		buttonSizer.AddButton( self.okButton )
		buttonSizer.Realize()
		
		vs = wx.BoxSizer( wx.VERTICAL )
		vs.Add( self.jobList, 1, flag=wx.ALL|wx.EXPAND, border=8 )
		vs.Add( buttonSizer, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border=8 )
		
		self.SetSizerAndFit( vs )
	
	def onOK( self, event ):
		self.Show( False )
	
	def set( self, uid, name=None, status=None, message=None, end=None ):
		row = self.findThread( uid )
		if row is None:
			self.jobList.Append( [
				name if name else '',
				status if status else '',
				message if message else '',
				datetime.datetime.now().strftime('%H:%M:%S'),
				'',	# end
				'',	# duration
				uid,
			])
		else:
			if end is not None:
				start = self.jobList.GetItem(row, self.startCol).GetText()
				end = end.strftime('%H:%M:%S')
				startSecs = sum( int(v)*60**(2-i) for i, v in enumerate(start.split(':')) )
				endSecs = sum( int(v)*60**(2-i) for i, v in enumerate(end.split(':')) )
				self.jobList.SetItem( row, self.endCol, end )
				self.jobList.SetItem( row, self.durCol, '    {}s'.format(max(1,round(abs(endSecs-startSecs)))) )
			if name is not None:
				self.jobList.SetItem( row, self.nameCol, name )
			if status is not None:
				self.jobList.SetItem( row, self.statusCol, status )
			if message is not None:
				self.jobList.SetItem( row, self.messageCol, message )
			
		for i in range(self.jobList.GetColumnCount()):
			self.jobList.SetColumnWidth( i, wx.LIST_AUTOSIZE )
		

		
	def findThread( self, uid ):
		for row in range(self.jobList.GetItemCount()):
			v = self.jobList.GetItem(row, self.idCol).GetText()
			if v == uid:
				return row
		return None
		
	def endThread( self, uid, message, timeoutSeconds=10*60 ):
		if timeoutSeconds:
			self.set( uid, status=_('Ended'), message=message, end=datetime.datetime.now() )
			wx.CallLater( int(timeoutSeconds*1000), self.endThread, uid, message, 0 )
		else:
			self.jobList.DeleteItem( self.findThread(uid) )

	def runAsThread( self, target, name, args=(), kwargs={} ):
		uid = '{:X}'.format(random.getrandbits(31))
		def wrapTarget():
			message = target( *args, **kwargs )
			wx.CallAfter( self.endThread, uid, '{}'.format(message) if message is not None else _('Success') )
		thread = threading.Thread( target=wrapTarget, name=name, daemon=True )
		self.set( uid, name, _('Running...') )
		thread.start()
		
if __name__ == '__main__':
	import time
	import random
	
	def delayFunc( d ):		
		time.sleep( d )
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	bjm = BackgroundJobMgr(mainWin)
	mainWin.Show()
	wx.CallLater( 500, bjm.ShowModal )
	for i in range(20):
		bjm.runAsThread( delayFunc, 'test {}'.format(i), args=(1.0+random.random()*20,) )
	app.MainLoop()
		