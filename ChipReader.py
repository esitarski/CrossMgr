import JChip
import RaceResult
import Ultra
import WebReader
import MyLapsServer

class ChipReader:
	JChip, RaceResult, Ultra, WebReader, MyLaps = tuple( range(5) )	# Add new options at the end.
	Choices = (_('JChip/Impinj/Alien'), _('RaceResult'), _('Ultra'), _('WebReader'), _('MyLaps'))
	
	def __init__( self ):
		self.chipReaderType = None
		self.reset()
		
	def reset( self, chipReaderType=None ):
		if self.chipReaderType is not None:
			JChip.StopListener()
			RaceResult.StopListener()
			Ultra.StopListener()
			WebReader.StopListener()
			MyLapsServer.StopListener()
		
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
						
		elif self.chipReaderType == ChipReader.MyLaps:
			self.StartListener = MyLapsServer.StartListener
			self.GetData = MyLapsServer.GetData
			self.StopListener = MyLapsServer.StopListener
			self.CleanupListener = MyLapsServer.CleanupListener
			self.IsListening = MyLapsServer.IsListening

		else: # self.chipReaderType == ChipReader.JChip:
			self.StartListener = JChip.StartListener
			self.GetData = JChip.GetData
			self.StopListener = JChip.StopListener
			self.CleanupListener = JChip.CleanupListener
			self.IsListening = JChip.IsListening
			
chipReaderCur = ChipReader()


