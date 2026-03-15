import wx
import re
import string
import datetime
import Utils

reNonTimeChars = re.compile(r'[^0-9:.]')

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

def trimTimeLeadingZeros( s ):
	if m := re.search('^[:0]+', s):
		s = s[len(m.group(0)):]
	if s and not s[0].isdigit():
		s = '0' + s
	return s

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
	emptyValue   = ''

	def __init__( self, parent, id=wx.ID_ANY, seconds=None, value=None, display_seconds=True, display_milliseconds=True, allow_none=False, trim_leading_zeros=False, style=0, size=wx.DefaultSize ):	
		self.allow_none = allow_none
		self.display_seconds = display_seconds
		self.display_milliseconds = display_seconds and display_milliseconds
		self.trim_leading_zeros = trim_leading_zeros
		if self.allow_none:
			self.defaultValue = ''
		else:
			self.defaultValue = '00:00:00.000'
			if not display_seconds:
				self.defaultValue = '00:00'
			elif not display_milliseconds:
				self.defaultValue = '00:00:00'
			if self.trim_leading_zeros:
				self.defaultValue = trimTimeLeadingZeros( self.defaultValue )
		value = self.defaultValue if value is None else reNonTimeChars.sub( '', f'{value}' )
		super().__init__(
			parent, id,
			value		= value,
			style		= style & ~(wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB|wx.TE_MULTILINE|wx.TE_PASSWORD),
			size        = size,
		)
		# Seconds, if given, overrides value.
		if seconds is not None:
			self.SetSeconds( seconds )
		self.Bind(wx.EVT_CHAR, self.onKeypress)
		self.Bind(wx.EVT_TEXT_PASTE, self.onPaste)
		self.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)

	ALLOWED_CODES = (
		{										# Allow tab, colon and control codes.
			9, 58,
			wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_CLEAR, wx.WXK_SHIFT, wx.WXK_ESCAPE, wx.WXK_TAB, 	
			wx.WXK_CANCEL, wx.WXK_SHIFT,
			wx.WXK_RETURN, wx.WXK_HOME, wx.WXK_END, wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_SELECT, wx.WXK_INSERT,
		} |
		{										# Allow keypad codes.
			wx.WXK_NUMPAD_DELETE,
			wx.WXK_NUMPAD_ENTER, wx.WXK_NUMPAD_HOME, wx.WXK_NUMPAD_LEFT, wx.WXK_NUMPAD_RIGHT,
			wx.WXK_NUMPAD_INSERT, wx.WXK_NUMPAD_END, wx.WXK_NUMPAD_BEGIN, wx.WXK_NUMPAD_DELETE,
			wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3, wx.WXK_NUMPAD4,
			wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7, wx.WXK_NUMPAD8, wx.WXK_NUMPAD9,
		} |
		{ ord(c) for c in string.digits }		# Allow digit codes.
	)
	PRINTABLE = { ord(c) for c in string.printable }
	DECIMAL_POINT = { wx.WXK_DECIMAL, wx.WXK_NUMPAD_DECIMAL, ord('.') }
	def onKeypress(self, event):
		keycode = event.GetKeyCode()
		obj = event.GetEventObject()
		val = super(HighPrecisionTimeEdit, obj).GetValue()	# Use the unformatted text value.
		
		# filter unicode characters
		if keycode == wx.WXK_NONE:
			pass 
		# allow digits and other valid key codes.
		elif keycode in HighPrecisionTimeEdit.ALLOWED_CODES:
			event.Skip()
		# allow other special, non-printable keycodes.
		elif keycode not in HighPrecisionTimeEdit.PRINTABLE:
			event.Skip()
		# accept one decimal point ('.') in the value.
		elif keycode in HighPrecisionTimeEdit.DECIMAL_POINT and val and '.' not in val:
			event.Skip()
		return
	
	def onPaste(self, event):
		self.text_data = wx.TextDataObject()
		if wx.TheClipboard.Open():
			success = wx.TheClipboard.GetData(self.text_data)
			wx.TheClipboard.Close()
		if success:
			# Change non-time characters to ':' with the exception of "'" (seconds), which we can delete.
			self.text_data = reNonTimeChars.sub( ':', self.text_data.GetText().replace("'", ' ' ).strip() )
			if self.ValidateTimeFormat(self.text_data):
				self.SetValue(self.text_data)
				return
			else:
				WarnTip = TextBoxTipPopup(self, wx.SIMPLE_BORDER, "Incorrect time format on the clipboard")
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
		return bool(re.match('^[0-9:.]+$', time))

	def GetSeconds( self ):
		v = self.GetValue()
		if self.allow_none and v == self.emptyValue:
			return None
		return valueToSecs( v, self.display_seconds, self.display_milliseconds )
		
	def SetSeconds( self, secs ):
		value = secsToValue(secs, self.allow_none, self.display_seconds, self.display_milliseconds) or ''
		if self.trim_leading_zeros:
			value = trimTimeLeadingZeros( value )
		super().SetValue( value )
		
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
		value = secsToValue( secs, self.allow_none, self.display_seconds, self.display_milliseconds )
		return trimTimeLeadingZeros(value) if self.trim_leading_zeros else value

if __name__ == '__main__':

	# Self-test.
	app = wx.App(False)
	mainWin = wx.Frame(None,title="hpte", size=(1024,600))
	vs = wx.BoxSizer( wx.VERTICAL )
	
	hpte1 = HighPrecisionTimeEdit( mainWin, value="10:00:00", allow_none=True, size=(200,-1) )
	hpte2 = HighPrecisionTimeEdit( mainWin, display_milliseconds=False, value="10:00", size=(200,-1) )
	hpte3 = HighPrecisionTimeEdit( mainWin, display_seconds=False, value="10:00", size=(200,-1) )
	
	hpte1.SetSeconds( None )
	#hpte1.SetValue( '' )
	
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

	
