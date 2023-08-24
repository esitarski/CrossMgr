import wx
import os
import math
import datetime
import wx.lib.intctrl

import Model
import Utils
import JChip
from ReadSignOnSheet import GetTagNums
from Undo		import undo
from HighPrecisionTimeEdit import HighPrecisionTimeEdit

def DoChipImport(	fname, parseTagTime, startTime = None,
					clearExistingData = True, timeAdjustment = None ):
	
	errors = []

	race = Model.race
	if race and race.isRunning():
		Utils.MessageOK( Utils.getMainWin(), '\n\n'.join( [_('Cannot Import into a Running Race.'), _('Wait until you have a complete data set, then import the full data into a New race.')] ),
						title = _('Cannot Import into Running Race'), iconMask = wx.ICON_ERROR )
		return

	# If startTime is None, the first time will be taken as the start time.
	# All first time's for each rider will then be ignored.
	
	if timeAdjustment is None:
		timeAdjustment = datetime.timedelta(seconds=0.0)
	
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
				errors.append( '{} {}: {} ({})'.format(_('line'), lineNo, _('time is before race start'), t.strftime('%H:%M:%S.%f')) )
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
					errors.append( '{} {}: {}: {}'.format(_('line'), lineNo, _('tag missing from Excel sheet'), tag) )
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
		
		for num, lapTimes in riderRaceTimes.items():
			for t in lapTimes:
				raceTime = (t - raceStart).total_seconds()
				if not race.hasTime(num, raceTime):
					race.addTime( num, raceTime )
			
		if tLast:
			race.finishTime = tLast + datetime.timedelta( seconds = 0.0001 )
			
		# Figure out the race minutes from the recorded laps.
		if riderRaceTimes:
			lapNumMax = max( len(ts) for ts in riderRaceTimes.values() )
			if lapNumMax > 0:
				tElapsed = min( ts[-1] for ts in riderRaceTimes.values() if len(ts) == lapNumMax )
				raceMinutes = int((tElapsed - raceStart).total_seconds() / 60.0) + 1
				race.minutes = raceMinutes
		
	return errors

#------------------------------------------------------------------------------------------------
class ChipImportDialog( wx.Dialog ):
	def __init__( self, chipName, parseTagTime, parent, id = wx.ID_ANY, fileSuffix = 'txt' ):
		super().__init__( parent, id, '{} {}'.format(chipName, _('Import')),
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
		
		self.chipName = chipName
		self.parseTagTime = parseTagTime
		self.fileSuffix = fileSuffix
		todoList = [
			'{} {}'.format(chipName, _('Import Data File')),
			'',
			_('You must first "New" a race and fill in the details.'),
			_('You must also configure a "Tag" field in your Sign-On Excel Sheet and link the sheet to the race.'),
			_('This is required so CrossMgr can link the tags in the import file back to rider numbers and info.'),
			'',
			_('Race Data:'),
			_('If the first chip read is NOT the start of the race, you will need to enter the start time manually.'),
			_('Otherwise the import will use the first chip read as the race start.'),
			'',
			_('TimeTrial Data:'),
			_("The first chip read for each rider will be interpreted as the rider's start time."),
			'',
			_('Warning: Importing from chip data could replace all the data in this race.'),
			_('Proceed with caution.'),
		]
		intro = '\n'.join(todoList)
		
		gs = wx.FlexGridSizer( rows=0, cols=3, vgap=10, hgap=5 )
		gs.Add( wx.StaticText(self, label = '{} {}:'.format(chipName, _('Data File'))), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.chipDataFile = wx.TextCtrl( self, -1, '', size=(450,-1) )
		defaultPath = Utils.getFileName()
		if not defaultPath:
			defaultPath = Utils.getDocumentsDir()
		else:
			defaultPath = os.path.join( os.path.split(defaultPath)[0], '' )
		self.chipDataFile.SetValue( defaultPath )
		gs.Add( self.chipDataFile, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW)

		btn = wx.Button( self, label=_('Browse') + '...' )
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
		self.timeAdjustment = HighPrecisionTimeEdit( self, size=(120,-1) )
		self.behindAhead = wx.Choice( self, choices=[_('Behind'), _('Ahead')] )
		self.behindAhead.SetSelection( 0 )
		self.timeAdjustment.SetSeconds( 0.0 )
		hb = wx.BoxSizer()
		hb.Add( self.behindAhead, flag=wx.ALIGN_BOTTOM|wx.BOTTOM, border=4 )
		hb.Add( self.timeAdjustment, flag=wx.ALL, border=4 )
		gs.Add( hb, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT )
		gs.AddSpacer(1)
		
		self.manualStartTime = wx.CheckBox(self, label = _('Race Start Time (if NOT first recorded time):') )
		self.Bind( wx.EVT_CHECKBOX, self.onChangeManualStartTime, self.manualStartTime )
		gs.Add( self.manualStartTime, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.raceStartTime = HighPrecisionTimeEdit( self, seconds=10*60*60 )
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
			
		bs = wx.BoxSizer( wx.VERTICAL )
		
		border = 4
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		
		try:
			image = wx.Image( os.path.join(Utils.getImageFolder(), '{}Logo.png'.format(chipName)), wx.BITMAP_TYPE_PNG )
		except Exception as e:
			image = wx.EmptyImage( 32, 32, True )
		hs.Add( wx.StaticBitmap(self, wx.ID_ANY, image.ConvertToBitmap()), 0 )
		hs.Add( wx.StaticText(self, label = intro), 1, wx.EXPAND|wx.LEFT, border*2 )
		
		bs.Add( hs, 1, wx.EXPAND|wx.ALL, border )
		
		#-------------------------------------------------------------------
		bs.AddSpacer( border )
		
		bs.Add( gs, 0, wx.EXPAND | wx.ALL, border )
		
		btnSizer = self.CreateStdDialogButtonSizer( wx.OK|wx.CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onOK, id=wx.ID_OK )
		if btnSizer:
			bs.Add( btnSizer, 0, wx.EXPAND | wx.ALL, border )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		wx.CallAfter( self.SetFocus )

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
			
		with wx.FileDialog( self, '{} {}'.format( self.chipName, _('Import file') ),
							style=wx.FD_OPEN | wx.FD_CHANGE_DIR,
							wildcard='RFID (*.{})|*.{}'.format(self.fileSuffix, self.fileSuffix),
							defaultDir=defaultPath if defaultPath else '',
							defaultFile=defaultFile if defaultFile else '',
							) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.chipDataFile.SetValue( dlg.GetPath() )
	
	def onOK( self, event ):
		fname = self.chipDataFile.GetValue()
		try:
			with open( fname ):
				pass
		except IOError:
			Utils.MessageOK( self, '{}:\n\n"{}"'.format(_('Could not open data file for import'), fname),
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
					'\n\n'.join( [_('Cannot Merge into Unstarted Race.'), _('Clear All Existing Data is allowed.')] ),
					title = _('Import Merge Failed'), iconMask = wx.ICON_ERROR
				)
				return
			startTime = Model.race.startTime.time()
		else:
			if self.manualStartTime.IsChecked():
				startSeconds = self.raceStartTime.GetSeconds()
				fraction, seconds = math.modf( startSeconds )
				seconds = int(seconds)
				startTime = datetime.time( (seconds//(60*60))%24, (seconds//60)%60, seconds%60, int(fraction*1000000) )
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
							'{}:\n\n{}\n\n{}.'.format(_('Import File contains errors'), tagStr, _('All errors have been copied to the clipboard')),
							_('Import Warning'),
							iconMask = wx.ICON_WARNING )
		else:
			Utils.MessageOK( self, _('Import Successful'), _('Import Successful') )
		wx.CallAfter( Utils.refresh )
		self.EndModal( wx.ID_OK )
