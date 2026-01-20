
import yaml
from Model import Competition, System, Event

def competition_read( fname ):
	with open(fname, encoding='utf-8') as f:
		y = yaml.safe_load( f )
	
	extra = set(y.keys()) - {'competition', 'elimination_ranking_policy', 'draw_lots', 'systems'}
	assert not extra, f'Unrecognized competition attribute(s): {extra}'
	
	assert 'competition' in y, "Missing 'competition:' name"
	competitonName = y['competition']
	assert isinstance(competitonName, str), 'competition: name must be a string'
	
	assert 'systems' in y, "Missing 'systems:' in competition"
	
	eliminationRankingPolicy = y.get('elimination_ranking_policy', 'QualifyingTime')
	assert isinstance(eliminationRankingPolicy, str), 'elimination_ranking_policy must be a string'
	eliminationRankingPolicy = eliminationRankingPolicy.strip()

	for i, name in enumerate(Competition.EliminationRankingPolicyNames):
		if name == eliminationRankingPolicy:
			eliminationRankingPolicy = i
			break
	else:
		raise ValueError( f'Unknown elimination_ranking_policy: {eliminationRankingPolicy}' )
	
	drawLots = y.get('draw_lots', True)
	assert isinstance( drawLots, bool ), 'draw_lots must be true or false'

	systems = []
	for s in y['systems']:
		extra = set(s.keys()) - {'system', 'best_of', 'events'}
		assert not extra, f'Unrecognized system attribute(s): {extra}'
		assert 'system' in s, "missing 'system:' in system"
		assert 'events' in s, "missing 'events:' in system"
		assert isinstance(s['events'], list), "'events:' must be a list"

		heatsMax = s.get('best_of', 1)
		assert heatsMax in {1,3}, "'best_of:' must be 1 or 3"
		events = []
		for e in s['events']:
			assert isinstance(e, str), f"event rule must be a string: {e}"
			e = e.strip()
			assert e, "event rule cannot be blank"
			assert '#' not in e, f"event rule must not contain '#': {e}"
			rule = e.replace('=', '->')
			assert rule.count('->') == 1, f"Rule must contain one '->': {e}"
			events.append( Event(rule, heatsMax) )
		systems.append( System(s['system'], events) )
		
	return Competition( competitonName, eliminationRankingPolicy, drawLots, systems )
	
if __name__ == '__main__':
	c = competition_read( 'TestComp.smc' )
	print( c )

	c = competition_read( 'TestComp2.smc' )
	print( c )

	c = competition_read( 'TestComp3.smc' )
	print( c )

	c = competition_read( 'SprintChallenge.smc' )
	print( c )
