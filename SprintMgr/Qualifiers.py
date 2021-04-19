import os
import sys
import wx
import wx.grid as gridlib

import TestData
import Utils
import Model
from Competitions import SetDefaultData
from ReorderableGrid import ReorderableGrid
from Events import GetFont
from HighPrecisionTimeEditor import HighPrecisionTimeEditor
from Competitions import getCompetitions

#--------------------------------------------------------------------------------
class Qualifiers(wx.Panel):

	def __init__(self, parent):
		super().__init__(parent)
 
		font = GetFont()
		self.title = wx.StaticText(self, label="Enter each rider's qualifying time in hh:mm:ss.ddd format.")
		self.title.SetFont( font )
		
		self.renumberButton = wx.Button( self, label='Renumber Bibs by Time' )
		self.renumberButton.SetFont( font )
		self.renumberButton.Bind( wx.EVT_BUTTON, self.doRenumber )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.title, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border = 6 )
		hs.AddStretchSpacer()
		hs.Add( self.renumberButton, 0, flag=wx.ALL, border = 6 )
 
		self.headerNames = ['Bib', 'Name', 'Team', 'Time', 'UCI Points', 'Status']
		self.headerNameMap = Model.Rider.GetHeaderNameMap( self.headerNames )
		self.iQualifyingTime = self.headerNameMap['qualifying_time']
		self.iStatus = self.headerNameMap['status']
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(self.headerNames) )
		self.setColNames()
		self.grid.EnableReorderRows( False )

		# Set specialized editors for appropriate columns.
		self.grid.SetLabelFont( font )
		for col in range(self.grid.GetNumberCols()):
			attr = gridlib.GridCellAttr()
			attr.SetFont( font )
			if col == self.iQualifyingTime:
				attr.SetEditor( HighPrecisionTimeEditor() )
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTRE )
			elif col == self.iStatus:
				attr.SetEditor( gridlib.GridCellChoiceEditor(choices = ['', 'DNQ']) )
				attr.SetReadOnly( False )
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
			else:
				if col == 0:
					attr.SetRenderer( gridlib.GridCellNumberRenderer() )
				attr.SetReadOnly( True )
			self.grid.SetColAttr( col, attr )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add( hs, 0, flag=wx.ALL|wx.EXPAND, border = 6 )
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6)
		self.SetSizer(sizer)
		
	def getGrid( self ):
		return self.grid
		
	def setColNames( self ):
		for col, headerName in enumerate(self.headerNames):
			self.grid.SetColLabelValue( col, headerName )
						
	def setTestData( self ):
		self.grid.ClearGrid()

		testData = TestData.getTestData()
		Utils.AdjustGridSize( self.grid, rowsRequired = len(testData) )
			
		for row, data in enumerate(testData):
			data['full_name'] = data['first_name'] + ' ' + data['last_name'].upper()
			for k,v in data.items():
				if k in self.headerNameMap:
					self.grid.SetCellValue( row, self.headerNameMap[k], '{}'.format(v) )
		
		# Fix up the column and row sizes.
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )
		
		Model.model.setCompetition( getCompetitions()[0], 0 )
		self.commit()
		
	def refresh( self ):
		model = Model.model
		riders = model.riders
		
		self.renumberButton.Show( model.competition.isMTB )
		
		Utils.AdjustGridSize( self.grid, rowsRequired = len(riders) )
		for row, r in enumerate(riders):
			for col, value in enumerate(['{}'.format(r.bib), r.full_name, r.team, r.qualifying_time_text]):
				self.grid.SetCellValue( row, col, value )
				
		# Fix up the column and row sizes.
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )
		self.grid.SetColSize( self.grid.GetNumberCols()-1, 96 )
		
		self.Layout()
		self.Refresh()
		
	def setQT( self ):
		# The qualifying times can be changed at any time, however, if the competition is under way, the events cannot
		# be adjusted.
		model = Model.model
		riders = model.riders
		
		self.grid.SaveEditControlValue()

		for row in range(self.grid.GetNumberRows()):
			v = self.grid.GetCellValue( row, self.iQualifyingTime ).strip()
			if v:
				qt = Utils.StrToSeconds( v )
			else:
				qt = Model.QualifyingTimeDefault
				
			qt = min( qt, Model.QualifyingTimeDefault )
			status = self.grid.GetCellValue( row, self.iStatus ).strip()
			
			rider = riders[row]
			if rider.qualifyingTime != qt or rider.status != status:
				rider.qualifyingTime = qt
				rider.status = status
				model.setChanged( True )
		
	def commit( self ):
		# The qualifying times can be changed at any time, however, if the competition is underway, the events cannot
		# be adusted.
		model = Model.model
		riders = model.riders
		self.setQT()
		if model.canReassignStarters():
			model.setQualifyingTimes()
			Utils.getMainWin().resetEvents()
			
	def doRenumber( self, event ):
		model = Model.model
		message = 'Sequence Bib numbers by Decreasing UCI Points.\n\nContinue?' if model.isKeirin else 'Sequence Bib numbers by Increasing Qualifying Time.\n\nContinue?'
		if not Utils.MessageOKCancel( self, message, 'Renumber Riders' ):
			return
	
		self.setQT()
		
		key = (lambda x: x.keyPoints()) if model.isKeirin else (lambda x: x.keyQualifying())
		riders = sorted( model.riders, key = key )
		for r, rider in enumerate(riders, 1):
			rider.bib = r
		
		wx.CallAfter( self.refresh )
		
########################################################################

class QualifiersFrame(wx.Frame):
	""""""
 
	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		wx.Frame.__init__(self, None, title="Qualifier Grid Test", size=(800,600) )
		panel = Qualifiers(self)
		panel.refresh()
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	Model.model = SetDefaultData()
	app = wx.App(False)
	frame = QualifiersFrame()
	app.MainLoop()
