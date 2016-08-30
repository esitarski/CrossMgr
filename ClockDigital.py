import wx
import datetime

class ClockDigital(wx.PyControl):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="ClockDigital", checkFunc=None ):
		"""
		Default class constructor.

		@param parent: Parent window. Must not be None.
		@param id: StatusBar identifier. A value of -1 indicates a default value.
		@param pos: StatusBar position. If the position (-1, -1) is specified
					then a default position is chosen.
		@param style: not used
		@param validator: Window validator.
		@param name: Window name.
		"""

		wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)
		
		self.timer = wx.Timer( self )
		self.Bind( wx.EVT_TIMER, self.onTimer )
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
		self.initialSize = size
		
		self.checkFunc = checkFunc if checkFunc else lambda: True
		self.tCur = datetime.datetime.now()
		wx.CallAfter( self.onTimer )
	
	def DoGetBestSize(self):
		return wx.Size(100, 20) if self.initialSize is wx.DefaultSize else self.initialSize

	def SetForegroundColour(self, colour):
		wx.PyControl.SetForegroundColour(self, colour)
		self.Refresh()

	def SetBackgroundColour(self, colour):
		wx.PyControl.SetBackgroundColour(self, colour)
		self.Refresh()
		
	def GetDefaultAttributes(self):
		return wx.StaticText.GetClassDefaultAttributes()

	def ShouldInheritColours(self):
		return True

	def onTimer( self, event=None):
		if not self.timer.IsRunning():
			self.tCur = datetime.datetime.now()
			self.Refresh()
			if self.checkFunc():
				self.timer.Start( 1001 - datetime.datetime.now().microsecond//1000, True )
	
	def Start( self ):
		self.onTimer()
	
	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def Draw(self, dc):
		dc.Clear()
		
		borderRatio = 0.08
		workRatio = (1.0 - borderRatio)
		
		t = self.tCur
		
		size = self.GetClientSize()
		width = size.width
		height = size.height
		
		tStr = t.strftime('%H:%M:%S')
		fontSize = int(height * workRatio)
		font = wx.FontFromPixelSize(
			(0,fontSize),
			wx.FONTFAMILY_SWISS,
			wx.FONTSTYLE_NORMAL,
			wx.FONTWEIGHT_NORMAL,
		)
		dc.SetFont( font )
		tWidth, tHeight = dc.GetTextExtent( tStr )
		if tWidth > width*workRatio:
			fontSize = int( fontSize * width*workRatio / tWidth )
			font = wx.FontFromPixelSize(
				(0,fontSize),
				wx.FONTFAMILY_SWISS,
				wx.FONTSTYLE_NORMAL,
				wx.FONTWEIGHT_NORMAL,
			)
			dc.SetFont( font )
			tWidth, tHeight = dc.GetTextExtent( tStr )
		dc.DrawText( tStr, (width-tWidth)//2, (height-tHeight)//2 )
		
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="ClockDigital", size=(600,400))
	ClockDigital = ClockDigital(mainWin)
	mainWin.Show()
	app.MainLoop()
