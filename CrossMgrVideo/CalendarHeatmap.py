# --------------------------------------------------------------------------------- #
# CALENDARHEATMAP wxPython IMPLEMENTATION
#
# Edward Sitarski, @ November 2018
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
# End Of Comments
# --------------------------------------------------------------------------------- #

"""
CalendarHeatmap is a custom-drawn button class which draws a calendar with a specified intensity on each day.


Description
===========

CalendarHeatmap is a custom-drawn class which draws a year-long calendar showing a specified intensity on each day.

Supported Platforms
===================

CalendarHeatmap has been tested on the following platforms:
  * Windows (Windows XP).
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

CalendarHeatmap is distributed under the wxPython license.

Latest Revision: Edward Sitarski @ 22 Dec 2017, 17.00 EST

Version 0.1

"""

import wx
import wx.lib.agw.artmanager as AM
from math import sqrt
import datetime

def daterange(start, end, step=datetime.timedelta(1)):
	curr = start
	while curr < end:
		yield curr
		curr += step

class CalendarHeatmapEvent(wx.PyCommandEvent):
	""" Event sent from L{CalendarHeatmap} when the button is activated. """
	
	def __init__(self, eventType, eventId):
		"""
		Default class constructor.

		:param `eventType`: the event type;
		:param `eventId`: the event identifier.
		"""
		
		super().__init__(eventType, eventId)
		self.theButton = None
		self.date = None

	def SetButtonObj(self, btn):
		"""
		Sets the event object for the event.

		:param `btn`: the button object, an instance of L{CalendarHeatmap}.
		"""
		
		self.theButton = btn

	def GetButtonObj(self):
		""" Returns the object associated with this event. """
		
		return self.theButton
		
	def SetDate( self, date ):
		self.date = date

	def GetDate(self):
		return self.date

	
class CalendarHeatmap(wx.Control):
	""" This is the main class implementation of L{CalendarHeatmap}. """
	
	def __init__(self, parent, id=wx.ID_ANY, year=None, dates=None, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.NO_BORDER, validator=wx.DefaultValidator,
				 name="CalendarHeatmap"):
		"""
		Default class constructor.

		:param `parent`: the L{CalendarHeatmap} parent;
		:param `id`: window identifier. A value of -1 indicates a default value;
		:param `year`: the year to display;
		:param `pos`: the control position. A value of (-1, -1) indicates a default position,
		 chosen by either the windowing system or wxPython, depending on platform;
		:param `size`: the control size. A value of (-1, -1) indicates a default size,
		 chosen by either the windowing system or wxPython, depending on platform;
		:param `style`: the button style (unused);
		:param `validator`: the validator associated to the button;
		:param `name`: the button name.
		"""
		
		super().__init__(parent, id, pos, size, style, validator, name)

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick )
		self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

		self._mouseAction = None
		self._hasFocus = False
		
		self.SetYear( year, False )
		self.SetDates( dates, False )
		self.date = None
		self.dateSelect = None
		
		self._getGridDate()
		self.InheritAttributes()
		self.SetInitialSize(size)

	def SetYear( self, year, refresh=True ):
		year = year or datetime.datetime.now().year
		self.year = year
		if refresh:
			self.Refresh()
		
	def SetDates( self, dates, refresh=True ):
		dates = dates or {}
		if not isinstance(dates, dict):
			dates = {v[0]:v[1] for v in dates}
		self.dates = dates
		if refresh:
			self.Refresh()
			
	def SetDate( self, date ):
		self.year = date.year
		self.dateSelect = date
		self.Refresh()
		
	def OnSize(self, event):
		event.Skip()
		self.Refresh()

		
	def OnLeftDClick(self, event):
		if not self.IsEnabled():
			return
		
		self.dateSelect = self.date
		if self.date:
			self.Notify(wx.wxEVT_COMMAND_LEFT_DCLICK)
		self.Refresh()
		event.Skip()


	def OnLeftUp(self, event):
		if not self.IsEnabled():
			return
		
		self.dateSelect = self.date
		if self.date:
			self.Notify()
		self.Refresh()
		event.Skip()


	def OnMouseMotion(self, event):
		self.date = self._dateFromXY( event.GetX(), event.GetY() )
		self.Refresh()

	def SetInitialSize(self, size=None):
		if size is None:
			size = self.DoGetBestSize()
		wx.Control.SetInitialSize(self, size)

	SetBestSize = SetInitialSize
	

	def AcceptsFocusFromKeyboard( self ):
		return True
		
	def AcceptsFocus( self ):
		return False
	
	def GetDefaultAttributes(self):
		return wx.Button.GetClassDefaultAttributes()


	def ShouldInheritColours(self):
		"""
		Overridden base class virtual. Buttons usually don't inherit
		the parent's colours.

		:note: Overridden from `wx.Control`.
		"""
		
		return False
	

	def Enable(self, enable=True):
		"""
		Enables/disables the button.

		:param `enable`: ``True`` to enable the button, ``False`` to disable it.
		
		:note: Overridden from `wx.Control`.
		"""
		
		wx.Control.Enable(self, enable)
		self.Refresh()


	def DoGetBestSize(self):
		"""
		Overridden base class virtual. Determines the best size of the
		button based on the label and bezel size.
		"""
		bestHeight = 150
		rowHeight = bestHeight // 9
		return wx.Size( rowHeight*53+rowHeight*3, bestHeight )


	def SetDefault(self):
		""" Sets the default button. """
		
		tlw = wx.GetTopLevelParent(self)
		if hasattr(tlw, 'SetDefaultItem'):
			tlw.SetDefaultItem(self)
			
	def GetValue( self ):
		return self.dateSelect
		
	def SetValue( self, d ):
		self.dateSelect = d
		
	def Notify(self, type=wx.wxEVT_COMMAND_BUTTON_CLICKED):
		""" Actually sends a ``wx.EVT_BUTTON`` event to the listener (if any). """
		
		evt = CalendarHeatmapEvent(type, self.GetId())
		evt.SetEventObject( self )
		evt.SetDate( self.dateSelect )
		self.GetEventHandler().ProcessEvent(evt)
		
	def _yearWeeks( self ):
		return 53
	
	def _setDimensions( self, dc ):
		x, y, width, height = self.GetClientRect()
		self.rowHeight = int(height / 9.0)
		font = wx.Font(wx.FontInfo((0,int(self.rowHeight)*.9)))
		dc.SetFont( font )
		self.leftLabelRect = wx.Rect( x, y+self.rowHeight*1, dc.GetTextExtent('W ')[0], self.rowHeight*7 )
		self.topLabelRect = wx.Rect( x+self.leftLabelRect.GetWidth(), y, self._yearWeeks()*self.rowHeight, self.rowHeight )
		self.bodyRect = wx.Rect( self.topLabelRect.GetX(), self.leftLabelRect.GetY(), self.topLabelRect.GetWidth(), self.rowHeight*7 )
		self.bottomLabelRect = wx.Rect( self.bodyRect.GetX(), self.bodyRect.GetBottom(), self.bodyRect.GetWidth(), self.rowHeight )
		
	def _getGridDate( self ):
		self.gridDate = {}
		self.dateGrid = {}
		weekCount = 0
		for d in daterange(datetime.date(self.year, 1, 1), datetime.date(self.year+1, 1, 1)):
			weekday = d.weekday()	# Monday=0, Sunday=6
			self.gridDate[(weekCount, weekday)] = d
			self.dateGrid[d] = (weekCount, weekday)
			if weekday == 6:
				weekCount += 1
	
	def _dateFromXY( self, x, y ):
		return self.gridDate.get( ((x-self.bodyRect.GetX())//self.rowHeight, (y-self.bodyRect.GetY())//self.rowHeight), None )
		
	def _xyFromDate( self, d ):
		c, r = self.dateGrid[d]
		x, y = self.bodyRect.GetX() + c*self.rowHeight, self.bodyRect.GetY() + r*self.rowHeight
		return x, y		
	
	def OnPaint(self, event):
		"""
		Handles the ``wx.EVT_PAINT`` event for L{CalendarHeatmap}.

		:param `event`: a `wx.PaintEvent` event to be processed.
		"""

		dc = wx.BufferedPaintDC(self)
		
		self._getGridDate()
		self._setDimensions( dc )
		
		am = AM.ArtManager()
		
		gc = wx.GraphicsContext.Create(dc)

		dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
		dc.Clear()
		
		colour = self.GetForegroundColour()
		textColour = am.DarkColour(wx.WHITE, 3.0) if am.IsDark(colour) else am.LightColour(wx.BLACK, 3.0)
		
		valueMax = max( self.dates.values(), default=1 )
		
		gc = wx.GraphicsContext.Create(dc)
		
		for r, w in enumerate('MTWTFSS'):
			x, y = self.leftLabelRect.GetX(), self.leftLabelRect.GetY() + self.rowHeight*r
			width = dc.GetTextExtent(w)[0]
			dc.DrawText( w, x + (self.leftLabelRect.GetWidth() - width) // 2, y )
		
		if self.date:
			x, y = self._xyFromDate( self.date )
			dText = '{}: {}'.format( self.date.strftime('%Y-%m-%d'), self.dates.get(self.date, 0) )
			width = dc.GetTextExtent( dText )[0]
			if x+width > self.bodyRect.GetRight():
				x = self.bodyRect.GetRight() - width
			dc.DrawText( dText, x, self.bottomLabelRect.GetY() )
		else:
			dText = '{}'.format( self.year )
			dc.DrawText( dText, self.bottomLabelRect.GetX(), self.bottomLabelRect.GetY() )
		
		backgrounds = [wx.Brush(wx.Colour(200,200,200), wx.SOLID), wx.Brush(wx.Colour(230,230,230), wx.SOLID)]
		monthCur = 0
		gc.SetPen( wx.TRANSPARENT_PEN )
		for d in daterange(datetime.date(self.year, 1, 1), datetime.date(self.year+1, 1, 1)):
			x, y = self._xyFromDate( d )
			gc.SetBrush( backgrounds[d.month&1] if d != self.date else wx.GREEN_BRUSH )			
			gc.DrawRectangle( x, y, self.rowHeight, self.rowHeight )
			
			s = self.dates.get(d, None)
			if s:
				gc.SetBrush( wx.RED_BRUSH )
				size = max(3, self.rowHeight * sqrt((float(s) / valueMax)))
				cc = (self.rowHeight - size) / 2
				gc.DrawEllipse( x + cc, y + cc, size, size )
			
			if d.month != monthCur:
				y = self.topLabelRect.GetY()
				dc.DrawText( d.strftime('%b'), x, y )
				monthCur = d.month
		
		if self.dateSelect:
			x, y = self._xyFromDate( self.dateSelect )
			gc.SetBrush( wx.TRANSPARENT_BRUSH )
			gc.SetPen( wx.Pen(wx.BLACK, 2) )
			gc.DrawRectangle( x-1, y-1, self.rowHeight+1, self.rowHeight+1 )
		
if __name__ == '__main__':
	import random

	# Self-test.
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CalendarHeatmap", size=(1156,400))
	mainWin.SetBackgroundColour( wx.WHITE )
	vs = wx.BoxSizer( wx.VERTICAL )
	
	year = datetime.datetime.now().year
	dates = [(d,random.randint(0,1000)) for d in daterange(datetime.date(year, 1, 1), datetime.date(year+1, 1, 1))]
	chm = CalendarHeatmap( mainWin, dates=dates )
	def onPress( event ):
		print( 'Pressed: ', event.GetDate() )
	
	chm.Bind( wx.EVT_BUTTON, onPress )
	vs.Add( chm )
	
	mainWin.SetSizer( vs )
	mainWin.Show()
	app.MainLoop()

