
import os
import wx
import wx.wizard as wiz
import wx.lib.filebrowsebutton as filebrowse
from GeoAnimation import GeoTrack
import Utils

class IntroPage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Import a GPX File containing coordinates for the course.\nContinue if you want to load or change the GPX course file.'),
					flag=wx.ALL, border = border )
		self.info = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_READONLY|wx.TE_MULTILINE)
		vbs.Add( self.info, flag=wx.ALL|wx.EXPAND, border = border )
		
		self.SetSizer( vbs )
	
	def setInfo( self, geoTrack, geoTrackFName ):
		if geoTrack:
			s = 'Existing GPX file:\n\nImported from: "%s"\n\nNumber of Coords: %d\n\nLap Length: %.3f km, %.3f miles' % (
				geoTrackFName,
				len(geoTrack.gpsPoints),
				geoTrack.lengthKm, geoTrack.lengthMiles )
		else:
			s = ''
		self.info.ChangeValue( s )
		self.GetSizer().Layout()
	
class FileNamePage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Specify the GPX File containing coordinates for the course.'),
					flag=wx.ALL, border = border )
		fileMask = [
			'GPX Files (*.gpx)|*.gpx',
		]
		self.fbb = filebrowse.FileBrowseButton( self, -1, size=(450, -1),
												labelText = 'GPX File:',
												fileMode=wx.OPEN,
												fileMask='|'.join(fileMask) )
		vbs.Add( self.fbb, flag=wx.ALL, border = border )
		
		vbs.Add( wx.StaticText(self, wx.ID_ANY, '\n\nTo revert back to the Oval track, set an Empty filename, and press Cancel.'),
			flag=wx.ALL, border = border )
		
		self.SetSizer( vbs )
	
	def setInfo( self, geoTrackFName ):
		if geoTrackFName:
			self.fbb.SetValue( geoTrackFName )
		else:
			self.fbb.SetValue( '' )
		self.GetSizer().Layout()
	
	def getFileName( self ):
		return self.fbb.GetValue()
	
class SummaryPage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Summary:'), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, ' '), flag=wx.ALL, border = border )

		rows = 0
		
		self.fileLabel = wx.StaticText( self, wx.ID_ANY, 'GPX File:' )
		self.fileName = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.numCoordsLabel = wx.StaticText( self, wx.ID_ANY, 'Number of Coords:' )
		self.numCoords = wx.StaticText( self, wx.ID_ANY, '' )
		rows += 1

		self.distanceLabel = wx.StaticText( self, wx.ID_ANY, 'Lap Length:' )
		self.distance = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_READONLY)
		rows += 1

		fbs = wx.FlexGridSizer( rows=rows, cols=2, hgap=5, vgap=2 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fbs.AddMany( [(self.fileLabel, 0, labelAlign),			(self.fileName, 	1, wx.EXPAND|wx.GROW),
					  (self.numCoordsLabel, 0, labelAlign),		(self.numCoords, 	1, wx.EXPAND|wx.GROW),
					  (self.distanceLabel, 0, labelAlign),		(self.distance,		1, wx.EXPAND|wx.GROW),
					 ] )
		fbs.AddGrowableCol( 1 )
		
		vbs.Add( fbs )
		
		self.SetSizer(vbs)
	
	def setInfo( self, fileName, numCoords, distance ):
		self.fileName.SetLabel( fileName )
		self.numCoords.SetLabel( '%d' % numCoords )
		self.distance.ChangeValue( '%.3f km, %.3f miles' % (distance, distance*0.621371) )
		
class GetGeoTrack( object ):
	def __init__( self, parent, geoTrack = None, geoTrackFName = None ):
		img_filename = os.path.join( Utils.getImageFolder(), 'gps.png' )
		img = wx.Bitmap(img_filename) if img_filename and os.path.exists(img_filename) else wx.NullBitmap
		
		self.parent = parent
		prewizard = wiz.PreWizard()
		prewizard.SetExtraStyle( wiz.WIZARD_EX_HELPBUTTON )
		prewizard.Create( parent, wx.ID_ANY, 'Import GPX Course File', img )
		self.wizard = prewizard
		self.wizard.Bind( wiz.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		self.wizard.Bind( wiz.EVT_WIZARD_CANCEL, self.onCancel )
		self.wizard.Bind( wiz.EVT_WIZARD_HELP,
			lambda evt: Utils.showHelp('Menu-DataMgmt.html#import-course-in-gpx-format') )
		
		self.introPage		= IntroPage( self.wizard )
		self.fileNamePage	= FileNamePage( self.wizard )
		self.summaryPage	= SummaryPage( self.wizard )
		
		wiz.WizardPageSimple_Chain( self.introPage, self.fileNamePage )
		wiz.WizardPageSimple_Chain( self.fileNamePage, self.summaryPage )

		self.wizard.SetPageSize( wx.Size(500,200) )
		self.wizard.GetPageAreaSizer().Add( self.introPage )
		
		self.geoTrackFName = geoTrackFName
		if geoTrackFName:
			self.introPage.setInfo( geoTrack, geoTrackFName )
			self.fileNamePage.setInfo( geoTrackFName )
		self.geoTrack = geoTrack

	def show( self ):
		if self.wizard.RunWizard(self.introPage):
			self.geoTrackFName = self.fileNamePage.getFileName()
		return self.geoTrack, self.geoTrackFName
	
	def onCancel( self, evt ):
		page = evt.GetPage()
		if page == self.introPage:
			pass
		elif page == self.fileNamePage:
			if self.geoTrack and Utils.MessageOKCancel( self.parent,
					'Unload Existing GPX Course?\n\n(shows the oval track)', 
					'Unload Existing GPX Course?', wx.ICON_EXCLAMATION):
				self.geoTrack = None
				self.geoTrackFName = None
		elif page == self.summaryPage:
			pass
	
	def onPageChanging( self, evt ):
		isForward = evt.GetDirection()
		if not isForward:
			return
		success = True
		page = evt.GetPage()
		
		if page == self.introPage:
			pass
		elif page == self.fileNamePage:
			fileName = self.fileNamePage.getFileName()
			try:
				open(fileName).close()
			except IOError:
				if fileName == '':
					message = 'Please specify a GPX file.'
				else:
					message = 'Cannot open file "%s".\nPlease check the file name and/or its read permissions.' % fileName
				Utils.MessageOK( self.wizard, message, title='File Open Error', iconMask=wx.ICON_ERROR)
				success = False
				evt.Veto()
				
			if success:
				self.geoTrack = GeoTrack()
				try:
					self.geoTrack.read( fileName )
					self.summaryPage.setInfo( fileName, len(self.geoTrack.gpsPoints), self.geoTrack.lengthKm )
					self.geoTrackFName = fileName
				except:
					Utils.MessageOK( self.wizard, 'File format error (is this a GPX file?)',
									title='GPX Format Error', iconMask=wx.ICON_ERROR)
					success = False
					self.geoTrack = None
					evt.Veto()
					
		elif page == self.summaryPage:
			pass
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
