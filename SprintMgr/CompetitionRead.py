
import yaml
from Model import Competition, System, Event

def competition_read( fname ):
	with open(fname, encoding='utf-8') as f:
		y = yaml.safe_load( f )
	
	systems = []
	for s in y['systems']:
		heatsMax = s.get('best_of', 1)
		assert heatsMax in {1,3}, "'best_of' value must be 1 or 3"
		events = []
		for e in s['events']:
			e = e.strip()
			if not e:
				continue
			assert '#' not in e, 'Rules cannot contain '#'"
			rule = e.strip()
			rule = rule.replace('=', '->')
			assert rule.count('->') == 1, "Rule must contain one '->'"
			events.append( Event(rule, heatsMax) )
		systems.append( System(s['system'], events) )
		
	return Competition( y['competition'], systems, y.get('consider_rounds',False), y.get('duplicate_ranking',False)  )
	
if __name__ == '__main__':
	c = competition_read( 'TestComp.smc' )
	print( c )

	c = competition_read( 'TestComp2.smc' )
	print( c )

	c = competition_read( 'TestComp3.smc' )
	print( c )
