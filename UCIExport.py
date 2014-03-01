import re
import math
import xlwt
import Model
import Utils
from GetResults import GetResults
from FitSheetWrapper import FitSheetWrapper

def formatTime( secs, highPrecision = False ):
	if secs is None:
		secs = 0
	if secs < 0:
		sign = '-'
		secs = -secs
	else:
		sign = ''
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = int(secs // (60*60))
	minutes = int( (secs // 60) % 60 )
	secs = secs % 60
	if highPrecision:
		decimal = '.%02d' % int( f * 100 )
	else:
		decimal = ''
	return "%s%02d:%02d:%02d%s" % (sign, hours, minutes, secs, decimal)

UCIFields = (
	'Pos',
	'Nr.',
	'Name',
	'Team',
	'UCI Code',
	'Time',
	'Gap',
)

reHighPrecision = re.compile( '^.*\.[0-9][0-9]"$' )

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
		try:
			finishTime = formatTime(rr.lastTime - rr.raceTimes[0]) if rr.status == Model.Rider.Finisher else ''
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
