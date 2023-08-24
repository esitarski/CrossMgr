import wx
import os

import Utils
import Model
from GetResults import GetResults
from ReorderableGrid import ReorderableGrid

class Prizes( wx.Panel ):
	rowsMax = 20
	
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize ):
		super().__init__( parent, id, size=size )
		
		vsOverall = wx.BoxSizer( wx.VERTICAL )
		
		self.grid = ReorderableGrid( self )
		self.grid.CreateGrid( 0, 10 )
		
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )
		
		self.grid.Bind( wx.grid.EVT_GRID_CELL_CHANGED, self.onCellChange )
		
		#---------------------------------------------------------------
		
		vsOverall.Add( self.grid, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		self.SetSizer( vsOverall )
	
	def onCellChange( self, event ):
		race = Model.race
		if not race:
			return
		row, col = event.GetRow(), event.GetCol()
		if col & 1:
			return
		categories = race.getCategories( startWaveOnly=False, publishOnly=True )
		if self.grid.GetNumberCols() != len(categories)*2:
			Utils.AdjustGridSize( self.grid, self.rowsMax, len(categories)*2 )
		if row >= self.grid.GetNumberRows() or col >= self.grid.GetNumberCols():
			return
		self.copyToRace()
		try:
			category = categories[col//2]
		except IndexError:
			return
		self.grid.SetCellValue( row, col+1, self.getRecepient(self.grid.GetCellValue(row, col), row, category) )
		wx.CallAfter( self.grid.AutoSizeColumns, False )
	
	def getRecepient( self, prize, row, category ):
		if not prize:
			return ''
		name = ''
		results = GetResults( category )
		try:
			name = '{}: {}'.format(results[row].num, results[row].full_name())
		except IndexError:
			pass
		return name
		
	def setCellPair( self, row, col, category ):
		try:
			prize = getattr( category, 'prizes', [] )[row]
		except IndexError:
			prize = ''
		self.grid.SetCellValue( row, col, prize )				
		self.grid.SetCellValue( row, col+1, self.getRecepient(prize, row, category) )
		
	def updateGrid( self ):
		race = Model.race
		if not race:
			self.grid.ClearGrid()
			return
		categories = race.getCategories( startWaveOnly=False, publishOnly=True )
		Utils.AdjustGridSize( self.grid, self.rowsMax, len(categories)*2 )
		col = 0
		for category in categories:
			fullname = category.fullname
			ib = fullname.rfind( '(' )
			catname, catgender = fullname[:ib].strip(), fullname[ib:]
			colName = '{}\n{}'.format( catname, catgender )
			self.grid.SetColLabelValue( col, colName )
			attr = wx.grid.GridCellAttr()
			attr.SetReadOnly( False )
			attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
			self.grid.SetColAttr( col, attr )
			
			self.grid.SetColLabelValue( col+1, _('Recipient') )
			attr = wx.grid.GridCellAttr()
			attr.SetReadOnly( True )
			attr.SetAlignment( wx.ALIGN_LEFT, wx.ALIGN_CENTRE )
			attr.SetBackgroundColour( wx.Colour(152,251,152) )
			self.grid.SetColAttr( col+1, attr )

			for row in range(self.rowsMax):
				self.setCellPair( row, col, category )
			col += 2
	
		self.grid.AutoSizeColumns( False )								# Resize to fit the column name.
		self.grid.AutoSizeRows( False )
	
	def refresh( self ):
		self.updateGrid()
		
	def copyToRace( self ):
		race = Model.race
		if not race:
			return
		
		categories = race.getCategories( startWaveOnly=False, publishOnly=True )
		for i, category in enumerate(categories):
			prizes = []
			for row in range(self.rowsMax):
				v = self.grid.GetCellValue( row, i*2 ).strip()
				if not v:
					break
				prizes.append( v )
			category.prizes = prizes
		
	def commit( self ):
		self.grid.SaveEditControlValue()	# Make sure the current edit is committed.
		self.grid.DisableCellEditControl()
		self.copyToRace()
			
if __name__ == '__main__':
	app = wx.App(False)
	app.SetAppName("CrossMgr")
	
	Utils.disable_stdout_buffering()
	
	race = Model.newRace()
	race._populate()
	
	fnameRiderInfo = os.path.join(Utils.getHomeDir(), 'SimulationRiderData.xlsx')
	
	mainWin = wx.Frame(None, title="Prizes", size=(800,700) )
	prizes = Prizes( mainWin )
	mainWin.Show()
	
	prizes.refresh()	
	app.MainLoop()
