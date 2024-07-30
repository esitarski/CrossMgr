from Model import *
import random

def Simulate( competition ):
	print( competition.name, 'Simulation' )
	print()

	print( 'Qualifying Times:' )
	for i, (t, rider) in enumerate(competition.state.getQualifyingTimes()):
		if rider != competition.state.OpenRider:
			print('{:2d}: {} {:.3f}'.format(i+1, rider, t) )
	print()
	
	tse = competition.getCanStart()
	while tse:
		#print()
		#print( 'Labels:' )
		#print( '\n'.join( '%s = %s' % (id, r) for id, r in sorted(competition.state.labels.items()) if r != OpenRider ) )
		#print()
		print()
		print( 'Results:' )
		results, dnfs, dqs = competition.getResults()
		for i, r in enumerate(results):
			if r and r != competition.state.OpenRider:
				print( '{:2d}: {}'.format(i+1, r) )
		print( '\n'.join( 'DNF: {}'.format(r) for r in dnfs ) )
		print( '\n'.join( 'DQ: {}'.format(r) for r in dqs ) )
			
		print()
		print( 'Available Events:' )
		print( '\n'.join( e.getRepr() for s, e in competition.getCanStart() ) )
		
		e = tse[0][2]
		
		print()
		print( '******************************************************************************' )
		print( 'Start:' )
		print( e )
		
		start = e.getStart()
		
		for i, p in enumerate(start.startPositions):
			print( 'Start Position {}: {}'.format(i+1, competition.state.labels[p]) )
		raw_input()
		
		if random.randint(1,5) == 1:
			start.restartRequired = True
			print()
			print( 'Restart:' )
			if random.randint(1, 2) == 1:
				id = random.choice(start.getRemainingComposition())
				print( 'With relegation of {}={}'.format(competition.state.labels[id], id) )
				start.addRelegation( id )
		elif random.randint(1,2) == 1:
			while 1:
				r = random.choice(e.composition)
				if competition.state.labels[r] != competition.state.OpenRider:
					# Need to set noncontinue riders in both the start and the competition.
					start.noncontinue[r] = 'DQ'
					print()
					print( 'DQ:', competition.state.labels[r], r )
					break
		else:
			places = [c for c in e.composition if competition.state.inContention(c)]
			random.shuffle( places )
			for i, c in enumerate(places):
				start.places[c] = i + 1
			print()
			print( 'Successful Results:' )
			for i, c in enumerate(places):
				print( 'Finish Position {}:  {}'.format(i+1, competition.state.labels[c]) )
		print()
		
		e.propagate()
		print( e )
		print()
		competition.propagate()
		raw_input()
			
	print()
	print( 'Results:' )
	for i, r in enumerate(competition.getResults()[0]):
		if r and r != competition.state.OpenRider:
			print( '{:2d}: {}'.format(i+1, r) )

if __name__ == '__main__':
	Model.model = SetDefaultData()
	Simulate( Model.model.competition )
