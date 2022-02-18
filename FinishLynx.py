import os
import csv
import operator
from collections import defaultdict

import Model

def strToSeconds( s = '' ):
	secs = 0.0
	for f in s.split(':'):
		try:
			n = float(f)
		except ValueError:
			n = 0.0
		secs = secs * 60.0 + n
	return secs

def strToInt( s ):
	try:
		return int(s.strip())
	except ValueError:
		return s
		
def getStatus( p ):
	p = p.upper().strip()
	if p.isdigit():
		return Model.Rider.Finisher
	if p == 'DNS':
		return Model.Rider.DNS
	if 'Q' in p:
		return Model.Rider.DQ
	return Model.Rider.DNF			# default DNF

def ReadLIF( crossMgrStart, fname ):
	reader = csv.reader( fname )
	# Place, ID, lane, last name, first name, affiliation, <time>, license, <delta time>, <ReacTime>, <splits>, time trial start time, user 1, user 2, user 3
	
	fields = ('place', 'id', 'lane', 'last_name', 'first_name', 'affiliation', 'time', 'delta_time', 'react_time', 'splits', 'tt_start_time')
	int_fields = {'id', 'lane'}
	time_fields = {'time', 'react_time', 'tt_start_time','delta_time'}
	
	def getFields( raceStart, row ):
		record = {f:None for f in fields}
		del record['splits']
		record['race_times'] = []
		record['lap_times'] = []
		record['status'] = Model.Rider.Finisher
		for i, f in enumerate(fields):
			try:
				v = row[i]
			except IndexError:
				break
				
			if f == 'splits':
				# "splits" is a comma separated field of "race_time (lap_time)" pairs.
				race_times = []
				lap_times = []
				for split in v.split(','):
					sv = split.split(' ')
					try:
						race_times.append( strToSeconds(sv[0]) )
						lap_times.append( strToSeconds(sv[1:-1]) )	# Remove brackets.
					except IndexError:
						break
				record['race_times'] = race_times
				record['lap_times'] = lap_times
				continue

			if f == 'place':
				record['status'] = getStatus( v )
			
			if f in time_fields:
				v = strToSeconds( v )
			elif f in int_fields:
				v = strToInt( v )
				
			record[f] = v
			
		return record

	with open( fname, newline='' ) as f:
		raceStart = None
		reader = csv.reader( f )
		for i, row in enumerate(reader):
			if i == 0:
				# Get the time of day start from the header.
				raceStart = strToSeconds( row[-1] )
			
			try:
				yield getFields(raceStart, row)
			except Exception as e:
				pass
	
def ImportLIF( fname ):
	race = Model.race
	if not race:
		return
	
	if race.startTime:
		crossMgrStartTime = strToSeconds( race.startTime.strftime('%H:%M:%S.f') )
	else:
		crossMgrStartTime = strToSeconds( race.self.scheduledStart )
	
	for r in ReadLIF(crossMgrStart, fname):
		rider = race.getRider( r['id'] )
		category = race.getCategory( rider.num )
		startOffset = self.categoryStartOffset(category)
		rider.times = [t + startOffset for t in record['race_times']]
		rider.status = record['status']
		
	race.setChanged()

#-----------------------------------------------------------------------

def Export( folder ):
	''' Export the race in FinishLynx file format (lynx.ppl, lynx.evt, lynx.sch). '''

	race = Model.race
	if not race:
		return
		
	try:
		externalInfo = race.excelLink.read()
	except Exception:
		externalInfo = {}
	
	# Create the people reference file.
	fname = os.path.join( folder, 'lynx.ppl' )
	# ID number, last name, first name, affiliation
	fields = ('LastName', 'FirstName', 'Team')
	with open(fname, 'w', newline='') as f:
		writer = csv.writer( f );
		for id, info in sorted( externalInfo.items(), key=operator.itemgetter(0) ):
			writer.writerow( [id] + [externalInfo.get(field,'') for field in fields] )

	# Partition riders by category.
	categoryRiders = defaultdict( list )
	for id in externalInfo.keys():
		categoryRiders[race.getCategory(id)].append( id )
			
	fname = os.path.join( folder, 'lynx.evt' )
	# Event number, round number, heat number, event name
	# <tab, space or comma>ID, lane
	categories = sorted(race.getCategories(), key=operator.methodcaller('getStartOffsetSecs'))
	with open(fname, 'w') as f:
		for event, category in enumerate(categories, 1):
			f.write( '{},1,1,{}\n'.format(event, category.fullname.replace(',', r'\,')) )
			for id in sorted(categoryRiders[category]):
				f.write( ',{}'.format(id) )
	
	fname = os.path.join( folder, 'lynx.sch' )
	# event number, round number, heat number
	with open(fname, 'w') as f:
		for event, category in enumerate(categories, 1):
			f.write( '{},1,1\n'.format(event) )

if __name__ == "__main__":
	Model.race = Model.Race()
	Model.race._populate()
	Export( 'finishlynx' )
