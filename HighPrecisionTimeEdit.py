
import wx
import wx.lib.masked             as  masked
import math
import Utils

class HighPrecisionTimeEdit( masked.TextCtrl ):
	mask         = u'##:##:##.###'
	defaultValue = u'00:00:00.000'
	emptyValue   = u'  :  :  .   '

	def __init__( self, parent, id=wx.ID_ANY, seconds=None, allow_none=False, style=0, size=wx.DefaultSize ):
		self.allow_none = allow_none
		masked.TextCtrl.__init__(
					self, parent, id,
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
			masked.TextCtrl.SetValue( self, self.emptyValue )
		else:
			masked.TextCtrl.SetValue( self, Utils.formatTime(
					secs,
					highPrecision=True,		extraPrecision=True,
					forceHours=True, 		twoDigitHours=True,
				)
			)

