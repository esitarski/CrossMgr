import requests
import datetime
import os
import wx
import wx.gizmos as gizmos
import Utils
import Clock

RaceDBUrlDefault = 'http://127.0.0.1:8000/RaceDB'

def GetRaceDBEvents( date=None ):
	url = RaceDBUrlDefault + '/GetEvents'
	if date:
		url += date.strftime('/%Y-%m-%d')
	req = requests.get( url + '/' )
	events = req.json()
	return events
	
def GetEventCrossMgr( eventId, eventType ):
	url = RaceDBUrlDefault + ['/EventMassStartCrossMgr','/EventTTCrossMgr'][eventType] + '/{}'.format(eventId)
	req = requests.get( url + '/' )
	content_disposition = req.headers['content-disposition'].encode('latin-1').decode('utf-8')
	filename = content_disposition.split('=')[1].replace("'",'').replace('"','')
	return filename, req.content

class RaceDB( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, size=(600,900) ):
		super(RaceDB, self).__init__(parent, id, style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME, size=size, title=_('Select RaceDB Event'))
		
		raceDBLogo = wx.StaticBitmap( self, bitmap=wx.Bitmap( os.path.join(Utils.getImageFolder(), 'RaceDB_big.png'), wx.BITMAP_TYPE_PNG ) )
		
		self.clock = Clock.Clock( self, size=(190,190) )
		
		self.raceDBUrl = wx.TextCtrl( self )
		self.raceFolder = wx.DirPickerCtrl( self )
		
		fgs = wx.FlexGridSizer( cols=2, rows=0, vgap=4, hgap=4 )
		fgs.AddGrowableCol( 1, 1 )
		
		fgs.Add( wx.StaticText(self, label=_('RaceDB URL')), flag=wx.ALIGN_RIGHT )
		fgs.Add( self.raceDBUrl, 1, flag=wx.EXPAND )
		fgs.Add( wx.StaticText(self, label=_('Race Folder')), flag=wx.ALIGN_RIGHT )
		fgs.Add( self.raceFolder, 1, flag=wx.EXPAND )
		
		hsHeader = wx.BoxSizer( wx.HORIZONTAL )
		hsHeader.Add( raceDBLogo )
		hsHeader.AddStretchSpacer()
		hsHeader.Add( self.clock )
		
		vsHeader = wx.BoxSizer( wx.VERTICAL )
		vsHeader.Add( hsHeader, flag=wx.EXPAND )
		vsHeader.Add( fgs, 1, flag=wx.EXPAND )
		
		self.tree = gizmos.TreeListCtrl( self, style=wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_ROW_LINES )
		
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
		self.okButton = wx.Button( self, label=_("Initialize Timing for Event") )
		self.okButton.Bind( wx.EVT_BUTTON, self.doOK )
		self.cancelButton = wx.Button( self, id=wx.ID_CANCEL )
		hs.Add( self.okButton )
		hs.AddStretchSpacer()
		hs.Add( self.cancelButton, flag=wx.LEFT, border=4 )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		vs.Add( vsHeader, flag=wx.ALL|wx.EXPAND, border=8 )
		vs.Add( self.tree, 1, flag=wx.EXPAND )
		vs.Add( hs, 0, flag=wx.EXPAND|wx.ALL, border=8 )
		self.SetSizer( vs )

	def doOK( self, event ):
		url = self.raceDBUrl.GetValue().strip()
		if not url:
			url = RaceDBUrlDefault
		dir = self.raceFolder.GetPath().strip()
		if not dir:
			dir = os.path.expanduser('~')
		try:
			filename, content = GetEventCrossMgr( self.dataSelect['pk'], self.dataSelect['event_type'] )
		except Exception as e:
			raise e
		print filename
		self.EndModal( wx.ID_OK )
		
	def selectChangedCB( self, evt ):
		try:
			self.dataSelect = self.tree.GetItemPyData(evt.GetItem())
		except Exception as e:
			self.dataSelect = None
		
	def refresh( self, events ):
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
		self.tree.SetItemText( self.root, unicode(sum(c['participant_count'] for c in competitions.itervalues())), self.participantCountCol )
		
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
				eventData = {'pk':e['pk'], 'event_type':e['event_type']}
				event = self.tree.AppendItem( competition, u'{}: {}'.format(_('Event'), e['name']), data=wx.TreeItemData(eventData) )
				self.tree.SetItemText( event, get_tod(e['date_time']), self.startTimeCol )
				self.tree.SetItemText( event, _('Mass Start') if e['event_type'] == 0 else _('Time Trial'), self.eventTypeCol )
				self.tree.SetItemText( event, unicode(e['participant_count']), self.participantCountCol )
				
				tEvent = datetime.datetime.combine( tNow.date(), get_time(e['date_time']) )
				if eventClosest is None and tEvent > tNow:
					eventClosest = event
					self.dataSelect = e['pk']
				
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

if __name__ == '__main__':
	events = GetRaceDBEvents()
	print GetRaceDBEvents( datetime.date.today() )
	print GetRaceDBEvents( datetime.date.today() - datetime.timedelta(days=2) )
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1000,400))
	raceDB = RaceDB(mainWin)
	raceDB.refresh( events )
	raceDB.ShowModal()
	#app.MainLoop()

