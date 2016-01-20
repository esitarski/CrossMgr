import wx
import wx.lib.colourselect as  csel
import wx.lib.intctrl as intctrl
import math
import datetime
import Model
import Utils

class LapCounterOptions( wx.Dialog ):
	def __init__( self, parent, lapCounter, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, _("Lap Counter Options"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
		
		self.lapCounter = lapCounter
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		vs.Add( wx.StaticText(self, label=_('Lap Counter Options') + u':'), flag=wx.LEFT|wx.TOP|wx.RIGHT, border=8 )

		fgs = wx.FlexGridSizer( cols=2, vgap=4, hgap=4 )
		
		fgs.Add( wx.StaticText(self, label=_('Type') + u':'), flag=wx.ALIGN_CENTRE_VERTICAL )
		self.counterType = wx.Choice(self, choices=(_('Lap Counter'), _('Countdown Timer')))
		self.counterType.SetSelection( 0 if not self.lapCounter.countdownTimer else 1 )
		fgs.Add( self.counterType )
		
		fgs.Add( wx.StaticText(self, label=_('Foreground') + u':'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.foreground = csel.ColourSelect(self, colour=lapCounter.GetForegroundColour(), size=(100,-1))
		fgs.Add( self.foreground )
		
		fgs.Add( wx.StaticText(self, label=_('Background') + u':'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.background = csel.ColourSelect(self, colour=lapCounter.GetBackgroundColour(), size=(100,-1))
		fgs.Add( self.background )
		
		fgs.Add( wx.StaticText(self, label=_('Lap Cycle') + u':'), flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALIGN_RIGHT )
		self.lapCounterCycle = intctrl.IntCtrl(self, value=lapCounter.lapCounterCycle, min=0, max=None, limited=True, allow_none=True, )
		fgs.Add( self.lapCounterCycle )
		
		vs.Add( fgs, flag=wx.ALL, border=16 )
		
		vs.Add( wx.StaticText(self, label=_("Seconds before Leader's ETA to change Lap Counter") + u':'), flag=wx.LEFT|wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=8 )
		self.slider = wx.Slider(
			self,
			value=Model.race.secondsBeforeLeaderToFlipLapCounter if Model.race else 5, minValue=1, maxValue=180,
			size=(360, -1), 
			style = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS 
		)
		self.slider.SetTickFreq(5, 1)
		vs.Add( self.slider, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=8 )
		
		buttonSizer = wx.StdDialogButtonSizer()
		buttonSizer.AddButton( wx.Button(self, wx.ID_OK) )
		buttonSizer.AddButton( wx.Button(self, wx.ID_CANCEL) )
		buttonSizer.Realize()
		
		vs.Add( buttonSizer, flag=wx.ALL, border=16 )
		
		self.SetSizerAndFit( vs )
		
	def OnOK( self, event ):
		self.EndModal( wx.ID_OK )
		
	def OnCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

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
		self.Bind( wx.EVT_RIGHT_UP, self.OnOptions )
		self.timer = wx.Timer( self )
		self.Bind( wx.EVT_TIMER, self.OnTimer )
		self.timer.Start( self.millis )
		
		self.flashOn = False
		self.font = None
		self.fontSize = -1
		
		self.SetCursor( wx.StockCursor(wx.CURSOR_RIGHT_BUTTON) )
		self.SetBackgroundColour( wx.BLACK )
		self.SetForegroundColour( wx.GREEN )

	def OnOptions( self, event ):
		d = LapCounterOptions( self, self )
		if d.ShowModal() == wx.ID_OK:
			
			self.SetForegroundColour( d.foreground.GetColour() )
			self.SetBackgroundColour( d.background.GetColour() )
			self.SetCountdownTimer( d.counterType.GetSelection() == 1 )
			self.lapCounterCycle = d.lapCounterCycle.GetValue() or None
			
			race = Model.race
			if race:
				race.lapCounterForeground = self.GetForegroundColour().GetAsString(wx.C2S_HTML_SYNTAX)
				race.lapCounterBackground = self.GetBackgroundColour().GetAsString(wx.C2S_HTML_SYNTAX)
				race.lapCounterBackground = self.GetBackgroundColour().GetAsString(wx.C2S_HTML_SYNTAX)
				race.lapCounterCycle = self.lapCounterCycle
				race.countdownTimer = self.countdownTimer
				race.setChanged()
			wx.CallAfter( self.Refresh )
		
		d.Destroy()
		
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
		self.font = wx.FontFromPixelSize( wx.Size(0,lineHeight), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD )
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
	
	def OnPaint( self, event ):
		dc = wx.AutoBufferedPaintDC( self )
		dc.SetBackground( wx.Brush(self.GetBackgroundColour(), wx.SOLID) )
		dc.SetTextForeground( self.GetForegroundColour() )
		dc.Clear()
		
		width, height = self.GetSizeTuple()
		border = 0

		if self.countdownTimer:
			label = self.GetCountdownTime()
			if not label:
				return
			lineHeight = height - border*2
			dc.SetFont( wx.FontFromPixelSize( wx.Size(0,lineHeight), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD ) )
			sizeLabel = '000000000:00:00'[-len(label):]
			w, h = dc.GetTextExtent(sizeLabel)
			if w > width-8:
				lineHeight *= float(width-8) / float(w)
			dc.SetFont( wx.FontFromPixelSize( wx.Size(0,lineHeight), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD ) )
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
			return u'{}'.format(int(label.strip()) % self.lapCounterCycle)
		
		if len(self.labels) <= 2:
			lineHeight = (height - border*2) // len(self.labels)
			#lineHeight *= (1.4 if len(self.labels) == 1 else 1)
			dc.SetFont( self.GetFont(lineHeight) )
			
			maxWidth = max( dc.GetTextExtent(getCycleLap(label))[0] for label, flash in self.labels ) if self.labels else 0
			if maxWidth > width - border*2:
				lineHeight = int( lineHeight * float(width - border*2) / float(maxWidth) )
				dc.SetFont( self.GetFont(lineHeight) )
				maxWidth = max( dc.GetTextExtent(label)[0] for label, flash in self.labels ) if self.labels else 0
			
			xRight = width - (width - maxWidth) // 2
			yTop = (height - (lineHeight * len(self.labels))) // 2
			for label, flash in self.labels:
				label = getCycleLap(label)
				if not flash or self.flashOn:
					dc.DrawText( label, xRight - dc.GetTextExtent(label)[0], yTop )
				yTop += lineHeight
		else:
			lineHeight = (height - border*2) // 2
			width /= 2
			dc.SetFont( self.GetFont(lineHeight) )
			
			maxWidth = max( dc.GetTextExtent(getCycleLap(label))[0] for label, flash in self.labels ) if self.labels else 0
			if maxWidth > width - border*2:
				lineHeight = int( lineHeight * float(width - border*2) / float(maxWidth) )
				dc.SetFont( self.GetFont(lineHeight) )
				maxWidth = max( dc.GetTextExtent(getCycleLap(label))[0] for label, flash in self.labels ) if self.labels else 0
			
			xRight = width - (width - maxWidth) // 2
			for i in xrange(0, 4, 2):
				yTop = (height - (lineHeight * 2)) // 2
				for label, flash in self.labels[i:i+2]:
					label = getCycleLap(label)
					if not flash or self.flashOn:
						dc.DrawText( label, xRight - dc.GetTextExtent(label)[0], yTop )
					yTop += lineHeight
				xRight += width
	
	def commit( self ):
		pass
		
	def getLapCycle( self, category ):
		lap = category.getNumLaps()
		if not self.lapCounterCycle:
			return lap
		return lap % self.lapCounterCycle
					
	def refresh( self ):
		race = Model.race
		if race:
			self.SetCountdownTimer( race.countdownTimer )
			self.SetForegroundColour( Utils.colorFromStr(race.lapCounterForeground) )
			self.SetBackgroundColour( Utils.colorFromStr(race.lapCounterBackground) )
			self.lapCounterCycle = race.lapCounterCycle or None
			if race.isUnstarted():
				
				if all( category.getNumLaps() for category in race.getCategories(startWaveOnly=True) ):
					lapCounter = [(u'{}'.format(self.getLapCycle(category)),False) for category in race.getCategories(startWaveOnly=True)]
				else:
					lapCounter = [(u'{} min'.format(race.minutes),False)] + [(u'{}'.format(self.getLapCycle(category)),False)
						for category in race.getCategories(startWaveOnly=True) if category.getNumLaps()]
				self.SetLabels( lapCounter )
			elif race.isFinished():
				self.SetLabels()
		else:
			self.SetLabels()
		
		self.Refresh()
	
if __name__ == '__main__':
	app = wx.App(False)
	
	displayWidth, displayHeight = wx.GetDisplaySize()
	mainWin = wx.Frame(None,title="LapCounter", size=(displayWidth/2,displayHeight/2))
	lapCounter = LapCounter( mainWin, labels=(('17',False), ('15',True)) )
	lapCounter.SetBackgroundColour( wx.BLACK )
	#lapCounter.SetForegroundColour( wx.GREEN )
	lapCounter.SetForegroundColour( wx.WHITE )
	
	mainWin.Show()
	
	for j, i in enumerate(xrange(0,40,4)):
		wx.CallLater( 4000*i, lambda a=17-j, b=15-j: lapCounter.SetLabels( (('{}'.format(a), True), ('{}'.format(b), False)) ) )
		wx.CallLater( 6000*i, lambda a=17-j, b=15-j : lapCounter.SetLabels( (('{}'.format(a), False), ('{}'.format(b), False)) ) )
		wx.CallLater( 8000*i, lambda a=16-j, b=14-j : lapCounter.SetLabels( (('{}'.format(a), False), ('{}'.format(b), True)) ) )
	
	app.MainLoop()
