import Utils
import Model
import wx
import re
from GetResults import GetResults
from math import modf
from ForecastHistory import getExpectedRecorded
from bisect import bisect_left, bisect_right

green = wx.Colour( 0, 200, 0 )
blue = wx.Colour( 0, 0, 200 )
grey = wx.Colour( 64, 64, 64 )
yellow = wx.Colour( 255,255,150 )
darkerYellow = wx.Colour( 240,240,140 )
orange = wx.Colour( 255, 165, 0 )
recordedChar = u"\u2190"

reGender = re.compile( r'\(([^)]+)\)$' )

def max_or_zero( seq ):
	try:
		return max( seq )
	except ValueError:
		return 0

def toOrdinal( pos ):
	try:
		return Utils.ordinal( int(pos) )
	except:
		return pos
		
def find_le( a, x ):
    'Find rightmost index less than or equal to x'
    return bisect_right(a, x) - 1
		
def find_ge( a, x ):
    'Find rightmost index greater than or equal to x'
    return bisect_left(a, x)
		
class Announcer( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super(Announcer, self).__init__(parent, id)
		self.SetBackgroundStyle( wx.BG_STYLE_PAINT )
		
		self.timer = wx.Timer( self )
		self.expected = []
		self.recorded = []
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_TIMER, self.OnTimer)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
	
	def OnErase(self, event):
		pass

	def resetTimer( self ):
		if self.timer.IsRunning():
			return
		race = Model.race
		if race and race.isRunning() and self.IsShown():
			tRace = race.curRaceTime()
			self.timer.StartOnce( int((1.0 - modf(tRace)[0]) * 1000.0) )
	
	def OnTimer( self, event ):
		self.Refresh()
		self.resetTimer()
	
	def OnSize( self, event ):
		self.Refresh()
	
	def OnPaint( self, event ):
		dc = wx.PaintDC( self )
		self.Draw( dc )
	
	cols = (u'Pos', u'Name', u'Bib', u'Gap', u'ETA', )
	iCol = {c:i for i, c in enumerate(cols)}
	def Draw( self, dc ):
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground(backBrush)
		dc.Clear()

		race = Model.race
		if not race:
			return
		
		tRace = race.lastRaceTime()
		isRunning = race.isRunning()
		
		width, height = self.GetClientSize()
		
		dc.SetPen( wx.TRANSPARENT_PEN )
		dc.SetBrush( wx.WHITE_BRUSH )
		dc.DrawRectangle( 0, 0, width, height )
		
		fontSize = 18
		font = wx.Font( (0,fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		boldFont = wx.Font( (0,fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD )
		dc.SetFont( font )
		
		lineHeight = int( fontSize * 1.4 )
		yNow = int( height * 0.5 )

		category = race.getCategories( startWaveOnly=True )[0]
		results = GetResults( category )
		
		Finisher = Model.Rider.Finisher
		if not results:
			return
		
		try:
			leaderLap = find_le( results[0].raceTimes, tRace )
			if results[0].interp[leaderLap]:
				leaderLap -= 1
			tLeader = results[0].raceTimes[leaderLap]
		except:
			leaderLap = tLeader = None
			
		bibExpected = { e.num:e for e in self.expected }
		bibRecorded = { e.num:e for e in self.recorded }
		bibETA = {}

		resultsData = [[] for col in self.cols]
		isRecorded = set()
		
		iGroup = -1
		rowGroup = []
		for row, rr in enumerate(results):
			resultsData[self.iCol[u'Pos']].append( u'{}'.format(rr.pos) )
			resultsData[self.iCol[u'Bib']].append( u'{}'.format(rr.num) )
			resultsData[self.iCol[u'Name']].append(
				u'{} {}'.format(getattr(rr,'FirstName',u''), getattr(rr,'LastName',u'')).strip()
			)
			resultsData[self.iCol[u'Gap']].append( rr.gap )
			e = bibExpected.get(rr.num, None) if rr.status == Finisher else None
			iGroup += 1
			if e: 
				eta = e.t - tRace
				bibETA[rr.num] = eta
				if row > 0:
					try:
						numPrev = results[row-1].num
						if abs(abs(eta - bibETA[results[row-1].num]) < 1.0):
							iGroup -= 1
					except:
						pass
			rowGroup.append( iGroup )			
			resultsData[self.iCol[u'ETA']].append( Utils.formatTime(eta) if e else u'' )
			
			e = bibRecorded.get( rr.num, None )
			if not isRunning or (leaderLap == 1 or (e and tLeader is not None and e.t >= tLeader)):
				isRecorded.add( row )
			else:
				resultsData[self.iCol[u'Pos']][-1] = u'{}{}'.format(resultsData[self.iCol[u'Pos']][-1], recordedChar)
				
		firstPlace = toOrdinal(1)
		
		iPos = self.iCol[u'Pos']
		iName = self.iCol[u'Name']
		iETA = self.iCol[u'ETA']
		borderWidth = dc.GetTextExtent(u'  ')[0]
		colWidths = {
			u'ETA':borderWidth + dc.GetTextExtent(u'1:00:00')[0],
			u'Gap':borderWidth + dc.GetTextExtent(u'1:00:00')[0],
			u'Pos':borderWidth + dc.GetTextExtent(u'9999')[0],
			u'Name':borderWidth + max_or_zero(dc.GetTextExtent(n)[0] for n in resultsData[iName]),
			u'Bib':borderWidth + dc.GetTextExtent(u'9999')[0],
		}
		colWidths = [colWidths[colName] for colName in self.cols]
		
		greenBrush = wx.Brush( wx.Colour(64,200,64), wx.SOLID )
		yellowBrush = wx.Brush( yellow, wx.SOLID )
		orangeBrush = wx.Brush( orange, wx.SOLID )
		grayPen = wx.Pen(wx.Colour(128,128,128), 1) 
		
		evenBrush = wx.Brush(wx.Colour(255,255,255), wx.SOLID )
		oddBrush = wx.Brush(wx.Colour(240,240,240), wx.SOLID )
		
		evenUnrecordedBrush = wx.Brush(wx.Colour(185,185,255), wx.SOLID )
		oddUnrecordedBrush = wx.Brush(wx.Colour(170,170,255), wx.SOLID )

		evenYellowBrush = yellowBrush
		oddYellowBrush = wx.Brush( darkerYellow, wx.SOLID )
		
		alertETA = 15
		greenDelta = 80
		greenTick = greenDelta / float(alertETA)
		greenScale = [wx.Colour(0,int(255-i*greenTick),0) for i in xrange(alertETA)]
		colorMap = {}
		colorMap.update( {i:greenScale[i] for i in xrange(alertETA)} )
		colorMap.update( {-i:greenScale[0] for i in xrange(alertETA)} )
		colorMap.update( {-alertETA-i:greenScale[i] for i in xrange(alertETA)} )
		gc = wx.GraphicsContext.Create( dc )
		
		def drawRow( x, y, w, h, row, iRow, isRecorded=False, eta=60.0 ):
			dc.SetPen( wx.TRANSPARENT_PEN )
			if not isRecorded:
				dc.SetBrush( oddUnrecordedBrush if iRow&1 else evenUnrecordedBrush )
			else:
				dc.SetBrush( oddBrush if iRow&1 else evenBrush )
			dc.DrawRectangle( x, y, w, h )
				
			yText = y + (lineHeight - fontSize)//2
			for c, v in enumerate(row):
				if c == iName:
					xText = x + borderWidth
				else:
					xText = x + colWidths[c] - dc.GetTextExtent(v)[0]
				if c == iETA:
					etaColor = colorMap.get(int(eta), None if eta >= 0.0 else greenScale[-1])
					if etaColor is not None:
						gc.SetBrush( wx.Brush(etaColor, wx.SOLID) )
						gc.SetPen( grayPen )
						gc.DrawRoundedRectangle( x+borderWidth/2, y, colWidths[c], h, 4 )
					
				dc.DrawText( v, xText, y )
				x += colWidths[c]
		
		dc.SetFont( boldFont )
		dc.SetTextForeground( wx.BLACK )
		# Draw the category and laps to go.
		y = 0
		x = 0
		v = category.fullname
		try:
			lapsToGo = len(results[0].raceTimes) - 1 - (leaderLap or 0)
		except Exception as e:
			lapsToGo = None
		if lapsToGo is not None:
			if lapsToGo == 0:
				v += u': {}'.format( _('Finish') )
			else:
				v += u': {} {}'.format( lapsToGo, _('laps to go') )
		xText = x + borderWidth
		dc.DrawText( v, xText, y )
		
		# Draw the column headers.
		y += lineHeight
		x = 0
		for c, v in enumerate(self.cols):
			if c == iName:
				xText = x + borderWidth
			else:
				xText = x + colWidths[c] - dc.GetTextExtent(v)[0]
			dc.DrawText( v, xText, y )
			x += colWidths[c]
		
		yResults = y + lineHeight
		
		# Draw the results
		xTextRight = sum( colWidths )
		
		dc.SetFont( font )
		dc.SetTextForeground( wx.BLACK )
		x = 0
		y = yResults
		for i, rr in enumerate(results):
			row = [resultsData[c][i] for c in xrange(len(self.cols))]
			drawRow( x, y, width, lineHeight, row, i, i in isRecorded, bibETA.get(rr.num,60.0) )
			y += lineHeight
			if y > height:
				break

		# Draw group indicators.
		if not race.isTimeTrial:
			fontSizeGroup = int(fontSize)
			fontSmall = wx.Font( (0,fontSizeGroup), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
			
			groupColor = wx.Colour(150,150,150)
			groupLineWidth = 2
			gc.SetPen( wx.Pen(groupColor, groupLineWidth) )
			dc.SetFont( fontSmall )
			dc.SetTextForeground( wx.Colour(64,64,64) )
			gc.SetBrush( wx.TRANSPARENT_BRUSH )
			
			groupLineOffset = 6
			x = 0
			y = yResults
			iStart = 0
			for i, g in enumerate(rowGroup):
				if g != rowGroup[iStart]:
					if i - iStart > 1:
						y1 = y + lineHeight*iStart
						y2 = y + lineHeight*i
						x1 = x2 = x + xTextRight + groupLineOffset*2
						gc.DrawRoundedRectangle( x+groupLineWidth//2, y1, x2, y2-y1, 6 )
						dc.DrawText( u'{}'.format(i-iStart), x1+groupLineOffset, y1 + (fontSize-fontSizeGroup) )
					iStart = i
				
	def refresh( self ):
		race = Model.race
		if race and race.isRunning():
			tRace = race.curRaceTime()
			self.expected, self.recorded = getExpectedRecorded()
		else:
			self.expected = self.recorded = []
		self.resetTimer()
		self.Refresh()
		
	def commit( self ):
		pass
		
