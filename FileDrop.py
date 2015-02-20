import wx
import os
import Utils
from ReadSignOnSheet	import IsValidRaceDBExcel

class FileDrop(wx.FileDropTarget):
	def __init__( self ):
		wx.FileDropTarget.__init__(self)

	def OnDropFiles(self, x, y, filenames):
		if len(filenames) != 1:
			return
		
		fname = filenames[0]
		mainWin = Utils.getMainWin()
		if not mainWin:
			return
		
		ext = os.path.splitext( fname )[1]
		if ext == '.cmn':
			mainWin.openRace( fname )
		elif ext in ('.xls', '.xlsx', '.xlsm'):
			if IsValidRaceDBExcel(fname):
				mainWin.openRaceDBExcel( fname )