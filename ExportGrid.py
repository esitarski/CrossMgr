
import wx
import os
import xlwt
import Utils
import Model
import Results
from ReadSignOnSheet import Fields, IgnoreFields

#---------------------------------------------------------------------------

# Sort sequence by rider status.
statusSortSeq = Model.Rider.statusSortSeq

class ExportGrid( object ):
	def __init__( self, title = '', colnames = [], data = [] ):
		self.title = title
		self.colnames = colnames
		self.data = data
		self.leftJustifyCols = set()
		self.infoColumns = set()
		self.iLapTimes = 0
	
	def _getFont( self, pixelSize = 28, bold = False ):
		return wx.FontFromPixelSize( (0,pixelSize), wx.FONTFAMILY_SWISS, wx.NORMAL,
									 wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL, False, 'Ariel' )
	
	def _getColSizeTuple( self, dc, font, col ):
		wSpace, hSpace, lh = dc.GetMultiLineTextExtent( '    ', font )
		extents = [ dc.GetMultiLineTextExtent(self.colnames[col], font) ]
		extents.extend( dc.GetMultiLineTextExtent(str(v), font) for v in self.data[col] )
		return max( e[0] for e in extents ), sum( e[1] for e in extents ) + hSpace/4
	
	def _getDataSizeTuple( self, dc, font ):
		wSpace, hSpace, lh = dc.GetMultiLineTextExtent( '    ', font )
		
		wMax, hMax = 0, 0
		
		# Sum the width of each column.
		for col, c in enumerate(self.colnames):
			w, h = self._getColSizeTuple( dc, font, col )
			wMax += w + wSpace
			hMax = max( hMax, h )
			
		if wMax > 0:
			wMax -= wSpace
		
		return wMax, hMax
	
	def _drawMultiLineText( self, dc, text, x, y ):
		if not text:
			return
		wText, hText, lineHeightText = dc.GetMultiLineTextExtent( text, dc.GetFont() )
		for line in text.split( '\n' ):
			dc.DrawText( line, x, y )
			y += lineHeightText

	def _getFontToFit( self, widthToFit, heightToFit, sizeFunc, isBold = False ):
		left = 1
		right = max(widthToFit, heightToFit)
		
		while right - left > 1:
			mid = (left + right) / 2.0
			font = self._getFont( mid, isBold )
			widthText, heightText = sizeFunc( font )
			if widthText <= widthToFit and heightText <= heightToFit:
				left = mid
			else:
				right = mid - 1
		
		return self._getFont( left, isBold )
			
	def drawToFitDC( self, dc ):
		# Get the dimentions of what we are printing on.
		(widthPix, heightPix) = dc.GetSizeTuple()
		
		# Get a reasonable border.
		borderPix = max(widthPix, heightPix) / 20
		
		widthFieldPix = widthPix - borderPix * 2
		heightFieldPix = heightPix - borderPix * 2
		
		xPix = borderPix
		yPix = borderPix
		
		# Draw the graphic.
		graphicFName = None;
		if Utils.getMainWin():
			graphicFName = Utils.getMainWin().getGraphicFName()
			extension = os.path.splitext( graphicFName )[1].lower()
			bitmapType = {
				'.gif': wx.BITMAP_TYPE_GIF,
				'.png': wx.BITMAP_TYPE_PNG,
				'.jpg': wx.BITMAP_TYPE_JPEG,
				'.jpeg':wx.BITMAP_TYPE_JPEG }.get( extension, wx.BITMAP_TYPE_PNG )
			bitmap = wx.Bitmap( graphicFName, bitmapType )
		else:
			bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'CrossMgrHeader.png'), wx.BITMAP_TYPE_PNG )
		bmWidth, bmHeight = bitmap.GetWidth(), bitmap.GetHeight()
		graphicHeight = heightPix * 0.15
		graphicWidth = float(bmWidth) / float(bmHeight) * graphicHeight
		graphicBorder = int(graphicWidth * 0.15)

		gc = wx.GraphicsContext.Create(dc)
		gc.DrawBitmap( bitmap, xPix, yPix, graphicWidth, graphicHeight )
		
		# Draw the title.
		font = self._getFontToFit( widthFieldPix - graphicWidth - graphicBorder, graphicHeight,
									lambda font: dc.GetMultiLineTextExtent(self.title, font)[:-1], True )
		dc.SetFont( font )
		self._drawMultiLineText( dc, self.title, xPix + graphicWidth + graphicBorder, yPix )
		# wText, hText, lineHeightText = dc.GetMultiLineTextExtent( self.title, font )
		# yPix += hText + lineHeightText/4
		yPix += graphicHeight + graphicBorder
		
		heightFieldPix = heightPix - yPix - borderPix
		
		# Draw the table.
		font = self._getFontToFit( widthFieldPix, heightFieldPix, lambda font: self._getDataSizeTuple(dc, font) )
		dc.SetFont( font )
		wSpace, hSpace, textHeight = dc.GetMultiLineTextExtent( '    ', font )
		
		yPixTop = yPix
		for col, c in enumerate(self.colnames):
			colWidth = self._getColSizeTuple( dc, font, col )[0]
			yPix = yPixTop
			w, h, lh = dc.GetMultiLineTextExtent( c, font )
			if col in self.leftJustifyCols:
				self._drawMultiLineText( dc, str(c), xPix, yPix )					# left justify
			else:
				self._drawMultiLineText( dc, str(c), xPix + colWidth - w, yPix )	# right justify
			yPix += h + hSpace/4
			if col == 0:
				yLine = yPix - hSpace/8
				for r in xrange(max(len(cData) for cData in self.data) + 1):
					dc.DrawLine( borderPix, yLine + r * textHeight, widthPix - borderPix, yLine + r * textHeight )
					
			for v in self.data[col]:
				vStr = str(v)
				if vStr:
					w, h, lh = dc.GetMultiLineTextExtent( vStr, font )
					if col in self.leftJustifyCols:
						self._drawMultiLineText( dc, vStr, xPix, yPix )					# left justify
					else:
						self._drawMultiLineText( dc, vStr, xPix + colWidth - w, yPix )	# right justify
				yPix += textHeight
			xPix += colWidth + wSpace
		
	def toExcelSheet( self, sheet ):
		''' Write the contents of the grid to an xlwt excel sheet. '''
		titleStyle = xlwt.XFStyle()
		titleStyle.font.bold = True
		titleStyle.font.height += titleStyle.font.height / 2

		rowTop = 0
		for line in self.title.split('\n'):
			sheet.write(rowTop, 0, line, titleStyle)
			rowTop += 1
			
		rowTop += 1
		
		# Write the colnames and data.
		for col, c in enumerate(self.colnames):
			headerStyle = xlwt.XFStyle()
			headerStyle.borders.bottom = xlwt.Borders.MEDIUM
			headerStyle.font.bold = True
			headerStyle.alignment.horz = xlwt.Alignment.HORZ_LEFT if col in self.leftJustifyCols \
																	else xlwt.Alignment.HORZ_RIGHT
			headerStyle.alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
			
			style = xlwt.XFStyle()
			style.alignment.horz = xlwt.Alignment.HORZ_LEFT if col in self.leftJustifyCols \
																	else xlwt.Alignment.HORZ_RIGHT
			
			sheet.write( rowTop, col, c, headerStyle )
			for row, v in enumerate(self.data[col]):
				sheet.write( rowTop + 1 + row, col, v, style )
	
	def _setRC( self, row, col, value ):
		if self.data:
			maxRow = max( len(c) for c in self.data )
		else:
			maxRow = 0
		while col >= len(self.data):
			self.data.append( [''] * maxRow )
		if row >= maxRow:
			growSize = row + 1 - maxRow
			for c in self.data:
				c.extend( [''] * growSize )
		
		self.data[col][row] = value
	
	def setResultsOneListRiderTimes( self, catName = 'All', getExternalData = True ):
		self.setResultsOneList( catName, getExternalData )

	def setResultsOneList( self, catName = 'All', getExternalData = True ):
		''' Format the results into columns. '''
		self.data = []
		self.colnames = []

		results = Results.GetResults( catName, getExternalData )
		if not results:
			return
		
		with Model.LockRace() as race:
			self.title = '\n'.join( [race.name, Utils.formatDate(race.date), 'Category: ' + catName] )
			category = race.categories.get( catName, None )

		startOffset = category.getStartOffsetSecs() if category else 0.0
		
		leader = results[0]
		infoFields = ['LastName', 'FirstName', 'Team', 'Category', 'License']
		infoFieldsPresent = set( infoFields ) & set( dir(leader) )
		infoFields = [f for f in infoFields if f in infoFieldsPresent]
		
		self.colnames = ['Pos', 'Bib'] + infoFields + ['Time', 'Gap']
		self.colnames = [name[:-4] + ' Name' if name.endswith('Name') else name for name in self.colnames]
		self.iLapTimes = len(self.colnames)
		if leader.lapTimes:
			self.colnames.extend( ['Lap %d' % lap for lap in xrange(1, len(leader.lapTimes)+1)] )
			
		data = [ [] for i in xrange(len(self.colnames)) ]
		for col, f in enumerate(['pos', 'num'] + infoFields + ['lastTime', 'gap']):
			for row, r in enumerate(results):
				if f == 'lastTime':
					lastTime = getattr( r, f, 0.0 )
					if lastTime <= 0.0:
						data[col].append( '' )
					else:
						lastTime = max( 0.0, lastTime - startOffset )
						data[col].append( Utils.formatTimeCompressed(lastTime) )
				else:
					data[col].append( getattr(r, f, '') )
		
		lapsMax = len(leader.lapTimes)
		for row, r in enumerate(results):
			for i, t in enumerate(r.lapTimes):
				data[self.iLapTimes+i].append( Utils.formatTimeCompressed(t) )
			for i in xrange(len(r.lapTimes), lapsMax):
				data[self.iLapTimes+i].append( '' )
		
		self.data = data
		self.infoColumns     = set( xrange(2, 2+len(infoFields)) ) if infoFields else set()
		self.leftJustifyCols = set( xrange(2, 2+len(infoFields)) ) if infoFields else set()
		
			
if __name__ == '__main__':
	pass
