import re
import wx
import wx.grid

class GridCellNumberEditorSafe( wx.grid.GridCellNumberEditor ):
	'''
		Ensure that the cell being passed to the GridCellNumberEditor
		is a valid integer.  Otherwise wx will throw an exception.
	'''
	def __init__(self, min=-1, max=-1):
		self._min, self._max = min, max
		super().__init__( min, max )
		
	def SetParameters( self, params ):
		self._params = params
		super().SetParameters( params )
		
	def Clone( self ):
		clone = GridCellNumberEditorSafe( self._min, self._max )
		if hasattr( self, '_params' ):
			clone.SetParameters( self._params )
		return clone

	def BeginEdit( self, row, col, grid ):
		v = vOrig = '{}'.format(grid.GetCellValue(row, col))
		v = re.sub( '[^0-9]', '', v )
		try:
			n = int( v )
		except ValueError:
			v = ''
		if v != vOrig:
			grid.SetCellValue( row, col, v )
		return super().BeginEdit( row, col, grid )
