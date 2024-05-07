import wx
import os
import sys
import getpass

import Utils
from Utils				import logCall, logException
import Model
import ExportGrid
from pdf import PDF
import xlsxwriter

from ReorderableGrid import ReorderableGrid
from FixCategories import FixCategories
from GetTeamResults			import GetTeamResults
from ReadSignOnSheet import ExcelLink
from RaceInputState import RaceInputState
import Version

class TeamResults( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize ):
		super().__init__( parent, id, size=size )
		
		self.state = RaceInputState()
		
		vsOverall = wx.BoxSizer( wx.VERTICAL )
		
		#---------------------------------------------------------------
		self.colnames = (
			_('Pos'),
			_('Team'),
			_('Time'),
			_('Gap'),
		)
		self.grid = ReorderableGrid( self )
		self.grid.CreateGrid( 0, len(self.colnames) )
		self.grid.SetRowLabelSize( 0 )
		self.grid.SetMargins( 0, 0 )
		self.grid.AutoSizeColumns( True )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()
		
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )

		#---------------------------------------------------------------
		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		
		self.categoryLabel = wx.StaticText( self, label = _('Category:') )
		self.categoryChoice = wx.Choice( self )
		self.Bind(wx.EVT_CHOICE, self.doChooseCategory, self.categoryChoice)
		
		self.exportButton = wx.Button( self, label='{} {}/{}'.format(_('Export'), _('Excel'), _('PDF')) )
		self.exportButton.Bind( wx.EVT_BUTTON, self.doExport )
		
		self.hbs.Add( self.categoryLabel, flag=wx.TOP|wx.BOTTOM|wx.LEFT|wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.categoryChoice, flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.Add( self.exportButton, flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL, border=4 )
		
		#---------------------------------------------------------------
		
		vsOverall.Add( self.hbs, flag=wx.ALL, border=4 )
		vsOverall.Add( self.grid, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		self.SetSizer( vsOverall )
	
	def doChooseCategory( self, event ):
		Model.setCategoryChoice( self.categoryChoice.GetSelection(), 'resultsCategory' )
		self.refresh()
		
	@logCall
	def doExport( self, event=None ):
		race = Model.race
		if not race:
			return
		
		fileName = Utils.getMainWin().fileName if Utils.getMainWin() else 'Test.cmn'
		
		#---------------------------------------------------------------------------------
		# Create an Excel file.
		#
		xlFileName = os.path.splitext(fileName)[0] + '-TeamResults.xlsx'

		try:
			wb = xlsxwriter.Workbook( xlFileName )
			formats = ExportGrid.ExportGrid.getExcelFormatsXLSX( wb )
			
			ues = Utils.UniqueExcelSheetName()
			for category in race.getCategories( publishOnly=True ):			
				eg = self.toExportGrid( category )
				if eg:
					ws = wb.add_worksheet( ues.getSheetName(category.fullname) )
					eg.toExcelSheetXLSX( formats, ws )
			wb.close()
		except Exception as e:
			logException( e, sys.exc_info() )
		del wb
		
		#---------------------------------------------------------------------------------
		# Create a PDF file.
		#
		pdfFileName = os.path.splitext(fileName)[0] + '-TeamResults.pdf'
		
		try:
			pdf = PDF( orientation = 'P' )
			pdf.set_font( 'Arial', '', 12 )
			pdf.set_author( getpass.getuser() )
			pdf.set_keywords( 'CrossMgr Team Results' )
			pdf.set_creator( Version.AppVerName )
			pdf.set_title( os.path.splitext(pdfFileName)[0].replace('-', ' ') )
			for category in race.getCategories( publishOnly=True ):
				eg = self.toExportGrid( category )
				if eg:
					eg.drawToFitPDF( pdf, orientation=wx.PORTRAIT )
			pdf.output( pdfFileName, 'F' )
		except Exception as e:
			logException( e, sys.exc_info() )
		del pdf
	
	def getColNames( self ):
		race = Model.race
		colnames = list( self.colnames )
		
		col = 2
		if   race.teamRankOption == race.teamRankByRiderTime:
			colnames[col] = '{}\n{}'.format(_('Time'), Utils.ordinal(race.nthTeamRider))
		elif race.teamRankOption == race.teamRankBySumPoints:
			colnames[col] = '{}\n{} {}'.format(_('Sum Points'), _('Top'), race.topTeamResults)
		elif race.teamRankOption == race.teamRankBySumTime:
			colnames[col] = '{}\n{} {}'.format(_('Sum Time'), _('Top'), race.topTeamResults)
		elif race.teamRankOption == race.teamRankBySumPercentTime:
			colnames[col] = '{}\n{} {}'.format(_('Sum %'), _('Top'), race.topTeamResults)
			
		if race.showNumTeamParticipants:
			colnames.append( _('Participants') )
		return colnames
	
	def updateGrid( self ):
		race = Model.race
		if not race:
			self.grid.ClearGrid()
			return
		category = FixCategories( self.categoryChoice, getattr(race, 'resultsCategory', 0) )
		self.hbs.Layout()
		for si in self.hbs.GetChildren():
			if si.IsWindow():
				si.GetWindow().Refresh()
		self.category = category
		
		colnames = self.getColNames()
		
		results = GetTeamResults( self.category )
		Utils.AdjustGridSize( self.grid, len(results), len(colnames) )
		
		for col, colName in enumerate(colnames):
			self.grid.SetColLabelValue( col, colName )
			attr = wx.grid.GridCellAttr()
			attr.SetReadOnly( True )
			if col != 1:
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_TOP )			
			self.grid.SetColAttr( col, attr )
		
		for row, r in enumerate(results):
			self.grid.SetCellValue( row, 0, '{}'.format(row+1) )
			self.grid.SetCellValue( row, 1, r.team )
			self.grid.SetCellValue( row, 2, r.criteria )
			self.grid.SetCellValue( row, 3, r.gap )
			if race.showNumTeamParticipants:
				self.grid.SetCellValue( row, 4, '{}'.format(r.numParticipants) )
		
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )
	
	def toExportGrid( self, category ):
		race = Model.race
		if not race:
			self.grid.ClearGrid()
			return None
		
		title = '\n'.join( [race.title, _('Team Results'), category.fullname,] )
		colnames = [c.replace('\n', ' ') for c in self.getColNames()]
		data = [[] for c in colnames]
		for pos, r in enumerate( GetTeamResults(category), 1 ):
			data[0].append( '{}'.format(pos) )
			data[1].append( r.team )
			data[2].append( r.criteria )
			data[3].append( r.gap )
			if race.showNumTeamParticipants:
				data[4].append( '{}'.format(r.numParticipants) )
		
		return ExportGrid.ExportGrid( colnames=colnames, data=data, title=title, leftJustifyCols=[1] )
	
	def refresh( self ):
		self.updateGrid()
		
	def commit( self ):
		pass

if __name__ == '__main__':
	app = wx.App(False)
	app.SetAppName("CrossMgr")
	
	Utils.disable_stdout_buffering()
	
	race = Model.newRace()
	race._populate()
	
	fnameRiderInfo = os.path.join(Utils.getHomeDir(), 'SimulationRiderData.xlsx')
	sheetName = 'RiderData'
	
	race.excelLink = ExcelLink()
	race.excelLink.setFileName( fnameRiderInfo )
	race.excelLink.setSheetName( sheetName )
	race.excelLink.setFieldCol( {'Bib#':0, 'LastName':1, 'FirstName':2, 'Team':3} )
	
	mainWin = wx.Frame(None, title="TeamResults", size=(800,700) )
	teamResults = TeamResults( mainWin )
	mainWin.Show()
	
	teamResults.refresh()	
	app.MainLoop()
