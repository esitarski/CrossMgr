import Model
import Utils
import wx
from FixCategories import FixCategories
import GanttChart

class Gantt( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)

		self.gantt = None
		
		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		
		self.ganttChart = GanttChart.GanttChart( self )

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
		pass

	def refresh( self ):
		race = Model.getRace()
		
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
		if category is not None:
			def match( num ) : return category.matches(num)
		else:
			def match( num ) : return True
		
		riderTimes = {}
		for e in entries:
			if match(e.num):
				riderTimes.setdefault(e.num, []).append( e.t )
			
		numTimes = [(k, v) for k, v in riderTimes.iteritems()]
		numTimes.sort( cmp=lambda x, y: cmp((-len(x[1]), x[1][-1]), (-len(y[1]), y[1][-1])) )

		labels = [str(n) for n, times in numTimes]
		data = [times for n, times in numTimes]
		self.ganttChart.SetData( data, labels, race.lastRaceTime() if race.isRunning() else None )
	
	def commit( self ):
		pass
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	gantt = Gantt(mainWin)
	gantt.refresh()
	mainWin.Show()
	app.MainLoop()
