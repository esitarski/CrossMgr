import wx
import re
import os
import wx.lib.intctrl as intctrl
import wx.lib.agw.flatnotebook as flatnotebook
import glob
import webbrowser
import threading
import subprocess
import platform
from RaceInputState import RaceInputState
import Utils
import Model
from Undo import undo
import ImageIO
from SetGraphic			import SetGraphicDialog
from FtpWriteFile import FtpProperties, FtpUploadFile, FtpIsConfigured, FtpPublishDialog
from FtpUploadProgress import FtpUploadProgress
from LapCounter import LapCounterProperties
from GeoAnimation import GeoAnimation
from GpxImport import GetGeoTrack
from TemplateSubstitute import TemplateSubstitute
import Template
from BatchPublishAttrs import batchPublishAttr, batchPublishRaceAttr
from HighPrecisionTimeEdit import HighPrecisionTimeEdit
import JChipSetup
import WebServer
import ChipReader
import HelpSearch

#------------------------------------------------------------------------------------------------

def GetTemplatesFolder():
	return os.path.join( os.path.expanduser("~"), 'CrossMgrTemplates' )

def addToFGS( fgs, labelFieldBatchPublish ):
	for item, column, flag in labelFieldBatchPublish:
		if not item:
			continue
		if column == 1:
			flag |= wx.EXPAND
		fgs.Add( item, flag=flag )

class GeneralInfoProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id )
		
		self.raceNameLabel = wx.StaticText( self, label=_('Event Name:') )
		self.raceName = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceName )
		
		self.raceLongNameLabel = wx.StaticText( self, label=_('Long Name:') )
		self.raceLongName = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceLongName )
		
		self.raceCityLabel = wx.StaticText( self, label=_('City') )
		self.raceCity = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceCity )
		
		self.raceStateProvLabel = wx.StaticText( self, label=_('State/Prov') )
		self.raceStateProv = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceStateProv )
		
		self.raceCountryLabel = wx.StaticText( self, label=_('Country') )
		self.raceCountry = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceCountry )
		
		self.locationSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.locationSizer.Add( self.raceCity, 4, flag=wx.EXPAND )
		self.locationSizer.Add( self.raceStateProvLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )
		self.locationSizer.Add( self.raceStateProv, 2, flag=wx.EXPAND|wx.LEFT, border=3 )
		self.locationSizer.Add( self.raceCountryLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )
		self.locationSizer.Add( self.raceCountry, 2, flag=wx.EXPAND|wx.LEFT, border=3 )
		
		self.dateLabel = wx.StaticText( self, label = _('Date') )
		dt = Utils.GetDateTimeToday()
		self.date = wx.adv.DatePickerCtrl(
			self,
			dt = dt,
			style = wx.adv.DP_DROPDOWN,
			size=(160,-1)
		)
		# Set a date range to avoid crashing on invalid years.
		self.date.SetRange( dt - wx.DateSpan(years=25), dt + wx.DateSpan(years=25) )
		self.Bind(wx.adv.EVT_DATE_CHANGED, self.onChanged, self.date)
		
		self.raceDisciplineLabel = wx.StaticText( self, label = _('Discipline') )
		self.raceDiscipline = wx.TextCtrl( self, value='Cyclo-cross', size=(160,-1) )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceDiscipline )
		
		self.dateDisciplineSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.dateDisciplineSizer.Add( self.date )
		self.dateDisciplineSizer.Add( self.raceDisciplineLabel, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border = 16 )
		self.dateDisciplineSizer.Add( self.raceDiscipline, flag=wx.LEFT, border=3 )
		self.dateDisciplineSizer.AddStretchSpacer()

		self.raceNumLabel = wx.StaticText( self, label=_('Race #') )
		self.raceNum = intctrl.IntCtrl( self, min=1, max=1000, allow_none=False, value=1, size=(64,-1), style=wx.ALIGN_RIGHT )
		self.Bind(intctrl.EVT_INT, self.onChanged, self.raceNum)
		
		self.scheduledStartLabel = wx.StaticText( self, label=_('Scheduled Start') )
		self.scheduledStart = HighPrecisionTimeEdit( self, display_seconds=False, value='10:00', size=(64,-1) )
		
		self.minutesLabel = wx.StaticText( self, label=_('Race Minutes') )
		self.minutes = intctrl.IntCtrl( self, min=1, max=60*48, allow_none=False, value=40, size=(64,-1), style=wx.ALIGN_RIGHT )

		self.numStartMinutesSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.numStartMinutesSizer.Add( self.raceNum )
		self.numStartMinutesSizer.Add( self.scheduledStartLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border = 16 )
		self.numStartMinutesSizer.Add( self.scheduledStart, flag=wx.FIXED_MINSIZE|wx.LEFT, border = 3 )
		self.numStartMinutesSizer.Add( self.minutesLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border = 16 )
		self.numStartMinutesSizer.Add( self.minutes, flag=wx.LEFT, border = 3 )
		self.numStartMinutesSizer.AddStretchSpacer()

		self.organizerLabel = wx.StaticText( self, label=_('Organizer') )
		self.organizer = wx.TextCtrl( self )

		self.commissaireLabel = wx.StaticText( self, label=_('Official/Commissaire') )
		self.commissaire = wx.TextCtrl( self )

		self.memoLabel = wx.StaticText( self, label=_('Memo') )
		self.memo = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.memo )
		
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		fgs = wx.FlexGridSizer( rows=0, cols=2, vgap=12, hgap=3 )
		fgs.AddGrowableCol( 1 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fieldAlign = wx.EXPAND
		
		labelFieldBatchPublish = [
			(self.raceNameLabel,	0, labelAlign),	(self.raceName,				1, fieldAlign),
			(self.raceLongNameLabel,0, labelAlign),	(self.raceLongName,			1, fieldAlign),
			(self.raceCityLabel,	0, labelAlign),	(self.locationSizer,		1, fieldAlign),
			(self.dateLabel,		0, labelAlign),	(self.dateDisciplineSizer,	1, fieldAlign),
			(self.raceNumLabel,		0, labelAlign),	(self.numStartMinutesSizer,	1, fieldAlign),
			(self.organizerLabel,	0, labelAlign),	(self.organizer, 			1, fieldAlign),
			(self.commissaireLabel,	0, labelAlign),	(self.commissaire, 			1, fieldAlign),
			(self.memoLabel,		0, labelAlign),	(self.memo, 				1, fieldAlign),
		]
		addToFGS( fgs, labelFieldBatchPublish )
		
		ms.Add( fgs, 1, flag=wx.EXPAND|wx.ALL, border=16 )

	def refresh( self ):
		race = Model.race
		self.raceName.SetValue( race.name )
		self.raceLongName.SetValue( race.longName )
		self.raceCity.SetValue( race.city )
		self.raceStateProv.SetValue( race.stateProv )
		self.raceCountry.SetValue( race.country )
		self.raceDiscipline.SetValue( getattr(race, 'discipline', 'Cyclo-cross') )
		d = wx.DateTime()
		d.ParseDate(race.date)
		self.date.SetValue( d )
		self.raceNum.SetValue( race.raceNum )
		self.scheduledStart.SetValue( race.scheduledStart )
		self.minutes.SetValue( race.minutes )
		self.organizer.SetValue( getattr(race, 'organizer', '') )
		self.commissaire.SetValue( getattr(race, 'commissaire', '') )
		self.memo.SetValue( race.memo )

	def commit( self ):
		race = Model.race
		race.name = self.raceName.GetValue().strip()
		race.longName = self.raceLongName.GetValue().strip()
		race.city = self.raceCity.GetValue().strip()
		race.stateProv = self.raceStateProv.GetValue().strip()
		race.country = self.raceCountry.GetValue().strip()
		race.discipline = self.raceDiscipline.GetValue().strip()
		race.date = self.date.GetValue().Format(Properties.dateFormat)
		race.raceNum = self.raceNum.GetValue()
		race.scheduledStart = self.scheduledStart.GetValue()
		race.minutes = self.minutes.GetValue()
		race.organizer = self.organizer.GetValue().strip()
		race.commissaire = self.commissaire.GetValue().strip()
		race.memo = self.memo.GetValue().strip()

	def onChanged( self, event ):
		#self.updateFileName()
		pass

#------------------------------------------------------------------------------------------------

class RaceOptionsProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id )
		
		self.timeTrial = wx.CheckBox( self, label=_('Time Trial') )
		self.timeTrial.Bind(wx.EVT_CHECKBOX, self.onChangeTimeTrial )
		
		self.allCategoriesFinishAfterFastestRidersLastLap = wx.CheckBox( self, label=_("All Categories Finish After Fastest Rider's Last Lap") )
		self.allCategoriesFinishAfterFastestRidersLastLap.SetValue( False )
		
		self.autocorrectLapsDefault = wx.CheckBox( self, label=_('Set "Autocorrect Lap Data" option by Default') )
		self.autocorrectLapsDefault.SetValue( True )

		self.highPrecisionTimes = wx.CheckBox( self, label=_('Show Times to 100s of a Second') )
		self.roadRaceFinishTimes = wx.CheckBox( self, label=_('Road Race Finish Times (ignore decimals, groups get same time)') )
		self.estimateLapsDownFinishTime = wx.CheckBox( self, label=_('Estimate Laps Down Finish Time (requires Road Race Finish Times)') )
		self.setNoDataDNS = wx.CheckBox( self, label=_('Consider Riders in Spreadsheet to be DNS if no race data') )
		
		self.rule80MinLapCountLabel = wx.StaticText( self, label=_("Lap Time for 80% Rule: ") )
		self.rule80MinLapCount1 = wx.RadioButton( self, label=_("1st Lap Time"), style=wx.RB_GROUP )
		self.rule80MinLapCount2 = wx.RadioButton( self, label=_("2nd Lap Time") )
		self.rule80MinLapCount2.SetValue( True )
		self.rule80MinLapCountSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.rule80MinLapCountSizer.Add( self.rule80MinLapCount1, flag=wx.RIGHT, border=8 )
		self.rule80MinLapCountSizer.Add( self.rule80MinLapCount2 )
		
		self.distanceUnitLabel = wx.StaticText( self, label=_('Distance Unit: ') )
		self.distanceUnit = wx.Choice( self, choices=['km', 'miles'] )
		self.distanceUnit.SetSelection( 0 )
		self.distanceUnitSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.distanceUnitSizer.Add( self.distanceUnit )
		self.distanceUnitSizer.AddStretchSpacer()
		
		self.showDetails = wx.CheckBox( self, label=_("Show Lap Notes, Edits and Projected Times in HTML Output") )
		self.showCourseAnimationInHtml = wx.CheckBox( self, label=_("Show Course Animation in Html") )
		self.showCourseAnimationInHtml.SetValue( True )

		self.minPossibleLapTimeLabel = wx.StaticText( self, label=_('Min. Possible Lap Time: ') )
		self.minPossibleLapTime = HighPrecisionTimeEdit( self, seconds = 0.0 )
		self.minPossibleLapTimeUnit = wx.StaticText( self, label=_('hh:mm:ss.ddd') )
		mplths = wx.BoxSizer( wx.HORIZONTAL )
		mplths.Add( self.minPossibleLapTime )		
		mplths.Add( self.minPossibleLapTimeUnit, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=4 )

		self.licenseLinkTemplateLabel = wx.StaticText( self, label=_('License Link HTML Template: ') )
		self.licenseLinkTemplate = wx.TextCtrl( self, size=(64,-1), style=wx.TE_PROCESS_ENTER )
		
		self.winAndOut = wx.CheckBox( self, label=_("Win and Out") )
		self.winAndOut.SetValue( False )
		self.winAndOut.Bind(wx.EVT_CHECKBOX, self.onChangeWinAndOut )

		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.HORIZONTAL )
		self.SetSizer( ms )
		
		fgs = wx.FlexGridSizer( rows=0, cols=2, vgap=7, hgap=3 )
		fgs.AddGrowableCol( 1 )

		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fieldAlign = wx.EXPAND
		
		blank = lambda : wx.StaticText( self, label='' )
		
		labelFieldBatchPublish = [
			(blank(),				0, labelAlign),		(self.timeTrial,				1, fieldAlign),
			(blank(),				0, labelAlign),		(self.allCategoriesFinishAfterFastestRidersLastLap,	1, fieldAlign),
			(blank(),				0, labelAlign),		(self.autocorrectLapsDefault,	1, fieldAlign),
			(blank(),				0, labelAlign),		(self.highPrecisionTimes,		1, fieldAlign),
			(blank(),				0, labelAlign),		(self.roadRaceFinishTimes,		1, fieldAlign),
			(blank(),				0, labelAlign),		(self.estimateLapsDownFinishTime,		1, fieldAlign),
			(blank(),				0, labelAlign),		(self.setNoDataDNS,				1, fieldAlign),
			(self.rule80MinLapCountLabel, 0, labelAlign),(self.rule80MinLapCountSizer,	1, fieldAlign),
			(self.distanceUnitLabel,0, labelAlign),		(self.distanceUnitSizer,		1, fieldAlign),
			(blank(),				0, labelAlign),		(self.showDetails,				1, fieldAlign),
			(blank(),				0, labelAlign),		(self.showCourseAnimationInHtml,1, fieldAlign),
			(self.minPossibleLapTimeLabel,0, labelAlign),(mplths,						0, 0),
			(self.licenseLinkTemplateLabel,0, labelAlign),(self.licenseLinkTemplate,	1, fieldAlign),
			(blank(),				0, labelAlign),		(self.winAndOut,				1, fieldAlign),
		]
		addToFGS( fgs, labelFieldBatchPublish )
		
		ms.Add( fgs, 1, flag=wx.EXPAND|wx.ALL, border=16 )

	def onChangeTimeTrial( self, event=None ):
		self.timeTrial.SetBackgroundColour( wx.Colour(255, 204, 153) if self.timeTrial.GetValue() else wx.WHITE )
		if event:
			event.Skip()
     
	def onChangeWinAndOut( self, event=None ):
		self.winAndOut.SetBackgroundColour( wx.Colour(255, 204, 153) if self.winAndOut.GetValue() else wx.WHITE )
		if event:
			event.Skip()
     
	def refresh( self ):
		race = Model.race
		self.timeTrial.SetValue( getattr(race, 'isTimeTrial', False) )
		self.winAndOut.SetValue( race.winAndOut )
		self.minPossibleLapTime.SetSeconds( race.minPossibleLapTime )
		self.allCategoriesFinishAfterFastestRidersLastLap.SetValue( getattr(race, 'allCategoriesFinishAfterFastestRidersLastLap', False) )
		self.autocorrectLapsDefault.SetValue( getattr(race, 'autocorrectLapsDefault', True) )
		self.highPrecisionTimes.SetValue( getattr(race, 'highPrecisionTimes', False) )
		self.roadRaceFinishTimes.SetValue( race.roadRaceFinishTimes )
		self.estimateLapsDownFinishTime.SetValue( race.estimateLapsDownFinishTime )
		self.setNoDataDNS.SetValue( getattr(race, 'setNoDataDNS', False) )
		if race.rule80MinLapCount == 1:
			self.rule80MinLapCount1.SetValue( True )
		else:
			self.rule80MinLapCount2.SetValue( True )
		self.distanceUnit.SetSelection( getattr(race, 'distanceUnit', 0) )
		self.showDetails.SetValue( not race.hideDetails )
		self.showCourseAnimationInHtml.SetValue( race.showCourseAnimationInHtml )
		self.licenseLinkTemplate.SetValue( race.licenseLinkTemplate )
		self.onChangeWinAndOut()
		self.onChangeTimeTrial()
		
	@property
	def distanceUnitValue( self ):
		return self.distanceUnit.GetSelection()
	
	def commit( self ):
		race = Model.race
		race.isTimeTrial = self.timeTrial.IsChecked()
		race.allCategoriesFinishAfterFastestRidersLastLap = self.allCategoriesFinishAfterFastestRidersLastLap.IsChecked()
		race.autocorrectLapsDefault = self.autocorrectLapsDefault.IsChecked()
		race.highPrecisionTimes = self.highPrecisionTimes.IsChecked()
		race.roadRaceFinishTimes = self.roadRaceFinishTimes.IsChecked()
		race.estimateLapsDownFinishTime = self.estimateLapsDownFinishTime.IsChecked()
		race.setNoDataDNS = self.setNoDataDNS.IsChecked()
		race.rule80MinLapCount = (1 if self.rule80MinLapCount1.GetValue() else 2)
		race.distanceUnit = self.distanceUnit.GetSelection()
		race.hideDetails = not self.showDetails.IsChecked()
		race.showCourseAnimationInHtml = self.showCourseAnimationInHtml.IsChecked()
		race.winAndOut = self.winAndOut.IsChecked()
		race.minPossibleLapTime = self.minPossibleLapTime.GetSeconds()
		race.licenseLinkTemplate = self.licenseLinkTemplate.GetValue().strip()
	
#------------------------------------------------------------------------------------------------

class RfidProperties( wx.Panel ):
	iResetStartClockOnFirstTag = 1
	iSkipFirstTagRead = 2
	choices = [	_('Manual Start: Collect every RFID read.') + '\n' + _('Does NOT restart race clock on first read.'),
				_('Automatic Start: Reset start clock on first RFID read.') + '\n' + _('All riders get the start time of the first read.'),
				_('Manual Start: Skip first RFID read for all riders.') + '\n' + _('Required when start run-up passes the finish on the first lap.')]

	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id )
		self.jchip = wx.CheckBox( self, style=wx.ALIGN_LEFT, label = _('Use RFID Reader During Race') )

		self.chipTimingOptions = wx.RadioBox(
			self,
			label=_("Chip Timing Options"),
			majorDimension=1,
			choices=self.choices,
			style=wx.RA_SPECIFY_COLS
		)
		
		self.chipTimingOptions.SetSelection( self.iResetStartClockOnFirstTag )

		self.ignoreTTStart = wx.CheckBox(
			self,
			label = '{}\n{}'.format( _('Ignore RFID reads for unstarted time trial riders.'), ('Riders must be started manually, or by using a spreadsheet.'))
		)
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( wx.StaticText( self, label='{}:'.format(_('Reader Type')) ), flag=wx.ALIGN_CENTER_VERTICAL )
		self.chipReaderChoices = ChipReader.ChipReader.Choices
		self.chipReaderType = wx.StaticText( self )
		hs.Add( self.chipReaderType, flag=wx.LEFT, border=4)
		
		self.setupButton = wx.Button( self, label=_('Setup/Test Rfid Reader...') )
		self.setupButton.Bind( wx.EVT_BUTTON, self.onSetup )
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		ms.Add( self.jchip, flag=wx.ALL, border=16 )
		ms.Add( self.chipTimingOptions, flag=wx.ALL, border=4 )
		ms.Add( self.ignoreTTStart, flag=wx.ALL, border=16 )
		ms.Add( hs, flag=wx.ALL, border=4 )
		ms.AddSpacer( 16 )
		ms.Add( self.setupButton, flag=wx.ALL, border=4 )

	def onSetup( self, event ):
		self.commit()
		if Model.race.isRunning():
			Utils.MessageOK( self, _('Cannot perform RFID setup while race is running.'), _('Cannot Perform RFID Setup'), iconMask=wx.ICON_ERROR )
			return
		with JChipSetup.JChipSetupDialog(self) as dlg:
			dlg.ShowModal()
		self.refresh()
		
	def refresh( self ):
		race = Model.race
		if not race:
			return
		self.jchip.SetValue( getattr(race, 'enableJChipIntegration', False) )
		self.ignoreTTStart.SetValue( getattr(race, 'timeTrialNoRFIDStart', False) )
		resetStartClockOnFirstTag = getattr(race, 'resetStartClockOnFirstTag', True)
		skipFirstTagRead = getattr(race, 'skipFirstTagRead', False)
		if resetStartClockOnFirstTag:
			self.chipTimingOptions.SetSelection( self.iResetStartClockOnFirstTag )
		elif skipFirstTagRead:
			self.chipTimingOptions.SetSelection( self.iSkipFirstTagRead )
		else:
			self.chipTimingOptions.SetSelection( 0 )
		self.chipReaderType.SetLabel( self.chipReaderChoices[max(getattr(race, 'chipReaderType', 0), 0)] )
		self.GetSizer().Layout()
		
	def commit( self ):
		race = Model.race
		if not race:
			return
		race.enableJChipIntegration = self.jchip.IsChecked()
		race.timeTrialNoRFIDStart = self.ignoreTTStart.IsChecked()
		iSelection = self.chipTimingOptions.GetSelection()
		race.resetStartClockOnFirstTag	= bool(iSelection == self.iResetStartClockOnFirstTag)
		race.skipFirstTagRead			= bool(iSelection == self.iSkipFirstTagRead)
	
#------------------------------------------------------------------------------------------------

class WebProperties( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id )

		fgs = wx.FlexGridSizer( rows=0, cols=2, vgap=7, hgap=6 )
		fgs.AddGrowableCol( 1 )
				
		fgs.Add( wx.StaticText(self, label=_("Contact Email")), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.email = wx.TextCtrl( self )
		fgs.Add( self.email, 1, flag=wx.EXPAND )
		
		fgs.Add( wx.StaticText( self, label=_('Google Analytics Tracking ID (of the form UA-XXXX-Y)') ),
				flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.gaTrackingID = wx.TextCtrl( self )
		fgs.Add( self.gaTrackingID, 1, flag=wx.EXPAND )
				
		fgs.Add( wx.StaticText( self, label=_('Google Maps API Key') ),
				flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.googleMapsApiKey = wx.TextCtrl( self )
		fgs.Add( self.googleMapsApiKey, 1, flag=wx.EXPAND )
				
		self.headerImageBitmap = wx.StaticBitmap( self )
		
		self.graphicFName = None
		
		self.graphicButton = wx.Button( self, label=_("Set Graphic") )
		self.graphicButton.Bind( wx.EVT_BUTTON, self.onSetGraphic )
		
		self.graphicSize = wx.StaticText( self )
		
		hsHeaderGraphic = wx.BoxSizer( wx.HORIZONTAL )
		hsHeaderGraphic.Add( wx.StaticText(self, label=_("Page Header Graphic")), flag=wx.ALIGN_CENTER_VERTICAL )
		hsHeaderGraphic.Add( self.graphicButton, flag=wx.LEFT, border=4 )
		hsHeaderGraphic.Add( self.graphicSize, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=4 )
		
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.VERTICAL )
		
		ms.Add( fgs, flag=wx.EXPAND|wx.ALL, border=4 )
		ms.AddSpacer( 16 )
		ms.Add( hsHeaderGraphic, flag=wx.ALL, border=4 )
		ms.Add( self.headerImageBitmap, flag=wx.ALL, border=4 )
		ms.Add( wx.StaticText(self, label=_("The Page Header Graphic will appears on HTML, Printouts and PDF files.")), flag=wx.ALL, border=4 )
		
		hsButtons = wx.BoxSizer( wx.HORIZONTAL )
		self.webIndexPageBtn = wx.Button( self, label=_('Show Index Page') )
		self.webIndexPageBtn.Bind( wx.EVT_BUTTON, self.doWebIndexPage )
		self.webQRCodePageBtn = wx.Button( self, label=_('Show QR Code Share') )
		self.webQRCodePageBtn.Bind( wx.EVT_BUTTON, self.doWebQRCodePage )
		
		hsButtons.Add( self.webIndexPageBtn )
		hsButtons.Add( self.webQRCodePageBtn, flag=wx.LEFT, border=16 )
		
		ms.Add( hsButtons, flag=wx.ALL, border=8 )
		
		self.SetSizer( ms )

	def doWebIndexPage( self, event ):
		self.commit()
		try:
			webbrowser.open( WebServer.GetCrossMgrHomePage(), new=2, autoraise=True )
		except Exception as e:
			pass
	
	def doWebQRCodePage( self, event ):
		self.commit()
		try:
			webbrowser.open( WebServer.GetCrossMgrHomePage() + '/qrcode.html' , new=2, autoraise=True )
		except Exception as e:
			pass

	def getDefaultGraphicFNameType( self ):
		return os.path.join(Utils.getImageFolder(), 'CrossMgrHeader.png'), wx.BITMAP_TYPE_PNG
		
	def onSetGraphic( self, event ):
		with SetGraphicDialog( self, graphic = self.graphicFName ) as dlg:
			if dlg.ShowModal() != wx.ID_OK:
				return				
			self.graphicFName = dlg.GetValue().strip() or self.getDefaultGraphicFNameType()[0]
		
		try:
			self.headerImage = ImageIO.toBufFromFile( self.graphicFName )
		except Exception as e:
			self.graphicFName = self.getDefaultGraphicFNameType()[0]
			self.headerImage = ImageIO.toBufFromFile( self.graphicFName )
			Utils.MessageOK( self, '{}:\n\n{}'.format(_("Error"), '\n\n'.join(str(e).split(':'))), _("Set Graphic Error"), iconMask=wx.ICON_ERROR )
			
		self.headerImageBitmap.SetBitmap( ImageIO.toBitmapFromBuf(self.headerImage) )
		self.setGraphicStats()
		self.GetSizer().Layout()
		self.Refresh()
	
	def setGraphicStats( self ):
		bitmap = self.headerImageBitmap.GetBitmap()
		self.graphicSize.SetLabel( '({}px \u2715 {}px)'.format(bitmap.GetWidth(), bitmap.GetHeight()) )
	
	def refresh( self ):
		race = Model.race
		mainWin = Utils.getMainWin()
		
		self.email.SetValue( race.email or '' )
		self.gaTrackingID.SetValue( getattr(race, 'gaTrackingID', '') )
		self.googleMapsApiKey.SetValue( getattr(race, 'googleMapsApiKey', '') )
		
		if race.headerImage:
			self.headerImage = race.headerImage
		elif mainWin:
			self.headerImage = ImageIO.toBufFromFile( mainWin.getGraphicFName() )
		else:
			self.headerImage = ImageIO.toBufFromFile( *self.getDefaultGraphicFNameType() )

		self.graphicFName = mainWin.getGraphicFName() if mainWin else self.getDefaultGraphicFNameType()[0]
		self.headerImageBitmap.SetBitmap( ImageIO.toBitmapFromBuf(self.headerImage) )
		self.setGraphicStats()
		self.GetSizer().Layout()
		
	def commit( self ):
		race = Model.race
		race.email = self.email.GetValue().strip()
		race.gaTrackingID = re.sub( '[^A-Z0-9]+', '-', self.gaTrackingID.GetValue().strip().upper() )
		race.googleMapsApiKey = self.googleMapsApiKey.GetValue().strip()
		race.headerImage = self.headerImage

#------------------------------------------------------------------------------------------------

class GPXProperties( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id )
		
		fgs = wx.FlexGridSizer( rows=0, cols=4, vgap=7, hgap=6 )
		fgs.AddGrowableCol( 1 )
		fgs.AddGrowableCol( 3 )
		
		fgs.Add( wx.StaticText(self, label=_("Distance")), flag=wx.ALIGN_RIGHT )
		self.distance = wx.StaticText( self,  )
		boldFont = Utils.BoldFromFont(self.distance.GetFont())
		self.distance.SetFont( boldFont )
		fgs.Add( self.distance )
		
		fgs.Add( wx.StaticText(self, label=_("Elevation Gain")), flag=wx.ALIGN_RIGHT )
		self.elevationGain = wx.StaticText( self )
		self.elevationGain.SetFont( boldFont )
		fgs.Add( self.elevationGain )

		fgs.Add( wx.StaticText(self, label=_("Course Type")), flag=wx.ALIGN_RIGHT )
		self.courseType = wx.StaticText( self )
		self.courseType.SetFont( boldFont )
		fgs.Add( self.courseType )

		fgs.Add( wx.StaticText(self, label=_("Number of Coords")), flag=wx.ALIGN_RIGHT )
		self.gpsPoints = wx.StaticText( self )
		self.gpsPoints.SetFont( boldFont )
		fgs.Add( self.gpsPoints )
		
		self.geoAnimation = GeoAnimation( self )
		
		self.setGPXCourse = wx.Button( self, label=_('Import GPX Course') )
		self.setGPXCourse.Bind( wx.EVT_BUTTON, self.onSetGPXCourse )
		
		self.reverse = wx.BitmapButton( self, bitmap=Utils.GetPngBitmap('reverse-icon-48px.png') )
		self.reverse.Bind( wx.EVT_BUTTON, self.onReverse )
		self.reverse.SetToolTip(wx.ToolTip(_('Reverse Course Direction')))
		
		self.showGoogleMap = wx.BitmapButton( self, bitmap=Utils.GetPngBitmap('Google-Maps-icon-48.png') )
		self.showGoogleMap.Bind( wx.EVT_BUTTON, self.onShowOnGoogleMap )
		self.showGoogleMap.SetToolTip(wx.ToolTip(_('Show on Google Map')))
		
		self.exportAsGPX = wx.BitmapButton( self, bitmap=Utils.GetPngBitmap('Files-Gpx-icon-48.png') )
		self.exportAsGPX.Bind( wx.EVT_BUTTON, self.onExportAsGPX )
		self.exportAsGPX.SetToolTip(wx.ToolTip(_('Export in GPX Format')))
		
		self.exportAsKML = wx.BitmapButton( self, bitmap=Utils.GetPngBitmap('Files-Kml-icon-48.png') )
		self.exportAsKML.Bind( wx.EVT_BUTTON, self.onExportAsKML )
		self.exportAsKML.SetToolTip(wx.ToolTip(_('Export in KML Format (requires Google Earth)')))
		
		hsButtons = wx.BoxSizer( wx.HORIZONTAL )
		hsButtons.Add( self.setGPXCourse )
		hsButtons.Add( self.showGoogleMap, flag=wx.LEFT, border=64 )
		hsButtons.Add( self.exportAsGPX, flag=wx.LEFT, border=32 )
		hsButtons.Add( self.exportAsKML, flag=wx.LEFT, border=4 )
		hsButtons.Add( self.reverse, flag=wx.LEFT, border=32 )
		
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.VERTICAL )
		
		ms.Add( fgs, flag=wx.ALL, border=4 )
		ms.Add( hsButtons, flag=wx.ALL, border=4 )
		ms.Add( self.geoAnimation, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		self.SetSizer( ms )

	def onSetGPXCourse( self, event ):
		race = Model.race
		args = [self]
		if race:
			args.extend( [getattr(race, 'geoTrack', None), getattr(race, 'geoTrackFName', '')] )
		gt = GetGeoTrack( *args )
		geoTrack, geoTrackFName, distanceKm = gt.show()
		if race:
			if not geoTrackFName:
				race.geoTrack, race.geoTrackFName = None, None
			else:
				race.geoTrack, race.geoTrackFName = geoTrack, geoTrackFName
				if race.geoTrack and distanceKm:
					race.setDistanceForCategories( distanceKm )

			race.showOval = (race.geoTrack is None)
			race.setChanged()
		self.refresh()
	
	def onReverse( self, event ):
		try:
			Model.race.geoTrack.reverse()
		except Exception:
			pass
		self.refresh()
	
	def onShowOnGoogleMap( self, event ):
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.menuExportCoursePreviewAsHtml()
	
	def onExportAsGPX( self, event ):
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.menuExportGpx()
		
	def onExportAsKML( self, event ):
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.menuExportCourseAsKml()
		
	def refresh( self ):
		race = Model.race
		if not race:
			return
		geoTrack = getattr(race, 'geoTrack', None)
		self.geoAnimation.SetGeoTrack( geoTrack )
		self.geoAnimation.Refresh()
		
		if geoTrack:
			self.distance.SetLabel( '{:.3f} km, {:.3f} miles'.format(geoTrack.lengthKm, geoTrack.lengthMiles) )
			self.elevationGain.SetLabel( '{:.0f} m, {:.0f} ft'.format(geoTrack.totalElevationGainM, geoTrack.totalElevationGainFt) )
			self.courseType.SetLabel( 'Point to Point' if geoTrack.isPointToPoint else 'Loop' )
			self.gpsPoints.SetLabel( '{}'.format( len(geoTrack.gpsPoints) ) )
		else:
			self.distance.SetLabel( '' )
			self.elevationGain.SetLabel( '' )
			self.courseType.SetLabel( '' )
			self.gpsPoints.SetLabel( '' )
		
		self.GetSizer().Layout()
		
	def commit( self ):
		pass
	
#------------------------------------------------------------------------------------------------

class CameraProperties( wx.Panel ):
	advanceMin, advanceMax = -2000, 2000
	
	def __init__( self, parent, id=wx.ID_ANY ):
		super().__init__( parent, id )
		
		choices = [
			_("Do Not Use Camera for Photo Finish"),
			_("Photos on Every Lap"),
			_("Photos at Race Finish Only"),
		]
		self.radioBox = wx.RadioBox( self, label=_("USB Camera Options"), choices=choices, majorDimension=1, style=wx.RA_SPECIFY_COLS )
		self.radioBox.SetBackgroundColour( wx.WHITE )
		
		ms = wx.BoxSizer( wx.VERTICAL )
		
		ms.Add( self.radioBox, flag=wx.ALL, border=16 )
		
		self.explanation = wx.StaticText( self, label=_('Requires CrossMgrVideo.  See help for details.') )
		ms.Add( self.explanation, flag=wx.ALL, border=16 )
		
		self.SetSizer( ms )

	def refresh( self ):
		race = Model.race
		if not race or not race.enableUSBCamera:
			self.radioBox.SetSelection( 0 )
		else:
			if not race.photosAtRaceEndOnly:
				self.radioBox.SetSelection( 1 )
			else:
				self.radioBox.SetSelection( 2 )
		self.GetSizer().Layout()
		
	def commit( self ):
		race = Model.race
		if not race:
			return
		
		race.advancePhotoMilliseconds = 0
		
		race.enableUSBCamera = False
		race.photosAtRaceEndOnly = False
		v = self.radioBox.GetSelection()
		if v == 1:
			race.enableUSBCamera = True
		elif v == 2:
			race.enableUSBCamera = True
			race.photosAtRaceEndOnly = True

#------------------------------------------------------------------------------------------------
class AnimationProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id )
		
		self.note = wx.StaticText( self, label='\n'.join ([
				_('This only applies to the Track animation.'),
				_('GPX animation follows the lat/lng coordinates.')
			])
		)
		self.finishTop = wx.CheckBox( self, label=_('Animation Finish on Top') )
		self.reverseDirection = wx.CheckBox( self, label=_('Animation Reverse Direction') )
		
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		ms.Add( self.note, flag=wx.TOP|wx.LEFT, border=16 )
		ms.Add( self.finishTop, flag=wx.TOP|wx.LEFT, border=16 )
		ms.Add( self.reverseDirection, flag=wx.TOP|wx.LEFT, border=16 )
		
	def refresh( self ):
		race = Model.race
		self.reverseDirection.SetValue( getattr(race, 'reverseDirection', False) )
		self.finishTop.SetValue( getattr(race, 'finishTop', False) )
		
	def commit( self ):
		race = Model.race
		race.reverseDirection = self.reverseDirection.GetValue()
		race.finishTop = self.finishTop.GetValue()

#------------------------------------------------------------------------------------------------
class TeamResultsProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id )
		
		self.teamRankOptionLabel = wx.StaticText( self, label=_('Team Rank Criteria') )
		choices = [
			_('by Nth Rider Time'),
			_('by Sum Time'),
			_('by Sum Points'),
			_('by Sum Percent Time'),
		]
		self.teamRankOption = wx.Choice( self, choices=choices )
		
		self.nthTeamRiderLabel = wx.StaticText( self, label=_('Nth Rider') )
		self.nthTeamRider = wx.Choice( self, choices=['{}'.format(i) for i in range(1,16)] )
		self.nthTeamRiderNote = wx.StaticText( self, label=_('for Nth Rider Time') )
		
		self.topTeamResultsLabel = wx.StaticText( self, label=_('# Top Results') )
		self.topTeamResults = wx.Choice( self, choices=['{}'.format(i) for i in range(1,16)] )
		self.topTeamResultsNote = wx.StaticText( self, label=_('for Sum Time, Points and Percent') )
		
		self.finishPointsStructureLabel = wx.StaticText( self, label=_('Finish Points') )
		self.finishPointsStructure = wx.TextCtrl( self, value="", style=wx.TE_PROCESS_ENTER, size=(240,-1) )
		self.finishPointsStructureNote = wx.StaticText( self, label=_('for Sum Points') )
		
		self.showNumTeamParticipants = wx.CheckBox( self, label=_('Show # of Team Participants'))
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.teamRankOptionLabel, flag=wx.ALIGN_CENTER_VERTICAL )
		hs.Add( self.teamRankOption, flag=wx.LEFT, border=4 )
		ms.Add( hs, flag=wx.ALL, border=4 )
		
		fgs = wx.FlexGridSizer( 3, 4, 4 )
		fgs.Add( self.nthTeamRiderLabel, flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		fgs.Add( self.nthTeamRider )
		fgs.Add( self.nthTeamRiderNote, flag=wx.ALIGN_CENTER_VERTICAL )
		
		fgs.Add( self.topTeamResultsLabel, flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		fgs.Add( self.topTeamResults )
		fgs.Add( self.topTeamResultsNote, flag=wx.ALIGN_CENTER_VERTICAL )

		fgs.Add( self.finishPointsStructureLabel, flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		fgs.Add( self.finishPointsStructure )
		fgs.Add( self.finishPointsStructureNote, flag=wx.ALIGN_CENTER_VERTICAL )

		fgs.Add( wx.StaticText(self, label='') )
		fgs.Add( self.showNumTeamParticipants, flag=wx.ALIGN_CENTER_VERTICAL )

		ms.Add( fgs, flag=wx.ALL, border=4 )
		
	def refresh( self ):
		race = Model.race
		self.teamRankOption.SetSelection( race.teamRankOption )
		self.nthTeamRider.SetSelection( race.nthTeamRider - 1 )
		self.topTeamResults.SetSelection( race.topTeamResults - 1 )
		self.finishPointsStructure.SetValue( race.finishPointsStructure )
		
	def commit( self ):
		race = Model.race
		race.teamRankOption = self.teamRankOption.GetSelection()
		race.nthTeamRider = self.nthTeamRider.GetSelection() + 1
		race.topTeamResults = self.topTeamResults.GetSelection() + 1
		race.finishPointsStructure = ','.join( re.sub( '[^0-9]', ' ', self.finishPointsStructure.GetValue() ).split() )
		race.showNumTeamParticipants = self.showNumTeamParticipants.GetValue()

#------------------------------------------------------------------------------------------------
class BatchPublishProperties( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, testCallback=None, ftpCallback=None ):
		super().__init__( parent, id )

		self.testCallback = testCallback
		self.ftpCallback = ftpCallback
		
		if ftpCallback:
			ftpBtn = wx.ToggleButton( self, label=_('Configure Ftp') )
			ftpBtn.Bind( wx.EVT_TOGGLEBUTTON, ftpCallback )
		else:
			ftpBtn = None
			
		explain = [
			wx.StaticText(self,label=_('Choose File Formats to Publish.  Select Ftp option to upload files to Ftp server.')),
		]
		font = explain[0].GetFont()
		fontUnderline = wx.FFont( font.GetPointSize(), font.GetFamily(), flags=wx.FONTFLAG_BOLD )
		
		fgs = wx.FlexGridSizer( cols=4, rows=0, hgap=0, vgap=1 )
		self.widget = []
		
		headers = [_('Format'), _('Ftp'), _('Note'), '']
		for h in headers:
			st = wx.StaticText(self, label=h)
			st.SetFont( fontUnderline )
			fgs.Add( st, flag=wx.ALL, border=4 )
		
		for i, attr in enumerate(batchPublishAttr):
			for k in range(len(headers)): fgs.Add( wx.StaticLine(self, size=(1,1)), flag=wx.EXPAND )
		
			attrCB = wx.CheckBox(self, label=attr.uiname)
			attrCB.Bind( wx.EVT_CHECKBOX, lambda event, iAttr=i: self.onSelect(iAttr) )
			fgs.Add( attrCB, flag=wx.ALIGN_CENTRE_VERTICAL )
			if attr.ftp:
				ftpCB = wx.CheckBox(self, label='          ')
				fgs.Add( ftpCB, flag=wx.ALIGN_CENTER|wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=4 )
			else:
				ftpCB = None
				fgs.AddSpacer( 8 )
			if attr.note:
				fgs.Add( wx.StaticText(self, label=attr.note), flag=wx.ALIGN_CENTRE_VERTICAL )
			else:
				fgs.AddSpacer( 0 )
				
			testBtn = wx.Button( self, label=_('Publish') )
			testBtn.Bind( wx.EVT_BUTTON, lambda event, iAttr=i: self.onTest(iAttr) )
			fgs.Add( testBtn, flag=wx.LEFT|wx.ALIGN_CENTRE_VERTICAL, border=8 )
			self.widget.append( (attrCB, ftpCB, testBtn) )
		
		self.bikeRegChoice = wx.RadioBox(
			self,
			label=_('BikeReg'),
			choices=[_('None'), 'CrossResults', 'RoadResults'],
			majorDimension=0
		)
		
		pps = wx.BoxSizer( wx.HORIZONTAL )
		pps.Add( wx.StaticText(self, label=_('Post Publish Command')), flag=wx.ALIGN_CENTRE_VERTICAL )
		self.postPublishCmd = wx.TextCtrl( self )
		pps.Add( self.postPublishCmd, 1, flag=wx.LEFT|wx.EXPAND, border=4 )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		if ftpBtn:
			for e in explain[:-1]:
				vs.Add( e, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=4 )
			h = wx.BoxSizer( wx.HORIZONTAL )
			h.Add( explain[-1], flag=wx.ALIGN_CENTRE_VERTICAL )
			h.Add( ftpBtn, flag=wx.LEFT, border=8 )
			vs.Add( h, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=8 )
		else:
			for e in explain:
				vs.Add( e, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=8 )
		vs.Add( fgs, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=8 )
		vs.Add( self.bikeRegChoice, flag=wx.ALL, border=4 )
		vs.Add( pps, flag=wx.ALL|wx.EXPAND, border=4 )
		vs.Add( wx.StaticText(self,label='\n'.join([
				_('Postpublish Command is run on CrossMgr generated files.  Use %* to insert the file names into the command line.'),
				_('You can also use Notes variables, for example: {=RaceDate}, {=Organizer} and {=City}.'),
				_('Scripts can be shell cmds or scripts (.bat, .py, .rb, .perl, ...).'),
			])),
			flag=wx.ALL|wx.EXPAND, border=4 )
		
		self.SetSizer( vs )
	
	def onTest( self, iAttr ):
		if self.testCallback:
			self.testCallback()
			
		attrCB, ftpCB, testBtn = self.widget[iAttr]
		doFtp = ftpCB and ftpCB.GetValue()
		doBatchPublish( iAttr, silent=False )
		
		race = Model.race
		mainWin = Utils.getMainWin()
		attr = batchPublishAttr[iAttr]
		
		if attr.filecode:
			fname = mainWin.getFormatFilename(attr.filecode)
			if doFtp and race.urlFull and race.urlFull != 'http://':
				webbrowser.open( os.path.basename(race.urlFull) + '/' + os.path.basename(fname), new = 0, autoraise = True )
			else:
				Utils.LaunchApplication( fname )
		else:
			pngFiles = os.path.join( os.path.dirname(Utils.getFileName()), 'FaceBookPNG', '*.png' )
			for fname in glob.glob(pngFiles):
				Utils.LaunchApplication( fname )
				return
	
	def onSelect( self, iAttr ):
		attrCB, ftpCB, testBtn = self.widget[iAttr]
		v = attrCB.GetValue()
		if ftpCB:
			ftpCB.Enable( v )
			if not v:
				ftpCB.SetValue( False )
		testBtn.Enable( v )
		
	def refresh( self ):
		race = Model.race
		for i, attr in enumerate(batchPublishAttr):
			raceAttr = batchPublishRaceAttr[i]
			attrCB, ftpCB, testBtn = self.widget[i]
			v = getattr( race, raceAttr, 0 )
			if v & 1:
				attrCB.SetValue( True )
				if ftpCB:
					ftpCB.Enable( True )
					ftpCB.SetValue( v & 2 != 0 )
				testBtn.Enable( True )
			else:
				attrCB.SetValue( False )
				if ftpCB:
					ftpCB.SetValue( False )
					ftpCB.Enable( False )
				testBtn.Enable( False )
		self.bikeRegChoice.SetSelection( getattr(race, 'publishFormatBikeReg', 0) )
		self.postPublishCmd.SetValue( race.postPublishCmd )
	
	def commit( self ):
		race = Model.race
		for i, attr in enumerate(batchPublishAttr):
			raceAttr = batchPublishRaceAttr[i]
			attrCB, ftpCB, testBtn = self.widget[i]
			setattr( race, raceAttr, 0 if not attrCB.GetValue() else (1 + (2 if ftpCB and ftpCB.GetValue() else 0)) )
		race.publishFormatBikeReg = self.bikeRegChoice.GetSelection()
		race.postPublishCmd = self.postPublishCmd.GetValue().strip()

def doBatchPublish( iAttr=None, silent=True, cmdline=False ):
	race = Model.race
	mainWin = Utils.getMainWin()
	ftpFiles = []
	allFiles = []
	success = True
	
	for i, attr in enumerate(batchPublishAttr):
		if iAttr is not None and i != iAttr:
			continue
		if cmdline and attr.name == 'IndexHtml':
			continue
		v = getattr( race, batchPublishRaceAttr[i], 0 )
			
		if v & 1:
			getattr( mainWin, attr.func )( silent=silent )
			if attr.filecode:
				files = mainWin.getFormatFilename(attr.filecode)
				for f in (files if isinstance(files, list) else [files]):
					allFiles.append( f )
					if v & 2:
						ftpFiles.append( f )
	
	if iAttr is None:
		publishFormatBikeReg = getattr(race, 'publishFormatBikeReg', 0)
		if publishFormatBikeReg == 1:
			with wx.BusyCursor():
				mainWin.menuExportCrossResults( silent=True )
		elif publishFormatBikeReg == 2:
			with wx.BusyCursor():
				mainWin.menuExportRoadResults( silent=True )
		
	e = None
	if ftpFiles:
		if not FtpIsConfigured() and (silent or Utils.MessageOKCancel(
					mainWin,
					'{}\n\n{}'.format( _('Ftp is Not Configured'), _('Configure it now?')), 
					('Ftp is Not Configured')
				)):
			with FtpPublishDialog( mainWin ) as dlg:
				dlg.ShowModal()
		
		if not silent:
			class FtpThread( threading.Thread ):
				def __init__(self, ftpFiles, progressDialog):
					super().__init__()
					self.ftpFiles = ftpFiles
					self.progressDialog = progressDialog
					self.e = None
			 
				def run(self):
					wx.CallAfter( self.progressDialog.ShowModal )
					self.e = FtpUploadFile( self.ftpFiles, self.progressDialog.update )
					wx.CallAfter( self.progressDialog.EndModal, 0 )
				
			bytesTotal = sum( os.path.getsize(f) for f in ftpFiles )
			uploadProgress = FtpUploadProgress( mainWin, fileTotal=len(ftpFiles), bytesTotal=bytesTotal, )
			uploadProgress.Centre()
			ftpThread = FtpThread( ftpFiles, uploadProgress )
			ftpThread.start()
			e = ftpThread.e
		else:
			e = FtpUploadFile( ftpFiles )
		
		if e:
			message = '{}\n\n{}'.format( _('Ftp Upload Error'), e)
			if not silent:
				Utils.MessageOK( mainWin, message, _('Ftp Upload Error'), wx.ICON_ERROR )
			Utils.writeLog( message )
			success = False

	postPublishCmd = getattr(race, 'postPublishCmd', None)
	if postPublishCmd and allFiles:
		postPublishCmd = TemplateSubstitute( postPublishCmd, race.getTemplateValues() )
		if platform.system() == 'Windows':
			files = ' '.join('""{}""'.format(f) for f in allFiles)
		else:
			files = ' '.join('"{}"'.format(f) for f in allFiles)
		if '%*' in postPublishCmd:
			cmd = postPublishCmd.replace('%*', files)
		else:
			cmd = ' '.join( [postPublishCmd, files] )

		Utils.writeLog( '{}: {}\n'.format( _('Post Publish Cmd'), cmd ) )
		
		try:
			subprocess.check_call( cmd, shell=True )
		except subprocess.CalledProcessError as e:
			message = '{}\n\n    {}\n{}: {}'.format(_('Post Publish Cmd Error'), e, _('return code'), e.returncode)
			if not silent:
				Utils.MessageOK( mainWin, message, _('Post Publish Cmd Error')  )
			Utils.writeLog( message )
			success = False

		except Exception as e:
			message = '{}\n\n    {}'.format(_('Post Publish Cmd Error'), e)
			if not silent:
				Utils.MessageOK( mainWin, message, _('Post Publish Cmd Error')  )
			Utils.writeLog( message )
			success = False
	
	if not silent and iAttr is None:
		Utils.MessageOK( mainWin, _('Publish Complete'), _('Publish Complete') )
		
	return success

class BatchPublishPropertiesDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY ):
		super().__init__( parent, id, _("Batch Publish Results"),
					style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
					
		self.batchPublishProperties = BatchPublishProperties(self, testCallback=self.commit, ftpCallback=self.onToggleFtp)
		self.batchPublishProperties.refresh()
		
		self.ftp = FtpProperties( self, uploadNowButton=False )
		self.ftp.refresh()
		self.ftp.Show( False )
		
		self.okBtn = wx.Button( self, label=_('Publish All') )
		self.okBtn.Bind( wx.EVT_BUTTON, self.onOK )
		self.saveBtn = wx.Button( self, label=_('Save Options and Close') )
		self.saveBtn.Bind( wx.EVT_BUTTON, self.onSave )
		self.cancelBtn = wx.Button( self, id=wx.ID_CANCEL )
		self.cancelBtn.Bind( wx.EVT_BUTTON, self.onCancel )

		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( self.okBtn )
		hb.Add( self.saveBtn, border = 60, flag=wx.LEFT )
		hb.Add( self.cancelBtn, border = 24, flag=wx.LEFT )
		self.okBtn.SetDefault()
		
		vs = wx.BoxSizer( wx.VERTICAL )
		hsContent = wx.BoxSizer( wx.HORIZONTAL )
		hsContent.Add( self.batchPublishProperties )
		hsContent.Add( self.ftp, flag=wx.ALL, border=8 )
		vs.Add( hsContent )
		vs.Add( hb, flag=wx.ALIGN_CENTRE|wx.ALL, border=8 )
		
		self.SetSizerAndFit( vs )
	
	def commit( self ):
		self.batchPublishProperties.commit()
		self.ftp.commit()
	
	def onToggleFtp( self, event ):
		self.ftp.Show( not self.ftp.IsShown() )
		self.ftp.Layout()
		self.GetSizer().Layout()
		self.Fit()
	
	def onOK( self, event ):
		self.commit()
		doBatchPublish()
		Utils.refresh()
		self.EndModal( wx.ID_OK )
		
	def onSave( self, event ):
		self.commit()
		Utils.refresh()
		self.EndModal( wx.ID_CANCEL )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

#------------------------------------------------------------------------------------------------
class NotesProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id )
		
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		self.notesLabel = wx.StaticText( self, label='\n'.join( [
			_("Notes to appear on Html output:"),
			_("(notes containing Html must start with <html> and end with </html>)")] ) )
		self.notes = wx.TextCtrl( self, style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB, size=(-1,60) )
		self.insertButton = wx.Button( self, label=_('Insert Variable...') )
		self.insertButton.Bind( wx.EVT_BUTTON, self.onInsertClick )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.notesLabel )
		hs.AddStretchSpacer()
		hs.Add( self.insertButton )
		ms.Add( hs, flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, border=12 )
		ms.Add( self.notes, 1, flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, border=12 )
		
	def onInsertClick( self, event ):
		race = Model.race
		if not race:
			return
		
		if not hasattr(self, 'men'):
			self.menu = wx.Menu()
			self.idVariable = {}
			for v in sorted(list(race.getTemplateValues().keys()) + ['Bib ', 'BibList ', 'BibTable ']):
				v = '{=' + v + '}'
				item = self.menu.Append( wx.ID_ANY, v )
				self.Bind( wx.EVT_MENU, self.onInsertVariable, item )
				self.idVariable[item.GetId()] = v
		
		self.PopupMenu( self.menu )
		wx.CallAfter( self.notes.SetFocus )
		
	def onInsertVariable( self, event ):
		v = self.idVariable[event.GetId()]
		iCur = self.notes.GetInsertionPoint()
		self.notes.Replace( iCur, iCur, v )
		self.notes.SetInsertionPoint( iCur + len(v) )
	
	def refresh( self ):
		race = Model.race
		self.notes.SetValue( race.notes )
		
	def commit( self ):
		race = Model.race
		race.notes = self.notes.GetValue()

#------------------------------------------------------------------------------------------------
class FilesProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id )
		
		self.fileNameLabel = wx.StaticText( self, label=_('File Name') )
		self.fileName = wx.StaticText( self )

		self.excelButton = wx.Button(self, label=_('Link External Excel Sheet...'))
		self.excelButton.Bind( wx.EVT_BUTTON, self.excelButtonCallback )

		self.excelName = wx.StaticText( self )

		self.categoriesFileLabel = wx.StaticText( self, label=_('Categories Initially Loaded From') )
		self.categoriesFile = wx.StaticText( self )
		
		self.templateFileNameLabel = wx.StaticText( self, label=_('Template File') )
		self.templateFileName = wx.StaticText( self )
		
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		fgs = wx.FlexGridSizer( rows=0, cols=2, vgap=12, hgap=8 )
		fgs.AddGrowableCol( 1 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fieldAlign = wx.EXPAND
		
		labelFieldBatchPublish = [
			(self.fileNameLabel,		0, labelAlign),		(self.fileName,			1, fieldAlign),
			(self.excelButton,			0, labelAlign),		(self.excelName,		1, fieldAlign),
			(self.categoriesFileLabel,	0, labelAlign),		(self.categoriesFile,	1, fieldAlign),
			(self.templateFileNameLabel,0, labelAlign),		(self.templateFileName,	1, fieldAlign),
		]
		addToFGS( fgs, labelFieldBatchPublish )
		ms.Add( fgs, 1, flag=wx.EXPAND|wx.ALL, border=16 )
		
	def excelButtonCallback( self, event ):
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.menuLinkExcel()
	
	def refresh( self ):
		race = Model.race
		excelLink = getattr(race, 'excelLink', None)
		if excelLink:
			self.excelName.SetLabel( '{}|{}'.format(
				os.path.basename(excelLink.fileName) if excelLink.fileName else '',
				excelLink.sheetName if excelLink.sheetName else '') )
		else:
			self.excelName.SetLabel( '' )
		self.categoriesFile.SetLabel( os.path.basename(getattr(race, 'categoriesImportFile', '')) )
		self.templateFileName.SetLabel( os.path.basename(getattr(race, 'templateFileName', '')) )
		
	def commit( self ):
		pass
		
#------------------------------------------------------------------------------------------------

class Properties( wx.Panel ):
	dateFormat = '%Y-%m-%d'

	def __init__( self, parent, id=wx.ID_ANY, addEditButton=True ):
		super().__init__(parent, id)
		
		self.state = RaceInputState()
		
		self.SetBackgroundColour( wx.WHITE )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( mainSizer )
		
		bookStyle = (
			  flatnotebook.FNB_NO_NAV_BUTTONS
			| flatnotebook.FNB_NO_X_BUTTON
			| flatnotebook.FNB_DROPDOWN_TABS_LIST
			| flatnotebook.FNB_NODRAG
		)
		self.notebook = flatnotebook.FlatNotebook( self, agwStyle=bookStyle )
		self.notebook.SetTabAreaColour( wx.WHITE )
		self.notebook.SetBackgroundColour( wx.WHITE )
		self.notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanging )

		self.propClassName = [
			('generalInfoProperties',	GeneralInfoProperties,		_('General Info') ),
			('raceOptionsProperties',	RaceOptionsProperties,		_('Race Options') ),
			('rfidProperties',			RfidProperties,				_('RFID') ),
			('webProperties',			WebProperties,				_('Web') ),
			('ftpProperties',			FtpProperties,				_('FTP') ),
			('batchPublishProperties',	BatchPublishProperties,		_('Batch Publish') ),
			('gpxProperties',			GPXProperties,				_('GPX') ),
			('notesProperties',			NotesProperties,			_('Notes') ),
			('cameraProperties',		CameraProperties,			_('Camera') ),
			('lapCounterProperties',	LapCounterProperties,		_('Lap Counter') ),
			('animationProperties',		AnimationProperties,		_('Animation') ),
			('filesProperties',			FilesProperties,			_('Files/Excel') ),
			('teamResultsProperties',	TeamResultsProperties,		_('Team Results') ),
		]
		for prop, PropClass, name in self.propClassName:
			setattr( self, prop, PropClass(self.notebook) )
			self.notebook.AddPage( getattr(self, prop), name )
		
		self.updateFileName()
		
		mainSizer.Add( self.notebook, 1, flag=wx.ALL|wx.EXPAND, border=4 )
		
		if addEditButton:
			
			self.commitButton = wx.Button(self, label=_('Commit'))
			self.commitButton.Bind( wx.EVT_BUTTON, self.commitButtonCallback )
			
			self.saveTemplateButton = wx.Button(self, label=_('Save Template'))
			self.saveTemplateButton.Bind( wx.EVT_BUTTON, self.saveTemplateButtonCallback )
			
			self.loadTemplateButton = wx.Button(self, label=_('Load Template'))
			self.loadTemplateButton.Bind( wx.EVT_BUTTON, self.loadTemplateButtonCallback )
			
			hs = wx.BoxSizer( wx.HORIZONTAL )
			hs.Add( self.commitButton )
			hs.Add( self.saveTemplateButton, flag=wx.LEFT, border=48 )
			hs.Add( self.loadTemplateButton, flag=wx.LEFT, border=16 )

			mainSizer.AddSpacer( 12 )
			mainSizer.Add( hs, flag=wx.ALL, border=4 )
			mainSizer.Add(
				wx.StaticText(self, label=_('Save as "default" for a default Template that is applied automatically to all New races')),
				flag=wx.ALL, border=4
			)
			
		self.setEditable()
		mainSizer.Fit(self)
		self.Layout()
		
	def onJChipIntegration( self, event ):
		self.rfidProperties.autocorrectLapsDefault.SetValue( not self.rfidProperties.jchip.GetValue() )
	
	def setPage( self, pageName ):
		for i, d in enumerate(self.propClassName):
			if pageName in d:
				self.notebook.SetSelection( i )
				break
	
	def onPageChanging( self, event ):
		'''
		if Model.race:
			notebook = event.GetEventObject()
			notebook.GetPage( event.GetOldSelection() ).commit()
			notebook.GetPage( event.GetSelection() ).refresh()
			self.updateFileName()
		'''
		if hasattr(self, 'cameraProperties'):
			notebook = event.GetEventObject()
			if notebook.GetPage(event.GetOldSelection()) == self.cameraProperties:
				self.cameraProperties.commit()
			if notebook.GetPage(event.GetSelection()) == self.cameraProperties:
				self.cameraProperties.refresh()
		event.Skip()	# Required to properly repaint the screen.
	
	def commitButtonCallback( self, event ):
		if Model.race:
			wx.CallAfter( self.commit )
		else:
			Utils.MessageOK(self, _("You must have a valid race.  Open or New a race first."), _("No Valid Race"), iconMask=wx.ICON_ERROR)
	
	def loadTemplateButtonCallback( self, event ):
		race = Model.race
		if not race:
			Utils.MessageOK(self, _("You must have a valid race.  Open or New a race first."), _("No Valid Race"), iconMask=wx.ICON_ERROR)
			return
		templatesFolder = GetTemplatesFolder()
		try:
			os.makedirs( templatesFolder )
		except Exception as e:
			pass
		fd = wx.FileDialog(
			self,
			defaultDir=templatesFolder,
			message=_("Load Template"),
			wildcard="CrossMgr template files (*.cmnt)|*.cmnt",
			style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST,
		)
		if fd.ShowModal() == wx.ID_OK:
			path = fd.GetPath()
			if not Utils.MessageOKCancel(
					self, '{}\n\n{}\n\n{}\n\n{}'.format(
						_("Load Template"),
						os.path.basename(path),
						_("This will replace existing Properties."),
						_('Continue?')
					),
					_("Confirm Load Template"),
					wx.ICON_QUESTION,
				):
				return

			template = Template.Template()
			try:
				template.read( path )
				template.toRace( Model.race, True )
				self.refresh()
			except Exception as e:
				Utils.MessageOK( self, '{}\n\n{}\n{}'.format(_("Template Load Failure"), e, path), _("Template Load Failure"), wx.ICON_ERROR )
	
	def saveTemplateButtonCallback( self, event ):
		race = Model.race
		if not race:
			Utils.MessageOK(self, _("You must have a valid race.  Open or New a race first."), _("No Valid Race"), iconMask=wx.ICON_ERROR)
			return			
		self.commit()
		templatesFolder = os.path.join( os.path.expanduser("~"), 'CrossMgrTemplates' )
		try:
			os.makedirs( templatesFolder )
		except Exception as e:
			pass
		with wx.FileDialog(
				self,
				defaultDir=templatesFolder,
				message=_("Save as Template"),
				wildcard="CrossMgr template files (*.cmnt)|*.cmnt",
				style=wx.FD_SAVE,
			) as fd:
			
			if fd.ShowModal() != wx.ID_OK:
				return
			
			path = fd.GetPath()
			if not path.endswith('.cmnt'):
				path += '.cmnt'
			
			if os.path.isfile(path):
				if not Utils.MessageOKCancel( self, '{}?\n\n{}'.format(_("Replace Existing Template"), path), _('Relace Template') ):
					return
			
			template = Template.Template( Model.race )
			try:
				template.write( path )
				race.templateFileName = path
				self.refresh()
				message = '{}\n\n{}'.format(_("Template Saved to"), path)
				if os.path.basename(path) == 'default.cmnt':
					message += '\n\n{}'.format( _("Default template will be used for New races.") )
				Utils.MessageOK( self, message, _("Save Template Successful") )
			except Exception as e:
				Utils.MessageOK( self, '{}\n\n{}\n{}'.format(_("Template Save Failure"), e, path), _("Template Save Failure"), wx.ICON_ERROR )
	
	def setEditable( self, editable = True ):
		pass
	
	def incNext( self ):
		try:
			gi = self.generalInfoProperties
		except AttributeError:
			return ''		
		
		gi.raceNum.SetValue( gi.raceNum.GetValue() + 1 )
		gi.memo.SetValue( '' )
		if	 gi.scheduledStart.GetValue() == '10:00' and gi.minutes.GetValue() == 40 and gi.raceNum.GetValue() == 2:
			gi.scheduledStart.SetValue( '11:30' )
			gi.minutes.SetValue( 50 )
		elif gi.scheduledStart.GetValue() == '11:30' and gi.minutes.GetValue() == 50 and gi.raceNum.GetValue() == 3:
			gi.scheduledStart.SetValue( '13:00' )
			gi.minutes.SetValue( 60 )
		else:
			sStr = gi.scheduledStart.GetValue()
			fields = sStr.split(':')
			if len(fields) == 2:
				mins = int(fields[0],10) * 60 + int(fields[1],10)
				mins += gi.minutes.GetValue()
				mins += 15	# Add time for a break.
				if (mins/60) >= 24:
					mins = 0
				sNew = '{:02d}:{:02d}:00'.format(int(mins/60), mins%60)
				gi.scheduledStart.SetValue( sNew )
	
	def onChanged( self, event ):
		self.updateFileName()
	
	def updateFileName( self ):
		try:
			gi = self.generalInfoProperties
			fi = self.filesProperties
		except ValueError:
			return ''
	
		fname = Utils.GetFileName(
			gi.date.GetValue().Format(Properties.dateFormat),
			gi.raceName.GetValue(),
			gi.raceNum.GetValue(),
			gi.memo.GetValue(),
		)
		fi.fileName.SetLabel( fname )
		return fname
	
	def saveFileNameFields( self ):
		try:
			gi = self.generalInfoProperties
		except AttributeError:
			return ''		
		for f in ('date', 'raceName', 'raceNum', 'memo'):
			setattr(self, f + 'Original', getattr(gi, f).GetValue())
		
	def restoreFileNameFields( self ):
		try:
			gi = self.generalInfoProperties
		except AttributeError:
			return ''
		for f in ('date', 'raceName', 'raceNum', 'memo'):
			getattr(gi, f).SetValue( getattr(self, f + 'Original') )
	
	def getFileName( self ):
		return self.updateFileName()
	
	def refresh( self, forceUpdate=False ):
		self.updateFileName()
		if not forceUpdate and not self.state.changed():
			return

		with Model.LockRace() as race:
			self.setEditable( False )
			if race is None:
				return
			
			for prop, PropClass, name in self.propClassName:
				getattr(self, prop).refresh()
			
			self.saveFileNameFields()
			
		self.GetSizer().Layout()
		
	def doCommit( self ):
		undo.pushState()
		with Model.LockRace() as race:
			if race is None:
				return
			for prop, PropClass, name in self.propClassName:
				getattr(self, prop).commit()
			race.setChanged()
			race.resetAllCaches()
			
		if Utils.getMainWin():
			Utils.getMainWin().record.setTimeTrialInput( race.isTimeTrial )
		
	def commit( self ):
		success = SetNewFilename( self, self )
		self.doCommit()
		Model.resetCache()
		mainWin = Utils.getMainWin()
		if mainWin:
			wx.CallAfter( mainWin.lapCounterDialog.refresh )
			wx.CallAfter( mainWin.writeRace, False )
		wx.CallAfter( Utils.refreshForecastHistory )
		if not success and mainWin:
			wx.CallAfter( mainWin.showPage, mainWin.iPropertiesPage )
		
class PropertiesDialog( wx.Dialog ):
	def __init__(
			self, parent, ID = wx.ID_ANY, title=_("Change Properties"), size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
			showFileFields = True,
			updateProperties = False,
		):

		super().__init__( parent, ID, title=title, size=size, pos=pos, style=style )
		
		self.properties = Properties( self, addEditButton=False )
		
		vsizer = wx.BoxSizer( wx.VERTICAL )
		vsizer.Add(self.properties, 1, flag=wx.ALL|wx.EXPAND, border=5)
		if updateProperties:
			self.properties.refresh()

		if showFileFields:
			fgs = wx.FlexGridSizer( rows=0, cols=3, vgap=5, hgap=5 )
			fgs.AddGrowableCol( 1 )
						
			fgs.Add( wx.StaticText(self, label='{}:'.format(_('Race File Folder'))), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			self.folder = wx.TextCtrl( self, size=(400,-1) )
			self.folder.SetValue( Utils.getDocumentsDir() )
			fgs.Add( self.folder, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND)

			btn = wx.Button( self, label='{}...'.format(_('Browse')) )
			btn.Bind( wx.EVT_BUTTON, self.onBrowseFolder )
			fgs.Add( btn, wx.ALIGN_CENTER_VERTICAL )
			
			fgs.Add( wx.StaticText(self, label=_('Categories Import File (*.brc):')), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			self.categoriesFile = wx.TextCtrl( self, size=(400,-1) )
			self.categoriesFile.SetValue( Utils.getDocumentsDir() )
			fgs.Add( self.categoriesFile, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND )

			btn = wx.Button( self, label='{}...'.format(_('Browse')) )
			btn.Bind( wx.EVT_BUTTON, self.onBrowseCategories )
			fgs.Add( btn, flag=wx.ALIGN_CENTER_VERTICAL )
			
			vsizer.Add( fgs, flag=wx.EXPAND|wx.ALL, border=5)
			
			vsizer.Add( wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND|wx.RIGHT|wx.TOP, border=5)
		
		#-------------------------------------------------------------------------------------------------------------
		btnsizer = wx.BoxSizer( wx.VERTICAL )
        
		btnsizer.AddSpacer( 40 )
		btn = wx.Button( self, wx.ID_OK )
		btn.Bind( wx.EVT_BUTTON, self.onOK )
		btn.SetDefault()
		btnsizer.Add( btn, flag=wx.ALL, border=4 )

		btn = wx.Button( self, wx.ID_CANCEL )
		btnsizer.Add( btn, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4 )
		
		helpBtn = wx.Button( self, wx.ID_HELP )
		self.Bind( wx.EVT_BUTTON, lambda evt: HelpSearch.showHelp('Properties.html'), helpBtn )
		btnsizer.Add( helpBtn, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4 )
		#-------------------------------------------------------------------------------------------------------------

		sizer = wx.BoxSizer( wx.HORIZONTAL )
		sizer.Add( btnsizer )
		sizer.Add( vsizer )
		
		self.SetSizer(sizer)
		sizer.Fit(self)
		self.Layout()
	
	def onOK( self, event ):
		Utils.refresh()
		Utils.refreshForecastHistory()
		self.EndModal( wx.ID_OK )
	
	def onBrowseFolder( self, event ):
		defaultPath = self.folder.GetValue()
		if not defaultPath:
			defaultPath = Utils.getDocumentsDir()
			
		with wx.DirDialog( self, _("Choose a Folder for the Race"),
							style=wx.DD_DEFAULT_STYLE, defaultPath=defaultPath ) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.folder.SetValue( dlg.GetPath() )
	
	def onBrowseCategories( self, event ):
		defaultFile = self.categoriesFile.GetValue()
		if defaultFile.endswith('.brc'):
			dirName = os.path.dirname( defaultFile )
			fileName = os.path.basename( defaultFile )
		else:
			dirName = defaultFile
			fileName = ''
			if not dirName:
				dirName = self.folder.GetValue()
		
		with wx.FileDialog( self, message=_("Choose Race Categories File"),
							defaultDir=dirName, 
							defaultFile=fileName,
							wildcard=_("Bicycle Race Categories (*.brc)|*.brc"),
							style=wx.FD_OPEN ) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.categoriesFile.SetValue( dlg.GetPath() )
		
	def GetPath( self ):
		self.properties.updateFileName()
		return os.path.join( self.folder.GetValue(), self.properties.getFileName() )
		
	def GetCategoriesFile( self ):
		categoriesFile = self.categoriesFile.GetValue()
		return categoriesFile if categoriesFile.endswith( '.brc' ) else None

def SetNewFilename( parent, properties ):
	mainWin = Utils.getMainWin()
	if not mainWin:
		return True
	
	dir = os.path.dirname(mainWin.fileName) if mainWin.fileName else Utils.getDocumentsDir()
	
	newBaseName = properties.getFileName()
	if not newBaseName:
		newBaseName = _('UnnamedRace')
	newFName = os.path.join( dir, newBaseName )
	
	success = True
	if newFName != mainWin.fileName:
		if (
			not mainWin.fileName or
			Utils.MessageOKCancel(parent, '\n\n'.join( [
				_("The filename will be changed to:"),
				'{}',
				_("Continue?")]).format(newBaseName), _("Change Filename?"))
		):
			if os.path.exists(newFName):
				if not Utils.MessageOKCancel(parent, '\n\n'.join( [
						_("This file already exists:"),
						'{}',
						_("Overwrite?")]).format(newFName), _("Overwrite Existing File?")):
					properties.restoreFileNameFields()
					success = False
		else:
			properties.restoreFileNameFields()
			success = False
	
	newBaseName = properties.getFileName()
	newFName = os.path.join( dir, newBaseName )
	
	mainWin.fileName = newFName
	wx.CallAfter( mainWin.updateRecentFiles )	# Add to the recent files list.
	wx.CallAfter( mainWin.updateRaceClock )		# Also updates the window title.
	return success

def ChangeProperties( parent ):
	with PropertiesDialog( parent, showFileFields=False, updateProperties=True, size=(600,400) ) as propertiesDialog:
		propertiesDialog.properties.setEditable( True )
		try:
			if propertiesDialog.ShowModal() != wx.ID_OK:
				raise NameError('User Cancel')
				
			if not SetNewFilename( propertiesDialog, propertiesDialog.properties ):
				raise NameError('User Cancel')
				
			mainWin = Utils.getMainWin()
			
			propertiesDialog.properties.refresh()
			Model.resetCache()
			mainWin.writeRace()
			Utils.refresh()
			wx.CallAfter( Utils.refreshForecastHistory )
				
		except (NameError, AttributeError, TypeError):
			pass

def HasDefaultTemplate():
	return os.path.isfile( os.path.join( GetTemplatesFolder(), 'default.cmnt' ) )

def ApplyDefaultTemplate( race ):
	if not race:
		return False
	fname = os.path.join( GetTemplatesFolder(), 'default.cmnt' )
	template = Template.Template()
	try:
		template.read( fname )
	except Exception:
		return False
	template.toRace( race )
	return True

if __name__ == '__main__':
	race = Model.newRace()
	race._populate()
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,660))
	
	with PropertiesDialog( mainWin, title=_("Properties Dialog Test"), showFileFields=True, updateProperties=True ) as propertiesDialog:
		propertiesDialog.Show()
	
	properties = Properties( mainWin )
	properties.setEditable( True )
	properties.refresh()
	mainWin.Show()
	
	app.MainLoop()
