
import os
import wx
import wx.wizard as wiz
import wx.lib.filebrowsebutton as filebrowse
from GeoAnimation import GeoTrack
import Utils

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
												labelText = 'GPX Files:',
												fileMode=wx.OPEN,
												fileMask='|'.join(fileMask) )
		vbs.Add( self.fbb, flag=wx.ALL, border = border )
		
		self.SetSizer( vbs )
	
	def setFileName( self, fileName ):
		self.fbb.SetValue( fileName )
	
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
		self.distance = wx.StaticText( self, wx.ID_ANY, '' )
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
		self.distance.SetLabel( '%.3f km, %.3f miles' % (distance/1000.0, distance*0.621371/1000.0) )
		
class GetGeoTrack( object ):
	def __init__( self, parent, geoTrackFName = None ):
		img_filename = os.path.join( Utils.getImageFolder(), 'gps.png' )
		img = wx.Bitmap(img_filename) if img_filename and os.path.exists(img_filename) else wx.NullBitmap
		
		prewizard = wiz.PreWizard()
		prewizard.SetExtraStyle( wiz.WIZARD_EX_HELPBUTTON )
		prewizard.Create( parent, wx.ID_ANY, 'Import GPX file', img )
		self.wizard = prewizard
		self.wizard.Bind( wiz.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		self.wizard.Bind( wiz.EVT_WIZARD_HELP,
			lambda evt: Utils.showHelp('Menu-DataMgmt.html#import-gpx-file') )
		
		self.fileNamePage = FileNamePage( self.wizard )
		self.summaryPage = SummaryPage( self.wizard )
		
		wiz.WizardPageSimple_Chain( self.fileNamePage, self.summaryPage )

		self.geoTrackFName = geoTrackFName
		if geoTrackFName:
			self.fileNamePage.setFileName( geoTrackFName )
		self.geoTrack = None

		self.wizard.GetPageAreaSizer().Add( self.fileNamePage )
		self.wizard.SetPageSize( wx.Size(500,200) )
		self.wizard.FitToPage( self.fileNamePage )
	
	def show( self ):
		if self.wizard.RunWizard(self.fileNamePage):
			self.geoTrackFName = self.fileNamePage.getFileName()
		return self.geoTrackFName
	
	def onPageChanging( self, evt ):
		isForward = evt.GetDirection()
		success = True
		if isForward:
			page = evt.GetPage()
			if page == self.fileNamePage:
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
						self.summaryPage.setInfo( fileName, len(self.geoTrack.gpsPoints), self.geoTrack.length )
					except:
						Utils.MessageOK( self.wizard, 'File format error (is this a GPX file?)', title='GPX Format Error', iconMask=wx.ICON_ERROR)
						success = False
						self.geoTrack = None
						evt.Veto()
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
