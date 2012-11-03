
import os
import wx
import wx.wizard as wiz
import wx.lib.filebrowsebutton as filebrowse
from GeoAnimation import GeoTrack, GpxHasTimes
import Utils

class IntroPage(wiz.WizardPageSimple):
	def __init__(self, parent, controller):
		wiz.WizardPageSimple.__init__(self, parent)
		
		self.controller = controller
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Import a GPX File containing coordinates for the course.\nContinue if you want to load or change the GPX course file.'),
					flag=wx.ALL, border = border )
		self.info = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_READONLY|wx.TE_MULTILINE)
		vbs.Add( self.info, flag=wx.ALL|wx.EXPAND, border = border )
		
		self.removeButton = wx.Button( self, wx.ID_ANY, 'Remove GPX Course' )
		self.Bind( wx.EVT_BUTTON, self.onRemove, self.removeButton )
		vbs.Add( self.removeButton, flag=wx.ALL|wx.ALIGN_RIGHT, border = border )
		
		self.SetSizer( vbs )
	
	def onRemove( self, event ):
		if self.geoTrack:
			if Utils.MessageOKCancel( self, 'Permanently Remove GPX Course?', 'Remove GPX Course' ):
				self.controller.clearData()
				self.setInfo( None, None )
		else:
			Utils.MessageOK( self, 'No GPX Course', 'No GPX Course' )
	
	def setInfo( self, geoTrack, geoTrackFName ):
		self.geoTrack = geoTrack
		if geoTrack:
			s = 'Existing GPX file:\n\nImported from: "%s"\n\nNumber of Coords: %d\n\nLap Length: %.3f km, %.3f miles' % (
				geoTrackFName,
				geoTrack.numPoints,
				geoTrack.lengthKm, geoTrack.lengthMiles )
		else:
			s = ''
		self.removeButton.Enable( bool(geoTrack) )
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
		
		self.SetSizer( vbs )
	
	def setInfo( self, geoTrackFName ):
		if geoTrackFName:
			self.fbb.SetValue( geoTrackFName )
		else:
			self.fbb.SetValue( '' )
		self.GetSizer().Layout()
	
	def getFileName( self ):
		return self.fbb.GetValue()

class UseTimesPage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		self.noTimes = wx.StaticText(self, wx.ID_ANY, 'This GPX file does not contain times.\n\nRace times will be calculated based on distance and change in elevation.' )
		vbs.Add( self.noTimes, flag=wx.ALL, border = border )
		
		self.useTimes = wx.CheckBox(self, wx.ID_ANY, 'Use times in the GPX file for more realistic animation')
		vbs.Add( self.useTimes, flag=wx.ALL|wx.EXPAND, border = border )
		
		self.SetSizer( vbs )
	
	def setInfo( self, geoTrackFName ):
		hasTimes = GpxHasTimes( geoTrackFName )
		self.noTimes.Show( not hasTimes )
		self.useTimes.Show( hasTimes )
		self.useTimes.SetValue( hasTimes )
		self.GetSizer().Layout()
	
	def getUseTimes( self ):
		return self.useTimes.IsChecked()

		
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
		
		self.introPage		= IntroPage( self.wizard, self )
		self.fileNamePage	= FileNamePage( self.wizard )
		self.useTimesPage	= UseTimesPage( self.wizard )
		self.summaryPage	= SummaryPage( self.wizard )
		
		wiz.WizardPageSimple_Chain( self.introPage, self.fileNamePage )
		wiz.WizardPageSimple_Chain( self.fileNamePage, self.useTimesPage )
		wiz.WizardPageSimple_Chain( self.useTimesPage, self.summaryPage )

		self.wizard.SetPageSize( wx.Size(500,200) )
		self.wizard.GetPageAreaSizer().Add( self.introPage )
		
		self.geoTrack = geoTrack
		self.geoTrackOriginal = geoTrack
		self.geoTrackFName = geoTrackFName
		self.geoTrackFNameOriginal = geoTrackFName
		
		self.introPage.setInfo( geoTrack, geoTrackFName )
		if geoTrackFName:
			self.fileNamePage.setInfo( geoTrackFName )

	def show( self ):
		if self.wizard.RunWizard(self.introPage):
			return self.geoTrack, self.geoTrackFName
		else:
			return self.geoTrackOriginal, self.geoTrackFNameOriginal
	
	def onCancel( self, evt ):
		page = evt.GetPage()
		if page == self.introPage:
			pass
		elif page == self.fileNamePage:
			pass
		elif page == self.summaryPage:
			pass
	
	def clearData( self ):
		self.geoTrack = None
		self.geoTrackFName = None
		self.geoTrackOriginal = None
		self.geoTrackFNameOriginal = None
		
	def onPageChanging( self, evt ):
		isForward = evt.GetDirection()
		if not isForward:
			return
		page = evt.GetPage()
		
		if page == self.introPage:
			pass
		elif page == self.fileNamePage:
			fileName = self.fileNamePage.getFileName()
			
			# Check for a valid file.
			try:
				open(fileName).close()
			except IOError:
				if fileName == '':
					message = 'Please specify a GPX file.'
				else:
					message = 'Cannot open file:\n\n    "%s"\n\nPlease check the file name and/or its read permissions.' % fileName
				Utils.MessageOK( self.wizard, message, title='File Open Error', iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
			
			# Check for valid content.
			geoTrack = GeoTrack()
			try:
				geoTrack.read( fileName )
				if geoTrack.numPoints >= 2:
					self.geoTrackFName = fileName
					self.geoTrack = geoTrack
					self.summaryPage.setInfo( self.geoTrackFName, self.geoTrack.numPoints, self.geoTrack.lengthKm )
					self.useTimesPage.setInfo( self.geoTrackFName )
				else:
					Utils.MessageOK( self.wizard,
						'Import Failed:  GPX file contains fewer than two points.',
						title='File Format Error',
						iconMask=wx.ICON_ERROR)
					evt.Veto()
					return
			except:
				Utils.MessageOK( self.wizard, 'Read error:  Is this a proper GPX file?',
								title='Read Error', iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
		elif page == self.useTimesPage:
			if self.useTimesPage.getUseTimes():
				self.geoTrack.read( self.geoTrackFName, True )
		elif page == self.summaryPage:
			pass
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
