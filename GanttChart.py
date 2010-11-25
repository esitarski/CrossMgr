import wx
import random
import math
import sys
import bisect
import Utils

havePopupWindow = 1
if wx.Platform == '__WXMAC__':
	havePopupWindow = 0
	wx.PopupWindow = wx.PopupTransientWindow = wx.Window
	
class BarInfoPopup( wx.PopupTransientWindow ):
    """Shows Specific Rider and Lap information."""
    def __init__(self, parent, style, text):
		wx.PopupTransientWindow.__init__(self, parent, style)
		self.SetBackgroundColour(wx.WHITE)
		border = 10
		st = wx.StaticText(self, -1, text, pos=(border/2,border/2))
		sz = st.GetBestSize()
		self.SetSize( (sz.width+border, sz.height+border) )
		
class GanttChart(wx.PyControl):
	def __init__(self, parent, id=wx.ID_ANY, startAtZero = False, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="GanttChart"):
		"""
		Default class constructor.

		@param parent: Parent window. Must not be None.
		@param id: StatusBar identifier. A value of -1 indicates a default value.
		@param pos: StatusBar position. If the position (-1, -1) is specified
					then a default position is chosen.
		@param size: StatusBar size. If the default size (-1, -1) is specified
					then a default size is chosen.
		@param style: not used
		@param validator: Window validator.
		@param name: Window name.
		"""

		# Ok, let's see why we have used wx.PyControl instead of wx.Control.
		# Basically, wx.PyControl is just like its wxWidgets counterparts
		# except that it allows some of the more common C++ virtual method
		# to be overridden in Python derived class. For StatusBar, we
		# basically need to override DoGetBestSize and AcceptsFocusFromKeyboard
		
		wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)
		self.SetBackgroundColour('white')
		self.data = None
		self.labels = None
		self.nowTime = None
		self.startAtZero = startAtZero
		
		self.colours = [
			wx.Colour(255, 0, 0),
			wx.Colour(0, 255, 0),
			wx.Colour(0, 0, 255),
			wx.Colour(255, 255, 0),
			wx.Colour(255, 0, 255),
			wx.Colour(0, 255, 255),
			wx.Colour(0, 0, 0) ]
			
		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)

	def DoGetBestSize(self):
		return wx.Size(100, 50)

	def SetForegroundColour(self, colour):
		wx.PyControl.SetForegroundColour(self, colour)
		self.Refresh()

	def SetBackgroundColour(self, colour):
		wx.PyControl.SetBackgroundColour(self, colour)
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

	def SetData( self, data, labels = None, nowTime = None ):
		"""
		* data is a list of lists.  Each list is a list of times.		
		* labels are the names of the series.  Optional.
		"""
		self.data = None
		self.labels = None
		self.nowTime = None
		if data and any( s for s in data ):
			self.data = data
			self.dataMax = max(max(s) if s else -sys.float_info.max for s in self.data)
			if labels:
				self.labels = [str(lab) for lab in labels]
				if len(self.labels) < len(self.data):
					self.labels = self.labels + [None] * (len(self.data) - len(self.labels))
				elif len(self.labels) > len(self.data):
					self.labels = self.labels[:len(self.data)]
			self.nowTime = nowTime
				
		self.Refresh()
	
	def OnPaint(self, event):
		#dc = wx.BufferedPaintDC(self)
		dc = wx.PaintDC(self)
		self.Draw(dc)

	def OnSize(self, event):
		self.Refresh()
		
	def OnLeftClick( self, event ):
		if getattr(self, 'empty', True):
			return
		x, y = event.GetPositionTuple()
		y -= self.barHeight if self.drawNowTime else 0
		x -= self.labelsWidth
		iRider = int(y / self.barHeight)
		if not 0 <= iRider < len(self.data):
			return
		iLap = bisect.bisect_left( self.data[iRider], x / self.xFactor )
		if not 1 <= iLap < len(self.data[iRider]):
			return
			
		bip = BarInfoPopup(self, wx.SIMPLE_BORDER,
								'Rider: %s  Lap: %d' % (self.labels[iRider] if self.labels else str(iRider), iLap) )

		xPos, yPos = event.GetPositionTuple()
		width, height = bip.GetClientSize()
		pos = self.ClientToScreen( (xPos - width, yPos - height) )
		bip.Position( pos, (0,0) )
		bip.Popup()
	
	def Draw(self, dc):
		size = self.GetClientSize()
		width = size.width
		height = size.height
		
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		if not self.data or width < 50 or height < 50:
			self.empty = True
			return
		self.empty = False

		drawNowTime = False
		if self.nowTime:
			drawNowTime = True
			
		barHeight = int(float(height) / float(len(self.data) + (2 if drawNowTime else 0)))
		if barHeight < 4:
			self.empty = True
			return
		if barHeight > 50:
			barHeight = 50
		
		font = wx.FontFromPixelSize( wx.Size(0,barHeight - 1), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.SetFont( font )
		textWidth, textHeight = dc.GetTextExtent( '0000' )
		
		drawLabels = False
		labelsWidth = 0
		legendSep = 4			# Separations between legend entries and the Gantt bars.
		if self.labels:
			labelsWidth = textWidth + legendSep
			drawLabels = True
			
		if labelsWidth > width / 2:
			labelsWidth = 0
			drawLabels = False

		# Draw the Gantt chart.
		penBar = wx.Pen( wx.Colour(128,128,128), 1 )
		penBar.SetCap( wx.CAP_BUTT )
		penBar.SetJoin( wx.JOIN_MITER )
		dc.SetPen( penBar )
		
		brushBar = wx.Brush( wx.Color(0,0,0) )
		
		xFactor = float(width - labelsWidth * 2) / float(self.dataMax)
		yLast = barHeight if drawNowTime else 0
		for i, s in enumerate(self.data):
			yCur = yLast + barHeight
			xLast = labelsWidth
			xCur = xLast
			for j, t in enumerate(s):
				xCur = int(labelsWidth + t * xFactor)
				brushBar.SetColour( self.colours[j%len(self.colours)] )
				dc.SetBrush( brushBar )
				dc.DrawRectangle( xLast, yLast, xCur - xLast + 1, yCur - yLast + 1 )
				xLast = xCur
			
			# Draw the last empty bar.
			xCur = int(labelsWidth + self.dataMax * xFactor)
			brushBar.SetColour( wx.WHITE )
			dc.SetBrush( brushBar )
			dc.DrawRectangle( xLast, yLast, xCur - xLast + 1, yCur - yLast + 1 )
			
			if drawLabels:
				labelWidth = dc.GetTextExtent( self.labels[i] )[0]
				dc.DrawText( self.labels[i], textWidth - labelWidth, yLast )
				dc.DrawText( self.labels[i], width - labelsWidth + legendSep, yLast )
			yLast = yCur
			
		if drawNowTime:
			x = int(labelsWidth + self.nowTime * xFactor)
			dc.SetPen( wx.Pen(wx.Color(200,200,200), 4) )
			dc.DrawLine( x, barHeight - 4, x, yLast + 4 )
			nowTimeStr = Utils.formatTime( self.nowTime )
			labelWidth = dc.GetTextExtent( nowTimeStr )[0]
			dc.DrawText( nowTimeStr, x - labelWidth / 2, 0 )
			dc.DrawText( nowTimeStr, x - labelWidth / 2, yLast )

		self.xFactor = xFactor
		self.barHeight = barHeight
		self.drawNowTime = drawNowTime
		self.drawLabels = drawLabels
		self.labelsWidth = labelsWidth
			
	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
if __name__ == '__main__':
	def GetData():
		data = []
		for i in xrange(20):
			data.append( [t + i*10 for t in xrange(0, 60*60, 7*60)] )
		return data

	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="GanttChart", size=(600,400))
	GanttChart = GanttChart(mainWin)

	random.seed( 10 )
	t = 55*60
	tVar = t * 0.15
	GanttChart.SetData( GetData() )

	mainWin.Show()
	app.MainLoop()
