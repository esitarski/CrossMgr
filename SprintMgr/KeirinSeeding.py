import operator
from collections import defaultdict
from itertools import pairwise

def KeirinSeeding( advanceCount:int, heatSize:int, heatCount: int, rank : dict[int,int|float], team : dict[int,str] | None = None) -> list[list[int]]:
	heats = [[] for h in range(heatCount)]

	# "Plow the field" to get the original allocation.
	iHeat = 0
	forward = True
	for b, r in sorted( rank.items(), key=operator.itemgetter(1) ):
		heats[iHeat].append( b )
		if forward:
			iHeat += 1
			if iHeat == heatCount:
				iHeat = heatCount - 1
				forward = False
		else:
			iHeat -= 1
			if iHeat < 0:
				iHeat = 0
				forward = True
	
	def maxTeamCount( heat ):
		# Return the maximum number of team members in the heat.
		teamCount = defaultdict( int )
		for b in heat:
			teamCount[team[b]] += 1
		return max( teamCount.values() )
	
	'''
	# Do complete pairwise swaps to reduce the maximum team member count per heat.
	for h0, h1 in pairwise( range(heatCount) ):
		mtcBest = max( maxTeamCount(heats[h0]), maxTeamCount(heats[h1]) )
		for i in range(len(heats[h0])):
			for j in range(len(heats[h1])):
				heats[h0][i], heats[h1][j] = heats[h1][j], heats[h0][i]					
				mtcNew = max( maxTeamCount(heats[h0]), maxTeamCount(heats[h1]) )
				if mtcNew < mtcBest:
					print( mtcBest, mtcNew )
					mtcBest = mtcNew
				else:
					heats[h0][i], heats[h1][j] = heats[h1][j], heats[h0][i]
	'''			
		
	# Do swaps at corresponding levels to reduce the maximum team member count per heat.
	# We do swaps at the same level to preserve the ranking integrity.
	success = True
	while success:
		success = False
		for h0, h1 in pairwise( range(heatCount) ):
			mtcBest = max( maxTeamCount(heats[h0]), maxTeamCount(heats[h1]) )
			for i in range(min(len(heats[h0]), len(heats[h1])) ):
				j = i
				heats[h0][i], heats[h1][j] = heats[h1][j], heats[h0][i]					
				mtcNew = max( maxTeamCount(heats[h0]), maxTeamCount(heats[h1]) )
				if mtcNew < mtcBest:
					print( mtcBest, mtcNew )
					mtcBest = mtcNew
					success = True
				else:
					# Failure.  Restore the previous configuration.
					heats[h0][i], heats[h1][j] = heats[h1][j], heats[h0][i]					
	
	return heats
		
	
if __name__ == '__main__':
	import random
	
	rank = {i:random.randint(1,1000) for i in range(1,29)}
	team = {b:random.choice('abcde') for b in rank.keys()}
	heats = KeirinSeeding( 2, 7, 4, rank, team )
	
	for h in heats:
		print( ''.join( f'{b:2} ({rank[b]:3}, {team[b]}) ' for b in h ) )
	
	
