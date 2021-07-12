import  wx
from  ExportGrid import ExportGrid

#----------------------------------------------------------------------

class SprintMgrPrintout(wx.Printout):
	def __init__(self, title, grid):
		self.title = title
		self.grid = grid
		super().__init__()

	def HasPage(self, page):
		return page == 1

	def GetPageInfo(self):
		return (1,1,1,1)

	def OnPrintPage(self, page):
		exportGrid = ExportGrid( self.title, self.grid )
		dc = self.GetDC()
		exportGrid.drawToFitDC( dc )
		return True


class GraphDrawPrintout(wx.Printout):
	def __init__(self, title, graph = None):
		self.title = title
		self.graph = graph
		super().__init__()

	def HasPage(self, page):
		return page == 1

	def GetPageInfo(self):
		return (1,1,1,1)

	def OnPrintPage(self, page):
		dc = self.GetDC()
		self.graph.graph.Print( dc )
		wx.CallAfter( self.graph.Refresh )
		return True
