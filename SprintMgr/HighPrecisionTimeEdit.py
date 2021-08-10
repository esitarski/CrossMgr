import wx
import re
import platform
import datetime
import Utils

reNonTimeChars = re.compile('[^0-9:.]')

def secsToValue( secs, allow_none, display_seconds, display_milliseconds ):
	if secs is None and allow_none:
		return secs
	v = Utils.formatTime(
			secs,
			highPrecision=True,		extraPrecision=True,
			forceHours=True, 		twoDigitHours=True,
		)
	if not display_seconds:
		v = v[:v.rfind(':')]
	elif not display_milliseconds:
		if '.' in v:
			v = v[:v.find('.')]
	return v
	
def valueToSecs( v, display_seconds, display_milliseconds ):
	if v is None:
		return v
	v = reNonTimeChars.sub( '', '{}'.format(v) )
	if not display_seconds:
		if len(v.split(':')) < 3:
			v += ':00'
	elif not display_milliseconds:
		v = v[:v.find('.')] if '.' in v else v
	return Utils.StrToSeconds( v )

def getSeconds( v, display_seconds, display_milliseconds ):
	if   isinstance( v, str ):
		return valueToSecs( v, display_seconds, display_milliseconds )
	elif isinstance( v, wx.DateTime ):
		return v.GetHour()*60*60 + v.GetMinute()*60 + v.GetSecond() + v.GetMillisecond()/1000.0
	elif isinstance( v, (datetime.datetime, datetime.time) ):
		return v.hour*60*60 + v.minute*60 + v.second + v.microsecond/1000000.0
	elif isinstance( v, (float, int) ):
		return v
	else:
		return 0.0

# Masked controls still don't work on anything but Windows.  Sigh :(
if platform.system() == 'Windows':
	import wx.lib.masked as masked
	class HighPrecisionTimeEdit( masked.TextCtrl ):
		mask         = '##:##:##.###'
		validRegex   = '[0-9][0-9]:[0-5][0-9]:[0-5][0-9]\.[0-9][0-9][0-9]'

		def __init__( self, parent, id=wx.ID_ANY, seconds=None, display_seconds=True, display_milliseconds=True, value=None, allow_none=False, style=0, size=wx.DefaultSize ):
			# Utils.writeLog( 'HighPrecisionTimeEdit: Windows' )
			
			self.allow_none = allow_none
			self.display_seconds = display_seconds
			self.display_milliseconds = display_seconds and display_milliseconds
			if not display_seconds:
				self.mask       = '##:##'
				self.validRegex = '[0-9][0-9]:[0-5][0-9]'
			elif not display_milliseconds:
				self.mask       = '##:##:##'
				self.validRegex = '[0-9][0-9]:[0-5][0-9]:[0-5][0-9]'			
			
			self.defaultValue = self.mask.replace('#', '0')
			self.emptyValue   = self.mask.replace('#', ' ')
			super().__init__(
				parent, id,
				mask		 = self.mask,
				defaultValue = value or self.defaultValue,
				validRegex   = self.validRegex,
				useFixedWidthFont = False,
				style		 = style & ~(wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB|wx.TE_MULTILINE|wx.TE_PASSWORD),
				size         = size,
			)
			if seconds is not None:
				self.SetSeconds( seconds )
		
		def GetSeconds( self ):
			v = self.GetValue()
			if self.allow_none and v == self.emptyValue:
				return None
			return valueToSecs( v, self.display_seconds, self.display_milliseconds )
			
		def SetSeconds( self, secs ):
			super().SetValue( secsToValue(secs, self.allow_none, self.display_seconds, self.display_milliseconds) )
			
		def SetValue( self, v ):
			if self.allow_none and v is None:
				super().SetValue( '' )
			else:
				self.SetSeconds( getSeconds(v, self.display_seconds, self.display_milliseconds) )

else:
	import string

	class TextBoxTipPopup( wx.PopupTransientWindow ):
		"""Basic Tooltip"""
		def __init__(self, parent, style, text):
			super().__init__(parent, style)
			self.SetBackgroundColour(wx.YELLOW)
			border = 10
			st = wx.StaticText(self, label = text, pos=(border/2,border/2))
			sz = st.GetBestSize()
			self.SetSize( (sz.width+border, sz.height+border) )

	class HighPrecisionTimeEdit( wx.TextCtrl ):
		defaultValue = '00:00:00.000'
		emptyValue   = ''

		def __init__( self, parent, id=wx.ID_ANY, seconds=None, value=None, display_seconds=True, display_milliseconds=True, allow_none=False, style=0, size=wx.DefaultSize ):
		
			# Utils.writeLog( 'HighPrecisionTimeEdit: Mac/Linux' )
			
			self.allow_none = allow_none
			self.display_seconds = display_seconds
			self.display_milliseconds = display_seconds and display_milliseconds
			if not display_seconds:
				self.defaultValue = '00:00'
			elif not display_milliseconds:
				self.defaultValue = '00:00:00'
			value = self.defaultValue if value is None else reNonTimeChars.sub( '', '{}'.format(value) )
			super().__init__(
				parent, id,
				value		= value,
				style		= style & ~(wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB|wx.TE_MULTILINE|wx.TE_PASSWORD),
				size        = size,
			)
			seconds = seconds if seconds is not None else valueToSecs( value, self.display_seconds, self.display_milliseconds )
			self.SetSeconds( seconds )
			self.Bind(wx.EVT_CHAR, self.onKeypress)
			self.Bind(wx.EVT_TEXT_PASTE, self.onPaste)
			self.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)

		def onKeypress(self, event):
			keycode = event.GetKeyCode()
			obj = event.GetEventObject()
			val = obj.GetValue()
			
			# filter unicode characters
			if keycode == wx.WXK_NONE:
				pass 
			# allow digits and colon
			elif chr(keycode) in string.digits or keycode == 9 or keycode == 58:
				event.Skip()
			# allow special, non-printable keycodes
			elif chr(keycode) not in string.printable:
				event.Skip() # allow all other special keycode
			# allow one '.'
			elif chr(keycode) == '.' and '.' not in val:
				event.Skip()
			return
		
		def onPaste(self, event):
			self.text_data = wx.TextDataObject()
			if wx.TheClipboard.Open():
				success = wx.TheClipboard.GetData(self.text_data)
				wx.TheClipboard.Close()
			if success:
				self.text_data = self.text_data.GetText()
				if self.ValidateTimeFormat(self.text_data):
					self.SetValue(self.text_data)
					return
				else:
					WarnTip = TextBoxTipPopup(self, wx.SIMPLE_BORDER,"Incorrect time format on the clipboard")
					xPos, yPos = self.GetPosition()
					height = WarnTip.GetClientSize()[1]
					pos = self.ClientToScreen( (xPos - xPos, yPos - yPos + height) )
					WarnTip.Position( pos, (0,0) )
					WarnTip.Popup()

		def onDoubleClick(self, event):
			self.SetSelection(-1,-1)

		def ValidateTimeFormat(self, time):
			if not time and self.allow_none:
				return True
			
			for format in ('%H:%M', '%H:%M:%S', '%H:%M:%S.%f'):
				try:
					datetime.datetime.strptime(time, format)
					return True
				except Exception:
					pass
				
			return False

		def GetSeconds( self ):
			v = self.GetValue()
			if self.allow_none and v == self.emptyValue:
				return None
			return valueToSecs( v, self.display_seconds, self.display_milliseconds )
			
		def SetSeconds( self, secs ):
			super().SetValue( secsToValue(secs, self.allow_none, self.display_seconds, self.display_milliseconds) )
			
		def SetValue( self, v ):
			if self.allow_none and v is None:
				super().SetValue( '' )
			else:
				self.SetSeconds( getSeconds(v, self.display_seconds, self.display_milliseconds) )
		
		def GetValue( self ):
			v = super().GetValue()
			if v is None:
				return None
			v = reNonTimeChars.sub( '', v )
			if v == self.emptyValue and self.allow_none:
				return None
			if not self.display_seconds and len(v.split(':')) < 3:
				v += ':00'
			secs = Utils.StrToSeconds( v )
			return secsToValue( secs, self.allow_none, self.display_seconds, self.display_milliseconds )

if __name__ == '__main__':

	# Self-test.
	app = wx.App(False)
	mainWin = wx.Frame(None,title="hpte", size=(1024,600))
	vs = wx.BoxSizer( wx.VERTICAL )
	
	hpte1 = HighPrecisionTimeEdit( mainWin, value="10:00:00", size=(200,-1) )
	hpte2 = HighPrecisionTimeEdit( mainWin, display_milliseconds=False, value="10:00", size=(200,-1) )
	hpte3 = HighPrecisionTimeEdit( mainWin, display_seconds=False, value="10:00", size=(200,-1) )
	
	def getValues( event ):
		print( 'hpte1: {}, {}'.format(hpte1.GetValue(), hpte1.GetSeconds()) ) 
		print( 'hpte2: {}, {}'.format(hpte2.GetValue(), hpte2.GetSeconds()) )
		print( 'hpte3: {}, {}'.format(hpte3.GetValue(), hpte3.GetSeconds()) )
	
	button = wx.Button( mainWin, label='Get Values' )
	button.Bind( wx.EVT_BUTTON, getValues )
	
	vs.Add( hpte1, flag=wx.ALL, border=16 )
	vs.Add( hpte2, flag=wx.ALL, border=16 )
	vs.Add( hpte3, flag=wx.ALL, border=16 )
	vs.Add( button, flag=wx.ALL, border=16 )

	mainWin.SetSizerAndFit( vs )
	mainWin.Show()
	app.MainLoop()

	
