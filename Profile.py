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

class Profile( object ):
	profileAttributes = {
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
		self.profile = {}
		if race:
			self.fromRace( race )
		
	def write( self, fname ):
		with io.open( fname, 'wb' ) as fp:
			json.dump( self.profile, fp, indent=1, sort_keys=True )
		
	def read( self, fname ):
		with io.open( fname, 'rb' ) as fp:
			self.profile = json.load( fp )
	
	def fromRace( self, race ):
		if not race:
			self.profile = {}
			return
		
		self.profile = { attr:getattr(race, attr) for attr in self.profileAttributes if hasattr(race, attr) }
		try:
			self.profile['course'] = {
				'isPointToPoint': race.geoTrack.isPointToPoint,
				'geoTrackFName': race.geoTrackFName,
				'points': [p._asdict() for p in race.geoTrack.gpsPoints],
			}
		except AttributeError:
			pass
		
	def toRace( self, race ):
		if not race:
			return
		for attr, value in self.profile.iteritems():
			if attr not in self.profileAttributes:
				continue
			if attr == 'course':
				course = self.profile['course']
				race.geoTrackFName = course.get('geoTrackFName', 'geoTrackFName')
				race.geoTrack = GeoTrack()
				race.geoTrack.setPoints( [GpsPoint(**p) for p in course.get('points',[])], course.get('isPointToPoint',False) )
			else:
				setattr( race, attr, value )
		race.setChanged()
			
	def __eq__(self, other):
		return (isinstance(other, self.__class__) and self.profile == other.profile)
			
if __name__ == '__main__':
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	Model.race.winAndOut = True
	Model.race.organizer = u'\u2713\u2713\u2713\u2713\u2713\u2713'
	p1 = Profile( Model.race )
	p1.write( 'ProfileTest1.profile' )
	p2 = Profile()
	p2.read( 'ProfileTest1.profile' )
	assert p1 == p2
	
	Model.race.winAndOut = False
	p2 = Profile( Model.race )
	p2.write( 'ProfileTest2.profile' )
	assert p1 != p2
