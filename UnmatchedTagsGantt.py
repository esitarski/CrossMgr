import wx
import os
import sys
import xlwt
import webbrowser
from FitSheetWrapper import FitSheetWrapper
import Utils
import Model
import GanttChartPanel

def GetNowTime():
	race = Model.race
	return race.lastRaceTime() if race and race.isRunning() else None

class UnmatchedTagsGantt( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__(parent, id)

		self.SetBackgroundColour( wx.WHITE )
		
		self.hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.titleLabel = wx.StaticText( self, label = '{}:'.format(_('Unmatched RFID Tags')) )
		self.excelButton = wx.Button( self, label=_('Export to Excel') )
		self.excelButton.Bind( wx.EVT_BUTTON, self.onExcel )
		
		self.ganttChart = GanttChartPanel.GanttChartPanel( self )
		self.ganttChart.getNowTimeCallback = GetNowTime

		self.hbs.Add( self.titleLabel, flag=wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, border=4 )
		self.hbs.AddStretchSpacer()
		self.hbs.Add( self.excelButton, flag=wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border=4 )

		bs = wx.BoxSizer(wx.VERTICAL)
		bs.Add(self.hbs, flag=wx.GROW|wx.HORIZONTAL)
		bs.Add(self.ganttChart, 1, wx.GROW|wx.ALL, 5)
		self.SetSizer(bs)
		bs.SetSizeHints(self)

	def onExcel( self, event ):
		results = self.getResults()
		if not results:
			return

		fileName = Utils.getFileName() or 'test.cmn'
		xlFName = os.path.splitext(fileName)[0] + '-Unmatched-RFID-Tags.xls'
		with wx.DirDialog( self, '{} "{}"'.format(_('Folder to write'), os.path.basename(xlFName)),
						style=wx.DD_DEFAULT_STYLE, defaultPath=os.path.dirname(xlFName) ) as dlg:
			if dlg.ShowModal()!= wx.ID_OK:
				return
			dName = dlg.GetPath()

		xlFName = os.path.join( dName, os.path.basename(xlFName) )
		
		wb = xlwt.Workbook()
		sheetCur = wb.add_sheet( 'Unmatched RFID Tags' )
		
		headerStyle = xlwt.XFStyle()
		headerStyle.borders.bottom = xlwt.Borders.MEDIUM
		headerStyle.font.bold = True

		sheetFit = FitSheetWrapper( sheetCur )

		sheetFit.write( 0, 0, _('Tag'), headerStyle, bold=True )
		for col, t in enumerate(results[0][1], 1):
			sheetFit.write( 0, col, '{} {}'.format(_('Time'), col), headerStyle, bold=True )
		
		for rowTop, (tag, times) in enumerate(self.getResults(), 1):
			sheetFit.write( rowTop, 0, tag )
			for col, t in enumerate(times, 1):
				sheetFit.write( rowTop, col,
					Utils.formatTime(
						t, extraPrecision=True, forceHours=True, twoDigitHours=True,
					)
				)
		
		try:
			wb.save( xlFName )
			Utils.LaunchApplication( xlFName )
			Utils.MessageOK(self, '{}:\n\n   {}'.format(_('Excel file written to'), xlFName), _('Excel Write'))
		except IOError:
			Utils.MessageOK(self,
						'{} "{}"\n\n{}\n{}'.format(
							_('Cannot write'), xlFName,
							_('Check if this spreadsheet is already open.'),
							_('If so, close it, and try again.')
						),
						_('Excel File Error'), iconMask=wx.ICON_ERROR )		

	def getResults( self ):
		race = Model.race
		return sorted(
			((tag, times) for tag, times in race.unmatchedTags.items()),
			key = lambda tt: (-len(tt[1]), tt[1][-1]),
		) if race and race.unmatchedTags else []

	def refresh( self ):
		results = self.getResults()
		if not results:
			self.ganttChart.SetData( None )
			return
		
		race = Model.race
		labels  = [tag for tag, times in results]
		data	= [times for tag, times in results]
		try:
			nowTime = race.lastRaceTime()
		except Exception:
			nowTime = None
		self.ganttChart.SetData( data, labels, nowTime )
	
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	race = Model.race
	race.unmatchedTags = {
		'ABC345345': [100,200,300,400,500,600],
		'AEDFA5345': [100,200,300,400,500,600],
		'A09809809': [100,200,300,400,500,600],
	}
	gantt = UnmatchedTagsGantt(mainWin)
	gantt.refresh()
	mainWin.Show()
	app.MainLoop()


