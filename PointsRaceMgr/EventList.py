import wx
import wx.grid		as gridlib
import re
import copy
import operator
from ReorderableGrid import ReorderableGrid
import Model
import Utils

def getIDFromBibText( bibText ):
	bibText = bibText.strip().upper()
	idEvent = Model.RaceEvent.Events[0][1]
	for name, idEventCur in Model.RaceEvent.Events:
		code = name[0] if name[0] in '+-' else name.upper()
		if bibText.endswith(code):
			return idEventCur
	return idEvent

class EventListGrid( ReorderableGrid ):
	def OnRearrangeEnd(self, evt):
		if self._didCopy and Utils.getMainWin():
			wx.CallAfter( Utils.getMainWin().eventList.commitReorder )
		return super().OnRearrangeEnd(evt)

class EventDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, title="Edit Race Event" ):
		super().__init__( parent, id, title=title, style=wx.RESIZE_BORDER )
		
		bigFont = wx.Font( (0,20), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )

		self.hbs = wx.BoxSizer(wx.VERTICAL)

		hs = wx.BoxSizer(wx.HORIZONTAL)
		bibTextLabel = wx.StaticText(self, label="Bibs:")
		bibTextLabel.SetFont( bigFont )
		
		self.bibText = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER )
		self.bibText.SetFont( bigFont )
		self.bibText.Bind( wx.EVT_TEXT_ENTER, self.onEnter )
		
		hs.Add( bibTextLabel, flag=wx.ALIGN_CENTER_VERTICAL )
		hs.Add( self.bibText, 1, flag=wx.EXPAND|wx.LEFT, border=2 )

		self.hbs.Add( hs, flag=wx.EXPAND|wx.ALL, border=4 )
		ws = wx.GridSizer(2, 4, 2, 2)
		self.choiceButtons = []
		self.idToButton = {}
		for name, idEvent in Model.RaceEvent.Events:
			if 'Sp' in name:
				name = 'Sprint'
			elif 'Finish' in name:
				continue
			self.choiceButtons.append( wx.Button(self, label=name) )
			self.choiceButtons[-1].Bind( wx.EVT_BUTTON, lambda event, idEvent=idEvent: self.onVerb(event, idEvent) )
			self.idToButton[idEvent] = self.choiceButtons[-1]
			ws.Add( self.choiceButtons[-1], flag=wx.LEFT, border=2 )
		self.hbs.Add( ws, flag=wx.ALL, border=4 )
				
		ws = wx.GridSizer(1, 4, 2, 2)
		for name, idEvent in Model.RaceEvent.States:
			self.choiceButtons.append( wx.Button(self, label=name) )
			self.choiceButtons[-1].Bind( wx.EVT_BUTTON, lambda event, idEvent=idEvent: self.onVerb(event, idEvent) )
			self.idToButton[idEvent] = self.choiceButtons[-1]
			ws.Add( self.choiceButtons[-1], flag=wx.LEFT, border=2 )
		
		self.hbs.Add( ws, flag=wx.ALL|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4 )
		
		dbs = wx.StdDialogButtonSizer()
		self.ok = wx.Button( self, wx.ID_OK )
		self.ok.SetDefault()
		self.cancel = wx.Button( self, wx.ID_CANCEL )
		dbs.Add( self.ok, flag=wx.ALL, border=16 )
		dbs.Add( self.cancel, flag=wx.ALL, border=16 )
		
		self.hbs.Add( dbs, flag=wx.EXPAND )
		self.SetSizerAndFit( self.hbs )
	
	def refresh( self, event=None ):
		self.e = event or self.e
		for id, btn in self.idToButton.items():
			if id == self.e.eventType:
				btn.SetBackgroundColour( wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT) )
			else:
				btn.SetBackgroundColour( wx.NullColour )
		self.bibText.SetValue( value=event.bibStr() )
		self.bibText.SetFocus()
		
	def onEnter( self, event ):
		self.onVerb( event, getIDFromBibText(self.bibText.GetValue()) )
	
	def onVerb( self, event, idEvent ):
		for id, btn in self.idToButton.items():
			if id == idEvent:
				btn.SetBackgroundColour( wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT) )
			else:
				btn.SetBackgroundColour( wx.NullColour )
		self.EndModal( wx.ID_OK )
		
	def commit( self ):
		changed = False

		highlightColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT).GetAsString(wx.C2S_CSS_SYNTAX)
		for id, btn in self.idToButton.items():
			if btn.GetBackgroundColour().GetAsString(wx.C2S_CSS_SYNTAX) == highlightColour:
				if id != self.e.eventType:
					self.e.eventType = id
					changed = True
				break
		
		if self.e.bibStr() != self.bibText.GetValue():
			self.e.setBibs( self.bibText.GetValue() )
			changed = True
		
		return changed

class EventPopupMenu( wx.Menu ):
	def __init__(self, row=None ):
		super().__init__()

		self.row = row		
		mmi = wx.MenuItem(self, wx.ID_DELETE)
		self.Append( mmi )
		self.Bind(wx.EVT_MENU, self.OnDelete, mmi)

	def OnDelete(self, event):
		events = Model.race.events[:]
		del events[self.row]
		Model.race.setEvents( events )
		if Utils.getMainWin():
			Utils.getMainWin().refresh()

class EventList( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY ):
		super().__init__(parent, id, style=wx.BORDER_SUNKEN)
		
		self.eventDialog = EventDialog( self )
		
		self.SetDoubleBuffered(True)
		self.SetBackgroundColour( wx.WHITE )
		
		bigFont = wx.Font( (0,20), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )

		self.hbs = wx.BoxSizer(wx.VERTICAL)

		hs = wx.BoxSizer(wx.HORIZONTAL)
		bibTextLabel = wx.StaticText(self, label="Bibs:")
		bibTextLabel.SetFont( bigFont )
		
		self.bibText = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER )
		self.bibText.SetFont( bigFont )
		self.bibText.Bind( wx.EVT_TEXT_ENTER, self.onEnter )
		
		hs.Add( bibTextLabel, flag=wx.ALIGN_CENTER_VERTICAL )
		hs.Add( self.bibText, 1, flag=wx.EXPAND|wx.LEFT, border=2 )

		self.hbs.Add( hs, flag=wx.EXPAND|wx.ALL, border=4 )
		ws = wx.GridSizer(2, 4, 2, 2)
		self.choiceButtons = []
		for name, idEvent in Model.RaceEvent.Events:
			if 'Sp' in name:
				name = 'Sprint'
			elif 'Finish' in name:
				continue
			self.choiceButtons.append( wx.Button(self, label=name) )
			self.choiceButtons[-1].Bind( wx.EVT_BUTTON, lambda event, idEvent=idEvent: self.onVerb(event, idEvent) )
			ws.Add( self.choiceButtons[-1] )
		self.hbs.Add( ws, flag=wx.ALL, border=4 )

		ws = wx.GridSizer(1, 4, 2, 2)
		for name, idEvent in Model.RaceEvent.States:
			self.choiceButtons.append( wx.Button(self, label=name) )
			self.choiceButtons[-1].Bind( wx.EVT_BUTTON, lambda event, idEvent=idEvent: self.onVerb(event, idEvent) )
			ws.Add( self.choiceButtons[-1], flag=wx.LEFT, border=2 )
		self.hbs.Add( ws, flag=wx.ALL, border=4 )

		self.grid = EventListGrid( self )
		self.grid.Bind( gridlib.EVT_GRID_CELL_LEFT_CLICK, self.onLeftClick )
		self.grid.Bind( gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.onRightClick )

		self.grid.CreateGrid( 0, 5 )
		self.grid.SetSelectionMode( gridlib.Grid.SelectRows )
		self.grid.SetSelectionBackground( wx.Colour(255,255,0) )
		self.grid.SetSelectionForeground( wx.Colour(80,80,80) )		
	
		self.hbs.Add( self.grid, 1, wx.EXPAND )
		self.SetSizer(self.hbs)

	def addNewEvent( self, e ):
		race = Model.race
		race.setEvents( race.events + [e] )
		(Utils.getMainWin() if Utils.getMainWin() else self).refresh()
		self.grid.MakeCellVisible( len(race.events)-1, 0 )
		self.grid.ClearSelection()
		self.grid.SelectRow( len(race.events)-1 )		
	
	def onEnter( self, event ):
		self.onVerb( event, getIDFromBibText(self.bibText.GetValue()) )
	
	def onVerb( self, event, idEvent ):
		bibText = self.bibText.GetValue().strip()
		if bibText:
			self.addNewEvent( Model.RaceEvent(idEvent, bibText) )
		self.bibText.SetValue( '' )
		wx.CallAfter( self.bibText.SetFocus )
		
	def onLeftClick( self, event ):
		race = Model.race
		self.grid.ClearSelection()
		
		rowCur = event.GetRow()
		self.grid.SelectRow( rowCur )
		eventCur = copy.deepcopy( race.events[rowCur] )
		wasState = eventCur.isState()
		
		self.eventDialog.refresh( eventCur )
		self.eventDialog.CentreOnScreen()
		
		if self.eventDialog.ShowModal() == wx.ID_OK:
			changed = self.eventDialog.commit()
			isState = self.eventDialog.e.isState()
			if wasState or isState:
				# Move the state to the end to show most recent state.
				# del race.events[rowCur]
				race.events.append( self.eventDialog.e )
				rowCur = len(race.events) - 1
			else:
				if not changed:
					return
				race.events[rowCur] = self.eventDialog.e
				
			race.setEvents( race.events )
			(Utils.getMainWin() or self).refresh()
			self.grid.MakeCellVisible( rowCur, 0 )
			self.grid.SelectRow( rowCur )
			
	def editRow( self, row ):
		class EditEventDuck:
			def GetRow( self ):
				return row
		self.onLeftClick( EditEventDuck() )
	
	def onRightClick( self, event ):
		self.PopupMenu(EventPopupMenu(event.GetRow()), event.GetPosition())
	
	def refresh( self ):
		race = Model.race
		events = race.events if race else []
			
		headers = ('Event', 'Bibs',)
		
		self.grid.BeginBatch()
		Utils.AdjustGridSize( self.grid, len(events), len(headers) )
		
		for c, name in enumerate(headers):
			self.grid.SetColLabelValue( c, name )
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly()
			attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
			attr.SetFont( Utils.BigFont() )
			self.grid.SetColAttr( c, attr )
		
		Sprint = Model.RaceEvent.Sprint
		Finish = Model.RaceEvent.Finish
		sprintCount = 0
		for row, e in enumerate(events):
			if e.eventType == Sprint:
				sprintCount += 1
				name = race.getSprintLabel(sprintCount)
			else:
				name = e.eventTypeName
				if e.eventType == Finish:
					sprintCount += 1
					name += ' ({})'.format( race.getSprintLabel(sprintCount) )
					
			self.grid.SetCellValue( row, 0, name )
			self.grid.SetCellValue( row, 1, e.bibStr() )
		
		self.grid.AutoSize()
		self.grid.EndBatch()
		
		self.Layout()

	def commit( self ):
		pass

	def commitReorder( self ):
		race = Model.race
		events = []
		for r in range(self.grid.GetNumberRows()):
			events.append( Model.RaceEvent(self.grid.GetCellValue(r, 0), self.grid.GetCellValue(r, 1)) )
		race.setEvents( events )
		Utils.refresh()
	
if __name__ == '__main__':
	app = wx.App( False )
	Utils.disable_stdout_buffering()
	mainWin = wx.Frame(None, title="EventList", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	rd = EventList(mainWin)
	rd.refresh()
	mainWin.Show()
	app.MainLoop()
