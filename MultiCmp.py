
def MultiCmp( attributes ):
	attrSense = [ (a[1:], -1) if a[0] == '-' else (a, 1) for a in attributes ]
	def _multiCmp( x, y ):
		for a in attrSense:
			c = cmp( getattr(x, a[0]), getattr(y, a[0]) )
			if c:
				return c * a[1]
		return 0
	return _multiCmp