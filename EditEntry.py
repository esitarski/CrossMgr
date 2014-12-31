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
		bs.Add( wx.StaticText( self, label = u'{}: {}   {}: {}'.format(
				_('Rider Lap'), self.entry.lap,
				_('Race Time'), Utils.formatTime(self.entry.t, True)
			)),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, label = u'{}:'.format(_("Rider:"))),  pos=(1,0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.numEdit, pos=(1,1), span=(1,2), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		choices = [u'{}:'.format(_("Race Time"))]
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
				Utils.MessageOK( self, u'\n\n'.join( [_('Cannot Enter Clock Time Before Race Start.'), _('(reminder: clock time is in 24-hour format)')] ),
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
		bs.Add( wx.StaticText( self, label = u'{}: {}   {}: {}'.format(
			_('Rider Lap'), self.entry.lap,
			_('Race Time'), Utils.formatTime(self.entry.t,True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, label = u'{}:'.format(_("Rider"))),  pos=(1,0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit, pos=(1,1), span=(1,2), border = border, flag=wx.GROW|wx.RIGHT|wx.TOP )
		bs.Add( self.shiftBox, pos=(2, 0), span=(1, 2), border = border, flag=wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM )
		bs.Add( wx.StaticText( self, label = u'{}:'.format(_("Shift Time"))),  pos=(3,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.BOTTOM )
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
		s = u'{}: {}  {}: {}'.format(_('Was'), Utils.formatTime(self.entry.t,True), _('Now'), Utils.formatTime(self.getNewTime(),True) )
		self.newTime.SetLabel( s )

#------------------------------------------------------------------------------------------------
class InsertNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Insert Number",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		
		self.numEdit = wx.lib.intctrl.IntCtrl( self, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		bs.Add( wx.StaticText( self, label = u'{}: {}   {}: {}'.format(
			_('Rider Lap'), self.entry.lap,
			_('Race Time'), Utils.formatTime(self.entry.t,True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, label = u'{}:'.format(_('Original')) ),
				pos=(1,0), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( wx.StaticText( self, label = u'{}'.format(self.entry.num) ),
				pos=(1,1), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_BOTTOM )
		
		shiftOptions = [_('Before Entry'), _('After Entry')]
		self.beforeAfterBox = wx.RadioBox( self, wx.ID_ANY, _('Insert'), wx.DefaultPosition, wx.DefaultSize, shiftOptions, 2, wx.RA_SPECIFY_COLS )
		bs.Add( self.beforeAfterBox, pos=(2,0), span=(1,2), border = border, flag=wx.TOP|wx.LEFT|wx.ALIGN_RIGHT )
				
		bs.Add( wx.StaticText( self, label = u'{}'.format(_('Number')) ),
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
		bs.Add( wx.StaticText( self, label = u'{}: {}   {}: {}'.format(
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
						   u'{}: {}  {}: {}   {}: {}\n\n{}?'.format(
								_('Num'), entry.num,
								_('Lap'), entry.lap,
								_('Race Time'), Utils.formatTime(entry.t, True),
								_('Confirm Delete')), _('Delete Entry'),
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

class StatusChangeDialog( wx.Dialog ):
	def __init__( self, parent, message, title, t=None, externalData=None, id=wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, title,
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		
		self.message = wx.StaticText( self, label=message )
		self.message.SetFont( font )
		
		if externalData is not None:
			self.externalData = wx.StaticText( self, label=externalData )
			self.externalData.SetFont( font )
		else:
			self.externalData = None
		
		if t is not None:
			self.entryTime = wx.CheckBox( self, label=_('and Enter Last Lap Time at: ') + Utils.formatTime(t) )
			self.entryTime.SetValue( False )
			self.entryTime.SetFont( font )
		else:
			self.entryTime = None
			
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )

		border = 16
		vs = wx.BoxSizer( wx.VERTICAL )
		vs.Add( self.message, flag=wx.ALL, border=border )
		if self.externalData:
			vs.Add( self.externalData, flag=wx.RIGHT|wx.LEFT|wx.BOTTOM, border=border )
		if self.entryTime:
			vs.Add( self.entryTime, flag=wx.RIGHT|wx.LEFT|wx.BOTTOM, border=border )
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.okBtn, flag=wx.ALL, border = border )
		self.okBtn.SetDefault()
		hs.AddStretchSpacer()
		hs.Add( self.cancelBtn, flag=wx.ALL, border = border )
		vs.Add( hs, flag=wx.EXPAND )
		
		self.SetSizerAndFit( vs )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def getSetEntryTime( self ):
		return self.entryTime and self.entryTime.IsChecked()
		
	def onOK( self, event ):
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
	
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
				externalData.append( unicode(externalInfo[num][f] ) )
				if f == 'Team':
					externalData[-1] = u'({})'.format(externalData[-1])
			except KeyError:
				pass
		if len(externalData) == 3:	# Format the team name slightly differently.
			externalData = u'{}: {}'.format( unicode(num), u', '.join(externalData[:-1]) ) + u' ' + externalData[-1]
		else:
			externalData = u'{}: {}'.format( unicode(num), u', '.join(externalData) ) if externalData else None
	except:
		externalData = None
	
	d = StatusChangeDialog(parent, message=message.format(num), title=title, externalData=externalData, t=lapTime)
	ret = d.ShowModal()
	lapTime = lapTime if d.getSetEntryTime() else None
	d.Destroy()
	if ret != wx.ID_OK:
		return False
	
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
	return True

def getActionMessage( actionName ):
	return actionName + u' {}?'
	
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
		try:
			tLeft = times[lap-1]
			tRight = times[lap]
			splitTime = (tRight - tLeft) / float(splits)
			for i in xrange( 1, splits ):
				newTime = tLeft + splitTime * i
				race.numTimeInfo.add( num, newTime, Model.NumTimeInfo.Split )
				race.addTime( num, newTime )
			return True
		except (TypeError, KeyError, ValueError, IndexError) as e:
			Utils.logException( e, sys.exc_info )
			return False
