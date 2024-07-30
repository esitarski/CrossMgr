import wx
import wx.grid as gridlib

import os
import SeriesModel
from ReorderableGrid import ReorderableGrid
import Utils

def shorterFilename( fileName ):
	fileName = fileName.replace('\\','/')
	components = fileName.split('/')
	return os.path.join( *components[-3:] )

class Errors(wx.Panel):
	ErrorCol = 0
	RaceCol = 1
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.headerNames = ['Error', 'Race']
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(self.headerNames) )
		for col in range(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, self.headerNames[col] )
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly( True )
			self.grid.SetColAttr( col, attr )
				
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6)
		self.SetSizer(sizer)
	
	def getGrid( self ):
		return self.grid
		
	def gridAutoSize( self ):
		self.grid.AutoSize()
		self.grid.EnableDragGridSize( False )
		self.grid.EnableDragColSize( False )
		self.Layout()
		self.Refresh()
	
	def refresh( self ):
		model = SeriesModel.model
		Utils.AdjustGridSize( self.grid, len(model.errors) )
		for row, (r, e) in enumerate(model.errors):
			self.grid.SetCellValue( row, self.RaceCol, shorterFilename(r.fileName) )
			self.grid.SetCellValue( row, self.ErrorCol, f'{e}' )
		wx.CallAfter( self.gridAutoSize )
	
	def commit( self ):
		pass
		
class ErrorsFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="Error Test", size=(800,600) )
		self.panel = Errors(self)
		self.Show()
 
if __name__ == "__main__":
	app = wx.App(False)
	frame = ErrorsFrame()
	frame.panel.refresh()
	app.MainLoop()
