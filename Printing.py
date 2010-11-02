import  wx
from  ExportGrid import ExportGrid
import  Model

#----------------------------------------------------------------------

def getRaceCategories():
	# Get all the categories available to print.
	race = Model.getRace()
	if race is None:
		return []
	categories = [ c.name for c in race.getCategories() if race.hasCategory(c.name) ]
	categories.append( 'All' )
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
		numCategories = len(getRaceCategories())
		if page - 1 < numCategories:
			return True
		return False

    def GetPageInfo(self):
		numCategories = len(getRaceCategories())
		if numCategories == 0:
			return (1,1,1,1)
		return (1, numCategories, 1, numCategories)

    def OnPrintPage(self, page):
		race = Model.getRace()
		if race is None:
			return

		iCat = page - 1
			
		categories = getRaceCategories()		
		if iCat >= len(categories):
			return

		dc = self.GetDC()
		export = ExportGrid()

		catName = categories[iCat]
		#export.setResults( catName )
		export.setResultsOneList( catName )

		export.drawToFitDC( dc )

		return True
