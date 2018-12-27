import wx
import wx.grid			as gridlib
import re
import os
import sys
import math
import operator
from collections import defaultdict
import Utils
import Model
from ReorderableGrid 	import ReorderableGrid
from FinishStrip		import ShowFinishStrip
from ReadSignOnSheet	import ExcelLink
from GetResults			import GetResults, getPulledCmpTuple
from RaceInputState import RaceInputState
from Undo import undo

def getRiderInfo( bib ):
	race = Model.race
	if not race or not bib:
		return u'', u''
	
	try:
		riderInfo = race.excelLink.read()[bib]
	except Exception as e:
		return u'', u''

	return u', '.join( f for f in (riderInfo.get('LastName',u''), riderInfo.get('FirstName',u'')) if f ), riderInfo.get('Team', u'')

class TimeEditor(gridlib.GridCellEditor):
	defaultValue = '00:00.000'

	def __init__(self):
		self._tc = None
		self.startValue = self.defaultValue
		gridlib.GridCellEditor.__init__(self)
		
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
			except:
				pass
		val = Utils.formatTime( s, highPrecision=True ) if s else u''
		if val != self.startValue:
			changed = True
			grid.GetTable().SetValue( row, col, val )
		
	def Reset( self ):
		self._tc.SetValue( self.startValue )
		
	def Clone( self ):
		return TimeEditor()
		
def FixCategories( choice, iSelection = None ):
	choice.InvalidateBestSize() 
	choice.SetSize(choice.GetBestSize()) 

	race = Model.race
	if iSelection is None:
		iSelection = getattr( race, 'modelCategory', 0 ) or 0
		if iSelection > 0:
			iSelection -= 1
	
	items = choice.GetItems()
	choice.SetSelection( iSelection )

	categories = race.getCategories( startWaveOnly=True ) if race else []
	newItems = [c.fullname for c in categories]
	if items == newItems:
		return categories[choice.GetSelection()]
	
	catNameCur = None
	if items:
		catNameCur = items[choice.GetSelection()]
	
	choice.Clear()
	choice.AppendItems( newItems )
	
	iNew = 0
	if catNameCur is not None:
		for i, fullname in enumerate(newItems):
			if catNameCur == fullname:
				iNew = i
				break
		
	choice.SetSelection( iNew )
	return categories[choice.GetSelection()]
	
def SetCategory( choice, cat ):
	if FixCategories(choice) != cat:
		if cat is None:
			choice.SetSelection( 0 )
		else:
			for i, item in enumerate(choice.GetItems()):
				if item.strip() == cat.fullname:
					choice.SetSelection( i )
					race.modelCategory = i+1
					break

class Pulled( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize ):
		super(Pulled, self).__init__( parent, id, size=size )
		
		self.state = RaceInputState()
		
		vsOverall = wx.BoxSizer( wx.VERTICAL )
		
		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.categoryLabel = wx.StaticText( self, label=_('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		self.commitBtn = wx.Button( self, label=_('Commit') )
		self.commitBtn.Bind( wx.EVT_BUTTON, self.doCommit )
		self.hbs.Add( self.categoryLabel, flag=wx.ALIGN_CENTRE_VERTICAL )
		self.hbs.Add( self.categoryChoice, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=2 )
		self.hbs.Add( self.commitBtn, flag=wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=64 )
		
		#---------------------------------------------------------------
		self.colNameFields = (
			(_('Laps to Go'),			'lapsToGo',		'i'),
			(u'    ' + _('Bib'),		'pulledBib',	'i'),
			(u'Name',					'pulledName',	's'),
			(u'Team',					'pulledTeam',	's'),
			(u'Message',				'pulledMessage','s'),
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
	
	def doChooseCategory( self, event ):
		self.refresh()
	
	def doCommit( self, event ):
		self.commit()
		self.refresh()
	
	def getCategory( self ):
		return FixCategories( self.categoryChoice, self.categoryChoice.GetSelection())
	
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
	
	def getMessage( self, bib, lapsToGo, laps ):
		if not bib:
			return u''
		if not lapsToGo:
			lapsToGo = 1
		success, info = self.getRaceInfo()
		if not success:
			return u''
		race, category, results, laps = info
		
		if bib not in race.riders:
			return _(u'Bib not in Race')
		if race.getCategory(bib) != category:
			return _(u'Bib not in Category')
		rider = race.riders[bib]
		if rider.status not in (Model.Rider.Pulled, Model.Rider.Finisher):
			return u'{}: {}'.format(_('Bib has non-finisher Status'), Model.Rider.statusNames[rider.status])			
		if lapsToGo >= laps:
			return u'{}: {}'.format(_('Laps To Go too large for Race Laps'), laps )
		return u''
	
	def onCellChange( self, event ):
		row, col = event.GetRow(), event.GetCol()
		colName = self.colNameFields[col][1]
		GetTranslation = _

		if colName == 'pulledBib' or colName == 'lapsToGo':
			bib = int( '0' + re.sub( '[^0-9]', '', self.grid.GetCellValue(row, self.iCol['pulledBib'])) )
			for r in xrange(row, -1, -1):
				lapsToGo = int( '0' + self.grid.GetCellValue(r, self.iCol['lapsToGo']) )
				if lapsToGo:
					break
			if not lapsToGo:
				lapsToGo = 1
			
			success, info = self.getRaceInfo()
			if not success:
				return
			race, category, results, laps = info
			
			name, team = getRiderInfo(bib)
			self.grid.SetCellValue( row, self.iCol['pulledName'], name )
			self.grid.SetCellValue( row, self.iCol['pulledTeam'], team )
			self.grid.SetCellValue( row, self.iCol['pulledMessage'], self.getMessage(bib, lapsToGo, laps) )
					
			wx.CallAfter( self.grid.AutoSizeColumns, False )
	
	def setRow( self, bib, lapsToGo, laps, row, updateGrid=True ):
		name, team = getRiderInfo(bib)
		values = { 'pulledBib':bib, 'pulledName':name, 'pulledTeam':team, 'pulledMessage':self.getMessage(bib, lapsToGo, laps), 'lapsToGo':lapsToGo }		
		for col, (name, attr, valuesType) in enumerate(self.colNameFields):
			self.grid.SetCellValue( row, col, unicode(values[attr]) )
		return values
	
	def getRow( self, row ):
		values = {'row':row}
		for col, (name, attr, dataType) in enumerate(self.colNameFields):
			v = self.grid.GetCellValue( row, col ).strip()
			if dataType == 'i':
				v = u''.join( c for c in v if c.isdigit() )
				v = int( v or 0 )
			elif dataType == 'f':
				v = u''.join( c for c in v if c.isdigit() or c == '.')
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
		for row in xrange(self.grid.GetNumberRows()-1, 0, -1):
			if self.grid.GetCellValue( row, col) == self.grid.GetCellValue( row-1, col):
				self.grid.SetCellValue( row, col, u'')
		
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
		tableBibs = set( int(u'0' + self.grid.GetCellValue(row, col)) for row in xrange(self.grid.GetNumberRows()) )
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
		
		rows = [self.getRow(r) for r in xrange(self.grid.GetNumberRows())]
		rows = [rv for rv in rows if rv['pulledBib']]
		if not rows:
			return True
		
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
		
		Finisher, Pulled = Model.Rider.Finisher, Model.Rider.Pulled
		for rr in results:
			rider = race.riders.get(rr.num, None)
			if not rider or race.getCategory(rr.num) != category:
				continue
			if rider.status == Pulled:
				rider.status = Finisher
		
		lapsToGoPulled = defaultdict( list )
		for rv in rows:
			lapsToGoPulled[rv['lapsToGo']].append( rv['pulledBib'] )
			
		for lapsToGo, bibs in lapsToGoPulled.iteritems():
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
