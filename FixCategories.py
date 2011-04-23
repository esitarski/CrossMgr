import wx
import Model

def FixCategories( choice, iSelection = None ):
	choice.InvalidateBestSize() 
	choice.SetSize(choice.GetBestSize()) 

	items = choice.GetItems()
	
	if iSelection is not None and iSelection < len(items):
		choice.SetSelection( iSelection )

	race = Model.getRace()
	newItems = ['All']
	newItems.extend( c.name for c in race.getCategories() )
	
	if items == newItems:
		return choice.GetStringSelection()
	
	catCur = None
	cItems = choice.GetItems()
	if cItems:
		iCur = choice.GetSelection()
		catCur = choice.GetString( iCur )
	
	choice.Clear()
	choice.AppendItems( newItems )
	
	iNew = 0
	if catCur is not None:
		i = choice.FindString(catCur)
		if i != wx.NOT_FOUND:
			iNew = i
		
	choice.SetSelection( iNew )
	return choice.GetStringSelection()
	
def SetCategory( choice, catName ):
	if FixCategories(choice) != catName:
		for i, item in enumerate(choice.GetItems()):
			if item == catName:
				choice.SetSelection( i )
				break
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	choice = wx.Choice(mainWin)
	FixCategories( choice )
	mainWin.Show()
	app.MainLoop()
