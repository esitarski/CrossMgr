import os
import sys
import datetime
import Utils
import random
from Model import Source
from Excel import GetExcelReader

RegistrationSheet = 'Registration'

def GetCallups( fname, soundalike=True, useUciId=True, useLicense=True, callbackfunc=None, callbackupdate=None, cycleLast=None ):

	if callbackupdate: callbackupdate( _('Reading spreadsheet...') )
	reader = GetExcelReader( fname )
	
	sheet_names = [name for name in reader.sheet_names()]
	
	registration_sheet_count = sum( 1 for sheet in sheet_names if sheet == RegistrationSheet )
	if registration_sheet_count == 0:
		raise ValueError( '{}: "{}"'.format('Spreadsheet is missing sheet', RegistrationSheet ) )
	if registration_sheet_count > 1:
		raise ValueError( '{}: "{}"'.format('Spreadsheet must have exactly one sheet named', RegistrationSheet ) )
	
	if callbackupdate: callbackupdate( '{}: {}'.format(_('Reading'), RegistrationSheet) )
	
	reader = GetExcelReader( fname )
	
	registration = Source( fname, RegistrationSheet, False )
	registrationErrors = registration.read( reader )
	
	if callbackfunc: callbackfunc( [registration], [registrationErrors] )
		
	sources = []
	errors = []
	for sheet in sheet_names:
		if sheet == RegistrationSheet:
			continue
		if callbackfunc: callbackfunc( sources + [registration], errors + [registrationErrors] )
		if callbackupdate: callbackupdate( '{}: {}'.format(_('Reading'), sheet) )
		source = Source( fname, sheet, soundalike=soundalike, useUciId=useUciId, useLicense=useLicense )
		errs = source.read( reader )
		sources.append( source )
		errors.append( errs )
		
	# Add a random sequence as a final sort order.
	registration.randomize_positions()
	
	sources.append( registration )
	errors.append( registrationErrors )
	
	if callbackfunc: callbackfunc( sources, errors )
	
	for reg in registration.results:
		reg.result_vector = [source.find(reg) for source in sources]
	
	callup_order = sorted(
		registration.results,
		key = lambda reg: tuple(r.get_sort_key() for r in reg.result_vector)
	)

	# Apply criteria cycling options.
	if cycleLast is not None and callup_order:
		callup_order_cycle = []
		cycleGroups = [[] for i in range(cycleLast)]
		noCriteria = []
		# Separate the cycling criteria into groups.
		for row, reg in enumerate(callup_order):
			
			# Nothing matches anything - add to no criteria so we can insert at the end.
			if all( r.get_status() == r.NoMatch for r in reg.result_vector[:-1] ):
				noCriteria.append( reg )
				continue
			
			iCycleLastEnd = len(reg.result_vector) - 1
			iCycleLastBegin = max(0, iCycleLastEnd - cycleLast)
			iCycleMax = iCycleLastEnd - iCycleLastBegin
			
			# If any criteria matches before cycleLast, this isn't in a cycle group.  Add it and ignore.
			if any( r.is_matched() for r in reg.result_vector[:iCycleLastBegin] ):
				callup_order_cycle.append( reg )
				continue
			
			# Find the cycle group for this result.
			for iLast in range(iCycleMax):
				if reg.result_vector[iCycleLastBegin+iLast].is_matched():
					cycleGroups[iLast].append( reg )
					break
			else:
				callup_order_cycle.append( reg )
			
		# Remove empty cycle groups.
		cycleGroups = [cg for cg in cycleGroups if cg]

		# Cycle through the groups until everyone has been inserted.
		# Reverse the groups so we can process them efficiently with pop().
		for cg in cycleGroups:
			cg.reverse()
		
		iCycleCur = 0
		while cycleGroups:
			callup_order_cycle.append( cycleGroups[iCycleCur].pop() )
			if not cycleGroups[iCycleCur]:
				cycleGroups.pop( iCycleCur )
			iCycleCur += 1
			if iCycleCur >= len(cycleGroups):
				iCycleCur = 0
			
		callup_order_cycle.extend( noCriteria )
		callup_order = callup_order_cycle

	# Randomize riders with no criteria.
	for i_random, reg in enumerate(callup_order):
		if all( r.get_status() == r.NoMatch for r in reg.result_vector[:-1] ):
			cu2 = callup_order[i_random:]
			random.seed()
			random.shuffle(cu2)
			callup_order = callup_order[:i_random] + cu2
			break
		
	callup_results = []
	registration_headers = registration.get_ordered_fields()
	
	# Also add the team code if there is one.
	if not 'team_code' in registration_headers:
		for iSource, source in enumerate(sources):
			if 'team_code' in source.get_ordered_fields():
				try:
					i_team = registration_headers.index('team')
					registration_headers = tuple(
						list(registration_headers[:i_team+1]) +
						['team_code'] +
						list(registration_headers[i_team+1:])
					)
				except ValueError:
					registration_headers = tuple( list(registration_headers) + ['team_code'] )
					
				for reg in callup_order:
					try:
						reg.team_code = reg.result_vector[iSource].matches[0].team_code
					except:
						pass
				break
	
	callup_headers = list(registration_headers) + [source.sheet_name for source in sources[:-1]]
	
	for reg in callup_order:
		row = [getattr(reg, f, '') for f in registration_headers]
		row.extend( reg.result_vector[:-1] )
		callup_results.append( row )
	
	return registration_headers, callup_headers, callup_results, sources, errors

def make_title( title ):
	t = ' '.join( (w[:1].upper() + w[1:]).replace('Uci','UCI').replace('Id','ID').replace('Of','of') for w in title.split('_') )
	return t.replace('Tagnum', 'TagNum').replace('Bibnum', 'BibNum')

if __name__ == '__main__':
	def callbackupdate( msg ):
		sys.stderr.write( msg + '\n' )
	
	fname = 'Men_Elite_XCO_CallupData.xlsx'
	registration_headers, callup_headers, callup_results, sources, errors = GetCallups( fname, callbackupdate=callbackupdate )
	#for row in callup_results:
	#	print [Utils.removeDiacritic('{}'.format(v)) for v in row]
	#CallupResultsToExcel( 'test_output.xlsx', registration_headers, callup_headers, callup_results )
