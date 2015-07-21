
import wx
import os
import xlwt
import Utils
import Model
import math
from GetResults import GetResults, GetCategoryDetails
from ReadSignOnSheet import ReportFields
from FitSheetWrapper import FitSheetWrapper
import qrcode
import urllib
# from reportlab.lib.pagesizes import letter, A4

#---------------------------------------------------------------------------

# Sort sequence by rider status.
statusSortSeq = Model.Rider.statusSortSeq

brandText = _('Powered by CrossMgr (sites.google.com/site/crossmgrsoftware)')

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

def getQRCodeBitmap( url ):
	''' Get a QRCode image for the results url. '''
	qr = qrcode.QRCode()
	qr.add_data( 'http://' + url )
	qr.make()
	border = 0
	img = wx.EmptyImage( qr.modules_count + border * 2, qr.modules_count + border * 2 )
	bm = img.ConvertToMonoBitmap( 0, 0, 0 )
	canvasQR = wx.MemoryDC()
	canvasQR.SelectObject( bm )
	canvasQR.SetBrush( wx.WHITE_BRUSH )
	canvasQR.Clear()
	canvasQR.SetPen( wx.BLACK_PEN )
	for row in xrange(qr.modules_count):
		for col, v in enumerate(qr.modules[row]):
			if v:
				canvasQR.DrawPoint( border + col, border + row )
	canvasQR.SelectObject( wx.NullBitmap )
	return bm

class ExportGrid( object ):
	PDFLineFactor = 1.10

	def __init__( self, title = '', colnames = [], data = [], footer = '', leftJustifyCols=None, infoColumns=None ):
		self.title = title
		self.footer = footer
		self.colnames = colnames
		self.data = data
		self.leftJustifyCols = (leftJustifyCols or set())
		self.infoColumns = (infoColumns or set())
		self.iLapTimes = 0
		self.rowDrawCount = 1000000
		
		self.fontName = 'Helvetica'
		self.fontSize = 16
	
	def _getFont( self, pixelSize = 28, bold = False ):
		return wx.FontFromPixelSize( (0,pixelSize), wx.FONTFAMILY_SWISS, wx.NORMAL,
									 wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL, False )
	
	def _getColSizeTuple( self, dc, font, col ):
		wSpace, hSpace, lh = dc.GetMultiLineTextExtent( '    ', font )
		extents = [ dc.GetMultiLineTextExtent(self.colnames[col], font) ]
		extents.extend( dc.GetMultiLineTextExtent(u'{}'.format(v), font) for v in self.data[col] )
		width = max( e[0] for e in extents )
		height = sum( e[1] for e in extents[:self.rowDrawCount] )
		return width, height + hSpace/4
	
	def _getDataSizeTuple( self, dc, font ):
		wSpace, hSpace, lh = dc.GetMultiLineTextExtent( '    ', font )
		
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
	
	def drawToFitDC( self, dc,
						rowDrawStart = 0, rowDrawCount = 1000000,
						pageNumber = None, pageNumberTotal = None ):
		self.rowDrawCount = rowDrawCount
			
		# Get the dimensions of what we are printing on.
		(widthPix, heightPix) = dc.GetSizeTuple()
		
		# Get a reasonable border.
		borderPix = max(widthPix, heightPix) / 20
		
		widthFieldPix = widthPix - borderPix * 2
		heightFieldPix = heightPix - borderPix * 2
		
		xPix = borderPix
		yPix = borderPix
		
		# Draw the graphic.
		bitmap = getHeaderBitmap()
		bmWidth, bmHeight = bitmap.GetWidth(), bitmap.GetHeight()
		graphicHeight = heightPix * 0.15
		graphicWidth = float(bmWidth) / float(bmHeight) * graphicHeight
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
		
		# Get the race URL (if defined).
		with Model.LockRace() as race:
			url = getattr( race, 'urlFull', None )
		if url and url.startswith( 'http://' ):
			url = urllib.quote( url[7:] )
			
		qrWidth = 0
		if url:
			qrWidth = graphicHeight
			bm = getQRCodeBitmap( url )
			img = bm.ConvertToImage()
			img.Rescale( qrWidth, qrWidth, wx.IMAGE_QUALITY_NORMAL )
			img = img.ConvertToGreyscale()
			bm = img.ConvertToBitmap( dc.GetDepth() )
			dc.DrawBitmap( bm, widthPix - borderPix - qrWidth, borderPix )
			qrWidth += graphicBorder
		
		# Draw the title.
		font = self._getFontToFit( widthFieldPix - graphicWidth - graphicBorder - qrWidth, graphicHeight,
									lambda font: dc.GetMultiLineTextExtent(self.title, font)[:-1], True )
		dc.SetFont( font )
		self._drawMultiLineText( dc, self.title, xPix + graphicWidth + graphicBorder, yPix )
		# wText, hText, lineHeightText = dc.GetMultiLineTextExtent( self.title, font )
		# yPix += hText + lineHeightText/4
		yPix += graphicHeight + graphicBorder
		
		heightFieldPix = heightPix - yPix - borderPix
		
		# Draw the table.
		# Remember: _getDataSizeTuple understands self.rowDrawCount and will compute the height using the count.
		font = self._getFontToFit( widthFieldPix, heightFieldPix, lambda font: self._getDataSizeTuple(dc, font) )
		dc.SetFont( font )
		wSpace, hSpace, textHeight = dc.GetMultiLineTextExtent( '    ', font )
		
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
			w, h, lh = dc.GetMultiLineTextExtent( c, font )
			if col in self.leftJustifyCols:
				self._drawMultiLineText( dc, u'{}'.format(c), xPix, yPix )					# left justify
			else:
				self._drawMultiLineText( dc, u'{}'.format(c), xPix + colWidth - w, yPix )	# right justify
			yPix += h + hSpace/4
			if col == 0:
				yLine = yPix - hSpace/8
				for r in xrange(max(len(cData) for cData in dataDraw) + 1):
					dc.DrawLine( borderPix, yLine + r * textHeight, widthPix - borderPix, yLine + r * textHeight )
					
			for v in dataDraw[col]:
				vStr = u'{}'.format(v)
				if vStr:
					if isSpeed:
						vStr = vStr.split()[0]
					w, h, lh = dc.GetMultiLineTextExtent( vStr, font )
					if col in self.leftJustifyCols:
						self._drawMultiLineText( dc, vStr, xPix, yPix )					# left justify
					else:
						self._drawMultiLineText( dc, vStr, xPix + colWidth - w, yPix )	# right justify
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
			w, h, lh = dc.GetMultiLineTextExtent( url, font )
			self._drawMultiLineText( dc, url, widthPix - borderPix - w, yPix )
			
		# Put CrossMgr branding at the bottom of the page.
		w, h, lh = dc.GetMultiLineTextExtent( brandText, font )
		yFooter = heightPix - borderPix + int(h*1.8)
		
		self._drawMultiLineText( dc, brandText, borderPix, yFooter )
		
		# Put the page number info at the bottom of the page.
		if pageNumber is not None:
			if pageNumberTotal is not None:
				s = u'{} {} / {}'.format(_('Page'), pageNumber, pageNumberTotal)
			else:
				s = u'{} {}'.format(_('Page'), pageNumber)
			w, h, lh = dc.GetMultiLineTextExtent( s, font )
			self._drawMultiLineText( dc, s, widthPix - w - borderPix, yFooter )
	
	'''
	def _setFontPDF( self, canvas, pointSize = 24, bold = False ):
		self.fontName = 'Helvetica' + ('-Bold' if bold else '')
		self.fontSize = pointSize
		canvas.setFont( self.fontName, self.fontSize )
	
	def _drawMultiLineTextPDF( self, canvas, text, x, y ):
		if not text:
			return
		lineHeightText = self.fontSize * PDFLineFactor
		for line in text.split( '\n' ):
			canvas.drawString( x, y, line )
			y -= lineHeightText

	def _getMultiLineTextExtentPDF( self, canvas, text, fontName = None, fontSize = None ):
		if fontName is None:
			fontName = self.fontName
		if fontSize is None:
			fontsize = self.fontSize
		width = 0
		height = 0
		for line in text.split('\n'):
			width = max( width, canvas.stringWidth(text, fontName, fontSize) )
			height += fontSize * self.PDFLineFactor
		return width, height
	
	def _setFontToFitPDF( self, canvas, text, widthToFit, heightToFit, isBold = False ):
		left = 1
		right = max(widthToFit, heightToFit)
		
		fontName = 'Helvectica' + '-Bold' if isBold else ''
		while right - left > 1:
			mid = (left + right) / 2.0
			fontSize = mid
			self._setFontPDF( fontSize, isBold )
			widthText, heightText = self._getMultiLineTextExtentPDF(canvas, text, fontName, fontSize)
			if widthText <= widthToFit and heightText <= heightToFit:
				left = mid
			else:
				right = mid - 1
		
		self._setFontPDF( left, isBold )
			
	def drawToFitPDF( self, canvas, pageSize = letter, landscape = True, blackAndWhite = True ):
		# Get the dimensions of what we are printing on.
		widthPnt, heightPnt = pageSize
		if landscape:
			canvas.translate( 0, widthPnt )
			canvas.rotate( 90 )
			widthPnt, heightPnt = heightPnt, widthPnt
	
		# Get a reasonable border.
		borderPnt = max(widthPnt, heightPnt) / 20
		
		widthFieldPnt = widthPnt - borderPnt * 2
		heightFieldPnt = heightPnt - borderPnt * 2
		
		xPnt = borderPnt
		yPnt = heightPnt - borderPnt
		
		# Draw the graphic.
		bitmap = getHeaderBitmap()
		bmWidth, bmHeight = bitmap.GetWidth(), bitmap.GetHeight()
		graphicHeight = heightPnt * 0.15
		graphicWidth = float(bmWidth) / float(bmHeight) * graphicHeight
		graphicBorder = int(graphicWidth * 0.15)
		image = bitmap.ConvertToImage()
		if blackAndWhite:
			image = image.ConvertToGreyscale()
		pil = ImageToPil( image )
		canvas.drawImage( pil, xPnt, yPnt - graphicHeight, graphicWidth, graphicHeight )
		image, bitmap, pil = None, None, None
		
		# Get the race URL (if defined).
		with Model.LockRace() as race:
			url = getattr( race, 'urlFull', None )
		if url and url.startswith( 'http://' ):
			url = urllib.quote( url[7:] )
			
		qrWidth = 0
		if url:
			bm = getQRCodeBitmap( url )
			img = bm.ConvertToImage()
			img = img.ConvertToGreyscale()
			pil = ImageToPil( img )
			qrWidth = graphicHeight
			canvas.drawImage( pil, widthPnt - borderPnt - graphicHeight, yPnt - qrWidth, qrWidth, qrWidth )
			qrWidth += graphicBorder
			img, bm, pil = None, None, None
		
		# Draw the title.
		self._setFontToFitPDF( canvas, self.title, widthFieldPnt - graphicWidth - graphicBorder - qrWidth, graphicHeight, True )
		self._drawMultiLineTextPDF( canvas, self.title, xPnt + graphicWidth + graphicBorder, yPnt )
		yPnt -= graphicHeight + graphicBorder
		
		heightFieldPnt = heightPnt - yPnt - borderPnt
		
		# Draw the table.
		self._setFontToFit( widthFieldPnt, heightFieldPnt, lambda font: self._getDataSizeTuple(canvas, font) )
		wSpace = canvas.stringWidth( '    ' )
		
		yPntTop = yPnt
		yPntMin = yPnt
		for col, c in enumerate(self.colnames):
			isSpeed = (c == 'Speed')
			if isSpeed and self.data[col]:
				c = self.colnames[col] = self.data[col][0].split()[1]
		
			colWidth = self._getColSizeTuple( canvas, font, col )[0]
			yPnt = yPntTop
			w, h, lh = canvas.GetMultiLineTextExtent( c, font )
			if col in self.leftJustifyCols:
				self._drawMultiLineText( canvas, u'{}'.format(c), xPnt, yPnt )					# left justify
			else:
				self._drawMultiLineText( canvas, u'{}'.format(c), xPnt + colWidth - w, yPnt )	# right justify
			yPnt += h + hSpace/4
			if col == 0:
				yLine = yPnt - hSpace/8
				for r in xrange(max(len(cData) for cData in self.data) + 1):
					canvas.DrawLine( borderPnt, yLine + r * textHeight, widthPnt - borderPnt, yLine + r * textHeight )
					
			for v in self.data[col]:
				vStr = '{}'.format(v)
				if vStr:
					if isSpeed:
						vStr = vStr.split()[0]
					w, h, lh = canvas.GetMultiLineTextExtent( vStr, font )
					if col in self.leftJustifyCols:
						self._drawMultiLineText( canvas, vStr, xPnt, yPnt )					# left justify
					else:
						self._drawMultiLineText( canvas, vStr, xPnt + colWidth - w, yPnt )	# right justify
				yPnt += textHeight
			yPntMin = max(yPntMin, yPnt)
			xPnt += colWidth + wSpace
			
			if isSpeed:
				self.colnames[col] = 'Speed'
				
		if url:
			yPnt = yPntMin + textHeight
			w = canvas.stringWidth( url )
			self.drawString( canvas, url, widthPnt - borderPnt - w, yPnt )
			
		# Put CrossMgr branding at the bottom of the page.
		fontSize = borderPnt // 5
		self._setFontPDF( canvas, fontSize, False )
		self.drawString( canvas, brandText, borderPnt, borderPnt - fontSize )
	'''
		
	def toExcelSheet( self, sheet ):
		''' Write the contents of the grid to an xlwt excel sheet. '''
		titleStyle = xlwt.XFStyle()
		titleStyle.font.bold = True
		titleStyle.font.height += titleStyle.font.height / 2

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
					v = '{}'.format(v).split()[0]
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
		sheet.write( rowMax + 2, 0, brandText, styleAlignLeft )
	
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
							showLapsFrequency = None, showLapTimes = True ):
		''' Format the results into columns. '''
		self.data = []
		self.colnames = []
		self.footer = None

		results = GetResults( category, getExternalData )
		if not results:
			return
		catDetails = dict( (cd['name'], cd) for cd in GetCategoryDetails() )
		try:
			cd = catDetails[category.fullname]
		except:
			cd = None
			
		if category:
			starters, lapped, dnf = 0, 0, 0
			for r in results:
				if r.status != Model.Rider.DNS:
					starters += 1
				if r.status == Model.Rider.DNF:
					dnf += 1
				if r.gap.startswith('-'):
					lapped += 1
			self.footer = (u''.join([
					_('Total'), u':',
					u'   {} ', _('Starters'),
					u',  {} ', _('DNF'),
					u',  {} ', _('Lapped')])).format( starters, dnf, lapped )
			
		leader = results[0]
		hasSpeeds = (hasattr(leader, 'lapSpeeds') or hasattr(leader, 'raceSpeeds'))
		hasFactor = (hasattr(leader, 'factor') and any( leader.factor != rr.factor for rr in results ))
		
		if showLapTimes and showLapsFrequency is None:
			# Compute a reasonable number of laps to show (max around 10).
			# Get the maximum laps in the data.
			maxLaps = 0
			for r in results:
				try:
					maxLaps = max(maxLaps, len(r.lapTimes))
				except:
					pass
			showLapsFrequency = max( 1, int(math.ceil(maxLaps / 10.0)) )
		
		with Model.LockRace() as race:
			catStr = 'All' if not category else category.fullname
			if cd and cd.get('raceDistance', None):
				catStr += u', {:.2f} {}, '.format(cd['raceDistance'], cd['distanceUnit'])
				if cd.get('lapDistance', None) and cd.get('laps', 0) > 1:
					if cd.get('firstLapDistance', None) and cd['firstLapDistance'] != cd['lapDistance']:
						catStr += u'{} {:.2f} {}, {} {} {:.2f} {}'.format(
									_('1st lap'), cd['firstLapDistance'], cd['distanceUnit'],
									cd['laps'] - 1, _('more laps of'), cd['lapDistance'], cd['distanceUnit']
								)
					else:
						catStr += u'{} {} {:.2f} {}'.format(cd['laps'], _('laps of'), cd['lapDistance'], cd['distanceUnit']);
				if leader.status == Model.Rider.Finisher:
					catStr += u', ' + u'{}: {} - {}'.format(_('winner'), Utils.formatTime(leader.lastTime - cd['startOffset']), leader.speed);
		
			self.title = u'\n'.join( [race.name, Utils.formatDate(race.date), catStr] )
			isTimeTrial = getattr( race, 'isTimeTrial', False )
			roadRaceFinishTimes = getattr( race, 'roadRaceFinishTimes', False )

		startOffset = category.getStartOffsetSecs() if category else 0.0
		
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
			self.colnames += [_('Speed')]
			
		self.colnames = [u'{} {}'.format(name[:-len(_('Name'))], _('Name')) if name.endswith(_('Name')) else name for name in self.colnames]
		self.iLapTimes = len(self.colnames)
		lapsMax = len(leader.lapTimes) if leader.lapTimes else 0
		if leader.lapTimes and showLapTimes:
			self.colnames.extend( [u'{} {}'.format(_('Lap'),lap) for lap in xrange(1, lapsMax+1) \
					if lap % showLapsFrequency == 0 or lap == 1 or lap == lapsMax] )
		
		highPrecision = Model.highPrecisionTimes()
		data = [ [] for i in xrange(len(self.colnames)) ]
		colsMax = len(self.colnames)
		rrFields = (['pos', 'num'] +
					infoFields +
					(['clockStartTime','startTime','finishTime'] if isTimeTrial else []) +
					(['lastTimeOrig', 'factor', 'lastTime'] if hasFactor else ['lastTimeOrig']) +
					(['gap'] if not hasFactor else [])
		)
		if hasSpeeds:
			rrFields += ['speed']
		for col, f in enumerate( rrFields ):
			for row, r in enumerate(results):
				if f in {'lastTime', 'lastTimeOrig'}:
					ttt = getattr( r, f, 0.0 )
					if ttt <= 0.0:
						data[col].append( '' )
					else:
						if not isTimeTrial:
							ttt = max( 0.0, ttt - startOffset )
						data[col].append( Utils.formatTimeCompressed(ttt, highPrecision) )
				elif f in {'clockStartTime', 'startTime', 'finishTime'}:
					sfTime = getattr( r, f, None )
					if sfTime is not None:
						data[col].append( Utils.formatTimeCompressed(sfTime, highPrecision) )
					else:
						data[col].append( '' )
				elif f == 'factor':
					factor = getattr( r, f, None )
					if factor is not None:
						data[col].append( '{:.2f}'.format(factor) )
					else:
						data[col].append( '' )
				else:
					data[col].append( getattr(r, f, '') )
		
		if showLapTimes:
			for row, r in enumerate(results):
				iCol = self.iLapTimes
				for i, t in enumerate(r.lapTimes):
					lap = i + 1
					if lap % showLapsFrequency == 0 or lap == 1 or lap == lapsMax:
						data[iCol].append( Utils.formatTimeCompressed(t, highPrecision) )
						iCol += 1
						if iCol >= colsMax:
							break
				# Pad out the rest of the columns.
				for i in xrange(len(r.lapTimes), lapsMax):
					lap = i + 1
					if lap % showLapsFrequency == 0 or lap == 1 or lap == lapsMax:
						data[iCol].append( '' )
						iCol += 1
		
		self.data = data
		self.infoColumns     = set( xrange(2, 2+len(infoFields)) ) if infoFields else set()
		self.leftJustifyCols = set( xrange(2, 2+len(infoFields)) ) if infoFields else set()
		try:
			self.leftJustifyCols.remove( self.colnames.index('Age') )
		except ValueError:
			pass
		
		if roadRaceFinishTimes:
			sameValue = '"    '
			try:
				iTime = self.colnames.index(_('Time'))
			except ValueError:
				iTime = -1
			if iTime > 0:
				lastTime = 'xxx'
				timeCol = self.data[iTime]
				for i in xrange(0, len(timeCol)):
					curTime = timeCol[i]
					if curTime == lastTime:
						timeCol[i] = sameValue
					else:
						lastTime = curTime
			try:
				iGap = self.colnames.index(_('Gap'))
			except ValueError:
				iGap = -1
			if iGap > 0:
				lastGap = 'xxx'
				gapCol = self.data[iGap]
				for i in xrange(0, len(gapCol)):
					curGap = gapCol[i]
					if curGap and not curGap.startswith('-') and curGap == lastGap:
						gapCol[i] = sameValue
					else:
						lastGap = curGap

if __name__ == '__main__':
	pass
