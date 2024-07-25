import wx

class AntennaReads(wx.Control):
	barColors = [
		wx.Colour(114, 147, 203),
		wx.Colour(225, 151,  76),
		wx.Colour(132, 186,  91),
		wx.Colour(144, 103, 167),
		wx.Colour(128, 133, 133),
		wx.Colour(211,  94,  96),
		wx.Colour(171, 104,  87),
		wx.Colour(204, 194,  16),
	]
	
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				antennaReads=None,
				name="AntennaReads" ):

		wx.Control.__init__(self, parent, id, pos, size, style, validator, name)
		self.antennaReads = antennaReads or []
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
		self.SetBackgroundColour(parent.GetBackgroundColour())
		
		self.initialSize = size
	
	def DoGetBestSize(self):
		return wx.Size(100, 16) if self.initialSize is wx.DefaultSize else self.initialSize

	def SetForegroundColour(self, colour):
		wx.Control.SetForegroundColour(self, colour)
		self.Refresh()

	def SetBackgroundColour(self, colour):
		wx.Control.SetBackgroundColour(self, colour)
		self.Refresh()
		
	def GetDefaultAttributes(self):
		return wx.StaticText.GetClassDefaultAttributes()

	def ShouldInheritColours(self):
		return True

	def OnPaint(self, event):
		if self.IsShown():
			dc = wx.BufferedPaintDC( self )
			self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def Set(self, antennaReads=None):
		self.antennaReads = antennaReads or []
		if self.antennaReads:
			total = max( 1.0, sum(self.antennaReads) )
			self.antennaReads = [a/total for a in self.antennaReads]
		self.Refresh()
		
	def Draw(self, dc):
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground(backBrush)
		dc.Clear()

		size = self.GetClientSize()
		
		width, height = size.width, size.height
		
		dc.SetPen( wx.Pen(wx.BLACK, 1) )
		
		xLast = 0
		wCur = 0.0
		for i, a in enumerate(self.antennaReads):
			wCur += width * a
			xCur = int(wCur)
			dc.SetBrush( wx.Brush(self.barColors[i%len(self.barColors)], wx.SOLID) )
			dc.DrawRectangle( xLast, 0, xCur, height )
			xLast = xCur
			
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass

import random
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="AntennaReads", size=(600,400))
	ar = AntennaReads(mainWin)
	
	class Timer(wx.Timer):
		def __init__( self ):
			super( wx.Timer, self ).__init__()
			self.Start( milliseconds=250 )

		def Notify( self ):
			ar.Set( [random.random()*1000.0 for i in range(int(random.random()*5))] )

	t = Timer()
	
	mainWin.Show()
	app.MainLoop()
