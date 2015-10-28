import Utils
import ReadSignOnSheet
import Model

def PrologMatchingCategory():
	race = Model.race
	if not race:
		return None
	for c in race.getCategories(startWaveOnly=False):
		c.resetNums()
	race.resetAllCaches()
	race.setChanged()

def AddToMatchingCategory( bib, fields ):
	race = Model.race
	if not race:
		return None
	categoryName, gender = fields.get('EventCategory',None), fields.get('Gender',None)
	if not categoryName:
		return None
	
	categories = race.categories
	getFullName = Model.Category.getFullName
	
	found = None
	if gender:
		found = categories.get(getFullName(categoryName,gender), None)
	
	if found is None:
		found = categories.get(getFullName(categoryName,'Men'), None) or categories.get(getFullName(categoryName,'Women'), None) or categories.get(getFullName(categoryName,'Open'), None)
	
	if found is None:
		found = Model.Category( name=categoryName, catStr=unicode(bib), sequence=len(categories), gender=gender )
		categories[found.fullname] = found
	else:
		found.intervals.append( (bib, bib) )

def EpilogMatchingCategory():
	race = Model.race
	if not race:
		return None
		
	EmptyInterval = (Model.Category.MaxBib, Model.Category.MaxBib)
	
	for key, c in race.categories.iteritems():
		c.intervals.sort()
		c.normalize()
	
	race.adjustAllCategoryWaveNumbers()
	
	empty_categories = set()
	for key, c in race.categories.iteritems():
		if c.intervals[-1] == EmptyInterval:
			c.intervals.pop()
		if not c.intervals:
			empty_categories.add( key )
			
	for key in empty_categories:
		del race.categories[key]
	
	for sequence, c in enumerate(sorted(race.categories.itervalues())):
		c.sequence = sequence
	
	race.resetAllCaches()
	race.setChanged()
