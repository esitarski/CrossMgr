import os
import sys
import random
from operator import attrgetter

import wx
import wx.grid as gridlib

import TestData
from ReorderableGrid import ReorderableGrid
import Model
import Utils
from Events import FontSize
from ReadStartList import ImportStartList
from Competitions import getCompetitions

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
		
		self.randomizeButton = wx.Button( self, label='Randomize...' )
		self.randomizeButton.Bind( wx.EVT_BUTTON, self.doRandomize )
		self.randomizeButton.SetFont( font )
 
		self.sortByUCIPointsButton = wx.Button( self, label='Sort by UCI Points...' )
		self.sortByUCIPointsButton.Bind( wx.EVT_BUTTON, self.doSortByUCIPoints )
		self.sortByUCIPointsButton.SetFont( font )
 
		self.importButton = wx.Button( self, label='Import From Excel' )
		self.importButton.Bind( wx.EVT_BUTTON, self.doImportFromExcel )
		self.importButton.SetFont( font )
 
		self.headerNames = ['Bib', 'First Name', 'Last Name', 'Team', 'Team Code', 'UCIID', 'UCI Points']
		self.headerNameMap = Model.Rider.GetHeaderNameMap( self.headerNames )
		
		self.iUCIPoints = self.headerNameMap['uci_points']
		
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
			if col == 0:
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
		hs.Add( self.sortByUCIPointsButton, 0, flag=wx.ALL, border=4 )
		hs.Add( self.randomizeButton, 0, flag=wx.ALL, border=4 )
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
		
		Model.model.setCompetition( getCompetitions()[0], 0 )
		self.commit()
		
	def getGrid( self ):
		return self.grid
	
	def doRandomize( self, event ):
		self.commit()
		self.refresh()
		
		selectedRows = self.grid.GetSelectedRows()
		if len(selectedRows) < 2:
			Utils.MessageOK( self, 'Please select some Rows to Randomize.', 'Insufficient Selected Rows' )
			return
			
		rMin = min( selectedRows )
		rMax = max( selectedRows ) + 1
		
		model = Model.model
		if len(model.riders) <= rMin:
			return
		rMax = min( rMax, len(model.riders) )
		
		if not Utils.MessageOKCancel( self, 'Randomize Rows {}-{} ?'.format(rMin+1, rMax), 'Confirm Randomize' ):
			return
		
		toRandomize = model.riders[rMin:rMax]
		random.shuffle( toRandomize )
		model.riders[rMin:rMax] = toRandomize
		self.refresh()
	
	def doSortByUCIPoints( self, event ):
		self.commit()
		self.refresh()
		
		selectedRows = self.grid.GetSelectedRows()
		if len(selectedRows) < 2:
			Utils.MessageOK( self, 'Please select some Rows to Sort.', 'Insufficient Selected Rows' )
			return
			
		rMin = min( selectedRows )
		rMax = max( selectedRows ) + 1
		
		model = Model.model
		if len(model.riders) <= rMin:
			return
		rMax = min( rMax, len(model.riders) )
		
		if not Utils.MessageOKCancel( self, 'Sort Rows {}-{} ?'.format(rMin+1, rMax), 'Confirm Sort' ):
			return
		
		toSort = model.riders[rMin:rMax]
		toSort.sort( key=attrgetter('uci_points'), reverse=True )
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
			fields = {}
			for attr, col in self.headerNameMap.items():
				fields[attr] = self.grid.GetCellValue(row, col).strip()
				
			try:
				fields['bib'] = int(fields['bib'])
			except ValueError:
				continue
			try:
				fields['uci_points'] = float(fields['uci_points'])
			except ValueError:
				continue
				
			if fields['bib']:
				riders.append( Model.Rider(**fields) )
		
		model = Model.model
		
		cn = self.communiqueNumber.GetValue()
		if cn != model.communique_number.get(self.phase, ''):
			model.communique_number[self.phase] = self.communiqueNumber.GetValue()
			model.setChanged()
		
		oldRiders = dict( (r.bib, r) for r in model.riders )
		oldPosition = dict( (r.bib, p) for p, r in enumerate(model.riders) )
		
		# Check for changes to the seeding.
		changed =  (len(riders) != len(model.riders))
		changed |= any( position != oldPosition.get(r.bib, -1) for position, r in enumerate(riders) )
		changed |= any( r.keyDataFields() != oldRiders.get(r.bib, Model.Rider(-1)).keyDataFields() for r in riders )
		if not changed:
			return
		
		model.setChanged( True )
		
		# Update riders if the competition has not yet started.
		if model.canReassignStarters():
			for r in riders:
				try:
					oldRiders[r.bib].copyDataFields( r )
				except KeyError:
					oldRiders[r.bib] = r
			model.riders = [oldRiders[r.bib] for r in riders]
			model.setQualifyingTimes()
			mainWin = Utils.getMainWin()
			if mainWin:
				Utils.getMainWin().resetEvents()
			return
		
		if len(riders) != len(model.riders):
			for r in riders:
				if r.bib in oldRiders:
					oldRiders[r.bib].copyDataFields( r )
			Utils.MessageOK( self, 'Cannot Add or Delete Riders after Competition has Started', 'Cannot Add or Delete Riders' )
			self.refresh()
			return
		
		if not all( r.bib in oldRiders for r in riders ):
			for r in riders:
				if r.bib in oldRiders:
					oldRiders[r.bib].copyDataFields( r )
			Utils.MessageOK( self, 'Cannot Change Bib Numbers after Competition has Started', 'Cannot Change Bib Numbers' )
			self.refresh()
			return
		
		# All the bib numbers match - just change the info and update the sequence.
		model.riders = [oldRiders[r.bib].copyDataFields(r) for r in riders]
		model.updateSeeding()
		
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
