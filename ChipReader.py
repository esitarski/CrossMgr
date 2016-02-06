import Utils
import JChip
import RaceResult
import Ultra

class ChipReader( object ):
	JChip = 0
	RaceResult = 1
	Ultra = 2
	
	def __init__( self ):
		self.chipReaderType = None
		self.reset()
		
	def reset( self, chipReaderType=None ):
		if self.chipReaderType is not None:
			JChip.StopListener()
			RaceResult.StopListener()
			Ultra.StopListener()
		
		self.chipReaderType = (chipReaderType or ChipReader.JChip)
		
		if self.chipReaderType == ChipReader.RaceResult:
			self.StartListener = RaceResult.StartListener
			self.GetData = RaceResult.GetData
			self.StopListener = RaceResult.StopListener
			self.CleanupListener = RaceResult.CleanupListener
			self.IsListening = RaceResult.IsListening
			
		elif self.chipReaderType == ChipReader.Ultra:
			self.StartListener = Ultra.StartListener
			self.GetData = Ultra.GetData
			self.StopListener = Ultra.StopListener
			self.CleanupListener = Ultra.CleanupListener
			self.IsListening = Ultra.IsListening
			
		else: # self.chipReaderType == ChipReader.JChip:
			self.StartListener = JChip.StartListener
			self.GetData = JChip.GetData
			self.StopListener = JChip.StopListener
			self.CleanupListener = JChip.CleanupListener
			self.IsListening = JChip.IsListening

chipReaderCur = ChipReader()


