import Utils
from Utils				import logCall
import wx
import wx.grid		as gridlib
import wx.lib.intctrl
import wx.lib.masked           as masked
import ColGrid
import Model

#------------------------------------------------------------------------------------------------
class CorrectNumberDialog( wx.Dialog ):
	def __init__( self, parent, entry, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Correct Number",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		self.entry = entry
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		self.numEdit = wx.lib.intctrl.IntCtrl( self, 20, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value=int(self.entry.num), allow_none=False, min=1, max=9999 )
		
		self.timeCtrl = masked.TimeCtrl( self, -1, name="Race Time:", fmt24hr=True )
		s = int(entry.t+0.5)
		seconds = s % 60
		minutes = (s / 60) % 60
		hours = s / (60*60)
		self.timeCtrl.ChangeValue( '%02d:%02d:%02d' % (hours, minutes, seconds) )
				
		self.okBtn = wx.Button( self, wx.ID_ANY, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_ANY, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		race = Model.getRace()
		border = 8
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'RiderLap: %d   RaceTime: %s' % (self.entry.lap, Utils.SecondsToMMSS(self.entry.t)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, -1, "Rider:"),  pos=(1,0), span=(1,1), border = border, flag=wx.GROW|wx.LEFT|wx.TOP|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit, pos=(1,1), span=(1,2), border = border, flag=wx.GROW|wx.RIGHT|wx.TOP )
		bs.Add( wx.StaticText( self, -1, "Race Time:"),  pos=(2,0), span=(1,1), border = border, flag=wx.GROW|wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT|wx.BOTTOM )
		bs.Add( self.timeCtrl, pos=(2,1), span=(1,1), border = border, flag=wx.GROW|wx.LEFT|wx.RIGHT|wx.BOTTOM )
		
		bs.Add( self.okBtn, pos=(3, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(3, 1), span=(1,1), border = border, flag=wx.ALL )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onOK( self, event ):
		num = self.numEdit.GetValue()
		t = Utils.StrToSeconds(self.timeCtrl.GetValue())
		if self.entry.num != num or self.entry.t != t:
			with Model.LockRace() as race:
				race.deleteTime( self.entry.num, self.entry.t )
				race.addTime( num, t )
				race.resetCache()
			mainWin = Utils.getMainWin()
			if mainWin:
				mainWin.refresh()
				mainWin.writeRace()
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
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'RiderLap: %d   RaceTime: %s' % (self.entry.lap, Utils.SecondsToMMSS(self.entry.t)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'Original:' ),
				pos=(1,0), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( wx.StaticText( self, wx.ID_ANY, str(self.entry.num) ),
				pos=(1,1), span=(1,1), border = border, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_BOTTOM )
				
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'Split 1:' ),
				pos=(2,0), span=(1,1), border = border, flag=wx.TOP|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit1,
				pos=(2,1), span=(1,1), border = border, flag=wx.TOP|wx.RIGHT|wx.ALIGN_BOTTOM )
				
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'Split 2:' ),
				pos=(3,0), span=(1,1), border = border, flag=wx.BOTTOM|wx.LEFT|wx.ALIGN_RIGHT )
		bs.Add( self.numEdit2,
				pos=(3,1), span=(1,1), border = border, flag=wx.BOTTOM|wx.RIGHT|wx.ALIGN_BOTTOM )

		bs.Add( self.okBtn, pos=(4, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(4, 1), span=(1,1), border = border, flag=wx.ALL|wx.ALIGN_RIGHT )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onOK( self, event ):
		with Model.LockRace() as race:
			num1 = self.numEdit1.GetValue()
			num2 = self.numEdit2.GetValue()
			
			# Delete the original entry.
			if self.entry.num != num1 and self.entry.num != num2:
				race.deleteTime( self.entry.num, self.entry.t )
			
			# Add the 1st split entry.
			if self.entry.num != num1:
				race.addTime( num1, self.entry.t )
			
			# Add the 2nd split entry.
			if self.entry.num != num2:
				race.addTime( num2, self.entry.t + 0.001 )	# Add a little extra time to keep the sequence
			
			race.resetCache()
			
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.refresh()
			mainWin.writeRace()
		
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
def SplitNumber( parent, entry ):
	dlg = SplitNumberDialog( parent, entry )
	dlg.ShowModal()
	dlg.Destroy()
		
@logCall
def DeleteEntry( parent, entry ):
	dlg = wx.MessageDialog(parent,
						   'Num: %d  RiderLap: %d   RaceTime: %s\n\nConfirm Delete (no undo)?' %
								(entry.num, entry.lap, Utils.SecondsToMMSS(entry.t)), 'Delete Entry',
							wx.OK | wx.CANCEL | wx.ICON_QUESTION )
	# dlg.CentreOnParent(wx.BOTH)
	if dlg.ShowModal() == wx.ID_OK:
		race = Model.getRace()
		race.deleteTime( entry.num, entry.t )
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.refresh()
			mainWin.writeRace()
	dlg.Destroy()
	
@logCall
def SwapEntry( parent, a, b ):
	race = Model.race
	if not race:
		return
	race.addTime( a.num, b.t )
	race.addTime( b.num, a.t )
	race.deleteTime( a.num, a.t )
	race.deleteTime( b.num, b.t )
	mainWin = Utils.getMainWin()
	if mainWin:
		mainWin.refresh()
		mainWin.writeRace()

def DoStatusChange( parent, num, message, title, newStatus ):
	if num is None or not Utils.MessageOKCancel(parent, message % num, title):
		return False
	with Model.LockRace() as race:
		if not race:
			return False
		rider = race.getRider( num )
		rider.setStatus( newStatus )
		Model.resetCache()
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
