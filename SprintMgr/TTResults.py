import os
import sys
import wx
import wx.grid as gridlib

import TestData
import Utils
import Model
from ReorderableGrid import ReorderableGrid
from Events import GetFont

class TTResults(wx.Panel):
	#----------------------------------------------------------------------
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
 
		self.headerNames = ['Pos', 'Bib', 'Name', 'Team', 'Time']
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 0 )
		self.grid.CreateGrid( 0, len(self.headerNames) )
		self.setColNames()
		self.grid.EnableReorderRows( False )

		# Set a larger font for the table.
		# Set specialized editors for appropriate columns.
		font = GetFont()
		self.grid.SetLabelFont( font )
		for col in range(self.grid.GetNumberCols()):
			attr = gridlib.GridCellAttr()
			attr.SetFont( font )
			if col == self.grid.GetNumberCols() - 1:
				attr.SetRenderer( gridlib.GridCellFloatRenderer(-1, 3) )
				attr.SetEditor( gridlib.GridCellFloatEditor(-1, 3) )
			else:
				if col in (0, 1):
					attr.SetRenderer( gridlib.GridCellNumberRenderer() )
				attr.SetReadOnly( True )
			self.grid.SetColAttr( col, attr )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6)
		self.SetSizer(sizer)
		
	def setColNames( self ):
		for col, headerName in enumerate(self.headerNames):
			self.grid.SetColLabelValue( col, headerName )
						
	def getGrid( self ):
		return self.grid
		
	def refresh( self ):
		riders = sorted( Model.model.riders, key = lambda r: r.qualifyingTime )
		starters = Model.model.competition.starters
		
		Utils.AdjustGridSize( self.grid, rowsRequired = len(riders) )
		for row, r in enumerate(riders):
			if row < starters:
				pos = u'{}'.format(row + 1)
			else:
				pos = 'DNQ'
				for col in range(self.grid.GetNumberCols()):
					self.grid.SetCellBackgroundColour( row, col, wx.Colour(200,200,200) )
			for col, value in enumerate([pos,u' {}'.format(r.bib), r.full_name, r.team, '%.3f' % r.qualifyingTime]):
				self.grid.SetCellValue( row, col, value )
				
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )
		
	def commit( self ):
		pass
		
########################################################################

class TTResultsFrame(wx.Frame):
	""""""
 
	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		wx.Frame.__init__(self, None, title="Qualifier Grid Test", size=(800,600) )
		panel = TTResults(self)
		panel.refresh()
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	Model.model = SetDefaultData()
	frame = TTResultsFrame()
	app.MainLoop()
