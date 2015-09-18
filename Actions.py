import wx
from wx.lib.wordwrap import wordwrap
import wx.lib.masked as masked
from roundbutton import RoundButton

import datetime

import Model
import Utils
import JChip
import OutputStreamer
from FtpWriteFile import realTimeFtpPublish
import Properties
from Undo import undo
import Checklist
from Clock import Clock
from CountdownClock import CountdownClock, EVT_COUNTDOWN
from SetNoDataDNS import SetNoDataDNS

undoResetTimer = None
def StartRaceNow():
	global undoResetTimer
	if undoResetTimer and undoResetTimer.IsRunning():
		undoResetTimer.Stop()
	undoResetTimer = None
	JChip.reset()
	
	undo.clear()
	undo.pushState()
	with Model.LockRace() as race:
		if race is None:
			return
		
		if not race.enableJChipIntegration:
			race.resetStartClockOnFirstTag = False
		
		Model.resetCache()
		race.startRaceNow()
		isTimeTrial = race.isTimeTrial
		
	OutputStreamer.writeRaceStart()
	
	# Refresh the main window and switch to the Record pane.
	mainWin = Utils.getMainWin()
	if mainWin is not None:
		mainWin.showPageName( _('Record') )
		mainWin.updateLapCounter()
		mainWin.refresh()
		
		if isTimeTrial and Utils.MessageOKCancel( mainWin, _('Create TTStart HTML Page?'), _('Create TTStart HTML Page?') ):
			mainWin.menuPublishHtmlTTStart()
	
	# For safety, clear the undo stack after 8 seconds.
	undoResetTimer = wx.CallLater( 8000, undo.clear )
	
	if race.ftpUploadDuringRace:
		realTimeFtpPublish.publishEntry( True )

def GetNowSeconds():
	t = datetime.datetime.now()
	return t.hour * 60 * 60 + t.minute * 60 + t.second
		
class StartRaceAtTime( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, _("Start Race at Time:"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		font = wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		
		self.startSeconds = None
		self.timer = None
		self.futureRaceTime = None
		
		race = Model.getRace()
		autoStartLabel = wx.StaticText( self, label = _('Automatically Start Race at:') )
		
		# Make sure we don't suggest a start time in the past.
		value = race.scheduledStart
		startSeconds = Utils.StrToSeconds( value ) * 60
		nowSeconds = GetNowSeconds()
		if startSeconds < nowSeconds:
			startOffset = 3 * 60
			startSeconds = nowSeconds - nowSeconds % startOffset
			startSeconds = nowSeconds + startOffset
			value = u'%02d:%02d' % (startSeconds / (60*60), (startSeconds / 60) % 60)
		
		self.autoStartTime = masked.TimeCtrl( self, fmt24hr=True, display_seconds=False, value=value )
		
		self.countdown = CountdownClock( self, size=(190,190), tFuture=None )
		self.Bind( EVT_COUNTDOWN, self.onCountdown )
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		vs = wx.BoxSizer( wx.VERTICAL )

		border = 8
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( autoStartLabel, border = border, flag=wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL )
		hs.Add( self.autoStartTime, border = border, flag=wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_BOTTOM )
		vs.Add( hs )
		
		vs.Add( self.countdown, 1, border = border, flag=wx.ALL|wx.ALIGN_CENTRE|wx.EXPAND )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.okBtn, border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		hs.AddStretchSpacer()
		hs.Add( self.cancelBtn, border = border, flag=wx.ALL )
		vs.Add( hs, flag=wx.EXPAND )
		
		self.SetSizerAndFit( vs )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onCountdown( self, event ):
		StartRaceNow()
		self.startTime = self.futureRaceTime
		self.EndModal( wx.ID_OK )
	
	def onOK( self, event ):
		startTime = self.autoStartTime.GetValue()

		self.startSeconds = Utils.StrToSeconds( startTime ) * 60.0
		if self.startSeconds < GetNowSeconds():
			Utils.MessageOK(
				None,
				u'\n\n'.join( [_('Scheduled Start Time is in the Past'),_('Please enter a Scheduled Start Time in the Future.')] ),
				_('Scheduled Start Time is in the Past')
			)
			return
			
		dateToday = datetime.date.today()
		self.futureRaceTime = datetime.datetime(
					year=dateToday.year, month=dateToday.month, day=dateToday.day,
					hour = 0, minute = 0, second = 0
				) + datetime.timedelta( seconds = self.startSeconds )
		self.countdown.Start( self.futureRaceTime )
		
		# Disable buttons and switch to countdown state.
		self.okBtn.Enable( False )
		self.autoStartTime.Enable( False )
		
	def onCancel( self, event ):
		self.countdown.Stop()
		self.EndModal( wx.ID_CANCEL )

#-------------------------------------------------------------------------------------------
StartText = u'\n'.join(_('Start Race').split())
FinishText = u'\n'.join(_('Finish Race').split())

class Actions( wx.Panel ):
	iResetStartClockOnFirstTag = 1
	iSkipFirstTagRead = 2

	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		
		self.SetBackgroundColour( wx.Colour(255,255,255) )
		
		ps = wx.BoxSizer( wx.VERTICAL )
		self.splitter = wx.SplitterWindow( self, wx.VERTICAL )
		ps.Add( self.splitter, 1, flag=wx.EXPAND )
		self.SetSizer( ps )
		
		#---------------------------------------------------------------------------------------------
		
		self.leftPanel = wx.Panel( self.splitter )
		bs = wx.BoxSizer( wx.VERTICAL )
		self.leftPanel.SetSizer( bs )
		self.leftPanel.SetBackgroundColour( wx.Colour(255,255,255) )
		self.leftPanel.Bind( wx.EVT_SIZE, self.setWrappedRaceInfo )
		
		buttonSize = 220
		self.button = RoundButton( self.leftPanel, size=(buttonSize, buttonSize) )
		self.button.SetLabel( FinishText )
		self.button.SetFontToFitLabel()
		self.button.SetForegroundColour( wx.Colour(128,128,128) )
		self.Bind(wx.EVT_BUTTON, self.onPress, self.button )
		
		self.clock = Clock( self, size=(190,190), checkFunc=self.updateClock )
		self.clock.SetBackgroundColour( wx.WHITE )
		
		self.raceIntro = wx.StaticText( self.leftPanel, label =  u'' )
		self.raceIntro.SetFont( wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL) )
		
		self.chipTimingOptions = wx.RadioBox(
			self.leftPanel,
			label = _("Chip Timing Options"),
			majorDimension = 1,
			choices = Properties.RfidProperties.choices,
			style = wx.RA_SPECIFY_COLS
		)
		
		self.Bind( wx.EVT_RADIOBOX, self.onChipTimingOptions, self.chipTimingOptions )
		
		self.startRaceTimeCheckBox = wx.CheckBox(self.leftPanel, label = _('Start Race Automatically at Future Time'))
		
		border = 8
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add(self.button, border=border, flag=wx.LEFT|wx.TOP)
		hs.Add(self.raceIntro, 1, border=border, flag=wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND)
		bs.Add( hs, border=border, flag=wx.ALL )
		
		hsClock = wx.BoxSizer(wx.HORIZONTAL)
		hsClock.AddSpacer( 26 )
		hsClock.Add( self.clock )
		hsClock.Add(self.startRaceTimeCheckBox, border=4, flag=wx.LEFT)
		bs.Add(hsClock, border=4, flag=wx.ALL)
		
		bs.Add(self.chipTimingOptions, border=border, flag=wx.ALL)
		
		#---------------------------------------------------------------------------------------------
		
		self.rightPanel = wx.Panel( self.splitter )
		self.rightPanel.SetBackgroundColour( wx.Colour(255,255,255) )
		checklistTitle = wx.StaticText( self.rightPanel, label = _('Checklist:') )
		checklistTitle.SetFont( wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL) )
		self.checklist = Checklist.Checklist( self.rightPanel )
		
		hsSub = wx.BoxSizer( wx.VERTICAL )
		hsSub.Add( checklistTitle, 0, flag=wx.ALL, border = 4 )
		hsSub.Add( self.checklist, 1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border = 4 )
		self.rightPanel.SetSizer( hsSub )
		
		#---------------------------------------------------------------------------------------------
		
		self.splitter.SplitVertically( self.leftPanel, self.rightPanel )
		self.splitter.SetMinimumPaneSize( 100 )
		wx.CallAfter( self.refresh )
		wx.CallAfter( self.splitter.SetSashPosition, 650 )
		
	def setWrappedRaceInfo( self, event = None ):
		wrapWidth = self.leftPanel.GetClientSizeTuple()[0] - self.button.GetClientSizeTuple()[0] - 20
		dc = wx.WindowDC( self.raceIntro )
		dc.SetFont( self.raceIntro.GetFont() )
		label = wordwrap( Model.race.getRaceIntro() if Model.race else u'', wrapWidth, dc )
		self.raceIntro.SetLabel( label )
		self.leftPanel.GetSizer().Layout()
		if event:
			event.Skip()
		
	def updateChipTimingOptions( self ):
		if not Model.race:
			return
			
		iSelection = self.chipTimingOptions.GetSelection()
		race = Model.race
		race.resetStartClockOnFirstTag	= bool(iSelection == self.iResetStartClockOnFirstTag)
		race.skipFirstTagRead			= bool(iSelection == self.iSkipFirstTagRead)
	
	def updateClock( self ):
		mainWin = Utils.getMainWin()
		return not mainWin or mainWin.isShowingPage(self)
	
	def onChipTimingOptions( self, event ):
		if not Model.race:
			return
		self.updateChipTimingOptions()
	
	def onPress( self, event ):
		if not Model.race:
			return
		with Model.LockRace() as race:
			running = race.isRunning()
		if running:
			self.onFinishRace( event )
			return
			
		self.updateChipTimingOptions()
		if getattr(Model.race, 'enableJChipIntegration', False):
			try:
				externalFields = race.excelLink.getFields()
				externalInfo = race.excelLink.read()
			except:
				externalFields = []
				externalInfo = {}
			if not externalInfo:
				Utils.MessageOK(
					self,
					u'\n\n'.join( [_('Cannot Start. Excel Sheet read failure.'), _('The Excel file is either unconfigured or unreadable.')] ),
					_('Excel Sheet Read '),
					wx.ICON_ERROR
				)
				return
			try:
				i = next((i for i, field in enumerate(externalFields) if field.startswith('Tag')))
			except StopIteration:
				Utils.MessageOK(
					self,
					u'\n\n'.join( [_('Cannot Start.  Excel Sheet missing Tag column.'), _('The Excel file must contain a Tag column to use RFID.')] ),
					_('Excel Sheet missing Tag column'),
					wx.ICON_ERROR
				)
				return
				
		if self.startRaceTimeCheckBox.IsChecked():
			self.onStartRaceTime( event )
		else:
			self.onStartRace( event )
	
	def onStartRace( self, event ):
		if Model.race and Utils.MessageOKCancel(self, _('Start Race Now?'), _('Start Race')):
			StartRaceNow()
	
	def onStartRaceTime( self, event ):
		if Model.race is None:
			return
		dlg = StartRaceAtTime( self )
		dlg.ShowModal()
		dlg.Destroy()  
	
	def onFinishRace( self, event ):
		if Model.race is None or not Utils.MessageOKCancel(self, _('Finish Race Now?'), _('Finish Race')):
			return
			
		with Model.LockRace() as race:
			race.finishRaceNow()
			if race.numLaps is None:
				race.numLaps = race.getMaxLap()
			SetNoDataDNS()
			Model.resetCache()
		
		Utils.writeRace()
		self.refresh()
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.refresh()
		JChip.StopListener()
		
		OutputStreamer.writeRaceFinish()
		OutputStreamer.StopStreamer()
		
		if getattr(Model.race, 'ftpUploadDuringRace', False):
			realTimeFtpPublish.publishEntry( True )
	
	def refresh( self ):
		self.clock.Start()
		self.button.Enable( False )
		self.startRaceTimeCheckBox.Enable( False )
		self.button.SetLabel( StartText )
		self.button.SetForegroundColour( wx.Colour(100,100,100) )
		self.chipTimingOptions.SetSelection( 0 )
		self.chipTimingOptions.Enable( False )
		
		with Model.LockRace() as race:
			if race:
				# Adjust the chip recording options for TT.
				if getattr(race, 'isTimeTrial', False):
					race.resetStartClockOnFirstTag = False
					race.skipFirstTagRead = False
					
				if getattr(race, 'resetStartClockOnFirstTag', True):
					self.chipTimingOptions.SetSelection( self.iResetStartClockOnFirstTag )
				elif getattr(race, 'skipFirstTagRead', False):
					self.chipTimingOptions.SetSelection( self.iSkipFirstTagRead )
					
				if race.startTime is None:
					self.button.Enable( True )
					self.button.SetLabel( StartText )
					self.button.SetForegroundColour( wx.Colour(0,128,0) )
					
					self.startRaceTimeCheckBox.Enable( True )
					self.startRaceTimeCheckBox.Show( True )
					
					self.chipTimingOptions.Enable( getattr(race, 'enableJChipIntegration', False) )
					self.chipTimingOptions.Show( getattr(race, 'enableJChipIntegration', False) )
				elif race.isRunning():
					self.button.Enable( True )
					self.button.SetLabel( FinishText )
					self.button.SetForegroundColour( wx.Colour(128,0,0) )
					
					self.startRaceTimeCheckBox.Enable( False )
					self.startRaceTimeCheckBox.Show( False )
					
					self.chipTimingOptions.Enable( False )
					self.chipTimingOptions.Show( False )
					
				# Adjust the time trial display options.
				if getattr(race, 'isTimeTrial', False):
					self.chipTimingOptions.Enable( False )
					self.chipTimingOptions.Show( False )
					
			self.GetSizer().Layout()
		
		self.setWrappedRaceInfo()
		self.checklist.refresh()
		
		mainWin = Utils.getMainWin()
		if mainWin is not None:
			mainWin.updateRaceClock()
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	actions = Actions(mainWin)
	Model.newRace()
	Model.race.enableJChipIntegration = False
	Model.race.isTimeTrial = False
	actions.refresh()
	mainWin.Show()
	app.MainLoop()
	
