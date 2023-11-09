import Utils
from Utils				import logCall
import wx
import wx.lib.intctrl
import Model
from HighPrecisionTimeEdit import HighPrecisionTimeEdit
from Undo import undo
import sys
import random
import datetime

#------------------------------------------------------------------------------------------------
class CorrectNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		super().__init__( parent, id, "Correct Number",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		self.numEdit = wx.lib.intctrl.IntCtrl( self, size=(64,-1), style=wx.TE_RIGHT, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		
		border = 4
		bs.Add( wx.StaticText( self, label = '{}: {}   {}: {}'.format(
				_('Rider Lap'), self.entry.lap,
				_('Race Time'), Utils.formatTime(self.entry.t, True)
			)),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, label = '{}:'.format(_("Rider"))),  pos=(1,0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.numEdit, pos=(1,1), span=(1,2), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		choices = ['{}:'.format(_("Race Time"))]
		self.timeChoiceLastSelection = 0
		race = Model.race
		if race and race.startTime:
			choices.append( _("24 hr Clock Time:") )
			self.timeChoiceLastSelection = getattr(race, 'editRaceTimeOrClockTime', 0)
		self.timeChoice = wx.Choice( self, -1, choices = choices )
		self.timeChoice.SetSelection( self.timeChoiceLastSelection )
		self.timeChoice.Bind( wx.EVT_CHOICE, self.doTimeChoice, self.timeChoice )
		
		# Get race time
		t = race.getRider(entry.num).riderTimeToRaceTime(entry.t) if race and race.startTime else entry.t
		if self.timeChoiceLastSelection:
			# Race time to clock time
			dtStart = Model.race.startTime
			dt = dtStart + datetime.timedelta( seconds = t )
			t = (dt - datetime.datetime(dtStart.year, dtStart.month, dtStart.day)).total_seconds()
		self.timeMsEdit = HighPrecisionTimeEdit( self, seconds=t, size=(120, -1) )
			
				
		bs.Add( self.timeChoice,  pos=(2,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.timeMsEdit, pos=(2,1), span=(1,1), border = border, flag=wx.RIGHT|wx.BOTTOM|wx.ALIGN_LEFT )
		
		bs.Add( wx.StaticText( self, label = '{}:'.format(_("Lap Note"))),  pos=(3,0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )		
		self.noteEdit = wx.TextCtrl( self, size=(250,-1) )
		if race:
			self.noteEdit.SetValue( getattr(race, 'lapNote', {}).get( (self.entry.num, self.entry.lap), '' ) )
		bs.Add( self.noteEdit, pos=(3,1), span=(1,2), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		btnSizer = self.CreateStdDialogButtonSizer( wx.OK|wx.CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onOK, id=wx.ID_OK )
		if btnSizer:
			bs.Add( btnSizer, pos=(4, 0), span=(1,2), flag=wx.ALL|wx.EXPAND, border = border )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )

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
		Model.race.editRaceTimeOrClockTime = iSelection  # Save last selection for next time
		
	def onOK( self, event ):
		# This gets confusing.
		# If this is a Time Trial, we have to be very careful about how we pass times to the various routines.
		# Some take race time (and subtract off the firstTime), other take the rider time (which already has the firstTime subtracted).
		num = self.numEdit.GetValue()
		t = self.timeMsEdit.GetSeconds()
		
		# First, make sure the input race time (time since race start).
		if self.timeChoice.GetSelection() == 1 and Model.race and Model.race.startTime:
			# Time given in 24-hour clock, not Race Time.
			dtStart = Model.race.startTime
			dtInput = datetime.datetime(dtStart.year, dtStart.month, dtStart.day) + datetime.timedelta(seconds = t)
			if dtInput < dtStart:
				Utils.MessageOK( self, '\n\n'.join( [_('Cannot Enter Clock Time Before Race Start.'), _('(reminder: clock time is in 24-hour format)')] ),
										_('Time Entry Error'), iconMask = wx.ICON_ERROR )
				return
			t = (dtInput - dtStart).total_seconds()				
			# Time now converted from 24-hour clock to race time.

		# Convert the time to rider time, that is, if a time trial, subtract firstTime.
		race = Model.race
		if race.isTimeTrial:
			t = race.getRider( num ).raceTimeToRiderTime( t )
			# Time converted from race time to rider time (that is, if a TT, subtract firstTime).
			# t is now in the same format as self.entry.t.
		else:
			# Check offset (only applies if this is not a TT).
			offset = race.getStartOffset( num )
			if t <= offset:
				Utils.MessageOK( self, '{}: {}\n\n{}\n{}'.format(
					_('Cannot enter a time that is before the Category Start Offset'), Utils.formatTime(offset, highPrecision=True),
					_('All times earlier than the Start Offset are ignored.'),
					_('Please enter a time after the Start Offset.')
					), _('Time Entry Error'), iconMask = wx.ICON_ERROR
				)
				return

		# Check for edit changes.
		race.lapNote = getattr( race, 'lapNote', {} )
		note = self.noteEdit.GetValue().strip()
		if note != race.lapNote.get( (self.entry.num, self.entry.lap), '' ) or self.entry.num != num or self.entry.t != t:
			undo.pushState()
			
			if not note:
				race.lapNote.pop( (self.entry.num, self.entry.lap), None )
			else:
				race.lapNote[(self.entry.num, self.entry.lap)] = note
				
			if self.entry.num != num or self.entry.t != t:
				rider = race.getRider( num )
				if self.entry.lap != 0:
					race.numTimeInfo.change( self.entry.num, self.entry.t, t )			# Change entry time (in rider time).
					race.deleteTime( self.entry.num, self.entry.t )						# Delete time (in rider time).
					race.addTime( num, rider.riderTimeToRaceTime(t) )					# Add time (in race time).
				else:
					firstTime = rider.riderTimeToRaceTime(t)							# Set firstTime (in race time).
					race.numTimeInfo.change( self.entry.num, rider.firstTime, firstTime  )
					rider.firstTime = firstTime
					
			race.setChanged()
			Utils.refresh()
		
		self.EndModal( wx.ID_OK )

#------------------------------------------------------------------------------------------------
class ShiftNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		super().__init__( parent, id, "Shift Time",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		self.numEdit = wx.lib.intctrl.IntCtrl( self, size=(40, -1),
			style=wx.TE_RIGHT,
			value=int(self.entry.num),
			allow_none=False, min=1, max=9999 )
		
		shiftOptions = [_('Earlier'), _('Later')]
		self.shiftBox = wx.RadioBox( self, wx.ID_ANY,
			_('Shift Direction'),
			wx.DefaultPosition, wx.DefaultSize,
			shiftOptions, 2, wx.RA_SPECIFY_COLS )
		self.Bind(wx.EVT_RADIOBOX, self.updateNewTime, self.shiftBox)
				
		self.timeMsEdit = HighPrecisionTimeEdit( self )
		self.timeMsEdit.Bind( wx.EVT_TEXT, self.updateNewTime )
		self.newTime = wx.StaticText( self, label = '00:00:00')
		
		border = 8
		bs.Add( wx.StaticText( self, label = '{}: {}   {}: {}'.format(
			_('Rider Lap'), self.entry.lap,
			_('Race Time'), Utils.formatTime(self.entry.t,True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, label = '{}:'.format(_("Rider"))),  pos=(1,0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit, pos=(1,1), span=(1,2), border = border, flag=wx.GROW|wx.RIGHT|wx.TOP )
		bs.Add( self.shiftBox, pos=(2, 0), span=(1, 2), border = border, flag=wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM )
		bs.Add( wx.StaticText( self, label = '{}:'.format(_("Shift Time"))),  pos=(3,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.BOTTOM )
		bs.Add( self.timeMsEdit, pos=(3,1), span=(1,1), border = border, flag=wx.GROW|wx.LEFT|wx.RIGHT )
		bs.Add( self.newTime, pos=(4,0), span=(1,2), border = border, flag=wx.GROW|wx.LEFT|wx.RIGHT )
		
		btnSizer = self.CreateStdDialogButtonSizer( wx.OK|wx.CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onOK, id=wx.ID_OK )
		if btnSizer:
			bs.Add( btnSizer, pos=(5, 1), span=(1,2), border = border, flag=wx.ALL|wx.EXPAND )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		wx.CallAfter( self.updateNewTime )
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )

	def getNewTime( self ):
		tAdjust = self.timeMsEdit.GetSeconds() * (-1 if self.shiftBox.GetSelection() == 0 else 1)
		return self.entry.t + tAdjust
	
	def updateNewTime( self, event = None ):
		s = '{}: {}  {}: {}'.format(_('Was'), Utils.formatTime(self.entry.t,True), _('Now'), Utils.formatTime(self.getNewTime(),True) )
		self.newTime.SetLabel( s )
	
	def onOK( self, event ):
		num = self.numEdit.GetValue()
		t = self.getNewTime()
		if self.entry.num != num or self.entry.t != t:
			undo.pushState()
			with Model.LockRace() as race:
				rider = race.getRider( num )
				if (self.entry.lap or 0) != 0:
					race.numTimeInfo.change( self.entry.num, self.entry.t, t )
					race.deleteTime( self.entry.num, self.entry.t )
					race.addTime( num, t + ((rider.firstTime or 0.0) if race.isTimeTrial else 0.0) )
				else:
					race.numTimeInfo.change( self.entry.num, rider.firstTime, t )
					rider.firstTime = t
					race.setChanged()
			Utils.refresh()
		self.EndModal( wx.ID_OK )

#------------------------------------------------------------------------------------------------
class InsertNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		super().__init__( parent, id, "Insert Number",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		
		self.numEdit = wx.lib.intctrl.IntCtrl( self, style=wx.TE_RIGHT, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		
		border = 8
		bs.Add( wx.StaticText( self, label = '{}: {}   {}: {}'.format(
			_('Rider Lap'), self.entry.lap,
			_('Race Time'), Utils.formatTime(self.entry.t,True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, label = '{}:'.format(_('Original')) ),
				pos=(1,0), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( wx.StaticText( self, label = '{}'.format(self.entry.num) ),
				pos=(1,1), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_BOTTOM )
		
		shiftOptions = [_('Before Entry'), _('After Entry')]
		self.beforeAfterBox = wx.RadioBox( self, wx.ID_ANY, _('Insert'), wx.DefaultPosition, wx.DefaultSize, shiftOptions, 2, wx.RA_SPECIFY_COLS )
		bs.Add( self.beforeAfterBox, pos=(2,0), span=(1,2), border = border, flag=wx.TOP|wx.LEFT|wx.ALIGN_RIGHT )
				
		bs.Add( wx.StaticText( self, label = '{}'.format(_('Number')) ),
				pos=(3,0), span=(1,1), border = border, flag=wx.TOP|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit,
				pos=(3,1), span=(1,1), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_BOTTOM )
		
		btnSizer = self.CreateStdDialogButtonSizer( wx.OK|wx.CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onOK, id=wx.ID_OK )
		if btnSizer:
			bs.Add( btnSizer, pos=(4, 1), span=(1,2), border = border, flag=wx.ALL|wx.EXPAND )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )

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
			race.addTime( num, tInsert + ((rider.firstTime or 0.0) if race.isTimeTrial else 0.0) )
			
		Utils.refresh()
		
		self.EndModal( wx.ID_OK )

#------------------------------------------------------------------------------------------------
class SplitNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		super().__init__( parent, id, "Split Number",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		
		self.numEdit1 = wx.lib.intctrl.IntCtrl( self, style=wx.TE_RIGHT, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		self.numEdit2 = wx.lib.intctrl.IntCtrl( self, style=wx.TE_RIGHT, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		
		border = 8
		bs.Add( wx.StaticText( self, label = '{}: {}   {}: {}'.format(
			_('Rider Lap'), self.entry.lap,
			_('Race Time'), Utils.formatTime(self.entry.t,True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, label = _('Num1:') ),
				pos=(1,0), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit1,
				pos=(1,1), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_BOTTOM )

		bs.Add( wx.StaticText( self, label =_('Num2:') ),
				pos=(2,0), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit2,
				pos=(2,1), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_BOTTOM )
		
		btnSizer = self.CreateStdDialogButtonSizer( wx.OK|wx.CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onOK, id=wx.ID_OK )
		if btnSizer:
			bs.Add( btnSizer, pos=(3, 1), span=(1,2), border = border, flag=wx.ALL|wx.EXPAND )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )

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
			race.addTime( num1, t1 + ((rider.firstTime or 0.0) if race.isTimeTrial else 0.0) )
			race.addTime( num2, t2 + ((rider.firstTime or 0.0) if race.isTimeTrial else 0.0) )
			
		Utils.refresh()
		
		self.EndModal( wx.ID_OK )

#------------------------------------------------------------------------------------------------

@logCall
def CorrectNumber( parent, entry ):
	with CorrectNumberDialog(parent, entry) as dlg:
		dlg.ShowModal()
		
@logCall
def ShiftNumber( parent, entry ):
	with ShiftNumberDialog(parent, entry) as dlg:
		dlg.ShowModal()
		
@logCall
def InsertNumber( parent, entry ):
	with InsertNumberDialog(parent, entry) as dlg:
		dlg.ShowModal()
		
@logCall
def SplitNumber( parent, entry ):
	if (entry.lap or 0) == 0:
		return
		
	with SplitNumberDialog(parent, entry) as dlg:
		dlg.ShowModal()
		
@logCall
def DeleteEntry( parent, entry ):
	if (entry.lap or 0) == 0:
		return
	
	race = Model.race
	raceStartTimeOfDay = Utils.StrToSeconds(race.startTime.strftime('%H:%M:%S.%f')) if race and race.startTime else None
		
	with wx.MessageDialog(parent,
						   '{}: {}\n{}: {}\n{}: {}\n{}: {}\n\n{}?'.format(
								_('Bib'), entry.num,
								_('Lap'), entry.lap,
								_('Race Time'), Utils.formatTime(entry.t, True),
								_('Clock Time'), Utils.formatTime(entry.t + raceStartTimeOfDay, True) if raceStartTimeOfDay is not None else '',
								_('Confirm Delete')), _('Delete Entry'),
							wx.OK | wx.CANCEL | wx.ICON_QUESTION ) as dlg:
		if dlg.ShowModal() != wx.ID_OK:
			return
		
		undo.pushState()
		with Model.LockRace() as race:
			if race:
				race.numTimeInfo.delete( entry.num, entry.t )
				race.deleteTime( entry.num, entry.t )
		Utils.refresh()
	
@logCall
def SwapEntry( a, b ):
	race = Model.race
	if not race:
		return
		
	riderA = race.getRider( a.num )
	riderB = race.getRider( b.num )
	
	# Add some numeric noise if the times are equal.
	if a.t == b.t:
		rAdjust = random.random() / 100000.0
		if a.num < b.num:
			a_tNew, b_tNew = a.t, b.t + rAdjust
		else:
			a_tNew, b_tNew = a.t + rAdjust, b.t
	else:
		a_tNew, b_tNew = a.t, b.t
	
	race.numTimeInfo.change( a.num, a.t, b_tNew, Model.NumTimeInfo.Swap )
	race.numTimeInfo.change( b.num, b.t, a_tNew, Model.NumTimeInfo.Swap )
	
	race.deleteTime( a.num, a.t )
	race.deleteTime( b.num, b.t )
	race.addTime( a.num, b_tNew + ((riderB.firstTime or 0.0) if race.isTimeTrial else 0.0) )
	race.addTime( b.num, a_tNew + ((riderA.firstTime or 0.0) if race.isTimeTrial else 0.0) )

class StatusChangeDialog( wx.Dialog ):
	def __init__( self, parent, message, title, t=None, externalData=None, id=wx.ID_ANY ):
		super().__init__( parent, id, title,
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		
		self.message = wx.StaticText( self, label=message )
		self.message.SetFont( font )
		
		if externalData is not None:
			self.externalData = wx.StaticText( self, label=externalData )
			self.externalData.SetFont( font )
		else:
			self.externalData = None
		
		if t is not None:
			self.entryTime = wx.CheckBox( self, label='{}: {}'.format(_('and Enter Last Lap Time at'), Utils.formatTime(t)) )
			self.entryTime.SetValue( True )
			self.entryTime.SetFont( font )
		else:
			self.entryTime = None
			
		border = 16
		vs = wx.BoxSizer( wx.VERTICAL )
		vs.Add( self.message, flag=wx.ALL, border=border )
		if self.externalData:
			vs.Add( self.externalData, flag=wx.RIGHT|wx.LEFT|wx.BOTTOM, border=border )
		if self.entryTime:
			vs.Add( self.entryTime, flag=wx.RIGHT|wx.LEFT|wx.BOTTOM, border=border )
			
		btnSizer = self.CreateStdDialogButtonSizer( wx.OK|wx.CANCEL )
		if btnSizer:
			vs.Add( btnSizer, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.SetSizerAndFit( vs )
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )

	def getSetEntryTime( self ):
		return self.entryTime and self.entryTime.IsChecked()
	
def DoStatusChange( parent, num, message, title, newStatus, lapTime=None ):
	if num is None:
		return False
		
	race = Model.race
	externalData = []
	try:
		excelLink = race.excelLink
		externalInfo = excelLink.read()
		for f in ['LastName', 'FirstName', 'Team']:
			try:
				externalData.append( '{}'.format(externalInfo[num][f] ) )
				if f == 'Team':
					externalData[-1] = '({})'.format(externalData[-1])
			except KeyError:
				pass
		if len(externalData) == 3:	# Format the team name slightly differently.
			externalData = '{}: {}'.format( '{}'.format(num), ', '.join(externalData[:-1]) ) + ' ' + externalData[-1]
		else:
			externalData = '{}: {}'.format( '{}'.format(num), ', '.join(externalData) ) if externalData else None
	except Exception:
		externalData = None
	
	with StatusChangeDialog(parent, message=message.format(num), title=title, externalData=externalData, t=lapTime) as d:
		if d.ShowModal() != wx.ID_OK:
			return False
		lapTime = lapTime if d.getSetEntryTime() else None
	
	undo.pushState()
	with Model.LockRace() as race:
		if not race:
			return False
		if lapTime:
			race.addTime( num, lapTime )
		rider = race.getRider( num )
		rider.setStatus( newStatus )
		race.setChanged()
	Utils.refresh()
	Utils.refreshForecastHistory()
	return True

def getActionMessage( actionName ):
	return actionName + ' {}?'
	
@logCall
def DoDNF( parent, num, lapTime=None ):
	return DoStatusChange( parent, num, getActionMessage(_('DNF')), _('Confirm Did Not FINISH'), Model.Rider.DNF, lapTime )

@logCall
def DoPull( parent, num, lapTime=None ):
	return DoStatusChange( parent, num, getActionMessage(_('Pull')), _('Confirm PULL Rider'), Model.Rider.Pulled, lapTime)

@logCall
def DoDNS( parent, num, lapTime=None ):
	return DoStatusChange( parent, num, getActionMessage(_('DNS')), _('Confirm Did Not START'), Model.Rider.DNS )

@logCall
def DoDQ( parent, num, lapTime=None ):
	return DoStatusChange( parent, num, getActionMessage(_('DQ')), _('Confirm Disqualify'), Model.Rider.DQ )
	
@logCall
def AddLapSplits( num, lap, times, splits ):
	undo.pushState()
	with Model.LockRace() as race:
		rider = race.riders[num]
		try:
			tLeft = times[lap-1]
			tRight = times[lap]
			
			# Split the first lap time to the same ratio as the distances.
			category = race.getCategory( num )
			if (	lap == 1 and
					category is not None and
					category.distanceType == category.DistanceByLap and
					category.distance and category.firstLapDistance and
					category.distance != category.firstLapDistance
				):
				flr = float(category.firstLapDistance) / float(category.distance)
				splitTime = (tRight - tLeft) / (flr + (splits-1))
				firstLapSplitTime = splitTime * flr
			else:
				splitTime = firstLapSplitTime = (tRight - tLeft) / float(splits)
			
			newTime = tLeft
			for i in range( 1, splits ):
				newTime += (firstLapSplitTime if i == 1 else splitTime)
				race.numTimeInfo.add( num, newTime, Model.NumTimeInfo.Split )
				race.addTime( num, newTime + ((rider.firstTime or 0.0) if race.isTimeTrial else 0.0) )
			return True
		except (TypeError, KeyError, ValueError, IndexError) as e:
			Utils.logException( e, sys.exc_info() )
			return False

if __name__ == '__main__':
	app = wx.App( False )
	frame = wx.Frame( None )
	
	d = SplitNumberDialog( frame, Model.Entry( 110, 3, 60*4+7, False ) )
	d.Show()
	app.MainLoop()
