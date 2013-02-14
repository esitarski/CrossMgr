import wx
import wx.lib.agw.gradientbutton as GB
import os
import wx.lib.intctrl
from wx.lib.stattext import GenStaticText 
import bisect
import Utils
from Utils import SetValue, SetLabel
from GetResults import GetResults, GetLastFinisherTime, GetLeaderFinishTime
import Model
import sys
import datetime
from collections import defaultdict
from keybutton import KeyButton
from RaceHUD import RaceHUD
from EditEntry import DoDNS, DoDNF, DoPull, DoDQ

def MakeButton( parent, id=wx.ID_ANY, label='', style = 0, size=(-1,-1) ):
	btn = KeyButton( parent, -1, None, label=label.replace('&',''), style=style|wx.NO_BORDER, size=size)
	return btn

# backspace, delete, comma, return, digits
validKeyCodes = set( [8, 127, 44, 13] + [x for x in xrange(48, 48+10)] )
	
class NumKeypad( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		self.bell = None
		self.lapReminder = {}
		
		self.SetBackgroundColour( wx.WHITE )
		
		fontPixels = 43
		font = wx.FontFromPixelSize(wx.Size(0,fontPixels), wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		dc = wx.WindowDC( self )
		dc.SetFont( font )
		wNum, hNum = dc.GetTextExtent( '999' )
		wNum += 8
		hNum += 8

		verticalMainSizer = wx.BoxSizer( wx.VERTICAL )
		horizontalMainSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		splitter = wx.SplitterWindow( self, wx.ID_ANY, style = wx.SP_3DSASH )
		
		panel = wx.Panel( splitter, wx.ID_ANY, style=wx.BORDER_SUNKEN )
		panel.SetSizer( horizontalMainSizer )
		
		outsideBorder = 4
		
		#-------------------------------------------------------------------------------
		# Create the edit field, numeric keybad and buttons.
		gbs = wx.GridBagSizer(4, 4)
		rowCur = 0
		
		self.numEdit = wx.TextCtrl( panel, wx.ID_ANY, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value='' )
		self.Bind( wx.EVT_TEXT_ENTER, self.onEnterPress, self.numEdit )
		self.numEdit.Bind( wx.EVT_CHAR, self.handleNumKeypress )
		self.numEdit.SetFont( font )
		gbs.Add( self.numEdit, pos=(rowCur,0), span=(1,3), flag=wx.EXPAND|wx.LEFT|wx.TOP, border = outsideBorder )
		self.num = []
		self.num.append( MakeButton( panel, wx.ID_ANY, label='&0', style=wx.BU_EXACTFIT) )
		self.num[-1].Bind( wx.EVT_BUTTON, lambda event, aValue = 0 : self.onNumPress(event, aValue) )
		gbs.Add( self.num[0], pos=(4+rowCur,0), span=(1,2), flag=wx.EXPAND )

		numButtonStyle = 0
		
		for i in xrange(0, 9):
			self.num.append( MakeButton( panel, id=wx.ID_ANY, label='&' + str(i+1), style=numButtonStyle, size=(wNum,hNum)) )
			self.num[-1].Bind( wx.EVT_BUTTON, lambda event, aValue = i+1 : self.onNumPress(event, aValue) )
			j = 8-i
			gbs.Add( self.num[-1], pos=(int(j/3)+1 + rowCur, 2-j%3) )
		
		for n in self.num:
			n.SetFont( font )
		
		self.delBtn = MakeButton( panel, id=wx.ID_DELETE, label='&Del', style=numButtonStyle, size=(wNum,hNum))
		self.delBtn.SetFont( font )
		self.delBtn.Bind( wx.EVT_BUTTON, self.onDelPress )
		gbs.Add( self.delBtn, pos=(4+rowCur,2) )
		
		self.enterBtn= MakeButton( panel, id=0, label='&Enter', style=wx.EXPAND|wx.GROW)
		self.enterBtn.SetFont( font )
		gbs.Add( self.enterBtn, pos=(5+rowCur,0), span=(1,3), flag=wx.EXPAND )
		self.enterBtn.Bind( wx.EVT_BUTTON, self.onEnterPress )
	
		rowCur += 7
		font = wx.FontFromPixelSize(wx.Size(0,fontPixels*.75), wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		self.dnfBtn= MakeButton( panel, id=wx.ID_ANY, label='DN&F', style=wx.EXPAND|wx.GROW)
		self.dnfBtn.SetFont( font )
		gbs.Add( self.dnfBtn, pos=(rowCur,0), span=(1,1), flag=wx.EXPAND )
		self.dnfBtn.Bind( wx.EVT_BUTTON, self.onDNFPress )
	
		self.pullBtn= MakeButton( panel, id=wx.ID_ANY, label='&Pull', style=wx.EXPAND|wx.GROW)
		self.pullBtn.SetFont( font )
		gbs.Add( self.pullBtn, pos=(rowCur,1), span=(1,1), flag=wx.EXPAND )
		self.pullBtn.Bind( wx.EVT_BUTTON, self.onPullPress )
	
		self.pullBtn= MakeButton( panel, id=wx.ID_ANY, label='&DQ', style=wx.EXPAND|wx.GROW)
		self.pullBtn.SetFont( font )
		gbs.Add( self.pullBtn, pos=(rowCur,2), span=(1,1), flag=wx.EXPAND )
		self.pullBtn.Bind( wx.EVT_BUTTON, self.onDQPress )
	
		horizontalMainSizer.Add( gbs, flag=wx.TOP|wx.LEFT, border = 4 )
		#------------------------------------------------------------------------------
		# Race time.
		labelAlign = wx.ALIGN_CENTRE | wx.ALIGN_CENTRE_VERTICAL

		self.raceTime = wx.StaticText( panel, wx.ID_ANY, '00:00')
		self.raceTime.SetFont( font )
		self.raceTime.SetDoubleBuffered(True)
		
		verticalSubSizer = wx.BoxSizer( wx.VERTICAL )
		horizontalMainSizer.Add( verticalSubSizer )
		verticalSubSizer.Add( self.raceTime, flag=wx.LEFT | wx.EXPAND | wx.ALIGN_CENTRE | wx.ALIGN_CENTRE_VERTICAL, border = 100 )
		
		#------------------------------------------------------------------------------
		# Lap Management.
		gbs = wx.GridBagSizer(4, 12)
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fontSize = 14
		font = wx.Font(fontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

		rowCur = 0
		colCur = 0
		self.automaticManualChoice = wx.Choice( panel, id=wx.ID_ANY, choices = ['Automatic', 'Manual'], size=(132,-1) )
		self.Bind(wx.EVT_CHOICE, self.doChooseAutomaticManual, self.automaticManualChoice)
		self.automaticManualChoice.SetSelection( 0 )
		self.automaticManualChoice.SetFont( font )
		gbs.Add( self.automaticManualChoice, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_LEFT )
		rowCur += 1
		
		label = wx.StaticText( panel, wx.ID_ANY, 'Total Laps')
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.numLaps = wx.Choice( panel, 21, choices = [''] + [str(x) for x in xrange(2,21)], size=(64,-1) )
		self.numLaps.SetSelection( 0 )
		self.numLaps.SetFont( font )
		self.numLaps.SetDoubleBuffered( True )
		self.Bind(wx.EVT_CHOICE, self.doChangeNumLaps, self.numLaps)
		gbs.Add( self.numLaps, pos=(rowCur, colCur+1), span=(1,1) )
		rowCur += 1
		
		label = wx.StaticText( panel, wx.ID_ANY, "Est. Leader Time")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.leaderFinishTime = wx.StaticText( panel, wx.ID_ANY, "")
		self.leaderFinishTime.SetFont( font )
		gbs.Add( self.leaderFinishTime, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1

		label = wx.StaticText( panel, wx.ID_ANY, "Est. Last Rider Time")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.lastRiderFinishTime = wx.StaticText( panel, wx.ID_ANY, "")
		self.lastRiderFinishTime.SetFont( font )
		gbs.Add( self.lastRiderFinishTime, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1

		label = wx.StaticText( panel, wx.ID_ANY, "Avg Lap Time")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.leadersLapTime = wx.StaticText( panel, wx.ID_ANY, "")
		self.leadersLapTime.SetFont( font )
		gbs.Add( self.leadersLapTime, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1

		label = wx.StaticText( panel, wx.ID_ANY, "Completing Lap")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.lapCompleting = wx.StaticText( panel, wx.ID_ANY, "")
		self.lapCompleting.SetFont( font )
		gbs.Add( self.lapCompleting, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1

		label = wx.StaticText( panel, wx.ID_ANY, "Show Laps to Go")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.lapsToGo = wx.StaticText( panel, wx.ID_ANY, "")
		self.lapsToGo.SetFont( font )
		gbs.Add( self.lapsToGo, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1
		
		rowCur += 1
		label = wx.StaticText( panel, wx.ID_ANY, "Manual Start")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.raceStartMessage = label
		self.raceStartTime = wx.StaticText( panel, wx.ID_ANY, '' )
		self.raceStartTime.SetFont( font )
		gbs.Add( self.raceStartTime, pos=(rowCur, colCur+1), span=(1, 1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		
		rowCur += 1
		label = wx.StaticText( panel, wx.ID_ANY, "Est. Leader Finish")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.estLeaderTime = wx.StaticText( panel, wx.ID_ANY, '' )
		self.estLeaderTime.SetFont( font )
		gbs.Add( self.estLeaderTime, pos=(rowCur, colCur+1), span=(1, 1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1
		label = wx.StaticText( panel, wx.ID_ANY, "Est. Last Rider Finish")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.estLastRiderTime = wx.StaticText( panel, wx.ID_ANY, '' )
		self.estLastRiderTime.SetFont( font )
		gbs.Add( self.estLastRiderTime, pos=(rowCur, colCur+1), span=(1, 1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		
		rowCur += 1
		self.hbClockPhoto = wx.BoxSizer( wx.HORIZONTAL )
		
		self.photoCount = wx.StaticText( panel, wx.ID_ANY, "000004" )
		self.photoCount.SetFont( font )
		self.hbClockPhoto.Add( self.photoCount, flag=wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT|wx.ALIGN_RIGHT, border = 6 )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'camera.png'), wx.BITMAP_TYPE_PNG )
		self.photoButton = wx.BitmapButton( panel, wx.ID_ANY, bitmap )
		self.photoButton.Bind( wx.EVT_BUTTON, self.onPhotoButton )
		self.hbClockPhoto.Add( self.photoButton, flag=wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT, border = 18 )
		
		label = wx.StaticText( panel, wx.ID_ANY, "Clock")
		label.SetFont( font )
		self.hbClockPhoto.Add( label, flag=wx.ALIGN_CENTRE_VERTICAL )
		
		gbs.Add( self.hbClockPhoto, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.clockTime = wx.StaticText( panel, wx.ID_ANY, '' )
		self.clockTime.SetFont( font )
		gbs.Add( self.clockTime, pos=(rowCur, colCur+1), span=(1, 1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1
		
		rowCur += 1
		self.message = wx.StaticText( panel, wx.ID_ANY, '' )
		self.message.SetFont( font )
		self.message.SetDoubleBuffered( True )
		gbs.Add( self.message, pos=(rowCur, colCur), span=(1, 2), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE )
		rowCur += 1
		
		verticalSubSizer.Add( gbs, flag=wx.LEFT|wx.TOP, border = 8 )
		
		#------------------------------------------------------------------------------
		# Rider Lap Count.
		rcVertical = wx.BoxSizer( wx.VERTICAL )
		rcVertical.AddSpacer( 32 )
		title = wx.StaticText( panel, wx.ID_ANY, 'Riders on Course:')
		title.SetFont( wx.Font(fontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL) )
		rcVertical.Add( title, flag=wx.ALL, border = 4 )
		
		self.lapCountList = wx.ListCtrl( panel, wx.ID_ANY, style = wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.BORDER_NONE )
		self.lapCountList.SetFont( wx.Font(int(fontSize*0.9), wx.DEFAULT, wx.NORMAL, wx.NORMAL) )
		self.lapCountList.InsertColumn( 0, 'Category',	wx.LIST_FORMAT_LEFT,	80 )
		self.lapCountList.InsertColumn( 1, 'Count',		wx.LIST_FORMAT_RIGHT,	70 )
		self.lapCountList.InsertColumn( 2, '',			wx.LIST_FORMAT_LEFT,	90 )
		rcVertical.Add( self.lapCountList, 1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border = 4 )
		
		horizontalMainSizer.Add( rcVertical, 1, flag=wx.EXPAND|wx.LEFT, border = 4 )
		
		#----------------------------------------------------------------------------------------------
		self.raceHUD = RaceHUD( splitter, wx.ID_ANY, style=wx.BORDER_SUNKEN )
		
		splitter.SetMinimumPaneSize( 20 )
		splitter.SplitHorizontally( panel, self.raceHUD, -100 )
		verticalMainSizer.Add( splitter, 1, flag=wx.EXPAND )
		
		self.SetSizer( verticalMainSizer )
		self.isEnabled = True
		
		self.splitter = splitter
		self.notDrawnYet = True
		
		self.refreshRaceTime()
	
	def refreshRaceHUD( self ):
		# Assumes Model is locked.
		race = Model.race
		if not race:
			return
			
		results = GetResults( None, False )
		if not results:
			return

		tCur = race.curRaceTime()
		raceTimes = []
		leader = []
		categoryRaceTimes = {}
		categories_seen = set()
		for rr in results:
			if rr.status != Model.Rider.Finisher or not rr.raceTimes:
				continue
			category = race.getCategory( rr.num )
			if category in categories_seen:			# If we have not seen this category, this is not the leader.
				# Make sure we update the red lantern time.
				newRaceTimes = categoryRaceTimes[category]
				if rr.raceTimes[-1] > newRaceTimes[-1]:
					newRaceTimes[-1] = rr.raceTimes[-1]
				continue
			categories_seen.add( category )
			leader.append( '%s %d' % (category.fullname if category else '<Missing>', rr.num) )
			# Add a copy of the race times.  Append the leader's last time as the current red lantern.
			raceTimes.append( rr.raceTimes + [rr.raceTimes[-1]] )
			categoryRaceTimes[category] = raceTimes[-1]
			
			try:
				tLeader = rr.raceTimes[bisect.bisect_left( rr.raceTimes, tCur )] - tCur
			except IndexError:
				continue
				
			if 0.0 <= tLeader <= 3.0 and not getattr(race, 'isTimeTrial', False):
				if category not in self.lapReminder:
					self.lapReminder[category] = Utils.PlaySound( 'reminder.wav' )
			elif category in self.lapReminder:
				del self.lapReminder[category]
		
		self.raceHUD.SetData( nowTime = tCur, raceTimes = raceTimes, leader = leader )
		
	def refreshRaceTime( self ):
		tClockStr = ''
		with Model.LockRace() as race:
			if race is not None:
				tRace = race.lastRaceTime()
				tStr = Utils.formatTime( tRace )
				self.refreshRaceHUD()
				if getattr(race, 'enableUSBCamera', False):
					self.photoButton.Show( True )
					self.photoCount.SetLabel( str(getattr(race, 'photoCount', '')) )
				else:
					self.photoButton.Show( False )
					self.photoCount.SetLabel( '' )
					
				if race.isRunning():
					tNow = datetime.datetime.now()
					tClockStr = '%02d:%02d:%02d' % (tNow.hour, tNow.minute, tNow.second)
			else:
				tStr = ''
				tRace = None
				self.photoButton.Show( False )
				self.photoCount.SetLabel( '' )
			self.raceTime.SetLabel( '  ' + tStr )
			self.clockTime.SetLabel( tClockStr )
		
		self.hbClockPhoto.Layout()
		
		mainWin = Utils.mainWin
		if mainWin is not None:
			try:
				mainWin.refreshRaceAnimation()
			except:
				pass
			mainWin.forecastHistory.updatedExpectedTimes( tRace )
	
	def onPhotoButton( self, event ):
		with Model.LockRace() as race:
			if not race or not getattr(race, 'enableUSBCamera', False) or not Utils.mainWin:
				return
			tLast, rLast = race.getLastKnownTimeRider()
			if not rLast:
				return
		Utils.mainWin.photoDialog.Show( True )
		Utils.mainWin.photoDialog.refresh( rLast.num )
	
	def doChangeNumLaps( self, event ):
		with Model.LockRace() as race:
			if race and race.isFinished():
				try:
					numLaps = int(self.numLaps.GetString(self.numLaps.GetSelection()))
					if race.numLaps != numLaps:
						race.numLaps = numLaps
						race.setChanged()
				except ValueError:
					pass
		self.refreshLaps()
	
	def doChooseAutomaticManual( self, event ):
		with Model.LockRace() as race:
			if race is not None:
				race.automaticManual = self.automaticManualChoice.GetSelection()
		self.refreshLaps()
		
	def onNumPress( self, event, value ):
		self.numEdit.SetInsertionPointEnd()
		txt = self.numEdit.GetValue()
		txt += str(value)
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
		if keycode < 255:
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
		self.refreshLaps()
		self.numEdit.SetValue( '' )
	
	def doAction( self, action ):
		success = False
		for num in self.getRiderNums():
			if action(self, num ):
				success = True
		if success:
			self.numEdit.SetValue( '' )
	
	def onDNFPress( self, event ):
		self.doAction( DoDNF )
	
	def onPullPress( self, event ):
		self.doAction( DoPull )
	
	def onDQPress( self, event ):
		self.doAction( DoDQ )
	
	def onDNSPress( self, event ):
		self.doAction( DoDNS )
	
	def resetLaps( self, enable = False ):
		# Assumes Model is locked.
		infoFields = [
				self.leaderFinishTime,
				self.lastRiderFinishTime,
				self.leadersLapTime,
				self.lapCompleting,
				self.lapsToGo,
				self.estLeaderTime, self.estLastRiderTime,
				self.message
				]
				
		for f in infoFields:
			f.Enable( enable )
		
		changed = False

		race = Model.race
		if race is None or not race.isFinished() or race.numLaps is None:
			if race is not None and self.automaticManualChoice.GetSelection() != 0:
				self.numLaps.SetItems( [str(x) for x in xrange(1, 16)] )
				self.numLaps.SetSelection( 4 )
			else:
				self.numLaps.SetItems( [''] )
				self.numLaps.SetSelection( 0 )
			for f in infoFields:
				SetLabel( f, '' )
			changed |= SetLabel( self.lapCompleting, '1' )
			changed |= SetLabel( self.message, 'Collecting Data' )
		else:
			self.numLaps.SetItems( [ str(race.numLaps) ] )
			self.numLaps.SetSelection( 0 )
			changed |= SetLabel( self.leaderFinishTime, Utils.formatTime(GetLeaderFinishTime()) )
			changed |= SetLabel( self.lastRiderFinishTime, Utils.formatTime(GetLastFinisherTime()) )
			changed |= SetLabel( self.leadersLapTime, Utils.formatTime(race.getLeaderLapTime()) )
			changed |= SetLabel( self.lapCompleting, str(race.numLaps if race.numLaps is not None else 0) )
			changed |= SetLabel( self.lapsToGo, '0' )
			changed |= SetLabel( self.message, '' )
			changed |= self.updateEstFinishTime()
			
		if changed:
			Utils.LayoutChildResize( self.message )
		self.refreshRaceHUD()
	
	def getLapInfo( self ):
		# Assumes Model is locked.
		# Returns (laps, lapsToGo, lapCompleting,
		#			leadersExpectedLapTime, leaderNum,
		#			raceFinishTime, isAutomatic)
		race = Model.race
		lapCompleting = 1
		if not race:
			return (None, None, lapCompleting, None, None, None, False)

		leaderTimes, leaderNums = race.getLeaderTimesNums()
		if not leaderTimes:
			return (None, None, lapCompleting, None, None, None, False)
		
		t = race.curRaceTime()
		lapCompleting = bisect.bisect_right( leaderTimes, t ) - 1
		if lapCompleting < 2:
			return (None, None, lapCompleting, None, None, None, False)
		
		raceTime = race.minutes * 60.0
		leadersExpectedLapTime = race.getLeaderLapTime()
		
		isAutomatic = False
		if self.automaticManualChoice.GetSelection() == 0:
			laps = bisect.bisect_left( leaderTimes, raceTime, hi=len(leaderTimes)-1 )
			if leaderTimes[laps] - raceTime > leadersExpectedLapTime * 0.5:
				laps -= 1
			isAutomatic = True
		else:
			try:
				laps = int(self.numLaps.GetString(self.numLaps.GetSelection()))
			except ValueError:
				laps = max(0, len(leaderTimes)-1)
		
		laps = max( laps, 0 )
		raceFinishTime = leaderTimes[laps] if laps < len(leaderTimes) else None
		leaderNum = leaderNums[laps] if laps < len(leaderNums) else None
		
		lapsToGo = max(0, laps - lapCompleting)

		return (laps, lapsToGo, lapCompleting,
				leadersExpectedLapTime, leaderNum,
				raceFinishTime, isAutomatic)
	
	def getMinMaxLapsRange( self ):
		race = Model.race
		curLaps = race.numLaps if race.numLaps is not None else 1
		minLaps = max(1, curLaps-5)
		maxLaps = minLaps + 10
		return minLaps, maxLaps
	
	def updateEstFinishTime( self ):
		race = Model.race
		changed = False
		if not race or getattr(race, 'isTimeTrial', False):
			changed |= SetLabel( self.estLeaderTime, '' )
			changed |= SetLabel( self.estLastRiderTime, '' )
			return changed
			
		try:
			changed |= SetLabel( self.estLeaderTime, 
				(race.startTime + datetime.timedelta(seconds = GetLeaderFinishTime())).strftime('%H:%M:%S') )
			changed |= SetLabel( self.estLastRiderTime,
				(race.startTime + datetime.timedelta(seconds = GetLastFinisherTime())).strftime('%H:%M:%S') )
		except:
			changed |= SetLabel( self.estLeaderTime, '' )
			changed |= SetLabel( self.estLastRiderTime, '' )
			
		return changed
			
	def refreshLaps( self ):
		with Model.LockRace() as race:
			enable = (race and race.isRunning())
			
			allCategoriesHaveRaceLapsDefined = race and getattr(race, 'allCategoriesHaveRaceLapsDefined', False)

			if allCategoriesHaveRaceLapsDefined:
				self.automaticManualChoice.Enable( False )
				self.automaticManualChoice.SetSelection( 0 )	# Default to Automatic and do not allow edit.
				self.numLaps.Enable( False )
			else:
				self.automaticManualChoice.Enable( enable )
				self.automaticManualChoice.SetSelection( getattr(race, 'automaticManual', 0) )
			
			# Allow the number of laps to be changed after the race is finished.
			numLapsEnable = (not allCategoriesHaveRaceLapsDefined and race and (race.isRunning() or race.isFinished()))
			self.numLaps.Enable( numLapsEnable )
			if numLapsEnable != enable:
				self.resetLaps( enable )
				minLaps, maxLaps = self.getMinMaxLapsRange()
				self.numLaps.SetItems( [str(x) for x in xrange(minLaps, maxLaps)] )
				if race.numLaps is not None:
					for i, v in enumerate(self.numLaps.GetItems()):
						if int(v) == race.numLaps:
							self.numLaps.SetSelection( i )
							break
				if not enable:
					return
				
			if not enable:
				self.resetLaps()
				return
			
			laps, lapsToGo, lapCompleting, leadersExpectedLapTime, leaderNum, expectedRaceFinish, isAutomatic = self.getLapInfo()
			if laps is None:
				self.resetLaps( True )
				SetLabel( self.lapCompleting, str(lapCompleting) if lapCompleting is not None else '1' )
				return
			
			if isAutomatic and lapCompleting >= 2:
				if self.numLaps.GetString(0) != str(lapCompleting):
					self.numLaps.SetItems( [str(x) for x in xrange(lapCompleting, laps+5)] )
					self.numLaps.SetSelection( 0 )
				if self.numLaps.GetString(self.numLaps.GetSelection()) != str(laps):
					for i, v in enumerate(self.numLaps.GetItems()):
						if int(v) == laps:
							self.numLaps.SetSelection( i )
							break
			
			raceMessage = { 0:'Finishers Arriving', 1:'Ring Bell', 2:'Prepare Bell' }
			
			changed = False
			
			# Set the projected finish time and laps.
			if lapCompleting >= 1 or not isAutomatic:
				changed |= SetLabel( self.leaderFinishTime, Utils.formatTime(expectedRaceFinish) )
				changed |= SetLabel( self.lastRiderFinishTime, Utils.formatTime(GetLastFinisherTime()) )
				changed |= SetLabel( self.leadersLapTime, Utils.formatTime(leadersExpectedLapTime) )
				changed |= SetLabel( self.lapsToGo, str(lapsToGo) )
				changed |= SetLabel( self.lapCompleting, str(lapCompleting) )
				changed |= self.updateEstFinishTime()
				
				if   lapsToGo == 2 and race.isLeaderExpected():
					changed |= SetLabel( self.message, '%d: Leader Bell Lap Alert' % leaderNum )
				elif lapsToGo == 1 and race.isLeaderExpected():
					changed |= SetLabel( self.message, '%d: Leader Finish Alert' % leaderNum )
				else:
					changed |= SetLabel( self.message, raceMessage.get(lapsToGo, '') )
				if race.numLaps != laps:
					race.numLaps = laps
					race.setChanged()
				
				if race.allRidersFinished():
					race.finishRaceNow()
			else:
				if self.numLaps.GetSelection() != 0:
					self.numLaps.SetSelection( 0 )
				changed |= SetLabel( self.leaderFinishTime, '' )
				changed |= SetLabel( self.lastRiderFinishTime, '' )
				changed |= SetLabel( self.leadersLapTime, '' )
				changed |= SetLabel( self.lapsToGo, '' )
				changed |= SetLabel( self.lapCompleting, str(lapCompleting) )
				changed |= SetLabel( self.estLeaderTime, '' )
				changed |= SetLabel( self.estLastRiderTime, '' )
				changed |= SetLabel( self.message, 'Collecting Data' )
				if race.numLaps is not None:
					race.numLaps = None
					race.setChanged()
		if changed:
			Utils.LayoutChildResize( self.message )
		wx.CallAfter( self.refreshRaceHUD )
	
	def refreshRiderLapCountList( self ):
		self.lapCountList.DeleteAllItems()
		with Model.LockRace() as race:
			if not race or not race.isRunning():
				return
		
		results = GetResults( None, False )
		if not results:
			return
		
		catLapCount = defaultdict(int)
		catCount = defaultdict(int)
		catRaceCount = defaultdict(int)
		with Model.LockRace() as race:
			t = Model.race.curRaceTime()
			for rr in results:
				category = race.getCategory( rr.num )
				catCount[category] += 1
				if rr.status != Model.Rider.Finisher:
					continue
				numLaps = race.getCategoryBestLaps( category )
				numLaps = (numLaps if numLaps else 1)
				
				tSearch = t
				if race.isTimeTrial:
					try:
						tSearch -= race[rr.num].firstTime
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
			r = self.lapCountList.InsertStringItem( sys.maxint, str(row[0]) if row else '' )
			for c in xrange(1, len(row)):
				self.lapCountList.SetStringItem( r, c, str(row[c]) )
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
		
		appendListRow( ('Total',
							'%d/%d' % (	sum(count for count in catLapCount.itervalues()),
										sum(count for count in catCount.itervalues())) ),
							colour=wx.BLUE, bold=True )

		lastCategory = None
		for category, lap, categoryLaps, count in catLapList:
			if category != lastCategory:
				appendListRow( (category.fullname, '%d/%d' % (catRaceCount[category], catCount[category]),
									('(%d lap%s)' % (categoryLaps, 's' if categoryLaps > 1 else '')) ),
								bold = True )
			appendListRow( ('', count, 'on lap %d' % lap) )
			lastCategory = category
			
	def refresh( self ):
		if self.notDrawnYet:
			self.notDrawnYet = False
			self.splitter.SetSashPosition( 440 )
	
		wx.CallAfter( self.numEdit.SetFocus )
		with Model.LockRace() as race:
			enable = (race and race.isRunning())
			if self.isEnabled != enable:
				for b in self.num:
					b.Enable( enable )
				for b in [self.numEdit, self.delBtn, self.enterBtn, self.dnfBtn, self.pullBtn]:
					b.Enable( enable )
				self.isEnabled = enable
			if not enable:
				self.numEdit.SetValue( '' )
			
			# Refresh the race start time.
			changed = False
			rst, rstSource = '', ''
			if race and race.startTime:
				st = race.startTime
				if getattr(race, 'enableJChipIntegration', False) and \
							getattr(race, 'resetStartClockOnFirstTag', False):
					if getattr(race, 'firstRecordedTime', None):
						rstSource = 'Chip Start'
					else:
						rstSource = 'Waiting...'
				else:
					rstSource = 'Manual Start'
				rst = '%02d:%02d:%02d.%02d' % (st.hour, st.minute, st.second, int(st.microsecond / 10000.0))
			changed |= SetLabel( self.raceStartMessage, rstSource )
			changed |= SetLabel( self.raceStartTime, rst )
			if changed:
				Utils.LayoutChildResize( self.raceStartTime )
				
		wx.CallAfter( self.refreshLaps )
		wx.CallAfter( self.refreshRiderLapCountList )
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	numKeypad = NumKeypad(mainWin)
	mainWin.Show()
	app.MainLoop()


