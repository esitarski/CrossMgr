import wx
import wx.grid		as gridlib
import Model
import Utils
from Animation import Animation
from FixCategories import FixCategories

class RaceAnimation( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		bs = wx.BoxSizer(wx.VERTICAL)

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )

		bs.Add( self.hbs )
		
		self.animation = Animation( self )
		bs.Add(self.animation, 2, flag=wx.GROW|wx.ALL, border=0 )

		self.playButton = wx.Button( self, wx.ID_ANY, 'Replay Race in 60 seconds' )
		self.Bind( wx.EVT_BUTTON, self.onPlay, self.playButton )
		bs.Add(self.playButton, 0, flag=wx.GROW|wx.ALL, border=0 )

		self.SetSizer(bs)
		
	def doChooseCategory( self, event ):
		if Model.race is not None:
			Model.race.raceAnimationCategory = self.categoryChoice.GetSelection()
		self.refresh()
	
	def onPlay( self, event ):
		self.refresh()
		self.animation.Animate(90)	# Run the animation in 90 seconds.
	
	def commit( self ):
			self.animation.StopAnimate()
	
	def refresh( self ):
		if not self.IsShown():
			self.animation.StopAnimate()
			return
		
		race = Model.getRace()
		if race is None:
			self.animation.SetData( None, 0 )
			self.animation.StopAnimate()
			self.playButton.Enable( True )
			return
		
		self.playButton.Enable( not race.isRunning() )
		
		catName = FixCategories( self.categoryChoice, getattr(race, 'raceAnimationCategory', 0) )

		results = race.getResultsList( catName )
		finishers = set( r.num for r in results )
		
		# Update the animation data.
		maxLap = race.getMaxLap()
		if race.numLaps is not None and race.numLaps < maxLap:
			maxLap = race.numLaps
		entries = race.interpolateLap( maxLap )
		entries = [e for e in entries if e.num in finishers]	# Trim the results to this category.
		animationData = {}
		for e in entries:
			if e.num not in animationData:
				animationData[e.num] = {'lapTimes': [], 'lastTime': None }
			animationData[e.num]['lapTimes'].append( e.t )

		for num, info in animationData.iteritems():
			rider = race[num]
			if rider.status != Model.Rider.Finisher:
				info['lastTime'] = rider.tStatus
			else:
				tLast = info['lapTimes'][-1]
				info['lastTime'] = tLast if not race.isRunning() or tLast >= race.minutes*60  else None
		
		self.animation.SetData( animationData, race.lastRaceTime() );
		if race.isRunning():
			if not self.animation.IsAnimating():
				self.animation.StartAnimateRealtime()
		else:
			self.animation.StopAnimate()
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	Model.getRace().finishRaceNow()
	raceAnimation = RaceAnimation(mainWin)
	raceAnimation.refresh()
	# raceAnimation.animation.Animate( 2*60 )
	mainWin.Show()
	app.MainLoop()