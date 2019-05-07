import wx
import six
import random
import bisect
import sys
import math

def makeColourGradient(frequency1, frequency2, frequency3,
                        phase1, phase2, phase3,
                        center = 128, width = 127, len = 50 ):
	fp = [(frequency1,phase1), (frequency2,phase2), (frequency3,phase3)]	
	grad = [wx.Colour(*[int(math.sin(f*i + p) * width + center) for f, p in fp]) for i in six.moves.range(len+1)]
	return grad[1:]
	
def makePastelColours( len = 50 ):
	return makeColourGradient(2.4,2.4,2.4,0,2,4,128,127,len+1)

def lighterColour( c ):
	rgb = c.Get( False )
	return wx.Colour( *[int(v + (255 - v) * 0.6) for v in rgb] )

def ShimazakiMethod( data, minN = 2, maxN = None ):
	# From shimazaki@brain.riken.jp
	dataMin = float(min(data))
	T = float(max(data)) - dataMin
	dataCount = float(len(data))
	
	# Default return: all data points in one bin.
	best = ([len(data)], sys.float_info.max, 1, T)

	for N in six.moves.range(minN, min(len(data), maxN or len(data))):
		width = T / N
		bins = [0] * N
		for x in data:
			try:
				bins[int((x-dataMin) / width)] += 1
			except IndexError:
				bins[-1] += 1
		
		kBar = dataCount / N
		v = math.fsum((k - kBar)**2 for k in bins) / N
		cost = (2.0 * kBar - v) / (width ** 2)
		if cost < best[1]:
			best = (bins, cost, N, width)

	return best
	
def BinByInterval( data, width, minN = 2 ):
	dataMin = float(min(data))
	N = int((float(max(data)) - dataMin) / width) + 1
	bins = [0 for i in six.moves.range(N)]
	for x in data:
		try:
			bins[int((x-dataMin) / width)] += 1
		except IndexError:
			bins[-1] += 1
	return bins, 0.0, N, width

def BinBySecond( data, minN = 2, maxN = None ):
	return BinByInterval( data, 1.0, minN )

def BinBy30Second( data, minN = 2, maxN = None ):
	return BinByInterval( data, 30.0, minN )

def BinByMinute( data, minN = 2, maxN = None ):
	return BinByInterval( data, 60.0, minN )

def BinBy5Minute( data, minN = 2, maxN = None ):
	return BinByInterval( data, 60.0*5.0, minN )
			
class Histogram(wx.Control):
	BinFunc = [ShimazakiMethod, BinBySecond, BinBy30Second, BinByMinute, BinBy5Minute]
	BinOptionAuto, BinOptionBySecond, BinOptionBy30Second, BinOptionByMinute, BinOptionBy5Minute = list(six.moves.range(len(BinFunc)))
	
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="LineGraph"):
		
		wx.Control.__init__(self, parent, id, pos, size, style, validator, name)
		self.SetBackgroundColour('white')

		self.binOption = self.BinOptionAuto
		self.data = None
		self.bins = None
		self.binWidth = None
		self.rectField = None
		self.iSelect = None
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_MOTION, self.OnMove )
		
	def DoGetBestSize(self):
		return wx.Size(100, 50)
		
	def SetBinOption( self, option ):
		if option < 0:
			option = 0
		if option >= len(self.BinFunc):
			option = len(self.BinFunc) - 1
		self.binOption = option
		self.setBins()
		self.Refresh()

	def SetForegroundColour(self, colour):
		wx.Control.SetForegroundColour(self, colour)
		self.Refresh()

	def SetBackgroundColour(self, colour):
		wx.Control.SetBackgroundColour(self, colour)
		self.Refresh()
		
	def GetDefaultAttributes(self):
		return wx.StaticText.GetClassDefaultAttributes()

	def ShouldInheritColours(self):
		return True
	
	def getIData( self, x, y ):
		if not self.bins or not self.rectField:
			return None
		boxWidth = self.rectField[2] / len(self.bins)
		boxHeight = self.rectField[3] / self.barMax
		b = int((x - self.rectField[0]) / boxWidth)
		h = self.barMax - 1 - int((y - self.rectField[1]) / boxHeight)
		return self.coords.get( (b, h), None )

	def OnMove( self, event ):
		iSelectNew = self.getIData( event.GetX(), event.GetY() )
		if iSelectNew != self.iSelect:
			self.iSelect = iSelectNew
			self.Refresh()
	
	def setBins( self ):
		if not self.data:
			return
		self.dataMax = max(self.data)
		self.dataMin = min(self.data)
		self.bins, _, _, self.binWidth = self.BinFunc[self.binOption]( self.data )
		self.barMax = max(self.bins)
	
	def SetData( self, data, label, category, binOption=BinOptionAuto ):
		self.binWidth = 60.0
		self.binOption = binOption
		self.bins = None
		self.iSelect = None
		self.data = []
		self.label = [six.text_type(lab) for lab in label]
		self.category = [six.text_type(cat) for cat in category]
		if data:
			self.data = [float(x) for x in data]
			self.setBins()
		while len(self.label) < len(self.data):
			self.label.append( u'' )
		while len(self.category) < len(self.data):
			self.category.append( u'' )
		self.categoryColor = makePastelColours( len(set(category)) )
		self.categoryMap = {}
		i = 0
		for c in self.category:
			if c not in self.categoryMap:
				self.categoryMap[c] = i
				i += 1
		self.Refresh()
		
	def OnPaint(self, event):
		dc = wx.PaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def Draw(self, dc):		
		size = self.GetClientSize()
		width = size.width
		height = size.height
		tickBorder = 4
		
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		if not self.bins or width < 50 or height < 50 or self.dataMax == self.dataMin:
			return

		textWidth, textHeight = dc.GetTextExtent( u'00:00' if self.dataMax < 60*60 else u'00:00:00' )
			
		xLeft = dc.GetTextExtent( six.text_type(self.barMax) )[0] + 4 + tickBorder
		xRight = width - 8 - tickBorder
		yBottom = height - textHeight - 8
		yTop = textHeight + 8

		# Draw the horizontal label.
		# Find some reasonable tickmarks for the x axis.
		numlabel = (xRight - xLeft) / (textWidth * 1.5)
		d = (self.dataMax - self.dataMin) / float(numlabel)
		intervals = [1, 2, 5, 10, 15, 20, 30, 1*60, 2*60, 5*60, 10*60, 15*60, 20*60, 30*60, 1*60*60, 2*60*60, 4*60*60, 8*60*60, 12*60*60, 24*60*60]
		d = intervals[bisect.bisect_left(intervals, d, 0, len(intervals)-1)]
		dFactor = (xRight - xLeft) / (self.dataMax - self.dataMin)
		tStart = int(self.dataMin)
		tStart -= tStart % d
		if tStart < int(self.dataMin):
			tStart += d
		dc.SetPen(wx.Pen('light gray', 1))
		for t in six.moves.range(tStart, int(self.dataMax), d):
			x = xLeft + (t - self.dataMin) * dFactor
			if x < xLeft:
				continue
			if t < 60*60:
				s = '{}:{:02d}'.format((t / 60), t%60)
			else:
				s = '{}:{:02d}:{:02d}'.format(t/(60*60), (t / 60)%60, t%60)
			w, h = dc.GetTextExtent(s)
			dc.DrawText( s, x - w/2, yBottom + 4)
			dc.DrawText( s, x - w/2, 0 + 4 )
			dc.DrawLine( x, yBottom+2, x, yTop )
		
		# Find some reasonable tickmarks for the y axis.
		numlabel = float(yBottom - yTop) / (textHeight * 3)
		d = self.barMax / numlabel
		intervals = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500]
		d = intervals[bisect.bisect_left(intervals, d, 0, len(intervals)-1)]
		dFactor = (yBottom - yTop) / float(self.barMax)
		dc.SetPen(wx.Pen('light gray', 1))
		for i in six.moves.range(0, self.barMax+1, d):
			s = u'{}'.format(i)
			y = yBottom - int(i * dFactor)
			w, h = dc.GetTextExtent(s)
			dc.DrawText( s, xLeft - w - 2 - tickBorder, y-textHeight/2 - 1)
			dc.DrawLine( xLeft, y, xRight + tickBorder, y )

		# Draw the data rectangles.
		pen = wx.Pen('dark gray', 1)
		dc.SetPen( pen )
		
		rSelect = None
		self.rectField = (xLeft, yTop, float(xRight-xLeft), float(yBottom-yTop))
		boxWidth = self.rectField[2] / len(self.bins)
		boxHeight = self.rectField[3] / self.barMax
		lenBins = len(self.bins)
		iBin = [0 for i in six.moves.range(lenBins)]
		xBin = [xLeft + int(i * boxWidth) for i in six.moves.range(len(self.bins)+1)]
		yHeight = [yBottom - int(i * boxHeight) for i in six.moves.range(self.barMax+1)]
		self.coords = {}
		brushes = [wx.Brush(c) for c in self.categoryColor]
		for i, (v, lab, cat) in enumerate(zip(self.data, self.label, self.category)):
			dc.SetBrush( brushes[self.categoryMap[cat]] )
			b = min(lenBins-1, int((v-self.dataMin) / self.binWidth))
			self.coords[(b, iBin[b])] = i
			iBin[b] += 1
			r = wx.Rect( xBin[b], yHeight[iBin[b]], xBin[b+1] - xBin[b], yHeight[iBin[b]-1] - yHeight[iBin[b]] )
			if i == self.iSelect:
				rSelect = r
				dc.SetPen( wx.Pen(wx.Colour(255,255,0), 1) )
			dc.DrawRectangle( r )
			if i == self.iSelect:
				dc.SetPen( pen )
		
		# draw the baseline
		dc.SetPen(wx.Pen('black', 2))
		dc.DrawLine(xLeft-tickBorder, yBottom, xRight+tickBorder, yBottom)
		
		# draw the hoverhelp
		if rSelect:
			t = self.data[self.iSelect]
			if t < 60:
				s = '{:.2f}'.format( t )
			else:
				t = int(t)
				if t < 60*60:
					s = '{}:{:02d}'.format((t/60), t%60)
				else:
					s = '{}:{:02d}:{:02d}'.format(t/(60*60), (t/60)%60, t%60)

			label = self.label[self.iSelect]
			category = self.category[self.iSelect]
			
			margin = 4
			widthMax = max( dc.GetTextExtent(v)[0] for v in (s, label, category) ) + margin * 2
			textWidth, textHeight = dc.GetTextExtent( s )
			heightMax = textHeight * 3 + margin * 2
			
			rHover = wx.Rect( rSelect.GetX() + rSelect.GetWidth() // 2 - widthMax, rSelect.GetY(), widthMax, heightMax )
			if rHover.GetLeft() < 0:
				rHover.SetX( 0 )
			if rHover.GetBottom() > height:
				rHover.SetY( height - rHover.GetHeight() )
			
			dc.SetPen( wx.Pen('black', 1) )
			dc.SetBrush( wx.Brush(wx.Colour(255,255,153)) )
			dc.DrawRectangle( rHover )
			
			xLeft = rHover.GetLeft() + margin
			yCur = rHover.GetY() + margin
			for v in (s, label, category):
				dc.DrawText( v, xLeft, yCur )
				yCur += textHeight
		
	def OnEraseBackground(self, event):
		pass
		
if __name__ == '__main__':
	# Data from Old Faithful
	data = [float(x) for x in 
'''4.37 3.87 4.00 4.03 3.50 4.08 2.25 4.70 1.73 4.93 1.73 4.62
3.43 4.25 1.68 3.92 3.68 3.10 4.03 1.77 4.08 1.75 3.20 1.85
4.62 1.97 4.50 3.92 4.35 2.33 3.83 1.88 4.60 1.80 4.73 1.77
4.57 1.85 3.52 4.00 3.70 3.72 4.25 3.58 3.80 3.77 3.75 2.50
4.50 4.10 3.70 3.80 3.43 4.00 2.27 4.40 4.05 4.25 3.33 2.00
4.33 2.93 4.58 1.90 3.58 3.73 3.73 1.82 4.63 3.50 4.00 3.67
1.67 4.60 1.67 4.00 1.80 4.42 1.90 4.63 2.93 3.50 1.97 4.28
1.83 4.13 1.83 4.65 4.20 3.93 4.33 1.83 4.53 2.03 4.18 4.43
4.07 4.13 3.95 4.10 2.72 4.58 1.90 4.50 1.95 4.83 4.12'''.split()]

	data = sorted(60.0*60.0 + random.normalvariate(10.0*60.0, 5.0*60.0) for i in six.moves.range(100))

	optimal = ShimazakiMethod( data )
	sys.stdout.write( '{}\n'.format(optimal) )
	
	bins, cost, N, width = optimal
	
	xMin = min(data)
	hMax = max(bins)
	hFactor = 1 if hMax < 40 else 40.0 / hMax
	for i, h in enumerate(bins):
		sys.stdout.write( '{:9.3f} {:9.3f}: {:6d}: {}\n'.format(xMin + i * width, xMin + (i+1) * width, h, '*' * int(h * hFactor)) )
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="Histogram", size=(600,400))
	histogram = Histogram(mainWin)
	mainWin.SetDoubleBuffered(True)

	random.seed( 10 )
	t = 55*60
	tVar = t * 0.15
	#histogram.SetData( [random.normalvariate(t, tVar) for x in six.moves.range(90)] )
	histogram.SetData( data, [], [random.randint(0,5) for d in data] )

	mainWin.Show()
	app.MainLoop()
