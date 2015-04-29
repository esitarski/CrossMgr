import wx
import wx.lib.intctrl
import wx.lib.masked			as masked
import os
import datetime

import Model
import Utils
import JChip
from JChipSetup import GetTagNums
from Undo		import undo
from HighPrecisionTimeEdit import HighPrecisionTimeEdit

def DoChipImport(	fname, parseTagTime, startTime = None,
					clearExistingData = True, timeAdjustment = None ):
	
	race = Model.race
	if race and race.isRunning():
		Utils.MessageOK( Utils.getMainWin(), u'\n\n'.join( [_('Cannot Import into a Running Race.'), _('Wait until you have a complete data set, then import the full data into a New race.')] ),
						title = _('Cannot Import into Running Race'), iconMask = wx.ICON_ERROR )
		return
	
	# If startTime is None, the first time will be taken as the start time.
	# All first time's for each rider will then be ignored.
	
	if timeAdjustment is None:
		timeAdjustment = datetime.timedelta(seconds=0.0)
	
	errors = []
	raceStart = None
	
	with open(fname) as f, Model.LockRace() as race:
		year, month, day = [int(n) for n in race.date.split('-')]
		raceDate = datetime.date( year=year, month=month, day=day )
		JChip.reset( raceDate )
		if startTime:
			raceStart = datetime.datetime.combine( raceDate, startTime )
			race.resetStartClockOnFirstTag = False
		else:
			race.resetStartClockOnFirstTag = True
		
		tagNums = GetTagNums( True )
		race.missingTags = set()
		
		tFirst, tLast = None, None
		lineNo = 0
		riderRaceTimes = {}
		for line in f:
			lineNo += 1
			
			line = line.strip()
			if not line or line[0] in '#;':
				continue
			
			tag, t = parseTagTime( line, lineNo, errors )
			if tag is None:
				continue
			if raceStart and t < raceStart:
				errors.append( u'{} {}: {} ({})'.format(_('line'), lineNo, _('time is before race start'), t.strftime('%H:%M:%S.%f')) )
				continue
			
			tag = tag.lstrip('0').upper()
			t += timeAdjustment
			
			if not tFirst:
				tFirst = t
			tLast = t
			try:
				num = tagNums[tag]
				riderRaceTimes.setdefault( num, [] ).append( t )
			except KeyError:
				if tag not in race.missingTags:
					errors.append( u'{} {}: {}: {}'.format(_('line'), lineNo, _('tag missing from Excel sheet'), tag) )
					race.missingTags.add( tag )
				continue

		#------------------------------------------------------------------------------
		# Populate the race with the times.
		if not riderRaceTimes:
			errors.insert( 0, _('No matching tags found in Excel link.  Import aborted.') )
			return errors
		
		# Put all the rider times into the race.
		if clearExistingData:
			race.clearAllRiderTimes()
			
		if not raceStart:
			raceStart = tFirst
			
		race.startTime = raceStart
		
		for num, lapTimes in riderRaceTimes.iteritems():
			for t in lapTimes:
				raceTime = (t - raceStart).total_seconds()
				if not race.hasTime(num, raceTime):
					race.addTime( num, raceTime )
			
		if tLast:
			race.finishTime = tLast + datetime.timedelta( seconds = 0.0001 )
			
		# Figure out the race minutes from the recorded laps.
		if riderRaceTimes:
			lapNumMax = max( len(ts) for ts in riderRaceTimes.itervalues() )
			if lapNumMax > 0:
				tElapsed = min( ts[-1] for ts in riderRaceTimes.itervalues() if len(ts) == lapNumMax )
				raceMinutes = int((tElapsed - raceStart).total_seconds() / 60.0) + 1
				race.minutes = raceMinutes
		
	return errors

#------------------------------------------------------------------------------------------------
class ChipImportDialog( wx.Dialog ):
	def __init__( self, chipName, parseTagTime, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, u'{} {}'.format(chipName, _('Import')),
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
		
		self.chipName = chipName
		self.parseTagTime = parseTagTime
		todoList = [
			u'{} {}'.format(chipName, _('Import Data File')),
			u'',
			_('You must first "New" a race and fill in the details.'),
			_('You must also configure a "Tag" field in your Sign-On Excel Sheet and link it to the race.'),
			_('This is required so CrossMgr can link the tags in the import file back to rider numbers and info.'),
			u'',
			_('Race Data:'),
			_('If the first chip read is NOT the start of the race, you will need to enter the start time manually.'),
			_('Otherwise the import will use the first chip read as the race start.'),
			u'',
			_('TimeTrial Data:'),
			_("The first chip read for each rider will be interpreted as the rider's start time."),
			u'',
			_('Warning: Importing from chip data will replace all the data in this race.'),
			_('Proceed with caution.'),
		]
		intro = u'\n'.join(todoList)
		
		gs = wx.FlexGridSizer( rows=0, cols=3, vgap=10, hgap=5 )
		gs.Add( wx.StaticText(self, label = u'{} {}:'.format(chipName, _('Data File'))), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.chipDataFile = wx.TextCtrl( self, -1, '', size=(450,-1) )
		defaultPath = Utils.getFileName()
		if not defaultPath:
			defaultPath = Utils.getDocumentsDir()
		else:
			defaultPath = os.path.join( os.path.split(defaultPath)[0], '' )
		self.chipDataFile.SetValue( defaultPath )
		gs.Add( self.chipDataFile, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW)

		btn = wx.Button( self, label=_('Browse') + u'...' )
		btn.Bind( wx.EVT_BUTTON, self.onBrowseChipReaderDataFile )
		gs.Add( btn, 0, wx.ALIGN_CENTER_VERTICAL )
		
		gs.AddSpacer(1)
		self.dataType = wx.StaticText( self, label = _("Data Is:") )
		gs.Add( self.dataType, 1, wx.ALIGN_LEFT )
		gs.AddSpacer(1)

		gs.Add( wx.StaticText(self, label = _('Data Policy:') ), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.importPolicy = wx.Choice( self, choices = [
				_('Clear All Existing Data Before Import'),
				_('Merge New Data with Existing')
			] )
		self.importPolicy.SetSelection( 0 )
		gs.Add( self.importPolicy, 1, wx.ALIGN_LEFT )
		gs.AddSpacer(1)
        
		gs.Add( wx.StaticText(self, label = _('Import Data Time Adjustment:') ), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.timeAdjustment = HighPrecisionTimeEdit( self )
		self.behindAhead = wx.Choice( self, choices=[_('Behind'), _('Ahead')] )
		if JChip.readerComputerTimeDiff:
			rtAdjust = JChip.readerComputerTimeDiff.total_seconds()
			if rtAdjust >= 0.0:
				self.behindAhead.SetSelection( 0 )
			else:
				self.behindAhead.SetSelection( 1 )
				rtAdjust *= -1.0
			self.timeAdjustment.SetSeconds( rtAdjust )
		else:
			self.behindAhead.SetSelection( 0 )
		hb = wx.BoxSizer()
		hb.Add( self.behindAhead, flag=wx.ALIGN_BOTTOM|wx.BOTTOM, border=4 )
		hb.Add( self.timeAdjustment, flag=wx.ALL, border=4 )
		gs.Add( hb, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT )
		gs.AddSpacer(1)
		
		self.manualStartTime = wx.CheckBox(self, label = _('Race Start Time (if NOT first recorded time):') )
		self.Bind( wx.EVT_CHECKBOX, self.onChangeManualStartTime, self.manualStartTime )
		gs.Add( self.manualStartTime, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.raceStartTime = masked.TimeCtrl( self, fmt24hr=True, value="10:00:00" )
		self.raceStartTime.Enable( False )
		gs.Add( self.raceStartTime, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
		gs.AddSpacer(1)
		
		with Model.LockRace() as race:
			isTimeTrial = getattr(race, 'isTimeTrial', False) if race else False

		if isTimeTrial:
			self.manualStartTime.Enable( False )
			self.manualStartTime.Show( False )
			self.raceStartTime.Enable( False )
			self.raceStartTime.Show( False )
			self.dataType.SetLabel( _('Data will be imported for a Time Trial') )
		else:
			self.dataType.SetLabel( _('Data will be imported for a Race') )
			
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		bs = wx.BoxSizer( wx.VERTICAL )
		
		border = 4
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		
		try:
			image = wx.Image( os.path.join(Utils.getImageFolder(), '%sLogo.png' % chipName), wx.BITMAP_TYPE_PNG )
		except Exception as e:
			image = wx.EmptyImage( 32, 32, True )
		hs.Add( wx.StaticBitmap(self, bitmap = image.ConvertToBitmap(8)), 0 )
		hs.Add( wx.StaticText(self, label = intro), 1, wx.EXPAND|wx.LEFT, border*2 )
		
		bs.Add( hs, 1, wx.EXPAND|wx.ALL, border )
		
		#-------------------------------------------------------------------
		bs.AddSpacer( border )
		
		bs.Add( gs, 0, wx.EXPAND | wx.ALL, border )
		
		buttonBox = wx.BoxSizer( wx.HORIZONTAL )
		buttonBox.AddStretchSpacer()
		buttonBox.Add( self.okBtn, flag = wx.RIGHT, border = border )
		self.okBtn.SetDefault()
		buttonBox.Add( self.cancelBtn )
		bs.Add( buttonBox, 0, wx.EXPAND | wx.ALL, border )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onChangeManualStartTime( self, event ):
		self.raceStartTime.Enable( event.IsChecked() )
		
	def onBrowseChipReaderDataFile( self, event ):
		defaultPath = self.chipDataFile.GetValue()
		if not defaultPath:
			defaultPath = Utils.getFileName()
			if defaultPath:
				defaultPath = os.path.split(defaultPath)[0]
			else:
				defaultPath = Utils.getDocumentsDir()
			defaultFile = ''
		else:
			defaultPath, defaultFile = os.path.split(defaultPath)
			
		dlg = wx.FileDialog( self, u"{} {}".format( self.chipName, _('Import file') ),
							style=wx.OPEN | wx.CHANGE_DIR,
							wildcard="RFID (*.txt)|*.txt",
							defaultDir=defaultPath if defaultPath else '',
							defaultFile=defaultFile if defaultFile else '',
							)
		if dlg.ShowModal() == wx.ID_OK:
			self.chipDataFile.SetValue( dlg.GetPath() )
		dlg.Destroy()
	
	def onOK( self, event ):
		fname = self.chipDataFile.GetValue()
		try:
			with open(fname) as f:
				pass
		except IOError:
			Utils.MessageOK( self, u'{}:\n\n"{}"'.format(_('Could not open data file for import'), fname),
									title = _('Cannot Open File'), iconMask = wx.ICON_ERROR)
			return
			
		clearExistingData = (self.importPolicy.GetSelection() == 0)
		timeAdjustment = self.timeAdjustment.GetSeconds()
		if self.behindAhead.GetSelection() == 1:
			timeAdjustment *= -1
		
		# Get the start time.
		if not clearExistingData:
			if not Model.race or not Model.race.startTime:
				Utils.MessageOK( self,
					u'\n\n'.join( [_('Cannot Merge into Unstarted Race.'), _('Clear All Existing Data is allowed.')] ),
					title = _('Import Merge Failed'), iconMask = wx.ICON_ERROR
				)
				return
			startTime = Model.race.startTime.time()
		else:
			if self.manualStartTime.IsChecked():
				startTime = datetime.time(*[int(x) for x in self.raceStartTime.GetValue().split(':')])
			else:
				startTime = None
			
		undo.pushState()
		errors = DoChipImport(	fname, self.parseTagTime, startTime,
								clearExistingData,
								datetime.timedelta(seconds = timeAdjustment) )
		
		if errors:
			# Copy the tags to the clipboard.
			clipboard = wx.Clipboard.Get()
			if not clipboard.IsOpened():
				clipboard.Open()
				clipboard.SetData( wx.TextDataObject('\n'.join(errors)) )
				clipboard.Close()
			
			if len(errors) > 10:
				errors = errors[:10]
				errors.append( '...' )
			tagStr = '\n'.join(errors)
			Utils.MessageOK( self,
							u'{}:\n\n{}\n\n{}.'.format(_('Import File contains errors'), tagStr, _('All errors have been copied to the clipboard')),
							_('Import Warning'),
							iconMask = wx.ICON_WARNING )
		else:
			Utils.MessageOK( self, _('Import Successful'), _('Import Successful') )
		wx.CallAfter( Utils.refresh )
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
