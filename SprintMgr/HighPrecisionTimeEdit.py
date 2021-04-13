import wx
import math
import re
import Utils

validChars = set( c for c in '0123456789:-. ' )
reRepeatingDecimals = re.compile( r'\.+' )
reNonTimeChars = re.compile( r'[^-0123456789:. ]*' )
class TimeCharValidator(wx.Validator):
	def __init__(self):
		super().__init__()
		self.Bind(wx.EVT_CHAR, self.OnChar)

	def Clone(self):
		return TimeCharValidator()

	def Validate(self, win):
		return True

	def TransferToWindow(self):
		return True

	def TransferFromWindow(self):
		return True

	def OnChar(self, event):
		key = event.GetKeyCode()
		if (	key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255 or
				chr(key) in validChars ):
			event.Skip()
			return

class HighPrecisionTimeEdit( wx.TextCtrl ):
	def __init__( self, parent, id=wx.ID_ANY, seconds=None, allow_none=False, style=0 ):
		super().__init__(
			parent, id,
			style=style | wx.TE_RIGHT,
			validator=TimeCharValidator()
		)	
		self.allow_none = allow_none
		if seconds is not None:
			self.SetSeconds( seconds )

	def GetSeconds( self ):
		v = super().GetValue().strip().replace(' ',':').replace('-',':')
		v = reNonTimeChars.sub( '', v )
		v = reRepeatingDecimals.sub( '.',  v )
		if self.allow_none and not v:
			return None
		else:
			return Utils.StrToSeconds(v)
		
	def SetSeconds( self, secs ):
		if secs is None and self.allow_none:
			super().SetValue( '' )
		else:
			super().SetValue( Utils.SecondsToStr(secs or 0) )
			
	def GetValue( self ):
		self.SetSeconds( self.GetSeconds() )
		return super().GetValue()
		
	def SetValue( self, v ):
		super().SetValue( v )
		self.SetSeconds( self.GetSeconds() )
