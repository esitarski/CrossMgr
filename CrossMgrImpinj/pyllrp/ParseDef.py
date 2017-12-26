#---------------------------------------------------------------------------
#
# Reformats the llrpdef.xml file into a Python-formatted description llrpdef.py
#
# The reason we so this is so we avoid a dependency on the xml parser in deployment.
# It is also much faster to use the .pyc file rather than parsing XML again
# on startup.
#
from xml.dom.minidom import parse
import datetime
import pprint
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
	Choices = [ (int(toAscii(c.attributes['value'].value)), toAscii(c.attributes['name'].value))
		for c in e.childNodes if c.nodeName == 'entry' ]
	return {'name':Name, 'choices':tuple(Choices) }

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
		Fields.append( {'name': 'VendorIdentifier', 'type': 'uintbe:32', 'default': vendors[toAscii(n.attributes['vendor'].value)]} )
		if isMessage:
			Fields.append( {'name': 'MessageSubtype', 'type': 'uintbe:8', 'default': int(n.attributes['subtype'].value)} )
		else:
			Fields.append( {'name': 'ParameterSubtype', 'type': 'uintbe:32', 'default': int(n.attributes['subtype'].value)} )
	
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
		elif c.nodeName == 'parameter' or c.nodeName == 'choice':
			repeat = toAscii(c.attributes['repeat'].value)
			minMax = repeat.split('-')
			if len(minMax) == 1:
				rMin = rMax = int(repeat)
			else:
				rMin = int(minMax[0])
				rMax = int(minMax[1]) if minMax[1] != 'N' else 99999
			Parameter = toAscii(c.attributes['type'].value)
			Parameters.append( {'parameter':Parameter, 'repeat': (rMin, rMax), 'choice': int(c.nodeName == 'choice')} )
	pm = {'name':Name, 'typeNum':TypeNum}
	if Fields:
		pm['fields'] = tuple(Fields)
	if Parameters:
		pm['parameters'] = tuple(Parameters)
	return pm
	
def getVendorCode( n ):
	name = toAscii(n.attributes['name'].value)
	id = int(n.attributes['vendorID'].value)
	return (name, id)

def getChoiceDefinition( n ):
	choices = {}
	name = toAscii(n.attributes['name'].value)
	for c in n.childNodes:
		if c.nodeName == 'parameter':
			choices[toAscii(c.attributes['type'].value)] = name	
	return choices

enums, parameters, messages = [], [], []
vendors = {}
choiceDefinitions = {}

llrpDefXml = 'llrp-1x0-def.xml'
dom = parse( llrpDefXml )

vendors.update( dict(getVendorCode(v) for v in dom.getElementsByTagName('vendorDefinition')) )
enums = [getEnum(e) for e in dom.getElementsByTagName('enumerationDefinition')]
parameters = [getParameterMessage(p, False) for p in dom.getElementsByTagName('parameterDefinition')]
messages = [getParameterMessage(m, True) for m in dom.getElementsByTagName('messageDefinition')]
for c in dom.getElementsByTagName('choiceDefinition'):
	choiceDefinitions.update( getChoiceDefinition(c) )
del choiceDefinitions['Custom']

dom.unlink()
dom = None

llrpCustomDefXml = 'Impinjdef-1.18-private.xml'
dom = parse( llrpCustomDefXml )

vendors.update( dict(getVendorCode(v) for v in dom.getElementsByTagName('vendorDefinition')) )
enums.extend( getEnum(e) for e in dom.getElementsByTagName('customEnumerationDefinition') )
parameters.extend( getParameterMessage(p, False) for p in dom.getElementsByTagName('customParameterDefinition') )
messages.extend( getParameterMessage(m, True) for m in dom.getElementsByTagName('customMessageDefinition') )
for p in dom.getElementsByTagName('customParameterDefinition'):
	choiceDefinitions[toAscii(p.attributes['name'].value)] = 'Custom'

with open('llrpdef.py', 'w') as fp:
	fp.write( '#-----------------------------------------------------------\n' )
	fp.write( '# DO NOT EDIT!\n' )
	fp.write( '# MACHINE GENERATED from "{}" and "{}"\n'.format(llrpDefXml, llrpCustomDefXml) )
	fp.write( '#\n' )
	fp.write( '#-----------------------------------------------------------\n' )
	for n in ['vendors', 'enums', 'parameters', 'messages', 'choiceDefinitions']:
		fp.write( '{}='.format(n) )
		pprint.pprint( globals()[n], fp )
		fp.write( '\n' )
