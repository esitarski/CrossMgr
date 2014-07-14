import wx
import Utils
import Model
import datetime

from GetResults import GetResults
from bisect import bisect_left
from copy import copy

def GetSituationGaps( category=None, t=None ):
	race = Model.race
	if not race:
		return None
		
	results = GetResults( category, True )
	validRiders = {rr.num for rr in results if rr.raceTimes and len(rr.raceTimes) >= 2}
	if not validRiders:
		return None
	results = [rr for rr in results if rr.num in validRiders]
	
	maxLaps = max( rr.laps for rr in results )
	if t is None:
		t = race.lastRaceTime()
	Finisher = Model.Rider.Finisher
	t = min( t, max(rr.raceTimes[-1] for rr in results) )
	
	leaderRaceTimes = [0.0] + [min(rr.raceTimes[lap] for rr in results if rr.laps >= lap) for lap in xrange(1, maxLaps+1)]
	
	def getInfo( rr, lapsDown ):
		names = []
		try:
			name.append( rr.LastName.upper() )
		except:
			pass
		try:
			name.append( u'{}.'.format(rr.FirstName[0]) )
		except:
			pass
		
		nameStr = (u': ' + u', '.join(names)) if names else u''
		lapsDownStr = u'' if lapsDown == 0 else u' ({})'.format(lapsDown)
		return u''.join([unicode(rr.num), nameStr, lapsDownStr])
	
	def getLapLE( raceTimes, t ):
		lap = bisect_left( raceTimes, t, hi=len(raceTimes)-1 )
		return lap-1 if raceTimes[lap] > t else lap
	
	gaps = []
	for rr in results:
		if rr.raceTimes[-1] < t and (rr.status != Finisher or rr.raceTimes[-1] < leaderRaceTimes[-1]):
			continue
	
		# Find the latest lap time for this rider at time t.
		thisLap = getLapLE( rr.raceTimes, t )
		if thisLap == 0:
			continue
			
		thisTime = rr.raceTimes[thisLap]
		
		# Find the latest lap time for the leader before that time.
		thisLeaderLap = getLapLE( leaderRaceTimes, thisTime )
		thisLeaderTime = leaderRaceTimes[thisLeaderLap]
		
		thisGap = thisTime - thisLeaderTime
		
		nextLap = thisLap + 1
		if nextLap < len(rr.raceTimes):
			nextTime = rr.raceTimes[nextLap]
			nextLeaderLap = getLapLE( leaderRaceTimes, nextTime )
			nextLeaderTime = leaderRaceTimes[nextLeaderLap]
			
			if nextLeaderLap != thisLeaderLap + 1:
				# This rider was lapped on this lap.  Don't project a gap, otherwise the rider will appear to "move up" quickly.
				gap = thisGap
			else:
				nextGap = nextTime - nextLeaderTime
				# Predict the gap give the time.
				gap = thisGap + (nextGap - thisGap) * (t - thisTime) / (nextTime - thisTime)
		else:
			gap = thisGap
		
		gaps.append( [gap, getInfo(rr, thisLeaderLap - thisLap)] )
	
	gaps.sort()
	gapMin = gaps[0][0]
	gaps = [[g[0] - gapMin, g[1]] for g in gaps]
	thisLap = getLapLE(leaderRaceTimes, t)
	
	tCur = t
	tClock = race.startTime.hour*60.0*60.0 + race.startTime.minute*60.0 + race.startTime.second + race.startTime.microsecond/1000000.0 + t
	tETA = leaderRaceTimes[thisLap+1] - t if thisLap+1 != len(leaderRaceTimes) else None
	tAfterLeader = t - leaderRaceTimes[thisLap]
	lap = thisLap + (1 if t > leaderRaceTimes[thisLap] else 0)
	lapsToGo = len(leaderRaceTimes) - lap
	
	title = u''
	if tCur is not None:
		title = u'Race: {}'.format(Utils.formatTime(tCur))
	if tClock is not None:
		if title:
			title += u'   Time of Day: {}'.format(Utils.formatTime(tClock))
	title += u'   Lap: {}   Laps to go: {}'.format(lap, lapsToGo)
	if tETA is not None:
		title += u'   ETA: {}'.format(Utils.formatTime(tETA))
	
	return gaps, tAfterLeader, title
	
class Situation(wx.PyPanel):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER,
				name="GanttChartPanel" ):
		"""
		Default class constructor.
		"""
		wx.PyPanel.__init__(self, parent, id, pos, size, style, name)
		self.SetBackgroundColour(wx.WHITE)
		
		self.gaps = None
		self.tCur = None
		self.tClock = None
		self.tETA = None
		self.tAfterLeader = None
		
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
	def SetData( self, gaps, tAfterLeader=None, title=None ):
		# gaps are of the form: [gapSeconds, text]
		# Expected to be sorted by increasing gapSeconds.
		self.gaps = gaps
		
		self.tAfterLeader = tAfterLeader
		self.title = title
		
		self.Refresh()
		
	def OnPaint( self, event ):
		dc = wx.BufferedPaintDC(self)
		self.Draw(dc)

	def Draw( self, dc ):
		dc = wx.GCDC( dc )
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground( backBrush )
		dc.Clear()
		if not self.gaps:
			return
		
		greyColour = wx.Colour(100,100,100, 64)
		greyPen = wx.Pen( greyColour, 0 )
		greyBrush = wx.Brush( greyColour, wx.SOLID )
		groupTextBrush = wx.Brush( wx.Colour(200,255,200), wx.SOLID )
			
		size = self.GetClientSize()
		width = size.width
		height = size.height

		# Partition the gaps into groups separated by at least one second.
		maxGapSec = 20.0*60.0	# Ignore gaps greater than 20 minutes.
		groups = []
		group = []
		gapPrev = None
		for gap in self.gaps:
			if gap[0] > maxGapSec:
				break
			if gapPrev is None or gap[0] - gapPrev[0] <= 1.0:
				group.append( gap )
			else:
				groups.append( group )
				group = [gap]
			gapPrev = gap
		groups.append( group )
		
		# Add the gap information to each group.
		for i, group in enumerate(groups):
			groupSize = len(group)
			if len(group) > 10:
				group[:] = group[:5] + [[group[5][0], u'...']] + group[-5:]
			if i == 0:
				group.insert( 0, [group[0][0], u'({})'.format(groupSize)] )
			else:
				group.insert( 0, [group[0][0], u'[{}] {} ({})'.format(i, Utils.formatTimeGap(group[0][0]), groupSize)] )
		
		fontHeight = height / 40
		font = wx.FontFromPixelSize( wx.Size(0,fontHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( font )
		spaceWidth = dc.GetTextExtent( u'  ' )[0]
		textBorder = spaceWidth / 2
		
		def GetGroupTextExtent( group ):
			widthMax = 0
			heightMax = 0
			for gap in group:
				tWidth, tHeight = dc.GetTextExtent( gap[1] )
				widthMax = max( widthMax, tWidth )
				heightMax += tHeight
			return widthMax, heightMax
		
		border = min( width, height ) // 30
		lastWidth = GetGroupTextExtent( groups[-1] )[0]
		
		xLeft = border*2
		yTop = border*2 + fontHeight*1.5
		xRight = width - border - lastWidth
		yBottom = height - border
		
		# Draw the title.
		if self.title:
			dc.DrawText( self.title, xLeft, border )
		
		# Draw a direction line.
		dc.SetPen( greyPen )
		dc.SetBrush( greyBrush )
		dc.DrawLine( xLeft - border, yTop, xRight, yTop )
		arrowLength = border * 0.8
		points = [wx.Point(0,0), wx.Point(arrowLength, arrowLength/4), wx.Point(arrowLength, -arrowLength/4)]
		dc.DrawPolygon( points, border/2, yTop )
		
		gapMax = groups[-1][-1][0] - groups[0][0][0]
		xScale = (xRight - xLeft) / (gapMax if gapMax else 1.0)
		
		def drawFinishLine():
			if self.tAfterLeader is None:
				return
			x = xLeft + self.tAfterLeader * xScale
			flWidth = width / 25
			if x - flWidth > width:
				return
			flY = border + fontHeight*1.5
			outlinePen = wx.Pen( wx.Colour(220,220,220), width / 800 )
			dc.SetPen( outlinePen )
			dc.SetBrush( wx.WHITE_BRUSH )
			dc.DrawRectangle( x - flWidth / 2, flY, flWidth, yBottom - flY )
			outlinePen.SetWidth( flWidth / 4 )
			outlinePen.SetCap( wx.CAP_BUTT )
			dc.SetPen( outlinePen )
			dc.DrawLine( x, flY, x, yBottom )
		
		drawFinishLine()
		
		dc.SetPen( greyPen )
		
		existingRects = []	# Sequenced by decreasing GetRight().
		groupColour = wx.Colour(128,128,255)
		groupHeight = height // 32
		groupPen1 = wx.Pen( groupColour, groupHeight )
		groupBrush = wx.Brush( groupColour, wx.SOLID )
		groupPen1.SetCap( wx.CAP_ROUND )
		groupPen2 = wx.Pen( wx.BLACK, height // 100 )
		groupPen2.SetCap( wx.CAP_BUTT )
		for group in groups:
			# Draw the group.
			xBegin = xLeft + group[0][0] * xScale
			xEnd = xLeft + group[-1][0] * xScale
			if xBegin != xEnd:
				dc.SetPen( groupPen1 )
				dc.DrawLine( xBegin, yTop, xEnd, yTop )
				dc.SetPen( groupPen2 )
				dc.DrawLine( xBegin, yTop, xEnd, yTop )
			else:
				dc.SetPen( wx.TRANSPARENT_PEN )
				dc.SetBrush( groupBrush )
				dc.DrawEllipse( xBegin - groupHeight/2, yTop - groupHeight/2, groupHeight, groupHeight )
			
			# Find a non-overlapping area to draw the group text.
			xText = xBegin
			yText = yTop + fontHeight
			gWidth, gHeight = GetGroupTextExtent( group )
			gRect = wx.Rect( xText, yText, gWidth + spaceWidth, gHeight + fontHeight / 8 )
			
			conflict = True
			while conflict:
				conflict = False
				for r in existingRects:
					if r.GetRight() < gRect.GetLeft():
						break
					if r.Intersects(gRect):
						gRect.SetTop( r.GetBottom()+1 )
						conflict = True
			
			# Insert the new rectangle into the list.  Keep sequenced by decreasing GetRight().
			existingRects.append( gRect )
			for i in xrange(len(existingRects)-2, -1, -1):
				if existingRects[i].GetRight() < existingRects[i+1].GetRight():
					existingRects[i], existingRects[i+1] = existingRects[i+1], existingRects[i]
				else:
					break
					
			# Draw the group text.
			dc.SetPen( greyPen )
			dc.SetBrush( groupTextBrush )
			dc.DrawRectangle( gRect.GetLeft(), gRect.GetTop(), gRect.GetWidth(), fontHeight*1.2 )
			yText = gRect.GetTop()
			for g in group:
				dc.DrawText( g[1], xText + textBorder, yText )
				yText += fontHeight
				
			# Connect the text to the group with a line.
			dc.DrawLine( xBegin, yTop, xBegin, gRect.GetTop() )
			
	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass

if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1000,800))
	situation = Situation(mainWin)
	
	Model.setRace( Model.Race() )
	model = Model.getRace()
	model._populate()
	tStart = datetime.datetime.now()
	def timerUpdate():
		tCur = datetime.datetime.now() + datetime.timedelta(seconds=300)
		situation.SetData( *GetSituationGaps(t=(tCur-tStart).total_seconds()) )
		wx.CallLater( 1001-tCur.microsecond/1000, timerUpdate )
	wx.CallLater( 10, timerUpdate )
	
	mainWin.Show()
	app.MainLoop()