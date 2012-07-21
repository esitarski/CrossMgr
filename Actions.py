import wx
import datetime
import os

import Model
import Utils
import JChip
import OutputStreamer
from Undo import undo

import wx.lib.masked as masked
from roundbutton import RoundButton

def StartRaceNow():
	undo.clear()
	with Model.LockRace() as race:
		if race is None:
			return
		
		if not getattr(race, 'enableJChipIntegration', False):
			race.resetStartClockOnFirstTag = False
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
				border = border, flag=wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL )
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
		if self.startSeconds < GetNowSeconds():
			Utils.MessageOK( None, 'Scheduled Start Time is in the Past.\n\nPlease enter a Scheduled Start Time in the Future.', 'Scheduled Start Time is in the Past' )
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

#-------------------------------------------------------------------------------------------
StartText = 'Start\nRace'
FinishText = 'Finish\nRace'

class Actions( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		bs = wx.BoxSizer( wx.VERTICAL )
		
		self.SetBackgroundColour( wx.Colour(255,255,255) )
		
		buttonSize = 220
		self.button = RoundButton( self, wx.ID_ANY, size=(buttonSize, buttonSize) )
		self.button.SetLabel( FinishText )
		self.button.SetFontToFitLabel()
		self.button.SetForegroundColour( wx.Colour(128,128,128) )
		self.Bind(wx.EVT_BUTTON, self.onPress, self.button )
		
		self.resetStartClockCheckBox = wx.CheckBox( self, wx.ID_ANY, 'Reset Start Clock on First Tag Read (all riders will get the same start time)' )
		self.Bind( wx.EVT_CHECKBOX, self.onResetStartClock, self.resetStartClockCheckBox )
		
		self.startRaceTimeCheckBox = wx.CheckBox(self, wx.ID_ANY, 'Start Race Automatically at Future Time')
		
		border = 8
		bs.Add(self.button, border=border, flag=wx.ALL)
		bs.Add(self.resetStartClockCheckBox, border=border, flag=wx.ALL)
		bs.Add(self.startRaceTimeCheckBox, border=border, flag=wx.ALL)
		self.SetSizer(bs)
		
		self.refresh()
	
	def onResetStartClock( self, event ):
		if not Model.race:
			return
		with Model.LockRace() as race:
			race.resetStartClockOnFirstTag = bool(self.resetStartClockCheckBox.IsChecked())
	
	def onPress( self, event ):
		if not Model.race:
			return
		with Model.LockRace() as race:
			running = race.isRunning()
		if running:
			self.onFinishRace( event )
			return
			
		race.resetStartClockOnFirstTag = bool(self.resetStartClockCheckBox.IsChecked())
		if getattr(Model.race, 'enableJChipIntegration', False):
			try:
				externalFields = race.excelLink.getFields()
				externalInfo = race.excelLink.read()
			except:
				externalFields = []
				externalInfo = {}
			if not externalInfo:
				Utils.MessageOK(self, 'Cannot Start. Excel Sheet read failure.\nThe Excel file is either unconfigured or unreadable.', 'Excel Sheet Read ', wx.ICON_ERROR )
				return
			try:
				i = (i for i, field in enumerate(externalFields) if field.startswith('Tag')).next()
			except StopIteration:
				Utils.MessageOK(self, 'Cannot Start.  Excel Sheet missing Tag or Tag2 column.\nThe Excel file must contain a Tag column to use JChip.', 'Excel Sheet missing Tag or Tag2 column', wx.ICON_ERROR )
				return
				
		if self.startRaceTimeCheckBox.IsChecked():
			self.onStartRaceTime( event )
		else:
			self.onStartRace( event )
	
	def onStartRace( self, event ):
		if Model.race and Utils.MessageOKCancel(self, 'Start Race Now?', 'Start Race'):
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
		
		OutputStreamer.writeRaceFinish()
		OutputStreamer.StopStreamer()
	
	def refresh( self ):
		self.button.Enable( False )
		self.startRaceTimeCheckBox.Enable( False )
		self.resetStartClockCheckBox.Enable( False )
		self.button.SetLabel( StartText )
		self.button.SetForegroundColour( wx.Colour(100,100,100) )
		with Model.LockRace() as race:
			self.resetStartClockCheckBox.SetValue( bool(getattr(race, 'resetStartClockOnFirstTag', True)) if race else False )
			if race is not None:
				if race.startTime is None:
					self.button.Enable( True )
					self.button.SetLabel( StartText )
					self.button.SetForegroundColour( wx.Colour(0,128,0) )
					
					self.startRaceTimeCheckBox.Enable( True )
					self.startRaceTimeCheckBox.Show( True )
					
					self.resetStartClockCheckBox.Enable( getattr(race, 'enableJChipIntegration', False) )
					self.resetStartClockCheckBox.Show( getattr(race, 'enableJChipIntegration', False) )
					
				elif race.isRunning():
					self.button.Enable( True )
					self.button.SetLabel( FinishText )
					self.button.SetForegroundColour( wx.Colour(128,0,0) )
					
					self.startRaceTimeCheckBox.Enable( False )
					self.startRaceTimeCheckBox.Show( False )
					
					self.resetStartClockCheckBox.Enable( False )
					self.resetStartClockCheckBox.Show( False )
					
		mainWin = Utils.getMainWin()
		if mainWin is not None:
			mainWin.updateRaceClock()
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	actions = Actions(mainWin)
	Model.newRace()
	actions.refresh()
	mainWin.Show()
	app.MainLoop()