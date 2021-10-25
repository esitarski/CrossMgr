import wx
from CalendarHeatmap import CalendarHeatmap
class DateSelectDialog( wx.Dialog ):
	def __init__( self, parent, triggerDates, id=wx.ID_ANY, ):
		super().__init__( parent, id, title=_("Date Select") )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		self.dateSelect = None
		
		self.triggerDates = triggerDates	# list of (date, trigger_count, race_name)
		
		self.chm = CalendarHeatmap( self, dates=self.triggerDates )
		self.chm.Bind( wx.EVT_BUTTON, self.onCHMSelect )
		self.chm.Bind( wx.EVT_COMMAND_LEFT_DCLICK, self.onCHMChoose )
		
		self.triggerDatesList = wx.ListCtrl( self, style=wx.LC_REPORT|wx.LC_SINGLE_SEL, size=(-1,230) )
		
		self.triggerDatesList.InsertColumn( 0, 'Date' )
		self.triggerDatesList.InsertColumn( 1, '# Triggers', format=wx.LIST_FORMAT_CENTRE, width=wx.LIST_AUTOSIZE_USEHEADER )
		self.triggerDatesList.InsertColumn( 2, 'Race', width=wx.LIST_AUTOSIZE_USEHEADER )
		for i, (d, c, r) in enumerate(triggerDates):
			self.triggerDatesList.InsertItem( i, d.strftime('%Y-%m-%d') )
			self.triggerDatesList.SetItem( i, 1, str(c) )
			self.triggerDatesList.SetItem( i, 2, r )
		
		for c in range(3):
			self.triggerDatesList.SetColumnWidth( c, -2 )
		
		if self.triggerDates:
			self.triggerDatesList.Select( 0 )
			self.chm.SetDate( self.triggerDates[0][0] )
		
		self.triggerDatesList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.onItemSelect )
		self.triggerDatesList.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivate )
		
		btnSizer = self.CreateSeparatedButtonSizer( wx.OK|wx.CANCEL )
		
		sizer.Add( self.chm, flag=wx.ALL, border=4 )
		sizer.Add( self.triggerDatesList, flag=wx.ALL|wx.EXPAND, border=4 )
		if btnSizer:
			sizer.Add( btnSizer, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.SetSizer( sizer )
		wx.CallAfter( self.Fit )

	def onCHMSelect( self, event ):
		dSelect = event.GetDate()
		for i, (d, c, r) in enumerate(self.triggerDates):
			if d == dSelect:
				self.triggerDatesList.Select( i )
				break
		
	def onCHMChoose( self, event ):
		self.onCHMSelect( event )
		self.dateSelect = event.GetDate()
		self.EndModal( wx.ID_OK )	
		
	def onItemSelect( self, event ):
		self.dateSelect = self.triggerDates[event.GetIndex()][0]
		self.chm.SetDate( self.dateSelect )
		
	def onItemActivate( self, event ):
		self.onItemSelect( event )
		self.EndModal( wx.ID_OK )	
		
	def GetDate( self ):
		return self.dateSelect

