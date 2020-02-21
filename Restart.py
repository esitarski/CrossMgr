import wx
import datetime

import Model
import Utils
import Undo
import bisect
from GetResults import GetEntries
from roundbutton import RoundButton

def RestartAfterLap( race, lap ):
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
	race.restartTime = datetime.datetime.now()
	race.startTime = race.restartTime - datetime.timedelta(seconds=tRestart)
	race.finishTime = None
	race.setChanged()

class Restart( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__(self, parent, id, title=_('Restart Race'))
		
		self.SetBackgroundColour( wx.Colour(255,255,255) )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		buttonSize = 220
		self.button = RoundButton( self, size=(buttonSize, buttonSize) )
		self.button.SetLabel( '\n'.join( _('Restart Now').split() ) )
		self.button.SetFontToFitLabel()
		self.button.SetForegroundColour( wx.Colour(0,128,0) )
		self.Bind(wx.EVT_BUTTON, self.onPress, self.button )
		
		lapLabel = wx.StaticText( self, label=_("After Lap") )
		self.lap = wx.Choice( self )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( lapLabel, flag=wx.ALIGN_CENTER_VERTICAL )
		hs.Add( self.lap, flag=wx.LEFT, border=2 )
		
		self.cancelButton = wx.Button(self, wx.ID_CANCEL)
		self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)
		
		buttonSizer = wx.StdDialogButtonSizer()
		buttonSizer.AddButton( self.cancelButton )
		buttonSizer.Realize()
		
		vs.Add( hs, flag=wx.ALL, border=8)
		vs.Add( self.button, flag=wx.ALL, border=16 )
		vs.Add( buttonSizer, flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=8)
		
		self.SetSizerAndFit( vs )
		
	def refresh( self ):
		race = Model.race
		if not race or not race.isFinished() or race.isTimeTrial:
			self.lap.Set( [] )
			return
		entries = GetEntries(None)
		lapMax = max( e.lap for e in entries ) if entries else 0
		choices = ['{}'.format(lap) for lap in range(max(0, lapMax-20), lapMax+1)]
		self.lap.Set( choices )
		self.lap.SetSelection( len(choices)-1 )
		
	def onPress( self, event ):
		race = Model.race
		if not race or not race.isFinished() or race.isTimeTrial:
			return
		
		i = self.lap.GetSelection()
		if i == wx.NOT_FOUND:
			return
		
		try:
			lap = int( self.lap.GetString(i) )
		except:
			return
			
		if not Utils.MessageOKCancel(self, _('Restart Race Now?\n\n'), _('Restart Race')):
			return
		
		Undo.undo.pushState()		
		RestartAfterLap( race, lap )
		
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
	
