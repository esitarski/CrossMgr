import wx
import datetime

import Model
import Utils
import Undo
import bisect
from GetResults import GetEntries
from HighPrecisionTimeEdit import HighPrecisionTimeEdit
from roundbutton import RoundButton

def RestartAfterLap( race, lap, rfidDelay ):
	entries = [e for e in GetEntries(None) if e.lap <= lap and e.lap <= race.getCategoryNumLaps(e.num)]
	
	history = [ [] ]
	numSeen = set()
	lapCur = 0
	for e in entries:
		if e.num in numSeen:
			numSeen.clear()
			lapCur += 1
			history.append( [] )
		history[lapCur].append( e )
		numSeen.add( e.num )
	
	# Remove any times after the restart time.
	lastTime = { e.num:e.t for e in history[lap] }
	for num, rider in race.riders.items():
		del rider.times[bisect.bisect(rider.times, lastTime.get(num, 0.0)):]
		
	try:
		tRestart = history[lap][0].t
	except IndexError:
		tRestart = 0.0
	
	# Also, remove any recorded times from unmatched tags.
	if race.unmatchedTags:
		for tag, times in race.unmatchedTags:
			del times[bisect.bisect(times, tRestart):]
	
	# Restart the race.  Adjust the race start time to compensate for the restart.
	restartTime = datetime.datetime.now()
	race.startTime = restartTime - datetime.timedelta(seconds=tRestart)
	race.finishTime = None
	if race.enableJChipIntegration:
		race.rfidRestartTime = restartTime + datetime.timedelta( seconds=(rfidDelay or 0.0) )
	else:
		race.rfidRestartTime = None
	race.setChanged()

class Restart( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__(self, parent, id, title=_('Restart Race'))
		
		self.SetBackgroundColour( wx.Colour(255,255,255) )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		lapLabel = wx.StaticText( self, label=_("Restart after Lap") )
		self.lap = wx.Choice( self )
		
		hsLaps = wx.BoxSizer( wx.HORIZONTAL )
		hsLaps.Add( lapLabel, flag=wx.ALIGN_CENTER_VERTICAL )
		hsLaps.Add( self.lap, flag=wx.LEFT, border=4 )
		
		self.rfidDelayLabel = wx.StaticText( self, label=_("RFID Delay after Restart") )
		self.rfidDelayLabel.SetToolTip( _('Time Delay after Restart to resume RFID reads') )
		self.rfidDelay = HighPrecisionTimeEdit( self, display_seconds=True, display_milliseconds=False )
		
		hsRFID = wx.BoxSizer( wx.HORIZONTAL )
		hsRFID.Add( self.rfidDelayLabel, flag=wx.ALIGN_CENTER_VERTICAL )
		hsRFID.Add( self.rfidDelay, flag=wx.LEFT, border=4 )
				
		buttonSize = 220
		self.button = RoundButton( self, size=(buttonSize, buttonSize) )
		self.button.SetLabel( '\n'.join( _('Restart Now').split() ) )
		self.button.SetFontToFitLabel()
		self.button.SetForegroundColour( wx.Colour(0,128,0) )
		self.Bind(wx.EVT_BUTTON, self.onPress, self.button )
		
		self.cancelButton = wx.Button(self, wx.ID_CANCEL)
		self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)
		
		buttonSizer = wx.StdDialogButtonSizer()
		buttonSizer.AddButton( self.cancelButton )
		buttonSizer.Realize()
		
		vs.Add( hsLaps, flag=wx.ALL, border=8)
		vs.Add( hsRFID, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=8)
		vs.Add( self.button, flag=wx.ALL, border=16 )
		vs.Add( buttonSizer, flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=8)
		
		self.SetSizerAndFit( vs )
		
	def refresh( self ):
		race = Model.race
		self.rfidDelayLabel.Enable( race and race.enableJChipIntegration )
		self.rfidDelay.Enable( race and race.enableJChipIntegration )
		
		if not race or not race.isFinished() or race.isTimeTrial:
			self.lap.Set( [] )
			return
			
		entries = GetEntries(None)
		lapMax = max( e.lap for e in entries if not e.interp) if entries else 0
		choices = ['{}'.format(lap) for lap in range(max(0, lapMax-20), lapMax+1)]
		self.lap.Set( choices )
		self.lap.SetSelection( len(choices)-1 )
		
		# Get median lap time.
		lapTimes = []
		last = {}
		for e in entries:
			if e.num in lapTimes:
				lapTimes.append( e.t - last[e.num] )
			last[e.num] = e.t
		lapTimes.sort()
		lapTimeMedian = lapTimes[len(lapTimes)//2] if lapTimes else 60.0
		self.rfidDelay.SetSeconds( min(5*60.0, lapTimeMedian * 0.75) )
		
	def onPress( self, event ):
		race = Model.race
		if not race or not race.isFinished() or race.isTimeTrial:
			return
		
		try:
			lap = int( self.lap.GetStringSelection() )
		except:
			return
			
		if not Utils.MessageOKCancel(self, _('Restart Race Now?\n\n'), _('Restart Race')):
			return
		
		Undo.undo.pushState()		
		RestartAfterLap( race, lap, self.rfidDelay.GetSeconds() )
		
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.refresh()
			mainWin.refreshWindows()
		
		self.OnOK( event )
	
	def OnOK( self, event ):
		self.commit()
		self.EndModal( wx.ID_OK )
		
	def OnCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

	def commit( self ):
		pass
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	restart = Restart(mainWin)
	Model.newRace()
	Model.race._populate()
	Model.race.finishTime = datetime.datetime.now()
	restart.refresh()
	mainWin.Show()
	restart.ShowModal()
	app.MainLoop()
	
