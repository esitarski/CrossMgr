import wx
from collections import defaultdict
from bisect import bisect_right

import Model
from GetResults import GetResults
import Utils

from collections.abc import Iterable

class DCStyle:
	# Class to support setting wxPython dc elements, and restoring them from a "with" statement.
	#
	# Example:
	#
	# ...
	# dc.SetPen( wx.RED_PEN )
	# dc.SetBrush( wx.WHITE_BRUSH )
	# ...
	#
	# with DCStyle( dc, Pen=wx.BLACK_PEN, Brush=wx.TRANSPARENT_BRUSH ):
	#    ... do some drawing in the DC using the black Pen and and transparent Brush.
	#    ... other settings of the dc will remain unchanged.
	#    ... do not use SetPen or SetBrush in the "with" block.
	#
	# ... Pen and Brush are automatically restored to their previous values (red, white).
	#
	# Explanation: The Pen and Brush are set to the new values inside the "with".
	# After the "with" block, the Pen and Brush are restored to the previous values.
	#
	# It is imperative that you do not modify elements of the dc state inside the "with" block
	# (eg. SetPen, SetBrush).  Otherwise, they may not be restored.
	#
	# If you with to use Set within the block, you can force them to be restored by specifying None
	# as the value.  For example:
	#
	# with DCStyle( dc, Pen=None, Brush=None ):
	#    dc.SetPen( wx.BLACK_PEN )
	#    dc.SetBrush( wx.TRANSPARENT_BRUSH )
	#    ...
	#    dc.SetBrush( wx.RED_BRUSH )
	#    .. OK to call SetPen and SetBrush in the block as we indicated None as the values.
	# 
	# When DCStyle is used without any keyword arguments, it restores the full state of the dc after the "with" block.
	# This allows you to change any state in the dc conventionally:
	#
	# Example:
	#
	# with DCStyle( dc ):
	#    dc.SetPen( wx.BLACK_PEN )
	#    dc.SetBrush( wx.TRANSPARENT_BRUSH )
	#    dc.SetBackground( wx.RED )
	#    ...
	#
	# The dc's full state will be restored after the "with".
	# Note: this is slower (and less clear, IMHO) than the previous examples.
	#
	# Finally, you can create DCStyle contexts ahead of time and reuse them.  For example:
	#
	# titleStyle = DCStyle( dc, Font=wx.Font(wx.FontInfo(24).Bold() )
	# linkStyle = DCStyle( dc, Font=wx.Font(wx.FontInfo(12).Italic().Underline()), TextForeground=wx.Colour(0,0,200) )
	#
	# Now you can do:
	#
	# with titleStyle:
	#    # draw a title
	#    dc.DrawText( "A Title', x, y )
	#
	# with linkStyle:
	#    # draw a link
	#    dc.DrawText( "link_to_cool_site', x, y )
	#
	# This make it easier to maintain formatting styles from a common location. 
	
	# Accepted arguments
	valid_kw = { 
		'AxisOrientation',
		'Background',
		'BackgroundMode',
		'Brush',
		'ClippingRegion',
		'DeviceClippingRegion',
		'DeviceOrigin',
		'Font',
		'LayoutDirection',
		'LogicalFunction',
		'LogicalOrigin',
		'LogicalScale',
		'MapMode',
		'Palette',
		'Pen',
		'TextBackground',
		'TextForeground',
		'TransformMatrix',
		'UserScale',
	}
	
	def __init__(self, dc, /, **kwargs):
		self.dc = dc
		if kwargs:
			# Check for invalid state parameters.
			if not all( k in self.valid_kw for k in kwargs.keys() ):
				for k in kwargs.keys():
					if k not in self.valid_kw:
						raise ValueError( f'Invalid argument: "{k}"' )
			self.contextNew = kwargs.copy()

	def __enter__(self):
		if not hasattr(self, 'contextNew'):
			# Cache all current state values to restore on __exit__.
			self.settersRestore = [('Set'+k, getattr(self.dc, 'Get'+k)()) for k in self.valid_kw]
		else:
			# Only cache what is different from the current dc.
			self.settersRestore = []
			for k, vNew in self.contextNew.items():
				if (vCur := getattr(self.dc, 'Get'+k)()) != vNew:
					funcName = 'Set' + k
					self.settersRestore.append( (funcName, vCur) )
					if isinstance(vNew, Iterable):
						getattr( self.dc, funcName )( *vNew )
					elif vNew is not None:
						getattr( self.dc, funcName )( vNew )
		return self

	def __exit__(self, *args):
		for funcName, vNew in self.settersRestore:
			if isinstance(vNew, Iterable):
				getattr( self.dc, funcName )( *vNew )
			else:
				getattr( self.dc, funcName )( vNew )

def LapsToGoCount( t=None ):
	ltgc = {}		# dict indexed by category with a list of (lapsToGo, count).
	sc = {}			# dict index by category with counts of each status.
	
	race = Model.race
	if not race or race.isUnstarted() or race.isFinished():
		return ltgc, sc

	if not t:
		t = race.curRaceTime()

	Finisher = Model.Rider.Finisher
	lapsToGoCountCategory = defaultdict( int )
	for category in race.getCategories():
		statusCategory = defaultdict( int )
		
		for rr in GetResults(category):
			statusCategory[rr.status] += 1
			if rr.status != Finisher or not rr.raceTimes:
				continue
			
			try:
				tSearch = race.riders[rr.num].raceTimeToRiderTime( t )
			except KeyError:
				continue
			
			if not (lap := bisect_right(rr.raceTimes, tSearch) ):
				continue
			lap -= 1
			
			lapsToGoCountCategory[len(rr.raceTimes) - lap - 1] += 1
		
		ltgc[category] = sorted( lapsToGoCountCategory.items(), reverse=True )
		lapsToGoCountCategory.clear()
		
		sc[category] = statusCategory

	return ltgc, sc

class LapsToGoCountGraph( wx.Control ):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="LapsToGoGraph"):
		
		super().__init__(parent, id, pos, size, style, validator, name)
		
		#self.barBrushes = [wx.Brush(wx.Colour( int(c[:2],16), int(c[2:4],16), int(c[4:],16)), wx.SOLID) for c in ('D8E6AD', 'E6ADD8', 'ADD8E6')]
		self.barBrushes = [wx.Brush(wx.Colour( int(c[:2],16), int(c[2:4],16), int(c[4:],16)), wx.SOLID) for c in ('A0A0A0', 'D3D3D3', 'E5E4E2')]
		self.statusKeys = sorted( (k for k in Model.Rider.statusSortSeq.keys() if isinstance(k, int)), key=lambda k: Model.Rider.statusSortSeq[k] )
		
		self.SetBackgroundColour(wx.WHITE)
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_SIZE, self.OnSize)

	def DoGetBestSize(self):
		return wx.Size(64, 128)

	def SetForegroundColour(self, colour):
		super().SetForegroundColour( colour )
		self.Refresh()
		
	def SetBackgroundColour(self, colour):
		super().SetBackgroundColour( colour )
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
				
		lapsToGoCount, statusCount = LapsToGoCount()
		if not lapsToGoCount or width < 100 or height < 64:
			return
			
		race = Model.race
		categories = race.getCategories()
		
		catLabelFontHeight = min( 12, int(height * 0.1) )
		catLabelHeight = int( catLabelFontHeight * 2.5 )
		yTop = catLabelHeight
		xLeft = 0
		
		xRight = width - xLeft
		yBottom = height - yTop

		catHeight = int( (yBottom-yTop) / len(categories) )
		
		catFieldHeight = catHeight - catLabelHeight
		barFieldHeight = catFieldHeight - catLabelHeight
		
		catLabelFont = wx.Font( wx.FontInfo(catLabelFontHeight).FaceName('Helvetica') )
		catLabelFontBold = wx.Font( wx.FontInfo(catLabelFontHeight).FaceName('Helvetica').Bold() )
		catLabelMargin = int( (catLabelHeight - catLabelFontHeight) / 2 )

		Finisher = Model.Rider.Finisher
		def statusCountStr( sc, lap0Count ):
			statusNames = Model.Rider.statusNames
			translate = _
			t = []
			onCourseCount = 0
			for status in self.statusKeys:
				if count := sc.get(status, 0):
					if status == Finisher:
						onCourseCount = count - lap0Count
					sName = translate(statusNames[status].replace('Finisher','Competing'))
					t.append( f'{count}={sName}' )
			return f"{onCourseCount}={_('OnCourse')} | " + ' | '.join( t )

		titleStyle = DCStyle( dc, Font=catLabelFontBold )
		chartLineStyle = DCStyle( dc, Pen=greyPen, Brush=wx.TRANSPARENT_BRUSH )

		lap0Total = finisherTotal = 0
		yCur = yTop
		for cat in categories:
			# Draw the chart lines.
			with chartLineStyle:
				dc.DrawRectangle( xLeft, yCur, xRight-xLeft, catFieldHeight )
			
			# Draw the lap bars.
			ltg = lapsToGoCount[cat]
			barCount = 1
			if ltg:
				barCount = ltg[0][0] - ltg[-1][0] + 1
			
			finisherTotal += statusCount[cat].get( Finisher, 0 )
			
			# Compute the barwidths so they take the entire horizontal line.
			barWidth = (xRight - xLeft) / barCount
			barX = [round( xLeft + i * barWidth ) for i in range(barCount)]
			barX.append( xRight )
			barTextWidth = barWidth - 2
			
			# Draw the bars and labels.
			countTotal = sum( count for lap, count in ltg )
			dc.SetPen( greyPen )
			dc.SetFont( catLabelFont )
			lap0Count = 0
			for lap, count in ltg:
				if lap:
					s = f'{lap} {_("to go")}'
					tWidth = dc.GetTextExtent( s ).width
					if tWidth >= barTextWidth:
						s = f'{lap}'
						tWidth = dc.GetTextExtent( s ).width
				else:
					lap0Count = lap
					lap0Total += lap
					s = f'{_("Finished")}'
					tWidth = dc.GetTextExtent( s ).width
					if tWidth >= barTextWidth:
						s = f'{_("Fin")}'
						tWidth = dc.GetTextExtent( s ).width
				
				barHeight = round( barFieldHeight * count / countTotal )
				if barHeight < catLabelFontHeight:
					continue
				
				i = ltg[0][0] - lap
				dc.SetBrush( self.barBrushes[lap%len(self.barBrushes)] )
				dc.DrawRectangle( barX[i], yCur + catFieldHeight - barHeight, barX[i+1] - barX[i], barHeight )
				
				y = yCur + catHeight - catLabelMargin - catLabelFontHeight
				x = barX[i] + (barX[i+1] - barX[i] - tWidth) // 2
				dc.DrawText( s, x, y )

				s = f'{count}'
				tWidth = dc.GetTextExtent( s ).width
				y = min( yCur + catFieldHeight - catLabelFontHeight- catLabelFontHeight//4, yCur + catFieldHeight - barHeight + catLabelFontHeight//2 )
				x = barX[i] + (barX[i+1] - barX[i] - tWidth) // 2
				dc.DrawText( s, x, y )
					
			# Draw the category label with the status totals.
			with titleStyle:
				catText = f'{cat.fullname}'
				titleTextWidth = dc.GetTextExtent(catText).width
				dc.DrawText( catText, xLeft + catLabelMargin, yCur + catLabelMargin )
			dc.DrawText( f'{statusCountStr(statusCount[cat], lap0Count)}', xLeft + titleTextWidth + catLabelMargin*2, int(yCur + catLabelMargin) )
			
			yCur += catHeight
			
		with titleStyle:
			catText = f'{_("All")}'
			titleTextWidth = dc.GetTextExtent(catText).width
			dc.DrawText( catText, xLeft + catLabelMargin, catLabelFontHeight//2 )
		dc.DrawText( f'{finisherTotal-lap0Total}={_("OnCourse")}', xLeft + titleTextWidth + catLabelMargin*2, catLabelFontHeight//2 )
	
	def OnEraseBackground(self, event):
		# This is intentionally empty.
		pass
	
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	ltg = LapsToGoCountGraph( mainWin )
	mainWin.Show()
	app.MainLoop()
