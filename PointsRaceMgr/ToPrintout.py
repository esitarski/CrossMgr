import wx
import os
import html
import math
import datetime
import Utils
from Utils import tag
from ExportGrid import ExportGrid
import Model

class GrowTable:
	bold, alignLeft, alignCentre, alignRight, alignTop, alignMiddle, alignBottom = [1<<i for i in range(7)]
	alignCenter = alignCentre
	attrDefault = alignRight|alignTop
	
	def __init__( self, alignHorizontal=alignCentre, alignVertical=alignCentre, cellBorder=True ):
		self.alignHorizontal = alignHorizontal
		self.alignVertical = alignVertical
		self.cellBorder = cellBorder
		self.clear()
	
	def clear( self ):
		self.table = []
		self.colWidths = []
		self.rowHeights = []
		self.vLines = []
		self.hLines = []
		self.width = None
		self.height = None
	
	def fromGrid( self, grid, horizontalGridlines=True, verticalGridlines=False ):
		self.clear()
		mapHorizontal = {
			wx.ALIGN_LEFT: self.alignLeft,
			wx.ALIGN_RIGHT: self.alignRight,
			wx.ALIGN_CENTER: self.alignCenter,
		}
		mapVertical = {
			wx.ALIGN_TOP: self.alignTop,
			wx.ALIGN_BOTTOM: self.alignBottom,
			wx.ALIGN_CENTER: self.alignMiddle,
		}
		rowLabel = 0
		colLabel = 0
		if grid.GetRowLabelSize() > 0:
			colLabel = 1
		if grid.GetColLabelSize() > 0 and grid.GetNumberCols():
			maxNewLines = max(grid.GetColLabelValue(c).count('\n') for c in range(grid.GetNumberCols()))
			def fixNewLines( v ):
				d = maxNewLines - v.count('\n')
				return v if d == 0 else '\n'*d + v
			for c in range(grid.GetNumberCols()):
				self.set( 0, c+colLabel, fixNewLines(grid.GetColLabelValue(c)), self.bold )
			rowLabel = 1
		if colLabel > 0:
			for r in range(grid.GetNumberRows()):
				self.set( r+rowLabel, 0, grid.GetRowLabelValue(r), self.bold )
		
		def isNumeric( v ):
			if not v:
				return True
			try:
				f = float(v)
				return True
			except:
				return False
		
		numericCols = set( c for c in range(grid.GetNumberCols()) if all(isNumeric(grid.GetCellValue(r, c)) for r in range(grid.GetNumberRows())) )
		for r in range(grid.GetNumberRows()):
			for c in range(grid.GetNumberCols()):
				v = grid.GetCellValue( r, c )
				if not v:
					continue
				aHoriz, aVert = grid.GetCellAlignment(r, c)
				if c in numericCols:
					aHoriz = wx.ALIGN_RIGHT
				self.set( r+rowLabel, c+colLabel, v, mapHorizontal.get(aHoriz, self.alignLeft) | mapVertical.get(aVert, self.alignTop) )
			
		numCols, numRows = self.getNumberCols(), self.getNumberRows()
		if horizontalGridlines:
			if rowLabel > 0:
				self.hLine( 1, 0, numCols, True )
			for r in range(rowLabel, grid.GetNumberRows()+1):
				self.hLine( r+rowLabel, 0, numCols )
		if verticalGridlines:
			self.vLine( 0, 0, numRows )
			if colLabel > 0:
				self.hLine( 1, 0, numRows, True )
			for c in range(colLabel+1, grid.GetNumberCols()+1):
				self.hLine( c+colLabel, 0, numRows )
		
	def set( self, row, col, value, attr=attrDefault ):
		self.table += [[] for i in range(max(0, row+1 - len(self.table)))]
		self.table[row] += [('', self.attrDefault) for i in range(max(0, col+1 - len(self.table[row])))]
		self.table[row][col] = (value, attr)
		return row, col
		
	def vLine( self, col, rowStart, rowEnd, thick = False ):
		# Drawn on the left of the col.
		self.vLines.append( (col, rowStart, rowEnd, thick) )
		
	def hLine( self, row, colStart, colEnd, thick = False ):
		# Drawn on the top of the row.
		self.hLines.append( (row, colStart, colEnd, thick) )
		
	def getNumberCols( self ):
		return max(len(r) for r in self.table)
		
	def getNumberRows( self ):
		return len(self.table)
		
	def getFonts( self, fontSize ):
		font = wx.Font( wx.Size(0,fontSize), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )
		fontBold = wx.Font( wx.Size(0,fontSize), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD )
		return font, fontBold
		
	def getCellBorder( self, fontSize ):
		return max(1, fontSize // 5) if self.cellBorder else 0
		
	def getSize( self, dc, fontSize ):
		font, fontBold = self.getFonts( fontSize )
		cellBorderX2 = self.getCellBorder( fontSize ) * 2
		self.colWidths = [0] * self.getNumberCols()
		self.rowHeights = [0] * self.getNumberRows()
		for row, r in enumerate(self.table):
			for col, (value, attr) in enumerate(r):
				dc.SetFont( fontBold if attr&self.bold else font )
				vWidth, vHeight = dc.GetMultiLineTextExtent(value)
				self.colWidths[col] = max(self.colWidths[col], vWidth + cellBorderX2)
				self.rowHeights[row] = max(self.rowHeights[row], vHeight + cellBorderX2)
		return sum( self.colWidths ), sum( self.rowHeights )
	
	def drawTextToFit( self, dc, text, x, y, width, height, attr, font=None ):
		if font and font != dc.GetFont():
			dc.SetFont( font )
		fontSize = dc.GetFont().GetPixelSize()[1]
		cellBorder = self.getCellBorder( fontSize )
		tWidth, tHeight = dc.GetMultiLineTextExtent(text)
		lineHeight = dc.GetTextExtent( 'PpJj' )[1]
		xLeft = x + cellBorder
		xRight = x + width - cellBorder
		
		if attr&self.alignMiddle:
			yTop = y + (height - tHeight) // 2
		elif attr&self.alignBottom:
			yTop = y + height - cellBorder - tHeight
		else:
			yTop = y + cellBorder
		
		for line in text.split( '\n' ):
			if attr & self.alignRight:
				dc.DrawText( line, xRight - dc.GetTextExtent(line)[0], yTop )
			elif attr & self.alignLeft:
				dc.DrawText( line, xLeft, yTop )
			else:
				dc.DrawText( line, x + (width - dc.GetTextExtent(line)[0]) // 2, yTop )
			yTop += lineHeight
			
	def setPen( self, dc, thick = False ):
		if not self.penThin:
			self.penThin = wx.Pen( wx.BLACK, 1, wx.SOLID )
			fontheight = dc.GetFont().GetPixelSize()[1]
			cellBorder = self.getCellBorder( fontheight )
			width = cellBorder / 2
			self.penThick = wx.Pen( wx.BLACK, width, wx.SOLID )
		newPen = self.penThick if thick else self.penThin
		if newPen != dc.GetPen():
			dc.SetPen( newPen )
	
	def drawToFitDC( self, dc, x, y, width, height ):
		self.penThin = None
		self.penThick = None
		
		fontSizeLeft, fontSizeRight = 2, 512
		for i in range(20):
			fontSize = (fontSizeLeft + fontSizeRight) // 2
			tWidth, tHeight = self.getSize( dc, fontSize )
			if tWidth < width and tHeight < height:
				fontSizeLeft = fontSize
			else:
				fontSizeRight = fontSize
			if fontSizeLeft == fontSizeRight:
				break
		
		fontSize = fontSizeLeft
		tWidth, tHeight = self.getSize( dc, fontSize )
		self.width, self.height = tWidth, tHeight
		
		# Align the entire table in the space.
		if self.alignHorizontal == self.alignCentre:
			x += (width - tWidth) // 2
		elif self.alignHorizontal == self.alignRight:
			x += width - tWidth

		if self.alignVertical == self.alignCentre:
			y += (height - tHeight) // 2
		elif self.alignVertical == self.alignBottom:
			y += height - tHeight
			
		self.x = x
		self.y = y

		font, fontBold = self.getFonts( fontSize )
		yTop = y
		for row, r in enumerate(self.table):
			xLeft = x
			for col, (value, attr) in enumerate(r):
				self.drawTextToFit( dc, value, xLeft, yTop, self.colWidths[col], self.rowHeights[row], attr, fontBold if attr&self.bold else font )
				xLeft += self.colWidths[col]
			yTop += self.rowHeights[row]
		
		# Draw the horizontal and vertical lines.
		# Lines are drawn on the left/top of the col/row.
		rowHeightSum = [y]
		for h in self.rowHeights:
			rowHeightSum.append( rowHeightSum[-1] + h )
		for i in range(50):
			rowHeightSum.append( rowHeightSum[-1] + rowHeightSum[-1] - rowHeightSum[-2] )
		
		colWidthSum = [x]
		for w in self.colWidths:
			colWidthSum.append( colWidthSum[-1] + w )
		
		curThick = None
		for col, rowStart, rowEnd, thick in self.vLines:
			if curThick != thick:
				self.setPen( dc, thick )
				curThick = thick
			colWidthSum[col]
			rowHeightSum[rowStart]
			colWidthSum[col]
			rowHeightSum[rowEnd]
			dc.DrawLine( colWidthSum[col], rowHeightSum[rowStart], colWidthSum[col], rowHeightSum[rowEnd] )
	
		curThick = None
		for row, colStart, colEnd, thick in self.hLines:
			if curThick != thick:
				self.setPen( dc, thick )
				curThick = thick
			dc.DrawLine( colWidthSum[colStart], rowHeightSum[row], colWidthSum[colEnd], rowHeightSum[row] )

	def toExcel( self, wx, rowStart=0, colStart=0 ):
		pass
	
	def toPDF( self, pdf, x, y, width, height ):
		pass
	
	def toHtml( self, html, attrs={} ):
		topBorder = set()
		bottomBorder = set()
		leftBorder = set()
		rightBorder = set()
		
		numberRows, numberCols = self.getNumberRows(), self.getNumberCols()
		for row, colStart, colEnd, thick in self.hLines:
			if row < numberRows:
				for col in range(colStart, colEnd):
					topBorder.add( (row, col) )
			else:
				for col in range(colStart, colEnd):
					bottomBorder.add( (numberRows-1, col) )
		
		for col, rowStart, rowEnd, think in self.vLines:
			if col < numberCols:
				for row in range(rowStart, rowEnd):
					leftBorder.add( (row, col) )
			else:
				for row in range(rowStart, rowEnd):
					rightBorder.add( (row, numberCols-1) )
		
		with tag( html, 'table', attrs ):
			with tag( html, 'tbody' ):
				for row, r in enumerate(self.table):
					with tag( html, 'tr' ):
						for col in range(numberCols):
							value, attr = r[col] if col < len(r) else ('', 0)
							value = '{}'.format(value)
							classDef = []
							if (row, col) in topBorder:
								classDef.append('topBorder')
							if (row, col) in bottomBorder:
								classDef.append('bottomBorder')
							if (row, col) in leftBorder:
								classDef.append('leftBorder')
							if (row, col) in rightBorder:
								classDef.append('rightBorder')
							if (attr & self.alignRight) and value:
								classDef.append('rightAlign')						
							attrs = {'class': ' '.join(classDef)} if classDef else {}
							with tag( html, 'td', attrs ):
								if (attr & self.bold) and value:
									with tag( html, 'strong' ):
										html.write( html.escape(value) )
								else:
									html.write( html.escape(value) )

def getTitleGrowTable( includeApprovedBy = True ):
	race = Model.race
	scoreSheet = Utils.getMainWin()
	gt = GrowTable(alignHorizontal=GrowTable.alignLeft, alignVertical=GrowTable.alignTop, cellBorder=False)
	titleAttr = GrowTable.bold | GrowTable.alignLeft
	rowCur = 0
	rowCur = gt.set( rowCur, 0, race.name, titleAttr )[0] + 1
	rowCur = gt.set( rowCur, 0, race.category, titleAttr )[0] + 1
	rowCur = gt.set( rowCur, 0, '{} Laps, {} Sprints, {} km'.format(race.laps, race.getNumSprints(), race.getDistance()), titleAttr )[0] + 1
	rowCur = gt.set( rowCur, 0, race.date.strftime('%Y-%m-%d'), titleAttr )[0] + 1
	
	if race.communique:
		rowCur = gt.set( rowCur, 0, 'Communiqu\u00E9: {}'.format(race.communique), GrowTable.alignRight )[0] + 1
	if includeApprovedBy:
		rowCur = gt.set( rowCur, 0, 'Approved by:________', GrowTable.alignRight )[0] + 1
	return gt

def ToPrintout( dc, grid ):
	race = Model.race
	rankSummary = Utils.getMainWin().rankSummary
	rankDetails = Utils.getMainWin().rankDetails
	
	#---------------------------------------------------------------------------------------
	# Format on the page.
	(widthPix, heightPix) = dc.GetSizeTuple()
	
	# Get a reasonable border.
	borderPix = max(widthPix, heightPix) / 25
	
	widthFieldPix = widthPix - borderPix * 2
	heightFieldPix = heightPix - borderPix * 2
	
	xPix = borderPix
	yPix = borderPix

	# Race Information
	xLeft = xPix
	yTop = yPix
	
	gt = getTitleGrowTable()
	
	# Draw the title
	titleHeight = heightFieldPix * 0.15
	
	image = wx.Image( os.path.join(Utils.getImageFolder(), 'Sprint1.png'), wx.BITMAP_TYPE_PNG )
	imageWidth, imageHeight = image.GetWidth(), image.GetHeight()
	imageScale = float(titleHeight) / float(imageHeight)
	newImageWidth, newImageHeight = int(imageWidth * imageScale), int(imageHeight * imageScale)
	image.Rescale( newImageWidth, newImageHeight, wx.IMAGE_QUALITY_HIGH )
	dc.DrawBitmap( wx.BitmapFromImage(image), xLeft, yTop )
	del image
	newImageWidth += titleHeight / 10
	
	gt.drawToFitDC( dc, xLeft + newImageWidth, yTop, widthFieldPix - newImageWidth, titleHeight )
	yTop += titleHeight * 1.20
	
	gt = getBodyGrowTable()
	gt.drawToFitDC( dc, xLeft + newImageWidth, yTop, widthFieldPix - newImageWidth, titleHeight )
	
	# Add a timestamp footer.
	fontSize = heightPix//85
	font = wx.Font( wx.Size(0,fontSize), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )
	dc.SetFont( font )
	text = 'Generated {}'.format( datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') )
	footerTop = heightPix - borderPix + fontSize/2
	dc.DrawText( text, widthPix - borderPix - dc.GetTextExtent(text)[0], footerTop )
	
	# Add branding
	text = 'Powered by PointsRaceMgr'
	dc.DrawText( text, borderPix, footerTop )

def ToHtml( html ):
	for i, (title, report) in enumerate((('Results', Utils.getMainWin().rankSummary), ('Details', Utils.getMainWin().rankDetails), )):
		if i:
			html.write( '<br/><hr/><br/>' )
		report.refresh()
		ExportGrid(title, report.grid).toHtml( html )
	
	# html.write( '<br/><hr/><br/>' )
	# Utils.getMainWin().commentary.refresh()
	# html.write('<span id="idRaceName">Commentary</span>')
	# Utils.getMainWin().commentary.toHtml(html)
	
def ToExcel( wb ):
	formats = ExportGrid.getExcelFormatsXLSX( wb )
	for title, report in (('Results', Utils.getMainWin().rankSummary), ('Details', Utils.getMainWin().rankDetails), ):
		sheetCur = wb.add_worksheet( title )
		report.refresh()
		ExportGrid(title, report.grid).toExcelSheet( sheetCur, formats )

