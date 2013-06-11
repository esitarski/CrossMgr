
import os
import sys
import wx
import wx.wizard as wiz
import wx.lib.filebrowsebutton as filebrowse
from GeoAnimation import GeoTrack, GpxHasTimes
import Utils
import Model
import traceback

class IntroPage(wiz.WizardPageSimple):
	def __init__(self, parent, controller):
		wiz.WizardPageSimple.__init__(self, parent)
		
		self.controller = controller
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, wx.ID_ANY, 'Import a GPX File containing coordinates for the course.\nContinue if you want to load or change the GPX course file.'),
					flag=wx.ALL, border = border )
		self.info = wx.TextCtrl(self, wx.ID_ANY, '\n\n\n\n\n\n', style=wx.TE_READONLY|wx.TE_MULTILINE, size=(-1,180))
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
			s = 'Existing GPX file:\n\nImported from: "%s"\n\nNumber of Coords: %d\n\nLap Length: %.3f km, %.3f miles\n\nTotal Elevation Gain: %.0f m, %.0f ft' % (
				geoTrackFName,
				geoTrack.numPoints,
				geoTrack.lengthKm, geoTrack.lengthMiles,
				geoTrack.totalElevationGainM, geoTrack.totalElevationGainFt)
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
		
		self.distanceKm = None
		self.distanceMiles = None
		
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

		self.totalElevationGainLabel = wx.StaticText( self, wx.ID_ANY, 'Total Elevation Gain:' )
		self.totalElevationGain = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_READONLY)
		rows += 1

		self.setCategoryDistanceLabel = wx.StaticText( self, wx.ID_ANY, '' )
		self.setCategoryDistanceCheckbox = wx.CheckBox( self, wx.ID_ANY, 'Set Category Distances to GPX Lap Length' )
		self.setCategoryDistanceCheckbox.SetValue( True )
		rows += 1

		fbs = wx.FlexGridSizer( rows=rows, cols=2, hgap=5, vgap=2 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fbs.AddMany( [(self.fileLabel, 0, labelAlign),			(self.fileName, 	1, wx.EXPAND|wx.GROW),
					  (self.numCoordsLabel, 0, labelAlign),		(self.numCoords, 	1, wx.EXPAND|wx.GROW),
					  (self.distanceLabel, 0, labelAlign),		(self.distance,		1, wx.EXPAND|wx.GROW),
					  (self.totalElevationGainLabel, 0, labelAlign),(self.totalElevationGain,		1, wx.EXPAND|wx.GROW),
					  (wx.StaticText(self,wx.ID_ANY,''), 0, labelAlign),			(wx.StaticText(self,wx.ID_ANY,''), 1, wx.EXPAND|wx.GROW),
					  (self.setCategoryDistanceLabel, 0, labelAlign), (self.setCategoryDistanceCheckbox, 1, wx.EXPAND|wx.GROW),
					 ] )
		fbs.AddGrowableCol( 1 )
		
		vbs.Add( fbs )
		
		self.SetSizer(vbs)
	
	def doFixCategoryDistances( self, event ):
		if not self.setCategoryDistanceCheckbox.GetValue():
			return
			
		with Model.LockRace() as race:
			if not race:
				return
			distance = self.distanceKm if race.distanceUnit == race.UnitKm else self.distanceMiles
			for c in race.categories.itervalues():
				c.distance = distance
			race.setChanged()
	
	def setInfo( self, fileName, numCoords, distance, totalElevationGain ):
		self.fileName.SetLabel( fileName )
		self.numCoords.SetLabel( '%d' % numCoords )
		self.distanceKm = distance
		self.distanceMiles = distance*0.621371
		self.distance.ChangeValue( '%.3f km, %.3f miles' % (self.distanceKm, self.distanceMiles) )
		self.totalElevationGainM = totalElevationGain
		self.totalElevationGainFt = totalElevationGain*3.28084
		self.totalElevationGain.ChangeValue( '%.0f m, %.0f ft' % (self.totalElevationGainM, self.totalElevationGainFt) )
		
class GetGeoTrack( object ):
	def __init__( self, parent, geoTrack = None, geoTrackFName = None ):
		img_filename = os.path.join( Utils.getImageFolder(), 'gps.png' )
		img = wx.Bitmap(img_filename) if img_filename and os.path.exists(img_filename) else wx.NullBitmap
		
		self.parent = parent
		prewizard = wiz.PreWizard()
		prewizard.SetExtraStyle( wiz.WIZARD_EX_HELPBUTTON )
		prewizard.Create( parent, wx.ID_ANY, 'Import GPX Course File', img )
		self.wizard = prewizard
		
		self.introPage		= IntroPage( self.wizard, self )
		self.fileNamePage	= FileNamePage( self.wizard )
		self.useTimesPage	= UseTimesPage( self.wizard )
		self.summaryPage	= SummaryPage( self.wizard )
		
		self.wizard.Bind( wiz.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		self.wizard.Bind( wiz.EVT_WIZARD_CANCEL, self.onCancel )
		self.wizard.Bind( wiz.EVT_WIZARD_HELP,
			lambda evt: Utils.showHelp('Menu-DataMgmt.html#import-course-in-gpx-format') )
		self.wizard.Bind( wiz.EVT_WIZARD_FINISHED, self.summaryPage.doFixCategoryDistances )
		
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
			except :
				Utils.MessageOK( self.wizard, 'Read error:  Is this GPX file properly formatted? (%s)' % sys.exc_info()[0],
								title='Read Error', iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
			
			# Check for too few points.
			if geoTrack.numPoints < 2:
				Utils.MessageOK( self.wizard,
					'Import Failed:  GPX file contains fewer than two points.',
					title='File Format Error',
					iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
				
			self.geoTrackFName = fileName
			self.geoTrack = geoTrack
			self.summaryPage.setInfo( self.geoTrackFName, self.geoTrack.numPoints, self.geoTrack.lengthKm, self.geoTrack.totalElevationGain )
			self.useTimesPage.setInfo( self.geoTrackFName )
			
		elif page == self.useTimesPage:
			if self.useTimesPage.getUseTimes():
				self.geoTrack.read( self.geoTrackFName, True )
		elif page == self.summaryPage:
			pass
		elif page == self.fixCategoryDistance:
			pass
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
