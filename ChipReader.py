import Utils
import JChip
import RaceResult
import Ultra
import WebReader

class ChipReader:
	JChip, RaceResult, Ultra, WebReader = tuple( range(4) )	# Add new options at the end.
	
	def __init__( self ):
		self.chipReaderType = None
		self.reset()
		
	def reset( self, chipReaderType=None ):
		if self.chipReaderType is not None:
			JChip.StopListener()
			RaceResult.StopListener()
			Ultra.StopListener()
			WebReader.StopListener()
		
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
			
		elif self.chipReaderType == ChipReader.WebReader:
			self.StartListener = WebReader.StartListener
			self.GetData = WebReader.GetData
			self.StopListener = WebReader.StopListener
			self.CleanupListener = WebReader.CleanupListener
			self.IsListening = WebReader.IsListening
			
		else: # self.chipReaderType == ChipReader.JChip:
			self.StartListener = JChip.StartListener
			self.GetData = JChip.GetData
			self.StopListener = JChip.StopListener
			self.CleanupListener = JChip.CleanupListener
			self.IsListening = JChip.IsListening

chipReaderCur = ChipReader()


