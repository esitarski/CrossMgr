import wx
import wx.grid			as gridlib
import re
import os
from collections import defaultdict

import Utils
import Model
from ReorderableGrid 	import ReorderableGrid
from ReadSignOnSheet	import ExcelLink
from FixCategories import FixCategories, SetCategory
from GetResults			import GetResults, getPulledCmpTuple
from RaceInputState import RaceInputState

def getRiderInfo( bib ):
	race = Model.race
	try:
		riderInfo = race.excelLink.read()[bib]
	except (KeyError, AttributeError) as e:
		return '', '', ''
	
	CatComponent = Model.Category.CatComponent
	for cat in race.getCategories( startWaveOnly=False ):
		if cat.catType == CatComponent and cat.matches(bib):
			componentName = cat.fullname
			break
	else:
		componentName = ''
	
	return ', '.join( f for f in (riderInfo.get('LastName',''), riderInfo.get('FirstName','')) if f ), riderInfo.get('Team', ''), componentName

class TimeEditor(gridlib.GridCellEditor):
	defaultValue = '00:00.000'

	def __init__(self):
		self._tc = None
		self.startValue = self.defaultValue
		super().__init__()
		
	def Create( self, parent, id = wx.ID_ANY, evtHandler = None ):
		self._tc = wx.TextCtrl( parent, id, value=self.defaultValue )
		self.SetControl( self._tc )
		if evtHandler:
			self._tc.PushEventHandler( evtHandler )
	
	def SetSize( self, rect ):
		self._tc.SetSize(rect.x, rect.y, rect.width+2, rect.height+2, wx.SIZE_ALLOW_MINUS_ONE )
	
	def BeginEdit( self, row, col, grid ):
		self.startValue = grid.GetTable().GetValue(row, col)
		self._tc.SetValue( self.startValue )
		self._tc.SetFocus()
		
	def EndEdit( self, row, col, grid, value = None ):
		changed = False
		val = self._tc.GetValue()
		val = re.sub( '[^0-9.:]', '', val )
		s = 0.0
		for f in val.split(':'):
			s *= 60.0
			try:
				s += float( f )
			except Exception:
				pass
		val = Utils.formatTime( s, highPrecision=True ) if s else ''
		if val != self.startValue:
			changed = True
			grid.GetTable().SetValue( row, col, val )
		
	def Reset( self ):
		self._tc.SetValue( self.startValue )
		
	def Clone( self ):
		return TimeEditor()

class Pulled( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize ):
		super().__init__( parent, id, size=size )
		
		self.state = RaceInputState()
		
		vsOverall = wx.BoxSizer( wx.VERTICAL )
		
		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.showingCategoryLabel = wx.StaticText( self, label='{}:'.format(_('Start Wave')) )
		self.showingCategory = wx.StaticText( self )
		self.showingCategory.SetFont( self.showingCategory.GetFont().Bold() )
		self.categoryLabel = wx.StaticText( self, label=_('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		self.useTableToPullRidersCkBox = wx.CheckBox( self, label=_('Use this Table to Pull Riders') )
		self.useTableToPullRidersCkBox.SetToolTip( wx.ToolTip(_('Also requires Laps to be set in Categories screen.')) )
		self.commitBtn = wx.Button( self, label=_('Commit') )
		self.commitBtn.Bind( wx.EVT_BUTTON, self.doCommit )
		self.hbs.Add( self.showingCategoryLabel, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=0 )
		self.hbs.Add( self.showingCategory, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=2 )
		self.hbs.Add( self.categoryLabel, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=18 )
		self.hbs.Add( self.categoryChoice, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=2 )
		self.hbs.Add( self.useTableToPullRidersCkBox, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=18 )
		self.hbs.Add( self.commitBtn, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=32 )
		
		#---------------------------------------------------------------
		self.colNameFields = (
			(_('Laps to Go'),			'lapsToGo',			'i'),
			('    ' + _('Bib'),			'pulledBib',		'i'),
			('Name',					'pulledName',		's'),
			('Team',					'pulledTeam',		's'),
			('Component',				'pulledComponent',	's'),
			('Error',					'pulledError',		's'),
		)
		self.colnames = [colName for colName, fieldName, dataType in self.colNameFields]
		self.iCol = dict( (fieldName, i) for i, (colName, fieldName, dataType) in enumerate(self.colNameFields) if fieldName )
		self.grid = ReorderableGrid( self )
		self.grid.CreateGrid( 0, len(self.colNameFields) )
		GetTranslation = _
		for col, (colName, fieldName, dataType) in enumerate(self.colNameFields):
			self.grid.SetColLabelValue( col, colName )
			attr = wx.grid.GridCellAttr()
			if dataType == 'i':
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_TOP )
				attr.SetEditor( wx.grid.GridCellFloatEditor(precision=0) )
				attr.SetRenderer( wx.grid.GridCellFloatRenderer(precision=0) )
			elif dataType == 'f':
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_TOP )
				attr.SetEditor( wx.grid.GridCellFloatEditor(precision=2) )
				attr.SetRenderer( wx.grid.GridCellFloatRenderer(precision=2) )
			elif dataType == 't':
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTRE )
				attr.SetEditor( TimeEditor() )
			
			self.grid.SetColAttr( col, attr )
		
		self.grid.Bind( wx.grid.EVT_GRID_CELL_CHANGED, self.onCellChange )
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )

		#---------------------------------------------------------------
		
		vsOverall.Add( self.hbs, 0, flag=wx.EXPAND|wx.ALL, border=4 )
		vsOverall.Add( self.grid, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		self.SetSizer( vsOverall )
	
	def setCategory( self, category ):
		for i, c in enumerate(Model.race.getCategories( startWaveOnly=False ) if Model.race else [], 1):
			if c == category:
				SetCategory( self.categoryChoice, c )
				Model.setCategoryChoice( i, 'resultsCategory' )
				return
		SetCategory( self.categoryChoice, None )
		Model.setCategoryChoice( 0, 'resultsCategory' )
	
	def doChooseCategory( self, event ):
		Model.setCategoryChoice( self.categoryChoice.GetSelection(), 'resultsCategory' )
		self.refresh()
	
	def doCommit( self, event ):
		self.commit()
		self.refresh()
	
	def getCategory( self ):
		race = Model.race
		if not race:
			category = None
		else:
			category = race.getCategoryStartWave( FixCategories(self.categoryChoice, getattr(race, 'resultsCategory', 0)) )
		categoryName = category.fullname if category else ''
		if categoryName != self.showingCategory.GetLabel():
			self.showingCategory.SetLabel( categoryName )
			self.hbs.Layout()
		return category
	
	def getRaceInfo( self ):
		race = Model.race
		if not race:
			return False, []
			
		category = self.getCategory()
		if not category:
			return False, []

		results = GetResults( category )
		if not results or not results[0].lapTimes:
			return False, []

		return True, [race, category, results, len(results[0].lapTimes)]
	
	def getError( self, bib, lapsToGo, laps ):
		if not bib:
			return ''
		if not lapsToGo:
			lapsToGo = 1
		success, info = self.getRaceInfo()
		if not success:
			return ''
		race, category, results, laps = info
		
		if bib not in race.riders:
			return _('Bib not in Race')
		if race.getCategory(bib) != category:
			return _('Bib not in Category')
		rider = race.riders[bib]
		if rider.status not in (Model.Rider.Pulled, Model.Rider.Finisher):
			return '{}: {}'.format(_('Bib has non-Finisher Status'), Model.Rider.statusNames[rider.status])			
		if lapsToGo >= laps:
			return '{}: {}'.format(_('Laps To Go exceeds for Race Laps'), laps )
		if lapsToGo <= 0:
			return '{}'.format(_('Laps To Go must be >= 0') )
		return ''
	
	def onCellChange( self, event ):
		row, col = event.GetRow(), event.GetCol()
		colName = self.colNameFields[col][1]
		GetTranslation = _

		if colName == 'pulledBib' or colName == 'lapsToGo':
			bib = int( '0' + re.sub( '[^0-9]', '', self.grid.GetCellValue(row, self.iCol['pulledBib'])) )
			for r in range(row, -1, -1):
				lapsToGo = int( '0' + self.grid.GetCellValue(r, self.iCol['lapsToGo']) )
				if lapsToGo:
					break
			if not lapsToGo:
				lapsToGo = 1
			
			success, info = self.getRaceInfo()
			if not success:
				return
			race, category, results, laps = info
			
			name, team, component = getRiderInfo(bib)
			self.grid.SetCellValue( row, self.iCol['pulledName'], name )
			self.grid.SetCellValue( row, self.iCol['pulledTeam'], team )
			self.grid.SetCellValue( row, self.iCol['pulledComponent'], component )
			self.grid.SetCellValue( row, self.iCol['pulledError'], self.getError(bib, lapsToGo, laps) )
					
			wx.CallAfter( self.grid.AutoSizeColumns, False )
	
	def setRow( self, bib, lapsToGo, laps, row, updateGrid=True ):
		name, team, component = getRiderInfo(bib)
		values = {
			'pulledBib':bib, 'pulledName':name, 'pulledTeam':team, 'pulledComponent':component,
			'pulledError':self.getError(bib, lapsToGo, laps), 'lapsToGo':lapsToGo
		}		
		for col, (name, attr, valuesType) in enumerate(self.colNameFields):
			self.grid.SetCellValue( row, col, str(values[attr]) )
		return values
	
	def getRow( self, row ):
		values = {'row':row}
		for col, (name, attr, dataType) in enumerate(self.colNameFields):
			v = self.grid.GetCellValue( row, col ).strip()
			if dataType == 'i':
				v = ''.join( c for c in v if c.isdigit() )
				v = int( v or 0 )
			elif dataType == 'f':
				v = ''.join( c for c in v if c.isdigit() or c == '.')
				v = float( v or 0.0 )
			elif dataType == 't':
				v = Utils.StrToSeconds( v or '' )
				
			values[attr] = v
		
		return values
		
	def updateGrid( self ):
		self.grid.ClearGrid()
		
		success, info = self.getRaceInfo()
		if not success:
			return
		race, category, results, laps = info
		
		if race.isTimeTrial:
			return
		
		Pulled = Model.Rider.Pulled
		pulled = []
		for rr in results:
			if race.riders[rr.num].status == Pulled:
				pulled.append( getPulledCmpTuple(rr, race.riders[rr.num], laps, False) )
		pulled.sort()
		bibLapsToGo = { p[-1].num:abs(p[0]) for p in pulled }
		pulled = [p[-1] for p in pulled]
		
		Utils.AdjustGridSize( self.grid, len(pulled) + 20 )
		for row, rr in enumerate(pulled):
			self.setRow( rr.num, bibLapsToGo[rr.num], laps, row )
		
		# Remove repeated lapsToGo entries.
		col = self.iCol['lapsToGo']
		for row in range(self.grid.GetNumberRows()-1, 0, -1):
			if self.grid.GetCellValue( row, col) == self.grid.GetCellValue( row-1, col):
				self.grid.SetCellValue( row, col, '')
		
		self.grid.AutoSizeColumns( False )								# Resize to fit the column name.
		self.grid.AutoSizeRows( False )
	
	def refresh( self ):
		success, info = self.getRaceInfo()
		if not success:
			return self.updateGrid()
		race, category, results, laps = info
		if race.isTimeTrial:
			self.grid.SaveEditControlValue()	# Make sure the current edit is committed.
			self.grid.DisableCellEditControl()
			self.grid.ClearGrid()
			return
		col = self.iCol['pulledBib']
		tableBibs = set( int('0' + self.grid.GetCellValue(row, col)) for row in range(self.grid.GetNumberRows()) )
		tableBibs.discard( 0 )
		if not tableBibs:
			return self.updateGrid()
		
		Pulled = Model.Rider.Pulled
		allBibs = set( rr.num for rr in results )
		if not allBibs >= tableBibs:
			return self.updateGrid()
		pulledBibs = set( rr.num for rr in results if race.riders[rr.num].status == Pulled )
		if not tableBibs >= pulledBibs:
			return self.updateGrid()
		
	def commit( self ):
		self.grid.SaveEditControlValue()	# Make sure the current edit is committed.
		self.grid.DisableCellEditControl()
		
		race = Model.race
		if not race:
			return
		race.useTableToPullRiders = self.useTableToPullRidersCkBox.GetValue()
		if not race.useTableToPullRiders:
			self.grid.ClearGrid()
			Utils.AdjustGridSize( self.grid, 20 )
			return
		
		rows = [self.getRow(r) for r in range(self.grid.GetNumberRows())]
		rows = [rv for rv in rows if rv['pulledBib']]
		
		# Fix any missing data lapsToGo in the table.
		lapsToGoLast = 1
		for rv in rows:
			if not rv['lapsToGo']:
				rv['lapsToGo'] = lapsToGoLast
			lapsToGoLast = rv['lapsToGo']
			
		success, info = self.getRaceInfo()
		if not success:
			return False
		race, category, results, laps = info
		rule80LapTime = race.getRule80LapTime( category )
		
		changed = False
		Finisher, Pulled = Model.Rider.Finisher, Model.Rider.Pulled
		for rr in results:
			rider = race.riders.get(rr.num, None)
			if not rider or race.getCategory(rr.num) != category:
				continue
			if rider.status == Pulled:
				rider.status = Finisher
				changed = True
		
		lapsToGoPulled = defaultdict( list )
		for rv in rows:
			lapsToGoPulled[rv['lapsToGo']].append( rv['pulledBib'] )
			
		for lapsToGo, bibs in lapsToGoPulled.items():
			if lapsToGo <= 0:
				continue
			for seq, bib in enumerate(bibs):
				try:
					rider = race.riders[bib]
				except KeyError:
					continue
					
				rider.status = Pulled
				rider.pulledLapsToGo = lapsToGo
				rider.pulledSequence = seq
				changed = True

		if changed:
			race.setChanged()
		self.updateGrid()

if __name__ == '__main__':
	app = wx.App(False)
	app.SetAppName("CrossMgr")
	
	Utils.disable_stdout_buffering()
	
	race = Model.newRace()
	race._populate()
	
	fnameRiderInfo = os.path.join(Utils.getHomeDir(), 'CrossMgrSimulation', 'SimulationRiderData.xlsx')
	sheetName = 'Registration'
	
	race.excelLink = ExcelLink()
	race.excelLink.setFileName( fnameRiderInfo )
	race.excelLink.setSheetName( sheetName )
	race.excelLink.setFieldCol( {'Bib#':0, 'LastName':1, 'FirstName':2, 'Team':3} )
	
	mainWin = wx.Frame(None, title="Pulled", size=(800,700) )
	pulled = Pulled( mainWin )
	mainWin.Show()
	
	pulled.refresh()	
	app.MainLoop()
