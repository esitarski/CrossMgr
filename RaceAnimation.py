import wx
import wx.grid		as gridlib
import Model
import Utils
from Animation import Animation
from FixCategories import FixCategories

def GetAnimationData( catName = 'All' ):
	race = Model.race
	results = race.getResultsList( catName )
	
	if not results:
		return None

	finishers = set( r.num for r in results )
	
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

	# Set the last times.
	for num, info in animationData.iteritems():
		rider = race[num]
		
		c = race.getCategory( num )
		try:
			info['category'] = c.name
		except:
			info['category'] = 'All'
		
		if rider.status != Model.Rider.Finisher:
			info['lastTime'] = rider.tStatus
		else:
			try:
				info['lastTime'] = info['lapTimes'][c.getNumLaps()]
			except:
				tLast = info['lapTimes'][-1]
				info['lastTime'] = tLast if not race.isRunning() or tLast >= race.minutes*60  else None
				
	return animationData
		

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
		
		self.animationSeconds = 90

		self.playButton = wx.Button( self, wx.ID_ANY, 'Replay Race in %d seconds' % self.animationSeconds )
		self.Bind( wx.EVT_BUTTON, self.onPlay, self.playButton )
		bs.Add(self.playButton, 0, flag=wx.GROW|wx.ALL, border=0 )

		self.SetSizer(bs)
		
	def doChooseCategory( self, event ):
		if Model.race is not None:
			Model.race.raceAnimationCategory = self.categoryChoice.GetSelection()
		self.refresh()
	
	def onPlay( self, event ):
		self.refresh()
		self.animation.Animate(self.animationSeconds)
	
	def commit( self ):
		race = Model.race
		if race and race.isRunning():
			self.animation.StopAnimate()
	
	def refresh( self ):
		race = Model.race
		if race is None:
			self.animation.SetData( None, 0 )
			self.animation.StopAnimate()
			self.playButton.Enable( True )
			return
		
		self.playButton.Enable( not race.isRunning() )
		catName = FixCategories( self.categoryChoice, getattr(race, 'raceAnimationCategory', 0) )
		animationData = GetAnimationData( catName )
		
		self.animation.SetData( animationData, race.lastRaceTime() )
		
		if race.isRunning():
			if not self.animation.IsAnimating():
				self.animation.StartAnimateRealtime()
	
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