import wx
import Model

def FixCategories( choice, iSelection = None, doSyncCategories = True ):
	choice.InvalidateBestSize() 
	choice.SetSize(choice.GetBestSize()) 

	race = Model.race
	if race and doSyncCategories and getattr(race, 'syncCategories', True):
		iSelection = getattr( race, 'modelCategory', 0 )
	
	items = choice.GetItems()
	
	if iSelection is not None and iSelection < len(items):
		choice.SetSelection( iSelection or 0 )

	categories = race.getCategories( startWaveOnly=False ) if race else []
	newItems = [(u'    ' if c.catType == Model.Category.CatComponent else u'') + c.fullname for c in categories]
	newItems.insert( 0, _('All') )
	categories.insert( 0, None )
	if items == newItems:
		return categories[choice.GetSelection()]
	
	catNameCur = None
	if items:
		catNameCur = items[choice.GetSelection()]
	
	choice.Clear()
	choice.AppendItems( newItems )
	
	iNew = 0
	if catNameCur is not None:
		for i, fullname in enumerate(newItems):
			if catNameCur == fullname:
				iNew = i
				break
		
	choice.SetSelection( iNew )
	return categories[choice.GetSelection()]
	
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
