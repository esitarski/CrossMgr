import wx
import wx.grid		as gridlib
import bisect
import Model
import Utils
import ColGrid
from GetResults import GetResultsCore
from FixCategories import FixCategories
from RiderDetail import ShowRiderDetailDialog

class Recommendations( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		
		self.numSelect = None
		self.textColour = {}
		self.backgroundColour = {}
		self.sortCol = 1
		self.sortDescending = False
		
		self.whiteColour = wx.Colour( 255, 255, 255 )
		self.blackColour = wx.Colour( 0, 0, 0 )

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )

		self.grid = ColGrid.ColGrid( self )
		self.grid.SetRightAlign( False )
		self.grid.SetRowLabelSize( 32 )
		self.grid.SetMargins( 0, 0 )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()

		self.Bind( wx.grid.EVT_GRID_SELECT_CELL, self.doNumSelect )
		self.Bind( wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.doNumDrilldown )
		#self.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doRightClick )
		self.Bind( wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.doColSort )
		
		bs = wx.BoxSizer(wx.VERTICAL)
		bs.Add(self.hbs, flag=wx.GROW|wx.HORIZONTAL)
		bs.Add(self.grid, 1, wx.GROW|wx.ALL, 5)
		self.SetSizer(bs)
		bs.SetSizeHints(self)

	'''
	def doRightClick( self, event ):
		if self.isEmpty:
			return
			
		self.rowPopup = event.GetRow()
		self.colPopup = event.GetCol()
		numSelect = self.getCellNum( self.rowPopup, self.colPopup )
		if not numSelect:
			return
			
		self.doNumSelect( event )
				
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				('Results', 	wx.NewId(), self.OnPopupResults),
				('RiderDetail',wx.NewId(), self.OnPopupRiderDetail),
				
				('Correct...',	wx.NewId(), self.OnPopupCorrect),
				('Insert...',	wx.NewId(), self.OnPopupSplit),
				('Delete...',	wx.NewId(), self.OnPopupDelete)
			]
			self.numEditActions = 2
			for p in self.popupInfo:
				self.Bind( wx.EVT_MENU, p[2], id=p[1] )

		isInterp = self.history[self.colPopup][self.rowPopup].interp
		
		race = Model.getRace()
		menu = wx.Menu()
		for i, p in enumerate(self.popupInfo):
			if i >= self.numEditActions and isInterp:		# Disallow editing of interpreted entries
				continue
			elif i == self.numEditActions and not isInterp:
				menu.AppendSeparator()
			elif p[0] == 'Record' and not race.isRunning():
				continue
			menu.Append( p[1], p[0] )
		
		self.PopupMenu( menu )
		menu.Destroy()
	'''
				
	def updateColours( self ):
		self.textColour = {}
		self.backgroundColour = {}
		c = 0
		for r in xrange(self.grid.GetNumberRows()):
			value = self.grid.GetCellValue( r, c )
			if not value:
				break				
			cellNum = value.split('=')[0]
			if cellNum == self.numSelect:
				self.textColour[ (r,c) ] = self.whiteColour
				self.backgroundColour[ (r,c) ] = self.blackColour
		
	def showNumSelect( self ):
		self.updateColours()
		self.grid.Set( textColour = self.textColour, backgroundColour = self.backgroundColour )
		self.grid.Reset()
	
	def doNumDrilldown( self, event ):
		self.doNumSelect( event )
		ShowRiderDetailDialog( self, self.numSelect )
	
	def getCellNum( self, row, col ):
		if row >= self.grid.GetNumberRows():
			return None
		value = self.grid.GetCellValue( row, 0 )
		try:
			numSelect = value.split('=')[0]
			if 0 <= int(numSelect) <= 50000:
				return numSelect
		except (AttributeError, ValueError):
			return None
	
	def doColSort( self, event ):
		iCol = event.GetCol()
		if iCol < 0:
			return
		if iCol == self.sortCol:
			self.sortDescending ^= True
		else:
			self.sortCol = iCol
			self.sortDescending = False
		self.grid.SortByColumn( self.sortCol, self.sortDescending )
	
	def doNumSelect( self, event ):
		if self.isEmpty:
			return
		numSelect = self.getCellNum(event.GetRow(), event.GetCol())
		if numSelect is not None:
			if self.numSelect != numSelect:
				self.numSelect = numSelect
				self.showNumSelect()
			if Utils.isMainWin():
				Utils.getMainWin().setNumSelect( numSelect )
	
	def doChooseCategory( self, event ):
		Utils.setCategoryChoice( self.categoryChoice.GetSelection(), 'recommendationsCategory' )
		self.refresh()
	
	def reset( self ):
		self.numSelect = None

	def setNumSelect( self, num ):
		self.numSelect = num if num is None else str(num)
	
	def clearGrid( self ):
		self.grid.Set( data = [], colnames = [], textColour = {}, backgroundColour = {} )
		self.grid.Reset()
	
	def refresh( self ):
		with Model.LockRace() as race:
			self.isEmpty = True
			
			if race is None:
				self.clearGrid()
				return

			category = FixCategories( self.categoryChoice, getattr(race, 'recommendationsCategory', 0) )
					
			excelErrors = []
			try:
				externalInfo = race.excelLink.read( True )
				excelErrors = race.excelLink.getErrors()
			except:
				externalInfo = {}
				excelErrors = []
				
			def getName( num ):
				info = externalInfo.get(num, {})
				last = info.get('LastName','')
				first = info.get('FirstName','')
				if last and first:
					return '%s, %s' % (last, first)
				return last or first or ' '
				
			colnames = [ 'Num', 'Name', 'Issue', 'Recommendation' ]
			data = [[],[], [], []]
			def append( num = '', name = '', issue = '', recommendation = '' ):
				data[0].append( str(num) )
				data[1].append( str(name) )
				data[2].append( str(issue) )
				data[3].append( str(recommendation) )
			
			self.isEmpty = False

			# Check for Excel errors (very bad!).
			for num, errorStr in excelErrors:
				append( num, getName(num), 'Excel', 'Fix ' + errorStr )
			
			entries = race.interpolate()
			if entries:

				# Get riders who did extra laps.
				for catCur in race.getCategories():
					if category and catCur != category:
						continue
					results = GetResultsCore( catCur )
					if not results:
						continue
					for rr in results:
						rider = race.riders[rr.num]
						if rider.status != rider.Finisher:
							break
						numRecordedTimes = len(rider.times)
						if numRecordedTimes > rr.laps:
							extra = numRecordedTimes - rr.laps
							append( rider.num, getName(rider.num), 'Laps', "Rider has %d recorded lap%s not shown in results (all riders finish on leader's last lap)"
																						% (extra, 's' if extra > 1 else '') )
				
				# Trim out all entries not in this category and all non-finishers.
				if category:
					def match( num ) : return category.matches(num)
				else:
					def match( num ) : return True
				entries = [e for e in entries if match(e.num) ]
				
				# Find the maximum recorded lap for each rider.
				riderMaxLapNonInterp, riderMaxLapInterp = {}, {}
				for e in entries:
					if e.interp:
						riderMaxLapInterp[e.num] = max( riderMaxLapInterp.get(e.num, 0), e.lap )
					else:
						riderMaxLapNonInterp[e.num] = max( riderMaxLapNonInterp.get(e.num, 0), e.lap )
				
				# Find the maximum recorded lap for each category.
				categoryMaxLapNonInterp, categoryMaxLapInterp = {}, {}
				for num, maxLap in riderMaxLapNonInterp.iteritems():
					riderCat = race.getCategory( num )
					if riderCat:
						categoryMaxLapNonInterp[riderCat] = max( categoryMaxLapNonInterp.get(riderCat, 0), maxLap )
				for num, maxLap in riderMaxLapInterp.iteritems():
					riderCat = race.getCategory( num )
					if riderCat:
						categoryMaxLapInterp[riderCat] = max( categoryMaxLapInterp.get(riderCat, 0), maxLap )
				
				# Check if all the riders in a particular category did not complete the maximum number of laps.
				raceLaps = race.getRaceLaps()
				for category, maxNonInterpLap in categoryMaxLapNonInterp.iteritems():
					maxCatLaps = (category.getNumLaps() or raceLaps)
					try:
						if maxNonInterpLap < maxCatLaps and categoryMaxLapInterp[category] > maxNonInterpLap:
							append( category.catStr, category.fullname,
									'Laps',
									'Verify that "%s" did %d max Race Laps.  Update Race Laps in Categories if necessary.' %
											(category.fullname, maxNonInterpLap)
									)
					except KeyError:
						pass
				
				# Collect all entries for every rider.
				riderEntries = {}
				for e in entries:
					riderEntries.setdefault( e.num, [] ).append( e )
					
				for num in sorted(r for r in race.getRiderNums() if match(r)):
					rider = race[num]
					statusName = Model.Rider.statusNames[rider.status]
					if rider.status == Model.Rider.Finisher:
						# Check for unreported DNFs.
						try:
							riderEntriesCur = riderEntries[num]
							iLast = (i for i in xrange(len(riderEntriesCur), 0, -1) if not riderEntriesCur[i-1].interp).next()
							if iLast != len(riderEntriesCur):
								append( num, getName(num),
										'DNF', 'Check for DNF after rider lap %d.' % (iLast-1) )
						except (KeyError, StopIteration):
							pass
							
						# Check for rider missing lap data relative to category.
						try:
							riderEntriesCur = riderEntries[num]
							leaderTimes = race.getCategoryTimesNums()[race.getCategory(num)][0]
							
							appearedInLap = [False] * len(riderEntriesCur)
							appearedInLap[0] = True
							for e in riderEntriesCur:
								i = bisect.bisect_left( leaderTimes, e.t )
								if e.t < leaderTimes[i]:
									i -= 1
								i = min( i, len(appearedInLap) - 1 )	# Handle if rider would have been lapped again on the last lap.
								appearedInLap[i] = True

							missingCount = sum( 1 for b in appearedInLap if not b )
							if missingCount:
								append( num, getName(num),
										'Lapped', "Confirm rider was lapped by Category Leader in leader's lap %s" %
											(', '.join( str(i) for i, b in enumerate(appearedInLap) if not b ))
										)
						except (KeyError, IndexError, ValueError):
							pass
							
					elif rider.status == Model.Rider.DNS:
						# Check for DNS's with recorded times.
						if rider.times:
							append( num, getName(num),
									'DNS', 'Check %s status.  Rider has recorded times.' % statusName
									)
							
					elif rider.status in [Model.Rider.DNF, Model.Rider.Pulled]:
						if rider.tStatus == None:
							# Missing status times.
							append( num, getName(num),
									'Time', 'Check if %s time is accurate.' % statusName )
						else:
							# Recorded time exceeds status time.
							if rider.times and rider.times[-1] > rider.tStatus:
								append( num, getName(num),
										'Time' , 'Check if %s time is accurate.  Found recorded time %s after %s time %s.' % (
													statusName,
													Utils.SecondsToStr(rider.times[-1]),
													statusName,
													Utils.SecondsToStr(rider.tStatus)
												)
										)

					# Check for bad numbers.
					category = race.getCategory( num )
					if not category:
						append( num, getName(num),
								'Category', 'Rider does not match any active category.  Check if rider is in right race or data entry error.' )
							
				# Show numbers with projected time.
				if race.isFinished():
					projectedNums = []
					for r in GetResultsCore( category ):
						pSum = sum( 1 for i in r.interp if i )
						if pSum > 0:
							projectedNums.append( (r.num, pSum) )
					projectedNums.sort()
					for num, count in projectedNums:
						append( num, getName(num),
								'Projected', 'Check rider has projected times (%d).' % count
								)
					
				# Show missing tag reads.
				missingTags = [str(m) for m in getattr(race, 'missingTags', set())]
				missingTags.sort()
				for m in missingTags:
					append( m, '',
							'Tag', 'Check chip tag missing from Excel sheet'
							)
				# end if entries
				
			self.grid.Set( data = data, colnames = colnames )
			self.grid.AutoSizeColumns( True )
			self.grid.Reset()
			self.updateColours()
			
			# Fix the grid's scrollbars.
			self.grid.SortByColumn( self.sortCol, self.sortDescending )
			self.grid.FitInside()
	
	def commit( self ):
		pass
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	race = Model.getRace()
	race._populate()
	race.numLaps = 10
	race[101].status = Model.Rider.DNS
	race[102].status = Model.Rider.DNF
	race[102].tStatus = race[102].interpolate()[2].t
	race[103].status = Model.Rider.DNF
	race[104].status = Model.Rider.Pulled
	recommendations = Recommendations(mainWin)
	recommendations.refresh()
	mainWin.Show()
	app.MainLoop()
