import Utils
from Utils				import logCall
import wx
import wx.grid		as gridlib
import wx.lib.intctrl
import wx.lib.masked           as masked
import ColGrid
import Model
from Undo import undo
import random
import math

class TimeMsEdit( object ):
	def __init__( self, parent, t = 0, changeCallback = None ):
		self.timeCtrl = masked.TimeCtrl( parent, -1, name="Race Time:", fmt24hr=True )
		
		f = self.timeCtrl.GetFont()
		dc = wx.WindowDC(parent)
		dc.SetFont(f)
		width, height = dc.GetTextExtent( '00:00:0000' )
		
		self.timeCtrl.SetSize( wx.Size(width, -1) )
		self.timeCtrl.SetParameters( useFixedWidthFont=False )
		
		width, height = dc.GetTextExtent( '00000' )
		self.msCtrl = wx.lib.intctrl.IntCtrl( parent, wx.ID_ANY, size=(width, -1),
				style=wx.TE_LEFT | wx.TE_PROCESS_ENTER | wx.ALIGN_LEFT,
				limited = True,
				value=0,
				allow_none=False, min=0, max=999 )
				
		self.timeSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.timeSizer.Add( self.timeCtrl )
		self.timeSizer.Add( wx.StaticText(parent, wx.ID_ANY, '.'), flag=wx.ALIGN_BOTTOM|wx.BOTTOM, border=4 )
		self.timeSizer.Add( self.msCtrl )
		
		self.SetValue( t )
		
		if changeCallback:
			self.timeCtrl.Bind( masked.EVT_TIMEUPDATE, lambda event: changeCallback() )
			self.msCtrl.Bind( wx.lib.intctrl.EVT_INT, lambda event: changeCallback()  )

	def SetValue( self, t ):
		s = int(t)
		seconds = s % 60
		minutes = (s / 60) % 60
		hours = s / (60*60)
		self.timeCtrl.ChangeValue( '%02d:%02d:%02d' % (hours, minutes, seconds) )
		self.msCtrl.SetValue( int(math.modf(t)[0] * 1000.0) )
	
	def GetValue( self ):
		t = Utils.StrToSeconds(self.timeCtrl.GetValue())
		ms = self.msCtrl.GetValue()
		if ms:
			while ms < 99:
				ms *= 10
			t += ms / 1000.0
		return t
				
#------------------------------------------------------------------------------------------------
class CorrectNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Correct Number",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		self.numEdit = wx.lib.intctrl.IntCtrl( self, 20, size=(64,-1), style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		
		self.timeMsEdit = TimeMsEdit( self, entry.t )
				
		self.okBtn = wx.Button( self, wx.ID_ANY, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_ANY, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'RiderLap: %d   RaceTime: %s' % (self.entry.lap, Utils.formatTime(self.entry.t, True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, -1, "Rider:"),  pos=(1,0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.numEdit, pos=(1,1), span=(1,2), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		bs.Add( wx.StaticText( self, -1, "Race Time:"),  pos=(2,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.timeMsEdit.timeSizer, pos=(2,1), span=(1,1), border = border, flag=wx.RIGHT|wx.BOTTOM|wx.ALIGN_LEFT )
		
		bs.Add( self.okBtn, pos=(3, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(3, 1), span=(1,1), border = border, flag=wx.ALL )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onOK( self, event ):
		num = self.numEdit.GetValue()
		t = self.timeMsEdit.GetValue()
		if self.entry.num != num or self.entry.t != t:
			undo.pushState()
			with Model.LockRace() as race:
				if self.entry.lap != 0:
					race.numTimeInfo.change( self.entry.num, self.entry.t, t )
					race.deleteTime( self.entry.num, self.entry.t )
					race.addTime( num, t )
				else:
					rider = race.getRider( num )
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
		self.numEdit = wx.lib.intctrl.IntCtrl( self, wx.ID_ANY, size=(40, -1),
			style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER,
			value=int(self.entry.num),
			allow_none=False, min=1, max=9999 )
		
		self.timeMsEdit = TimeMsEdit( self, changeCallback=self.updateNewTime )
		self.newTime = wx.StaticText( self, wx.ID_ANY, "00:00:00")
		
		shiftOptions = ['Earlier', 'Later']
		self.shiftBox = wx.RadioBox( self, wx.ID_ANY,
			'Shift Direction',
			wx.DefaultPosition, wx.DefaultSize,
			shiftOptions, 2, wx.RA_SPECIFY_COLS )
		self.Bind(wx.EVT_RADIOBOX, self.updateNewTime, self.shiftBox)
				
		self.okBtn = wx.Button( self, wx.ID_ANY, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_ANY, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'RiderLap: %d   RaceTime: %s' % (self.entry.lap, Utils.formatTime(self.entry.t,True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, -1, "Rider:"),  pos=(1,0), span=(1,1), border = border, flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit, pos=(1,1), span=(1,2), border = border, flag=wx.GROW|wx.RIGHT|wx.TOP )
		bs.Add( self.shiftBox, pos=(2, 0), span=(1, 2), border = border, flag=wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM )
		bs.Add( wx.StaticText( self, -1, "Shift Time:"),  pos=(3,0), span=(1,1), border = border, flag=wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.BOTTOM )
		bs.Add( self.timeMsEdit.timeSizer, pos=(3,1), span=(1,1), border = border, flag=wx.GROW|wx.LEFT|wx.RIGHT )
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
		tAdjust = self.timeMsEdit.GetValue() * (-1 if self.shiftBox.GetSelection() == 0 else 1)
		return self.entry.t + tAdjust

	def onOK( self, event ):
		num = self.numEdit.GetValue()
		t = self.getNewTime()
		if self.entry.num != num or self.entry.t != t:
			undo.pushState()
			with Model.LockRace() as race:
				if self.entry.lap != 0:
					race.numTimeInfo.change( self.entry.num, self.entry.t, t )
					race.deleteTime( self.entry.num, self.entry.t )
					race.addTime( num, t )
				else:
					rider = race.getRider( num )
					race.numTimeInfo.change( self.entry.num, rider.firstTime, t )
					rider.firstTime = t
					race.setChanged()
			Utils.refresh()
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
		
	def updateNewTime( self, event = None ):
		s = 'Was: %s  Now: %s' % (Utils.formatTime(self.entry.t,True),Utils.formatTime(self.getNewTime(),True) )
		self.newTime.SetLabel( s )

#------------------------------------------------------------------------------------------------
class InsertNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Insert Number",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		
		self.numEdit = wx.lib.intctrl.IntCtrl( self, 20, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		
		self.okBtn = wx.Button( self, wx.ID_ANY, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_ANY, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'RiderLap: %d   RaceTime: %s' % (self.entry.lap, Utils.formatTime(self.entry.t, True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'Original:' ),
				pos=(1,0), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( wx.StaticText( self, wx.ID_ANY, str(self.entry.num) ),
				pos=(1,1), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_BOTTOM )
		
		shiftOptions = ['Before Entry', 'After Entry']
		self.beforeAfterBox = wx.RadioBox( self, wx.ID_ANY, 'Insert', wx.DefaultPosition, wx.DefaultSize, shiftOptions, 2, wx.RA_SPECIFY_COLS )
		bs.Add( self.beforeAfterBox, pos=(2,0), span=(1,2), border = border, flag=wx.TOP|wx.LEFT|wx.ALIGN_RIGHT )
				
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'Number:' ),
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
			race.numTimeInfo.add( self.entry.num, tInsert )
			race.addTime( num, tInsert )
			
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
		
		self.numEdit1 = wx.lib.intctrl.IntCtrl( self, 20, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		self.numEdit2 = wx.lib.intctrl.IntCtrl( self, 20, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		
		self.okBtn = wx.Button( self, wx.ID_ANY, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_ANY, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'RiderLap: %d   RaceTime: %s' % (self.entry.lap, Utils.formatTime(self.entry.t, True)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'Num1:' ),
				pos=(1,0), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit1,
				pos=(1,1), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_BOTTOM )

		bs.Add( wx.StaticText( self, wx.ID_ANY, 'Num2:' ),
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
		num2 = self.numEdit1.GetValue()
		if not num1 or not num2 or num1 == num2:
			return
			
		t1 = self.entry.t
		t2 = self.entry.t + 0.0001 * random.random()
		
		undo.pushState()
		with Model.LockRace() as race:
		
			race.numTimeInfo.delete( entry.num, entry.t )
			race.numTimeInfo.add( num1, t1 )
			race.numTimeInfo.add( num2, t2 )
			
			race.deleteTime( entry.num, entry.t )
			race.addTime( num1, t1 )
			race.addTime( num2, t2 )
			
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
						   'Num: %d  Lap: %d   RaceTime: %s\n\nConfirm Delete?' %
								(entry.num, entry.lap, Utils.formatTime(entry.t, True)), 'Delete Entry',
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
	race.numTimeInfo.change( a.num, a.t, b.t, Model.NumTimeInfo.Swap )
	race.numTimeInfo.change( b.num, b.t, a.t, Model.NumTimeInfo.Swap )
	
	race.deleteTime( a.num, a.t )
	race.deleteTime( b.num, b.t )
	race.addTime( a.num, b.t )
	race.addTime( b.num, a.t )

def DoStatusChange( parent, num, message, title, newStatus ):
	if num is None or not Utils.MessageOKCancel(parent, message % num, title):
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
	return DoStatusChange( parent, num, 'DNF rider %d?', 'Confirm Did Not FINISH', Model.Rider.DNF )

@logCall
def DoPull( parent, num ):
	return DoStatusChange( parent, num, 'Pull rider %d?', 'Confirm PULL Rider', Model.Rider.Pulled )

@logCall
def DoDNS( parent, num ):
	return DoStatusChange( parent, num, 'DNS rider %d?', 'Confirm Did Not START', Model.Rider.DNS )

@logCall
def DoDQ( parent, num ):
	return DoStatusChange( parent, num, 'DQ rider %d?', 'Confirm Disqualify', Model.Rider.DQ )
	
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

