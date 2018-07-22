import Utils
import Model
import wx
import re
from GetResults import GetResults
from math import modf
from ForecastHistory import getExpectedRecorded
from GanttChartPanel import lighterColour
from bisect import bisect_left, bisect_right
from collections import defaultdict

green = wx.Colour( 0, 200, 0 )
blue = wx.Colour( 0, 0, 200 )
grey = wx.Colour( 64, 64, 64 )
yellow = wx.Colour( 255,255,150 )
darkerYellow = wx.Colour( 240,240,140 )
orange = wx.Colour( 255, 165, 0 )

recordedColour = wx.WHITE
unrecordedColour = wx.Colour(220, 220, 220)
recordedChar = u"\u2192"

reGender = re.compile( r'\(([^)]+)\)$' )

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
	cols = (u'Pos', u'Name', u'Team', u'Bib', u'Gap', u'Group', u'ETA' )
	iCol = {c:i for i, c in enumerate(cols)}
	groupColours = [wx.Colour(int(c[1:3],16),int(c[3:5],16),int(c[5:7],16)) for c in '#66c2a5,#fc8d62,#8da0cb,#e78ac3,#a6d854,#ffd92f,#e5c494,#b3b3b3'.split(',')]
	groupTextColours = [Utils.GetContrastTextColour(c) for c in groupColours]
	
	def __init__( self, parent, id = wx.ID_ANY ):
		super(Announcer, self).__init__(parent, id)
		
		self.iCategory = 0
		self.tExpected = []
		self.isRecorded = []
		self.expected = []
		self.recorded = []
		
		self.bibExpected = {}
		self.tExpected = []
		
		self.title = wx.StaticText( self )
		
		self.wrapCategories = wx.WrapSizer()
		self.categoryButtons = []
		self.iCategoryButtonMax = 0
		
		self.grid = wx.grid.Grid( self )
		self.grid.CreateGrid( 0, len(self.cols) )
		self.grid.SetRowLabelSize( 0 )
		self.grid.SetMargins( 0, 0 )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()
		self.grid.SetGridLineColour( self.grid.GetBackgroundColour() )
		
		for i, c in enumerate(self.cols):
			a = wx.grid.GridCellAttr()
			a.SetAlignment( wx.ALIGN_RIGHT if c not in (u'Name', u'Team') else wx.ALIGN_LEFT, wx.ALIGN_CENTRE )
			a.SetReadOnly( True )
			self.grid.SetColAttr( i, a )
			self.grid.SetColLabelValue( i, c )
		
		self.timer = wx.Timer( self )
		self.Bind( wx.EVT_TIMER, self.OnTimer )

		vs = wx.BoxSizer( wx.VERTICAL )
		vs.Add( self.wrapCategories, 0, flag=wx.EXPAND|wx.ALL, border=4 )
		vs.Add( self.title, 0, flag=wx.EXPAND|wx.ALL, border=4 )
		vs.Add( self.grid, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.grid.AutoSize()
		
		self.createGreenScale( 15 )
		self.SetDoubleBuffered( True )
		self.SetSizer( vs )
	
	greenScale = [
		wx.Colour(int(c[1:3],16),int(c[3:5],16),int(c[5:7],16)) for c in reversed(
			'#6AA661,#6EAC65,#72B268,#76B86C,#7BBE70,#7FC574,#83CB77,#87D17B,#8CD87F,#90DE83,#95E587,#99EB8B,#9EF28F,#A2F893,#A7FF96'.split(',')
		)
	]
	def createGreenScale( self, alertETA ):
		self.colourMap = {}
		for i in xrange(alertETA):
			self.colourMap[i]			= self.greenScale[i]
			self.colourMap[-i]			= self.greenScale[0]
			self.colourMap[-alertETA-i]	= self.greenScale[i]
	
	def resetTimer( self ):
		if self.timer.IsRunning():
			return
		race = Model.race
		if race and race.isRunning() and self.IsShown():
			tRace = race.curRaceTime()
			self.timer.StartOnce( int((1.0 - modf(tRace)[0]) * 1000.0) )
	
	def OnTimer( self, event ):
		self.refreshETA()
		self.resetTimer()
		
	def setICategory( self, iCategory ):
		self.iCategory = iCategory
		wx.CallAfter( self.refresh )
	
	def refreshCategories( self, race ):
		categories = race.getCategories( startWaveOnly=False, publishOnly=True )
		while len(categories) > len(self.categoryButtons):
			b = wx.Button( self )
			b.Bind( wx.EVT_BUTTON, lambda e, i=len(self.categoryButtons): self.setICategory(i) )
			self.categoryButtons.append( b )
		
		if self.iCategoryButtonMax == len(categories) and all(b.GetLabel().endswith(c.fullname)  for c, b in zip(categories, self.categoryButtons)):
			return categories
			
		for b, c in zip(self.categoryButtons, categories):
			b.SetLabel( u' ' + c.fullname )
		for b in self.categoryButtons[len(categories):]:
			b.Show( False )
			
		self.wrapCategories.Clear()
		for b in self.categoryButtons[:len(categories)]:
			self.wrapCategories.Add( b, flag=wx.ALL, border=4 )
		self.iCategoryButtonMax = len(categories)
		self.wrapCategories.Layout()
		return categories
	
	def refreshETA( self ):
		race = Model.race
		if race and race.isRunning():
			tRace = race.curRaceTime()
		else:
			self.tExpected = [None] * len(self.tExpected)
		
		backgroundColour = wx.WHITE
		iCol = self.iCol[u'ETA']
		for row, et in enumerate(self.tExpected):
			if row >= self.grid.GetNumberRows():
				break
			colour = recordedColour if self.isRecorded[row] else unrecordedColour
			if et is not None:
				eta = et - tRace
				etaColour = self.colourMap.get(int(eta), self.greenScale[-1] if eta < 0.0 else None )
				colour = etaColour or colour
			self.grid.SetCellValue( row, iCol, Utils.formatTime(eta) if et else u'' )				
			self.grid.SetCellBackgroundColour( row, iCol, colour )
	
		categories = race.getCategories( startWaveOnly=False, publishOnly=True )
		for c, b in zip(categories, self.categoryButtons):
			results = GetResults( c )
			colour = unrecordedColour
			e = self.bibExpected.get( results[0].num, None ) if results else None
			if e is not None:
				eta = e.t - tRace
				etaColour = self.colourMap.get(int(eta), None)
				colour = etaColour or colour
			b.SetLabel( u'{} {}'.format(Utils.formatTime(eta) if e else u'', c.fullname) )
			b.SetBackgroundColour( colour )
	
	def refresh( self ):
		race = Model.race
		if race and race.isRunning():
			tRace = race.curRaceTime()
			self.expected, self.recorded = getExpectedRecorded()
		else:
			self.expected = self.recorded = []
		self.resetTimer()
		
		tRace = race.lastRaceTime()
		isRunning = race.isRunning()
		
		categories = self.refreshCategories( race )
		
		gridLastX, gridLastY = self.grid.GetViewStart()
		
		if not categories:
			self.grid.ClearGrid()
			return
		
		
		self.iCategory = min( self.iCategory, len(categories)-1 )
		category = categories[self.iCategory]
		results = GetResults( category )
		
		Finisher = Model.Rider.Finisher
		try:
			leader = results[0]
			leaderLap = find_le( leader.raceTimes, tRace )
			if leader.interp[leaderLap]:
				leaderLap -= 1
			tLeader = leader.raceTimes[leaderLap]
		except:
			leader = leaderLap = tLeader = None
			
		v = category.fullname
		try:
			lapsToGo = len(leader.raceTimes) - 1 - (leaderLap or 0)
		except Exception as e:
			lapsToGo = None
		if lapsToGo is not None:
			if lapsToGo == 0:
				v += u': {}'.format( _('Finish') )
			else:
				v += u': {} {}'.format( lapsToGo, _('laps to go') )
		if leader and hasattr(leader, 'speed'):
			v += u' {}'.format( leader.speed )
		
		self.title.SetLabel( v )
		
		if not results:
			Utils.AdjustGridSize( self.grid, 0, None )
			self.grid.ClearGrid()
			return
		
		self.bibExpected = { e.num:e for e in self.expected }
		bibRecorded = { e.num:e for e in self.recorded }
		bibETA = {}

		Utils.AdjustGridSize( self.grid, len(results), None )
		self.isRecorded = []
		
		self.tExpected = []
		iGroup = -1
		groupCount = defaultdict( int )
		group = []
		for row, rr in enumerate(results):
			self.grid.SetCellValue( row, self.iCol[u'Pos'], u'{}'.format(rr.pos) )
			self.grid.SetCellValue( row, self.iCol[u'Bib'], u'{}'.format(rr.num) )
			self.grid.SetCellValue( row, self.iCol[u'Name'],
				u'{} {}'.format(getattr(rr,'FirstName',u''), getattr(rr,'LastName',u'')).strip()
			)
			self.grid.SetCellValue( row, self.iCol[u'Team'], getattr(rr,'Team',u'') )
			self.grid.SetCellValue( row, self.iCol[u'Gap'], rr.gap )
			e = self.bibExpected.get(rr.num, None) if rr.status == Finisher else None
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
			
			self.tExpected.append( e.t if e else None )
			group.append( iGroup+1 )
			groupCount[iGroup+1] += 1
			self.grid.SetCellValue( row, self.iCol[u'ETA'], Utils.formatTime(eta) if e else u'' )
			
			e = bibRecorded.get( rr.num, None )
			if not isRunning or (leaderLap == 1 or (e and tLeader is not None and e.t >= tLeader)):
				self.isRecorded.append( True )
			else:
				self.grid.SetCellValue( row, self.iCol[u'Pos'], u'{}{}'.format(self.grid.GetCellValue(row, self.iCol[u'Pos']), recordedChar) )
				self.isRecorded.append( False )
			
			rowColour = recordedColour if self.isRecorded[-1] else unrecordedColour
			for c in xrange(len(self.cols)):
				self.grid.SetCellBackgroundColour( row, c, rowColour )
		
		gCur = 0
		gLast = None
		gColIndex = 0
		groupColour = None
		iCol = self.iCol[u'Group']
		for row, g in enumerate(group):
			self.grid.SetCellValue( row, iCol, u'' )
			if groupCount[g] == 1:
				continue
			if g == gLast:
				self.grid.SetCellBackgroundColour( row, iCol, groupColour )
				continue
				
			gLast = g
			groupColour = self.groupColours[gColIndex%len(self.groupColours)]
			groupTextColour = self.groupTextColours[gColIndex%len(self.groupTextColours)]
			gColIndex += 1
			gCur += 1
			self.grid.SetCellValue( row, iCol, u'{} [{}]'.format(gCur, groupCount[g],) )
			self.grid.SetCellBackgroundColour( row, iCol, groupColour )
			self.grid.SetCellTextColour( row, iCol, groupTextColour )
		
		self.refreshETA()
		self.grid.AutoSize()
		self.grid.Scroll( gridLastX, gridLastY )
		self.GetSizer().Layout()
				
	def commit( self ):
		pass
		
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,200))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	announcer = Announcer(mainWin)
	announcer.refresh()
	mainWin.Show()
	app.MainLoop()
