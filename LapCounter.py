import wx
import  wx.lib.colourselect as  csel
import Utils

class LapCounterOptions( wx.Dialog ):
	def __init__( self, parent, lapCounter, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, _("Lap Counter Options"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
		
		self.lapCounter = lapCounter
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		vs.Add( wx.StaticText(self, label=_('Lap Counter Options') + u':'), flag=wx.LEFT|wx.TOP|wx.RIGHT, border=8 )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( wx.StaticText(self, label=_('Foreground') + u':'), flag=wx.RIGHT, border=4 )
		self.foreground = csel.ColourSelect(self, colour=lapCounter.GetForegroundColour(), size=(100,-1))
		hs.Add( self.foreground )
		vs.Add( hs, flag=wx.ALL, border=16 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( wx.StaticText(self, label=_('Background') + u':'), flag=wx.RIGHT, border=4 )
		self.background = csel.ColourSelect(self, colour=lapCounter.GetBackgroundColour(), size=(100,-1))
		hs.Add( self.background )
		vs.Add( hs, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=16 )
		
		vs.Add( wx.StaticText(self, label=_("Seconds before Leader's ETA to flip Lap Counter") + u':'), flag=wx.LEFT|wx.TOP|wx.RIGHT, border=8 )
		self.slider = wx.Slider(
			self,
			value=25, minValue=1, maxValue=180,
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
	millis = 500
	
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
		
		self.backgroundColour = wx.BLACK
		self.foregroundColour = wx.GREEN
		
		self.SetBackgroundColour( self.backgroundColour )
		self.SetForegroundColour( self.foregroundColour )

	def OnOptions( self, event ):
		d = LapCounterOptions( self, self )
		if d.ShowModal() == wx.ID_OK:
			secondsBeforeLeaderETAToFlipLapCounter = d.slider.GetValue()
			try:
				Utils.mainWin.secondsBeforeLeaderETAToFlipLapCounter = secondsBeforeLeaderETAToFlipLapCounter
			except:
				pass
			self.backgroundColour = d.foreground.GetColour()
			self.foregroundColour = d.background.GetColour()
			
			self.SetForegroundColour( self.backgroundColour )
			self.SetBackgroundColour( self.foregroundColour )
			wx.CallAfter( self.Refresh )
		
		d.Destroy()
		
	def OnTimer( self, event ):
		self.flashOn = not self.flashOn
		if any( flash for label, flash in self.labels ):
			self.Refresh()

	def SetLabels( self, labels ):
		''' labels is of the format [(label1, flash), (label2, flash)] '''
		if self.labels == labels:
			return
		
		self.labels = labels[:4]
		if not any( flash for label, flash in self.labels ):
			self.timer.Stop()
			self.flashOn = True
		elif not self.timer.IsRunning():
			self.timer.Start( self.millis )
		self.Refresh()
	
	def OnSize( self, event ):
		self.Refresh()
	
	def GetFont( self, lineHeight ):
		return wx.FontFromPixelSize( wx.Size(0,lineHeight), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD )
	
	def OnPaint( self, event ):
		dc = wx.AutoBufferedPaintDC( self )
		dc.SetBackground( wx.Brush(self.GetBackgroundColour(), wx.SOLID) )
		dc.SetTextForeground( self.GetForegroundColour() )
		dc.Clear()
		
		width, height = self.GetSizeTuple()
		border = 4
		
		if len(self.labels) <= 2:
			lineHeight = (height - border*2) // max(len(self.labels), 1)
			dc.SetFont( self.GetFont(lineHeight) )
			
			maxWidth = max( dc.GetTextExtent(label)[0] for label, flash in self.labels ) if self.labels else 0
			if maxWidth > width - border*2:
				lineHeight *= int( float(width - border*2) / float(maxWidth) )
				dc.SetFont( self.GetFont(lineHeight) )
				maxWidth = max( dc.GetTextExtent(label)[0] for label, flash in self.labels ) if self.labels else 0
			
			xRight = width - (width - maxWidth) // 2
			yTop = (height - (lineHeight * len(self.labels))) // 2
			for label, flash in self.labels:
				if not(flash and self.flashOn):
					dc.DrawText( label, xRight - dc.GetTextExtent(label)[0], yTop )
				yTop += lineHeight
		else:
			lineHeight = (height - border*2) // 2
			width /= 2
			dc.SetFont( self.GetFont(lineHeight) )
			
			maxWidth = max( dc.GetTextExtent(label)[0] for label, flash in self.labels ) if self.labels else 0
			if maxWidth > width - border*2:
				lineHeight *= int( float(width - border*2) / float(maxWidth) )
				dc.SetFont( self.GetFont(lineHeight) )
				maxWidth = max( dc.GetTextExtent(label)[0] for label, flash in self.labels ) if self.labels else 0
			
			xRight = width - (width - maxWidth) // 2
			for i in xrange(0, 4, 2):
				yTop = (height - (lineHeight * 2)) // 2
				for label, flash in self.labels[i:i+2]:
					if not(flash and self.flashOn):
						dc.DrawText( label, xRight - dc.GetTextExtent(label)[0], yTop )
					yTop += lineHeight
				xRight += width
	
	def commit( self ):
		pass
		
	def refresh( self ):
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
