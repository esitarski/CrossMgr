import xlwt
import Model
import Utils
from GetResults import GetResults
from FitSheetWrapper import FitSheetWrapper

UCIFields = (
	'Pos',
	'Nr.',
	'Name',
	'UCI Code',
	'Team',
)

def UCIExport( sheet, cat ):
	race = Model.race
	if not race:
		return
		
	sheetFit = FitSheetWrapper( sheet )
	
	titleStyle = xlwt.XFStyle()
	titleStyle.font.bold = True
	
	leftAlignStyle = xlwt.XFStyle()
	
	rightAlignStyle = xlwt.XFStyle()
	rightAlignStyle.alignment.horz = xlwt.Alignment.HORZ_RIGHT
	
	results = GetResults( cat, True )
		
	def toInt( n ):
		try:
			return int(n)
		except:
			return n
			
	row = 0
	for col, field in enumerate(UCIFields):
		sheetFit.write( row, col, field, titleStyle, bold=True )
	row += 1
	
	for rr in results:
		for col, field in enumerate(UCIFields):
			{
				'Pos':		lambda : sheetFit.write( row, col, toInt(rr.pos), rightAlignStyle ),
				'Nr.':		lambda : sheetFit.write( row, col, rr.num, rightAlignStyle ),
				'Name':		lambda : sheetFit.write( row, col, rr.full_name(), leftAlignStyle ),
				'UCI Code':	lambda : sheetFit.write( row, col, getattr(rr, 'License', ''), leftAlignStyle ),
				'Team':		lambda : sheetFit.write( row, col, getattr(rr, 'Team', ''), leftAlignStyle ),
			}[field]()
		row += 1
