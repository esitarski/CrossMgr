# --------------------------------------------------------------------------------- #
# ROUNDBUTTON wxPython IMPLEMENTATION
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
# Or, obviously, to the wxPython mailing list!!!
#
#
# End Of Comments
# --------------------------------------------------------------------------------- #

"""
RoundButton is another custom-drawn button class which mimics Windows CE mobile
gradient buttons.


Description
===========

RoundButton is another custom-drawn button class which mimics a Mac keyboard.

Supported Platforms
===================

RoundButton has been tested on the following platforms:
  * Windows (Windows XP).


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

RoundButton is distributed under the wxPython license.

Latest Revision: Andrea Gavana @ 27 Nov 2009, 17.00 GMT

Version 0.3

"""

import wx
import math
import wx.lib.agw.artmanager as AM

HOVER = 1
CLICK = 2

class RoundButtonEvent(wx.PyCommandEvent):
	""" Event sent from L{RoundButton} when the button is activated. """
	
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

		:param `btn`: the button object, an instance of L{RoundButton}.
		"""
		
		self.theButton = btn


	def GetButtonObj(self):
		""" Returns the object associated with this event. """
		
		return self.theButton

	
class RoundButton(wx.PyControl):
	""" This is the main class implementation of L{RoundButton}. """
	
	def __init__(self, parent, id=wx.ID_ANY, bitmap=None, label="", pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				 name="roundbutton"):
		"""
		Default class constructor.

		:param `parent`: the L{RoundButton} parent;
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
		self._buttonRadius = 10
		
		self.SetLabel(label)
		self.InheritAttributes()
		self.SetInitialSize(size)

	def OnSize(self, event):
		"""
		Handles the ``wx.EVT_SIZE`` event for L{RoundButton}.

		:param `event`: a `wx.SizeEvent` event to be processed.
		"""
		
		event.Skip()
		self.Refresh()

		
	def ContainsEvent( self, event ):
		rect = self.GetClientRect()
		x = rect.GetX() + rect.GetWidth() / 2
		y = rect.GetY() + rect.GetHeight() / 2
		px, py = event.GetPosition().Get()
		dx = px - x
		dy = py - y
		return dx * dx + dy * dy < self._buttonRadius * self._buttonRadius
		
	def OnLeftDown(self, event):
		"""
		Handles the ``wx.EVT_LEFT_DOWN`` event for L{RoundButton}.

		:param `event`: a `wx.MouseEvent` event to be processed.
		"""

		if not self.IsEnabled() or not self.ContainsEvent(event):
			return
		
		self._mouseAction = CLICK
		self.CaptureMouse()
		self.Refresh()
		event.Skip()


	def OnLeftUp(self, event):
		"""
		Handles the ``wx.EVT_LEFT_UP`` event for L{RoundButton}.

		:param `event`: a `wx.MouseEvent` event to be processed.
		"""

		if not self.IsEnabled() or not self.HasCapture():
			return
		
		if self.HasCapture():
			self.ReleaseMouse()
			
		if self.ContainsEvent(event):
			self._mouseAction = HOVER
			self.Notify()
		else:
			self._mouseAction = None

		self.Refresh()
		event.Skip()


	def OnMouseEnter(self, event):
		"""
		Handles the ``wx.EVT_ENTER_WINDOW`` event for L{RoundButton}.

		:param `event`: a `wx.MouseEvent` event to be processed.
		"""

		if not self.IsEnabled():
			return
		
		self._mouseAction = HOVER
		self.Refresh()
		event.Skip()


	def OnMouseLeave(self, event):
		"""
		Handles the ``wx.EVT_LEAVE_WINDOW`` event for L{RoundButton}.

		:param `event`: a `wx.MouseEvent` event to be processed.
		"""

		self._mouseAction = None
		self.Refresh()
		event.Skip()


	def OnGainFocus(self, event):
		"""
		Handles the ``wx.EVT_SET_FOCUS`` event for L{RoundButton}.

		:param `event`: a `wx.FocusEvent` event to be processed.
		"""
		
		self._hasFocus = True
		self.Refresh()
		self.Update()


	def OnLoseFocus(self, event):
		"""
		Handles the ``wx.EVT_KILL_FOCUS`` event for L{RoundButton}.

		:param `event`: a `wx.FocusEvent` event to be processed.
		"""

		self._hasFocus = False
		self.Refresh()
		self.Update()


	def OnKeyDown(self, event):
		"""
		Handles the ``wx.EVT_KEY_DOWN`` event for L{RoundButton}.

		:param `event`: a `wx.KeyEvent` event to be processed.
		"""
		
		if self._hasFocus and event.GetKeyCode() == ord(" "):
			self._mouseAction = HOVER
			self.Refresh()
		event.Skip()


	def OnKeyUp(self, event):
		"""
		Handles the ``wx.EVT_KEY_UP`` event for L{RoundButton}.

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


	def DoGetBestSize(self):
		"""
		Overridden base class virtual. Determines the best size of the
		button based on the label and bezel size.
		"""

		label = self.GetLabel()
		if not label:
			return wx.Size(32, 32)
		
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
		
		evt = RoundButtonEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
		evt.SetButtonObj(self)
		evt.SetEventObject(self)
		self.GetEventHandler().ProcessEvent(evt)

	def OnPaint(self, event):
		"""
		Handles the ``wx.EVT_PAINT`` event for L{RoundButton}.

		:param `event`: a `wx.PaintEvent` event to be processed.
		"""

		dc = wx.BufferedPaintDC(self)
		
		am = AM.ArtManager()
		
		gc = wx.GraphicsContext.Create(dc)
		dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
		dc.Clear()
		
		clientRect = self.GetClientRect()
		boundaryRect = clientRect

		x, y, width, height = clientRect
		colour = self.GetForegroundColour()
		textColour = am.DarkColour(wx.WHITE, 3.0) if am.IsDark(colour) else am.LightColour(wx.BLACK, 3.0)
					
		pressed = False
		if wx.Window.GetCapture() != self:
			if self._mouseAction == HOVER:
				colour = am.LightColour(colour, 10.0)
		else:
			colour = am.DarkColour(colour, 10.0)
			textColour = am.DarkColour(textColour, 10.0)
			pressed = True

		r = min(boundaryRect.GetWidth(), boundaryRect.GetHeight()) // 2
		xCenter = x + width // 2
		yCenter = y + height // 2
		
		gc.SetPen( wx.TRANSPARENT_PEN )
		
		def drawCircle( x, y, r ):
			gc.DrawEllipse( x - r, y - r, r * 2, r * 2 )
		
		# Draw the metal ring
		gc.SetBrush( gc.CreateRadialGradientBrush(
						xCenter, yCenter - r,
						xCenter, yCenter - r,
						r * 2,
						wx.WHITE, wx.Colour(33,33,33) ) )
		drawCircle( xCenter, yCenter, r )
		
		rSmaller = r * 0.80
		gc.SetBrush( gc.CreateRadialGradientBrush(
						xCenter, yCenter + rSmaller,
						xCenter, yCenter + rSmaller,
						rSmaller * 2,
						wx.WHITE, wx.Colour(33,33,33) ) )
		drawCircle( xCenter, yCenter, rSmaller )
		
		# Draw the body of the button.
		rSmaller *= 0.93
		if pressed:
			rSmaller *= 0.95
		cRegular = colour
		gc.SetBrush( gc.CreateRadialGradientBrush(
						xCenter, yCenter + rSmaller * 0.9,
						xCenter, yCenter + rSmaller,
						rSmaller * 2,
						am.LightColour(colour, 75.0), cRegular ) )
		drawCircle( xCenter, yCenter, rSmaller )
		self._buttonRadius = rSmaller
		
		# Draw the flare at the top of the button.
		gc.SetBrush( gc.CreateLinearGradientBrush(
						xCenter - rSmaller, yCenter - rSmaller,
						xCenter - rSmaller, yCenter,
						am.LightColour(colour, 40.0), am.LightColour(colour, 30.0)) )
		rWidth = (rSmaller * 2.0 * 0.7) * 0.9
		rHeight = (rSmaller * 0.8) * 0.9
		gc.DrawEllipse( xCenter - rWidth / 2, yCenter - rSmaller, rWidth, rHeight )
		
		# Draw an outline around the body - this also covers up any gaps between the flare and the edge of the button.
		gc.SetPen( wx.Pen(wx.Colour(50,50,50), r * 0.025) )
		gc.SetBrush( wx.TRANSPARENT_BRUSH )
		gc.DrawEllipse( xCenter - rSmaller, yCenter - rSmaller, rSmaller * 2, rSmaller * 2 )
		
		dc.SetTextForeground( textColour )

		label = self.GetLabel().strip()
		if not label:
			return
		lines = label.split('\n') 
		dc.SetFont( self.GetFont() )
		textWidth, textHeight = dc.GetTextExtent( label[0] )
		textHeightMax = textHeight * len(lines)
		textWidthMax = max( dc.GetTextExtent(line)[0] for line in lines )
		
		yText = yCenter - textHeight * len(lines) / 2.0
		for line in lines:
			textWidth, textHeight = dc.GetTextExtent( line )
			dc.DrawText( line, xCenter - textWidth // 2, yText )
			yText += textHeight
		
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="roundbutton", size=(400,180))
	#btn = RoundButton(mainWin, wx.ID_ANY, None, 'Start\nat Time')
	#btn = RoundButton(mainWin, wx.ID_ANY, None, 'STOP')
	btn = RoundButton(mainWin, wx.ID_ANY, None, 'GO')
	btn.SetBackgroundColour( wx.WHITE )
	#btn.SetForegroundColour( wx.Colour(0,0,128) )
	btn.SetForegroundColour( wx.Colour(0,128,0) )
	#btn.SetForegroundColour( wx.Colour(128,0,0) )
	btn.SetFont( wx.Font(36, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, face = 'Arial Rounded MT Bold' ) )
	mainWin.Show()
	app.MainLoop()

