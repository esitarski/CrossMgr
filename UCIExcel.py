import Model
import Utils
from GetResults import GetResults

import copy
import xlsxwriter
import operator

def formatUciId( uci_id ):
	return u' '.join( uci_id[i:i+3] for i in xrange(0, len(uci_id), 3) ) if uci_id.isdigit() else uci_id
	
def countryFromUciId( uci_id ):
	if uci_id.isdigit():
		return u''
	return uci_id[:3]
	
def UCIExcel( category, fname, startList=False ):
	race = Model.race
	if not startList and race.isUnstarted():
		return
	
	Finisher = Model.Rider.Finisher
	statusNames = Model.Rider.statusNames
	
	if race.isUnstarted():
		with UnstartedRaceWrapper():
			results = GetResults( category )
	else:
		results = GetResults( category )
	
	if startList:
		results = list( copy.deepcopy( GetResults(category) ) )
		results.sort( key=operator.attrgetter('num') )
		for pos, rr in enumerate(results, 1):
			rr.pos = u'{}'.format(pos)
			rr.status = Finisher
	
	wb = xlsxwriter.Workbook( fname )
	
	title_format = wb.add_format( dict(font_size=24, valign='vcenter') )
	
	general_header_format = wb.add_format( dict(font_color='white', bg_color='black', bottom=1, right=1) )
	general_format = wb.add_format( dict(bottom=1, right=1) )
	
	#-------------------------------------------------------------------------------------------------------
	ws = wb.add_worksheet('General')
	if startList:
		ws.write( 0, 0, u"UCI Event's Start List File", title_format )
	else:
		ws.write( 0, 0, u"UCI Event's Results File", title_format )
	ws.set_row( 0, 26 )
	
	general = [
		(u'Field',				u'Value',		u'Description',								u'Comment'),
		(u'Competition Code',	u'',			u'UCI unique competition code',				u'Filled by the system'),
		(u'Event Code',			u'',			u'UCI unique event code',					u'Filled by the system'),
		(u'Race Type',			u'IRR',			u'Race type of the Event (IRR, XCO, OM)',	u'Optional'),
		(u'Competitor Type',	u'A',			u'A or T (Athlete or Team)',				u'Mandatory'),
		(u'Result type',		u'Time',		u'Points or Time',							u'Mandatory'),
		(u'Document version',	1.0,			u'Version number of the file',				u'Mandatory'),
	]
	
	colWidths = {}
	def ww( row, col, v, fmt=None ):
		if fmt:
			ws.write( row, col, v, fmt )
		else:
			ws.write( row, col, v )
		colWidths[col] = max( colWidths.get(col, 0), len(unicode(v)) )
	
	fmt = general_header_format
	for row, r in enumerate(general, 3):
		for col, v in enumerate(r):
			ww( row, col, v, fmt )
		fmt = general_format

	for col, width in colWidths.iteritems():
		ws.set_column( col, col, width+2 )

	#-------------------------------------------------------------------------------------------------------	
	header_format = wb.add_format( dict(font_color='white', bg_color='black', bottom=1) )
	
	gray = 'D8D8D8'
	
	odd_format = wb.add_format( dict(bottom=1) )
	even_format = wb.add_format( dict(bg_color=gray, bottom=1) )
	
	odd_format_last = wb.add_format( dict(bottom=1, right=1) )
	even_format_last = wb.add_format( dict(bg_color=gray, bottom=1, right=1) )
	
	odd_format_center = wb.add_format( dict(align='center',bottom=1) )
	even_format_center = wb.add_format( dict(align='center',bg_color=gray, bottom=1) )
	
	odd_format_right = wb.add_format( dict(align='right',bottom=1) )
	even_format_right = wb.add_format( dict(align='right',bg_color=gray, bottom=1) )
	
	if startList:
		ws = wb.add_worksheet('StartList')
	else:
		ws = wb.add_worksheet('Results')
	
	if startList:
		colNames = ['Start Order', 'BIB', 'UCI ID', 'Last Name', 'First Name', 'Country', 'Team', 'Gender']
	else:
		colNames = ['Rank', 'BIB', 'UCI ID', 'Last Name', 'First Name', 'Country', 'Team', 'Gender', 'Phase', 'Heat', 'Result', 'IRM', 'Sort Order']
	
	def getFmt( name, row ):
		if name == 'Sort Order':
			return odd_format_last if row&1 else even_format_last
		if name in ('Start Order', 'Rank', 'BIB'):
			return odd_format_center if row&1 else even_format_center
		if name == 'Result':
			return odd_format_right if row&1 else even_format_right
		return odd_format if row&1 else even_format
		
	def toInt( n ):
		try:
			return int(n.split()[0])
		except:
			return n

	def getFinishTime( rr ):
		if rr.status != Finisher:
			return u''
		try:
			finishTime = rr.lastTime - rr.raceTimes[0]
			return Utils.formatTime(finishTime, forceHours=True, twoDigitHours=True)
		except:
			return u''
			
	def getIRM( rr ):
		if 'REL' in unicode(rr.pos):
			return 'REL'
		return u'' if rr.status == Finisher else statusNames[rr.status].replace('DQ', 'DSQ')
	
	getValue = {
		'Start Order':	lambda rr: toInt(rr.pos),
		'Rank':			lambda rr: toInt(rr.pos) if rr.status == Finisher else '',
		'BIB':			operator.attrgetter('num'),
		'UCI ID':		lambda rr: formatUciId(getattr(rr, 'UCIID', u'')),
		'Last Name':	lambda rr: getattr(rr, 'LastName', u''),
		'First Name':	lambda rr: getattr(rr, 'FirstName', u''),
		'Country':		lambda rr: getattr(rr, 'NatCode', u''),
		'Team':			lambda rr: getattr(rr, 'TeamCode', u''),
		'Gender':		lambda rr: getattr(rr, 'Gender', u'')[:1],
		'Result':		getFinishTime,
		'IRM':			getIRM,
		'Phase':		lambda rr: u'Final',
	}

	colWidths = {}
	for c, name in enumerate(colNames):
		ww( 0, c, name, header_format )
		
	for row, rr in enumerate(results, 1):
		for col, name in enumerate(colNames):
			ww( row, col, getValue.get(name, lambda rr:u'')(rr), getFmt(name, row) )
	
	for col, width in colWidths.iteritems():
		ws.set_column( col, col, width+2 )
	
	ws.autofilter( 0, 0, len(results)+1, len(colNames) )	
	
	wb.close()
