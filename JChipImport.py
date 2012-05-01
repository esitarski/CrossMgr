import Model
import Utils
import JChip
from JChipSetup import GetTagNums
from Utils				import logCall
import wx
import wx.lib.intctrl
import wx.lib.masked           as masked
import  wx.lib.mixins.listctrl  as  listmix
import  wx.lib.rcsizer  as rcs
import socket
import sys
import os
import datetime

def DoJchipImport( fname, startTime ):
	missingTags = []
	missingTagSet = set()
	
	with open(fname) as f, Model.LockRace() as race:
		race.deleteAllRiderTimes()
		
		year, month, day = [int(n) for n in race.date.split('-')]
		raceDate = datetime.date( year=year, month=month, day=day )
		raceStart = datetime.datetime.combine( raceDate, startTime )
		race.startTime = raceStart
		tagNums = GetTagNums( True )
		
		tLast = None
		for line in f:
			try:
				fields = line.split()
				tag = fields[0][1:]
				tStr = fields[1]
			except IndexError:
				continue
			
			t = datetime.datetime.combine( raceDate, JChip.parseTime(tStr) )
			if t < raceStart:
				continue
			tLast = t
			lapTime = (t - raceStart).total_seconds()
			try:
				num = tagNums[tag]
				race.importTime( num, lapTime )
			except KeyError:
				if tag not in missingTagSet:
					missingTags.append( tag )
					missingTagSet.add( tag )
				continue
		
		if tLast:
			race.finishTime = tLast
		race.setChanged()
	return missingTags

#------------------------------------------------------------------------------------------------
class JChipImportDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "JChip Import",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
		
		
		
		gs = wx.FlexGridSizer( rows=2, cols=3, vgap = 5, hgap = 5 )
		gs.Add( wx.StaticText(self, -1, 'JChip Data File:'), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.jchipDataFile = wx.TextCtrl( self, -1, '', size=(400,-1) )
		self.jchipDataFile.SetValue( Utils.getDocumentsDir() )
		gs.Add( self.jchipDataFile, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW)

		btn = wx.Button( self, 10, label='Browse...' )
		btn.Bind( wx.EVT_BUTTON, self.onBrowseJChipDataFile )
		gs.Add( btn, 0, wx.ALIGN_CENTER_VERTICAL )
		
		gs.Add( wx.StaticText(self, -1, 'Actual Race Start Time (HH:MM:SS):'), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.raceStartTime = masked.TimeCtrl( self, -1, fmt24hr=True, value="10:00:00" )
		gs.Add( self.raceStartTime, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW)
		
		self.okBtn = wx.Button( self, wx.ID_OK, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		bs = wx.BoxSizer( wx.VERTICAL )
		
		border = 4
		
		#-------------------------------------------------------------------
		bs.AddSpacer( border )
		
		bs.Add( gs, 0, wx.EXPAND | wx.ALL, border )
		
		buttonBox = wx.BoxSizer( wx.HORIZONTAL )
		buttonBox.AddStretchSpacer()
		buttonBox.Add( self.okBtn, flag = wx.RIGHT, border = border )
		self.okBtn.SetDefault()
		buttonBox.Add( self.cancelBtn )
		bs.Add( buttonBox, 0, wx.EXPAND | wx.ALL, border )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onBrowseJChipDataFile( self, event ):
		defaultPath = self.jchipDataFile.GetValue()
		if not defaultPath:
			defaultPath = Utils.getDocumentsDir()
			defaultFile = ''
		else:
			defaultPath, defaultFile = os.path.split(defaultPath)
			
		dlg = wx.FileDialog( self, "Choose a JChip file",
							style=wx.OPEN | wx.CHANGE_DIR,
							wildcard="JChip Data (*.txt)|*.txt",
							defaultDir=defaultPath if defaultPath else '',
							defaultFile=defaultFile if defaultFile else '',
							)
		if dlg.ShowModal() == wx.ID_OK:
			self.jchipDataFile.SetValue( dlg.GetPath() )
		dlg.Destroy()		
	
	def onOK( self, event ):
		fname = self.jchipDataFile.GetValue()
		try:
			with open(fname) as f:
				pass
		except IOError:
			Utils.MessageOK( self, 'Could not open JChip data file for import:\n\n"%s"' % fname,
									title = 'Cannot Open File', iconMask = wx.ICON_ERROR)
			return
		startStr = self.raceStartTime.GetValue()
		hh, mm, ss = [int(x) for x in startStr.split(':')]
		missingTags = DoJchipImport( fname, datetime.time(hh, mm, ss) )
		if missingTags:
			tags = []
			for i in xrange(0, len(missingTags), 8):
				tags.append( ', '.join(missingTags[i:min(len(missingTags), i+8)]) )
			tagStr = '\n'.join(tags)
			Utils.MessageOK( self, 'JChip Import File contains tags not defined in the Excel sheet:\n\n%s' % tagStr, 'JChip Import Warning', iconMask = wx.ICON_WARNING )
		else:
			Utils.MessageOK( self, 'JChip Import Successful', 'JChip Import Successful' )
		wx.CallAfter( Utils.refresh )
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	dlg = JChipImportDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

