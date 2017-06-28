import wx
import os
import wx.lib.intctrl
import wx.lib.buttons
import bisect
import sys
import datetime
from collections import defaultdict

import Utils
from Utils import SetLabel
from GetResults import GetResults, GetLastFinisherTime, GetLeaderFinishTime, GetLastRider, RiderResult
import Model
from keybutton import KeyButton
from RaceHUD import RaceHUD
from EditEntry import DoDNF, DoDNS, DoPull, DoDQ
from TimeTrialRecord import TimeTrialRecord
from ClockDigital import ClockDigital
from NonBusyCall import NonBusyCall

SplitterMinPos = 390
SplitterMaxPos = 530

def MakeKeypadButton( parent, id=wx.ID_ANY, label='', style = 0, size=(-1,-1), font = None ):
	label = label.replace('&','')
	btn = KeyButton( parent, label=label, style=style|wx.NO_BORDER, size=size )
	if font:
		btn.SetFont( font )
	return btn

# backspace, delete, comma, return, digits
validKeyCodes = set( [8, 127, 44, 13] + [x for x in xrange(48, 48+10)] )

class Keypad( wx.Panel ):
	def __init__( self, parent, controller, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		self.SetBackgroundColour( wx.WHITE )
		self.controller = controller
		
		fontPixels = 43
		font = wx.Font((0,fontPixels), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		dc = wx.WindowDC( self )
		dc.SetFont( font )
		wNum, hNum = dc.GetTextExtent( '999' )
		wNum += 8
		hNum += 8
		
		outsideBorder = 4

		vsizer = wx.BoxSizer( wx.VERTICAL )
		
		self.numEditHS = wx.BoxSizer( wx.HORIZONTAL )
		
		self.numEditLabel = wx.StaticText(self, label=u'{}'.format(_('Bib')))
		self.numEditLabel.SetFont( font )
		
		editWidth = 140
		self.numEdit = wx.TextCtrl( self, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER,
							size=(editWidth, fontPixels*1.2) if 'WXMAC' in wx.Platform else (editWidth,-1) )
		self.numEdit.Bind( wx.EVT_CHAR, self.handleNumKeypress )
		self.numEdit.SetFont( font )
		
		self.numEditHS.Add( self.numEditLabel, wx.ALIGN_CENTRE | wx.ALIGN_CENTRE_VERTICAL )
		self.numEditHS.Add( self.numEdit, flag=wx.LEFT|wx.EXPAND, border = 4 )
		vsizer.Add( self.numEditHS, flag=wx.EXPAND|wx.LEFT|wx.TOP, border = outsideBorder )
		
		#------------------------------------------------------------------------------------------
		self.keypadPanel = wx.Panel( self )
		gbs = wx.GridBagSizer(4, 4)
		self.keypadPanel.SetSizer( gbs )
		
		rowCur = 0		
		numButtonStyle = 0
		self.num = []

		self.num.append( MakeKeypadButton( self.keypadPanel, label=u'&0', style=wx.BU_EXACTFIT, font = font) )
		self.num[-1].Bind( wx.EVT_BUTTON, lambda event, aValue = 0 : self.onNumPress(event, aValue) )
		gbs.Add( self.num[0], pos=(3+rowCur,0), span=(1,2), flag=wx.EXPAND )

		for i in xrange(0, 9):
			self.num.append( MakeKeypadButton( self.keypadPanel, label=u'&{}'.format(i+1), style=numButtonStyle, size=(wNum,hNum), font = font) )
			self.num[-1].Bind( wx.EVT_BUTTON, lambda event, aValue = i+1 : self.onNumPress(event, aValue) )
			j = 8-i
			gbs.Add( self.num[-1], pos=(j//3 + rowCur, 2-j%3) )
		
		self.delBtn = MakeKeypadButton( self.keypadPanel, id=wx.ID_DELETE, label=_('&Del'), style=numButtonStyle, size=(wNum,hNum), font = font)
		self.delBtn.Bind( wx.EVT_BUTTON, self.onDelPress )
		gbs.Add( self.delBtn, pos=(3+rowCur,2) )
		rowCur += 4
	
		self.enterBtn = MakeKeypadButton( self.keypadPanel, id=0, label=_('&Enter'), style=wx.EXPAND|wx.GROW, font = font)
		gbs.Add( self.enterBtn, pos=(rowCur,0), span=(1,3), flag=wx.EXPAND )
		self.enterBtn.Bind( wx.EVT_LEFT_DOWN, self.onEnterPress )
		rowCur += 1
		
		self.showTouchScreen = False
		self.keypadPanel.Show( self.showTouchScreen )
		vsizer.Add( self.keypadPanel, flag=wx.TOP, border=4 )
			
		font = wx.Font((0,int(fontPixels*.6)), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		
		hbs = wx.GridSizer( 2, 2, 4, 4 )
		for label, actionFn in [(_('DN&F'),DoDNF), (_('DN&S'),DoDNS), (_('&Pull'),DoPull), (_('D&Q'),DoDQ)]:
			btn = MakeKeypadButton( self, label=label, style=wx.EXPAND|wx.GROW, font = font)
			btn.Bind( wx.EVT_BUTTON, lambda event, fn = actionFn: self.doAction(fn) )
			hbs.Add( btn, flag=wx.EXPAND )
		
		vsizer.Add( hbs, flag=wx.EXPAND|wx.TOP, border=4 )
		
		self.touchBitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'touch24.png'), wx.BITMAP_TYPE_PNG )
		self.touchButton = wx.BitmapButton( self, bitmap = self.touchBitmap )
		self.touchButton.Bind( wx.EVT_BUTTON, self.onToggleTouchScreen)
		self.touchButton.SetToolTip(wx.ToolTip(_("Touch Screen Toggle")))
		
		vsizer.Add( self.touchButton, flag=wx.TOP|wx.ALIGN_CENTRE, border=12 )
		self.SetSizer( vsizer )
	
	def onToggleTouchScreen( self, event ):
		self.showTouchScreen ^= True
		self.keypadPanel.Show( self.showTouchScreen )
		self.GetSizer().Layout()
		self.GetParent().GetParent().SetSashPosition( SplitterMaxPos if self.showTouchScreen else SplitterMinPos )
		try:
			self.GetParent().GetSizer().Layout()
		except:
			pass
	
	def onNumPress( self, event, value ):
		self.numEdit.SetInsertionPointEnd()
		txt = self.numEdit.GetValue()
		txt += '{}'.format(value)
		self.numEdit.SetValue( txt )
		self.numEdit.SetInsertionPointEnd()
		
	def onDelPress( self, event ):
		txt = self.numEdit.GetValue()
		if txt is not None:
			self.numEdit.SetValue( txt[:-1] )
	
	def getRiderNums( self ):
		nums = []
		txt = self.numEdit.GetValue()
		mask = Model.race.getCategoryMask() if Model.race else None
		for num in txt.split( ',' ):
			if not num:
				continue
			if mask:	# Add common prefix numbers to the entry.
				s = num
				dLen = len(mask) - len(s)
				if dLen > 0:
					sAdjust = mask[:dLen] + s
					sAdjust = sAdjust.replace( '.', '0' )
					num = sAdjust
			nums.append( int(num) )
		return nums
	
	def handleNumKeypress(self, event):
		keycode = event.GetKeyCode()
		if keycode == wx.WXK_NUMPAD_ENTER or keycode == wx.WXK_RETURN:
			self.onEnterPress()
		elif keycode < 255:
			if keycode in validKeyCodes:
				event.Skip()
		else:
			event.Skip()
	
	def onEnterPress( self, event = None ):
		nums = self.getRiderNums()
		if nums:
			mainWin = Utils.getMainWin()
			if mainWin is not None:
				mainWin.forecastHistory.logNum( nums )
		self.controller.refreshLaps()
		wx.CallAfter( self.numEdit.SetValue, '' )
	
	def doAction( self, action ):
		race = Model.race
		t = race.curRaceTime() if race and race.isRunning() else None
		success = False
		for num in self.getRiderNums():
			if action(self, num, t):
				success = True
		if success:
			self.numEdit.SetValue( '' )
			wx.CallAfter( Utils.refreshForecastHistory )
	
	def Enable( self, enable ):
		wx.Panel.Enable( self, enable )
		
def getLapInfo( lap, lapsTotal, tCur, tNext, leader ):
	race = Model.race
	if not race or not race.startTime:
		return
	info = []
	startTime = race.startTime
	
	if lap > lapsTotal:
		info.append( (_("Last Rider"), (startTime + datetime.timedelta(seconds=tNext)).strftime('%H:%M:%S')) )
		return info	
	
	tLap = tNext - tCur
	info.append( (_("Lap"), u'{}/{} ({} {})'.format(lap,lapsTotal,lapsTotal-lap, _('to go'))) )
	info.append( (_("Time"), Utils.formatTimeGap(tLap, highPrecision=False)) )
	info.append( (_("Start"), (startTime + datetime.timedelta(seconds=tCur)).strftime('%H:%M:%S')) )
	info.append( (_("End"), (startTime + datetime.timedelta(seconds=tNext)).strftime('%H:%M:%S')) )
	lapDistance = None
	try:
		bib = int(leader.split()[-1])
		category = race.getCategory( bib )
		lapDistance = category.getLapDistance( lap )
	except:
		pass
	if lapDistance is not None:
		sLap = (lapDistance / tLap) * 60.0*60.0
		info.append( (u'', u'{:.02f} {}'.format(sLap, 'km/h')) )
	return info
		
class NumKeypad( wx.Panel ):
	SwitchToTimeTrialEntryMessage = _('Switch to Time Trial Entry')
	SwitchToNumberEntryMessage = _('Switch to Regular Number Entry')

	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		
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
		panel.SetDoubleBuffered( True )
		panel.SetSizer( horizontalMainSizer )
		panel.SetBackgroundColour( wx.WHITE )
		
		#-------------------------------------------------------------------------------
		# Create the edit field, numeric keypad and buttons.
		self.keypad = Keypad( panel, self )
		horizontalMainSizer.Add( self.keypad, 0, flag=wx.TOP|wx.LEFT|wx.EXPAND, border = 4 )
		
		self.timeTrialRecord = TimeTrialRecord( panel, self )
		self.timeTrialRecord.Show( False )
		self.horizontalMainSizer = horizontalMainSizer
		
		#------------------------------------------------------------------------------
		# Race time.
		labelAlign = wx.ALIGN_CENTRE | wx.ALIGN_CENTRE_VERTICAL

		self.raceTime = wx.StaticText( panel, label = u'0:00')
		self.raceTime.SetFont( font )
		self.raceTime.SetDoubleBuffered(True)
		
		self.keypadBitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'keypad.png'), wx.BITMAP_TYPE_PNG )
		self.ttRecordBitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'stopwatch.png'), wx.BITMAP_TYPE_PNG )
		
		self.keypadTimeTrialToggleButton = wx.BitmapButton( panel, bitmap = self.ttRecordBitmap )
		self.keypadTimeTrialToggleButton.Bind( wx.EVT_BUTTON, self.swapKeypadTimeTrialRecord )
		self.keypadTimeTrialToggleButton.SetToolTip(wx.ToolTip(self.SwitchToTimeTrialEntryMessage))
		
		verticalSubSizer = wx.BoxSizer( wx.VERTICAL )
		horizontalMainSizer.Add( verticalSubSizer )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.keypadTimeTrialToggleButton, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border = 8 )
		hs.Add( self.raceTime, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=100-40-8 )
		verticalSubSizer.Add( hs, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, border = 2 )
		
		#------------------------------------------------------------------------------
		# Lap Management.
		gbs = wx.GridBagSizer(4, 12)
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fontSize = 14
		font = wx.Font(fontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		fontBold = wx.Font(fontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

		rowCur = 0
		colCur = 0
		rowCur += 1
		
		label = wx.StaticText( panel, label = _("Manual Start"))
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.raceStartMessage = label
		self.raceStartTime = wx.StaticText( panel )
		self.raceStartTime.SetFont( font )
		gbs.Add( self.raceStartTime, pos=(rowCur, colCur+1), span=(1, 1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		
		rowCur += 1
		line = wx.StaticLine( panel, style=wx.LI_HORIZONTAL )
		gbs.Add( line, pos=(rowCur, colCur), span=(1,2), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		
		rowCur += 1
		label = wx.StaticText( panel, label = u'{}:'.format(_("Est. Last Rider")) )
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,2), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1
		self.lastRiderOnCourseTime = wx.StaticText( panel )
		self.lastRiderOnCourseTime.SetFont( font )
		gbs.Add( self.lastRiderOnCourseTime, pos=(rowCur, colCur), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1
		self.lastRiderOnCourseName = wx.StaticText( panel )
		self.lastRiderOnCourseName.SetFont( fontBold )
		gbs.Add( self.lastRiderOnCourseName, pos=(rowCur, colCur), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1
		self.lastRiderOnCourseTeam = wx.StaticText( panel )
		self.lastRiderOnCourseTeam.SetFont( font )
		gbs.Add( self.lastRiderOnCourseTeam, pos=(rowCur, colCur), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1
		self.lastRiderOnCourseCategory = wx.StaticText( panel )
		self.lastRiderOnCourseCategory.SetFont( font )
		gbs.Add( self.lastRiderOnCourseCategory, pos=(rowCur, colCur), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		
		rowCur += 1
		self.hbClockPhoto = wx.BoxSizer( wx.HORIZONTAL )
		
		self.photoCount = wx.StaticText( panel, label = u"000004" )
		self.photoCount.SetFont( font )
		self.hbClockPhoto.Add( self.photoCount, flag=wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT|wx.ALIGN_RIGHT, border = 6 )
		
		self.camera_bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'camera.png'), wx.BITMAP_TYPE_PNG )
		self.camera_broken_bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'camera_broken.png'), wx.BITMAP_TYPE_PNG )
		
		self.photoButton = wx.BitmapButton( panel, bitmap = self.camera_bitmap )
		self.camera_tooltip = wx.ToolTip( _('Show Last Photos...') )
		self.photoButton.SetToolTip( self.camera_tooltip )
		self.photoButton.Bind( wx.EVT_BUTTON, self.onPhotoButton )
		self.hbClockPhoto.Add( self.photoButton, flag=wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT, border = 18 )
		
		gbs.Add( self.hbClockPhoto, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		rowCur += 1
		
		self.clock = ClockDigital( panel, size=(100,24), checkFunc=self.doClockUpdate )
		self.clock.SetBackgroundColour( wx.WHITE )
		gbs.Add( self.clock, pos=(rowCur, 0), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT )
		rowCur += 1
		
		verticalSubSizer.Add( gbs, flag=wx.LEFT|wx.TOP, border = 8 )
		
		#------------------------------------------------------------------------------
		# Rider Lap Count.
		rcVertical = wx.BoxSizer( wx.VERTICAL )
		rcVertical.AddSpacer( 32 )
		title = wx.StaticText( panel, label = _('Riders on Course:') )
		title.SetFont( wx.Font(fontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL) )
		rcVertical.Add( title, flag=wx.ALL, border = 4 )
		
		self.lapCountList = wx.ListCtrl( panel, wx.ID_ANY, style = wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.BORDER_NONE )
		self.lapCountList.SetFont( wx.Font(int(fontSize*0.9), wx.DEFAULT, wx.NORMAL, wx.NORMAL) )
		self.lapCountList.InsertColumn( 0, _('Category'),	wx.LIST_FORMAT_LEFT,	140 )
		self.lapCountList.InsertColumn( 1, _('Count'),		wx.LIST_FORMAT_RIGHT,	70 )
		self.lapCountList.InsertColumn( 2, u'',				wx.LIST_FORMAT_LEFT,	90 )
		rcVertical.Add( self.lapCountList, 1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border = 4 )
		
		horizontalMainSizer.Add( rcVertical, 1, flag=wx.EXPAND|wx.LEFT, border = 4 )
		
		#----------------------------------------------------------------------------------------------
		self.raceHUD = RaceHUD( splitter, wx.ID_ANY, style=wx.BORDER_SUNKEN, lapInfoFunc=getLapInfo )
		
		splitter.SetMinimumPaneSize( 20 )
		splitter.SplitHorizontally( panel, self.raceHUD, -100 )
		verticalMainSizer.Add( splitter, 1, flag=wx.EXPAND )
		
		self.SetSizer( verticalMainSizer )
		self.isEnabled = True
		
		self.splitter = splitter
		self.firstTimeDraw = True
		
		self.refreshRaceTime()
	
	def doClockUpdate( self ):
		mainWin = Utils.getMainWin()
		return not mainWin or mainWin.isShowingPage(self)
	
	def isKeypadInputMode( self ):
		return self.keypadTimeTrialToggleButton.GetBitmapLabel() == self.ttRecordBitmap
		
	def isTimeTrialInputMode( self ):
		return not self.isKeypadInputMode()
	
	def swapKeypadTimeTrialRecord( self, event = None ):
		if self.isKeypadInputMode():
			self.keypad.Show( False )
			self.timeTrialRecord.Show( True )
			self.timeTrialRecord.refresh()
			self.horizontalMainSizer.Replace( self.keypad, self.timeTrialRecord )
			self.keypadTimeTrialToggleButton.SetBitmapLabel( self.keypadBitmap )
			self.keypadTimeTrialToggleButton.SetToolTip(wx.ToolTip(self.SwitchToNumberEntryMessage))
			wx.CallAfter( self.timeTrialRecord.Refresh )
			wx.CallLater( 100, self.timeTrialRecord.grid.SetFocus )
		else:
			self.keypad.Show( True )
			self.timeTrialRecord.Show( False )
			self.horizontalMainSizer.Replace( self.timeTrialRecord, self.keypad )
			self.keypadTimeTrialToggleButton.SetBitmapLabel( self.ttRecordBitmap )
			self.keypadTimeTrialToggleButton.SetToolTip(wx.ToolTip(self.SwitchToTimeTrialEntryMessage))
			wx.CallAfter( self.keypad.Refresh )
			wx.CallLater( 100, self.keypad.numEdit.SetFocus )
		self.horizontalMainSizer.Layout()
		self.GetSizer().Layout()
		wx.CallAfter( self.Refresh )
		
	def setKeypadInput( self, b = True ):
		if b:
			if not self.isKeypadInputMode():
				self.swapKeypadTimeTrialRecord()
		else:
			if not self.isTimeTrialInputMode():
				self.swapKeypadTimeTrialRecord()
	
	def setTimeTrialInput( self, b = True ):
		self.setKeypadInput( not b )
	
	def refreshRaceHUD( self ):
		race = Model.race
		if not race:
			self.raceHUD.SetData()
			if Utils.mainWin:
				Utils.mainWin.updateLapCounter()
			return
			
		results = GetResults( None )
		if not results:
			self.raceHUD.SetData()
			if Utils.mainWin:
				lapCounter = []
				if all( race.getNumLapsFromCategory(category) for category in race.getCategories(startWaveOnly=True) ):
					lapCounter = [(u'{}'.format(race.getNumLapsFromCategory(category)),False) for category in race.getCategories(startWaveOnly=True)]
				else:
					lapCounter = [(u'{} min'.format(race.minutes),False)] + [(u'{}'.format(race.getNumLapsFromCategory(category)),False)
						for category in race.getCategories(startWaveOnly=True) if race.getNumLapsFromCategory(category)]
				Utils.mainWin.updateLapCounter(lapCounter)
			return

		Finisher = Model.Rider.Finisher
		tCur = race.curRaceTime()
		raceTimes = []
		leader = []
		categoryRaceTimes = {}
		categories_seen = set()
		getCategory = race.getCategory
		leaderCategory = None
		lapCounter = []
		
		secondsBeforeLeaderToFlipLapCounter = race.secondsBeforeLeaderToFlipLapCounter + 1.0
		
		def appendLapCounter( leaderCategory, category, lapCur, lapMax, tLeader=sys.float_info.max ):
			if race.isTimeTrial or not(category == leaderCategory or race.getNumLapsFromCategory(category)):
				return
			lapsToGo = max( 0, lapMax - lapCur )
			if secondsBeforeLeaderToFlipLapCounter < tLeader <= secondsBeforeLeaderToFlipLapCounter+5.0:
				lapCounter.append( ('{}'.format(lapsToGo), True) )
			elif 0.0 <= tLeader <= secondsBeforeLeaderToFlipLapCounter:
				lapCounter.append( ('{}'.format(max(0,lapsToGo-1)), False) )
			else:
				lapCounter.append( ('{}'.format(lapsToGo), False) )
		
		for rr in results:
			if rr.status != Finisher or not rr.raceTimes:
				continue
			category = getCategory( rr.num )
			if category in categories_seen:			# If we have not seen this category, this is not the leader.
				# Make sure we update the red lantern time.
				newRaceTimes = categoryRaceTimes[category]
				if rr.raceTimes[-1] > newRaceTimes[-1]:
					newRaceTimes[-1] = rr.raceTimes[-1]
				continue
			if leaderCategory is None:
				leaderCategory = category
			categories_seen.add( category )
			leader.append( u'{} {}'.format(category.fullname if category else u'<{}>'.format(_('Missing')), rr.num) )
			# Add a copy of the race times.  Append the leader's last time as the current red lantern.
			raceTimes.append( rr.raceTimes + [rr.raceTimes[-1]] )
			categoryRaceTimes[category] = raceTimes[-1]
			
			try:
				lapCur = bisect.bisect_left( rr.raceTimes, tCur )
				tLeader = rr.raceTimes[lapCur] - tCur
			except IndexError:
				appendLapCounter( leaderCategory, category, len(rr.raceTimes)-1, len(rr.raceTimes)-1 )
				continue
			
			appendLapCounter( leaderCategory, category, lapCur, len(rr.raceTimes), tLeader )
				
			if 0.0 <= tLeader <= 3.0 and not race.isTimeTrial:
				if category not in self.lapReminder:
					self.lapReminder[category] = Utils.PlaySound( 'reminder.wav' )
			elif category in self.lapReminder:
				del self.lapReminder[category]
		
		self.raceHUD.SetData( raceTimes, leader, tCur if race.isRunning() else None )
		if Utils.mainWin:
			Utils.mainWin.updateLapCounter( lapCounter )
		
	def refreshRaceTime( self ):
		race = Model.race
		
		if race is not None:
			tRace = race.lastRaceTime()
			tStr = Utils.formatTime( tRace )
			if tStr.startswith('0'):
				tStr = tStr[1:]
			self.refreshRaceHUD()
			if race.enableUSBCamera:
				self.photoButton.Show( True )
				self.photoCount.SetLabel( u'{}'.format(race.photoCount) )
				if Utils.cameraError:
					self.photoButton.SetBitmapLabel( self.camera_broken_bitmap )
					self.photoButton.SetToolTip( wx.ToolTip(Utils.cameraError) )
				else:
					self.photoButton.SetBitmapLabel( self.camera_bitmap )
					self.photoButton.SetToolTip( self.camera_tooltip )
			else:
				self.photoButton.Show( False )
				self.photoCount.SetLabel( '' )
		else:
			tStr = ''
			tRace = None
			self.photoButton.Show( False )
			self.photoCount.SetLabel( '' )
		self.raceTime.SetLabel( '  ' + tStr )
		
		self.hbClockPhoto.Layout()
		
		mainWin = Utils.mainWin
		if mainWin is not None:
			try:
				mainWin.refreshRaceAnimation()
			except:
				pass
	
	def onPhotoButton( self, event ):
		if not Utils.mainWin:
			return
		Utils.mainWin.photoDialog.Show( True )
		Utils.mainWin.photoDialog.refresh( Utils.mainWin.photoDialog.ShowAllPhotos )
	
	raceMessage = { 0:_("Finishers Arriving"), 1:_("Ring Bell"), 2:_("Prepare Bell") }
	def refreshLaps( self ):
		wx.CallAfter( self.refreshRaceHUD )
	
	def refreshRiderLapCountList( self ):
		self.lapCountList.DeleteAllItems()
		race = Model.race
		if not race or not race.isRunning():
			return
		
		Finisher = Model.Rider.Finisher
		getCategory = race.getCategory
		
		results = GetResults(None)
		if race.enableJChipIntegration and race.resetStartClockOnFirstTag and len(results) != len(race.riders):
			# Add rider entries who have been read by RFID but have not completed the first lap.
			results = list(results)
			resultNums = set( rr.num for rr in results )
			for a in race.riders.itervalues():
				if a.num not in resultNums and a.firstTime is not None:
					category = getCategory( a.num )
					if category:
						results.append(
							#              num,   status,    lastTime, raceCat,           lapTimes, raceTimes, interp
							RiderResult( a.num, a.status, a.firstTime, category.fullname,       [],        [],     [] )
						)
		if not results:
			return
		
		categoryLapMax = defaultdict(int)
		catLapCount = defaultdict(int)
		catCount = defaultdict(int)
		catRaceCount = defaultdict(int)
		
		t = race.curRaceTime()
		for rr in results:
			category = getCategory( rr.num )
			catCount[category] += 1
			if rr.status == Finisher:
				categoryLapMax[category] = max(1, len(rr.raceTimes)-1, categoryLapMax[category])
			
		for rr in results:
			category = getCategory( rr.num )
			numLaps = categoryLapMax[category]
			
			tSearch = t
			if race.isTimeTrial:
				try:
					tSearch -= race.riders[rr.num].firstTime
				except:
					pass
			lap = max( 1, bisect.bisect_left(rr.raceTimes, tSearch) )
			
			if lap <= numLaps:
				# Rider is still on course.
				key = (category, lap, numLaps)
				catLapCount[key] += 1
				catRaceCount[category] += 1
		
		if not catLapCount:
			return
			
		catLapList = [(category, lap, categoryLaps, count)
						for (category, lap, categoryLaps), count in catLapCount.iteritems()]
		catLapList.sort( key=lambda x: (x[0].getStartOffsetSecs(), x[0].fullname, -x[1]) )
		
		def appendListRow( row = tuple(), colour = None, bold = None ):
			r = self.lapCountList.InsertItem( sys.maxint, u'{}'.format(row[0]) if row else u'' )
			for c in xrange(1, len(row)):
				self.lapCountList.SetItem( r, c, u'{}'.format(row[c]) )
			if colour is not None:
				item = self.lapCountList.GetItem( r )
				item.SetTextColour( colour )
				self.lapCountList.SetItem( item )
			if bold is not None:
				item = self.lapCountList.GetItem( r )
				font = self.lapCountList.GetFont()
				font.SetWeight( wx.FONTWEIGHT_BOLD )
				item.SetFont( font )
				self.lapCountList.SetItem( item )
			return r
		
		appendListRow( (
							_('Total'),
							u'{}/{}'.format(sum(count for count in catLapCount.itervalues()),
											sum(count for count in catCount.itervalues()))
						),
						colour=wx.BLUE,
						bold=True )

		lastCategory = None
		for category, lap, categoryLaps, count in catLapList:
			if category != lastCategory:
				appendListRow( (category.fullname, u'{}/{}'.format(catRaceCount[category], catCount[category]),
									(u'({} {})'.format(categoryLaps, _('laps') if categoryLaps > 1 else _('lap'))) ),
								bold = True )
			appendListRow( (u'', count, u'{} {}'.format( _('on lap'), lap ) ) )
			lastCategory = category

	def refreshLastRiderOnCourse( self ):
		race = Model.race
		lastRiderOnCourse = GetLastRider( None )
		changed = False
		
		if lastRiderOnCourse:
			maxLength = 24
			rider = race.riders[lastRiderOnCourse.num]
			short_name = lastRiderOnCourse.short_name(maxLength)
			if short_name:
				lastRiderOnCourseName = u'{}: {}'.format(lastRiderOnCourse.num, lastRiderOnCourse.short_name())
			else:
				lastRiderOnCourseName = u'{}'.format(lastRiderOnCourse.num)
			
			lastRiderOnCourseTeam = u'{}'.format( getattr(lastRiderOnCourse, 'Team', u'Independent') )
			if len(lastRiderOnCourseTeam) > maxLength:
				lastRiderOnCourseTeam = lastRiderOnCourseTeam[:maxLength].strip() + u'...'
			
			category = race.getCategory( lastRiderOnCourse.num )
			lastRiderOnCourseCategory = category.fullname
			
			t = (lastRiderOnCourse._lastTimeOrig or 0.0) + ((rider.firstTime or 0.0) if race.isTimeTrial else 0.0)
			tFinish = race.startTime + datetime.timedelta( seconds=t )
			lastRiderOnCourseTime = u'{} {}'.format(_('Finishing at'), tFinish.strftime('%H:%M:%S') )
		else:
			lastRiderOnCourseName = u''
			lastRiderOnCourseTeam = u''
			lastRiderOnCourseCategory = u''
			lastRiderOnCourseTime = u''
		changed |= SetLabel( self.lastRiderOnCourseName, lastRiderOnCourseName )
		changed |= SetLabel( self.lastRiderOnCourseTeam, lastRiderOnCourseTeam )
		changed |= SetLabel( self.lastRiderOnCourseCategory, lastRiderOnCourseCategory )
		changed |= SetLabel( self.lastRiderOnCourseTime, lastRiderOnCourseTime )
		if changed:
			Utils.LayoutChildResize( self.raceStartTime )
	
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
		self.refreshRiderLapCountList()
		self.refreshLastRiderOnCourse()

	def refresh( self ):
		self.clock.Start()

		race = Model.race
		enable = bool(race and race.isRunning())
		if self.isEnabled != enable:
			self.keypad.Enable( enable )
			self.timeTrialRecord.Enable( enable )
			self.isEnabled = enable
		if not enable and self.isKeypadInputMode():
			self.keypad.numEdit.SetValue( '' )
			
		self.photoCount.Show( bool(race and race.enableUSBCamera) )
		self.photoButton.Show( bool(race and race.enableUSBCamera) )
		
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
			wx.CallLater( 100, self.keypad.numEdit.SetFocus )
		if self.isTimeTrialInputMode():
			wx.CallAfter( self.timeTrialRecord.refresh )
	
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1000,800))
	Model.setRace( Model.Race() )
	model = Model.getRace()
	model._populate()
	model.enableUSBCamera = True
	numKeypad = NumKeypad(mainWin)
	numKeypad.refresh()
	mainWin.Show()
	app.MainLoop()


