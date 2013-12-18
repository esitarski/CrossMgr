#---------------------------------------------------------------------------
#
# Reformats the llrpdef.xml file into a json (aka Python) formatted description llrpdef.py
#
# The reason we so this is so we avoid using the xml parser during deployment.
# It is also faster to use the pre-compiled Python data structures rather than parsing XML
# on every start up.
#
from xml.dom.minidom import parse
import datetime
import json
import sys

# Map the xml field types to our types (bitstring standard, and our custom ones).
fieldMap = {
	'u1':		'bool',
	'u2':		'bits:2',
	'u8':		'uintbe:8',
	'u16':		'uintbe:16',
	'u32':		'uintbe:32',
	'u64':		'uintbe:64',
	'u96':		'uintbe:96',
	
	's8':		'intbe:8',
	's16':		'intbe:16',
	's32':		'intbe:32',
	's64':		'intbe:64',
	
	'utf8v':	'string',
	
	'u1v':		'bitarray',
	'u8v':		'array:8',
	'u16v':		'array:16',
	'u32v':		'array:32',
	
	'bytesToEnd':	'bytesToEnd',	# Used for the Custom message type.
}

def toAscii( s ):
	return s.encode('ascii', 'ignore')

def getEnum( e ):
	Name = toAscii(e.attributes['name'].value)
	Choices = [ [int(toAscii(c.attributes['value'].value)), toAscii(c.attributes['name'].value)]
		for c in e.childNodes if c.nodeName == 'entry' ]
	return {'name':Name, 'choices':Choices }

def getParameterMessage( n, isMessage ):
	Name = toAscii(n.attributes['name'].value)
	
	Fields = []
	Parameters = []
	
	print Name, 'Message' if isMessage else 'Parameter'
	try:
		TypeNum = int(n.attributes['typeNum'].value)
	except KeyError:
		# This is a custom parameter or message.
		TypeNum = 1023		# Code for custom Message and Parameter.
		Fields.append( {'name': 'VendorIdentifier', 'type': 'uintbe:32', 'default': 25882} )	# Impinj Vendor Number
		Fields.append( {'name': 'MessageSubtype' if isMessage else 'ParameterSubtype', 'type': 'uintbe:8',
						'default': int(n.attributes['subtype'].value)} )
	
	for c in n.childNodes:
		if c.nodeName == 'field':
			fieldInfo = { 'name': toAscii(c.attributes['name'].value), 'type': fieldMap[toAscii(c.attributes['type'].value)] }
			try:
				fieldInfo['enumeration'] = toAscii(c.attributes['enumeration'].value)
			except:
				pass
			try:
				fieldInfo['format'] = toAscii(c.attributes['format'].value)
			except:
				pass
			Fields.append( fieldInfo )
		elif c.nodeName == 'reserved':
			bitCount = int(toAscii(c.attributes['bitCount'].value))
			code = 'skip:%d' % bitCount
			Fields.append( {'name':code, 'type':code} )
		elif c.nodeName == 'parameter':
			repeat = toAscii(c.attributes['repeat'].value)
			minMax = repeat.split('-')
			if len(minMax) == 1:
				rMin = rMax = int(repeat)
			else:
				rMin = int(minMax[0])
				rMax = int(minMax[1]) if minMax[1] != 'N' else 99999
			Parameter = toAscii(c.attributes['type'].value)
			Parameters.append( {'parameter':Parameter, 'repeat': [rMin, rMax]} )
	pm = {'name':Name, 'typeNum':TypeNum}
	if Fields:
		pm['fields'] = Fields
	if Parameters:
		pm['parameters'] = Parameters
	return pm

enums, parameters, messages = [], [], []

llrpDefXml = 'llrp-1x0-def.xml'
dom = parse( llrpDefXml )

enums = [getEnum(e) for e in dom.getElementsByTagName('enumerationDefinition')]
parameters = [getParameterMessage(p, False) for p in dom.getElementsByTagName('parameterDefinition')]
messages = [getParameterMessage(m, True) for m in dom.getElementsByTagName('messageDefinition')]

dom.unlink()
dom = None

llrpCustomDefXml = 'Impinjdef-1.18-private.xml'
dom = parse( llrpCustomDefXml )

enums.extend( getEnum(e) for e in dom.getElementsByTagName('customEnumerationDefinition') )
parameters.extend( getParameterMessage(p, False) for p in dom.getElementsByTagName('customParameterDefinition') )
messages.extend( getParameterMessage(m, True) for m in dom.getElementsByTagName('customMessageDefinition') )

with open('llrpdef.py', 'w') as fp:
	fp.write( '#-----------------------------------------------------------\n' )
	fp.write( '# DO NOT EDIT!\n' )
	fp.write( '# MACHINE GENERATED from %s\n' % llrpDefXml )
	fp.write( '#\n' )
	fp.write( '# Created: %s \n' % datetime.datetime.now() )
	fp.write( '#-----------------------------------------------------------\n' )
	for n in ['enums', 'parameters', 'messages']:
		fp.write( '%s = ' % n )
		json.dump( globals()[n], fp, indent=1, sort_keys=True )
		fp.write( '\n' )
