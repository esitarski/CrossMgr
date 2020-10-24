import re
import wx

class GridCellNumberEditorSafe( wx.grid.GridCellNumberEditor ):
	'''
		Ensure that the cell being passed to the GridCellNumberEditor
		is a valid integer.  Otherwise wx will throw an exception.
	'''
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
