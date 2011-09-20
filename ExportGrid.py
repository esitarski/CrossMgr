
import wx
import xlwt
import Utils
import Model
from ReadSignOnSheet import Fields

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
		race = Model.getRace()
		
		# Get the category start offset.
		category = race.categories.get( catName, None )
		startOffsetSecs = category.getStartOffsetSecs() if category is not None else 0.0
		
		raceLaps = race.getRaceLaps()
		entries = race.interpolateLap( raceLaps )
		entries = [e for e in entries if e.t > 0]
		entries.sort( key = lambda x : (x.num, x.t) )
		
		# Record the rider times and compensate for the category start offsets.
		riderTimes = {}
		for e in entries:
			riderTimes.setdefault( e.num, [] ).append( max(e.t - startOffsetSecs, 0.0) )

		positionCol = self.colnames.index('Position')
		bibCol      = self.colnames.index('Bib#')
		lapTimesCol = len(self.colnames)
		for row in xrange(len(self.data[0])):
			# Only print times for placed riders.
			try:
				p = int(self.data[positionCol][row])
			except (IndexError, ValueError):
				continue
			num = self.data[bibCol][row]
			for i, t in enumerate( riderTimes.get(int(num), []) ):
				self._setRC( row, lapTimesCol + i, Utils.formatTime(t) )

		self.colnames += ['Lap %d' % lap for lap in xrange(1,len(self.data)-lapTimesCol+1)]
				
	def setResults( self, catName ):
		race = Model.getRace()
		self.title = 'Race: '+ race.name + '\n' + Utils.formatDate(race.date) + '\nCategory: ' + catName
		self.colnames, results, dnf, dns, dq = race.getResults( catName )
		
		# Format the results.
		self.data = []
		pos = 1
		for col, d in enumerate(results):
			self.data.append( [str(e.num) + ' (' + str(row+pos) + ')' for row, e in enumerate(d)] )
			pos += len(d)
		
		if dnf:
			self.colnames.append( 'DNF' )
			self.data.append( [str(e[0]) for e in dnf] )
		
		if dns:
			self.colnames.append( 'DNS' )
			self.data.append( [str(e[0]) for e in dns] )
		
		if dq:
			self.colnames.append( 'NP' )
			self.data.append( [str(e[0]) for e in dq] )
	
	def setResultsOneList( self, catName ):
		race = Model.getRace()
		self.title = 'Race: '+ race.name + '\n' + Utils.formatDate(race.date) + '\nCategory: ' + catName
		
		colnames, results, dnf, dns, dq = race.getResults( catName )

		self.data	= []
		self.colnames = []
		
		if not any([colnames, results, dnf, dns, dq]):
			return
		
		position	= []
		number		= []
		laps		= []
		finishTime	= []
		gap			= []
		notes		= []
		
		leaderLaps = int(colnames[0])
		leaderTime = results[0][0].t

		if results:
			pos = 1
			for col, c in enumerate(results):
				lapsCompleted = int(colnames[col])
				number.extend( e.num for e in c )
				notes.extend( 'OTL' if race[e.num].isPulled() else ' ' for e in c )
				position.extend( p for p in xrange(pos, pos+len(c)) )
				
				# Don't show riders a lap down unless they really were lapped by their race leader.
				laps.extend( lapsCompleted if col == 0 or e.t > leaderTime else leaderLaps + lapsCompleted for e in c )
				
				finishTime.extend( Utils.formatTime(e.t) for e in c )
				pos += len(c)
			if finishTime:
				leaderTime = Utils.StrToSeconds( finishTime[0] )
				leaderLaps = int(laps[0])
				gap.append( ' ' )
				for row in xrange(1, len(finishTime)):
					riderLaps = int(laps[row])
					if riderLaps != leaderLaps:
						break
					riderTime = Utils.StrToSeconds( finishTime[row] )
					gap.append( Utils.SecondsToMMSS(riderTime - leaderTime) )
	
		if dnf:
			number.extend( str(n) for n, t in dnf )
			position.extend( ['DNF'] * len(dnf) )

		if dns:
			number.extend( str(n) for n, t in dns )
			position.extend( ['DNS'] * len(dns) )

		if dq:
			number.extend( str(n) for n, t in dq )
			position.extend( ['NP'] * len(dq) )

		# Get linked information.
		linkedCol = []
		linkedInfo = []
		try:
			info = race.excelLink.read()
			for f in Fields[1:]:
				if not race.excelLink.hasField(f):
					continue
				linkedCol.append( f )
				d = []
				for n in number:
					try:
						d.append( info[n][f] )
					except KeyError:
						d.append( ' ' )
				linkedInfo.append( d )
		except (AttributeError, IOError, ValueError):
			pass
		
		# Reformat the laps to show negative laps as Dn #
		# laps = [str(lap) if lap > 0 else 'Dn ' + str(-lap) for lap in laps]
		
		# Don't change these names without checking setResultsOneListRiderTimes!
		self.colnames = ['Position', 'Bib#', 'Laps', 'Finish Time', 'Gap', 'Note']
		self.data = [position, number, laps, finishTime, gap, notes]
		self.colnames[2:2] = linkedCol
		self.data[2:2] = linkedInfo
		self.leftJustifyCols = set( xrange(2, 2+len(linkedCol)) )

		# Remove the gap column if empty.
		if not gap:
			col = self.colnames.index('Gap')
			del self.colnames[col]
			del self.data[col]
			
		# Remove the notes column if empty.
		if not any( n != ' ' for n in notes ):
			col = self.colnames.index('Note')
			del self.colnames[col]
			del self.data[col]
			
	def toHTML( self, html ):
		pass

if __name__ == '__main__':
	pass
