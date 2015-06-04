import Utils
import Model
from JChipSetup import GetTagNums

def UnmatchedTagsUpdate():
	race = Model.race
	if not race or not race.unmatchedTags:
		return
	
	tagNums = GetTagNums( forceUpdate=True )
	tagsFound = False
	for tag, times in race.unmatchedTags.iteritems():
		try:
			num = tagNums[tag]
		except KeyError:
			continue
		
		for t in times:
			race.addTime( num, t )
		tagsFound = True
	
	if tagsFound:
		race.unmatchedTags = { tag: times for tag, times in race.unmatchedTags.iteritems() if tag not in tagNums }
	
