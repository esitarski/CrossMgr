import wx
from collections import defaultdict
from bisect import bisect_right

import Model
from GetResults import GetResults
import Utils

def LapsToGoCount( t=None ):
	# Returns a dict indexed by category with a list of (lapsToGo, count).
	ltgc = defaultdict( list )
	
	race = Model.race
	if not race or race.isUnstarted() or race.isFinished():
		return ltgc

	if not t:
		t = race.curRaceTime()

	Finisher = Model.Rider.Finisher
	lapsToGoCountCategory = defaultdict( int )
	for category in race.getCategories():
		for rr in GetResults(category):
			if rr.status != Finisher or not rr.raceTimes:
				break
			try:
				tSearch = race.riders[rr.num].raceTimeToRiderTime( t )
			except KeyError:
				continue
			
			if rr.raceTimes[-1] <= tSearch or not (lap := bisect_right(rr.raceTimes, tSearch) ):
				continue
			
			lapsToGoCountCategory[len(rr.raceTimes) - lap] += 1
		
		ltgc[category] = sorted( lapsToGoCountCategory.items(), reverse=True )
		lapsToGoCountCategory.clear()
		
	return ltgc

class lapsToGoCountGraph( wx.Control ):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="LapsToGoGraph"):
		
		super().__init__(parent, id, pos, size, style, validator, name)
		
		self.SetBackgroundColour(wx.WHITE)
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		#self.Bind(wx.EVT_MOTION, self.OnMove )

	def DoGetBestSize(self):
		return wx.Size(128, 128)

	def SetForegroundColour(self, colour):
		wx.Panel.SetForegroundColour(self, colour)
		self.Refresh()
		
	def SetBackgroundColour(self, colour):
		wx.Panel.SetBackgroundColour(self, colour)
		self.Refresh()
		
	def ShouldInheritColours(self):
		return True

	def OnPaint(self, event ):
		dc = wx.PaintDC(self)
		self.Draw(dc)
	
	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def Draw( self, dc ):
		size = self.GetClientSize()
		width, height = size.width, size.height
		
		backColour = self.GetBackgroundColour()
		greyColour = wx.Colour( 196, 196, 196 )
		
		greyPen = wx.Pen( greyColour )

		backBrush = wx.Brush(backColour, wx.SOLID)
		greyBrush = wx.Brush( greyColour, wx.SOLID )
		
		lightGreyBrush = wx.Brush( wx.Colour(220,220,220), wx.SOLID )

		dc.SetBackground(backBrush)
		dc.Clear()
				
		lapsToGoCount = LapsToGoCount()
		if not lapsToGoCount or width < 100 or height < 64:
			return
			
		race = Model.race
		categories = race.getCategories()
		
		xLeft = int( width * 0.03 )
		xRight = width - xLeft
		yTop = int( height * 0.03 )
		yBottom = height - yTop

		catHeight = int( (yBottom-yTop) / len(categories) )
		catFieldHeight = int( catHeight * 0.75 )
		catLabelHeight = catHeight - catFieldHeight
		
		catLabelFontHeight = int(catLabelHeight * 0.8)
		catLabelFont = wx.Font( wx.FontInfo(catLabelFontHeight).FaceName('Helvetica') )
		catLabelMargin = int( (catLabelHeight - catLabelFontHeight) / 2 )

		yCur = yTop
		for cat in categories:
			# Draw the lines.
			dc.SetPen( greyPen )
			dc.DrawLine( xLeft, yCur + catFieldHeight, xLeft, yCur )
			dc.DrawLine( xRight, yCur + catFieldHeight, xRight, yCur )
			dc.DrawLine( xLeft, yCur + catFieldHeight, xRight, yCur + catFieldHeight )
			dc.DrawLine( xLeft, yCur, xRight, yCur )
			
			# Draw the lap bars.
			ltg = lapsToGoCount[cat]
			barCount = 1
			if ltg:
				barCount = ltg[0][0] - ltg[-1][0] + 1
				
			# Compute the barwidths so they take the entire horizontal line.
			barWidth = (xRight - xLeft) / barCount
			barX = [round( xLeft + i * barWidth ) for i in range(barCount)]
			barX.append( xRight )
			
			# Draw the bars and labels.
			countTotal = sum( count for lap, count in ltg )
			dc.SetPen( wx.BLACK_PEN )
			dc.SetBrush( wx.Brush(wx.Colour(173, 216, 230), wx.SOLID) )
			for lap, count in ltg:
				barHeight = round( catFieldHeight * count / countTotal )
				i = ltg[0][0] - lap
				dc.DrawRectangle( barX[i], yCur + catFieldHeight - barHeight, barX[i+1] - barX[i], barHeight )
				s = f'{count} @ {lap} {_("to go")}'
				y = yCur + catHeight - catLabelMargin - catLabelFontHeight
				tWidth = dc.GetTextExtent( s ).width
				x = barX[i] + (barX[i+1] - barX[i] - tWidth) // 2
				dc.DrawText( s, x, y )
					
			# Draw the category label with the on course total.
			onCourse = countTotal - (ltg[-1][1] if ltg and ltg[-1][0] == 0 else 0)
			finished = countTotal - onCourse
			dc.DrawText( f'{cat.fullname}: {onCourse} {_("on course")}, {finished} {_("finished")}', xLeft + catLabelMargin, yCur + catLabelMargin )
			
			yCur += catHeight
			
		
		
			
	
	def OnEraseBackground(self, event):
		# This is intentionally empty.
		pass
	
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	ltg = lapsToGoCountGraph( mainWin )
	mainWin.Show()
	app.MainLoop()
