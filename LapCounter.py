import wx
import wx.lib.colourselect as  csel
import wx.lib.intctrl as intctrl
import math
import datetime
import Model
import Utils

from GetResults import GetResults

defaultBackgroundColours = [wx.Colour(16,16,16), wx.Colour(34,139,34), wx.Colour(235,155,0), wx.Colour(147,112,219)]
def getForegroundsBackgrounds():
	race = Model.race
	foregrounds, backgrounds = [], []
	for i in xrange(len(defaultBackgroundColours)):
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
				super( LapCounterOptionsClass, self ).__init__( parent, id, _("Lap Counter Options"),
							style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
			else:
				super( LapCounterOptionsClass, self ).__init__( parent, id )
			
			vs = wx.BoxSizer( wx.VERTICAL )
			
			vs.Add( wx.StaticText(self, label=_('Lap Counter Options')), flag=wx.LEFT|wx.TOP|wx.RIGHT, border=8 )

			fgs = wx.FlexGridSizer( cols=2, vgap=4, hgap=4 )
			
			fgs.Add( wx.StaticText(self, label=_('Type')), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
			self.counterType = wx.Choice(self, choices=(_('Lap Counter'), _('Countdown Timer')))
			self.counterType.SetSelection( 0 )
			fgs.Add( self.counterType )
			
			fgs.Add( wx.StaticText(self, label=_('Foregrounds')), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
			self.foregrounds = [csel.ColourSelect(self, colour=wx.WHITE, size=(40,-1))
				for i in xrange(len(defaultBackgroundColours))]
			hs = wx.BoxSizer( wx.HORIZONTAL )
			for i, cs in enumerate(self.foregrounds):
				hs.Add( cs, flag=wx.LEFT, border=4 if i else 0 )
			fgs.Add( hs )
			
			fgs.Add( wx.StaticText(self, label=_('Backgrounds')), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
			self.backgrounds = [csel.ColourSelect(self, size=(40,-1), colour=defaultBackgroundColours[i])
				for i in xrange(len(defaultBackgroundColours))]
			hs = wx.BoxSizer( wx.HORIZONTAL )
			for i, cs in enumerate(self.backgrounds):
				hs.Add( cs, flag=wx.LEFT, border=4 if i else 0 )
			fgs.Add( hs )
			
			fgs.Add( wx.StaticText(self, label=_('Lap Cycle')), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
			self.lapCounterCycle = intctrl.IntCtrl(self, min=0, max=None, limited=True, allow_none=True, )
			fgs.Add( self.lapCounterCycle )
			
			vs.Add( fgs, flag=wx.ALL, border=16 )
			
			vs.Add( wx.StaticText(self, label=_("Seconds before Leader's ETA to change Lap Counter")), flag=wx.LEFT|wx.TOP|wx.RIGHT, border=8 )
			self.slider = wx.Slider(
				self,
				value=Model.race.secondsBeforeLeaderToFlipLapCounter if Model.race else 5, minValue=1, maxValue=180,
				size=(360, -1), 
				style = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS 
			)
			self.slider.SetTickFreq(5)
			vs.Add( self.slider, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=8 )
			
			if isDialog:
				self.okButton = wx.Button(self, wx.ID_OK)
				self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
				self.cancelButton = wx.Button(self, wx.ID_CANCEL)
				self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)
				
				buttonSizer = wx.StdDialogButtonSizer()
				buttonSizer.AddButton( self.okButton )
				buttonSizer.AddButton( self.cancelButton )
				buttonSizer.Realize()
				
				vs.Add( buttonSizer, flag=wx.ALL, border=16 )
				
				self.refresh()
			
			self.SetSizerAndFit( vs )
			
		def commit( self ):
			race = Model.race
			if race:
				race.lapCounterForegrounds = [self.foregrounds[i].GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
					for i in xrange(len(defaultBackgroundColours))]
				race.lapCounterBackgrounds = [self.backgrounds[i].GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
					for i in xrange(len(defaultBackgroundColours))]
				race.lapCounterCycle = self.lapCounterCycle.GetValue() or None
				race.countdownTimer = (self.counterType.GetSelection() == 1)
				race.secondsBeforeLeaderToFlipLapCounter = self.slider.GetValue()
		
		def refresh( self ):
			race = Model.race
			if race:
				self.counterType.SetSelection( 1 if race.countdownTimer else 0 )
				
				fg, bg = getForegroundsBackgrounds()
				for i in xrange(len(defaultBackgroundColours)):
					self.foregrounds[i].SetColour( fg[i] )
					self.backgrounds[i].SetColour( bg[i] )
				
				self.lapCounterCycle.SetValue( race.lapCounterCycle or None )
				self.slider.SetValue( race.secondsBeforeLeaderToFlipLapCounter )
			
		def OnOK( self, event ):
			self.commit()
			self.EndModal( wx.ID_OK )
			
		def OnCancel( self, event ):
			self.EndModal( wx.ID_CANCEL )
			
	return LapCounterOptionsClass

def LapCounterOptions( *args, **kwargs ):
	return getLapCounterOptions(True)( *args, **kwargs )
	
def LapCounterProperties( *args, **kwargs ):
	return getLapCounterOptions(False)( *args, **kwargs )
	
class LapCounter( wx.Panel ):
	millis = 333
	lapCounterCycle = None
	countdownTimer = False
	
	def __init__( self, parent, labels=[], id=wx.ID_ANY, size=(640,480), style=0 ):
		super(LapCounter, self).__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		self.labels = labels
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_RIGHT_DOWN, self.OnRightClick )
		self.timer = wx.Timer( self )
		self.Bind( wx.EVT_TIMER, self.OnTimer )
		self.timer.Start( self.millis )
		
		self.flashOn = False
		self.font = None
		self.fontSize = -1
		
		self.SetCursor( wx.Cursor(wx.CURSOR_RIGHT_BUTTON) )
		self.SetBackgroundColour( wx.BLACK )
		self.SetForegroundColour( wx.GREEN )
		self.foregrounds = [wx.WHITE] * len(defaultBackgroundColours)
		self.backgrounds = list(defaultBackgroundColours)
		
		self.xClick = 0
		self.yClick = 0

	def GetState( self ):
		lenLabels = len(self.labels)
		fg, bg = getForegroundsBackgrounds()
		return {
			'cmd': 'refresh',
			'labels': self.labels,
			'foregrounds': [c.GetAsString(wx.C2S_CSS_SYNTAX) for c in fg[:lenLabels]],
			'backgrounds': [c.GetAsString(wx.C2S_CSS_SYNTAX) for c in bg[:lenLabels]],
		}

	def OnOptions( self, event ):
		d = LapCounterOptions( self )
		if d.ShowModal() == wx.ID_OK:
			wx.CallAfter( self.refresh )
			mainWin = Utils.getMainWin()
			if mainWin:
				wx.CallAfter( mainWin.lapCounterDialog.refresh )
		d.Destroy()
	
	def OnPopupLockLapsToGo( self, event ):
		race = Model.race
		if not race or race.isUnstarted() or race.isTimeTrial:
			return
		
		try:
			categoryLaps = Utils.getMainWin().record.raceHUD.GetLaps()
		except:
			return
		
		for (x, y, w, h), laps, category in zip(self.tessellate(len(self.labels)), categoryLaps, race.getCategories(startWaveOnly=True)):
			if x <= self.xClick < x+w and y <= self.yClick < y+h:
				category._numLaps = laps
				return
	
	def OnRightClick( self, event ):
		race = Model.race
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
				(wx.NewId(), _('Lock in Laps to Go'),		_('Lock in Laps to Go'),	self.OnPopupLockLapsToGo),
				(wx.NewId(), _('Options') + u'...',		_('Options'),			self.OnOptions),
			]
			for p in self.popupInfo:
				if p[0]:
					self.Bind( wx.EVT_MENU, p[3], id=p[0] )
		
		menu = wx.Menu()
		for i, (id, name, text, callback) in enumerate(self.popupInfo):
			if i == 0:
				if race and race.isUnstarted():
					continue
				if category.isNumLapsLocked():
					continue
			menu.Append( id, name, text )
		
		self.PopupMenu( menu )
		menu.Destroy()
		
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
			if any( flash for label, flash in self.labels ):
				self.Refresh()

	def SetCountdownTimer( self, countdownTimer ):
		self.countdownTimer = countdownTimer
		if self.countdownTimer and not self.timer.IsRunning():
			self.OnTimer()

	def SetLabels( self, labels=[], showTime=False ):
		labels = labels or [(u'\u25AF\u25AF', False)]
		
		self.showTime = showTime
		
		''' labels is of the format [(label1, flash), (label2, flash)] '''
		if self.labels == labels:
			return
			
		self.labels = labels[:4]
		if self.countdownTimer:
			if not self.timer.IsRunning():
				self.OnTimer()
			return
		
		if not any( flash for label, flash in self.labels ):
			self.timer.Stop()
			self.flashOn = True
		elif not self.timer.IsRunning():
			self.timer.Start( self.millis )
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
			return u'{} {}'.format( race.minutes, _('min') )
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
	
	def tessellate( self, numLabels ):
		width, height = self.GetSize()
		if numLabels == 1:
			return ((0, 0, width, height),)
		if numLabels == 2:
			w = width // 2
			return ((0, 0, w, height), (w, 0, w, height),)
		w = width // 2
		h = height // 2
		return (
			(0, 0, w, h), (w, 0, w, h),
			(0, h, w, h), (w, h, w, h),
		)
			
	def OnPaint( self, event ):
		dc = wx.AutoBufferedPaintDC( self )
		dc.SetBackground( wx.Brush(self.GetBackgroundColour(), wx.SOLID) )
		dc.SetTextForeground( self.GetForegroundColour() )
		dc.Clear()
		
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
			return u'{}'.format(lapCur)
		
		dc.SetPen( wx.TRANSPARENT_PEN )
		
		def getFontSizeToFit( text, w, h ):
			w = int( w * 0.9 )
			h = int( h * 0.9 )
			fontSize = h
			dc.SetFont( wx.Font( (0,fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD ) )
			wText, hText = dc.GetTextExtent( text )
			if wText > w:
				fontSize = int( fontSize * w / wText )
				dc.SetFont( wx.Font( (0,fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD ) )
			return fontSize
		
		def drawLapText( label, colour, x, y, w, h ):
			labelWidth, labelHeight = dc.GetTextExtent( label )
			xText, yText = x + (w - labelWidth) // 2, y + (h - labelHeight) // 2
			dc.SetTextForeground( wx.BLACK )
			shadowOffset = labelHeight//52
			dc.DrawText( label, xText + shadowOffset, yText + shadowOffset )
			dc.SetTextForeground( colour )
			dc.DrawText( label, xText, yText )
		
		rects = self.tessellate(len(self.labels))
		for i, (label, flash) in enumerate(self.labels):
			x, y, w, h = rects[i]
			
			dc.SetBrush( wx.Brush(self.backgrounds[i], wx.SOLID) )
			dc.DrawRectangle( x, y, w, h )
			
			lineBorderWidth = 4
			dc.SetPen( wx.Pen(wx.BLACK, lineBorderWidth) )
			dc.DrawRectangle( x, y, w, h )
			
			if not flash or self.flashOn:
				label = getCycleLap(label)
				getFontSizeToFit( label, w, h )
				drawLapText( label, self.foregrounds[i], x, y, w, h )
	
	def commit( self ):
		pass
		
	def getLapCycle( self, category ):
		race = Model.race
		lap = race.getNumLapsFromCategory(category) if race else category.getNumLaps()
		return lap % self.lapCounterCycle if self.lapCounterCycle else lap
	
	def refresh( self ):
		race = Model.race
		self.foregrounds, self.backgrounds = getForegroundsBackgrounds()
		
		if race:
			self.SetCountdownTimer( race.countdownTimer )
			self.SetForegroundColour( self.foregrounds[0] )
			self.SetBackgroundColour( self.backgrounds[0] )
			self.lapCounterCycle = race.lapCounterCycle or None
			if race.isUnstarted():
				if all( race.getNumLapsFromCategory(category) for category in race.getCategories(startWaveOnly=True) ):
					lapCounter = [(u'{}'.format(self.getLapCycle(category)),False) for category in race.getCategories(startWaveOnly=True)]
				else:
					lapCounter = [(u'{} min'.format(race.minutes),False)] + [(u'{}'.format(self.getLapCycle(category)),False)
						for category in race.getCategories(startWaveOnly=True) if race.getNumLapsFromCategory(category)]
				self.SetLabels( lapCounter )
			elif race.isFinished():
				self.SetLabels()
		else:
			self.SetLabels()
		
		self.Refresh()
	
if __name__ == '__main__':
	app = wx.App(False)
	
	Model.setRace( Model.Race() )
	model = Model.getRace()
	model._populate()
	
	displayWidth, displayHeight = wx.GetDisplaySize()
	mainWin = wx.Frame(None,title="LapCounter", size=(displayWidth/2,displayHeight/2))
	lapCounter = LapCounter( mainWin, labels=(('17',False), ('15',True)) )
	lapCounter.refresh()
	
	mainWin.Show()
	
	for j, i in enumerate(xrange(0,40,4)):
		wx.CallLater( 4000*i, lambda a=17-j, b=15-j, c=11-j, d=7-j: lapCounter.SetLabels( (
			('{}'.format(a), True),
			('{}'.format(b), False),
			('{}'.format(c), False),
			('{}'.format(d), False),
		)) )
		wx.CallLater( 6000*i, lambda a=17-j, b=15-j, c=11-j, d=7-j: lapCounter.SetLabels( (
			('{}'.format(a), False),
			('{}'.format(b), True),
			('{}'.format(c), False),
			('{}'.format(d), False),
		)) )
		wx.CallLater( 8000*i, lambda a=17-j, b=15-j, c=11-j, d=7-j: lapCounter.SetLabels( (
			('{}'.format(a), False),
			('{}'.format(b), False),
			('{}'.format(c), True),
			('{}'.format(d), True),
		)) )
	
	app.MainLoop()
