import wx
from wx.lib.masked import NumCtrl
import os
import sys
import math
import Utils
import Model
from FinishStrip		import ShowFinishStrip
from ReadSignOnSheet	import ExcelLink
from GetResults			import GetResults

def getWinnerInfo( bib ):
	race = Model.race
	if not race or not bib:
		return u''
	
	try:
		riderInfo = race.excelLink.read()[bib]
	except Exception as e:
		return u''

	fields = [
		u' '.join( f for f in (riderInfo.get('FirstName',u''), riderInfo.get('LastName',u'')) if f ),
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

from wx.lib.agw import ultimatelistctrl as ULC
class PrimesList( ULC.UltimateListCtrl ):
	def __init__( self, *args, **kwargs ):
		if 'agwStyle' not in kwargs:
			kwargs['agwStyle'] = wx.LC_REPORT
		ULC.UltimateListCtrl.__init__( self, *args, **kwargs )

class Primes( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize ):
		super(Primes, self).__init__( parent, id, size=size )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		
		vsOverall = wx.BoxSizer( wx.VERTICAL )
		
		#---------------------------------------------------------------
		
		fgs = wx.FlexGridSizer( cols=2, vgap=4, hgap=4 )
		fgs.AddGrowableCol( 1, 1 )
		
		self.sponsorLabel = wx.StaticText( self, label=u'{}:'.format(_('Sponsor')) )
		self.sponsor = wx.ComboBox( self, choices=self.getSponsors(), style=wx.TE_PROCESS_ENTER )
		
		self.cashLabel = wx.StaticText( self, label=u'{}:'.format(_('Cash')) )
		self.cash = NumCtrl( self, fractionWidth=2, size=(40, 0), allowNone=True, style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER )
		self.cash.SetMinSize( (100, -1) )
		
		self.merchandiseLabel = wx.StaticText( self, label=u'{}:'.format(_('Merchandise')) )
		self.merchandise = wx.ComboBox( self, choices=self.getMerchandise(), style=wx.TE_PROCESS_ENTER )
		
		self.lapsToGoLabel = wx.StaticText( self,label=u'{}:'.format(_('Laps to Go')) )
		self.lapsToGo = wx.SpinCtrl( self, min=0, max=9999, size=(64,-1), style=wx.TE_RIGHT )
		
		GetTranslation = _
		self.effortLabel = wx.StaticText( self, label=u'{}:'.format(_('For')) )
		self.effort = wx.Choice( self, choices=[GetTranslation(v) for i, v in EffortChoices] )
		self.effort.Bind( wx.EVT_CHOICE, self.onEffortChoice )
		self.effortCustom = wx.TextCtrl( self )
		
		self.winnerLabel = wx.StaticText( self, label=u'{}:'.format(_('Winner Bib')) )
		self.winner = NumCtrl( self, min=0, max=99999, allowNone=True, groupDigits=False, style=wx.TE_RIGHT|wx.TE_PROCESS_ENTER )
		self.winner.SetMinSize( (64, -1) )
		self.winner.Bind( wx.EVT_TEXT, self.updateWinnerInfo )
		
		self.winnerInfo = wx.StaticText( self )

		self.Bind( wx.EVT_TEXT_ENTER, self.doEnter )
		self.Bind( wx.EVT_TEXT, self.doEnter )
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
		
		fgs.Add( self.lapsToGoLabel, flag=labelFlag )
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.lapsToGo )
		hs.Add( self.effortLabel, flag=labelFlag|wx.LEFT, border=12 )		
		hs.Add( self.effort, flag=wx.LEFT, border=2 )
		hs.Add( self.effortCustom, 1, flag=wx.EXPAND|wx.LEFT, border=4 )
		fgs.Add( hs, flag=wx.EXPAND )
		
		fgs.Add( self.winnerLabel, flag=labelFlag )
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.winner )
		hs.Add( self.winnerInfo, flag=wx.LEFT|wx.ALIGN_CENTRE_VERTICAL, border=4 )
		fgs.Add( hs )
		
		#---------------------------------------------------------------
		self.primeList = PrimesList( self, size=(-1, 128), agwStyle=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_HRULES )
		self.colNameFields = (
			(u'',						'num'),
			(_('Sponsor'),				'sponsor'),
			(_('Cash'),					'cash'),
			(_('Merchandise'),			'merchandise'),
			(_('LapsToGo'),				'lapsToGo'),
			(_('For'),					'effort'),
			(_('Bib'),					'winner'),
			(_('Info'),					'winnerInfo'),
		)
		self.colnames = [colName for colName, fieldName in self.colNameFields]
		self.iCol = dict( (fieldName, i) for i, (colName, fieldName) in enumerate(self.colNameFields) if fieldName )
		for col, (colName, fieldName) in enumerate(self.colNameFields):
			self.primeList.InsertColumn(
				col,
				colName,
				format=wx.LIST_FORMAT_RIGHT if fieldName in ('lapsToGo', 'cash', 'winner', 'num') else wx.LIST_FORMAT_LEFT
			)
		
		self.primeList.Bind( wx.EVT_LIST_ITEM_DESELECTED, self.onItemDeselected )
		self.primeList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected )
		self.primeList.Bind( ULC.EVT_LIST_BEGIN_DRAG, self.onBeginDrag )
		self.primeList.Bind( ULC.EVT_LIST_END_DRAG, self.onEndDrag )
		self.iDrag = -1	# Current item being dragged.
		
		#---------------------------------------------------------------
		self.photosButton = wx.Button( self, label=u'{}...'.format(_('Photos')) )
		self.photosButton.Bind( wx.EVT_BUTTON, self.onPhotos )
		self.finishStrip = wx.Button( self, label=u'{}...'.format(_('Finish Strip')) )
		self.finishStrip.Bind( wx.EVT_BUTTON, self.onFinishStrip )
		
		self.newButton = wx.Button( self, id=wx.ID_NEW )
		self.newButton.Bind( wx.EVT_BUTTON, self.onNew )
		self.deleteButton = wx.Button( self, id=wx.ID_DELETE )
		self.deleteButton.Bind( wx.EVT_BUTTON, self.onDelete )
		hsButtons = wx.BoxSizer( wx.HORIZONTAL )
		hsButtons.Add( self.photosButton, flag=wx.ALL, border=4 )
		hsButtons.Add( self.finishStrip, flag=wx.ALL, border=4 )
		hsButtons.AddStretchSpacer()
		hsButtons.Add( self.newButton, flag=wx.ALL, border=4 )
		hsButtons.Add( self.deleteButton, flag=wx.ALL, border=4 )
		
		#---------------------------------------------------------------
		
		vsOverall.Add( self.primeList, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		vsOverall.Add( fgs, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border=4 )
		vsOverall.Add( hsButtons, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4 )
		self.SetSizer( vsOverall )
		self.updateEffort()
	
	def onBeginDrag( self, event ):
		self.iDrag = event.GetIndex()
		event.Skip()
	
	def onEndDrag( self, event ):
		if self.iDrag < 0:
			event.Skip()
			return
		race = Model.race
		iOld, iNew = self.iDrag, event.GetIndex()
		if not race or iOld == iNew:
			return
		iStart, iEnd = sorted( [iOld, iNew] )
		
		iMax = len(race.primes)
		self.primeList.Select( iOld, False )
		while iOld != iNew:
			iNext = iOld + (1 if iOld < iNew else -1)
			race.primes[iOld], race.primes[iNext] = race.primes[iNext], race.primes[iOld]
			iOld = iNext
		
		for i in xrange(iStart, min(iEnd+1, iMax)):
			self.setRow( race.primes[i], i )
			
		self.primeList.Select( min(iMax-1,max(0,iNew)), True )
		self.iDrag = -1
		event.Skip()
	
	def getT( self ):
		race = Model.race
		if not race:
			return 0
		lapsToGo = self.lapsToGo.GetValue()
		tMax = 0.0
		for rr in GetResults(None):
			try:
				tMax = min( tMax, rr.raceTimes[-1-lapsToGo] )
			except IndexError:
				pass
		return tMax
	
	def onPhotos( self, event ):
		mainWin = Utils.getMainWin()
		if not mainWin:
			return
		mainWin.photoDialog.SetT( self.getT() )
		mainWin.photoDialog.Show()
		
	def onFinishStrip( self, event ):
		ShowFinishStrip( self, self.getT() )
		
	def onNew( self, event ):
		self.itemCommit()
		race = Model.race
		if race:
			race.primes = getattr(race, 'primes', None) or []
			race.primes.append( {} )
			rowNew = len(race.primes) - 1
			self.updateList()
			for i in xrange(len(race.primes)):
				self.primeList.Select(i, False)
			self.primeList.Select(rowNew, True)
			self.SetValues( race.primes[rowNew] )
			self.sponsor.SetFocus()
		
	def onDelete( self, event ):
		rowDelete = self.primeList.GetNextSelected(-1)
		if rowDelete < 0:
			return
		race = Model.race
		if race and Utils.MessageOKCancel( self, u'{}: {} ?'.format(_('Delete Primes'), rowDelete+1), _('Confirm Delete Primes') ):
			race.primes = getattr(race, 'primes', None) or []
			try:
				del race.primes[rowDelete]
			except Exception as e:
				return
			if race.primes:
				rowDelete = min(rowDelete, len(race.primes)-1)
				self.SetValues( race.primes[rowDelete] )
				for i in xrange(len(race.primes)):
					self.primeList.Select(i, False)
				self.primeList.Select(rowDelete, True)
			self.updateList()
		
	def doEnter( self, event ):
		self.itemCommit()

	def itemCommit( self, rowCommit=None ):
		race = Model.race
		if not race:
			return
		race.primes = getattr(race, 'primes', None) or []
		if not race.primes:
			return
		if rowCommit is None:
			rowCommit = self.primeList.GetNextSelected(-1)
		if rowCommit < 0:
			return
		if rowCommit < len(race.primes):
			race.primes[rowCommit] = self.GetValues()
			self.setRow( race.primes[rowCommit], rowCommit )
			self.updateColWidths()
			self.updateComboBoxes()
	
	def onItemDeselected( self, event ):
		self.itemCommit( event.GetIndex() )
		
	def onItemSelected( self, event ):
		race = Model.race
		if race:
			rowUpdate = event.GetIndex()
			race.primes = getattr(race, 'primes', None) or []
			if rowUpdate < len(race.primes):
				self.SetValues( race.primes[rowUpdate] )
		
	def getSponsors( self ):
		race = Model.race
		if not race:
			return []
		sponsors = [prime.get('sponsor', u'') for prime in getattr(race, 'primes', [])] + [race.organizer]
		sponsors = [s for s in sponsors if s]
		return sponsors
		
	def getMerchandise( self ):
		race = Model.race
		if not race:
			return []
		merchandise = [prime.get('merchandise', u'') for prime in getattr(race, 'primes', [])]
		merchandise = [m for m in merchandise if m]
		return merchandise
	
	def onEffortChoice( self, event ):
		self.itemCommit()
		wx.CallAfter( self.updateEffort )
	
	def setRow( self, prime, row, updateList=True ):
		GetTranslation = _
		
		data = []
		for col, (name, attr) in enumerate(self.colNameFields):
			if col == 0:
				v = u'{}.'.format(row+1)
			elif attr == 'effort':
				effortType = prime.get('effortType', 'Pack')
				v = prime.get('effortCustom', u'') if effortType == 'Custom' else GetTranslation(effortType)
			elif attr == 'winner':
				winnerBib = prime.get('winnerBib', None)
				v = u'' if not winnerBib else unicode(winnerBib)
			elif attr == 'winnerInfo':
				v = getWinnerInfo(winnerBib)
			elif attr == 'cash':
				cash = prime.get('cash', 0.0)
				v = u'{:.2f}'.format( prime.get('cash', 0.0) ) if cash else u''
			else:
				v = unicode(prime.get(attr, u''))
			if updateList:
				if row == self.primeList.GetItemCount():
					self.primeList.InsertStringItem( row, v )
				else:
					self.primeList.SetStringItem( row, col, v )
			data.append( v )
		
		return data
	
	def updateComboBoxes( self ):
		self.sponsor.SetItems( self.getSponsors() )
		self.merchandise.SetItems( self.getMerchandise() )		
	
	def updateColWidths( self ):
		race = Model.race
		if not race or not hasattr(race, 'primes'):
			return
		dc = wx.WindowDC( self.primeList )
		dc.SetFont( self.primeList.GetFont() )
		rows = [self.setRow( prime, row ) for row, prime in enumerate(race.primes)]
		for col, (name, attr) in enumerate(self.colNameFields):
			self.primeList.SetColumnWidth( col, (max(dc.GetTextExtent(r[col])[0] for r in rows)+16) if attr != 'lapsToGo' else 72 )
	
	def updateList( self ):
		race = Model.race
		if not race or not hasattr(race, 'primes'):
			self.primeList.DeleteAllItems()
			return
			
		while self.primeList.GetItemCount() > len(race.primes):
			self.primeList.DeleteItem( self.primeList.GetItemCount()-1 )
		for row, prime in enumerate(race.primes):
			self.setRow( prime, row )
			
		self.updateColWidths()
		
		if self.primeList.GetNextSelected(-1) < 0 and self.primeList.GetItemCount() > 0:
			self.primeList.Select(0, True)
			self.SetValues( race.primes[0] )
			
		self.updateComboBoxes()
			
	def updateEffort( self ):
		self.effortCustom.Enable( bool(len(self.effort.GetItems())-1 == self.effort.GetSelection()) )
		
	def updateWinnerInfo( self, event=None ):
		self.winnerInfo.SetLabel( getWinnerInfo(self.winner.GetValue()) )
		if event:
			event.Skip()
	
	def GetValues( self ):
		iEffort = self.effort.GetSelection()
		EffortCodeFromIndex = { k:i for k, (i, v) in enumerate(EffortChoices) }
		effortCode = EffortCodeFromIndex.get( iEffort, 0)
		return {
			'sponsor':		self.sponsor.GetValue().strip(),
			'effortType':	EffortChoices[iEffort][1],	# Untranslated effort name
			'effortCustom':	self.effortCustom.GetValue().strip() if effortCode < 0 else u'',
			'cash':			self.cash.GetValue(),
			'merchandise':	self.merchandise.GetValue().strip(),
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
				widget.SetValue( defaultVal )
		self.updateWinnerInfo()
			
		effortType = values.get('effortType', EffortChoices[0][1])
		IndexFromEffortType = { v:k for k, (i, v) in enumerate(EffortChoices) }
		self.effort.SetSelection( IndexFromEffortType.get(effortType, 0) )
		self.effortCustom.SetValue( values.get('effortCustom', u'') if effortType != 'Custom' else u'' )
		self.updateEffort()
		
	def refresh( self ):
		self.updateList()
		
	def commit( self ):
		self.itemCommit()

if __name__ == '__main__':
	app = wx.App(False)
	app.SetAppName("CrossMgr")

	
	race = Model.newRace()
	race._populate()
	
	fnameRiderInfo = os.path.join(Utils.getHomeDir(), 'SimulationRiderData.xlsx')
	sheetName = 'RiderData'
	
	race.excelLink = ExcelLink()
	race.excelLink.setFileName( fnameRiderInfo )
	race.excelLink.setSheetName( sheetName )
	race.excelLink.setFieldCol( {'Bib#':0, 'LastName':1, 'FirstName':2, 'Team':3} )
	
	race.primes = [
		{'sponsor': u'McLovinMcLovinMcLovinMcLovinMcLovinMcLovin', 'cash': 100, 'merchandise': u'', 'winnerBib': 101, 'lapsToGo': 7 },
		{'sponsor': u'McDuck', 'cash': 200, 'merchandise': u'', 'winnerBib': 110, 'lapsToGo': 6 },
		{'sponsor': u'McCloud', 'cash': 0, 'merchandise': u'Water bottle', 'winnerBib': 115, 'lapsToGo': 5 },
		{'sponsor': u'McMack', 'cash': 300, 'merchandise': u'', 'winnerBib': 199, 'lapsToGo': 4 },
		{'sponsor': u'McDonalds', 'cash': 0.51, 'merchandise': u'New bike', 'winnerBib': 101, 'lapsToGo': 3 },
	]
	
	mainWin = wx.Frame(None, title="Primes", size=(800,700) )
	primes = Primes( mainWin )
	mainWin.Show()
	
	primes.refresh()	
	app.MainLoop()
