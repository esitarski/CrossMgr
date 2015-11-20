
import Utils
import JChip
import RaceResult

class ChipReader( object ):
	JChip = 0
	RaceResult = 1
	
	def __init__( self ):
		self.chipReaderType = None
		self.reset()
		
	def reset( self, chipReaderType=None ):
		if self.chipReaderType is not None:
			JChip.StopListener()
			RaceResult.StopListener()
		self.chipReaderType = (chipReaderType or ChipReader.JChip)
		if self.chipReaderType == ChipReader.JChip:
			self.StartListener = JChip.StartListener
			self.GetData = JChip.GetData
			self.StopListener = JChip.StopListener
			self.CleanupListener = JChip.CleanupListener
		elif self.chipReaderType == ChipReader.RaceResult:
			self.StartListener = RaceResult.StartListener
			self.GetData = RaceResult.GetData
			self.StopListener = RaceResult.StopListener
			self.CleanupListener = RaceResult.CleanupListener
		else:
			assert False, 'Unrecognized ChipReader: {}'.format(self.chipReaderType)
	
	@property
	def listener( self ):
		if self.chipReaderType == ChipReader.JChip:
			return JChip.listener
		elif self.chipReaderType == ChipReader.RaceResult:
			return RaceResult.listener
		else:
			assert False, 'Unrecognized ChipReader'

chipReaderCur = ChipReader()


