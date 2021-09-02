import wx
import sys
import Model
from keybutton import KeyButton

# key codes recognized as Enter.
enterCodes = {
	wx.WXK_RETURN,
	wx.WXK_SPACE,
	wx.WXK_TAB,
	wx.WXK_NUMPAD_ENTER,
	wx.WXK_NUMPAD_SPACE,
	wx.WXK_NUMPAD_TAB,
	
	 9,     # \h vertical tab
	10,		# \r linefeed
	11,	    # \t horizontal tab
	12,     # \r formfeed
	13,		# \n newline
}
if sys.platform == 'darwin':
	enterCodes.add( 370 )		# Mac's numeric keypad enter code (exceeds 255, but whatever).

# backspace, delete, comma, digits
validKeyCodes = set( [8, 127, 44] + list(range(48, 48+10)) )

# Codes to clear the entry.
clearCodes = { 0x2327, 27, ord('c'), ord('C') }

# Codes to do actions.
# / - DNF
# * - DNS
# - - PUL
# + - DQ
actionCodes = { ord('/'), ord('*'), ord('-'), ord('+') }

def getRiderNumsFromText( txt ):
	nums = []
	mask = Model.race.getCategoryMask() if Model.race else None
	for num in txt.split( ',' ):
		if not num:
			continue
		if mask:	# Add common prefix numbers to the entry.
			s = num
			dLen = len(mask) - len(s)
			if dLen > 0:
				sAdjust = mask[:dLen] + s
				sAdjust = sAdjust.replace( '.', '0' )
				num = sAdjust
		nums.append( int(num) )
	return nums

def MakeKeypadButton( parent, id=wx.ID_ANY, label='', style = 0, size=(-1,-1), font = None ):
	label = label.replace('&','')
	btn = KeyButton( parent, label=label, style=style|wx.NO_BORDER, size=size )
	if font:
		btn.SetFont( font )
	return btn



