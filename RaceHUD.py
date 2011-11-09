import wx
import random
import math
import sys
import bisect
import Utils
import os

def lighterColour( c ):
	rgb = c.Get( False )
	return wx.Colour( *[int(v + (255 - v) * 0.6) for v in rgb] )
		
class RaceHUD(wx.PyControl):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="RaceHUD"):
		"""
		Default class constructor.
		"""
		wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)
		self.SetBackgroundColour(wx.WHITE)
		self.lapTimes = None	# Last time is red lantern.
		self.leader = None
		self.nowTime = None
		self.getNowTimeCallback = None
		
		# self.colour = wx.Colour(0, 200, 0)
		self.colour = wx.Colour(0, 191, 255)
		self.lighterColour = lighterColour( self.colour )

		self.checkeredFlag = wx.Bitmap(os.path.join(Utils.getImageFolder(), 'CheckeredFlag.png'), wx.BITMAP_TYPE_PNG)
		self.broom = wx.Bitmap(os.path.join(Utils.getImageFolder(), 'Broom.png'), wx.BITMAP_TYPE_PNG)
		self.bell = wx.Bitmap(os.path.join(Utils.getImageFolder(), 'LittleBell.png'), wx.BITMAP_TYPE_PNG)
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)

	def DoGetBestSize(self):
		return wx.Size(128, 64)

	def SetForegroundColour(self, colour):
		wx.PyControl.SetForegroundColour(self, colour)
		self.Refresh()

	def SetBackgroundColour(self, colour):
		wx.PyControl.SetBackgroundColour(self, colour)
		self.Refresh()
		
	def GetDefaultAttributes(self):
		"""
		Overridden base class virtual.  By default we should use
		the same font/colour attributes as the native wx.StaticText.
		"""
		return wx.StaticText.GetClassDefaultAttributes()

	def ShouldInheritColours(self):
		"""
		Overridden base class virtual.  If the parent has non-default
		colours then we want this control to inherit them.
		"""
		return True

	def SetData( self, lapTimes = None, leader = None, nowTime = None ):
		self.lapTimes = lapTimes if lapTimes and len(lapTimes) >= 2 and lapTimes[-1] >= lapTimes[-2] else None
		self.leader = leader
		self.nowTime = nowTime
		self.Refresh()
	
	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
	
	def getRiderLap( self, event ):
		x, y = event.GetPositionTuple()
		y -= self.barHeight
		x -= self.labelsWidth
		iRider = int(y / self.barHeight)
		if not 0 <= iRider < len(self.data):
			return None, None

		iLap = bisect.bisect_left( self.data[iRider], x / self.xFactor )
		if not 1 <= iLap < len(self.data[iRider]):
			return iRider, None
			
		return iRider, iLap
	
	def Draw(self, dc):
		size = self.GetClientSize()
		width = size.width
		height = size.height
		
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		backPen = wx.Pen(backColour, 0)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		if not self.lapTimes or len(self.lapTimes) < 4 or width < 50 or height < 50:
			self.empty = True
			return
		self.empty = False

		legendHeight = max( height / 4, 16 )
		fontLegend = wx.FontFromPixelSize( wx.Size(0,legendHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( fontLegend )
		textWidth, textHeight = dc.GetTextExtent( '1:00:00' )
		broomTimeWidth = textWidth
		
		tickHeight = (height - textHeight * 2) / 2
		if tickHeight < 4:
			self.empty = True
			return
		
		fontRaceTime = wx.FontFromPixelSize( wx.Size(0,tickHeight * 2 * 0.6), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( fontRaceTime )
		textWidth, textHeight = dc.GetTextExtent( str(self.leader) + '0' if self.leader else '0000' )
		textWidth = max( textWidth, int(self.checkeredFlag.GetWidth() * 1.2) )
		
		# Draw the lap legend.
		dy = int(tickHeight * 2 * 0.75)

		labelsWidth = textWidth
		xLeft = labelsWidth
		xRight = width - max( self.broom.GetWidth(), broomTimeWidth )

		xMult = (xRight - xLeft) / float(self.lapTimes[-1])

		# Draw the legend.
		dc.SetFont( fontLegend )
		textWidth, textHeight = dc.GetTextExtent( '0:00:00' )
		hMiddle = textHeight + tickHeight
		dc.DrawLine( xLeft, hMiddle, xRight, hMiddle)
		dc.DrawLine( xLeft, hMiddle - tickHeight, xLeft, hMiddle + tickHeight )
		n = str(len(self.lapTimes)-1)
		textWidth, textHeight = dc.GetTextExtent( n )
		dc.DrawText( n, xLeft - textWidth // 2, hMiddle + tickHeight )
		lapMax = len(self.lapTimes) - 2
		for i, t in enumerate(self.lapTimes):
			x = xLeft + int( t * xMult )
			dc.DrawLine( x, hMiddle - tickHeight, x, hMiddle + tickHeight )
			if t != self.lapTimes[-1]:
				n = str(lapMax - i)
				textWidth, textHeight = dc.GetTextExtent( n )
				dc.DrawText( n, x - textWidth // 2, hMiddle + tickHeight )
		
		# Draw checkered flag
		dc.SetFont( fontLegend )
		t = self.lapTimes[-2]
		tCur = Utils.formatTime( t )
		textWidth, textHeight = dc.GetTextExtent( tCur )
		x = xLeft + int( t * xMult )
		dc.DrawBitmap( self.checkeredFlag, x - self.checkeredFlag.GetWidth() - 1, hMiddle - self.checkeredFlag.GetHeight() // 2, False )
		dc.DrawText( tCur, x - textWidth - textHeight / 8, hMiddle - tickHeight - textHeight )
		
		# Draw broom.
		t = self.lapTimes[-1]
		tCur = Utils.formatTime( t )
		textWidth, textHeight = dc.GetTextExtent( tCur )
		x = xLeft + int( t * xMult )
		dc.DrawBitmap( self.broom, x + 3, hMiddle - self.broom.GetHeight() // 2, False )
		dc.DrawText( tCur, x + textHeight / 8, hMiddle - tickHeight - textHeight )
		
		# Draw the progress bar.
		transparentBrush = wx.Brush( wx.WHITE, style = wx.TRANSPARENT )
		ctx = wx.GraphicsContext_Create(dc)
		ctx.SetPen( wx.Pen(wx.WHITE, 1, style = wx.TRANSPARENT ) )
		dd = int(dy * 0.3)
		
		yCur = int(hMiddle - dy / 2)
		xCur = (self.nowTime * xMult)
		b1 = ctx.CreateLinearGradientBrush(0, yCur, 0, yCur + dd + 1, self.colour, self.lighterColour)
		ctx.SetBrush(b1)
		ctx.DrawRectangle(xLeft, yCur, xCur, dd + 1)
		
		b2 = ctx.CreateLinearGradientBrush(0, yCur + dd, 0, yCur + dy, self.lighterColour, self.colour)
		ctx.SetBrush(b2)
		ctx.DrawRectangle(xLeft, yCur + dd, xCur, dy-dd )
		
		dc.SetPen( wx.Pen(wx.Colour(128,128,128)) )
		dc.SetBrush( wx.TRANSPARENT_BRUSH )
		dc.DrawRectangle( xLeft, hMiddle - dy / 2, xCur, dy )
		dc.SetPen( wx.BLACK_PEN )
		
		# Draw the time to the leader's next lap (or the broom if the race is over).
		dc.SetFont( fontRaceTime )
		nextLap = bisect.bisect_left( self.lapTimes, self.nowTime )
		if nextLap < len(self.lapTimes):
			t = self.lapTimes[nextLap] - self.nowTime
			tToLeader = t
			tCur = Utils.formatTime( t )
			if tCur[0] == '0':
				tCur = tCur[1:]
			textWidth, textHeight = dc.GetTextExtent( tCur )
			t = self.nowTime
			x = xLeft + int( t * xMult )
			x = max( x - textWidth - textHeight / 8, xLeft + 2 )
			dc.DrawText( tCur, x, hMiddle - textHeight / 2 )
			
			if	(nextLap == len(self.lapTimes)-2 and tToLeader > 15) or \
				(nextLap == len(self.lapTimes)-3 and tToLeader < 15):
				x -= self.bell.GetWidth() + textHeight / 8
				if x >= xLeft:
					dc.DrawBitmap( self.bell, x, hMiddle - self.bell.GetHeight() / 2)
		
		# Draw the leader.
		if self.leader is not None:
			leaderText = str(self.leader)
			textWidth, textHeight = dc.GetTextExtent( leaderText )
			dc.DrawText( leaderText, xLeft - textWidth - textHeight / 8, hMiddle - textHeight / 2 )
					
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	import datetime
	
	def GetData():
		return [t for t in xrange(0, 300, 32)]

	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="RaceHUD", size=(800,200))
	RaceHUD = RaceHUD(mainWin)
	
	random.seed( 10 )
	t = 55*60
	tVar = t * 0.15
	data = GetData()
	RaceHUD.SetData( data, leader = 20, nowTime = data[3] - 13.0 - 30)

	startTime = datetime.datetime.now()
	def updateTime():
		nowTime = (datetime.datetime.now() - startTime).total_seconds()
		RaceHUD.SetData( data, leader = 20, nowTime = nowTime )
		if nowTime < data[-1]:
			wx.CallLater( 1000, updateTime )

	wx.CallLater( 1000, updateTime )
	mainWin.Show()
	app.MainLoop()
