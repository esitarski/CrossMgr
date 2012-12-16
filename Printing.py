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
    def __init__(self):
        wx.Printout.__init__(self)

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
		numCategories = len(getRaceCategories()) - 1	# Ignore the 'All' category.
		if page - 1 < numCategories:
			return True
		return False

    def GetPageInfo(self):
		numCategories = len(getRaceCategories())
		if numCategories == 0:
			return (1,1,1,1)
		return (1, numCategories, 1, numCategories)

    def OnPrintPage(self, page):
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
