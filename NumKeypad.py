import wx
import wx.lib.agw.gradientbutton as GB
import os
import wx.lib.intctrl
from wx.lib.stattext import GenStaticText 
import bisect
import Utils
from Utils import SetValue, SetLabel
import Model
import sys
from keybutton import KeyButton
from RaceHUD import RaceHUD

def MakeButton( parent, id=wx.ID_ANY, label='', style = 0, size=(-1,-1) ):
	'''
	btn = GB.GradientButton(parent, -1, None, label=label.replace('&',''), style=style|wx.NO_BORDER, size=size)
	btn.SetTopStartColour( 		wx.Colour(200,200,200) )
	btn.SetTopEndColour( 		wx.Colour(112,112,112) )
	btn.SetBottomStartColour( 	wx.Colour(112,112,112) )
	btn.SetBottomEndColour( 	wx.Colour( 32, 32, 32) )
	btn.SetBackgroundColour(	wx.Colour(255,255,255) )
	'''
	'''
	btn = AquaButton( parent, -1, None, label=label.replace('&',''), style=style|wx.NO_BORDER, size=size )
	btn.SetBackgroundColour( wx.Colour(0, 128, 192) )
	btn.SetHoverColour( wx.Colour(128, 128, 255) )
	'''
	btn = KeyButton( parent, -1, None, label=label.replace('&',''), style=style|wx.NO_BORDER, size=size)
	return btn

class NumKeypad( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		gbs = wx.GridBagSizer(4, 4)
		
		self.bell = None
		self.tada = None
		
		self.SetBackgroundColour( wx.WHITE )
		
		fontSize = 24
		font = wx.Font(fontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
		dc = wx.WindowDC( self )
		dc.SetFont( font )
		wNum, hNum = dc.GetTextExtent( '999' )
		wNum += 8
		hNum += 8

		rowCur = 1
		
		self.numEdit = wx.lib.intctrl.IntCtrl( self, 20, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER, value=None, allow_none=True, min=0, max=9999 )
		self.Bind( wx.EVT_TEXT_ENTER, self.onEnterPress, self.numEdit )
		self.numEdit.SetFont( font )
		gbs.Add( self.numEdit, pos=(rowCur,0), span=(1,3), flag=wx.EXPAND )
		self.num = []
		self.num.append( MakeButton(self, id=0, label='&0', style=wx.BU_EXACTFIT) )
		self.num[-1].Bind( wx.EVT_BUTTON, lambda event, aValue = 0 : self.onNumPress(event, aValue) )
		gbs.Add( self.num[0], pos=(4+rowCur,0), span=(1,2), flag=wx.EXPAND )

		#numButtonStyle = wx.BU_EXACTFIT
		numButtonStyle = 0
		
		for i in xrange(0, 9):
			self.num.append( MakeButton(self, id=wx.ID_ANY, label='&' + str(i+1), style=numButtonStyle, size=(wNum,hNum)) )
			self.num[-1].Bind( wx.EVT_BUTTON, lambda event, aValue = i+1 : self.onNumPress(event, aValue) )
			j = 8-i
			gbs.Add( self.num[-1], pos=(int(j/3)+1 + rowCur, 2-j%3) )
		
		for n in self.num:
			n.SetFont( font )
		
		self.delBtn = MakeButton(self, id=wx.ID_DELETE, label='&Del', style=numButtonStyle, size=(wNum,hNum))
		self.delBtn.SetFont( font )
		self.delBtn.Bind( wx.EVT_BUTTON, self.onDelPress )
		gbs.Add( self.delBtn, pos=(4+rowCur,2) )
		
		self.enterBtn= MakeButton(self, id=0, label='&Enter', style=wx.EXPAND|wx.GROW)
		self.enterBtn.SetFont( font )
		gbs.Add( self.enterBtn, pos=(5+rowCur,0), span=(1,3), flag=wx.EXPAND )
		self.enterBtn.Bind( wx.EVT_BUTTON, self.onEnterPress )
	
		self.dnfBtn= MakeButton(self, id=wx.ID_ANY, label='DN&F', style=wx.EXPAND|wx.GROW)
		self.dnfBtn.SetFont( font )
		gbs.Add( self.dnfBtn, pos=(7+rowCur,0), span=(1,3), flag=wx.EXPAND )
		self.dnfBtn.Bind( wx.EVT_BUTTON, self.onDNFPress )
	
		self.pullBtn= MakeButton(self, id=wx.ID_ANY, label='&Pull', style=wx.EXPAND|wx.GROW)
		self.pullBtn.SetFont( font )
		gbs.Add( self.pullBtn, pos=(8+rowCur,0), span=(1,3), flag=wx.EXPAND )
		self.pullBtn.Bind( wx.EVT_BUTTON, self.onPullPress )
	
		#------------------------------------------------------------------------------
		# Race time.
		rowCur = 0
		colCur = 0
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL

		self.raceTime = wx.StaticText(self, wx.ID_ANY, '00:00')
		self.raceTime.SetFont( wx.Font(36, wx.DEFAULT, wx.NORMAL, wx.NORMAL) )
		self.raceTime.SetDoubleBuffered(True)
		gbs.Add( self.raceTime, pos=(0, 3), span=(1,2), flag=wx.ALIGN_CENTRE | wx.ALIGN_CENTRE_VERTICAL )
		self.refreshRaceTime()
		
		#------------------------------------------------------------------------------
		# Lap Management.
		fontSize = 14
		font = wx.Font(fontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

		rowCur = 1
		colCur = 4
		self.automaticManualChoice = wx.Choice( self, id=wx.ID_ANY, choices = ['Automatic', 'Manual'], size=(132,-1) )
		self.Bind(wx.EVT_CHOICE, self.doChooseAutomaticManual, self.automaticManualChoice)
		self.automaticManualChoice.SetSelection( 0 )
		self.automaticManualChoice.SetFont( font )
		gbs.Add( self.automaticManualChoice, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_LEFT )
		rowCur += 1
		
		label = wx.StaticText(self, wx.ID_ANY, 'Total Laps:')
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.numLaps = wx.Choice( self, 21, choices = [''] + [str(x) for x in xrange(2,21)], size=(64,-1) )
		self.numLaps.SetSelection( 0 )
		self.numLaps.SetFont( font )
		self.numLaps.SetDoubleBuffered( True )
		self.Bind(wx.EVT_CHOICE, self.doChangeNumLaps, self.numLaps)
		gbs.Add( self.numLaps, pos=(rowCur, colCur+1), span=(1,1) )
		rowCur += 1
		
		label = wx.StaticText(self, wx.ID_ANY, "Est Finish:")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.leadersFinishTime = wx.StaticText(self, wx.ID_ANY, "")
		self.leadersFinishTime.SetFont( font )
		gbs.Add( self.leadersFinishTime, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1

		label = wx.StaticText(self, wx.ID_ANY, "Avg Lap Time:")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.leadersLapTime = wx.StaticText(self, wx.ID_ANY, "")
		self.leadersLapTime.SetFont( font )
		gbs.Add( self.leadersLapTime, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1

		label = wx.StaticText(self, wx.ID_ANY, "80% Time Limit:")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.rule80Time = wx.StaticText(self, wx.ID_ANY, "")
		self.rule80Time.SetFont( font )
		gbs.Add( self.rule80Time, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1

		label = wx.StaticText(self, wx.ID_ANY, "Completing Lap:")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.lapCompleting = wx.StaticText(self, wx.ID_ANY, "")
		self.lapCompleting.SetFont( font )
		gbs.Add( self.lapCompleting, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1

		label = wx.StaticText(self, wx.ID_ANY, "Show Laps to Go:")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.lapsToGo = wx.StaticText(self, wx.ID_ANY, "")
		self.lapsToGo.SetFont( font )
		gbs.Add( self.lapsToGo, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1

		label = wx.StaticText(self, wx.ID_ANY, "Leader ETA:")
		label.SetFont( font )
		gbs.Add( label, pos=(rowCur, colCur), span=(1,1), flag=labelAlign )
		self.timeToLeader = GenStaticText(self, wx.ID_ANY, "")
		self.timeToLeader.SetFont( font )
		self.timeToLeader.SetDoubleBuffered(True)
		gbs.Add( self.timeToLeader, pos=(rowCur, colCur+1), span=(1,1), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_LEFT )
		rowCur += 1

		self.message = wx.StaticText(self, wx.ID_ANY, "")
		self.message.SetFont( font )
		gbs.Add( self.message, pos=(rowCur, colCur), span=(1,2), flag=wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE )
		rowCur += 1

		self.raceHUD = RaceHUD( self, wx.ID_ANY )
		gbs.Add( self.raceHUD, pos=(rowCur, 0), span=(2, 7), flag=wx.EXPAND )
		rowCur += 1
		
		self.SetSizer( gbs )
		self.isEnabled = True
		
	def refreshTimeToLeader( self ):
		# Assumes Model is locked.
		race = Model.race
		timeToLeader = '  '
		bgColour = wx.WHITE
		if race is not None:
			numLaps, leaderLapsToGo, lapCompleting, leadersExpectedLapTime, leaderNum, expectedRaceFinish, isAutomatic = self.getLapInfo()
			if not leaderLapsToGo:
				leaderLapsToGo = -1
				
			nLeader, tLeader = race.getTimeToLeader()
			
			# Update the RaceHUD
			tCur = race.curRaceTime()
			if not numLaps or numLaps < 2 or not race.isRunning():
				self.raceHUD.SetData()
			else:
				leaderTimes = race.getLeaderTimesNums()[0][1:numLaps+1]
				leaderTimes.append( race.getLastFinisherTime() )
				self.raceHUD.SetData( nowTime = tCur, lapTimes = leaderTimes, leader = leaderNum )
				
			if tLeader is not None:
			
				if tLeader <= 3.0:
					if not self.tada:
						self.tada = Utils.PlaySound( 'tada.wav' )
				else:
					self.tada = None
						
				# update the Time to Leader.
				leaderLapsToGo -= 1
				if leaderLapsToGo >= 0:
					timeToLeader = '%s (%d to see %d to go)' % (Utils.formatTime(tLeader), nLeader, leaderLapsToGo)
					
					# Play the bell reminder.
					if leaderLapsToGo == 1 and tLeader <= 10.0:
						if not self.bell:
							self.bell = Utils.PlaySound( 'bell.wav' )
					else:
						self.bell = None
						
				else:
					timeToLeader = '%s (%d)' % (Utils.formatTime(tLeader), nLeader)
			
				if tLeader < 30.0:
					bgColour = wx.GREEN
				
		self.timeToLeader.SetBackgroundColour( bgColour )
		self.timeToLeader.SetLabel( timeToLeader )

	def refreshRaceTime( self ):
		with Model.lock:
			race = Model.race
			if race is not None:
				tStr = Utils.formatTime( race.lastRaceTime() )
				self.refreshTimeToLeader()
			else:
				tStr = ''
			self.raceTime.SetLabel( '  ' + tStr )
			
		mainWin = Utils.getMainWin()
		if mainWin is not None:
			try:
				mainWin.forecastHistory.refreshRule80()
				mainWin.refreshRaceAnimation()
			except:
				pass
	
	def doChangeNumLaps( self, event ):
		with Model.lock:
			race = Model.race
			if race and race.isFinished():
				try:
					race.numLaps = int(self.numLaps.GetString(self.numLaps.GetSelection()))
				except ValueError:
					pass
		self.refreshLaps()
	
	def doChooseAutomaticManual( self, event ):
		with Model.lock:
			race = Model.race
			if race is not None:
				race.automaticManual = self.automaticManualChoice.GetSelection()
		self.refreshLaps()
		
	def onNumPress( self, event, value ):
		self.numEdit.SetInsertionPointEnd()
		t = self.numEdit.GetValue()
		if not t:
			t = 0
		t = t * 10 + value
		t %= 10000000
		self.numEdit.SetValue( t )
		self.numEdit.SetInsertionPointEnd()
		
	def onDelPress( self, event ):
		t = self.numEdit.GetValue()
		if t is not None:
			self.numEdit.SetValue( int(t//10) if t > 9 else None )
	
	def getRiderNum( self ):
		num = self.numEdit.GetValue()
		if num is not None:
			mask = Model.race.getCategoryMask() if Model.race else None
			if mask:	# Add common prefix numbers to the entry.
				s = str(num)
				dLen = len(mask) - len(s)
				if dLen > 0:
					sAdjust = mask[:dLen] + s
					sAdjust = sAdjust.replace( '.', '0' )
					num = int(sAdjust)
		return num
	
	def onEnterPress( self, event = None ):
		num = self.getRiderNum()
		if num is not None:
			mainWin = Utils.getMainWin()
			if mainWin is not None:
				mainWin.forecastHistory.logNum(num)
			else:
				self.refreshLaps()
				self.numEdit.SetValue( None )
	
	def onDNFPress( self, event ):
		race = Model.race
		if not race:
			return
			
		num = self.getRiderNum()
		if num is None:
			return
		if not Utils.MessageOKCancel(self, 'DNF rider %d?' % num, 'Confirm Did Not FINISH' ):
			return
		rider = race.getRider( num )
		rider.setStatus( Model.Rider.DNF )
		self.numEdit.SetValue( None )
		Model.resetCache()
		Utils.refresh()
	
	def onPullPress( self, event ):
		race = Model.race
		if not race:
			return
			
		num = self.getRiderNum()
		if num is None:
			return
		if not Utils.MessageOKCancel(self, 'Pull rider %d?' % num, 'Confirm PULL Rider', iconMask = wx.ICON_QUESTION):
			return
		rider = race.getRider( num )
		rider.setStatus( Model.Rider.Pulled )
		self.numEdit.SetValue( None )
		Model.resetCache()
		Utils.refresh()
	
	def onDNSPress( self, event ):
		race = Model.race
		if not race:
			return
			
		num = self.getRiderNum()
		if num is None:
			return
		if not Utils.MessageOKCancel(self, 'DNS rider %d?' % num, 'Confirm Did Not START'):
			return
		rider = race.getRider( num )
		rider.setStatus( Model.Rider.DNS )
		self.numEdit.SetValue( None )
		Model.resetCache()
		Utils.refresh()
	
	def resetLaps( self, enable = False ):
		# Assumes Model is locked.
		infoFields = [
				self.leadersFinishTime,
				self.leadersLapTime,
				self.rule80Time,
				self.lapCompleting,
				self.lapsToGo,
				self.timeToLeader,
				self.message
				]
				
		for f in infoFields:
			f.Enable( enable )
				
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
			SetLabel( self.lapCompleting, '1' )
			SetLabel( self.message, 'Collecting Data' )
		else:
			self.numLaps.SetItems( [ str(race.numLaps) ] )
			self.numLaps.SetSelection( 0 )
			SetLabel( self.leadersFinishTime, 'Leader %s   Last Rider %s' %
							(Utils.formatTime(race.getLeaderTime()), Utils.formatTime(race.getLastFinisherTime())) )
			SetLabel( self.leadersLapTime, Utils.formatTime(race.getLeaderLapTime()) )
			rule80Time = race.getRule80CountdownTime()
			SetLabel( self.rule80Time, Utils.formatTime(rule80Time) if rule80Time else '' )
			SetLabel( self.lapCompleting, str(race.numLaps if race.numLaps is not None else 0) )
			SetLabel( self.lapsToGo, '0' )
			SetLabel( self.message, '' )
			
		self.refreshTimeToLeader()
	
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
			
		raceFinishTime = leaderTimes[laps]
		leaderNum = leaderNums[laps]
		
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
	
	def refreshLaps( self ):
		with Model.lock:
			race = Model.race
			enable = True if race is not None and race.isRunning() else False
			
			self.automaticManualChoice.Enable( enable )
			self.automaticManualChoice.SetSelection( getattr(race, 'automaticManual', 0) )
			
			# Allow the number of laps to be changed after the race is finished.
			numLapsEnable = True if race is not None and (race.isRunning() or race.isFinished()) else False
			self.numLaps.Enable( numLapsEnable )
			if numLapsEnable != enable:
				self.resetLaps()
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
			
			# Set the projected finish time and laps.
			if lapCompleting >= 2 or not isAutomatic:
				SetLabel( self.leadersFinishTime, 'Leader %s   Last Rider %s' %
					(Utils.formatTime(expectedRaceFinish), Utils.formatTime(race.getLastFinisherTime())) )
				SetLabel( self.leadersLapTime, Utils.formatTime(leadersExpectedLapTime) )
				rule80Time = race.getRule80CountdownTime()
				SetLabel( self.rule80Time, Utils.formatTime(rule80Time) if rule80Time else '' )
				SetLabel( self.lapsToGo, str(lapsToGo) )
				SetLabel( self.lapCompleting, str(lapCompleting) )
				
				if   lapsToGo == 2 and race.isLeaderExpected():
					SetLabel( self.message, '%d: Leader Bell Lap Alert' % leaderNum )
				elif lapsToGo == 1 and race.isLeaderExpected():
					SetLabel( self.message, '%d: Leader Finish Alert' % leaderNum )
				else:
					SetLabel( self.message, raceMessage.get(lapsToGo, '') )
				race.numLaps = laps
				
				if race.allRidersFinished():
					race.finishRaceNow()
			else:
				if self.numLaps.GetSelection() != 0:
					self.numLaps.SetSelection( 0 )
				SetLabel( self.leadersFinishTime, '' )
				SetLabel( self.leadersLapTime, '' )
				SetLabel( self.lapsToGo, '' )
				SetLabel( self.lapCompleting, str(lapCompleting) )
				SetLabel( self.message, 'Collecting Data' )
				race.numLaps = None
			
		self.refreshTimeToLeader()
		
	def refresh( self ):
		wx.CallAfter( self.numEdit.SetFocus )
		with Model.lock:
			race = Model.race
			enable = True if race is not None and race.isRunning() else False
			if self.isEnabled != enable:
				for b in self.num:
					b.Enable( enable )
				for b in [self.numEdit, self.delBtn, self.enterBtn, self.dnfBtn, self.pullBtn]:
					b.Enable( enable )
				self.isEnabled = enable
			if not enable:
				self.numEdit.SetValue( None )
		self.refreshLaps()
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,700))
	numKeypad = NumKeypad(mainWin)
	mainWin.Show()
	app.MainLoop()


