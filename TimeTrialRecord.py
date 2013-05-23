import wx
import wx.grid			as gridlib
from wx.lib import masked
import math
import Model
import Utils
from ReorderableGrid import ReorderableGrid
from HighPrecisionTimeEdit import HighPrecisionTimeEdit

def formatTime( secs ):
	if secs is None:
		secs = 0
	if secs < 0:
		sign = '-'
		secs = -secs
	else:
		sign = ''
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = int(secs // (60*60))
	minutes = int( (secs // 60) % 60 )
	secs = secs % 60
	decimal = '.%03d' % int( f * 1000 )
	return " %s%02d:%02d:%02d%s " % (sign, hours, minutes, secs, decimal)

class HighPrecisionTimeEditor(gridlib.PyGridCellEditor):
	def __init__(self):
		self._tc = None
		self.startValue = '00:00:00.000'
		gridlib.PyGridCellEditor.__init__(self)
		
	def Create( self, parent, id, evtHandler ):
		self._tc = HighPrecisionTimeEdit(parent, id, allow_none = False)
		self.SetControl( self._tc )
		if evtHandler:
			self._tc.PushEventHandler( evtHandler )
	
	def SetSize( self, rect ):
		self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2, wx.SIZE_ALLOW_MINUS_ONE )
	
	def BeginEdit( self, row, col, grid ):
		self.startValue = grid.GetTable().GetValue(row, col).strip()
		self._tc.SetValue( self.startValue )
		self._tc.SetFocus()
		
	def EndEdit( self, row, col, grid ):
		changed = False
		val = self._tc.GetValue()
		if val != self.startValue:
			change = True
			grid.GetTable().SetValue( row, col, int(val) )
		self.startValue = '00:00:00.000'
		self._tc.SetValue( self.startValue )
		
	def Reset( self ):
		self._tc.SetValue( self.startValue )
		
	def Clone( self ):
		return HighPrecisionTimeEditor()

class BibEditor(gridlib.PyGridCellEditor):
	def __init__(self):
		self._tc = None
		self.startValue = ''
		gridlib.PyGridCellEditor.__init__(self)
		
	def Create( self, parent, id, evtHandler ):
		self._tc = masked.NumCtrl( parent, id, style = wx.TE_PROCESS_ENTER  )
		self._tc.SetAllowNone( True )
		self.SetControl( self._tc )
		if evtHandler:
			self._tc.PushEventHandler( evtHandler )
	
	def SetSize( self, rect ):
		self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2, wx.SIZE_ALLOW_MINUS_ONE )
	
	def BeginEdit( self, row, col, grid ):
		self.startValue = int(grid.GetTable().GetValue(row, col).strip() or 0)
		self._tc.SetValue( self.startValue )
		self._tc.SetFocus()
		
	def EndEdit( self, row, col, grid ):
		changed = False
		val = self._tc.GetValue()
		if not val:
			val = ''
		else:
			val = str(val)
		if val != str(self.startValue):
			change = True
			grid.GetTable().SetValue( row, col, val )
		self._tc.SetValue( self.startValue )
		
	def Reset( self ):
		self._tc.SetValue( self.startValue )
		
	def Clone( self ):
		return BibEditor()
		
class TimeTrialRecord( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)

		self.headerNames = ['Time', 'Bib']
		
		self.maxRows = 10
		
		self.font = wx.FontFromPixelSize( wx.Size(0,16), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )
		self.vbs = wx.BoxSizer(wx.VERTICAL)
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.SetFont( self.font )
		self.grid.EnableReorderRows( False )
		self.grid.SetRowLabelSize( 0 )
		self.grid.CreateGrid( self.maxRows, len(self.headerNames) )
		for col, name in enumerate(self.headerNames):
			self.grid.SetColLabelValue( col, name )
		self.grid.SetLabelFont( self.font )
		for col in xrange(self.grid.GetNumberCols()):
			attr = gridlib.GridCellAttr()
			attr.SetFont( self.font )
			if col == 0:
				attr.SetEditor( HighPrecisionTimeEditor() )
			elif col == 1:
				attr.SetRenderer( gridlib.GridCellNumberRenderer() )
				attr.SetEditor( BibEditor() )
			self.grid.SetColAttr( col, attr )
		
		self.vbs.Add( self.grid, 1, flag=wx.ALL|wx.EXPAND, border = 4 )
		
		hbs = wx.BoxSizer( wx.HORIZONTAL )
		
		self.recordTimeButton = wx.Button( self, wx.ID_ANY, 'Record Time' )
		self.recordTimeButton.Bind( wx.EVT_BUTTON, self.doRecordTime )
		self.recordTimeButton.SetFont( self.font )
		self.commitButton = wx.Button( self, wx.ID_ANY, 'Commit' )
		self.commitButton.Bind( wx.EVT_BUTTON, self.doCommit )
		self.commitButton.SetFont( self.font )
		
		hbs.Add( self.recordTimeButton, flag=wx.ALL, border = 4 )
		hbs.Add( self.commitButton, flag=wx.ALL, border = 4 )
		
		self.vbs.Add( hbs, 0, flag=wx.ALL, border = 4 )
		
		self.SetSizer(self.vbs)
	
	def doRecordTime( self, event ):
		t = Model.race.curRaceTime()
		
		if not Model.race:
			return
			
		# Trigger the camera.
		pass
	
		# Find the last row without a time.
		self.grid.SaveEditControlValue()
		
		emptyRow = 0
		success = False
		for i in xrange(2):
			for row in xrange(self.grid.GetNumberRows()-1, -1, -1):
				if self.grid.GetCellValue(row, 0):
					emptyRow = row + 1
					break
			if emptyRow > self.grid.GetNumberRows():
				self.doCommit( event )
			else:
				success = True
				break
		
		if not success:
			Utils.MessageOK( self, 'Insufficient space to Record Time.\nEnter Bib numbers and press Commit.\nOr delete some entries', 'Record Time Failed.' )
			return
			
		self.grid.SetCellValue( emptyRow, 0, formatTime(t) )
		self.grid.SetCellValue( emptyRow, 1, '' )
		
		# Set the edit cursor at the first empty bib position.
		for row in xrange(self.grid.GetNumberRows()):
			text = self.grid.GetCellValue(row, 1)
			if not text or text == '0':
				self.grid.SetGridCursor( row, 1 )
				break
		
	def doCommit( self, event ):
		timesBibs = []
		timesNoBibs = []
		for row in xrange(self.grid.GetNumberRows()):
			t = self.grid.GetCellValue(row, 0).strip()
			bib = self.grid.GetCellValue(row, 1).strip()
			if not t:
				continue
			if bib:
				timesBibs.append( (t, bib) )
			else:
				timesNoBibs.append( t )
				
		for row in xrange(self.grid.GetNumberRows()):
			for column in xrange(self.grid.GetNumberCols()):
				self.grid.SetCellValue(row, column, '' )
			
		for row, t in enumerate(timesNoBibs):
			self.grid.SetCellValue( row, 0, t )
		self.grid.SetGridCursor( 0, 1 )
			
		if timesBibs:
			with Model.LockRace() as race:
				for t, bib in timesBibs:
					race.addTime( bib, Utils.StrToSeconds(t) )
			Utils.refresh()
	
	def refresh( self ):
		self.grid.AutoSizeRows( False )
		
		dc = wx.WindowDC( self.grid )
		dc.SetFont( self.font )
		
		width, height = dc.GetTextExtent(" 00:00:00.000 ")
		self.grid.SetColSize( 0, width )
		
		width, height = dc.GetTextExtent(" 9999 ")
		self.grid.SetColSize( 1, width )
		
		self.grid.ForceRefresh()
		
	def commit( self ):
		pass
		
if __name__ == '__main__':
	Utils.disable_stdout_buffering()
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,600))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	timeTrialRecord = TimeTrialRecord(mainWin)
	timeTrialRecord.refresh()
	mainWin.Show()
	app.MainLoop()
