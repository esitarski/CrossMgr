import wx
import os
import re
from string import Template
import operator
import Model
import Utils
import ColGrid
from FixCategories import FixCategories, SetCategory
from GetResults import TimeDifference, GetEntries, GetResults
import EditEntry
from RiderDetail import ShowRiderDetailDialog
from Undo import undo

reNonDigits = re.compile( '[^0-9]' )
reIntPrefix = re.compile( '^[0-9]+' )

class History( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)

		self.showTimes = False
		self.showPosition = False
		self.showLapTimes = False
		self.showTimeDown = False
		self.showRiderName = False
		self.numSelect = None
		self.isEmpty = True
		self.history = None
		self.rcInterp = set()
		self.rcNumTime = set()
		self.textColour = {}
		self.backgroundColour = {}
		self.category = None
		
		self.whiteColour = wx.Colour( 255, 255, 255 )
		self.blackColour = wx.Colour( 0, 0, 0 )
		self.yellowColour = wx.Colour( 255, 255, 0 )
		self.orangeColour = wx.Colour( 255, 140, 0 )
		self.greyColour = wx.Colour( 150, 150, 150 )
		
		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, label=_('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.sync = wx.ToggleButton( self, label=_('Sync Category'), style=wx.RB_GROUP )
		self.sync.SetValue( True )
		self.sync.Bind( wx.EVT_TOGGLEBUTTON, lambda event: self.refresh() )
		
		self.showPositionToggle = wx.ToggleButton( self, label=_('Position'), style=wx.BU_EXACTFIT )
		self.showPositionToggle.SetValue( self.showPosition )
		self.Bind( wx.EVT_TOGGLEBUTTON, self.onShowPosition, self.showPositionToggle )
		
		self.showTimesToggle = wx.ToggleButton( self, label=_('Race Times'), style=wx.BU_EXACTFIT )
		self.showTimesToggle.SetValue( self.showTimes )
		self.Bind( wx.EVT_TOGGLEBUTTON, self.onShowTimes, self.showTimesToggle )
		
		self.showLapTimesToggle = wx.ToggleButton( self, label=_('Lap Times'), style=wx.BU_EXACTFIT )
		self.showLapTimesToggle.SetValue( self.showLapTimes )
		self.Bind( wx.EVT_TOGGLEBUTTON, self.onShowLapTimes, self.showLapTimesToggle )
		
		self.showTimeDownToggle = wx.ToggleButton( self, label=_('Time Down per Lap'), style=wx.BU_EXACTFIT )
		self.showTimeDownToggle.SetValue( self.showTimeDown )
		self.Bind( wx.EVT_TOGGLEBUTTON, self.onShowTimeDown, self.showTimeDownToggle )
		
		self.showRiderNameToggle = wx.ToggleButton( self, label=_('Names'), style=wx.BU_EXACTFIT )
		self.showRiderNameToggle.SetValue( self.showRiderName )
		self.Bind( wx.EVT_TOGGLEBUTTON, self.onShowRiderName, self.showRiderNameToggle )
		
		self.search = wx.SearchCtrl(self, size=(80,-1), style=wx.TE_PROCESS_ENTER )
		# self.search.ShowCancelButton( True )
		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
		self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancelSearch, self.search)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch, self.search)
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'Zoom-In-icon.png'), wx.BITMAP_TYPE_PNG )
		self.zoomInButton = wx.BitmapButton( self, wx.ID_ZOOM_IN, bitmap, style=wx.BU_EXACTFIT | wx.BU_AUTODRAW )
		self.Bind( wx.EVT_BUTTON, self.onZoomIn, self.zoomInButton )
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'Zoom-Out-icon.png'), wx.BITMAP_TYPE_PNG )
		self.zoomOutButton = wx.BitmapButton( self, wx.ID_ZOOM_OUT, bitmap, style=wx.BU_EXACTFIT | wx.BU_AUTODRAW )
		self.Bind( wx.EVT_BUTTON, self.onZoomOut, self.zoomOutButton )
		
		self.hbs.Add( self.categoryLabel, flag=wx.ALIGN_CENTRE_VERTICAL )
		self.hbs.Add( self.categoryChoice, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=2 )
		self.hbs.Add( self.sync, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=2 )
		self.hbs.Add( self.showPositionToggle, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=18 )
		self.hbs.Add( self.showTimesToggle, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showLapTimesToggle, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showTimeDownToggle, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showRiderNameToggle, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( wx.StaticText(self, label = u' '), proportion=2 )
		self.hbs.Add( self.search, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomInButton, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomOutButton, flag=wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border=4 )

		self.grid = ColGrid.ColGrid( self )
		self.grid.SetRightAlign( True )
		self.grid.SetRowLabelSize( 32 )
		self.grid.SetMargins( 0, 0 )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()

		# Set the col labels tall enough for lap, lapsToGo, lapTime, raceTime.
		width, height = wx.ClientDC(self).GetMultiLineTextExtent( "0\n0\n0\n0" )
		self.grid.SetColLabelSize( height )
		
		self.Bind( wx.grid.EVT_GRID_SELECT_CELL, self.doNumSelect )
		self.Bind( wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.doNumDrilldown )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doRightClick )
		
		bs = wx.BoxSizer(wx.VERTICAL)
		bs.Add(self.hbs, flag=wx.GROW|wx.HORIZONTAL|wx.ALL, border=4)
		bs.Add(self.grid, 1, wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM, 4)
		self.SetSizer(bs)
		bs.SetSizeHints(self)
		self.SetDoubleBuffered( True )

	def OnSearch( self, event ):
		self.OnDoSearch()
		
	def OnCancelSearch( self, event ):
		self.search.SetValue( '' )
		
	def OnDoSearch( self, event = None ):
		wx.CallAfter( self.search.SetFocus )
		n = self.search.GetValue()
		if n:
			n = reNonDigits.sub( '', n )
			self.search.SetValue( n )
		if not n:
			n = None
		if n:
			self.numSelect = n
			if self.category and not self.category.matches( int(n) ):
				self.setCategoryAll()
			self.refresh()
			if Utils.isMainWin():
				Utils.getMainWin().setNumSelect( n )

	def onZoomOut( self, event ):
		self.grid.Zoom( False )
			
	def onZoomIn( self, event ):
		self.grid.Zoom( True )
		
	def doRightClick( self, event ):
		wx.CallAfter( self.search.SetFocus )
		
		if self.isEmpty:
			return
			
		self.rowPopup = event.GetRow()
		self.colPopup = event.GetCol()
		numSelect = self.getCellNum( self.rowPopup, self.colPopup )
		if not numSelect:
			return
			
		self.doNumSelect( event )
		
		allCases = 0
		interpCase = 1
		nonInterpCase = 2
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				(wx.NewId(), _('Results'), 		_('Switch to Results tab'), self.OnPopupResults, allCases),
				(wx.NewId(), _('RiderDetail'),	_('Show RiderDetail tab'), self.OnPopupRiderDetail, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Correct...'),	_('Change number or time'),	self.OnPopupCorrect, interpCase),
				(wx.NewId(), _('Shift...'),		_('Move time earlier/later'),	self.OnPopupShift, interpCase),
				(wx.NewId(), _('Insert...'),	_('Insert a number before/after existing entry'),	self.OnPopupInsert, nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), _('Delete...'),	_('Delete an entry'),	self.OnPopupDelete, nonInterpCase),
				(wx.NewId(), _('Split...'),		_('Split an entry into two'),self.OnPopupSplit, nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), u'{}...'.format(_('Swap with Entry before')),	_('Swap with Entry before'), self.OnPopupSwapBefore, nonInterpCase),
				(wx.NewId(), u'{}...'.format(_('Swap with Entry after')),_('Swap with Entry after'),	self.OnPopupSwapAfter, nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), _('Pull After Lap') + u'...',	_('Pull After lap'),	self.OnPopupPull, nonInterpCase),
				(wx.NewId(), _('DNF After Lap') + u'...',	_('DNF After lap'),	self.OnPopupDNF, nonInterpCase),
			]
			for id, name, text, callback, cCode in self.popupInfo:
				if id:
					self.Bind( wx.EVT_MENU, callback, id=id )

		isInterp = self.history[self.colPopup][self.rowPopup].interp
		caseCode = 1 if isInterp else 2
		
		menu = wx.Menu()
		for i, (id, name, text, callback, cCode) in enumerate(self.popupInfo):
			if not id:
				Utils.addMissingSeparator( menu )
				continue
			if caseCode < cCode:
				continue
			menu.Append( id, name, text )
		
		Utils.deleteTrailingSeparators( menu )
		try:
			self.PopupMenu( menu )
			menu.Destroy()
		except Exception as e:
			Utils.writeLog( 'History:doRightClick: {}'.format(e) )
			
	def OnPopupSwapBefore( self, event ):
		if not hasattr(self, 'rowPopup'):
			return
		c, r, h = self.colPopup, self.rowPopup, self.history
		success = False
		undo.pushState()
		with Model.LockRace() as race:
			for rPrev in xrange( r - 1, -1, -1 ):
				if not h[c][rPrev].interp and (self.category is None or race.inCategory(h[c][rPrev].num, self.category)):
					EditEntry.SwapEntry( h[c][r], h[c][rPrev] )
					success = True
					break
		if success and Utils.isMainWin():
			Utils.getMainWin().refresh()
		
	def OnPopupSwapAfter( self, event ):
		if not hasattr(self, 'rowPopup'):
			return
		c, r, h = self.colPopup, self.rowPopup, self.history
		success = False
		undo.pushState()
		with Model.LockRace() as race:
			for rNext in xrange( r + 1, len(h[c]) ):
				if not h[c][rNext].interp and (self.category is None or race.inCategory(h[c][rNext].num, self.category)):
					EditEntry.SwapEntry( h[c][r], h[c][rNext] )
					success = True
					break
		if success and Utils.isMainWin():
			Utils.getMainWin().refresh()
			
	def OnPopupPull( self, event ):
		if not hasattr(self, 'rowPopup'):
			return
			
		entry = self.history[self.colPopup][self.rowPopup]

		if not entry:
			return
		if not Utils.MessageOKCancel( self,
			u'{}: {}  {} {} - {}?'.format(
				_('Bib'), entry.num,
				_('Pull after lap'), entry.lap, Utils.formatTime(entry.t+1, True), ),
			_('Pull Rider') ):
			return
		try:
			undo.pushState()
			race = Model.race
			race.getRider(entry.num).setStatus( Model.Rider.Pulled, entry.t + 1 )
			race.setChanged()
		except:
			pass
		wx.CallAfter( self.refresh )
		wx.CallAfter( Utils.refreshForecastHistory )
		
	def OnPopupDNF( self, event ):
		if not hasattr(self, 'rowPopup'):
			return
			
		entry = self.history[self.colPopup][self.rowPopup]

		if not Utils.MessageOKCancel( self,
			u'{}: {}  {} {} - {}?'.format(
				_('Bib'), entry.num,
				_('DNF after lap'), entry.lap, Utils.formatTime(entry.t+1, True), ),
			_('DNF Rider') ):
			return
		try:
			undo.pushState()
			race = Model.race
			race.getRider(entry.num).setStatus( Model.Rider.DNF, entry.t + 1 )
			race.setChanged()
		except:
			pass
		wx.CallAfter( self.refresh )
		wx.CallAfter( Utils.refreshForecastHistory )
		
	def OnPopupCorrect( self, event ):
		if hasattr(self, 'rowPopup'):
			EditEntry.CorrectNumber( self, self.history[self.colPopup][self.rowPopup] )
		
	def OnPopupShift( self, event ):
		if hasattr(self, 'rowPopup'):
			EditEntry.ShiftNumber( self, self.history[self.colPopup][self.rowPopup] )
		
	def OnPopupSplit( self, event ):
		if hasattr(self, 'rowPopup'):
			EditEntry.SplitNumber( self, self.history[self.colPopup][self.rowPopup] )
		
	def OnPopupInsert( self, event ):
		if hasattr(self, 'rowPopup'):
			EditEntry.InsertNumber( self, self.history[self.colPopup][self.rowPopup] )
		
	def OnPopupDelete( self, event ):
		if hasattr(self, 'rowPopup'):
			EditEntry.DeleteEntry( self, self.history[self.colPopup][self.rowPopup] )
		
	def OnPopupResults( self, event ):
		if Utils.isMainWin():
			Utils.getMainWin().showPageName( _('Results') )
			
	def OnPopupRiderDetail( self, event ):
		ShowRiderDetailDialog( self, self.numSelect )
	
	def onShowPosition( self, event ):
		self.showPosition ^= True
		self.refresh()	
	
	def onShowTimes( self, event ):
		self.showTimes ^= True
		self.refresh()
		
	def onShowLapTimes( self, event ):
		self.showLapTimes ^= True
		self.refresh()
		
	def onShowTimeDown( self, event ):
		self.showTimeDown ^= True
		self.refresh()
		
	def onShowRiderName( self, event ):
		self.showRiderName ^= True
		self.refresh()
		
	def updateColours( self ):
		self.textColour = {}
		self.backgroundColour = dict( ((rc, self.yellowColour) for rc in self.rcInterp) )
		self.backgroundColour.update( dict(((rc, self.orangeColour) for rc in self.rcNumTime )) )
		if not self.history:
			return
		try:
			nSelect = int(self.numSelect)
		except (TypeError, ValueError):
			return
		for c, h in enumerate(self.history):
			try:
				r = (r for r, e in enumerate(h) if e.num == nSelect).next()
				self.textColour[ (r,c) ] = self.whiteColour
				self.backgroundColour[ (r,c) ] = self.blackColour if (r,c) not in self.rcInterp and (r,c) not in self.rcNumTime else self.greyColour
			except StopIteration:
				pass
		
	def showNumSelect( self ):
		self.updateColours()
		self.grid.Set( textColour = self.textColour, backgroundColour = self.backgroundColour )
		self.grid.Reset()
	
	def doNumDrilldown( self, event ):
		self.doNumSelect( event )
		mainWin = Utils.getMainWin()
		if self.numSelect is not None and mainWin:
			ShowRiderDetailDialog( self, self.numSelect )
	
	def getCellNum( self, row, col ):
		numSelect = None
		if row < self.grid.GetNumberRows() and col < self.grid.GetNumberCols():
			value = self.grid.GetCellValue( row, col )
			if value:
				if ':' in value:
					value = value.split(':', 1)[1].strip()
				
				m = reIntPrefix.match( value )
				if m:
					numSelect = m.group(0)
		return numSelect
	
	def doNumSelect( self, event ):
		if self.isEmpty:
			return
		numSelect = self.getCellNum(event.GetRow(), event.GetCol())
		if numSelect is not None:
			if self.numSelect != numSelect:
				self.numSelect = numSelect
				self.showNumSelect()
			if Utils.isMainWin():
				Utils.getMainWin().setNumSelect( numSelect )
	
	def doChooseCategory( self, event ):
		Model.setCategoryChoice( self.categoryChoice.GetSelection(), 'historyCategory' )
		self.refresh()
	
	def setCategoryAll( self ):
		FixCategories( self.categoryChoice, 0 )
		Model.setCategoryChoice( 0, 'historyCategory' )
	
	def setCategory( self, category ):
		for i, c in enumerate(Model.race.getCategories( startWaveOnly=False ) if Model.race else [], 1):
			if c == category:
				SetCategory( self.categoryChoice, c )
				Model.setCategoryChoice( i, 'historyCategory' )
				return
		SetCategory( self.categoryChoice, None )
		Model.setCategoryChoice( 0, 'historyCategory' )
	
	def reset( self ):
		self.numSelect = None

	def setNumSelect( self, num ):
		self.numSelect = num if num is None else '{}'.format(num)
		if self.numSelect:
			self.search.SetValue( self.numSelect )
	
	def clearGrid( self ):
		self.textColour = {}
		self.backgroundColour = {}
		self.grid.Set( data = [], colnames = [], textColour = {}, backgroundColour = {} )
		self.grid.Reset()
	
	def refresh( self ):
		self.isEmpty = True
		self.history = None
		self.category = None
		self.rcInterp = set()
		self.rcNumTime = set()
		
		self.search.SelectAll()
		wx.CallAfter( self.Refresh )
		
		race = Model.race
		if race is None:
			self.clearGrid()
			return

		isTimeTrial = race.isTimeTrial
		tRace = race.lastRaceTime()
		lastGridX, lastGridY = self.grid.GetViewStart()
		
		highPrecision = Model.highPrecisionTimes()
		
		if highPrecision or isTimeTrial:
			formatTime = lambda t: Utils.formatTime(t, True)
			formatTimeDiff = lambda a, b: Utils.formatTimeGap(TimeDifference(a, b, True), True)
		else:
			formatTime = Utils.formatTime
			formatTimeDiff = lambda a, b: Utils.formatTimeGap(TimeDifference(a, b, False), False)
		
		category = FixCategories( self.categoryChoice, getattr(race, 'historyCategory', 0), doSyncCategories=self.sync.GetValue() )
		self.hbs.Layout()
		
		Finisher = Model.Rider.Finisher
		results = GetResults( category )
		lapsDown = { rr.num:rr.gap for rr in results if unicode(rr.gap).startswith('-') }
		position = { rr.num:pos for pos, rr in enumerate(results, 1) if rr.status == Finisher }
		winnerLaps = None
		if results and results[0].status == Finisher:
			winnerLaps = results[0].laps

		maxLaps = 0
		doLapsToGo = True
		if race.winAndOut:
			entries = GetEntries( category )
			if entries:
				try:
					maxLaps = max( e.lap for e in entries if not e.interp )
				except ValueError:
					pass
				if race.isRunning():
					maxLaps += 2
		else:
			try:
				maxLaps = race.getNumLapsFromCategory(category)
			except Exception as e:
				maxLaps = race.numLaps
			doLapsToGo = True
			if not maxLaps:
				maxLaps = race.getMaxLap()
				if race.isRunning():
					maxLaps += 2
				doLapsToGo = False
			
		entries = GetEntries( category )
		if maxLaps:
			entries = [e for e in entries if e.lap <= maxLaps]
		entries = [e for e in entries if e.lap <= race.getCategoryNumLaps(e.num)]
		
		if isTimeTrial:
			entries = [Model.Entry(e.num, e.lap, (race.riders[e.num].firstTime or 0.0) + e.t, e.interp) for e in entries]
			entries.extend( [Model.Entry(r.num, 0, (race.riders[r.num].firstTime or 0.0), r.firstTime > tRace) for r in race.riders.itervalues()] )
			entries.sort( key = operator.attrgetter('t', 'num') )
		
		# Collect the number and times for all entries so we can compute lap times.
		numTimes = {(e.num, e.lap) : e.t for e in entries}
		
		self.category = category
		
		if not isTimeTrial:
			# Trim out the lap 0 starts.
			entries = [e for e in entries if e.lap > 0]
		
		if not entries:
			self.clearGrid()
			return
		
		# Organize all the entries into a grid as we would like to see them.
		self.history = [ [] ]
		if isTimeTrial:
			leaderTimes = []
			for e in entries:
				while len(self.history) <= e.lap:
					self.history.append( [] )
				if e.lap >= len(leaderTimes):
					leaderTimes.append( e.t )
				self.history[e.lap].append( e )
		else:
			numSeen = set()
			lapCur = 0
			leaderTimes = [entries[0].t]
			for e in entries:
				if e.num in numSeen:
					numSeen.clear()
					lapCur += 1
					self.history.append( [] )
					leaderTimes.append( e.t )
				self.history[lapCur].append( e )
				numSeen.add( e.num )
		
		if not any( h for h in self.history ):
			self.clearGrid()
			return
		
		# Show the values.
		self.isEmpty = False
			
		numTimeInfo = race.numTimeInfo
		
		colnames = []
		raceTime = 0
		for c, h in enumerate(self.history):
			try:
				lapTime = h[0].t - raceTime
				raceTime = h[0].t
			except IndexError as e:
				lapTime = 0
				
			colnames.append( '{}\n{}\n{}\n{}'.format(
								c+(0 if isTimeTrial else 1),
								(maxLaps - c - 1) if doLapsToGo else ' ',
								formatTime(lapTime),
								formatTime(raceTime))
							)
		
		formatStr = ['$num']
		if self.showTimes:		formatStr.append(', $raceTime')
		if self.showLapTimes:	formatStr.append(', $lapTime')
		if self.showTimeDown:	formatStr.append(', $downTime')
		if self.showRiderName:	formatStr.append(', $riderName')
		template = Template( u''.join(formatStr) )
		
		try:
			info = race.excelLink.read()
		except:
			info = {}
			
		def getName( num ):
			d = info.get(num, {})
			return u', '.join( v for v in [d.get('LastName',None), d.get('FirstName',None)] if v )
		
		templateSave = template
		data = []
		for col, h in enumerate(self.history):
			template = templateSave
			if col+1 == winnerLaps:
				if self.showPosition:
					formatStr.insert(0, '$pos$lapsDown: ')
				template = Template( u''.join(formatStr) )
			
			data.append( [ template.safe_substitute(
				{
					'num':		e.num,
					'pos':		Utils.ordinal(position.get(e.num, '')),
					'lapsDown':	u' ({})'.format(lapsDown[e.num]) if e.num in lapsDown else u'',
					'raceTime':	formatTime(e.t) if self.showTimes else '',
					'lapTime':	formatTime(e.t - numTimes[(e.num,e.lap-1)]) if self.showLapTimes and (e.num,e.lap-1) in numTimes else '',
					'downTime':	formatTimeDiff(e.t, leaderTimes[col]) if self.showTimeDown and col < len(leaderTimes) else '',
					'riderName': getName(e.num) if self.showRiderName else '',
				} ) for e in h] )
			self.rcInterp.update( (row, col) for row, e in enumerate(h) if e.interp )
			self.rcNumTime.update( (row, col) for row, e in enumerate(h) if numTimeInfo.getInfo(e.num, e.t) is not None )

		self.grid.Set( data = data, colnames = colnames )
		self.grid.AutoSizeColumns( True )
		self.grid.Reset()
		self.updateColours()
		self.grid.Set( textColour = self.textColour, backgroundColour = self.backgroundColour )
		
		# Fix the grid's scrollbars.
		self.grid.FitInside()
		self.grid.Scroll( lastGridX, lastGridY )
	
	def commit( self ):
		pass
	
if __name__ == '__main__':
	#for x in dir(wx):
	#	if x.startswith('MOD_'):
	#		print x
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	for i, rider in enumerate(Model.getRace().riders.itervalues()):
		rider.firstTime = i * 30.0
	Model.getRace().isTimeTrial = True
	history = History(mainWin)
	history.refresh()
	mainWin.Show()
	app.MainLoop()
