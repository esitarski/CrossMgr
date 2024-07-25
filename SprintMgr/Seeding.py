import os
import random

import wx
import wx.grid as gridlib

import TestData
from ReorderableGrid import ReorderableGrid
import Model
import Utils
from Events import FontSize
from ReadStartList import ImportStartList
from Competitions import getCompetitions

class SortDialog( wx.Dialog ):
	def __init__( self, parent, rMin = 0, rMax = 0, id = wx.ID_ANY ):
		super().__init__( parent, id, "Sort Seeding",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		FontSize = 24
		font = wx.Font( (0,FontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'view_sort_descending.png'), wx.BITMAP_TYPE_PNG )
		restartBitmap = wx.StaticBitmap( self, bitmap=bitmap )
		
		title = wx.StaticText( self, label='Sort Seeding' )
		title.SetFont( font )
		self.titleText = title
		
		hsTitle = wx.BoxSizer( wx.HORIZONTAL )
		hsTitle.Add( restartBitmap, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		hsTitle.Add( title, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border = 4 )
		
		sizer.Add( hsTitle, flag=wx.EXPAND )
		
		rows = wx.StaticText( self, label="Rows {}-{}".format(rMin+1, rMax) )
		sizer.Add( rows, flag=wx.EXPAND|wx.ALL, border=4 )

		explain = wx.StaticText( self, label="Sort by Decreasing Points, then Increasing Rank" )
		sizer.Add( explain, flag=wx.EXPAND|wx.ALL, border=4 )

		self.ttOrder = wx.CheckBox( self, label="Time Trial Order (highest goes last)" )
		self.ttOrder.SetValue( Model.model.competition and not Model.model.competition.isKeirin )

		self.randomize = wx.CheckBox( self, label="Randomize Ties" )
		self.randomize.SetValue( False )
		
		sizer.Add( self.randomize, flag=wx.ALL, border = 4 )
		sizer.Add( self.ttOrder, flag=wx.ALL, border = 4 )
		
		btnSizer = self.CreateStdDialogButtonSizer( wx.OK|wx.CANCEL )
		if btnSizer:
			sizer.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border = 4 )
		self.SetSizerAndFit( sizer )

class Seeding(wx.Panel):
	#----------------------------------------------------------------------
	
	phase = 'Seeding'

	def __init__(self, parent):
		super().__init__(parent)
 
		font = wx.Font( (0,FontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		
		self.title = wx.StaticText(self, label="Seeding" + ':')
		self.title.SetFont( font )
		
		self.communiqueLabel = wx.StaticText( self, label='Communiqu\u00E9:' )
		self.communiqueLabel.SetFont( font )
		self.communiqueNumber = wx.TextCtrl( self, size=(64,-1) )
		self.communiqueNumber.SetFont( font )
		
		self.sortButton = wx.Button( self, label='Sort Rows...' )
		self.sortButton.Bind( wx.EVT_BUTTON, self.doSort )
		self.sortButton.SetFont( font )
 
		self.importButton = wx.Button( self, label='Import From Excel' )
		self.importButton.Bind( wx.EVT_BUTTON, self.doImportFromExcel )
		self.importButton.SetFont( font )
 
		self.headerNames = ['Bib', 'First Name', 'Last Name', 'Team', 'Team Code', 'UCIID', 'UCI Points', 'Seeding Rank']
		self.headerNameMap = Model.Rider.GetHeaderNameMap( self.headerNames )
		
		self.iBib = 0
		self.iUCIPoints = self.headerNameMap['uci_points']
		self.iSeedingRank = self.headerNameMap['seeding_rank']
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 200, len(self.headerNames) )
		self.setColNames()

		# Set specialized editors for appropriate columns.
		self.grid.SetLabelFont( font )
		for col in range(self.grid.GetNumberCols()):
			attr = gridlib.GridCellAttr()
			attr.SetFont( font )
			if col in (self.iBib, self.iSeedingRank):
				attr.SetRenderer( gridlib.GridCellNumberRenderer() )
				attr.SetEditor( gridlib.GridCellNumberEditor() )
			elif col == self.iUCIPoints:
				attr.SetRenderer( gridlib.GridCellFloatRenderer(precision=2) )
				attr.SetEditor( gridlib.GridCellFloatEditor(precision=2) )
			self.grid.SetColAttr( col, attr )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.title, 0, flag=wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT, border = 8 )
		hs.Add( self.communiqueLabel, 0, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=4 )
		hs.Add( self.communiqueNumber, 0, flag=wx.ALL|wx.EXPAND, border=4 )
		hs.AddStretchSpacer()
		hs.Add( self.sortButton, 0, flag=wx.ALL, border=4 )
		hs.Add( self.importButton, 0, flag=wx.ALL, border=4 )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add( hs, 0, flag=wx.ALL|wx.EXPAND, border=6 )
		sizer.Add( wx.StaticText(self, label='Set Bib to 0 to Delete row.  Drag-and-drop row numbers to Change Sequence.'), flag=wx.LEFT, border = 8 )
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border=6)
		self.SetSizer(sizer)
		
	def setColNames( self ):
		for col, headerName in enumerate(self.headerNames):
			self.grid.SetColLabelValue( col, headerName )
						
	def setTestData( self ):
		self.grid.ClearGrid()
		
		testData = TestData.getTestData()
		for row, data in enumerate(testData):
			for k, v in data.items():
				if k in self.headerNameMap:
					if k == 'uci_points':
						v = '{:.2f}'.format(v)
					self.grid.SetCellValue( row, self.headerNameMap[k],'{}'.format(v) )
		
		# Fix up the column and row sizes.
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )
		
		Model.model.setCompetition( next(c for c in getCompetitions() if 'Keirin' in c.name), 0 )
		self.commit()
		
	def getGrid( self ):
		return self.grid
	
	def doSort( self, event ):
		model = Model.model
		
		if not model.canReassignStarters():
			Utils.MessageOK( self, 'Cannot sort seeding after Competition has Started', 'Cannot Sort' )
			return
		
		self.commit()
		self.refresh()

		selectedRows = self.grid.GetSelectedRows()
		if len(selectedRows) < 2:
			selectedRows = (0, len(model.riders)-1)
			
		rMin, rMax = min(selectedRows), max(selectedRows) + 1
		
		if len(model.riders) <= rMin:
			return
		rMax = min( rMax, len(model.riders) )
		
		with SortDialog(self, rMin=rMin, rMax=rMax) as sortDlg:
			sortDlg.randomize.SetValue( getattr(self, 'randomize', False) )
			if sortDlg.ShowModal() == wx.ID_OK:
				self.randomize = sortDlg.randomize.GetValue()
				ttOrder = sortDlg.ttOrder.GetValue()
				toSort = model.riders[rMin:rMax]
				if self.randomize:
					keyFunc = lambda r: (-r.uci_points, r.seeding_rank, random.random())
				else:
					keyFunc = lambda r: (-r.uci_points, r.seeding_rank)
				toSort.sort( key=keyFunc, reverse=ttOrder )
				model.riders[rMin:rMax] = toSort
				
		self.refresh()
		
	def doImportFromExcel( self, event ):
		ImportStartList( self )
		
	def getTitle( self ):
		title = 'Communique: {}\n{} '.format(
					self.communiqueNumber.GetValue(),
					'Qualifier Seeding' )
		return title
	
	def refresh( self ):
		riders = Model.model.riders
		for row, r in enumerate(riders):
			for attr, col in self.headerNameMap.items():
				value = getattr( r, attr )
				if attr == 'uci_points':
					value = '' if not value else '{:.2f}'.format(value)
				elif attr == 'seeding_rank':
					value = '' if not value else value
				self.grid.SetCellValue( row, col, '{}'.format(value) )
				
		for row in range(len(riders), self.grid.GetNumberRows()):
			for col in range(self.grid.GetNumberCols()):
				self.grid.SetCellValue( row, col, '' )
				
		# Fix up the column and row sizes.
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )
		
		# Sync the communique value.
		self.communiqueNumber.SetValue( Model.model.communique_number.get(self.phase, '') )
		
		self.Layout()
		self.Refresh()
				
	def commit( self ):
		self.grid.SaveEditControlValue()

		riders = []
		for row in range(self.grid.GetNumberRows()):
			fields = { attr:self.grid.GetCellValue(row, col).strip() for attr, col in self.headerNameMap.items() }
				
			try:
				fields['bib'] = int(fields['bib'])
			except ValueError:
				continue

			if fields['bib']:
				riders.append( Model.Rider(**fields) )
		
		model = Model.model
		
		cn = self.communiqueNumber.GetValue()
		if cn != model.communique_number.get(self.phase, ''):
			model.communique_number[self.phase] = self.communiqueNumber.GetValue()
			model.setChanged()
		
		oldRiders = { r.bib:r for r in model.riders }
		oldPosition = { r.bib:p for p, r in enumerate(model.riders) }
		
		def sameData( rTo, rFrom ):
			return all( getattr(rTo, attr) == getattr(rFrom, attr) for attr in self.headerNameMap.keys() )
		
		# Check for changes.
		missingRider = Model.Rider(-1)
		changed =  (
			len(riders) != len(model.riders) or
			any( position != oldPosition.get(r.bib, -1) for position, r in enumerate(riders) ) or
			any( not sameData(r, oldRiders.get(r.bib, missingRider)) for r in riders )
		)
		if not changed:
			return
		
		model.setChanged( True )
		
		def copySeedingData( rTo, rFrom ):
			for attr in self.headerNameMap.keys():
				setattr( rTo, attr, getattr(rFrom, attr) )
			return rTo
		
		if model.canReassignStarters():
			# The competition has not started.
			# We can reset all the rider data, including seeding order.
			for r in riders:
				try:
					copySeedingData( oldRiders[r.bib], r )
				except KeyError:
					oldRiders[r.bib] = r
			model.riders = [oldRiders[r.bib] for r in riders]
			model.setQualifyingInfo()
			mainWin = Utils.getMainWin()
			if mainWin:
				mainWin.resetEvents()
		else:
			# The competition has started.
			# Just copy the data fields to the riders.
			for r in riders:
				if r.bib in oldRiders:
					copySeedingData( oldRiders[r.bib], r )
			Utils.MessageOK( self, 'Cannot Add, Delete or Change Seeding after Competition has Started', 'Cannot Add or Delete Riders' )
			
		wx.CallAfter( self.refresh )
		
########################################################################

class SeedingFrame(wx.Frame):
	def __init__(self):
		"""Constructor"""
		super().__init__(parent=None, title="Seeding Test", size=(800,600) )
		panel = Seeding(self)
		panel.setTestData()
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	frame = SeedingFrame()
	app.MainLoop()
