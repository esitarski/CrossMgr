import os
import datetime
import random
import xlsxwriter
import Utils
from Excel import GetExcelReader
from FitSheetWrapper import FitSheetWrapper
from Model import Source, Result
from GetCallups import make_title

def random_license():
	return ''.join( 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[random.randint(0,25)] for i in range(6) )

def random_uci_id():
	id = '9{}'.format(''.join( random.choice('0123456789') for i in range(8)) )
	id += '{:02d}'.format( int(id) % 97 )
	return id

def MakeExampleExcel(
		include_national_champion=True,
		include_regional_champion=True,
		include_uci_points=True,
		include_eastern_series=True,
		include_western_series=True
	):
	Year = datetime.date.today().year
	YearAdjust = Year - 2017
	
	fname = os.path.join(Utils.getImageFolder(), 'UCIPoints.xlsx')
	reader = GetExcelReader( fname )
	uci_points = Source( fname, 'Individual' )
	uci_points.read( reader )
	for r in uci_points.results:
		r.age += YearAdjust
		r.license = random_license()

	uci_sample = random.sample( uci_points.results, 20 )
	
	common_first_names = 'Léopold Grégoire Aurélien Rémi Léandre Thibault Kylian Nathan Lucas Enzo Léo Louis Hugo Gabriel Ethan Mathis Jules Raphaël Arthur Théo Noah Timeo Matheo Clément Maxime Yanis Maël'.split()
	common_last_names = 'Tisserand Lavergne Guignard Parmentier Evrard Leclerc Martin Bernard Dubois Petit Durand Leroy Moreau Simon Laurent Lefevre Roux Fournier Dupont'.split()
	
	other_sample = []
	for i in range(20):
		other_sample.append( Result(
				first_name=common_first_names[i%len(common_first_names)],
				last_name=common_last_names[i%len(common_last_names)],
				uci_id=random_uci_id(),
				license=random_license(),
			)
		)
		
	registration = list(uci_sample) + other_sample
	
	bibs = list(range(100,200))
	random.shuffle( bibs )
	
	for i, r in enumerate(registration):
		r.bib = bibs[i]
	
	fname_excel = os.path.join( Utils.getHomeDir(), 'CS_Test_Input.xlsx' )
	
	wb = xlsxwriter.Workbook( fname_excel )
	ws = wb.add_worksheet('Registration')
	fit_sheet = FitSheetWrapper( ws )
	
	fields = ['bib', 'first_name', 'last_name', 'uci_id', 'license']
	for c, field in enumerate(fields):
		fit_sheet.write( 0, c, make_title(field) )
	for r, result in enumerate(registration):
		for c, field in enumerate(fields):
			fit_sheet.write( r+1, c, getattr(result, field) )
	
	if include_national_champion:
		ws = wb.add_worksheet('National Champ')
		fit_sheet = FitSheetWrapper( ws )
		for c, header in enumerate(['UCI ID', 'Name']):
			fit_sheet.write( 0, c, header )
		row = 1
		result = registration[4]
		fit_sheet.write( row, 0, result.uci_id if result.uci_id else '' )
		fit_sheet.write( row, 1, '{} {}'.format(result.last_name.upper(), result.first_name) )
	
	if include_regional_champion:
		ws = wb.add_worksheet('Regional Champ')
		fit_sheet = FitSheetWrapper( ws )
		for c, header in enumerate(['UCI ID', 'Name']):
			fit_sheet.write( 0, c, header )
		row = 1
		result = registration[8]
		fit_sheet.write( row, 0, result.uci_id if result.uci_id else '' )
		fit_sheet.write( row, 1, '{} {}'.format(result.last_name.upper(), result.first_name) )
	
	if include_uci_points:
		ws = wb.add_worksheet('UCIPoints')
		fit_sheet = FitSheetWrapper( ws )
		for c, header in enumerate(['Rank', 'UCI ID', 'Name', 'Team Code', 'Age', 'Points']):
			fit_sheet.write( 0, c, header )
		for r, result in enumerate(uci_points.results):
			row = r + 1
			fit_sheet.write( row, 0, '{}'.format(row) )
			fit_sheet.write( row, 1, result.uci_id if result.uci_id else '' )
			fit_sheet.write( row, 2, '{} {}'.format(result.last_name.upper(), result.first_name) )
			fit_sheet.write( row, 3, result.team_code if result.team_code else '' )
			fit_sheet.write( row, 4, result.age )
			fit_sheet.write( row, 5, result.points )

	eligible_for_points = other_sample + [rr for rr in uci_points.results if rr.nation_code == 'FRA']

	if include_eastern_series:
		ws = wb.add_worksheet('Eastern Series')
		fit_sheet = FitSheetWrapper( ws )
		for c, header in enumerate(['First Name', 'Last Name', 'License', 'Ability', 'Points']):
			fit_sheet.write( 0, c, header )
		
		for r, result in enumerate(random.sample(eligible_for_points, min(len(eligible_for_points),35))):
			row = r + 1
			fit_sheet.write( row, 0, result.first_name )
			fit_sheet.write( row, 1, result.last_name )
			fit_sheet.write( row, 2, result.license )
			fit_sheet.write( row, 3, 'Cat{}'.format(r%4+1) )
			fit_sheet.write( row, 4, random.randint(1, 200) )
	
	if include_western_series:
		ws = wb.add_worksheet( 'Western Series' )
		fit_sheet = FitSheetWrapper( ws )
		for c, header in enumerate(['Pos', 'First Name', 'Last Name', 'UCI ID', 'License']):
			fit_sheet.write( 0, c, header )
		for r, result in enumerate(random.sample(eligible_for_points, min(len(eligible_for_points),35))):
			row = r + 1
			fit_sheet.write( row, 0, row )
			fit_sheet.write( row, 1, result.first_name )
			fit_sheet.write( row, 2, result.last_name )
			fit_sheet.write( row, 3, result.uci_id )
			fit_sheet.write( row, 4, result.license )

	wb.close()
	
	return fname_excel
	
if __name__ == '__main__':
	MakeExampleExcel()
	
	
