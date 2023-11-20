import wx
import datetime

import Utils
import Model
from HighPrecisionTimeEdit import HighPrecisionTimeEdit
from Undo import undo

class ChangeRaceStartTimeDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id, "Change Race Start Time",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		race = Model.race
		if not race or not race.startTime:
			return
		
		bs = wx.GridBagSizer( vgap=4, hgap=4 )
		
		border = 4
		
		row = 0		
		timeNowEditWidth = 127

		#---------------------------------------------------------------

		if race.isRunning():
			label = wx.StaticText( self, label = _('Set Stopwatch Race Time:') )
			bs.Add( label, pos=(row,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.BOTTOM|wx.TOP|wx.ALIGN_CENTRE_VERTICAL )
			
			seconds = int( race.curRaceTime() ) + 10
			self.raceStopwatchTimeEdit = HighPrecisionTimeEdit( self, display_milliseconds=False, seconds=seconds, size=(timeNowEditWidth,-1) )
			self.raceStopwatchTimeEdit.SetMinSize( (timeNowEditWidth, -1) )
			bs.Add( self.raceStopwatchTimeEdit, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.BOTTOM|wx.TOP|wx.ALIGN_LEFT )
			
			self.setRaceStopwatchTime = wx.Button( self, id=wx.ID_OK )
			self.setRaceStopwatchTime.Bind( wx.EVT_BUTTON, self.onSetRaceStopwatchTime )
			bs.Add( self.setRaceStopwatchTime, pos=(row,2), span=(1,1), border = border, flag=wx.ALL )
			row += 1
		
		#---------------------------------------------------------------

		self.timeLabel = wx.StaticText( self, label = _('Start at Time of Day (24hr clock):') )
		bs.Add( self.timeLabel, pos=(row,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.BOTTOM|wx.TOP|wx.ALIGN_CENTRE_VERTICAL )
		
		timeNowEditWidth = 127
		seconds = (race.startTime - race.startTime.replace(hour=row, minute=row, second=0)).total_seconds()
		self.timeNowEdit = HighPrecisionTimeEdit( self, seconds = seconds, size=(timeNowEditWidth,-1) )
		self.timeNowEdit.SetMinSize( (timeNowEditWidth, -1) )
		bs.Add( self.timeNowEdit, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.BOTTOM|wx.TOP|wx.ALIGN_LEFT )
		
		self.setTime = wx.Button( self, id=wx.ID_OK )
		self.setTime.Bind( wx.EVT_BUTTON, self.onSetTime )
		bs.Add( self.setTime, pos=(row,2), span=(1,1), border = border, flag=wx.ALL )

		row += 1

		#---------------------------------------------------------------

		label = wx.StaticText( self, label = _('Start Earlier by:') )
		bs.Add( label, pos=(row,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.BOTTOM|wx.TOP|wx.ALIGN_CENTRE_VERTICAL )
		
		self.timeEarlierEdit = HighPrecisionTimeEdit( self, seconds = 0.0, size=(timeNowEditWidth,-1) )
		self.timeEarlierEdit.SetMinSize( (timeNowEditWidth, -1) )
		bs.Add( self.timeEarlierEdit, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.BOTTOM|wx.TOP|wx.ALIGN_LEFT )
		
		self.setTimeEarlier = wx.Button( self, id=wx.ID_OK )
		self.setTimeEarlier.Bind( wx.EVT_BUTTON, self.onSetTimeEarlier )
		bs.Add( self.setTimeEarlier, pos=(row,2), span=(1,1), border = border, flag=wx.ALL )
		row += 1
		
		#---------------------------------------------------------------
		
		label = wx.StaticText( self, label = _('Start Later by:') )
		bs.Add( label, pos=(row,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.BOTTOM|wx.TOP|wx.ALIGN_CENTRE_VERTICAL )

		self.timeLaterEdit = HighPrecisionTimeEdit( self, seconds = 0.0, size=(timeNowEditWidth,-1) )
		self.timeLaterEdit.SetMinSize( (timeNowEditWidth, -1) )
		bs.Add( self.timeLaterEdit, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.BOTTOM|wx.TOP|wx.ALIGN_LEFT )
		
		self.setTimeLater = wx.Button( self, id=wx.ID_OK )
		self.setTimeLater.Bind( wx.EVT_BUTTON, self.onSetTimeLater )
		bs.Add( self.setTimeLater, pos=(row,2), span=(1,1), border = border, flag=wx.ALL )
		row += 1
		
		
		#---------------------------------------------------------------
		
		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		bs.Add( self.cancelBtn, pos=(row, 1), span=(1,1), border = border, flag=wx.ALL )

		self.SetSizerAndFit( bs )
		bs.Fit( self )

		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )
		
	def onSetRaceStopwatchTime( self, event ):
		race = Model.race
		if race and race.startTime:
			self.onOK( event, race.startTime - datetime.timedelta(seconds=race.curRaceTime()-self.raceStopwatchTimeEdit.GetSeconds()) )

	def onSetTimeEarlier( self, event ):
		race = Model.race
		if race and race.startTime:
			self.onOK( event, race.startTime - datetime.timedelta(seconds=self.timeEarlierEdit.GetSeconds()) )

	def onSetTimeLater( self, event ):
		race = Model.race
		if race and race.startTime:
			self.onOK( event, race.startTime + datetime.timedelta(seconds=self.timeLaterEdit.GetSeconds()) )
		
	def onSetTime( self, event ):
		race = Model.race
		if race and race.startTime:
			self.onOK( event, race.startTime.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(seconds=self.timeNowEdit.GetSeconds() ) )

	def onOK( self, event, startTimeNew ):
		race = Model.race
		if not race or not race.startTime:
			return
		
		dTime = (startTimeNew - race.startTime).total_seconds()
		
		if dTime:		
			if dTime > 0.0 and not Utils.MessageOKCancel( self,
					_('Are you Sure you want to change the Race Start to Later?'), _('Are you sure?') ):
				return
			
			undo.pushState()
			
			# Adjust all rider times to account for the new start time.
			if race.isTimeTrial:
				for rider in race.riders.values():
					# Don't change the start times as they are relative to the old race start.
					# Increase all the recorded times (if an earlier start), otherwise decrease all the recorded times (if a later start).
					rider.times[:] = [max(0.0, v - dTime) for v in rider.times]
			else:
				for rider in race.riders.values():
					try:
						rider.firstTime = max( 0.0, rider.firstTime - dTime )
					except TypeError:
						pass
					rider.times[:] = [max(0.0, v - dTime) for v in rider.times]
			
				race.numTimeInfo.adjustAllTimes( -dTime )
				
			# Fix unmatched tags too.
			if race.unmatchedTags:
				for times in race.unmatchedTags.values():
					times[:] = [max(0.0, v - dTime) for v in times]
			
			race.startTime = startTimeNew
			race.setChanged()
			Utils.refresh()
		
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

if __name__ == '__main__':
	app = wx.App(False)
	Model.newRace()
	Model.race.enableJChipIntegration = False
	Model.race.isTimeTrial = False
	Model.race.startRaceNow()
	
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	dialog = ChangeRaceStartTimeDialog(mainWin)
	mainWin.Show()
	dialog.Show()
	app.MainLoop()
	
