
import wx
import xlwt
import Utils
import Model
import RaceAnimation
from ReadSignOnSheet import Fields, IgnoreFields

#---------------------------------------------------------------------------

class ExportGrid( object ):
	def __init__( self, title = '', colnames = [], data = [] ):
		self.title = title
		self.colnames = colnames
		self.data = data
		self.leftJustifyCols = set()
	
	def _getFont( self, pointSize = 28, bold = False ):
		return wx.Font( pointSize, wx.FONTFAMILY_SWISS, wx.NORMAL,
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
			mid = int((left + right) / 2)
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
		
		# Draw the title.
		font = self._getFontToFit( widthFieldPix, int(heightFieldPix*0.10), lambda font: dc.GetMultiLineTextExtent(self.title, font)[:-1], True )
		dc.SetFont( font )
		self._drawMultiLineText( dc, self.title, xPix, yPix )
		wText, hText, lineHeightText = dc.GetMultiLineTextExtent( self.title, font )
		yPix += hText + lineHeightText/4
		
		heightFieldPix = heightPix - yPix - borderPix
		
		# Draw the table.
		font = self._getFontToFit( widthFieldPix, heightFieldPix, lambda font: self._getDataSizeTuple(dc, font) )
		dc.SetFont( font )
		wSpace, hSpace, lh = dc.GetMultiLineTextExtent( '    ', font )
		
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
					dc.DrawLine( borderPix, yLine + r * lh, widthPix - borderPix, yLine + r * lh )
			for v in self.data[col]:
				vStr = str(v)
				w, h, lh = dc.GetMultiLineTextExtent( vStr, font )
				if col in self.leftJustifyCols:
					self._drawMultiLineText( dc, vStr, xPix, yPix )					# left justify
				else:
					self._drawMultiLineText( dc, vStr, xPix + colWidth - w, yPix )	# right justify
				yPix += lh
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
	
	def setResultsOneListRiderTimes( self, catName = 'All' ):
		''' Add the lap times to the setResultsOneList output. '''
		self.setResultsOneList( catName )
		return
					
	def setResultsOneList( self, catName ):
		self.data = []
		self.colnames = []
			
		with Model.LockRace() as race:
			self.title = 'Race: '+ race.name + '\n' + Utils.formatDate(race.date) + '\nCategory: ' + catName
			results = RaceAnimation.GetAnimationData( catName, True )
			category = race.categories.get(catName, None)
			if not results:
				return
			if category:
				results = dict( (num, info) for num, info in results.iteritems() if race.getCategory(num) == category )

		infoFields = ['License', 'LastName', 'FirstName', 'Category', 'Team']
		infoFieldsPresent = set()
		
		# Figure out which additional fields are used.
		for num, data in results.iteritems():
			for f in infoFields:
				if f in data:
					infoFieldsPresent.add( f )
		
		infoFields = [f for f in infoFields if f in infoFieldsPresent]
		
		#  num,  status,   laps,   lastTime,    raceCat,    lapTimes,   otherinfo
		#   0       1        2        3            4           5           6, 7, 8...
		finishInfo = []
		for num, info in results.iteritems():
			e = [num, info['status'], len(info['lapTimes']),
				 info['lastTime'], info['raceCat'], info['lapTimes']]
			e += [info.get(f, '') for f in infoFields]
			finishInfo.append( e )
		
		statusSort = { 'Finisher':0, 'PUL':1, 'OTL':5, 'DNF':2, 'DQ':3, 'DNS':4, 'NP':5 }
		# sort by status, laps, lastTime, 
		finishInfo.sort( key = lambda x: (statusSort.get(x[1],100), -x[2], x[3], x[0]) )
		
		leaderLaps = finishInfo[0][2]
		leaderTime = finishInfo[0][3]
		
		position	= []
		number		= []
		finishTime	= []
		gap			= []
		infoData	= [[] for i in xrange(len(infoFields))]
		lapTimes	= [[] for i in xrange(finishInfo[0][2])]
		
		self.colnames = ['Pos', 'Bib'] + infoFields + ['Time', 'Gap'] + ['Lap %d' % lap for lap in xrange(1,finishInfo[0][2])]
		if not results:
			return
		pos = 0
		for info in finishInfo:
			#  num,  status,   laps,   lastTime,    raceCat,    lapTimes,   otherinfo
			#   0       1        2        3            4           5           6, 7, 8...
			finisher = (info[1] == 'Finisher')
			
			pos += 1
			position.append( pos if finisher else info[1] )
			
			number.append( info[0] )
			finishTime.append( Utils.formatTime(info[3]) if finisher else ' ' )
			
			gapEntry = ' '
			if finisher:
				if info[2] == leaderLaps:
					if info[3] != leaderTime:
						gapEntry = Utils.SecondsToMMSS(info[3] - leaderTime)
						if gapEntry[0] == '0':
							gapEntry = gapEntry[1:]
				elif info[3] > leaderTime:
					lapsDown = leaderLaps - info[2]
					gapEntry = '%d %s' % (lapsDown, 'lap' if lapsDown == 1 else 'laps')
			gap.append( gapEntry )
			
			for p, t in enumerate(Utils.formatTimeCompressed(info[5][i] - info[5][i-1]) for i in xrange(1, len(info[5]))):
				lapTimes[p].append( t )
			
			for i, j in enumerate(xrange(6, 6 + len(infoFields))):
				try:
					rf = info[j]
				except IndexError:
					rf = ''
				if rf is None:
					rf = ' '
				infoData[i].append( rf )

		self.data = [position, number] + infoData + [finishTime, gap]
		for lt in lapTimes:
			self.data.append( lt )
		self.leftJustifyCols = set( xrange(2, 2+len(infoFields)) )
			
if __name__ == '__main__':
	pass
