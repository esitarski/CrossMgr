import re
import math
import xlwt
import Model
import Utils
from GetResults import GetResults
from FitSheetWrapper import FitSheetWrapper
from ReadSignOnSheet import SyncExcelLink

UCIFields = (
	'Pos',
	'Nr.',
	'Name',
	'Team',
	'UCI Code',
	'Time',
	'Gap',
)

def formatTimeGap( secs ):
	return Utils.formatTimeGap(
		secs,
		forceHours=True,
		separateWithQuotes=False,
	)

reHighPrecision = re.compile( '^.*\.[0-9][0-9]"$' )

def UCIExport( sheet, cat ):
	race = Model.race
	if not race:
		return
		
	SyncExcelLink( race )
	
	sheetFit = FitSheetWrapper( sheet )
	
	titleStyle = xlwt.XFStyle()
	titleStyle.font.bold = True
	
	leftAlignStyle = xlwt.XFStyle()
	
	rightAlignStyle = xlwt.XFStyle()
	rightAlignStyle.alignment.horz = xlwt.Alignment.HORZ_RIGHT
	
	results = GetResults( cat )
		
	def toInt( n ):
		try:
			return int(n.split()[0])
		except:
			return n
			
	row = 0
	for col, field in enumerate(UCIFields):
		sheetFit.write( row, col, field, titleStyle, bold=True )
	row += 1
	
	for rr in results:
		try:
			finishTime = formatTimeGap(rr.lastTime - rr.raceTimes[0]) if rr.status == Model.Rider.Finisher else ''
		except Exception as e:
			finishTime = ''
			
		gap = getattr(rr, 'gap', '')
		if reHighPrecision.match(gap):
			gap = gap[:-4] + '"'

		for col, field in enumerate(UCIFields):
			{
				'Pos':		lambda : sheetFit.write( row, col, toInt(rr.pos), rightAlignStyle ),
				'Nr.':		lambda : sheetFit.write( row, col, rr.num, rightAlignStyle ),
				'Name':		lambda : sheetFit.write( row, col, rr.full_name(), leftAlignStyle ),
				'Team':		lambda : sheetFit.write( row, col, getattr(rr, 'Team', ''), leftAlignStyle ),
				'UCI Code':	lambda : sheetFit.write( row, col, getattr(rr, 'UCICode', ''), leftAlignStyle ),
				'Time':		lambda : sheetFit.write( row, col, finishTime, rightAlignStyle ),
				'Gap':		lambda : sheetFit.write( row, col, gap, rightAlignStyle ),
			}[field]()
		row += 1
