import Utils
import Model
from Undo import undo
import wx
import re
import os
import wx.lib.intctrl as intctrl
import wx.lib.masked as masked

class Properties( wx.Panel ):
	badFileCharsRE = re.compile( '[^a-zA-Z0-9_ ]+' )
	dateFormat = '%Y-%m-%d'

	def __init__( self, parent, id = wx.ID_ANY, addEditButton = True ):
		wx.Panel.__init__(self, parent, id)

		rows = 0
		
		self.raceNameLabel = wx.StaticText( self, wx.ID_ANY, _('Race Name:') )
		self.raceName = wx.TextCtrl( self, wx.ID_ANY, value='' )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceName )
		rows += 1
		
		self.dateLabel = wx.StaticText( self, wx.ID_ANY, _('Date:') )
		self.date = wx.DatePickerCtrl( self, wx.ID_ANY, style = wx.DP_DROPDOWN )
		self.Bind(wx.EVT_DATE_CHANGED, self.onChanged, self.date)
		rows += 1
		
		self.raceNumLabel = wx.StaticText( self, wx.ID_ANY, _('Race #:') )
		self.raceNum = intctrl.IntCtrl( self, wx.ID_ANY, min=1, max=1000, allow_none=False, value=1 )
		self.Bind(intctrl.EVT_INT, self.onChanged, self.raceNum)
		rows += 1
		
		self.scheduledStartLabel = wx.StaticText( self, wx.ID_ANY, _('Scheduled Start:') )
		self.scheduledStart = masked.TimeCtrl( self, wx.ID_ANY, fmt24hr=True, display_seconds=False, value='10:00:00' )
		rows += 1

		self.minutesLabel = wx.StaticText( self, wx.ID_ANY, _('Race Minutes:') )
		self.minutes = intctrl.IntCtrl( self, wx.ID_ANY, min=1, max=60*12, allow_none=False, value=40 )
		rows += 1

		self.raceDisciplineLabel = wx.StaticText( self, wx.ID_ANY, _('Discipline:') )
		self.raceDiscipline = wx.TextCtrl( self, wx.ID_ANY, value='' )
		self.raceDiscipline.SetValue( 'Cyclo-cross' )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceDiscipline )
		rows += 1
		
		self.organizerLabel = wx.StaticText( self, wx.ID_ANY, _('Organizer:') )
		self.organizer = wx.TextCtrl( self, wx.ID_ANY, value='' )
		rows += 1
		
		self.commissaireLabel = wx.StaticText( self, wx.ID_ANY, _('Commissaire:') )
		self.commissaire = wx.TextCtrl( self, wx.ID_ANY, value='' )
		rows += 1
		
		self.memoLabel = wx.StaticText( self, wx.ID_ANY, _('Memo:') )
		self.memo = wx.TextCtrl( self, wx.ID_ANY, value='' )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.memo )
		rows += 1
		
		self.allCategoriesFinishAfterFastestRidersLastLapLabel = wx.StaticText( self, wx.ID_ANY, _("All Categories Finish After Fastest Rider's Last Lap:") )
		self.allCategoriesFinishAfterFastestRidersLastLap = wx.CheckBox( self, wx.ID_ANY, style=wx.ALIGN_LEFT )
		self.allCategoriesFinishAfterFastestRidersLastLap.SetValue( True )
		rows += 1
		
		self.timeTrialLabel = wx.StaticText( self, wx.ID_ANY, _('Time Trial:') )
		self.timeTrial = wx.CheckBox( self, wx.ID_ANY, style=wx.ALIGN_LEFT )
		rows += 1
		
		self.distanceUnitLabel = wx.StaticText( self, wx.ID_ANY, _('Distance Unit: ') )
		self.distanceUnit = wx.Choice( self, wx.ID_ANY, choices=['km', 'miles'] )
		self.distanceUnit.SetSelection( 0 )
		rows += 1

		self.highPrecisionTimesLabel = wx.StaticText( self, wx.ID_ANY, _('Show Times to 100s of a Second: ') )
		self.highPrecisionTimes = wx.CheckBox( self, wx.ID_ANY, style=wx.ALIGN_LEFT )
		rows += 1

		self.enableUSBCameraLabel = wx.StaticText( self, wx.ID_ANY, _('Enable USB Camera Photo Finish: ') )
		self.enableUSBCamera = wx.CheckBox( self, wx.ID_ANY, style=wx.ALIGN_LEFT )
		rows += 1

		self.jchipLabel = wx.StaticText( self, wx.ID_ANY, _('JChip Integration: ') )
		self.jchip = wx.CheckBox( self, wx.ID_ANY, style=wx.ALIGN_LEFT )
		#self.Bind( wx.EVT_CHECKBOX, self.onJChipIntegration, self.jchip )
		rows += 1

		self.autocorrectLapsDefaultLabel = wx.StaticText( self, wx.ID_ANY, _('Set "Autocorrect Lap Data" option by Default: ') )
		self.autocorrectLapsDefault = wx.CheckBox( self, wx.ID_ANY, style=wx.ALIGN_LEFT )
		self.autocorrectLapsDefault.SetValue( True )
		rows += 1

		self.finishTopLabel = wx.StaticText( self, wx.ID_ANY, _('Animation Finish on Top: ') )
		self.finishTop = wx.CheckBox( self, wx.ID_ANY, style=wx.ALIGN_LEFT )
		rows += 1

		self.reverseDirectionLabel = wx.StaticText( self, wx.ID_ANY, _('Animation Reverse Direction: ') )
		self.reverseDirection = wx.CheckBox( self, wx.ID_ANY, style=wx.ALIGN_LEFT )
		rows += 1

		self.notesLabel = wx.StaticText( self, wx.ID_ANY, _('Notes to appear on Html output:\n(Notes using Html tags must start with <html> and end with </html>)') )
		self.notes = wx.TextCtrl( self, wx.ID_ANY, style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB )
		rows += 1

		self.fileNameLabel = wx.StaticText( self, wx.ID_ANY, _('File Name: ') )
		self.fileName = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.excelLabel = wx.StaticText( self, wx.ID_ANY, _('Excel Sheet: ') )
		self.excelName = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.categoriesFileLabel = wx.StaticText( self, wx.ID_ANY, _('Categories Imported From: ') )
		self.categoriesFile = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.updateFileName()
		
		if addEditButton:
			rows += 1
		fbs = wx.GridBagSizer( hgap=2, vgap=1 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fieldAlign = wx.EXPAND|wx.GROW
		
		blank = lambda : None
		
		labelFieldFormats = [
			(self.raceNameLabel,	0, labelAlign),		(self.raceName, 		1, fieldAlign),
			(self.dateLabel,		0, labelAlign),		(self.date, 			1, fieldAlign),
			(self.raceNumLabel,		0, labelAlign),		(self.raceNum,			1, fieldAlign),
			(self.scheduledStartLabel, 0, labelAlign),	(self.scheduledStart,	1, fieldAlign),
			(self.minutesLabel,		0, labelAlign),		(self.minutes, 			1, fieldAlign),
			(self.raceDisciplineLabel,	0, labelAlign),	(self.raceDiscipline, 	1, fieldAlign),
			(self.organizerLabel,	0, labelAlign),		(self.organizer,		1, fieldAlign),
			(self.commissaireLabel,	0, labelAlign),		(self.commissaire, 		1, fieldAlign),
			(self.memoLabel,		0, labelAlign),		(self.memo, 			1, fieldAlign),
			
			(blank(),				0, labelAlign),		(blank(),				1, fieldAlign),
			(self.allCategoriesFinishAfterFastestRidersLastLapLabel,	0, labelAlign),		(self.allCategoriesFinishAfterFastestRidersLastLap,		1, fieldAlign),
			(blank(),				0, labelAlign),		(blank(),				1, fieldAlign),
			(self.timeTrialLabel,	0, labelAlign),		(self.timeTrial,		1, fieldAlign),
			
			(blank(),				0, labelAlign),		(blank(),				1, fieldAlign),
			(self.distanceUnitLabel,0, labelAlign),		(self.distanceUnit,		1, fieldAlign),
			(self.highPrecisionTimesLabel,0, labelAlign),(self.highPrecisionTimes,1, fieldAlign),
			
			(blank(),				0, labelAlign),		(blank(),				1, fieldAlign),
			(self.enableUSBCameraLabel,		0, labelAlign),		(self.enableUSBCamera,			1, fieldAlign),
			(blank(),				0, labelAlign),		(blank(),				1, fieldAlign),
			(self.jchipLabel,		0, labelAlign),		(self.jchip,			1, fieldAlign),
			(self.autocorrectLapsDefaultLabel,0, labelAlign),(self.autocorrectLapsDefault,1, fieldAlign),
			
			(blank(),				0, labelAlign),		(blank(),				1, fieldAlign),
			(self.finishTopLabel,0, labelAlign),		(self.finishTop,		1, fieldAlign),
			(self.reverseDirectionLabel,0, labelAlign),	(self.reverseDirection,	1, fieldAlign),
			
			(self.notesLabel,		0, 0),				(self.notes,			1, 0),
			
			(blank(),				0, labelAlign),		(blank(),				1, fieldAlign),
			(self.excelLabel,		0, labelAlign),		(self.excelName, 		1, fieldAlign),
			(self.categoriesFileLabel, 0, labelAlign),	(self.categoriesFile,	1, fieldAlign),
			
			(blank(),				0, labelAlign),		(blank(),				1, fieldAlign),
			(self.fileNameLabel,	0, labelAlign),		(self.fileName, 		1, fieldAlign),
		]
		row = 0
		for i, (item, column, flag) in enumerate(labelFieldFormats):
			if not item:
				continue
			if column == 1:
				flag |= wx.EXPAND
			if item == self.notes:
				row += 1
				fbs.Add( item, pos=(row, 0), span=(1,2), flag=flag )
				row += 1
			else:
				fbs.Add( item, pos=(row, column), span=(1,1), flag=flag )
				if column == 1:
					row += 1
				
		#fbs.AddMany( labelFieldFormats )
		
		if addEditButton:
			hs = wx.BoxSizer( wx.HORIZONTAL )
			
			self.editButton = wx.Button(self, wx.ID_ANY, _('Change Properties...'))
			self.editButton.Bind( wx.EVT_BUTTON, self.editButtonCallback )
			hs.Add( self.editButton, border = 8, flag = wx.TOP|wx.BOTTOM )
			row += 1
			
			self.excelButton = wx.Button(self, wx.ID_ANY, _('Link External Excel Sheet...'))
			self.excelButton.Bind( wx.EVT_BUTTON, self.excelButtonCallback )
			hs.Add( self.excelButton, border = 8, flag = wx.LEFT|wx.TOP|wx.BOTTOM )

			fbs.Add( hs, pos=(row, 1), span=(1,1) )
		
		fbs.AddGrowableCol( 1 )
		self.SetSizer(fbs)
		
		self.editFields = [labelFieldFormats[i][0] for i in xrange(1, len(labelFieldFormats), 2)]
		self.editFields = [e for e in self.editFields if e]
	
	def onJChipIntegration( self, event ):
		self.autocorrectLapsDefault.SetValue( not self.jchip.GetValue() )
	
	def excelButtonCallback( self, event ):
		mainWin = Utils.getMainWin()
		if mainWin:
			mainWin.menuLinkExcel()
	
	def editButtonCallback( self, event ):
		if not Model.race:
			mainWin = Utils.getMainWin()
			if mainWin:
				wx.CallAfter( mainWin.menuNew, event )
			else:
				Utils.MessageOK( self,
					_('You must have a valid race File|Open...\nOr create one with File|New....'), _('Valid Race Required'),
					wx.ICON_WARNING )
		else:
			ChangeProperties( self )
	
	def setEditable( self, editable = True ):
		for f in self.editFields:
			f.Enable()
			try:
				f.SetEditable( editable )
			except:
				if not editable and not isinstance(f, wx.StaticText):
					f.Disable()
	
	def incNext( self ):
		self.raceNum.SetValue( self.raceNum.GetValue() + 1 )
		self.memo.SetValue( '' )
		if	 self.scheduledStart.GetValue() == '10:00' and self.minutes.GetValue() == 40 and self.raceNum.GetValue() == 2:
			self.scheduledStart.SetValue( '11:30' )
			self.minutes.SetValue( 50 )
		elif self.scheduledStart.GetValue() == '11:30' and self.minutes.GetValue() == 50 and self.raceNum.GetValue() == 3:
			self.scheduledStart.SetValue( '13:00' )
			self.minutes.SetValue( 60 )
		else:
			sStr = '{}'.format(self.scheduledStart.GetValue())
			fields = sStr.split(':')
			if len(fields) == 2:
				mins = int(fields[0],10) * 60 + int(fields[1],10)
				mins += self.minutes.GetValue()
				mins += 15	# Add time for a break.
				if (mins/60) >= 24:
					mins = 0
				sNew = '%02d:%02d:00' % (int(mins/60), mins%60)
				self.scheduledStart.SetValue( sNew )
	
	def onChanged( self, event ):
		self.updateFileName()
	
	def updateFileName( self ):
		rDate = self.date.GetValue().Format(Properties.dateFormat)
		rName = Properties.badFileCharsRE.sub( ' ', self.raceName.GetValue() ).strip()
		rMemo = Properties.badFileCharsRE.sub( ' ', self.memo.GetValue() ).strip()
		fname = '%s-%s-r%d-%s.cmn' % (rDate, rName, self.raceNum.GetValue(), rMemo )
		self.fileName.SetLabel( fname )
	
	def getFileName( self ):
		return self.fileName.GetLabel()
	
	def refresh( self ):
		with Model.LockRace() as race:
			self.setEditable( False )
			if race is None:
				return
			self.raceName.SetValue( race.name )
			self.raceDiscipline.SetValue( getattr(race, 'discipline', 'Cyclo-cross') )
			self.organizer.SetValue( getattr(race, 'organizer', '') )
			d = wx.DateTime()
			d.ParseDate(race.date)
			self.date.SetValue( d )
			self.raceNum.SetValue( race.raceNum )
			self.scheduledStart.SetValue( race.scheduledStart )
			self.allCategoriesFinishAfterFastestRidersLastLap.SetValue( getattr(race, 'allCategoriesFinishAfterFastestRidersLastLap', False) )
			self.timeTrial.SetValue( getattr(race, 'isTimeTrial', False) )
			self.minutes.SetValue( race.minutes )
			self.commissaire.SetValue( race.commissaire )
			self.memo.SetValue( race.memo )
			self.updateFileName()
			
			self.jchip.SetValue( getattr(race, 'enableJChipIntegration', False) )
			self.autocorrectLapsDefault.SetValue( getattr(race, 'autocorrectLapsDefault', True) )
			self.highPrecisionTimes.SetValue( getattr(race, 'highPrecisionTimes', False) )
			self.distanceUnit.SetSelection( getattr(race, 'distanceUnit', 0) )
			
			self.enableUSBCamera.SetValue( getattr(race, 'enableUSBCamera', False) )
			
			self.reverseDirection.SetValue( getattr(race, 'reverseDirection', False) )
			self.finishTop.SetValue( getattr(race, 'finishTop', False) )
			
			self.notes.SetValue( getattr(race, 'notes', '') )
			
			excelLink = getattr(race, 'excelLink', None)
			if excelLink:
				self.excelName.SetLabel( '%s|%s' % (
					os.path.basename(excelLink.fileName) if excelLink.fileName else '',
					excelLink.sheetName if excelLink.sheetName else '') )
			else:
				self.excelName.SetLabel( '' )
			self.categoriesFile.SetLabel( os.path.basename(getattr(race, 'categoriesImportFile', '')) )
			
		self.GetSizer().Layout()
		
	def update( self, race = None ):
		undo.pushState()
		with Model.lock:
			if race is None:
				race = Model.getRace()
			if race is None:
				return
			race.name = self.raceName.GetValue()
			race.discipline = self.raceDiscipline.GetValue()
			race.organizer = self.organizer.GetValue()
			race.date = self.date.GetValue().Format(Properties.dateFormat)
			race.raceNum = self.raceNum.GetValue()
			race.scheduledStart = self.scheduledStart.GetValue()
			race.allCategoriesFinishAfterFastestRidersLastLap = self.allCategoriesFinishAfterFastestRidersLastLap.IsChecked()
			race.isTimeTrial = self.timeTrial.IsChecked()
			race.enableJChipIntegration = self.jchip.IsChecked()
			race.autocorrectLapsDefault = self.autocorrectLapsDefault.IsChecked()
			race.highPrecisionTimes = self.highPrecisionTimes.IsChecked()
			race.distanceUnit = self.distanceUnit.GetSelection()
			race.reverseDirection = self.reverseDirection.IsChecked()
			race.enableUSBCamera = self.enableUSBCamera.IsChecked()
			race.finishTop = self.finishTop.IsChecked()
			race.minutes = self.minutes.GetValue()
			race.commissaire = self.commissaire.GetValue()
			race.memo = self.memo.GetValue()
			race.notes = self.notes.GetValue()
			race.setChanged()
			
		if Utils.getMainWin():
			Utils.getMainWin().record.setTimeTrialInput( race.isTimeTrial )
		
class PropertiesDialog( wx.Dialog ):
	def __init__(
			self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
			showFileFields = True,
			refreshProperties = False
			):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		pre = wx.PreDialog()
		#pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)

		self.properties = Properties( self, addEditButton = False )
		if refreshProperties:
			self.properties.refresh()
		sizer.Add(self.properties, 0, wx.ALIGN_CENTRE|wx.ALL|wx.GROW, 5)

		if showFileFields:
			gs = wx.FlexGridSizer( rows=2, cols=3, vgap = 5, hgap = 5 )
			gs.Add( wx.StaticText(self, -1, _('Race File Folder:')), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			self.folder = wx.TextCtrl( self, -1, '', size=(400,-1) )
			self.folder.SetValue( Utils.getDocumentsDir() )
			gs.Add( self.folder, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW)

			btn = wx.Button( self, 10, label=_('Browse...') )
			btn.Bind( wx.EVT_BUTTON, self.onBrowseFolder )
			gs.Add( btn, 0, wx.ALIGN_CENTER_VERTICAL )
			
			gs.Add( wx.StaticText(self, -1, _('Categories Import File (*.brc):')), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			self.categoriesFile = wx.TextCtrl( self, -1, '', size=(400,-1) )
			self.categoriesFile.SetValue( Utils.getDocumentsDir() )
			gs.Add( self.categoriesFile, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW )

			btn = wx.Button( self, 10, label=_('Browse...') )
			btn.Bind( wx.EVT_BUTTON, self.onBrowseCategories )
			gs.Add( btn, 0, wx.ALIGN_CENTER_VERTICAL )
			
			gs.AddGrowableCol( 0, 1 )
			
			sizer.Add( gs, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
			
			line = wx.StaticLine( self, -1, size=(20, -1), style=wx.LI_HORIZONTAL)
			sizer.Add( line, -1, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		
		btnsizer = wx.StdDialogButtonSizer()
        
		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		
		self.helpBtn = wx.Button( self, wx.ID_HELP )
		self.Bind( wx.EVT_BUTTON, lambda evt: Utils.showHelp('Properties.html'), self.helpBtn )
		btnsizer.AddButton(self.helpBtn)
		
		btnsizer.Realize()

		sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.ALIGN_RIGHT, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)
		
	def onBrowseFolder( self, event ):
		defaultPath = self.folder.GetValue()
		if not defaultPath:
			defaultPath = Utils.getDocumentsDir()
			
		dlg = wx.DirDialog( self, _("Choose a Folder for the Race"),
							style=wx.DD_DEFAULT_STYLE, defaultPath=defaultPath )
		if dlg.ShowModal() == wx.ID_OK:
			self.folder.SetValue( dlg.GetPath() )
		dlg.Destroy()		
	
	def onBrowseCategories( self, event ):
		defaultFile = self.categoriesFile.GetValue()
		if defaultFile.endswith('.brc'):
			dirName = os.path.dirname( defaultFile )
			fileName = os.path.basename( defaultFile )
		else:
			dirName = defaultFile
			fileName = ''
			if not dirName:
				dirName = self.folder.GetValue()
		
		dlg = wx.FileDialog( self, message=_("Choose Race Categories File"),
							defaultDir=dirName, 
							defaultFile=fileName,
							wildcard=_("Bicycle Race Categories (*.brc)|*.brc"),
							style=wx.OPEN )
		if dlg.ShowModal() == wx.ID_OK:
			self.categoriesFile.SetValue( dlg.GetPath() )
		dlg.Destroy()
		
	def GetPath( self ):
		self.properties.updateFileName()
		return os.path.join( self.folder.GetValue(), self.properties.getFileName() )
		
	def GetCategoriesFile( self ):
		categoriesFile = self.categoriesFile.GetValue()
		return categoriesFile if categoriesFile.endswith( '.brc' ) else None

def ChangeProperties( parent ):
	propertiesDialog = PropertiesDialog( parent, -1, _("Change Properties"), showFileFields = False, refreshProperties = True, size=(600,400) )
	propertiesDialog.properties.setEditable( True )
	try:
		if propertiesDialog.ShowModal() != wx.ID_OK:
			raise NameError('User Cancel')
		mainWin = Utils.getMainWin()
		dir = os.path.dirname( mainWin.fileName )
		
		newBaseName = propertiesDialog.properties.getFileName()
		newFName = os.path.join( dir, newBaseName )
		
		if newFName != mainWin.fileName:
			if Utils.MessageOKCancel(parent, _("The filename will be changed to:\n\n{}\n\nContinue?").format(newBaseName), _("Change Filename?")):
				if os.path.exists(newFName):
					if not Utils.MessageOKCancel(parent, _("This file already exists:\n\n{}\n\nOverwrite?").format(newFName), _("Overwrite Existing File?")):
						raise NameError('User Cancel')
					
		propertiesDialog.properties.update()
		mainWin.fileName = newFName
		Model.resetCache()
		mainWin.writeRace()
		Utils.refresh()
		wx.CallAfter( Utils.refreshForecastHistory )
			
	except (NameError, AttributeError, TypeError):
		pass
	
	propertiesDialog.Destroy()
		
if __name__ == '__main__':
	race = Model.newRace()
	race._populate()
	
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,600))
	properties = Properties(mainWin)
	properties.setEditable( True )
	properties.refresh()
	mainWin.Show()
	propertiesDialog = PropertiesDialog( mainWin, -1, "Properties Dialog Test", showFileFields=False, refreshProperties=True )
	propertiesDialog.Show()
	app.MainLoop()
