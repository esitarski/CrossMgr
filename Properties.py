import Utils
import Model
from PhotoFinish import HasPhotoFinish
from Undo import undo
import wx
import re
import os
import wx.lib.intctrl as intctrl
import wx.lib.masked as masked
import wx.lib.agw.flatnotebook as flatnotebook

#------------------------------------------------------------------------------------------------

def addToFGS( fgs, labelFieldFormats ):
	row = 0
	for i, (item, column, flag) in enumerate(labelFieldFormats):
		if not item:
			continue
		if column == 1:
			flag |= wx.EXPAND
		fgs.Add( item, flag=flag )

class GeneralInfoProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super(GeneralInfoProperties, self).__init__( parent, id )
		
		self.raceNameLabel = wx.StaticText( self, label=_('Event Name:') )
		self.raceName = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceName )
		
		self.raceCityLabel = wx.StaticText( self, label=_('City:') )
		self.raceCity = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceCity )
		
		self.raceStateProvLabel = wx.StaticText( self, label=_('State/Prov:') )
		self.raceStateProv = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceStateProv )
		
		self.raceCountryLabel = wx.StaticText( self, label=_('Country:') )
		self.raceCountry = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceCountry )
		
		self.locationSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.locationSizer.Add( self.raceCity, 4, flag=wx.EXPAND )
		self.locationSizer.Add( self.raceStateProvLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )
		self.locationSizer.Add( self.raceStateProv, 2, flag=wx.EXPAND )
		self.locationSizer.Add( self.raceCountryLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=16 )
		self.locationSizer.Add( self.raceCountry, 2, flag=wx.EXPAND )
		
		self.dateLabel = wx.StaticText( self, label = _('Date:') )
		self.date = wx.DatePickerCtrl( self, style = wx.DP_DROPDOWN, size=(160,-1) )
		self.Bind(wx.EVT_DATE_CHANGED, self.onChanged, self.date)
		
		self.raceDisciplineLabel = wx.StaticText( self, label = _('Discipline:') )
		self.raceDiscipline = wx.TextCtrl( self, value=u'Cyclo-cross', size=(160,-1) )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceDiscipline )
		
		self.dateDisciplineSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.dateDisciplineSizer.Add( self.date )
		self.dateDisciplineSizer.Add( self.raceDisciplineLabel, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border = 16 )
		self.dateDisciplineSizer.Add( self.raceDiscipline )
		self.dateDisciplineSizer.AddStretchSpacer()

		self.raceNumLabel = wx.StaticText( self, label=_('Race #:') )
		self.raceNum = intctrl.IntCtrl( self, min=1, max=1000, allow_none=False, value=1, size=(64,-1), style=wx.ALIGN_RIGHT )
		self.Bind(intctrl.EVT_INT, self.onChanged, self.raceNum)
		
		self.scheduledStartLabel = wx.StaticText( self, label=_('Scheduled Start:') )
		self.scheduledStart = masked.TimeCtrl( self, fmt24hr=True, display_seconds=False, value='10:00:00', size=(128,-1) )
		
		self.minutesLabel = wx.StaticText( self, label=_('Race Minutes:') )
		self.minutes = intctrl.IntCtrl( self, min=1, max=60*48, allow_none=False, value=40, size=(64,-1), style=wx.ALIGN_RIGHT )

		self.numStartMinutesSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.numStartMinutesSizer.Add( self.raceNum )
		self.numStartMinutesSizer.Add( self.scheduledStartLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border = 16 )
		self.numStartMinutesSizer.Add( self.scheduledStart )
		self.numStartMinutesSizer.Add( self.minutesLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border = 16 )
		self.numStartMinutesSizer.Add( self.minutes )
		self.numStartMinutesSizer.AddStretchSpacer()

		self.organizerLabel = wx.StaticText( self, label=_('Organizer:') )
		self.organizer = wx.TextCtrl( self )

		self.commissaireLabel = wx.StaticText( self, label=_('Official/Commissaire:') )
		self.commissaire = wx.TextCtrl( self )

		self.memoLabel = wx.StaticText( self, label=_('Memo:') )
		self.memo = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.memo )
		
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		fgs = wx.FlexGridSizer( rows=0, cols=2, vgap=12, hgap=3 )
		fgs.AddGrowableCol( 1 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fieldAlign = wx.EXPAND
		
		labelFieldFormats = [
			(self.raceNameLabel,	0, labelAlign),	(self.raceName,				1, fieldAlign),
			(self.raceCityLabel,	0, labelAlign),	(self.locationSizer,		1, fieldAlign),
			(self.dateLabel,		0, labelAlign),	(self.dateDisciplineSizer,	1, fieldAlign),
			(self.raceNumLabel,		0, labelAlign),	(self.numStartMinutesSizer,	1, fieldAlign),
			(self.organizerLabel,	0, labelAlign),	(self.organizer, 			1, fieldAlign),
			(self.commissaireLabel,	0, labelAlign),	(self.commissaire, 			1, fieldAlign),
			(self.memoLabel,		0, labelAlign),	(self.memo, 				1, fieldAlign),
		]
		addToFGS( fgs, labelFieldFormats )
		
		ms.Add( fgs, 1, flag=wx.EXPAND|wx.ALL, border=16 )

	def refresh( self ):
		race = Model.race
		self.raceName.SetValue( race.name )
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
		super(RaceOptionsProperties, self).__init__( parent, id )
		
		self.timeTrial = wx.CheckBox( self, label=_('Time Trial') )
		
		self.allCategoriesFinishAfterFastestRidersLastLap = wx.CheckBox( self, label=_("All Categories Finish After Fastest Rider's Last Lap") )
		self.allCategoriesFinishAfterFastestRidersLastLap.SetValue( True )
		
		self.autocorrectLapsDefault = wx.CheckBox( self, label=_('Set "Autocorrect Lap Data" option by Default') )
		self.autocorrectLapsDefault.SetValue( True )

		self.highPrecisionTimes = wx.CheckBox( self, label=_('Show Times to 100s of a Second') )
		
		self.rule80MinLapCountLabel = wx.StaticText( self, label=_("Lap Time for 80% Rule: ") )
		self.rule80MinLapCount1 = wx.RadioButton( self, label=_("1st Lap Time"), style=wx.RB_GROUP )
		self.rule80MinLapCount2 = wx.RadioButton( self, label=_("2nd Lap Time") )
		self.rule80MinLapCount2.SetValue( True )
		self.rule80MinLapCountSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.rule80MinLapCountSizer.Add( self.rule80MinLapCount1, flag=wx.RIGHT, border=8 )
		self.rule80MinLapCountSizer.Add( self.rule80MinLapCount2 )
		
		self.distanceUnitLabel = wx.StaticText( self, label=_('Distance Unit: ') )
		self.distanceUnit = wx.Choice( self, choices=[u'km', u'miles'] )
		self.distanceUnit.SetSelection( 0 )
		self.distanceUnitSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.distanceUnitSizer.Add( self.distanceUnit )
		self.distanceUnitSizer.AddStretchSpacer()
		
		self.showDetails = wx.CheckBox( self, label=_("Show Lap Notes, Edits and Projected Times in HTML Output") )

		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.HORIZONTAL )
		self.SetSizer( ms )
		
		fgs = wx.FlexGridSizer( rows=0, cols=2, vgap=12, hgap=3 )
		fgs.AddGrowableCol( 1 )

		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fieldAlign = wx.EXPAND
		
		blank = lambda : wx.StaticText( self, label=u'' )
		
		labelFieldFormats = [
			(blank(),				0, labelAlign),		(self.timeTrial,				1, fieldAlign),
			(blank(),				0, labelAlign),		(self.allCategoriesFinishAfterFastestRidersLastLap,	1, fieldAlign),
			(blank(),				0, labelAlign),		(self.autocorrectLapsDefault,	1, fieldAlign),
			(blank(),				0, labelAlign),		(self.highPrecisionTimes,		1, fieldAlign),
			(self.rule80MinLapCountLabel, 0, labelAlign),(self.rule80MinLapCountSizer,	1, fieldAlign),
			(self.distanceUnitLabel,0, labelAlign),		(self.distanceUnitSizer,		1, fieldAlign),
			(blank(),				0, labelAlign),		(self.showDetails,				1, fieldAlign),
		]
		addToFGS( fgs, labelFieldFormats )
		
		ms.Add( fgs, 1, flag=wx.EXPAND|wx.ALL, border=16 )

	def refresh( self ):
		race = Model.race
		self.timeTrial.SetValue( getattr(race, 'isTimeTrial', False) )
		self.allCategoriesFinishAfterFastestRidersLastLap.SetValue( getattr(race, 'allCategoriesFinishAfterFastestRidersLastLap', False) )
		self.autocorrectLapsDefault.SetValue( getattr(race, 'autocorrectLapsDefault', True) )
		self.highPrecisionTimes.SetValue( getattr(race, 'highPrecisionTimes', False) )
		if race.rule80MinLapCount == 1:
			self.rule80MinLapCount1.SetValue( True )
		else:
			self.rule80MinLapCount2.SetValue( True )
		self.distanceUnit.SetSelection( getattr(race, 'distanceUnit', 0) )
		self.showDetails.SetValue( not race.hideDetails )
	
	def commit( self ):
		race = Model.race
		race.isTimeTrial = self.timeTrial.IsChecked()
		race.allCategoriesFinishAfterFastestRidersLastLap = self.allCategoriesFinishAfterFastestRidersLastLap.IsChecked()
		race.autocorrectLapsDefault = self.autocorrectLapsDefault.IsChecked()
		race.highPrecisionTimes = self.highPrecisionTimes.IsChecked()
		race.rule80MinLapCount = (1 if self.rule80MinLapCount1.GetValue() else 2)
		race.distanceUnit = self.distanceUnit.GetSelection()
		race.hideDetails = not self.showDetails.IsChecked()
	
#------------------------------------------------------------------------------------------------

class RfidProperties( wx.Panel ):
	iResetStartClockOnFirstTag = 1
	iSkipFirstTagRead = 2
	choices = [	_('Manual Start: Collect every chip. \nDoes NOT restart race clock on first read.'),
				_('Automatic Start: Reset start clock on first tag read. \nAll riders get the start time of the first read.'),
				_('Manual Start: Skip first tag read for all riders. \nRequired when start run-up passes the finish on the first lap.')]

	def __init__( self, parent, id = wx.ID_ANY ):
		super(RfidProperties, self).__init__( parent, id )
		self.jchip = wx.CheckBox( self, style=wx.ALIGN_LEFT, label = _('Use RFID Reader') )

		self.chipTimingOptions = wx.RadioBox(
			self,
			label=_("Chip Timing Options"),
			majorDimension=1,
			choices=self.choices,
			style=wx.RA_SPECIFY_COLS
		)
		
		self.chipTimingOptions.SetSelection( self.iResetStartClockOnFirstTag )
		
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		ms.Add( self.jchip, flag=wx.ALL, border=16 )
		ms.Add( self.chipTimingOptions, flag=wx.ALL, border=4 )
		
	def refresh( self ):
		race = Model.race
		self.jchip.SetValue( getattr(race, 'enableJChipIntegration', False) )
		resetStartClockOnFirstTag = getattr(race, 'resetStartClockOnFirstTag', True)
		skipFirstTagRead = getattr(race, 'skipFirstTagRead', False)
		if resetStartClockOnFirstTag:
			self.chipTimingOptions.SetSelection( self.iResetStartClockOnFirstTag )
		elif skipFirstTagRead:
			self.chipTimingOptions.SetSelection( self.iSkipFirstTagRead )
		else:
			self.chipTimingOptions.SetSelection( 0 )
		
	def commit( self ):
		race = Model.race
		race.enableJChipIntegration = self.jchip.IsChecked()
		iSelection = self.chipTimingOptions.GetSelection()
		race.resetStartClockOnFirstTag	= bool(iSelection == self.iResetStartClockOnFirstTag)
		race.skipFirstTagRead			= bool(iSelection == self.iSkipFirstTagRead)
	
#------------------------------------------------------------------------------------------------

class CameraProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super(CameraProperties, self).__init__( parent, id )
		
		choices = [
			_("Do Not Use Camera for Photo Finish"),
			_("Photos on Every Lap"),
			_("Photos at Race Finish Only"),
		]
		self.radioBox = wx.RadioBox( self, label=_("USB Camera Options"), choices=choices, majorDimension=1, style=wx.RA_SPECIFY_COLS )
		
		'''
		self.enableUSBCamera = wx.CheckBox( self, label=_('Use USB Camera for Photo Finish') )
		self.photosAtRaceEndOnly = wx.CheckBox( self, label=_('Take Photos at Race End Only') )
		'''
		
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		ms.Add( self.radioBox, flag=wx.ALL, border=16 )
		
	def refresh( self ):
		race = Model.race
		if not getattr(race, 'enableUSBCamera', False):
			self.radioBox.SetSelection( 0 )
		else:
			if not race.photosAtRaceEndOnly:
				self.radioBox.SetSelection( 1 )
			else:
				self.radioBox.SetSelection( 2 )
		
	def commit( self ):
		race = Model.race
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
		super(AnimationProperties, self).__init__( parent, id )
		
		self.note = wx.StaticText( self, label=u'\n'.join ([
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
class NotesProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super(NotesProperties, self).__init__( parent, id )
		
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		self.notesLabel = wx.StaticText( self, label=u'\n'.join( [
			_("Notes to appear on Html output:"),
			_("(notes containing Html tags must start with <html> and end with </html>)")] ) )
		self.notes = wx.TextCtrl( self, style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB, size=(-1,60) )
		self.insertButton = wx.Button( self, label=_('Insert Variable...') )
		self.insertButton.Bind( wx.EVT_BUTTON, self.onInsertClick )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.notesLabel )
		hs.AddStretchSpacer()
		hs.Add( self.insertButton )
		ms.Add( hs, flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, border=16 )
		ms.Add( self.notes, 1, flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border=16 )

	def onInsertClick( self, event ):
		race = Model.race
		if not race:
			return
		
		if not hasattr(self, 'menu'):
			self.menu = wx.Menu()
			self.idVariable = {}
			for v in sorted(race.getTemplateValues().keys()):
				idCur = wx.NewId()
				v = u'{=' + v + u'}'
				self.idVariable[idCur] = v
				self.menu.Append( idCur, v )
				self.Bind( wx.EVT_MENU, self.onInsertVariable, id=idCur )
		
		self.PopupMenu( self.menu )
		wx.CallAfter( self.notes.SetFocus )
		
	def onInsertVariable( self, event ):
		v = self.idVariable[event.GetId()]
		iCur = self.notes.GetInsertionPoint()
		self.notes.Replace( iCur, iCur, v )
		self.notes.SetInsertionPoint( iCur + len(v) )
	
	def refresh( self ):
		race = Model.race
		self.notes.SetValue( getattr(race, 'notes', '') )
		
	def commit( self ):
		race = Model.race
		race.notes = self.notes.GetValue()

#------------------------------------------------------------------------------------------------
class FilesProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super(FilesProperties, self).__init__( parent, id )
		
		self.fileNameLabel = wx.StaticText( self, label=_('File Name:') )
		self.fileName = wx.StaticText( self )

		self.excelNameLabel = wx.StaticText( self, label=_('Excel Link File:') )
		self.excelName = wx.StaticText( self )

		self.categoriesFileLabel = wx.StaticText( self, label=_('Categories Initially Loaded From:') )
		self.categoriesFile = wx.StaticText( self )

		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		fgs = wx.FlexGridSizer( rows=0, cols=2, vgap=12, hgap=3 )
		fgs.AddGrowableCol( 1 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fieldAlign = wx.EXPAND
		
		blank = lambda : wx.StaticText( self, label='' )
		
		labelFieldFormats = [
			(self.fileNameLabel,		0, labelAlign),		(self.fileName,			1, fieldAlign),
			(self.excelNameLabel,		0, labelAlign),		(self.excelName,		1, fieldAlign),
			(self.categoriesFileLabel,	0, labelAlign),		(self.categoriesFile,	1, fieldAlign),
		]
		addToFGS( fgs, labelFieldFormats )
		ms.Add( fgs, 1, flag=wx.EXPAND|wx.ALL, border=16 )
		
	def refresh( self ):
		race = Model.race
		excelLink = getattr(race, 'excelLink', None)
		if excelLink:
			self.excelName.SetLabel( u'%s|%s' % (
				os.path.basename(excelLink.fileName) if excelLink.fileName else '',
				excelLink.sheetName if excelLink.sheetName else '') )
		else:
			self.excelName.SetLabel( '' )
		self.categoriesFile.SetLabel( os.path.basename(getattr(race, 'categoriesImportFile', '')) )
		
	def commit( self ):
		pass
		
#------------------------------------------------------------------------------------------------

class Properties( wx.Panel ):
	badFileCharsRE = re.compile( '[^a-zA-Z0-9_ ]+' )
	dateFormat = '%Y-%m-%d'

	def __init__( self, parent, id=wx.ID_ANY, addEditButton=True ):
		super(Properties, self).__init__(parent, id)

		self.SetBackgroundColour( wx.WHITE )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( mainSizer )
		
		bookStyle = (
			  flatnotebook.FNB_NO_NAV_BUTTONS
			| flatnotebook.FNB_NO_X_BUTTON
			| flatnotebook.FNB_VC8
			| flatnotebook.FNB_NODRAG
		)
		self.notebook = flatnotebook.FlatNotebook( self, agwStyle=bookStyle )
		self.notebook.SetBackgroundColour( wx.WHITE )
		self.notebook.SetTabAreaColour( wx.WHITE )
		self.notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanging )

		self.propClassName = [
			('generalInfoProperties',	GeneralInfoProperties,		_('General Info') ),
			('raceOptionsProperties',	RaceOptionsProperties,		_('Race Options') ),
			('notesProperties',			NotesProperties,			_('Notes') ),
			('rfidProperties',			RfidProperties,				_('RFID') ),
			('cameraProperties',		CameraProperties,			_('Camera') ),
			('animationProperties',		AnimationProperties,		_('Animation') ),
			('filesProperties',			FilesProperties,			_('Files') ),
		]
		for prop, PropClass, name in self.propClassName:
			setattr( self, prop, PropClass(self.notebook) )
			self.notebook.AddPage( getattr(self, prop), name )
		
		self.updateFileName()
		
		mainSizer.Add( self.notebook, 1, flag=wx.ALL|wx.EXPAND, border=4 )
		
		if addEditButton:
			hs = wx.BoxSizer( wx.HORIZONTAL )
			
			self.commitButton = wx.Button(self, label=_('Commit'))
			self.commitButton.Bind( wx.EVT_BUTTON, self.commitButtonCallback )
			hs.Add( self.commitButton, flag=wx.TOP|wx.BOTTOM, border=8 )
			
			self.excelButton = wx.Button(self, label=_('Link External Excel Sheet...'))
			self.excelButton.Bind( wx.EVT_BUTTON, self.excelButtonCallback )
			hs.Add( self.excelButton, flag=wx.LEFT|wx.TOP|wx.BOTTOM, border=8 )

			mainSizer.Add( hs, flag=wx.ALL, border=4 )
			
		self.setEditable()
		mainSizer.Fit(self)
		self.Layout()
		
	def onJChipIntegration( self, event ):
		self.rfidProperties.autocorrectLapsDefault.SetValue( not self.rfidProperties.jchip.GetValue() )
	
	def onPageChanging( self, event ):
		'''
		if Model.race:
			notebook = event.GetEventObject()
			notebook.GetPage( event.GetOldSelection() ).commit()
			notebook.GetPage( event.GetSelection() ).refresh()
			self.updateFileName()
		'''
		event.Skip()	# Required to properly repaint the screen.
	
	def excelButtonCallback( self, event ):
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.menuLinkExcel()
	
	def commitButtonCallback( self, event ):
		mainWin = Utils.getMainWin()
		if Model.race:
			wx.CallAfter( self.commit )
		else:
			Utils.MessageOK( self,
				_('You must have a valid race File|Open...\nOr create one with File|New....'), _('Valid Race Required'),
				wx.ICON_WARNING )
	
	def setEditable( self, editable = True ):
		if hasattr(self, 'cameraProperties') and not HasPhotoFinish():
			self.cameraProperties.enableUSBCamera.Disable()
	
	def incNext( self ):
		if not hasattr(self,'generalInfoProperties'):
			return ''

		gi = self.generalInfoProperties
		
		gi.raceNum.SetValue( gi.raceNum.GetValue() + 1 )
		gi.memo.SetValue( '' )
		if	 gi.scheduledStart.GetValue() == '10:00' and gi.minutes.GetValue() == 40 and gi.raceNum.GetValue() == 2:
			gi.scheduledStart.SetValue( '11:30' )
			gi.minutes.SetValue( 50 )
		elif gi.scheduledStart.GetValue() == '11:30' and gi.minutes.GetValue() == 50 and gi.raceNum.GetValue() == 3:
			gi.scheduledStart.SetValue( '13:00' )
			gi.minutes.SetValue( 60 )
		else:
			sStr = '{}'.format(gi.scheduledStart.GetValue())
			fields = sStr.split(':')
			if len(fields) == 2:
				mins = int(fields[0],10) * 60 + int(fields[1],10)
				mins += gi.minutes.GetValue()
				mins += 15	# Add time for a break.
				if (mins/60) >= 24:
					mins = 0
				sNew = '%02d:%02d:00' % (int(mins/60), mins%60)
				gi.scheduledStart.SetValue( sNew )
	
	def onChanged( self, event ):
		self.updateFileName()
	
	def updateFileName( self ):
		if not hasattr(self,'filesProperties') or not hasattr(self,'generalInfoProperties'):
			return ''
		
		gi = self.generalInfoProperties
		
		rDate = gi.date.GetValue().Format(Properties.dateFormat)
		rName = Properties.badFileCharsRE.sub( ' ', gi.raceName.GetValue() ).strip()
		rNum = gi.raceNum.GetValue()
		rMemo = Properties.badFileCharsRE.sub( ' ', gi.memo.GetValue() ).strip()
		
		fname = u'%s-%s-r%d-%s.cmn' % (rDate, rName, rNum, rMemo )
		self.filesProperties.fileName.SetLabel( fname )
		return fname
	
	def saveFileNameFields( self ):
		if not hasattr(self,'generalInfoProperties'):
			return ''
		gi = self.generalInfoProperties
		
		for f in ['date', 'raceName', 'raceNum', 'memo']:
			setattr(self, f + 'Original', getattr(gi, f).GetValue())
		
	def restoreFileNameFields( self ):
		if not hasattr(self,'generalInfoProperties'):
			return ''
		gi = self.generalInfoProperties
		for f in ['date', 'raceName', 'raceNum', 'memo']:
			getattr(gi, f).SetValue( getattr(self, f + 'Original') )
	
	def getFileName( self ):
		return self.updateFileName()
	
	def refresh( self ):
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
			
		if Utils.getMainWin():
			Utils.getMainWin().record.setTimeTrialInput( race.isTimeTrial )
		
	def commit( self ):
		success = SetNewFilename( self, self )
		self.doCommit()
		Model.resetCache()
		mainWin = Utils.getMainWin()
		if mainWin:
			wx.CallAfter( mainWin.writeRace, False )
		wx.CallAfter( Utils.refreshForecastHistory )
		if not success and mainWin:
			wx.CallAfter( mainWin.showPageName, _("Properties") )
		
class PropertiesDialog( wx.Dialog ):
	def __init__(
			self, parent, ID = wx.ID_ANY, title=_("Change Properties"), size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
			showFileFields = True,
			updateProperties = False,
		):

		super( PropertiesDialog, self ).__init__( parent, ID, title=title, size=size, pos=pos, style=style )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer(sizer)

		self.properties = Properties( self, addEditButton=False )
		sizer.Add(self.properties, 1, flag=wx.ALL|wx.EXPAND, border=5)
		if updateProperties:
			self.properties.refresh()

		if showFileFields:
			fgs = wx.FlexGridSizer( rows=0, cols=3, vgap=5, hgap=5 )
			fgs.AddGrowableCol( 1 )
						
			fgs.Add( wx.StaticText(self, label=_('Race File Folder:')), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			self.folder = wx.TextCtrl( self, size=(400,-1) )
			self.folder.SetValue( Utils.getDocumentsDir() )
			fgs.Add( self.folder, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND)

			btn = wx.Button( self, label=_('Browse...') )
			btn.Bind( wx.EVT_BUTTON, self.onBrowseFolder )
			fgs.Add( btn, wx.ALIGN_CENTER_VERTICAL )
			
			fgs.Add( wx.StaticText(self, label=_('Categories Import File (*.brc):')), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			self.categoriesFile = wx.TextCtrl( self, size=(400,-1) )
			self.categoriesFile.SetValue( Utils.getDocumentsDir() )
			fgs.Add( self.categoriesFile, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.EXPAND )

			btn = wx.Button( self, label=_('Browse...') )
			btn.Bind( wx.EVT_BUTTON, self.onBrowseCategories )
			fgs.Add( btn, flag=wx.ALIGN_CENTER_VERTICAL )
			
			sizer.Add( fgs, flag=wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL, border=5)
			
			sizer.Add( wx.StaticLine(self, style=wx.LI_HORIZONTAL), flag=wx.EXPAND|wx.RIGHT|wx.TOP, border=5)
		
		#-------------------------------------------------------------------------------------------------------------
		btnsizer = wx.StdDialogButtonSizer()
        
		btn = wx.Button( self, wx.ID_OK )
		btn.SetDefault()
		btnsizer.AddButton( btn )

		btn = wx.Button( self, wx.ID_CANCEL )
		btnsizer.AddButton( btn )
		
		helpBtn = wx.Button( self, wx.ID_HELP )
		self.Bind( wx.EVT_BUTTON, lambda evt: Utils.showHelp('Properties.html'), helpBtn )
		btnsizer.AddButton( helpBtn )
		
		btnsizer.Realize()

		sizer.Add(btnsizer, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.ALIGN_RIGHT, border=5)
		#-------------------------------------------------------------------------------------------------------------
		
		sizer.Fit(self)
		self.Layout()
		
	def onBrowseFolder( self, event ):
		defaultPath = self.folder.GetValue()
		if not defaultPath:
			defaultPath = Utils.getDocumentsDir()
			
		dlg = wx.DirDialog( self, _("Choose a Folder for the Race"),
							style=wx.DD_DEFAULT_STYLE, defaultPath=defaultPath )
		if dlg.ShowModal() == wx.ID_OK:
			self.folder.SetValue( dlg.GetPath() )
		dlg.Destroy()		
	
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
		
		dlg = wx.FileDialog( self, message=_("Choose Race Categories File"),
							defaultDir=dirName, 
							defaultFile=fileName,
							wildcard=_("Bicycle Race Categories (*.brc)|*.brc"),
							style=wx.OPEN )
		if dlg.ShowModal() == wx.ID_OK:
			self.categoriesFile.SetValue( dlg.GetPath() )
		dlg.Destroy()
		
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
			Utils.MessageOKCancel(parent, u'\n\n'.join( [
				_("The filename will be changed to:"),
				u'{}',
				_("Continue?")]).format(newBaseName), _("Change Filename?"))
		):
			if os.path.exists(newFName):
				if not Utils.MessageOKCancel(parent, u'\n\n'.join( [
						_("This file already exists:"),
						u'{}',
						_("Overwrite?")]).format(newFName), _("Overwrite Existing File?")):
					properties.restoreFileNameFields()
					success = False
		else:
			properties.restoreFileNameFields()
			success = False
	
	newBaseName = properties.getFileName()
	newFName = os.path.join( dir, newBaseName )
	
	mainWin.fileName = newFName
	return success

def ChangeProperties( parent ):
	propertiesDialog = PropertiesDialog( parent, showFileFields=False, updateProperties=True, size=(600,400) )
	propertiesDialog.properties.setEditable( True )
	try:
		if propertiesDialog.ShowModal() != wx.ID_OK:
			raise NameError('User Cancel')
			
		if not SetNewFilename( propertiesDialog, propertiesDialog.properties ):
			raise NameError('User Cancel')
			
		mainWin = Utils.getMainWin()
		dir = os.path.dirname( mainWin.fileName )
		
		propertiesDialog.properties.refresh()
		Model.resetCache()
		mainWin.writeRace()
		Utils.refresh()
		wx.CallAfter( Utils.refreshForecastHistory )
			
	except (NameError, AttributeError, TypeError):
		pass
	
	propertiesDialog.Destroy()
		
if __name__ == '__main__':
	race = Model.newRace()
	race._populate()
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,600))
	
	propertiesDialog = PropertiesDialog( mainWin, title=_("Properties Dialog Test"), showFileFields=True, updateProperties=True )
	propertiesDialog.Show()
	
	properties = Properties( mainWin )
	properties.setEditable( True )
	properties.refresh()
	mainWin.Show()
	
	app.MainLoop()
