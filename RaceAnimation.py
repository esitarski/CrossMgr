import wx
import wx.grid		as gridlib
import Model
import Utils
import string
import re
from gettext import gettext as _
from Animation import Animation
from GeoAnimation import GeoAnimation
from FixCategories import FixCategories
from ReadSignOnSheet import IgnoreFields
from GetResults import GetResults, GetCategoryDetails

statusNames = Model.Rider.statusNames

def GetAnimationData( category = None, getExternalData = False ):
	results = GetResults( category, getExternalData )
	if not results:
		return {}
	
	animationData = {}
	
	ignoreFields = set(['pos', 'num', 'gap', 'laps', 'lapTimes'])
	with Model.LockRace() as race:
		for rr in results:
			info = { 'flr': race.getCategory(rr.num).firstLapRatio }
			for a in dir(rr):
				if a[0] == '_' or a in ignoreFields:
					continue
				if a == 'raceTimes':
					info['raceTimes'] = getattr(rr, a)
					bestLaps = race.getNumBestLaps( rr.num )
					if bestLaps is not None and len(info['raceTimes']) > bestLaps:
						info['raceTimes'] = info['raceTimes'][:bestLaps+1]
				elif a == 'status':
					info['status'] = statusNames[getattr(rr, a)]
				else:
					info[a] = getattr( rr, a )
					
			animationData[rr.num] = info
		
	return animationData
		
class NumListValidator(wx.PyValidator):
    def __init__(self, pyVar=None):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return NumListValidator()

    def Validate(self, win):
		tc = self.GetWindow()
		val = tc.GetValue()

		for x in val:
			if x != ',' and x not in string.digits:
				return False;

		return True

    def OnChar(self, event):
		key = event.GetKeyCode()
		try:
			if key <= wx.WXK_SPACE or key == wx.WXK_DELETE or chr(key) == ',' or key > 255 or chr(key) in string.digits:
				event.Skip()
				return
		except:
			event.Skip()
			return

		# Returning without calling event.Skip eats the event before it gets to the text control
		return

class RaceAnimation( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)
		bs = wx.BoxSizer(wx.VERTICAL)

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, _('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice )
		self.showGPX = wx.RadioButton( self, wx.ID_ANY, _("GPX Track"), style=wx.RB_GROUP )
		self.showGPX.Enable( False )
		self.Bind(wx.EVT_RADIOBUTTON, self.changeTrack, self.showGPX )
		self.showOval = wx.RadioButton( self, wx.ID_ANY, _("Oval Track") )
		self.showOval.SetValue( True )
		self.isShowingOval = True
		self.Bind(wx.EVT_RADIOBUTTON, self.changeTrack, self.showOval )
		self.finishTop = wx.CheckBox( self, wx.ID_ANY, _("Finish on Top") )
		self.Bind(wx.EVT_CHECKBOX, self.doFinishTop, self.finishTop)
		self.reverseDirection = wx.Button( self, wx.ID_ANY, _("Reverse Direction") )
		self.Bind(wx.EVT_BUTTON, self.doReverseDirection, self.reverseDirection)
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showGPX, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.showOval, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.finishTop, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border = 4 )
		self.hbs.Add( self.reverseDirection, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border = 4 )

		bs.Add( self.hbs )
		
		self.animationTrack = Animation( self )
		self.animationGeo = GeoAnimation( self )
		self.animationGeo.Hide()
		
		self.animation = self.animationTrack
		bs.Add(self.animation, 2, flag=wx.GROW|wx.ALL, border=0 )
		
		self.animationSeconds = self.animationSecondsNormal = 90

		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.rewindButton = wx.Button( self, wx.ID_ANY, _('Rewind') )
		self.Bind( wx.EVT_BUTTON, self.onRewind, self.rewindButton )
		hs.Add(self.rewindButton, 0, flag=wx.GROW|wx.ALL, border=2 )
		self.playStopButton = wx.Button( self, wx.ID_ANY, _('Play') )
		self.Bind( wx.EVT_BUTTON, self.onPlayStop, self.playStopButton )
		hs.Add(self.playStopButton, 0, flag=wx.GROW|wx.ALL, border=2 )
		hs.Add( wx.Size(20, 1) )
		self.playbackSpeed = wx.StaticText(self, wx.ID_ANY, _('Playback Speed:') )
		hs.Add(self.playbackSpeed, 0, flag=wx.ALIGN_CENTER|wx.ALL, border=2 )
		
		self.speed = []
		for i in xrange(5):
			b = wx.RadioButton( self, wx.ID_ANY, name='PlaybackSpeed' )
			self.speed.append( b )
			self.Bind( wx.EVT_RADIOBUTTON, self.onPlaybackSpeed, b )
			hs.Add( b, 0, flag=wx.GROW|wx.ALL, border = 2 )
		self.speed[int(len(self.speed)/2)].SetValue( True )
		
		bs.Add( hs, 0, flag=wx.GROW|wx.ALL, border = 0 )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.watchText = wx.StaticText( self, wx.ID_ANY, _('Highlight Numbers:') )
		hs.Add( self.watchText, 0, flag=wx.ALIGN_CENTER|wx.ALL, border = 2 )
		
		self.watch = wx.TextCtrl( self, wx.ID_ANY, validator=NumListValidator(), style=wx.PROCESS_ENTER )
		self.watch.Bind( wx.EVT_TEXT_ENTER, self.onUpdateWatch )
		hs.Add( self.watch, 1, flag = wx.GROW|wx.ALL, border = 2 )
		
		self.updateWatch = wx.Button( self, wx.ID_ANY, _('Update') )
		self.updateWatch.Bind( wx.EVT_BUTTON, self.onUpdateWatch )
		hs.Add( self.updateWatch, 0, flag = wx.GROW|wx.ALL, border = 2 )
		
		self.controls = [self.rewindButton, self.playStopButton, self.playbackSpeed]
		self.controls.extend( self.speed )
		
		bs.Add( hs, 0, flag=wx.GROW|wx.ALL, border = 0 )

		self.SetSizer(bs)

	def changeTrack( self, event ):
		with Model.LockRace() as race:
			if not race:
				return
			geoTrack = getattr( race, 'geoTrack', None ) if race else None
		self.setAnimationType( geoTrack )
		self.refresh()
		
	def setAnimationType( self, geoTrack = None ):
		needGeo = (geoTrack is not None and not self.showOval.GetValue())
		haveGeo = (self.animation.course == 'geo')
		
		if needGeo != haveGeo:
			# Swap the animation object.
			# Find the existing animation widget
			bs = self.GetSizer()
			i = (i for i, c in enumerate(bs.GetChildren()) if c.GetWindow() == self.animation).next()

			if self.playStopButton.GetLabel() == _('Play'):
				self.onPlayStop()
			self.onRewind()
			
			newAnimation = self.animationGeo if needGeo else self.animationTrack
			bs.Insert(i, newAnimation, 2, flag=wx.GROW|wx.ALL, border=0 )
			bs.RemovePos( i + 1 )
			
			self.animation.Hide()
			self.animation = newAnimation
			self.animationGeo.SetGeoTrack( geoTrack )
			self.animation.Show( True )
			
			self.finishTop.Enable( not needGeo )
			self.reverseDirection.Enable( True )
			bs.Layout()
			with Model.LockRace() as race:
				race.showOval = (not needGeo)
			
		self.showGPX.Enable( (geoTrack is not None) )
		
		self.showOval.SetValue( not needGeo )
		self.showGPX.SetValue( needGeo )
		
	def doFinishTop( self, event ):
		with Model.LockRace() as race:
			if not race:
				return
			race.finishTop = event.IsChecked()
			race.reverseDirection = (False if getattr(race, 'reverseDirection', True) else True)
			race.setChanged()
		wx.CallAfter( self.refresh )
	
	def doReverseDirection( self, event ):
		with Model.LockRace() as race:
			if not race:
				return
			if self.showGPX.IsEnabled() and self.showGPX.GetValue():
				if getattr(race, 'geoTrack', None):
					race.geoTrack.reverse()
					self.animationGeo.SetGeoTrack( race.geoTrack )
			else:
				race.reverseDirection = (False if getattr(race, 'reverseDirection', True) else True)
			race.setChanged()
			
		wx.CallAfter( self.refresh )
		
	def	setNumSelect( self, num ):
		self.watch.SetValue( '{}'.format(num) if num else '' )
		self.onUpdateWatch( None )
		
	def doChooseCategory( self, event ):
		Utils.setCategoryChoice( self.categoryChoice.GetSelection(), 'raceAnimationCategory' )
		self.refresh()
	
	def onPlaybackSpeed( self, event ):
		b = event.GetEventObject()
		i = self.speed.index(b) - len(self.speed)/2
		self.animationSeconds = self.animationSecondsNormal
		factor = 0.65
		while i < 0:
			self.animationSeconds /= factor
			i += 1
		while i > 0:
			self.animationSeconds *= factor
			i -= 1
		self.animation.Animate( self.animationSeconds, self.animation.tMax, self.animation.t )
	
	def onUpdateWatch( self, event ):
		value = self.watch.GetValue()
		value = re.sub( ' ', ',', value )
		value = re.sub( '[^\d,]', '', value )
		value = re.sub( ',+', ',', value )
		try:
			numsToWatch = set( int(n) for n in value.split(',') )
		except:
			numsToWatch = set()

		self.animation.SetNumsToWatch( numsToWatch )
		self.watch.SetValue( value )
	
	def onPlayStop( self, event = None ):
		if self.animation.IsAnimating():
			self.animation.SuspendAnimate()
			self.playStopButton.SetLabel( _('Play') )
		else:
			self.animation.Animate( self.animationSeconds, self.animation.tMax, self.animation.t )
			self.playStopButton.SetLabel( _('Stop') )
	
	def onRewind( self, event = None ):
		self.animation.Animate( self.animationSeconds, None, self.getStartTime(self.animation.data) )
		self.animation.SuspendAnimate()
		self.playStopButton.SetLabel( _('Play') )
	
	def commit( self ):
		race = Model.race
		if race and race.isRunning():
			self.animation.StopAnimate()
	
	def getStartTime( self, animationData ):
		if not animationData:
			return 0
		t = 999999
		for info in animationData.itervalues():
			try:
				t = min( t, info['raceTimes'][0] )
			except:
				pass
		return t
	
	def refresh( self ):
		with Model.LockRace() as race:
			enabled = (race is None) or not race.isRunning()
			for w in self.controls:
				w.Enable( enabled )
				
			if race is None:
				self.setAnimationType( None )
				self.animation.SetData( None, 0 )
				self.animation.SetOptions()
				self.animation.StopAnimate()
				return
			
			self.showOval.SetValue( getattr(race, 'showOval', True) )
			self.showGPX.SetValue( not getattr(race, 'showOval', True) )
			self.animationGeo.SetGeoTrack( getattr(race, 'geoTrack', None ) )
			
			self.setAnimationType( getattr(race, 'geoTrack', None) )
			category = FixCategories( self.categoryChoice, getattr(race, 'raceAnimationCategory', 0) )
			self.hbs.Layout()
			raceTime = race.lastRaceTime() if race.isRunning() else self.animation.t
			raceIsRunning = race.isRunning()
			
		self.finishTop.SetValue( getattr(race, 'finishTop', False) )
		
		animationData = GetAnimationData( category, True )
		self.animation.SetData( animationData, raceTime, GetCategoryDetails() )
		self.animation.SetOptions( getattr(race, 'reverseDirection', False), getattr(race, 'finishTop', False) )
		if raceIsRunning:
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
	raceAnimation.animation.Animate( 2*60 )
	raceAnimation.animation.SuspendAnimate()
	mainWin.Show()
	app.MainLoop()
