import six
import fpdf

class PDF( fpdf.FPDF ):
	def __init__( self, orientation='L', format='Letter' ):
		super( PDF, self ).__init__( orientation=orientation, unit='pt', format=format )
	
	def center_in_rectangle( self, x, y, width, height, text ):
		self.rect( x, y, width, height )
		
		xCenter = x + width / 2.0
		yCenter = y + height / 2.0
		width *= 1.1
		height *= 1.25
		
		# Encode the text as windows-1252.
		text = six.text_type(text).encode('windows-1252', 'ignore')
		fs, fsMin, fsMax = 0.0, 0.0, 720.0
		
		def widthHeight( fs ):
			self.set_font_size( fs )
			return self.get_string_width(text), fs
			
		while fsMax - fsMin > 0.01:
			fs = (fsMin + fsMax) / 2.0
			widthMax, heightMax = widthHeight( fs )
			if widthMax > width or heightMax > height:
				fsMax = fs
			else:
				fsMin = fs
		
		fs = fsMin
		widthMax, heightMax = widthHeight( fs )
		
		xCur = xCenter - widthMax / 2.0
		yCur = yCenter + fs*1.2 / 2.0
		#self.text( xCur, yCur, text )
		self.set_xy( xCur, yCenter - heightMax / 2.0 )
		self.cell( widthMax, heightMax, text, align='C' )
		
		self.set_draw_color(0, 0, 0)
		self.set_line_width(1)
		
		yCur = yCenter - heightMax / 2.0
		self.rect( xCur, yCur, widthMax, heightMax )
		
		return widthMax, heightMax
	
	def table_in_rectangle( self,
			x, y, width, height, table,
			leftJustifyCols=None, hasHeader=True, horizontalLines=True, verticalLines=False ):
		if not table:
			return
		leftJustifyCols = set( leftJustifyCols or [] )
		
		# Encode the entire table as windows-1252.
		table = [[six.text_type(v).encode('windows-1252', 'ignore') for v in row] for row in table]
		colMax = max( len(row) for row in table )
		for row in table:
			if len(row) < colMax:
				row.extend( [''] * (colMax - len(row)) )
				
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
		for i in six.moves.range(len(table)+1):
			self.yRow.append( self.yRow[-1] + lineHeight )
		
		self.xCol = [x+cellPad]
		for w in widths:
			self.xCol.append( self.xCol[-1] + w )
		return widthMax, heightMax
	
	def to_bytes( self ):
		return self.output( dest='S' ).encode('latin-1', 'ignore') if six.PY3 else self.output( dest='S' )
