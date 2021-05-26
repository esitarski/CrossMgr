import re
import sys
import datetime
import threading
from queue import Queue, Empty
import wx
import wx.lib.mixins.listctrl as listmix

import Utils

class AutoWidthListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, id = wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, id, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

class BackgroundJobMgr( wx.Dialog ):
	timeoutSecs = 10*60
	
	def __init__( self, parent, id = wx.ID_ANY, style=0 ):
		super().__init__( parent, id, _('Background Job Mgr'),
						style=style|wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL|wx.RESIZE_BORDER )
		self.jobList = AutoWidthListCtrl( self, style = wx.LC_REPORT|wx.LC_HRULES )
		for col, (k, name, align) in enumerate((
				('num',			'     ',		wx.LIST_FORMAT_RIGHT),
				('name', 		_('Name'),		wx.LIST_FORMAT_LEFT),
				('start',		_('Start'),		wx.LIST_FORMAT_RIGHT),
				('end',			_('End'),		wx.LIST_FORMAT_RIGHT),
				('dur',			_('Dur'),		wx.LIST_FORMAT_RIGHT),
				('status', 		_('Status'),	wx.LIST_FORMAT_LEFT),
				('message',		_('Message'),	wx.LIST_FORMAT_LEFT),
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
		
		self.jobs = {}
		
		self.q = Queue()
		self.q_processor = threading.Thread( target=self.processQ )
		self.q_processor.daemon = True
		self.q_processor.start()
		
		self.callLater = None
		
		self.SetSizerAndFit( vs )
		
	def refresh( self ):
		if not self.IsShownOnScreen():
			return
		
		def formatTime( t ):
			return t.strftime('%H:%M:%S') if t is not None else ''
		
		def formatDiff( end, start ):
			secs = int((end - start).total_seconds())
			hh = secs // (60*60)
			mm = (secs // 60) % 60
			ss = secs % 60
			return '{:02d}:{:02d}:{:02d}'.format( hh, mm, ss )

		self.jobList.DeleteAllItems()

		now = datetime.datetime.now()
		delta = datetime.timedelta( seconds=self.timeoutSecs )
		self.jobs = {k:v for k,v in self.jobs.items() if now - v.get('end',now) < delta}

		colours = (wx.GREEN, wx.YELLOW, wx.RED)

		allDone = True
		highlight = {}
		for row, v in enumerate( sorted( self.jobs.values(), key=lambda v: (v['start'], v.get('end', now)) ) ):
			self.jobList.Append( [
				'{}.'.format(row+1),
				v.get('name',''),
				formatTime( v.get('start',None) ),
				formatTime( v.get('end',None) ),
				formatDiff( v.get('end', now), v.get('start',now) ),
				v.get('status',''),
				v.get('message',''),
			])
			if v['code'] != 0 or 'end' in v:
				highlight[row] = colours[v['code']]
			if 'end' not in v:
				allDone = False
				
		for row, colour in highlight.items():
			self.jobList.SetItemBackgroundColour( row, colour )
			if colour == wx.RED:
				self.jobList.SetItemTextColour( row, wx.WHITE )
			
		for i in range(self.jobList.GetColumnCount()):
			self.jobList.SetColumnWidth( i, wx.LIST_AUTOSIZE_USEHEADER )
		
		if not allDone:
			if not self.callLater:
				self.callLater = wx.CallLater( 1000, self.refresh )
			elif not self.callLater.IsRunning():
				self.callLater.Start( 1000 )
	
	def ShowModal( self, *args, **kwargs ):
		wx.CallAfter( self.refresh )
		return super().ShowModal( *args, **kwargs )
	
	def processQ( self ):
		while True:
			msg = self.q.get()
			cmd, id = msg.get('cmd', None), msg.get('id', None)
			
			# recognized messages are 'start', 'update' and 'end'
			# messages must include a unique 'id' field.
			# messages can also include other fields including 'name', 'status' and 'message'
			# code can have values of 0, 1 and 2. 0 = OK, 1 = Caution, 2 = Error
			if   cmd == 'start':
				msg['start'] = datetime.datetime.now()
				msg['code'] = msg.get('code',0)
				self.jobs[id] = msg
			elif cmd == 'update':
				self.jobs[id].update( msg )
			elif cmd == 'end':
				msg['end'] = datetime.datetime.now()
				self.jobs[id].update( msg )
			
			wx.CallAfter( self.refresh )
	
	def send( self, msg ):
		self.q.put( msg )
	
	def onOK( self, event ):
		self.Show( False )
		
	def onCopyToClipboard( self, event ):
		def csvEscape( s ):
			s = s.strip()
			if not re.match( '[",\n]', s):
				return s
			return '"{}"'.format( s.replace('"', '""') )	# double-up quotes to escape.
		
		rowsToCopy = []
		for row in range(self.jobList.GetItemCount()):
			for col in range(1, self.jobList.GetColumnCount()):
				rowsToCopy.append(','.join(csvEscape(self.jobList.GetItemText(row, col))))

		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData( wx.TextDataObject( '\n'.join(rowsToCopy) ) )
			wx.TheClipboard.Close()
			
if __name__ == '__main__':
	import time
	import uuid
	import random
	
	def doSomething( q ):
		id = uuid.uuid4().hex
		def put( kwargs ):
			kwargs['id'] = id
			q.put( kwargs )
		put( {'cmd':'start', 'name':'doSomething', 'message':'In progress', 'status':'OK'} )
		time.sleep( random.randrange(5, 20) )
		if random.randrange(0,2):
			put( {'cmd':'update', 'message':'Still Processing', 'status':'More work than expected', 'code':random.randrange(1,3)} )
			time.sleep( random.randrange(5, 30) )
		if random.randrange(0,2):
			put( {'cmd':'update', 'message':'Unexpected Processing', 'status':'That was unexpected!', 'code':2} )
			time.sleep( random.randrange(5, 30) )
		put( {'cmd':'end', 'message':'Done.', 'status':'Success', 'code':0} )
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	bjm = BackgroundJobMgr(mainWin)
	mainWin.Show()
	wx.CallLater( 500, bjm.ShowModal )
	for i in range(15):
		threading.Thread( target=doSomething, args=(bjm.q,) ).start()
	app.MainLoop()
		
