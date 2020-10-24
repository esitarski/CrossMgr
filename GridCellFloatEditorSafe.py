import re
import wx

class GridCellFloatEditorSafe( wx.grid.GridCellFloatEditor ):
	'''
		Ensure that the cell being passed to the GridCellFloatEditor
		is a valid float.
	'''
	def BeginEdit( self, row, col, grid ):
		v = vOrig = '{}'.format(grid.GetCellValue(row, col))
		v = re.sub( '[^0-9.]', '', v )
		v = '.'.join(v.split('.')[:2])
		try:
			f = float( v )
		except ValueError:
			v = ''
		if v != vOrig:
			grid.SetCellValue( row, col, v )
		return super().BeginEdit( row, col, grid )
