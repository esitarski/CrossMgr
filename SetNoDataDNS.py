import Utils
import Model

def SetNoDataDNS():
	race = Model.race
	if not race or not race.setNoDataDNS:
		return
		
	try:
		externalInfo = race.excelLink.read()
	except Exception:
		return
	
	Finisher, DNS, NP = Model.Rider.Finisher, Model.Rider.DNS, Model.Rider.NP
	
	isChanged = False
	
	if race.isRunning():
		for num in externalInfo.keys():
			rider = race.getRider( num )
			if rider.status == NP:
				if rider.times:
					rider.status = Finisher
					isChanged = True
			elif rider.status == Finisher:
				if not rider.times:
					rider.status = NP
					isChanged = True
	
	elif race.isFinished():
		for num in externalInfo.keys():
			rider = race.getRider( num )
			if rider.status == NP:
				if rider.times:
					rider.status = Finisher
					isChanged = True
			elif rider.status == Finisher:
				if not rider.times:
					rider.status = DNS
					isChanged = True
	
	if isChanged:
		race.setChanged()
