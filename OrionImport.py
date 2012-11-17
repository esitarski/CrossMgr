import Model
import Utils
import JChip
from JChipSetup import GetTagNums
from Utils		import logCall
from Undo		import undo
import wx
import wx.lib.intctrl
import wx.lib.masked			as masked
import wx.lib.mixins.listctrl	as  listmix
import wx.lib.rcsizer			as rcs
import socket
import sys
import os
import datetime

class parseTagTime( object ):
	def __init__( self, raceDate ):
		self.raceDate = raceDate

	def __call__( self, line, lineNo, errors ):
		try:
			fields = line.split(';' if ';' in line else ',')
			msg = fields[0]
			if msg != '$P':
				None, None
			tag = fields[2]
			tStr = fields[5]
		except IndexError:
			errors.append( 'line %d: unrecognized input' % lineNo )
			return None, None
		
		try:
			secs = int(tStr) / 1000.0	# Convert from 1000's of a second.
		except ValueError:
			errors.append( 'line %d: invalid time' % lineNo )
			return None, None
		else:
			t = datetime.datetime.combine( self.raceDate, datetime.time() ) + datetime.timedelta( seconds = secs )
			
		return tag, t

def DoOrionImport( fname, startTime = None ):
	# If startTime is None, the first time will be taken as the start time.
	# All first time's for each rider will then be ignored.
	
	errors = []
	raceStart = None
	
	with open(fname) as f, Model.LockRace() as race:
		year, month, day = [int(n) for n in race.date.split('-')]
		raceDate = datetime.date( year=year, month=month, day=day )
		JChip.dateToday = raceDate
		if startTime:
			raceStart = datetime.datetime.combine( raceDate, startTime )
			race.resetStartClockOnFirstTag = False
		else:
			race.resetStartClockOnFirstTag = True
		
		tagNums = GetTagNums( True )
		race.missingTags = set()
		
		tFirst, tLast = None, None
		lineNo = 0
		riderRaceTimes = {}
		for line in f:
			lineNo += 1
			
			if line.startswith('#'):
				continue
			
			try:
				fields = line.split(';' if ';' in line else ',')
				msg = fields[0]
				if msg != '$P':
					continue
				tag = fields[2]
				tStr = fields[5]
			except IndexError:
				errors.append( 'line %d: unrecognized input' % lineNo )
				continue
			
			try:
				secs = int(tStr) / 1000.0	# Convert from 1000's of a second.
			except ValueError:
				errors.append( 'line %d: invalid time' % lineNo )
				continue
			else:
				t = datetime.datetime.combine( raceDate, datetime.time() ) + datetime.timedelta( seconds = secs )
				
			if raceStart and t < raceStart:
				errors.append( 'line %d: time before race start (%s)' % (lineNo, tStr) )
				continue
				
			if not tFirst:
				tFirst = t
			tLast = t
			try:
				num = tagNums[tag]
				riderRaceTimes.setdefault( num, [] ).append( t )
			except KeyError:
				if tag not in race.missingTags:
					errors.append( 'line %d: tag %s missing from Excel sheet' % (lineNo, tag) )
					race.missingTags.add( tag )
				continue

		#------------------------------------------------------------------------------
		# Populate the race with the times.
		if not riderRaceTimes:
			errors.insert( 0, 'No matching tags found in Excel link.  Import aborted.' )
			return errors
		
		race.clearAllRiderTimes()
		
		if not raceStart:
			raceStart = tFirst
			
		race.startTime = raceStart
		
		# Put all the rider times into the race.
		for num, lapTimes in riderRaceTimes.iteritems():
			for t in lapTimes:
				raceTime = (t - raceStart).total_seconds()
				race.addTime( num, raceTime )
		
		if tLast:
			race.finishTime = tLast
			
		# Figure out the race minutes from the recorded laps.
		if riderRaceTimes:
			lapNumMax = max( len(ts) for ts in riderRaceTimes.itervalues() )
			if lapNumMax > 0:
				tElapsed = min( ts[-1] for ts in riderRaceTimes.itervalues() if len(ts) == lapNumMax )
				raceMinutes = int((tElapsed - raceStart).total_seconds() / 60.0) + 1
				race.minutes = raceMinutes
		
		race.setChanged()
	return errors

#------------------------------------------------------------------------------------------------
class OrionImportDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Orion Import",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
		
		todoList = [
			'Import Orion Data File',
			'',
			'You must first "New" a race and fill in the details.',
			'You must also configure a "Tag" field in your Sign-On Excel Sheet and link it to the race.',
			'This is required so CrossMgr can link the tags in the Orion file back to rider numbers and info.',
			'',
			'Race Data:',
			'If the first chip read is NOT the start of the race, you will need to enter the start time manually.',
			'Otherwise the import will use the first chip read as the race start.',
			'',
			'TimeTrial Data:',
			"The first chip read for each rider will be interpreted as the rider's start time.",
			'',
			'Warning: Importing from Orion will replace all the data in this race.',
			'Proceed with caution.',
		]
		intro = '\n'.join(todoList)
		
		gs = wx.FlexGridSizer( rows=3, cols=3, vgap=5, hgap=5 )
		gs.Add( wx.StaticText(self, wx.ID_ANY, 'Orion Data File:'), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.orionDataFile = wx.TextCtrl( self, -1, '', size=(450,-1) )
		defaultPath = Utils.getFileName()
		if not defaultPath:
			defaultPath = Utils.getDocumentsDir()
		else:
			defaultPath = os.path.join( os.path.split(defaultPath)[0], '' )
		self.orionDataFile.SetValue( defaultPath )
		gs.Add( self.orionDataFile, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW)

		btn = wx.Button( self, wx.ID_ANY, label='Browse...' )
		btn.Bind( wx.EVT_BUTTON, self.onBrowseOrionDataFile )
		gs.Add( btn, 0, wx.ALIGN_CENTER_VERTICAL )
		
		gs.AddSpacer(1)
		self.dataType = wx.StaticText( self, wx.ID_ANY, "Data Is:" )
		gs.Add( self.dataType, 1, wx.ALIGN_LEFT )
		gs.AddSpacer(1)
        
		self.manualStartTime = wx.CheckBox(self, wx.ID_ANY, 'Race Start Time (if NOT first recorded time):' )
		self.Bind( wx.EVT_CHECKBOX, self.onChangeManualStartTime, self.manualStartTime )
		gs.Add( self.manualStartTime, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.raceStartTime = masked.TimeCtrl( self, wx.ID_ANY, fmt24hr=True, value="10:00:00" )
		self.raceStartTime.Enable( False )
		gs.Add( self.raceStartTime, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW)
		
		with Model.LockRace() as race:
			isTimeTrial = getattr(race, 'isTimeTrial', False) if race else False

		if isTimeTrial:
			self.manualStartTime.Enable( False )
			self.manualStartTime.Show( False )
			self.raceStartTime.Enable( False )
			self.raceStartTime.Show( False )
			self.dataType.SetLabel( 'Data will be imported for a Time Trial' )
		else:
			self.dataType.SetLabel( 'Data will be imported for a Race' )
			
		self.okBtn = wx.Button( self, wx.ID_OK, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		bs = wx.BoxSizer( wx.VERTICAL )
		
		border = 4
		bs.Add( wx.StaticText(self, -1, intro), 0, wx.EXPAND|wx.ALL, border )
		
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

	def onChangeManualStartTime( self, event ):
		self.raceStartTime.Enable( event.IsChecked() )
		
	def onBrowseOrionDataFile( self, event ):
		defaultPath = self.orionDataFile.GetValue()
		if not defaultPath:
			defaultPath = Utils.getFileName()
			if defaultPath:
				defaultPath = os.path.split(defaultPath)[0]
			else:
				defaultPath = Utils.getDocumentsDir()
			defaultFile = ''
		else:
			defaultPath, defaultFile = os.path.split(defaultPath)
			
		dlg = wx.FileDialog( self, "Choose a Orion file",
							style=wx.OPEN | wx.CHANGE_DIR,
							wildcard="Orion Data (*.txt *.csv)|*.txt;*.csv",
							defaultDir=defaultPath if defaultPath else '',
							defaultFile=defaultFile if defaultFile else '',
							)
		if dlg.ShowModal() == wx.ID_OK:
			self.orionDataFile.SetValue( dlg.GetPath() )
		dlg.Destroy()		
	
	def onOK( self, event ):
		fname = self.orionDataFile.GetValue()
		try:
			with open(fname) as f:
				pass
		except IOError:
			Utils.MessageOK( self, 'Could not open Orion data file for import:\n\n"%s"' % fname,
									title = 'Cannot Open File', iconMask = wx.ICON_ERROR)
			return
			
		if self.manualStartTime.IsChecked():
			startTime = datetime.time(*[int(x) for x in self.raceStartTime.GetValue().split(':')])
		else:
			startTime = None
		
		undo.pushState()
		errors = DoOrionImport( fname, startTime )
		
		if errors:
			# Copy the tags to the clipboard.
			clipboard = wx.Clipboard.Get()
			if not clipboard.IsOpened():
				clipboard.Open()
				clipboard.SetData( wx.TextDataObject('\n'.join(errors)) )
				clipboard.Close()
			
			if len(errors) > 10:
				errors = errors[:10]
				errors.append( '...' )
			tagStr = '\n'.join(errors)
			Utils.MessageOK( self,
							'Orion Import File contains errors:\n\n%s\n\nAll errors have been copied to the clipboard.' % tagStr,
							'Orion Import Warning',
							iconMask = wx.ICON_WARNING )
		else:
			Utils.MessageOK( self, 'Orion Import Successful', 'Orion Import Successful' )
		wx.CallAfter( Utils.refresh )
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	Model.setRace( Model.Race() )
	mainWin.Show()
	dlg = OrionImportDialog( mainWin )
	dlg.ShowModal()
	dlg.Destroy()

