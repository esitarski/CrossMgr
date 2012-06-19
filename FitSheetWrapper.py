import arial10
import datetime
import Utils

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
			label = Utils.removeDiacritic( unicode(label) )
		if label.find( '\n' ) >= 0:
			width, height = arial10.fitWidthHeight(label, isBold)
			if height > self.heights.get(r, 0):
				self.heights[r] = height
				self.sheet.row(r).height = height
		else:
			width = arial10.fitWidth(label, isBold)
		if width > self.widths.get(c, 0):
			self.widths[c] = width
			self.sheet.col(c).width = width

	def __getattr__(self, attr):
		return getattr(self.sheet, attr)