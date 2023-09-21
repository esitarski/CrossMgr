import re
import wx
import wx.grid		as gridlib
import Model
import Utils

class RankDetails( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY, labelClickCallback=None, labelDClickCallback=None ):
		super().__init__(parent, id, style=wx.BORDER_SUNKEN)
		
		self.labelClickCallback = labelClickCallback
		self.labelDClickCallback = labelDClickCallback
		
		self.SetDoubleBuffered(True)
		self.SetBackgroundColour( wx.WHITE )

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)

		self.grid = gridlib.Grid( self )
		self.grid.CreateGrid( 0, 5 )
		self.grid.SetRowLabelSize( 0 )
		if self.labelClickCallback:
			self.grid.Bind( gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.onLabelClick)
		if self.labelDClickCallback:
			self.grid.Bind( gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.onLabelDClick)

		self.hbs.Add( self.grid, 1, wx.EXPAND )
		self.SetSizer(self.hbs)

	def onLabelClick( self, event ):
		self.labelClickCallback(self.grid, event.GetCol())
		event.Skip()

	def onLabelDClick( self, event ):
		self.labelDClickCallback(self.grid, event.GetCol())
		event.Skip()

	def refresh( self ):
		race = Model.race
		riders = race.getRiders() if race else []
		
		Finisher = Model.Rider.Finisher
		
		hasExistingPoints = any( rr.existingPoints for rr in riders )

		hasNumWins = race.rankBy == race.RankByLapsPointsNumWins

		pointsFmt = Utils.asInt if all(rr.pointsTotal == int(rr.pointsTotal) for rr in riders) else Utils.asFloat
		existingPointsFmt = Utils.asInt if all(rr.existingPoints == int(rr.existingPoints) for rr in riders) else Utils.asFloat
		
		headers = ['Rank', 'Bib', 'Points',] + [race.getSprintLabel(s) for s in range(1, race.sprintCount+1)] + ['+/- Laps']
		if hasNumWins:
			headers.append('Num Wins')
		if hasExistingPoints:
			headers.append('Existing')
		headers.append( 'Finish' )
		
		self.grid.BeginBatch()
		Utils.AdjustGridSize( self.grid, len(riders), len(headers) )
		
		for c in range(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( c, headers[c] )
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly()
			attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
			attr.SetFont( Utils.BigFont() )
			if headers[c] == 'Bib':
				attr.SetBackgroundColour( wx.Colour(178, 236, 255) )
			self.grid.SetColAttr( c, attr )
			
		getRank = Model.GetRank()
		for rank, rr in enumerate(riders, 1):
			row = rank-1
			col = 0
			
			# Rank
			self.grid.SetCellValue( row, col, getRank(rank, rr) )
			col += 1
			
			# Bib
			self.grid.SetCellValue( row, col, '{}'.format(rr.num) )
			col += 1
	
			# Points
			self.grid.SetCellValue( row, col, pointsFmt(rr.pointsTotal) )
			col += 1
			
			# Sprints
			for s in range(1, race.sprintCount+1):
				place, points, tie = rr.sprintPlacePoints.get(s, (-1, -1, False))
				self.grid.SetCellValue( row, col, '{}'.format(points) if points > 0 else '')
				col += 1
			
			# +/- Laps
			self.grid.SetCellValue( row, col, '{}'.format(rr.lapsTotal) if rr.lapsTotal else '' )
			col += 1
			
			# Wins
			if hasNumWins:
				self.grid.SetCellValue( row, col, '{}'.format(rr.numWins) if rr.numWins else '' )
				col += 1
				
			# Existing Points
			if hasExistingPoints:
				self.grid.SetCellValue( row, col, existingPointsFmt(rr.existingPoints) if rr.existingPoints else '' )
				col += 1
				
			# Finish order
			text = ''
			if rr.status == Finisher:
				if rr.pulled:
					text = 'Ⓟ {}'.format( rr.finishOrder )
				elif race.isFinished:
					text = '{}'.format( rr.finishOrder )
			self.grid.SetCellValue( row, col, text )
			col += 1
		
		self.grid.EndBatch()
		self.grid.AutoSize()
		self.Layout()

	def commit( self ):
		pass
	
if __name__ == '__main__':
	app = wx.App( False )
	mainWin = wx.Frame(None,title="RankDetails", size=(600,400))
	Model.newRace()
	Model.race._populate()
	rd = RankDetails(mainWin)
	rd.refresh()
	mainWin.Show()
	app.MainLoop()
