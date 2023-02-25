
import os
import sys
import wx
import wx.adv as adv
import wx.lib.filebrowsebutton as filebrowse
import traceback
import Utils
from Utils import logException
from GeoAnimation import GeoTrack, ParseGpxFile, GreatCircleDistance, CompassBearing
import Model
import HelpSearch
from GpxParse import GpxParse
import datetime
import tzlocal
from ReorderableGrid import ReorderableGrid
import wx.grid as gridlib

class IntroPage(adv.WizardPageSimple):
	def __init__(self, parent, controller):
		super().__init__(parent)
		
		self.controller = controller
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _("Import a GPX File containing a rider's laps.\nThe track must contain times as well as positions.")),
					flag=wx.ALL, border = border )
		self.info = wx.TextCtrl(self, value = '\n\n\n\n\n\n', style=wx.TE_READONLY|wx.TE_MULTILINE, size=(-1,180))
		vbs.Add( self.info, flag=wx.ALL|wx.EXPAND, border = border )
		
		self.fileHeading = wx.StaticText(self, label = _("Specify the GPX File containing the rider's recorded race:") )
		vbs.Add( self.fileHeading, flag=wx.ALL, border = border )
		fileMask = [
			'GPX Files (*.gpx)|*.gpx',
		]
		self.fbb = filebrowse.FileBrowseButton( self, -1, size=(450, -1),
												labelText = 'GPX File:',
												fileMode=wx.FD_OPEN,
												fileMask='|'.join(fileMask),
												startDirectory=Utils.getFileDir() )
		self.fbb.SetValue('/home/kim/documents/programming/CrossMgr/CrossMgr-test/2022-10-16_Track_2022-10-16 133507.gpx')
		vbs.Add( self.fbb, flag=wx.ALL, border = border )
		hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.bibHeading = wx.StaticText(self, label = _("Rider's bib number:") )
		hbs.Add( self.bibHeading, flag=wx.ALL, border = border )
		self.bibEntry = wx.TextCtrl( self, value="1" )
		hbs.Add( self.bibEntry, flag=wx.ALL, border = border )
		vbs.Add(hbs)
		
		self.SetSizer( vbs )
	
	def setInfo( self, geoTrack, geoTrackFName ):
		self.geoTrack = geoTrack
		if geoTrack:
			startLineLat = geoTrack.asCoordinates()[1];
			startLineLon = geoTrack.asCoordinates()[0];
			s = '\n'.join( [
					_('Course info:'),
					'{}: "{}"'.format(('Imported from'), geoTrackFName),
					'{}: {:.6f},{:.6f}'.format(_('Start Line coordinates'), startLineLat, startLineLon),
					'{}: {:.3f} km, {:.3f} {}'.format(_('Lap Length'), geoTrack.lengthKm, geoTrack.lengthMiles, _('miles'))
				] )
		else:
			s = 'A GPX course must be loaded first!\nSee Properties: GPX'
			self.fileHeading.Disable()
			self.fbb.Disable()
			self.bibHeading.Disable()
			self.bibEntry.Disable()
		self.info.ChangeValue( s )
		self.GetSizer().Layout()
		
	def getFileName( self ):
		return self.fbb.GetValue()
	
	def getBib( self ):
		return self.bibEntry.GetValue()

class UseTimesPage(adv.WizardPageSimple):
	headerNames = ['Time of Day', 'Race\nTime', 'Lat (°)', 'Long (°)', 'Distance\n(km)', 'Proximity\nto start (m)', 'Bearing\nfrom finish (°)', 'Import\nlap']
	
	def __init__(self, parent):
		super().__init__(parent)
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		self.noTimes = wx.StaticText(self, label = _('This GPX file does not contain times.\nCannot continue!') )
		vbs.Add( self.noTimes, flag=wx.ALL, border = border )
		hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.proxFilterHeading = wx.StaticText(self, label = _("Filter by proximity to finish line (m):") )
		hbs.Add( self.proxFilterHeading, flag=wx.ALL, border = border )
		self.proxFilterEntry = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER, value="50" )
		self.proxFilterEntry.Bind( wx.EVT_TEXT_ENTER, self.onFilterEntry )
		hbs.Add( self.proxFilterEntry, flag=wx.ALL, border = border )
		vbs.Add(hbs)
		
		
		hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.timeOffsetHeading = wx.StaticText(self, label = _("Race clock offset relative to GPS time (seconds):") )
		hbs.Add( self.timeOffsetHeading, flag=wx.ALL, border = border )
		self.timeOffsetEntry = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER, value="0" )
		self.timeOffsetEntry.Bind( wx.EVT_TEXT_ENTER, self.onFilterEntry )
		hbs.Add( self.timeOffsetEntry, flag=wx.ALL, border = border )
		vbs.Add(hbs)
		
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.CreateGrid( 0, len(self.headerNames) )
		self.grid.SetColFormatBool( 7 )
		self.grid.SetColLabelSize( 64 )
		self.grid.SetRowLabelSize( 0 )
		self.grid.EnableReorderRows( False )
		self.grid.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doCellRightClick )
		self.grid.Bind( wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.doCellClick )
		self.sortCol = None
		
		vbs.Add(self.grid, 1, flag=wx.EXPAND|wx.TOP|wx.ALL, border = 4)
		
		self.SetSizer( vbs )
		
	def doCellClick( self, event ):
		if event.GetCol() == len(self.headerNames) -1:
			col = len(self.headerNames) - 1
			row = event.GetRow()
			v = self.grid.GetCellValue( row, col )
			if v == "":
				self.grid.SetCellValue( row, col, "1" )
			else:
				self.grid.SetCellValue( row, col, "" )
			

	def doCellRightClick( self, event ):
		# copy to clipboard option here?
		pass
	
	def onFilterEntry( self, event ):
		self.refresh()
	
	def refresh( self ):
		self.grid.ClearGrid()
		if (self.grid.GetNumberRows() > 0):
			self.grid.DeleteRows( 0, self.grid.GetNumberRows() )
		for col, headerName in enumerate(self.headerNames):
			self.grid.SetColLabelValue( col, headerName )
			attr = gridlib.GridCellAttr()
			attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_TOP )
			attr.SetReadOnly( True )
			self.grid.SetColAttr( col, attr )
		
		timeOffset = datetime.timedelta( seconds=float( self.timeOffsetEntry.GetValue() ) )
		startLineLat = self.geoTrack.asCoordinates()[1]
		startLineLon = self.geoTrack.asCoordinates()[0]
		proxFilter = float( self.proxFilterEntry.GetValue() )
		row = 0
		distance = 0
		laps = 0
		prevLat = self.latLonEleTimes[0][0]
		prevLon = self.latLonEleTimes[0][1]
		prevBearing = 0
		prevProx = 0
		prevProxDecreasing = False
		for latLonEleTime in self.latLonEleTimes:   #fixme interpolate data points for < 1 pps GPX
			wallTime = latLonEleTime[3]
			if isinstance( wallTime, datetime.datetime ):
				wallTime += timeOffset
				raceTime = wallTime - self.raceStartTime
				if raceTime < datetime.timedelta():
					raceTime = datetime.timedelta()
				lat = latLonEleTime[0]
				lon = latLonEleTime[1]
				distance += GreatCircleDistance( prevLat, prevLon, lat, lon )
				prox = GreatCircleDistance( startLineLat, startLineLon, lat, lon )
				bearing = CompassBearing( startLineLat, startLineLon, lat, lon )
				if (prox - prevProx < 0):
					proxDecreasing = True
				else:
					proxDecreasing = False
				if prox <= proxFilter:
					self.grid.InsertRows( pos=row+1, numRows=1)
					self.grid.SetCellValue( row, 0, '{}'.format(wallTime or '') )
					self.grid.SetCellAlignment(row, 0, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					if raceTime > datetime.timedelta():
						self.grid.SetCellValue( row, 1, '{}'.format(str(raceTime).split('.')[0]) )
					self.grid.SetCellAlignment(row, 1, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellValue( row, 2, '{:.6f}'.format(lat or 0) )
					self.grid.SetCellAlignment(row, 2, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellValue( row, 3, '{:.6f}'.format(lon or 0) )
					self.grid.SetCellAlignment(row, 3, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellValue( row, 4, '{:.2f}'.format(distance/1000 or 0) )
					self.grid.SetCellAlignment(row, 4, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellValue( row, 5, '{:.2f}'.format(prox or 0) )
					self.grid.SetCellAlignment(row, 5, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellValue( row, 6, '{:.1f}'.format(bearing or 0) )
					self.grid.SetCellAlignment(row, 6, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellRenderer(row, 7, gridlib.GridCellBoolRenderer())
					self.grid.SetCellEditor(row, 7, gridlib.GridCellBoolEditor())
					self.grid.SetCellValue(row, 7, "")
					if raceTime >= self.minPossibleLapTime:
						# fixme filter by lap length?
						setLap = False
						if (abs(prevBearing - bearing) > 90 and abs(prevBearing - bearing) < 300) and (not proxDecreasing and prevProxDecreasing):
							setLap = True
							self.grid.SetCellBackgroundColour( row, 5, wx.Colour(153, 205, 255) )
							self.grid.SetCellBackgroundColour( row, 6, wx.Colour(153, 205, 255) )
						elif (not proxDecreasing and prevProxDecreasing):
							setLap = True
							self.grid.SetCellBackgroundColour( row, 5, wx.Colour(153, 205, 255) )
						elif (abs(prevBearing - bearing) > 90 and abs(prevBearing - bearing) < 300):
							setLap = True
							self.grid.SetCellBackgroundColour( row, 6, wx.Colour(153, 205, 255) )
						else:
							self.grid.SetCellValue(row, 7, "")
						if setLap:
							self.grid.SetCellValue(row, 7, "1")
							laps += 1
							#if the previous lap is set, unset it
							if row > 0:
								prevSetLap = self.grid.GetCellValue( row - 1, 7 )
								if prevSetLap == "1":
									self.grid.SetCellValue( row - 1, 7, "" )
					row += 1
				prevLat = lat
				prevLon = lon
				prevBearing = bearing
				prevProx = prox
				prevProxDecreasing = proxDecreasing
				
		if distance > 0:
			self.noTimes.Hide()
		self.grid.AutoSize()
		self.GetSizer().Layout()
		self.grid.EnableEditing(True)
		
	def setInfo( self, geoTrack, riderBib, latLonEleTimes, raceStartTime, minPossibleLapTime = 0 ):
		self.geoTrack = geoTrack
		self.riderBib = riderBib
		self.latLonEleTimes = latLonEleTimes  
		self.raceStartTime = raceStartTime
		self.minPossibleLapTime = datetime.timedelta( seconds=minPossibleLapTime )
		local_tz = tzlocal.get_localzone()
		tz_offset = int(raceStartTime.astimezone(local_tz).utcoffset().total_seconds())
		self.timeOffsetEntry.SetValue( str(tz_offset) )
		self.refresh()
		
	def getLapTimes( self ):
		lapTimes = []
		for row in range(self.grid.GetNumberRows()):
			if self.grid.GetCellValue( row, len(self.headerNames) -1 ) == "1":
				try:
					dt = datetime.datetime.strptime(self.grid.GetCellValue( row, 1 ),'%H:%M:%S')
					seconds = dt.second + dt.minute*60 + dt.hour*3600
					lapTimes.append( seconds )
				except ValueError:
					pass
		return lapTimes
		
class SummaryPage(adv.WizardPageSimple):
	def __init__(self, parent):
		super().__init__(parent)
		self.headerNames = ['RaceTime']
		self.bib = 0
		self.lapTimes = []
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		self.bibHeader = wx.StaticText( self )
		vbs.Add( self.bibHeader, flag=wx.ALL, border = border )
		self.fileName = wx.StaticText( self )
		vbs.Add( self.fileName, flag=wx.ALL, border = border )
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.CreateGrid( 0, len(self.headerNames) )
		self.grid.SetColLabelSize( 64 )
		self.grid.SetRowLabelSize( 0 )
		self.grid.EnableReorderRows( False )
		self.sortCol = None
		for col, headerName in enumerate(self.headerNames):
			self.grid.SetColLabelValue( col, headerName )
			attr = gridlib.GridCellAttr()
			attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_TOP )
			attr.SetReadOnly( True )
			self.grid.SetColAttr( col, attr )
		vbs.Add(self.grid, 1, flag=wx.EXPAND|wx.TOP|wx.ALL, border = 4)
		self.SetSizer(vbs)
	
	def setInfo( self, bib, riderName, fileName, lapTimes ):
		self.bib = bib
		self.bibHeader.SetLabel( str(len(lapTimes)) + ' lap times for rider #' + str(self.bib) + ' ' + riderName + ' will be imported from:' )
		self.fileName.SetLabel( fileName )
		self.lapTimes = lapTimes
		row = 0
		for lap in lapTimes:
			td = datetime.timedelta(seconds = lap)
			self.grid.InsertRows( pos=row+1, numRows=1)
			self.grid.SetCellValue( row, 0, '{}'.format(td or '') )
			self.grid.SetCellAlignment(row, 0, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
			row += 1
		self.grid.AutoSize()
		self.GetSizer().Layout()
		self.grid.EnableEditing(False)
		
class GetRiderTimes:
	def __init__( self, parent, race = None):
		self.race = race
		self.geoTrack = getattr(self.race, 'geoTrack', None)
		self.geoTrackFName = getattr(race, 'geoTrackFName', '')
		img_filename = os.path.join( Utils.getImageFolder(), 'gps.png' )
		bitmap = wx.Bitmap(img_filename) if img_filename and os.path.exists(img_filename) else wx.NullBitmap
		
		self.parent = parent
		self.wizard = adv.Wizard()
		self.wizard.SetExtraStyle( adv.WIZARD_EX_HELPBUTTON )
		self.wizard.Create( parent, title = _('Import times from GPX file'), bitmap = bitmap )
		
		self.introPage		= IntroPage( self.wizard, self )
		self.useTimesPage	= UseTimesPage( self.wizard )
		self.summaryPage	= SummaryPage( self.wizard )
		
		self.wizard.Bind( adv.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		self.wizard.Bind( adv.EVT_WIZARD_CANCEL, self.onCancel )
		self.wizard.Bind( adv.EVT_WIZARD_HELP,
			lambda evt: HelpSearch.showHelp('Menu-DataMgmt.html#import-riders-times-from-gpx') )
		
		if self.geoTrack:
			adv.WizardPageSimple.Chain( self.introPage, self.useTimesPage )
			adv.WizardPageSimple.Chain( self.useTimesPage, self.summaryPage )

		self.wizard.SetPageSize( wx.Size(1032,800) )
		self.wizard.GetPageAreaSizer().Add( self.introPage )
		
		
		
		self.introPage.setInfo( self.geoTrack, self.geoTrackFName )

	def show( self ):
		if self.wizard.RunWizard(self.introPage):
			return( self.bib, self.lapTimes )
	
	def onCancel( self, evt ):
		page = evt.GetPage()
		if page == self.introPage:
			pass
		elif page == self.summaryPage:
			pass

		
	def onPageChanging( self, evt ):
		isForward = evt.GetDirection()
		if not isForward:
			return
		page = evt.GetPage()
		
		if page == self.introPage:
			fileName = self.introPage.getFileName()
			riderBib = self.introPage.getBib()
			
			# Check for a valid bib
			try:
				int(riderBib)
			except ValueError:
				Utils.MessageOK( self.wizard, message=_('Bib number must be an integer!'), title=_('Bib error'), iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
			
			# Check for a valid file
			try:
				open(fileName).close()
			except IOError:
				if fileName == '':
					message = _('Please specify a GPX file.')
				else:
					message = '{}:\n\n    "{}"\n\n{}'.format(
							_('Cannot open file'), fileName,
							_('Please check the file name and/or its read permissions.'),
						)
				Utils.MessageOK( self.wizard, message, title=_('File Open Error'), iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
			
			# Check for valid content.
			latLonEleTimes = []
			try:
				latLonEleTimes = ParseGpxFile( fileName )
			except Exception as e:
				logException( e, sys.exc_info() )
				Utils.MessageOK( self.wizard, '{}:  {}\n({})'.format(_('Read Error'), _('Is this GPX file properly formatted?'), e),
								title='Read Error', iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
			
			# Check for too few points.
			if len(latLonEleTimes) < 2:
				Utils.MessageOK( self.wizard,
					'{}: {}'.format(_('Import Failed'), _('GPX file contains fewer than two points.')),
					title=_('File Format Error'),
					iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
			
			# Check for valid times.
			haveTimes = False
			for latLonEleTime in latLonEleTimes:
				t = latLonEleTime[3]
				if isinstance( t, datetime.datetime ):
					haveTimes = True
					break
			if not haveTimes:
				Utils.MessageOK( self.wizard, message=_('GPX file does not contain any time data!'), title=_('GPX error'), iconMask=wx.ICON_ERROR)
				evt.Veto()
				return
			self.latLonEleTimes = latLonEleTimes
			self.useTimesPage.setInfo( self.geoTrack, riderBib, latLonEleTimes, self.race.startTime, self.race.minPossibleLapTime )
			
			
		elif page == self.useTimesPage:
			self.bib = self.introPage.getBib()
			self.lapTimes = self.useTimesPage.getLapTimes()
			if self.race is not None:
				try:
					externalInfo = self.race.excelLink.read()
					info = externalInfo.get(int(self.bib), {})
					riderName = ', '.join( n for n in [info.get('LastName', ''), info.get('FirstName', '')] if n )
				except AttributeError:
					riderName = ''
			self.summaryPage.setInfo( self.bib, riderName, self.introPage.getFileName(), self.lapTimes )
			
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()

