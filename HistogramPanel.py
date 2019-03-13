import wx
import os
import six
import sys
import math
import bisect
import Utils
import Model
from ReadSignOnSheet	import ExcelLink
from FixCategories import FixCategories, SetCategory
from GetResults import GetResults
from Histogram import Histogram

class GetCategoryName( object ):
	def __init__( self, categories ):
		self.categories = categories
		self.lastCategory = categories[0]
		self.catName = {c:c.fullname for c in categories}
		
	def __call__( self, bib ):
		race = Model.race
		if race.inCategory( bib, self.lastCategory ):
			return self.catName[self.lastCategory]
		for c in self.categories:
			if race.inCategory( bib, c ):
				self.lastCategory = c
				return self.catName[c]
		return u''

class HistogramPanel( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize ):
		super(HistogramPanel, self).__init__( parent, id, size=size )
		self.category = None
		
		self.hbs = wx.BoxSizer( wx.HORIZONTAL )
		self.categoryLabel = wx.StaticText( self, label = _('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.hbs.Add( self.categoryLabel, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL, border=4 )
		
		self.hbs.Add( wx.StaticText(self, label=_('Lap')+u':'), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=24 )
		self.lapOption = wx.Choice(self, choices=[_('Last')])
		self.lapOption.SetSelection( 0 )
		self.lapOption.Bind( wx.EVT_CHOICE, self.doChooseLap )
		self.hbs.Add( self.lapOption, flag=wx.ALL, border=4 )
		self.lap = 0
		
		self.hbs.Add( wx.StaticText(self, label=_('Bin by')+u':'), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=24 )
		self.binOption = wx.Choice(self, choices=[_('Auto'), _('1 second'), _('30 seconds'), _('1 minute'), _('5 minutes')])
		self.binOption.SetSelection( 0 )
		self.binOption.Bind( wx.EVT_CHOICE, self.doChooseBinOption )
		self.hbs.Add( self.binOption, flag=wx.ALL, border=4 )
		
		self.hbs.Add( wx.StaticText(self, label=_('Bin width')+u':'), flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=24 )
		self.binWidthLabel = wx.StaticText( self )
		self.hbs.Add( self.binWidthLabel, 1, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=4 )
		
		self.histogram = Histogram( self )
		bs = wx.BoxSizer( wx.VERTICAL )
		
		bs.Add( self.hbs, 0, wx.EXPAND )
		bs.Add( self.histogram, 1, wx.EXPAND )
		
		self.SetDoubleBuffered( True )
		self.SetSizer( bs )
	
	def doChooseLap( self, event ):
		self.lap = self.lapOption.GetSelection()
		self.refresh()
		
	def fixBinWidth( self ):
		binWidthLabel = Utils.formatTime(self.histogram.binWidth or 0.0)
		if binWidthLabel != self.binWidthLabel.GetLabel():
			self.binWidthLabel.SetLabel( binWidthLabel )
			self.GetSizer().Layout()
	
	def doChooseBinOption( self, event ):
		self.histogram.SetBinOption( self.binOption.GetSelection() )
		self.fixBinWidth()
	
	def doChooseCategory( self, event ):
		Model.setCategoryChoice( self.categoryChoice.GetSelection(), 'histogramCategory' )
		self.lap = 0
		self.refresh()
	
	def refresh( self ):
		race = Model.race
		if not race:
			self.histogram.SetData( [], [], [] )
			return
		self.category = FixCategories( self.categoryChoice, getattr(race, 'histogramCategory', 0) )
		if self.category is None:
			categories = race.getCategories( startWaveOnly=True )
			if not categories:
				return
			getCatName = GetCategoryName( categories )
		elif self.category.catType == Model.Category.CatWave:
			components = race.getComponentCategories( self.category )
			if components:
				getCatName = GetCategoryName( components )
			else:
				def getCatName( bib, name=self.category.fullname ):
					return name		
		else:
			def getCatName( bib, name=self.category.fullname ):
				return name		
		
		results = GetResults( self.category )
		Finisher = Model.Rider.Finisher
		data, label, category = [], [], []
		maxLaps = None
		for rr in results:
			if rr.status != Finisher or not rr.raceTimes or len(rr.raceTimes) < 2:
				continue
			if maxLaps is None:
				if race.isRunning():
					maxLaps = bisect.bisect_left( rr.raceTimes, race.curRaceTime(), 0, len(rr.raceTimes)-1 )
				else:
					maxLaps = len(rr.raceTimes) - 1
				if self.lapOption.GetCount() != maxLaps + 1:
					self.lapOption.SetItems( [_('Last')] + [six.text_type(i) for i in six.moves.range(1,maxLaps+1)] )
					if self.lap >= self.lapOption.GetCount():
						self.lap = 0
					self.lapOption.SetSelection( self.lap )
				if self.lap:
					maxLaps = self.lap
			if len(rr.raceTimes) - 1 < maxLaps:
				continue
			data.append( rr.raceTimes[self.lap or -1] )
			label.append( u'{}: {}'.format(rr.num, rr.short_name()) )
			category.append( getCatName(rr.num) )
		self.histogram.SetData( data, label, category, self.binOption.GetSelection() )
		self.fixBinWidth()

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

