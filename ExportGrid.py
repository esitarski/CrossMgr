import wx
import os
import re
import xlwt
import xlsxwriter
import uuid
import datetime
import Utils
import Model
import math
from GetResults import GetResults, GetCategoryDetails
from ReadSignOnSheet import ReportFields
from FitSheetWrapper import FitSheetWrapper, FitSheetWrapperXLSX
import qrcode
from urllib.parse import quote
import Flags
import ImageIO

# from reportlab.lib.pagesizes import letter, A4

#---------------------------------------------------------------------------

# Sort sequence by rider status.
statusSortSeq = Model.Rider.statusSortSeq

brandText = _('Powered by CrossMgr (sites.google.com/site/crossmgrsoftware)')
def getBrandText():
	return '{}      {}'.format( brandText, datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') )

'''
def ImageToPil( image ):
	"""Convert wx.Image to PIL Image."""
	w, h = image.GetSize()
	data = image.GetData()

	redImage = Image.new("L", (w, h))
	redImage.fromstring(data[0::3])
	greenImage = Image.new("L", (w, h))
	greenImage.fromstring(data[1::3])
	blueImage = Image.new("L", (w, h))
	blueImage.fromstring(data[2::3])

	if image.HasAlpha():
		alphaImage = Image.new("L", (w, h))
		alphaImage.fromstring(image.GetAlphaData())
		pil = Image.merge('RGBA', (redImage, greenImage, blueImage, alphaImage))
	else:
		pil = Image.merge('RGB', (redImage, greenImage, blueImage))
	return pil
'''

def getHeaderBitmap():
	''' Get the header bitmap if specified, or use a default.  '''
	if Utils.getMainWin():
		if Model.race and Model.race.headerImage:
			try:
				bitmap = ImageIO.toBitmapFromBuf( Model.race.headerImage )
				return bitmap
			except Exception:
				pass
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
	return bitmap

def drawQRCode( url, dc, x, y, size ):
	qr = qrcode.QRCode()
	qr.add_data( 'http://' + url )
	qr.make()
	dc.SetBrush( wx.BLACK_BRUSH )
	dc.SetPen( wx.TRANSPARENT_PEN )
	squareSize = float(size) / float(qr.modules_count)
	offset = [round(squareSize*i) for i in range(qr.modules_count+1)];
	for row in range(qr.modules_count):
		for col, v in enumerate(qr.modules[row]):
			if v:
				dc.DrawRectangle( x + offset[col], y + offset[row], offset[col+1] - offset[col], offset[row+1] - offset[row] )
	dc.SetBrush( wx.NullBrush )
	dc.SetPen( wx.NullPen )

class ExportGrid:
	PDFLineFactor = 1.10

	def __init__( self, title='', colnames=None, data=None, footer='', leftJustifyCols=None, infoColumns=None ):
		self.title = title
		self.footer = footer
		self.colnames = (colnames or [])
		self.data = (data or [])
		self.leftJustifyCols = (leftJustifyCols or set())
		self.infoColumns = (infoColumns or set())
		self.setTimeCols()
		self.iLapTimes = 0
		self.rowDrawCount = 1000000
		
		self.brandText = getBrandText()
		
		self.fontName = 'Helvetica'
		self.fontSize = 16
	
	def setTimeCols( self ):
		cols = {_('time'), _('finish'), _('start'), _('clock')} 
		self.timeCols = set( c for c, name in enumerate(self.colnames) if name.lower().strip() in cols or name.startswith(_('Lap') + ' ')  )
	
	def combineFirstLastNames( self ):
		try:
			iLast = self.colnames.index(_('Last Name'))
			iFirst = self.colnames.index(_('First Name'))
		except ValueError:
			return
		
		nameCol = []
		for r in range(max(len(self.data[iLast]), len(self.data[iFirst]))):
			try:
				last = self.data[iLast][r]
			except IndexError:
				last = None
			try:
				first = self.data[iFirst][r]
			except IndexError:
				first = None
			if first and last:
				name = '{}, {}'.format( last, first )
			elif first:
				name = first
			else:
				name = last
			nameCol.append( name )
		self.data[iLast] = nameCol
		self.colnames[iLast] = _('Name')
		del self.data[iFirst]
		del self.colnames[iFirst]
		self.leftJustifyCols = set( c - 1 if c > iLast else c for c in self.leftJustifyCols if c != iFirst )
		self.infoColumns = set( c - 1 if c > iLast else c for c in self.infoColumns if c != iFirst )
		self.iLapTimes -= 1
	
	def _getFont( self, pixelSize = 28, bold = False ):
		return wx.Font( (0,max(pixelSize,1)), wx.FONTFAMILY_SWISS, wx.NORMAL,
									 wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL, False )
	
	def _getColSizeTuple( self, dc, font, col ):
		dc.SetFont( font )
		wSpace, hSpace = dc.GetMultiLineTextExtent( '    ' )
		extents = [ dc.GetMultiLineTextExtent(self.colnames[col]) ]
		extents.extend( dc.GetMultiLineTextExtent('{}'.format(v)) for v in self.data[col] )
		width = max( e[0] for e in extents )
		height = sum( e[1] for e in extents[:self.rowDrawCount] )
		return width, height + hSpace/4
	
	def _getDataSizeTuple( self, dc, font ):
		dc.SetFont( font )
		wSpace, hSpace = dc.GetMultiLineTextExtent( '    ' )
		
		wMax, hMax = 0, 0
		
		# Sum the width of each column, and record the max of each column.
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
		lineHeightText = dc.GetTextExtent( 'Py' )[1]
		for line in text.split( '\n' ):
			dc.DrawText( line, round(x), round(y) )
			y += lineHeightText

	def _getFontToFit( self, widthToFit, heightToFit, sizeFunc, isBold = False ):
		left = 1
		right = max(widthToFit, heightToFit)
		
		while right - left > 1:
			mid = (left + right) // 2
			font = self._getFont( mid, isBold )
			widthText, heightText = sizeFunc( font )
			if widthText <= widthToFit and heightText <= heightToFit:
				left = mid
			else:
				right = mid - 1
		
		return self._getFont( left, isBold )
	
	def drawToFitDC( self, dc,
						rowDrawStart = 0, rowDrawCount = 1000000,
						pageNumber = None, pageNumberTotal = None ):
		self.combineFirstLastNames()
		flagCache = {}
		
		self.rowDrawCount = rowDrawCount
			
		# Get the dimensions of what we are printing on.
		widthPix, heightPix = dc.GetSize()
		
		# Get a reasonable border.
		borderPix = int(max(widthPix, heightPix) / 20)
		
		widthFieldPix = widthPix - borderPix * 2
		heightFieldPix = heightPix - borderPix * 2
		
		xPix = yPix = borderPix
		
		# Draw the graphic.
		bitmap = getHeaderBitmap()
		bmWidth, bmHeight = bitmap.GetWidth(), bitmap.GetHeight()
		graphicHeight = int(heightPix * 0.15)
		graphicWidth = int(float(bmWidth) / float(bmHeight) * graphicHeight)
		graphicBorder = int(graphicWidth * 0.15)

		# Rescale the graphic to the correct size.
		# We cannot use a GraphicContext because it does not support a PrintDC.
		image = bitmap.ConvertToImage()
		image.Rescale( graphicWidth, graphicHeight, wx.IMAGE_QUALITY_HIGH )
		bitmap = ( image.ConvertToGreyscale() if dc.GetDepth() == 8 else image ).ConvertToBitmap()
		dc.DrawBitmap( bitmap, xPix, yPix )
		image, bitmap = None, None
		
		# Get the race URL (if defined).
		with Model.LockRace() as race:
			url = getattr( race, 'urlFull', None )
		if url and url.startswith( 'http://' ):
			url = quote( url[7:] )
			
		qrWidth = 0
		if url:
			qrWidth = graphicHeight
			drawQRCode( url, dc, widthPix - borderPix - qrWidth, borderPix, qrWidth )
			qrWidth += graphicBorder
			url = url.replace( '%20', ' ' )
		
		# Draw the title.
		def getTitleTextSize( font ):
			dc.SetFont( font )
			return dc.GetMultiLineTextExtent( self.title )
		font = self._getFontToFit( widthFieldPix - graphicWidth - graphicBorder - qrWidth, graphicHeight, getTitleTextSize, True )
		dc.SetFont( font )
		self._drawMultiLineText( dc, self.title, xPix + graphicWidth + graphicBorder, yPix )
		yPix += graphicHeight + graphicBorder
		
		heightFieldPix = heightPix - yPix - borderPix
		
		# Draw the table.
		# Add space for the flag on the NatCode.
		def padCol( iCodeCol ):
			for c, v in enumerate(self.data[iCodeCol]):
				self.data[iCodeCol][c] = '     ' + v
				
		try:
			iUCICodeCol = self.colnames.index( _("UCICode") )
			padCol( iUCICodeCol )
		except ValueError:
			iUCICodeCol = None
		
		try:
			iNatCodeCol = self.colnames.index( _("NatCode") )
			padCol( iNatCodeCol )
		except ValueError:
			iNatCodeCol = None
		
		# Remember: _getDataSizeTuple understands self.rowDrawCount and will compute the height using the count.
		font = self._getFontToFit( widthFieldPix, heightFieldPix, lambda font: self._getDataSizeTuple(dc, font) )
		dc.SetFont( font )
		wSpace, hSpace = dc.GetMultiLineTextExtent( '    ' )
		textHeight = lh = dc.GetTextExtent( 'Py' )[1]
		
		# Get the row slice for each column.
		dataDraw = [col[rowDrawStart:rowDrawStart+rowDrawCount] for col in self.data]
		
		yPixTop = yPixMax = yPix
		for col, c in enumerate(self.colnames):
			isSpeed = (c == _('Speed'))
			if isSpeed and dataDraw[col]:
				try:
					c = self.colnames[col] = self.data[col][0].split()[1]
				except IndexError:
					c = self.colnames[col] = ''
		
			colWidth = self._getColSizeTuple( dc, font, col )[0]
			yPix = yPixTop
			w, h = dc.GetMultiLineTextExtent( c )
			if col in self.leftJustifyCols:
				self._drawMultiLineText( dc, '{}'.format(c), xPix, yPix )					# left justify
			else:
				self._drawMultiLineText( dc, '{}'.format(c), xPix + colWidth - w, yPix )	# right justify
			yPix += h + hSpace//4
			if col == 0:
				yLine = yPix - hSpace//8
				dc.SetPen( wx.Pen(wx.Colour(200,200,200)) )
				for r in range(max(len(cData) for cData in dataDraw) + 1):
					dc.DrawLine( borderPix, round(yLine + r * textHeight), round(widthPix - borderPix), round(yLine + r * textHeight) )
				dc.SetPen( wx.BLACK_PEN )
			
			for v in dataDraw[col]:
				vStr = '{}'.format(v)
				if vStr:
					if isSpeed:
						vStr = vStr.split()[0]
						if vStr == '"':
							vStr += '    '
					w, h = dc.GetMultiLineTextExtent( vStr )
					if col in self.leftJustifyCols:
						self._drawMultiLineText( dc, vStr, xPix, yPix )					# left justify
					else:
						self._drawMultiLineText( dc, vStr, xPix + colWidth - w, yPix )	# right justify
				if col == iUCICodeCol or col == iNatCodeCol:
					ioc = vStr.strip()[:3].upper()
					try:
						bmp = flagCache[ioc]
					except KeyError:
						img = Flags.GetFlagImage( ioc )
						if img:
							h = int( textHeight * 0.66 )
							w = int( float(img.GetWidth()) / float(img.GetHeight()) * float(h) )
							bmp = flagCache[ioc] = img.Scale(w, h, wx.IMAGE_QUALITY_NORMAL).ConvertToBitmap()
						else:
							bmp = flagCache[ioc] = None
					if bmp:
						padding = (textHeight - bmp.GetHeight()) // 2
						dc.DrawBitmap( bmp, int(xPix), int(yPix+padding) )

				yPix += textHeight
			yPixMax = max(yPixMax, yPix)
			xPix += colWidth + wSpace
			
			if isSpeed:
				self.colnames[col] = _('Speed')
		
		# Switch to smaller font.
		font = self._getFont( borderPix // 4, False )
		dc.SetFont( font )
		
		if url:
			yPix = yPixMax + textHeight
			w, h = dc.GetMultiLineTextExtent( url )
			self._drawMultiLineText( dc, url, widthPix - borderPix - w, yPix )
			
		# Put CrossMgr branding at the bottom of the page.
		w, h = dc.GetMultiLineTextExtent( self.brandText )
		yFooter = heightPix - borderPix + int(h*1.8)
		
		self._drawMultiLineText( dc, self.brandText, borderPix, yFooter )
		
		# Put the page number info at the bottom of the page.
		if pageNumber is not None:
			if pageNumberTotal is not None:
				s = '{} {} / {}'.format(_('Page'), pageNumber, pageNumberTotal)
			else:
				s = '{} {}'.format(_('Page'), pageNumber)
			w, h = dc.GetMultiLineTextExtent( s )
			self._drawMultiLineText( dc, s, widthPix - w - borderPix, yFooter )
			
		# Clean up the extra spaces for the flags.
		for iColCode in (iUCICodeCol, iNatCodeCol):
			if iColCode is not None:
				for c, v in enumerate(self.data[iColCode]):
					self.data[iColCode][c] = v.strip()
	
	def drawToFitPDF( self, pdf, orientation,
						rowDrawStart = 0, rowDrawCount = 1000000,
						pageNumber = None, pageNumberTotal = None ):
							
		self.combineFirstLastNames()
		
		self.rowDrawCount = rowDrawCount
		
		pdf.add_page()
		pdf.set_font( 'Helvetica', '', 12 )
		pdf.set_draw_color( 200, 200, 200 )
		pdf.set_line_width( 0.2 )
		pdf.set_margins( 0, 0, 0 )
		pdf.set_auto_page_break( False, 0 )
		
		# Get the dimensions of the page.
		widthPix, heightPix = 72.0*11, 72.0*8.5
		if orientation != wx.LANDSCAPE:
			widthPix, heightPix = heightPix, widthPix
		
		# Get a reasonable border.
		borderPix = int(max(widthPix, heightPix) / 20)
		
		widthFieldPix = widthPix - borderPix * 2
		heightFieldPix = heightPix - borderPix * 2
		
		xPix = yPix = borderPix
		
		# Draw the graphic.
		bitmap = getHeaderBitmap()
		bmWidth, bmHeight = bitmap.GetWidth(), bitmap.GetHeight()
		
		graphicHeight = int(heightPix * 0.15)
		graphicWidth = int(float(bmWidth) / float(bmHeight) * graphicHeight)
		graphicBorder = int(graphicWidth * 0.15)

		image = bitmap.ConvertToImage()
		graphicFName = os.path.join( os.path.expanduser('~'), uuid.uuid4().hex + '.png' )
		image.SaveFile( graphicFName, wx.BITMAP_TYPE_PNG )
		image, bitmap = None, None
		pdf.image( graphicFName, xPix, yPix, graphicWidth, graphicHeight )
		os.remove( graphicFName )
		
		# Get the race URL (if defined).
		with Model.LockRace() as race:
			url = getattr( race, 'urlFull', None )
		if url and url.startswith( 'http://' ):
			url = quote( url[7:] )
		qrWidth = 0
		if url:
			url = url.replace( '%20', ' ' )
		
		# Draw the title.
		table = [ [line] for line in self.title.split('\n') ]
		pdf.table_in_rectangle(
			xPix + graphicWidth + graphicBorder, yPix,
			widthFieldPix - graphicWidth - graphicBorder - qrWidth, graphicHeight,
			table,
			leftJustifyCols=[0], hasHeader=False, horizontalLines=False, verticalLines=False,
		)
		yPix += graphicHeight + graphicBorder
		
		heightFieldPix = heightPix - yPix - borderPix
		
		# Get the row slice for each column.
		dataDraw = [col[rowDrawStart:rowDrawStart+rowDrawCount] for col in self.data]
		
		# Get the table headers.
		headers = []
		speedCol = None
		uciCodeCol = None
		natCodeCol = None
		for col, c in enumerate(self.colnames):
			if c == _('Speed'):
				speedCol = col
				try:
					c = dataDraw[col][0].split()[1]
				except IndexError:
					pass
			elif c == _('UCICode'):
				uciCodeCol = col
			elif c == _('NatCode'):
				natCodeCol = col
			headers.append( c )

		table = [headers]
		
		# Get the table data.
		for r in range(max(len(col) for col in dataDraw)):
			row = []
			for c in range(len(dataDraw)):
				try:
					v = dataDraw[c][r]
				except IndexError:
					v = ''
				v = '{}'.format(v)
				if c == speedCol:
					v = (v.split() or [''])[0]
					if v == '"':
						v += '    '
				elif c == uciCodeCol or c == natCodeCol:
					v = '     ' + v	# Add some spacing to fit the flag on the UCI code.
				row.append( v )
			table.append( row )
	
		tableWidth, tableHeight = pdf.table_in_rectangle(
			borderPix, yPix,
			widthFieldPix, heightFieldPix - borderPix/1.5,
			table, 
			leftJustifyCols=self.leftJustifyCols, hasHeader=True, horizontalLines=True, verticalLines=False,
		)
		for codeCol in [uciCodeCol, natCodeCol]:
			if codeCol is None:
				continue
			flagStatus = {}
			for r in range(1, len(table)):
				ioc = table[r][codeCol].strip()[:3].upper()
				flagFName = Flags.GetFlagFName( ioc )
				if ioc not in flagStatus:
					flagStatus[ioc] = os.path.exists( flagFName )
				if not flagStatus[ioc]:
					continue
				x, y, height = pdf.xCol[codeCol], pdf.yRow[r], pdf.yRow[r+1] - pdf.yRow[r]
				img = Flags.GetFlagImage( ioc )
				h = int( height * 0.66 )
				w = int( float(img.GetWidth()) / float(img.GetHeight()) * float(h) )
				padding = (height - h) // 2
				pdf.image( flagFName, x=x, y=y+int(padding*1.75), w=w, h=h, type='PNG' )
				
		# Switch to smaller font.
		h = int(borderPix / 4.0)
		pdf.set_font_size( h )
		textHeight = int(h * 1.15)
		
		def write_link( x, y, text, link ):
			pdf.set_xy( x, y )
			pdf.set_font( '', 'U' )
			pdf.set_text_color( 0, 0, 255 )
			pdf.write( h, text, link.replace(' ', '%20') )
			pdf.set_font( '', '' )
			pdf.set_text_color( 0, 0, 0 )
			
		def write_text( x, y, text ):
			pdf.set_xy( x, y )
			pdf.write( h, text )
		
		yPixMax = yPix + tableHeight
		if url:
			yPix = yPixMax + textHeight
			write_link( widthPix - borderPix - pdf.get_string_width(url), yPix+h/2, url, url )
		
		# Put CrossMgr branding at the bottom of the page.
		yFooter = heightPix - borderPix + int(h*1.8) - h
		m = re.search( ' \([^)]+\) ', self.brandText )
		urlStart, urlEnd = m.start() + 2, m.end() - 2
		bt = [self.brandText[:urlStart], self.brandText[urlStart:urlEnd], self.brandText[urlEnd:]]
		
		xCur = borderPix
		write_text( xCur, yFooter, bt[0] )
		xCur += pdf.get_string_width(bt[0])
		write_link( xCur, yFooter, bt[1], bt[1] )
		xCur += pdf.get_string_width(bt[1])
		write_text( xCur, yFooter, bt[2] )
		
		# Put the page number info at the bottom of the page.
		if pageNumber is not None:
			if pageNumberTotal is not None:
				s = '{} {} / {}'.format(_('Page'), pageNumber, pageNumberTotal)
			else:
				s = '{} {}'.format(_('Page'), pageNumber)
			write_text( widthPix - pdf.get_string_width(s) - borderPix, yFooter, s )
			
	def toExcelSheet( self, sheet ):
		''' Write the contents of the grid to an xlwt excel sheet. '''
		titleStyle = xlwt.XFStyle()
		titleStyle.font.bold = True
		titleStyle.font.height += titleStyle.font.height // 2

		headerStyleAlignLeft = xlwt.XFStyle()
		headerStyleAlignLeft.borders.bottom = xlwt.Borders.MEDIUM
		headerStyleAlignLeft.font.bold = True
		headerStyleAlignLeft.alignment.horz = xlwt.Alignment.HORZ_LEFT
		headerStyleAlignLeft.alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
		
		headerStyleAlignRight = xlwt.XFStyle()
		headerStyleAlignRight.borders.bottom = xlwt.Borders.MEDIUM
		headerStyleAlignRight.font.bold = True
		headerStyleAlignRight.alignment.horz = xlwt.Alignment.HORZ_RIGHT
		headerStyleAlignRight.alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
		
		styleAlignLeft = xlwt.XFStyle()
		styleAlignLeft.alignment.horz = xlwt.Alignment.HORZ_LEFT
		
		styleAlignRight = xlwt.XFStyle()
		styleAlignRight.alignment.horz = xlwt.Alignment.HORZ_RIGHT
		
		rowTop = 0
		if self.title:
			for line in self.title.split('\n'):
				sheet.write(rowTop, 0, line, titleStyle)
				rowTop += 1
			rowTop += 1
		
		sheetFit = FitSheetWrapper( sheet )
		
		# Write the colnames and data.
		rowMax = 0
		for col, c in enumerate(self.colnames):
			isSpeed = (c == _('Speed'))
			if isSpeed and self.data[col]:
				try:
					c = self.colnames[col] = self.data[col][0].split()[1]
				except IndexError:
					c = self.colnames[col] = ''

			headerStyle = headerStyleAlignLeft if col in self.leftJustifyCols else headerStyleAlignRight
			style = styleAlignLeft if col in self.leftJustifyCols else styleAlignRight
			
			sheetFit.write( rowTop, col, c, headerStyle, bold=True )
			for row, v in enumerate(self.data[col]):
				if isSpeed and v:
					v = ('{}'.format(v).split() or [''])[0]
					if v == '"':
						v += '    '
				rowCur = rowTop + 1 + row
				if rowCur > rowMax:
					rowMax = rowCur
				sheetFit.write( rowCur, col, v, style )
			
			if isSpeed:
				self.colnames[col] = _('Speed')
		
		if self.footer:
			rowMax += 2
			for line in self.footer.split('\n'):
				sheet.write( rowMax, 0, line.strip(), styleAlignLeft )
				rowMax += 1
		
		# Add branding at the bottom of the sheet.
		sheet.write( rowMax + 2, 0, self.brandText, styleAlignLeft )
	
	@staticmethod
	def getExcelFormatsXLSX( workbook ):
		titleStyle = workbook.add_format({
			'bold': True,
			'font_size': 17,
		})

		headerStyleAlignLeft = workbook.add_format({
			'bottom':	2,
			'bold':		True,
			'text_wrap':True,
		})
		
		headerStyleAlignRight = workbook.add_format({
			'bottom':	2,
			'bold':		True,
			'text_wrap':True,
			'align':	'right',
		})
		
		styleAlignLeft = workbook.add_format()
		
		styleAlignRight = workbook.add_format({
			'align':	'right',
		})
		
		#---------------------------------------------------------------
		styleTime = workbook.add_format({
			'align':	'right',
			'num_format': 'hh:mm:ss.000',
		})
		
		styleMMSS = workbook.add_format({
			'align':	'right',
			'num_format': 'mm:ss.000',
		})
		
		styleSS = workbook.add_format({
			'align':	'right',
			'num_format': 'ss.000',
		})
		
		#---------------------------------------------------------------
		# Low-precision time formats
		#
		styleTimeLP = workbook.add_format({
			'align':	'right',
			'num_format': 'hh:mm:ss',
		})
		
		styleMMSSLP = workbook.add_format({
			'align':	'right',
			'num_format': 'mm:ss',
		})
		
		styleSSLP = workbook.add_format({
			'align':	'right',
			'num_format': 'ss',
		})
		
		return {
			'titleStyle':				titleStyle,
			'headerStyleAlignLeft':		headerStyleAlignLeft,
			'headerStyleAlignRight':	headerStyleAlignRight,
			'styleAlignLeft':			styleAlignLeft,
			'styleAlignRight':			styleAlignRight,
			'styleTime':				styleTime,
			'styleHHMMSS':				styleTime,
			'styleMMSS':				styleMMSS,
			'styleSS':					styleSS,

			'styleTimeLP':				styleTimeLP,
			'styleHHMMSSLP':			styleTimeLP,
			'styleMMSSLP':				styleMMSSLP,
			'styleSSLP':				styleSSLP,
		}
	
	def toExcelSheetXLSX( self, formats, sheet ):
		''' Write the contents of the grid to an xlwt excel sheet. '''
		titleStyle				= formats['titleStyle']
		headerStyleAlignLeft	= formats['headerStyleAlignLeft']
		headerStyleAlignRight	= formats['headerStyleAlignRight']
		styleAlignLeft			= formats['styleAlignLeft']
		styleAlignRight			= formats['styleAlignRight']
		
		styleTime				= formats['styleTime']
		styleMMSS				= formats['styleMMSS']
		styleSS					= formats['styleSS']
		
		styleTimeLP				= formats['styleTimeLP']
		styleMMSSLP				= formats['styleMMSSLP']
		styleSSLP				= formats['styleSSLP']
				
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
			isSpeed = (c == _('Speed'))
			if isSpeed and self.data[col]:
				try:
					c = self.colnames[col] = self.data[col][0].split()[1]
				except IndexError:
					c = self.colnames[col] = ''

			headerStyle = headerStyleAlignLeft if col in self.leftJustifyCols else headerStyleAlignRight
			style = styleTime if col in self.timeCols else styleAlignLeft if col in self.leftJustifyCols else styleAlignRight
			
			if col in self.timeCols:
				# Find a time format closest to the maximum value.
				vMax = 0.0
				highPrecision = False
				for v in self.data[col]:
					try:
						v = abs(Utils.StrToSeconds(v))
						highPrecision |= (int(v) != v)
						vMax = max( vMax, v )
					except Exception as e:
						print( e )
						continue
				# If all the times lack decimals, use low precision format.
				if vMax < 60.0:
					style = styleSS if highPrecision else styleSSLP
				elif vMax < 60.0*60.0:
					style = styleMMSS if highPrecision else styleMMSSLP
				else:
					style = styleTime if highPrecision else styleTimeLP
			
			sheetFit.write( rowTop, col, c, headerStyle, bold=True )
			for row, v in enumerate(self.data[col]):
				if isSpeed and v:
					v = ('{}'.format(v).split() or [''])[0]
					if v == '"':
						v += '    '
				elif col in self.timeCols:
					if v:
						try:
							v = Utils.StrToSeconds(v) / (24.0*60.0*60.0)	# Convert seconds to fraction of a day for Excel.
						except Exception:
							pass
				
				rowCur = rowTop + 1 + row
				if rowCur > rowMax:
					rowMax = rowCur
				sheetFit.write( rowCur, col, v, style )
			
			if isSpeed:
				self.colnames[col] = _('Speed')
		
		if self.footer:
			rowMax += 2
			for line in self.footer.split('\n'):
				sheet.write( rowMax, 0, line.strip(), styleAlignLeft )
				rowMax += 1
		
		# Add branding at the bottom of the sheet.
		sheet.write( rowMax + 2, 0, self.brandText, styleAlignLeft )
	
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
	
	def setResultsOneList( self, category = None, getExternalData = True,
							showLapsFrequency = None, showLapTimes = True,
							showPrizes = False ):
		''' Format the results into columns. '''
		self.data = []
		self.colnames = []
		self.footer = None

		results = GetResults( category )
		if not results:
			return
		
		Finisher = Model.Rider.Finisher
		race = Model.race
		prizes = category.prizes if category else []
		showPrizes = showPrizes and bool(prizes)
		
		catDetails = { cd['name']:cd for cd in GetCategoryDetails() }
		try:
			cd = catDetails[category.fullname]
		except Exception:
			cd = None
			
		if category:
			starters, lapped, dnf = 0, 0, 0
			for rr in results:
				if rr.status != Model.Rider.DNS:
					starters += 1
				if rr.status == Model.Rider.DNF:
					dnf += 1
				if rr.gap.startswith('-'):
					lapped += 1
			self.footer = (''.join([
					_('Total'), ':',
					'   {} ', _('Starters'),
					',  {} ', _('DNF'),
					',  {} ', _('Lapped')])).format( starters, dnf, lapped )

		leader = results[0]
		
		hasSpeeds = (hasattr(leader, 'lapSpeeds') or hasattr(leader, 'raceSpeeds'))
		hasFactor = (hasattr(leader, 'factor') and any( leader.factor != rr.factor for rr in results ))
		
		leaderTime = (
			Utils.formatTime(leader.lastTime - leader.raceTimes[0])
				if leader.lastTime and leader.raceTimes and leader.status == Finisher
				else ''
		)
		
		if showLapTimes and showLapsFrequency is None:
			# Compute a reasonable number of laps to show (max around 10).
			# Get the maximum laps in the data.
			maxLaps = max( len(r.lapTimes or []) for r in results )
			showLapsFrequency = max( 1, int(math.ceil(maxLaps / 10.0)) )
		
		catStr = category.fullname if category else 'All'
		catData = []
		if cd and cd.get('raceDistance', None):
			catData.append( '{:.2f} {}'.format(cd['raceDistance'], cd['distanceUnit']) )
			if cd.get('lapDistance', None) and cd.get('laps', 0) > 1:
				if cd.get('firstLapDistance', None) and cd['firstLapDistance'] != cd['lapDistance']:
					catData.append(
						'{} {:.2f} {}, {} {} {:.2f} {}'.format(
								_('1st lap'), cd['firstLapDistance'], cd['distanceUnit'],
								cd['laps'] - 1, _('more laps of'), cd['lapDistance'], cd['distanceUnit']
						)
					)
				else:
					catData.append( '{} {} {:.2f} {}'.format(cd['laps'], _('laps of'), cd['lapDistance'], cd['distanceUnit']) )
		if leader.status == Finisher:
			if getattr(leader, 'speed', None):
				catData.append( '{}: {} - {}'.format(_('winner'), leaderTime, leader.speed) )
			else:
				catData.append( '{}: {}'.format(_('winner'), leaderTime) )
	
		self.title = '\n'.join( [race.title, Utils.formatDate(race.date), catStr, ', '.join(catData)] )
		isTimeTrial = getattr( race, 'isTimeTrial', False )
		roadRaceFinishTimes = race.roadRaceFinishTimes

		infoFields = ReportFields if getExternalData else []
		infoFieldsPresent = set( infoFields ) & set( dir(leader) )
		infoFields = [f for f in infoFields if f in infoFieldsPresent]
		
		self.colnames = ([_('Pos'), _('Bib')] +
						infoFields +
						([_('Clock'),_('Start'),_('Finish')] if isTimeTrial else []) +
						([_('ElapsedTime'), _('Factor %')] if hasFactor else []) +
						[_('Time')] +
						([_('Gap')] if not hasFactor else [])
		)
		if hasSpeeds:
			self.colnames.append( _('Speed') )
		if showPrizes:
			self.colnames.append( _('Prize') )
			
		self.colnames = ['{} {}'.format(name[:-len(_('Name'))], _('Name')) if name.endswith(_('Name')) else name for name in self.colnames]
		self.iLapTimes = len(self.colnames)
		if race.winAndOut:
			lapsMax = max(len(rr.lapTimes or []) for rr in results)
		else:
			lapsMax = len(leader.lapTimes or [])
			
		if leader.lapTimes and showLapTimes:
			self.colnames.extend( ['{} {}'.format(_('Lap'),lap) for lap in range(1, lapsMax+1) \
					if lap % showLapsFrequency == 0 or lap == 1 or lap == lapsMax] )
		
		self.setTimeCols()
		
		highPrecision = Model.highPrecisionTimes()
		data = [ [] for i in range(len(self.colnames)) ]
		colsMax = len(self.colnames)
		rrFields = (['pos', 'num'] +
					infoFields +
					(['clockStartTime','startTime','finishTime'] if isTimeTrial else []) +
					(['lastTimeOrig', 'factor', 'lastTime'] if hasFactor else ['lastTime']) +
					(['gap'] if not hasFactor else []) 
		)
		if hasSpeeds:
			rrFields.append( 'speed' )
		if showPrizes:
			rrFields.append( 'prize' )
		for col, f in enumerate( rrFields ):
			if f in ('lastTime', 'lastTimeOrig'):
				for row, rr in enumerate(results):
					if rr.status == Finisher:
						v = getattr( rr, f, 0.0 )
						ttt = (v - rr.raceTimes[0]) if v and rr.raceTimes else 0.0
						data[col].append( Utils.formatTimeCompressed(ttt, highPrecision) if ttt > 0.0 else '' )
					else:
						data[col].append( '' )
			elif f in ('clockStartTime', 'startTime', 'finishTime'):
				for row, rr in enumerate(results):
					if f == 'finishTime' and rr.status != Finisher:
						data[col].append( '' )
						continue
						
					sfTime = getattr( rr, f, None )
					if sfTime is not None:
						data[col].append( Utils.formatTimeCompressed(sfTime, highPrecision) )
						continue
						
					data[col].append( '' )
			elif f == 'factor':
				for row, rr in enumerate(results):
					factor = getattr( rr, f, None )
					if factor is not None:
						data[col].append( '{:.2f}'.format(factor) )
					else:
						data[col].append( '' )
			elif f == 'prize':
				for row, rr in enumerate(results):
					try:
						data[col].append( prizes[row] )
					except IndexError:
						data[col].append( '' )
			else:
				for row, rr in enumerate(results):
					data[col].append( getattr(rr, f, '') )
		
		if showLapTimes:
			for row, rr in enumerate(results):
				iCol = self.iLapTimes
				for i, t in enumerate(rr.lapTimes):
					lap = i + 1
					if lap % showLapsFrequency == 0 or lap == 1 or lap == lapsMax:
						try:
							data[iCol].append( Utils.formatTimeCompressed(t, highPrecision) )
							iCol += 1
							if iCol >= colsMax:
								break
						except IndexError as e:
							break
				
				# Pad out the rest of the columns.
				for i in range(len(rr.lapTimes), lapsMax):
					lap = i + 1
					if lap % showLapsFrequency == 0 or lap == 1 or lap == lapsMax:
						try:
							data[iCol].append( '' )
							iCol += 1
						except IndexError as e:
							break
		
		self.data = data
		self.infoColumns     = set( range(2, 2+len(infoFields)) ) if infoFields else set()
		self.leftJustifyCols = set( range(2, 2+len(infoFields)) ) if infoFields else set()
		try:
			self.leftJustifyCols.remove( self.colnames.index(_('Age')) )
		except ValueError:
			pass
		
		if roadRaceFinishTimes:
			sameValue = '"    '
			try:
				iSpeed = self.colnames.index(_('Speed'))
			except ValueError:
				iSpeed = -1
			
			try:
				iTime = self.colnames.index(_('Time'))
			except ValueError:
				iTime = -1
			if iTime > 0:
				lastTime = 'xxx'
				timeCol = self.data[iTime]
				speedCol = self.data[iSpeed] if iSpeed >= 0 else None
				for i in range(0, len(timeCol)):
					curTime = timeCol[i]
					if curTime == lastTime:
						timeCol[i] = sameValue
						if speedCol:
							speedCol[i] = sameValue
					else:
						lastTime = curTime
			try:
				iGap = self.colnames.index(_('Gap'))
			except ValueError:
				iGap = -1
			if iGap > 0:
				lastGap = 'xxx'
				gapCol = self.data[iGap]
				for i in range(0, len(gapCol)):
					curGap = gapCol[i]
					if curGap and not curGap.startswith('-') and curGap == lastGap:
						gapCol[i] = sameValue
					else:
						lastGap = curGap
						
		self.colnames = [Utils.translate(n) if n in infoFieldsPresent else n for n in self.colnames]

if __name__ == '__main__':
	pass
