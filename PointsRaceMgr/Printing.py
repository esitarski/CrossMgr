import wx
import Model
import Utils

class PointsMgrPrintout( wx.Printout ):
	def HasPage(self, page):
		return page in (1, 2)

	def GetPageInfo(self):
		if Model.race.riderInfo:
			return (1,2,1,2)
		else:
			return (1,1,1,1)

	def OnPrintPage(self, page):
		dc = self.GetDC()
		if page == 1 and Model.race.riderInfo:
			Utils.getMainWin().GetParent().GetParent().resultsList.toPrintout( dc )
		return True

