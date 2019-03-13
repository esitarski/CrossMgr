import sys
import six
import codecs
from .pyllrp import *
from .TagInventory import TagInventory

def padToWords( epc ):
	if isinstance(epc, six.integer_types):
		epc = u'{}'.format(epc)
	else:
		epc = epc.lstrip('0')
	len_epc = len(epc)
	return epc.zfill( len_epc + (-len_epc%4) )
	
def getTagMask( epc ):
	epc = padToWords( epc )
	return '{:04X}{}'.format( ((1<<5)-1)<<(16-5), 'F' * len(epc) )
	
def addLengthPrefix( epc ):
	# Pad out to a 16-bit word.
	# Then, add the length in words as the highest 5-bits of the first word.
	# We don't care about the other bits - just leave them at zero.
	epc = padToWords( epc )
	epc = u'{:04X}{}'.format( (len(epc)//4)<<(16-5), epc )
	return epc
	
def hexToWords( epc ):
	assert len(epc) % 4 == 0, 'epc must be a 16-bit word multiple'
	return [int(epc[i:i+4], 16) for i in six.moves.range(0, len(epc), 4)]

def hexToBytes( epc ):
	assert len(epc) % 2 == 0, 'epc must be a byte multiple'
	return codec.decode(epc, 'hex_codec')

class TagWriter( TagInventory ):
	accessSpecID = 456

	def GetAccessSpec(	self,
						MessageID = None,			# If None, one will be assigned.
						epcOld = '',				# Old EPC.  Empty matches anything.
						epcNew = '0123456789',		# New EPC.
						roSpecID = 0,				# ROSpec to trigger this ROSpec.  0 = run when any ROSpec runs.
						opSpecID = 1,				# Something unique.
						operationCount = 10,		# Number of times to execute.
						antenna = None ):
		
		TagMask = hexToBytes( getTagMask(epcOld) ) if epcOld else b''
		TagData = hexToBytes( addLengthPrefix(epcOld) ) if epcOld else b''
		
		accessSpecMessage = ADD_ACCESSSPEC_Message( MessageID = MessageID, Parameters = [
			AccessSpec_Parameter(
				AccessSpecID  = self.accessSpecID,
				AntennaID = antenna if antenna else 0,	# Unspecified antenna: apply to all antennas
				ProtocolID = AirProtocols.EPCGlobalClass1Gen2,
				CurrentState = bool(AccessSpecState.Disabled),
				ROSpecID = roSpecID,
				
				Parameters = [
					AccessSpecStopTrigger_Parameter(
						AccessSpecStopTrigger = AccessSpecStopTriggerType.Operation_Count,
						OperationCountValue = operationCount
					),
					AccessCommand_Parameter(
						Parameters = [
							C1G2TagSpec_Parameter(
								Parameters = [
									C1G2TargetTag_Parameter(
										MB = 1,						# Memory Bank 1 = EPC
										Pointer = 16,				# 16 bits offset - skip CRC.
										TagMask = TagMask,
										TagData = TagData,
										Match = True,
									)
								]
							),
							C1G2Write_Parameter(
								MB = 1,
								WordPointer = 1,					# Skip CRC, but include the length and flags.
								WriteData = hexToWords( addLengthPrefix(epcNew) ),
								OpSpecID = opSpecID,
								AccessPassword = 0,
							),
						]
					),
					AccessReportSpec_Parameter(
						AccessReportTrigger = AccessReportTriggerType.End_Of_AccessSpec
					)
				]
			)
		])	# ADD_ACCESS_SPEC_Message
		
		return accessSpecMessage
		
	def _prologTW( self, epcOld, epcNew, antenna = None ):
		response = self.connector.transact( DELETE_ACCESSSPEC_Message(AccessSpecID = 0) )
		assert response.success(), 'Delete AccessSpec Fails\n{}'.format(response)
		
		message = self.GetAccessSpec(
					epcOld = epcOld,
					epcNew = epcNew,
					antenna = antenna,
		)
		response = self.connector.transact( message )
		assert response.success(), 'Add AccessSpec Fails\n{}'.format(response)
	
	def _executeTW( self ):
		response = self.connector.transact( ENABLE_ACCESSSPEC_Message(AccessSpecID = self.accessSpecID) )
		assert response.success(), 'Enable AccessSpec Fails\n{}'.format(response)
		
		# Run the TagInventory to trigger our AccessSpec.
		self._execute()
		
		response = self.connector.transact( DISABLE_ACCESSSPEC_Message(AccessSpecID = self.accessSpecID) )
		assert response.success(), 'Disable AccessSpec Fails\n{}'.format(response)
		
	def _epilogTW( self ):
		response = self.connector.transact( DELETE_ACCESSSPEC_Message(AccessSpecID = self.accessSpecID) )
		assert response.success(), 'Delete AccessSpec Fails\n{}'.format(response)
		
	def WriteTag( self, epcOld, epcNew, antenna = None ):
		''' Change a single tag. '''
		self._prolog( antenna )
		self._prologTW( epcOld, epcNew, antenna )
		
		self._executeTW()
		
		self._epilogTW()
		self._epilog()
		
	def WriteFOVConsecutive( self, tagStart, tagFormat = '{}' ):
		''' Change all tags in the "Field Of View" to consecutive values, starting from tagStart. '''
		tagInventory, otherMessages = self.GetTagInventory()
		
		self._prolog()
		tagCur = tagStart
		for tag in sorted(tagInventory, reverse=True):	# Go in reverse to avoid overlap increment conflicts.
			self._prologTW( tag, tagFormat.format(tagStart) )
			self._executeTW()
			self._epilogTW()
			tagCur += 1
			
		self._epilog()
		return tagCur

if __name__ == '__main__':
	print ( '{}\n'.format('*' * 75) )
	
	impinjHost = '192.168.0.101'
	tw = TagWriter( impinjHost )
	tw.Connect()
	
	print ( 'Before tags' )
	tagInventory, otherMessages = tw.GetTagInventory()
	print ( '\n'.join( tagInventory ) )
	
	tagValue = '256'
	print ( 'Writing tag: {}'.format(tagValue) )
	tw.WriteTag( '', tagValue )
	
	print ( 'After Tags' )
	tagInventory, otherMessages = tw.GetTagInventory()
	print ( '\n'.join( tagInventory ) )
	
	tw.Disconnect()
	tw.Connect()
	tagInventory, otherMessages = tw.GetTagInventory()
	for tag in tagInventory:
		tw.Connect()
		epcOld = tag
		epcNew = u'{:X}'.format(int(tag,16)+1)
		print ( u'{} {}'.format(epcOld, epcNew) )
		tw.WriteTag( epcOld, epcNew )
		tw.Disconnect()

	tw.Connect()
	print ( '{}\n'.format('*' * 75) )
	tagInventory, otherMessages = tw.GetTagInventory()
	print ( '\n'.join(tagInventory) )
	
	tw.Disconnect()
	
