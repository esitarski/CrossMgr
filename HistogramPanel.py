import wx
import os
import sys
import math
import Utils
import Model
from ReadSignOnSheet	import ExcelLink
from FixCategories import FixCategories, SetCategory
from GetResults import GetResults
from Histogram import Histogram

class HistogramPanel( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize ):
		super(HistogramPanel, self).__init__( parent, id, size=size )
		self.category = None
		
		self.hbs = wx.BoxSizer( wx.HORIZONTAL )
		self.categoryLabel = wx.StaticText( self, label = _('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL, border=4 )
		
		self.histogram = Histogram( self )
		bs = wx.BoxSizer( wx.VERTICAL )
		
		bs.Add( self.hbs, 0, wx.EXPAND )
		bs.Add( self.histogram, 1, wx.EXPAND )
		
		self.SetDoubleBuffered( True )
		self.SetSizer( bs )
	
	def doChooseCategory( self, event ):
		Model.setCategoryChoice( self.categoryChoice.GetSelection(), 'histogramCategory' )
		self.refresh()
	
	def refresh( self ):
		race = Model.race
		if not race:
			self.histogram.SetData( [], [], [] )
		self.category = FixCategories( self.categoryChoice, getattr(race, 'histogramCategory', 0) )
		if self.category is None:
			categories = race.getCategories( startWaveOnly=True )
			def getCatName( bib ):
				for c in categories:
					if race.inCategory( bib, c ):
						return c.fullname
				return u''
		elif self.category.catType == Model.Category.CatWave:
			components = race.getComponentCategories( self.category )
			if components:
				def getCatName( bib ):
					for c in components:
						if race.inCategory( bib, c ):
							return c.fullname
					return u''
			else:
				def getCatName( bib ):
					return self.category.fullname			
		else:
			def getCatName( bib ):
				return self.category.fullname
		
		results = GetResults( self.category )
		Finisher = Model.Rider.Finisher
		data, label, category = [], [], []
		maxLaps = None
		for rr in results:
			if rr.status != Finisher or len(rr.raceTimes or []) < 2:
				continue
			if maxLaps is None:
				maxLaps = len(rr.raceTimes) - 1
			if len(rr.raceTimes) - 1 != maxLaps:
				continue
			data.append( rr.raceTimes[-1] )
			label.append( u'{}: {}'.format(rr.num, rr.short_name()) )
			category.append( getCatName(rr.num) )
		self.histogram.SetData( data, label, category )

if __name__ == '__main__':
	app = wx.App(False)
	app.SetAppName("CrossMgr")
	
	Utils.disable_stdout_buffering()
	
	race = Model.newRace()
	race._populate()
	
	fnameRiderInfo = os.path.join(Utils.getHomeDir(), 'SimulationRiderData.xlsx')
	sheetName = 'RiderData'
	
	race.excelLink = ExcelLink()
	race.excelLink.setFileName( fnameRiderInfo )
	race.excelLink.setSheetName( sheetName )
	race.excelLink.setFieldCol( {'Bib#':0, 'LastName':1, 'FirstName':2, 'Team':3} )
	
	mainWin = wx.Frame(None, title="Primes", size=(800,700) )
	histogram = HistogramPanel( mainWin )
	mainWin.Show()
	
	histogram.refresh()
	app.MainLoop()

