
import  time
import  wx

#---------------------------------------------------------------------------

class CurStatus(wx.StatusBar):
	def __init__(self, parent):
		wx.StatusBar.__init__(self, parent, -1)

		# This status bar has three fields
		self.SetFieldsCount(3)
		# Sets the three fields to be relative widths to each other.
		self.SetStatusWidths([-2, -1, -2])
		self.sizeChanged = False
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_IDLE, self.OnIdle)

		# Field 0 ... just text
		self.SetMessage()

		# This will fall into field 1 (the second field)
		self.cb = wx.CheckBox(self, 1001, "toggle clock")
		self.Bind(wx.EVT_CHECKBOX, self.OnToggleClock, self.cb)
		self.cb.SetValue(True)

		# set the initial position of the checkbox
		self.Reposition()

	def SetMessage( self, message = '' ):
		self.SetStatusText( message, 0 )
		
	# Handles events from the timer we started in __init__().
	# We're using it to drive a 'clock' in field 2 (the third field).
	def refresh(self, event):
		t = time.localtime(time.time())
		st = time.strftime("%d-%b-%Y   %H:%M:%S", t)
		self.SetStatusText(st, 2)

	# the checkbox was clicked
	def OnToggleClock(self, event):
		if self.cb.GetValue():
			self.timer.Start(1000)
			self.OnTimer(None)
		else:
			self.timer.Stop()

	def OnSize(self, evt):
		self.Reposition()  # for normal size events

		# Set a flag so the idle time handler will also do the repositioning.
		# It is done this way to get around a buglet where GetFieldRect is not
		# accurate during the EVT_SIZE resulting from a frame maximize.
		self.sizeChanged = True

	def OnIdle(self, evt):
		if self.sizeChanged:
			self.Reposition()

	# reposition the checkbox
	def Reposition(self):
		rect = self.GetFieldRect(1)
		self.cb.SetPosition((rect.x+2, rect.y+2))
		self.cb.SetSize((rect.width-4, rect.height-4))
		self.sizeChanged = False
