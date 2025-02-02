import re

import wx.grid as gridlib

class DistanceCellEditor(gridlib.GridCellFloatEditor):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('width', 7)
		kwargs.setdefault('precision', 3)
		super().__init__(*args, **kwargs)

	def EndEdit(self, row, col, grid, oldval):
		new_value = self.Control.GetValue()
		new_value = self.clean_float(new_value)

		import sys
		if new_value is not None and float(new_value) == -sys.float_info.max:
			new_value = ''
		elif new_value is None:
			new_value = ''

		if oldval == new_value:
			return None

		self.Control.SetValue(new_value)
		return new_value

	@staticmethod
	def clean_float(float_str:str) -> str | None:
		if not float_str:
			return None
		cleaned_str = float_str
		cleaned_str = cleaned_str.replace(',', '.')
		# Use regex to keep only digits, decimal points, and minus signs
		cleaned_str = re.sub(r'[^0-9.-]', '', cleaned_str)
		cleaned_str = cleaned_str.count('.') > 1 and cleaned_str.replace('.', '', 1) or cleaned_str
		return cleaned_str

	def BeginEdit(self, row, col, grid):
		currentValue = grid.GetCellValue(row, col)
		try:
			parsed = self.clean_float(currentValue)
		except ValueError:
			return None
		if parsed is None:
			parsed = ''
		self.Control.SetValue(parsed)
		self.Control.SetFocus()
		self.Control.SetSelection(0, self.Control.GetLastPosition())