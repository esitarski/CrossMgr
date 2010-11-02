import wx
import datetime

import Model
import Utils

import wx.lib.masked as masked

def StartRaceNow():
	race = Model.getRace()
	if race is None:
		return
		
	Model.resetCache()
	race.startRaceNow()
	
	# Refresh the main window and switch to the Record pane.
	mainWin = Utils.getMainWin()
	if mainWin is not None:
		mainWin.showPageName( 'Record' )
		mainWin.refresh()

def GetNowSeconds():
	t = datetime.datetime.now()
	return t.hour * 60 * 60 + t.minute * 60 + t.second
		
class StartRaceAtTime( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Start Race at Time:",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		bs = wx.GridBagSizer(vgap=5, hgap=5)

		font = wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		
		self.startSeconds = None
		self.timer = None

		race = Model.getRace()
		autoStartLabel = wx.StaticText( self, wx.ID_ANY, 'Automatically Start Race at:' )
		
		# Make sure we don't suggest a start time in the past.
		value = race.scheduledStart
		startSeconds = Utils.StrToSeconds( value ) * 60
		nowSeconds = GetNowSeconds()
		if startSeconds < nowSeconds:
			startOffset = 3 * 60
			startSeconds = nowSeconds - nowSeconds % startOffset
			startSeconds = nowSeconds + startOffset
			value = '%02d:%02d' % (startSeconds / (60*60), (startSeconds / 60) % 60)
		
		self.autoStartTime = masked.TimeCtrl( self, wx.ID_ANY, fmt24hr=True, display_seconds=False, value=value )
													
		self.countdown = wx.StaticText( self, wx.ID_ANY, '      ' )
		self.countdown.SetFont( font )
													
		self.okBtn = wx.Button( self, wx.ID_ANY, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_ANY, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		border = 8
		bs.Add( autoStartLabel, pos=(0,0), span=(1,1),
				border = border, flag=wx.LEFT|wx.TOP|wx.BOTTOM )
		bs.Add( self.autoStartTime, pos=(0,1), span=(1,1),
				border = border, flag=wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_BOTTOM )
		bs.Add( self.countdown, pos=(1,0), span=(1,2), border = border, flag=wx.ALL )
		bs.Add( self.okBtn, pos=(2, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(2, 1), span=(1,1), border = border, flag=wx.ALL )
		
		bs.AddGrowableRow( 1 )
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def updateCountdownClock( self, event = None ):
		if self.startSeconds is None:
			return
	
		nowSeconds = GetNowSeconds()
		
		if nowSeconds < self.startSeconds:
			self.countdown.SetLabel( Utils.SecondsToStr(self.startSeconds - nowSeconds) )
			return
		
		# Stop the timer.
		self.startSeconds = None
		self.timer.Stop()
		
		# Start the race.
		StartRaceNow()
		self.EndModal( wx.ID_OK )
	
	def onOK( self, event ):
		startTime = self.autoStartTime.GetValue()

		self.startSeconds = Utils.StrToSeconds( startTime ) * 60
		if self.startSeconds < GetNowSeconds() and \
			not Utils.MessageOKCancel( None, 'Race start time is in the past.\nStart race now?', 'Start Race Now', iconMask = wx.ICON_QUESTION ):
			return

		# Setup the countdown clock.
		self.timer = wx.Timer( self, id=1009 )
		self.Bind( wx.EVT_TIMER, self.updateCountdownClock, self.timer )
		self.timer.Start( 1000 )
		
		# Disable buttons and switch to countdown state.
		self.okBtn.Enable( False )
		self.autoStartTime.Enable( False )
		self.updateCountdownClock()
		
	def onCancel( self, event ):
		self.startSeconds = None
		if self.timer is not None:
			self.timer.Stop()
		self.EndModal( wx.ID_CANCEL )
		
class Actions( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		bs = wx.GridBagSizer(vgap=5, hgap=5)
		
		font = wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

		self.startRaceBtn = wx.Button( self, 10, 'Start Race &Now' )
		self.Bind( wx.EVT_BUTTON, self.onStartRace, self.startRaceBtn )
		self.startRaceBtn.SetFont( font )
		
		self.startRaceTimeBtn = wx.Button( self, 11, 'Start Race at &Time' )
		self.Bind( wx.EVT_BUTTON, self.onStartRaceTime, self.startRaceTimeBtn )
		self.startRaceTimeBtn.SetFont( font )
		
		self.finishRaceBtn = wx.Button( self, 20, '&Finish Race' )
		self.Bind( wx.EVT_BUTTON, self.onFinishRace, self.finishRaceBtn )
		self.finishRaceBtn.SetFont( font )
		
		border = 8
		bs.Add(self.startRaceBtn, pos=(0,0), span=(1,1), border=border, flag=wx.TOP|wx.LEFT)
		bs.Add(self.startRaceTimeBtn, pos=(1,0), span=(1,1), border=border, flag=wx.TOP|wx.LEFT)
		bs.Add(self.finishRaceBtn, pos=(2,0), span=(1,1), border=border, flag=wx.TOP|wx.LEFT)
		bs.AddGrowableRow( 3 )
		self.SetSizer(bs)
		
		self.refresh()
	
	def onStartRace( self, event ):
		race = Model.getRace()
		if race is not None and Utils.MessageOKCancel(self, 'Start Race Now?', 'Start Race', iconMask = wx.ICON_QUESTION):
			StartRaceNow()
	
	def onStartRaceTime( self, event ):
		race = Model.getRace()
		if race is None:
			return
		dlg = StartRaceAtTime( self )
		dlg.ShowModal()
		dlg.Destroy()  
	
	def onFinishRace( self, event ):
		race = Model.getRace()
		if race is None or not Utils.MessageOKCancel(self, 'Finish Race Now?', 'Finish Race', iconMask = wx.ICON_QUESTION):
			return
		race.finishRaceNow()
		if race.numLaps is None:
			race.numLaps = race.getMaxLap()
		Model.resetCache()
		Utils.writeRace()
		self.refresh()
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.refresh()
	
	def refresh( self ):
		self.startRaceBtn.Enable( False )
		self.startRaceTimeBtn.Enable( False )
		self.finishRaceBtn.Enable( False )
		race = Model.getRace()
		if race is None:
			return
		mainWin = Utils.getMainWin()
		if mainWin is not None:
			mainWin.updateRaceClock()
		if race.startTime is None:
			self.startRaceBtn.Enable( True )
			self.startRaceTimeBtn.Enable( True )
		elif race.isRunning():
			self.finishRaceBtn.Enable( True )
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	actions = Actions(mainWin)
	Model.newRace()
	actions.refresh()
	mainWin.Show()
	app.MainLoop()