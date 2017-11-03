import Utils
import Model
import wx
import re
from ForecastHistory import getExpectedRecorded
from GetResults import GetResults
from math import modf

green = wx.Colour( 0, 200, 0 )
blue = wx.Colour( 0, 0, 200 )
grey = wx.Colour( 64, 64, 64 )

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
		dc = wx.AutoBufferedPaintDC( self )
		self.Draw( dc )
	
	expectedCols = (u'ETA', u'Pos', u'Bib', u'Name', u'Wave')
	expectedICol = {c:i for i, c in enumerate(expectedCols)}
	recordedCols = (u'Gap', u'Pos', u'Bib', u'Name', u'Wave')
	recordedICol = {c:i for i, c in enumerate(recordedCols)}
	def Draw( self, dc ):
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground(backBrush)
		dc.Clear()

		race = Model.race
		if not race or not race.isRunning():
			return
		
		tRace = race.curRaceTime()
		
		width, height = self.GetClientSize()
		
		dc.SetPen( wx.BLACK_PEN )
		dc.DrawRectangle( 0, 0, width, height )
		
		fontSize = 16
		font = wx.Font( (0,fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( font )
		
		lineHeight = int( fontSize * 1.4 )
		yNow = int( height * 0.5 )

		expectedCount = int((yNow - lineHeight) / lineHeight) + 1
		recordedCount = int((height - yNow) / lineHeight)
		expected = self.expected[:expectedCount]
		recorded = self.recorded[::-1][:recordedCount]
		
		Finisher = Model.Rider.Finisher
		bibRR = {}
		bibLeader = set()
		nameWidthMax = 0
		for category in race.getCategories( startWaveOnly=True ):
			results = GetResults( category )
			if not results:
				continue
			bibRR.update( {rr.num:rr for rr in results} )
			nameWidthMax = max(
				nameWidthMax,
				max(dc.GetTextExtent(u'{} {}'.format(getattr(rr,'FirstName',u''), getattr(rr,'LastName',u'')).strip())[0] for rr in results )
			)
			if results and results[0].status == Finisher and results[0].raceTimes:
				bibLeader.add( results[0].num )
		
		firstPlace = toOrdinal(1)
		
		iPos = self.expectedICol[u'Pos']
		iName = self.expectedICol[u'Name']
		iWave = self.expectedICol[u'Wave']
		expectedData = [[] for c in self.expectedCols]
		for e in expected:
			rr = bibRR[e.num]
			expectedData[self.expectedICol[u'Pos']].append( u'{}'.format(toOrdinal(rr.pos)) )
			expectedData[self.expectedICol[u'Bib']].append( u'{}'.format(e.num) )
			expectedData[self.expectedICol[u'Name']].append(
				u'{} {}'.format(getattr(rr,'FirstName',u''), getattr(rr,'LastName',u'')).strip()
			)
			expectedData[self.expectedICol[u'ETA']].append( Utils.formatTime(e.t - tRace) )
			expectedData[self.expectedICol[u'Wave']].append(
				reGender.sub( lambda g: u'({})'.format(g.group(1)[0]), race.getCategory(e.num).fullname)
			)
		
		recordedData = [[] for c in self.recordedCols]
		for e in recorded:
			rr = bibRR[e.num]
			recordedData[self.expectedICol[u'Pos']].append( u'{}'.format(toOrdinal(rr.pos)) )
			recordedData[self.recordedICol[u'Bib']].append( u'{}'.format(e.num) )
			recordedData[self.recordedICol[u'Name']].append(
				u'{} {}'.format(getattr(rr,'FirstName',u''), getattr(rr,'LastName',u'')).strip()
			)
			recordedData[self.recordedICol[u'Gap']].append(
				_('Lead') if e.num in bibLeader else rr.gap
			)
			recordedData[self.expectedICol[u'Wave']].append(
				reGender.sub( lambda g: u'({})'.format(g.group(1)[0]), race.getCategory(e.num).fullname)
			)

		
		borderWidth = dc.GetTextExtent(u'  ')[0]
		colWidths = {
			u'ETA':borderWidth + dc.GetTextExtent(u'1:00:00')[0],
			u'Pos':borderWidth + dc.GetTextExtent(u'9999')[0],
			u'Name':borderWidth + nameWidthMax,
			u'Bib':borderWidth + dc.GetTextExtent(u'9999')[0],
			u'Wave':borderWidth + max(
				max_or_zero(dc.GetTextExtent(n)[0] for n in expectedData[iWave]),
				max_or_zero(dc.GetTextExtent(n)[0] for n in recordedData[iWave]),
			),
		}
		colWidths = [colWidths[colName] for colName in self.expectedCols]
		
		greenBrush = wx.Brush( wx.Colour(64,200,64), wx.SOLID )
		grayPen = wx.Pen(wx.Colour(128,128,128), 1) 
		evenBrush = wx.Brush(wx.Colour(255,255,255), wx.SOLID )
		oddBrush = wx.Brush(wx.Colour(240,240,240), wx.SOLID )
		
		def drawRow( x, y, w, h, row, iRow, horizon=False ):
			if row[iPos] == firstPlace:
				dc.SetBrush( greenBrush )
				dc.SetPen( grayPen )
				dc.DrawRectangle( x, y, w, h )
			elif iRow&1:
				dc.SetBrush( oddBrush )
				dc.SetPen( wx.TRANSPARENT_PEN )
				dc.DrawRectangle( x, y, w, h )
			else:
				dc.SetBrush( evenBrush )
				dc.SetPen( wx.TRANSPARENT_PEN )
				dc.DrawRectangle( x, y, w, h )
				
			yText = y + int((lineHeight - fontSize)/2.0)
			for c, v in enumerate(row):
				if c in (iName, iWave):
					xText = x + borderWidth
				else:
					xText = x + colWidths[c] - dc.GetTextExtent(v)[0]
				dc.DrawText( v, xText, y )
				x += colWidths[c]
		
			
		dc.SetFont( font )
		dc.SetTextForeground( wx.BLACK )
		y = yNow
		x = 0
		for i, e in enumerate(reversed(recorded)):
			row = [recordedData[c][i] for c in xrange(len(self.recordedCols))]
			drawRow( x, y, width, lineHeight, row, i )
			y -= lineHeight
		
		yFinish = yNow + lineHeight
		hFinish = lineHeight // 2
		dc.SetPen( grayPen )
		dc.SetBrush( wx.WHITE_BRUSH )
		dc.DrawRectangle( 0, yFinish, width, hFinish )
		dc.SetPen( wx.Pen(wx.BLACK, 2) )
		dc.DrawLine( 0, yFinish + hFinish//2, width, yFinish + hFinish//2 )

		dc.SetTextForeground( wx.BLACK )
		y = yFinish + hFinish
		x = 0
		for i, e in enumerate(expected):
			row = [expectedData[c][i] for c in xrange(len(self.expectedCols))]
			drawRow( x, y, width, lineHeight, row, i )
			y += lineHeight

	def refresh( self ):
		race = Model.race
		if race and race.isRunning():
			tRace = race.curRaceTime()
			tMin = tRace - max( race.getAverageLapTime(), 10*60.0 )
			self.expected, self.recorded = getExpectedRecorded( tMin )
		else:
			self.expected = self.recorded = []
		self.resetTimer()
		self.Refresh()
		
	def commit( self ):
		pass
		
