import os
import io
import json
import getpass
import socket
import datetime
import Version
import Utils
import Model
from GeoAnimation import GpsPoint, GeoTrack

class Template( object ):
	templateAttributes = {
		'distanceUnit',	
		'rule80MinLapCount',

		'isTimeTrial',
		'roadRaceFinishTimes',

		'enableJChipIntegration',
		'resetStartClockOnFirstTag',
		'skipFirstTagRead',

		'chipReaderType',
		'chipReaderPort',
		'chipReaderIpAddr',

		'autocorrectLapsDefault',

		'enableUSBCamera',
		'photosAtRaceEndOnly',
		
		'advancePhotoMilliseconds',
		'finishKMH',
	
		'ftpUploadDuringRace',
		'ftpUploadPhotos',
		
		'ftpHost',
		'ftpUser',
		'ftpPassword',
		'ftpPath',

		'groupByStartWave',
		'winAndOut',

		'city',
		'stateProv',
		'country',
		'discipline',

		'showCourseAnimationInHtml',
		'licenseLinkTemplate',
		'hideDetails',

		'lapCounterForeground',
		'lapCounterBackground',
		'secondsBeforeLeaderToFlipLapCounter',
		'countdownTimer',

		'setNoDataDNS',

		'organizer',
	
		'minutes',

		'allCategoriesFinishAfterFastestRidersLastLap',
	
		'highPrecisionTimes'
		'syncCategories',
		'finishTop',
		'reverseDirection',
		
		'headerImage',
		'email',
		
		'course',
	}
	
	def __init__( self, race=None ):
		self.template = {}
		if race:
			self.fromRace( race )
		
	def write( self, fname ):
		with io.open( fname, 'wb' ) as fp:
			json.dump( self.template, fp, indent=1, sort_keys=True )
		
	def read( self, fname ):
		with io.open( fname, 'rb' ) as fp:
			self.template = json.load( fp )
	
	def fromRace( self, race ):
		if not race:
			self.template = {}
			return
		
		self.template = { attr:getattr(race, attr) for attr in self.templateAttributes if hasattr(race, attr) }
		
		try:
			firstLapDistance = max( c.firstLapDistance for c in race.getCategories( startWaveOnly=True ) if c.firstLapDistance )
			firstLapDistance *= 1000.0 if race.distanceUnit.UnitKM else 1609.344
		except ValueError:
			firstLapDistance = None
		
		try:
			self.template['course'] = {
				'isPointToPoint': race.geoTrack.isPointToPoint,
				'geoTrackFName': race.geoTrackFName,
				'points': [p._asdict() for p in race.geoTrack.gpsPoints],
				'firstLapDistance': firstLapDistance,
			}
		except AttributeError:
			pass
		
	def toRace( self, race ):
		if not race:
			return
		for attr, value in self.template.iteritems():
			if attr not in self.templateAttributes:
				continue
			if attr == 'course':
				course = self.template['course']
				race.geoTrackFName = course.get('geoTrackFName', 'geoTrackFName')
				race.geoTrack = GeoTrack()
				race.geoTrack.setPoints( [GpsPoint(**p) for p in course.get('points',[])], course.get('isPointToPoint',False) )
				if course['firstLapDistance']:
					race.geoTrack.firstLapDistance = course['firstLapDistance']
			else:
				setattr( race, attr, value )
		race.setChanged()
			
	def __eq__(self, other):
		return (isinstance(other, self.__class__) and self.template == other.template)

if __name__ == '__main__':
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	Model.race.winAndOut = True
	Model.race.organizer = u'\u2713\u2713\u2713\u2713\u2713\u2713'
	p1 = Template( Model.race )
	p1.write( 'TemplateTest1.template' )
	p2 = Template()
	p2.read( 'TemplateTest1.template' )
	assert p1 == p2
	
	Model.race.winAndOut = False
	p2 = Template( Model.race )
	p2.write( 'TemplateTest2.template' )
	assert p1 != p2
