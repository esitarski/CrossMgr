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
	
def rescaleBitmap( b, s ):
	i = b.ConvertToImage()
	i = i.Scale( i.GetWidth() * s, i.GetHeight() * s, wx.IMAGE_QUALITY_HIGH )
	return i.ConvertToBitmap()
		
class RaceHUD(wx.PyControl):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="RaceHUD"):
		"""
		Default class constructor.
		"""
		wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)
		self.SetBackgroundColour(wx.WHITE)
		self.raceTimes = None	# Last time is red lantern.
		self.leader = None
		self.nowTime = None
		self.getNowTimeCallback = None
		
		# self.colour = wx.Colour(0, 200, 0)
		self.colour = wx.Colour(0, 191, 255)
		self.lighterColour = lighterColour( self.colour )

		self.checkeredFlag = wx.Bitmap(os.path.join(Utils.getImageFolder(), 'CheckeredFlag.png'), wx.BITMAP_TYPE_PNG)
		self.broom = wx.Bitmap(os.path.join(Utils.getImageFolder(), 'Broom.png'), wx.BITMAP_TYPE_PNG)
		self.bell = wx.Bitmap(os.path.join(Utils.getImageFolder(), 'LittleBell.png'), wx.BITMAP_TYPE_PNG)

		#for a in ['checkeredFlag', 'broom', 'bell']:
		#	setattr( self, a, rescaleBitmap(getattr(self, a), 0.75) )
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)

	def DoGetBestSize(self):
		return wx.Size(128, 100)

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

	def SetData( self, raceTimes = None, leader = None, nowTime = None ):
		self.raceTimes = raceTimes if raceTimes and len(raceTimes[0]) >= 2 and raceTimes[0][-1] >= raceTimes[0][-2] else None
		self.leader = leader
		self.nowTime = nowTime
		
		if self.raceTimes:
			self.raceTimes = self.raceTimes[:3]
		if self.leader:
			self.leader = self.leader[:3]
		self.Refresh()
	
	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
	
	def Draw(self, dc):
		size = self.GetClientSize()
		width = size.width
		height = size.height
		
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		backPen = wx.Pen(backColour, 0)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		if not self.raceTimes or not self.raceTimes[0] or len(self.raceTimes[0]) < 4 or width < 50 or height < 30:
			self.empty = True
			return
		self.empty = False
		
		hudHeight = min( height / len(self.raceTimes), 80 )

		legendHeight = max( hudHeight / 4, 10 )
		fontLegend = wx.FontFromPixelSize( wx.Size(0,legendHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( fontLegend )
		textWidth, textHeight = dc.GetTextExtent( '1:00:00' )
		broomTimeWidth = textWidth
		
		tickHeight = (hudHeight - textHeight * 2) / 2
		if tickHeight < 2:
			self.empty = True
			return
		
		raceTimeHeight = tickHeight * 2 * 0.6
		fontRaceTime = wx.FontFromPixelSize( wx.Size(0,raceTimeHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( fontRaceTime )
		textWidth, textHeight = dc.GetTextExtent( '0' )
		textWidth = max( dc.GetTextExtent(str(ldr))[0] for ldr in self.leader )
		textWidth = max( textWidth, int(self.checkeredFlag.GetWidth() * 1.2) )
		textWidth += dc.GetTextExtent('  ')[0]
		
		dy = int(tickHeight * 2 * 0.75)

		labelsWidth = textWidth
		xLeft = labelsWidth
		xRight = width - max( self.broom.GetWidth(), broomTimeWidth )

		xMult = (xRight - xLeft) / float(max(rt[-1] if rt else 0 for rt in self.raceTimes))

		yTop = 0
		for leader, raceTimes in zip(self.leader, self.raceTimes):
			if not raceTimes:
				continue
		
			# Draw the legend.
			dc.SetFont( fontLegend )
			textWidth, textHeight = dc.GetTextExtent( '0:00:00' )
			hMiddle = textHeight + tickHeight
			dc.DrawLine( xLeft, yTop + hMiddle, xLeft + raceTimes[-1] * xMult, yTop + hMiddle )
			dc.DrawLine( xLeft, yTop + hMiddle - tickHeight, xLeft, yTop + hMiddle + tickHeight )

			lapMax = len(raceTimes) - 2
			for i, t in enumerate(raceTimes):
				x = xLeft + int( t * xMult )
				dc.DrawLine( x, yTop + hMiddle - tickHeight, x, yTop + hMiddle + tickHeight )
				if t != raceTimes[-1]:
					n = str(lapMax - i)
					textWidth, textHeight = dc.GetTextExtent( n )
					dc.DrawText( n, x - textWidth // 2, yTop + hMiddle + tickHeight )
		
			# Draw the progress bar.
			transparentBrush = wx.Brush( wx.WHITE, style = wx.TRANSPARENT )
			ctx = wx.GraphicsContext_Create(dc)
			ctx.SetPen( wx.Pen(wx.WHITE, 1, style = wx.TRANSPARENT ) )
			dd = int(dy * 0.3)
			
			yCur = int(hMiddle - dy / 2)
			xCur = ((self.nowTime - raceTimes[0]) * xMult)
			xStart = raceTimes[0] * xMult + xLeft
			b1 = ctx.CreateLinearGradientBrush( 0, yTop + yCur,      0, yTop + yCur + dd + 1, self.colour,        self.lighterColour )
			b2 = ctx.CreateLinearGradientBrush( 0, yTop + yCur + dd, 0, yTop + yCur + dy    , self.lighterColour, self.colour )
			ctx.SetBrush(b1)
			ctx.DrawRectangle(xStart, yTop + yCur, xCur, dd + 1)
			
			ctx.SetBrush(b2)
			ctx.DrawRectangle(xStart, yTop + yCur + dd, xCur, dy-dd )
			
			# Draw an outline around the progress bar.
			ctx.SetPen( wx.Pen(wx.Colour(128,128,128)) )
			ctx.SetBrush( wx.TRANSPARENT_BRUSH )
			ctx.DrawRectangle( xStart, yTop + hMiddle - dy / 2, xCur, dy )
			
			# Draw checkered flag
			dc.SetFont( fontLegend )
			t = raceTimes[-2]
			tCur = Utils.formatTime( t )
			textWidth, textHeight = dc.GetTextExtent( tCur )
			x = xLeft + int( t * xMult )
			dc.DrawBitmap( self.checkeredFlag, x - self.checkeredFlag.GetWidth() - 1, yTop + hMiddle - self.checkeredFlag.GetHeight() // 2, False )
			dc.DrawText( tCur, x - textWidth - textHeight / 8, yTop + hMiddle - tickHeight - textHeight )
			
			# Draw broom.
			t = raceTimes[-1]
			tCur = Utils.formatTime( t )
			textWidth, textHeight = dc.GetTextExtent( tCur )
			x = xLeft + int( t * xMult )
			dc.DrawBitmap( self.broom, x + 3, yTop + hMiddle - self.broom.GetHeight() // 2, False )
			dc.DrawText( tCur, x + textHeight / 8, yTop + hMiddle - tickHeight - textHeight )
			
			# Draw indicator for the finish time.
			iRadius = dy / 3
			x = xLeft + int( raceTimes[-2] * xMult )
			ctx.SetBrush( wx.Brush(wx.Colour(0,255,0)) )
			ctx.DrawEllipse( x - iRadius / 2, yTop + hMiddle - tickHeight - iRadius/4, iRadius, iRadius )
			
			# Draw indicator for the last rider on course.
			x = xLeft + int( raceTimes[-1] * xMult )
			ctx.SetBrush( wx.Brush(wx.Colour(255,0,0)) )
			ctx.DrawEllipse( x - iRadius / 2, yTop + hMiddle - tickHeight - iRadius/4, iRadius, iRadius )
			
			ctx.SetPen( wx.BLACK_PEN )
			
			# Draw the time to the leader's next lap (or the broom if the race is over).
			dc.SetFont( fontRaceTime )
			nextLap = bisect.bisect_left( raceTimes, self.nowTime )
			if nextLap < len(raceTimes):
				t = raceTimes[nextLap] - self.nowTime
				tToLeader = t
				tCur = Utils.formatTime( t )
				if tCur[0] == '0':
					tCur = tCur[1:]
				textWidth, textHeight = dc.GetTextExtent( tCur )
				t = self.nowTime
				x = xLeft + int( t * xMult )
				x = max( x - textWidth - textHeight / 8, xLeft + 2 )
				dc.DrawText( tCur, x, yTop + hMiddle - textHeight / 2 )
				
				if	(nextLap == len(raceTimes)-2 and tToLeader > 15) or \
					(nextLap == len(raceTimes)-3 and tToLeader < 15):
					x -= self.bell.GetWidth() + textHeight / 8
					if x >= xLeft:
						dc.DrawBitmap( self.bell, x, yTop + hMiddle - self.bell.GetHeight() / 2)
			
			# Draw the leader.
			if leader is not None:
				leaderText = str(leader)
				dc.SetFont( fontLegend if legendHeight > raceTimeHeight else fontRaceTime )
				textWidth, textHeight = dc.GetTextExtent( leaderText )
				dc.DrawText( leaderText, xLeft - textWidth - textHeight / 8, yTop + hMiddle - textHeight / 2 )
				
			yTop += hudHeight
					
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	import datetime
	
	def GetData():
		return [
			[t for t in xrange(0, 300, 32)],
			[t for t in xrange(0, 300, 44)],
		]

	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="RaceHUD", size=(800,200))
	RaceHUD = RaceHUD(mainWin)
	
	random.seed( 10 )
	t = 55*60
	tVar = t * 0.15
	data = GetData()
	RaceHUD.SetData( data, leader = [20,120], nowTime = data[0][3] - 13.0 - 30)

	startTime = datetime.datetime.now() - datetime.timedelta( seconds = 20 )
	def updateTime():
		nowTime = (datetime.datetime.now() - startTime).total_seconds()
		RaceHUD.SetData( data, leader = [20,120], nowTime = nowTime )
		if nowTime < data[-1]:
			wx.CallLater( 1000, updateTime )

	wx.CallLater( 1000, updateTime )
	mainWin.Show()
	app.MainLoop()
