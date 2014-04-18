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

class RaceProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super(RaceProperties, self).__init__( parent, id )
		rows = 0
		self.rule80MinLapCountLabel = wx.StaticText( self, label = _("Lap Time for 80% Rule: ") )
		self.rule80MinLapCount1 = wx.RadioButton( self, label = _("1st Lap Time"), style = wx.RB_GROUP )
		self.rule80MinLapCount2 = wx.RadioButton( self, label = _("2nd Lap Time") )
		self.rule80MinLapCount2.SetValue( True )
		self.rule80MinLapCountSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.rule80MinLapCountSizer.Add( self.rule80MinLapCount1, flag=wx.RIGHT, border=8 )
		self.rule80MinLapCountSizer.Add( self.rule80MinLapCount2 )
		rows += 1
		
		self.allCategoriesFinishAfterFastestRidersLastLap = wx.CheckBox( self, style=wx.ALIGN_LEFT, label = _("All Categories Finish After Fastest Rider's Last Lap") )
		self.allCategoriesFinishAfterFastestRidersLastLap.SetValue( True )
		rows += 1
		
		self.timeTrial = wx.CheckBox( self, style=wx.ALIGN_LEFT, label = _('Time Trial') )
		rows += 1
		
		self.autocorrectLapsDefault = wx.CheckBox( self, style=wx.ALIGN_LEFT, label = _('Set "Autocorrect Lap Data" option by Default') )
		self.autocorrectLapsDefault.SetValue( True )
		rows += 1

		self.distanceUnitLabel = wx.StaticText( self, label = _('Distance Unit: ') )
		self.distanceUnit = wx.Choice( self, choices=['km', 'miles'] )
		self.distanceUnit.SetSelection( 0 )
		rows += 1

		self.highPrecisionTimes = wx.CheckBox( self, style=wx.ALIGN_LEFT, label = _('Show Times to 100s of a Second') )
		rows += 1
		
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.HORIZONTAL )
		self.SetSizer( ms )
		
		fgs = wx.FlexGridSizer( rows=rows, cols=2, vgap=3, hgap=3 )
		ms.Add( fgs, 1, flag=wx.EXPAND|wx.ALL, border=16 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fieldAlign = wx.EXPAND|wx.GROW
		
		blank = lambda : wx.StaticText( self, label='' )
		
		labelFieldFormats = [
			(self.rule80MinLapCountLabel,	0, labelAlign),		(self.rule80MinLapCountSizer,		1, fieldAlign),
			(blank(),	0, labelAlign),		(self.allCategoriesFinishAfterFastestRidersLastLap,		1, fieldAlign),
			(blank(),				0, labelAlign),		(self.timeTrial,		1, fieldAlign),
			(blank(),				0, labelAlign),(self.autocorrectLapsDefault,1, fieldAlign),
			(self.distanceUnitLabel,0, labelAlign),		(self.distanceUnit,		1, fieldAlign),
			(blank(),				0, labelAlign),(self.highPrecisionTimes,1, fieldAlign),
		]
		addToFGS( fgs, labelFieldFormats )

	def update( self ):
		race = Model.race
		if race.rule80MinLapCount == 1:
			self.rule80MinLapCount1.SetValue( True )
		else:
			self.rule80MinLapCount2.SetValue( True )
		self.allCategoriesFinishAfterFastestRidersLastLap.SetValue( getattr(race, 'allCategoriesFinishAfterFastestRidersLastLap', False) )
		self.timeTrial.SetValue( getattr(race, 'isTimeTrial', False) )
		self.highPrecisionTimes.SetValue( getattr(race, 'highPrecisionTimes', False) )
		self.distanceUnit.SetSelection( getattr(race, 'distanceUnit', 0) )
		self.autocorrectLapsDefault.SetValue( getattr(race, 'autocorrectLapsDefault', True) )
	
	def commit( self ):
		race = Model.race
		race.rule80MinLapCount = (1 if self.rule80MinLapCount1.GetValue() else 2)
		race.allCategoriesFinishAfterFastestRidersLastLap = self.allCategoriesFinishAfterFastestRidersLastLap.IsChecked()
		race.isTimeTrial = self.timeTrial.IsChecked()
		race.highPrecisionTimes = self.highPrecisionTimes.IsChecked()
		race.distanceUnit = self.distanceUnit.GetSelection()
		race.autocorrectLapsDefault = self.autocorrectLapsDefault.IsChecked()
	
#------------------------------------------------------------------------------------------------

class RfidProperties( wx.Panel ):
	iResetStartClockOnFirstTag = 1
	iSkipFirstTagRead = 2

	def __init__( self, parent, id = wx.ID_ANY ):
		super(RfidProperties, self).__init__( parent, id )
		self.jchip = wx.CheckBox( self, style=wx.ALIGN_LEFT, label = _('Use RFID Reader') )

		choices = [	_('Record Every Tag Individually'),
					_('Reset Start Clock on First Tag Read (all riders will get the same start time of the first read)'),
					_('Skip First Tag Read for All Riders (required when there is a start run-up that passes through the finish on the first lap)')]
		self.chipTimingOptions = wx.RadioBox( self, label = _("Chip Timing Options"), majorDimension = 1, choices = choices, style = wx.RA_SPECIFY_COLS )
		
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		ms.Add( self.jchip, flag=wx.ALL, border = 16 )
		ms.Add( self.chipTimingOptions, flag=wx.ALL, border = 4 )
		
	def update( self ):
		race = Model.race
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
		iSelection = self.chipTimingOptions.GetSelection()
		race.resetStartClockOnFirstTag	= bool(iSelection == self.iResetStartClockOnFirstTag)
		race.skipFirstTagRead			= bool(iSelection == self.iSkipFirstTagRead)
	
#------------------------------------------------------------------------------------------------

class CameraProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super(CameraProperties, self).__init__( parent, id )
		self.enableUSBCamera = wx.CheckBox( self,style=wx.ALIGN_LEFT, label = _('Use USB Camera for Photo Finish') )
		
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		ms.Add( self.enableUSBCamera, flag=wx.ALL, border=16 )
		
	def update( self ):
		race = Model.race
		self.enableUSBCamera.SetValue( getattr(race, 'enableUSBCamera', False) )
		
	def commit( self ):
		race = Model.race
		race.enableUSBCamera = self.enableUSBCamera.GetValue()
	
#------------------------------------------------------------------------------------------------

class AnimationProperties( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super(AnimationProperties, self).__init__( parent, id )
		
		self.finishTop = wx.CheckBox( self, style=wx.ALIGN_LEFT, label=_('Animation Finish on Top') )
		self.reverseDirection = wx.CheckBox( self, style=wx.ALIGN_LEFT, label=_('Animation Reverse Direction') )
		self.note = wx.StaticText( self, label=_('This only applie to the Track animation.\nThe GPX animation follows the lat/lng coordinates.') )
		
		#-------------------------------------------------------------------------------
		ms = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( ms )
		
		ms.Add( self.note, flag=wx.TOP|wx.LEFT, border=16 )
		ms.Add( self.finishTop, flag=wx.TOP|wx.LEFT, border=16 )
		ms.Add( self.reverseDirection, flag=wx.TOP|wx.LEFT, border=16 )
		
	def update( self ):
		race = Model.race
		self.reverseDirection.SetValue( getattr(race, 'reverseDirection', False) )
		self.finishTop.SetValue( getattr(race, 'finishTop', False) )
		
	def commit( self ):
		race = Model.race
		race.reverseDirection = self.reverseDirection.GetValue()
		race.finishTop = self.finishTop.GetValue()

#------------------------------------------------------------------------------------------------

class Properties( wx.Panel ):
	badFileCharsRE = re.compile( '[^a-zA-Z0-9_ ]+' )
	dateFormat = '%Y-%m-%d'

	def __init__( self, parent, id = wx.ID_ANY, addEditButton = True ):
		wx.Panel.__init__(self, parent, id)

		self.SetBackgroundColour( wx.WHITE )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		self.SetSizer( vs )
		
		rows = 0
		
		self.raceNameLabel = wx.StaticText( self, label = _('Event Name:') )
		self.raceName = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceName )
		rows += 1
		
		self.raceCityLabel = wx.StaticText( self, label = _('City:') )
		self.raceCity = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceCity )
		
		self.raceStateProvLabel = wx.StaticText( self, label = _('State/Prov:') )
		self.raceStateProv = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceStateProv )
		
		self.raceCountryLabel = wx.StaticText( self, label = _('Country') )
		self.raceCountry = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceCountry )
		
		self.locationSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.locationSizer.Add( self.raceCity, 4, flag=wx.EXPAND )
		self.locationSizer.Add( self.raceStateProvLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border = 4 )
		self.locationSizer.Add( self.raceStateProv, 1, flag=wx.EXPAND )
		self.locationSizer.Add( self.raceCountryLabel, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border = 4 )
		self.locationSizer.Add( self.raceCountry, 2, flag=wx.EXPAND )
		rows += 1
		
		self.dateLabel = wx.StaticText( self, label = _('Date:') )
		self.date = wx.DatePickerCtrl( self, style = wx.DP_DROPDOWN )
		self.Bind(wx.EVT_DATE_CHANGED, self.onChanged, self.date)
		rows += 1
		
		self.raceNumLabel = wx.StaticText( self, label = _('Race #:') )
		self.raceNum = intctrl.IntCtrl( self, min=1, max=1000, allow_none=False, value=1 )
		self.Bind(intctrl.EVT_INT, self.onChanged, self.raceNum)
		rows += 1
		
		self.scheduledStartLabel = wx.StaticText( self, label = _('Scheduled Start:') )
		self.scheduledStart = masked.TimeCtrl( self, fmt24hr=True, display_seconds=False, value='10:00:00' )
		rows += 1

		self.minutesLabel = wx.StaticText( self, label = _('Race Minutes:') )
		self.minutes = intctrl.IntCtrl( self, min=1, max=60*24, allow_none=False, value=40 )
		rows += 1

		self.raceDisciplineLabel = wx.StaticText( self, label = _('Discipline:') )
		self.raceDiscipline = wx.TextCtrl( self, value=u'Cyclo-cross' )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceDiscipline )
		rows += 1
		
		self.organizerLabel = wx.StaticText( self, label = _('Organizer:') )
		self.organizer = wx.TextCtrl( self )
		rows += 1
		
		self.commissaireLabel = wx.StaticText( self, label = _('Official/Commissaire:') )
		self.commissaire = wx.TextCtrl( self )
		rows += 1
		
		self.memoLabel = wx.StaticText( self, label = _('Memo:') )
		self.memo = wx.TextCtrl( self )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.memo )
		rows += 1
		
		bookStyle = (
			  flatnotebook.FNB_NO_NAV_BUTTONS
			| flatnotebook.FNB_NO_NAV_BUTTONS
			| flatnotebook.FNB_NO_X_BUTTON
			| flatnotebook.FNB_VC8
			| flatnotebook.FNB_NODRAG
		)
		self.notebook = flatnotebook.FlatNotebook(self, wx.ID_ANY, agwStyle=bookStyle)
		self.notebook.SetBackgroundColour( wx.WHITE )
		self.notebook.SetTabAreaColour( wx.WHITE )
		self.propClass = [
			('raceProperties', RaceProperties),
			('RFIDProperties', RfidProperties),
			('cameraProperties', CameraProperties),
			('animationProperties', AnimationProperties),
		]
		for prop, PropClass in self.propClass:
			setattr( self, prop, PropClass(self.notebook) )
			self.notebook.AddPage( getattr(self, prop), prop[0].upper() + prop[1:-10] )
		
		self.notesLabel = wx.StaticText( self, label = _('Notes to appear on Html output:\n(Notes containing Html tags must start with <html> and end with </html>)') )
		self.notes = wx.TextCtrl( self, style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB, size=(-1,60) )

		self.fileNameLabel = wx.StaticText( self, label = _('File Name: ') )
		self.fileName = wx.StaticText( self )

		self.excelLabel = wx.StaticText( self, label = _('Excel Sheet: ') )
		self.excelName = wx.StaticText( self )

		self.categoriesFileLabel = wx.StaticText( self, label = _('Categories Imported From: ') )
		self.categoriesFile = wx.StaticText( self )

		self.updateFileName()
		
		fgs = wx.FlexGridSizer( rows=rows, cols=2, vgap=2, hgap=2 )
		fgs.AddGrowableCol( 1 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fieldAlign = wx.EXPAND|wx.GROW
		
		blank = lambda : None
		
		labelFieldFormats = [
			(self.raceNameLabel,	0, labelAlign),		(self.raceName, 		1, fieldAlign),
			(self.raceCityLabel,	0, labelAlign),		(self.locationSizer,	1, fieldAlign),
			(self.dateLabel,		0, labelAlign),		(self.date, 			1, fieldAlign),
			(self.raceNumLabel,		0, labelAlign),		(self.raceNum,			1, fieldAlign),
			(self.scheduledStartLabel, 0, labelAlign),	(self.scheduledStart,	1, fieldAlign),
			(self.minutesLabel,		0, labelAlign),		(self.minutes, 			1, fieldAlign),
			(self.raceDisciplineLabel,	0, labelAlign),	(self.raceDiscipline, 	1, fieldAlign),
			(self.organizerLabel,	0, labelAlign),		(self.organizer,		1, fieldAlign),
			(self.commissaireLabel,	0, labelAlign),		(self.commissaire, 		1, fieldAlign),
			(self.memoLabel,		0, labelAlign),		(self.memo, 			1, fieldAlign),
		]

		row = 0
		for i, (item, column, flag) in enumerate(labelFieldFormats):
			if not item:
				continue
			if column == 1:
				flag |= wx.EXPAND
			fgs.Add( item, flag=flag )
			if column == 1:
				row += 1
		
		vs.Add( fgs )
		
		vs.Add( self.notebook, flag=wx.ALL, border=4 )
		vs.Add( self.notesLabel, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=4 )
		vs.Add( self.notes, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		fgs = wx.FlexGridSizer( rows=3, cols=2, vgap=2, hgap=2 )
		fgs.AddGrowableCol( 1 )
		
		fgs.Add( self.excelLabel, flag=wx.ALIGN_RIGHT )
		fgs.Add( self.excelName )
		
		fgs.Add( self.fileNameLabel, flag=wx.ALIGN_RIGHT )
		fgs.Add( self.fileName )
		
		fgs.Add( self.categoriesFileLabel, flag=wx.ALIGN_RIGHT )
		fgs.Add( self.categoriesFile )
		
		vs.Add( fgs )
		
		if addEditButton:
			hs = wx.BoxSizer( wx.HORIZONTAL )
			
			self.commitButton = wx.Button(self, label = _('Commit'))
			self.commitButton.Bind( wx.EVT_BUTTON, self.commitButtonCallback )
			hs.Add( self.commitButton, border = 8, flag = wx.TOP|wx.BOTTOM )
			
			self.excelButton = wx.Button(self, label = _('Link External Excel Sheet...'))
			self.excelButton.Bind( wx.EVT_BUTTON, self.excelButtonCallback )
			hs.Add( self.excelButton, border = 8, flag = wx.LEFT|wx.TOP|wx.BOTTOM )

			vs.Add( hs, flag=wx.ALL, border = 4 )
		
		self.editFields = [labelFieldFormats[i][0] for i in xrange(1, len(labelFieldFormats), 2)] + [
				self.notebook, self.excelName, self.fileName,]
		self.editFields = [e for e in self.editFields if e and not isinstance(e, wx.BoxSizer)]
		self.editFields.extend( [self.raceCity, self.raceStateProv, self.raceCountry] )
		
		self.setEditable( True )
		
	def onJChipIntegration( self, event ):
		self.autocorrectLapsDefault.SetValue( not self.jchip.GetValue() )
	
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
		'''
		for f in self.editFields:
			f.Enable()
			try:
				f.SetEditable( editable )
			except:
				if not editable and not isinstance(f, wx.StaticText):
					f.Disable()
		'''
		if not HasPhotoFinish():
			self.cameraProperties.enableUSBCamera.Disable()
	
	def incNext( self ):
		self.raceNum.SetValue( self.raceNum.GetValue() + 1 )
		self.memo.SetValue( '' )
		if	 self.scheduledStart.GetValue() == '10:00' and self.minutes.GetValue() == 40 and self.raceNum.GetValue() == 2:
			self.scheduledStart.SetValue( '11:30' )
			self.minutes.SetValue( 50 )
		elif self.scheduledStart.GetValue() == '11:30' and self.minutes.GetValue() == 50 and self.raceNum.GetValue() == 3:
			self.scheduledStart.SetValue( '13:00' )
			self.minutes.SetValue( 60 )
		else:
			sStr = '{}'.format(self.scheduledStart.GetValue())
			fields = sStr.split(':')
			if len(fields) == 2:
				mins = int(fields[0],10) * 60 + int(fields[1],10)
				mins += self.minutes.GetValue()
				mins += 15	# Add time for a break.
				if (mins/60) >= 24:
					mins = 0
				sNew = '%02d:%02d:00' % (int(mins/60), mins%60)
				self.scheduledStart.SetValue( sNew )
	
	def onChanged( self, event ):
		self.updateFileName()
	
	def updateFileName( self ):
		rDate = self.date.GetValue().Format(Properties.dateFormat)
		rName = Properties.badFileCharsRE.sub( ' ', self.raceName.GetValue() ).strip()
		rNum = self.raceNum.GetValue()
		rMemo = Properties.badFileCharsRE.sub( ' ', self.memo.GetValue() ).strip()
		fname = '%s-%s-r%d-%s.cmn' % (rDate, rName, rNum, rMemo )
		self.fileName.SetLabel( fname )
	
	def saveFileNameFields( self ):
		for f in ['date', 'raceName', 'raceNum', 'memo']:
			setattr(self, f + 'Original', getattr(self, f).GetValue())
		
	def restoreFileNameFields( self ):
		for f in ['date', 'raceName', 'raceNum', 'memo']:
			getattr(self, f).SetValue( getattr(self, f + 'Original') )
	
	def getFileName( self ):
		self.updateFileName()
		return self.fileName.GetLabel()
	
	def refresh( self ):
		with Model.LockRace() as race:
			self.setEditable( False )
			if race is None:
				return
			self.raceName.SetValue( race.name )
			self.raceCity.SetValue( race.city )
			self.raceStateProv.SetValue( race.stateProv )
			self.raceCountry.SetValue( race.country )
			self.raceDiscipline.SetValue( getattr(race, 'discipline', 'Cyclo-cross') )
			self.organizer.SetValue( getattr(race, 'organizer', '') )
			d = wx.DateTime()
			d.ParseDate(race.date)
			self.date.SetValue( d )
			self.raceNum.SetValue( race.raceNum )
			self.scheduledStart.SetValue( race.scheduledStart )
			
			for prop, PropClass in self.propClass:
				getattr(self, prop).update()
			
			self.notes.SetValue( getattr(race, 'notes', '') )
			
			excelLink = getattr(race, 'excelLink', None)
			if excelLink:
				self.excelName.SetLabel( '%s|%s' % (
					os.path.basename(excelLink.fileName) if excelLink.fileName else '',
					excelLink.sheetName if excelLink.sheetName else '') )
			else:
				self.excelName.SetLabel( '' )
			self.categoriesFile.SetLabel( os.path.basename(getattr(race, 'categoriesImportFile', '')) )
			
			self.saveFileNameFields()
			
		self.GetSizer().Layout()
		
	def update( self, race = None ):
		undo.pushState()
		with Model.lock:
			if race is None:
				race = Model.getRace()
			if race is None:
				return
			race.name = self.raceName.GetValue().strip()
			race.city = self.raceCity.GetValue().strip()
			race.stateProv = self.raceStateProv.GetValue().strip()
			race.country = self.raceCountry.GetValue().strip()
			race.discipline = self.raceDiscipline.GetValue().strip()
			race.organizer = self.organizer.GetValue().strip()
			race.date = self.date.GetValue().Format(Properties.dateFormat)
			race.raceNum = self.raceNum.GetValue()
			race.scheduledStart = self.scheduledStart.GetValue()
			
			for prop, PropClass in self.propClass:
				getattr(self, prop).commit()
			
			race.minutes = self.minutes.GetValue()
			race.commissaire = self.commissaire.GetValue().strip()
			race.memo = self.memo.GetValue().strip()
			race.notes = self.notes.GetValue().strip()
			race.setChanged()
			
		if Utils.getMainWin():
			Utils.getMainWin().record.setTimeTrialInput( race.isTimeTrial )
		
	def commit( self ):
		success = SetNewFilename( self, self )
		self.update()
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
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
			showFileFields = True,
			refreshProperties = False
			):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		pre = wx.PreDialog()
		#pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title = title, pos = pos, size = size, style = style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)

		self.properties = Properties( self, addEditButton = False )
		if refreshProperties:
			self.properties.refresh()
		sizer.Add(self.properties, 0, wx.ALIGN_CENTRE|wx.ALL|wx.GROW, 5)

		if showFileFields:
			gs = wx.FlexGridSizer( rows=2, cols=3, vgap = 5, hgap = 5 )
			gs.Add( wx.StaticText(self, label = _('Race File Folder:')), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			self.folder = wx.TextCtrl( self, value = '', size=(400,-1) )
			self.folder.SetValue( Utils.getDocumentsDir() )
			gs.Add( self.folder, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW)

			btn = wx.Button( self, label=_('Browse...') )
			btn.Bind( wx.EVT_BUTTON, self.onBrowseFolder )
			gs.Add( btn, 0, wx.ALIGN_CENTER_VERTICAL )
			
			gs.Add( wx.StaticText(self, label = _('Categories Import File (*.brc):')), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			self.categoriesFile = wx.TextCtrl( self, value='', size=(400,-1) )
			self.categoriesFile.SetValue( Utils.getDocumentsDir() )
			gs.Add( self.categoriesFile, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW )

			btn = wx.Button( self, label=_('Browse...') )
			btn.Bind( wx.EVT_BUTTON, self.onBrowseCategories )
			gs.Add( btn, 0, wx.ALIGN_CENTER_VERTICAL )
			
			gs.AddGrowableCol( 0, 1 )
			
			sizer.Add( gs, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
			
			line = wx.StaticLine( self, size=(20, -1), style=wx.LI_HORIZONTAL)
			sizer.Add( line, -1, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		
		btnsizer = wx.StdDialogButtonSizer()
        
		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		
		self.helpBtn = wx.Button( self, wx.ID_HELP )
		self.Bind( wx.EVT_BUTTON, lambda evt: Utils.showHelp('Properties.html'), self.helpBtn )
		btnsizer.AddButton(self.helpBtn)
		
		btnsizer.Realize()

		sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.ALIGN_RIGHT, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)
		
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
		if		not mainWin.fileName or \
				Utils.MessageOKCancel(parent, _("The filename will be changed to:\n\n{}\n\nContinue?").format(newBaseName), _("Change Filename?")):
			if os.path.exists(newFName):
				if not Utils.MessageOKCancel(parent, _("This file already exists:\n\n{}\n\nOverwrite?").format(newFName), _("Overwrite Existing File?")):
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
	propertiesDialog = PropertiesDialog( parent, showFileFields = False, refreshProperties = True, size=(600,400) )
	propertiesDialog.properties.setEditable( True )
	try:
		if propertiesDialog.ShowModal() != wx.ID_OK:
			raise NameError('User Cancel')
			
		if not SetNewFilename( propertiesDialog, propertiesDialog.properties ):
			raise NameError('User Cancel')
			
		mainWin = Utils.getMainWin()
		dir = os.path.dirname( mainWin.fileName )
		
		propertiesDialog.properties.update()
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
	properties = Properties(mainWin)
	properties.setEditable( True )
	properties.refresh()
	mainWin.Show()
	propertiesDialog = PropertiesDialog( mainWin, title = _("Properties Dialog Test"), showFileFields=False, refreshProperties=True )
	propertiesDialog.Show()
	app.MainLoop()
