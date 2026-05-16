import sys
import math
import datetime
import operator
from bisect import bisect_left

import wx
import wx.lib.colourselect as  csel
import wx.lib.intctrl as intctrl

import Model
import Utils

from SetLaps import SetLaps
from GetResults import GetResultsWithData

import heapq

class TopNTracker:
	"""Tracks the top N largest elements seen so far using a min-heap."""

	def __init__(self, n: int):
		if n <= 0:
			raise ValueError("n must be a positive integer")
		self.n = n
		self._heap = []  # min-heap: heap[0] is always the smallest of the top-N

	def add(self, value) -> None:
		"""Add a new element. O(log N) time."""
		if len(self._heap) < self.n:
			heapq.heappush(self._heap, value)
		elif value > self._heap[0]:
			heapq.heapreplace(self._heap, value)  # pop min, push new in one step

	def top(self) -> list:
		"""Return the top N elements in descending order. O(N log N)."""
		return sorted(self._heap, reverse=True)

	def topUnsorted( self ) -> list:
		"""Return a copy of the top elements unsorted."""
		return self._heap[:]

	def peek_min(self):
		"""Return the smallest element among the top N (the threshold). O(1)."""
		if not self._heap:
			raise IndexError("tracker is empty")
		return self._heap[0]

	def __len__(self) -> int:
		return len(self._heap)

	def __repr__(self) -> str:
		return f"TopNTracker(n={self.n}, top={self.top()})"

defaultBackgroundColours = [
	wx.Colour(16,16,16), wx.Colour(34,139,34), wx.Colour(235,155,0),
	wx.Colour(147,112,219), wx.Colour(0,0,139), wx.Colour(139,0,0)
]
def getForegroundsBackgrounds():
	race = Model.race
	foregrounds, backgrounds = [], []
	for i in range(len(defaultBackgroundColours)):
		try:
			foregrounds.append( Utils.colorFromStr(race.lapCounterForegrounds[i]) )
		except (IndexError, AttributeError):
			foregrounds.append( wx.WHITE )
		try:
			backgrounds.append( Utils.colorFromStr(race.lapCounterBackgrounds[i]) )
		except (IndexError, AttributeError):
			backgrounds.append( defaultBackgroundColours[i] )
	return foregrounds, backgrounds

def getLapCounterOptions( isDialog ):
	parentClass = wx.Dialog if isDialog else wx.Panel
	class LapCounterOptionsClass( parentClass ):
		def __init__( self, parent, id=wx.ID_ANY ):
			if isDialog:
				super().__init__( parent, id, _("Lap Counter Options"),
							style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
			else:
				super().__init__( parent, id )
			
			vs = wx.BoxSizer( wx.VERTICAL )
			
			vs.Add( wx.StaticText(self, label=_('Lap Counter Options')), flag=wx.LEFT|wx.TOP|wx.RIGHT, border=8 )

			fgs = wx.FlexGridSizer( cols=2, vgap=4, hgap=4 )
			
			fgs.Add( wx.StaticText(self, label=_('Type')), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
			self.counterType = wx.Choice(self, choices=(_('Lap Counter'), _('Countdown Timer')))
			self.counterType.SetSelection( 0 )
			fgs.Add( self.counterType )
			
			fgs.Add( wx.StaticText(self, label=_('Foregrounds')), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
			self.foregrounds = [csel.ColourSelect(self, colour=wx.WHITE, size=(40,-1))
				for i in range(len(defaultBackgroundColours))]
			hs = wx.BoxSizer( wx.HORIZONTAL )
			for i, cs in enumerate(self.foregrounds):
				hs.Add( cs, flag=wx.LEFT, border=4 if i else 0 )
			fgs.Add( hs )
			fgs.Add( wx.StaticText(self, label=_('Backgrounds')), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
			self.backgrounds = [csel.ColourSelect(self, size=(40,-1), colour=defaultBackgroundColours[i])
				for i in range(len(defaultBackgroundColours))]
			hs = wx.BoxSizer( wx.HORIZONTAL )
			for i, cs in enumerate(self.backgrounds):
				hs.Add( cs, flag=wx.LEFT, border=4 if i else 0 )
			fgs.Add( hs )
			
			fgs.Add( wx.StaticText(self, label=''), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
			self.lapElapsedClock = wx.CheckBox(self, label=_('Show Lap Elapsed Time'))
			fgs.Add( self.lapElapsedClock )
			
			fgs.Add( wx.StaticText(self, label=_('Lap Cycle')), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
			self.lapCounterCycle = intctrl.IntCtrl(self, min=0, max=None, limited=True, allow_none=True, )
			fgs.Add( self.lapCounterCycle )
			
			vs.Add( fgs, flag=wx.ALL, border=16 )
			
			vs.Add( wx.StaticText(self, label=_("Seconds before Leader's ETA to change Lap Counter")), flag=wx.LEFT|wx.TOP|wx.RIGHT, border=8 )
			self.slider = wx.Slider(
				self,
				value=int(Model.race.secondsBeforeLeaderToFlipLapCounter) if Model.race else 5, minValue=1, maxValue=180,
				size=(360, -1), 
				style = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS 
			)
			self.slider.SetTickFreq(5)
			vs.Add( self.slider, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=8 )
			
			if isDialog:
				btnSizer = self.CreateButtonSizer( wx.OK|wx.CANCEL )
				self.Bind( wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK )
				if btnSizer:
					vs.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border=16 )
				self.refresh()
			
			self.SetSizerAndFit( vs )
			
		def commit( self ):
			race = Model.race
			if race:
				race.lapCounterForegrounds = [self.foregrounds[i].GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
					for i in range(len(defaultBackgroundColours))]
				race.lapCounterBackgrounds = [self.backgrounds[i].GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
					for i in range(len(defaultBackgroundColours))]
				race.lapCounterCycle = self.lapCounterCycle.GetValue() or None
				race.countdownTimer = (self.counterType.GetSelection() == 1)
				race.secondsBeforeLeaderToFlipLapCounter = self.slider.GetValue()
				race.lapElapsedClock = self.lapElapsedClock.GetValue()
		
		def refresh( self ):
			race = Model.race
			if race:
				self.counterType.SetSelection( 1 if race.countdownTimer else 0 )
				
				fg, bg = getForegroundsBackgrounds()
				for i in range(len(defaultBackgroundColours)):
					self.foregrounds[i].SetColour( fg[i] )
					self.backgrounds[i].SetColour( bg[i] )
				
				self.lapCounterCycle.SetValue( race.lapCounterCycle or None )
				self.slider.SetValue( int(race.secondsBeforeLeaderToFlipLapCounter) )
				self.lapElapsedClock.SetValue( race.lapElapsedClock )
			
		def OnOK( self, event ):
			self.commit()
			self.EndModal( wx.ID_OK )
			
	return LapCounterOptionsClass

def LapCounterOptions( *args, **kwargs ):
	return getLapCounterOptions(True)( *args, **kwargs )
	
def LapCounterProperties( *args, **kwargs ):
	return getLapCounterOptions(False)( *args, **kwargs )

#-----------------------------------------------------------------------

textHeightFactor = 1

def getFontSizeToFit( dc, text, w, h ):
	w, h = max( 1, int(w * 0.9) ), max( 1, int(h * 0.9) )
	fontSize = h
	lines = text.split( '\n' )
	while True:
		dc.SetFont( wx.Font( (0,fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD ) )
		extents = [dc.GetTextExtent(line) for line in lines]
		wText = max( wText for wText, hText in extents )
		hText = round( extents[0][1] * len(lines) * textHeightFactor )
		if fontSize == 1:
			break
		elif wText > w:
			fontSize = max( 1, int(fontSize * w / wText) )
		elif hText > h:
			fontSize = max( 1, int(fontSize * h / hText) )
		else:
			break
	return fontSize

def drawText( dc, label, colour, x, y, w, h ):
	lines = label.split( '\n' )
	lineHeight = dc.GetTextExtent( lines[0] )[1] * textHeightFactor
	yCur = y + (h - lineHeight*len(lines)) // 2
	for line in lines:
		lineWidth, lineHeight = dc.GetTextExtent( line )
		xText, yText = x + (w - lineWidth) // 2, round(yCur)
		dc.SetTextForeground( colour )
		dc.DrawText( line, xText, yText )
		y += lineHeight

def drawLapText( dc, label, colour, x, y, w, h ):
	lines = label.split( '\n' )
	lineHeight = round( dc.GetTextExtent( lines[0] )[1] * textHeightFactor )
	yCur = y + (h - lineHeight*len(lines)) // 2
	for line in lines:
		lineWidth, lineHeight = dc.GetTextExtent( line )
		xText, yText = x + (w - lineWidth) // 2, round(yCur)
		if colour.GetAsString(wx.C2S_HTML_SYNTAX) != '#000000':
			dc.SetTextForeground( wx.BLACK )
			shadowOffset = lineHeight//52
			dc.DrawText( line, xText + shadowOffset, yText + shadowOffset )
		dc.SetTextForeground( colour )
		dc.DrawText( line, xText, yText )
		yCur += lineHeight

#-----------------------------------------------------------------------

class LapCounter( wx.Panel ):
	millis = 333
	lapCounterCycle = None
	countdownTimer = False
	lapElapsedClock = True
	
	def __init__( self, parent, labels=None, id=wx.ID_ANY, size=(640,480), style=0 ):
		super().__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		self.labels = labels or []
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_RIGHT_DOWN, self.OnRightClick )
		self.timer = wx.Timer( self )
		self.Bind( wx.EVT_TIMER, self.OnTimer )
		self.timer.Start( self.millis )
		
		self.flashOn = False
		self.font = None
		self.fontSize = -1
		self.showTime = False
		
		self.SetCursor( wx.Cursor(wx.CURSOR_RIGHT_BUTTON) )
		self.SetBackgroundColour( wx.BLACK )
		self.SetForegroundColour( wx.GREEN )
		self.foregrounds = [wx.WHITE] * len(defaultBackgroundColours)
		self.backgrounds = list(defaultBackgroundColours)
		
		self.ttSpots = []	# Used to manage the spots in the TT lap counter.
		
		self.xClick = 0
		self.yClick = 0

	def GetState( self ):
		lenLabels = len(self.labels)
		fg, bg = getForegroundsBackgrounds()
		race = Model.race
		isTimeTrial = (race and race.isTimeTrial)
		return {
			'cmd': 'refresh',
			'isTimeTrial': (race and race.isTimeTrial),
			'labels': self.labels if not isTimeTrial else [],
			'ttSpotText': self.getTTSpotText() if isTimeTrial else [],
			'foregrounds': [c.GetAsString(wx.C2S_CSS_SYNTAX) for c in fg[:lenLabels]],
			'backgrounds': [c.GetAsString(wx.C2S_CSS_SYNTAX) for c in bg[:lenLabels]],
			'raceStartTime': race.startTime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] if race and race.startTime else None,
			'lapElapsedClock': self.lapElapsedClock,
		}

	def OnOptions( self, event ):
		with LapCounterOptions( self ) as d:
			if d.ShowModal() != wx.ID_OK:
				return
			wx.CallAfter( self.refresh )
			mainWin = Utils.getMainWin()
			if mainWin:
				wx.CallAfter( mainWin.lapCounterDialog.refresh )
	
	def OnPopupLockLapsToGo( self, event ):
		race = Model.race
		if not race or race.isUnstarted() or race.isTimeTrial:
			return
		
		try:
			categoryLaps = Utils.getMainWin().record.raceHUD.GetLaps()
		except Exception:
			return
		
		for (x, y, w, h), laps, category in zip(self.tessellate(len(self.labels)), categoryLaps, race.getCategories(startWaveOnly=True)):
			if x <= self.xClick < x+w and y <= self.yClick < y+h:
				category._numLaps = laps
				return
	
	def OnPopupSetLaps( self, event ):
		race = Model.race
		if not race or race.isTimeTrial:
			return

		try:
			categoryLaps = Utils.getMainWin().record.raceHUD.GetLaps()
		except Exception:
			return
		
		for (x, y, w, h), laps, category in zip(self.tessellate(len(self.labels)), categoryLaps, race.getCategories(startWaveOnly=True)):
			if x <= self.xClick < x+w and y <= self.yClick < y+h:
				with SetLaps(self, category=category) as setLaps:
					setLaps.ShowModal()
				return		
	
	def OnRightClick( self, event ):
		race = Model.race
		if not race:
			return
		
		self.xClick, self.yClick = event.GetX(), event.GetY()

		for (x, y, w, h), category in zip(self.tessellate(len(self.labels)), race.getCategories(startWaveOnly=True)):
			if x <= self.xClick < x+w and y <= self.yClick < y+h:
				break
		else:
			category = None
		
		if not category:
			return

		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				(_('Lock in Laps to Go'),	_('Lock in Laps to Go'),	self.OnPopupLockLapsToGo),
				(_('Set Laps...'),			_('Set Laps...'),			self.OnPopupSetLaps),
				(_('Options') + '...',		_('Options'),				self.OnOptions),
			]
			self.menuOptions = []
			for caseCode in range(2):
				menu = wx.Menu()
				for i, (name, text, callback) in enumerate(self.popupInfo):
					if i == 0 and caseCode == 0:
						continue
					item = menu.Append( wx.ID_ANY, name, text )
					self.Bind( wx.EVT_MENU, callback, item )
				self.menuOptions.append( menu )
		
		caseCode = 0 if (race and race.isUnstarted()) or category.isNumLapsLocked() else 1
		self.PopupMenu( self.menuOptions[caseCode] )
		
	def OnTimer( self, event=None ):
		if self.countdownTimer:
			race = Model.race
			self.timer.Stop()
			if not race or not race.isRunning():
				return
			self.timer.Start( 500, oneShot = True )
			self.Refresh()
		else:
			self.flashOn = not self.flashOn
			if self.lapElapsedClock or any( flash for label, flash, tLapTime in self.labels ):
				self.Refresh()

	def SetCountdownTimer( self, countdownTimer ):
		self.countdownTimer = countdownTimer
		if self.countdownTimer and not self.timer.IsRunning():
			self.OnTimer()

	def SetLabels( self, labels=None, showTime=False ):
		labels = labels or [('\u25AF\u25AF', False, None)]
		
		self.showTime = showTime
		
		''' labels is of the format [(label1, flash), (label2, flash)] '''
		if self.labels == labels:
			return
			
		self.labels = labels[:self.MaxLabels]
		if self.countdownTimer:
			if not self.timer.IsRunning():
				self.OnTimer()
			return
		
		if any( flash for label, flash, tLapStart in self.labels ) or (
				self.lapElapsedClock and any(tLapStart is not None for label, flash, tLapStart in self.labels)):
			if not self.timer.IsRunning():
				self.timer.Start( self.millis )
		else:
			self.timer.Stop()
			self.flashOn = True
		self.Refresh()
	
	def OnSize( self, event ):
		self.Refresh()
	
	def GetFont( self, lineHeight ):
		if lineHeight == self.fontSize:
			return self.font
		self.fontSize = lineHeight
		self.font = wx.Font( (0,lineHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD )
		return self.font
		
	def GetCountdownTime( self ):
		race = Model.race
		if not race:
			return None
		if race.isUnstarted():
			return '{} {}'.format( race.minutes, _('min') )
		if not race.isRunning():
			return None
		
		endTime = race.startTime + datetime.timedelta(seconds=race.minutes*60.0)
		nowTime = datetime.datetime.now()
		secs = math.floor((endTime - nowTime).total_seconds())
		over = ''
		if secs < 0:
			over = '+'
			secs = -secs
		
		secs = int(secs)
		hours = secs // (60*60)
		minutes = (secs // 60) % 60
		seconds = secs % 60
		if hours:
			return '{}{}:{:02d}:{:02d}'.format( over, hours, minutes, seconds )
		return '{}{}:{:02d}'.format( over, minutes, seconds )
	
	MaxLabels = 6
	
	def tessellate( self, numLabels=999 ):
		# Defaults to returning the maximum number of tesselations.
		width, height = self.GetSize()
		if numLabels == 1:
			return ((0, 0, width, height),)
		if numLabels == 2:
			w = width // 2
			return ((0, 0, w, height), (w, 0, w, height),)
		if numLabels <= 4:
			w = width // 2
			h = height // 2
			return (
				(0, 0, w, h), (w, 0, w, h),
				(0, h, w, h), (w, h, w, h),
			)
		else:
			w = width // 3
			h = height // 2
			return (
				(0, 0, w, h), (w, 0, w, h), (2*w, 0, w, h),
				(0, h, w, h), (w, h, w, h), (2*w, h, w, h),
			)
	
	def paintMassStart( self, dc ):
		width, height = self.GetSize()
		border = 0

		if self.countdownTimer:
			label = self.GetCountdownTime()
			if not label:
				return
			lineHeight = height - border*2
			dc.SetFont( wx.Font( (0,lineHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD ) )
			sizeLabel = '000000000:00:00'[-len(label):]
			w, h = dc.GetTextExtent(sizeLabel)
			if w > width-8:
				lineHeight *= float(width-8) / float(w)
			dc.SetFont( wx.Font( (0,lineHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD ) )
			yTop = (height - lineHeight) // 2
			dc.DrawText( label, (width - dc.GetTextExtent(sizeLabel)[0]) // 2, yTop )
			if not self.timer.IsRunning():
				self.OnTimer()
			return
		
		if not self.labels:
			return
		
		def getCycleLap( label ):
			if not self.lapCounterCycle or not label.strip().isdigit():
				return label
			lapCur = int(label.strip())
			if lapCur > 0:
				lapCur %= self.lapCounterCycle
				if lapCur == 0:
					lapCur = self.lapCounterCycle
			return f'{lapCur}'
		
		dc.SetPen( wx.TRANSPARENT_PEN )
		
		race = Model.race
		tRace = race.curRaceTime() if self.lapElapsedClock and race and race.isRunning() else None
		
		footerMult = 0.15
		rects = self.tessellate(len(self.labels))
		for i, (label, flash, tLapStart) in enumerate(self.labels):
			x, y, w, h = rects[i]
			
			dc.SetBrush( wx.Brush(self.backgrounds[i], wx.SOLID) )
			dc.DrawRectangle( x, y, w, h )
			
			lineBorderWidth = 4
			dc.SetPen( wx.Pen(wx.BLACK, lineBorderWidth) )
			dc.DrawRectangle( x, y, w, h )
								
			# Draw the lapcount identifier.
			if len(self.labels) > 1:
				text = chr( ord('A') + i )
				hCC = int( h * footerMult )
				yCC = y + h - hCC
				getFontSizeToFit( dc, text, hCC, hCC )
				drawText( dc, text, self.foregrounds[i], x, yCC, hCC, hCC )

			if label == '1':
				text = '\U0001F514'
				hCC = int( h * footerMult )
				yCC = y + h - hCC
				getFontSizeToFit( dc, text, hCC, hCC )
				drawText( dc, text, self.foregrounds[i], x + w - hCC, yCC, hCC, hCC )

			if self.lapElapsedClock:
				hCC = int( h * footerMult )
				yCC = y + h - hCC
				h -= hCC
				if tLapStart is not None and tRace:
					secs = tRace - tLapStart
					tElapsed = Utils.formatTime( secs )
					getFontSizeToFit( dc, tElapsed, w, hCC )
					drawText( dc, tElapsed, self.foregrounds[i], x, yCC, w, hCC )
			
			if not flash or self.flashOn:
				label = getCycleLap(label)
				getFontSizeToFit( dc, label, w, h )
				drawLapText( dc, label, self.foregrounds[i], x, y, w, h )
	
	#-------------------------------------------------------------------
	def getTTSpotText( self ):
		rects = self.tessellate()

		race = Model.race
		if not race or not race.isRunning() or not race.isTimeTrial:
			return [''] * len(rects)
		
		if len(self.ttSpots) < len(rects):
			self.ttSpots = [None] * (len(rects) - len(self.ttSpots))

		tRace = race.curRaceTime()
		
		rects = self.tessellate()
		if len(self.ttSpots) < len(rects):
			self.ttSpots = [None] * (len(rects) - len(self.ttSpots))

		# Find the closest interpreted times to tRace.
		Finisher = Model.Rider.Finisher
		resultsAll = []
		topN = TopNTracker( len(rects) )
		for category in race.getCategories( startWaveOnly=True ):
			numLaps = category.getNumLaps()
			if numLaps <= 1:
				continue	# Can't show a lap counter on a 1-lap race.
			
			for rr in GetResultsWithData( category ):
				# If not a Finisher, or if the last lap is recorded then this rider is done.
				# In either case we can skip the rider as no lap counter is necessary.
				if rr.status != Finisher or not rr.interp or not rr.interp[-1]:
					continue
				
				# Find the closest interpolated raceTime before or after the current race time.
				rider = race.riders[rr.num]
				startTime = rider.firstTime
				
				# Since raceTimes are in elapsed time, so we have to adjust for the startTime in the search.
				iClosest = max(0, bisect_left(rr.raceTimes, tRace - startTime) )
				dtBest = (-sys.float_info.max, None)
				for lap in range(max(1, iClosest-1), min(len(rr.interp), iClosest+1)):
					if rr.interp[lap]:
						t = rr.raceTimes[lap] + startTime
						dt = -abs(t - tRace)
						if dt > dtBest[0]:	# As the values are negative, do the opposite comparison.
							dtBest = (dt, t, startTime, rr.num, numLaps - lap, rr)
						
				# Add the closest time for this rider to the overall closest laps.
				if dtBest[-1] is not None:
					topN.add( dtBest )
		
		# Sort by time and startTime.
		ttEntries = sorted( topN.topUnsorted(), key = operator.itemgetter(1, 2) )
		if not ttEntries:
			return [''] * len(rects)
		
		# Clean up spots displaying expired data.
		# self.ttSpots[i] will either be None (empty) or contain the tuple (num, lapsToGo, t).
		ttNums = { num:(num, lapsToGo, t) for dt, t, startTime, num, lapsToGo, rr in ttEntries }
		ttSpotNums = set()
		ttEmptySpots = []
		for i in range(len(self.ttSpots)):
			try:
				num = self.ttSpots[i][0]
				self.ttSpots[i] = ttNums[num]
				ttSpotNums.add( num )
			except (TypeError, KeyError):
				self.ttSpots[i] = None
				ttEmptySpots.append( i )
		
		# Fill any open spots with the closest data.
		iEmptySpotCur = 0
		for num, lapsToGo, t in ttNums.values():
			if num not in ttSpotNums:
				self.ttSpots[ttEmptySpots[iEmptySpotCur]] = (num, lapsToGo, t)
				iEmptySpotCur += 1;
		
		# Format each spot as text.
		flag = '\U0001F3C1'
		bell = '\U0001F514'

		spotText = []
		for e in self.ttSpots:
			if e is None:
				spotText.append( '' )
				continue
				
			num, lapsToGo, t = e
			match lapsToGo:
				case 0:
					text = f'{num}\n{flag}'
				case 1:
					text = f'{num}\n{lapsToGo} {bell}'
				case _:
					text = f'{num}\n{lapsToGo}'
			
			spotText.append( text );
		
		if len(spotText) < len(rects):
			spotText.extend( [''] * (len(rects) - len(spotText)) )
			
		return spotText
	
	def paintTT( self, dc ):		
		spotText = self.getTTSpotText()
		width, height = self.GetSize()
		border = 0

		dc.SetPen( wx.TRANSPARENT_PEN )
		
		rects = self.tessellate()
		foreground, background = self.foregrounds[0], self.backgrounds[0]
		for i, text in enumerate(self.getTTSpotText()):
			x, y, w, h = rects[i]
						
			dc.SetBrush( wx.Brush(background, wx.SOLID) )
			dc.DrawRectangle( x, y, w, h )
			
			lineBorderWidth = 4
			dc.SetPen( wx.Pen(wx.BLACK, lineBorderWidth) )
			dc.DrawRectangle( x, y, w, h )
			
			if text:
				getFontSizeToFit( dc, text, w, h )
				drawLapText( dc, text, foreground, x, y, w, h )
			
	def OnPaint( self, event ):
		dc = wx.AutoBufferedPaintDC( self )
		dc.SetBackground( wx.Brush(self.GetBackgroundColour(), wx.SOLID) )
		dc.SetTextForeground( self.GetForegroundColour() )
		dc.Clear()
		
		if Model.race:
			if not Model.race.isTimeTrial:
				self.paintMassStart( dc )
			else:
				self.paintTT( dc )
	
	def commit( self ):
		pass
		
	def getLapCycle( self, category ):
		race = Model.race
		lap = race.getNumLapsFromCategory(category) if race else category.getNumLaps()
		return lap % self.lapCounterCycle if self.lapCounterCycle else lap
		
	def getLapText( self, category ):
		race = Model.race
		lap = race.getNumLapsFromCategory( category )
		if lap:
			lap = lap % self.lapCounterCycle if self.lapCounterCycle else lap
			return '{}'.format( lap )
		minutes = category.raceMinutes if category.raceMinutes else race.raceMinutes
		return '{} min'.format( minutes ) if minutes else ''
	
	def refresh( self ):
		race = Model.race
		self.foregrounds, self.backgrounds = getForegroundsBackgrounds()
		if race:
			self.SetCountdownTimer( race.countdownTimer )
			self.SetForegroundColour( self.foregrounds[0] )
			self.SetBackgroundColour( self.backgrounds[0] )
			self.lapCounterCycle = race.lapCounterCycle or None
			self.lapElapsedClock = race.lapElapsedClock
			if race.isUnstarted():
				self.SetLabels( [(self.getLapText(category),False,None) for category in race.getCategories(startWaveOnly=True)] )
			elif race.isFinished():
				self.SetLabels()
			else:
				self.SetLabels( self.labels, self.showTime )
		else:
			self.SetLabels()
		
		self.Refresh()
	
if __name__ == '__main__':
	app = wx.App(False)
	
	Model.setRace( Model.Race() )
	model = Model.getRace()
	model._populate()
	
	displayWidth, displayHeight = wx.GetDisplaySize()
	mainWin = wx.Frame(None,title="LapCounter", size=(int(displayWidth/2),int(displayHeight/2)))
	lapCounter = LapCounter( mainWin, labels=(('17',False), ('15',True)) )
	lapCounter.refresh()
	
	mainWin.Show()
	
	for j, i in enumerate(range(0,40,4)):
		wx.CallLater( 4000*i, lambda a=17-j, b=15-j, c=11-j, d=7-j, e=5-j, f=3-j: lapCounter.SetLabels( (
			('{}'.format(a), True, i),
			('{}'.format(b), False, i),
			('{}'.format(c), False, i),
			('{}'.format(d), False, i),
			('{}'.format(e), False, i),
			('{}'.format(f), False, i),
		)) )
		wx.CallLater( 6000*i, lambda a=17-j, b=15-j, c=11-j, d=7-j, e=5-j, f=3-j: lapCounter.SetLabels( (
			('{}'.format(a), False, i),
			('{}'.format(b), True, i),
			('{}'.format(c), False, i),
			('{}'.format(d), False, i),
			('{}'.format(e), False, i),
			('{}'.format(f), False, i),
		)) )
		wx.CallLater( 8000*i, lambda a=17-j, b=15-j, c=11-j, d=7-j, e=5-j, f=3-j: lapCounter.SetLabels( (
			('{}'.format(a), False, i),
			('{}'.format(b), False, i),
			('{}'.format(c), True, i),
			('{}'.format(d), True, i),
			('{}'.format(e), False, i),
			('{}'.format(f), False, i),
		)) )
	
	app.MainLoop()
