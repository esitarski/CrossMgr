import wx
import random
import bisect
import copy
import sys

class LineGraph(wx.Control):
	def __init__(self, parent, id=wx.ID_ANY, startAtZero = False, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="LineGraph"):
		wx.Control.__init__(self, parent, id, pos, size, style, validator, name)
		self.SetBackgroundColour('white')
		self.data = None
		self.startAtZero = startAtZero
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
	def DoGetBestSize(self):
		return wx.Size(100, 50)

	def SetForegroundColour(self, colour):
		wx.Control.SetForegroundColour(self, colour)
		self.Refresh()

	def SetBackgroundColour(self, colour):
		wx.Control.SetBackgroundColour(self, colour)
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

	def SetData( self, data, interpolated = None, labels = None ):
		"""
		* data is a list of lists.  Each list is a data series.
		Example:
			data = [ [1,2,3], [4,5,6,7,8], [9, 10] ]
		The first series will be drawn on top.
		
		* interpolated is optional.
		Same dimensions at data, but with True/False.
		
		* labels are the names of the series.  Optional.
		"""
		self.data = None
		self.interpolated = None
		self.labels = None
		if data and any( s for s in data ):
			# Reverse the sequence of the data so we plot the 1st series on top.
			self.data = [[max(float(x),0.0) for x in s] for s in data]
			self.data.reverse()		# Ensures that the first series will be drawn last.
			self.dataMax = max(max(s) if s else -sys.float_info.max for s in self.data)
			self.dataMin = min(min(s) if s else  sys.float_info.max for s in self.data)
			self.seriesMax = max(len(s) for s in self.data)
			if interpolated:
				self.interpolated = copy.deepcopy(interpolated)
				self.interpolated.reverse()
			else:
				self.interpolated = [ [False] * len(s) for s in self.data ]
			if labels:
				self.labels = labels
				if len(self.labels) < len(self.data):
					self.labels = self.labels + [None] * (len(self.data) - len(self.labels))
				elif len(self.labels) > len(self.data):
					self.labels = self.labels[:len(self.data)]
				self.labels.reverse()
				
		self.Refresh()
	
	def OnPaint(self, event):
		#dc = wx.BufferedPaintDC(self)
		dc = wx.PaintDC(self)
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
		dc.SetBackground(backBrush)
		dc.Clear()
		
		if not self.data or width < 50 or height < 50:
			return
			
		ctx = wx.GraphicsContext.Create(dc)

		textWidth, textHeight = dc.GetTextExtent( '00:00' if self.dataMax < 60*60 else '00:00:00' )
		
		if len(self.data) == 1:
			colours = [wx.Colour(0, 0, 255, 1.0)]
		else:
			colours = [ wx.Colour(255, 0, 0),
						wx.Colour(0, 255, 0),
						wx.Colour(0, 0, 255),
						wx.Colour(255, 255, 0),
						wx.Colour(255, 0, 255),
						wx.Colour(0, 255, 255),
						wx.Colour(0, 0, 0) ]
			if len(self.data) < len(colours):
				colours = colours[:len(self.data)]
			colours.reverse()
			
		drawLabels = False
		legendLength = 30		# Length of the legend lines
		legendSep = 10			# Separations between legend entries
		legendLabelSep = 4		# Separation between legend line and label
		if self.labels:
			labelsWidth = sum(legendLength + legendSep + legendLabelSep + dc.GetTextExtent(lab)[0] for lab in self.labels)
			if labelsWidth <= width - 8:
				drawLabels = True
		
		xLeft = textWidth + 4
		xRight = width - 8
		yBottom = height - (textHeight + 8) * (2 if drawLabels else 1)
		yTop = textHeight + 8
			
		thick = int((xRight - xLeft) / float(max(1,self.seriesMax-1)))
		dataMaxRange = self.dataMax * 1.05
		dataMinRange = 0 if self.startAtZero else self.dataMin * 0.95
		dFactor = float(yBottom - yTop) / (dataMaxRange - dataMinRange)

		# Draw the legend.
		if drawLabels:
			x, y = xRight, height - textHeight - 4
			for i, lab in enumerate(self.labels):
				pen = wx.Pen( colours[i%len(colours)], 6 )
				pen.SetCap(wx.CAP_BUTT)
				dc.SetPen(pen)
				w, h = dc.GetTextExtent(lab)
				x -= w
				dc.DrawText( lab, x, y );
				x -= legendLength + legendLabelSep
				dc.DrawLine( x, y + textHeight/2, x + legendLength, y + textHeight/2 )
				x -= legendSep
		
		# Draw the lap labels and vertical lines.
		dc.SetPen(wx.Pen('light gray', 1))
		# Find some reasonable tickmarks.
		numLabels = float(xRight - xLeft) / (dc.GetTextExtent('{}'.format(self.seriesMax))[0] * 1.5)
		d = self.seriesMax / numLabels
		intervals = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500]
		d = intervals[bisect.bisect_left(intervals, d, 0, len(intervals)-1)]
		for i in xrange(d-1, self.seriesMax, d):
			x = xLeft + i * thick
			dc.DrawLine( x, yBottom+2, x, yTop );
			s = '{}'.format(i+1)
			w, h = dc.GetTextExtent(s)
			dc.DrawText( s, x - w/2, yBottom + 4)
			dc.DrawText( s, x - w/2, 0 + 4)
			
		# Draw the horizontal lines.
		# Find some reasonable tickmarks.
		dc.SetPen(wx.Pen('light gray', 1))
		numLabels = max( float(yBottom - yTop) / (textHeight * 3), 1 )
		d = (dataMaxRange - dataMinRange) / numLabels
		intervals = [1, 2, 5, 10, 15, 30, 1*60, 2*60, 5*60, 10*60, 15*60, 20*60, 30*60, 1*60*60, 2*60*60, 4*60*60, 8*60*60, 24*60*60]
		d = intervals[bisect.bisect_left(intervals, d, 0, len(intervals)-1)]
			
		for t in xrange(int(dataMinRange) - int(dataMinRange%d), int(dataMaxRange * 2), d):
			y = yBottom - (t - dataMinRange) * dFactor
			if y > yBottom:
				continue
			if y < yTop:
				break
			if t < 60*60:
				s = '%d:%02d' % ((t / 60), t%60)
			else:
				s = '%d:%02d:%02d' % (t/(60*60), (t / 60)%60, t%60)
			w, h = dc.GetTextExtent(s)
			dc.DrawText( s, textWidth - w, y-textHeight/2 - 2 )
			dc.DrawLine( xLeft-3, y, xRight, y )
		
		# Draw the baseline
		dc.SetPen(wx.Pen('black', 2))
		dc.DrawLine(xLeft, yBottom, xRight, yBottom)
		dc.DrawLine(xLeft, yBottom, xLeft, yTop)
	
		# Define a path for the indicator about the origin.
		radius = 12
		ctx.SetPen( wx.Pen( wx.Colour(128,128,128), 1 ) )
		ctx.SetBrush( ctx.CreateRadialGradientBrush( 0, - radius*0.50, 0, 0, radius + 1, wx.WHITE, wx.Colour(220,220,0) ) )
		path = ctx.CreatePath()
		path.MoveToPoint( 0, -radius )
		path.AddLineToPoint( -radius, 0 )
		path.AddLineToPoint( 0, radius )
		path.AddLineToPoint( radius, 0 )
		path.AddLineToPoint( 0, -radius )
			
		# Draw the data lines.
		for i, s in enumerate(self.data):
			pen = wx.Pen( colours[i%len(colours)], 6 )
			pen.SetCap(wx.CAP_ROUND)
			dc.SetPen(pen)
			points = []
			x = xLeft
			for d in s:
				y = yBottom - (d - dataMinRange) * dFactor
				points.append( wx.Point(x, y) )
				x += thick
			if points:
				dc.DrawLines( points );
			
			# Draw indicators for interpolated values.
			ctx.SetPen( wx.Pen( wx.Colour(128,128,128), 1 ) )
			for j, p in enumerate(points):
				if self.interpolated[i][j]:
					ctx.PushState()
					ctx.Translate( *p )
					ctx.DrawPath( path )
					ctx.PopState()
		
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	def GetData():
		# Data from Old Faithful
		d = '''4.37 3.87 4.00 4.03 3.50 4.08 2.25 4.70 1.73 4.93 1.73 4.62 
		 3.43 4.25 1.68 3.92 3.68 3.10 4.03 1.77 4.08 1.75 3.20 1.85 
		 4.62 1.97 4.50 3.92 4.35 2.33 3.83 1.88 4.60 1.80 4.73 1.77 
		 4.57 1.85 3.52 4.00 3.70 3.72 4.25 3.58 3.80 3.77 3.75 2.50 
		 4.50 4.10 3.70 3.80 3.43 4.00 2.27 4.40 4.05 4.25 3.33 2.00 
		 4.33 2.93 4.58 1.90 3.58 3.73 3.73 1.82 4.63 3.50 4.00 3.67 
		 1.67 4.60 1.67 4.00 1.80 4.42 1.90 4.63 2.93 3.50 1.97 4.28 
		 1.83 4.13 1.83 4.65 4.20 3.93 4.33 1.83 4.53 2.03 4.18 4.43 
		 4.07 4.13 3.95 4.10 2.27 4.58 1.90 4.50 1.95 4.83 4.12'''
		return [float(x) for x in d.split()]

	app = wx.App(False)
	mainWin = wx.Frame(None,title="LineGraph", size=(600,400))
	lineGraph = LineGraph(mainWin)

	random.seed( 10 )
	t = 55*60
	tVar = t * 0.15
	lineGraph.SetData( [[random.normalvariate(t, tVar) for x in xrange(9)],
						[random.normalvariate(t, tVar) for x in xrange(10)]] )
	#lineGraph.SetData( [[random.normalvariate(t, tVar) for x in xrange(9)]] )
	#lineGraph.SetData( [GetData()] )

	mainWin.Show()
	app.MainLoop()
