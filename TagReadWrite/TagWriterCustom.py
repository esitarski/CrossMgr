import re
import operator
from pyllrp.pyllrp import *
from pyllrp.TagWriter import TagWriter

def getAllParametersByClass( v, parameterClass ):
	# Workaround for bug in llrp.
	for p in v.Parameters:
		if isinstance( p, parameterClass ):
			yield p
		else:
			yield from getAllParametersByClass( p, parameterClass )

def GetReceiveTransmitPower( connector):
	# Query the reader to get the receive and transmit power tables.
	message = GET_READER_CAPABILITIES_Message( MessageID = 0xed, RequestedData = GetReaderCapabilitiesRequestedData.All )
	response = connector.transact( message )
	
	# Receive power expressed as -80db + value relative to maximum power.
	receive_sensitivity_table = [-80 + e.ReceiveSensitivityValue
		for e in sorted(getAllParametersByClass(response,ReceiveSensitivityTableEntry_Parameter), key=operator.attrgetter('Index'))
	]
	# Transmit power expressed as dBm*100 (dB relative to a milliwatt).
	transmit_power_table = [e.TransmitPowerValue/100.0
		for e in sorted(getAllParametersByClass(response,TransmitPowerLevelTableEntry_Parameter), key=operator.attrgetter('Index'))
	]
	return receive_sensitivity_table, transmit_power_table

class TagWriterCustom( TagWriter ):
	def Connect( self, receivedB, transmitdBm ):
		# In order to validate the parameters, we need to do two connects.
		# The first call gets the tables, the second call sets the receive sensitivity and transmit power based on the available options.
		super().Connect()
		self.receive_sensitivity_table, self.transmit_power_table = GetReceiveTransmitPower( self.connector )
		super().Disconnect()
		self.setReceiveSensitivity_dB( receivedB )
		self.setTransmitPower_dBm( transmitdBm )
		super().Connect()

	def setReceiveSensitivity_dB( self, dB ):
		self.receiverSensitivity = None
		try:
			dB = float( re.sub('[^.0-9-]', '', dB) )
		except ValueError:
			return
		if len(self.receive_sensitivity_table) <= 1 or dB <= self.receive_sensitivity_table[0]:
			return
		for self.receiverSensitivity, dB_cur in enumerate(self.receive_sensitivity_table, 1):
			if dB_cur >= dB:
				break

	def setTransmitPower_dBm( self, dBm ):
		self.transmitPower = None
		try:
			dBm = float( re.sub('[^.0-9]', '', dBm) )
		except ValueError:
			return
		if len(self.transmit_power_table) <= 1 or dBm > self.transmit_power_table[-1]:
			return
		for self.transmitPower, dBm_cur in enumerate(self.transmit_power_table, 1):
			if dBm_cur >= dBm:
				break
