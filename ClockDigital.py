import wx
from math import modf
import datetime

now = datetime.datetime.now

def formatTime( s ):
	if s < 0:
		sgn = '-'
		s = -s
	else:
		sgn = ''
		
	s = int(s)
	hours, minutes, seconds = s//(60*60), (s//60)%60, s%60
	if hours:
		return '{}{:d}:{:02d}:{:02d}'.format( sgn, hours, minutes, seconds )
	else:
		return '{}{:d}:{:02d}'.format( sgn, minutes, seconds )

class ClockDigital(wx.Control):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="ClockDigital", refTime=None, countDown=False, checkFunc=None ):

		super( ClockDigital, self ).__init__(parent, id, pos, size, style, validator, name)
		
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
		self.refTime = refTime
		self.countDown = countDown
		self.tCur = now()
		wx.CallAfter( self.onTimer )
	
	def DoGetBestSize(self):
		return wx.Size(100, 20) if self.initialSize is wx.DefaultSize else self.initialSize

	def SetForegroundColour(self, colour):
		super(ClockDigital, self).SetForegroundColour(colour)
		self.Refresh()

	def SetBackgroundColour(self, colour):
		super(ClockDigital, self).SetBackgroundColour(colour)
		self.Refresh()
		
	def GetDefaultAttributes(self):
		return wx.StaticText.GetClassDefaultAttributes()

	def ShouldInheritColours(self):
		return True
		
	def SetRefTime( self, refTime ):
		self.refTime = refTime
		self.Refresh()

	def onTimer( self, event=None):
		if not self.timer.IsRunning():
			self.tCur = now()
			self.Refresh()
			if self.checkFunc():
				if self.refTime:
					s = (now() - self.refTime).total_seconds()
					if s <= 0.0:
						millis = int(modf(-s)[0] * 1000.0)
					else:
						millis = 1001 - int(modf(s)[0] * 1000.0)
					self.timer.Start( millis, True )
				else:
					self.timer.Start( 1001 - now().microsecond//1000, True )
	
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
		
		if self.refTime:
			if self.countDown:
				tStr = formatTime( (self.refTime-t).total_seconds() )
			else:
				tStr = formatTime( (t-self.refTime).total_seconds() )
		else:
			tStr = t.strftime('%H:%M:%S')
		
		fontSize = int(height * workRatio)
		font = wx.Font(
			(0,fontSize),
			wx.FONTFAMILY_SWISS,
			wx.FONTSTYLE_NORMAL,
			wx.FONTWEIGHT_NORMAL,
		)
		dc.SetFont( font )
		tWidth, tHeight = dc.GetTextExtent( tStr )
		if tWidth > width*workRatio:
			fontSize = int( fontSize * width*workRatio / tWidth )
			font = wx.Font(
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
	ClockDigital = ClockDigital(mainWin, refTime=now()+datetime.timedelta(seconds=5), countDown=False)
	#ClockDigital = ClockDigital(mainWin)
	mainWin.Show()
	app.MainLoop()
