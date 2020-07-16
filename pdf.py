import fpdf

def normalize_text( text ):
	''' Make sure we only have characters supported by the font. '''
	return u'{}'.format(text).encode('latin-1', 'replace').decode('latin-1')

class PDF( fpdf.FPDF ):
	def __init__( self, orientation='L', format='Letter' ):
		super().__init__( orientation=orientation, unit='pt', format=format )
	
	def scale_text_in_rectangle( self, x, y, width, height, text ):
		'''
			Make the text fit by stretching the font vertically or horizontally as necessary.
		'''
		text = normalize_text( text )
		asc_correct = 1.5 if self.font_family.endswith('-e') else 1.45
		
		t_height = 72.0*5.0
		font_height = t_height * asc_correct
		self.set_font_size( font_height )
		t_width = self.get_string_width( text )
		
		sy = float(height) / t_height
		sx = sy
		t_width_new = t_width * sx
		if t_width_new > width:
			sx = float(width) / t_width
			t_width_new = t_width * sx
		x_left = (width-t_width_new)/2.0
		
		o = self._out
		o( 'q' )
		o( '1 0 0 1 {tx} {ty} cm'.format(tx=x+x_left, ty=self.h-(y+height)) )
		o( '{sx} 0 0 {sy} 0 0 cm'.format(sx=sx, sy=sy) )
		p_save = (self.h, self.k)
		self.h, self.k = 0, 1.0
		self.text( 0, 0, text )
		self.h, self.k = p_save
		o( 'Q' )
	
	def fit_text_in_rectangle( self, x, y, width, height, text, align = 'M' ):
		'''
			Make the font bigger/smaller to make it fit but to not stretch it.
		'''
		text = normalize_text( text )
		
		lineFactor = 1.15
		fs = height
		self.set_font_size( fs )
		t_height = fs
		t_width = self.get_string_width( text )
		if t_width > width:
			fs *= width / float(t_width)
			self.set_font_size( fs )
			t_width = self.get_string_width( text )
		
		if align == 'M':
			x += (width - t_width) / 2.0
		elif align == 'L':
			pass
		else:
			x += width - t_width
			
		y += height - (height - fs) / 2.0 - fs*0.13
		self.text( x, y, text )
	
	def table_in_rectangle( self,
			x, y, width, height, table,
			leftJustifyCols=None, hasHeader=True, horizontalLines=True, verticalLines=False ):
		if not table:
			return
		leftJustifyCols = set( leftJustifyCols or [] )
		
		table = [[normalize_text(v) for v in row] for row in table]
		colMax = max( len(row) for row in table )
		for row in table:
			if len(row) < colMax:
				row.extend( [u''] * (colMax - len(row)) )
				
		lineFactor = 1.15
		fs, fsMin, fsMax = 0.0, 0.0, 144.0
		
		cellSpace = '  '
		
		def maxColWidths():
			cellPad = self.get_string_width( cellSpace )
			widths = [max(self.get_string_width(row[col]) for row in table) + cellPad for col in range(colMax) ]
			return widths
		
		def widthHeight( fs ):
			self.set_font_size( fs )
			return sum(maxColWidths()), len(table) * fs * lineFactor
			
		while fsMax - fsMin > 0.01:
			fs = (fsMin + fsMax) / 2.0
			widthMax, heightMax = widthHeight( fs )
			if widthMax > width or heightMax > height:
				fsMax = fs
			else:
				fsMin = fs
		
		fs = fsMin
		widthMax, heightMax = widthHeight( fs )
		lineHeight = fs * lineFactor
		
		cellPad = self.get_string_width( cellSpace ) / 2.0
		widths = maxColWidths()
		
		if verticalLines:
			xCur = x
			self.line( xCur, y, xCur, y+heightMax )
			for w in widths:
				xCur += w
				self.line( xCur, y, xCur, y+heightMax )
		
		if horizontalLines:
			yCur = y + lineHeight * 0.08
			if not hasHeader:
				self.line( x, yCur, x+widthMax, yCur )
			for row in table:
				yCur += lineHeight
				self.line( x, yCur, x+widthMax, yCur )

		yCur = y + fs
		for r, row in enumerate(table):
			if r == 0 and hasHeader:
				self.set_font( '', 'B' )
			xCur = x
			for c, v in enumerate(row):
				if c in leftJustifyCols or (r == 0 and hasHeader):
					self.text( xCur + cellPad, yCur, v )
				else:
					self.text( xCur + widths[c] - cellPad - self.get_string_width(v), yCur, v )
				xCur += widths[c]
			if r == 0 and hasHeader:
				self.set_font( '', '' )
			yCur += lineHeight
		
		self.yRow = [y + lineHeight * 0.08]
		for i in range(len(table)+1):
			self.yRow.append( self.yRow[-1] + lineHeight )
		
		self.xCol = [x+cellPad]
		for w in widths:
			self.xCol.append( self.xCol[-1] + w )
		return widthMax, heightMax
	
	def to_bytes( self ):
		return self.output( dest='S' ).encode('latin-1', 'replace')
