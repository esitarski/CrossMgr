
import Utils
import Model
import ReadSignOnSheet
from FtpWriteFile import ftpFields

class RaceInputState( object ):
	def __init__( self ):
		self.reset()
	
	def reset( self ):
		self.state = None
	
	def changed( self ):
		race = Model.race
		newState = [
			Utils.getFileName(),
			ReadSignOnSheet.stateCache,
		]
		if race:
			newState.extend( [
					getattr(race, 'lastOpened', None),
					race.enableJChipIntegration,
					race.resetStartClockOnFirstTag,
					race.firstRecordedTime,
					race.skipFirstTagRead ,
					
					race.chipReaderType,
					race.chipReaderPort,
					race.chipReaderIpAddr,
				]
			)
			newState.extend( [getattr(race, attr, None) for attr in ftpFields] )
		if not self.state or self.state != newState:
			self.state = newState
			return True
		return False
