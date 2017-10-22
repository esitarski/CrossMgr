import wx
import math
import Utils

if 'WXMAC' not in wx.Platform:
	import wx.lib.masked  as  masked
	class HighPrecisionTimeEdit( masked.TextCtrl ):
		mask         = u'##:##:##.###'
		defaultValue = u'00:00:00.000'
		emptyValue   = u'  :  :  .   '

		def __init__( self, parent, id=wx.ID_ANY, seconds=None, allow_none=False, style=0, size=wx.DefaultSize ):
			self.allow_none = allow_none
			super( HighPrecisionTimeEdit, self ).__init__(
				parent, id,
				mask		 = self.mask,
				defaultValue = self.defaultValue,
				validRegex   = u'[0-9][0-9]:[0-5][0-9]:[0-5][0-9]\.[0-9][0-9][0-9]',
				useFixedWidthFont = False,
				style		 = style,
				size         = size,
			)
			if seconds is not None:
				self.SetSeconds( seconds )
		
		def GetSeconds( self ):
			v = self.GetValue()
			if self.allow_none and v == self.emptyValue:
				return None
			else:
				return Utils.StrToSeconds(v)
			
		def SetSeconds( self, secs ):
			if secs is None and self.allow_none:
				v = self.emptyValue
			else:
				v = Utils.formatTime(
						secs,
						highPrecision=True,		extraPrecision=True,
						forceHours=True, 		twoDigitHours=True,
					)
				)
			super( HighPrecisionTimeEdit, self ).SetValue( v )

else:
	import re
	class HighPrecisionTimeEdit( wx.TextCtrl ):
		defaultValue = u'00:00:00.000'
		emptyValue   = u''
		reNonTimeChars = re.compile(u'[^0-9:.]')

		def __init__( self, parent, id=wx.ID_ANY, seconds=None, allow_none=False, style=0, size=wx.DefaultSize ):
			self.allow_none = allow_none
			super( HighPrecisionTimeEdit, self ).__init__(
				parent, id,
				value		= self.defaultValue,
				style		= style,
				size        = size,
			)
			if seconds is not None:
				self.SetSeconds( seconds )
		
		def GetSeconds( self ):
			v = self.GetValue()
			if self.allow_none and v == self.emptyValue:
				return None
			else:
				return Utils.StrToSeconds(self.reNonTimeChars.sub('',v))
			
		def SetSeconds( self, secs ):
			if secs is None and self.allow_none:
				v = self.emptyValue
			else:
				v = Utils.formatTime(
						secs,
						highPrecision=True,		extraPrecision=True,
						forceHours=True, 		twoDigitHours=True,
					)
				)
			super( HighPrecisionTimeEdit, self ).SetValue( v )
