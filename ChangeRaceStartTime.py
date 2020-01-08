import wx
import datetime

import Utils
import Model
from HighPrecisionTimeEdit import HighPrecisionTimeEdit
from Undo import undo

class ChangeRaceStartTimeDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Change Race Start Time",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		race = Model.race
		if not race:
			return
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		
		seconds = (race.startTime - race.startTime.replace(hour=0, minute=0, second=0)).total_seconds()
		self.timeMsEdit = HighPrecisionTimeEdit( self, seconds = seconds, size=(80,-1) )
		self.timeMsEdit.SetMinSize( (80, -1) )
		
		self.setTimeNow = wx.Button( self, label=_('Tap for NOW') )
		self.setTimeNow.Bind( wx.EVT_LEFT_DOWN, self.onSetTimeNow )
				
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		self.timeLabel = wx.StaticText( self, label = _('New Race Start Time (24hr clock):') )
		bs.Add( self.timeLabel,  pos=(0,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.BOTTOM|wx.TOP|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.timeMsEdit, pos=(0,1), span=(1,1), border = border, flag=wx.RIGHT|wx.BOTTOM|wx.TOP|wx.ALIGN_LEFT )
		bs.Add( self.setTimeNow, pos=(0,2), span=(1,1), border = border, flag=wx.ALL )
		
		bs.Add( self.okBtn, pos=(1, 1), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(1, 2), span=(1,1), border = border, flag=wx.ALL )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )

	def onSetTimeNow( self, event ):
		tNow = datetime.datetime.now()
		self.timeMsEdit.SetSeconds( (tNow - tNow.replace(hour=0, minute=0, second=0)).total_seconds() )
		event.Skip()

	def onOK( self, event ):
		race = Model.race
		if not race:
			return
		if race.isTimeTrial and race.hasRiderTimes():
			Utils.MessageOKCancel( self,
				_('Cannot change Time Trial Start Time') + u'\n\n' + _('There are already recorded results.'),
				_('Cannot change Start Time')
			)
			self.EndModal( wx.ID_OK )
		
		tOld = race.startTime
		startTimeNew = tOld.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(seconds=self.timeMsEdit.GetSeconds())
		dTime = (startTimeNew - race.startTime).total_seconds()
		
		if not dTime:
			return
		
		if dTime > 0.0 and not Utils.MessageOKCancel( self,
				_('Are you Sure you want to change the Race Start to Later?') + u'\n' + _('(you can always undo).'), _('Are you sure?') ):
			return
		
		undo.pushState()
		
		# Adjust all rider times to account for the new start time.
		if not race.isTimeTrial:
			for rider in race.riders.values():
				try:
					rider.firstTime = max( 0.0, rider.firstTime - dTime )
				except TypeError:
					pass
				rider.times[:] = [max(0.0, v - dTime) for v in rider.times]
		
			race.numTimeInfo.adjustAllTimes( -dTime )
			
			# Also fix any unread tags.
			if race.unmatchedTags:
				for times in race.unmatchedTags.values():
					times[:] = [max(0.0, v - dTime) for v in times]
		
		race.startTime = startTimeNew
		race.setChanged()
		Utils.refresh()
		
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
