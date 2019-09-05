import operator
from collections import defaultdict

import Model
import Utils
from GetResults import GetResults

class TeamResult:
	def __init__( self, team, t=None, points=None, bestPos=0, note=u'' ):
		self.team = team
		self.t = t
		self.points = points
		self.bestPos = bestPos
		self.note = note
		self.criteria = ''
		self.gap = ''
		
	def __repr__( self ):
		values = [u'{}={}'.format(a, getattr(self, a)) for a in ('team', 't', 'points', 'bestPos', 'note', 'criteria')]
		return ', '.join( values )

@Model.memoize
def GetTeamResults( category ):
	results = GetResults( category )
	if not results:
		return tuple()
		
	race = Model.race
	Finisher = Model.Rider.Finisher
	
	formatTime = lambda t: Utils.formatTime( t, highPrecision=race.highPrecisionTimes )
	formatTimeGap = lambda t: Utils.formatTimeGap( t, highPrecision=race.highPrecisionTimes )
	
	# Group the results by teams.
	teamInfo = defaultdict( list )
	independent = _('Independent').lower()
	fastestTime = None
	
	def getPercentTime( rr ):
		return 100.0 * ((rr.lastTime - race.getStartOffset(rr.num)) / fastestTime)
	
	for pos, rr in enumerate(results, 1):
		if rr.status != Finisher:
			continue
		if fastestTime is None:
			fastestTime = rr.lastTime - race.getStartOffset(rr.num) if rr.lastTime else None
		team = getattr( rr, 'Team', u'' )
		if team and not (team.lower().startswith(independent) or team.lower().startswith('independent')):
			rr.pos = pos
			teamInfo[team].append( rr )

	# Create the team rank criteria based on the individual results.
	teamResults = []
	if race.teamRankOption == race.teamRankByRiderTime:		# by nth rider (team time trial)
		for team, rrs in teamInfo.items():
			try:
				rr = rrs[race.nthTeamRider-1]
			except IndexError:
				continue
			teamResults.append( TeamResult(team, t=rr.lastTime - race.getStartOffset(rr.num),  note=u'{}'.format(rr.num)) )
			
		if teamResults:
			teamResults.sort( key=operator.attrgetter('t') )
			top = teamResults[0]
			for tr in teamResults:
				tr.criteria = formatTime( tr.t )
				tr.gap = formatTimeGap( tr.t - top.t ) if tr != top else ''
	
	elif race.teamRankOption == race.teamRankBySumPoints:		# sum of individual points
		pointsForPos = {pos:points for pos, points in enumerate( (int(v.strip()) for v in race.finishPointsStructure.split(',')), 1) }
		for team, rrs in teamInfo.items():
			if len(rrs) < race.topTeamResults:
				continue
			rrs = rrs[:race.topTeamResults]
			teamResults.append(
				TeamResult(
					team,
					points=sum(pointsForPos.get(rr.pos, 0) for rr in rrs),
					bestPos=rrs[0].pos,
					note=u', '.join(u'{}:{} ({})'.format(pointsForPos.get(rr.pos, 0), rr.pos, rr.num))
				)
			)
		if teamResults:
			teamResults.sort( key=lambda x:(-x.points, x.bestPos) )
			top = teamResults[0]
			for tr in teamResults:
				tr.criteria = u'{}'.format( tr.points )
				tr.gap = u'{}'.format( tr.points - top.points ) if tr != top else ''
	
	elif race.teamRankOption == race.teamRankBySumTime:		# sum of individual times
		for team, rrs in teamInfo.items():
			if len(rrs) < race.topTeamResults:
				continue
			rrs = rrs[:race.topTeamResults]
			teamResults.append(
				TeamResult(
					team,
					t=sum(rr.lastTime - race.getStartOffset(rr.num) for rr in rrs),
					bestPos=rrs[0].pos,
					note=u', '.join(u'{}:{} ({})'.format(formatTime(rr.lastTime - race.getStartOffset(rr.num)), rr.pos, rr.num))
				)
			)
		if teamResults:
			teamResults.sort( key=lambda x:(x.t, x.bestPos) )
			top = teamResults[0]
			for tr in teamResults:
				tr.criteria = formatTime( tr.t )
				tr.gap = formatTimeGap( tr.t - top.t ) if tr != top else ''

	elif race.teamRankOption == race.teamRankBySumPercentTime and fastestTime:	# sum of percent times of winner.  Must be the last in the if-else.
		for team, rrs in teamInfo.items():
			if len(rrs) < race.topTeamResults:
				continue
			rrs = rrs[:race.topTeamResults]
			teamResults.append(
				TeamResult(
					team,
					points=sum(getPercentTime(rr) for rr in rrs),
					bestPos=rrs[0].pos,
					note=u', '.join(u'{:.2f}:{} ({})'.format(getPercentTime(rr), rr.pos, rr.num))
				)
			)
		if teamResults:
			teamResults.sort( key=lambda x:(-x.points, x.bestPos) )
			top = teamResults[0]
			for tr in teamResults:
				tr.criteria = u'{:.2f}'.format( tr.points )
				tr.gap = u'{:.2f}'.format( tr.points - top.points ) if tr != top else ''
	
	return tuple( teamResults )
