import wx
import Model
import Utils
from FixCategories import FixCategories, SetCategory
import GapChartPanel
from GetResults import GetResults

class GapChart( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__(parent, id)

		self.numSelect = None

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, label = _('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind( wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice )
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		
		self.gapChart = GapChartPanel.GapChartPanel( self )

		bs = wx.BoxSizer(wx.VERTICAL)
		bs.Add(self.hbs, flag=wx.GROW|wx.HORIZONTAL)
		bs.Add(self.gapChart, 1, wx.GROW|wx.ALL, 5)
		self.SetSizer(bs)
		bs.SetSizeHints(self)
		self.SetDoubleBuffered( True )

	def doChooseCategory( self, event ):
		Model.setCategoryChoice( self.categoryChoice.GetSelection(), 'gapChartCategory' )
		self.refresh()
		
	def setCategory( self, category ):
		for i, c in enumerate(Model.race.getCategories( startWaveOnly=False ) if Model.race else [], 1):
			if c == category:
				SetCategory( self.categoryChoice, c )
				Model.setCategoryChoice( i, 'gapChartCategory' )
				return
		SetCategory( self.categoryChoice, None )
		Model.setCategoryChoice( 0, 'gapChartCategory' )
		
	def reset( self ):
		self.gapChart.numSelect = None

	def setNumSelect( self, num ):
		self.gapChart.numSelect = num if num is None else '{}'.format(num)
	
	def refresh( self ):
		race = Model.race
		if not race or race.isUnstarted():
			self.gapChart.SetData( None )
			return
		
		category = FixCategories( self.categoryChoice, getattr(race, 'gapChartCategory', 0) )
		results = GetResults( category )
		if not results:
			self.gapChart.SetData( None )
			return
		
		data = []
		labels = []
		interp = []
		if not race.isRunning():
			lapMax = len(results[0].raceTimes)

		for rr in results:
			if not rr.raceTimes:
				continue
			
			if race.isRunning():
				try:
					lapMax = next( i+1 for i in range(len(rr.interp)-1, -1, -1) if not rr.interp[i] )
				except Exception:
					continue
			
			if lapMax:			
				data.append( rr.raceTimes[:lapMax] )
				labels.append( str(rr.num) )
				interp.append( rr.interp[:lapMax] )
		
		self.gapChart.SetData( data, labels, interp )
	
	def commit( self ):
		pass
	
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	gapChart = GapChart(mainWin)
	gapChart.refresh()
	mainWin.Show()
	app.MainLoop()
