import wx
import Model
import Utils
from FixCategories import FixCategories
import GanttChartPanel
from GetResults import GetResults, RidersCanSwap
from Undo import undo
import EditEntry

def UpdateSetNum( num ):
	if num is None:
		return
	from RiderDetail import ShowRiderDetailDialog
	mainWin = Utils.getMainWin()
	mainWin.setNumSelect( num )
	ShowRiderDetailDialog( mainWin, num )

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
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, _('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		self.statsLabel = wx.StaticText( self, wx.ID_ANY, '' )
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.statsLabel, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL | wx.GROW, border=4 )
		
		self.ganttChart = GanttChartPanel.GanttChartPanel( self )
		self.ganttChart.dClickCallback = UpdateSetNum
		self.ganttChart.rClickCallback = self.onRightClick
		#self.ganttChart.lClickCallback = self.onLeftClick
		self.ganttChart.getNowTimeCallback = GetNowTime

		bs = wx.BoxSizer(wx.VERTICAL)
		bs.Add(self.hbs, flag=wx.GROW|wx.HORIZONTAL)
		bs.Add(self.ganttChart, 1, wx.GROW|wx.ALL, 5)
		self.SetSizer(bs)
		bs.SetSizeHints(self)

	def doChooseCategory( self, event ):
		Utils.setCategoryChoice( self.categoryChoice.GetSelection(), 'ganttCategory' )
		self.refresh()
	
	def reset( self ):
		self.ganttChart.numSelect = None

	def setNumSelect( self, num ):
		self.ganttChart.numSelect = num if num is None else '{}'.format(num)
	
	def onLeftClick( self, xPos, yPos, num, iRider, iLap, t ):
		if not Utils.mainWin:
			return
		Utils.mainWin.photoDialog.Show( True )
		Utils.mainWin.photoDialog.refresh( num, t )
		
	def onRightClick( self, xPos, yPos, num, iRider, iLap ):
		with Model.LockRace() as race:
			if not race or num not in race:
				return
			category = FixCategories( self.categoryChoice, getattr(race, 'ganttCategory', 0) )
			entries = race.getRider(num).interpolate()
			try:
				self.entry = entries[iLap]
				self.entryStart = entries[iLap-1]
				self.entryEnd = self.entry
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
				(wx.NewId(), _('Pull after Lap End...'),	_('Pull after lap end'),		self.OnPopupPull, allCases),
				(wx.NewId(), _('DNF after Lap End...'),		_('DNF after lap end'),			self.OnPopupDNF, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Note...'),					_('Add/Edit Lap Note'),			self.OnPopupLapNote, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Correct Lap End Time...'),	_('Change number or lap end time'),		self.OnPopupCorrect, interpCase),
				(wx.NewId(), _('Shift Lap End Time...'),	_('Move lap end time earlier/later'),	self.OnPopupShift, interpCase),
				(wx.NewId(), _('Delete Lap End Time...'),	_('Delete lap end time'),		self.OnPopupDelete, nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), _('Turn off Autocorrect...'),	_('Turn off Autocorrect'),		self.OnPopupAutocorrect, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Swap with Rider before'),	_('Swap with Rider before'),	self.OnPopupSwapBefore, nonInterpCase),
				(wx.NewId(), _('Swap with Rider after'),	_('Swap with Rider after'),		self.OnPopupSwapAfter, nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), _('Show Lap Details...'), 		_('Show Lap Details'),			self.OnPopupLapDetail, allCases),
				(None, None, None, None, None),
				(wx.NewId(), _('Photos...'), 				_('Show Photos'),				self.OnPopupPhotos, allCases),
				(wx.NewId(), _('RiderDetail'),				_('Show RiderDetail Dialog'),	self.OnPopupRiderDetail, allCases),
				(wx.NewId(), _('Results'), 					_('Switch to Results tab'),		self.OnPopupResults, allCases),
			]
			self.splitMenuInfo = [
					(wx.NewId(),
					_('{} Split(s)').format(split-1),
					lambda evt, s = self, splits = split: s.doSplitLap(splits)) for split in xrange(2,8) ] + [
					(wx.NewId(),
					'Custom...',
					lambda evt, s = self: s.doCustomSplitLap())]
			for id, name, text, callback, cCase in self.popupInfo:
				if id:
					self.Bind( wx.EVT_MENU, callback, id=id )
			for id, name, callback in self.splitMenuInfo:
				self.Bind( wx.EVT_MENU, callback, id=id )
				
		caseCode = 1 if entries[iLap].interp else 2
		
		riderResults = dict( (r.num, r) for r in GetResults(category) )
		
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
			if (_('before') in name and not self.numBefore) or (_('after') in name and not self.numAfter):
				continue
			menu.Append( id, name, text )
			
		if caseCode == 2:
			submenu = wx.Menu()
			for id, name, callback in self.splitMenuInfo:
				submenu.Append( id, name )
			Utils.addMissingSeparator( menu )
			menu.PrependSeparator()
			menu.PrependMenu( wx.NewId(), _('Add Missing Split'), submenu )
			
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
		
	def doCustomSplitLap( self ):
		dlg = wx.NumberEntryDialog( self, message = "", caption = _("Add Missing Splits"), prompt = _("Missing Splits to Add:"),
									value = 1, min = 1, max = 500 )
		splits = None
		if dlg.ShowModal() == wx.ID_OK:
			splits = dlg.GetValue() + 1
		dlg.Destroy()
		if splits is not None:
			self.doSplitLap( splits )
		
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
			category = FixCategories( self.categoryChoice, getattr(race, 'ganttCategory', 0) )
			
		riderResults = dict( (r.num, r) for r in GetResults(category) )
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

	def OnPopupPull( self, event ):
		if not self.entry:
			return
		if not Utils.MessageOKCancel( self,
			_('Pull Rider {} at {} after lap {}?').format(self.entry.num, Utils.formatTime(self.entry.t+1, True), self.entry.lap),
			_('Pull Rider') ):
			return
		try:
			undo.pushState()
			with Model.LockRace() as race:
				if not race:
					return
				race.getRider(self.entry.num).setStatus( Model.Rider.Pulled, self.entry.t + 1 )
				race.setChanged()
		except:
			pass
		wx.CallAfter( self.refresh )
		
	def OnPopupDNF( self, event ):
		if not self.entry:
			return
		if not Utils.MessageOKCancel( self,
			_('DNF Rider {} at {} after lap {}?').format(self.entry.num, Utils.formatTime(self.entry.t+1, True), self.entry.lap),
			_('DNF Rider') ):
			return
		try:
			undo.pushState()
			with Model.LockRace() as race:
				if not race:
					return
				race.getRider(self.entry.num).setStatus( Model.Rider.DNF, self.entry.t + 1 )
				race.setChanged()
		except:
			pass
		wx.CallAfter( self.refresh )
		
	def OnPopupAutocorrect( self, event ):
		if not self.entry:
			return
		if not Utils.MessageOKCancel( self,
			_('Turn off Autocorrect for Rider {}?').format(self.entry.num),
			_('Turn off Autocorrect') ):
			return
		try:
			undo.pushState()
			with Model.LockRace() as race:
				if not race:
					return
				race.getRider(self.entry.num).setAutoCorrect( False )
				race.setChanged()
		except:
			pass
		wx.CallAfter( self.refresh )
	
	def OnPopupLapNote( self, event ):
		if not self.entry or not Model.race:
			return
		if not hasattr(Model.race, 'lapNote'):
			Model.race.lapNote = {}
		dlg = wx.TextEntryDialog( self, _("Note for Rider {} on Lap {}:").format(self.entry.num, self.entry.lap), _("Lap Note"),
					Model.race.lapNote.get( (self.entry.num, self.entry.lap), '' ) )
		ret = dlg.ShowModal()
		value = dlg.GetValue().strip()
		dlg.Destroy()
		if ret != wx.ID_OK:
			return
		undo.pushState()
		with Model.LockRace() as race:
			if value:
				race.lapNote[(self.entry.num, self.entry.lap)] = value
				race.setChanged()
			else:
				try:
					del race.lapNote[(self.entry.num, self.entry.lap)]
					race.setChanged()
				except KeyError:
					pass
		wx.CallAfter( self.refresh )
	
	def OnPopupLapDetail( self, event ):
		with Model.LockRace() as race:
			if not race:
				return
			tLapStart = self.entryStart.t
			tLapEnd = self.entryEnd.t
			
			iLap = self.entryStart.lap
			try:
				leaderNum = GanttChartPanel.numFromLabel( self.ganttChart.labels[0] )
				leaderEntries = race.getRider(leaderNum).interpolate()
				leaderEntryStart = leaderEntries[self.entryStart.lap]
				leaderEntryEnd = leaderEntries[self.entryEnd.lap]
			except:
				leaderEntryStart = None
				leaderEntryEnd = None
		
			try:
				riderInfo = race.excelLink.read()[self.entryEnd.num]
			except:
				riderInfo = {}
				
			try:
				riderName = u'{}, {} {}'.format(riderInfo['LastName'], riderInfo['FirstName'], self.entryEnd.num)
			except KeyError:
				try:
					riderName = u'{} {}'.format(riderInfo['LastName'], self.entryEnd.num)
				except KeyError:
					try:
						riderName = u'{} {}'.format(riderInfo['FirstName'], self.entryEnd.num)
					except KeyError:
						riderName = u'{}'.format(self.entryEnd.num)
						
			if leaderEntryStart:
				tDown = tLapStart - leaderEntryStart.t
				infoDownStart = _('\nLap Start {} down from leader {}').format(Utils.formatTime(tDown, True), leaderEntryStart.num)
			else:
				infoDownStart = ''
			if leaderEntryEnd:
				tDown = tLapEnd - leaderEntryEnd.t
				infoDownEnd = _('\nLap End {} down from leader {}').format(Utils.formatTime(tDown, True), leaderEntryStart.num)
			else:
				infoDownEnd = ''
				
			infoStart = race.numTimeInfo.getInfoStr( self.entryStart.num, tLapStart )
			if infoStart:
				infoStart = _('\nLap Start ') + infoStart
			infoEnd = race.numTimeInfo.getInfoStr( self.entryEnd.num, tLapEnd )
			if infoEnd:
				infoEnd = _('\nLap End ') + infoEnd
		
			info = (_('Rider: {}  Lap: {}\nLap Start:  {} Lap End: {}\nLap Time: {}\n{}{}{}{}').format(
					riderName, self.entryEnd.lap,
					Utils.formatTime(tLapStart),
					Utils.formatTime(tLapEnd),
					Utils.formatTime(tLapEnd - tLapStart),
					infoDownStart, infoDownEnd, infoStart, infoEnd )).strip()
					
		Utils.MessageOK( self, info, _('Lap Details') )
		
	def OnPopupResults( self, event ):
		if Utils.isMainWin():
			Utils.getMainWin().showPageName( _('Results') )
			
	def OnPopupRiderDetail( self, event ):
		from RiderDetail import ShowRiderDetailDialog
		ShowRiderDetailDialog( self, self.numSelect )
		
	def OnPopupPhotos( self, event ):
		mainWin = Utils.mainWin
		if not mainWin:
			return
		mainWin.photoDialog.Show( True )
		mainWin.photoDialog.refresh( self.numSelect, self.entryEnd.t if self.entryEnd else None )
		
	def updateStats( self, results ):
		s = ''
		if results:
			total, projected, edited = 0, 0, 0
			getInfo = Model.race.numTimeInfo.getInfo if getattr(Model.race, 'numTimeInfo', None) else lambda num, t: False
			if Model.race.isRunning():
				tCur = Model.race.curRaceTime()
			else:
				tCur = 10.0*24.0*60.0*60.0
			for r in results:
				if not r.raceTimes:
					continue
				total		+= sum( 1 for t in r.raceTimes				if t < tCur ) - 1
				edited		+= sum( 1 for t in r.raceTimes				if t < tCur and getInfo(r.num, t) is not None )
				projected	+= sum( 1 for i, n in enumerate(r.interp)	if n and i < len(r.raceTimes) and r.raceTimes[i] < tCur )
			if total:
				toPercent = 100.0 / float(total)
				s = _('  Total Entries: {}    Projected: {} ({:.2f}%)    Edited: {} ({:.2f}%)    Projected or Edited: {} ({:.2f}%)    Photos: %d').format(
						total,
						projected,			projected			* toPercent,
						edited,				edited				* toPercent,
						edited+projected,	(edited+projected)	* toPercent,
						getattr(Model.race, 'photoCount', 0) )
			
		self.statsLabel.SetLabel( s )
		self.hbs.Layout()
		
	def refresh( self ):
		if not Model.race:
			self.ganttChart.SetData( None )
			self.updateStats( None )
			return
		
		category = FixCategories( self.categoryChoice, getattr(Model.race, 'ganttCategory', 0) )
		results = GetResults( category, True )
		
		#labels	= ['{}'.format(r.num) for r in results]
		labels = []
		for r in results:
			last = getattr(r, 'LastName', None)
			first = getattr(r, 'FirstName', None)
			if last and first:
				labels.append( u'{}, {} {}'.format(last, first, r.num) )
			elif first:
				labels.append( u'{} {}'.format(first, r.num) )
			elif last:
				labels.append( u'{} {}'.format(last, r.num) )
			else:
				labels.append( u'{}'.format(r.num) )
			
		data	= [r.raceTimes for r in results]
		interp	= [r.interp for r in results]
		self.ganttChart.SetData(data, labels, GetNowTime(), interp,
								set(i for i, r in enumerate(results) if r.status != Model.Rider.Finisher),
								Model.race.numTimeInfo,
								getattr( Model.race, 'lapNote', None) )
		self.updateStats( results )
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
