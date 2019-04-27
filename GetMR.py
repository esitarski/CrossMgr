import os
import six
import datetime
import xml.etree.ElementTree as ET
import Utils
from GetResults import GetResults
from ReadSignOnSheet	import ReportFields
import Model
import Version
from collections import OrderedDict

def getRaceAttr( race ):
	try:
		reportFields = set( ReportFields )
		infoFields = [f for f in race.excelLink.getFields() if f in reportFields]
	except AttributeError:
		infoFields = []
	
	return OrderedDict([
		('version',		Version.AppVerName),
		('created',		datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
		('raceName',	race.name),
		('raceLongName',race.longName),
		('raceDate',	race.date),
		('raceTime',	race.scheduledStart),
		('city',		race.city),
		('stateProv',	race.stateProv),
		('country',		race.country),
		('organizer',	getattr(race, 'organizer', '')),
		('email',		race.email),
		('distanceUnit',['km', 'miles'][race.distanceUnit]),
		('speedUnit', 	['km/h', 'mph'][race.distanceUnit]),
		('isRunning',	race.isRunning()),
		('isTimeTrial',	race.isTimeTrial),
		('winAndOut',	race.winAndOut),
		('rfid',		race.enableJChipIntegration),
		('infoFields',	infoFields),
	])

def getCategoryAttr( category ):
	return OrderedDict([
		('categoryFullName',	category.fullname),
		('categoryName',		category.name),
		('categoryGender',		category.gender),
		('categoryType',		['StartWave', 'Component', 'Custom'][category.catType]),
	])
	
ignoreAttr = { 'lastTimeOrig', 'raceCat', 'interp', 'gapValue', 'raceTimes' }
attrSub = { 'num': 'bib' }
def getRaceResultsAttr( rr ):
	attrs = OrderedDict()
	for attr, value in six.iteritems(rr.__dict__):
		if attr.startswith('_') or attr in ignoreAttr:
			continue
		if attr == 'status':
			value = Model.Rider.statusNames[value].lower()
		attrs[attrSub.get(attr, attr)] = value
	return attrs

def GetXML():
	race = Model.race
	if not race:
		return ''
		
	eventE = ET.Element('event')
	
	raceAttr = getRaceAttr( race )
	for k, v in six.iteritems(raceAttr):
		if k == 'infoFields':
			infoFieldsE = ET.SubElement( eventE, k )
			for f in v:
				ET.SubElement( infoFieldsE, 'f' ).text = six.text_type( f )
		else:
			ET.SubElement( eventE, k ).text = six.text_type( v )
	
	raceResultsE = ET.SubElement( eventE, 'raceResults' )
	for category in race.getCategories(startWaveOnly=False, publishOnly=False):
		categoryE = ET.SubElement( raceResultsE, 'category' )
		for k, v in six.iteritems(getCategoryAttr(category)):
			ET.SubElement( categoryE, k ).text = six.text_type( v )
		categoryResultsE = ET.SubElement( categoryE, 'categoryResults' )
		results = GetResults( category )
		for rr in results:
			entryE = ET.SubElement( categoryResultsE, 'entry' )
			for k, v in six.iteritems(getRaceResultsAttr(rr)):
				if k == 'lapTimes':
					attrE = ET.SubElement( entryE, k )
					for t in v:
						ET.SubElement( attrE, 't' ).text = six.text_type(t)
				else:
					ET.SubElement( entryE, k ).text = six.text_type(v)
				
	return ET.tostring(eventE, 'utf-8')
	
def GetJSON():
	race = Model.race
	if not race:
		return ''
		
	raceAttr = getRaceAttr( race )
	raceResults = []
	for category in race.getCategories(startWaveOnly=False, publishOnly=False):
		categoryAttr = getCategoryAttr(category)
		categoryAttr['categoryResults'] = [getRaceResultsAttr(rr) for rr in GetResults(category)]
		raceResults.append( categoryAttr )
	raceAttr['raceResults'] = raceResults

	return Utils.ToJson( raceAttr )
	
from xml.dom import minidom
if __name__ == '__main__':
	race = Model.newRace()
	race._populate()

	xml = GetXML()
	six.print_( xml )
	six.print_( '\n'.join( minidom.parseString( xml ).toprettyxml(indent=" ").split('\n')[:50] ) )
	six.print_( GetJSON() )
