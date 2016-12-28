import requests
import datetime
import os
import wx
import wx.gizmos as gizmos
import Utils
import Model
from ReadSignOnSheet	import ExcelLink

globalRaceDBUrl = ''

def RaceDBUrlDefault():
	#return 'http://{}:8000/RaceDB'.format( Utils.GetDefaultHost() )
	return globalRaceDBUrl or 'http://{}:8000/RaceDB'.format( '127.0.0.1' )
	
def CrossMgrFolderDefault():
	return os.path.join( os.path.expanduser('~'), 'CrossMgrRaces' )

def GetRaceDBEvents( url = None, date=None ):
	url = url or RaceDBUrlDefault()
	url += '/GetEvents'
	if date:
		url += date.strftime('/%Y-%m-%d')
	req = requests.get( url + '/' )
	events = req.json()
	return events
	
def GetEventCrossMgr( url, eventId, eventType ):
	url = url or RaceDBUrlDefault()
	url +=['/EventMassStartCrossMgr','/EventTTCrossMgr'][eventType] + '/{}'.format(eventId)
	req = requests.get( url + '/' )
	content_disposition = req.headers['content-disposition'].encode('latin-1').decode('utf-8')
	filename = content_disposition.split('=')[1].replace("'",'').replace('"','')
	return filename, req.content

class URLDropTarget(wx.PyDropTarget):
	def __init__(self, window, callback=None):
		wx.PyDropTarget.__init__(self)
		self.window = window
		self.callback = callback
		self.data = wx.URLDataObject();
		self.SetDataObject(self.data)

	def OnDragOver(self, x, y, d):
		return wx.DragLink

	def OnData(self, x, y, d):
		if not self.GetData():
			return wx.DragNone
		url = self.data.GetURL()
		if not (url.startswith('http://') or url.startswith('https://')):
			url = 'http://' + url
		self.window.SetValue(url)
		if self.callback:
			wx.CallAfter( self.callback )
		return d

class RaceDB( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, size=(1100,500) ):
		super(RaceDB, self).__init__(parent, id, style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME, size=size, title=_('Open RaceDB Event'))
		
		fontPixels = 20
		font = wx.FontFromPixelSize(wx.Size(0,fontPixels), wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		
		explain = wx.StaticText( self, label=(u'{}:').format(
			_('Drag and Drop any RaceDB URL from the browser.\n\nDrag the small icon just to the left of the URL\non the browser page to the RaceDB logo below') ) )
		explain.SetFont( font )
		
		raceDBLogo = wx.StaticBitmap( self, bitmap=wx.Bitmap( os.path.join(Utils.getImageFolder(), 'RaceDB_big.png'), wx.BITMAP_TYPE_PNG ) )
		
		self.raceFolder = wx.DirPickerCtrl( self, path=CrossMgrFolderDefault() )
		self.raceDBUrl = wx.TextCtrl( self, value=RaceDBUrlDefault(), style=wx.TE_PROCESS_ENTER )
		self.raceDBUrl.Bind( wx.EVT_TEXT_ENTER, self.onChange )
		self.raceDBUrl.SetDropTarget(URLDropTarget(self.raceDBUrl, self.refresh))
		raceDBLogo.SetDropTarget(URLDropTarget(self.raceDBUrl, self.refresh))
		self.datePicker = wx.DatePickerCtrl( self, size=(120,-1), style = wx.DP_DROPDOWN | wx.DP_SHOWCENTURY )
		self.datePicker.Bind( wx.EVT_DATE_CHANGED, self.onChange )
		
		fgs = wx.FlexGridSizer( cols=2, rows=0, vgap=4, hgap=4 )
		fgs.AddGrowableCol( 1, 1 )
		
		fgs.Add( wx.StaticText(self, label=_('Race Folder Base')), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		fgs.Add( self.raceFolder, 1, flag=wx.EXPAND )
		fgs.Add( wx.StaticText(self, label=_('RaceDB URL')), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		fgs.Add( self.raceDBUrl, 1, flag=wx.EXPAND )
		fgs.Add( wx.StaticText(self, label=_('All Events On')), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.datePicker, flag=wx.ALIGN_CENTER_VERTICAL )
		self.updateButton = wx.Button( self, label=_('Update') )
		self.updateButton.Bind( wx.EVT_BUTTON, self.onChange )
		hs.Add( self.updateButton, flag=wx.LEFT, border=16 )
		fgs.Add( hs )
		
		vsHeader = wx.BoxSizer( wx.VERTICAL )
		vsHeader.Add( raceDBLogo, flag=wx.ALIGN_CENTRE )
		vsHeader.Add( fgs, 1, flag=wx.EXPAND )
		
		self.tree = gizmos.TreeListCtrl( self, style=wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_ROW_LINES )
		self.tree.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.onEventSelect )
		
		isz = (16,16)
		self.il = wx.ImageList( *isz )
		self.closedIdx		= self.il.Add( wx.ArtProvider_GetBitmap(wx.ART_FOLDER,	 	wx.ART_OTHER, isz))
		self.expandedIdx	= self.il.Add( wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, 	wx.ART_OTHER, isz))
		self.fileIdx		= self.il.Add( wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE,	wx.ART_OTHER, isz))
		self.selectedIdx	= self.il.Add( wx.ArtProvider_GetBitmap(wx.ART_LIST_VIEW, 	wx.ART_OTHER, isz))
		
		self.tree.SetImageList( self.il )
		
		self.tree.AddColumn( _('Event Info') )
		self.tree.AddColumn( _('Event Type'), flag=wx.ALIGN_LEFT )
		self.eventTypeCol = 1
		self.tree.AddColumn( _('Start Time'), flag=wx.ALIGN_RIGHT )
		self.startTimeCol = 2
		self.tree.AddColumn( _('Participants'), flag=wx.ALIGN_RIGHT)
		self.participantCountCol = 3
		
		self.tree.SetMainColumn( 0 )
		self.tree.SetColumnWidth( 0, 320 )
		self.tree.SetColumnWidth( self.eventTypeCol, 80 )
		self.tree.SetColumnWidth( self.startTimeCol, 80 )
		self.tree.SetColumnWidth( self.participantCountCol, 80 )
		
		self.tree.Bind( wx.EVT_TREE_SEL_CHANGED, self.selectChangedCB )
		self.dataSelect = None
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.okButton = wx.Button( self, label=_("Open Event") )
		self.okButton.Bind( wx.EVT_BUTTON, self.doOK )
		self.cancelButton = wx.Button( self, id=wx.ID_CANCEL )
		hs.Add( self.okButton )
		hs.AddStretchSpacer()
		hs.Add( self.cancelButton, flag=wx.LEFT, border=4 )
		
		hsMain = wx.BoxSizer( wx.HORIZONTAL )
		
		vs1 = wx.BoxSizer( wx.VERTICAL )
		vs1.Add( explain, flag=wx.ALL, border=8 )
		vs1.Add( vsHeader, flag=wx.ALL|wx.EXPAND, border=8 )
		
		vs2 = wx.BoxSizer( wx.VERTICAL )
		vs2.Add( self.tree, 1, flag=wx.EXPAND )
		vs2.Add( hs, 0, flag=wx.EXPAND|wx.ALL, border=8 )
		
		hsMain.Add( vs1 )
		hsMain.Add( vs2, 1, flag=wx.EXPAND )
		self.SetSizer( hsMain )
		
		self.refresh()

	def onChange( self, event ):
		wx.CallAfter( self.refresh )
	
	def fixUrl( self ):
		global globalRaceDBUrl
		url = self.raceDBUrl.GetValue().strip()
		if not url:
			url = RaceDBUrlDefault()
		url = url.split('RaceDB')[0] + 'RaceDB'
		while url.endswith( '/' ):
			url = url[:-1]
		self.raceDBUrl.SetValue( url )
		globalRaceDBUrl = url
		return url
	
	def doOK( self, event ):
		if not self.dataSelect:
			return
		
		url = self.fixUrl()
		
		try:
			filename, content = GetEventCrossMgr( url, self.dataSelect['pk'], self.dataSelect['event_type'] )
		except Exception as e:
			Utils.MessageOK(
				self,
				u'{}\n\n"{}"\n\n{}'.format(_('Error Connecting to RaceDB Server'), url, e),
				_('Error Connecting to RaceDB Server'),
				iconMask=wx.ICON_ERROR )
			return
		
		if not Utils.MessageOKCancel( self, u'{}:\n\n"{}"'.format( _('Confirm Open Event'), filename), _('Confirm Open Event') ):
			return
		
		dir = os.path.join(
			self.raceFolder.GetPath().strip() or CrossMgrFolderDefault(),
			Utils.RemoveDisallowedFilenameChars(self.dataSelect['competition_name']),
		)
		if not os.path.isdir(dir):
			try:
				os.makedirs( dir )
			except Exception as e:
				Utils.MessageOK(
					self,
					u'{}\n\n"{}"'.format( _('Error Creating Folder'), e),
					_('Error Creating Folder'),
					iconMask=wx.ICON_ERROR,
				)
				return
		
		excelFName = os.path.join(dir, filename)
		try:
			with open( excelFName, 'wb' ) as f:
				f.write( content )
		except Exception as e:
			Utils.MessageOKCancel(
				self,
				u'{}\n\n{}\n\n{}'.format( _('Error Writing File'), e, excelFName),
				_('Error Writing File'),
				iconMask=wx.ICON_ERROR,
			)
			return
		
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.openRaceDBExcel( excelFName, overwriteExisting=False )
		
		self.EndModal( wx.ID_OK )		
	
	def selectChangedCB( self, evt ):
		try:
			self.dataSelect = self.tree.GetItemPyData(evt.GetItem())
		except Exception as e:
			self.dataSelect = None
	
	def onEventSelect( self, evt ):
		try:
			self.dataSelect = self.tree.GetItemPyData(evt.GetItem())
			self.doOK( evt )
		except Exception as e:
			self.dataSelect = None
	
	def refresh( self, events=None ):
		if events is None:
			try:
				d = self.datePicker.GetValue()
				events = GetRaceDBEvents(
					url=self.fixUrl(),
					date=datetime.date( d.GetYear(), d.GetMonth()+1, d.GetDay() ),
				)
			except Exception as e:
				print e
				events = {'events':[]}
		
		competitions = {}
		for e in events['events']:
			try:
				competition = competitions[e['competition_name']]
			except KeyError:
				competition = competitions[e['competition_name']] = {
					'num':len(competitions),
					'name':e['competition_name'],
					'participant_count':0,
					'events':[],
				}
			competition['events'].append( e )
			competition['participant_count'] += e['participant_count']
		
		self.tree.DeleteAllItems()
		self.root = self.tree.AddRoot( _('All') )
		self.tree.SetItemText(
			self.root,
			unicode(sum(c['participant_count'] for c in competitions.itervalues())), self.participantCountCol
		)
		
		def get_tod( t ):
			return t.split()[1][:5].lstrip('0')
			
		def get_time( t ):
			return datetime.time( *[int(f) for f in get_tod(t).split(':')] )
			
		tNow = datetime.datetime.now()
		eventClosest = None
		self.dataSelect = None
		
		for cName, events, participant_count, num in sorted(
				((c['name'], c['events'], c['participant_count'], c['num']) for c in competitions.itervalues()), key=lambda x: x[-1] ):
			competition = self.tree.AppendItem( self.root, cName )
			self.tree.SetItemText( competition, unicode(participant_count), self.participantCountCol )
			for e in events:
				eventData = e
				event = self.tree.AppendItem( competition, u'{}: {}'.format(_('Event'), e['name']), data=wx.TreeItemData(eventData) )
				self.tree.SetItemText( event, get_tod(e['date_time']), self.startTimeCol )
				self.tree.SetItemText( event, _('Mass Start') if e['event_type'] == 0 else _('Time Trial'), self.eventTypeCol )
				self.tree.SetItemText( event, unicode(e['participant_count']), self.participantCountCol )
				
				tEvent = datetime.datetime.combine( tNow.date(), get_time(e['date_time']) )
				if eventClosest is None and tEvent > tNow:
					eventClosest = event
					self.dataSelect = eventData
				
				for w in e['waves']:
					wave = self.tree.AppendItem( event, u'{}: {}'.format(_('Wave'), w['name']), data=wx.TreeItemData(eventData) )
					self.tree.SetItemText( wave, unicode(w['participant_count']), self.participantCountCol )
					start_offset = w.get('start_offset',None)
					if start_offset:
						self.tree.SetItemText( wave, '+' + start_offset, self.startTimeCol )
					for cat in w['categories']:
						category = self.tree.AppendItem( wave, cat['name'], data=wx.TreeItemData(eventData) )
						self.tree.SetItemText( category, unicode(cat['participant_count']), self.participantCountCol )
			self.tree.Expand( competition )
						
		self.tree.Expand( self.root )
		if eventClosest:
			self.tree.SelectItem( eventClosest )
			self.tree.Expand( eventClosest )

#----------------------------------------------------------------------------------------------------------------------------
def PostEventCrossMgr( url ):
	url = (url or RaceDBUrlDefault()) + '/UploadCrossMgr'
	mainWin = Utils.getMainWin()
	payload = mainWin.getBasePayload( publishOnly=False ) if mainWin else {}
	req = requests.post( url + '/', json=payload )
	return req.json()

class RaceDBUpload( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, size=(700,500) ):
		super(RaceDBUpload, self).__init__(parent, id, style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME, size=size, title=_('Upload Results to RaceDB'))
		
		fontPixels = 20
		font = wx.FontFromPixelSize(wx.Size(0,fontPixels), wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		self.headerDefault = u'{}\n{}'.format(_('Upload'),u'')
		self.header = wx.StaticText( self, label=self.headerDefault )
		self.header.SetFont( font )
		
		fontPixels = 15
		font = wx.FontFromPixelSize(wx.Size(0,fontPixels), wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		explain = wx.StaticText( self, label=(u'{}:').format(
			_('Drag and Drop any RaceDB URL from the browser.\n\nDrag the small icon just to the left of the URL\non the browser page to the RaceDB logo below') ) )
		explain.SetFont( font )
		
		raceDBLogo = wx.StaticBitmap( self, bitmap=wx.Bitmap( os.path.join(Utils.getImageFolder(), 'RaceDB_big.png'), wx.BITMAP_TYPE_PNG ) )
		
		self.raceDBUrl = wx.TextCtrl( self, value=RaceDBUrlDefault(), style=wx.TE_PROCESS_ENTER )
		self.raceDBUrl.SetDropTarget(URLDropTarget(self.raceDBUrl, self.refresh))
		raceDBLogo.SetDropTarget(URLDropTarget(self.raceDBUrl, self.refresh))
		
		self.uploadStatus = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER|wx.TE_READONLY|wx.TE_DONTWRAP)
		
		fgs = wx.FlexGridSizer( cols=2, rows=0, vgap=4, hgap=4 )
		fgs.AddGrowableCol( 1, 1 )
		
		fgs.Add( wx.StaticText(self, label=_('RaceDB URL')), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		fgs.Add( self.raceDBUrl, 1, flag=wx.EXPAND )
		
		vsHeader = wx.BoxSizer( wx.VERTICAL )
		vsHeader.Add( raceDBLogo, flag=wx.ALIGN_CENTRE )
		vsHeader.Add( fgs, 1, flag=wx.EXPAND )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.okButton = wx.Button( self, label=_("Upload") )
		self.okButton.Bind( wx.EVT_BUTTON, self.doUpload )
		self.cancelButton = wx.Button( self, id=wx.ID_CANCEL, label=_("Done") )
		hs.Add( self.okButton )
		hs.AddStretchSpacer()
		hs.Add( self.cancelButton, flag=wx.LEFT, border=4 )
		
		mainSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		vs1 = wx.BoxSizer( wx.VERTICAL )
		vs1.Add( self.header, flag=wx.ALL, border=8 )
		vs1.Add( explain, flag=wx.ALL, border=8 )
		vs1.Add( vsHeader, flag=wx.ALL|wx.EXPAND, border=8 )
		vs1.Add( hs, flag=wx.ALL, border=4 )
		
		mainSizer.Add( vs1 )
		mainSizer.Add( self.uploadStatus, 1, flag=wx.ALL|wx.EXPAND, border=4 )
		
		self.SetSizer( mainSizer )
		
		self.refresh()

	def fixUrl( self ):
		global globalRaceDBUrl
		url = self.raceDBUrl.GetValue().strip()
		if not url:
			url = RaceDBUrlDefault()
		url = url.split('RaceDB')[0] + 'RaceDB'
		while url.endswith( '/' ):
			url = url[:-1]
		self.raceDBUrl.SetValue( url )
		globalRaceDBUrl = url
		return url
	
	def refresh( self, events=None ):
		self.fixUrl()
		headerText = self.headerDefault
		race = Model.race
		if race:
			headerText = u'{}\n{} {}'.format(race.name, race.date, race.scheduledStart)
		self.header.SetLabel( headerText )

	def doUpload( self, event ):
		busy = wx.BusyCursor()
		url = self.fixUrl()
		try:
			response = PostEventCrossMgr( url )
		except Exception as e:
			response = {'errors':[unicode(e)], 'warnings':[]}
		
		if response.get('errors',None) or response.get('warnings',None):
			resultText = u'\n'.join( u'{}: {}'.format(_('Error'), e) for e in response.get('errors',[]) )
			if resultText:
				resultText += u'\n\n'
			resultText += u'\n'.join( u'{}: {}'.format(_('Warning'),w) for w in response.get('warnings',[]) )
		
		if not response.get('errors',None):
			if resultText:
				resultText += u'\n\n'
			resultText += u_('Upload Successful.')
		
		self.uploadStatus.SetValue( resultText )
	
if __name__ == '__main__':
	if True:
		app = wx.App(False)
		mainWin = wx.Frame(None,title="CrossMan", size=(1000,400))
		raceDBUpload = RaceDBUpload(mainWin)
		raceDBUpload.ShowModal()
	
	else:

		events = GetRaceDBEvents()
		print GetRaceDBEvents( date=datetime.date.today() )
		print GetRaceDBEvents( date=datetime.date.today() - datetime.timedelta(days=2) )
		
		app = wx.App(False)
		mainWin = wx.Frame(None,title="CrossMan", size=(1000,400))
		raceDB = RaceDB(mainWin)
		raceDB.refresh( events )
		raceDB.ShowModal()
		#app.MainLoop()

