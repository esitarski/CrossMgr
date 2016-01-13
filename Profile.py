import os
import io
import json
import getpass
import socket
import datetime
import cPickle as pickle
import Version
import Utils
import Model

class Profile( object ):
	profileAttributes = [
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
		
		'geoTrack', 'geoTrackFName',
	]
	
	def __init__( self, model=None ):
		self.profile = {}
		if model:
			self.fromModel( model )
		
	def write( self, fname ):
		with io.open( fname, 'wb' ) as fp:
			pickle.dump( Model.race, fp, 2 )
		
	def read( self, fname ):
		with io.open( fname, 'rb' ) as fp:
			self.profile = pickle.load( fp )
	
	def fromModel( self, model ):
		self.profile = { attr:getattr(model, attr) for attr in self.profileAttributes if hasattr(model, attr) }
		
	def toModel( self, model ):
		for attr, value in self.profile.iteritems():
			setattr( model, attr, value )
			
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
	
	Model.race.winAndOut = False
	p2 = Profile( Model.race )
	p2.write( 'ProfileTest2.profile' )
