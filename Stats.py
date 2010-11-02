import wx
import wx.grid		as gridlib
import Model
import Utils
from Histogram import Histogram
from LineGraph import LineGraph
from FixCategories import FixCategories

class Stats( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		bs = wx.BoxSizer(wx.VERTICAL)

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )

		bs.Add( self.hbs )
		
		bs.Add( wx.StaticText(self, wx.ID_ANY, 'Top Riders:'), border = 5 )
		
		self.lineGraph = LineGraph( self )
		bs.Add(self.lineGraph, 2, flag=wx.GROW|wx.ALL, border=5 )
		
		self.histogram = Histogram( self )
		bs.Add(self.histogram, 2, flag=wx.GROW|wx.ALL, border=5 )
		self.SetSizer(bs)
		
	def doChooseCategory( self, event ):
		if Model.race is not None:
			Model.race.statsCategory = self.categoryChoice.GetSelection()
		self.refresh()
	
	def refresh( self ):
		race = Model.getRace()
		if race is None:
			self.lineGraph.SetData( None )
			self.histogram.SetData( None )
			return
			
		catName = FixCategories( self.categoryChoice, getattr(race, 'statsCategory', 0) )

		results = race.getResultsList( catName )
		finishers = set( r.num for r in results )
			
		# Update the histogram.
		maxLap = race.getMaxLap()
		if race.numLaps is not None and race.numLaps < maxLap:
			maxLap = race.numLaps
		histogramData = []
		entries = race.interpolateLap( maxLap )
		entries = [e for e in entries if e.num in finishers]	# Trim the results to this category.
		lastRiderLapTime = {}
		riderDataCount = {}
		for e in (e for e in entries if e.t > 0):
			riderDataCount[e.num] = riderDataCount.get(e.num, 0) + 1
		for e in (e for e in entries if e.t > 0):
			if riderDataCount[e.num] > maxLap / 2:
				histogramData.append( e.t - lastRiderLapTime.get(e.num, 0) )
				lastRiderLapTime[e.num] = e.t
		
		if histogramData:
			average = sum(histogramData, 0.0) / len(histogramData)
			stdev = sum( ((h - average) ** 2 for h in histogramData), 0.0 ) / len(histogramData)
			var = stdev ** 0.5
			aveLow, aveHigh = average - var * 4, average + var * 4
			histogramData = [d for d in histogramData if aveLow < d < aveHigh]
			
		self.histogram.SetData( histogramData )

		# Get a line graph for the top finishers.
		lgData = []
		lgLabels = []
		lgInterpolated = []
		results = results[:min(5, len(results))]
		for i, r in enumerate(results):
			lgLabels.append( '%s (%d)' % (str(r.num), i+1) )
			riderEntries = [e for e in entries if e.num == r.num]
			lgData.append( [riderEntries[i].t - riderEntries[i-1].t for i in xrange(1, len(riderEntries))] )
			lgInterpolated.append( [e.interp for e in riderEntries if e.t > 0] )
		
		self.lineGraph.SetData( lgData, labels = lgLabels, interpolated = lgInterpolated )

	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	stats = Stats(mainWin)
	stats.refresh()
	mainWin.Show()
	app.MainLoop()