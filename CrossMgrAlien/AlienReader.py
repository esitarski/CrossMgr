
import os
import sys
import string
import re
import math
import datetime
import random
from functools import partial

regexURL = re.compile(
	r'^(?:http|ftp)s?://'  # http:// or https://
	r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
	r'localhost|'  # localhost...
	r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
	r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
	r'(?::\d+)?'  # optional port
	r'(?:/?|[/?]\S+)$', re.IGNORECASE)

regexEmail = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain
	
def validateURL( value ):
	if not regexURL.search(value):
		raise ValueError('Invalid URL')
	return True

def validateEmail( value ):
	if not regexEmail.search(value):
		raise ValueError('Invalid Email')
	return True
		
class Type( object ):
	def toStr( self, v ):
		return str(v)
	def validate( self, v ):
		return True
	def fromStr( self, v ):
		return str(v)
	def repValue( self ):
		raise ValueError( 'repValue not implemented' )

class String( Type ):
	def repValue( self ):
		return 'representative string'
	
class NonEmptyString( String ):
	def validate( self, v ):
		if not v:
			raise ValueError( 'String cannot be empty' )
		return True

class MACAddress( Type ):
	def validate( self, v ):
		values = v.split( ':' )
		if len(values) != 6:
			raise ValueError( '{}: Invalid MACAddress: requires 6 hex values'.format(v) )
		for v in values:
			i = int( v, 16 )
		return True
	def repValue( self ):
		return '00:00:00:00:00:00'

class IPAddress( Type ):
	def validate( self, v ):
		values = v.split( '.' )
		if len(values) != 4:
			raise ValueError( '{}: Invalid IPAddress: requires 4 decimal values'.format(v) )
		for v in values:
			i = int( v.strip() )
		return True
	def repValue( self ):
		return '0.0.0.0'

class IPAddressSerial( IPAddress ):
	def validate( self, v ):
		if v.upper() == "SERIAL":
			return True
		return super(IPAddressSerial, self).validate( v )
		
class IPAddressPortSerial( IPAddress ):
	def validate( self, v ):
		if v.upper() == "SERIAL":
			return True
		host, port = v.split( ':' )
		p = int( port )
		return super( IPAddressPortSerial, self ).validate( host )

class IPAddressPortSerialEmail( IPAddressPortSerial ):
	def validate( self, v ):
		if v.find('@') >= 0:
			return validateEmail( v )
		return super( IPAddressPortSerialEmail, self ).validate( host )
		
class URL( Type ):
	def validate( self, v ):
		return validateURL( v )
	def repValue( self ):
		return 'http://www.google.com'
		
class Int( Type ):
	def validate( self, v ):
		if not isinstance(v, int):
			raise ValueError( 'value must be int type' )
		return True
	def fromStr( self, v ):
		return int(v)
	def repValue( self ):
		return 999

class IntRange( Int ):
	def __init__( self, iMin = 0, iMax = sys.maxint ):
		self.iMin, self.iMax = iMin, iMax
	def validate( self, v ):
		if not isinstance(v, int):
			raise ValueError( 'value must be int type' )
		if not (self.iMin <= v <= self.iMax):
			raise ValueError( '{} must be in range [{}, {}] inclusive'.format(v, self.iMin, self.iMax) )
		return True
	def repValue( self ):
		return self.iMin
			
def NonNegInt():
	return IntRange(0, sys.maxint)
			
class IntChoice( Type ):
	def __init__( self, choices ):
		self.choices = choices
	def validate( self, v ):
		i = int(reponse)
		if i not in self.choices:
			raise ValueError( '{} must be one of {}'.format(i, ','.join( '{}'.format(k) for k in self.choices) ) )
		return True
	def fromStr( self, v ):
		return int(v)
	def repValue( self ):
		return choices[0]
		
class StringChoice( Type ):
	def __init__( self, choices ):
		self.choices = choices
	def validate( self, v ):
		if v not in self.choices:
			raise ValueError( '"{}" must be one of {}'.format(v, ','.join( '"{}"'.format(k) for k in self.choices) ) )
		return True
	def fromStr( self, v ):
		return v
	def repValue( self ):
		return choices[0]
		
class Bool( Type ):
	def toStr( self, v ):
		return 'ON' if v else 'OFF'
	def validate( self, v ):
		if not isinstance(v, bool):
			raise ValueError( 'Value must be Bool type' )
		return True
	def fromStr( self, v ):
		return v.upper() == 'ON'
	def repValue( self ):
		return True
		
class DateTime( Type ):
	def toStr( self, v ):
		return v.strftime( '%Y/%M/%D %H:%M:%S' )
	def validate( self, v ):
		if not isintance(v, datetime.datetime):
			raise ValueError( 'Value must be datetime type' )
		return True
	timeDelimTrans = string.maketrans( '/:', '  ' )
	def fromStr( self, v ):
		fields = v.translate(self.timeDelimTrans).split()
		if len(fields) != 6:
			raise ValueError( '{}: wrong number of datetime fields'.format(v) )
		year, month, day, hour, minute, second = fields
		fract, second = math.fmod( float(second) )
		microsecont = fract * 1000000.0
		return datetime.datetime(	year=int(year), month=int(month), day=int(day),
									hour=int(hour), minutes=int(minute), second=int(second), microsecond=int(microsecont) )
	def repValue( self ):
		return datetime.datetime.now()

#-----------------------------------------------------------------------------------------
# Code the operations of each command
#
In, Out, InOut = 'In', 'Out', 'InOut'

OutString			= { Out: String() }
InOutString			= { InOut: String() }
InOutNonEmptyString	= { InOut: NonEmptyString() }
OutNonEmptyString	= { Out: NonEmptyString() }
InOutInt			= { InOut: Int() }
InOutNonNegInt		= { InOut: NonNegInt() }
InOutIPAddress		= { InOut: IPAddress() }
InOutBool			= { InOut: Bool() }
InOutFormat			= { InOut: StringChoice( ('Text', 'Terse', 'XML', 'Custom') ) }

cmds = {
	'Info':				OutString,
	'ReaderName':		OutString,
	'ReaderType':		OutString,
	'ReaderVersion':	OutString,
	'DSPVersion':		OutString,
	'ReaderNumber':		{ InOut: IntRange(1,255) },
	'BaudRate':			{ InOut: IntChoice( (0, 1, 2, 3, 4, 9600, 19200, 38400, 57600, 115200) ) },
	'UpdateTime':		InOutNonNegInt,
	'Username':			InOutNonEmptyString,
	'Password':			InOutNonEmptyString,
	'MaxAntenna':		{ Out: IntRange(0, 7) },
	'AntennaSequence':	InOutNonEmptyString,
	'RFAttenuation':	InOutNonEmptyString,
	'RFLevel':			InOutNonEmptyString,
	'RFModulation':		{ InOut: StringChoice( ('STD', 'HS', 'DRM') ) },
	'FactorySettings':	OutString,
	'Reboot':			OutString,
	'Service':			InOutNonEmptyString,
	'ETSMode':			{ InOut: StringChoice( ('302.208', '300.220') ) },

	'MACAddress':		{ Out: MACAddress() },
	'DHCP':				{ InOut: Bool() },
	'IPAddress':		InOutIPAddress,
	'Gateway':			InOutIPAddress,
	'Netmask':			InOutIPAddress,
	'DNS':				InOutIPAddress,
	'Hostname':			InOutBool,
	'NetworkUpgrade':	InOutBool,
	'UpgradeAddress':	{ InOut: URL() },
	'UpgradeIPAddress':	InOutIPAddress,
	'UpgradePort':		{ InOut: IntRange(0, 65535) },
	'NetworkTimeout':	InOutNonNegInt,
	'CommandPort':		{ InOut: IntRange(0, 65535) },
	'Ping':				InOutString,
	'HeartbeatPort':	{ InOut: IntRange(0, 65535) },
	'HeartbeatTime':	{ InOut: NonNegInt() },
	'HeartbeatAddress':	InOutIPAddress,
	'HeartbeatCount':	{ InOut: IntRange(-1, 65535) },
	'WWWPort':			{ InOut: IntRange(0, 65535) },
	'HostLog':			OutString,
	'DebugHost':		InOutBool,

	'TimeServer':		InOutIPAddress,
	'TimeZone':			{ InOut: IntRange(-13,13) },
	'Time':				{ InOut: DateTime() },

	'ExternalInput':	{ Out: IntRange(0,15) },
	'ExternalOutput':	{ InOut: IntRange(0,15) },
	'InvertExternalInput': InOutBool,
	'InvertExternalOutput': InOutBool,
	'InitExternalOutput': { InOut: IntRange(0,15) },
	'IOList':			OutString,
	'IOType':			{ InOut: StringChoice( ('DI','DO','DIO') ) },
	'IOListFormat':		InOutFormat,
	'IOListCustomFormat': InOutString,
	'IOStreamMode':		InOutBool,
	'IOStreamAddress':	{ InOut: IPAddressSerial() },
	'IOStreamFormat':	InOutFormat,
	'IOStreamCustomFormat': InOutString,
	'IOStreamKeepAliveTime': { InOut: IntRange(0,32767) },

	'TagList':			OutString,
	'PersistTime':		{ InOut: IntRange(-1) },
	'TagListFormat':	InOutFormat,
	'TagListCustomFormat': InOutString,
	'TagListAntennaCombine': InOutBool,
	'TagListMillis':		InOutBool,
	'TagStreamMode':	InOutBool,
	'TagStreamAddress': { InOut: IPAddressPortSerial() },
	'TagStreamFormat':	InOutFormat,
	'TagStreamCustomFormat': InOutString,
	'TagStreamKeepAliveTime': { InOut: IntRange(0,32767) },
	'StreamHeader':		InOutBool,

	'AcquireMode':		{ InOut: StringChoice( ('Inventory', 'Global Scroll') ) },
	'TagType':			{ InOut: IntRange(0,255) },
	'AcqC1Cycles':		{ InOut: IntRange(1,255) },
	'AcqCycles':		{ InOut: IntRange(1,255) },
	'AcqC1EnterWakeCount': { InOut: IntRange(0,255) },
	'AcqEnterWakeCount': { InOut: IntRange(0,255) },
	'AcqC1Count':		{ InOut: IntRange(1,255) },
	'AcqCount':			{ InOut: IntRange(1,255) },
	'AcqC1SleepCount':	{ InOut: IntRange(0,255) },
	'AcqSleepCount':	{ InOut: IntRange(0,255) },
	'AcqC1ExitWakeCount': { InOut: IntRange(0,255) },
	'AcqExitWakeCount': { InOut: IntRange(0,255) },
	'AcqG2Cycles':		{ InOut: IntRange(1,255) },
	'AcqG2Count':		{ InOut: IntRange(1,255) },
	'AcqG2Q':			{ InOut: IntRange(0,5) },

	'AutoMode':			InOutBool,
	'AutoWaitOutput':	{ InOut: IntRange(0,15) },
	'AutoStartTrigger':	InOutString,
	'AutoStartPause':	{ InOut: NonNegInt() },
	'AutoWorkOutput':	{ InOut: IntRange(0,15) },
	'AutoAction':		{ InOut: StringChoice(('None','Acquire','ProgramEPC','Erase','ProgramAndLockEPC','Kill')) },
	'AutoStopTrigger':	InOutString,
	'AutoStopTimer':	{ InOut: IntRange(-1, 86400000) },
	'AutoStopPause':	InOutNonNegInt,
	'AutoTrueOutput':	{ InOut: IntRange(-1,15) },
	'AutoTruePause':	InOutNonNegInt,
	'AutoFalseOutput':	{ InOut: IntRange(-1,15) },
	'AutoFalsePause':	InOutNonNegInt,
	'AutoModeStatus':	OutNonEmptyString,
	'AutoModeReset':	OutNonEmptyString,
	'AutoModeTriggerNow': OutNonEmptyString,

	'NotifyMode':		InOutBool,
	'NotifyAddress':	{ InOut: IPAddressPortSerialEmail },
	'NotifyTime':		InOutNonNegInt,
	'NotifyTrigger':	{ InOut: StringChoice( ('Add','Remove','Change','True','False','TrueFalse') ) },
	'NotifyFormat':		InOutFormat,
	'NotifyHeader':		InOutBool,
	'NotifyKeepAliveTime':	{ InOut: IntRange(0,65535) },
	'MailServer':		{ InOut: IPAddress() },
	'MailFrom':			InOutString,
	'NotifyRetryCount':	{ InOut: IntRange(-1,32767) },
	'NotifyRetryPause':	{ InOut: IntRange(0,32767) },
	'NotifyQueueLimit':	{ InOut: IntRange(0,1000) },
	'NotifyInclude':	{ InOut: StringChoice( ('Tags','DI','DO','DIO','All') ) },
	'NotifyNow':		OutNonEmptyString,
	
	'Function':			{ InOut: StringChoice( ('Programmer','Reader') ) },
	'Clear':			OutNonEmptyString,
}

# Validate that all the commands are coded correctly.
cmdsNormalized = {}
for cmd, cmdInfo in cmds.iteritems():
	assert isinstance(cmd, basestring)
	try:
		assert isinstance(cmdInfo, dict)
	except AssertionError:
		print ( 'command: "{}" is described incorrectly:'.format(cmd), cmdInfo )
		raise
		
	# Check if InOut is specified, it is the only type.
	if cmdInfo.get(InOut, None):
		try:
			assert len(cmdInfo) == 1
		except AssertionError:
			print ( 'command: "{}" specifies InOut but also has other specifier: {}'.format(cmd, tName), ','.join( cmdInfo.keys() ) )
			raise
	
	# Check for any unknown type specifiers.
	for tName, tValue in cmdInfo.iteritems():
		try:
			assert tName in [In, Out, InOut]
		except AssertionError:
			print ( 'command: "{}" has unknown specifier: {}'.format(cmd, tName) )
			raise
			
	# Normalize types to In and Out only
	try:
		inType = outType = cmdInfo[InOut]
		del cmdInfo[InOut]
	except KeyError:
		inType, outType = cmdInfo.get(In, None), cmdInfo.get(Out, None)
	cmdInfo[In] = inType
	cmdInfo[Out] = outType
	
	# Normalize the cmd name to upper case.
	cmdsNormalized[cmd.upper()] = cmdInfo
	
cmds = cmdsNormalized
		
def sendCmd( cmdSocket, cmd, cmdStr, outType ):
	if not cmdSocket:
		if cmdStr.startswith( 'set ' ):
			return cmdStr[4:]
		elif cmdStr.startswith( 'Clear' ):
			return '{} has been cleared!'.format(cmdStr.split()[1])
		return outType.toStr( outType.repValue() )
	else:
		# Send the command to the Alien reader and get the response.
		pass

alienProperties = {}
def setter( self, value, cmd, inType, outType ):
	if not inType:
		raise ValueError( '"{}" is a read only'.format(cmd) )
	
	assert inType.validate(value)
	
	inStr = inType.toStr( value )
	response = sendCmd( self.cmdSocket, cmd, u'set {} = {}'.format(cmd, inStr), outType )
	
	if not outType:
		return None
	
	ieq = response.index( '=' )
	retcmd, retValue = response[:ieq], response[ieq+1:]
	ret = outType.fromStr( retValue.strip() )
	if self.testMode:
		print(cmd, '=', ret)
	return ret

def getter( self, cmd, inType, outType ):
	if not outType:
		raise ValueError( '"{}" is a write only'.format(cmd) )

	# Send the command and return the response.
	cmdStr = ('get {}'.format(cmd)) if inType else cmd
	response = sendCmd( self.cmdSocket, cmd, cmdStr, outType )
	try:
		ieq = response.index( '=' )
		retcmd, retValue = response[:ieq], response[ieq+1:]
		ret = outType.fromStr( retValue.strip() )
	except:
		ret = outType.fromStr( response )
	if self.testMode:
		print('{}:'.format(cmd), ret)
	return ret
	
def deleter( self, cmd, inType, outType ):
	raise ValueError( 'Cannot delete command "{}"'.format(cmd) )
			
for cmd, cmdInfo in cmds.iteritems():
	context = { 'cmd': cmd, 'inType':  cmdInfo[In], 'outType': cmdInfo[Out] }
	alienProperties[cmd] = property( partial(getter,**context), partial(setter,**context), partial(deleter,**context), cmd )

AlienProperties = type( 'AlienProperties', (object,), alienProperties )
print(dir(AlienProperties))

class AlienRdr( AlienProperties ):
	def __init__( self ):
		self.cmdSocket = None
		self.testMode = True

ar = AlienRdr()
#ar.Password = 'ems'
ar.NotifyHeader = True
	
#-----------------------------------------------------------------------------------------------
	
class CmdSocket( object ):
	def __init__( self, ar, username = 'alien', password = 'password', testMode = False ):
		self.ar = ar
		self.username = username
		self.password = password
		self.testMode = testMode
	
	def __enter__( self ):
		self.ar.testMode = self.testMode
		if not self.testMode:
			self.ar.OpenCmdSocket( self.username, self.password )
		
	def __exit__( self, type, value, traceback ):
		self.ar.CloseCmdSocket()
		
class AlienReader( object ):
	CmdDelim = '\r\n'
	ResponseDelim = '\r\n\0'
	SupressPrefix = '\1'
	
	nonCmdAttributes = set( ('testMode', 'CmdHost', 'CmdPort', 'cmdSocket', 'keepGoing') )
	def __init__( self ):
		self.testMode = True
		self.CmdHost = None
		self.CmdPort = None
		self.cmdSocket = None
		self.keepGoing = True

	def checkKeepGoing( self ):
		return self.keepGoing
	
	def GetHeartbeat( self, heartbeatPort = 3988 ):
		heartbeatSocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
		heartbeatSocket.settimeout( 1 )
		heartbeatSocket.bind( ('', heartbeatPort) )

		data = None
		while self.checkKeepGoing():
			try:
				data, addr = heartbeatSocket.recvfrom( 2048 )
				break
			except socket.timeout:
				pass
				
		heartbeatSocket.close()
		
		if not data:
			return None

		data = data.replace( '\0', '' )
		doc = parseString( data.strip() )
			
		info = {}
		for h in doc.getElementsByTagName( 'Alien-RFID-Reader-Heartbeat' ):
			for c in h.childNodes:
				if c.nodeType == c.ELEMENT_NODE:
					info[c.tagName] = c.firstChild.nodeValue.strip()
			break
		self.CmdHost = info['IPAddress']
		self.CmdPort = int(info['CommandPort'])
		return data
	
	def OpenCmdSocket( self, username = 'alien', password = 'password' ):
		ar.cmdSocket = socket.stocket( socket.AF_INET, socket.SOCK_STREAM )
		ar.bind( (ar.CmdHost, ar.cmdSocket) )

	def CloseCmdSocket( self ):
		if self.cmdSocket:
			self.ar.cmdSocket.close()
			self.ar.cmdSocket = None
		
	def __getattr__( self, name ):
		try:
			cmdInfo = cmds[name.upper()]
		except KeyError:
			raise ValueError( '"{}" is not a recognized command'.format(name) )
		
		inType, outType = cmdInfo[In], cmdInfo[Out]
		if not outType:
			raise ValueError( '{} has no return value'.format(name) )
				
		# Send the command and return the response.
		cmdStr = ('get {}'.format(name)) if inType else name
		response = self.sendCmd( name, cmdStr )
		try:
			ieq = response.index( '=' )
			retName, retValue = response[:ieq], response[ieq+1:]
			ret = outType.fromStr( retValue.strip() )
		except:
			ret = outType.fromStr( response )
		if self.testMode:
			print ( '{}:'.format(name), ret )
		return ret
		
	def __setattr__( self, name, value ):
		if name in self.nonCmdAttributes:
			return super( AlienReader, self ).__setattr__(name, value)
			
		try:
			cmdInfo = cmds[name.upper()]
		except KeyError:
			raise ValueError( '{} is not a recognized command'.format(name) )
		
		inType, outType = cmdInfo[In], cmdInfo[Out]
		if not inType:
			raise ValueError( '{} is a read only attribute'.format(name) )
		
		assert inType.validate(value)
		
		inStr = inType.toStr( value )
		response = self.sendCmd( name, 'set {} = {}'.format(name, inStr) )
		
		if not outType:
			return None
		
		ieq = response.index( '=' )
		retName, retValue = response[:ieq], response[ieq+1:]
		ret = outType.fromStr( retValue.strip() )
		if self.testMode:
			print('{}={}'.format( name, ret ))
		return ret
	
	def getResponse( self, conn ):
		# Read delimited data from the reader
		response = ''
		while not response.endswith( self.ReaderDelim ):
			more = conn.recv( 4096 )
			if not more:
				break
			response += more
		return response
	
	def sendCmd( self, name, cmdStr ):
		if self.testMode:
			if cmdStr.startswith( 'set ' ):
				return cmdStr[4:]
			elif cmdStr.startswith( 'Clear' ):
				return '{}s has been cleared!'.format(cmdStr.split()[1])
			cmdInfo = cmds[name.upper()]
			outType = cmdInfo.get(InOut, None) or cmdInfo.get(Out, None)
			return outType.toStr( outType.repValue() )
		else:
			# Send the command to the Alien reader and get the response.
			self.cmdSocket.sendall( u'{}{}{}'.format(self.SupressPrefix, cmdStr, self.CmdDelim).encode() )
			response = self.getResponse( self.cmdSocket )
			return response
	
	def Clear( self, listName ):
		if listName not in ['IOList', 'TagList']:
			raise ValueError( '{} is not a list for Clear'.format(listName) )
		ret = self.sendCmd( 'Clear', 'Clear {}'.format(listName) )
		if self.testMode:
			print ( 'Clear:', ret )
		return ret == '{} has been cleared!'.format(listName if listName != 'IOList' else 'IO List')

	def execCmd( self, cmdStr ):
		cmdStr = cmdStr.strip()
		if cmdStr.startswith('?'):
			return self.__getattr__( cmdStr[1:].strip() )
		if cmdStr.lower().startswith('get '):
			return self.__getattr__( cmdStr[4:].strip() )
		if cmdStr.lower().startswith('clear '):
			clr, listName = cmdStr.split()
			return self.Clear( listName )
		if cmdStr.lower().startswith( 'set ' ):
			name, value = [s.strip() for s in cmdStr[4:].split( '=', 1 )]
			try:
				cmdInfo = cmds[name.upper()]
			except KeyError:
				raise ValueError( '{} is not a recognized command'.format(name) )
			value = cmdInfo[In].fromStr( value )
			return self.__setattr__( name, value )
		return self.__getattr__( name )
	
if __name__ == '__main__':
	ar = AlienReader()
	with CmdSocket( ar, 'alien', 'password', testMode = True ):
		ar.TagListMillis = True
		ar.PersistTime = 2
		ar.HeartbeatTime = 15
		
		ar.AutoModeReset
		ar.AutoStopTimer = 0
		ar.AutoAction = 'Acquire'
		ar.AutoTruePause = 0 
		ar.AutoFalsePause = 0
		ar.AutoStartTrigger = '0,0'
		
		ar.NotifyKeepAliveTime = 30
		ar.NotifyHeader = True
		ar.NotifyQueueLimit = 1000
		ar.NotifyInclude = 'Tags'
		ar.NotifyRetryPause = 10
		ar.NotifyRetryCount = -1
		ar.NotifyFormat = 'XML'
		ar.NotifyTrigger = 'Add'
		ar.Clear( 'TagList' )

		ar.Function = 'Reader'

		ar.NotifyMode = True
		ar.AutoMode = True
