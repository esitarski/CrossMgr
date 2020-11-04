import wx
import os
import bisect
import random
import Utils

def lighterColour( c ):
	rgb = c.Get( False )
	return wx.Colour( *[int(v + (255 - v) * 0.6) for v in rgb] )
	
def rescaleBitmap( b, s ):
	i = b.ConvertToImage()
	i = i.Scale( i.GetWidth() * s, i.GetHeight() * s, wx.IMAGE_QUALITY_HIGH )
	return i.ConvertToBitmap()
		
class RaceHUD(wx.Control):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name=_("RaceHUD"), lapInfoFunc=None ):
		wx.Control.__init__(self, parent, id, pos, size, style, validator, name)
		self.SetBackgroundColour(wx.WHITE)
		self.raceTimes = None	# Last time is red lantern.
		self.leader = None
		self.nowTime = None
		self.getNowTimeCallback = None
		self.lapInfoFunc = lapInfoFunc
		
		self.resetDimensions()
		
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
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)

	def resetDimensions(self):
		self.xLeft = self.xRight = self.xMult = self.hudHeight = self.iRaceTimesHover = self.iLapHover = None

	def DoGetBestSize(self):
		return wx.Size(128, 100)

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
		
	def SetData( self, raceTimes = None, leader = None, nowTime = None ):
		self.raceTimes = raceTimes if raceTimes and len(raceTimes[0]) >= 2 and raceTimes[0][-1] >= raceTimes[0][-2] else None
		self.leader = leader
		self.nowTime = nowTime
		
		maxRaceTimes = 16
		if self.raceTimes:
			self.raceTimes = self.raceTimes[:maxRaceTimes]
		if self.leader:
			self.leader = self.leader[:maxRaceTimes]
		self.Refresh()
	
	def GetLaps( self ):
		return [max(0,len(rt)-2) for rt in self.raceTimes] if self.raceTimes else []
	
	def OnLeave(self, event):
		if self.iRaceTimesHover is not None:
			self.iRaceTimesHover = None
			self.iLapHover = None
			wx.CallAfter( self.Refresh )
	
	def OnMotion(self, event):
		if not self.lapInfoFunc or not self.raceTimes:
			event.Skip()
			return
		x, y = event.GetX(), event.GetY()
		if self.xLeft is None or x < self.xLeft or self.xRight < x:
			event.Skip()
			return
		
		iRaceTimesHover = None
		iLapHover = None
		yTop = 0
		for i, raceTimes in enumerate(self.raceTimes):
			if not raceTimes:
				continue
			if yTop <= y < yTop + self.hudHeight:
				iRaceTimesHover = i
				break
			yTop += self.hudHeight

		if iRaceTimesHover is None:
			if self.iRaceTimesHover != iRaceTimesHover:
				wx.CallAfter( self.Refresh )
			self.iRaceTimesHover = None
			self.iLapHover = None
			return
		
		iLapHover = (bisect.bisect(self.raceTimes[iRaceTimesHover], (x - self.xLeft) / self.xMult, hi=len(self.raceTimes[iRaceTimesHover])-1) or 1)
		if iLapHover > len(self.raceTimes[iRaceTimesHover]):
			iLapHover = None
		
		if iRaceTimesHover != self.iRaceTimesHover or iLapHover != self.iLapHover:
			self.iRaceTimesHover = iRaceTimesHover
			self.iLapHover = iLapHover
			wx.CallAfter( self.Refresh )
	
	def OnPaint(self, event):
		dc = wx.BufferedPaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		event.Skip()
	
	def Draw(self, dc):
		size = self.GetClientSize()
		width = size.width
		height = size.height
		
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		backPen = wx.Pen(backColour, 0)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		render = wx.RendererNative.Get()
		
		tooSmall = (width < 50 or height < 24)
		
		def drawTooSmall():
			dc.SetPen( wx.BLACK_DASHED_PEN )
			dc.DrawLine( 0, height//2, width, height//2 )
		
		if not self.raceTimes or not self.raceTimes[0] or len(self.raceTimes[0]) < 4 or tooSmall:
			self.empty = True
			if tooSmall:
				drawTooSmall()
			self.resetDimensions()
			return
		self.empty = False
		
		hudHeight = self.hudHeight = min( height / len(self.raceTimes), 80 )

		legendHeight = max( hudHeight / 4, 10 )
		fontLegend = wx.Font( (0,legendHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( fontLegend )
		textWidth, textHeight = dc.GetTextExtent( u'1:00:00' )
		broomTimeWidth = textWidth
		
		tickHeight = (hudHeight - textHeight * 2) / 2
		if tickHeight < 2:
			self.empty = True
			drawTooSmall()
			return
		
		raceTimeHeight = tickHeight * 2 * 0.6
		fontRaceTime = wx.Font( (0,raceTimeHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( fontRaceTime )
		textWidth, textHeight = dc.GetTextExtent( u'0' )
		zeroCharWidth = textWidth
		textWidth = max( dc.GetTextExtent(u'{}'.format(ldr))[0] for ldr in self.leader )
		textWidth = max( textWidth, int(self.checkeredFlag.GetWidth() * 1.2) )
		textWidth += dc.GetTextExtent(u'  ')[0]
		
		dy = int(tickHeight * 2 * 0.75)

		labelsWidth = textWidth
		xLeft = self.xLeft = labelsWidth
		xRight = self.xRight = width - max( self.broom.GetWidth(), broomTimeWidth )
		if xRight - xLeft < 16:
			self.empty = True
			drawTooSmall()
			return

		xMult = self.xMult = (xRight - xLeft) / float(max(rt[-1] if rt else 0 for rt in self.raceTimes))

		yTop = 0
		for iRaceTimes, (leader, raceTimes) in enumerate(zip(self.leader, self.raceTimes)):
			if not raceTimes:
				continue
				
			nowTime = min( (self.nowTime or raceTimes[-1]), raceTimes[-1] )
		
			# Draw the legend.
			dc.SetFont( fontLegend )
			textWidth, textHeight = dc.GetTextExtent( u'0:00:00' )
			hMiddle = textHeight + tickHeight
			dc.DrawLine( xLeft, yTop + hMiddle, xLeft + raceTimes[-1] * xMult, yTop + hMiddle )
			dc.DrawLine( xLeft, yTop + hMiddle - tickHeight, xLeft, yTop + hMiddle + tickHeight )

			lapMax = len(raceTimes) - 2
			xTextRight = 10000000
			for i in range(len(raceTimes)-1, -1, -1):
				t = raceTimes[i]
				x = xLeft + int( t * xMult )
				dc.DrawLine( x, yTop + hMiddle - tickHeight, x, yTop + hMiddle + tickHeight )
				if t != raceTimes[-1]:
					n = '{}'.format(lapMax-i)
					textWidth, textHeight = dc.GetTextExtent( n )
					xTextNew = x - textWidth // 2
					if xTextNew + textWidth <= xTextRight:
						dc.DrawText( n, xTextNew, yTop + hMiddle + tickHeight )
						xTextRight = xTextNew - zeroCharWidth//3
		
			# Draw the progress bar.
			transparentBrush = wx.Brush( wx.WHITE, style = wx.TRANSPARENT )
			ctx = wx.GraphicsContext.Create(dc)
			ctx.SetPen( wx.Pen(wx.WHITE, 1, style = wx.TRANSPARENT ) )
			dd = int(dy * 0.3)
			
			yCur = int(hMiddle - dy / 2)
			xCur = (nowTime - raceTimes[0]) * xMult
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
			nextLap = bisect.bisect_left( raceTimes, nowTime )
			if nextLap < len(raceTimes):
				t = raceTimes[nextLap] - nowTime
				tToLeader = t
				tCur = Utils.formatTime( t )
				if tCur[0] == '0':
					tCur = tCur[1:]
				textWidth, textHeight = dc.GetTextExtent( tCur )
				t = nowTime
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
				leaderText = u'{}'.format(leader)
				dc.SetFont( fontLegend if legendHeight > raceTimeHeight else fontRaceTime )
				textWidth, textHeight = dc.GetTextExtent( leaderText )
				dc.DrawText( leaderText, xLeft - textWidth - textHeight / 8, yTop + hMiddle - textHeight / 2 )
			
			yTop += hudHeight
		
		if self.iRaceTimesHover is not None and self.lapInfoFunc:
			yTop = 0
			for iRaceTimes, (leader, raceTimes) in enumerate(zip(self.leader, self.raceTimes)):
				if not raceTimes:
					continue
				if iRaceTimes == self.iRaceTimesHover:
					tCur, tNext = raceTimes[self.iLapHover-1:self.iLapHover+1]
					info = self.lapInfoFunc( self.iLapHover, len(raceTimes)-2, tCur, tNext, leader )
					hoverLineHeight = min(20, max( 16, hudHeight//len(info) ) )
					fontHover = wx.Font( (0,int(hoverLineHeight * 0.85)), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
					dc.SetFont( fontHover )
					labelHoverWidth = max(dc.GetTextExtent(label)[0] for label, value in info)
					valueHoverWidth = max(dc.GetTextExtent(value)[0] for label, value in info)
					hoverBorderHeight = dc.GetTextExtent(u'  ')[1]//3
					hoverBorderWidth = dc.GetTextExtent(u'  ')[0]
					hoverWidth = labelHoverWidth + valueHoverWidth + dc.GetTextExtent(u' ')[0]
					hoverHeight = hoverLineHeight * len(info)
					xHover = xLeft + int( tCur * xMult ) - hoverWidth
					if xHover < 0:
						xHover = 0
					yHover = yTop + (hudHeight - hoverHeight)//2 - hoverBorderHeight
					if yHover < 0:
						yHover = 0
					elif yHover + hoverHeight + hoverBorderHeight*2 > height:
						yHover = height - hoverHeight + hoverBorderHeight*2
					dc.SetBrush( wx.WHITE_BRUSH )
					render.DrawPushButton( self, dc, (
							xHover - hoverBorderWidth, yHover - hoverBorderHeight,
							hoverWidth + hoverBorderWidth*2, hoverHeight + hoverBorderHeight*2
						), wx.CONTROL_ISDEFAULT )
					for label, value in info:
						dc.DrawText( label, xHover+labelHoverWidth-dc.GetTextExtent(label)[0], yHover )
						dc.DrawText( value, xHover+hoverWidth-valueHoverWidth, yHover )
						yHover += hoverLineHeight
				yTop += hudHeight
			
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	import datetime
	startTime = datetime.datetime.now()
	
	def lapInfoFunc( lap, lapsTotal, tCur, tNext, leader ):
		info = []
		
		if lap > lapsTotal:
			info.append( (_("Last Rider"), (startTime + datetime.timedelta(seconds=tNext)).strftime('%H:%M:%S')) )
			return info		

		tLap = tNext - tCur
		info.append( (_("Lap"), u'{}/{} ({} {})'.format(lap,lapsTotal,lapsTotal-lap, _('to go'))) )
		info.append( (_("Time"), Utils.formatTimeGap(tLap, highPrecision=False)) )
		info.append( (_("Start"), (startTime + datetime.timedelta(seconds=tCur)).strftime('%H:%M:%S')) )
		info.append( (_("End"), (startTime + datetime.timedelta(seconds=tNext)).strftime('%H:%M:%S')) )
		lapDistance = 1.5
		if lapDistance is not None:
			sLap = (lapDistance / tLap) * 60.0*60.0
			info.append( (u'', u'{:.02f} {}'.format(sLap, 'km/h')) )
		return info
	
	multiple = 10
	def GetData():
		return [
			[t for t in range(0, 300*multiple, 32)],
			[t for t in range(0, 300*multiple, 44)],
		]

	app = wx.App(False)
	mainWin = wx.Frame(None,title=_("RaceHUD"), size=(800,200))
	RaceHUD = RaceHUD(mainWin, lapInfoFunc=lapInfoFunc)
	
	random.seed( 10 )
	t = 55*60
	tVar = t * 0.15
	data = GetData()
	RaceHUD.SetData( data, leader = [20,120], nowTime = data[0][3] - 13.0 - 30)

	startTime = datetime.datetime.now() - datetime.timedelta( seconds = 20 )
	def updateTime():
		nowTime = (datetime.datetime.now() - startTime).total_seconds() / 2
		RaceHUD.SetData( data, leader = [20,120], nowTime = nowTime )
		if nowTime < data[-1]:
			wx.CallLater( 1000, updateTime )

	wx.CallLater( 1000, updateTime )
	mainWin.Show()
	app.MainLoop()
