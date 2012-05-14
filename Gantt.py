import Model
import Utils
import wx
from FixCategories import FixCategories
import GanttChart
from GetResults import GetResults
from EditEntry import CorrectNumber, ShiftNumber, InsertNumber, DeleteEntry, SwapEntry

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
		
		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		
		self.ganttChart = GanttChart.GanttChart( self )
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
			entries = race.getRider(num).interpolate()
			try:
				self.entry = entries[iLap]
			except (IndexError, KeyError):
				return
		self.setNumSelect( num )
		if Utils.isMainWin():
			wx.CallAfter( Utils.getMainWin().setNumSelect, self.ganttChart.numSelect )
			
		self.iLap = iLap
		
		allCases = 0
		interpCase = 1
		nonInterpCase = 2
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				(wx.NewId(), 'Results', 	'Switch to Results tab', self.OnPopupResults, allCases),
				(wx.NewId(), 'RiderDetail',	'Switch to RiderDetail tab', self.OnPopupRiderDetail, allCases),
				(None, None, None, None),
				(wx.NewId(), 'Correct...',	'Change number or lap end time...',	self.OnPopupCorrect, interpCase),
				(wx.NewId(), 'Shift...',	'Move lap end time earlier/later...',	self.OnPopupShift, interpCase),
				(wx.NewId(), 'Delete...',	'Delete lap end time...',	self.OnPopupDelete, nonInterpCase),
			]
			for p in self.popupInfo:
				if p[0]:
					self.Bind( wx.EVT_MENU, p[3], id=p[0] )
		caseCode = 1 if entries[iLap].interp else 2
		
		menu = wx.Menu()
		for i, p in enumerate(self.popupInfo):
			if not p[0]:
				menu.AppendSeparator()
				continue
			if caseCode < p[4]:
				continue
			menu.Append( p[0], p[1], p[2] )
		
		self.PopupMenu( menu )
		menu.Destroy()

	def OnPopupCorrect( self, event ):
		CorrectNumber( self, self.entry )
		
	def OnPopupShift( self, event ):
		ShiftNumber( self, self.entry )

	def OnPopupDelete( self, event ):
		DeleteEntry( self, self.entry )

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
