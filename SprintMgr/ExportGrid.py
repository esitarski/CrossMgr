import wx
import os
import Utils
import Model
import math
from html import escape
import base64
from FitSheetWrapper import FitSheetWrapperXLSX
from contextlib import contextmanager

#---------------------------------------------------------------------------

@contextmanager
def tag( buf, name, attrs = {} ):
	if isinstance(attrs, str) and attrs:
		attrs = { 'class': attrs }
	buf.write( '<{}>'.format( u' '.join(
			[name] + ['{}="{}"'.format(attr, value) for attr, value in attrs.items()]
		) ) )
	yield
	buf.write( '</{}>\n'.format(name) )

brandText = 'Powered by SprintMgr (sites.google.com/site/crossmgrsoftware)'

def getHeaderFName():
	''' Get the header bitmap if specified and exists, or use a default.  '''
	try:
		graphicFName = Utils.getMainWin().getGraphicFName()
		with open(graphicFName, 'rb') as f:
			pass
		return graphicFName
	except Exception:
		return os.path.join(Utils.getImageFolder(), 'SprintMgr.png')

def getHeaderBitmap():
	''' Get the header bitmap if specified, or use a default.  '''
	if Utils.getMainWin():
		graphicFName = Utils.getMainWin().getGraphicFName()
		extension = os.path.splitext( graphicFName )[1].lower()
		bitmapType = {
			'.gif': wx.BITMAP_TYPE_GIF,
			'.png': wx.BITMAP_TYPE_PNG,
			'.jpg': wx.BITMAP_TYPE_JPEG,
			'.jpeg':wx.BITMAP_TYPE_JPEG }.get( extension, wx.BITMAP_TYPE_ANY )
		try:
			return wx.Bitmap( graphicFName, bitmapType )
		except Exception as e:
			pass
	
	return wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SprintMgr.png'), wx.BITMAP_TYPE_PNG )

def writeHtmlHeader( buf, title ):
	buf.write( '<style>\n' )
	buf.write( 'td { vertical-align: top; }\n')
	buf.write( 'th { vertical-align: top; }\n')
	buf.write( '</style>\n')
	with tag(buf, 'table', {'class': 'TitleTable'} ):
		with tag(buf, 'tr'):
			with tag(buf, 'td', dict(valign='top')):
				data = base64.b64encode(open(getHeaderFName(),'rb').read())
				buf.write( '<img id="idImgHeader" src="data:image/png;base64,%s" />' % data )
			with tag(buf, 'td'):
				buf.write( '&nbsp;&nbsp;&nbsp;&nbsp;' )
			with tag(buf, 'td'):
				with tag(buf, 'span', {'id': 'idRaceName'}):
					buf.write( escape(title).replace('\n', '<br/>\n') )
				if Model.model.organizer:
					with tag(buf, 'br'):
						pass
					with tag(buf, 'span', {'id': 'idOrganizer'}):
						buf.write( 'by ' )
						buf.write( escape(Model.model.organizer) )

class ExportGrid:
	PDFLineFactor = 1.10

	def __init__( self, title, grid ):
		self.title = title
		self.grid = grid
		self.colnames = [grid.GetColLabelValue(c) for c in range(grid.GetNumberCols())]
		self.data = [ [grid.GetCellValue(r, c) for r in range(grid.GetNumberRows())] for c in range(len(self.colnames)) ]
		
		# Trim all empty rows.
		self.numRows = 0
		for col in self.data:
			for iRow, v in enumerate(col):
				if v.strip() and iRow >= self.numRows:
					self.numRows = iRow + 1
		
		for col in self.data:
			del col[self.numRows:]
		
		self.fontName = 'Helvetica'
		self.fontSize = 16
		
		self.leftJustifyCols = {}
		self.rightJustifyCols = {}
		
		rightJustify = {'Pos', 'Bib', 'Time'}
		for c, n in enumerate(self.colnames):
			if n in rightJustify:
				self.rightJustifyCols[c] = True
			else:
				self.leftJustifyCols[c] = True
	
	def _getFont( self, pixelSize = 28, bold = False ):
		return wx.Font( (0,pixelSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL,
									 wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL )
	
	def _getColSizeTuple( self, dc, font, col ):
		dc.SetFont( font )
		wSpace, hSpace = dc.GetTextExtent( '    ' )
		extents = [ dc.GetMultiLineTextExtent(self.colnames[col]) ]
		extents.extend( dc.GetMultiLineTextExtent('{}'.format(v)) for v in self.data[col] )
		return max( e[0] for e in extents ), sum( e[1] for e in extents ) + hSpace/4
	
	def _getDataSizeTuple( self, dc, font ):
		dc.SetFont( font )
		wSpace, hSpace = dc.GetTextExtent( '    ' )
		
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
		wText, hText = dc.GetMultiLineTextExtent( text )
		lineHeightText = dc.GetTextExtent( 'PpJj' )[1]
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
		(widthPix, heightPix) = dc.GetSize()
		
		# Get a reasonable border.
		borderPix = max(widthPix, heightPix) / 20
		
		widthFieldPix = widthPix - borderPix * 2
		heightFieldPix = heightPix - borderPix * 2
		
		xPix = borderPix
		yPix = borderPix
		
		graphicWidth = 0
		graphicHeight = heightPix * 0.15
		graphicBorder = 0
		qrWidth = 0
		
		# Draw the graphic.
		bitmap = getHeaderBitmap()
		bmWidth, bmHeight = bitmap.GetWidth(), bitmap.GetHeight()
		graphicHeight = int(heightPix * 0.12)
		graphicWidth = int(float(bmWidth) / float(bmHeight) * graphicHeight)
		graphicBorder = int(graphicWidth * 0.15)

		# Rescale the graphic to the correct size.
		# We cannot use a GraphicContext because it does not support a PrintDC.
		image = bitmap.ConvertToImage()
		image.Rescale( graphicWidth, graphicHeight, wx.IMAGE_QUALITY_HIGH )
		if dc.GetDepth() == 8:
			image = image.ConvertToGreyscale()
		bitmap = image.ConvertToBitmap( dc.GetDepth() )
		dc.DrawBitmap( bitmap, xPix, yPix )
		image, bitmap = None, None
		
		# Draw the title.
		def getTitleSize( font ):
			dc.SetFont( font )
			return dc.GetMultiLineTextExtent( self.title )
		font = self._getFontToFit( widthFieldPix - graphicWidth - graphicBorder - qrWidth, graphicHeight, getTitleSize, True )
		dc.SetFont( font )
		self._drawMultiLineText( dc, self.title, xPix + graphicWidth + graphicBorder, yPix )
		yPix += graphicHeight + graphicBorder
		
		heightFieldPix = heightPix - yPix - borderPix
		
		# Draw the table.
		font = self._getFontToFit( widthFieldPix, heightFieldPix, lambda font: self._getDataSizeTuple(dc, font) )
		dc.SetFont( font )
		wSpace, hSpace = dc.GetTextExtent( '    ' )
		
		# Get the max height per row.
		rowHeight = [0] * (self.numRows + 1)
		for r in range(self.numRows):
			rowHeight[r] = max( dc.GetMultiLineTextExtent(self.grid.GetCellValue(r, c))[1] for c in range(len(self.colnames)))
		
		yPixTop = yPix
		yPixMax = yPix
		for col, c in enumerate(self.colnames):
			colWidth = self._getColSizeTuple( dc, font, col )[0]
			yPix = yPixTop
			w, h = dc.GetMultiLineTextExtent( c )
			if col in self.leftJustifyCols:
				self._drawMultiLineText( dc,' {}'.format(c), xPix, yPix )					# left justify
			else:
				self._drawMultiLineText( dc,' {}'.format(c), xPix + colWidth - w, yPix )	# right justify
			yPix += h + hSpace/4
			if col == 0:
				yLine = yPix - hSpace/8
				dc.DrawLine( borderPix, yLine, widthPix - borderPix, yLine )
				for r in rowHeight:
					yLine += r
					dc.DrawLine( borderPix, yLine, widthPix - borderPix, yLine )
					
			for r, v in enumerate(self.data[col]):
				vStr = ' {}'.format(v)
				if vStr:
					w, h = dc.GetMultiLineTextExtent( vStr )
					if col in self.leftJustifyCols:
						self._drawMultiLineText( dc, vStr, xPix, yPix )					# left justify
					else:
						self._drawMultiLineText( dc, vStr, xPix + colWidth - w, yPix )	# right justify
				yPix += rowHeight[r]
			yPixMax = max(yPixMax, yPix)
			xPix += colWidth + wSpace
				
		# Put CrossMgr branding at the bottom of the page.
		font = self._getFont( borderPix // 5, False )
		dc.SetFont( font )
		w, h = dc.GetMultiLineTextExtent( brandText )
		self._drawMultiLineText( dc, brandText, borderPix, heightPix - borderPix + h )
	
	@staticmethod
	def getExcelFormatsXLSX( workbook ):
		titleStyle = workbook.add_format({
			'bold': True,
			'font_size': 17,
		})

		headerStyleLeft = workbook.add_format({
			'bottom':	2,
			'bold':		True,
			'text_wrap':True,
		})
		
		headerStyleRight = workbook.add_format({
			'bottom':	2,
			'bold':		True,
			'text_wrap':True,
			'align':	'right',
		})
		
		styleLeft = workbook.add_format()
		
		styleRight = workbook.add_format({
			'align':	'right',
		})
		
		return {
			'titleStyle':		titleStyle,
			'headerStyleLeft':	headerStyleLeft,
			'headerStyleRight':	headerStyleRight,
			'styleLeft':		styleLeft,
			'styleRight':		styleRight,
		}
	
	def toExcelSheet( self, sheet, formats ):

		''' Write the contents of the grid to an excel sheet. '''
		titleStyle			= formats['titleStyle']
		headerStyleLeft		= formats['headerStyleLeft']
		headerStyleRight	= formats['headerStyleRight']
		styleLeft			= formats['styleLeft']
		styleRight			= formats['styleRight']
		
		rowTop = 0
		if self.title:
			for line in self.title.split('\n'):
				sheet.write(rowTop, 0, line, titleStyle)
				rowTop += 1
			rowTop += 1
		
		sheetFit = FitSheetWrapperXLSX( sheet )
		
		# Write the colnames and data.
		rowMax = 0
		for col, c in enumerate(self.colnames):
			sheetFit.write( rowTop, col, c, headerStyleLeft if col in self.leftJustifyCols else headerStyleRight, bold=True )
			style = styleLeft if col in self.leftJustifyCols else styleRight
			for row, v in enumerate(self.data[col]):
				rowCur = rowTop + 1 + row
				if rowCur > rowMax:
					rowMax = rowCur
				sheetFit.write( rowCur, col, v, style )
				
		# Add branding at the bottom of the sheet.
		sheet.write( rowMax + 2, 0, brandText, styleLeft )
		
	def toHtml( self, buf ):
		''' Write the contents to the buffer in HTML format. '''
		writeHtmlHeader( buf, self.title )
		
		with tag(buf, 'table', {'class': 'results'} ):
			with tag(buf, 'thead'):
				with tag(buf, 'tr'):
					for col in self.colnames:
						with tag(buf, 'th'):
							buf.write( escape(col).replace('\n', '<br/>\n') )
			with tag(buf, 'tbody'):
				for row in range(max(len(d) for d in self.data)):
					with tag(buf, 'tr'):
						for col in range(len(self.colnames)):
							with tag(buf, 'td', {'class':'rAlign'} if col not in self.leftJustifyCols else {}):
								try:
									buf.write( escape(self.data[col][row]).replace('\n', '<br/>\n') )
								except IndexError:
									buf.write( '&nbsp;' )
									
		with tag(buf, 'p', {'class': 'smallfont'}):
			buf.write( 'Powered by ' )
			with tag(buf, 'a', dict(href="http://www.sites.google.com/site/crossmgrsoftware")):
				buf.write( 'SprintMgr' )
		return buf
