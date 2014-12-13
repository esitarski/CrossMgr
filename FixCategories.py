import wx
import Model

def FixCategories( choice, iSelection = None ):
	choice.InvalidateBestSize() 
	choice.SetSize(choice.GetBestSize()) 

	race = Model.race
	if race and getattr(race, 'syncCategories', True):
		iSelection = getattr( race, 'modelCategory', 0 )
	
	items = choice.GetItems()
	
	if iSelection is not None and iSelection < len(items):
		choice.SetSelection( iSelection )

	nameCat = [(_('All'), None)]
	if race:
		nameCat.extend( [((u'    ' if c.catType == Model.Category.CatComponent else u'') + c.fullname, c) for c in race.getCategories(False)] )
	
	newItems = [ fullname for fullname, cat in nameCat ]
	if items == newItems:
		return nameCat[choice.GetSelection()][1]
	
	catCur = None
	cItems = choice.GetItems()
	if cItems:
		iCur = choice.GetSelection()
		catCur = choice.GetString( iCur ).strip()
	
	choice.Clear()
	choice.AppendItems( newItems )
	
	iNew = 0
	if catCur is not None:
		for i, (fullname, cat) in enumerate(nameCat):
			if catCur == fullname:
				iNew = i
				break
		
	choice.SetSelection( iNew )
	return nameCat[choice.GetSelection()][1]
	
def SetCategory( choice, cat ):
	if FixCategories(choice) != cat:
		if cat is None:
			choice.SetSelection( 0 )
		else:
			for i, item in enumerate(choice.GetItems()):
				if item.strip() == cat.fullname:
					choice.SetSelection( i )
					break
	
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	choice = wx.Choice(mainWin)
	FixCategories( choice )
	mainWin.Show()
	app.MainLoop()
