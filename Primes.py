import wx
from wx.lib.masked import NumCtrl
import os
import six
import sys
import math
import Utils
import Model
from ReorderableGrid import ReorderableGrid
from FinishStrip		import ShowFinishStrip
from ReadSignOnSheet	import ExcelLink
from GetResults			import GetResults
from RaceInputState import RaceInputState
from Categories import TimeEditor

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

class Primes( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize ):
		super(Primes, self).__init__( parent, id, size=size )
		
		self.state = RaceInputState()
		
		vsOverall = wx.BoxSizer( wx.VERTICAL )
		
		#---------------------------------------------------------------
		self.colNameFields = (
			(_('Prime For'),			'effortType',	's'),
			(_('or Custom'),			'effortCustom',	's'),
			(_('Position'),				'position',		'i'),
			(_('Laps\nTo Go'),			'lapsToGo',		'i'),
			(_('Sponsor'),				'sponsor', 		's'),
			(_('Cash'),					'cash', 		'f'),
			(_('Merchandise'),			'merchandise', 	's'),
			(_('Points'),				'points', 		'i'),
			(_('Time\nBonus'),			'timeBonus', 	't'),
			(_('Winner\nBib'),			'winnerBib',	'i'),
			(u'',						'winnerInfo',	's'),
		)
		self.colnames = [colName for colName, fieldName, dataType in self.colNameFields]
		self.iCol = dict( (fieldName, i) for i, (colName, fieldName, dataType) in enumerate(self.colNameFields) if fieldName )
		self.grid = ReorderableGrid( self )
		self.grid.CreateGrid( 0, len(self.colNameFields) )
		GetTranslation = _
		for col, (colName, fieldName, dataType) in enumerate(self.colNameFields):
			self.grid.SetColLabelValue( col, colName )
			attr = wx.grid.GridCellAttr()
			if fieldName == 'effortType':
				attr.SetEditor( wx.grid.GridCellChoiceEditor(choices=[GetTranslation(name) for code, name in EffortChoices]) )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_TOP )
			elif fieldName == 'position':
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_TOP )
			elif fieldName == 'winnerInfo':
				attr.SetReadOnly( True )
			elif dataType == 'i':
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_TOP )
				attr.SetEditor( wx.grid.GridCellFloatEditor(precision=0) )
				attr.SetRenderer( wx.grid.GridCellFloatRenderer(precision=0) )
			elif dataType == 'f':
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_TOP )
				attr.SetEditor( wx.grid.GridCellFloatEditor(precision=2) )
				attr.SetRenderer( wx.grid.GridCellFloatRenderer(precision=2) )
			elif dataType == 't':
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
				attr.SetEditor( TimeEditor() )
			
			self.grid.SetColAttr( col, attr )
			if fieldName == 'lapsToGo':
				self.lapsToGoCol = col
		
		self.grid.Bind( wx.grid.EVT_GRID_CELL_CHANGED, self.onCellChange )
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )

		#---------------------------------------------------------------
		self.photosButton = wx.Button( self, label=u'{}...'.format(_('Photos')) )
		self.photosButton.Bind( wx.EVT_BUTTON, self.onPhotos )
		self.finishStrip = wx.Button( self, label=u'{}...'.format(_('Finish Strip')) )
		self.finishStrip.Bind( wx.EVT_BUTTON, self.onFinishStrip )
		self.history = wx.Button( self, label=u'{}...'.format(_('Passings')) )
		self.history.Bind( wx.EVT_BUTTON, self.onHistory )
		
		self.newButton = wx.Button( self, id=wx.ID_NEW )
		self.newButton.SetToolTip( wx.ToolTip(_('Create a new Prime')) )
		self.newButton.Bind( wx.EVT_BUTTON, self.onNew )
		self.nextPositionButton = wx.Button( self, label=('Next Position') )
		self.nextPositionButton.SetToolTip( wx.ToolTip(_('Create a Prime from an Existing Prime for the Next Position')) )
		self.nextPositionButton.Bind( wx.EVT_BUTTON, self.onNextPosition )
		self.nextPrimeButton = wx.Button( self, label=('Next Prime') )
		self.nextPrimeButton.SetToolTip( wx.ToolTip(_('Create a Prime from an Existing Prime')) )
		self.nextPrimeButton.Bind( wx.EVT_BUTTON, self.onNextPrime )
		self.deleteButton = wx.Button( self, id=wx.ID_DELETE )
		self.deleteButton.SetToolTip( wx.ToolTip(_('Delete a Prime')) )
		self.deleteButton.Bind( wx.EVT_BUTTON, self.onDelete )
		hsButtons = wx.BoxSizer( wx.HORIZONTAL )
		hsButtons.Add( self.photosButton, flag=wx.ALL, border=4 )
		hsButtons.Add( self.finishStrip, flag=wx.ALL, border=4 )
		hsButtons.Add( self.history, flag=wx.ALL, border=4 )
		hsButtons.AddStretchSpacer()
		hsButtons.Add( self.newButton, flag=wx.ALL, border=4 )
		hsButtons.Add( self.nextPositionButton, flag=wx.ALL, border=4 )
		hsButtons.Add( self.nextPrimeButton, flag=wx.ALL, border=4 )
		hsButtons.Add( self.deleteButton, flag=wx.ALL, border=4 )
		
		#---------------------------------------------------------------
		
		vsOverall.Add( self.grid, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		vsOverall.Add( hsButtons, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4 )
		self.SetSizer( vsOverall )
	
	def onCellChange( self, event ):
		row, col = event.GetRow(), event.GetCol()
		colName = self.colNameFields[col][1]
		GetTranslation = _
		if colName == 'effortCustom':
			if self.grid.GetCellValue(row, col).strip():
				self.grid.SetCellValue( row, col-1, GetTranslation('Custom') )
		elif colName == 'effortType':
			if self.grid.GetCellValue(row, col) != 'Custom':
				self.grid.SetCellValue( row, col+1, u'' )
		elif colName == 'winnerBib':
			bib = int( u''.join(c for c in self.grid.GetCellValue(row, col) if c.isdigit()) )
			self.grid.SetCellValue( row, col+1, getWinnerInfo(bib) )
		
		wx.CallAfter( self.grid.AutoSizeColumns, False )
	
	def getT( self ):
		race = Model.race
		if not race:
			return 0
		row = self.grid.GetGridCursorRow()
		if row is None or row < 0:
			return
		lapsToGo = int( u''.join(c for c in self.grid.GetCellValue(row, self.lapsToGoCol) if c.isdigit()) )
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
	
	def onHistory( self, event ):
		mainWin = Utils.getMainWin()
		if not mainWin:
			return
		mainWin.openMenuWindow( 'Passings' )
	
	def selectGridRow( self, row ):
		self.grid.SelectRow( row )
		self.grid.SetGridCursor( row, 0 )
		self.grid.ShowCellEditControl()
	
	def onNew( self, event ):
		race = Model.race
		if not race:
			Utils.MessageOK( self, _('You must have a Race to create a Prime.'), _('Missing Race') )
			return
		self.commit()
		race.primes = getattr(race, 'primes', [])
		rowNew = len( race.primes )
		race.primes.append( {} )
		self.updateGrid()
		self.selectGridRow( rowNew )
	
	def onNextPosition( self, event ):
		rowNext = self.grid.GetGridCursorRow()
		if rowNext is None or rowNext < 0:
			return
		self.commit()
		race = Model.race
		if not race:
			Utils.MessageOK( self, _('You must have a Race to create a next Prime.'), _('Missing Race') )
			return
		
		nextPrime = race.primes[rowNext].copy()
		
		nextPoints = {
			(1, 5):	3,
			(2, 3): 2,
			(3, 2): 1,
		}.get( (nextPrime['position'], nextPrime['points']), None )
		
		if nextPoints is not None:
			nextPrime['points'] = nextPoints
		
		try:
			nextPrime['position'] += 1
		except:
			pass
		nextPrime['winnerBib'] = None
		race.primes = race.primes[:rowNext+1] + [nextPrime] + race.primes[rowNext+1:]
		self.updateGrid()
		self.selectGridRow( rowNext + 1 )
	
	def onNextPrime( self, event ):
		rowNext = self.grid.GetGridCursorRow()
		if rowNext is None or rowNext < 0:
			return
		self.commit()
		race = Model.race
		if not race:
			Utils.MessageOK( self, _('You must have a Race to create a next Prime.'), _('Missing Race') )
			return
		nextPrime = race.primes[rowNext].copy()
		nextPrime['position'] = 1
		if nextPrime['points']:
			nextPrime['points'] = 5
		if nextPrime['lapsToGo'] > 0:
			nextPrime['lapsToGo'] -= 1
		nextPrime['winnerBib'] = None
		race.primes = race.primes[:rowNext+1] + [nextPrime] + race.primes[rowNext+1:]
		self.updateGrid()
		self.selectGridRow( rowNext + 1 )
		
	def onDelete( self, event ):
		rowDelete = self.grid.GetGridCursorRow()
		if rowDelete is None or rowDelete < 0:
			return
		self.commit()
		race = Model.race
		if race and Utils.MessageOKCancel( self, u'{}: {} ?'.format(_('Delete Prime'), rowDelete+1), _('Confirm Delete Primes') ):
			race.primes = getattr(race, 'primes', [])
			try:
				del race.primes[rowDelete]
			except Exception as e:
				return
			self.updateGrid()
			if race.primes:
				self.grid.SetGridCursor( rowDelete, 0 )
		
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
	
	def setRow( self, prime, row, updateGrid=True ):
		GetTranslation = _
		
		data = []
		for col, (name, attr, dataType) in enumerate(self.colNameFields):
			if attr == 'effortType':
				effortType = prime.get('effortType', 'Pack')
				v = GetTranslation(effortType)
			elif attr == 'position':
				position = prime.get('position', 1)
				v = u'' if position == 0 else six.text_type(position)
			elif attr == 'points':
				points = prime.get('points', 0)
				v = u'' if points == 0 else six.text_type(points)
			elif attr == 'winnerBib':
				winnerBib = prime.get('winnerBib', None)
				v = u'' if not winnerBib else six.text_type(winnerBib)
			elif attr == 'winnerInfo':
				v = getWinnerInfo(winnerBib)
			elif dataType == 'f':
				f = prime.get(attr, 0.0)
				v = u'{:.2f}'.format(f) if f else u''
			elif dataType == 't':
				t = prime.get(attr, 0.0)
				v = Utils.formatTime(t, forceHours=True, twoDigitHours=True) if t != 0 else u''
			else:
				v = six.text_type(prime.get(attr, u''))
			if updateGrid:
				self.grid.SetCellValue( row, col, v )
			data.append( v )
		
		return data
	
	def getRow( self, row ):
		values = {}
		for col, (name, attr, dataType) in enumerate(self.colNameFields):
			v = self.grid.GetCellValue( row, col ).strip()
			if dataType == 'i':
				v = u''.join( c for c in v if c.isdigit() )
				v = int( v or 0 )
			elif dataType == 'f':
				v = u''.join( c for c in v if c.isdigit() or c == '.')
				v = float( v or 0.0 )
			elif dataType == 't':
				v = Utils.StrToSeconds( v )
				
			if attr == 'position' and not v:
				v = 1
			
			values[attr] = v
		
		GetTranslation = _
		for code, name in EffortChoices:
			if values['effortType'] == GetTranslation(name):
				values['effortType'] = name
				break
		
		if values['effortCustom']:
			values['effortType'] = 'Custom'
		return values
	
	def updateGrid( self ):
		race = Model.race
		if not race or not getattr(race, 'primes', None):
			self.grid.ClearGrid()
			return
		
		Utils.AdjustGridSize( self.grid, len(race.primes) )
		for row, prime in enumerate(race.primes):
			self.setRow( prime, row )
		
		self.grid.AutoSizeColumns( False )								# Resize to fit the column name.
		self.grid.AutoSizeRows( False )
	
	def refresh( self ):
		if self.state.changed():
			self.updateGrid()
		
	def commit( self ):
		self.grid.SaveEditControlValue()	# Make sure the current edit is committed.
		self.grid.DisableCellEditControl()
		race = Model.race
		if not race:
			return
		race.primes = [self.getRow(row) for row in range(self.grid.GetNumberRows())]

def GetGrid():
	race = Model.race
	if not race:
		return {}
	primes = getattr( race, 'primes', [] )
	if not primes:
		return {}
	
	try:
		excelLink = race.excelLink
		externalFields = set(excelLink.getFields())
		externalInfo = excelLink.read()
	except:
		excelLink = None
		externalFields = set()
		externalInfo = {}
	
	title = u'\n'.join( [race.title, Utils.formatDate(race.date), u'Primes'] )
	
	rightJustifyCols = set([0, 1])
	colnames = [u'Prime', _('Bib'),]
	hasName = ('FirstName' in externalFields or 'LastName' in externalFields)
	if hasName:
		colnames.append( _('Name') )
		
	hasTeam = 'Team' in externalFields
	if hasTeam:
		colnames.append( _('Team') )
	
	rightJustifyCols.add( len(colnames) )
	colnames.append( _('Laps to go') )
	
	colnames.append( _('For') )
	
	hasCash = any( prime.get('cash',0) for prime in primes)
	hasMerchandise = any( prime.get('merchandise',None) for prime in primes)
	hasPoints = any( prime.get('points',0) for prime in primes )
	hasTimeBonus = any( prime.get('timeBonus',0) for prime in primes )
	hasSponsor = any( prime.get('sponsor',None) for prime in primes )
	
	if not any( [hasCash, hasMerchandise, hasPoints, hasTimeBonus] ):
		hasCash = True
	
	if hasCash:
		rightJustifyCols.add( len(colnames) )
		colnames.append( _('Cash') )
	if hasMerchandise:
		colnames.append( _('Merchandise') )
	if hasPoints:
		rightJustifyCols.add( len(colnames) )
		colnames.append( _('Points') )
	if hasTimeBonus:
		rightJustifyCols.add( len(colnames) )
		colnames.append( _('Time Bonus') )
	if hasSponsor:
		colnames.append( _('Sponsor') )

	leftJustifyCols = set( i for i in range(len(colnames)) if i not in rightJustifyCols )
	
	data = [[] for c in range(len(colnames))]	# Column oriented table.
	GetTranslation = _
	for p, prime in enumerate(primes):
		row = []
		bib = prime['winnerBib']
		info = externalInfo.get( bib, {} )
		
		row.append( p+1 )
		row.append( bib or u'' )
		
		if hasName:
			row.append( u', '.join( f for f in [info.get('LastName', u''), info.get('FirstName', u'')] if f ) )
		if hasTeam:
			row.append( info.get('Team', u'') )
		row.append( prime['lapsToGo'] )
		effortType = prime['effortType']
		row.append( GetTranslation(effortType) if effortType != 'Custom' else prime.get('effortCustom',u'') )

		if hasCash:
			row.append( u'{:.2f}'.format(prime.get('cash',0.0)) )
		if hasMerchandise:
			row.append( prime.get('merchandise',u'') )
		if hasPoints:
			points = prime.get('points',0)
			row.append( '{}'.format(points) if points else '' )
		if hasTimeBonus:
			timeBonus = prime.get('timeBonus',0)
			row.append( Utils.formatTime(timeBonus) if timeBonus else '' )
		if hasSponsor:
			row.append( prime.get('sponsor',u'') )
		
		for c, v in enumerate(row):
			data[c].append( six.text_type(v) )
		
	return {'title':title, 'colnames':colnames, 'data':data, 'leftJustifyCols':leftJustifyCols}

if __name__ == '__main__':
	app = wx.App(False)
	app.SetAppName("CrossMgr")
	
	Utils.disable_stdout_buffering()
	
	race = Model.newRace()
	race._populate()
	
	fnameRiderInfo = os.path.join(Utils.getHomeDir(), 'SimulationRiderData.xlsx')
	sheetName = 'RiderData'
	
	race.excelLink = ExcelLink()
	race.excelLink.setFileName( fnameRiderInfo )
	race.excelLink.setSheetName( sheetName )
	race.excelLink.setFieldCol( {'Bib#':0, 'LastName':1, 'FirstName':2, 'Team':3} )
	
	race.primes = [
		{'sponsor': u'11111111111111', 'cash': 100, 'merchandise': u'', 'winnerBib': 101, 'lapsToGo': 7 },
		{'sponsor': u'22222222222222', 'cash': 200, 'merchandise': u'', 'winnerBib': 110, 'lapsToGo': 6 },
		{'sponsor': u'33333333333333', 'cash': 0, 'merchandise': u'Water bottle', 'winnerBib': 115, 'lapsToGo': 5 },
		{'sponsor': u'44444444444444', 'cash': 300, 'merchandise': u'', 'winnerBib': 199, 'lapsToGo': 4 },
		{'sponsor': u'55555555555555', 'cash': 0.51, 'merchandise': u'New bike', 'winnerBib': 101, 'lapsToGo': 3 },
	]
	
	mainWin = wx.Frame(None, title="Primes", size=(800,700) )
	primes = Primes( mainWin )
	mainWin.Show()
	
	primes.refresh()	
	app.MainLoop()
