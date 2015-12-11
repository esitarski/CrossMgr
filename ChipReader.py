
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
		if self.chipReaderType == ChipReader.RaceResult:
			self.StartListener = RaceResult.StartListener
			self.GetData = RaceResult.GetData
			self.StopListener = RaceResult.StopListener
			self.CleanupListener = RaceResult.CleanupListener
			self.IsListening = RaceResult.IsListening
		else:
			self.StartListener = JChip.StartListener
			self.GetData = JChip.GetData
			self.StopListener = JChip.StopListener
			self.CleanupListener = JChip.CleanupListener
			self.IsListening = JChip.IsListening

chipReaderCur = ChipReader()


