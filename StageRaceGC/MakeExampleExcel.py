# coding=utf8

import os
import datetime
import operator
import random
import xlsxwriter
import Utils
from Excel import GetExcelReader
from FitSheetWrapper import FitSheetWrapperXLSX

def get_license():
	return ''.join( 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[random.randint(0,25)] for i in range(6) )

def get_uci_id():
	dob = datetime.date.today() - datetime.timedelta( days=random.normalvariate(25,3)*365.25 )
	return 'FRA{}'.format( dob.strftime( '%Y%m%d' ) ) 

def get_uci_id():
	uci_id = ''.join(random.choice('123456789') for i in range(9))
	uci_id += '{:02d}'.format(int(uci_id)%97)
	return uci_id

stage_points = '''
50	30	20	18	16	14	12	10	8	7	6	5	4	3	2
30	25	22	19	17	15	13	11	9	7	6	5	4	3	2
20	17	15	13	11	10	9	8	7	6	5	4	3	2	1'''.strip()
stage_points = stage_points.split( '\n' )
stage_points = [[int(n) for n in s.split()] for s in stage_points]

mountain_points = '''
1st	1	2	5	10	25
2nd		1	3	8	20
3rd			2	6	16
4th			1	4	14
5th				2	12
6th				1	10
7th					8
8th					6
9th					4
10th				2'''.strip()

kom_by_category = [[] for x in range(5)]
for c in range(5):
	for p, line in enumerate(mountain_points.split('\n')):
		try:
			kom_by_category[c].append( int(line.split('\t')[5-c]) )
		except Exception as e:
			break

def MakeExampleExcel():
	random.seed( 0xed )
	
	common_first_names = 'Léopold Grégoire Aurélien Rémi Léandre Thibault Kylian Nathan Lucas Enzo Léo Louis Hugo Gabriel Ethan Mathis Jules Raphaël Arthur Théo Noah Timeo Matheo Clément Maxime Yanis Maël'.split()
	common_last_names = 'Tisserand Lavergne Guignard Parmentier Evrard Leclerc Martin Bernard Dubois Petit Durand Leroy Moreau Simon Laurent Lefevre Roux Fournier Dupont'.split()
	teams = 'Pirates of the Pavement,Coastbusters,Tour de Friends,Pesky Peddlers,Spoke & Mirrors'.split(',')
	
	fname_excel = os.path.join( Utils.getHomeDir(), 'StageRaceGC_Test_Input.xlsx' )
	
	wb = xlsxwriter.Workbook( fname_excel )
	bold_format = wb.add_format( {'bold': True} )
	time_format = wb.add_format( {'num_format': 'hh:mm:ss'} )
	high_precision_time_format = wb.add_format( {'num_format': 'hh:mm:ss.000'} )
	
	ws = wb.add_worksheet('Registration')
	fit_sheet = FitSheetWrapperXLSX( ws )
	
	fields = ['bib', 'first_name', 'last_name', 'uci_id', 'license', 'team']
	row = 0
	for c, field in enumerate(fields):
		fit_sheet.write( row, c, Utils.fieldToHeader(field), bold_format )
		
	riders = 25
	team_size = riders // len(teams)
	bibs = []
	for i in range(riders):
		row += 1
		bibs.append((i//team_size+1)*10 + (i%team_size))
		fit_sheet.write( row, 0, bibs[i] )
		fit_sheet.write( row, 1, common_first_names[i%len(common_first_names)] )
		fit_sheet.write( row, 2, common_last_names[i%len(common_last_names)] )
		fit_sheet.write( row, 3, get_uci_id() )
		fit_sheet.write( row, 4, get_license() )
		fit_sheet.write( row, 5, teams[i//team_size] )

	stageCount = 5
	for stage in range(stageCount):
		isTT = (stage == 3-1)
		if isTT:
			tf = high_precision_time_format
			race_time = 60*60
			ws = wb.add_worksheet('Stage {}-ITT'.format(stage+1))
		else:
			tf = time_format
			race_time = 4*60*60
			ws = wb.add_worksheet('Stage {}-RR'.format(stage+1))
		fit_sheet = FitSheetWrapperXLSX( ws )
		
		fields = ['bib', 'time', 'place', 'penalty', 'bonus', 'kom 1 1C', 'kom 2 HC', 'sprint 1', 'stage sprint']
		if isTT:
			fields = fields[:5]
		
		row = 0
		for c, field in enumerate(fields):
			fit_sheet.write( row, c, Utils.fieldToHeader(field), bold_format )
		
		bibAB = []
		for i, (bib, t) in enumerate(sorted( ((bib, random.normalvariate(race_time-bib/4.0, 5*60)) for bib in bibs), key=operator.itemgetter(1) )):
			row += 1
			fit_sheet.write( row, 0, bib )
			fit_sheet.write( row, 1, t/(24.0*60.0*60.0), tf )
			if stage in (4-1, 5-1) and i == len(bibs)-1:
				bibAB.append( bib )
				fit_sheet.write( row, 2, 'AB' )
	
		for b in bibAB:
			bibs.remove( b )
			
		if not isTT:
			for c in range(5,9):
				positions = [x for x in range(len(bibs))]
				random.shuffle( positions )
				if fields[c] == 'stage sprint':
					points = stage_points[stage%len(stage_points)]
					positions.sort()
				elif fields[c] == 'sprint 1':
					points = [6,4,2]
				elif fields[c] == 'kom 2 HC':
					points = kom_by_category[0]
				elif fields[c] == 'kom 1 1C':
					points = kom_by_category[1]
				for point, pos in zip(points, positions):
					fit_sheet.write( pos+1, c, point )
	
	wb.close()
	
	return fname_excel
	
if __name__ == '__main__':
	print( MakeExampleExcel() )
