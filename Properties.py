import Model
import Utils
import wx
import re
import os
import wx.lib.intctrl as intctrl
import wx.lib.masked as masked

class Properties( wx.Panel ):
	badFileCharsRE = re.compile( '[^a-zA-Z0-9_ ]+' )
	dateFormat = '%Y-%m-%d'

	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Panel.__init__(self, parent, id)

		rows = 0
		
		self.raceNameLabel = wx.StaticText( self, wx.ID_ANY, 'Race Name:' )
		self.raceName = wx.TextCtrl( self, wx.ID_ANY, value='' )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.raceName )
		rows += 1
		
		self.dateLabel = wx.StaticText( self, wx.ID_ANY, 'Date:' )
		self.date = wx.DatePickerCtrl( self, wx.ID_ANY, style = wx.DP_DROPDOWN )
		self.Bind(wx.EVT_DATE_CHANGED, self.onChanged, self.date)
		rows += 1
		
		self.raceNumLabel = wx.StaticText( self, wx.ID_ANY, 'Race #:' )
		self.raceNum = intctrl.IntCtrl( self, wx.ID_ANY, min=1, max=20, allow_none=False, value=1 )
		self.Bind(intctrl.EVT_INT, self.onChanged, self.raceNum)
		rows += 1
		
		self.scheduledStartLabel = wx.StaticText( self, wx.ID_ANY, 'Scheduled Start:' )
		self.scheduledStart = masked.TimeCtrl( self, wx.ID_ANY, fmt24hr=True, display_seconds=False, value='10:00:00' )
		rows += 1

		self.minutesLabel = wx.StaticText( self, wx.ID_ANY, 'Race Minutes:' )
		self.minutes = intctrl.IntCtrl( self, wx.ID_ANY, min=1, max=300, allow_none=False, value=40 )
		rows += 1

		self.memoLabel = wx.StaticText( self, wx.ID_ANY, 'Memo:' )
		self.memo = wx.TextCtrl( self, wx.ID_ANY, value='' )
		self.Bind( wx.EVT_TEXT, self.onChanged, self.memo )
		rows += 1
		
		self.commissaireLabel = wx.StaticText( self, wx.ID_ANY, 'Commissaire:' )
		self.commissaire = wx.TextCtrl( self, wx.ID_ANY, value='' )
		rows += 1
		
		self.fileNameLabel = wx.StaticText( self, wx.ID_ANY, 'File Name: ' )
		self.fileName = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.updateFileName()
		
		fbs = wx.FlexGridSizer( rows=rows, cols=2, hgap=5, vgap=3 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fbs.AddMany( [(self.raceNameLabel, 0, labelAlign),		(self.raceName, 1, wx.EXPAND|wx.GROW),
					  (self.dateLabel, 0, labelAlign),			(self.date, 	1, wx.EXPAND|wx.GROW),
					  (self.raceNumLabel, 0, labelAlign),		(self.raceNum,	1, wx.EXPAND|wx.GROW),
					  (self.scheduledStartLabel, 0, labelAlign),(self.scheduledStart, 1, wx.EXPAND|wx.GROW),
					  (self.minutesLabel, 0, labelAlign),		(self.minutes, 1, wx.EXPAND|wx.GROW),
					  (self.memoLabel, 0, labelAlign),			(self.memo, 1, wx.EXPAND|wx.GROW),
					  (self.commissaireLabel, 0,labelAlign),	(self.commissaire, 1, wx.EXPAND|wx.GROW),
					  (self.fileNameLabel, 0, labelAlign),		(self.fileName, 1, wx.EXPAND|wx.GROW),
					 ] )
		fbs.AddGrowableCol( 1 )
		self.SetSizer(fbs)
	
	def setEditable( self, editable = True ):
		return
		self.raceName.SetEditable( editable )
		# self.date.SetEditable( editable )
		self.raceNum.SetEditable( editable )
		self.scheduledStart.SetEditable( editable )
		self.minutes.SetEditable( editable )
		self.memo.SetEditable( editable )
		self.commissaire.SetEditable( editable )
	
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
			sStr = str(self.scheduledStart.GetValue())
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
		self.setEditable( False )
		race = Model.getRace()
		if race is None:
			return
		self.raceName.SetValue( race.name )
		d = wx.DateTime()
		d.ParseDate(race.date)
		self.date.SetValue( d )
		self.raceNum.SetValue( race.raceNum )
		self.scheduledStart.SetValue( race.scheduledStart )
		self.minutes.SetValue( race.minutes )
		self.commissaire.SetValue( race.commissaire )
		self.memo.SetValue( race.memo )
		
		self.updateFileName()
		
	def update( self, race = None ):
		if race is None:
			race = Model.getRace()
		if race is None:
			return
		race.name = self.raceName.GetValue()
		race.date = self.date.GetValue().Format(Properties.dateFormat)
		race.raceNum = self.raceNum.GetValue()
		#print str(self.scheduledStart.GetValue())
		race.scheduledStart = self.scheduledStart.GetValue()
		race.minutes = self.minutes.GetValue()
		race.commissaire = self.commissaire.GetValue()
		race.memo = self.memo.GetValue()

class PropertiesDialog( wx.Dialog ):
	def __init__(
			self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
			useMetal=False,
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

		# This extra style can be set after the UI object has been created.
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)

		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)

		self.properties = Properties(self)
		sizer.Add(self.properties, 0, wx.ALIGN_CENTRE|wx.ALL|wx.GROW, 5)

		gs = wx.FlexGridSizer( rows=2, cols=3, vgap = 5, hgap = 5 )
		gs.Add( wx.StaticText(self, -1, 'Race File Folder:'), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.folder = wx.TextCtrl( self, -1, '', size=(400,-1) )
		self.folder.SetValue( Utils.getDirName() )
		gs.Add( self.folder, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW)

		btn = wx.Button( self, 10, label='Browse...' )
		btn.Bind( wx.EVT_BUTTON, self.onBrowseFolder )
		gs.Add( btn, 0, wx.ALIGN_CENTER_VERTICAL )
		
		gs.Add( wx.StaticText(self, -1, 'Categories Import File (*.brc):'), 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		self.categoriesFile = wx.TextCtrl( self, -1, '', size=(400,-1) )
		self.categoriesFile.SetValue( Utils.getDirName() )
		gs.Add( self.categoriesFile, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.GROW )

		btn = wx.Button( self, 10, label='Browse...' )
		btn.Bind( wx.EVT_BUTTON, self.onBrowseCategories )
		gs.Add( btn, 0, wx.ALIGN_CENTER_VERTICAL )
		
		gs.AddGrowableCol( 0, 1 )
		
		sizer.Add( gs, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		
		line = wx.StaticLine( self, -1, size=(20, -1), style=wx.LI_HORIZONTAL)
		sizer.Add( line, -1, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		
		btnsizer = wx.StdDialogButtonSizer()
        
		if wx.Platform != "__WXMSW__":
			btn = wx.ContextHelpButton(self)
			btnsizer.AddButton(btn)
        
		btn = wx.Button(self, wx.ID_OK)
		btn.SetDefault()
		btnsizer.AddButton(btn)

		btn = wx.Button(self, wx.ID_CANCEL)
		btnsizer.AddButton(btn)
		btnsizer.Realize()

		sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)
	
	def onBrowseFolder( self, event ):
		defaultPath = self.folder.GetValue()
		if not defaultPath:
			defaultPath = Utils.getDirName()
			
		dlg = wx.DirDialog( self, "Choose a Folder for the Race",
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
		
		dlg = wx.FileDialog( self, message="Choose Race Categories File",
							defaultDir=dirName, 
							defaultFile=fileName,
							wildcard="Bicycle Race Categories (*.brc)|*.brc",
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
		
if __name__ == '__main__':
	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	properties = Properties(mainWin)
	# properties.setEditable( False )
	properties.refresh()
	mainWin.Show()
	app.MainLoop()
