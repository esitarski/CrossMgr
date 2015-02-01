
import os
import sys
import wx
import wx.wizard as wiz
import wx.lib.filebrowsebutton as filebrowse
import traceback
import Utils
from Utils import logException
from GeoAnimation import GeoTrack, GpxHasTimes
import Model

class IntroPage(wiz.WizardPageSimple):
	def __init__(self, parent, controller):
		wiz.WizardPageSimple.__init__(self, parent)
		
		self.controller = controller
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Import a GPX File containing coordinates for the course.\nContinue if you want to load or change the GPX course file.')),
					flag=wx.ALL, border = border )
		self.info = wx.TextCtrl(self, value = u'\n\n\n\n\n\n', style=wx.TE_READONLY|wx.TE_MULTILINE, size=(-1,180))
		vbs.Add( self.info, flag=wx.ALL|wx.EXPAND, border = border )
		
		self.removeButton = wx.Button( self, label = _('Remove GPX Course') )
		self.Bind( wx.EVT_BUTTON, self.onRemove, self.removeButton )
		vbs.Add( self.removeButton, flag=wx.ALL|wx.ALIGN_RIGHT, border = border )
		
		self.SetSizer( vbs )
	
	def onRemove( self, event ):
		if self.geoTrack:
			if Utils.MessageOKCancel( self, _('Permanently Remove GPX Course?'), _('Remove GPX Course') ):
				self.controller.clearData()
				self.setInfo( None, None )
		else:
			Utils.MessageOK( self, _('No GPX Course'), _('No GPX Course') )
	
	def setInfo( self, geoTrack, geoTrackFName ):
		self.geoTrack = geoTrack
		if geoTrack:
			s = u'\n\n'.join( [
					_('Existing GPX file:'),
					u'{}: "{}"'.format(('Imported from'), geoTrackFName),
					u'{}: {}'.format(_('Number of Coords'), geoTrack.numPoints),
					u'{}: {:.3f} km, {:.3f} {}'.format(_('Lap Length'), geoTrack.lengthKm, geoTrack.lengthMiles, _('miles')),
					u'{}: {:.0f} m, {:.0f} ft'.format(_('Total Elevation Gain'), geoTrack.totalElevationGainM, geoTrack.totalElevationGainFt),
					u'{}: {}'.format(_('Course Type'), _('Point to Point') if getattr(geoTrack, 'isPointToPoint', False) else _('Loop'))
				] )
		else:
			s = u''
		self.removeButton.Enable( bool(geoTrack) )
		self.info.ChangeValue( s )
		self.GetSizer().Layout()
	
class FileNamePage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Specify the GPX File containing coordinates for the course.') ),
					flag=wx.ALL, border = border )
		fileMask = [
			'GPX Files (*.gpx)|*.gpx',
		]
		self.fbb = filebrowse.FileBrowseButton( self, -1, size=(450, -1),
												labelText = 'GPX File:',
												fileMode=wx.OPEN,
												fileMask='|'.join(fileMask),
												changeCallback = self.setElevationStatus )
												
		self.courseTypeRadioBox = wx.RadioBox( self, choices=[_('Course is a Loop'), _('Course is Point-to-Point')] )
		
		self.elevationCheckBox = wx.CheckBox( self, label = _('Read "elevation.csv" File (in same folder as GPX file)') )
		vbs.Add( self.fbb, flag=wx.ALL, border = border )
		vbs.Add( self.courseTypeRadioBox, flag=wx.ALL, border = border )
		vbs.Add( self.elevationCheckBox, flag=wx.ALL, border = border )
		self.setElevationStatus()
		
		self.SetSizer( vbs )
	
	def setElevationStatus( self, evt = None ):
		fileNameElevation = os.path.join( os.path.dirname(self.fbb.GetValue()), 'elevation.csv' )
		exists = os.path.isfile(fileNameElevation)
		self.elevationCheckBox.Enable( exists )
		self.elevationCheckBox.SetValue( exists )
	
	def setInfo( self, geoTrackFName ):
		if geoTrackFName:
			self.fbb.SetValue( geoTrackFName )
			self.setElevationStatus()
		else:
			self.fbb.SetValue( '' )
			self.elevationCheckBox.SetValue( False )
		self.GetSizer().Layout()
	
	def getFileName( self ):
		return self.fbb.GetValue()
		
	def getUseElevation( self ):
		return self.elevationCheckBox.GetValue()
		
	def getIsPointToPoint( self ):
		return self.courseTypeRadioBox.GetSelection() == 1

class UseTimesPage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		self.noTimes = wx.StaticText(self, label = _('This GPX file does not contain times.\n\nRace times will be calculated based on distance and elevation.') )
		vbs.Add( self.noTimes, flag=wx.ALL, border = border )
		
		self.useTimes = wx.CheckBox(self, label = _('Use times in the GPX file for more realistic animation') )
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
		vbs.Add( wx.StaticText(self, label = u'{}:'.format(_('Summary'))), flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = u' '), flag=wx.ALL, border = border )

		self.fileLabel = wx.StaticText( self, label = u'{}:'.format(_('GPX File')) )
		self.fileName = wx.StaticText(self )

		self.numCoordsLabel = wx.StaticText( self, label = u'{}:'.format(_('Number of Coords')) )
		self.numCoords = wx.StaticText(self )

		self.distanceLabel = wx.StaticText( self, label = u'{}:'.format(_('Lap Length')) )
		self.distance = wx.TextCtrl(self, style=wx.TE_READONLY)

		self.totalElevationGainLabel = wx.StaticText( self, label = u'{}:'.format(_('Total Elevation Gain')) )
		self.totalElevationGain = wx.TextCtrl(self, style=wx.TE_READONLY)

		self.courseTypeLabel = wx.StaticText( self, label = u'{}:'.format(_('Course is')) )
		self.courseType = wx.TextCtrl(self, style=wx.TE_READONLY)

		self.setCategoryDistanceLabel = wx.StaticText( self )
		self.setCategoryDistanceCheckbox = wx.CheckBox( self, label = _('Set Category Distances to GPX Lap Length') )
		self.setCategoryDistanceCheckbox.SetValue( True )

		fbs = wx.FlexGridSizer( rows=0, cols=2, hgap=5, vgap=2 )
		fbs.AddGrowableCol( 1 )
		
		labelAlign = wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL
		fbs.AddMany( [(self.fileLabel, 0, labelAlign),			(self.fileName, 	1, wx.EXPAND|wx.GROW),
					  (self.numCoordsLabel, 0, labelAlign),		(self.numCoords, 	1, wx.EXPAND|wx.GROW),
					  (self.distanceLabel, 0, labelAlign),		(self.distance,		1, wx.EXPAND|wx.GROW),
					  (self.totalElevationGainLabel, 0, labelAlign),(self.totalElevationGain,		1, wx.EXPAND|wx.GROW),
					  (self.courseTypeLabel, 0, labelAlign),(self.courseType,		1, wx.EXPAND|wx.GROW),
					  (wx.StaticText(self), 0, labelAlign),			(wx.StaticText(self), 1, wx.EXPAND|wx.GROW),
					  (self.setCategoryDistanceLabel, 0, labelAlign), (self.setCategoryDistanceCheckbox, 1, wx.EXPAND|wx.GROW),
					 ] )
		
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
	
	def setInfo( self, fileName, numCoords, distance, totalElevationGain, isPointToPoint ):
		self.fileName.SetLabel( fileName )
		self.numCoords.SetLabel( u'%d' % numCoords )
		self.distanceKm = distance
		self.distanceMiles = distance*0.621371
		self.distance.ChangeValue( u'%.3f km, %.3f miles' % (self.distanceKm, self.distanceMiles) )
		self.totalElevationGainM = totalElevationGain
		self.totalElevationGainFt = totalElevationGain*3.28084
		self.totalElevationGain.ChangeValue( u'%.0f m, %.0f ft' % (self.totalElevationGainM, self.totalElevationGainFt) )
		self.courseType.ChangeValue( _('Point to Point') if isPointToPoint else _('Loop') )
		
class GetGeoTrack( object ):
	def __init__( self, parent, geoTrack = None, geoTrackFName = None ):
		img_filename = os.path.join( Utils.getImageFolder(), 'gps.png' )
		bitmap = wx.Bitmap(img_filename) if img_filename and os.path.exists(img_filename) else wx.NullBitmap
		
		self.parent = parent
		prewizard = wiz.PreWizard()
		prewizard.SetExtraStyle( wiz.WIZARD_EX_HELPBUTTON )
		prewizard.Create( parent, title = _('Import GPX Course File'), bitmap = bitmap )
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
					message = _('Please specify a GPX file.')
				else:
					message = u'{}:\n\n    "{}"\n\n{}'.format(
							_('Cannot open file'), fileName,
							_('Please check the file name and/or its read permissions.'),
						)
				Utils.MessageOK( self.wizard, message, title=_('File Open Error'), iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
			
			# Check for valid content.
			geoTrack = GeoTrack()
			try:
				geoTrack.read( fileName, isPointToPoint = self.fileNamePage.getIsPointToPoint() )
			except Exception as e:
				logException( e, sys.exc_info() )
				Utils.MessageOK( self.wizard, '{}:  {}\n({})'.format(_('Read Error'), _('Is this GPX file properly formatted?'), e),
								title='Read Error', iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
			
			# Check for too few points.
			if geoTrack.numPoints < 2:
				Utils.MessageOK( self.wizard,
					u'{}: {}'.format(_('Import Failed'), _('GPX file contains fewer than two points.')),
					title=_('File Format Error'),
					iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
			
			if self.fileNamePage.getUseElevation():
				fileNameElevation = os.path.join( os.path.dirname(fileName), 'elevation.csv' )
				try:
					open(fileNameElevation).close()
				except IOError as e:
					logException( e, sys.exc_info() )
					message = u'{}: {}\n\n    "{}"\n\n{}'.format(
							_('Cannot Open Elevation File'), e, fileNameElevation,
							_('Please check the file name and/or its read permissions.'),
						)
					Utils.MessageOK( self.wizard, message, title=_('File Open Error'), iconMask=wx.ICON_ERROR)
				else:
					try:
						geoTrack.readElevation( fileNameElevation )
					except Exception as e:
						logException( e, sys.exc_info() )
						message = u'{}: {}\n\n    "{}"'.format(_('Elevation File Error'), e, fileNameElevation )
						Utils.MessageOK( self.wizard, message, title=_('File Read Error'), iconMask=wx.ICON_ERROR )
				
			self.geoTrackFName = fileName
			self.geoTrack = geoTrack
			self.summaryPage.setInfo(	self.geoTrackFName, self.geoTrack.numPoints,
										self.geoTrack.lengthKm, self.geoTrack.totalElevationGainM,
										getattr( self.geoTrack, 'isPointToPoint', False) )
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
		
