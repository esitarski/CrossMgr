import wx
import datetime
import os
import sys
import math
import itertools
from bisect import bisect_left
import wx.lib.mixins.listctrl as listmix
from copy import copy
import cPickle as pickle

import Utils
import Model
from ReadSignOnSheet	import ResetExcelLinkCache, SyncExcelLink
from GetResults import GetResults
from FixCategories import FixCategories, SetCategory

def formatTimeGap( t ):
	tStr = Utils.formatTimeGap( t )
	if tStr.startswith( "0'0" ):
		tStr = tStr[3:]
	elif tStr.startswith( "0'" ):
		tStr = tStr[2:]
	return tStr

def GetRaceTMax( category ):
	race = Model.race
	if not race:
		return None
	results = GetResults( category, True )
	try:
		return max(rr.raceTimes[-1] for rr in results if rr.raceTimes and len(rr.raceTimes) >= 2)
	except:
		return None
	
def GetLapLE( raceTimes, t ):
	lap = bisect_left( raceTimes, t, hi=len(raceTimes)-1 )
	return lap-1 if raceTimes[lap] > t else lap
	
def GetPositionSpeed( raceTimes, t ):
	lap = GetLapLE( raceTimes, t )
	lapStartTime = raceTimes[lap]
	try:
		lapTime = raceTimes[lap+1] - raceTimes[lap]
	except IndexError:
		lapTime = raceTimes[lap] - raceTimes[lap-1]
	speed = 1.0 / lapTime
	return lap + (t - lapStartTime) * speed, speed
	
def GetLeaderGap( leaderPosition, leaderSpeed, leaderRaceTimes, raceTimes, t ):
	if not raceTimes:
		return None, None
	if t >= raceTimes[-1]:
		if t >= leaderRaceTimes[-1]:
			return (
				raceTimes[-1] - leaderRaceTimes[-1] if len(leaderRaceTimes) == len(raceTimes) else None,
				len(raceTimes) - len(leaderRaceTimes)
			)
		return None, len(raceTimes) - len(leaderRaceTimes)
		
	riderPosition, riderSpeed = GetPositionSpeed( raceTimes, t )
	positionFraction = math.modf( leaderPosition - riderPosition )[0]
	if positionFraction < 0.0:
		positionFraction += 1.0
	#print 'leaderPosition:', leaderPosition, 'riderPosition:', riderPosition, 'positionFraction:', positionFraction, 'lapsDown:', int(leaderPosition - riderPosition)
	return positionFraction / leaderSpeed, int(riderPosition - leaderPosition)

def GetSituationGaps( category=None, t=None ):
	race = Model.race
	if not race:
		return [None, None, None]
		
	results = GetResults( category, True )
	validRiders = {rr.num for rr in results if rr.raceTimes and len(rr.raceTimes) >= 2}
	if not validRiders:
		return []
	results = [rr for rr in results if rr.num in validRiders]
	
	maxLaps = max( rr.laps for rr in results )
	if t is None:
		t = race.lastRaceTime() if not race.isRunning() else (datetime.datetime.now() - race.startTime).total_seconds()
	Finisher = Model.Rider.Finisher
	t = min( t, max(rr.raceTimes[-1] for rr in results) )
	
	leaderRaceTimes = [min(rr.raceTimes[lap] for rr in results if rr.laps >= lap) for lap in xrange(maxLaps+1)]
	
	def getInfo( rr, lapsDown ):
		names = []
		try:
			names.append( rr.LastName.upper() )
		except:
			pass
		try:
			names.append( rr.FirstName[0] )
		except:
			pass
		
		nameStr = (u' ' + u','.join(names)) if names else u''
		lapsDownStr = u'' if lapsDown == 0 else u' ({})'.format(lapsDown)
		return u''.join([unicode(rr.num), nameStr, lapsDownStr])
	
	leaderPosition, leaderSpeed = GetPositionSpeed( leaderRaceTimes, t )
	gaps = []
	for rr in results:
		try:
			gap, lapsDown = GetLeaderGap( leaderPosition, leaderSpeed, leaderRaceTimes, rr.raceTimes, t )
		except TypeError:
			print 'TypeError:', leaderPosition, leaderSpeed, leaderRaceTimes, rr.raceTimes, t
			continue
		if gap is not None:
			gaps.append( (gap, getInfo(rr, lapsDown)) )
	
	gaps.sort()
	
	if gaps:
		gapMin = gaps[0][0]
		gaps = [[g[0] - gapMin, g[1]] for g in gaps]
	thisLap = GetLapLE(leaderRaceTimes, t)
	
	tCur = t
	tClock = race.startTime.hour*60.0*60.0 + race.startTime.minute*60.0 + race.startTime.second + race.startTime.microsecond/1000000.0 + t
	tETA = leaderRaceTimes[thisLap+1] - t if thisLap+1 != len(leaderRaceTimes) else None
	tAfterLeader = t - leaderRaceTimes[thisLap]
	laps = len(leaderRaceTimes) - 1
	lap = min( thisLap + 1, laps )
	lapsToGo = max(laps - lap, 0)
	
	title =  u'   Lap: {}/{}   Laps to go: {}'.format(lap, laps, lapsToGo)
	if tCur is not None:
		title += u'    Race: {}'.format(Utils.formatTime(tCur))
	if tClock is not None:
		if title:
			title += u'   Clock: {}'.format(Utils.formatTime(tClock))
	if tETA is not None:
		title += u'   Leader ETA: {}'.format(Utils.formatTime(tETA))
	
	return gaps, tAfterLeader, title
	
class SituationPanel(wx.PyPanel):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER,
				name="GanttChartPanel" ):
		"""
		Default class constructor.
		"""
		wx.PyPanel.__init__(self, parent, id, pos, size, style, name)
		self.SetBackgroundColour(wx.WHITE)
		
		self.gaps = []
		self.groupRectList = []
		self.groupFullData = []

		self.tAfterLeader = None
		self.title = None
		self.zoom = 1.0
		self.listHeight = 0
		
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
		self.clickHandler = None
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp )
		
	def SetData( self, gaps, tAfterLeader=None, title=None ):
		# each gap is of the form: [gapSeconds, text]
		# Expected to be sorted by increasing gapSeconds.
		self.gaps = gaps or []
		
		self.tAfterLeader = tAfterLeader
		self.title = title
		
		self.Refresh()
	
	def SetClickHandler( self, handler=None ):
		self.clickHandler = handler
		
	def SetZoom( self, zoom ):
		self.zoom = zoom
		self.Refresh()
		
	def OnPaint( self, event ):
		#self.Draw(wx.GCDC(wx.BufferedPaintDC(self)))
		self.Draw(wx.BufferedPaintDC(self))

	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def OnMouseUp( self, event ):
		if not self.clickHandler:
			return
		
		x = event.GetX()
		y = event.GetY()
		for i, (group, gRect) in enumerate(self.groupRectList):
			if gRect.ContainsXY( x, y ):
				self.clickHandler( self, rect=gRect, groupData=self.groupFullData[i] )
				break
		
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass

	def Draw( self, dc ):
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground( backBrush )
		dc.Clear()
		
		self.groupRectList = []
		self.groupFullData = []
		
		greyColour = wx.Colour(100,100,100, 64)
		greyPen = wx.Pen( greyColour, 1 )
		greyBrush = wx.Brush( wx.Colour(232,232,232), wx.SOLID )
		groupTextBrush = wx.Brush( wx.Colour(200,255,200), wx.SOLID )
			
		size = self.GetClientSize()
		width = size.width
		height = size.height

		# Partition the gaps into groups separated by at least one second.
		maxGapSec = 20.0*60.0*60.0	# Ignore gaps that are too great.
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
		
		self.groupFullData = [group[:] for group in groups]
		
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
				group.insert( 0, [group[0][0], u'{} {} {}'.format(i, formatTimeGap(group[0][0]), groupSize)] )
		
		fontHeight = height / 40
		font = wx.FontFromPixelSize( wx.Size(0,fontHeight), wx.DEFAULT, wx.NORMAL, wx.NORMAL )
		dc.SetFont( font )
		spaceWidth, fontHeight = dc.GetTextExtent( u'0 0' )
		spaceWidth = fontHeight / 2
		
		smallFontHeight = fontHeight * 0.75
		smallFont = wx.FontFromPixelSize( wx.Size(0,smallFontHeight), wx.DEFAULT, wx.NORMAL, wx.NORMAL )
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
		
		lastWidth = GetGroupTextExtent( groups[-1] )[0]
		
		xRight = width - border - lastWidth
		yBottom = height - border
		
		gapMax = groups[-1][-1][0] - groups[0][0][0] if groups and groups[0] else 0.0
		xScale = (xRight - xLeft) / (gapMax if gapMax else 1.0) * self.zoom
		
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
			dc.SetPen( wx.TRANSPARENT_PEN )
			dc.SetBrush( wx.WHITE_BRUSH )
			dc.DrawRectangle( width-border, 0, width, height )
		
		drawFinishLine()
		
		# Draw a direction line.
		dc.SetPen( wx.Pen(wx.Colour(0,0,0), 1) )
		dc.SetBrush( wx.Brush(wx.Colour(0,0,0), wx.SOLID) )
		dc.DrawLine( xLeft - border, yTop, width-border, yTop )
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
		groupRectList = []
		for group in groups:
			# Draw the group.
			xBegin = xLeft + group[0][0] * xScale
			xEnd = xLeft + group[-1][0] * xScale
			
			dc.SetPen( wx.TRANSPARENT_PEN )
			dc.SetBrush( groupBrush )
			dc.DrawRectangle( xBegin - groupHeight/2, yTop - groupHeight/2, xEnd - xBegin + groupHeight, groupHeight )
			dc.SetPen( groupPen2 )
			dc.DrawLine( xBegin, yTop, xEnd, yTop )
			
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
					
			groupRectList.append( (group, gRect) )
		
		# Connect the text to the group with a line.
		dc.SetPen( greyPen )
		for group, gRect in groupRectList:
			dc.DrawLine( gRect.GetLeft(), yTop, gRect.GetLeft(), gRect.GetTop() )
			
		for group, gRect in groupRectList:
			# Draw the group outline.
			dc.SetPen( greyPen )
			dc.SetBrush( greyBrush if group[0][0] != groupTimeMaxSize else wx.Brush( wx.Colour(200,255,200), wx.SOLID ) )
			dc.DrawRoundedRectangle( gRect.GetLeft(), gRect.GetTop(), gRect.GetWidth()-1, gRect.GetHeight()-fontHeight/2, fontHeight/3 )
			
			xText = gRect.GetLeft()

			
			# Draw the group text.
			dc.SetPen( greyPen )
			dc.SetBrush( groupTextBrush )
			yText = gRect.GetTop()
			for i, g in enumerate(group):
				
				if i == 0:
					# Draw the coloured rectangles to highlight the title fields.
					title = g[1]
					fieldWidths = [-spaceWidth+2]
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
						dc.DrawRectangle( xLast, yText, tWidth, fontHeight*1.08 )
						iBrush += 1
						xLast += tWidth
					
				dc.DrawText( g[1], xText + spaceWidth, yText )
				yText += fontHeight
				
		self.groupRectList = groupRectList
				
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
			sepStr = formatTimeGap(tNext - tPrev)
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
			
#------------------------------------------------------------------------------------------------------

class AutoWidthListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID = wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.ListCtrlAutoWidthMixin.__init__(self)

class GroupInfoPopup( wx.PopupTransientWindow, listmix.ColumnSorterMixin ):
	def __init__( self, parent ):
		wx.PopupTransientWindow.__init__( self, parent=parent, style=wx.SIMPLE_BORDER )
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.il = wx.ImageList(16, 16)
		self.sm_rt = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallRightArrow.png'), wx.BITMAP_TYPE_PNG))
		self.sm_up = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallUpArrow.png'), wx.BITMAP_TYPE_PNG))
		self.sm_dn = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallDownArrow.png'), wx.BITMAP_TYPE_PNG ))
		
		self.list = AutoWidthListCtrl( self, style = wx.LC_REPORT 
														 | wx.BORDER_NONE
														 | wx.LC_SORT_ASCENDING
														 | wx.LC_HRULES
														 )
		self.list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		sizer.Add( self.list, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.SetSizer( sizer )
		
	def GetListCtrl( self ):
		return self.list
		
	def GetSortImages(self):
		return (self.sm_dn, self.sm_up)
		
	def refresh( self, groupInfo ):
		self.list.ClearAll()
		
		potentialDNS = {}
		with Model.LockRace() as race:
			if not race:
				return
				
			try:
				externalFields = race.excelLink.getFields()
				externalInfo = race.excelLink.read()
			except:
				externalFields = [ _('Bib#') ]
				externalInfo = None
				return
			
		# Get the bibs.
		nums = []
		for i, (gap, info) in enumerate(groupInfo):
			nums.append( int(info.split()[0]) )
		
		# Create an artificial external info if we don't have a spreadsheet.
		if externalInfo is None:
			externalInfo = { num: {_('Bib#'): num} for num in nums }
		else:
			# Adjust to usual name format.
			def GetName( info ):
				return u', '.join( n for n in [info.get(_('LastName'),'').upper(), info.get(_('FirstName'), '')] if n )
			externalFields = [f if f != _('LastName') else _('Name') for f in externalFields if f != _('FirstName')]
			externalInfo = { num : externalInfo[num].copy() for num in nums }
			for num, info in externalInfo.iteritems():
				info[_('Name')] = GetName(info)
				try:
					del info[_('LastName')]
				except:
					pass
				try:
					del info[_('FirstName')]
				except:
					pass
			
		# Add the headers.
		for c, f in enumerate(externalFields):
			self.list.InsertColumn( c+1, f, wx.LIST_FORMAT_RIGHT if f.startswith(_('Bib')) else wx.LIST_FORMAT_LEFT )
		
		# Create the data.  Sort by Bib#
		data = [tuple( num if i == 0 else externalInfo.get(num).get(f, '') for i, f in enumerate(externalFields)) for num in nums]
		data.sort()
		
		# Populate the list.
		for row, d in enumerate(data):
			index = self.list.InsertImageStringItem(sys.maxint, u'{}'.format(d[0]), self.sm_rt)
			for i, v in enumerate(itertools.islice(d, 1, len(d))):
				self.list.SetStringItem( index, i+1, unicode(v) )
			self.list.SetItemData( row, d[0] )		# This key links to the sort fields used by ColumnSorterMixin
		
		# Set the sort fields and configure the sorter mixin.
		self.itemDataMap = dict( (d[0], d) for d in data )
		listmix.ColumnSorterMixin.__init__(self, len(externalFields))

		# Make all column widths autosize.
		for i, f in enumerate(externalFields):
			self.list.SetColumnWidth( i, wx.LIST_AUTOSIZE )
			
		# Fixup the Bib number, as autosize gets confused with the graphic.
		self.list.SetColumnWidth( 0, 64 )
		self.list.SetFocus()
		
		self.SetSize( (10,10) )
		self.GetSizer().Layout()
		self.Fit()
		
		dc = wx.WindowDC( self.list )
		self.listHeight = int(dc.GetTextExtent( u'00' )[1] * 1.15 * (len(data) + 4))
		

class Situation( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super(Situation, self).__init__( parent, id )
		
		self.tCur = None
		
		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, label = _('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL, border=4 )
		
		self.zoomSlider = wx.Slider( self, style=wx.VERTICAL|wx.SL_INVERSE )
		self.zoomSlider.SetMin( 0 )
		self.zoomSlider.SetMax( 50 )
		self.zoomSlider.Bind( wx.EVT_SCROLL, self.zoomScroll )
		
		self.timeSlider = wx.Slider( self, style=wx.HORIZONTAL )
		self.timeSlider.SetMin( 0 )
		self.timeSlider.SetMax( 10000 )
		self.timeSlider.Bind( wx.EVT_SCROLL, self.timeScroll )
		
		self.timeSlider.SetValue( self.timeSlider.GetMax() )
		
		self.situation = SituationPanel( self )
		self.situation.SetClickHandler( self.groupClick )
		
		self.groupInfoPopup = GroupInfoPopup( self )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		# Add the Category selector.
		vs.Add( self.hbs, 0, flag=wx.ALL, border=4 )
		
		# Add the time zoom.  Add a spacer so it lines up on the left.
		hsTS = wx.BoxSizer( wx.HORIZONTAL )
		hsTS.AddSpacer( self.zoomSlider.GetSize()[0] )
		hsTS.Add( self.timeSlider, 1, flag=wx.EXPAND )
		vs.Add( hsTS, 0, flag=wx.EXPAND )
		
		# Add the zoom slider and the situation display.
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.zoomSlider, 0, flag=wx.EXPAND )
		hs.Add( self.situation, 1, flag=wx.EXPAND )
		
		vs.Add( hs, 1, flag=wx.EXPAND )
		
		self.SetSizer( vs )
		wx.CallAfter( self.timeScroll )
		wx.CallAfter( self.situation.Refresh )
	
	def doChooseCategory( self, event ):
		Model.setCategoryChoice( self.categoryChoice.GetSelection(), 'situationCategory' )
		self.refresh()
	
	def zoomScroll( self, event ):
		zoom = 1.0 + (self.zoomSlider.GetValue() / float(self.zoomSlider.GetMax())) * 5.0
		self.situation.SetZoom( zoom )
		
	def timeAtMax( self ):
		return self.timeSlider.GetValue() == self.timeSlider.GetMax()
		
	def timeScroll( self, event=None ):
		if self.timeAtMax():
			self.timerUpdate()
			return
		
		race = Model.race
		if not race:
			return
		
		category = FixCategories( self.categoryChoice, getattr(race, 'situationCategory', 0) )
		tMax = GetRaceTMax(category) or 0.01
		
		t = tMax * (float(self.timeSlider.GetValue()) / float(self.timeSlider.GetMax()))
		self.situation.SetData( *GetSituationGaps(category=category, t=t) )
	
	def timerUpdate( self ):
		if not self.timeAtMax():
			return
		mainWin = Utils.getMainWin()
		if mainWin and not mainWin.isShowingPage(self):
			return
		
		race = Model.race
		if not race:
			return
		
		category = FixCategories( self.categoryChoice, getattr(race, 'situationCategory', 0) )
		self.situation.SetData( *GetSituationGaps(category=category, t=None) )
		
		if race and race.isRunning():
			wx.CallLater( 1001-datetime.datetime.now().microsecond//1000, self.timerUpdate )
	
	def groupClick( self, situation, rect, groupData ):
		pos = self.situation.ClientToScreen( (rect.GetX(), rect.GetY()) )
		self.groupInfoPopup.Dismiss()
		self.groupInfoPopup.refresh( groupData )
		sz = self.groupInfoPopup.GetSize()
		#self.groupInfoPopup.SetSize( (sz[0], 24*(len(groupData)+2)) )
		self.groupInfoPopup.SetSize( (sz[0], self.groupInfoPopup.listHeight) )
		self.groupInfoPopup.Position(wx.Point(pos[0], pos[1]+20), wx.Size(0,0))
		self.groupInfoPopup.Popup()
	
	def refresh( self ):
		self.timeScroll()
	
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1000,800))
	situation = Situation(mainWin)
	
	'''
	tOffset = datetime.timedelta( seconds=5*60*0 )
	try:
		fileName = os.path.join( 'Binghampton', '2014-04-27-Binghamton Circuit Race-r3-.cmn' )
		with open(fileName, 'rb') as fp:
			race = pickle.load( fp )
		Model.setRace( race )
		ResetExcelLinkCache()
		race.resetAllCaches()
		SyncExcelLink( race )
	except Exception as e:
		print e
		Model.setRace( Model.Race() )
		race = Model.getRace()
		race._populate()

	tStart = datetime.datetime.now()
	def timerUpdate():
		tCur = datetime.datetime.now()
		situation.SetData( *GetSituationGaps(t=(tCur-tStart+tOffset).total_seconds()) )
		wx.CallLater( 1001-tCur.microsecond/1000, timerUpdate )
	wx.CallLater( 10, timerUpdate )
	'''
	
	try:
		fileName = os.path.join( 'Binghampton', '2014-04-27-Binghamton Circuit Race-r3-.cmn' )
		with open(fileName, 'rb') as fp:
			race = pickle.load( fp )
		Model.setRace( race )
		ResetExcelLinkCache()
		race.resetAllCaches()
		SyncExcelLink( race )
	except Exception as e:
		print e
		Model.setRace( Model.Race() )
		race = Model.getRace()
		race._populate()
	
	mainWin.Show()
	situation.refresh()
	app.MainLoop()
