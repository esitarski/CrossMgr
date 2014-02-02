import Utils
from Utils				import logCall
import wx
import wx.lib.intctrl
import Model
from HighPrecisionTimeEdit import HighPrecisionTimeEdit
from Undo import undo
import random
import datetime

#------------------------------------------------------------------------------------------------
class CorrectNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Correct Number",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		self.numEdit = wx.lib.intctrl.IntCtrl( self, size=(64,-1), style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		
		self.timeMsEdit = HighPrecisionTimeEdit( self, seconds = entry.t )
				
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		bs.Add( wx.StaticText( self, label = _('RiderLap: {}   RaceTime: {}').format(self.entry.lap, Utils.formatTime(self.entry.t, True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, label = _("Rider:")),  pos=(1,0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.numEdit, pos=(1,1), span=(1,2), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		choices = [_("Race Time:")]
		if Model.race and Model.race.startTime:
			choices.append( _("24 hr Clock Time:") )
		self.timeChoice = wx.Choice( self, -1, choices = choices )
		self.timeChoiceLastSelection = 0
		self.timeChoice.SetSelection( self.timeChoiceLastSelection )
		self.timeChoice.Bind( wx.EVT_CHOICE, self.doTimeChoice, self.timeChoice )
		bs.Add( self.timeChoice,  pos=(2,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.timeMsEdit, pos=(2,1), span=(1,1), border = border, flag=wx.RIGHT|wx.BOTTOM|wx.ALIGN_LEFT )
		
		bs.Add( self.okBtn, pos=(3, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(3, 1), span=(1,1), border = border, flag=wx.ALL )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def doTimeChoice( self, event ):
		iSelection = event.GetSelection()
		if iSelection == self.timeChoiceLastSelection:
			return
		if not (Model.race and Model.race.startTime):
			return
			
		dtStart = Model.race.startTime
		t = self.timeMsEdit.GetSeconds()
		if iSelection == 0:
			# Clock time to race time.
			dtInput = datetime.datetime(dtStart.year, dtStart.month, dtStart.day) + datetime.timedelta(seconds = t)
			t = (dtInput - dtStart).total_seconds()
		else:
			# Race time to clock time.
			dtInput = dtStart + datetime.timedelta( seconds = t )
			t = (dtInput - datetime.datetime(dtStart.year, dtStart.month, dtStart.day)).total_seconds()
		
		self.timeMsEdit.SetSeconds( t )
		self.timeChoiceLastSelection = iSelection
		
	def onOK( self, event ):
		num = self.numEdit.GetValue()
		t = self.timeMsEdit.GetSeconds()
		
		if self.timeChoice.GetSelection() == 1 and Model.race and Model.race.startTime:
			dtStart = Model.race.startTime
			dtInput = datetime.datetime(dtStart.year, dtStart.month, dtStart.day) + datetime.timedelta(seconds = t)
			if dtInput < dtStart:
				Utils.MessageOK( self, _('Cannot Enter Clock Time Before Race Start.\n\n(reminder: clock time is in 24-hour format)'),
										_('Time Entry Error'), iconMask = wx.ICON_ERROR )
				return
			t = (dtInput - dtStart).total_seconds()
			
		if self.entry.num != num or self.entry.t != t:
			undo.pushState()
			with Model.LockRace() as race:
				rider = race.getRider( num )
				if self.entry.lap != 0:
					race.numTimeInfo.change( self.entry.num, self.entry.t, t )
					race.deleteTime( self.entry.num, self.entry.t )
					race.addTime( num, t + (rider.firstTime if getattr(race, 'isTimeTrial', False) and getattr(rider, 'firstTime', None) is not None else 0.0) )
				else:
					race.numTimeInfo.change( self.entry.num, rider.firstTime, t )
					rider.firstTime = t
					race.setChanged()
			Utils.refresh()
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

#------------------------------------------------------------------------------------------------
class ShiftNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Shift Time",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		self.numEdit = wx.lib.intctrl.IntCtrl( self, size=(40, -1),
			style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER,
			value=int(self.entry.num),
			allow_none=False, min=1, max=9999 )
		
		self.timeMsEdit = HighPrecisionTimeEdit( self )
		self.timeMsEdit.Bind( wx.EVT_TEXT, self.updateNewTime )
		self.newTime = wx.StaticText( self, label = u"00:00:00")
		
		shiftOptions = [_('Earlier'), _('Later')]
		self.shiftBox = wx.RadioBox( self, wx.ID_ANY,
			_('Shift Direction'),
			wx.DefaultPosition, wx.DefaultSize,
			shiftOptions, 2, wx.RA_SPECIFY_COLS )
		self.Bind(wx.EVT_RADIOBOX, self.updateNewTime, self.shiftBox)
				
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		bs.Add( wx.StaticText( self, label = _('RiderLap: {}   RaceTime: {}').format(self.entry.lap, Utils.formatTime(self.entry.t,True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, label = _("Rider:")),  pos=(1,0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit, pos=(1,1), span=(1,2), border = border, flag=wx.GROW|wx.RIGHT|wx.TOP )
		bs.Add( self.shiftBox, pos=(2, 0), span=(1, 2), border = border, flag=wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM )
		bs.Add( wx.StaticText( self, label = _("Shift Time:")),  pos=(3,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.BOTTOM )
		bs.Add( self.timeMsEdit, pos=(3,1), span=(1,1), border = border, flag=wx.GROW|wx.LEFT|wx.RIGHT )
		bs.Add( self.newTime, pos=(4,0), span=(1,2), border = border, flag=wx.GROW|wx.LEFT|wx.RIGHT )
		
		bs.Add( self.okBtn, pos=(5, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(5, 1), span=(1,1), border = border, flag=wx.ALL )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		wx.CallAfter( self.updateNewTime )
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def getNewTime( self ):
		tAdjust = self.timeMsEdit.GetSeconds() * (-1 if self.shiftBox.GetSelection() == 0 else 1)
		return self.entry.t + tAdjust

	def onOK( self, event ):
		num = self.numEdit.GetValue()
		t = self.getNewTime()
		if self.entry.num != num or self.entry.t != t:
			undo.pushState()
			with Model.LockRace() as race:
				rider = race.getRider( num )
				if self.entry.lap != 0:
					race.numTimeInfo.change( self.entry.num, self.entry.t, t )
					race.deleteTime( self.entry.num, self.entry.t )
					race.addTime( num, t + (rider.firstTime if getattr(race, 'isTimeTrial', False) and getattr(rider, 'firstTime', None) is not None else 0.0) )
				else:
					race.numTimeInfo.change( self.entry.num, rider.firstTime, t )
					rider.firstTime = t
					race.setChanged()
			Utils.refresh()
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
		
	def updateNewTime( self, event = None ):
		s = _('Was: {}  Now: {}').format(Utils.formatTime(self.entry.t,True), Utils.formatTime(self.getNewTime(),True) )
		self.newTime.SetLabel( s )

#------------------------------------------------------------------------------------------------
class InsertNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Insert Number",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		
		self.numEdit = wx.lib.intctrl.IntCtrl( self, wx.ID_ANY, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		bs.Add( wx.StaticText( self, label = _('RiderLap: {}   RaceTime: {}').format(self.entry.lap, Utils.formatTime(self.entry.t, True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, label = _('Original:') ),
				pos=(1,0), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( wx.StaticText( self, label = u'{}'.format(self.entry.num) ),
				pos=(1,1), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_BOTTOM )
		
		shiftOptions = [_('Before Entry'), _('After Entry')]
		self.beforeAfterBox = wx.RadioBox( self, wx.ID_ANY, _('Insert'), wx.DefaultPosition, wx.DefaultSize, shiftOptions, 2, wx.RA_SPECIFY_COLS )
		bs.Add( self.beforeAfterBox, pos=(2,0), span=(1,2), border = border, flag=wx.TOP|wx.LEFT|wx.ALIGN_RIGHT )
				
		bs.Add( wx.StaticText( self, label = _('Number:') ),
				pos=(3,0), span=(1,1), border = border, flag=wx.TOP|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit,
				pos=(3,1), span=(1,1), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_BOTTOM )
				
		bs.Add( self.okBtn, pos=(4, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(4, 1), span=(1,1), border = border, flag=wx.ALL|wx.ALIGN_RIGHT )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onOK( self, event ):
		num = self.numEdit.GetValue()
		if not num or num == self.entry.num:
			return
			
		tAdjust = 0.0001 + random.random() / 10000.0	# Add some randomness so that all inserted times will be unique.
		if self.beforeAfterBox.GetSelection() == 0:
			tAdjust = -tAdjust
		tInsert = self.entry.t + tAdjust
		
		undo.pushState()
		with Model.LockRace() as race:
			rider = race.getRider( num )
			race.numTimeInfo.add( num, tInsert )
			race.addTime( num, tInsert + (rider.firstTime if getattr(race, 'isTimeTrial', False) and getattr(rider, 'firstTime', None) is not None else 0.0) )
			
		Utils.refresh()
		
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

#------------------------------------------------------------------------------------------------
class SplitNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Split Number",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		
		self.numEdit1 = wx.lib.intctrl.IntCtrl( self, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		self.numEdit2 = wx.lib.intctrl.IntCtrl( self, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		bs.Add( wx.StaticText( self, label = _('RiderLap: {}   RaceTime: {}').format(self.entry.lap, Utils.formatTime(self.entry.t, True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, label = _('Num1:') ),
				pos=(1,0), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit1,
				pos=(1,1), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_BOTTOM )

		bs.Add( wx.StaticText( self, label =_('Num2:') ),
				pos=(2,0), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit2,
				pos=(2,1), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_BOTTOM )
		
		bs.Add( self.okBtn, pos=(3, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(3, 1), span=(1,1), border = border, flag=wx.ALL|wx.ALIGN_RIGHT )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onOK( self, event ):
		num1 = self.numEdit1.GetValue()
		num2 = self.numEdit2.GetValue()
		if not num1 or not num2 or num1 == num2:
			return
			
		t1 = self.entry.t
		t2 = self.entry.t + 0.0001 * random.random()
		
		undo.pushState()
		with Model.LockRace() as race:
			rider = race.getRider( self.entry.num )

			race.numTimeInfo.delete( self.entry.num, self.entry.t )
			race.numTimeInfo.add( num1, t1 )
			race.numTimeInfo.add( num2, t2 )
			
			race.deleteTime( self.entry.num, self.entry.t )
			race.addTime( num1, t1 + (rider.firstTime if getattr(race, 'isTimeTrial', False) and getattr(rider, 'firstTime', None) is not None else 0.0) )
			race.addTime( num2, t2 + (rider.firstTime if getattr(race, 'isTimeTrial', False) and getattr(rider, 'firstTime', None) is not None else 0.0) )
			
		Utils.refresh()
		
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

#------------------------------------------------------------------------------------------------

@logCall
def CorrectNumber( parent, entry ):
	dlg = CorrectNumberDialog( parent, entry )
	dlg.ShowModal()
	dlg.Destroy()
		
@logCall
def ShiftNumber( parent, entry ):
	dlg = ShiftNumberDialog( parent, entry )
	dlg.ShowModal()
	dlg.Destroy()
		
@logCall
def InsertNumber( parent, entry ):
	dlg = InsertNumberDialog( parent, entry )
	dlg.ShowModal()
	dlg.Destroy()
		
@logCall
def SplitNumber( parent, entry ):
	if entry.lap == 0:
		return
		
	dlg = SplitNumberDialog( parent, entry )
	dlg.ShowModal()
	dlg.Destroy()
		
@logCall
def DeleteEntry( parent, entry ):
	if entry.lap == 0:
		return
		
	dlg = wx.MessageDialog(parent,
						   _('Num: {}  Lap: {}   RaceTime: {}\n\nConfirm Delete?').format(
								entry.num, entry.lap, Utils.formatTime(entry.t, True)), _('Delete Entry'),
							wx.OK | wx.CANCEL | wx.ICON_QUESTION )
	# dlg.CentreOnParent(wx.BOTH)
	if dlg.ShowModal() == wx.ID_OK:
		undo.pushState()
		with Model.LockRace() as race:
			if race:
				race.numTimeInfo.delete( entry.num, entry.t )
				race.deleteTime( entry.num, entry.t )
		Utils.refresh()
	dlg.Destroy()
	
@logCall
def SwapEntry( a, b ):
	race = Model.race
	if not race:
		return
		
	riderA = race.getRider( a.num )
	riderB = race.getRider( b.num )
	
	race.numTimeInfo.change( a.num, a.t, b.t, Model.NumTimeInfo.Swap )
	race.numTimeInfo.change( b.num, b.t, a.t, Model.NumTimeInfo.Swap )
	
	race.deleteTime( a.num, a.t )
	race.deleteTime( b.num, b.t )
	race.addTime( a.num, b.t + (riderB.firstTime if getattr(race, 'isTimeTrial', False) and riderB.firstTime is not None else 0.0) )
	race.addTime( b.num, a.t + (riderA.firstTime if getattr(race, 'isTimeTrial', False) and riderA.firstTime is not None else 0.0) )

def DoStatusChange( parent, num, message, title, newStatus ):
	if num is None or not Utils.MessageOKCancel(parent, message.format(num), title):
		return False
	undo.pushState()
	with Model.LockRace() as race:
		if not race:
			return False
		rider = race.getRider( num )
		rider.setStatus( newStatus )
		race.setChanged()
	Utils.refresh()
	return True

@logCall
def DoDNF( parent, num ):
	return DoStatusChange( parent, num, _('DNF rider {}?'), _('Confirm Did Not FINISH'), Model.Rider.DNF )

@logCall
def DoPull( parent, num ):
	return DoStatusChange( parent, num, _('Pull rider {}?'), _('Confirm PULL Rider'), Model.Rider.Pulled )

@logCall
def DoDNS( parent, num ):
	return DoStatusChange( parent, num, _('DNS rider {}?'), _('Confirm Did Not START'), Model.Rider.DNS )

@logCall
def DoDQ( parent, num ):
	return DoStatusChange( parent, num, _('DQ rider {}?'), _('Confirm Disqualify'), Model.Rider.DQ )
	
@logCall
def AddLapSplits( num, lap, times, splits ):
	undo.pushState()
	with Model.LockRace() as race:
		try:
			tLeft = times[lap-1]
			tRight = times[lap]
			splitTime = (tRight - tLeft) / float(splits)
			for i in xrange( 1, splits ):
				newTime = tLeft + splitTime * i
				race.numTimeInfo.add( num, newTime, Model.NumTimeInfo.Split )
				race.addTime( num, newTime )
			return True
		except (TypeError, KeyError, ValueError, IndexError):
			return False
