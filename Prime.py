import wx
from wx.lib.masked import NumCtrl
import os
import sys
import math
import Utils
import Model

def getWinnerInfo( bib ):
	race = Model.race
	if not race or not bib:
		return u''
	try:
		excelLink = race.excelLink
		externalInfo = excelLink.read()
	except:
		return u''
	
	try:
		riderInfo = externalInfo[bib]
	except KeyError:
		return u''

	fields = [
		u' '.join( f for f in (riderInfo.get('LastName',u''), riderInfo.get('FirstName',u'')) if f ),
		riderInfo.get('Team', u''),
	]
	
	return u', '.join( f for f in fields if f )
	
# Do not change the number codes.
with Utils.SuspendTranslation():
	EffortChoices = (
		(0, _('Pack')),
		(1, _('Break')),
		(2, _('Chase')),
		(-1, _('Custom')),	# This one must be last.
	)

class Prime( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize ):
		super(Prime, self).__init__( parent, id, size=size )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		
		fgs = wx.FlexGridSizer( cols=2, vgap=4, hgap=4 )
		fgs.AddGrowableCol( 1, 1 )
		
		self.sponsorLabel = wx.StaticText( self, label=u'{}:'.format(_('Sponsor')) )
		self.sponsor = wx.ComboBox( self, choices=self.getSponsors(), style=wx.TE_PROCESS_ENTER )
		
		self.cashLabel = wx.StaticText( self, label=u'{}:'.format(_('Cash')) )
		self.cash = NumCtrl( self, fractionWidth=2, size=(40, 0), allowNone=True, style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER )
		self.cash.SetMinSize( (80, -1) )
		
		self.merchandiseLabel = wx.StaticText( self, label=u'{}:'.format(_('Merchandise')) )
		self.merchandise = wx.ComboBox( self, choices=self.getMerchandise(), style=wx.TE_PROCESS_ENTER )
		
		GetTranslation = _
		self.effortLabel = wx.StaticText( self, label=u'{}:'.format(_('For')) )
		self.effort = wx.Choice( self, choices=[GetTranslation(v) for i, v in EffortChoices] )
		self.effort.Bind( wx.EVT_CHOICE, self.onEffortChoice )
		self.effortCustom = wx.TextCtrl( self )
		
		self.lapsToGoLabel = wx.StaticText( self,label=u'{}:'.format(_('Laps to Go')) )
		self.lapsToGo = wx.SpinCtrl( self, min=0, size=(64,-1), style=wx.TE_RIGHT )
		
		self.winnerLabel = wx.StaticText( self, label=u'{}:'.format(_('Winner Bib')) )
		self.winner = NumCtrl( self, min=0, max=99999, allowNone=True, style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER )
		self.winner.SetMinSize( (64, -1) )
		self.winner.Bind( wx.EVT_TEXT, self.updateWinnerInfo )
		
		self.winnerInfo = wx.StaticText( self )

		#---------------------------------------------------------------
		
		labelFlag = wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL
		fgs.Add( self.sponsorLabel, flag=labelFlag )
		fgs.Add( self.sponsor, 1, flag=wx.EXPAND )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.cash )
		hs.Add( self.merchandiseLabel, flag=wx.LEFT|wx.ALIGN_CENTRE_VERTICAL, border=12 )
		hs.Add( self.merchandise, 1, flag=wx.EXPAND|wx.LEFT, border=2 )
		
		fgs.Add( self.cashLabel, flag=labelFlag )
		fgs.Add( hs, 1, flag=wx.EXPAND )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.effort, flag=wx.ALIGN_RIGHT )
		hs.Add( self.effortCustom, 1, flag=wx.EXPAND|wx.LEFT, border=4 )
		
		fgs.Add( self.effortLabel, flag=labelFlag )
		fgs.Add( hs, flag=wx.EXPAND )
		
		fgs.Add( self.lapsToGoLabel, flag=labelFlag )
		fgs.Add( self.lapsToGo )
		
		fgs.Add( self.winnerLabel, flag=labelFlag )
		fgs.Add( self.winner )
		
		fgs.Add( wx.StaticText(self) )
		fgs.Add( self.winnerInfo, 1, flag=wx.EXPAND )
		
		self.SetSizer( fgs )
		self.updateEffort()
		
	def getSponsors( self ):
		race = Model.race
		if not race:
			return []
		sponsers = [race.organizer] + [prime.get('sponsor', '') for prime in getattr(race, 'primes', [])]
		sponsers.reverse()
		return sponsers
		
	def getMerchandise( self ):
		race = Model.race
		if not race:
			return []
		merchandise = [prime.get('merchandise', '') for prime in getattr(race, 'primes', [])]
		merchandise.reverse()
		return merchandise
	
	def onEffortChoice( self, event ):
		wx.CallAfter( self.updateEffort )
	
	def updateEffort( self ):
		self.effortCustom.Enable( bool(len(self.effort.GetItems())-1 == self.effort.GetSelection()) )
		
	def updateWinnerInfo( self, event=None ):
		self.winnerInfo.SetLabel( getWinnerInfo(self.winner.GetValue()) )
	
	def GetValues( self ):
		iEffort = self.effort.GetSelection()
		EffortCodeFromIndex = { k:i for k, (i, v) in enumerate(EffortChoices) }
		effortCode = EffortCodeFromIndex.get( iEffort, 0)
		return {
			'sponsor':		self.sponsor.GetValue().strip(),
			'effortType':	EffortChoices[iEffort][1],	# Untranslated effort name
			'effortCustom':	self.effortCustom.GetValue().strip() if effortCode < 0 else u'',
			'cash':			self.cash.GetValue(),
			'merchandise':	self.merchandise.GetValue(),
			'winnerBib':	self.winner.GetValue(),
			'lapsToGo':		self.lapsToGo.GetValue(),
		}
		
	def SetValues( self, values={} ):
		for attr, widget, defaultVal in (
				('sponsor',			self.sponsor, u''),
				('cash',			self.cash, 0),
				('merchandise',		self.merchandise, u''),
				('winnerBib',		self.winner, 0),
				('lapsToGo',		self.lapsToGo, 0),
			):
			try:
				widget.SetValue( values.get(attr, defaultVal) )
			except Exception as e:
				pass
		self.updateWinnerInfo()
			
		effortType = values.get('effortType', EffortChoices[0][1])
		IndexFromEffortType = { v:k for k, (i, v) in enumerate(EffortChoices) }
		self.effort.SetSelection( IndexFromEffortType.get(effortType, 0) )
		self.effortCustom.SetValue( values.get('effortCustom', u'') if effortType != 'Custom' else u'' )
		self.updateEffort()

if __name__ == '__main__':
	app = wx.App(False)
	
	race = Model.newRace()
	race._populate()
	
	mainWin = wx.Frame(None, title="Prime")
	prime = Prime( mainWin )
	mainWin.Show()
	
	print prime.GetValues()
	prime.SetValues( {
			'sponsor': u'Awesome Sponsor',
			'cash': 100,
			'merchandise': u'Awesome T-Shirt',
			'winnerBib': 119,
			'lapsToGo': 6,
		}
	)
	print prime.GetValues()
	
	app.MainLoop()
