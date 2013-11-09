# --------------------------------------------------------------------------------- #
# KEYBUTTON wxPython IMPLEMENTATION
#
# Edward Sitarski, @ 07 November 2011
#
#
# TODO List
#
# 1) Anything to do?
#
#
# For all kind of problems, requests of enhancements and bug reports, please
# write to me at:
#
# edward.sitarski@gmail.com
#
#
# End Of Comments
# --------------------------------------------------------------------------------- #

"""
KeyButton is another custom-drawn button class that looks similar to a key on a Mac.


Description
===========

KeyButton is another custom-drawn button class that looks similar to a key on a Mac
No bitmaps are used.  Effects are done with gradient shading.

Supported Platforms
===================

KeyButton has been tested on the following platforms:
  * Windows (Windows XP, Vista, Windows 7).
  * Linux (Ubuntu)


Window Styles
=============

`No particular window styles are available for this class.`


Events Processing
=================

This class processes the following events:

================= ==================================================
Event Name		Description
================= ==================================================
``wx.EVT_BUTTON`` Process a `wx.wxEVT_COMMAND_BUTTON_CLICKED` event, when the button is clicked. 
================= ==================================================


License And Version
===================

KeyButton is distributed under the wxPython license.

Latest Revision: Andrea Gavana @ 27 Nov 2009, 17.00 GMT

Version 0.3

"""

import wx

HOVER = 1
CLICK = 2

class KeyButtonEvent(wx.PyCommandEvent):
	""" Event sent from L{KeyButton} when the button is activated. """
	
	def __init__(self, eventType, eventId):
		"""
		Default class constructor.

		:param `eventType`: the event type;
		:param `eventId`: the event identifier.
		"""
		
		wx.PyCommandEvent.__init__(self, eventType, eventId)
		self.isDown = False
		self.theButton = None


	def SetButtonObj(self, btn):
		"""
		Sets the event object for the event.

		:param `btn`: the button object, an instance of L{KeyButton}.
		"""
		
		self.theButton = btn


	def GetButtonObj(self):
		""" Returns the object associated with this event. """
		
		return self.theButton

	
class KeyButton(wx.PyControl):
	""" This is the main class implementation of L{KeyButton}. """
	
	def __init__(self, parent, id=wx.ID_ANY, bitmap=None, label="", pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				 name="keybutton"):
		"""
		Default class constructor.

		:param `parent`: the L{KeyButton} parent;
		:param `id`: window identifier. A value of -1 indicates a default value;
		:param `bitmap`: the button bitmap (if any);
		:param `label`: the button text label;
		:param `pos`: the control position. A value of (-1, -1) indicates a default position,
		 chosen by either the windowing system or wxPython, depending on platform;
		:param `size`: the control size. A value of (-1, -1) indicates a default size,
		 chosen by either the windowing system or wxPython, depending on platform;
		:param `style`: the button style (unused);
		:param `validator`: the validator associated to the button;
		:param `name`: the button name.
		"""
		
		wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
		self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
		self.Bind(wx.EVT_SET_FOCUS, self.OnGainFocus)
		self.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
		self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

		self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDown)

		self._mouseAction = None
		self._bitmap = bitmap
		self._hasFocus = False
		
		self.SetLabel(label)
		self.InheritAttributes()
		self.SetInitialSize(size)

		# The following defaults draw a Mac style key.
		self._outsideBottomColour = wx.Colour(164, 164, 164)
		self._outsideTopColour = wx.Colour(215, 215, 215)
		self._outsideLineColour = wx.Colour(154, 154, 154)
		
		self._insideEdgeColour = wx.Colour(215, 215, 215)
		self._insideCenterColour = wx.Colour(230, 230, 230)
		self._insideLineColour = wx.Colour(242, 242, 242)
		
		self.SetForegroundColour( wx.Colour(81, 81, 81) )

		for method in dir(self):
			if method.endswith("Colour"):
				newMethod = method[0:-6] + "Colour"
				if not hasattr(self, newMethod):
					setattr(self, newMethod, method)
		

	def LightColour(self, colour, percent = 25.0):
		"""
		Return light contrast of `colour`. The colour returned is from the scale of
		`colour` ==> white.

		:param `colour`: the input colour to be brightened;
		:param `percent`: determines how light the colour will be. `percent` = 100
		 returns white, `percent` = 0 returns `colour`.
		"""

		end_colour = wx.WHITE
		rd = end_colour.Red() - colour.Red()
		gd = end_colour.Green() - colour.Green()
		bd = end_colour.Blue() - colour.Blue()
		high = 100

		# We take the percent way of the colour from colour -. white
		i = percent
		r = colour.Red() + ((i*rd*100)/high)/100
		g = colour.Green() + ((i*gd*100)/high)/100
		b = colour.Blue() + ((i*bd*100)/high)/100

		return wx.Colour(r, g, b)

	def DarkColour(self, colour, percent = 10.0):
		"""
		Return light contrast of `colour`. The colour returned is from the scale of
		`colour` ==> white.

		:param `colour`: the input colour to be brightened;
		:param `percent`: determines how dark the colour will be. `percent` = 100
		 returns black, `percent` = 100 returns `colour`.
		"""

		# We take the percent way of the colour from colour -. white
		i = (100.0 - percent) / 100.0
		r = colour.Red() * i
		g = colour.Green() * i
		b = colour.Blue() * i

		return wx.Colour(r, g, b)


	def OnSize(self, event):
		"""
		Handles the ``wx.EVT_SIZE`` event for L{KeyButton}.

		:param `event`: a `wx.SizeEvent` event to be processed.
		"""
		
		event.Skip()
		self.Refresh()


	def OnLeftDown(self, event):
		"""
		Handles the ``wx.EVT_LEFT_DOWN`` event for L{KeyButton}.

		:param `event`: a `wx.MouseEvent` event to be processed.
		"""

		if not self.IsEnabled():
			return
		
		self._mouseAction = CLICK
		self.CaptureMouse()
		self.Refresh()
		event.Skip()


	def OnLeftUp(self, event):
		"""
		Handles the ``wx.EVT_LEFT_UP`` event for L{KeyButton}.

		:param `event`: a `wx.MouseEvent` event to be processed.
		"""

		if not self.IsEnabled() or not self.HasCapture():
			return
		
		pos = event.GetPosition()
		rect = self.GetClientRect()

		if self.HasCapture():
			self.ReleaseMouse()
			
		if rect.Contains(pos):
			self._mouseAction = HOVER
			self.Notify()
		else:
			self._mouseAction = None

		self.Refresh()
		event.Skip()


	def OnMouseEnter(self, event):
		"""
		Handles the ``wx.EVT_ENTER_WINDOW`` event for L{KeyButton}.

		:param `event`: a `wx.MouseEvent` event to be processed.
		"""

		if not self.IsEnabled():
			return
		
		self._mouseAction = HOVER
		self.Refresh()
		event.Skip()


	def OnMouseLeave(self, event):
		"""
		Handles the ``wx.EVT_LEAVE_WINDOW`` event for L{KeyButton}.

		:param `event`: a `wx.MouseEvent` event to be processed.
		"""

		self._mouseAction = None
		self.Refresh()
		event.Skip()


	def OnGainFocus(self, event):
		"""
		Handles the ``wx.EVT_SET_FOCUS`` event for L{KeyButton}.

		:param `event`: a `wx.FocusEvent` event to be processed.
		"""
		
		self._hasFocus = True
		self.Refresh()
		self.Update()


	def OnLoseFocus(self, event):
		"""
		Handles the ``wx.EVT_KILL_FOCUS`` event for L{KeyButton}.

		:param `event`: a `wx.FocusEvent` event to be processed.
		"""

		self._hasFocus = False
		self.Refresh()
		self.Update()


	def OnKeyDown(self, event):
		"""
		Handles the ``wx.EVT_KEY_DOWN`` event for L{KeyButton}.

		:param `event`: a `wx.KeyEvent` event to be processed.
		"""
		
		if self._hasFocus and event.GetKeyCode() == ord(" "):
			self._mouseAction = HOVER
			self.Refresh()
		event.Skip()


	def OnKeyUp(self, event):
		"""
		Handles the ``wx.EVT_KEY_UP`` event for L{KeyButton}.

		:param `event`: a `wx.KeyEvent` event to be processed.
		"""
		
		if self._hasFocus and event.GetKeyCode() == ord(" "):
			self._mouseAction = HOVER
			self.Notify()
			self.Refresh()
		event.Skip()


	def SetInitialSize(self, size=None):
		"""
		Given the current font and bezel width settings, calculate
		and set a good size.

		:param `size`: an instance of `wx.Size`.		
		"""
		
		if size is None:
			size = wx.DefaultSize			
		wx.PyControl.SetInitialSize(self, size)

	SetBestSize = SetInitialSize
	

	def AcceptsFocus(self):
		"""
		Can this window be given focus by mouse click?

		:note: Overridden from `wx.PyControl`.
		"""
		
		return self.IsShown() and self.IsEnabled()


	def GetDefaultAttributes(self):
		"""
		Overridden base class virtual. By default we should use
		the same font/colour attributes as the native `wx.Button`.
		"""
		
		return wx.Button.GetClassDefaultAttributes()


	def ShouldInheritColours(self):
		"""
		Overridden base class virtual. Buttons usually don't inherit
		the parent's colours.

		:note: Overridden from `wx.PyControl`.
		"""
		
		return False
	

	def Enable(self, enable=True):
		"""
		Enables/disables the button.

		:param `enable`: ``True`` to enable the button, ``False`` to disable it.
		
		:note: Overridden from `wx.PyControl`.
		"""
		
		wx.PyControl.Enable(self, enable)
		self.Refresh()


	def SetTopStartColour(self, colour):
		"""
		Sets the top start colour for the gradient shading.

		:param `colour`: a valid `wx.Colour` object.
		"""

		self._topStartColour = colour
		self.Refresh()


	def GetTopStartColour(self):
		""" Returns the top start colour for the gradient shading. """

		return self._topStartColour
	

	def SetTopEndColour(self, colour):
		"""
		Sets the top end colour for the gradient shading.

		:param `colour`: a valid `wx.Colour` object.
		"""

		self._topEndColour = colour
		self.Refresh()


	def GetTopEndColour(self):
		""" Returns the top end colour for the gradient shading. """

		return self._topEndColour
		

	def SetBottomStartColour(self, colour):
		"""
		Sets the top bottom colour for the gradient shading.

		:param `colour`: a valid `wx.Colour` object.
		"""

		self._bottomStartColour = colour
		self.Refresh()


	def GetBottomStartColour(self):
		""" Returns the bottom start colour for the gradient shading. """

		return self._bottomStartColour
	
		
	def SetBottomEndColour(self, colour):
		"""
		Sets the bottom end colour for the gradient shading.

		:param `colour`: a valid `wx.Colour` object.
		"""

		self._bottomEndColour = colour
		self.Refresh()


	def GetBottomEndColour(self):
		""" Returns the bottom end colour for the gradient shading. """

		return self._bottomEndColour
	

	def SetPressedTopColour(self, colour):
		"""
		Sets the pressed top start colour for the gradient shading.

		:param `colour`: a valid `wx.Colour` object.
		"""

		self._pressedTopColour = colour
		self.Refresh()


	def GetPressedTopColour(self):
		""" Returns the pressed top start colour for the gradient shading. """

		return self._pressedTopColour
	
		
	def SetPressedBottomColour(self, colour):
		"""
		Sets the pressed bottom start colour for the gradient shading.

		:param `colour`: a valid `wx.Colour` object.
		"""

		self._pressedBottomColour = colour
		self.Refresh()


	def GetPressedBottomColour(self):
		""" Returns the pressed bottom start colour for the gradient shading. """

		return self._pressedBottomColour
	

	def SetForegroundColour(self, colour):
		"""
		Sets the L{KeyButton} foreground (text) colour.

		:param `colour`: a valid `wx.Colour` object.

		:note: Overridden from `wx.PyControl`.		
		"""

		wx.PyControl.SetForegroundColour(self, colour)
		self.Refresh()
		
		
	def DoGetBestSize(self):
		"""
		Overridden base class virtual. Determines the best size of the
		button based on the label and bezel size.
		"""

		label = self.GetLabel()
		if not label:
			return wx.Size(112, 48)
		
		dc = wx.ClientDC(self)
		dc.SetFont(self.GetFont())
		retWidth, retHeight = dc.GetTextExtent(label)
		
		bmpWidth = bmpHeight = 0
		constant = 15
		if self._bitmap:
			bmpWidth, bmpHeight = self._bitmap.GetWidth()+10, self._bitmap.GetHeight()
			retWidth += bmpWidth
			retHeight = max(bmpHeight, retHeight)
			constant = 15

		return wx.Size(retWidth+constant, retHeight+constant) 


	def SetDefault(self):
		""" Sets the default button. """
		
		tlw = wx.GetTopLevelParent(self)
		if hasattr(tlw, 'SetDefaultItem'):
			tlw.SetDefaultItem(self)
		
	def Notify(self):
		""" Actually sends a ``wx.EVT_BUTTON`` event to the listener (if any). """
		
		evt = KeyButtonEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
		evt.SetButtonObj(self)
		evt.SetEventObject(self)
		self.GetEventHandler().ProcessEvent(evt)

	def GetRoundedRectPath(self, gc, rc, r):
		"""
		Returns a rounded `wx.GraphicsPath` rectangle.

		:param `gc`: an instance of `wx.GraphicsContext`;
		:param `rc`: a client rectangle;
		:param `r`: the radious of the rounded part of the rectangle.
		"""
	
		x, y, w, h = rc
		path = gc.CreatePath()
		path.AddRoundedRectangle(x, y, w, h, r)
		path.CloseSubpath()
		return path

	def OnPaint(self, event):
		"""
		Handles the ``wx.EVT_PAINT`` event for L{KeyButton}.

		:param `event`: a `wx.PaintEvent` event to be processed.
		"""

		dc = wx.BufferedPaintDC(self)
		
		gc = wx.GraphicsContext.Create(dc)
		dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
		dc.Clear()
		
		clientRect = self.GetClientRect()

		x, y, width, height = clientRect
		colours = [	self._outsideBottomColour, self._outsideTopColour, self._outsideLineColour,
					self._insideEdgeColour, self._insideCenterColour, self._insideLineColour]
		textColour = wx.BLACK
		outsideRect = wx.Rect(*clientRect)
					
		if wx.Window.GetCapture() != self:
			if self._mouseAction == HOVER:
				colours = [self.LightColour(c) for c in colours]
				textColour = self.LightColour(textColour)
		else:
			# outsideRect.Deflate( 2, 2 )
			colours = [self.DarkColour(c) for c in colours]
			textColour = self.DarkColour(textColour)

		outsideRadius = min(outsideRect.GetWidth(), outsideRect.GetHeight()) // 9
		insideRect = wx.Rect(*clientRect)
		insideRect.Deflate( outsideRadius, outsideRadius )
		insideRadius = min(insideRect.GetWidth(), insideRect.GetHeight()) // 9
		
		outsideBottom, outsideTop, outsideLine, insideEdge, insideCenter, insideLine = colours
		
		# Draw the outside of the button.
		outsidePath = self.GetRoundedRectPath(gc, outsideRect, outsideRadius)
		gc.SetBrush( gc.CreateLinearGradientBrush(
						outsideRect.GetLeft(), outsideRect.GetTop(),
						outsideRect.GetLeft(), outsideRect.GetBottom(),
						outsideTop, outsideBottom) )
		gc.FillPath( outsidePath )
		gc.SetPen( wx.Pen(outsideLine) )
		gc.StrokePath(outsidePath)
		
		# Draw the inside of the button.  First the left half.
		innerRoundedRect = self.GetRoundedRectPath( gc, insideRect, insideRadius )
		xMiddle = width // 2
		gc.SetBrush( gc.CreateLinearGradientBrush(
						insideRect.GetLeft(), insideRect.GetTop(),
						xMiddle, insideRect.GetTop(),
						insideEdge, insideCenter) )
		gc.FillPath( innerRoundedRect )
		
		# Then the right half.  We use a clip region to control the gradient brush.
		gc.SetBrush( gc.CreateLinearGradientBrush(
						xMiddle-1, insideRect.GetTop(),
						insideRect.GetLeft() + insideRect.GetWidth(), insideRect.GetTop(),
						insideCenter, insideEdge) )				
		gc.ClipRegion( wx.Region(xMiddle, 0, width, height) )
		gc.FillPath( innerRoundedRect )
		gc.ClipRegion( wx.Region() )
		
		# Draw the outline of the inner rectangle.
		gc = wx.GraphicsContext.Create(dc)
		gc.SetPen( wx.Pen(insideLine) )
		gc.StrokePath( innerRoundedRect )
		
		gc.SetFont( gc.CreateFont(self.GetFont(), textColour) )
		textHeight = gc.GetTextExtent('0')[1]
		
		#dc.SetTextForeground( textColour )
		#gc.SetTextForeground( wx.BLACK )

		label = self.GetLabel()
		lines = label.split( '\n' )
		yText = (height - textHeight * len(lines)) // 2
		for line in lines:
			textWidth, textHeight = gc.GetTextExtent( line )
                        xText = x + (width - textWidth) // 2
			#print line, (textWidth, textHeight), width, (xText, yText), (width, height)
			gc.DrawText( line, int(xText), int(yText) )
			yText += textHeight
		
		
if __name__ == '__main__':
	# Draw a keyboard with keybuttons.
	# Define the key labels for each row.
	keyRows = [
		['Esc'] + ['F%d' % (i+1) for i in xrange(12)],
		['%s\n%s' % (u,l) for u, l in zip('~!@#$%^&*()_+','`1234567890-=')] + ['Backspace'],
		['Tab'] + [k for k in 'QWERTYUIOP'] + ['%s\n%s' % (u,l) for u, l in zip('{}|','[]\\')],
		['Caps Lock'] + [k for k in 'ASDFGHJKL'] + ['%s\n%s' % (u,l) for u, l in zip(':"',';\'')] + ['Enter'],
		['Shift'] + [k for k in 'ZXCVBNM'] + ['%s\n%s' % (u,l) for u, l in zip('<>?',',./')] + ['Shift'],
		['Ctrl', 'Alt', ' ', 'Alt', 'Ctrl']
	]
	# Specify width exceptions for certain keys.
	# For repeated exceptions for keys with the same name, use a list.
	keyWidth = {'Backspace': 2.0,
				'Tab': 1.5, '|\n\\': 1.5,
				'Caps Lock': 1.75, 'Enter': 2.25,
				'Shift': [2.0, 3.0],
				'Ctrl': 1.75, 'Alt': 1.5, ' ': 8.5 }
	# Specify space exceptions after certain keys.
	keySpaceAfter = {'Esc': 1.0/3.0, 'F4': 1.0/3.0, 'F8': 1.0/3.0 }
	
	# Specify font size exceptions for certain keys.
	keyFontHeight = {'Backspace': 0.95, 'Caps Lock': 0.9 }
	
	border = 8
	rowHeight = 48
	fontSize = rowHeight / 2.6
	shrink = 0.95
	
	backgroundColour = wx.Colour(245,245,245)
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="keybutton", size=((rowHeight+0.75) * 15 + border * 2, rowHeight * (len(keyRows)+0.75) + border * 2))
	mainWin.SetBackgroundColour( backgroundColour )
	
	font = wx.FontFromPixelSize( (0, fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD )
	y = border
	keyWidthCount = {}
	for row in keyRows:
		x = border
		for key in row:
			try:
				mult = keyWidth[key]
				if isinstance( mult, list ):
					try:
						mult = mult[keyWidthCount.setdefault(key, 0)]
						keyWidthCount[key] += 1
					except IndexError:
						mult = 1.0
			except KeyError:
				mult = 1.0
		
			width = rowHeight * mult
			btn = KeyButton( mainWin, wx.ID_ANY, None, key, pos=(x, y), size=(width - rowHeight * (1.0-shrink), rowHeight * shrink) )
			btn.SetBackgroundColour( backgroundColour )
			if key in keyFontHeight:
				btn.SetFont( wx.FontFromPixelSize( (0, fontSize*keyFontHeight[key]), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ) )
			else:
				btn.SetFont( font )
			x += width + keySpaceAfter.get(key, 0) * rowHeight
		y += rowHeight
	mainWin.Show()
	app.MainLoop()

