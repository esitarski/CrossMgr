import wx
from wx.lib.wordwrap import wordwrap
from roundbutton import RoundButton
from HighPrecisionTimeEdit import HighPrecisionTimeEdit

import datetime

import Model
import Utils
import ChipReader
import OutputStreamer
from FtpWriteFile import realTimeFtpPublish
import Properties
from Undo import undo
import Checklist
from Clock import Clock
from CountdownClock import CountdownClock, EVT_COUNTDOWN
from SetNoDataDNS import SetNoDataDNS
from Properties import PropertiesDialog

undoResetTimer = None
def StartRaceNow( page=_('Record') ):
	global undoResetTimer
	if undoResetTimer and undoResetTimer.IsRunning():
		undoResetTimer.Stop()
	undoResetTimer = None
	ChipReader.chipReaderCur.reset( Model.race.chipReaderType if Model.race else None )
	
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
	
	# Refresh the main window and switch to the specified pane.
	mainWin = Utils.getMainWin()
	if mainWin is not None:
		mainWin.showPageName( page )
		mainWin.updateLapCounter()
		mainWin.refresh()
		
		if isTimeTrial:
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
		super().__init__( parent, id, _("Start Race at Time:"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		
		self.startSeconds = None
		self.timer = None
		self.futureRaceTime = None
		
		race = Model.getRace()
		autoStartLabel = wx.StaticText( self, label = _('Automatically Start Race at:') )
		
		# Make sure we don't suggest a start time in the past.
		startSeconds = Utils.StrToSeconds( race.scheduledStart ) * 60	# race.scheduledStart has no seconds.
		nowSeconds = GetNowSeconds()
		if startSeconds < nowSeconds:
			startOffset = 3 * 60
			startSeconds = nowSeconds - nowSeconds % startOffset
			startSeconds = nowSeconds + startOffset
		
		autoStartTimeSize = wx.Size(80,-1)
		self.autoStartTime = HighPrecisionTimeEdit( self, display_seconds=False, seconds=startSeconds, size=autoStartTimeSize )
		
		self.pagesLabel = wx.StaticText( self, label=_('After Start, Switch to:') )
		mainWin = Utils.getMainWin()
		if mainWin:
			pageNames = [name for a, b, name in mainWin.attrClassName]
		else:
			pageNames = [
				_('Actions'),
				_('Record'),
				_('Results'),
				_('Passings'),
				_('RiderDetail'),
				_('Chart'),
				_('Animation'),
				_('Recommendations'),
				_('Categories'),
				_('Properties'),
				_('Primes'),
				_('Situation'),
				_('LapCounter'),
			]
		pageNames = pageNames[1:]	# Skip the Actions screen.
		self.pages = wx.Choice( self, choices=pageNames )
		self.pages.SetSelection( 0 )	# Record screen.
		
		self.countdown = CountdownClock( self, size=(400,400), tFuture=None )
		self.countdown.SetBackgroundColour( wx.WHITE );
		self.Bind( EVT_COUNTDOWN, self.onCountdown )
		
		self.okBtn = wx.Button( self, wx.ID_OK, label=_('Start at Above Time') )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )
		
		self.start30 = wx.Button( self, label=_('Start in 30s') )
		self.start30.Bind( wx.EVT_BUTTON, lambda event: self.startInFuture(event, 30) )
		self.start60 = wx.Button( self, label=_('Start in 60s') )
		self.start60.Bind( wx.EVT_BUTTON, lambda event: self.startInFuture(event, 60) )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		vs = wx.BoxSizer( wx.VERTICAL )

		border = 8
		fgs = wx.FlexGridSizer( cols=4, vgap=8, hgap=8 )
		fgs.AddGrowableCol( 1 )
		fgs.Add( autoStartLabel, flag=wx.ALIGN_CENTER_VERTICAL )
		fgs.Add( self.autoStartTime, flag=wx.ALIGN_CENTER_VERTICAL )
		fgs.Add( self.pagesLabel, flag=wx.ALIGN_CENTER_VERTICAL )
		fgs.Add( self.pages, flag=wx.ALIGN_CENTER_VERTICAL )
		vs.Add( fgs, flag=wx.EXPAND|wx.ALL, border=8 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.okBtn, border = border, flag=wx.ALL )
		hs.Add( self.start30, flag=wx.TOP|wx.BOTTOM|wx.RIGHT, border = border )
		hs.Add( self.start60, flag=wx.TOP|wx.BOTTOM|wx.RIGHT, border = border)
		self.okBtn.SetDefault()
		hs.AddStretchSpacer()
		hs.Add( self.cancelBtn, flag=wx.ALL, border = border )
		vs.Add( hs, flag=wx.EXPAND )
		
		vs.Add( self.countdown, 1, border = border, flag=wx.ALL|wx.EXPAND )
		
		self.SetSizerAndFit( vs )
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )
		
		wx.CallLater( 100, self.autoStartTime.SetSize, autoStartTimeSize )

	def startInFuture( self, event, seconds ):
		startSeconds = GetNowSeconds() + seconds
		
		dt = wx.DateTime()
		dt.SetToCurrent()
		dt.SetHour( startSeconds//(60*60) )
		dt.SetMinute( (startSeconds//60)%60 )
		self.autoStartTime.SetValue( dt )
		
		return self.onOK( event, startSeconds )
		
	def onCountdown( self, event ):
		StartRaceNow( self.pages.GetStringSelection() )
		self.startTime = self.futureRaceTime
		self.EndModal( wx.ID_OK )
	
	def onOK( self, event, startSeconds = None ):
		startTime = self.autoStartTime.GetSeconds()

		self.startSeconds = startTime if startSeconds is None else startSeconds
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
					hour=0, minute=0, second=0
				) + datetime.timedelta( seconds = self.startSeconds )
		self.countdown.Start( self.futureRaceTime )
		
		# Disable buttons and switch to countdown state.
		self.okBtn.Enable( False )
		self.start30.Enable( False )
		self.start60.Enable( False )
		self.autoStartTime.Enable( False )
		
	def onCancel( self, event ):
		self.countdown.Stop()
		self.EndModal( wx.ID_CANCEL )

#-------------------------------------------------------------------------------------------
StartText = '\n'.join(_('Start Race').split(maxsplit=1))
FinishText = '\n'.join(_('Finish Race').split(maxsplit=1))

class Actions( wx.Panel ):
	iResetStartClockOnFirstTag = 1
	iSkipFirstTagRead = 2

	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__(parent, id)
		
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
		self.raceIntro.SetFont( wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.NORMAL) )
		
		self.chipTimingOptions = wx.RadioBox(
			self.leftPanel,
			label = _("Chip Timing Options"),
			majorDimension = 1,
			choices = Properties.RfidProperties.choices,
			style = wx.RA_SPECIFY_COLS
		)
		
		self.Bind( wx.EVT_RADIOBOX, self.onChipTimingOptions, self.chipTimingOptions )
		
		self.settingsButton = wx.BitmapButton( self.leftPanel, bitmap=Utils.GetPngBitmap('settings-icon.png') )
		self.settingsButton.SetToolTip( wx.ToolTip(_('Properties Shortcut')) )
		self.settingsButton.Bind( wx.EVT_BUTTON, self.onShowProperties )
		
		self.startRaceTimeCheckBox = wx.CheckBox(self.leftPanel, label = _('Start Race Automatically at Future Time'))

		hsSettings = wx.BoxSizer( wx.HORIZONTAL )
		hsSettings.Add( self.settingsButton, flag=wx.ALIGN_CENTER_VERTICAL )
		hsSettings.Add( self.startRaceTimeCheckBox, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=12 )
		
		border = 8
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add(self.button, border=border, flag=wx.LEFT|wx.TOP)
		hs.Add(self.raceIntro, 1, border=border, flag=wx.LEFT|wx.TOP|wx.RIGHT|wx.EXPAND)
		bs.Add( hs, border=border, flag=wx.ALL )
		
		hsClock = wx.BoxSizer(wx.HORIZONTAL)
		hsClock.AddSpacer( 26 )
		hsClock.Add( self.clock )
		hsClock.Add(hsSettings, border=4, flag=wx.LEFT )
		bs.Add(hsClock, border=4, flag=wx.ALL)
		
		bs.Add(self.chipTimingOptions, border=border, flag=wx.ALL)
		
		#---------------------------------------------------------------------------------------------
		
		self.rightPanel = wx.Panel( self.splitter )
		self.rightPanel.SetBackgroundColour( wx.Colour(255,255,255) )
		checklistTitle = wx.StaticText( self.rightPanel, label = _('Checklist:') )
		checklistTitle.SetFont( wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL) )
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
		wx.CallAfter( self.GetSizer().Layout )
		
	def setWrappedRaceInfo( self, event = None ):
		wrapWidth = self.leftPanel.GetClientSize()[0] - self.button.GetClientSize()[0] - 20
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
	
	def onShowProperties( self, event ):
		if not Model.race:
			Utils.MessageOK(self, _("You must have a valid race.  Open or New a race first."), _("No Valid Race"), iconMask=wx.ICON_ERROR)
			return
		if not hasattr(self, 'propertiesDialog'):
			self.propertiesDialog = PropertiesDialog( self, showFileFields=False, updateProperties=True, size=(600,400) )
		else:
			self.propertiesDialog.properties.refresh( forceUpdate = True )
		self.propertiesDialog.properties.setPage( 'raceOptionsProperties' )
		if self.propertiesDialog.ShowModal() == wx.ID_OK:
			self.propertiesDialog.properties.doCommit()
			Utils.refresh()

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
			except Exception:
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
		if Model.race and Utils.MessageOKCancel(self, _('Start Race Now?\n\n'), _('Start Race')):
			StartRaceNow()
	
	def onStartRaceTime( self, event ):
		if Model.race is None:
			return
		dlg = StartRaceAtTime( self )
		dlg.ShowModal()
		dlg.Destroy()  
	
	def onFinishRace( self, event, confirm=True ):
		if Model.race is None:
			return
		if confirm and not Utils.MessageOKCancel(self, _('Finish Race Now?'), _('Finish Race')):
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
		
		OutputStreamer.writeRaceFinish()
		OutputStreamer.StopStreamer()
		try:
			ChipReader.chipReaderCur.StopListener()
		except Exception:
			pass

		if getattr(Model.race, 'ftpUploadDuringRace', False):
			realTimeFtpPublish.publishEntry( True )
	
	def commit( self ):
		self.checklist.commit()
	
	def refresh( self ):
		self.clock.Start()
		self.button.Enable( False )
		self.startRaceTimeCheckBox.Enable( False )
		self.settingsButton.Enable( False )
		self.button.SetLabel( StartText )
		self.button.SetForegroundColour( wx.Colour(100,100,100) )
		self.chipTimingOptions.SetSelection( 0 )
		self.chipTimingOptions.Enable( False )
		
		with Model.LockRace() as race:
			if race:
				self.settingsButton.Enable( True )
				
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
	
