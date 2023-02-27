
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
import numpy
import re
from ReorderableGrid import ReorderableGrid
import wx.grid as gridlib

class IntroPage(adv.WizardPageSimple):
	def __init__(self, parent, controller ):
		super().__init__(parent)
		self.controller = controller
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _("Attempt to derive a rider's lap times from a GPX recording of the race...")),
					flag=wx.ALL, border = border )
		self.info = wx.TextCtrl(self, value = '\n\n\n\n\n\n', style=wx.TE_READONLY|wx.TE_MULTILINE, size=(-1,180))
		vbs.Add( self.info, flag=wx.ALL|wx.EXPAND, border = border )
		
		self.fileHeading = wx.StaticText(self, label = _("Select the GPX File containing the rider's recording.\nThe track must contain timestamps as well as positions.") )
		vbs.Add( self.fileHeading, flag=wx.ALL, border = border )
		fileMask = [
			'GPX Files (*.gpx)|*.gpx',
		]
		self.fbb = filebrowse.FileBrowseButton( self, -1, size=(450, -1),
												labelText = 'GPX File:',
												fileMode=wx.FD_OPEN,
												fileMask='|'.join(fileMask),
												startDirectory=Utils.getFileDir(),
												changeCallback=self.fbbChange)
		self.fbb.SetValue('')
		vbs.Add( self.fbb, flag=wx.ALL, border = border )
		hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.bibHeading = wx.StaticText(self, label = _("Rider's bib number:") )
		hbs.Add( self.bibHeading, flag=wx.ALL, border = border )
		self.bibEntry = wx.TextCtrl( self, value="" )
		hbs.Add( self.bibEntry, flag=wx.ALL, border = border )
		vbs.Add(hbs)
		
		self.SetSizer( vbs )
		
	def fbbChange( self, evt ):
		#pre-populate the bib field if there's a rider number in the GPX filename
		filename = os.path.basename(self.fbb.GetValue()).lower()
		try:
			splitat = filename.find('bib')+3
			bib = re.split(r'\D+', filename[splitat:])[0]
			self.bibEntry.SetValue( bib )
			return
		except ValueError:
			pass
		try:
			splitat = filename.find('rider')+3
			bib = re.split(r'\D+', filename[splitat:])[0]
			self.bibEntry.SetValue( bib )
			return
		except ValueError:
			pass
		self.bibEntry.SetValue( '' )
	
	def setInfo( self, geoTrack, geoTrackFName ):
		if geoTrack:
			startLineLat = geoTrack.asCoordinates()[1];  #list is lon, lat
			startLineLon = geoTrack.asCoordinates()[0];
			if getattr( geoTrack, 'isPointToPoint', False):
				finishLineLat = geoTrack.asCoordinates()[-1]  #last element in list
				finishLineLon = geoTrack.asCoordinates()[-2]  #penultimate element in list
			else:  #course is a loop
				finishLineLat = startLineLat
				finishLineLon = startLineLon
			s = '\n'.join( [
					_('Course info:'),
					'{}: "{}"'.format(('Imported from'), geoTrackFName),
					'{}: {:.6f},{:.6f}'.format(_('Start line coordinates'), startLineLat, startLineLon),
					'{}: {:.6f},{:.6f}'.format(_('Finish line coordinates'), finishLineLat, finishLineLon),
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
	headerNames = ['Time of Day\n(local)', 'Race\nTime', 'Lat (°)', 'Long (°)', 'Race\n(km)', 'Lap\n(km)', 'Proximity\nto start (m)', 'Bearing\n(°)', 'Import\nlap']
	
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
		self.proxFilterEntry.Bind( wx.EVT_TEXT_ENTER, self.onChangeSetting )
		hbs.Add( self.proxFilterEntry, flag=wx.ALL, border = border )
		vbs.Add(hbs)
		
		hbs = wx.BoxSizer(wx.HORIZONTAL)
		self.timeOffsetHeading = wx.StaticText(self, label = _("Race clock offset relative to GPS time (seconds):") )
		hbs.Add( self.timeOffsetHeading, flag=wx.ALL, border = border )
		self.timeOffsetEntry = wx.TextCtrl( self, style=wx.TE_PROCESS_ENTER, value="0" )
		self.timeOffsetEntry.Bind( wx.EVT_TEXT_ENTER, self.onChangeSetting )
		hbs.Add( self.timeOffsetEntry, flag=wx.ALL, border = border )
		vbs.Add(hbs)
		
		self.interpolateEntry = wx.CheckBox( self, label='Interpolate trackpoints', name='Interpolate')
		self.interpolateEntry.Bind( wx.EVT_CHECKBOX, self.onChangeSetting )
		self.interpolateEntry.SetValue( True )
		vbs.Add( self.interpolateEntry, flag=wx.ALL, border = border )
		
		
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
			self.updateLapDistances()
			

	def doCellRightClick( self, event ):
		# copy to clipboard option here?
		pass
	
	def onChangeSetting( self, event ):
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
		if getattr( self.geoTrack, 'isPointToPoint', False):
			finishLineLat = geoTrack.asCoordinates()[-1]  #last element in list
			finishLineLon = geoTrack.asCoordinates()[-2]  #penultimate element in list
		else:  #course is a loop
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
		latLonTimeInterpeds = []
		lastLapAtDistance = 0
		lapDistance = 0
		if self.interpolateEntry.GetValue():
			latLonTimeInterpeds = self.interpolatePoints(self.latLonEleTimes, step=1)
		else:
			latLonTimeInterpeds = self.interpolatePoints(self.latLonEleTimes, step=0)
		for latLonTimeInterp in latLonTimeInterpeds:
			wallTime = latLonTimeInterp[2]
			if isinstance( wallTime, datetime.datetime ):
				wallTime += timeOffset
				raceTime = wallTime - self.raceStartTime
				if raceTime < datetime.timedelta():
					raceTime = datetime.timedelta()
				lat = latLonTimeInterp[0]
				lon = latLonTimeInterp[1]
				distance += GreatCircleDistance( prevLat, prevLon, lat, lon )
				lapDistance = distance - lastLapAtDistance
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
						self.grid.SetCellValue( row, 1, '{}.{:03.0f}'.format( str(raceTime).split('.')[0], raceTime.microseconds//1000 ) )
					self.grid.SetCellAlignment(row, 1, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellValue( row, 2, '{:.6f}'.format(lat or 0) )
					self.grid.SetCellAlignment(row, 2, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellValue( row, 3, '{:.6f}'.format(lon or 0) )
					self.grid.SetCellAlignment(row, 3, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellValue( row, 4, '{:.2f}'.format(distance/1000 or 0) )
					self.grid.SetCellAlignment(row, 4, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellValue( row, 5, '{:.2f}'.format(lapDistance/1000 or 0) )
					self.grid.SetCellAlignment(row, 4, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellValue( row, 6, '{:.2f}'.format(prox or 0) )
					self.grid.SetCellAlignment(row, 6, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellValue( row, 7, '{:.1f}'.format(bearing or 0) )
					self.grid.SetCellAlignment(row, 7, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
					self.grid.SetCellRenderer(row, len(self.headerNames)-1, gridlib.GridCellBoolRenderer())
					self.grid.SetCellEditor(row, len(self.headerNames)-1, gridlib.GridCellBoolEditor())
					self.grid.SetCellValue(row, len(self.headerNames)-1, "")
					if latLonTimeInterp[3]:  #point was interpolated, shade yellow to indicate fictional data
						for col in range(self.grid.GetNumberCols() - 1):
							self.grid.SetCellBackgroundColour( row, col, wx.Colour( 255, 255, 0 ) )
					withinMinLapLength = False
					if (abs(self.geoTrack.lengthKm * 1000 - lapDistance)) < proxFilter:  #shade if we're within filter distance of lap length
						self.grid.SetCellBackgroundColour( row, 5, wx.Colour(153, 205, 255) )
						withinMinLapLength = True
					if raceTime >= self.minPossibleLapTime:
						#look for new laps and shade/select
						setLap = False
						if (abs(prevBearing - bearing) > 90 and abs(prevBearing - bearing) < 300) and (not proxDecreasing and prevProxDecreasing):
							setLap = True
							self.grid.SetCellBackgroundColour( row, 6, wx.Colour(153, 205, 255) )
							self.grid.SetCellBackgroundColour( row, 7, wx.Colour(153, 205, 255) )
						elif (not proxDecreasing and prevProxDecreasing):
							setLap = True
							self.grid.SetCellBackgroundColour( row, 6, wx.Colour(153, 205, 255) )
						elif (abs(prevBearing - bearing) > 90 and abs(prevBearing - bearing) < 300):
							setLap = True
							self.grid.SetCellBackgroundColour( row, 7, wx.Colour(153, 205, 255) )
						else:
							self.grid.SetCellValue(row, len(self.headerNames)-1, "")
						if setLap and withinMinLapLength:
							self.grid.SetCellValue(row, len(self.headerNames)-1, "1")
							lastLapAtDistance = distance
							laps += 1
							#if the previous lap is set, unset it
							if row > 0:
								prevSetLap = self.grid.GetCellValue( row - 1, len(self.headerNames)-1 )
								if prevSetLap == "1":
									self.grid.SetCellValue( row - 1, len(self.headerNames)-1, "" )
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
		self.grid.ForceRefresh()
		
	def updateLapDistances( self ):
		proxFilter = float( self.proxFilterEntry.GetValue() )
		lastLapAtKm = 0
		lapDistance = 0
		for row in range(self.grid.GetNumberRows()):
			distance = float(self.grid.GetCellValue( row, 4 ) )
			lapDistance = distance - lastLapAtKm
			self.grid.SetCellValue( row, 5, '{:.2f}'.format(lapDistance or 0) )
			self.grid.SetCellAlignment(row, 4, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
			if (abs(self.geoTrack.lengthKm - lapDistance)) < proxFilter/1000:
				self.grid.SetCellBackgroundColour( row, 5, wx.Colour(153, 205, 255) )
			else:
				self.grid.SetCellBackgroundColour( row, 5, wx.Colour(255, 255, 255) )
			if self.grid.GetCellValue( row, len(self.headerNames)-1 ):
				lastLapAtKm = distance
				if row > 0 and self.grid.GetCellValue( row -1, len(self.headerNames)-1 ):
					self.grid.SetCellBackgroundColour( row -1, len(self.headerNames)-1, wx.Colour( 255, 165, 0 ) )
					self.grid.SetCellBackgroundColour( row, len(self.headerNames)-1, wx.Colour( 255, 165, 0 ) )
				else:
					self.grid.SetCellBackgroundColour( row, len(self.headerNames)-1, wx.Colour(255, 255, 255) )
			else:
				self.grid.SetCellBackgroundColour( row, len(self.headerNames)-1, wx.Colour(255, 255, 255) )
		self.grid.ForceRefresh()  #needed to make colour changes update
			
	def interpolatePoints( self, latLonEleTimes, step = 0):
		times = []
		lats = []
		lons = []
		for latLonEleTime in latLonEleTimes:
			if isinstance( latLonEleTime[3], datetime.datetime ):
				lats.append(latLonEleTime[0])
				lons.append(latLonEleTime[1])
				times.append(latLonEleTime[3].timestamp())
		if step > 0:  #simple linear interpolation, could be improved
			startTime = times[0]
			endTime = times[-1]
			intervals = numpy.arange( startTime, endTime, step )
			interpLats = numpy.interp(intervals, times, lats)
			interpLons = numpy.interp(intervals, times, lons)
		else: #if step is 0, don't interpolate
			intervals = times
			interpLats = lats
			interpLons = lons
		latLonTimeInterpeds = []
		for i in range(len(intervals)):
			interpolatedPoint = not (intervals[i] in times)
			tup = (interpLats[i], interpLons[i], datetime.datetime.fromtimestamp(intervals[i]), interpolatedPoint)
			latLonTimeInterpeds.append( tup )
		return(latLonTimeInterpeds)
		
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
					dt = datetime.datetime.strptime(self.grid.GetCellValue( row, 1 ),'%H:%M:%S.%f')
					seconds = dt.second + dt.minute*60 + dt.hour*3600 + dt.microsecond/1000000
					lapTimes.append( seconds )
				except ValueError:
					pass
		return lapTimes
		
class SummaryPage(adv.WizardPageSimple):
	def __init__(self, parent):
		super().__init__(parent)
		self.headerNames = ['Race Time', 'Lap Time']
		self.bib = 0
		self.lapTimes = []
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		self.bibHeader = wx.StaticText( self )
		vbs.Add( self.bibHeader, flag=wx.ALL, border = border )
		self.fileName = wx.StaticText( self )
		vbs.Add( self.fileName, flag=wx.ALL, border = border )
		self.closeTimesWarning = wx.StaticText(self, label = _('\nWARNING: Some of these lap times are smaller than the minimum possible lap time!') )
		vbs.Add( self.closeTimesWarning, flag=wx.ALL, border = border )
		
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
	
	def setInfo( self, bib, riderName, fileName, lapTimes, raceStartTime, minPossibleLapTime ):
		self.bib = bib
		self.bibHeader.SetLabel( str(len(lapTimes)) + ' lap times for rider #' + str(self.bib) + ' ' + riderName + ' will be imported from:' )
		self.fileName.SetLabel( fileName )
		self.lapTimes = lapTimes
		self.raceStartTime = raceStartTime
		self.minPossibleLapTime = minPossibleLapTime
		if (self.grid.GetNumberRows() > 0):
			self.grid.DeleteRows( 0, self.grid.GetNumberRows() )
		row = 0
		prevLapTime = 0
		closeLaps = False
		for lap in lapTimes:
			td = datetime.timedelta(seconds = lap)
			ltd = datetime.timedelta(seconds = lap - prevLapTime)
			self.grid.InsertRows( pos=row+1, numRows=1)
			self.grid.SetCellValue( row, 0, '{}.{:03.0f}'.format( str(td).split('.')[0], td.microseconds//1000 ) )
			self.grid.SetCellAlignment(row, 0, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
			if row == 0:  #lap time == race time
				self.grid.SetCellValue( row, 1, '{}.{:03.0f}'.format( str(td).split('.')[0], td.microseconds//1000 ) )
				self.grid.SetCellAlignment(row, 1, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
				if lap < self.minPossibleLapTime:
					self.grid.SetCellBackgroundColour( row, 1, wx.Colour( 153, 205, 255 ) )
					closeLaps = True
				else:
					self.grid.SetCellBackgroundColour( row, 0, wx.Colour( 255, 255, 255 ) )
			elif row > 0:
				self.grid.SetCellValue( row, 1, '{}.{:03.0f}'.format( str(ltd).split('.')[0], ltd.microseconds//1000 ) )
				self.grid.SetCellAlignment(row, 1, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE_VERTICAL)
				if lap - prevLapTime < self.minPossibleLapTime:
					self.grid.SetCellBackgroundColour( row, 1, wx.Colour( 153, 205, 255 ) )
					closeLaps = True
				else:
					self.grid.SetCellBackgroundColour( row, 0, wx.Colour( 255, 255, 255 ) )
			row += 1
			prevLapTime = lap
		if closeLaps:
			self.closeTimesWarning.Show()
		else:
			self.closeTimesWarning.Hide()
		self.grid.AutoSize()
		self.GetSizer().Layout()
		self.grid.EnableEditing(False)
		self.grid.ForceRefresh()  #needed to make colour changes update
		
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

		self.wizard.SetPageSize( wx.Size(1024,800) )
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
			self.summaryPage.setInfo( self.bib, riderName, self.introPage.getFileName(), self.lapTimes, self.race.startTime, self.race.minPossibleLapTime )
			
		
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()

