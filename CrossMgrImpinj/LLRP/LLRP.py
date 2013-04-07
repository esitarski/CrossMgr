
import bitstring
from cStringIO import StringIO
import types
from enums import *

#----------------------------------------------------------------------------------
# Python support for LLRP (Low Level Reader Protocol).
#
# Edward Sitarski, 2013 (edward.sitarski@gmail.com)
#
# Fields types and bit lengths are defined for all Messages and Parameters in the LLRP.
# The field specs are understood by the _MessagePackUnpack and _ParameterPackUnpack classes which
# can read/write in binary to buffers based on the specs.
#
# All integer fields are intialized to zero, all boolean fields are intialized to False, all strings to empty.
#
# The PackUnpack classes handle the variable number of Parameters in Messages, in Parameters,
# and Parameters nested in Parameters.
#
# Classes for the Messages and Parameters are created dynamically in _MakeClass from field specs.
# The "__slots__" feature is used to limit the available fields in each Message and Parameter.
# This prevents assignment to non-existent fields by mistake.
#
# A Message class looks as follows if it were declared in Python:
#
# class MESSAGE_Message( object ):
#	def __init__( self, <fields specific to message> )
#		# Any fields not specified take default values.
#		pass
#
#	def __repr__( self )
#		''' Print out the message and all its nested structure. '''
#		pass
#
#	def send( self, socket ):
#		''' Send this object, in LLRP binary, to a socket.
#		pass
#

def _ReadField( s, format, obj, attr, bytesRemaining = None ):
	''' Read a field from the bitstring in the given format.  Assign it to the obj attr. '''
	if format.startswith('uintbe') or format == 'bool':
		setattr( obj, attr, s.read(format) )
	elif format == 'string':
		length = s.read( 'uintbe:16' )
		eformat = 'bytes:%d' % length
		st = s.read( eformat )
		setattr( obj, attr, str(st) )
	elif format.startswith('array'):
		length = s.read( 'uintbe:16' )
		eformat = 'uintbe:%s' % format.split(':')[1]
		arr = []
		for i in xrange(length):
			arr.append( s.read(eformat) )
		setattr( obj, attr, arr )
	elif format == 'bitarray':
		length = s.read( 'uintbe:16' )
		eformat = 'bits:%d' % length
		bstr = s.read( eformat )
		setattr( obj, attr, bstr.tobytes() )
	elif format.startswith('skip'):
		skip = int(format.split(':',1)[1])
		s.read( 'int:%d' % skip )
	elif format == 'payload':
		b = s.read( 'bytes:%d' % bytesRemaining )				# Read as bytes.
		setattr( obj, attr, bitstring.BitStream(bytes=b) )		# Set attr to a bitstream.
	else:
		assert False
	
def _WriteField( s, format, obj, attr ):
	''' Write a field to the bitstring in the given format.  Read it from the obj attr. '''
	try:
		if format.startswith('uintbe') or format == 'bool':
			s.append( bitstring.pack(format, getattr(obj, attr)) )
		elif format == 'string':
			st = getattr(obj, attr, '')
			s.append( bitstring.Bits(uintbe=len(st), length=16) )
			s.append( bitstring.Bits(bytes=bytes(st)) )
		elif format.startswith('array'):
			arr = getattr( obj, attr, [] )
			length = int(format.split(':')[1])
			s.append( bitstring.Bits(uintbe=len(arr), length=16) )
			for e in arr:
				s.append( bitstring.Bits(uintbe=e, length=length) )
		elif format == 'bitarray':
			st = getattr(obj, attr, '')
			s.append( bitstring.Bits(uintbe=len(st), length=16) )
			s.append( bitstring.Bits(bytes=bytes(st)) )
		elif format.startswith('skip'):
			skip = int(format.split(':',1)[1])
			assert skip > 0
			s.append( bitstring.pack('int:%d=0'%skip) )
		elif format == 'payload':
			s.append( getattr(obj, attr) )		# assume the   is a bitstream
		else:
			assert False
	except bitstring.CreationError, e:
		print '_WriteField:', format, attr
		raise

def _InitField( format, obj, attr ):
	''' Initialize a field value based on its format. '''
	if format.startswith('uintbe'):
		setattr( obj, attr, 0 )
	elif format == 'bool':
		setattr( obj, attr, False )
	elif format == 'string':
		setattr( obj, attr, '' )
	elif format.startswith('array'):
		setattr( obj, attr, [] )
	elif format == 'bitarray':
		setattr( obj, attr, bytes() )
	elif format == 'payload':
		setattr( obj, attr, bitstring.BitStream() )
	else:
		assert format.startswith('skip'), 'Unknown format: "%s"' % format

#----------------------------------------------------------------------------------

def _initSpecifiedFields( self, *args, **kwargs ):
	''' Initialize all data fields based on each format. '''
	for name, format in self.SpecifiedFields:
		_InitField( format, self, name )
		
	self.Parameters = []
	self._Length = 0
	
	# If this is a Message, initialize the message id to an invalid value.
	try:
		self._MessageID = None
	except AttributeError:
		pass
	
	# For convenience, Messages and Parameters with only one field can be initialized with a positional argument.
	# For example, it is posssible to write ROSpecID_Parameter(123) as it only has one field (ROSpecID).
	# For objects with multiple values, each values must be specified with kwargs.
	if args:
		assert self.FieldCount == 1, 'Object can only have one field to initialize with positional argument'
		assert len(args) == 1, 'Cannot initialize more than one field with positional initialization'
		setattr( self, self.__slots__[0], args[0] )
		
	for key, value in kwargs.iteritems():
		if key == 'MessageID':
			self._MessageID = value
		else:
			setattr( self, key, value )
	
	try:
		assert self._MessageID is not None, 'Missing MessageID Parameter'
	except AttributeError:
		pass
	
def _getValues( self ):
	''' Get all specified values of an LLRP object. '''
	return [(name, getattr(self, name)) for name, format in self.SpecifiedFields if not format.startswith('skip')]

def _getRepr( self, indent = '' ):
	''' Get the representation of an LLRP object. '''
	# Check for the number of values
	values = self._getValues()
	numValues = len(values) + (1 if hasattr(self, '_MessageID') else 0)
	
	s = StringIO()
	
	if numValues > 1 or self.Parameters:
		# Output in long form (one line per value and parameter).
		s.write( '%s%s(\n' % (indent, self.Name) )
		try:
			s.write( '%s  %s=%s,\n' % (indent, 'MessageID', repr(self._MessageID)) )
		except AttributeError:
			pass
			
		for name, value in values:
			s.write( '%s  %s=%s,\n' % (indent, name, repr(value)) )
		if self.Parameters:
			s.write( '%s  Parameters=[\n' % indent )
			for p in self.Parameters:
				s.write( p._getRepr( indent + '    ' ) )
			s.write( '%s  ]\n' % indent )
		s.write( '%s)%s\n' % (indent, ',' if indent else '') )
	else:
		# Output in short form as there is only one value.
		s.write( '%s%s( ' % (indent, self.Name) )
		
		try:
			s.write( ' %s=%s )\n' % ('MessageID', repr(self._MessageID)) )
		except AttributeError:
			pass
			
		for name, value in values:
			s.write( '%s=%s )%s\n' % (name, repr(value), ',' if indent else '') )
		
	return s.getvalue()
	
def _addParameter( self, p ):
	''' Add a parameter to an LLRP object. '''
	self.Parameters.append( p )
	return p

def _getPTypeName( pType ):
	return pType.Name if not isinstance(pType, tuple) else ' or '.join( v.Name for v in pType )
	
def _validate( self ):
	''' _validate the values of an LLRP object. '''
	for name, format in self.SpecifiedFields:
		if format.startswith('skip'):	# Pass over skip fields first as there is no attribute field associated.
			continue
			
		assert hasattr(self, name), 'Missing LLRP attribute: %s' % name
		
		if format.startswith('uintbe'):
			assert isinstance( getattr(self, name), (int, long) ), 'LLRP field "%s" must be "int" type not "%s"' % (
					name, getattr(self, name).__class__.__name__)
		elif format == 'bool':
			assert isinstance( getattr(self, name), bool ), 'LLRP field "%s" must be "bool" type not "%s"' % (
					name, getattr(self, name).__class__.__name__)
		elif format.startswith('array'):
			arr = getattr(self, name)
			assert isinstance( arr, list ), 'LLRP field "%s" must be "list" type not "%s"' % (
					name, getattr(self, name).__class__.__name__)
			for i, e in enumerate(arr):
				assert isinstance( e, (int, long) ), 'LLRP field "%s" must contain all "ints" or "longs" (not "%s" at position %d)' % (
						name, e.__class__.__name__, i)
		elif format == 'string':
			assert isinstance( getattr(self, name), basestring ), 'LLRP field "%s" must be "string" type not "%s"' % (
					name, getattr(self, name).__class__.__name__)
		elif format == 'bitarray':
			assert isinstance( getattr(self, name), bytes ), 'LLRP field "%s" must be "bytes" type not "%s"' % (
					name, getattr(self, name).__class__.__name__)
		elif format == 'payload':
			assert isinstance( getattr(self, namt), bitstream.BitStream ), 'LLRP Payload field "%s" must be "bitstream.BitStream" type not "%s"' % (
					name, getattr(self, name).__class__.__name__)
		else:
			assert False, 'Unknown LLRP field format: "%s"' % format
			
		# Check that the number and type of parameters match the constraints.
		if self._PConstraints is not None:
			i, iMax = 0, len(self.Parameters)
			for pType, nMin, nMax in self._PConstraints:
				iStart = i
				while i < iMax and isinstance(self.Parameters[i], pType):
					i += 1
				assert i - iStart >= nMin, 'Missing Parameter (%d-%d) of type: %s' % (nMin, nMax, _getPTypeName(pType))
				assert i - iStart <= nMax, 'Too many Parameters (%d-%d) of type: %s' % (nMin, nMax, _getPTypeName(pType))
			
		# Recursively validate all parameters.
		for p in self.Parameters:
			p._validate()

def _getMessageID( self ):
	return self._MessageID
			
def _setMessageID( self, MessageID ):
	self._MessageID = MessageID

def _sendToSocket( self, socket ):
	socket.sendall( self.pack(bitstring.BitStream()).tobytes() )
	
def _MakeClass( messageOrParameter, Name, Type, PackUnpack ):
	''' Make an LLRP class (Message or Parameter). '''
	extraFields = ['Parameters', '_Length']
	if messageOrParameter == 'Message':
		extraFields.append( '_MessageID' )
		
	classAttrs = {
		'Name':				Name,					# Name of this message/paramter.
		'Type':				Type,					# LLRP Type integer
		'PackUnpack':		PackUnpack,				# Instance to pack/unpack it into a bitstream.
		'SpecifiedFields':	PackUnpack.SpecifiedFields,	# Fields specified for this object.
		'__slots__':		[ name for name, format in PackUnpack.SpecifiedFields if not format.startswith('skip') ] + extraFields,	# Available fields in this object.
		'FieldCount':		sum( 1 for name, format in PackUnpack.SpecifiedFields if not format.startswith('skip') ),				# Field count for convenience.
		'DataFields':		[ name for name, format in PackUnpack.SpecifiedFields if not format.startswith('skip') ],				# List of data fields.
		'__init__':			_initSpecifiedFields,	# Initialize the object and defailt field values.
		'_getRepr':			_getRepr,				# Routine to format the message/parameter.
		'__repr__':			_getRepr,				# Default formatting call.
		'_getValues':		_getValues,				# Gets all values of specified fields.
		'add':				_addParameter,			# Convenience function to add a parameter.
		'_validate':		_validate,				# Validate all data fields and parameters.
		'_PConstraints':	None,					# Used to validate number and type of Parameters
		'pack':				lambda self, s: self.PackUnpack.pack(s, self),
	}
	if messageOrParameter == 'Parameter':
		classAttrs['Encoding'] = PackUnpack.Encoding							# Add encoding if a Parameter.
	else:
		classAttrs['MessageID'] = property( _getMessageID, _setMessageID )		# Add MessageID if a Message.
		classAttrs['send'] = _sendToSocket										# Also add "send" method.
	MPClass = type( Name + '_' + messageOrParameter, (object,), classAttrs )	# Dynamically create the class.
	return MPClass

def _skip( bits ):
	''' Create a skip code for bits. '''
	skipStr = 'skip:%d' % bits
	return (skipStr, skipStr)
	
def _fixSpecifiedFields( SpecifiedFields ):
	''' Fix up the field types by bit length. '''
	sf = []
	for name, format in SpecifiedFields:
		if isinstance(format, (int, long)):
			if format == 1:
				format = 'bool'
			elif format < 8:
				format = 'bits:%d' % format
			else:
				format = 'uintbe:%d' % format
		sf.append( (name, format) )
	return sf
	
#---------------------------------------------------------------------------------------------------------

class _MessagePackUnpack( object ):
	''' Pack and Unpack an LLRP Message. '''
	def __init__( self, Type, Name, SpecifiedFields ):
		self.Type = Type
		self.Name = Name
		self.SpecifiedFields = SpecifiedFields

	def unpack( self, s ):
		m = _messageClassFromType[self.Type]( MessageID = -1 )	# Use a dummy MessageID for now - we get the real one later.
	
		beginPos = s.pos
		Type = s.read('uintbe:16')
		Type &= ((1<<10)-1)
		assert m.Type == Type
		m._Length = s.read('uintbe:32')
		m._MessageID = s.read('uintbe:32')
		
		lengthRemaining = m._Length
		
		for name, format in self.SpecifiedFields:
			_ReadField( s, format, m, name, m._Length - ((s.pos - beginPos) >> 3) )
		while ((s.pos - beginPos) >> 3) < m._Length:
			m.Parameters.append( UnpackParameter(s) )
			
		return m
		
	def pack( self, s, m ):
		m._validate()
		
		beginPos = len(s)
		# Code Version 1 to the message type (1<<10)
		s.append( bitstring.pack('uintbe:16, uintbe:32, uintbe:32', (1<<10) | m.Type, 0, m._MessageID) )
		
		for name, format in self.SpecifiedFields:
			_WriteField( s, format, m, name )
		for p in m.Parameters:
			p.pack( s )

		# Fix the length field.
		endPos = len(s)
		m._Length = (endPos - beginPos) >> 3
		s.overwrite( bitstring.pack('uintbe:32', m._Length), beginPos + 16 )
		s.pos = endPos
		return s

#---------------------------------------------------------------------------------------------------------

class _ParameterPackUnpack( object ):
	''' Pack and Unpack an LLRP Parameter (TLV or TV encoding). '''
	TLV = 'TLV'
	TV = 'TV'
	def __init__( self, Type, Name, Encoding, SpecifiedFields, Length = -1 ):
		self.Type = Type
		self.Name = Name
		self.Encoding = Encoding
		self.SpecifiedFields = SpecifiedFields
		self.Length = Length	# for TV encoded _parameters

	def unpack( self, s ):
		p = _parameterClassFromType[self.Type]()
		
		beginPos = s.pos
		Type = s.peek( 'uintbe:8' )
		if Type & (1<<7):
			Type &= ((1<<7) - 1)
			p._Length = self.Length
			assert p.Encoding == self.TV
			s.read( 'uintbe:8' )
		else:
			Type = s.read('uintbe:16')
			Type &= ((1<<10)-1)
			#print self.Name, self.Type, self.Encoding, p.Encoding
			assert p.Encoding == self.TLV
			p._Length = s.read('uintbe:16')
		
		assert Type == self.Type
		
		for name, format in self.SpecifiedFields:
			_ReadField( s, format, p, name )
			
		if p.Encoding == self.TLV:
			while ((s.pos - beginPos) >> 3) < p._Length:
				p.Parameters.append( UnpackParameter(s) )

		return p
		
	def pack( self, s, p ):
		p._validate()

		beginPos = len(s)
		# print 'Packing:', p.Name, beginPos >> 3
		if p.Encoding == self.TLV:
			s.append( bitstring.pack('uintbe:16, uintbe:16', p.Type, 0) )
		else:
			assert not p.Parameters, 'LLRP TV _parameters cannot contain nested _parameters'
			s.append( bitstring.pack('uintbe:8', p.Type | 128 ) )
		
		for name, format in self.SpecifiedFields:
			_WriteField( s, format, p, name )

		# Fix the length field.
		if p.Encoding == self.TLV:
			for pp in p.Parameters:
				pp.pack( s )
				
			endPos = len(s)
			p._Length = (endPos - beginPos) >> 3
			s.overwrite( bitstring.pack('uintbe:16', p._Length), beginPos + 16 )
			s.pos = endPos
		else:
			p._Length = self.Length
		return s

def _DefTV( Type, Name, SpecifiedFields ):
	''' Define a TV parameter (no explicit length field). '''
	Length = 8		# Adjust for the leading Type byte.
	for name, format in SpecifiedFields:
		if isinstance(format, (int, long)):
			Length += format
		else:
			assert 'array' not in format
			Length += int(format.split(':')[1])
	assert Length & 7 == 0
	Length >>= 3	# Divide by 8 to get bytes from bits.
	return Type, _ParameterPackUnpack( Type, Name, _ParameterPackUnpack.TV, _fixSpecifiedFields(SpecifiedFields), Length )
	
def _DefTLV( Type, Name, SpecifiedFields = [] ):
	''' Define a TLV parameter (length field included). '''
	return Type, _ParameterPackUnpack( Type, Name, _ParameterPackUnpack.TLV, _fixSpecifiedFields(SpecifiedFields) )

#-----------------------------------------------------------------------------
# Define Parameters and their binary layouts.
#
_parameters = [
	_DefTLV( 128,	'UTCTimestamp',		[('Microseconds',64)] ),
	_DefTLV( 129,	'Uptime',			[('Microseconds',64)] ),
	_DefTLV( 137,	'GeneralDeviceCapabilities', [
		('MaxNumberOfAntennaSupported',16),
		('CanSetAntennaProperties',1),('HasUTCClockCapability',1),_skip(14),
		('DeviceManufacturerName',32),
		('ModelName',32),
		('ReaderFirmwareVersion','string'),
	] ),
	_DefTLV( 363,	'MaximumReceiveSensitivity',	[('MaximumSensitivityValue',16)] ),
	_DefTLV( 139,	'ReceiveSensitivityTableEntry',	[('Index', 16),('ReceiveSensitivityValue',16)] ),
	_DefTLV( 149,	'PerAntennaReceiveSensitivityRange',	[
		('AntennaID',16),
		('ReceiveSensitivityIndexMin',16),
		('ReceiveSensitivityIndexMax',16)] ),
	_DefTLV( 140,	'PerAntennaAirProtocol',	[('AntennaID',16),('ProtocolIDs','array:8')] ),
	_DefTLV( 141,	'GPIOCapabiltities',	[('NumGPIs',16),('NumGPOs',16)] ),
	_DefTLV( 142,	'LLRPCapabilities', [
		('CanDoRFSurvey',1),('CanDoReportBufferFillWarning',1),('SupportsClientRequestOpSpec',1),
		('CanDoTagInventoryStateAwareSingulation',1),('SupportsEventAndReportHolding',1),_skip(3),
		('MaxPriorityLevelSupported',16),
		('ClientRequestOpSpecTimeout',16),
		('MaxNumROSpecs',32),
		('MaxNumSpecsPerROSpec',32),
		('MaxNumInventoryParametersSpecsPerAISpec',32),
		('MaxNumAccessSpecs',32),
		('MaxNumOpSpecsPerAccessSpec',32),
	] ),
	_DefTLV( 143,	'RegulatoryCapabilities',	[('CountryCode',16),('CommunicationsStandard',16)] ),
	_DefTLV( 144,	'UHFBandCapabilities' ),
	_DefTLV( 145,	'TransmitPowerLevelTableEntry',	[('Index',16),('TransmitPowerValue',16)] ),
	_DefTLV( 146,	'FrequencyInformation' ),
	_DefTLV( 147,	'FrequencyHopTable',	[('HopTableID',8),_skip(8),('Frequencies','array:32')] ),
	_DefTLV( 148,	'FixedFrequencyTable',	[('Frequencies','array:16')] ),
	_DefTLV( 365,	'RFSurveyFrequencyCapabilities',	[('MinimumFrequency',32),('MaximumFrequency',32)] ),
	_DefTLV( 177,	'ROSpec',	[('ROSpecID',32),('Priority',8),('CurrentState',8)] ),
	_DefTLV( 178,	'ROBoundarySpec'),
	_DefTLV( 179,	'ROSpecStartTrigger',	[('ROSpecStartTriggerType',8)] ),
	_DefTLV( 180,	'PeriodicTriggerValue',	[('Offset',32),('Period',32)] ),
	_DefTLV( 181,	'GPITriggerValue',	[('GPIPortNum',16),('GPIEvent',1),_skip(7),('Timeout',32)] ),
	_DefTLV( 182,	'ROSpecStopTrigger',	[('ROSpecStopTriggerType',8),('DurationTriggerValue',32)] ),
	_DefTLV( 183,	'AISpec',	[('AntennaIDs','array:16')] ),
	_DefTLV( 184,	'AISpecStopTrigger',	[('AISpecStopTriggerType',8),('DurationTriggerValue',32)] ),
	_DefTLV( 185,	'TagObservationTrigger',	[('TriggerType',8),_skip(8),('NumberOfTags',16),('NumberOfAttempts',16),('T',16),('Timeout',32)] ),
	_DefTLV( 186,	'InventoryParameterSpec', [('InventoryParameterSpecID',16),('ProtocolID',8)]),
	_DefTLV( 187,	'RFSurveySpec', [('AntennaID',16),('StartFrequency',32),('EndFrequency',32)]),
	_DefTLV( 188,	'RFSurveySpecStopTrigger', [('StopTriggerType',8),('Duration',32),('N',32)]),
	_DefTLV( 355,	'LoopSpec', [('LoopCount',32)]),
	_DefTLV( 207,	'AccessSpec',	[('AccessSpecID',32),('AntennaID',16),('ProtocolID',8),('CurrentState',1),_skip(7),('ROSpecID',32)] ),
	_DefTLV( 208,	'AccessSpecStopTrigger',	[('AccessStopTrigger',8),('OperationCountValue',16)] ),
	_DefTLV( 209,	'AccessCommand' ),
	_DefTLV( 210,	'ClientRequestOpSpec', [('OpSpecID',16)] ),
	_DefTLV( 211,	'ClientRequestResponse', [('AccessSpecID',32)] ),
	_DefTLV( 217,	'LLRPConfigurationStateValue', [('LLRPConfigurationStateValue',32)] ),
	_DefTLV( 218,	'Identification', [('IDType',8),('ReaderID','string')] ),
	_DefTLV( 219,	'GPOWriteData', [('GPOPortNumber',16),('GPOData',1),_skip(7)] ),
	_DefTLV( 220,	'KeepaliveSpec', [('KeepaliveTriggerType',8),('TimeInterval',32)] ),
	_DefTLV( 221,	'AntennaProperties', [('AntennaConnected',1),_skip(7),('AntennaID',16),('AntennaGain',16)] ),
	_DefTLV( 222,	'AntennaConfiguration', [('AntennaID',16)] ),
	_DefTLV( 223,	'RFReceiver', [('ReceiverSensitivity',16)] ),
	_DefTLV( 224,	'RFTransmitter', [('HopTableID',16),('ChannelIndex',16),('TransmitPower',16)] ),
	_DefTLV( 225,	'GPIPortCurrentState', [('GPIPortNum',16),('CPIConfig',1),_skip(7),('GPIState',8)] ),
	_DefTLV( 226,	'EventsAndReports', [('HoldEventsAndReportsUponRequest',1),_skip(7)] ),
	_DefTLV( 237,	'ROReportSpec', [('ROReportTrigger',8),('N',16)] ),
	_DefTLV( 238,	'TagReportContentSelector', [
		('EnableROSpecID',1),('EnableSpecIndex',1),('EnableInventoryParameterSpecID',1),('EnableAntennaID',1),
		('EnableChannelIndex',1),('EnablePeakRSSI',1),('EnableFirstSeenTimestamp',1),('EnableLastSeenTimestamp',1),
		('EnableTagSeenCount',1),('EnableAccessSpecID',1),_skip(6),
	]),
	_DefTLV( 239,	'AccessReportSpec', [('AccessReportTrigger',8)] ),
	_DefTLV( 240,	'TagReportData' ),
	_DefTLV( 241,	'EPCData', [('EPC','bitarray')] ),
	
	_DefTV(  13,	'EPC_96', [('EPC','bytes:96')] ),
	_DefTV(   9,	'ROSpecID', [('ROSpecID',32)] ),
	_DefTV(  14,	'SpecIndex', [('SpecIndex',16)] ),
	_DefTV(  10,	'InventoryParameterSpecID', [('InventoryParameterSpecID',16)] ),
	_DefTV(   1,	'AntennaID', [('AntennaID',16)] ),
	_DefTV(   6,	'PeakRSSI', [('PeakRSSI',8)] ),
	_DefTV(   7,	'ChannelIndex', [('ChannelIndex',16)] ),
	_DefTV(   2,	'FirstSeenTimestampUTC', [('Microseconds',64)] ),
	_DefTV(   3,	'FirstSeenTimestampUptime', [('Microseconds',64)] ),
	_DefTV(   4,	'LastSeenTimestampUTC', [('Microseconds',64)] ),
	_DefTV(   5,	'LastSeenTimestampUptime', [('Microseconds',64)] ),
	_DefTV(   8,	'TagSeenCount', [('TagCount',16)] ),
	_DefTV(  15,	'ClientRequestOpSpecResult', [('OpSpecID',16)] ),
	_DefTV(  16,	'AccessSpecID', [('AccessSpecID',32)] ),
	
	_DefTLV( 242,	'RFSurveyReportData' ),
	_DefTLV( 243,	'FrequencyRSSILevelEntry', [('Frequency',32),('Bandwidth',32),('AverageRSSI',16),('PeakRSSI',16)] ),
	_DefTLV( 244,	'ReaderEventNotificationSpec' ),
	_DefTLV( 245,	'EventNotificationState', [('EventType',16),('NotificationState',1),_skip(7)] ),
	_DefTLV( 246,	'ReaderEventNotificationData' ),
	_DefTLV( 247,	'HoppingEvent', [('HopTableID',16),('NextChannelIndex',16)] ),
	_DefTLV( 248,	'GPIEvent', [('GPIPortNumber',16),('GPIEvent',1),_skip(7)] ),
	_DefTLV( 249,	'ROSpecEvent', [('EventType',8),('ROSpecID',32),('PreemptingROSpecID',32)] ),
	_DefTLV( 250,	'ReportBufferLevelWarningEvent', [('ReportBufferPercentageFull',8)] ),
	_DefTLV( 251,	'ReportBufferOverflowErrorEvent' ),
	_DefTLV( 252,	'ReaderExceptionEvent', [('Message','string')] ),
	
	_DefTV(  17,	'OpSpecID', [('OpSpecID',16)] ),
		
	_DefTLV( 253,	'RFSurveyEvent', [('EventType',8),('ROSpecID',32),('SpecIndex',16)] ),
	_DefTLV( 254,	'AISpecEvent', [('EventType',8),('ROSpecID',32),('SpecIndex',16)] ),
	_DefTLV( 255,	'AntennaEvent', [('EventType',8),('AntennaID',16)] ),
	_DefTLV( 256,	'ConnectionAttempt', [('Status',16)] ),
	_DefTLV( 257,	'ConnectionCloseEvent' ),
	_DefTLV( 356,	'SpecLoopEvent', [('ROSpecID',32),('LoopCount',32)] ),
	_DefTLV( 287,	'LLRPStatus', [('StatusCode',16),('ErrorDescription','string')] ),
	_DefTLV( 288,	'FieldError', [('FieldNum',16),('ErrorCode',16)] ),
	_DefTLV( 289,	'ParameterError', [('ParameterType',16),('ErrorCode',16)] ),
	_DefTLV(1023,	'Custom', [('VendorID',32),('Subtype',32),('Data','payload')] ),
	_DefTLV( 327,	'C1G2LLRPCapabilities', [
		('CanSupportBlockErase',1),('CanSupportBlockWrite',1),('CanSupportBlockPermalock',1),
		('CanSupportTagRecommissioning',1),('CanSupportUMIMethod2',1),('CanSupportXPC',1),_skip(2),
		('MaxNumSelectFiltersPerQuery',16),
	]),
	_DefTLV( 328,	'UHFC1G2RFModeTable' ),
	_DefTLV( 329,	'UHFC1G2RFModeTableEntry', [
		('ModeIdentifier',32),
		('DRValue',1),('EPCHAGTandCConformance',1),_skip(6),
		('Modulation',8),('ForwardLinkModulation',8),('SpecialMaskIndicator',8),
		('BDRValue',32),('PIEValue',32),('MinTariValue',32),('MaxTariValue',32),('StepTariValue',32),
	]),
	_DefTLV( 330,	'C1G2InventoryCommand', [('TagInventoryStateAware',1),_skip(7)] ),
	_DefTLV( 331,	'C1G2Filter', [('T',2),_skip(6)] ),
	_DefTLV( 332,	'C1G2TagInventoryMask', [('MB',2),_skip(6),('Pointer',16),('TagMask','bitarray')] ),
	_DefTLV( 333,	'C1G2TagInventoryStateAwareFilterAction', [('Target',8),('Action',8)] ),
	_DefTLV( 334,	'C1G2TagInventoryStateUnawareFilterAction', [('Action',8)] ),
	_DefTLV( 335,	'C1G2RFControl', [('ModeIndex',16),('Tari',16)] ),
	_DefTLV( 336,	'C1G2SingulationControl', [('S',2),_skip(6),('TagPopulation',16),('TagTransitTime',32)] ),
	_DefTLV( 337,	'C1G2TagInventoryStateAwareSingulationAction' ),	# This one is suspect!
	
	_DefTLV( 338,	'C1G2TagSpec' ),
	_DefTLV( 339,	'C1G2TargetTag', [('MB',2),('Match',1),_skip(5),('Pointer',16),('TagMask','bitarray'),('TagData','bitarray')] ),
	_DefTLV( 341,	'C1G2Read', [('OpSpecID',16),('AccessPassword',32),('MB',2),_skip(6),('WordPointer',16),('WordCount',16)] ),
	_DefTLV( 342,	'C1G2Write', [('OpSpecID',16),('AccessPassword',32),('MB',2),_skip(6),('WriteData','array:16')] ),
	_DefTLV( 343,	'C1G2Kill', [('OpSpecID',16),('KillPassword',32)] ),
	_DefTLV( 357,	'C1G2Recommission', [('OpSpecID',16),('KillPassword',32),_skip(5),('SB3',1),('SB2',1),('LSB',1)] ),
	_DefTLV( 344,	'C1G2Lock', [('OpSpecID',16),('AccessPassword',32)] ),
	_DefTLV( 345,	'C1G2LockPayload', [('Privilege',8),('DataField',8)] ),
	_DefTLV( 346,	'C1G2BlockErase', [('OpSpecID',16),('AccessPassword',32),('MB',2),_skip(6),('WordPointer',16),('WordCount',16)] ),
	_DefTLV( 347,	'C1G2BlockWrite', [('OpSpecID',16),('AccessPassword',32),('MB',2),_skip(6),('WordPointer',16),('WriteData','array:16')] ),
	_DefTLV( 358,	'C1G2BlockPermalock', [('OpSpecID',16),('AccessPassword',32),('MB',2),_skip(6),('BlockPointer',16),('BlockMask','array:16')] ),
	_DefTLV( 348,	'C1G2EPCMemorySelected', [('EnableCRC',1),('EnablePCBits',1),('EnableXPCBits',1),_skip(5)] ),
	
	_DefTV(  12,	'C1G2PC', [('PC_BITS',16)] ),
	_DefTV(  19,	'C1G2XPCW1', [('XPC_W1',16)] ),
	_DefTV(  20,	'C1G2PCPCW2', [('XPC_W2',16)] ),
	_DefTV(  11,	'C1G2CRC', [('CRC',16)] ),
	_DefTV(  18,	'C1G2SingulationDetails', [('NumCollisionSlots',16),('NumEmptySlots',16)] ),
	
	_DefTLV( 349,	'C1G2ReadOpSpecResult', [('Result',8),('OpSpecID',16),('ReadData','array:16')] ),
	_DefTLV( 350,	'C1G2WriteOpSpecResult', [('Result',8),('OpSpecID',16),('NumWordsWritten',16)] ),
	_DefTLV( 351,	'C1G2KillOpSpecResult', [('Result',8),('OpSpecID',16)] ),
	_DefTLV( 360,	'C1G2RecommissionOpSpecResult', [('Result',8),('OpSpecID',16)] ),
	_DefTLV( 352,	'C1G2LockOpSpecResult', [('Result',8),('OpSpecID',16)] ),
	_DefTLV( 353,	'C1G2BlockEraseSpecResult', [('Result',8),('OpSpecID',16)] ),
	_DefTLV( 354,	'C1G2BlockWriteOpSpecResult', [('Result',8),('OpSpecID',16),('NumWordsWritten',16)] ),
	_DefTLV( 361,	'C1G2BlockPermalockOpSpecResult', [('Result',8),('OpSpecID',16)] ),
	_DefTLV( 362,	'C1G2BlockPermalockOpStatusOpSpecResult', [('Result',8),('OpSpecID',16),('PermalockStatus','array:16')] ),
]
#--------------------------------------------------------------------------------------------

def _DefMessage( Type, Name, SpecifiedFields = [] ):
	''' Initialize a _MessagePackUnpack instance. '''
	return Type, _MessagePackUnpack(Type, Name, _fixSpecifiedFields(SpecifiedFields))
		
#-----------------------------------------------------------------------------
# Define Messages with binary layouts.
#
_messages = [
	_DefMessage( 46,	'GET_SUPPORTED_VERSION' ),
	_DefMessage( 56,	'GET_SUPPORTED_VERSION_RESPONSE', [('CurrentVersion',8),('SupportedVersion',8)] ),
	_DefMessage( 47,	'SET_PROTOCOL_VERSION', [('ProtocolVersion',8)] ),
	_DefMessage( 57,	'SET_PROTOCOL_VERSION_RESPONSE'),
	_DefMessage(  1,	'GET_READER_CAPABILITIES', [('RequestedData',8)] ),
	_DefMessage( 11,	'GET_READER_CAPABILITIES_RESPONSE' ),
	_DefMessage( 20,	'ADD_ROSPEC' ),
	_DefMessage( 30,	'ADD_ROSPEC_RESPONSE' ),
	_DefMessage( 21,	'DELETE_ROSPEC', [('ROSpecID',32)]),
	_DefMessage( 31,	'DELETE_ROSPEC_RESPONSE' ),
	_DefMessage( 22,	'START_ROSPEC', [('ROSpecID',32)]),
	_DefMessage( 32,	'START_ROSPEC_RESPONSE' ),
	_DefMessage( 23,	'STOP_ROSPEC', [('ROSpecID',32)]),
	_DefMessage( 33,	'STOP_ROSPEC_RESPONSE' ),
	_DefMessage( 24,	'ENABLE_ROSPEC', [('ROSpecID',32)]),
	_DefMessage( 34,	'ENABLE_ROSPEC_RESPONSE' ),
	_DefMessage( 25,	'DISABLE_ROSPEC', [('ROSpecID',32)]),
	_DefMessage( 35,	'DISABLE_ROSPEC_RESPONSE' ),
	_DefMessage( 26,	'GET_ROSPECS' ),
	_DefMessage( 36,	'GET_ROSPECS_RESPONSE' ),
	_DefMessage( 40,	'ADD_ACCESSSPEC' ),
	_DefMessage( 50,	'ADD_ACCESSSPEC_RESPONSE' ),
	_DefMessage( 41,	'DELETE_ACCESSSPEC', [('AccessSpecID',32)]),
	_DefMessage( 51,	'DELETE_ACCESSSPEC_RESPONSE' ),
	_DefMessage( 42,	'ENABLE_ACCESSSPEC', [('AccessSpecID',32)]),
	_DefMessage( 52,	'ENABLE_ACCESSSPEC_RESPONSE' ),
	_DefMessage( 43,	'DISABLE_ACCESSSPEC', [('AccessSpecID',32)]),
	_DefMessage( 53,	'DISABLE_ACCESSSPEC_RESPONSE' ),
	_DefMessage( 44,	'GET_ACCESSSPECS' ),
	_DefMessage( 54,	'GET_ACCESSSPECS_RESPONSE' ),
	_DefMessage( 45,	'CLIENT_REQUEST_OP' ),
	_DefMessage( 55,	'CLIENT_REQUEST_OP_RESPONSE' ),
	_DefMessage( 60,	'GET_REPORT' ),
	_DefMessage( 61,	'RO_ACCESS_REPORT' ),
	_DefMessage( 62,	'KEEPALIVE' ),
	_DefMessage( 72,	'KEEPALIVE_ACK' ),
	_DefMessage( 63,	'READER_EVENT_NOTIFICATION' ),
	_DefMessage( 64,	'ENABLE_EVENTS_AND_REPORTS' ),
	_DefMessage(100,	'ERROR_MESSAGE' ),
	_DefMessage(  2,	'GET_READER_CONFIG', [('AntennaID',16),('RequestedData',8),('GPIPortNum',16),('GPOPortNum',16)] ),
	_DefMessage( 12,	'GET_READER_CONFIG_RESPONSE' ),
	_DefMessage(  3,	'SET_READER_CONFIG', [('ResetToFactoryDefaults',1),_skip(7)]),
	_DefMessage( 13,	'SET_READER_CONFIG_RESPONSE' ),
	_DefMessage( 14,	'CLOSE_CONNECTION' ),
	_DefMessage(  4,	'CLOSE_CONNECTION_RESPONSE' ),
	_DefMessage(1023,	'CUSTOM_MESSAGE', [('VendorIdentifier',32),('MessageSubtype',8)]),
]

#-----------------------------------------------------------------------------
# Create Parameter classes from the specs.
# Initialize a dict to retrieve the Parameter PackUnpack class from the Type.
# Initialize a dict to retrieve the Parameter class from the Type.
#
_ParameterPackUnpackLookup = {}
_parameterClassFromName = {}
_parameterClassFromType = {}
for Type, d in _parameters:
	parameterClassName = d.Name + '_Parameter'
	assert Type not in _ParameterPackUnpackLookup, 'Type duplicate.  Parameter: Name = "%s", Type = %d' % (d.Name, Type)
	assert parameterClassName not in _parameterClassFromName, 'Name duplicate.  Parameter: Name = "%s", Type = %d' % (d.Name, Type)
	_ParameterPackUnpackLookup[Type] = d
	_parameterClassFromType[Type] = _parameterClassFromName[parameterClassName] = _MakeClass( 'Parameter', d.Name, Type, d )
	
globals().update( _parameterClassFromName )	# Add Parameter classes to global namespace.
del _parameterClassFromName

#-----------------------------------------------------------------------------
# Create Messages classes from the specs.
# Initialize a dict to retrieve the Message PackUnpack class from the Type.
# Initialize a dict to retrieve the Message class from the Type.
#
_MessagePackUnpackLookup = {}
_messageClassFromName = {}
_messageClassFromType = {}
for Type, d in _messages:
	messageClassName = d.Name + '_Message'
	assert Type not in _MessagePackUnpackLookup, 'Type duplicate.  Message: Name = "%s", Type = %d' % (d.Name, Type)
	assert messageClassName not in _messageClassFromName, 'Name duplicate.  Message: Name = "%s", Type = %d' % (d.Name, Type)
	_MessagePackUnpackLookup[Type] = d
	_messageClassFromType[Type] = _messageClassFromName[messageClassName] = _MakeClass( 'Message', d.Name, Type, d )
	
globals().update( _messageClassFromName )	# Add Message classes to global namespace.
	
#-----------------------------------------------------------------------------
# Define the allowable Parameter Types and the Min-Max.
#

n = 1000000
ADD_ROSPEC_Message._PConstraints = [(ROSpec_Parameter, 1, 1)]
ADD_ACCESSSPEC_Message._PConstraints = [(AccessSpec_Parameter, 1, 1)]
CLIENT_REQUEST_OP_Message._PConstraints = [(TagReportData_Parameter, 1, 1)]
CLIENT_REQUEST_OP_RESPONSE_Message._PConstraints = [(ClientRequestResponse_Parameter, 1, 1)]
RO_ACCESS_REPORT_Message._PConstraints = [
	(TagReportData_Parameter, 0, n),
	(RFSurveyReportData_Parameter, 0, n)
]
READER_EVENT_NOTIFICATION_Message._PConstraints = [(ReaderEventNotificationData_Parameter, 1, 1)]
SET_READER_CONFIG_Message._PConstraints = [
	(ReaderEventNotificationSpec_Parameter, 0, 1),
	(AntennaProperties_Parameter, 			0, n),
	(AntennaConfiguration_Parameter,		0, n),
	(ROReportSpec_Parameter,				0, 1),
	(AccessReportSpec_Parameter,			0, 1),
	(KeepaliveSpec_Parameter,				0, 1),
	(GPOWriteData_Parameter,				0, n),
	(GPIPortCurrentState_Parameter,			0, n),
	(EventsAndReports_Parameter,			0, 1),
]
#-----------------------------------------------------------------------------

RegulatoryCapabilities_Parameter._PConstraints = [
	(UHFBandCapabilities_Parameter,			0, n),
	(Custom_Parameter,						0, n)
]
UHFBandCapabilities_Parameter._PConstraints = [
	(TransmitPowerLevelTableEntry_Parameter,1, n),
	(FrequencyInformation_Parameter,		1, 1),
	#(UHFRFModeTable_Parameter,				1, n),
	(RFSurveyFrequencyCapabilities_Parameter,0,1)
]
FrequencyInformation_Parameter._PConstraints = [
	(FrequencyHopTable_Parameter,			0, n),
	(FixedFrequencyTable_Parameter,			0, 1),
]
ROSpec_Parameter._PConstraints = [
	(ROBoundarySpec_Parameter,				1, 1),
	((AISpec_Parameter,RFSurveySpec_Parameter,LoopSpec_Parameter),	1, n),
	(ROReportSpec_Parameter,				0, 1)
]
ROBoundarySpec_Parameter._PConstraints = [
	(ROSpecStartTrigger_Parameter,			1, 1),
	(ROSpecStopTrigger_Parameter,			1, 1)
	
]
ROSpecStartTrigger_Parameter._PConstraints = [
	(PeriodicTriggerValue_Parameter,		0, 1),
	(GPITriggerValue_Parameter,				0, 1)
]
PeriodicTriggerValue_Parameter._PConstraints = [
	(UTCTimestamp_Parameter,				0, 1)
]
ROSpecStopTrigger_Parameter._PConstraints = [
	(GPITriggerValue_Parameter,				0, 1)
]
AISpec_Parameter._PConstraints = [
	(AISpecStopTrigger_Parameter,			1, 1),
	(InventoryParameterSpec_Parameter,		1, n),
	(Custom_Parameter,						0, n)
]
AISpecStopTrigger_Parameter._PConstraints = [
	(GPITriggerValue_Parameter,				0, 1),
	(TagObservationTrigger_Parameter,		0, 1),
]
InventoryParameterSpec_Parameter._PConstraints = [
	(AntennaConfiguration_Parameter,		0, n),
	(Custom_Parameter,						0, n)
]
RFSurveySpec_Parameter._PConstraints = [
	(RFSurveySpecStopTrigger_Parameter,		1, 1),
	(Custom_Parameter,						0, n)
]
AccessSpec_Parameter._PConstraints = [
	(AccessSpecStopTrigger_Parameter,		1, 1),
	(AccessCommand_Parameter,				1, 1),
	(AccessReportSpec_Parameter,			0, 1),
	(Custom_Parameter,						0, n)
]
AccessCommand_Parameter._PConstraints = [
	(Custom_Parameter,						1, n)
]
AntennaConfiguration_Parameter._PConstraints = [
	(RFReceiver_Parameter,					0, 1),
	(RFTransmitter_Parameter,				0, 1),
	(C1G2InventoryCommand_Parameter, 		0, n),
	(Custom_Parameter,						0, n)
]
ROReportSpec_Parameter._PConstraints = [
	(TagReportContentSelector_Parameter,	1, 1),
	(Custom_Parameter, 						0, n)
]
RFSurveyReportData_Parameter._PConstraints = [
	(ROSpecID_Parameter,					0, 1),
	(SpecIndex_Parameter,					0, 1),
	(FrequencyRSSILevelEntry_Parameter, 	1, n),
	(Custom_Parameter,						0, n),
]
FrequencyRSSILevelEntry_Parameter._PConstraints = [
	((UTCTimestamp_Parameter, Uptime_Parameter),	1, 1)
]
ReaderEventNotificationSpec_Parameter._PConstraints = [
	(EventNotificationState_Parameter,		1, n)
]
#------------------------------------------------------------------
def UnpackMessageFromSocket( sock ):
	# Read the header bytes to get the messageID and length.
	headerBytes = (16+32) >> 3
	message = ''
	while len(message) < headerBytes:
		message += sock.recv( headerBytes - len(message) )
		
	# Convert to a BitStream to get the message Type and Length.
	s = bitstring.ConstBitStream( bytes=message )
	Type = s.read('uintbe:16')
	Type &= ((1<<10)-1)
	Length = s.read('uintbe:32')
	
	# print 'UnpackMessageFromSocket: Type=%d Length=%d %s' % (Type, Length, _messageClassFromType[Type].__name__)
	
	# Read the remaining message from the socket into memory based on the Length.
	while len(message) < Length:
		message += sock.recv( Length - len(message) )
		
	# Convert the full message to a BitStream and parse it.
	s = bitstring.ConstBitStream( bytes=message )
	return _MessagePackUnpackLookup[Type].unpack( s )

def UnpackMessage( s ):
	''' Parameter s is a bitstream. '''
	s.pos = 0
	Type = s.peek('uintbe:16')
	Type &= ((1<<10)-1)
	return _MessagePackUnpackLookup[Type].unpack( s )
	
def PackMessage( m ):
	''' Pack message into a bistream. '''
	assert m.Type in _messageClassFromType
	return m.pack( bitstring.BitStream() )
	
def UnpackParameter( s ):
	Type = s.peek( 'uintbe:8' )
	if Type & (1<<7):
		Type &= ((1<<7) - 1)			# TV Encoding
	else:
		Type = s.peek('uintbe:16')		# TLV Encoding
		Type &= ((1<<10)-1)
	return _ParameterPackUnpackLookup[Type].unpack( s )
	
def GetResponseClass( message ):
	''' Get the corresponding response class of a message. '''
	responseClassName = message.__class__.__name__.replace('_Message', '_RESPONSE_Message')
	return _messageClassFromName[responseClassName]
	
def WaitForMessage( MessageID, ResponseClass, sock ):
	''' Wait for an expected message matching the MessageID and ResponseClass. '''
	while 1:
		response = UnpackMessageFromSocket( sock )
		if response.MessageID == MessageID and isinstance(response, ResponseClass):
			return response
			
#-----------------------------------------------------------------------------

def GetBasicAddRospecMessage( MessageID, ROSpecID = 123, inventoryParameterSpecID = 1234 ):
	#-----------------------------------------------------------------------------
	# Create a basic Reader Operation Spec message
	#
	rospecMessage = ADD_ROSPEC_Message( MessageID = MessageID, Parameters = [
		# Initialize to disabled.
		ROSpec_Parameter( ROSpecID = ROSpecID, CurrentState = ROSpecState_Disabled, Parameters = [
			ROBoundarySpec_Parameter(		# Configure boundary spec (start and stop triggers for the reader).
				Parameters = [
					# Start immediately.
					ROSpecStartTrigger_Parameter(ROSpecStartTriggerType = ROSpecStartTriggerType_Immediate),
					# No stop trigger.
					ROSpecStopTrigger_Parameter(ROSpecStopTriggerType = ROSpecStopTriggerType_Null),
				]
			),
			AISpec_Parameter(				# Antenna Inventory Spec (specifies which antennas and protocol to use)
				AntennaIDs = [0],			# Use all antennas.
				Parameters = [
					AISpecStopTrigger_Parameter( AISpecStopTriggerType = AISpecStopTriggerType_Null ),
					InventoryParameterSpec_Parameter(
						InventoryParameterSpecID = inventoryParameterSpecID,
						ProtocolID = AirProtocols_EPCGlobalClass1Gen2,
					),
				]
			),
			ROReportSpec_Parameter(			# Report spec (specified how often and what to send from the reader)
				ROReportTrigger = ROReportTriggerType_Upon_N_Tags_Or_End_Of_ROSpec,
				N = 1,						# N = 1 --> update on each tag.
				Parameters = [
					TagReportContentSelector_Parameter(
						EnableAntennaID = True,
						EnableFirstSeenTimestamp = True,
						EnableTagSeenCount = True,
					),
				]
			),
		])	# ROSpec_Parameter
	])	# ADD_ROSPEC_Message
	return rospecMessage

def GetEnableRospecMesssage( MessageID, ROSpecID = 123 ):
	return ENABLE_ROSPEC_Message(MessageID = MessageID, ROSpecID = ROSpecID)
	
def _getTagData( self ):
	actions = {
		EPC_96_Parameter:					lambda x: ('EPC', x.EPC),
		EPCData_Parameter: 					lambda x: ('EPC', x.EPC),
		FirstSeenTimestampUTC_Parameter:	lambda x: ('Timestamp', x.Microseconds),
		AntennaID_Parameter:				lambda x: ('AntennaID', x.AntennaID),
		TagSeenCount_Parameter:				lambda x: ('TagSeenCount', x.TagCount),
	}
	tagData = []
	for p in self.Parameters:
		if not isinstance( p, TagReportData_Parameter ):
			continue
		data = {}
		for pp in p.Parameters:
			try:
				key, value = actions[type(pp)](pp)
				data[key] = value
			except KeyError:
				pass
		tagData.append( data )
			
	return tagData

# Add a 'getTagData' convenience method to the RO_ACCESS_REPORT message.
RO_ACCESS_REPORT_Message.getTagData = types.MethodType( _getTagData, None, RO_ACCESS_REPORT_Message )
			
if __name__ == '__main__':
	rospecMessage = GetBasicAddRospecMessage( 1 )
	rospecEnableMessage = GetEnableRospecMesssage( 2 )
	
	print rospecMessage
	rospecMessage._validate()
	
	print rospecEnableMessage
	rospecEnableMessage._validate()
	
	s = rospecMessage.pack( bitstring.BitStream() )
	print s
	
	m = UnpackMessage( s )
	print m
	
	bytes=s.tobytes()
	t = bitstring.ConstBitStream( bytes=bytes )
	n = UnpackMessage( t )
	print n
	
	s = rospecEnableMessage.pack( bitstring.BitStream() )
	print s
	
	m = UnpackMessage( s )
	print m
	
	bytes=s.tobytes()
	t = bitstring.ConstBitStream( bytes=bytes )
	n = UnpackMessage( t )
	print n
	
