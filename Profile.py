import os
import io
import json
import getpass
import socket
import datetime
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
	]
	
	def __init__( self, model=None ):
		self.profile = {}
		if model:
			self.fromModel( model )
		
	def write( self, fname ):
		header = '''
		---------------------------------------------
		CrossMgr Profile
		Machine Generated File. Do Not Edit!
		
		for details see http://www.sites.google.com/site/crossmgrsoftware
		
		Created On: {timestamp}
		User      : {user}
		Computer  : {computer}
		Version   : {version}
		---------------------------------------------
		'''.format(
				timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
				user=getpass.getuser(),
				version=Version.AppVerName,
				computer=socket.gethostname(),
			)
		profile = { '//{:03d}'.format(i):line.strip() for i, line in enumerate(header.strip().split('\n')) }
		profile.update( self.profile )
		with io.open( fname, 'wb' ) as f:
			json.dump( profile, f, indent=1, sort_keys=True )
		
	def read( self, fname ):
		with io.open( fname, 'rb' ) as f:
			profile = json.load( f )
		delkeys = [key for key in profile.iterkeys() if key.startswith('//') ]
		for key in delkeys:
			del profile[key]
		self.profile = profile
		
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
	p1.write( 'ProfileTest1.json' )
	p2 = Profile()
	p2.read( 'ProfileTest1.json' )
	assert p1 == p2
	
	Model.race.winAndOut = False
	p2 = Profile( Model.race )
	p2.write( 'ProfileTest2.json' )
	assert p1 != p2
