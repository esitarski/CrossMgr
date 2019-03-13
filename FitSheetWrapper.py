import arial10
import six
import datetime
import Utils
import math

class FitSheetWrapper(object):
	"""Try to fit columns to max size of any entry.
	To use, wrap this around a worksheet returned from the 
	workbook's add_sheet method, like follows:

		sheet = FitSheetWrapper(book.add_sheet(sheet_name))

	The worksheet interface remains the same: this is a drop-in wrapper
	for auto-sizing columns.
    """
	def __init__(self, sheet):
		self.sheet = sheet
		self.widths = {}
		self.heights = {}

	def write(self, r, c, label='', *args, **kwargs):
		if 'bold' in kwargs:
			isBold = True
			del kwargs['bold']
		else:
			isBold = False
		
		self.sheet.write(r, c, label, *args, **kwargs)
		if isinstance(label, datetime.date):
			label = label.strftime('%b %d, %Y')
		elif isinstance(label, datetime.time):
			label = '00:00:00'
		else:
			label = Utils.removeDiacritic( six.text_type(label) )
		if label.find( '\n' ) >= 0:
			width, height = arial10.fitWidthHeight(label, isBold)
			if height > self.heights.get(r, 0):
				self.heights[r] = height
				self.sheet.row(r).height = height
		else:
			width = arial10.fitWidth(label, isBold)
		width = min( int(math.ceil(width)), 65535 )
		if width > self.widths.get(c, 0):
			self.widths[c] = width
			self.sheet.col(c).width = width

	def __getattr__(self, attr):
		return getattr(self.sheet, attr)
		
StandardCharWidth = arial10.charwidths['0'] * 0.95
class FitSheetWrapperXLSX(object):
	"""Try to fit columns to max size of any entry.
	To use, wrap this around a worksheet returned from the 
	workbook's add_sheet method, like follows:

		sheet = FitSheetWrapper(book.add_sheet(sheet_name))

	The worksheet interface remains the same: this is a drop-in wrapper
	for auto-sizing columns.
    """
	def __init__(self, sheet):
		self.sheet = sheet
		self.widths = {}
		self.heights = {}

	def write(self, r, c, data, *args, **kwargs):
		isBold = kwargs.pop('bold', False)
		self.sheet.write(r, c, data, *args, **kwargs)
		
		if isinstance(data, datetime.date):
			data = data.strftime('%b %d, %Y')
		elif isinstance(data, datetime.time):
			data = '00:00:00'
		else:
			data = Utils.removeDiacritic( six.text_type(data) )
		if '\n' in data:
			width, height = arial10.fitWidthHeight(data, isBold)
			height /= StandardCharWidth
			if height > self.heights.get(r, 0.0):
				self.heights[r] = height
				self.sheet.set_row(r, height)
		else:
			width = arial10.fitWidth(data, isBold)
		width /= StandardCharWidth
		if width > self.widths.get(c, 0.0):
			self.widths[c] = width
			self.sheet.set_column( c, c, width )

	def __getattr__(self, attr):
		return getattr(self.sheet, attr)
