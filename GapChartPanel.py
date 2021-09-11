import wx
import sys
import math
import operator
from bisect import bisect_left
import Model
import Utils
from GanttChartPanel import makeColourGradient, makePastelColours, lighterColour
from GetResults import GetResults

from math import atan2, sin, cos, pi
def DrawArrowLine( dc, x0, y0, x1, y1, arrowFrom=True, arrowTo=True, arrowLength=16, arrowWidth=8 ):
	'''
		Draws a line with arrows in a regular wxPython DC.
		The line is drawn with the dc's wx.Pen.  The arrows are filled with the current Pen's colour.
		Edward Sitarski 2021.
	'''
	dc.DrawLine( x0, y0, x1, y1 )
	if x0 == x1 and y0 == y1:
		return
	
	# Set up the dc for drawing the arrows.
	penSave, brushSave = dc.GetPen(), dc.GetBrush()
	dc.SetPen( wx.TRANSPARENT_PEN )
	dc.SetBrush( wx.Brush(penSave.GetColour()) )
	
	# Compute the "to" arrow polygon.
	angle = atan2( y1 - y0, x1 - x0 )
	toCosAngle, toSinAngle = -cos(angle), -sin(angle)
	toArrowPoly = [
		(int(xp*toCosAngle - yp*toSinAngle + 0.5), int(yp*toCosAngle + xp*toSinAngle + 0.5)) for xp, yp in (
			(0,0),
			(arrowLength, arrowWidth/2),
			(arrowLength, -arrowWidth/2),
		)
	]
	
	# Draw the arrows.
	if arrowTo:
		dc.DrawPolygon( toArrowPoly, x1, y1 )
	if arrowFrom:
		dc.DrawPolygon( [(-x,-y) for x,y in toArrowPoly], x0, y0 )
	
	# Restore the dc.
	dc.SetPen( penSave )
	dc.SetBrush( brushSave )
		
class GapChartPanel(wx.Panel):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER,
				name="GapChartPanel" ):
		
		super().__init__(parent, id, pos, size, style, name)
		
		self.SetBackgroundColour(wx.WHITE)
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		
		self.data = []
		self.labels = []
		self.interp = []
		self.maxLaps = 0
		self.earliestLapTimes = []
		self.maximumGap = 0.0
		self.yTop = self.yBottom = 0
		self.xLeft = self.xRight = 0
		self.xMove = self.yMove = 0
		self.xDrag = self.yDrag = 0
		self.isDrag = False
		
		class MoveTimer( wx.Timer ):
			def __init__( self, cb ):
				super().__init__()
				self.cb = cb
			
			def Notify( self ):
				wx.CallAfter( self.cb )
		
		self.moveTimer = MoveTimer( self.Refresh )
		
		self.colours = makeColourGradient(2.4,2.4,2.4,0,2,4,128,127,500)
		
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_MOTION, self.OnMove)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)

	def DoGetBestSize(self):
		return wx.Size(128, 100)

	def SetForegroundColour(self, colour):
		wx.Panel.SetForegroundColour(self, colour)
		self.Refresh()
		
	def SetBackgroundColour(self, colour):
		wx.Panel.SetBackgroundColour(self, colour)
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

	def SetData( self, data, labels = None, interp = None, ):
		"""
		* data is a list of lists.  Each a list of race times.
		* labels are the names of the series.  Optional.
		"""
		self.data = data or []
		if data and any( s for s in data ):
			self.data = data
			if labels:
				self.labels = ['{}'.format(lab) for lab in labels]
				if len(self.labels) < len(self.data):
					self.labels = self.labels + [''] * (len(self.data) - len(self.labels))
				elif len(self.labels) > len(self.data):
					self.labels = self.labels[:len(self.data)]
			else:
				self.labels = [''] * len(data)
		self.interp = interp or []
			
		# Find the first lap times.
		self.earliestLapTimes = []
		if data:
			self.maxLaps = max( len(times) for times in data )
			self.earliestLapTimes = [min( times[iLap] for times in data if len(times) > iLap ) for iLap in range(self.maxLaps)]
		
		self.maxLaps = max( self.maxLaps, 2 )
		# Add a sentinal to avoid edge cases.
		self.earliestLapTimes.append( sys.float_info.max )
		
		# Find the maximum gap.
		self.maximumGap = 0.0
		for times in self.data:
			iLap = 0
			for t in times:
				while not (self.earliestLapTimes[iLap] <= t < self.earliestLapTimes[iLap+1]):
					iLap += 1
				self.maximumGap = max( self.maximumGap, t - self.earliestLapTimes[iLap] )
		
		self.interp = interp
		self.Refresh()
		
	def OnPaint(self, event ):
		dc = wx.PaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.OnLeave( event )
		self.Refresh()
		event.Skip()
		
	def OnLeave(self, event):
		self.xMove = self.yMove = self.xDrag = self.yDrag = 0
		self.isDrag = False
		if self.moveTimer.IsRunning():
			self.moveTimer.Stop()
		event.Skip()
		
	def OnLeftDown( self, event ):
		self.isDrag = True
		
	def OnLeftUp( self, event ):
		self.isDrag = False
		self.xDrag = self.yDrag = 0
		
	def OnMove( self, event ):
		if self.isDrag:
			self.xDrag, self.yDrag = event.GetPosition()
		else:
			self.xMove, self.yMove = event.GetPosition()
		if not self.moveTimer.IsRunning():
			self.moveTimer.StartOnce( 50 )
			
	intervals = (1, 2, 5, 10, 15, 20, 30, 1*60, 2*60, 5*60, 10*60, 15*60, 20*60, 30*60, 1*60*60, 2*60*60, 4*60*60, 6*60*60, 8*60*60, 12*60*60) + tuple(24*60*60*k for k in range(1,200))
	def Draw( self, dc ):
		size = self.GetClientSize()
		width = size.width
		height = size.height
		
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		greyPen = wx.Pen( wx.Colour(200, 200, 200), 1 )
		dc.SetBackground(backBrush)
		dc.Clear()
		
		lappedText = '(L) '
		
		tooSmall = (width < 50 or height < 24)
		
		if not self.data or tooSmall:
			self.empty = True
			if tooSmall:
				dc.SetPen( wx.BLACK_DASHED_PEN )
				dc.DrawLine( 0, height//2, width, height//2 )
			return
		
		self.empty = False
		
		# Draw the chart scale.
		border = min( width, height ) // 30
		scaleFontSize = 14
		scaleFont = wx.Font( (0, scaleFontSize), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		
		# Height of drawing field.
		self.yTop = yTop = border + scaleFontSize + border//2
		self.yBottom = yBottom = height - border - scaleFontSize - border//2 - scaleFontSize - border//2

		# Labels
		labelFontSize = min( scaleFontSize, max(1, int( 1.0/1.15 * (yBottom - yTop) / len(self.labels) )) )
		labelFont = wx.Font( (0, labelFontSize), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		
		dc.SetFont( labelFont )
		maxLabelWidth = max( dc.GetTextExtent(lappedText + label)[0] for label in self.labels )
		
		dc.SetFont( scaleFont )

		# Vertical scale
		scaleTick = 1
		for i in range(bisect_left(self.intervals, self.maximumGap/2), -1, -1):
			if self.intervals[i] * 4 < self.maximumGap:
				scaleTick = self.intervals[i]
				break
		
		tickText = []
		tickTextWidth = scaleTextHeight = 1
		tVertMax = 1
		for i in range(max(2,len(self.intervals))):
			t = scaleTick * i
			tVertMax = max( t, tVertMax )
			tickText.append( Utils.formatTimeGap(t) )
			tWidth, scaleTextHeight = dc.GetTextExtent( tickText[-1] )
			tickTextWidth = max( tickTextWidth, tWidth )
			if i >= 1 and t >= self.maximumGap:
				break
		
		# Width of the drawing field.		
		self.xLeft = xLeft = border + scaleTextHeight + border//2 + tickTextWidth + border//2
		self.xRight = xRight = width - 3*border - maxLabelWidth
		xMost = xRight - int((xRight - xLeft) / (self.maxLaps-1))

		# Vertical axis label.
		tWidth, tHeight = dc.GetTextExtent( _('Gap') )
		xText = border
		yText = yTop + (yBottom - yTop)//2 + tWidth//2
		dc.DrawRotatedText( _('Gap'), xText, yText, 90 )
		
		dc.SetPen( greyPen )

		# Vertical scale text.
		for i, text in enumerate(tickText):
			tWidth, tHeight = dc.GetTextExtent( text )
			xText = border + scaleTextHeight + border//2 + tickTextWidth - tWidth
			yText = yTop + i * (yBottom - yTop) // max(1,len(tickText)-1)
			dc.DrawText( text, xText, yText - labelFontSize//2 )
			dc.DrawLine( xLeft - 3, yText, xRight, yText )
		
		# Horizontal axis label.
		tWidth, tHeight = dc.GetTextExtent( _('Lap') )
		xText = xLeft + (xRight - xLeft)//2 - tWidth//2
		yText = height - border - tHeight
		dc.DrawText( _('Lap'), xText, yText )
		
		# Horizontal scale text.
		yText = height - border - scaleTextHeight*2 - border//2
		xTextRightLast = 0
		for lap in range(self.maxLaps):
			text = str(lap)
			tWidth, tHeight = dc.GetTextExtent( text )
			xText = xLeft + lap * (xRight - xLeft)//(self.maxLaps-1) - tWidth//2
			dc.DrawLine( xText + tWidth//2, yTop, xText + tWidth//2, yBottom+3 )
			if xText > xTextRightLast:
				dc.DrawText( text, xText, yText )
				dc.DrawText( text, xText, border )
				xTextRightLast = xText + tWidth + border
		
		# Border
		dc.DrawLines( ((xRight, yTop), (xLeft, yTop), (xLeft, yBottom), (xRight, yBottom)) )
		
		# Draw the gap lines and labels.
		dc.SetFont( labelFont )
		xText = xRight + border*2

		yDelta = yBottom - yTop
		points = []
		pointsLapped = []
		xytLabel = []
		for iData, times in enumerate(self.data):
			points.clear()
			pointsLapped.clear()
			wasLapped = False
			iLap = 0
			iLapLast = None
			for t in times:
				while not (self.earliestLapTimes[iLap] <= t < self.earliestLapTimes[iLap+1]):
					iLap += 1
				if iLapLast is not None and iLap != iLapLast + 1:
					wasLapped = True
					pointsLapped.append( len(points) )
				iLapLast = iLap
					
				gap = t - self.earliestLapTimes[iLap]
				y = int(yTop + yDelta * (gap / tVertMax))
				x = int(xLeft + iLap * (xRight - xLeft) / (self.maxLaps-1))
				points.append( (x, y) )
				
			colour = self.colours[iData % len(self.colours)]
			lineWidth = 3
			penSolid = wx.Pen( colour, lineWidth, wx.PENSTYLE_SOLID )
			penDashed = wx.Pen( colour, lineWidth, wx.PENSTYLE_SHORT_DASH )
			if len(points) > 1:
				if not pointsLapped:
					dc.SetPen( penSolid )
					dc.DrawLines( points )
				else:
					pLast = 0
					for p in pointsLapped:
						drawPoints = points[pLast:p]
						if len(drawPoints) >= 2:
							dc.SetPen( penSolid )
							dc.DrawLines( drawPoints )
						drawPoints = points[p-1:p+1]
						if len(drawPoints) >= 2:
							dc.SetPen( penDashed )
							dc.DrawLines( drawPoints )
						pLast = p + 1
			
			# Record the gap position, the label position, and the label.
			xytLabel.append( [*points[-1], points[-1][1], (lappedText if wasLapped else '') + self.labels[iData]] )

		# Sort by the finish gaps positions.
		xytLabel.sort( key=operator.itemgetter(1) )
		dc.SetPen( greyPen )

		# Construct a list of rectangles for each label so we can check for overlaps.
		# Default to putting the label next to the corresponding gap.
		labelLineHeight = int(labelFontSize*1.15)
		
		# Check the labels and reposition to remove overlaps.
		for p in range(len(xytLabel)):
			# Check if two adjacent labels overlap each other.
			foundConflict = False
			for b in range(len(xytLabel)-1):
				if xytLabel[b][2] + labelLineHeight > xytLabel[b+1][2]:
					foundConflict = True
					
					# Find the top of the conflict group
					for a in range(b, 0, -1):
						if xytLabel[a][2] > xytLabel[a-1][2] + labelLineHeight:
							break
					else:
						a = 0
						
					# Find the bottom of the conflict group
					for c in range(b, len(xytLabel)-1):
						if xytLabel[c][2] + labelLineHeight < xytLabel[c+1][2]:
							break
					else:
						c = len(xytLabel) - 1
					
					# Compute the least-squares error for the non-overlapping position for the conflict labels.
					tCentroid = sum( xytLabel[i][1] for i in range(a,c+1) ) / (c-a+1)
					y = tCentroid - labelLineHeight*(c-a) / 2
					
					# Ensure we don't go off the drawing area.
					if y < labelLineHeight:
						y = labelLineHeight
					elif y + labelLineHeight*(c-a) > height - labelLineHeight:
						y = height - labelLineHeight*(c-a+1)

					# Reposition the labels so they don't overlap.
					y = int(y)			
					for i in range(a,c+1):
						xytLabel[i][2] = y
						y += labelLineHeight
			
			if not foundConflict:
				break
			
		# Draw the labels in their optimal non-overlapping positions.
		border2 = border//2
		border4 = border//4
		labelFontSize2 = labelFontSize//2
		for x, y, t, label in xytLabel:
			yText = t - labelFontSize2
			dc.DrawLines( ((x, y), (x + border4, y), (xText - border2, yText + labelFontSize2), (xText - border4, yText + labelFontSize2)) )
			dc.DrawText( label, xText, yText )
		
		# Drawn the dynamic move lines.
		if self.yTop <= self.yMove <= self.yBottom and self.xLeft <= self.xMove <= self.xRight:
			gap = self.maximumGap * (self.yMove - self.yTop) / (self.yBottom - self.yTop)
			text = Utils.formatTimeGap( gap )
			tWidth, tHeight = dc.GetTextExtent( text )
			xText = border + scaleTextHeight + border2 + tickTextWidth - tWidth
			dc.SetPen( wx.BLACK_PEN )
			dc.SetBrush( wx.YELLOW_BRUSH )
			dc.DrawLine( self.xLeft - border2, self.yMove, self.xRight + border2, self.yMove )
			dc.DrawRoundedRectangle( xText - border4, self.yMove - labelFontSize2 - border4, tWidth + border2, tHeight + border2, border4 )
			dc.DrawText( text, xText, self.yMove - labelFontSize2 )
			
			if not (self.yTop <= self.yDrag <= self.yBottom and self.xLeft <= self.xDrag <= self.xRight):
				return
				
			gapDiff = abs( gap - self.maximumGap * (self.yDrag - self.yTop) / (self.yBottom - self.yTop) )
			text = Utils.formatTimeGap( gapDiff, highPrecision=True )
			tWidth, tHeight = dc.GetTextExtent( text )
			xText = border + scaleTextHeight + border2 + tickTextWidth - tWidth
			dc.SetBrush( wx.GREEN_BRUSH )
			dc.DrawLine( self.xLeft - border2, self.yDrag, self.xRight + border2, self.yDrag )
			dc.DrawRoundedRectangle( xText - border4, self.yDrag - labelFontSize2 - border4, tWidth + border2, tHeight + border2, border4 )
			dc.DrawText( text, xText, self.yDrag - labelFontSize2 )
			
			dc.SetPen( wx.Pen(wx.BLACK, 2) )
			DrawArrowLine( dc, self.xDrag, self.yMove, self.xDrag, self.yDrag, arrowWidth=12 )
			
	def OnEraseBackground(self, event):
		pass
		
if __name__ == '__main__':
	
	Model.setRace( Model.Race() )
	race = Model.getRace()
	race._populate()

	data = []
	labels = []
	interp = []
	category = None
	for num in race.riders.keys():
		category = race.getCategory( num )
		break
	for rr in GetResults( category ):
		data.append( rr.raceTimes )
		labels.append( str(rr.num) )
		interp.append( rr.interp )
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="GapChartPanel", size=(600,400))
	gapChart = GapChartPanel( mainWin )
	gapChart.SetData( data, labels, interp )

	mainWin.Show()
	app.MainLoop()
