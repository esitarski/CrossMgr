import wx
import wx.grid		as gridlib
Button = wx.Button
from Colours import *
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

ID_COPY_EVENT = wx.ID_YES
ID_DELETE_EVENT = wx.ID_NO

class EventDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, title="Edit Race Event" ):
		super().__init__( parent, id, title=title, style=wx.RESIZE_BORDER )
		
		bigFont = wx.Font( (0,20), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )

		hbs = wx.BoxSizer(wx.VERTICAL)
		
		self.titleText = 'Event:'
		self.title = wx.StaticText(self, label=self.titleText )
		self.title.SetFont( bigFont )

		hs = wx.BoxSizer(wx.HORIZONTAL)
		bibTextLabel = wx.StaticText(self, label="Bibs:")
		bibTextLabel.SetFont( bigFont )
		
		self.bibText = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER )
		self.bibText.SetFont( bigFont )
		self.bibText.Bind( wx.EVT_TEXT_ENTER, self.onEnter )
		
		hs.Add( bibTextLabel, flag=wx.ALIGN_CENTER_VERTICAL )
		hs.Add( self.bibText, 1, flag=wx.EXPAND|wx.LEFT, border=2 )

		hbs.Add( self.title, flag=wx.EXPAND|wx.ALL, border=4 )
		hbs.Add( hs, flag=wx.EXPAND|wx.ALL, border=4 )
		ws = wx.GridSizer(2, 4, 2, 2)
		self.choiceButtons = []
		self.idToButton = {}
		for name, idEvent in Model.RaceEvent.Events:
			if 'Sp' in name:
				name = 'Sprint'
			elif 'Finish' in name:
				continue
			self.choiceButtons.append( Button(self, label=name) )
			self.choiceButtons[-1].SetForegroundColour( eventColour )
			self.choiceButtons[-1].Bind( wx.EVT_BUTTON, lambda event, idEvent=idEvent: self.onVerb(event, idEvent) )
			self.idToButton[idEvent] = self.choiceButtons[-1]
			ws.Add( self.choiceButtons[-1], flag=wx.LEFT, border=2 )
		hbs.Add( ws, flag=wx.ALL, border=4 )
				
		ws = wx.GridSizer(1, 4, 2, 2)
		for name, idEvent in Model.RaceEvent.States:
			self.choiceButtons.append( Button(self, label=name) )
			self.choiceButtons[-1].SetForegroundColour( stateColour )
			self.choiceButtons[-1].Bind( wx.EVT_BUTTON, lambda event, idEvent=idEvent: self.onVerb(event, idEvent) )
			self.idToButton[idEvent] = self.choiceButtons[-1]
			ws.Add( self.choiceButtons[-1], flag=wx.LEFT, border=2 )
		
		hbs.Add( ws, flag=wx.ALL|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4 )
		
		editSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.copyBtn = wx.Button( self, label='Copy' )
		self.copyBtn.Bind( wx.EVT_BUTTON, self.onCopy )
		
		self.deleteBtn = wx.Button( self, label='Delete' )
		self.deleteBtn.Bind( wx.EVT_BUTTON, self.onDelete )
		
		editSizer.Add( self.copyBtn, flag=wx.ALL, border=4 )
		editSizer.Add( self.deleteBtn, flag=wx.ALL, border=4 )
		hbs.Add( wx.StaticLine(self), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=2 )
		hbs.Add( editSizer, flag=wx.EXPAND|wx.ALL, border=4 )
		
		btnSizer = self.CreateButtonSizer( wx.OK|wx.CANCEL )
		if btnSizer:
			hbs.Add( wx.StaticLine(self), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=2 )
			hbs.Add( btnSizer, flag=wx.EXPAND|wx.ALL, border=4 )
		self.SetSizerAndFit( hbs )
	
	def refresh( self, event=None, rowCur=None ):
		self.e = event or self.e
		eventTypeName = None
		for id, btn in self.idToButton.items():
			if id == self.e.eventType:
				btn.SetBackgroundColour( wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT) )
				eventTypeName = btn.GetLabel()
			else:
				btn.SetBackgroundColour( wx.NullColour )
		self.titleText = ''
		if eventTypeName is not None:
			self.titleText = 'Event {}: {}'.format( rowCur+1, eventTypeName )
		self.title.SetLabel( self.titleText )
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
		
	def onCopy( self, event ):
		self.EndModal( ID_COPY_EVENT )
		
	def onDelete( self, event ):
		with wx.MessageDialog( self, '{}\n\nConfirm Delete?'.format(self.titleText), 'Confirm Delete', style=wx.OK|wx.CANCEL ) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.EndModal( ID_DELETE_EVENT )
		
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

		hbs = wx.BoxSizer(wx.VERTICAL)

		hs = wx.BoxSizer(wx.HORIZONTAL)
		bibTextLabel = wx.StaticText(self, label="Bibs:")
		bibTextLabel.SetFont( bigFont )
		
		self.bibText = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER )
		self.bibText.SetFont( bigFont )
		self.bibText.Bind( wx.EVT_TEXT_ENTER, self.onEnter )
		
		hs.Add( bibTextLabel, flag=wx.ALIGN_CENTER_VERTICAL )
		hs.Add( self.bibText, 1, flag=wx.EXPAND|wx.LEFT, border=2 )

		hbs.Add( hs, flag=wx.EXPAND|wx.ALL, border=4 )
		ws = wx.GridSizer(2, 4, 2, 2)
		self.choiceButtons = []
		for name, idEvent in Model.RaceEvent.Events:
			if 'Sp' in name:
				name = 'Sprint'
			elif 'Finish' in name:
				continue
			self.choiceButtons.append( wx.Button(self, label=name) )
			self.choiceButtons[-1].SetForegroundColour( eventColour )
			self.choiceButtons[-1].Bind( wx.EVT_BUTTON, lambda event, idEvent=idEvent: self.onVerb(event, idEvent) )
			ws.Add( self.choiceButtons[-1] )
		hbs.Add( ws, flag=wx.ALL, border=4 )

		ws = wx.GridSizer(1, 4, 2, 2)
		for name, idEvent in Model.RaceEvent.States:
			self.choiceButtons.append( wx.Button(self, label=name) )
			self.choiceButtons[-1].SetForegroundColour( stateColour )
			self.choiceButtons[-1].Bind( wx.EVT_BUTTON, lambda event, idEvent=idEvent: self.onVerb(event, idEvent) )
			ws.Add( self.choiceButtons[-1], flag=wx.LEFT, border=2 )
		hbs.Add( ws, flag=wx.ALL, border=4 )

		self.grid = EventListGrid( self )
		self.grid.Bind( gridlib.EVT_GRID_CELL_LEFT_CLICK, self.onLeftClick )
		#self.grid.Bind( gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.onRightClick )

		self.grid.CreateGrid( 0, 5 )
		self.grid.SetSelectionMode( gridlib.Grid.SelectRows )
		self.grid.SetSelectionBackground( wx.Colour(255,255,0) )
		self.grid.SetSelectionForeground( wx.Colour(80,80,80) )		
	
		hbs.Add( self.grid, 1, wx.EXPAND )
		self.SetSizer( hbs )

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
		
		while True:
			self.eventDialog.refresh( eventCur, rowCur)
			self.eventDialog.CentreOnScreen()
			
			result = self.eventDialog.ShowModal()
			
			if result == wx.ID_CANCEL:
				return
			
			if result == wx.ID_OK:
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
				return
				
			if result == ID_DELETE_EVENT:
				events = race.events[:]
				events.pop( rowCur )
				race.setEvents( events )
				rowCur = min( len(race.events)-1, rowCur )
				if race.events:
					self.grid.MakeCellVisible( rowCur, 0 )				
					self.grid.SelectRow( rowCur )
				(Utils.getMainWin() or self).refresh()
				return

			if result == ID_COPY_EVENT:
				changed = self.eventDialog.commit()
				if changed:
					race.events[rowCur] = self.eventDialog.e
				race.events.append( copy.deepcopy(race.events[rowCur]) )
				race.setEvents( race.events )
				
				rowCur = len(race.events) - 1
				(Utils.getMainWin() or self).refresh()
				self.grid.MakeCellVisible( rowCur, 0 )
				
				self.grid.SelectRow( rowCur )
				eventCur = copy.deepcopy( race.events[rowCur] )
				wasState = eventCur.isState()
			
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
