
import Utils
import Model
import ReadSignOnSheet

class RaceInputState( object ):
	def __init__( self ):
		self.state = (None, None, None)
		
	def changed( self ):
		newState = (Utils.getFileName(), ReadSignOnSheet.stateCache, getattr(Model.race, 'lastOpened', None) if Model.race else None)
		if self.state != newState:
			self.state = newState
			return True
		return False
