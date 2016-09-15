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
	ParticipationCol = 4
	DNFCol = 5
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		#--------------------------------------------------------------------------
		box = wx.StaticBox( self, -1, 'Score Competitors by' )
		bsizer = wx.StaticBoxSizer( box, wx.VERTICAL )
		
		self.scoreByPoints = wx.RadioButton( self, label='Points', style=wx.RB_GROUP )
		self.scoreByPoints.Bind( wx.EVT_RADIOBUTTON, self.fixEnable )
		
		self.scoreByTime = wx.RadioButton( self, label='Time' )
		self.scoreByTime.Bind( wx.EVT_RADIOBUTTON, self.fixEnable )
		
		self.scoreByPercent = wx.RadioButton( self, label='Percent Time (100 * WinnersTime / FinishTime)' )
		self.scoreByPercent.Bind( wx.EVT_RADIOBUTTON, self.fixEnable )
		
		self.scoreByTrueSkill = wx.RadioButton( self, label='TrueSkill' )
		self.scoreByTrueSkill.Bind( wx.EVT_RADIOBUTTON, self.fixEnable )
		
		self.scoreByPoints.SetValue( True )
		
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( self.scoreByPoints )
		hb.Add( self.scoreByTime, flag=wx.LEFT, border=16 )
		hb.Add( self.scoreByPercent, flag=wx.LEFT, border=16 )
		hb.Add( self.scoreByTrueSkill, flag=wx.LEFT, border=16 )
		bsizer.Add( hb, flag=wx.ALL, border=2 )
		
		#--------------------------------------------------------------------------
		bsizer.Add( wx.StaticLine(self), 1, flag=wx.EXPAND|wx.ALL, border=4 )
		self.considerPrimePointsOrTimeBonus = wx.CheckBox( self, label='Consider Points or Time Bonuses from CrossMgr Primes' )
		self.considerPrimePointsOrTimeBonus.SetValue( True )
		bsizer.Add( self.considerPrimePointsOrTimeBonus, 0, flag=wx.ALL, border=4 )
		
		#--------------------------------------------------------------------------
		bsizer.Add( wx.StaticLine(self), 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		maxOptions = 30
		self.considerLabel = wx.StaticText( self, label='{}:'.format('Consider') )
		self.bestResultsToConsider = wx.Choice( self, choices = ['All Result', 'Best Result Only'] + ['{} {} {}'.format('Best', i, 'Results Only') for i in xrange(2,maxOptions+1)] )
		
		self.participationLabel = wx.StaticText( self, label='{}:'.format('Must have completed') )
		self.mustHaveCompleted = wx.Choice( self, choices = ['{} {}'.format(i, 'or more Events') for i in xrange(0,maxOptions+1)] )
		
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( self.considerLabel, flag=wx.ALIGN_CENTRE_VERTICAL )
		hb.Add( self.bestResultsToConsider )
		hb.Add( self.participationLabel, flag=wx.LEFT|wx.ALIGN_CENTRE_VERTICAL, border=16 )
		hb.Add( self.mustHaveCompleted )
		bsizer.Add( hb, flag=wx.ALL, border=2 )
		
		#--------------------------------------------------------------------------
		bsizer.Add( wx.StaticLine(self), 1, flag=wx.EXPAND|wx.ALL, border=4 )
		self.ifRidersTiedOnPoints = wx.StaticText(self, label='If Riders are Tied on Points:')
		bsizer.Add( self.ifRidersTiedOnPoints, flag=wx.ALL, border=2 )
		self.mostEventsCompleted = wx.CheckBox( self, label='Consider Number of Events Completed' )
		self.mostEventsCompleted.SetValue( False )
		bsizer.Add( self.mostEventsCompleted, 0, flag=wx.ALL, border=4 )
		
		bsizer.Add( wx.StaticLine(self), 1, flag=wx.EXPAND|wx.ALL, border=4 )
		self.numPlacesTieBreaker = wx.RadioBox(self, majorDimension=3, style=wx.RA_SPECIFY_ROWS, choices = [
			'Do not consider Place Finishes.',
			'Number of 1st Place Finishes',
			'Number of 1st then 2nd Place Finishes',
			'Number of 1st, 2nd then 3rd Place Finishes',
			'Number of 1st, 2nd, 3rd then 4th Place Finishes',
			'Number of 1st, 2nd, 3rd, 4th then 5th Place Finishes',
		])
		self.numPlacesTieBreaker.SetLabel( u'If Riders are still Tied on Points:' )
		bsizer.Add( self.numPlacesTieBreaker, 0, flag=wx.ALL|wx.EXPAND, border=2 )
		self.ifRidersAreStillTiedOnPoints = wx.StaticText(self, label=u'If Riders are still Tied on Points, use most Recent Results')
		bsizer.Add( self.ifRidersAreStillTiedOnPoints, flag=wx.ALL, border=4 )

		self.headerNames = ['Name', 'OldName', 'Depth', 'Points for Position', 'Participation', 'DNF']
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 50, len(self.headerNames) )
		for col in xrange(self.grid.GetNumberCols()):
			self.grid.SetColLabelValue( col, self.headerNames[col] + (u'       ' if  self.headerNames[col] == 'DNF' else '') )
		
		attr = gridlib.GridCellAttr()
		attr.SetReadOnly( True )
		attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		self.grid.SetColAttr( self.DepthCol, attr )
		
		attr = gridlib.GridCellAttr()
		attr.SetEditor( PointsEditor() )
		self.grid.SetColAttr( self.PointsCol, attr )
		
		for c in (self.ParticipationCol, self.DNFCol):
			attr = gridlib.GridCellAttr()
			attr.SetRenderer( wx.grid.GridCellNumberRenderer() )
			attr.SetEditor( wx.grid.GridCellNumberEditor(0, 10000) )
			self.grid.SetColAttr( c, attr )
		
		self.gridAutoSize()

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(bsizer, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		self.pointsStructures = wx.StaticText(self, wx.ID_ANY, 'Points Structures:')
		sizer.Add( self.pointsStructures, 0, flag=wx.ALL, border = 4 )
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6)
		self.SetSizer(sizer)
		
		self.scoreByPointsControls = [
			self.ifRidersTiedOnPoints,
			self.mostEventsCompleted,
			self.numPlacesTieBreaker,
			self.ifRidersAreStillTiedOnPoints,
			self.pointsStructures,
			self.grid,
		]
		
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
		if row >= 0:
			self.updateDepth( row )
		wx.CallAfter( self.gridAutoSize )
	
	def fixEnable( self, event = None ):
		enable = self.scoreByPoints.GetValue()
		for c in self.scoreByPointsControls:
			c.Enable( enable )
	
	def refresh( self ):
		model = SeriesModel.model
		for row in xrange(self.grid.GetNumberRows()):
			for col in xrange(self.grid.GetNumberCols()):
				self.grid.SetCellValue( row, col, '' )
		
		for row, ps in enumerate(model.pointStructures):
			self.grid.SetCellValue( row, self.NameCol, ps.name )
			self.grid.SetCellValue( row, self.OldNameCol, ps.name )
			self.grid.SetCellValue( row, self.PointsCol, ps.getStr() )
			self.grid.SetCellValue( row, self.ParticipationCol, unicode(ps.participationPoints) )
			self.grid.SetCellValue( row, self.DNFCol, unicode(ps.dnfPoints) )
			self.updateDepth( row )
			
		wx.CallAfter( self.gridAutoSize )
		
		self.considerPrimePointsOrTimeBonus.SetValue( model.considerPrimePointsOrTimeBonus )
		self.bestResultsToConsider.SetSelection( model.bestResultsToConsider )
		self.mustHaveCompleted.SetSelection( model.mustHaveCompleted )
		
		self.mostEventsCompleted.SetValue( model.useMostEventsCompleted )
		self.numPlacesTieBreaker.SetSelection( model.numPlacesTieBreaker )

		if model.scoreByTime:
			self.scoreByTime.SetValue( True )
		elif model.scoreByPercent:
			self.scoreByPercent.SetValue( True )
		elif model.scoreByTrueSkill:
			self.scoreByTrueSkill.SetValue( True )
		else:
			self.scoreByPoints.SetValue( True )
		self.fixEnable()
	
	def commit( self ):
		self.grid.SaveEditControlValue()
		self.grid.DisableCellEditControl()	# Make sure the current edit is committed.
		pointsList = []
		for row in xrange(self.grid.GetNumberRows()):
			if( self.grid.GetCellValue(row, self.NameCol).strip() ):
				pointsList.append( (self.grid.GetCellValue(row, self.NameCol),
									self.grid.GetCellValue(row, self.OldNameCol),
									self.grid.GetCellValue(row, self.PointsCol),
									self.grid.GetCellValue(row, self.ParticipationCol),
									self.grid.GetCellValue(row, self.DNFCol),
									) )
		
		model = SeriesModel.model
		model.setPoints( pointsList )
		
		modelUpdate = {
			'considerPrimePointsOrTimeBonus': self.considerPrimePointsOrTimeBonus.GetValue(),
			'bestResultsToConsider': self.bestResultsToConsider.GetSelection(),
			'mustHaveCompleted': self.mustHaveCompleted.GetSelection(),
			'useMostEventsCompleted': self.mostEventsCompleted.GetValue(),
			'numPlacesTieBreaker': self.numPlacesTieBreaker.GetSelection(),
			'scoreByTime': self.scoreByTime.GetValue(),
			'scoreByPercent': self.scoreByPercent.GetValue(),
			'scoreByTrueSkill': self.scoreByTrueSkill.GetValue(),
		}
		
		for attr, value in modelUpdate.iteritems():
			if getattr(model, attr) != value:
				setattr( model, attr, value )
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
