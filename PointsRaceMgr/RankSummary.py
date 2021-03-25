import wx
import wx.grid		as gridlib
import Model
import Utils
import re

class RankSummary( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__(parent, id, style=wx.BORDER_SUNKEN)
		
		self.SetDoubleBuffered(True)
		self.SetBackgroundColour( wx.WHITE )

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)

		self.grid = gridlib.Grid( self )
		self.grid.CreateGrid( 0, 5 )
		self.grid.SetRowLabelSize( 0 )

		self.hbs.Add( self.grid, 1, wx.EXPAND )
		self.SetSizer(self.hbs)

	def refresh( self ):
		race = Model.race
		riders = race.getRiders() if race else []
		hasNumWins = race.rankBy == race.RankByLapsPointsNumWins
		pointsFmt = Utils.asInt if all(rr.pointsTotal == int(rr.pointsTotal) for rr in riders) else Utils.asFloat
		existingPointsFmt = Utils.asInt if all(rr.existingPoints == int(rr.existingPoints) for rr in riders) else Utils.asFloat
				
		riderInfo = {info.bib:info for info in race.riderInfo} if race else {}
		
		headers = ['Rank', 'Points', 'Bib',]
		iRiderInfoBegin = len(headers)
		headerNames = Model.RiderInfo.HeaderNames[2:]
		fieldNames = Model.RiderInfo.FieldNames[2:]
		headers.extend( headerNames )
		iRiderInfoEnd = len(headers)
		if hasNumWins:
			headers.append('Num Wins')
		headers.append( 'Finish' )
		
		self.grid.BeginBatch()
		Utils.AdjustGridSize( self.grid, len(riders), len(headers) )
		
		for c in range(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( c, headers[c] )
			attr = gridlib.GridCellAttr()
			attr.SetReadOnly()
			attr.SetAlignment(wx.ALIGN_LEFT if iRiderInfoBegin <= c < iRiderInfoEnd else wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
			attr.SetFont( Utils.BigFont() )
			if headers[c] == 'Bib':
				attr.SetBackgroundColour( wx.Colour(178, 236, 255) )
			self.grid.SetColAttr( c, attr )
		
		gr = Model.GetRank()
		for rank, rr in enumerate(riders, 1):
			row = rank-1
			col = 0
			
			# Rank
			self.grid.SetCellValue( row, col, gr(rank, rr) )
			col += 1
			
			# Points
			self.grid.SetCellValue( row, col, pointsFmt(rr.pointsTotal) )
			col += 1
			
			# Bib
			self.grid.SetCellValue( row, col, '{}'.format(rr.num) )
			col += 1
	
			# Rider info.
			ri = riderInfo.get(rr.num, None)
			for f in fieldNames:
				self.grid.SetCellValue( row, col, '{}'.format(getattr(ri,f,'')) )
				col += 1
				
			# Wins
			if hasNumWins:
				self.grid.SetCellValue( row, col, '{}'.format(rr.numWins) if rr.numWins else '' )
				col += 1
				
			# Finish order
			self.grid.SetCellValue( row, col, '{}'.format(rr.finishOrder) if rr.finishOrder not in (0,1000) else '' )
			col += 1

		self.grid.EndBatch()
		self.grid.AutoSize()
		self.Layout()
	
	def commit( self ):
		pass
	
if __name__ == '__main__':
	app = wx.App( False )
	mainWin = wx.Frame(None,title="RankSummary", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	rd = RankSummary(mainWin)
	rd.refresh()
	mainWin.Show()
	app.MainLoop()
