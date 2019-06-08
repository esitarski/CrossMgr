import re
import os
import wx
import requests
import datetime
import wx.dataview as dataview
import Utils
import Model
from ReadSignOnSheet	import ExcelLink

globalRaceDBUrl = ''

def RaceDBUrlDefault():
	#return 'http://{}:8000/RaceDB'.format( Utils.GetDefaultHost() )
	return globalRaceDBUrl or 'http://{}:8000/RaceDB'.format( '127.0.0.1' )

def fixUrl( url ):
	global globalRaceDBUrl
	url = url.strip()
	if not url:
		url = RaceDBUrlDefault()
	if not (url.startswith('http://') or url.startswith('https://')):
		url = 'http://' + url.lstrip('/')
	url = url.split('RaceDB')[0] + 'RaceDB'
	url = url.rstrip('/')
	globalRaceDBUrl = url
	return url

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
	content_disposition = req.headers['content-disposition'].encode('latin-1').decode()
	filename = content_disposition.split('=')[1].replace("'",'').replace('"','')
	return filename, req.content

class URLDropTarget(wx.DropTarget):
	def __init__(self, window, callback=None):
		super( URLDropTarget, self ).__init__()
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
		super(RaceDB, self).__init__(parent, id, style=wx.DEFAULT_DIALOG_STYLE, size=size, title=_('Open RaceDB Event'))
		
		fontPixels = 20
		font = wx.Font((0,fontPixels), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		
		explain = wx.StaticText( self, label=(u'{}:').format(
			_('Drag and Drop any RaceDB URL from the browser.\n\nDrag the small icon just to the left of the URL\non the browser page to the RaceDB logo below') ) )
		explain.SetFont( font )
		
		raceDBLogo = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( os.path.join(Utils.getImageFolder(), 'RaceDB_big.png'), wx.BITMAP_TYPE_PNG ) )
		
		self.raceFolder = wx.DirPickerCtrl( self, path=CrossMgrFolderDefault() )
		self.raceDBUrl = wx.TextCtrl( self, value=RaceDBUrlDefault(), style=wx.TE_PROCESS_ENTER )
		self.raceDBUrl.Bind( wx.EVT_TEXT_ENTER, self.onChange )
		self.raceDBUrl.SetDropTarget(URLDropTarget(self.raceDBUrl, self.refresh))
		raceDBLogo.SetDropTarget(URLDropTarget(self.raceDBUrl, self.refresh))
		self.datePicker = wx.adv.DatePickerCtrl(
			self,
			size=(120,-1),
			dt=Utils.GetDateTimeToday(),
			style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY
		)
		self.datePicker.Bind( wx.adv.EVT_DATE_CHANGED, self.onChange )
		
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
		
		self.tree = dataview.TreeListCtrl( self, style=wx.dataview.TL_SINGLE )
		self.tree.Bind( dataview.EVT_TREELIST_ITEM_ACTIVATED, self.onEventSelect )
		
		self.status = wx.StaticText( self, label=u'\n\n' )
		
		isz = (16,16)
		self.il = wx.ImageList( *isz )
		self.closedIdx		= self.il.Add( wx.ArtProvider.GetBitmap(wx.ART_FOLDER,	 	wx.ART_OTHER, isz))
		self.expandedIdx	= self.il.Add( wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, 	wx.ART_OTHER, isz))
		self.fileIdx		= self.il.Add( wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE,	wx.ART_OTHER, isz))
		self.selectedIdx	= self.il.Add( wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, 	wx.ART_OTHER, isz))
		
		self.tree.SetImageList( self.il )
		
		self.tree.AppendColumn( _('Event Info') )
		self.tree.AppendColumn( _('Event Type'), align=wx.ALIGN_LEFT )
		self.eventTypeCol = 1
		self.tree.AppendColumn( _('Start Time'), align=wx.ALIGN_RIGHT )
		self.startTimeCol = 2
		self.tree.AppendColumn( _('Participants'), align=wx.ALIGN_RIGHT)
		self.participantCountCol = 3
		
		self.tree.SetColumnWidth( 0, 320 )
		self.tree.SetColumnWidth( self.eventTypeCol, 80 )
		self.tree.SetColumnWidth( self.startTimeCol, 80 )
		self.tree.SetColumnWidth( self.participantCountCol, 80 )
		
		self.tree.Bind( dataview.EVT_TREELIST_SELECTION_CHANGED, self.selectChangedCB )
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
		vs2.Add( self.status, 0, flag=wx.ALL|wx.EXPAND, border=4 )
		vs2.Add( hs, 0, flag=wx.EXPAND|wx.ALL, border=8 )
		
		hsMain.Add( vs1 )
		hsMain.Add( vs2, 1, flag=wx.EXPAND )
		self.SetSizer( hsMain )
		
		self.refresh()

	def onChange( self, event ):
		wx.CallAfter( self.refresh )
	
	def fixUrl( self ):
		url = fixUrl( self.raceDBUrl.GetValue() )
		self.raceDBUrl.SetValue( url )
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
			self.dataSelect = self.tree.GetItemData(evt.GetItem())
		except Exception as e:
			self.dataSelect = None
	
	def onEventSelect( self, evt ):
		try:
			self.dataSelect = self.tree.GetItemData(evt.GetItem())
			self.doOK( evt )
		except Exception as e:
			self.dataSelect = None
	
	def refresh( self, events=None ):
		e = None
		if events is None:
			try:
				d = self.datePicker.GetValue()
				events = GetRaceDBEvents(
					url=self.fixUrl(),
					date=datetime.date( d.GetYear(), d.GetMonth()+1, d.GetDay() ),
				)
			except Exception as e_current:
				e = e_current
				events = {'events':[]}

		if not e and not (events and events.get('events',None)):
			e = u'{} {:04d}-{:02d}-{:02d}'.format( _('No Events found on'), d.GetYear(), d.GetMonth()+1, d.GetDay() )
		self.status.SetLabel( u'{}'.format(e) if e else u'{}.'.format(_('Events retrieved successfully')) )
				
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
		self.root = self.tree.GetRootItem()
		
		def get_tod( t ):
			return t.split()[1][:5].lstrip('0')
			
		def get_time( t ):
			return datetime.time( *[int(f) for f in get_tod(t).split(':')] )
		
		dNow = datetime.datetime.now() + datetime.timedelta(minutes=15)
		def in_the_past( t ):
			values = re.sub( '[^0-9]', ' ', t ).split()[:6]	# get Y M D H M S - ignore timezone
			d = datetime.datetime( *[int(v) for v in values] )
			return d < dNow
			
		tNow = datetime.datetime.now()
		eventClosest = None
		self.dataSelect = None
		
		for cName, events, participant_count, num in sorted(
				((c['name'], c['events'], c['participant_count'], c['num']) for c in competitions.values()), key=lambda x: x[-1] ):
			competition = self.tree.AppendItem( self.root, cName )
			self.tree.SetItemText( competition, self.participantCountCol, u'{}'.format(participant_count) )
			for e in events:
				eventData = e
				event = self.tree.AppendItem( competition,
					u'{}{}: {}'.format(
						u'<{}> '.format(_('Past')) if in_the_past(e['date_time']) else u'',
						_('Event'),
						e['name']),
					data=eventData
				)
				self.tree.SetItemText( event, self.startTimeCol, get_tod(e['date_time']) )
				self.tree.SetItemText( event, self.eventTypeCol, _('Mass Start') if e['event_type'] == 0 else _('Time Trial') )
				self.tree.SetItemText( event, self.participantCountCol, u'{}'.format(e['participant_count']) )
				
				tEvent = datetime.datetime.combine( tNow.date(), get_time(e['date_time']) )
				if eventClosest is None and tEvent > tNow:
					eventClosest = event
					self.dataSelect = eventData
				
				for w in e['waves']:
					wave = self.tree.AppendItem( event, u'{}: {}'.format(_('Wave'), w['name']), data=eventData )
					self.tree.SetItemText( wave, self.participantCountCol, u'{}'.format(w['participant_count']) )
					start_offset = w.get('start_offset',None)
					if start_offset:
						self.tree.SetItemText( wave, self.startTimeCol, '+' + start_offset )
					for cat in w['categories']:
						category = self.tree.AppendItem( wave, cat['name'], data=eventData )
						self.tree.SetItemText( category, self.participantCountCol, u'{}'.format(cat['participant_count']) )
			self.tree.Expand( competition )
						
		self.tree.Expand( self.root )
		if eventClosest:
			self.tree.Select( eventClosest )
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
		super(RaceDBUpload, self).__init__(parent, id, style=wx.DEFAULT_DIALOG_STYLE, size=size, title=_('Upload Results to RaceDB'))
		
		fontPixels = 20
		font = wx.Font((0,fontPixels), wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		self.headerDefault = u'{}\n{}'.format(_('Upload'),u'')
		self.header = wx.StaticText( self, label=self.headerDefault )
		self.header.SetFont( font )
		
		fontPixels = 15
		font = wx.Font((0,fontPixels), wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		explain = wx.StaticText( self, label=(u'{}:').format(
			_('Drag and Drop any RaceDB URL from the browser.\n\nDrag the small icon just to the left of the URL\non the browser page to the RaceDB logo below') ) )
		explain.SetFont( font )
		
		raceDBLogo = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( os.path.join(Utils.getImageFolder(), 'RaceDB_big.png'), wx.BITMAP_TYPE_PNG ) )
		
		self.raceDBUrl = wx.TextCtrl( self, value=RaceDBUrlDefault(), style=wx.TE_PROCESS_ENTER )
		self.raceDBUrl.SetDropTarget(URLDropTarget(self.raceDBUrl, self.refresh))
		raceDBLogo.SetDropTarget(URLDropTarget(self.raceDBUrl, self.refresh))
		
		self.uploadStatus = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER|wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_BESTWRAP)
		
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
		url = fixUrl( self.raceDBUrl.GetValue() )
		self.raceDBUrl.SetValue( url )
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
		
		self.uploadStatus.SetValue( _("Starting Upload...") )
		resultText = u''
		
		url = self.fixUrl()
		try:
			response = PostEventCrossMgr( url )
		except Exception as e:
			response = {'errors':[u'{}'.format(e)], 'warnings':[]}
		
		if response.get('errors',None) or response.get('warnings',None):
			resultText = u'\n'.join( u'RaceDB{}: {}'.format(_('Error'), e) for e in response.get('errors',[]) )
			if resultText:
				resultText += u'\n\n'
			resultText += u'\n'.join( u'RaceDB{}: {}'.format(_('Warning'),w) for w in response.get('warnings',[]) )
		
		if not response.get('errors',None):
			if resultText:
				resultText += u'\n\n'
			if response.get('warnings',None):
				resultText += _('Otherwise, Upload Successful.')
			else:
				resultText += _('Upload Successful.')
		
		if resultText:
			resultText = u'url="{}"'.format( url ) + '\n' + resultText
		
		self.uploadStatus.SetValue( resultText )
		del busy
		Utils.MessageOK( self, u'{}:\n\n{}'.format(_('RaceDB Upload Status'), resultText), _('RaceDB Upload Status') )
	
if __name__ == '__main__':
	if True:
		app = wx.App(False)
		mainWin = wx.Frame(None,title="CrossMan", size=(1000,400))
		raceDBUpload = RaceDBUpload(mainWin)
		raceDBUpload.ShowModal()
	
	else:

		events = GetRaceDBEvents()
		print ( GetRaceDBEvents( date=datetime.date.today() ) )
		print ( GetRaceDBEvents( date=datetime.date.today() - datetime.timedelta(days=2) ) )
		
		app = wx.App(False)
		mainWin = wx.Frame(None,title="CrossMan", size=(1000,400))
		raceDB = RaceDB(mainWin)
		raceDB.refresh( events )
		raceDB.ShowModal()
		#app.MainLoop()

