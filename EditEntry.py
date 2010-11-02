import Utils
import wx
import wx.grid		as gridlib
import wx.lib.intctrl
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
		
		self.okBtn = wx.Button( self, wx.ID_ANY, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_ANY, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		race = Model.getRace()
		border = 8
		bs.Add( wx.StaticText( self, wx.ID_ANY, 'RiderLap: %d   RaceTime: %s' % (self.entry.lap, Utils.SecondsToMMSS(self.entry.t)) ),
			pos=(0,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( self.numEdit, pos=(1,0), span=(1,2), border = border, flag=wx.GROW|wx.ALL )
		bs.Add( self.okBtn, pos=(2, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(2, 1), span=(1,1), border = border, flag=wx.ALL )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onOK( self, event ):
		num = self.numEdit.GetValue()
		if self.entry.num != num:
			race = Model.getRace()
			race.deleteTime( self.entry.num, self.entry.t )
			race.addTime( num, self.entry.t )
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
		race = Model.getRace()
		
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

def CorrectNumber( parent, entry ):
	dlg = CorrectNumberDialog( parent, entry )
	dlg.ShowModal()
	dlg.Destroy()
		
def SplitNumber( parent, entry ):
	dlg = SplitNumberDialog( parent, entry )
	dlg.ShowModal()
	dlg.Destroy()
		
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
	
