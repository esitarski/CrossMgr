import Model
import Utils
import wx
import wx.grid		as gridlib
import re
import os
import bisect
from string import Template
import ColGrid
from FixCategories import FixCategories, SetCategory
from ExportGrid import ExportGrid

reNonDigits = re.compile( '[^0-9]' )

from ReadSignOnSheet import IgnoreFields
statusSortSeq = Model.Rider.statusSortSeq

class RiderResult( object ):
	def __init__( self, num, status, lastTime, lapTimes, raceTimes ):
		self.num		= num
		self.status		= status
		self.gap		= ''
		self.pos		= ''
		self.laps		= len(lapTimes)
		self.lastTime	= lastTime
		self.lapTimes	= lapTimes
		self.raceTimes	= raceTimes
		
def GetResults( catName = 'All', getExternalData = False ):
	with Model.LockRace() as race:
		if not race:
			return []
		
		# Get the number of race laps for each category.
		raceNumLaps = (race.numLaps or 1000)
		categoryWinningTime = {}
		for c, (times, nums) in race.getCategoryTimesNums().iteritems():
			if not times:
				continue
			# If the category num laps is specified, use that.
			if c.getNumLaps():
				categoryWinningTime[c] = times[c.getNumLaps()]
			else:
				# Otherwise, set the number of laps by the winner first after the race finish time.
				try:
					categoryWinningTime[c] = times[bisect.bisect_left( times, race.minutes * 60.0, hi=len(times)-1 )]
				except IndexError:
					categoryWinningTime[c] = race.minutes * 60.0
							
		if not categoryWinningTime:
			return []
			
		category = race.categories.get( catName, None )
		startOffset = category.getStartOffsetSecs() if category else 0.0
			
		riderResults = []
		for rider in race.riders.itervalues():
			riderCategory = race.getCategory( rider.num )
			if category and riderCategory != category:
				continue
			times = [e.t for e in rider.interpolate()]
			
			if times:
				times[0] = min(riderCategory.getStartOffsetSecs(), times[1])
				laps = bisect.bisect_left( times, categoryWinningTime[riderCategory], hi=len(times)-1 )
				times = times[:laps+1]
			else:
				laps = 0
			lastTime = rider.tStatus
			if not lastTime:
				if times:
					lastTime = times[-1]
					if category:
						lastTime = max( lastTime - startOffset, 0.0 )
				else:
					lastTime = 0.0
					
			riderResults.append( RiderResult(rider.num, rider.status, lastTime,
									[times[i] - times[i-1] for i in xrange(1, len(times))], times) )
		
		if not riderResults:
			return []
			
		riderResults.sort( key = lambda x: (statusSortSeq[x.status], -x.laps, x.lastTime) )

		# Get the linked external data.
		externalFields = []
		externalInfo = None
		if getExternalData:
			try:
				externalFields = race.excelLink.getFields()
				externalInfo = race.excelLink.read()
				for ignoreField in IgnoreFields:
					try:
						externalFields.remove( ignoreField )
					except ValueError:
						pass
			except:
				externalFields = []
				externalInfo = None
		
		# Add external data.
		# Add the position (or status, if not a Finisher).
		# Fill in the gap field (include laps down if appropriate).
		leader = riderResults[0]
		for pos, rr in enumerate(riderResults):
			for f in externalFields:
				try:
					setattr( rr, f, externalInfo[rr.num][f] )
				except KeyError:
					setattr( rr, f, '' )
		
			if rr.status != Model.Rider.Finisher:
				rr.pos = Model.Rider.statusNames[rr.status]
				continue
				
			rr.pos = str(pos+1)
			
			if rr.laps != leader.laps:
				if rr.lastTime > leader.lastTime:
					lapsDown = leader.laps - rr.laps
					rr.gap = '%d %s' % (lapsDown, 'laps' if lapsDown > 1 else 'lap')
			elif rr != leader:
				rr.gap = Utils.formatTimeCompressed( rr.lastTime - leader.lastTime )
		
		# Format the last time as a string.
		for rr in riderResults:
			if rr.lastTime:
				rr.lastTime = Utils.formatTimeCompressed( rr.lastTime )
			else:
				rr.lastTime = ''
		
		return riderResults
		
class Results( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		
		self.category = None
		
		self.rcInterp = set()
		self.numSelect = None
		self.isEmpty = True
		self.reSplit = re.compile( '[\[\]\+= ]+' )	# seperators for the fields.

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.search = wx.SearchCtrl(self, size=(80,-1), style=wx.TE_PROCESS_ENTER )
		# self.search.ShowCancelButton( True )
		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
		self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancelSearch, self.search)
		self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch, self.search)
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'Zoom-In-icon.png'), wx.BITMAP_TYPE_PNG )
		self.zoomInButton = wx.BitmapButton( self, wx.ID_ZOOM_IN, bitmap, style=wx.BU_EXACTFIT | wx.BU_AUTODRAW )
		self.Bind( wx.EVT_BUTTON, self.onZoomIn, self.zoomInButton )
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'Zoom-Out-icon.png'), wx.BITMAP_TYPE_PNG )
		self.zoomOutButton = wx.BitmapButton( self, wx.ID_ZOOM_OUT, bitmap, style=wx.BU_EXACTFIT | wx.BU_AUTODRAW )
		self.Bind( wx.EVT_BUTTON, self.onZoomOut, self.zoomOutButton )
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL, border=4 )
		self.hbs.Add( wx.StaticText(self, wx.ID_ANY, ' '), proportion=2 )
		self.hbs.Add( self.search, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomInButton, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.zoomOutButton, flag=wx.TOP | wx.BOTTOM | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, border=4 )

		self.whiteColour = wx.Colour( 255, 255, 255 )
		self.blackColour = wx.Colour( 0, 0, 0 )
		self.yellowColour = wx.Colour( 255, 255, 0 )
		self.greyColour = wx.Colour( 150, 150, 150 )
		
		self.grid = ColGrid.ColGrid( self )
		self.grid.SetRowLabelSize( 0 )
		self.grid.SetMargins( 0, 0 )
		self.grid.SetRightAlign( True )
		#self.grid.SetDoubleBuffered( True )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()
		
		self.Bind( wx.grid.EVT_GRID_SELECT_CELL, self.doNumSelect )
		self.Bind( wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.doNumDrilldown )
		self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doRightClick )
		
		bs = wx.BoxSizer(wx.VERTICAL)
		#bs.Add(self.hbs)
		#bs.Add(self.grid, 1, wx.GROW|wx.ALL, 5)
		
		bs.Add(self.hbs, 0, wx.EXPAND )
		bs.Add(self.grid, 1, wx.EXPAND|wx.GROW|wx.ALL, 5 )
		
		self.SetSizer(bs)
		bs.SetSizeHints(self)
		
	def OnSearch( self, event ):
		self.OnDoSearch()
		
	def OnCancelSearch( self, event ):
		self.search.SetValue( '' )
		
	def OnDoSearch( self, event = None ):
		wx.CallAfter( self.search.SetFocus )
		n = self.search.GetValue()
		if n:
			n = reNonDigits.sub( '', n )
			self.search.SetValue( n )
		if not n:
			n = None
		if n:
			self.numSelect = n
			if self.category and not self.category.matches( int(n) ):
				self.setCategoryAll()

			self.refresh()
			if Utils.isMainWin():
				Utils.getMainWin().setNumSelect( n )

	def onZoomOut( self, event ):
		self.grid.Zoom( False )
			
	def onZoomIn( self, event ):
		self.grid.Zoom( True )
		
	def doRightClick( self, event ):
		wx.CallAfter( self.search.SetFocus )

		self.doNumSelect( event )
		if self.numSelect is None:
			return
			
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				('RiderDetail',	wx.NewId(), self.OnPopupRiderDetail),
				('History', 	wx.NewId(), self.OnPopupHistory),
			]
			for p in self.popupInfo:
				self.Bind( wx.EVT_MENU, p[2], id=p[1] )
		
		race = Model.getRace()
		
		menu = wx.Menu()
		for i, p in enumerate(self.popupInfo):
			if p[0] == 'Record' and not race.isRunning():
				continue
			menu.Append( p[1], p[0] )
		
		self.PopupMenu( menu )
		menu.Destroy()
		
	def OnPopupHistory( self, event ):
		if Utils.isMainWin():
			Utils.getMainWin().showPageName( 'History' )
	def OnPopupRiderDetail( self, event ):
		if Utils.isMainWin():
			Utils.getMainWin().showRiderDetail()
		
	def showNumSelect( self ):
		race = Model.race
		if race is None:
			return
			
		textColour = {}
		backgroundColour = dict( ((rc, self.yellowColour) for rc in self.rcInterp) )
		for r in xrange(self.grid.GetNumberRows()):
		
			value = self.grid.GetCellValue( r, 1 )
			if not value:
				break	
			
			cellNum = value
			if cellNum == self.numSelect:
				for c in xrange(self.grid.GetNumberCols()):
					textColour[ (r,c) ] = self.whiteColour
					backgroundColour[ (r,c) ] = self.blackColour if (r,c) not in self.rcInterp else self.greyColour
					
				self.grid.MakeCellVisible( r, 0 )
				break
					
		self.grid.Set( textColour = textColour, backgroundColour = backgroundColour )
		self.grid.Reset()
			
	def doNumDrilldown( self, event ):
		self.doNumSelect( event )
		if self.numSelect is not None and Utils.isMainWin():
			Utils.getMainWin().showPageName( 'History' )
	
	def doNumSelect( self, event ):
		if self.isEmpty:
			return
		row, col = event.GetRow(), event.GetCol()
		if row >= self.grid.GetNumberRows() or col >= self.grid.GetNumberCols():
			return
		
		col = 1
		value = self.grid.GetCellValue( row, col )
		numSelect = None
		if value:
			numSelect = value
		if self.numSelect != numSelect:
			self.numSelect = numSelect
			self.showNumSelect()
		mainWin = Utils.getMainWin()
		if mainWin:
			historyCategoryChoice = mainWin.history.categoryChoice
			historyCatName = FixCategories( historyCategoryChoice )
			if historyCatName and historyCatName != 'All':
				catName = FixCategories( self.categoryChoice )
				if historyCatName != catName:
					if Model.race:
						Model.race.resultsCategory = self.categoryChoice.GetSelection()
					SetCategory( historyCategoryChoice, catName )
			mainWin.setNumSelect( numSelect )
				
	def setCategoryAll( self ):
		FixCategories( self.categoryChoice, 0 )
		if Model.race:
			Model.race.resultsCategory = 0
	
	def doChooseCategory( self, event ):
		if Model.race:
			Model.race.resultsCategory = self.categoryChoice.GetSelection()
		self.refresh()
	
	def reset( self ):
		self.numSelect = None
	
	def setNumSelect( self, num ):
		self.numSelect = num if num is None else str(num)
		if self.numSelect:
			self.search.SetValue( self.numSelect )

	def clearGrid( self ):
		self.grid.Set( data = [], colnames = [], textColour = {}, backgroundColour = {} )
		self.grid.Reset()

	def refresh( self ):
		self.category = None
		self.isEmpty = True
		self.rcInterp = set()	# Set of row/col coordinates of interpolated numbers.
		
		self.search.SelectAll()
		wx.CallAfter( self.search.SetFocus )
		
		with Model.LockRace() as race:
			if not race:
				self.clearGrid()
				return
			catName = FixCategories( self.categoryChoice, getattr(race, 'resultsCategory', 0) )
			self.hbs.Layout()
			self.category = race.categories.get( catName, None )
		
		exportGrid = ExportGrid()
		exportGrid.setResultsOneList( catName, False )
		
		if not exportGrid.colnames:
			self.clearGrid()
			return
		
		self.grid.Set( data = exportGrid.data, colnames = exportGrid.colnames )
		self.grid.AutoSizeColumns( True )
		self.grid.Reset()
		self.isEmpty = False

		# Highlight interpolated entries.
		with Model.LockRace() as race:
			for r in xrange(self.grid.GetNumberRows()):
				try:
					rider = race[int(self.grid.GetCellValue(r, 1))]
					entries = rider.interpolate()
					if not entries:
						continue
				except:
					continue
				eItr = (e for e in entries)
				eItr.next()						# Skip the first zero entry.
				for c in xrange(exportGrid.iLapTimes, self.grid.GetNumberCols()):
					if not self.grid.GetCellValue(r, c):
						break
					if eItr.next().interp:
						self.rcInterp.add( (r, c) )
		
		self.grid.MakeCellVisible( 0, 0 )
		self.showNumSelect()
						
		# Fix the grid's scrollbars.
		self.grid.FitInside()

	def commit( self ):
		pass
		
if __name__ == '__main__':
	import cPickle as pickle
	Utils.disable_stdout_buffering()
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,200))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	results = Results(mainWin)
	results.refresh()
	mainWin.Show()
	app.MainLoop()
