import Model
import Utils
from GetResults import GetResults, UnstartedRaceWrapper

import copy
import xlsxwriter
import operator

countryReference = '''Code	French Country Name	English Country Name
AFG	AFGHANISTAN	AFGHANISTAN
AHO	ANTILLES NEERLANDAISES	NETHERLANDS ANTILLES
ALB	ALBANIE	ALBANIA
ALG	ALGERIE	ALGERIA
AND	ANDORRE	ANDORRA
ANG	ANGOLA	ANGOLA
ANT	ANTIGUA-ET-BARBUDA	ANTIGUA AND BARBUDA
ARG	ARGENTINE	ARGENTINA
ARM	ARMENIE	ARMENIA
ARU	ARUBA	ARUBA
AUS	AUSTRALIE	AUSTRALIA
AUT	AUTRICHE	AUSTRIA
AZE	AZERBAIDJAN	AZERBAIJAN
BAH	BAHAMAS	BAHAMAS
BAN	BANGLADESH	BANGLADESH
BAR	BARBADE	BARBADOS
BDI	BURUNDI	BURUNDI
BEL	BELGIQUE	BELGIUM
BEN	BENIN	BENIN
BER	BERMUDES	BERMUDA
BIH	BOSNIE-HERZEGOVINE	BOSNIA AND HERZEGOVINA
BIR	BIRMA	BURMA
BIZ	BELIZE	BELIZE
BLR	BELARUS	BELARUS
BOL	BOLIVIE	BOLIVIA
BOT	BOTSWANA	BOTSWANA
BRA	BRESIL	BRAZIL
BRN	BAHREIN	BAHRAIN
BRU	BRUNEI DARUSSALAM	BRUNEI DARUSSALAM
BUL	BULGARIE	BULGARIA
BUR	BURKINA FASO	BURKINA FASO
CAF	REPUBLIQUE CENTRAFRICAINE	CENTRAL AFRICAN REPUBLIC
CAM	CAMBODGE	CAMBODIA
CAN	CANADA	CANADA
CAY	ILES CAÏMANS	CAYMAN ISLANDS
CGO	CONGO	CONGO
CHA	TCHAD	CHAD
CHI	CHILI	CHILE
CHN	REPUBLIQUE POPULAIRE DE CHINE	PEOPLE'S REPUBLIC OF CHINA
CIV	COTE D'IVOIRE	COTE D'IVOIRE
CMR	CAMEROUN	CAMEROON
COD	REPUBLIQUE DEMOCRATIQUE DU CONGO	DEMOCRATIC REPUBLIC OF THE CONGO
COL	COLOMBIE	COLOMBIA
COM	COMORES	COMOROS
CPV	CAP-VERT	CAPE VERDE
CRC	COSTA RICA	COSTA RICA
CRO	CROATIE	CROATIA
CUB	CUBA	CUBA
CUR	CURAÇAO	CURACAO
CYP	CHYPRE	CYPRUS
CZE	REPUBLIQUE TCHEQUE	CZECH REPUBLIC
DEN	DANEMARK	DENMARK
DJI	DJIBOUTI	DJIBOUTI
DOM	REPUBLIQUE DOMINICAINE	DOMINICAN REPUBLIC
ECU	EQUATEUR	ECUADOR
EGY	EGYPTE	EGYPT
ERI	ERYTHREE	ERITREA
ESA	EL SALVADOR	EL SALVADOR
ESP	ESPAGNE	SPAIN
EST	ESTONIE	ESTONIA
ETH	ETHIOPIE	ETHIOPIA
FIJ	FIDJI	FIJI
FIN	FINLANDE	FINLAND
FRA	FRANCE	FRANCE
GAB	GABON	GABON
GAM	GAMBIE	GAMBIA
GBR	GRANDE BRETAGNE	GREAT BRITAIN
GEO	GEORGIE	GEORGIA
GER	ALLEMAGNE	GERMANY
GHA	GHANA	GHANA
GRE	GRECE	GREECE
GRN	GRENADA	GRENADA
GUA	GUATEMALA	GUATEMALA
GUI	GUINEE	GUINEA
GUM	GUAM	GUAM
GUY	GUYANA	GUYANA
HAI	HAITI	HAITI
HKG	HONG-KONG, CHINE	HONG KONG, CHINA
HON	HONDURAS	HONDURAS
HUN	HONGRIE	HUNGARY
INA	INDONESIE	INDONESIA
IND	INDE	INDIA
IRI	REPUBLIQUE ISLAMIQUE D'IRAN	ISLAMIC REPUBLIC OF IRAN
IRL	IRLANDE	IRELAND
IRQ	IRAQ	IRAQ
ISL	ISLANDE	ICELAND
ISR	ISRAEL	ISRAEL
ISV	ILES VIERGES	VIRGIN ISLANDS
ITA	ITALIE	ITALY
JAM	JAMAIQUE	JAMAICA
JOR	JORDANIE	JORDAN
JPN	JAPON	JAPAN
KAZ	KAZAKHSTAN	KAZAKHSTAN
KEN	KENYA	KENYA
KGZ	KIRGHIZISTAN	KYRGYZSTAN
KOR	COREE	KOREA
KOS	KOSOVO	KOSOVO
KSA	ARABIE SAOUDITE	SAUDI ARABIA
KUW	KOWEIT	KUWAIT
LAO	REPUBLIQUE POPULAIRE DEMOCRATIQUE LAO	LAO PEOPLE'S DEMOCRATIC REPUBLIC
LAT	LETTONIE	LATVIA
LBA	LIBYE	LIBYA
LBR	LIBERIA	LIBERIA
LCA	SAINTE-LUCIE	SAINT LUCIA
LES	LESOTHO	LESOTHO
LIB	LIBAN	LEBANON
LIE	LIECHTENSTEIN	LIECHTENSTEIN
LTU	LITUANIE	LITHUANIA
LUX	LUXEMBOURG	LUXEMBOURG
MAC	MACAO, CHINE	MACAO, CHINA
MAD	MADAGASCAR	MADAGASCAR
MAR	MAROC	MOROCCO
MAS	MALAISIE	MALAYSIA
MAW	MALAWI	MALAWI
MDA	REPUBLIQUE DE MOLDOVA	REPUBLIC OF MOLDOVA
MEX	MEXIQUE	MEXICO
MGL	MONGOLIE	MONGOLIA
MKD	EX-REPUBLIQUE YOUGOSLAVE DE MACEDOINE	FORMER YUGOSLAV REPUBLIC OF MACEDONIA
MLI	MALI	MALI
MLT	MALTE	MALTA
MNE	MONTENEGRO	MONTENEGRO
MON	MONACO	MONACO
MOZ	MOZAMBIQUE	MOZAMBIQUE
MRI	MAURICE	MAURITIUS
MTN	MAURITANIE	MAURITANIA
MYA	MYANMAR	MYANMAR
NAM	NAMIBIE	NAMIBIA
NCA	NICARAGUA	NICARAGUA
NED	PAYS-BAS	NETHERLANDS
NEP	NEPAL	NEPAL
NGR	NIGERIA	NIGERIA
NIG	NIGER	NIGER
NOR	NORVEGE	NORWAY
NZL	NOUVELLE-ZELANDE	NEW ZEALAND
OMA	OMAN	OMAN
PAK	PAKISTAN	PAKISTAN
PAN	PANAMA	PANAMA
PAR	PARAGUAY	PARAGUAY
PER	PEROU	PERU
PHI	PHILIPPINES	PHILIPPINES
PNG	PAPUA NEW GUINEA	PAPUA NEW GUINEA
POL	POLOGNE	POLAND
POR	PORTUGAL	PORTUGAL
PRK	REPUBLIQUE POPULAIRE DEMOCRATIQUE DE COREE	DEMOCRATIC PEOPLE'S REPUBLIC OF KOREA
PUR	PORTO RICO	PUERTO RICO
QAT	QATAR	QATAR
ROU	ROUMANIE	ROMANIA
RSA	AFRIQUE DU SUD	SOUTH AFRICA
RUS	FEDERATION DE RUSSIE	RUSSIAN FEDERATION
RWA	RWANDA	RWANDA
SAM	SAMOA	SAMOA
SCG	SERBIE ET MONTENEGRO	SERBIA AND MONTENEGRO
SEN	SENEGAL	SENEGAL
SEY	SEYCHELLES	SEYCHELLES
SIN	SINGAPOUR	SINGAPORE
SKN	SAINT KITTS ET NEVIS	SAINT KITTS AND NEVIS
SLE	SIERRA LEONE	SIERRA LEONE
SLO	SLOVENIE	SLOVENIA
SMR	SAINT-MARIN	SAN MARINO
SOM	SOMALIE	SOMALIA
SRB	SERBIE	SERBIA
SRI	SRI LANKA	SRI LANKA
STP	SAO TOME ET PRINCIPE	SAO TOME AND PRINCIPE
SUD	SOUDAN	SUDAN
SUI	SUISSE	SWITZERLAND
SUR	SURINAME	SURINAME
SVK	SLOVAQUIE	SLOVAKIA
SWE	SUEDE	SWEDEN
SWZ	SWAZILAND	SWAZILAND
SYR	REPUBLIQUE ARABE SYRIENNE	SYRIAN ARAB REPUBLIC
TAN	REPUBLIQUE UNIE DE TANZANIE	UNITED REPUBLIC OF TANZANIA
THA	THAILANDE	THAILAND
TKM	TURKMENISTAN	TURKMENISTAN
TLS	TIMOR-LESTE	TIMOR LESTE
TOG	TOGO	TOGO
TPE	CHINESE TAIPEI	CHINESE TAIPEI
TTO	TRINITE-ET-TOBAGO	TRINIDAD AND TOBAGO
TUN	TUNISIE	TUNISIA
TUR	TURQUIE	TURKEY
UAE	EMIRATS ARABES UNIS	UNITED ARAB EMIRATES
UGA	OUGANDA	UGANDA
UKR	UKRAINE	UKRAINE
UNK	UNKNOWN	UNKNOWN
URU	URUGUAY	URUGUAY
USA	ETATS-UNIS D'AMERIQUE	UNITED STATES OF AMERICA
UZB	OUZBEKISTAN	UZBEKISTAN
VAN	VANUATU	VANUATU
VEN	RÉPUBLIQUE BOLIVARIENNE DU VENEZUELA	BOLIVARIAN REPUBLIC OF VENEZUELA
VIE	VIETNAM	VIETNAM
VIN	SAINT-VINCENT-ET-LES-GRENADINES	SAINT VINCENT AND THE GRENADINES
YAR	YEMEN ARABIAN REPUBLIC	YEMEN ARABIAN REPUBLIC
YEM	YEMEN	YEMEN
ZAM	ZAMBIE	ZAMBIA
ZIM	ZIMBABWE	ZIMBABWE'''

reference = '''Attribute	Value	Comment
Result type	TIME	Result based on time
	POINTS	Result based on points
Competitor Type	A	Individual event
	T	Team event
Gender	M	Man
	W	Woman
IRM	DNF	Did not finish
	DNS	Did not start
	DSQ	Disqualified
	LAP	Lapped
	OTL	Over Time Limit
	REL	Relegated
	OVL	Overlapped
Version	1	
	2	
	3	
	4	
	5	
	6	
	7	
	8	
	9	
	10	
Phase	Final	Final
	1/2 Finals	Semifinals
	1/4 Finals	Quarterfinals
	1/8 Finals	
	1/16 Finals	
	1/32 Finals	
	1/64 Finals	
Race Type	IRR	Individual Road Race
	TTT	Team Time Trial
	ITT	Individual Time Trial
	OM	Omnium
	DHI	Downhill'''

def formatUciId( uci_id ):
	# Normalize to a string.
	if isinstance(uci_id, float):
		uci_id = '{:.0f}'.format( uci_id )
	else:
		uci_id = '{}'.format( uci_id )
	#s = u' '.join( uci_id[i:i+3] for i in range(0, len(uci_id), 3) ) if uci_id.isdigit() else uci_id	# add separating spaces to UCI ID.
	s = uci_id
	return s.replace( ' ', '' )		# UCI does not accept spaces in UCI IDs.
	
def UCIExcel( category, fname, startList=False ):
	race = Model.race
	if not startList and race.isUnstarted():
		return
	
	Finisher = Model.Rider.Finisher
	statusNames = Model.Rider.statusNames
	
	rrWinner = None
	if race.isUnstarted():
		with UnstartedRaceWrapper():
			results = GetResults( category )
	else:
		results = GetResults( category )
		try:
			rrWinner = results[0]
		except:
			pass
	
	if startList:
		results = sorted( copy.deepcopy(results), key=operator.attrgetter('num') )
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
		(u'Race Type',			u'',			u'Race type of the Event (IRR, XCO, OM)',	u'Optional'),
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
		colWidths[col] = max( colWidths.get(col, 0), len('{}'.format(v)) )
	
	fmt = general_header_format
	for row, r in enumerate(general, 3):
		for col, v in enumerate(r):
			ww( row, col, v, fmt )
		fmt = general_format

	for col, width in colWidths.items():
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
	
	odd_format_merge = wb.add_format( dict(bottom=1, valign='vcenter') )

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
		if rrWinner and rrWinner.laps != rr.laps:
			return rr.laps - rrWinner.laps
		try:
			finishTime = rr.lastTime - rr.raceTimes[0]
			return Utils.formatTime(finishTime, forceHours=True, twoDigitHours=True)
		except:
			return u''
			
	def getIRM( rr ):
		if 'REL' in '{}'.format(rr.pos):
			return 'REL'
		if rrWinner and rr.laps != rrWinner.laps:
			return 'LAP'
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

	colWidths.clear()
	for c, name in enumerate(colNames):
		ww( 0, c, name, header_format )
		
	for row, rr in enumerate(results, 1):
		for col, name in enumerate(colNames):
			ww( row, col, getValue.get(name, lambda rr:u'')(rr), getFmt(name, row) )
	
	for col, width in colWidths.items():
		ws.set_column( col, col, width+2 )
	
	ws.autofilter( 0, 0, len(results)+1, len(colNames) )	

	#-------------------------------------------------------------------
	# Reference sheets
	#-------------------------------------------------------------------
	ws = wb.add_worksheet('Reference')
	colWidths.clear()
	rowLast = len(reference.split('\n'))
	merge = {}
	rowMergeLast = None
	for row, line in enumerate(reference.split('\n')):
		fields = line.split('\t')
		for col, v in enumerate(fields):
			if row == 0:
				fmt = header_format
			elif row == rowLast:
				fmt = odd_format_last
			else:
				fmt = odd_format
			if row != 0 and col == 0:
				if v:
					merge[row] = {'data':v}
					rowMergeLast = row
				merge[rowMergeLast]['last_row'] = row
			else:
				ww( row, col, v, fmt )
	for first_row, md in merge.items():
		ws.merge_range(first_row, 0, md['last_row'], 0, md['data'], odd_format_merge)
		colWidths[0] = max( colWidths.get(0, 0), len('{}'.format(md['data'])) )
	for col, width in colWidths.items():
		ws.set_column( col, col, width+2 )

	#-------------------------------------------------------------------
	ws = wb.add_worksheet('Country Reference')
	colWidths.clear()
	rowLast = len(countryReference.split('\n'))
	for row, line in enumerate(countryReference.split('\n')):
		fields = line.split('\t')
		for col, v in enumerate(fields):
			if row == 0:
				fmt = header_format
			elif row == rowLast:
				fmt = even_format_last if row%2 == 0 else odd_format_last
			else:
				fmt = even_format if row%2 == 0 else odd_format
			ww( row, col, v, fmt )
	for col, width in colWidths.items():
		ws.set_column( col, col, width+2 )
	
	wb.close()
