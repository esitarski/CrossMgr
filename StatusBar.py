import wx
import Utils

def lighterColour( c ):
	rgb = c.Get( False )
	return wx.Colour( *[int(v + (255 - v) * 0.6) for v in rgb] )

class StatusBar(wx.Control):
	def __init__(self, parent, id=wx.ID_ANY, value=0, range=100, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				name="StatusBar"):
		"""
		Default class constructor.

		@param parent: Parent window. Must not be None.
		@param id: StatusBar identifier. A value of -1 indicates a default value.
		@param value: Value of the statusbar
		@param range: Range of the statusbar (from 0)
		@param pos: StatusBar position. If the position (-1, -1) is specified
					then a default position is chosen.
		@param size: StatusBar size. If the default size (-1, -1) is specified
					then a default size is chosen.
		@param style: not used in this demo, StatusBar has only 2 state
		@param validator: Window validator.
		@param name: Window name.
		"""

		# Ok, let's see why we have used wx.Control instead of wx.Control.
		# Basically, wx.Control is just like its wxWidgets counterparts
		# except that it allows some of the more common C++ virtual method
		# to be overridden in Python derived class. For StatusBar, we
		# basically need to override DoGetBestSize and AcceptsFocusFromKeyboard
		
		super().__init__(parent, id, pos, size, style, validator, name)
		
		self._value = int(value)
		self._range = int(range)
		
		# Reset the width and height.
		self.textWidth, self.textHeight = None, None
		
		# Initialize the focus pen colour/dashes, for faster drawing later
		self.InitializeColours()
		
		# Ok, set the wx.Control label, its initial size (formerly known an
		# SetBestFittingSize), and inherit the attributes from the standard
		# wx.CheckBox
		self.SetInitialSize(size)
		self.InheritAttributes()

		# Bind the events related to our control: first of all, we use a
		# combination of wx.BufferedPaintDC and an empty handler for
		# wx.EVT_ERASE_BACKGROUND (see later) to reduce flicker
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		
	def InitializeColours(self):
		self._orange = wx.Colour(255,140,0)
		self._green = wx.Colour(0, 0xC0, 0)
			
	def SetFont(self, font):
		wx.Control.SetFont(self, font)

		self.textWidth, self.textHeight = None, None

		# The font for text label has changed, so we must recalculate our best
		# size and refresh ourselves.        
		self.InvalidateBestSize()
		self.Refresh()
		
	def DoGetBestSize(self):
		font = self.GetFont()
		if not font:
			font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
		dc = wx.ClientDC(self)
		dc.SetFont(font)
		textWidth, textHeight = dc.GetTextExtent(u'00:00')
		return wx.Size(textWidth, textHeight)

	def SetForegroundColour(self, colour):
		wx.Control.SetForegroundColour(self, colour)

		# We have to re-initialize the focus indicator per colour as it should
		# always be the same as the foreground colour
		self.InitializeColours()
		self.Refresh()

	def SetBackgroundColour(self, colour):
		""" Overridden base class virtual. """

		wx.Control.SetBackgroundColour(self, colour)

		# We have to refresh ourselves
		self.Refresh()


	def Enable(self, enable=True):
		""" Enables/Disables StatusBar. """

		wx.Control.Enable(self, enable)

		# We have to refresh ourselves, as our state changed        
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


	def GetValue(self):
		return self._value

	def GetRange(self):
		return self._range

	def SetValue(self, value):
		value = int(value)
		if self._value != value:
			self._value = value
			self.Refresh()

	def SetRange(self, range):
		range = int(range)
		if self._range != range:
			self._range = range
			self.Refresh()
		
	def OnPaint(self, event):
		# If you want to reduce flicker, a good starting point is to
		# use wx.BufferedPaintDC.
		dc = wx.BufferedPaintDC(self)

		# Is is advisable that you don't overcrowd the OnPaint event
		# (or any other event) with a lot of code, so let's do the
		# actual drawing in the Draw() method, passing the newly
		# initialized wx.BufferedPaintDC
		self.Draw(dc)

	def Draw(self, dc):
		# Get the actual client size of ourselves
		width, height = self.GetClientSize()

		if not width or not height:
			return

		# Initialize the wx.BufferedPaintDC, assigning a background
		# colour and a foreground colour (to draw the text)
		backColour = self.GetBackgroundColour()
		backBrush = wx.Brush(backColour, wx.SOLID)
		dc.SetBackground(backBrush)
		dc.Clear()
		
		value = self._value
		range = self._range
		
		value = max(value, 0)
		range = max(range, 1)
		value = min(value, range)
		
		dc.SetFont(self.GetFont())
		
		if self.textWidth is None:
			self.textWidth, self.textHeight = dc.GetTextExtent('00:00')
		
		if self._range != 0 and value == 0:
			# Draw the Do Not Enter sign.
			radius = min(width, height) / 2 - 1
			xCenter, yCenter = width/2, radius
			lineHeight = 2 * int(radius * 0.25)
			lineWidth = 2 * int(radius * 0.70)
			sep = 4
			ctx = wx.GraphicsContext.Create( dc )
			ctx.SetPen( wx.GREY_PEN )
			ctx.SetBrush( wx.GREY_BRUSH )
			ctx.DrawEllipse( xCenter+2 - radius, yCenter+2 - radius, radius * 2, radius * 2 )
			ctx.SetPen( wx.BLACK_PEN )
			ctx.SetBrush( wx.RED_BRUSH )
			ctx.DrawEllipse( xCenter - radius, yCenter - radius, radius * 2, radius * 2 )
			ctx.SetPen( wx.WHITE_PEN )
			ctx.SetBrush( wx.WHITE_BRUSH )
			ctx.DrawRectangle(xCenter - lineWidth/2, yCenter - lineHeight/2, lineWidth, lineHeight )
		elif value != 0:
			# Draw the status bar.
			x, y = 0, 0
			border = 0
			if width > border * 4:
				x += border
				width -= 2*border
			if height > border * 4:
				y += border
				height -= 2*border
				
			dc.SetPen( wx.TRANSPARENT_PEN )
			dc.SetBrush( wx.WHITE_BRUSH )
			dc.DrawRectangle(x, y, width, height)
			
			#---------------------------------------------------------------------
			ctx = wx.GraphicsContext.Create(dc)
			ctx.SetPen( wx.Pen(wx.WHITE, 1, style=wx.TRANSPARENT ) )
			
			colour = self._green if value > range/4 else self._orange
			
			w = int(float(width) * float(value) / float(range))
			dd = int( height * 0.3 )
			b1 = ctx.CreateLinearGradientBrush(x, y, x, y + dd + 1, colour, lighterColour(colour))
			ctx.SetBrush(b1)
			ctx.DrawRectangle(x, y, x + w, dd + 1)
					
			b2 = ctx.CreateLinearGradientBrush(x, y + dd, x, height, lighterColour(colour), colour )
			ctx.SetBrush(b2)
			ctx.DrawRectangle(x, y + dd, x + w, height-dd )
			
			# dc.SetBrush( wx.GREEN_BRUSH if value > range/4 else self._orangeBrush )
			# dc.DrawRectangle(x, y, int(float(width) * float(value) / float(range)), height)
			
			s = Utils.SecondsToMMSS(value)
			if s[0] == '0':
				s = s[1:]
			dc.DrawText(s, (width - self.textWidth) / 2, 0)
			
			dc.SetPen( wx.BLACK_PEN )
			dc.SetBrush( wx.TRANSPARENT_BRUSH )
			dc.DrawRectangle(x, y, width, height)

	def OnEraseBackground(self, event):
		# This is intentionally empty, because we are using the combination
		# of wx.BufferedPaintDC + an empty OnEraseBackground event to
		# reduce flicker
		pass
		
