import  wx
from  ExportGrid import ExportGrid
import  Model

#----------------------------------------------------------------------

def getRaceCategories():
	# Get all the categories available to print.
	with Model.LockRace() as race:
		if race is None:
			return []
		categories = [ (c.fullname, c) for c in race.getCategories() if race.hasCategory(c) ]
	categories.append( ('All', None) )
	return categories

class CrossMgrPrintout(wx.Printout):
    def __init__(self, printSelection = False):
		wx.Printout.__init__(self)
		self.category = None
		if Model.race and printSelection:
			iSelection = getattr( Model.race, 'modelCategory', 0 )
			if iSelection != 0:
				try:
					self.category = race.getCategories()[iSelection-1]
				except:
					self.category = None

    def OnBeginDocument(self, start, end):
        return super(CrossMgrPrintout, self).OnBeginDocument(start, end)

    def OnEndDocument(self):
        super(CrossMgrPrintout, self).OnEndDocument()

    def OnBeginPrinting(self):
        super(CrossMgrPrintout, self).OnBeginPrinting()

    def OnEndPrinting(self):
        super(CrossMgrPrintout, self).OnEndPrinting()

    def OnPreparePrinting(self):
        super(CrossMgrPrintout, self).OnPreparePrinting()

    def HasPage(self, page):
		if self.category:
			return page == 1
		numCategories = len(getRaceCategories()) - 1	# Ignore the 'All' category.
		if page - 1 < numCategories:
			return True
		return False

    def GetPageInfo(self):
		if self.category:
			return (1,1,1,1)
		numCategories = len(getRaceCategories())
		if numCategories == 0:
			return (1,1,1,1)
		return (1, numCategories, 1, numCategories)

    def OnPrintPage(self, page):
		if self.category:
			category = self.category
		else:
			iCat = page - 1
			categories = getRaceCategories()
			if iCat >= len(categories):
				return False
			category = categories[iCat][1]
		
		exportGrid = ExportGrid()
		exportGrid.setResultsOneList( category, True )

		dc = self.GetDC()
		
		exportGrid.drawToFitDC( dc )
		return True
