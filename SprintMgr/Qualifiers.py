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
from Excel import GetExcelReader

#--------------------------------------------------------------------------------
class Qualifiers(wx.Panel):

	def __init__(self, parent):
		super().__init__(parent)
 
		font = GetFont()
		self.title = wx.StaticText(self, label="Qualifying times in hh:mm:ss.000 format.")
		self.title.SetFont( font )
		
		self.renumberButton = wx.Button( self, label='Renumber Bibs by Time' )
		self.renumberButton.SetFont( font )
		self.renumberButton.Bind( wx.EVT_BUTTON, self.doRenumber )
		
		self.excelImportButton = wx.Button( self, label='Import Times from Excel' )
		self.excelImportButton.SetFont( font )
		self.excelImportButton.Bind( wx.EVT_BUTTON, self.doExcelImport )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.title, 0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border = 6 )
		hs.AddStretchSpacer()
		hs.Add( self.renumberButton, flag=wx.ALL, border = 6 )
		hs.Add( self.excelImportButton, flag=wx.ALL, border = 6 )
 
		self.headerNames = ['Bib', 'Name', 'Team', 'Time', 'Status']
		self.headerNameMap = Model.Rider.GetHeaderNameMap( self.headerNames )
		self.iBib = 0
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
			elif col == 0:
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
			data['full_name'] = data['last_name'].upper() + ' ' + data['first_name']
			for k,v in data.items():
				if k in self.headerNameMap:
					self.grid.SetCellValue( row, self.headerNameMap[k], '{}'.format(v) )
		
		# Fix up the column and row sizes.
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )
		
		Model.model.setCompetition( next(c for c in getCompetitions() if 'Keirin' in c.name), 0 )
		self.commit()
	
	def doExcelImport( self, event ):
		self.grid.SaveEditControlValue()
		
		model = Model.model
		riders = model.riders
		
		with wx.FileDialog(self, "Choose Excel file with Qualifying times", wildcard="Excel files (*.xlsx)|*.xlsx",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR) as fileDialog:
		
			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return
			pathname = fileDialog.GetPath()

		reader = GetExcelReader( pathname )
		sheet_names = reader.sheet_names()
		with wx.SingleChoiceDialog(self, "Choose Sheet with qualifying times", "Choose Qualifying Sheet", sheet_names) as choiceDialog:
			if choiceDialog.ShowModal() == wx.ID_CANCEL:
				return
			sheet_name = choiceDialog.GetStringSelection()

		# Extract the times from the sheet.
		bib_headers = {'bib', 'bib#', 'bibnum', 'bibnumber', 'riderbib', 'ridernum', 'num', 'number'}
		time_headers = {'time', 'qualifying', 'qualifyingtime'}

		qualifyingTimes = {}
		headerMap = {}
		for row in reader.iter_list(sheet_name):
			if len(headerMap) < 2:
				for c, v in enumerate(row):
					if str(v).lower().replace(' ','').replace('_','').strip() in bib_headers:
						headerMap['bib'] = c
					if str(v).lower().replace(' ','').replace('_','').strip() in time_headers:
						headerMap['time'] = c
				continue
				
			try:
				qualifyingTimes[int(row[headerMap['bib']])] = Utils.StrToSeconds(str(row[headerMap['time']]))
			except Exception as e:
				pass
	
		if len(headerMap) < 2:
			message = '{}:\n\n\t{}\n\n{}'.format(
				"Recognized Excel column headers are",
				', '.join(str(h) for h in sorted(bib_headers|time_headers)),
				'Capitalization and spaces are ignored.'
			)
			with wx.MessageDialog( self, message, "Unrecognized column headers in Excel sheet", style=wx.OK ) as messageDialog:
				messageDialog.ShowModal()
				return

		# Write the qualifying times into the grid.
		missingBibs = []
		for row in range(self.grid.GetNumberRows()):
			try:
				bib = int(self.grid.GetCellValue( row, self.iBib ).strip())
			except Exception:
				continue
				
			if bib in qualifyingTimes:
				self.grid.SetCellValue( row, self.iQualifyingTime, Utils.SecondsToStr(qualifyingTimes[bib]) )
			else:
				missingBibs.append( bib )
	
		# Report any missing bibs.
		if missingBibs:
			message = '{}:\n\n\t\t{}'.format(
				"Bibs missing from Import",
				', '.join(str(bib) for bib in missingBibs)
			)
			with wx.MessageDialog( self, message, "Import Warning", style=wx.OK ) as messageDialog:
				messageDialog.ShowModal()
	
	def refresh( self ):
		model = Model.model
		riders = model.riders
		
		self.renumberButton.Show( model.competition.isMTB )
		
		Utils.AdjustGridSize( self.grid, rowsRequired = len(riders) )
		for row, r in enumerate(riders):
			for attr,col in self.headerNameMap.items():
				if attr == 'qualifying_time':
					value = getattr( r, attr + '_text' )
				else:
					value = getattr( r, attr )
				self.grid.SetCellValue( row, col, '{}'.format(value) )
				
		# Fix up the column and row sizes.
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )
		self.grid.SetColSize( self.grid.GetNumberCols()-2, 96 )
		
		self.Layout()
		self.Refresh()
		
	def setQualifyingInfo( self ):
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
			if rider.qualifying_time != qt or rider.status != status:
				rider.qualifying_time = qt
				rider.status = status
				model.setChanged( True )
		
	def commit( self ):
		# The qualifying times can be changed at any time, however, if the competition is underway, the events cannot
		# be adusted.
		model = Model.model
		riders = model.riders
		self.setQualifyingInfo()
		if model.canReassignStarters():
			model.setQualifyingInfo()
			Utils.getMainWin().resetEvents()
			
	def doRenumber( self, event ):
		model = Model.model
		message = 'Sequence Bib numbers by Decreasing UCI Points.\n\nContinue?' if model.isKeirin else 'Sequence Bib numbers by Increasing Qualifying Time.\n\nContinue?'
		if not Utils.MessageOKCancel( self, message, 'Renumber Riders' ):
			return
	
		self.setQualifyingInfo()
		
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
