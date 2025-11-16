import wx
import sys
import string
import Model
from keybutton import KeyButton
from ReadSignInSheet import GetTagNums

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

# backspace, delete, comma + valid characters
validKeyCodes = set( [8, 127, 44] + list(ord(c) for c in string.digits) )
validKeyCodesRFID = set( list(validKeyCodes) + list(ord(c) for c in string.ascii_letters) )

# Codes to clear the entry.
clearCodes = { 0x2327, 27, ord('c'), ord('C') }

# Codes to do actions.
# / - DNF
# * - DNS
# - - PUL
# + - DQ
actionCodes = { ord('/'), ord('*'), ord('-'), ord('+') }

def getRiderNumsFromText( txt ):
	race = Model.race
	if race:
		mask = race.getCategoryMask()
		allowManualRFID = race.allowManualRFID
		tagNums = GetTagNums() if allowManualRFID else None
	else:
		mask = None
		allowManualRFID = False
		tagNums = None
	
	nums = []
	for num in txt.split(','):
		if not num:
			continue

		applyMask = True
		if allowManualRFID:
			# If allowManualRFID is True, try to find the entry in the tagNums dict.
			# If the entry is found, use the corresponding bib.
			num = num.upper()
			found = tagNums.get( num, None )
			if found is not None:
				num = found
				applyMask = False	# Don't apply the mask if we match the tag.
			elif not num.isdigit():
				# Register a missing tag.
				# We can only detect this if the tag contains a non-digit character.
				# If all-digits, the entry is assumed to be a bib number.
				race.missingTags.add( num )
				continue
		
		if mask and applyMask:	# Add common prefix numbers to the entry.
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



