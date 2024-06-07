import wx
import wx.lib.intctrl
import bisect
import datetime

import Model
import Utils
from GetResults import GetResults
from HighPrecisionTimeEdit import HighPrecisionTimeEdit

class SetLaps( wx.Dialog ):
	updateInterval = 5314
	
	def __init__( self, parent, category, id=wx.ID_ANY ):
		super().__init__( parent, id, _("Set Laps"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
		
		self.race = Model.getRace()
		self.category = self.race.getCategoryStartWave( category )
		
		font = wx.Font( wx.FontInfo(16) )
		
		fields = (
			('raceLaps', _('Race Laps'), wx.StaticText),
			(None, None, None),
			('winnerFinish', _('Winner Time'), wx.StaticText),
			('winnerDelta', _('Winner Time Delta'), wx.StaticText),
			('lastOnCourseFinish', _('Last on Course Time'), wx.StaticText),
			(None, None, None),
			('winnerClock', _('Winner Clock'), wx.StaticText),
			('lastOnCourseClock', _('Last on Course Clock'), wx.StaticText),
			(None, None, None),
			('timeElapsed', _('Race Time Elapsed'), wx.StaticText),
			('timeToGo', _('Race Time To Go'), wx.StaticText),
			(None, None, None),
			('lapsElapsed', _('Laps Elapsed'), wx.StaticText),
			('lapsToGo', _('Laps To Go'), wx.StaticText),
			('lapsTotal', _('Laps Total'), wx.StaticText),
		)
		
		self.fgs = wx.FlexGridSizer( cols=3, vgap=4, hgap=4 )
		self.fgs.AddGrowableCol( 1 )
		self.fgs.AddGrowableCol( 2 )
		
		self.fgs.Add( wx.StaticText(self) )
		self.fgs.Add( wx.StaticText(self, label=_('Current')), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.fgs.Add( wx.StaticText(self, label=_('Proposed')), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		
		class Column:	# Dummy class to hold column attributes.
			pass
		
		self.column = [Column(), Column()]
		for row, (field, label, fieldType) in enumerate(fields):
			if field is None:
				for c in range(3):
					self.fgs.Add( wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND )
				continue
			
			self.fgs.Add( wx.StaticText(self, label=label + ': '), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
			for c in range(2):
				ctrl = wx.lib.intctrl.IntCtrl(self, min=0, allow_none=True, limited=True, size=(64,-1)) if c == 1 and field == 'raceLaps' else fieldType(self)
				setattr( self.column[c], field, ctrl )
				self.fgs.Add( ctrl, flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
			
		self.column[1].raceLaps.SetValue( self.category._numLaps )
		self.column[1].raceLaps.Bind( wx.EVT_TEXT, self.onNewRaceLaps )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		self.title = wx.StaticText( self, label='Title' )
		self.title.SetFont( font )
		vs.Add( self.title, flag=wx.ALL, border=8 )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( wx.StaticText(self, label='{}:  '.format(_('Scheduled Race Duration')) ) )
		self.scheduledRaceDuration = wx.StaticText( self, label='6000 min (100:00:00)' )
		hs.Add( self.scheduledRaceDuration )
		vs.Add( hs, flag=wx.ALL, border=8 )
		
		# Add the fields for the early bell.
		for c in range(3):
			self.fgs.Add( wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND )
		self.fgs.Add( wx.StaticText(self, label=_('Early Bell')), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.earlyBellTime = HighPrecisionTimeEdit( self, allow_none=True, display_milliseconds=False )
		self.fgs.Add( self.earlyBellTime, flag=wx.ALIGN_CENTER_VERTICAL )
		self.earlyBellTimeButton = wx.Button( self, label=_('Tap for NOW') )
		self.earlyBellTimeButton.Bind( wx.EVT_LEFT_DOWN, self.setEarlyBellTime )
		self.fgs.Add( self.earlyBellTimeButton, flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		
		vs.Add( self.fgs, flag=wx.ALL, border=8 )
		
		btnSizer = self.CreateButtonSizer( wx.OK|wx.CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onOK, id=wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL )
		if btnSizer:
			vs.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border=4 )
		
		vs.Add( wx.StaticText(self) )
		
		self.updateTimer = wx.CallLater( self.updateInterval, self.onUpdateTimer )
		self.update()
		self.SetSizerAndFit( vs )
	
	def setEarlyBellTime( self, event ):
		race = Model.getRace()
		if race and race.isRunning():
			self.earlyBellTime.SetSeconds( race.curRaceTime() )
	
	def update( self, fromTimer=False ):
		Finisher = Model.Rider.Finisher
		race = Model.getRace()
		
		if self.category.numLaps:
			raceMinutes = None
		else:
			raceMinutes = (self.category.raceMinutes or race.minutes)
		
		self.title.SetLabel( self.category.fullname )
		self.scheduledRaceDuration.SetLabel( '{} min ({})'.format(raceMinutes, Utils.formatTime(raceMinutes * 60)) if raceMinutes else '' )
		
		categoryOffset = Utils.StrToSeconds(self.category.startOffset or '0')
		tStart = race.startTime + datetime.timedelta( seconds=categoryOffset )
		tCur = (race.curRaceTime() - categoryOffset) if race.isRunning() else -1

		def updateColumn( results, c ):
			self.column[c].timeElapsed.SetLabel( Utils.formatTime(tCur) if tCur > 0.0 else '')
			
			lapCur, winnerTime, winnerLaps, lastOnCourseTime = None, None, None, None
			for rr in results:
				if rr.status != Finisher or not rr.raceTimes:
					continue
				if winnerTime is None:
					winnerTime = rr.raceTimes[-1] - categoryOffset
					winnerLaps = len(rr.raceTimes) - 1
					lapCur = bisect.bisect_left( rr.raceTimes, tCur + categoryOffset ) if race.isRunning else winnerLaps

				lastOnCourseTime = max( lastOnCourseTime or 0.0, rr.raceTimes[-1] - categoryOffset )
			
			if c == 0:	# Current laps.
				self.column[c].raceLaps.SetLabel( '{}{}'.format(winnerLaps, ' ({})'.format(_('est')) if raceMinutes is not None else '') if winnerLaps else '' )

			self.column[c].timeToGo.SetLabel( Utils.formatTime(winnerTime - tCur) if winnerTime else '')
			
			self.column[c].winnerFinish.SetLabel( Utils.formatTime(winnerTime) if winnerTime else '' )
			self.column[c].lastOnCourseFinish.SetLabel( Utils.formatTime(lastOnCourseTime) if lastOnCourseTime else '' )
			
			delta = (winnerTime - raceMinutes*60.0) if winnerTime and raceMinutes else None
			if delta is not None:
				delta = ('+' if delta > 0.0 else '') + Utils.formatTime(delta)
			self.column[c].winnerDelta.SetLabel( delta or '' )

			self.column[c].winnerClock.SetLabel( (tStart + datetime.timedelta(seconds=winnerTime)).strftime('%H:%M:%S') if winnerTime else '' )
			self.column[c].lastOnCourseClock.SetLabel( (tStart + datetime.timedelta(seconds=lastOnCourseTime)).strftime('%H:%M:%S') if lastOnCourseTime else '' )
			
			self.column[c].lapsElapsed.SetLabel( str(lapCur) if lapCur else '' )
			self.column[c].lapsToGo.SetLabel( str(winnerLaps - lapCur) if winnerLaps else '' )
			self.column[c].lapsTotal.SetLabel( str(winnerLaps) if winnerLaps else '' )

		# Update the current race information.
		updateColumn( GetResults(self.category), 0 )
		
		# Swap in the new lap count and get the proposed results.
		# This is hacky.  Some thread in CrossMgr might pick up the proposed laps before we can put the model back the way it was.
		numLapsSave = self.category.numLaps
		self.category.numLaps = self.column[1].raceLaps.GetValue()
		race.setChanged()
		results = GetResults( self.category )
		
		# Put the model back the way it was.
		self.category.numLaps = numLapsSave
		race.setChanged()
		
		# Ensure that the rest of CrossMgr is showing the current laps.  It is unlikely that anything picked up the change, but you never know.
		Utils.refresh()

		# Update the proposed race information from the results we took earlier.
		updateColumn( results, 1 )
		
		# Update the earlyBellTime.
		if not fromTimer:
			self.earlyBellTime.SetSeconds( self.category.earlyBellTime )
		
		# Ensure that updated text is size adjusted.
		self.fgs.Layout()

	def onUpdateTimer( self ):
		self.update( fromTimer=True )
		self.updateTimer.Start( self.updateInterval )

	def onNewRaceLaps( self, event ):
		self.update()

	def onOK( self, event ):
		self.updateTimer.Stop()
		self.category._numLaps = self.column[1].raceLaps.GetValue()
		self.category.earlyBellTime = self.earlyBellTime.GetSeconds()
		race = Model.getRace()
		if race:
			race.setChanged()
		Utils.refresh()
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.updateTimer.Stop()
		self.EndModal( wx.ID_CANCEL )

if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan SetLaps", size=(1000,550))
	Model.setRace( Model.Race() )
	race = Model.getRace()
	race._populate()
	race.setCategories( [
		{'name':'test1', 'catStr':'100-199,999'+','+','.join('{}'.format(i) for i in range(1, 50, 2)),'gender':'Men'},
		{'name':'test2', 'catStr':'200-299,888', 'startOffset':'00:10', 'distance':'6'},
		{'name':'test3', 'catStr':'300-399', 'startOffset':'00:20','gender':'Women'},
		{'name':'test4', 'catStr':'400-499', 'startOffset':'00:30','gender':'Open'},
		{'name':'test5', 'catStr':'500-599', 'startOffset':'01:00','gender':'Men'},
	] )
	setLaps = SetLaps(mainWin, race.getCategories()[1])
	mainWin.Show()
	setLaps.ShowModal()
	app.MainLoop()
