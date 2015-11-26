import fpdf

class PDF( fpdf.FPDF ):
	def __init__( self, orientation='L', format='Letter' ):
		super( PDF, self ).__init__( orientation=orientation, unit='pt', format=format )
	
	def table_in_rectangle( self,
			x, y, width, height, table,
			leftJustifyCols=None, hasHeader=True, horizontalLines=True, verticalLines=False ):
		if not table:
			return
		leftJustifyCols = set( leftJustifyCols or [] )
		
		# Encode the entire table as windows-1252.
		table = [[unicode(v).encode('windows-1252', 'ignore') for v in row] for row in table]
		colMax = max( len(row) for row in table )
		for row in table:
			if len(row) < colMax:
				row.extend( [''] * (colMax - len(row)) )
				
		lineFactor = 1.15
		fs, fsMin, fsMax = 0.0, 0.0, 144.0
		
		cellSpace = '  '
		
		def maxColWidths():
			cellPad = self.get_string_width( cellSpace )
			widths = [max(self.get_string_width(row[col]) for row in table) + cellPad for col in xrange(colMax) ]
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
		for i in xrange(len(table)+1):
			self.yRow.append( self.yRow[-1] + lineHeight )
		
		self.xCol = [x+cellPad]
		for w in widths:
			self.xCol.append( self.xCol[-1] + w )
		return widthMax, heightMax
