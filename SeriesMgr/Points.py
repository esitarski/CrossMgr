import wx
import wx.grid as gridlib

import os
import sys
from ReorderableGrid import ReorderableGrid
import SeriesModel
import Utils

class PointsEditor(gridlib.PyGridCellEditor):

	DefaultStartValue = ''

	def __init__(self):
		self._tc = None
		self.startValue = self.DefaultStartValue
		gridlib.PyGridCellEditor.__init__(self)
		
	def Create( self, parent, id, evtHandler ):
		self._tc = wx.TextCtrl( parent, id, value = self.DefaultStartValue, style=wx.TE_PROCESS_ENTER )
		self.SetControl( self._tc )
		if evtHandler:
			self._tc.PushEventHandler( evtHandler )
	
	def SetSize( self, rect ):
		self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2, wx.SIZE_ALLOW_MINUS_ONE )
	
	def BeginEdit( self, row, col, grid ):
		self.startValue = grid.GetTable().GetValue(row, col)
		self._tc.SetValue( self.startValue )
		self._tc.SetFocus()
		
	def EndEdit( self, row, col, grid, value = None ):
		changed = False
		val = self._tc.GetValue().strip()
		if val:
			val = SeriesModel.PointStructure( 'EditCheck', val ).getStr()
		if val != self.startValue:
			change = True
			grid.GetTable().SetValue( row, col, val )
			grid.GetParent().updateDepth( row )
			wx.CallAfter( grid.GetParent().gridAutoSize )
		self.startValue = self.DefaultStartValue
		self._tc.SetValue( self.startValue )
		
	def Reset( self ):
		self._tc.SetValue( self.startValue )
		
	def Clone( self ):
		return PointsEditor()

class Points(wx.Panel):
	#----------------------------------------------------------------------
	NameCol = 0
	OldNameCol = 1
	DepthCol = 2
	PointsCol = 3
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		box = wx.StaticBox( self, -1, 'Scoring Rules' )
		bsizer = wx.StaticBoxSizer( box, wx.VERTICAL )
		bsizer.Add( wx.StaticText(self, label='Score Riders by Points:'), flag=wx.ALL, border=2 )
		
		bsizer.Add( wx.StaticLine(self), 1, flag=wx.EXPAND|wx.ALL, border=4 )
		bsizer.Add( wx.StaticText(self, label='If Riders are Tied on Points:'), flag=wx.ALL, border=2 )
		self.mostEventsCompleted = wx.CheckBox( self, label='Consider Most Events Completed' )
		self.mostEventsCompleted.SetValue( False )
		bsizer.Add( self.mostEventsCompleted, 0, flag=wx.ALL, border=4 )
		
		bsizer.Add( wx.StaticLine(self), 1, flag=wx.EXPAND|wx.ALL, border=4 )
		self.numPlacesTieBreaker = wx.RadioBox(self, majorDimension = 1, choices = [
			'Do not consider Place Finishes.',
			'Most 1st Place Finishes',
			'Most 1st and 2nd Place Finishes',
			'Most 1st, 2nd and 3rd Place Finishes',
			'Most 1st, 2nd, 3rd and 4th Place Finishes',
			'Most 1st, 2nd, 3rd, 4th and 5th Place Finishes',
		])
		self.numPlacesTieBreaker.SetLabel( u'If Riders are still Tied on Points:' )
		bsizer.Add( self.numPlacesTieBreaker, 0, flag=wx.ALL, border=2 )
		bsizer.Add( wx.StaticText(self, label=u'If Rider are still Tied on Points, use most Recent Results'), flag=wx.ALL, border=4 )

		self.headerNames = ['Name', 'OldName', 'Depth', 'Points for Position']
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 50, len(self.headerNames) )
		for col in xrange(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, self.headerNames[col] )
		
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly( True )
		attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		self.grid.SetColAttr( self.DepthCol, attr )
		
		attr = gridlib.GridCellAttr()
		attr.SetEditor( PointsEditor() )
		self.grid.SetColAttr( self.PointsCol, attr )
		
		self.gridAutoSize()

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(bsizer, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		sizer.Add( wx.StaticText(self, wx.ID_ANY, 'Points Structures:'), 0, flag=wx.ALL, border = 4 )
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6)
		self.SetSizer(sizer)
		
	def getGrid( self ):
		return self.grid
	
	def gridAutoSize( self ):
		self.grid.AutoSize()
		self.grid.SetColMinimalAcceptableWidth( 0 )
		self.grid.SetColMinimalWidth( self.OldNameCol, 0 )
		self.grid.SetColSize( self.OldNameCol, 0 )
		self.grid.EnableDragGridSize( False )
		self.grid.EnableDragColSize( False )
		self.Layout()
		self.Refresh()
	
	def updateDepth( self, row ):
		v = self.grid.GetCellValue(row, self.PointsCol).strip()
		depth = unicode(len(v.split())) if v else u''
		self.grid.SetCellValue( row, self.DepthCol, depth )
	
	def onGridChange( self, event ):
		row = event.GetRow()
		print 'onGridChange', row
		if row >= 0:
			self.updateDepth( row )
		wx.CallAfter( self.gridAutoSize )
	
	def refresh( self ):
		model = SeriesModel.model
		for row in xrange(self.grid.GetNumberRows()):
			for col in xrange(self.grid.GetNumberCols()):
				self.grid.SetCellValue( row, col, '' )
		
		for row, ps in enumerate(model.pointStructures):
			self.grid.SetCellValue( row, self.NameCol, ps.name )
			self.grid.SetCellValue( row, self.OldNameCol, ps.name )
			self.grid.SetCellValue( row, self.PointsCol, ps.getStr() )
			self.updateDepth( row )
			
		wx.CallAfter( self.gridAutoSize )
		
		self.mostEventsCompleted.SetValue( model.useMostEventsCompleted )
		self.numPlacesTieBreaker.SetSelection( model.numPlacesTieBreaker )
	
	def commit( self ):
		self.grid.DisableCellEditControl()	# Make sure the current edit is committed.
		pointsList = []
		for row in xrange(self.grid.GetNumberRows()):
			if( self.grid.GetCellValue(row, self.NameCol).strip() ):
				pointsList.append( (self.grid.GetCellValue(row, self.NameCol),
									self.grid.GetCellValue(row, self.OldNameCol),
									self.grid.GetCellValue(row, self.PointsCol) ) )
		
		model = SeriesModel.model
		model.setPoints( pointsList )
		if model.useMostEventsCompleted != self.mostEventsCompleted.GetValue():
			model.useMostEventsCompleted = self.mostEventsCompleted.GetValue()
			model.changed = True
		if model.numPlacesTieBreaker != self.numPlacesTieBreaker.GetSelection():
			model.numPlacesTieBreaker = self.numPlacesTieBreaker.GetSelection()
			model.changed = True
		
########################################################################

class PointsFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		wx.Frame.__init__(self, None, title="Reorder Grid Test", size=(800,600) )
		self.panel = Points(self)
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	frame = PointsFrame()
	frame.panel.refresh()
	app.MainLoop()