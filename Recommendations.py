import wx
import bisect
import Model
import Utils
import ColGrid
from GetResults import GetResults
from FixCategories import FixCategories
from RiderDetail import ShowRiderDetailDialog
from ReadSignOnSheet import SyncExcelLink

class Recommendations( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__(parent, id)
		
		self.numSelect = None
		self.textColour = {}
		self.backgroundColour = {}
		self.sortCol = 1
		self.sortDescending = False
		
		self.whiteColour = wx.Colour( 255, 255, 255 )
		self.blackColour = wx.Colour( 0, 0, 0 )

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, label = _('Category:') )
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
				
	def updateColours( self ):
		self.textColour = {}
		self.backgroundColour = {}
		c = 0
		for r in range(self.grid.GetNumberRows()):
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
		Model.setCategoryChoice( self.categoryChoice.GetSelection(), 'recommendationsCategory' )
		self.refresh()
	
	def reset( self ):
		self.numSelect = None

	def setNumSelect( self, num ):
		self.numSelect = num if num is None else '{}'.format(num)
	
	def clearGrid( self ):
		self.grid.Set( data = [], colnames = [], textColour = {}, backgroundColour = {} )
		self.grid.Reset()
	
	def refresh( self ):
		with Model.LockRace() as race:
			self.isEmpty = True
			
			if race is None:
				self.clearGrid()
				return

			SyncExcelLink( race )
			category = FixCategories( self.categoryChoice, getattr(race, 'recommendationsCategory', 0) )
					
			excelErrors = []
			try:
				externalInfo = race.excelLink.read( True )
				excelErrors = race.excelLink.getErrors()
			except Exception:
				externalInfo = {}
				excelErrors = []
				
			def getName( num ):
				info = externalInfo.get(num, {})
				last = info.get('LastName','')
				first = info.get('FirstName','')
				if last and first:
					return '{}, {}'.format(last, first)
				return last or first or ' '
				
			colnames = [ _('Num'), _('Name'), _('Issue'), _('Recommendation') ]
			data = [[],[], [], []]
			def append( num = '', name = '', issue = '', recommendation = '' ):
				data[0].append( '{}'.format(num) )
				data[1].append( '{}'.format(name) )
				data[2].append( '{}'.format(issue) )
				data[3].append( '{}'.format(recommendation) )
			
			self.isEmpty = False
			
			# Check for Excel errors (very bad!).
			for num, errorStr in excelErrors:
				append( num, getName(num), 'Excel', '{} {}'.format(_('Fix'), errorStr) )

			# Check if external info exists.
			if not externalInfo:
				append( issue=_('No Excel Spreadsheet Data'), recommendation=_('Link to an Excel spreadsheet for Name and Team info.') )

			firstRiderInCategory = []
			entries = race.interpolate()
			if entries:

				# Get riders who did extra laps.
				for catCur in race.getCategories():
					if category and catCur != category:
						continue
						
					# Get the first recorded rider of the category.
					firstRiderTime = None
					for e in entries:
						if not race.inCategory(e.num, catCur):
							continue
						rider = race.riders[e.num]
						t = rider.getFirstKnownTime()
						if t is None:
							continue
						if firstRiderTime is None or t < firstRiderTime[0]:
							firstRiderTime = (t, rider, catCur)
					if firstRiderTime:
						firstRiderInCategory.append( firstRiderTime )
						
					results = GetResults( catCur )
					if not results:
						continue
						
					# Check for times recorded before the Category startOffset.
					for rr in results:
						rider = race.riders[rr.num]
						earlyTimeCount = rider.countEarlyTimes()
						if earlyTimeCount > 0:
							startOffsetStr = Utils.formatTime( race.getStartOffset(rider.num) )
							append( rider.num, getName(rider.num),
									_('EarlyTimes'),
									'{} {} ({}={}, {}={} {}, {}="{}")'.format(
										_('Rider has entries before the Start Offset.'),
										_('Early times are not shown in the results.'),
										_('Count'), earlyTimeCount,
										_('StartOffset'), startOffsetStr, 'HH:MM:SS'[-len(startOffsetStr):],
										_('Category'), race.getCategory(rider.num).fullname,
									)
								)
					
					# Check for extra recorded laps.
					for rr in results:
						rider = race.riders[rr.num]
						if rider.status != rider.Finisher:
							break
						numRecordedTimes = len(rider.times)
						if numRecordedTimes > rr.laps:
							extra = numRecordedTimes - rr.laps
							append( rider.num, getName(rider.num),
									_('Laps'),
									'{} ({}={})'.format(
										_("Rider has extra laps not shown in results (all riders finish on leader's last lap)"),
										_('Count'), extra,
									),
								)
					
					# Report time penalties
					if getattr(race, 'isTimeTrial', False):
						for rr in results:
							rider = race.riders[rr.num]
							if rider.status == rider.Finisher and getattr(rr,'ttPenalty',0.0) > 0.0:
								reason = ' '.join( ['{:.3f}'.format(getattr(rr,'ttPenalty')), _('sec'), _("time penalty")] )
								if getattr(rr, 'ttNote', ''):
									reason += ' - {}'.format( getattr(rr, 'ttNote') )
								append( rider.num, getName(rider.num), _('Penalty'), reason )
				
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
				for num, maxLap in riderMaxLapNonInterp.items():
					riderCat = race.getCategory( num )
					if riderCat:
						categoryMaxLapNonInterp[riderCat] = max( categoryMaxLapNonInterp.get(riderCat, 0), maxLap )
				for num, maxLap in riderMaxLapInterp.items():
					riderCat = race.getCategory( num )
					if riderCat:
						categoryMaxLapInterp[riderCat] = max( categoryMaxLapInterp.get(riderCat, 0), maxLap )
				
				# Check if all the riders in a particular category did not complete the maximum number of laps.
				raceLaps = race.getRaceLaps()
				for category, maxNonInterpLap in categoryMaxLapNonInterp.items():
					maxCatLaps = (race.getNumLapsFromCategory(category) or raceLaps)
					try:
						if maxNonInterpLap < maxCatLaps and categoryMaxLapInterp[category] > maxNonInterpLap:
							append(
								category.catStr, category.fullname,
								_('Laps'),
								'{}: {}  {}: {}  {}'.format(
									_('Category'), category.fullname,
									_('Race Laps'), maxNonInterpLap,
									_('Verify that Category did Race Laps.  Update Race Laps for Category if necessary.'),
								)
							)
					except KeyError:
						pass
				
				# Collect all entries for every rider.
				riderEntries = {}
				for e in entries:
					riderEntries.setdefault( e.num, [] ).append( e )
					
				for num in sorted(r for r in race.getRiderNums() if match(r)):
					rider = race.riders[num]
					statusName = Model.Rider.statusNames[rider.status]
					if rider.status == Model.Rider.Finisher:
						# Check for unreported DNFs.
						try:
							riderEntriesCur = riderEntries[num]
							iLast = next(i for i in range(len(riderEntriesCur), 0, -1) if not riderEntriesCur[i-1].interp)
							if iLast != len(riderEntriesCur) and race.isFinished():
								append( num, getName(num),
										_('DNF'),
										'{} {}.'.format(_('Check for DNF after rider lap'), iLast-1) )
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
										_('Lapped'),
										'{} {}'.format(
											_("Confirm rider was lapped by Category Leader in leader's lap"),
											(', '.join( '{}'.format(i) for i, b in enumerate(appearedInLap) if not b ))
										)
								)
						except (KeyError, IndexError, ValueError):
							pass
							
					elif rider.status == Model.Rider.DNS:
						# Check for DNS's with recorded times.
						if rider.times:
							append( num, getName(num),
									_('DNS'),
									'{} {}: {}'.format(_('Rider has recorded times.'), _('Check status'), statusName)
							)
							
					elif rider.status in [Model.Rider.DNF, Model.Rider.Pulled]:
						if rider.tStatus == None:
							# Missing status times.
							append( num, getName(num),
									_('Time'),
									'{}  {}: {}'.format(_('Check if time is accurate.'), _('Status'), statusName)
							)
						else:
							# Recorded time exceeds status time.
							if rider.times and rider.times[-1] > rider.tStatus:
								append(
									num, getName(num),
									_('Time'),
									'{}: {}.  {}: {} > {}'.format(
										_('Check time for Status'), statusName,
										_('Found recorded time'), Utils.SecondsToStr(rider.times[-1]), Utils.SecondsToStr(rider.tStatus),
									)
								)

					# Check for bad numbers.
					category = race.getCategory( num )
					if not category:
						append( num, getName(num),
								_('Category'),
								_('Rider does not match any active category.  Check if rider is in right race or data entry error.') )
							
				# Show numbers with projected time.
				if race.isFinished():
					projectedNums = []
					for r in GetResults( category ):
						pSum = sum( 1 for i in r.interp if i )
						if pSum > 0:
							projectedNums.append( (r.num, pSum) )
					projectedNums.sort()
					for num, count in projectedNums:
						append(
							num, getName(num),
							_('Projected'),
							'{} ({})'.format(_('Check rider has projected times'), count)
						)
					
				# Show missing tag reads.
				missingTags = ['{}'.format(m) for m in getattr(race, 'missingTags', set())]
				missingTags.sort()
				for m in missingTags:
					append( m, '',
							_('Tag'),
							_('Imported chip Tag missing from Excel sheet.  Check if a stray read.  If not, add Tag to Excel sheet and run Chip Import again')
							)
							
				# Add information about the rider categories.
				firstRiderInCategory.sort( key = lambda f: (f[0], f[2].name) )
				for t, rider, catCur in firstRiderInCategory:
					append( rider.num, getName(rider.num),
							_('Start'),
							'{}: {}  {}: {}'.format(_('Category'), catCur.name, _('First recorded time'), Utils.formatTime(t, True), )
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
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	race = Model.getRace()
	race._populate()
	race.numLaps = 10
	race.riders[101].status = Model.Rider.DNS
	race.riders[102].status = Model.Rider.DNF
	race.riders[102].tStatus = race.riders[102].interpolate()[2].t
	race.riders[103].status = Model.Rider.DNF
	race.riders[104].status = Model.Rider.Pulled
	for i, category in enumerate(race.getCategories()):
		category.startOffset = '00:{:02d}:00'.format(i * 5)
	recommendations = Recommendations(mainWin)
	recommendations.refresh()
	mainWin.Show()
	app.MainLoop()
