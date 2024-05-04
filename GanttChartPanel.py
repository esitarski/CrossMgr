import wx
import random
import math
import sys
import bisect
import Utils
from PhotoFinish import hasPhoto

def SetScrollbarParameters( sb, thumbSize, rng, pageSize ):
	thumbSize = int(thumbSize)
	rng = int(rng)
	pageSize = int(pageSize)
	sb.SetScrollbar( min(sb.GetThumbPosition(), rng - thumbSize), thumbSize, rng, pageSize )

def makeColourGradient(frequency1, frequency2, frequency3,
                        phase1, phase2, phase3,
                        center = 128, width = 127, len = 50 ):
	fp = [(frequency1,phase1), (frequency2,phase2), (frequency3,phase3)]	
	grad = [wx.Colour(*[int(math.sin(f*i + p) * width + center) for f, p in fp]) for i in range(len+1)]
	return grad[1:]
	
def makePastelColours( len = 50 ):
	return makeColourGradient(2.4,2.4,2.4,0,2,4,128,127,len+1)

def lighterColour( c, factor = 0.6 ):
	rgb = c.Get( False )
	return wx.Colour( *[int(v + (255 - v) * factor) for v in rgb] )

def numFromLabel( s ):
	try:
		lastSpace = s.rfind( ' ' )
		if lastSpace >= 0:
			try:
				return int(s[lastSpace+1:])
			except ValueError:
				pass
		firstSpace = s.find( ' ' )
		if firstSpace < 0:
			return int(s)
		return int(s[:firstSpace])
	except Exception as e:
		return None

class KeyWrapper:
	def __init__( self, items, key ):
		self._items = items
		self._key = key

	def __len__(self):
		return len(self._items)

	def __getitem__(self, i):
		return self._key(self._items[i])
		
class GanttChartPanel(wx.Panel):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER,
				name="GanttChartPanel" ):
		
		super().__init__(parent, id, pos, size, style, name)
		
		self.SetBackgroundColour(wx.WHITE)
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		
		self.data = None
		self.labels = None
		self.status = None
		self.greyOutSet = None
		self.nowTime = None
		self.numSelect = None
		self.dClickCallback = None
		self.lClickCallback = None
		self.rClickCallback = None
		self.getNowTimeCallback = None
		self.minimizeLabels = False
		self.headerSet = set()
		self.xMove = -1
		self.yMove = -1
		self.moveIRider = None
		self.moveLap = None
		self.moveTimer = wx.Timer( self, wx.ID_ANY )
		
		self.barHeight = 8
		self.labelsWidthLeft = 8000
		self.xFactor = 1
		
		self.yellowColour = wx.Colour(220,220,0)
		self.orangeColour = wx.Colour(255,165,0)
		
		self.horizontalSB = wx.ScrollBar( self, style=wx.SB_HORIZONTAL )
		self.horizontalSB.Bind( wx.EVT_SCROLL, self.OnHorizontalScroll )
		self.verticalSB = wx.ScrollBar( self, style=wx.SB_VERTICAL )
		self.verticalSB.Bind( wx.EVT_SCROLL, self.OnVerticalScroll )
		self.scrollbarWidth = 16
		self.horizontalSB.Show( False )
		self.verticalSB.Show( False )
		
		self.colours = makeColourGradient(2.4,2.4,2.4,0,2,4,128,127,500)
		self.lighterColours = [lighterColour(c) for c in self.colours]
		
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_MOTION, self.OnMove)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)
		self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
		self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheel )
		
		self.Bind(wx.EVT_TIMER, self.OnMoveTimer, self.moveTimer)

	def OnWheel( self, event ):
		if not self.verticalSB.IsShown():
			return
		amt = event.GetWheelRotation()
		units = -amt / event.GetWheelDelta()
		sb = self.verticalSB
		pos = sb.GetThumbPosition() + units
		pos = round( min( max( pos, 0 ), sb.GetRange() - sb.GetThumbSize() ) )
		if pos != sb.GetThumbPosition():
			sb.SetThumbPosition( pos )
			self.OnVerticalScroll( event )
		
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

	def SetData( self, data, labels = None, nowTime = None, interp = None, greyOutSet = set(),
					numTimeInfo = None, lapNote = None, status = None,
					headerSet = None, earlyBellTimes = None ):
		"""
		* data is a list of lists.  Each list is a list of times.
		* labels are the names of the series.  Optional.
		"""
		self.data = None
		self.labels = None
		self.status = status
		self.nowTime = None
		self.greyOutSet = greyOutSet
		self.numTimeInfo = numTimeInfo
		self.lapNote = lapNote
		self.headerSet = headerSet or set()
		self.earlyBellTimes = earlyBellTimes
		if data and any( s for s in data ):
			self.data = data
			self.dataMax = max(max(s) if s else -sys.float_info.max for s in self.data)
			if labels:
				self.labels = ['{}'.format(lab) for lab in labels]
				if len(self.labels) < len(self.data):
					self.labels = self.labels + [None] * (len(self.data) - len(self.labels))
				elif len(self.labels) > len(self.data):
					self.labels = self.labels[:len(self.data)]
			else:
				self.labels = [''] * len(data)
				self.status = [''] * len(data)
			self.nowTime = nowTime
			
		self.interp = interp
		self.earlyBellTimes = earlyBellTimes or []
		self.Refresh()
	
	def OnPaint(self, event ):
		dc = wx.PaintDC(self)
		self.Draw(dc)

	def OnVerticalScroll( self, event ):
		self.Refresh()
		
	def OnHorizontalScroll( self, event ):
		self.Refresh()
		
	def OnSize(self, event):
		self.Refresh()
		event.Skip()
		
	def OnLeftClick( self, event ):
		if getattr(self, 'empty', True):
			return
		if not self.data:
			return
			
		iRider, iLap = self.getRiderLap( event )
		if iRider is None or iLap is None:
			return
		
		self.numSelect = numFromLabel( self.labels[iRider] )
		if self.getNowTimeCallback:
			self.nowTime = self.getNowTimeCallback()
		self.Refresh()
		lClickCallback = getattr(self, 'lClickCallback', None)
		if lClickCallback is not None:
			xPos, yPos = event.GetPosition()
			lClickCallback( xPos, yPos, self.numSelect, iRider, iLap, self.data[iRider][iLap] )
	
	def OnLeftDClick( self, event ):
		if getattr(self, 'empty', True):
			return
		iRider, iLap = self.getRiderLap( event )
		if iRider is None:
			return
		self.numSelect = numFromLabel( self.labels[iRider] )
		if self.numSelect is not None and self.dClickCallback:
			self.dClickCallback( self.numSelect )
	
	def OnMove( self, event ):
		# Set a timer to update the screen a few milliseconds after the mouse stops moving.
		# This prevents redraw performance problems.
		self.moveTimer.Start( 25, True )	# If the timer is already running, it will be stopped and restarted.
	
	def OnMoveTimer( self, event ):
		# Get latest mouse coordinates to eliminate last-minute movement errors.
		self.xMove, self.yMove = self.ScreenToClient(wx.GetMousePosition())
		self.moveIRider, self.moveLap = self.getRiderLapXY( self.xMove, self.yMove )
		self.Refresh()
	
	def getRiderLapXY( self, x, y ):
		if not self.data:
			return None, None
			
		y -= self.barHeight
		x -= self.labelsWidthLeft
		iRider = int(y / self.barHeight)
		if self.verticalSB.IsShown():
			iRider += self.verticalSB.GetThumbPosition()
		if not 0 <= iRider < len(self.data):
			return None, None

		t = x / self.xFactor
		if self.horizontalSB.IsShown():
			t += self.horizontalSB.GetThumbPosition()
		iLap = bisect.bisect_left( self.data[iRider], t )
		if not 1 <= iLap < len(self.data[iRider]):
			return iRider, None
			
		return iRider, iLap
		
	def getRiderLap( self, event ):
		x, y = event.GetPosition()
		return self.getRiderLapXY( x, y )
		
	def OnRightClick( self, event ):
		if getattr(self, 'empty', True):
			return
			
		iRider, iLap = self.getRiderLap( event )
		if iRider is None:
			return
			
		self.numSelect = numFromLabel(self.labels[iRider])
		if self.getNowTimeCallback:
			self.nowTime = self.getNowTimeCallback()
		self.Refresh()
		
		if iLap is None:
			return
		rClickCallback = getattr(self, 'rClickCallback', None)
		if rClickCallback is not None:
			xPos, yPos = event.GetPosition()
			rClickCallback( xPos, yPos, self.numSelect, iRider, iLap )

	intervals = [1, 2, 5, 10, 15, 20, 30, 1*60, 2*60, 5*60, 10*60, 15*60, 20*60, 30*60, 1*60*60, 2*60*60, 4*60*60, 6*60*60, 8*60*60, 12*60*60] + [24*60*60*k for k in range(1,200)]
	def Draw( self, dc ):
		size = self.GetClientSize()
		width = size.width
		height = size.height
		
		maxBib = '999999'
		
		minBarWidth = 48
		minBarHeight = 18
		maxBarHeight = 28
		
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		greyBrush = wx.Brush( wx.Colour(196,196,196), wx.SOLID )
		lightGreyBrush = wx.Brush( wx.Colour(220,220,220), wx.SOLID )
		backPen = wx.Pen(backColour, 0)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		tooSmall = (width < 50 or height < 24)
		self.tCursor = None
		
		if not self.data or self.dataMax == 0 or tooSmall:
			self.empty = True
			self.verticalSB.Show( False )
			self.horizontalSB.Show( False )
			if tooSmall:
				dc.SetPen( wx.BLACK_DASHED_PEN )
				dc.DrawLine( 0, height//2, width, height//2 )
			return
		
		self.empty = False
		
		barHeight = int(float(height) / float(len(self.data) + 2))
		barHeight = max( barHeight, minBarHeight )
		barHeight = min( barHeight, maxBarHeight )
		fontBarLabel = wx.Font( (0,int(min(barHeight-2, barHeight*0.9))), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( fontBarLabel )
		textWidthLeftMax, textHeightMax = dc.GetTextExtent( maxBib )
		
		statusTextSpace = dc.GetTextExtent(' ')[0]
		if self.status:
			statusTextWidth = max( dc.GetTextExtent(s)[0] for s in self.status )
			if statusTextWidth:
				statusTextWidth += statusTextSpace
		else:
			statusTextWidth = 0
			self.status = [''] * len(self.data)
			
		textWidthLeftMax += statusTextWidth
		
		maxBibWidth = textWidthLeftMax
		textWidthRightMax = 0
		for label in self.labels:
			if label not in self.headerSet:
				textWidthLeftMax = max( textWidthLeftMax, dc.GetTextExtent(label)[0] + statusTextWidth )
				num = numFromLabel(label)
				if num is not None:
					textWidthRightMax = max( textWidthRightMax, dc.GetTextExtent('{}'.format(num))[0] )
		textWidthRightMax += statusTextWidth
				
		if textWidthLeftMax + textWidthRightMax > width:
			self.horizontalSB.Show( False )
			self.verticalSB.Show( False )
			self.empty = True
			return
		
		maxLaps = max( len(d) for d in self.data )
		if maxLaps and (width - textWidthLeftMax - textWidthRightMax) / maxLaps < minBarWidth:
			self.horizontalSB.Show( True )
		else:
			self.horizontalSB.Show( False )
		
		if self.horizontalSB.IsShown():
			height -= self.scrollbarWidth
			
		barHeight = int(float(height) / float(len(self.data) + 2))
		barHeight = max( barHeight, minBarHeight )
		barHeight = min( barHeight, maxBarHeight )
		drawHeight = height - 2 * barHeight
		if barHeight * len(self.data) > drawHeight:
			self.verticalSB.Show( True )
			self.verticalSB.SetPosition( (width - self.scrollbarWidth, barHeight) )
			self.verticalSB.SetSize( (self.scrollbarWidth, drawHeight) )
			pageSize = int(drawHeight / barHeight)
			SetScrollbarParameters( self.verticalSB, pageSize-1, len(self.data)-1, pageSize )
		else:
			self.verticalSB.Show( False )
			
		if self.verticalSB.IsShown():
			width -= self.scrollbarWidth
			
		iDataShowStart = self.verticalSB.GetThumbPosition() if self.verticalSB.IsShown() else 0
		iDataShowEnd = iDataShowStart + self.verticalSB.GetThumbSize() + 1 if self.verticalSB.IsShown() else len(self.data)
		tShowStart = self.horizontalSB.GetThumbPosition() if self.horizontalSB.IsShown() else 0

		dc.SetFont( fontBarLabel )

		textWidthLeftMax, textHeightMax = dc.GetTextExtent( maxBib )
		textWidthRightMax = 0
		for label in self.labels:
			if label not in self.headerSet:
				textWidthLeftMax = max( textWidthLeftMax, dc.GetTextExtent(label)[0] + statusTextWidth )
				num = numFromLabel(label)
				if num is not None:
					textWidthRightMax = max( textWidthRightMax, dc.GetTextExtent( '{}'.format(num) )[0] )
		textWidthRightMax += statusTextWidth
				
		if textWidthLeftMax + textWidthRightMax > width:
			self.horizontalSB.Show( False )
			self.verticalSB.Show( False )
			self.empty = True
			return

		legendSep = 4			# Separations between legend entries and the Gantt bars.
		labelsWidthLeft = textWidthLeftMax + legendSep
		labelsWidthRight = textWidthRightMax + legendSep
			
		xLeft = labelsWidthLeft
		xRight = width - labelsWidthRight
		yBottom = min( barHeight * (len(self.data) + 1), barHeight + drawHeight )
		yTop = barHeight

		if self.horizontalSB.IsShown():
			viewWidth = minBarWidth * maxLaps
			ratio = float(xRight - xLeft) / float(viewWidth)
			sbMax = int(self.dataMax) + 1
			pageSize = int(sbMax * ratio) / 2.0
			SetScrollbarParameters( self.horizontalSB, pageSize-1, sbMax, pageSize )
			self.horizontalSB.SetPosition( (labelsWidthLeft, height) )
			self.horizontalSB.SetSize( (xRight - xLeft, self.scrollbarWidth) )
		
		fontLegend = wx.Font( (0,int(barHeight*.75)), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		fontNote = wx.Font( (0,int(barHeight*.8)), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )

		self.fontLegend = fontLegend
		dc.SetFont( fontLegend )
		textWidth, textHeight = dc.GetTextExtent( '00:00' if self.dataMax < 60*60 else '00:00:00' )
			
		# Draw the horizontal labels.
		# Find some reasonable tickmarks for the x axis.
		numLabels = (xRight - xLeft) / (textWidth * 1.5)
		tView = self.dataMax if not self.horizontalSB.IsShown() else self.horizontalSB.GetThumbSize()
				
		if self.horizontalSB.IsShown():
			tAdjust = self.horizontalSB.GetThumbPosition()
			viewWidth = minBarWidth * maxLaps
			dFactor = float(viewWidth) / float(self.dataMax)
		else:
			tAdjust = 0
			dFactor = (xRight - xLeft) / float(self.dataMax)
		
		def getTickLabel( t ):
			if t < 60:
				return ':{:02d}'.format(t)
			elif t < 60*60:
				return '{}:{:02d}'.format((t // 60), t%60)
			elif t < 24*60*60:
				return '{}:{:02d}:{:02d}'.format(t//(60*60), (t // 60)%60, t%60)
			else:
				if t % (24*60*60) == 0:
					return '{}d'.format(t//(24*60*60))
				elif t % (60*60) == 0:
					return '{}d{:02d}h'.format( t//(24*60*60), (t%(24*60*60))//(60*60) )
				else:
					return '{}d{:02d}:{:02d}'.format( t//(24*60*60), (t%(24*60*60))//(60*60), (t // 60)%60 )
			
		def getXT( d ):
			for t in range(int(tAdjust) - int(tAdjust)%d, int(self.dataMax), d):
				x = xLeft + (t-tAdjust) * dFactor
				if x < xLeft:
					continue
				if x > xRight:
					return
				yield int(x), t

		def overlaps( d ):
			wSpace = dc.GetTextExtent(' ')[0] * 1.25
			xLast = None
			for x, t in getXT( d ):
				w = dc.GetTextExtent( getTickLabel(t) )[0]
				w2 = w//2
				if xLast is None:
					xLast = x + w2
					continue
				xText = x - w2
				if xText - xLast < wSpace:
					return True
				xLast = x + w2
		
		d = tView / max(1.0, float(numLabels))
		iInterval = bisect.bisect_left(self.intervals, d, 0, len(self.intervals)-1)
		
		# Check if the labels will overlap in the space available.
		while overlaps( self.intervals[iInterval] ):
			iInterval += 1
		
		# Draw the labels.
		dc.SetPen(wx.Pen(wx.BLACK, 1))
		for x, t in getXT( self.intervals[iInterval] ):
			s = getTickLabel( t )
			w, h = dc.GetTextExtent(s)
			xText = int(x - w/2)
			dc.DrawText( s, xText, 0 + 4 )
			dc.DrawText( s, xText, yBottom + 4)
			dc.DrawLine( x, yBottom+3, x, yTop-3 )
		
		# Draw the Gantt chart.
		dc.SetFont( fontBarLabel )
		textWidth, textHeight = dc.GetTextExtent( maxBib )

		penBar = wx.Pen( wx.Colour(128,128,128), 1 )
		penBar.SetCap( wx.CAP_BUTT )
		penBar.SetJoin( wx.JOIN_MITER )
		dc.SetPen( penBar )
		
		penEBT = wx.Pen( wx.Colour(230,0,0), 3 )
		penEBT.SetCap( wx.CAP_BUTT )
		
		brushBar = wx.Brush( wx.BLACK )
		transparentBrush = wx.Brush( wx.WHITE, style = wx.TRANSPARENT )
		
		ctx = wx.GraphicsContext.Create(dc)
		ctx.SetPen( wx.Pen(wx.BLACK, 1) )
		
		xyInterp = []
		xyNumTimeInfo = []
		xyDuplicate = []
		
		xFactor = dFactor
		yLast = barHeight
		yHighlight = None
		
		tLeaderLast = None
		dy = 0

		tToX = lambda t: int(labelsWidthLeft + (t-tAdjust) * xFactor)
		# Set inverse function to get from screen x coords to time.
		xToT = lambda x: (x-labelsWidthLeft) / xFactor + tAdjust
		
		for i, s in enumerate(self.data):
			# Record the leader's last x position.
			if tLeaderLast is None:
				tLeaderLast = s[-1] if s else 0.0
			if not ( iDataShowStart <= i < iDataShowEnd ):
				continue
			
			try:
				num = numFromLabel(self.labels[i])
			except (TypeError, IndexError):
				num = -1
				
			yCur = yLast + barHeight
			xLast = labelsWidthLeft
			xCur = xLast
			tTooShort = 9.0	# If a lap is shorter than 9 seconds, consider it a duplicate entry.
			
			# Quickly find the first visible gantt chart rectangle.
			for j in range(max(0, bisect.bisect_left(KeyWrapper(s, tToX), labelsWidthLeft)-1), len(s)):
				if xLast >= xRight:
					break
				t = s[j]
				xCur = xOriginal = tToX( t )
				if xCur < labelsWidthLeft:
					continue
					
				if xCur > xRight:
					xCur = xRight
				if j == 0:
					brushBar.SetColour( wx.WHITE )
					dc.SetBrush( brushBar )
					dc.DrawRectangle( xLast, yLast, xCur - xLast + 1, yCur - yLast + 1 )
				else:
					ctx.SetPen( wx.Pen(wx.WHITE, 1, style=wx.TRANSPARENT ) )
					dy = yCur - yLast + 1
					dd = int(dy * 0.3)
					ic = j % len(self.colours)
					
					ctx.SetBrush( ctx.CreateLinearGradientBrush(0, yLast, 0, yLast + dd + 1, self.colours[ic], self.lighterColours[ic]) )
					ctx.DrawRectangle(xLast, yLast, xCur - xLast + 1, dd + 1)
					
					ctx.SetBrush( ctx.CreateLinearGradientBrush(0, yLast + dd, 0, yLast + dy, self.lighterColours[ic], self.colours[ic]) )
					ctx.DrawRectangle(xLast, yLast + dd, xCur - xLast + 1, dy-dd )
					
					dc.SetBrush( transparentBrush )
					dc.SetPen( penBar )
					dc.DrawRectangle( xLast, yLast, xCur - xLast + 1, dy )
					
					if self.lapNote:
						note = self.lapNote.get( (num, j), None )
						if note:
							dc.SetFont( fontNote )
							noteWidth, noteHeight = dc.GetTextExtent( note )
							noteBorderWidth = int(dc.GetTextExtent( '   ' )[0] / 2)
							noteBarWidth = xCur - xLast - noteBorderWidth * 2
							if noteBarWidth <= 0:
								noteBarWidth = xCur - xLast
								noteBorderWidth = 0
								note = '...'
								noteWidth, noteHeight = dc.GetTextExtent( note )
							elif noteWidth > noteBarWidth:
								lenLeft, lenRight = 1, len(note)
								while lenRight - lenLeft > 1:
									lenMid = (lenRight + lenLeft) // 2
									noteWidth, noteHeight = dc.GetTextExtent( note[:lenMid].strip() + '...' )
									if noteWidth < noteBarWidth:
										lenLeft = lenMid
									else:
										lenRight = lenMid
								note = note[:lenLeft].strip() + '...'
								noteWidth, noteHeight = dc.GetTextExtent( note )
							dc.DrawText( note, round(xLast + noteBorderWidth), round(yLast + (dy - noteHeight) / 2) )
							dc.SetFont( fontBarLabel )
					
					if j == self.moveLap and self.moveIRider == i:
						if hasPhoto(num, t):
							# Draw a little camera icon.
							cameraHeight = int(dy * 0.75)
							cameraWidth = int(cameraHeight * 1.5)
							dc.SetBrush( wx.BLACK_BRUSH )
							dc.DrawRoundedRectangle( round(xCur - 2 - cameraWidth), round(yLast + (dy - cameraHeight) / 2), cameraWidth, cameraHeight, round(cameraHeight/5) )
							dc.SetPen( wx.WHITE_PEN )
							dc.SetBrush( transparentBrush )
							dc.DrawCircle( round(xCur - 2 - cameraWidth / 2), round(yLast + dy / 2), round(cameraHeight * (0.6 / 2)) ) 
					
					if xOriginal <= xRight:
						try:
							if self.interp[i][j]:
								xyInterp.append( (xOriginal, yLast) )
						except (TypeError, ValueError, IndexError):
							pass
						if self.numTimeInfo and self.numTimeInfo.getInfo(num, t) is not None:
							xyNumTimeInfo.append( (xOriginal, yLast) )
						if t - s[j-1] < tTooShort:
							xyDuplicate.append( (xOriginal, yLast) )

				xLast = xCur
			
			# Draw the last empty bar.
			xCur = int(labelsWidthLeft + self.dataMax * xFactor)
			if xCur > xRight:
				xCur = xRight
			dc.SetPen( penBar )
			brushBar.SetColour( wx.WHITE )
			dc.SetBrush( brushBar )
			dc.DrawRectangle( xLast, yLast, xCur - xLast + 1, yCur - yLast + 1 )
			
			# Draw the early bell line.
			if self.earlyBellTimes and self.earlyBellTimes[i]:
				ebtX = tToX( self.earlyBellTimes[i] )
				dc.SetPen( penEBT )
				dc.DrawLine( ebtX, yLast, ebtX, yLast+dy )
			
			# Draw the label on both ends.
			if self.greyOutSet and i in self.greyOutSet:
				dc.SetPen( wx.TRANSPARENT_PEN )
				dc.SetBrush( greyBrush )
				dc.DrawRectangle( 0, yLast, textWidthLeftMax, yCur - yLast + 1 )
				dc.SetBrush( backBrush )
			if self.status[i] == _('PUL'):
				dc.SetPen( wx.TRANSPARENT_PEN )
				dc.SetBrush( lightGreyBrush )
				dc.DrawRectangle( 0, yLast, textWidthLeftMax, yCur - yLast + 1 )
				dc.SetBrush( backBrush )
			if self.labels[i] in self.headerSet:
				dc.DrawText( self.labels[i], labelsWidthLeft + 4, yLast )    # This is a Category Label.
			else:
				labelWidth = dc.GetTextExtent( self.labels[i] )[0]
				dc.DrawText( self.labels[i], textWidthLeftMax - labelWidth - statusTextWidth, yLast )
				if statusTextWidth and self.status[i]:
					dc.DrawText( self.status[i], textWidthLeftMax - statusTextWidth + statusTextSpace, yLast )
				if not self.minimizeLabels:
					label = self.labels[i]
					lastSpace = label.rfind( ' ' )
					if lastSpace > 0:
						label = label[lastSpace+1:]
					labelWidth = dc.GetTextExtent( label )[0]
					dc.DrawText( label, width - labelsWidthRight + legendSep, yLast )
					if statusTextWidth and self.status[i]:
						dc.DrawText( self.status[i], width - statusTextWidth + statusTextSpace, yLast )

			if f'{self.numSelect}' == f'{numFromLabel(self.labels[i])}':
				yHighlight = yCur

			yLast = yCur
				
		if yHighlight is not None and len(self.data) > 1:
			dc.SetPen( wx.Pen(wx.BLACK, 2) )
			dc.SetBrush( wx.TRANSPARENT_BRUSH )
			dc.DrawLine( 0, yHighlight, width, yHighlight )
			yHighlight -= barHeight
			dc.DrawLine( 0, yHighlight, width, yHighlight )
		
		# Draw indicators for interpolated values.
		radius = (dy/2) * 0.9
		
		# Define a path for the interp indicator about the origin.
		diamondPath = ctx.CreatePath()
		diamondPath.MoveToPoint( 0, -radius )
		diamondPath.AddLineToPoint( -radius, 0 )
		diamondPath.AddLineToPoint( 0, radius )
		diamondPath.AddLineToPoint( radius, 0 )
		diamondPath.AddLineToPoint( 0, -radius )
		
		def getStarPath( ctx, numPoints, radius, radiusInner ):
			path = ctx.CreatePath()
			angle = (math.pi * 2.0) / numPoints
			angle2 = angle / 2.0
			path.MoveToPoint( 0, -radius )
			for p in range(numPoints):
				a = p * angle + angle2 + math.pi / 2.0
				path.AddLineToPoint( math.cos(a) * radiusInner, -math.sin(a) * radiusInner )
				a = (p + 1) * angle + math.pi / 2.0
				path.AddLineToPoint( math.cos(a) * radius, -math.sin(a) * radius )
			path.AddLineToPoint( 0, -radius )
			return path
		starPath = getStarPath( ctx, 5, radius, radius / 2 )

		# Draw the interp indicators.
		ctx.SetPen( penBar )
		ctx.SetBrush( ctx.CreateRadialGradientBrush( 0, - radius*0.50, 0, 0, radius + 1, wx.WHITE, self.yellowColour ) )
		for xCur, yCur in xyInterp:
			ctx.PushState()
			ctx.Translate( xCur, yCur + dy/2.0 - (dy/2.0 - radius) / 4 )
			ctx.DrawPath( diamondPath )
			ctx.PopState()
		
		# Draw the edit indictors.
		ctx.SetPen( penBar )
		ctx.SetBrush( ctx.CreateRadialGradientBrush( 0, - radius*0.50, 0, 0, radius + 1, wx.WHITE, self.orangeColour ) )
		for xCur, yCur in xyNumTimeInfo:
			ctx.PushState()
			ctx.Translate( xCur, yCur + dy/2.0 - (dy/2.0 - radius) / 4 )
			ctx.DrawPath( starPath )
			ctx.PopState()
			
		# Draw the duplicate indicators.
		radius = int(radius * 1.5)
		ctx.SetPen( wx.Pen(wx.RED, 3) )
		ctx.SetBrush( wx.TRANSPARENT_BRUSH )
		for xCur, yCur in xyDuplicate:
			ctx.DrawEllipse( xCur - radius, yCur + dy/2.0 - radius, radius*2, radius*2 )
		
		# Draw the now timeline.
		timeLineTime = self.nowTime if self.nowTime and self.nowTime < self.dataMax else tLeaderLast
		nowTimeStr = Utils.formatTime( timeLineTime )
		labelWidth, labelHeight = dc.GetTextExtent( nowTimeStr )
		x = int(labelsWidthLeft + (timeLineTime - tAdjust) * xFactor)
		if xLeft <= x < xRight:			
			ntColour = '#339966'
			dc.SetPen( wx.Pen(ntColour, 3) )
			dc.DrawLine( x, barHeight - 4, x, yLast + 4 )
			dc.SetPen( wx.Pen(wx.WHITE, 1) )
			dc.DrawLine( x, barHeight - 4, x, yLast + 4 )
			
			dc.SetBrush( wx.Brush(ntColour) )
			dc.SetPen( wx.Pen(ntColour,1) )
			rect = wx.Rect( x - labelWidth//2-2, 0, labelWidth+4, labelHeight )
			dc.DrawRectangle( rect )
			if not self.minimizeLabels:
				rect.SetY( yLast+2 )
				dc.DrawRectangle( rect )

			dc.SetTextForeground( wx.WHITE )
			dc.DrawText( nowTimeStr, x - labelWidth // 2, 0 )
			if not self.minimizeLabels:
				dc.DrawText( nowTimeStr, x - labelWidth // 2, yLast + 2 )
		
		# Draw the cursor crosshair.
		if self.moveIRider is not None and xLeft <= self.xMove < xRight:
			x = self.xMove
			self.tCursor = xToT( self.xMove )
			
			tStr = Utils.formatTime( self.tCursor )
			labelWidth, labelHeight = dc.GetTextExtent( nowTimeStr )
			
			# Draw the vertical and horizontal lines.
			ctColour = '#3F3F3F'
			ctTextColour = wx.WHITE
			
			dc.SetPen( wx.Pen(ctColour, 3) )
			dc.DrawLine( x, barHeight - 4, x, yLast + 4 )
			if self.data[self.moveIRider]:
				dc.DrawLine( xLeft-4, self.yMove, xRight+4, self.yMove )
			
			# Draw the time text.
			dc.SetBrush( wx.Brush(ctColour) )
			dc.SetPen( wx.Pen(ctColour,1) )
			rect = wx.Rect( x - labelWidth//2-2, 0, labelWidth+4, labelHeight )
			dc.DrawRectangle( rect )
			if not self.minimizeLabels:
				rect.SetY( yLast+2 )
				dc.DrawRectangle( rect )

			dc.SetTextForeground( ctTextColour )
			dc.DrawText( tStr, x - labelWidth // 2, 0 )
			if not self.minimizeLabels:
				dc.DrawText( tStr, x - labelWidth // 2, yLast + 2 )			
		
		# Store the drawing scale parameters.
		self.xFactor = xFactor
		self.barHeight = barHeight
		self.labelsWidthLeft = labelsWidthLeft
			
	def OnEraseBackground(self, event):
		# This is intentionally empty.
		pass
		
if __name__ == '__main__':
	def GetData():
		data = []
		interp = []
		for i in range(1000):
			data.append( [t + i*10.0 for t in range(0, 60*60 * 24 * 2, 7*60)] )
			if i % 5 == 1:
				data[-1].insert( (i//3) + 1, data[-1][i//3] + 0.05 )
			interp.append( [((t + i*10)%100)//10 for t in range(0, 60*60 * 3, 7*60)] )
		return data, interp

	app = wx.App(False)
	mainWin = wx.Frame(None,title="GanttChartPanel", size=(600,400))
	gantt = GanttChartPanel( mainWin )
	gantt.SetDoubleBuffered( True )

	random.seed( 10 )
	t = 55*60
	tVar = t * 0.15
	data, interp = GetData()
	gantt.SetData( data, ['{}'.format(i) for i in range(100, 100+len(data))],
		interp = interp,
		status = [['','PUL ', 'DNF ', 'DQ ', 'NP '][i%5] for i in range(len(data))],
	)

	mainWin.Show()
	app.MainLoop()
