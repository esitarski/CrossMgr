import bisect
import datetime
import os
import sys
from typing import cast

import wx

import Model
import Utils
from BibTimeRecord import BibTimeRecord
from ClockDigital import ClockDigital
from GetResults import GetResultsWithData, GetLastRider
from LapsToGoCount import LapsToGoCountGraph
from Log import getLogger
from ManualTimeEntryPanel import TimeEntryController, ManualTimeEntryPanel
from NonBusyCall import NonBusyCall
from Keypad import Keypad, getLapInfo, SplitterMinPos
from RaceHUD import RaceHUD
from SetLaps import SetLaps
from TimeTrialRecord import TimeTrialRecord
from Utils import SetLabel


class Record(wx.Panel, TimeEntryController):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__(parent, id)

		self.bell = None
		self.lapReminder = {}

		self.SetBackgroundColour( wx.WHITE )

		self.refreshInputUpdateNonBusy = NonBusyCall( self.refreshInputUpdate, min_millis=1000, max_millis=3000 )

		fontPixels = 50
		font = wx.Font((0,fontPixels), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

		verticalMainSizer = wx.BoxSizer( wx.VERTICAL )
		horizontalMainSizer = wx.BoxSizer( wx.HORIZONTAL )

		splitter = wx.SplitterWindow( self, wx.ID_ANY, style = wx.SP_3DSASH )
		splitter.Bind( wx.EVT_PAINT, self.onPaint )

		panel = wx.Panel( splitter, style=wx.BORDER_SUNKEN )
		panel.SetSizer( horizontalMainSizer )
		panel.SetBackgroundColour( wx.WHITE )

		#-------------------------------------------------------------------------------
		# Create the edit field, numeric keypad and buttons.
		self.notebook = wx.Notebook( panel, style=wx.NB_BOTTOM )
		self.notebook.SetBackgroundColour( wx.WHITE )

		self.keypad = Keypad( self.notebook, self )
		self.timeTrialRecord = TimeTrialRecord( self.notebook )
		self.bibTimeRecord = BibTimeRecord( self.notebook, controller=cast(ManualTimeEntryPanel, self) )

		self.notebook.AddPage( self.keypad, _("Bib"), select=True )
		self.notebook.AddPage( self.timeTrialRecord, _("TimeTrial") )
		self.notebook.AddPage( self.bibTimeRecord, _("BibTime") )
		self.notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged )
		horizontalMainSizer.Add( self.notebook, 0, flag=wx.TOP|wx.LEFT|wx.EXPAND, border = 4 )

		self.horizontalMainSizer = horizontalMainSizer

		#------------------------------------------------------------------------------
		# Race time.
		#
		self.raceTime = wx.StaticText( panel, label = '00:00', size=(-1,64))
		self.raceTime.SetFont( font )
		self.raceTime.SetDoubleBuffered( True )

		verticalSubSizer = wx.BoxSizer( wx.VERTICAL )
		horizontalMainSizer.Add( verticalSubSizer )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.raceTime, flag=wx.LEFT, border=100-40-8 )
		verticalSubSizer.Add( hs, flag=wx.ALIGN_LEFT | wx.ALL, border = 2 )

		#------------------------------------------------------------------------------
		# Lap Management.
		#
		gbs = wx.GridBagSizer(4, 12)
		gbs.SetMinSize( 256, 200 )

		fontSize = 12
		font = wx.Font(fontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		fontBold = wx.Font(fontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

		rowCur = 0
		colCur = 0

		panel.SetMinSize( (256, 60) )

		line = wx.StaticLine( panel, style=wx.LI_HORIZONTAL )
		gbs.Add( line, pos=(rowCur, 0), span=(1,2), flag=wx.EXPAND )
		rowCur += 1

		label = wx.StaticText( panel, label = _("Manual Start") )
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=wx.EXPAND|wx.ALL, border=3 )
		rowCur += 1

		self.raceStartMessage = label
		self.raceStartTime = wx.StaticText( panel, label='00:00:00.000' )
		self.raceStartTime.SetFont( font )
		gbs.Add( self.raceStartTime, pos=(rowCur, colCur), span=(1, 1), flag=wx.EXPAND|wx.ALL, border=3 )
		rowCur += 1

		line = wx.StaticLine( panel, style=wx.LI_HORIZONTAL )
		gbs.Add( line, pos=(rowCur, 0), span=(1,2), flag=wx.EXPAND|wx.ALL, border=2 )
		rowCur += 1

		label = wx.StaticText( panel, label = '{}:'.format(_("Last Rider")) )
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,2), flag=wx.EXPAND|wx.ALL, border=3 )
		rowCur += 1
		self.lastRiderOnCourseTime = wx.StaticText( panel, label='00:00:00' )
		self.lastRiderOnCourseTime.SetFont( font )
		gbs.Add( self.lastRiderOnCourseTime, pos=(rowCur, colCur), span=(1, 2), flag=wx.EXPAND|wx.ALL, border=3 )
		rowCur += 1
		self.lastRiderOnCourseName = wx.StaticText( panel )
		self.lastRiderOnCourseName.SetFont( fontBold )
		gbs.Add( self.lastRiderOnCourseName, pos=(rowCur, colCur), span=(1, 2), flag=wx.EXPAND|wx.ALL, border=3 )
		rowCur += 1
		self.lastRiderOnCourseTeam = wx.StaticText( panel )
		self.lastRiderOnCourseTeam.SetFont( font )
		gbs.Add( self.lastRiderOnCourseTeam, pos=(rowCur, colCur), span=(1, 2), flag=wx.EXPAND|wx.ALL, border=3 )
		rowCur += 1
		self.lastRiderOnCourseCategory = wx.StaticText( panel )
		self.lastRiderOnCourseCategory.SetFont( font )
		gbs.Add( self.lastRiderOnCourseCategory, pos=(rowCur, colCur), span=(1, 2), flag=wx.EXPAND|wx.ALL, border=3 )
		rowCur += 1

		line = wx.StaticLine( panel, style=wx.LI_HORIZONTAL )
		gbs.Add( line, pos=(rowCur, 0), span=(1,2), flag=wx.EXPAND|wx.ALL, border=2 )
		rowCur += 1

		self.hbClockPhoto = wx.BoxSizer( wx.HORIZONTAL )

		self.photoCount = wx.StaticText( panel, label = "000000", size=(64,-1) )
		self.photoCount.SetFont( font )
		self.hbClockPhoto.Add( self.photoCount, flag=wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT, border = 6 )

		self.camera_bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'camera.png'), wx.BITMAP_TYPE_PNG )
		self.camera_broken_bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'camera_broken.png'), wx.BITMAP_TYPE_PNG )

		self.photoBitmap = wx.StaticBitmap( panel, bitmap = self.camera_bitmap )
		self.hbClockPhoto.Add( self.photoBitmap, flag=wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT, border = 18 )

		gbs.Add( self.hbClockPhoto, pos=(rowCur, colCur), span=(1,1) )
		rowCur += 1

		self.clock = ClockDigital( panel, size=(100,24), checkFunc=self.doClockUpdate )
		self.clock.SetBackgroundColour( wx.WHITE )
		gbs.Add( self.clock, pos=(rowCur, 0), span=(1, 2), flag=wx.ALIGN_CENTRE )
		rowCur += 1

		verticalSubSizer.Add( gbs, 0, flag=wx.LEFT|wx.TOP|wx.EXPAND, border = 3 )
		self.sizerLapInfo = gbs
		self.sizerSubVertical = verticalSubSizer

		#------------------------------------------------------------------------------
		# Rider Lap Count.
		rcVertical = wx.BoxSizer( wx.VERTICAL )
		self.lapsToGoCountGraph = LapsToGoCountGraph( panel )
		rcVertical.Add( self.lapsToGoCountGraph, 1, flag=wx.EXPAND|wx.TOP|wx.RIGHT, border = 4 )

		horizontalMainSizer.Add( rcVertical, 1, flag=wx.EXPAND|wx.LEFT, border = 4 )
		self.horizontalMainSizer = horizontalMainSizer

		#----------------------------------------------------------------------------------------------
		self.raceHUD = RaceHUD( splitter, wx.ID_ANY, style=wx.BORDER_SUNKEN,
			lapInfoFunc=getLapInfo,
			leftClickFunc=self.doLeftClickHUD,
			rightClickFunc=self.doLeftClickHUD,
		)

		splitter.SetMinimumPaneSize( 20 )
		splitter.SplitHorizontally( panel, self.raceHUD, -100 )
		verticalMainSizer.Add( splitter, 1, flag=wx.EXPAND )

		self.SetSizer( verticalMainSizer )
		self.isEnabled = True

		self.splitter = splitter
		self.firstTimeDraw = True

		self.refreshRaceTime()

	def doLeftClickHUD( self, iWave ):
		race = Model.race
		if not race:
			return
		try:
			category = race.getCategories()[iWave]
		except IndexError:
			return

		with SetLaps( self, category=category ) as setLaps:
			setLaps.ShowModal()

	def doClockUpdate( self ):
		mainWin = Utils.getMainWin()
		return not mainWin or mainWin.isShowingPage(self)

	def isKeypadInputMode( self ):
		return self.notebook.GetSelection() == 0

	def isTimeTrialInputMode( self ):
		return self.notebook.GetSelection() == 1

	def isBibTimeInputMode( self ):
		return self.notebook.GetSelection() == 2

	def setTimeTrialInput( self, isTimeTrial=True ):
		page = 1 if isTimeTrial else 0
		if self.notebook.GetSelection() != page:
			self.notebook.SetSelection( page )
			self.timeTrialRecord.refresh()

	def onPageChanged( self, event ):
		if self.isBibTimeInputMode():
			self.bibTimeRecord.refresh()

	def swapKeypadTimeTrialRecord( self ):
		self.notebook.SetSelection( 1 - self.notebook.GetSelection() )

	def refreshRaceHUD( self ):
		race = Model.race
		if not race or race.isTimeTrial:
			self.raceHUD.SetData()
			if Utils.mainWin:
				Utils.mainWin.updateLapCounter()
			return

		categories = race.getCategories( startWaveOnly=True )
		noLap = ''
		tCur = race.curRaceTime() if race.isRunning() else None

		def getNoDataCategoryLap( category ):
			offset = race.categoryStartOffset(category)
			tLapStart = offset if tCur and tCur >= offset else None
			cn = race.getNumLapsFromCategory( category )
			if cn and tCur and tCur > offset + 30.0:
				cn -= 1
			return ('{}'.format(cn) if cn else noLap, False, tLapStart)

		lapCounter = [getNoDataCategoryLap(category) for category in categories]
		categoryToLapCounterIndex = {category:i for i, category in enumerate(categories)}

		if tCur is None or not categories:
			self.raceHUD.SetData()
			if Utils.mainWin:
				Utils.mainWin.updateLapCounter(lapCounter)
			return

		Finisher = Model.Rider.Finisher
		leaderCategory = categories[0]

		secondsBeforeLeaderToFlipLapCounter = race.secondsBeforeLeaderToFlipLapCounter + 1.0

		def setLapCounter( leaderCategory, category, lapCur, lapMax, tLeaderArrival=sys.float_info.max, tLapStart=None ):
			if not category:
				return
			if not (category == leaderCategory or race.getNumLapsFromCategory(category)):
				return

			lapsToGo = max( 0, lapMax - lapCur )
			if secondsBeforeLeaderToFlipLapCounter < tLeaderArrival <= secondsBeforeLeaderToFlipLapCounter+5.0:
				v = ('{}'.format(lapsToGo), True, tLapStart)				# Flash current lap (about to be flipped).
			elif 0.0 <= tLeaderArrival <= secondsBeforeLeaderToFlipLapCounter:
				v = ('{}'.format(max(0,lapsToGo-1)), False, tLapStart)		# Flip lap counter before leader.
			else:
				v = ('{}'.format(lapsToGo), False, tLapStart)				# Show current lap.

			try:
				lapCounter[categoryToLapCounterIndex[category]] = v
			except (KeyError, IndexError):
				pass

		leader, raceTimes, earlyBellTime = [], [], []
		for category in categories:
			results = GetResultsWithData( category )
			if not results or not results[0].status == Finisher or not results[0].raceTimes:
				leader.append( category.fullname )
				raceTimes.append( [] )
				continue

			earlyBellTime.append( category.earlyBellTime )
			leader.append( '{} [{}]'.format(category.fullname, results[0].num) )
			for rank, rr in enumerate(results, 1):
				if rr.status != Finisher or not rr.raceTimes or len(rr.raceTimes) < 2:
					break

				if rank > 1:
					catRaceTimes = raceTimes[-1]
					if rank <= 10:
						# Update the fastest lap times, which may not be the current leader's time.
						for i, t in enumerate(rr.raceTimes):
							if t < catRaceTimes[i]:
								catRaceTimes[i] = t

					# Update the last rider finish time.
					if rr.raceTimes[-1] > catRaceTimes[-1]:
						catRaceTimes[-1] = rr.raceTimes[-1]
					continue

				# Add a copy of the race times.  Set the leader's last time as the current last rider finish.
				raceTimes.append( rr.raceTimes + [rr.raceTimes[-1]] )

				# Find the next expected lap arrival.
				try:
					lapCur = bisect.bisect_left( rr.raceTimes, tCur )
					# Time before leader's arrival.
					tLeaderArrival = rr.raceTimes[lapCur] - tCur
				except IndexError:
					# At the end of the race, use the leader's race time.
					# Make sure it is a recorded time, not a projected time.
					try:
						tLapStart = rr.raceTimes[-2] if rr.interp[-1] else rr.raceTimes[-1]
					except Exception:
						tLapStart = None

					setLapCounter(
						leaderCategory, category, len(rr.raceTimes)-1, len(rr.raceTimes)-1,
						tLapStart = tLapStart
					)
					continue

				if lapCur <= 1:
					tLapStart = race.categoryStartOffset(category)
				else:
					lapPrev = lapCur-1
					# Make sure we use an actual recorded time - not a projected time.
					# A projected time is possible if the leader has a slow lap.
					if rr.interp[lapPrev]:
						lapPrev -= 1
					try:
						tLapStart = rr.raceTimes[lapPrev] if lapPrev else race.categoryStartOffset(category)
					except IndexError:
						tLapStart = None

				setLapCounter( leaderCategory, category, lapCur, len(rr.raceTimes), tLeaderArrival, tLapStart )

				if tLeaderArrival is not None:
					if 0.0 <= tLeaderArrival <= 3.0:
						if category not in self.lapReminder:
							self.lapReminder[category] = Utils.PlaySound( 'reminder.wav' )
					elif category in self.lapReminder:
						del self.lapReminder[category]

		# Ensure that the raceTime and leader are sorted the same as the Categories are defined.
		self.raceHUD.SetData( raceTimes, leader, tCur if race.isRunning() else None, earlyBellTime )
		if Utils.mainWin:
			Utils.mainWin.updateLapCounter( lapCounter )
		self.updateLayout()

	def updateLayout( self ):
		self.sizerLapInfo.Layout()
		self.sizerSubVertical.Layout()
		self.horizontalMainSizer.Layout()
		self.Layout()

	def refreshRaceTime( self ):
		race = Model.race

		if race is not None:
			tRace = race.lastRaceTime()
			tStr = Utils.formatTime( tRace )
			if tStr.startswith('0'):
				tStr = tStr[1:]
			self.refreshRaceHUD()
			if race.enableUSBCamera:
				self.photoBitmap.Show( True )
				self.photoCount.SetLabel( '{}'.format(race.photoCount) )
				self.photoBitmap.SetBitmap( self.camera_broken_bitmap if Utils.cameraError else self.camera_bitmap )
			else:
				self.photoBitmap.Show( False )
				self.photoCount.SetLabel( '' )
		else:
			tStr = ''
			tRace = None
			self.photoBitmap.Show( False )
			self.photoCount.SetLabel( '' )
		self.raceTime.SetLabel( '  ' + tStr )

		self.hbClockPhoto.Layout()

		mainWin = Utils.mainWin
		if mainWin is not None:
			try:
				mainWin.refreshRaceAnimation()
			except Exception:
				pass

	raceMessage = { 0:_("Finishers Arriving"), 1:_("Ring Bell"), 2:_("Prepare Bell") }

	def refreshLaps( self ):
		wx.CallAfter( self.refreshRaceHUD )

	def refreshRiderCategoryStatsList( self ):
		self.lapsToGoCountGraph.Refresh()

	def refreshLastRiderOnCourse( self ):
		race = Model.race
		lastRiderOnCourse = GetLastRider( None )
		changed = False

		if lastRiderOnCourse:
			maxLength = 24
			rider = race.riders[lastRiderOnCourse.num]
			short_name = lastRiderOnCourse.short_name(maxLength)
			if short_name:
				lastRiderOnCourseName = '{}: {}'.format(lastRiderOnCourse.num, lastRiderOnCourse.short_name())
			else:
				lastRiderOnCourseName = '{}'.format(lastRiderOnCourse.num)

			lastRiderOnCourseTeam = '{}'.format( getattr(lastRiderOnCourse, 'Team', '') )
			if len(lastRiderOnCourseTeam) > maxLength:
				lastRiderOnCourseTeam = lastRiderOnCourseTeam[:maxLength].strip() + '...'

			category = race.getCategory( lastRiderOnCourse.num )
			lastRiderOnCourseCategory = category.fullname

			t = (lastRiderOnCourse._lastTimeOrig or 0.0) + ((rider.firstTime or 0.0) if race.isTimeTrial else 0.0)
			tFinish = race.startTime + datetime.timedelta( seconds=t )
			lastRiderOnCourseTime = '{} {}'.format(_('Finishing'), tFinish.strftime('%H:%M:%S') )
		else:
			lastRiderOnCourseName = ''
			lastRiderOnCourseTeam = ''
			lastRiderOnCourseCategory = ''
			lastRiderOnCourseTime = ''
		changed |= SetLabel( self.lastRiderOnCourseName, lastRiderOnCourseName )
		changed |= SetLabel( self.lastRiderOnCourseTeam, lastRiderOnCourseTeam )
		changed |= SetLabel( self.lastRiderOnCourseCategory, lastRiderOnCourseCategory )
		changed |= SetLabel( self.lastRiderOnCourseTime, lastRiderOnCourseTime )
		if changed:
			self.updateLayout()

	def refreshAll( self ):
		self.refreshRaceTime()
		self.refreshLaps()

	def commit( self ):
		pass

	def onPaint( self, event ):
		if self.firstTimeDraw:
			self.firstTimeDraw = False
			self.splitter.SetSashPosition( SplitterMinPos )
		event.Skip()

	def refreshInputUpdate( self ):
		self.refreshLaps()
		self.refreshRiderCategoryStatsList()
		self.refreshLastRiderOnCourse()

	def refresh( self ):
		self.clock.Start()

		race = Model.race
		if race is None:
			enable = False
			disableReason = 'No race is open.'
		elif not race.isRunning():
			enable = False
			disableReason = 'Race is not running'
		else:
			enable = True
			disableReason = None

		if self.isEnabled != enable:
			self.isEnabled = enable

		self.keypad.Disable(not enable, reason=disableReason)
		self.timeTrialRecord.Disable(not enable, reason=disableReason)
		self.bibTimeRecord.Disable(not enable, reason=disableReason)

		if not enable and self.isKeypadInputMode():
			self.keypad.numEdit.SetValue( '' )

		if self.isBibTimeInputMode():
			self.bibTimeRecord.refresh()

		self.photoCount.Show( bool(race and race.enableUSBCamera) )
		self.photoBitmap.Show( bool(race and race.enableUSBCamera) )

		# Refresh the race start time.
		changed = False
		rst, rstSource = '', ''
		if race and race.startTime:
			st = race.startTime
			if race.enableJChipIntegration and race.resetStartClockOnFirstTag:
				if race.firstRecordedTime:
					rstSource = _('Chip Start')
				else:
					rstSource = _('Waiting...')
			else:
				rstSource = _('Manual Start')
			rst = '{:02d}:{:02d}:{:02d}.{:02d}'.format(st.hour, st.minute, st.second, int(st.microsecond / 10000.0))
		changed |= SetLabel( self.raceStartMessage, rstSource )
		changed |= SetLabel( self.raceStartTime, rst )

		self.refreshInputUpdateNonBusy()

		if self.isKeypadInputMode():
			if self.keypad.numEdit.IsEditable():
				getLogger('Record').debug('Setting focus to keypad edit field.')
				wx.CallLater( 100, self.keypad.SetFocus )
		elif self.isBibTimeInputMode():
			if self.bibTimeRecord.numEdit.IsEditable():
				getLogger('Record').debug('Setting focus to bibTimeRecord edit field.')
				wx.CallLater( 100, self.bibTimeRecord.SetFocus )


if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1000,800))
	Model.setRace( Model.Race() )
	model = Model.getRace()
	model._populate()
	model.enableUSBCamera = True
	numKeypad = Record(mainWin)
	numKeypad.refresh()
	mainWin.Show()
	app.MainLoop()
