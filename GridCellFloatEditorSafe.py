import re
import wx
import wx.grid

def santitizeFloatStr( v ):
	v = v.replace(',', '.')				# In case there is a comma decimal separator
	v = re.sub( '[^0-9.]', '', v )		# In case there are non-digit thousands separators
	v = '.'.join(v.split('.')[:2])		# Ensure there is only one decimal place.
	return v

class GridCellFloatEditorSafe( wx.grid.GridCellFloatEditor ):
	'''
		Ensure that the cell being passed to the GridCellFloatEditor
		is a valid float.  Otherwise wx will throw an exception.
	'''
	def __init__( self, width=-1, precision=-1, format=wx.grid.GRID_FLOAT_FORMAT_DEFAULT ):
		self._width, self._precision, self._format = width, precision, format
		super().__init__( width, precision, format )
		
	def SetParameters( self, params ):
		self._params = params
		super().SetParameters( params )
		
	def Clone( self ):
		clone = GridCellFloatEditorSafe( self._width, self._precision, self._format )
		if hasattr( self, '_params' ):
			clone.SetParameters( self._params )
		return clone
		
	def BeginEdit( self, row, col, grid ):
		vOrig = '{}'.format(grid.GetCellValue(row, col))
		v = santitizeFloatStr( vOrig )
		try:
			f = float( v )
		except ValueError:
			v = ''
		if v != vOrig:
			grid.SetCellValue( row, col, v )
		return super().BeginEdit( row, col, grid )
