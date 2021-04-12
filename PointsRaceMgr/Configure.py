import wx
import wx.adv
import wx.lib.masked.numctrl as NC
import wx.lib.intctrl as IC
import sys
import os
import re
import datetime

import Utils
import Model
import Version

class Configure( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=(200,200) ):
		super().__init__(parent, id, size=size)
		
		self.SetBackgroundColour( wx.WHITE )
		self.SetDoubleBuffered(True)

		self.inRefresh = False
		
		#-----------------------------------------------------------------------
		self.vbs = wx.BoxSizer( wx.VERTICAL )
		
		self.gbs = wx.GridBagSizer( 4, 4 )
		
		#--------------------------------------------------------------------------------------------------------------
		label = wx.StaticText( self, label='Race Name:' )
		self.gbs.Add( label, pos=(0, 0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER )
		ctrl.Bind(wx.EVT_TEXT, self.onChange)
		self.gbs.Add( ctrl, pos=(0, 1), span=(1,5), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND )
		self.nameLabel = label
		self.nameCtrl = ctrl
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		label = wx.StaticText( self, label='Date:' )
		hs.Add( label, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = wx.adv.DatePickerCtrl( self, style = wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY, size=(132,-1) )
		ctrl.Bind( wx.adv.EVT_DATE_CHANGED, self.onChange )
		hs.Add( ctrl, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4 )
		self.dateLabel = label
		self.dateCtrl = ctrl
		
		label = wx.StaticText( self, label='Communiqu\u00E9:' )
		hs.Add( label, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER )
		ctrl.Bind(wx.EVT_TEXT, self.onChange)
		hs.Add( ctrl, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=4 )
		self.communiqueLabel = label
		self.communiqueCtrl = ctrl
		
		self.gbs.Add( hs, pos=(0, 6), span=(1, 3) )
		
		#--------------------------------------------------------------------------------------------------------------
		label = wx.StaticText( self, label='Category:' )
		self.gbs.Add( label, pos=(1, 0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER )
		ctrl.Bind(wx.EVT_TEXT, self.onChange)
		self.gbs.Add( ctrl, pos=(1, 1), span=(1,5), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND )
		self.categoryLabel = label
		self.categoryCtrl = ctrl
		
		label = wx.StaticText( self, label='Rank By:', style = wx.ALIGN_RIGHT )
		self.gbs.Add( label, pos=(1, 6), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = wx.Choice( self, choices=[
				'Points then Finish Order',
				'Laps Completed, Points then Finish Order',
				'Laps Completed, Points, Num Wins then Finish Order'
			]
		)
		ctrl.SetSelection( 0 )
		self.Bind(wx.EVT_CHOICE, self.onChange, ctrl)
		self.gbs.Add( ctrl, pos=(1, 7), span=(1, 2), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.rankByLabel = label
		self.rankByCtrl = ctrl

		#--------------------------------------------------------------------------------------------------------------
		label = wx.StaticText( self, label='Total:' )
		self.gbs.Add( label, pos=(2, 0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = IC.IntCtrl( self, min=1, max=300, value=1, limited=True, style=wx.ALIGN_RIGHT, size=(64,-1) )
		ctrl.Bind(IC.EVT_INT, self.onChange)
		self.gbs.Add( ctrl, pos=(2, 1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )
		unitsLabel = wx.StaticText( self, label='laps' )
		self.gbs.Add( unitsLabel, pos=(2, 2), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.lapsLabel = label
		self.lapsUnitsLabel = unitsLabel
		self.lapsCtrl = ctrl
		
		#--------------------------------------------------------------------------------------------------------------
		label = wx.StaticText( self, label='Start Laps:' )
		self.gbs.Add( label, pos=(2, 3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = IC.IntCtrl( self, min=0, max=300, value=0, limited=True, style=wx.ALIGN_RIGHT, size=(40,-1) )
		ctrl.Bind(IC.EVT_INT, self.onChange)
		self.gbs.Add( ctrl, pos=(2, 4), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.startLapsLabel = label
		self.startLapsCtrl = ctrl
		
		ctrl = wx.StaticText( self, -1, 'Distance: 10.0m' )
		self.gbs.Add( ctrl, pos=(2, 5), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
		self.distanceCtrl = ctrl

		label = wx.StaticText( self, label='Points for Place:', style = wx.ALIGN_RIGHT )
		self.gbs.Add( label, pos=(2, 6), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = wx.TextCtrl( self )
		ctrl.Bind(wx.EVT_TEXT, self.onChange)
		self.gbs.Add( ctrl, pos=(2, 7), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.pointsForPlaceLabel = label
		self.pointsForPlaceCtrl = ctrl

		label = wx.CheckBox( self, label='Double Points on Last Sprint' )
		self.gbs.Add( label, pos=(2, 8), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = label
		ctrl.Bind( wx.EVT_CHECKBOX, self.onChange )
		self.doublePointsForLastSprintLabel = label
		self.doublePointsForLastSprintCtrl = ctrl
		
		#--------------------------------------------------------------------------------------------------------------
		label = wx.StaticText( self, label='Sprint Every:' )
		self.gbs.Add( label, pos=(3, 0), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = IC.IntCtrl( self, min=1, max=300, value=1, limited=True, style=wx.ALIGN_RIGHT, size=(40,-1) )
		ctrl.Bind(IC.EVT_INT, self.onChange)
		self.gbs.Add( ctrl, pos=(3, 1), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND )
		unitsLabel = wx.StaticText( self, label='laps' )
		self.gbs.Add( unitsLabel, pos=(3, 2), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.sprintEveryLabel = label
		self.sprintEveryCtrl = ctrl
		self.sprintEveryUnitsLabel = unitsLabel
		
		label = wx.StaticText( self, label='Course Len:' )
		self.gbs.Add( label, pos=(3, 3), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		
		ctrl = NC.NumCtrl( self, min = 0, integerWidth=3, fractionWidth=2, style=wx.ALIGN_RIGHT, size=(40,-1), useFixedWidthFont=False )
		ctrl.SetAllowNegative(False)
		ctrl.Bind(wx.EVT_TEXT, self.onChange)
		self.gbs.Add( ctrl, pos=(3, 4), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )
		
		unitCtrl = wx.Choice( self, choices=['m', 'km'] )
		unitCtrl.SetSelection( 0 )
		unitCtrl.Bind(wx.EVT_CHOICE, self.onChange)
		self.gbs.Add( unitCtrl, pos=(3, 5), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.courseLengthLabel = label
		self.courseLengthCtrl = ctrl
		self.courseLengthUnitCtrl = unitCtrl

		label = wx.StaticText( self, label='+/- Lap Points:' )
		self.gbs.Add( label, pos=(3, 6), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = IC.IntCtrl( self, min=0, max=100, value=0, limited=True, style=wx.ALIGN_RIGHT, size=(40,-1) )
		ctrl.Bind(IC.EVT_INT, self.onChange)
		self.gbs.Add( ctrl, pos=(3, 7), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )
		self.pointsForLappingLabel = label
		self.pointsForLappingCtrl = ctrl

		label = wx.CheckBox( self, label='Snowball' )
		self.gbs.Add( label, pos=(3, 8), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=16 )
		ctrl = label
		ctrl.Bind( wx.EVT_CHECKBOX, self.onChange )
		self.snowballLabel = label
		self.snowballCtrl = ctrl

		branding = wx.adv.HyperlinkCtrl( self, id=wx.ID_ANY, label="Powered by CrossMgr", url="http://www.sites.google.com/site/crossmgrsoftware/" )
		branding.SetBackgroundColour( wx.WHITE )
		self.gbs.Add( branding, pos=(3, 9), flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL )

		#-----------------------------------------------------------------------------------------------------------
		self.vbs.Add( self.gbs, flag = wx.ALL, border = 4 )
		
		self.SetSizerAndFit( self.vbs )
		
		self.ConfigurePointsRace()
		self.refresh()
	
	def getDirName( self ):
		return Utils.getDirName()

	#--------------------------------------------------------------------------------------------

	def configurePointsRaceOptions( self ):
		self.rankByCtrl.SetSelection( Model.Race.RankByPoints )
		self.snowballCtrl.SetValue( False )
		self.doublePointsForLastSprintCtrl.SetValue( True )
		self.startLapsCtrl.SetValue( 0 )
		self.pointsForLappingCtrl.SetValue( 20 )
		self.lapsCtrl.SetValue( 120 )
		self.sprintEveryCtrl.SetValue( 10 )
		self.pointsForPlaceCtrl.SetValue( '5,3,2,1' )
		
		self.commit()
		self.refresh()

	def ConfigurePointsRace( self ):
		self.configurePointsRaceOptions()
		
	def ConfigureMadison( self ):
		self.ConfigurePointsRace()
	
	def ConfigureTempoRace( self ):
		self.configurePointsRaceOptions()
		self.doublePointsForLastSprintCtrl.SetValue( False )
		self.pointsForLappingCtrl.SetValue( 4 )
		self.lapsCtrl.SetValue( 4*10 )
		self.startLapsCtrl.SetValue( 5 )
		self.sprintEveryCtrl.SetValue( 1 )
		self.pointsForPlaceCtrl.SetValue( '1' )
		self.commit()
		self.refresh()
	
	def ConfigureTempoTop2Race( self ):
		self.configurePointsRaceOptions()
		self.doublePointsForLastSprintCtrl.SetValue( False )
		self.pointsForLappingCtrl.SetValue( 4 )
		self.lapsCtrl.SetValue( 4*10 )
		self.startLapsCtrl.SetValue( 5 )
		self.sprintEveryCtrl.SetValue( 1 )
		self.pointsForPlaceCtrl.SetValue( '2,1' )
		self.commit()
		self.refresh()
	
	def ConfigureSnowballRace( self ):
		self.snowballCtrl.SetValue( True )
		self.rankByCtrl.SetSelection( Model.Race.RankByPoints )
		self.doublePointsForLastSprintCtrl.SetValue( False )
		self.pointsForPlaceCtrl.SetValue( '1' )
		self.commit()
		self.refresh()
		
	def ConfigureCriteriumRace( self ):
		self.ConfigurePointsRace()
		self.rankByCtrl.SetSelection( Model.Race.RankByLapsPointsNumWins )
		self.pointsForLappingCtrl.SetValue( 0 )
		self.doublePointsForLastSprintCtrl.SetValue( False )
		self.commit()
		self.refresh()

	def onChange( self, event ):
		self.commit()
		if Utils.getMainWin():
			Utils.getMainWin().refresh( False )	# False means don't include the Configure page.  This avoids an infinite loop.
	
	#--------------------------------------------------------------------------------------

	def updateDependentFields( self ):
		race = Model.race
		if not race:
			return

		self.distanceCtrl.SetLabel( '{}, {} Sprints'.format(race.getDistanceStr(), race.getNumSprints()) )
		self.gbs.Layout()

	def commit( self ):
		if self.inRefresh:	# Don't commit anything while we are refreshing.
			return
		race = Model.race
		if not race:
			return

		for field in [	'name', 'category', 'communique', 'laps', 'startLaps', 'sprintEvery', 'courseLength',
						'doublePointsForLastSprint', 'pointsForLapping', 'snowball']:
			v = getattr(self, field + 'Ctrl').GetValue()
			race.setattr( field, v )
			
		for field in ['rankBy', 'courseLengthUnit']:
			v = getattr(self, field + 'Ctrl').GetCurrentSelection()
			race.setattr( field, v )
			
		for field in ['date']:
			dt = getattr(self, field + 'Ctrl').GetValue()
			v = datetime.date( dt.GetYear(), dt.GetMonth() + 1, dt.GetDay() )	# Adjust for 0-based month.
			race.setattr( field, v )
			
		pfp = [int(f) for f in re.sub(r'[^\d]', ' ', self.pointsForPlaceCtrl.GetValue()).split()]
		pfp = [f for f in pfp if f > 0]
		pointsForPlace = {r:p for r, p in enumerate(pfp,1)}
		race.setattr( 'pointsForPlace', pointsForPlace )
			
		self.updateDependentFields()
	
	def refresh( self ):
		self.inRefresh = True
		race = Model.race
		
		for field in [	'name', 'category', 'communique', 'laps', 'startLaps', 'sprintEvery', 'courseLength',
						'doublePointsForLastSprint', 'pointsForLapping', 'snowball']:
			getattr(self, field + 'Ctrl').SetValue( getattr(race, field) )
		
		for field in ['rankBy', 'courseLengthUnit']:
			getattr(self, field + 'Ctrl').SetSelection( getattr(race, field) )
			
		for field in ['date']:
			d = getattr( race, field )
			dt = wx.DateTime(d.day, d.month - 1, d.year)	# Adjust for 0-based month
			getattr(self, field + 'Ctrl').SetValue( dt )
		
		v = ','.join( '{}'.format(points) for place, points in sorted( race.pointsForPlace.items()) )
		self.pointsForPlaceCtrl.SetValue( v )
		
		self.updateDependentFields()
				
		self.inRefresh = False

if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App( False )
	mainWin = wx.Frame(None,title="PointsRaceMan", size=(1000,600))

	dataDir = Utils.getHomeDir()
	os.chdir( dataDir )
	redirectFileName = os.path.join(dataDir, 'PointsRaceMgr.log')
	
	Model.newRace()
	c = Configure( mainWin )
	mainWin.Show()

	# Start processing events.
	app.MainLoop()
	

