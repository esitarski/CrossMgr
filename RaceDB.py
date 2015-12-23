import requests
import datetime
import wx
import wx.gizmos as gizmos
import Utils
import Clock

UrlRaceDB = 'http://127.0.0.1:8000/RaceDB'

def GetRaceDBEvents( date=None ):
	url = UrlRaceDB + '/GetEvents'
	if date:
		url += date.strftime('/%Y-%m-%d')
	req = requests.get( url + '/' )
	print req.content
	events = req.json()
	return events
	
def GetEventCrossMgr( eventId, eventType ):
	url = UrlRaceDB + ['/EventMassStartCrossMgr','/EventTTCrossMgr'][eventType] + '/{}'.format(eventId)
	req = requests.get( url + '/' )
	return req.content

class RaceDB( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, size=(600,600) ):
		super(RaceDB, self).__init__(parent, id, style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME, size=size, title=_('Select RaceDB Event'))
		
		self.clock = Clock.Clock( self )
		self.clock.SetSize( wx.Size(96,96) )
		
		self.tree = gizmos.TreeListCtrl( self, style=wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_ROW_LINES )
		
		isz = (16,16)
		self.il = wx.ImageList( *isz )
		self.closedIdx		= self.il.Add( wx.ArtProvider_GetBitmap(wx.ART_FOLDER,	 	wx.ART_OTHER, isz))
		self.expandedIdx	= self.il.Add( wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, 	wx.ART_OTHER, isz))
		self.fileIdx		= self.il.Add( wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE,	wx.ART_OTHER, isz))
		self.selectedIdx	= self.il.Add( wx.ArtProvider_GetBitmap(wx.ART_LIST_VIEW, 	wx.ART_OTHER, isz))
		
		self.tree.SetImageList( self.il )
		
		self.tree.AddColumn( _('Event Info') )
		self.tree.AddColumn( _('Start Time'), flag=wx.ALIGN_RIGHT )
		self.startTimeCol = 1
		self.tree.AddColumn( _('Participants'), flag=wx.ALIGN_RIGHT)
		self.participantCountCol = 2
		
		self.tree.SetMainColumn( 0 )
		self.tree.SetColumnWidth( 0, 320 )
		
		self.tree.Bind( wx.EVT_TREE_SEL_CHANGED, self.selectChangedCB )
		self.pkSelect = None
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.okButton = wx.Button( self, label=_("Initialize Timing for this Event") )
		self.okButton.Bind( wx.EVT_BUTTON, self.doOK )
		self.cancelButton = wx.Button( self, id=wx.ID_CANCEL )
		hs.Add( self.okButton )
		hs.AddStretchSpacer()
		hs.Add( self.cancelButton, flag=wx.LEFT, border=4 )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		vs.Add( self.clock, flag=wx.ALIGN_CENTER|wx.ALL, border=8 )
		vs.Add( self.tree, 1, flag=wx.EXPAND )
		vs.Add( hs, 0, flag=wx.EXPAND|wx.ALL, border=8 )
		self.SetSizer( vs )

	def doOK( self, event ):
		pass
		
	def selectChangedCB( self, evt ):
		try:
			self.pkSelect = self.tree.GetItemPyData(evt.GetItem())['pk']
		except Exception as e:
			self.pkSelect = None
		
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
		self.pkSelect = None
		
		for cName, events, participant_count, num in sorted(
				((c['name'], c['events'], c['participant_count'], c['num']) for c in competitions.itervalues()), key=lambda x: x[-1] ):
			competition = self.tree.AppendItem( self.root, cName )
			self.tree.SetItemText( competition, unicode(participant_count), self.participantCountCol )
			for e in events:
				event = self.tree.AppendItem( competition, u'{}: {}'.format(_('Event'), e['name']), data=wx.TreeItemData({'pk':e['pk']}) )
				self.tree.SetItemText( event, get_tod(e['date_time']), self.startTimeCol )
				self.tree.SetItemText( event, unicode(e['participant_count']), self.participantCountCol )
				
				tEvent = datetime.datetime.combine( tNow.date(), get_time(e['date_time']) )
				if eventClosest is None and tEvent > tNow:
					eventClosest = event
					self.pkSelect = e['pk']
				
				for w in e['waves']:
					wave = self.tree.AppendItem( event, u'{}: {}'.format(_('Wave'), w['name']), data=wx.TreeItemData({'pk':e['pk']}) )
					self.tree.SetItemText( wave, unicode(w['participant_count']), self.participantCountCol )
					start_offset = w.get('start_offset',None)
					if start_offset:
						self.tree.SetItemText( wave, '+' + start_offset, self.startTimeCol )
					for cat in w['categories']:
						category = self.tree.AppendItem( wave, cat['name'], data=wx.TreeItemData({'pk':e['pk']}) )
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

