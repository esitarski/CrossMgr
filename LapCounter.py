import wx

class LapCounter( wx.Panel ):
	millis = 500
	
	def __init__( self, parent, labels=[], id=wx.ID_ANY, size=(640,480), style=0 ):
		super(LapCounter, self).__init__( parent, id, size=size, style=style )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		self.labels = labels
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.Bind( wx.EVT_SIZE, self.OnSize )
		self.Bind( wx.EVT_RIGHT_UP, self.OnConfigure )
		self.timer = wx.Timer( self )
		self.Bind( wx.EVT_TIMER, self.OnTimer )
		self.timer.Start( self.millis )
		self.flashOn = False
		
		self.backgroundColour = wx.BLACK
		self.foregroundColour = wx.GREEN
		
		self.SetBackgroundColour( self.backgroundColour )
		self.SetForegroundColour( self.foregroundColour )

	def OnConfigure( self, event ):
		pass
		
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
