import wx
import wx.grid
from ColGrid import ColGrid

class ColGridHoverRow( ColGrid ):
	def __init__( self, *args, **kwargs ):
		super().__init__( *args, **kwargs )
		self.GetGridWindow().Bind( wx.EVT_MOTION, self.OnMotionHover )
		# self.GetGridWindow().Bind( wx.EVT_LEAVE_WINDOW, self.OnLeaveHover )
		
	def HitRowTest(self,x,y):
		"""Convert client coordinates to cell position.

		@return: a tuple of (row,col). If the position is not over a column or row,
				then it will have a value of -1.
				
		Note: client coordinates are client coordinates of wx.Grid.GetGridWindow(), not
				the grid itself!
		"""
		x, y = self.CalcUnscrolledPosition(x, y)
		return self.YToRow(y)
		
	def OnLeaveHover( self, event ):
		self.ClearSelection()
		
	def OnMotionHover( self, event ):
		row = self.HitRowTest( event.GetX(), event.GetY() )
		if row < 0:
			self.ClearSelection()
		else:
			self.SelectRow( row )
			
def AugmentGridHoverRow( grid ):
	def HitRowTest( x, y ):
		"""Convert client coordinates to cell position.

		@return: a tuple of (row,col). If the position is not over a column or row,
				then it will have a value of -1.
				
		Note: client coordinates are client coordinates of wx.Grid.GetGridWindow(), not
				the grid itgrid!
		"""
		x, y = grid.CalcUnscrolledPosition(x, y)
		return grid.YToRow(y)
		
	def OnLeaveHover( event ):
		grid.ClearSelection()
		
	def OnMotionHover( event ):
		row = HitRowTest( event.GetX(), event.GetY() )
		if row < 0:
			grid.ClearSelection()
		else:
			grid.SelectRow( row )

	grid.GetGridWindow().Bind( wx.EVT_MOTION, OnMotionHover )
	# grid.GetGridWindow().Bind( wx.EVT_LEAVE_WINDOW, OnLeaveHover )
	return grid
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,200))
	grid = ColGridHoverRow( mainWin )
	
	max_cols = 10
	max_rows = 10
	colnames = ['Col {}'.format(c) for c in range(max_cols)]
	data = [['({},{})'.format(r, c) for r in range(max_rows)] for c in range(max_cols)]
	grid.Set( data=data, colnames=colnames )
	
	mainWin.Show()
	app.MainLoop()
