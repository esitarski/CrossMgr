import Model
import Utils
import wx
from FixCategories import FixCategories
import GanttChartPanel
from GetResults import GetResults, RidersCanSwap
from Undo import undo
import EditEntry

def UpdateSetNum( num ):
	if num is None:
		return
	mainWin = Utils.getMainWin()
	mainWin.setNumSelect( num )
	mainWin.showRiderDetail()

def GetNowTime():
	race = Model.race
	return race.lastRaceTime() if race and race.isRunning() else None

class Gantt( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)

		self.numSelect = None
		self.entry = None
		self.numBefore = None
		self.numAfter = None
		
		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		
		self.ganttChart = GanttChartPanel.GanttChartPanel( self )
		self.ganttChart.dClickCallback = UpdateSetNum
		self.ganttChart.rClickCallback = self.onRightClick
		self.ganttChart.getNowTimeCallback = GetNowTime

		bs = wx.BoxSizer(wx.VERTICAL)
		bs.Add(self.hbs, flag=wx.GROW|wx.HORIZONTAL)
		bs.Add(self.ganttChart, 1, wx.GROW|wx.ALL, 5)
		self.SetSizer(bs)
		bs.SetSizeHints(self)

	def doChooseCategory( self, event ):
		if Model.race is not None:
			Model.race.GanttCategory = self.categoryChoice.GetSelection()
		self.refresh()
	
	def reset( self ):
		self.ganttChart.numSelect = None

	def setNumSelect( self, num ):
		self.ganttChart.numSelect = num if num is None else str(num)
	
	def onRightClick( self, xPos, yPos, num, iRider, iLap ):
		with Model.LockRace() as race:
			if not race or num not in race:
				return
			catName = FixCategories( self.categoryChoice, getattr(race, 'resultsCategory', 0) )
			entries = race.getRider(num).interpolate()
			try:
				self.entry = entries[iLap]
			except (IndexError, KeyError):
				return
		self.setNumSelect( num )
		self.numSelect = num
		if Utils.isMainWin():
			wx.CallAfter( Utils.getMainWin().setNumSelect, self.ganttChart.numSelect )
			
		self.iLap = iLap
		self.iRow = iRider
		
		allCases = 0
		interpCase = 1
		nonInterpCase = 2
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				(wx.NewId(), 'Results', 	'Switch to Results tab', self.OnPopupResults, allCases),
				(wx.NewId(), 'RiderDetail',	'Switch to RiderDetail tab', self.OnPopupRiderDetail, allCases),
				(None, None, None, None, None),
				(wx.NewId(), 'Correct Lap End Time...',	'Change number or lap end time...',	self.OnPopupCorrect, interpCase),
				(wx.NewId(), 'Shift Lap End Time...',	'Move lap end time earlier/later...',	self.OnPopupShift, interpCase),
				(wx.NewId(), 'Delete Lap End Time...',	'Delete lap end time...',	self.OnPopupDelete, nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), 'Swap with Rider before',	'Swap with Rider before',	self.OnPopupSwapBefore, nonInterpCase),
				(wx.NewId(), 'Swap with Rider after',	'Swap with Rider after',	self.OnPopupSwapAfter, nonInterpCase),

			]
			self.splitMenuInfo = [
					(wx.NewId(),
					'Add %d Missing Split%s' % (split-1, 's' if split > 2 else ''),
					lambda evt, s = self, splits = split: s.doSplitLap(splits)) for split in xrange(2,8) ]
			for id, name, text, callback, cCase in self.popupInfo:
				if id:
					self.Bind( wx.EVT_MENU, callback, id=id )
			for id, name, callback in self.splitMenuInfo:
				self.Bind( wx.EVT_MENU, callback, id=id )
				
		caseCode = 1 if entries[iLap].interp else 2
		
		riderResults = dict( (r.num, r) for r in GetResults(catName) )
		
		self.numBefore, self.numAfter = None, None
		for iRow, attr in [(self.iRow - 1, 'numBefore'), (self.iRow + 1, 'numAfter')]:
			if not(0 <= iRow < len(self.ganttChart.labels)):
				continue
			numAdjacent = GanttChartPanel.numFromLabel(self.ganttChart.labels[iRow])
			if RidersCanSwap( riderResults, num, numAdjacent ):
				setattr( self, attr, numAdjacent )
		
		menu = wx.Menu()
		for id, name, text, callback, cCase in self.popupInfo:
			if not id:
				Utils.addMissingSeparator( menu )
				continue
			if caseCode < cCase:
				continue
			if (name.endswith('before') and not self.numBefore) or (name.endswith('after') and not self.numAfter):
				continue
			menu.Append( id, name, text )
			
		if caseCode == 2:
			submenu = wx.Menu()
			for id, name, callback in self.splitMenuInfo:
				submenu.Append( id, name )
			Utils.addMissingSeparator( menu )
			menu.AppendMenu( wx.NewId(), 'Add Missing Split', submenu )
			
		Utils.deleteTrailingSeparators( menu )
		self.PopupMenu( menu )
		menu.Destroy()

	def doSplitLap( self, splits ):
		with Model.LockRace() as race:
			try:
				num = int(self.ganttChart.numSelect)
				lap = self.iLap
				times = [e.t for e in race.riders[num].interpolate()]
			except (TypeError, KeyError, ValueError, IndexError):
				return
		EditEntry.AddLapSplits( num, lap, times, splits )
		self.refresh()
		
	def swapEntries( self, num, numAdjacent ):
		if not num or not numAdjacent:
			return
		with Model.LockRace() as race:
			if (not race or
				num not in race or
				numAdjacent not in race ):
				return
			e1 = race.getRider(num).interpolate()
			e2 = race.getRider(numAdjacent).interpolate()
			catName = FixCategories( self.categoryChoice, getattr(race, 'ganttCategory', 0) )
			
		riderResults = dict( (r.num, r) for r in GetResults(catName) )
		try:
			laps = riderResults[num].laps
			undo.pushState()
			with Model.LockRace() as race:
				EditEntry.SwapEntry( e1[laps], e2[laps] )
			wx.CallAfter( self.refresh )
		except KeyError:
			pass
	
	def OnPopupSwapBefore( self, event ):
		self.swapEntries( int(self.numSelect), self.numBefore )
		
	def OnPopupSwapAfter( self, event ):
		self.swapEntries( int(self.numSelect), self.numAfter )
	
	def OnPopupCorrect( self, event ):
		EditEntry.CorrectNumber( self, self.entry )
		
	def OnPopupShift( self, event ):
		EditEntry.ShiftNumber( self, self.entry )

	def OnPopupDelete( self, event ):
		EditEntry.DeleteEntry( self, self.entry )

	def OnPopupResults( self, event ):
		if Utils.isMainWin():
			Utils.getMainWin().showPageName( 'Results' )
			
	def OnPopupRiderDetail( self, event ):
		if Utils.isMainWin():
			Utils.getMainWin().showPageName( 'RiderDetail' )
		
	def refresh( self ):
		if not Model.race:
			self.ganttChart.SetData( None )
			return
		
		catName = FixCategories( self.categoryChoice, getattr(Model.race, 'GanttCategory', 0) )
		results = GetResults( catName, True )
		
		#labels	= [str(r.num) for r in results]
		labels = []
		for r in results:
			last = getattr(r, 'LastName', None)
			first = getattr(r, 'FirstName', None)
			if last and first:
				labels.append( '%s, %s %d' % (last, first, r.num) )
			elif first:
				labels.append( '%s %d' % (first, r.num) )
			elif last:
				labels.append( '%s %d' % (last, r.num) )
			else:
				labels.append( str(r.num) )
			
		data	= [r.raceTimes for r in results]
		interp	= [r.interp for r in results]
		self.ganttChart.SetData( data, labels, GetNowTime(), interp,
								set(i for i, r in enumerate(results) if r.status != Model.Rider.Finisher) )
		wx.CallAfter( self.ganttChart.SetFocus )
	
	def commit( self ):
		pass
	
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	gantt = Gantt(mainWin)
	gantt.refresh()
	mainWin.Show()
	app.MainLoop()
