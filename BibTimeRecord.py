import wx
import wx.grid			as gridlib
import wx.lib.buttons

import Model
import Utils
from ReorderableGrid import ReorderableGrid
from EditEntry import DoDNF, DoDNS, DoPull, DoDQ
from InputUtils import enterCodes, validKeyCodes, clearCodes, actionCodes, getRiderNumsFromText, MakeKeypadButton

class BibTimeRecord( wx.Panel ):
	def __init__( self, parent, controller, id = wx.ID_ANY ):
		super().__init__(parent, id)
		# self.SetBackgroundColour( wx.Colour(173, 216, 230) )
		self.SetBackgroundColour( wx.WHITE )

		self.controller = controller
		
		fontPixels = 36
		font = wx.Font((0,fontPixels), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		dc = wx.WindowDC( self )
		dc.SetFont( font )
		wNum, hNum = dc.GetTextExtent( '999' )
		wNum += 8
		hNum += 8		

		outsideBorder = 4

		vsizer = wx.BoxSizer( wx.VERTICAL )
		
		self.numEditHS = wx.BoxSizer( wx.HORIZONTAL )
		
		self.numEditLabel = wx.StaticText(self, label='{} \u23F1'.format(_('Bib')))
		self.numEditLabel.SetFont( font )
		
		editWidth = 140
		self.numEdit = wx.TextCtrl( self, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER,
							size=(editWidth, int(fontPixels*1.2)) if 'WXMAC' in wx.Platform else (editWidth,-1) )
		self.numEdit.Bind( wx.EVT_CHAR, self.handleNumKeypress )
		self.numEdit.SetFont( font )
		
		self.numEditHS.Add( self.numEditLabel, wx.ALIGN_CENTRE | wx.ALIGN_CENTRE_VERTICAL )
		self.numEditHS.Add( self.numEdit, flag=wx.LEFT|wx.EXPAND, border = 4 )
		vsizer.Add( self.numEditHS, flag=wx.EXPAND|wx.LEFT|wx.TOP, border = outsideBorder )

		font = wx.Font((0,int(fontPixels*.6)), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		
		hbs = wx.GridSizer( 2, 2, 4, 4 )
		for label, actionFn in [(_('DN&F'),DoDNF), (_('DN&S'),DoDNS), (_('&Pull'),DoPull), (_('D&Q'),DoDQ)]:
			btn = MakeKeypadButton( self, label=label, style=wx.EXPAND|wx.GROW, font = font)
			btn.Bind( wx.EVT_BUTTON, lambda event, fn = actionFn: self.doAction(fn) )
			hbs.Add( btn, flag=wx.EXPAND )
		
		vsizer.Add( hbs, flag=wx.EXPAND|wx.TOP, border=4 )
		
		fontSize = 18
		self.font = wx.Font( (0,fontSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		self.bigFont = wx.Font( (0,int(fontSize*1.30)), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		
		inputExplain = wx.StaticText( self, label=_('Enter Bibs first, then click on them to record times.') )
		inputExplain.SetFont( self.font )

		vsizer.Add( inputExplain, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.headerNames = ('   {}   '.format(_('Bib')),)
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.SetFont( self.font )
		self.grid.EnableReorderRows( False )
		self.grid.DisableDragColSize()
		self.grid.DisableDragRowSize()

		dc = wx.WindowDC( self.grid )
		dc.SetFont( self.font )
		width, height = dc.GetTextExtent(' 999 ')
		self.rowLabelSize = width
		self.grid.SetRowLabelSize( self.rowLabelSize )
		
		self.grid.CreateGrid( 0, len(self.headerNames) )
		self.grid.Bind( gridlib.EVT_GRID_CELL_LEFT_CLICK, self.doSetTime )
		self.grid.Bind( gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.doPopup )

		for col, name in enumerate(self.headerNames):
			self.grid.SetColLabelValue( col, name )
		self.grid.SetLabelFont( self.font )
		for col in range(self.grid.GetNumberCols()):
			attr = gridlib.GridCellAttr()
			attr.SetFont( self.font )
			attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_CENTRE )
			attr.SetReadOnly( True )
			self.grid.SetColAttr( col, attr )
		
		vsizer.Add( self.grid, 1, flag=wx.ALL|wx.EXPAND, border = 4 )
				
		self.SetSizerAndFit(vsizer)
		
	def handleNumKeypress(self, event):
		keycode = event.GetKeyCode()
		if keycode in enterCodes:
			self.onEnterPress()
		elif keycode in clearCodes:
			self.numEdit.SetValue( '' )
		elif keycode in actionCodes:
			pass
		elif keycode < 255:
			if keycode in validKeyCodes:
				event.Skip()
			else:
				Utils.writeLog( 'handleNumKeypress: ignoring keycode < 255: {}'.format(keycode) )
		else:
			Utils.writeLog( 'handleNumKeypress: ignoring keycode: >= 255 {}'.format(keycode) )
			event.Skip()
	
	def onEnterPress( self, event = None ):
		race = Model.race
		if race and race.isRunning():
			nums = getRiderNumsFromText( self.numEdit.GetValue() )
			with gridlib.GridUpdateLocker(self.grid):
				Utils.AdjustGridSize( self.grid, rowsRequired=self.grid.GetNumberRows() + len(nums) )
				for iRow, num in enumerate(nums, self.grid.GetNumberRows() - len(nums)):
					self.grid.SetCellValue( iRow, 0, str(num) )
				self.grid.AutoSize()
		wx.CallAfter( self.numEdit.SetValue, '' )
	
	def doSetTime( self, event ):
		race = Model.race
		t = race.curRaceTime() if race and race.isRunning() else None
		row = event.GetRow()
		num = self.grid.GetCellValue( row, 0 ) if row < self.grid.GetNumberRows() else ''
		if t is not None and num:
			mainWin = Utils.getMainWin()
			if mainWin is not None:
				mainWin.forecastHistory.logNum( int(num) )
			if self.controller:
				self.controller.refreshLaps()
		if row < self.grid.GetNumberRows():
			self.grid.DeleteRows( row, 1 )
	
	def doAction( self, action ):
		race = Model.race
		t = race.curRaceTime() if race and race.isRunning() else None
		success = False
		for num in getRiderNumsFromText( self.numEdit.GetValue() ):
			if action(self, num, t):
				success = True
		if success:
			self.numEdit.SetValue( '' )
			self.refresh()
			wx.CallAfter( Utils.refreshForecastHistory )
	
	def Layout( self ):
		self.GetSizer().Layout()
		
	def refresh( self ):
		valuesToKeep = []
		
		race = Model.race
		Finisher = Model.Rider.Finisher
		raceIsValid = (race and race.isRunning())
		if raceIsValid:
			for r in range(self.grid.GetNumberRows()):
				value = self.grid.GetCellValue(r, 0)
				try:
					bib = int(value)
				except Exception:
					continue
				if race.getRider(bib).status == Finisher:
					valuesToKeep.append( value )
		else:
			self.numEdit.SetValue( '' )
				
		if self.grid.GetNumberRows() != len(valuesToKeep):
			with gridlib.GridUpdateLocker(self.grid):
				Utils.AdjustGridSize( self.grid, rowsRequired=len(valuesToKeep) )
				for row, value in enumerate(valuesToKeep):
					self.grid.SetCellValue( row, 0, value )
		
	def commit( self ):
		pass
	
	def getBib( self, event ):
		r = event.GetRow()
		if r >= self.grid.GetNumberRows():
			return None
		try:
			return int(self.grid.GetCellValue(r, 0))
		except Exception:
			return None
		
	def doPopup( self, event ):
		if not hasattr(self, 'bibTimePopupInfo'):
			self.bibTimePopupInfo = [
				('{}...'.format(_('Delete')),	self.OnPopupDelete),
				(None,							None),
				('{}...'.format(_('DNF')),		self.OnPopupDNF),
				('{}...'.format(_('Pull')),		self.OnPopupPull),
				(None,							None),
				(_('RiderDetail'),				self.OnPopupRiderDetail),
				(_('Results'),					self.OnPopupResults),
				(_('Passings'),					self.OnPopupPassings),
				(_('Chart'),					self.OnPopupChart),
			]

			menu = wx.Menu()
			for name, callback in self.bibTimePopupInfo:
				if name:
					item = menu.Append( wx.ID_ANY, name )
					self.Bind( wx.EVT_MENU, callback, item )
				else:
					menu.AppendSeparator()
			self.menu = menu
		
		self.rowCur = event.GetRow()
		self.bibCur = self.getBib( event )
		if self.bibCur is not None:
			self.PopupMenu( self.menu )
			self.refresh()
		
	def OnPopupDelete( self, event ):
		self.grid.SetCellValue( self.rowCur, 0, '' )
		self.refresh()
		
	def OnPopupDNF( self, event ):
		try:
			DoDNF( self, self.bibCur )
		except Exception:
			pass
		
	def OnPopupPull( self, event ):
		try:
			DoPull( self, self.bibCur )
		except Exception:
			pass

	def OnPopupRiderDetail( self, event ):
		mainWin = Utils.getMainWin()
		if self.bibCur and mainWin:
			mainWin.forecastHistory.SelectNumShowPage( self.bibCur, 'iRiderDetailPage' )
	
	def OnPopupResults( self, event ):
		mainWin = Utils.getMainWin()
		if self.bibCur and mainWin:
			mainWin.forecastHistory.SelectNumShowPage( self.bibCur, 'iResultsPage' )
	
	def OnPopupPassings( self, event ):
		mainWin = Utils.getMainWin()
		if self.bibCur and mainWin:
			mainWin.forecastHistory.SelectNumShowPage( self.bibCur, 'iPassingsPage' )
				
	def OnPopupChart( self, event ):
		mainWin = Utils.getMainWin()
		if self.bibCur and mainWin:
			mainWin.forecastHistory.SelectNumShowPage( self.bibCur, 'iChartPage' )
	
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,600))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	bibTimeRecord = BibTimeRecord(mainWin, None)
	bibTimeRecord.refresh()
	mainWin.Show()
	app.MainLoop()
