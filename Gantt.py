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
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		self.statsLabel = wx.StaticText( self, wx.ID_ANY, '' )
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.statsLabel, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL | wx.GROW, border=4 )
		
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
		Utils.setCategoryChoice( self.categoryChoice.GetSelection(), 'ganttCategory' )
		self.refresh()
	
	def reset( self ):
		self.ganttChart.numSelect = None

	def setNumSelect( self, num ):
		self.ganttChart.numSelect = num if num is None else str(num)
	
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
				(wx.NewId(), 'Pull after Lap End...',	'Pull after lap end',		self.OnPopupPull, allCases),
				(wx.NewId(), 'DNF after Lap End...',	'DNF after lap end',		self.OnPopupDNF, allCases),
				(None, None, None, None, None),
				(wx.NewId(), 'Note...',					'Add/Edit Lap Note',		self.OnPopupLapNote, allCases),
				(None, None, None, None, None),
				(wx.NewId(), 'Correct Lap End Time...',	'Change number or lap end time',		self.OnPopupCorrect, interpCase),
				(wx.NewId(), 'Shift Lap End Time...',	'Move lap end time earlier/later',	self.OnPopupShift, interpCase),
				(wx.NewId(), 'Delete Lap End Time...',	'Delete lap end time',	self.OnPopupDelete, nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), 'Turn off Autocorrect...',	'Turn off Autocorrect',		self.OnPopupAutocorrect, allCases),
				(None, None, None, None, None),
				(wx.NewId(), 'Swap with Rider before',	'Swap with Rider before',	self.OnPopupSwapBefore, nonInterpCase),
				(wx.NewId(), 'Swap with Rider after',	'Swap with Rider after',	self.OnPopupSwapAfter, nonInterpCase),
				(None, None, None, None, None),
				(wx.NewId(), 'Show Lap Details...', 	'Show Lap Details',			self.OnPopupLapDetail, allCases),
				(None, None, None, None, None),
				(wx.NewId(), 'RiderDetail',				'Show RiderDetail Dialog',	self.OnPopupRiderDetail, allCases),
				(wx.NewId(), 'Results', 				'Switch to Results tab',	self.OnPopupResults, allCases),
				(wx.NewId(), 'Photos...', 				'Show Photos',				self.OnPopupPhotos, allCases),
			]
			self.splitMenuInfo = [
					(wx.NewId(),
					'%d Split%s' % (split-1, 's' if split > 2 else ''),
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
			if (name.endswith('before') and not self.numBefore) or (name.endswith('after') and not self.numAfter):
				continue
			menu.Append( id, name, text )
			
		if caseCode == 2:
			submenu = wx.Menu()
			for id, name, callback in self.splitMenuInfo:
				submenu.Append( id, name )
			Utils.addMissingSeparator( menu )
			menu.PrependSeparator()
			menu.PrependMenu( wx.NewId(), 'Add Missing Split', submenu )
			
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
		dlg = wx.NumberEntryDialog( self, message = "", caption = "Add Missing Splits", prompt = "Missing Splits to Add:",
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
			'Pull Rider %d at %s after lap %d?' % (self.entry.num, Utils.formatTime(self.entry.t+1, True), self.entry.lap),
			'Pull Rider' ):
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
			'DNF Rider %d at %s after lap %d?' % (self.entry.num, Utils.formatTime(self.entry.t+1, True), self.entry.lap),
			'DNF Rider' ):
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
			'Turn off Autocorrect for Rider %d?' % self.entry.num,
			'Turn off Autocorrect' ):
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
		dlg = wx.TextEntryDialog( self, "Note for Rider %d on Lap %d:" % (self.entry.num, self.entry.lap), "Lap Note",
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
				riderName = '%s, %s %d' % (riderInfo['LastName'], riderInfo['FirstName'], self.entryEnd.num)
			except KeyError:
				try:
					riderName = '%s %d' % (riderInfo['LastName'], self.entryEnd.num)
				except KeyError:
					try:
						riderName = '%s %d' % (riderInfo['FirstName'], self.entryEnd.num)
					except KeyError:
						riderName = str(self.entryEnd.num)
						
			if leaderEntryStart:
				tDown = tLapStart - leaderEntryStart.t
				infoDownStart = '\nLap Start %s down from leader %d' % (Utils.formatTime(tDown, True), leaderEntryStart.num)
			else:
				infoDownStart = ''
			if leaderEntryEnd:
				tDown = tLapEnd - leaderEntryEnd.t
				infoDownEnd = '\nLap End %s down from leader %d' % (Utils.formatTime(tDown, True), leaderEntryStart.num)
			else:
				infoDownEnd = ''
				
			infoStart = race.numTimeInfo.getInfoStr( self.entryStart.num, tLapStart )
			if infoStart:
				infoStart = '\nLap Start ' + infoStart
			infoEnd = race.numTimeInfo.getInfoStr( self.entryEnd.num, tLapEnd )
			if infoEnd:
				infoEnd = '\nLap End ' + infoEnd
		
			info = ('Rider: %s  Lap: %d\nLap Start:  %s Lap End: %s\nLap Time: %s\n%s%s%s%s' %
					(riderName, self.entryEnd.lap,
					Utils.formatTime(tLapStart),
					Utils.formatTime(tLapEnd),
					Utils.formatTime(tLapEnd - tLapStart),
					infoDownStart, infoDownEnd, infoStart, infoEnd )).strip()
					
		Utils.MessageOK( self, info, 'Lap Details' )
		
	def OnPopupResults( self, event ):
		if Utils.isMainWin():
			Utils.getMainWin().showPageName( 'Results' )
			
	def OnPopupRiderDetail( self, event ):
		ShowRiderDetailDialog( self, self.numSelect )
		
	def OnPopupPhotos( self, event ):
		mainWin = Utils.mainWin
		if not mainWin:
			return
		mainWin.photoDialog.Show( True )
		mainWin.photoDialog.setNumSelect( self.numSelect )
		
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
				projected	+= sum( 1 for i, n in enumerate(r.interp)	if n and r.raceTimes[i] < tCur )
			if total:
				toPercent = 100.0 / float(total)
				s = '  Total Entries: %d    Projected: %d (%.2f%%)    Edited: %d (%.2f%%)    Projected or Edited: %d (%.2f%%)    Photos: %d' % (
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
