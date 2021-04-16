import wx
import Utils
import Model
from Competitions import SetDefaultData, DoRandomSimulation
from Utils import WriteCell
from Events import GetFont, GetBoldFont
import bisect
import pickle
from collections import defaultdict

class Graph( wx.Control ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id )
		
		self.model = None
		self.selectedRider = None
		self.SetDoubleBuffered( True )
		
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt: None)
		
		self.rectRiders = []
		self.colX = []

	def OnSize( self, evt ):
		self.Refresh()
	
	def OnLeftDown( self, evt ):
		self.selectedRider = None
		wx.CallAfter( self.Refresh )
	
	def OnLeftUp( self, evt ):
		if not self.colX:
			return
		
		x, y = evt.GetX(), evt.GetY()
		i = max( 0, bisect.bisect_left(self.colX, x, hi=len(self.colX)-1) - 1 )
		if self.colX[i] <= x < self.colX[i+1]:
			for rect, rider in self.rectRiders[i]:
				if rect.Contains(x, y):
					if self.selectedRider != rider:
						self.selectedRider = rider;
						wx.CallAfter( self.Refresh )
					return
				if rect.GetY() > y:
					return
	
	def OnPaint(self, evt):
		dc = wx.PaintDC(self)
		self.Draw(dc)
	
	def Print( self, dc ):
		self.Draw( dc, True )
	
	def Draw( self, dc, toPrinter=False ):
		width, height = dc.GetSize()
		if not width or not height:
			width, height = self.GetClientSize()
		
		#---------------------------------------------------------------------------
		# Set up a memory dc to draw into.
		dcIn = dc
		bitmap = wx.Bitmap( width, height )
		dcMemory = wx.MemoryDC()
		dcMemory.SelectObject( bitmap )
		dc = wx.GCDC( dcMemory )		# Use a graphics context dc to get anti-aliased drawing.
		
		#---------------------------------------------------------------------------
		backgroundColour = wx.WHITE
		dc.SetBackground( wx.WHITE_BRUSH )
		dc.Clear()
			
		model = self.model or Model.model
		competition = model.competition
		state = competition.state
		
		def getFullName( rider, v ):
			if not rider:
				return ''
			name = rider.bib_full_name
			if 'rank' in v:
				name += ' \u2192 {}'.format( v['rank'] )
			return name
			
		def riderName( id ):
			try:
				return state.labels[id].bib_full_name
			except KeyError:
				return ''
		
		# Set the list of qualifiers.  Double-space the rows.
		grid = [[{'title':'Qualifiers'}, {}]]
		for i in range(competition.starters):
			grid[0].append( {'rider':state.labels.get('N{}'.format(i+1),None)} )
			grid[0].append( {} )
		
		# Add the event results.
		for tournamentCount, tournament in enumerate(competition.tournaments):
			if tournamentCount == 0:
				rowStart = 0
				col = 1
			else:
				rowStart = len(grid[1])
				col = 2
				
			while len(grid) <= col:
				grid.append( [] )
			
			if tournament.name:
				grid[col].extend( [{}] * (rowStart - len(grid[col])) )
				grid[col].extend( [{'title': 'Tournament "{}"'.format(tournament.name)}, {}] )
				rowStart += 2
			for s, system in enumerate(tournament.systems):
			
				while len(grid) <= col:
					grid.append( [] )
					
				grid[col].extend( [{}] * (rowStart - len(grid[col])) )
				grid[col].extend( [{'title':system.name}, {}] )
				for event in system.events:
					if 'Repechages' in system.name and event.i == 0:
						grid[col].extend( [{}] * (len(grid[col-1]) - len(grid[col])) )
					elif system.name.startswith('Small'):
						grid[col].extend( [{}] * (13 if 'XCE' in competition.name or 'Keirin' in competition.name else 8) )
					elif '5-8' in system.name:
						grid[col].extend( [{}] * 12 )
					elif 'XCE' not in competition.name and len(event.composition) == 4: # Offset the 4-ways to another column (if not XCE)
						rowLast = len(grid[col])
						if 'Repechages' in system.name:
							rowLast -= (4+1)
						col += 1
						while len(grid) <= col:
							grid.append( [] )
						grid[col].extend( [{}] * (rowLast - len(grid[col])) )
					elif '5-6 Final' in system.name:
						grid[col].extend( [{}] * 7 )
					
					# If the event has happend, sequence by results.
					# If the event has not happened, sequence by qualifying time.
					if not event.finishRiderRank:
						eventComposition = sorted( event.composition, key = lambda c: state.labels.get(c,state.OpenRider).qualifyingTime )
					else:
						eventComposition = sorted( event.composition, key = lambda c: event.finishRiderRank.get(state.labels.get(c,state.OpenRider),999) )
					for p, c in enumerate(eventComposition):
						rider = state.labels.get(c,state.OpenRider)
						values = {'rider':rider}
						if rider in event.finishRiderPlace:
							values['rank'] = event.finishRiderPlace[rider]
						if len(event.composition) != 4 and values.get('rank',None) == 1:
							values['winner'] = True
							
						grid[col].append( values )
					grid[col].append( {} )
				col += 1
	
		results, dnfs, dqs = model.competition.getResults()
		grid.append( [{'title':'Final Classification'}, {}] )
		for i, (classification, rider) in enumerate(results):
			values = {'classification':classification}
			if rider:
				values['rider'] = rider
			grid[-1].append( values )
			grid[-1].append( {} )
	
		if toPrinter:
			for c, col in enumerate(grid):
				if c == 0:
					col.insert( 0, {'title':model.competition_name} )
				elif c == 1:
					col.insert( 0, {'title':model.date.strftime('%Y-%m-%d')} )
				else:
					col.insert( 0, {} )
				col.insert( 1, {} )
	
		inCR = defaultdict( list )
		for c, col in enumerate(grid):
			for r, v in enumerate(col):
				if 'rider' in v and v['rider'] and v['rider'].bib:
					inCR[v['rider']].append( (c, r) )
					
		def getToCR( cFrom, rider ):
			try:
				for c, r in inCR[rider]:
					if c > cFrom:
						return c, r
			except KeyError:
				pass
				
			return None, None
	
		# Binary search for the right font size.
		fontSize = 0.4 * height / float(model.competition.starters)
		fontSizeMin, fontSizeMax = 0.0, fontSize * 3
		for ff in range(10):
			fontSize = int((fontSizeMax + fontSizeMin) / 2.0)
			
			font = wx.Font((0,fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
			boldFont = wx.Font((0,fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
			dc.SetFont( font )
			textHeight = dc.GetTextExtent( 'My What a Nice String!' )[1]
			rowHeight = textHeight * 1.15
			
			colWidths = [0] * len(grid)
			for c, col in enumerate(grid):
				for v in col:
					if 'title' in v:
						dc.SetFont( boldFont )
						colWidths[c] = max( colWidths[c], dc.GetFullTextExtent(v['title'])[0] )
						dc.SetFont( font )
					elif 'name' in v:
						colWidths[c] = max( colWidths[c], dc.GetFullTextExtent(v['name'] + '00. ')[0] )
					if v.get('rider',None):
						colWidths[c] = max( colWidths[c], dc.GetFullTextExtent(v['rider'].bib_full_name + '00. ')[0] )
			
			border = width / 15 if toPrinter else 8
			xLeft = border
			yTop = border
			colX = [xLeft]
			colSpace = rowHeight * 5
			for c, w in enumerate(colWidths):
				colX.append( colX[-1] + w + colSpace )

			rows = max( len(col) for col in grid )
			xMax, yMax = colX[len(grid)] - colSpace, rows * rowHeight
			if xMax > width - border or yMax > height - border:
				fontSizeMax = fontSize
			else:
				if fontSizeMax - fontSizeMin < 1.001:
					break
				fontSizeMin = fontSize
		
		thinLine = max( 1, int(fontSize / 10.0) )
		thickLine = max( 4, int(fontSize / 3.0) )
		
		whiteFont = wx.Font((0,fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		greenPen = wx.Pen(wx.Colour(0,200,0), thinLine)
		greenPenThick = wx.Pen(wx.Colour(0,200,0), thickLine)
		redPen = wx.Pen( wx.RED, thinLine )
		redPenThick = wx.Pen(wx.Colour(255,0,0), thickLine)
		blackPen = wx.Pen(wx.BLACK, thinLine)
		bluePen = wx.Pen(wx.Colour(0,0,200), thinLine)
		whitePen = wx.Pen( wx.WHITE, thinLine )
		blackBrush = wx.BLACK_BRUSH
		whiteBrush = wx.WHITE_BRUSH
		
		dc.SetBrush( whiteBrush )
		
		topSpace = 0
		if toPrinter:
			titleFontSize = border / 4
			titleFont = wx.Font((0,titleFontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
			dc.SetFont( titleFont )
			model = Model.model
			cNum = model.communique_number.get(GraphDraw.phase, '')
			dc.DrawText( 'Communiqu\u00E9: {}  Sprint Summary for {}: {}'.format(cNum, model.competition_name, model.category),
				border, border - 2*titleFontSize )
			
		dc.SetFont( font )
		
		controlRatio = 0.78
		def drawSCurve( x1, y1, x2, y2 ):
			cx1, cy1 = x2 - (x2 - x1)*controlRatio, y1
			cx2, cy2 = x1 + (x2 - x1)*controlRatio, y2
			dc.DrawSpline( [wx.Point(int(x1),int(y1)), wx.Point(int(cx1),int(cy1)), wx.Point(int(cx2),int(cy2)), wx.Point(int(x2),int(y2))] )
		
		# Draw the connections.
		for c, col in enumerate(grid):
			for r, v in enumerate(col):
				if 'rider' not in v:
					continue
				rider = v['rider']
				x1 = colX[c] + dc.GetFullTextExtent(getFullName(rider, v))[0]
				y1 = yTop + r * rowHeight + rowHeight / 2
				
				cTo, rTo = getToCR(c, rider)
				if cTo is None:
					continue
				
				x2 = colX[cTo]
				y2 = yTop + rTo * rowHeight + rowHeight / 2
				
				if 'winner' in v:
					if rider == self.selectedRider:
						dc.SetPen( greenPenThick if v['winner'] else redPenThick )
					else:
						dc.SetPen( greenPen if v['winner'] else redPen )
				else:
					dc.SetPen( greenPenThick if rider == self.selectedRider else greenPen )
				
				drawSCurve( x1, y1, x2, y2 )
			
		# Create a map of the last event for all riders.
		riderLastEvent = {}
		for cFrom in range(len(grid)-2, -1, -1):
			for rFrom, vFrom in enumerate(grid[cFrom]):
				try:
					rider = state.labels[vFrom['rider']]
				except KeyError:
					continue
				if rider not in riderLastEvent:
					riderLastEvent[rider] = (cFrom, rFrom)
						
		def getIsBlocked( cFrom, rFrom, cTo, rTo ):
			''' Check if there is an entry in the rectangle between cFrom, rFrom and cTo, rTo. '''
			for c in range(cFrom+1, cTo):
				for r in range( min(rFrom, rTo), min(max(rFrom, rTo), len(grid[c])) ):
					if grid[c][r]:
						return True
			return False
			
		# Draw the connections to the results.
		colAvoidCount = [6 if competition.starters == 24 else 1] * len(grid)
		cTo = len(grid) - 1
		for rTo, v in enumerate(grid[-1]):
			try:
				pos = v['classification']
			except KeyError:
				continue
			rider = v.get('rider', None)
			if rider not in riderLastEvent:
				continue
				
			cFrom, rFrom = riderLastEvent[rider]
			
			dc.SetPen( greenPenThick if rider == self.selectedRider else greenPen )
				
			x1 = colX[cFrom] + dc.GetFullTextExtent(getFullName(rider,v))[0]
			y1 = yTop + rFrom * rowHeight + rowHeight / 2
			x2 = colX[cTo]
			y2 = yTop + rTo * rowHeight + rowHeight / 2
			
			if competition.starters == 18 or not getIsBlocked(cFrom, rFrom, cTo, rTo):
				drawSCurve( x1, y1, x2, y2 )
			else:
				maxRowBetween = max( len(grid[c]) for c in range(cFrom+1, cTo) )
				xa = colX[cFrom+1]
				rAvoid = maxRowBetween + colAvoidCount[cFrom]
				colAvoidCount[cFrom] += 2
				ya = yTop + rAvoid * rowHeight
				drawSCurve( x1, y1, xa, ya )
				for cNext in range(cFrom+2, cTo+1):
					if not getIsBlocked(cNext, rAvoid, cTo, rTo):
						break
				xb = colX[min(cNext+1, len(grid)-1)] - colSpace
				yb = ya
				dc.DrawLine( xa, ya, xb, yb )
				drawSCurve( xb, yb, x2, y2 )
		
		def drawName( name, x, y, selected, pos = -1 ):
			if not name:
				return ''
			if pos > 0:
				name = '{:02d}. {}'.format( pos, name )
			dc.SetFont( whiteFont )
			xborder = fontSize / 2
			yborder = fontSize / 10
			width, height = dc.GetFullTextExtent(name)[:2]
			if selected:
				dc.SetBrush( blackBrush )
				dc.SetPen( blackPen )
				dc.DrawRoundedRectangle( int(x-xborder), int(y-yborder), int(width + xborder*2), int(height + yborder*2), int((height + yborder*2) / 4) )
				dc.SetTextForeground( wx.WHITE )
				if pos > 0 and name.startswith('0'):
					name = name[1:]
					x += dc.GetFullTextExtent('0')[0]
				dc.DrawText( name, int(x), int(y) )
				dc.SetTextForeground( wx.BLACK )
				dc.SetFont( font )
			else:
				if pos > 0 and name.startswith('0'):
					name = name[1:]
					x += dc.GetFullTextExtent('0')[0]
				dc.SetBrush( wx.WHITE_BRUSH )
				dc.SetPen( wx.TRANSPARENT_PEN )
				dc.DrawRoundedRectangle( int(x-xborder), int(y-yborder), int(width + xborder*2), int(height + yborder*2), int((height + yborder*2) / 4) )
				dc.DrawText( name, int(x), int(y) )
			return name
		
		# Draw the node names.
		self.rectRiders = []
		for c, col in enumerate(grid):
			colRects = []
			for r, v in enumerate(col):
				x = colX[c]
				y = yTop + r * rowHeight
				if 'title' in v:
					dc.SetFont( boldFont )
					dc.DrawText( v['title'], int(x), int(y) )
					dc.SetFont( font )
				elif 'name' in v:
					try:
						pos = v['classification']
					except KeyError:
						pos = -1
					rider = v.get('rider', None)
					if rider:
						name = drawName( getFullName(rider, v), x, y, rider == self.selectedRider, pos )
						colRects.append( (wx.Rect(int(x), int(y), dc.GetFullTextExtent(name)[0], int(rowHeight)), rider) )
				elif 'rider' in v:
					rider = v['rider']
					if rider:
						name = getFullName( rider, v )
						if 'classification' in v:
							pos = u'{}'.format(v['classification'])
							if pos.isdigit():
								name = u'{}.  {}'.format(pos, name)
							else:
								name = u'{}  {}'.format(pos, name)
						drawName( name, x, y, rider == self.selectedRider )
						colRects.append( (wx.Rect(int(x), int(y), dc.GetFullTextExtent(name)[0], int(rowHeight)), rider) )
			self.rectRiders.append( colRects )
		self.colX = colX
		
		# Copy the bitmap into the original dc.
		dcIn.Blit( 0, 0, width, height, dcMemory, 0, 0 )
		dcMemory.SelectObject( wx.NullBitmap )

	def getImage( self, toPrinter = False ):
		bitmap = wx.Bitmap( 1366, 768 )
		mdc = wx.MemoryDC( bitmap )
		self.Draw( mdc, toPrinter )
		image = bitmap.ConvertToImage()
		mdc.SelectObject( wx.NullBitmap )
		return image

class GraphDraw( wx.Panel ):
	phase = 'Competition Summary'

	def __init__(self, parent):
		super().__init__( parent )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		self.title = wx.StaticText( self, wx.ID_ANY, '' )
		self.title.SetFont( GetBoldFont() )
		
		self.communiqueLabel = wx.StaticText( self, wx.ID_ANY, 'Communiqu\u00E9:' )
		self.communiqueLabel.SetFont( GetFont() )
		self.communiqueNumber = wx.TextCtrl( self, wx.ID_ANY, '', size=(64,-1) )
		self.communiqueNumber.SetFont( GetFont() )
		
		hs = wx.BoxSizer(wx.HORIZONTAL)
		hs.Add( self.title, 0, flag=wx.ALIGN_CENTRE_VERTICAL|wx.ALL, border = 4 )
		hs.Add( self.communiqueLabel, 0, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border = 4 )
		hs.Add( self.communiqueNumber, 0, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		vs.Add( hs, 0, flag=wx.ALL, border = 6 )
		
		vs.Add( wx.StaticText(self, label='Click on a name below to show the progress through the competition.'), flag=wx.LEFT, border = 8 )
		
		self.graph = Graph( self )
		vs.Add( self.graph, 1, flag=wx.ALL|wx.EXPAND, border = 6 )
		
		self.SetSizer( vs )

	def refresh( self ):
		model = Model.model
		self.title.SetLabel( '{}:{} - {} - Format: {}    '.format(
								model.competition_name,
								model.category,
								model.date.strftime('%Y-%m-%d'),
								model.competition.name,
							) )
		self.communiqueNumber.SetValue( model.communique_number.get(self.phase, u'') )
		self.GetSizer().Layout()
		self.Refresh()
		
	def getTitle( self ):
		title = 'Communiqu\u00E9: {}\n{}'.format(
					self.communiqueNumber.GetValue(),
					self.phase )
		return title
		
	def getImage( self ):
		return self.graph.getImage()
	
	def commit( self ):
		model = Model.model
		cn = self.communiqueNumber.GetValue()
		if cn != model.communique_number.get(self.phase, u''):
			model.communique_number[self.phase] = self.communiqueNumber.GetValue()
			model.setChanged()
		
#----------------------------------------------------------------------

class GraphDrawFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="Graph Test", size=(1000,800) )
		self.panel = GraphDraw( self )
		self.panel.refresh()
		self.Show()
 
	def getImage( self ):
		return self.panel.getImage()
		
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	#Model.model = SetDefaultData()
	#with open(r'Races\TestFinished.smr', 'rb') as fp:
	#	Model.model = pickle.load( fp )
	#Model.model = SetDefaultData('XCE 32')
	Model.model = SetDefaultData('World Cup')
	#Model.model = SetDefaultData('XCE Fewer than 18')
	#Model.model = SetDefaultData('XCE 36')
	#Model.model = SetDefaultData('Four Cross 64')
	#Model.model = SetDefaultData('Four Cross 32')
	#Model.model = SetDefaultData('Four Cross 16')
	#Model.model = SetDefaultData('XCE Fewer than 24')
	#Model.model = SetDefaultData('Keirin 21')
	#Model.model = SetDefaultData('Keirin 22-28')
	#Model.model = SetDefaultData('Keirin 29-42')
	#Model.model = SetDefaultData('Keirin 12-14')
	for i, r in enumerate(Model.model.riders):
		r.status = 'DNQ'
		if i > 12:
			break
	DoRandomSimulation()
	frame = GraphDrawFrame()
	app.MainLoop()
