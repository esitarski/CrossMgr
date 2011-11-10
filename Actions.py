import wx
import datetime
import os

import Model
import Utils
import JChip
import OutputStreamer

import wx.lib.masked as masked
# import wx.lib.agw.gradientbutton as GB

def MakeButton( parent, id = wx.ID_ANY, img = None, text = '' ):
	# btn = wx.Button( parent, wx.ID_ANY, text )
	# img = img.ShrinkBy( 2, 2 )
	lighten = 1.2
	img = img.AdjustChannels(lighten,lighten,lighten)
	btn = wx.BitmapButton( parent, wx.ID_ANY, bitmap = img.ConvertToBitmap(), style = wx.NO_BORDER )
	btn.SetBackgroundColour( wx.Colour(255,255,255) )

	# Derive hover image.
	lighten = 1.25
	hover_img = img.AdjustChannels(lighten,lighten,lighten)
	btn.SetBitmapHover( hover_img.ConvertToBitmap() )

	# Derive disabled image.
	# Lighten the text.
	img.Replace( 0, 0, 0, 64, 64, 64 )
	lighten = 1.4
	disabled_img = img.ConvertToGreyscale().AdjustChannels(lighten,lighten,lighten)
	btn.SetBitmapDisabled( disabled_img.ConvertToBitmap() )
	return btn

def StartRaceNow():
	with Model.LockRace() as race:
		if race is None:
			return
			
		Model.resetCache()
		race.startRaceNow()
		
	OutputStreamer.writeRaceStart()
	
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
			not Utils.MessageOKCancel( None, 'Race start time is in the past.\nStart race now?', 'Start Race Now' ):
			return

		# Setup the countdown clock.
		self.timer = wx.Timer( self, id=wx.NewId() )
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
		bs = wx.GridBagSizer(vgap=4, hgap=4)
		
		self.SetBackgroundColour( wx.Colour(255,255,255) )
		
		font = wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

		img = wx.Image( os.path.join(Utils.getImageFolder(), 'StartRace.png'), wx.BITMAP_TYPE_PNG )
		self.startRaceBtn = MakeButton( self, img = img, text = '&Start Race Now' )
		self.Bind( wx.EVT_BUTTON, self.onStartRace, self.startRaceBtn )
		self.startRaceBtn.SetFont( font )
		
		img = wx.Image( os.path.join(Utils.getImageFolder(), 'StartRaceAtTime.png'), wx.BITMAP_TYPE_PNG )
		self.startRaceTimeBtn = MakeButton( self, img = img, text = 'Start Race at &Time' )
		self.Bind( wx.EVT_BUTTON, self.onStartRaceTime, self.startRaceTimeBtn )
		self.startRaceTimeBtn.SetFont( font )
		
		img = wx.Image( os.path.join(Utils.getImageFolder(), 'FinishRace.png'), wx.BITMAP_TYPE_PNG )
		self.finishRaceBtn = MakeButton( self, img = img, text = '&Finish Race' )
		self.Bind( wx.EVT_BUTTON, self.onFinishRace, self.finishRaceBtn )
		self.finishRaceBtn.SetFont( font )
		
		border = 0
		bs.Add(self.startRaceBtn, pos=(0,0), span=(1,1), border=border, flag=wx.TOP|wx.LEFT)
		bs.Add(self.startRaceTimeBtn, pos=(0,1), span=(1,1), border=border, flag=wx.TOP|wx.LEFT)
		bs.Add(self.finishRaceBtn, pos=(1,0), span=(1,1), border=border, flag=wx.TOP|wx.LEFT)
		bs.AddGrowableRow( 1 )
		self.SetSizer(bs)
		
		self.refresh()
	
	def onStartRace( self, event ):
		if Model.race is not None and Utils.MessageOKCancel(self, 'Start Race Now?', 'Start Race'):
			StartRaceNow()
	
	def onStartRaceTime( self, event ):
		if Model.race is None:
			return
		dlg = StartRaceAtTime( self )
		dlg.ShowModal()
		dlg.Destroy()  
	
	def onFinishRace( self, event ):
		if Model.race is None or not Utils.MessageOKCancel(self, 'Finish Race Now?', 'Finish Race'):
			return
			
		with Model.LockRace() as race:
			race.finishRaceNow()
			if race.numLaps is None:
				race.numLaps = race.getMaxLap()
			Model.resetCache()
		
		Utils.writeRace()
		self.refresh()
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.refresh()
		JChip.StopListener()
		
		# Give the output streamer a chance to write the last message.
		OutputStreamer.writeRaceFinish()
		wx.CallLater( 2000, OutputStreamer.StopStreamer )
	
	def refresh( self ):
		self.startRaceBtn.Enable( False )
		self.startRaceTimeBtn.Enable( False )
		self.finishRaceBtn.Enable( False )
		with Model.LockRace() as race:
			if race is not None:
				if race.startTime is None:
					self.startRaceBtn.Enable( True )
					self.startRaceTimeBtn.Enable( True )
				elif race.isRunning():
					self.finishRaceBtn.Enable( True )
		mainWin = Utils.getMainWin()
		if mainWin is not None:
			mainWin.updateRaceClock()
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	actions = Actions(mainWin)
	Model.newRace()
	actions.refresh()
	mainWin.Show()
	app.MainLoop()