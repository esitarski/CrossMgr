import wx
import Utils
import Model
import datetime
import os

from GetResults import GetResults
from bisect import bisect_left
from copy import copy
import cPickle as pickle

def GetSituationGaps( category=None, t=None ):
	race = Model.race
	if not race:
		return []
		
	results = GetResults( category, True )
	validRiders = {rr.num for rr in results if rr.raceTimes and len(rr.raceTimes) >= 2}
	if not validRiders:
		return []
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
		
		# print 'thisLeaderLap:', thisLeaderLap, 'thisLap:', thisLap, 'lapsDown:', thisLap - thisLeaderLap
		gaps.append( (gap, getInfo(rr, thisLap - thisLeaderLap)) )
	
	gaps.sort()
	
	if gaps:
		gapMin = gaps[0][0]
		gaps = [[g[0] - gapMin, g[1]] for g in gaps]
	thisLap = getLapLE(leaderRaceTimes, t)
	
	tCur = t
	tClock = race.startTime.hour*60.0*60.0 + race.startTime.minute*60.0 + race.startTime.second + race.startTime.microsecond/1000000.0 + t
	tETA = leaderRaceTimes[thisLap+1] - t if thisLap+1 != len(leaderRaceTimes) else None
	tAfterLeader = t - leaderRaceTimes[thisLap]
	lap = thisLap
	laps = len(leaderRaceTimes) - 1
	lapsToGo = laps - lap
	
	title = u''
	if tCur is not None:
		title = u'Race: {}'.format(Utils.formatTime(tCur))
	if tClock is not None:
		if title:
			title += u'   Clock: {}'.format(Utils.formatTime(tClock))
	title += u'   Lap: {}/{}   Laps to go: {}'.format(lap, laps, lapsToGo)
	if tETA is not None:
		title += u'   Leader ETA: {}'.format(Utils.formatTime(tETA))
	
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
		
		self.gaps = []
		self.tAfterLeader = None
		self.title = None
		
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
	def SetData( self, gaps, tAfterLeader=None, title=None ):
		# each gap is of the form: [gapSeconds, text]
		# Expected to be sorted by increasing gapSeconds.
		self.gaps = gaps or []
		
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
		
		greyColour = wx.Colour(100,100,100, 64)
		greyPen = wx.Pen( greyColour, 1 )
		greyBrush = wx.Brush( wx.Colour(200,200,200), wx.SOLID )
		groupTextBrush = wx.Brush( wx.Colour(200,255,200), wx.SOLID )
			
		size = self.GetClientSize()
		width = size.width
		height = size.height

		# Partition the gaps into groups separated by at least one second.
		maxGapSec = 20.0*60.0	# Ignore gaps greater than 20 minutes from the leader.
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
		if group:
			groups.append( group )
		
		groupMax = max( len(group) for group in groups ) if groups else 0
		try:
			groupTimeMaxSize = next(group[0][0] for group in groups if len(group) == groupMax)
		except:
			groupTimeMaxSize = 0
		
		# Add the gap information to each group.
		for i, group in enumerate(groups):
			if not group:
				continue
			groupSize = len(group)
			if len(group) > 10:
				group[:] = group[:5] + [[group[5][0], u'...']] + group[-5:]
			if i == 0:
				group.insert( 0, [group[0][0], u'\u2714 \u200B {}'.format(groupSize)] )
			else:
				group.insert( 0, [group[0][0], u'{} {} {}'.format(i, Utils.formatTimeGap(group[0][0]), groupSize)] )
		
		fontHeight = height / 40
		font = wx.FontFromPixelSize( wx.Size(0,fontHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( font )
		spaceWidth, fontHeight = dc.GetTextExtent( u'0 0' )
		spaceWidth = fontHeight / 2
		
		smallFontHeight = fontHeight * 0.75
		smallFont = wx.FontFromPixelSize( wx.Size(0,smallFontHeight), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( smallFont )
		smallFontHeight = dc.GetTextExtent( u'0 0' )[1]

		#---------------------------------------------------------------------
		dc.SetFont( font )
		border = min( width, height ) // 25
		xLeft = border*2
		yTop = border*2.25 + fontHeight
		if self.title:
			dc.DrawText( self.title, xLeft, border )
		
		if not groups:
			return
		
		def GetGroupTextExtent( group ):
			widthMax = 0
			heightMax = 0
			for gap in group:
				tWidth, tHeight = dc.GetTextExtent( gap[1] )
				widthMax = max( widthMax, tWidth )
				heightMax += tHeight
			return widthMax, heightMax
		
		lastWidth = GetGroupTextExtent( groups[-1][1] )[0]
		
		xRight = width - border - lastWidth
		yBottom = height - border
		
		gapMax = groups[-1][-1][0] - groups[0][0][0] if groups and groups[0] else 0.0
		xScale = (xRight - xLeft) / (gapMax if gapMax else 1.0)
		
		def drawFinishLine():
			if self.tAfterLeader is None:
				return
			x = xLeft + self.tAfterLeader * xScale
			flWidth = width / 32
			if x - flWidth > width:
				return
			flTop = yTop - border / 2
			flBottom = flTop + border
			outlinePen = wx.Pen( wx.Colour(220,220,220), max(width / 800, 1) )
			dc.SetPen( outlinePen )
			dc.SetBrush( wx.WHITE_BRUSH )
			dc.DrawRectangle( x - flWidth / 2, flTop, flWidth, flBottom - flTop )
			outlinePen.SetWidth( flWidth / 4 )
			outlinePen.SetCap( wx.CAP_BUTT )
			dc.SetPen( outlinePen )
			dc.DrawLine( x, flTop, x, flBottom )
		
		drawFinishLine()
		
		# Draw a direction line.
		dc.SetPen( wx.Pen(wx.Colour(0,0,0), 1) )
		dc.SetBrush( wx.Brush(wx.Colour(0,0,0), wx.SOLID) )
		dc.DrawLine( xLeft - border, yTop, xRight, yTop )
		arrowLength = border * 0.8
		points = [wx.Point(0,0), wx.Point(arrowLength, arrowLength/4), wx.Point(arrowLength, -arrowLength/4)]
		dc.DrawPolygon( points, border/2, yTop )
		
		dc.SetPen( greyPen )
		
		groupTitleBrushes = [
			wx.Brush( wx.Colour(0xFF, 0xCC, 0x99), wx.SOLID ),	# Group Index
			wx.WHITE_BRUSH,										# Gap
			wx.Brush( wx.Colour(0x99, 0xCC, 0xFF), wx.SOLID ),	# Group Size
		]
		
		existingRects = []	# Sequenced by decreasing GetRight().
		groupColour = wx.Colour(128,128,255)
		groupHeight = height // 40
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
			yText = yTop + groupHeight/2 + fontHeight
			gWidth, gHeight = GetGroupTextExtent( group )
			gRect = wx.Rect( xText, yText, gWidth + spaceWidth*2, gHeight + fontHeight / 2 )
			
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
					
			# Draw the group outline.
			dc.SetPen( greyPen )
			dc.SetBrush( greyBrush if group[0][0] != groupTimeMaxSize else wx.Brush( wx.Colour(200,255,200), wx.SOLID ) )
			dc.DrawRoundedRectangle( gRect.GetLeft(), gRect.GetTop(), gRect.GetWidth()-1, gRect.GetHeight()-fontHeight/2, -0.1 )
			
			# Draw the group text.
			dc.SetPen( greyPen )
			dc.SetBrush( groupTextBrush )
			yText = gRect.GetTop()
			for i, g in enumerate(group):
				
				if i == 0:
					# Draw the coloured rectangles to highlight the fields.
					title = g[1]
					fieldWidths = [-spaceWidth]
					iSpace = 0
					while True:
						iSpace = title.find( u' ', iSpace )
						if iSpace < 0:
							fieldWidths.append( dc.GetTextExtent(title)[0] + spaceWidth/2 )
							break
						fieldWidths.append( dc.GetTextExtent(title[:iSpace])[0] + spaceWidth/2 )
						iSpace += 1
					
					fieldWidths[-1] += spaceWidth/2
					iBrush = 0 if len(fieldWidths) > 2 else 2
					xLast = xText
					for iField in xrange(1, len(fieldWidths)):
						tWidth = fieldWidths[iField] - fieldWidths[iField-1]
						dc.SetBrush( groupTitleBrushes[iBrush] )
						dc.DrawRectangle( xLast, yText, tWidth, fontHeight*1.10 )
						iBrush += 1
						xLast += tWidth
					
				dc.DrawText( g[1], xText + spaceWidth, yText )
				yText += fontHeight
				
			# Connect the text to the group with a line.
			dc.DrawLine( xBegin, yTop, xBegin, gRect.GetTop() )
			
		# Draw the gaps between the groups with dimension lines.
		dc.SetPen( greyPen )
		dc.SetBrush( greyBrush )
		dc.SetFont( smallFont )
		yUp = yTop - groupHeight - smallFontHeight
		yText = yUp + smallFontHeight/2
		yTextCenter = yText + smallFontHeight * 0.5
		yUp += smallFontHeight/4
		
		arrowLength = smallFontHeight * 0.75
		leftArrow = [wx.Point(0,0), wx.Point(arrowLength, arrowLength/4), wx.Point(arrowLength, -arrowLength/4)]
		rightArrow = [wx.Point(-p.x, p.y) for p in leftArrow]

		for iGroup in xrange(1, len(groups)):
			groupPrev, groupNext = groups[iGroup-1:iGroup+1]
			tPrev, tNext = groupPrev[-1][0], groupNext[0][0]
			xPrev, xNext = xLeft + tPrev * xScale, xLeft + tNext * xScale
			sepStr = Utils.formatTimeGap(tNext - tPrev)
			tWidth = dc.GetTextExtent( sepStr )[0]
			if xNext - xPrev < tWidth * 1.25:
				continue
			
			dc.DrawLine( xPrev, yTop, xPrev, yUp )
			dc.DrawLine( xNext, yTop, xNext, yUp )
			
			if xNext - xPrev > tWidth + arrowLength * 4:
				dc.DrawLine( xPrev, yTextCenter, xPrev + (xNext - xPrev - tWidth) / 2 - 2, yTextCenter )
				dc.DrawLine( xNext - (xNext - xPrev - tWidth) / 2 + 2, yTextCenter, xNext, yTextCenter )
				dc.DrawPolygon( leftArrow, xPrev, yTextCenter )
				dc.DrawPolygon( rightArrow, xNext, yTextCenter )
			
			dc.DrawText( sepStr, xPrev + (xNext - xPrev - tWidth) / 2, yText )
			
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
	
	# Model.setRace( Model.Race() )
	# model = Model.getRace()
	# model._populate()
	fileName = os.path.join( 'Binghampton', '2014-04-27-Binghamton Circuit Race-r3-.cmn' )
	with open(fileName, 'rb') as fp:
		race = pickle.load( fp )
	Model.setRace( race )
	tStart = datetime.datetime.now()
	def timerUpdate():
		tCur = datetime.datetime.now()
		situation.SetData( *GetSituationGaps(t=(tCur-tStart).total_seconds()) )
		wx.CallLater( 1001-tCur.microsecond/1000, timerUpdate )
	wx.CallLater( 10, timerUpdate )
	
	mainWin.Show()
	app.MainLoop()
