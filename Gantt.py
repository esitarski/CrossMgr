import Model
import Utils
import wx
from FixCategories import FixCategories
import GanttChart

def UpdateSetNum( num ):
	if num is None:
		return
	mainWin = Utils.getMainWin()
	mainWin.setNumSelect( num )
	mainWin.showRiderDetail()

def GetNowTime():
	race = Model.getRace()
	return race.lastRaceTime() if race and race.isRunning() else None

class Gantt( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)

		self.numSelect = None
		
		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		
		self.ganttChart = GanttChart.GanttChart( self )
		self.ganttChart.dClickCallback = UpdateSetNum
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
		
	def refresh( self ):
		with Model.LockRace() as race:
			if race is None:
				self.ganttChart.SetData( None )
				return

			catName = FixCategories( self.categoryChoice, getattr(race, 'GanttCategory', 0) )
			maxLaps = race.numLaps
			if maxLaps is None:
				maxLaps = race.getMaxLap()
				if race.isRunning():
					maxLaps += 2
			
			entries = race.interpolateLap( maxLaps )
			category = race.categories.get( catName, None )
			print category
			if category:
				# Filter by category and num laps in that category.
				numLaps = category.getNumLaps()
				if not numLaps:
					numLaps = 1000
				entries = [e for e in entries if race.getCategory(e.num) == category and e.lap <= numLaps]
			else:
				# Filter by the number of laps for each individual category.
				entries = [e for e in entries if e.lap <= race.getCategoryNumLaps(e.num)]
			
			riderTimes = {}
			riderInterp = {}
			for e in entries:
				riderTimes.setdefault(e.num, []).append( e.t )
				riderInterp.setdefault(e.num, []).append( e.interp )
			
			# Adjust for the start times offset.
			catOffset = {}
			for r, t in riderTimes.iteritems():
				category = race.getCategory( r )
				if category:
					t[0] = min(catOffset.setdefault( category, category.getStartOffsetSecs() ), t[1])
				
			numTimes = [(k, v) for k, v in riderTimes.iteritems()]
			numTimes.sort( key = lambda x : (-len(x[1]), x[1][-1]) )

			labels = [str(n) for n, times in numTimes]
			data = [times for n, times in numTimes]
			interp = [riderInterp[n] for n, times in numTimes]
			self.ganttChart.SetData( data, labels, GetNowTime(), interp )
	
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
