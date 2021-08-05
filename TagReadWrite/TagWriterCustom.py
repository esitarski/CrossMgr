import re
import operator
from pyllrp.pyllrp import *
from pyllrp.TagWriter import TagWriter

def GetReceiveTransmitPowerGeneralCapabilities( connector):
	# Enable Impinj Extensions
	message = IMPINJ_ENABLE_EXTENSIONS_Message( MessageID = 0xeded )
	response = connector.transact( message )
	hasImpinjExtensions = response.success()
	
	# Query the reader to get the receive and transmit power tables.
	message = GET_READER_CAPABILITIES_Message( MessageID = 0xed, RequestedData = GetReaderCapabilitiesRequestedData.All )
	response = connector.transact( message )
	
	# Receive power expressed as -80db + value relative to maximum power.
	receive_sensitivity_table = [-80 + e.ReceiveSensitivityValue
		for e in sorted(response.getAllParametersByClass(ReceiveSensitivityTableEntry_Parameter), key=operator.attrgetter('Index'))
	]
	# Transmit power expressed as dBm*100 (dB relative to a milliwatt).
	transmit_power_table = [e.TransmitPowerValue/100.0
		for e in sorted(response.getAllParametersByClass(TransmitPowerLevelTableEntry_Parameter), key=operator.attrgetter('Index'))
	]

	# General device info.
	device_fields = {}
	general_capabilities = {}
	
	def set_capability( k, v ):
		general_capabilities[k] = v
		if k not in device_fields:
			device_fields[k] = len(device_fields)

	p = response.getFirstParameterByClass( GeneralDeviceCapabilities_Parameter )
	if p:
		for a in ('ReaderFirmwareVersion', 'DeviceManufacturerName', 'ModelName', 'MaxNumberOfAntennaSupported', 'HasUTCClockCapability'):
			v = getattr( p, a, 'missing' )
			set_capability( a, getVendorName(v) if a == 'DeviceManufacturerName' else v )

	if hasImpinjExtensions:
		# Impinj Detailed Version.
		p = response.getFirstParameterByClass( ImpinjDetailedVersion_Parameter )
		if p:
			for a in ('ModelName', 'SerialNumber', 'SoftwareVersion', 'FirmwareVersion'):
				v = getattr( p, a, 'missing' )
				set_capability( a, v )

		# Reader Temperature.
		message = GET_READER_CONFIG_Message( MessageID = 0xededed, RequestedData = GetReaderConfigRequestedData.All )
		response = connector.transact( message )
		if response.success():
			p = response.getFirstParameterByClass( ImpinjReaderTemperature_Parameter )
			#if not p:
			#	p = ImpinjReaderTemperature_Parameter( Temperature=33 )
			if p:
				a = 'Temperature'
				v = getattr( p, a, 'missing' )
				if isinstance( v, int ):
					set_capability( a, '{}C  |  {}F'.format(v, int(v * (9.0/5.0) + 32.0 + 0.5)) )
	
	return receive_sensitivity_table, transmit_power_table, [(a,general_capabilities[a]) for a in sorted(device_fields.keys(), key=device_fields.__getitem__)]

class TagWriterCustom( TagWriter ):
	def Connect( self, receivedB, transmitdBm ):
		# In order to validate the parameters, we need to do two connects.
		# The first call gets the tables, the second call sets the receive sensitivity and transmit power based on the available options.
		super().Connect()
		self.receive_sensitivity_table, self.transmit_power_table, self.general_capabilities = GetReceiveTransmitPowerGeneralCapabilities( self.connector )
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
