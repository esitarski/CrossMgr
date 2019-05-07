import six
import Utils
import Model

def SetNoDataDNS():
	race = Model.race
	if not (race and race.isFinished() and getattr(race, 'setNoDataDNS', False)):
		return
		
	try:
		externalInfo = race.excelLink.read()
	except:
		return
	
	Finisher = Model.Rider.Finisher
	DNS = Model.Rider.DNS
	
	for num in six.iterkeys(externalInfo):
		rider = race.getRider( num )
		if rider.status == Finisher and not rider.times:
			rider.status = DNS
	
	race.setChanged()
