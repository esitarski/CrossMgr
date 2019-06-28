import json
import time
import datetime
import operator
import websocket

PORT_NUMBER = 8765 + 1

def applyRAM( dest, ram ):
	# Apply the RAM information (RAM = Remove, Add, Modify).
	# First apply Add and Modify, which are key/object pairs.
	dest.update( ram['a'] )
	dest.update( ram['m'] )
	# Then apply Deletes, which are an array of keys to delete.
	for k in ram['r']:
		dest.pop( k, None )	# Use pop instead of del (safer).

class SynchronizedRaceData:
	def __init__( self, hostname='localhost', port=PORT_NUMBER ):
		self.info = {}					# Reference data accessed by bib number.
		self.categoryDetails = {}		# Category details accessed by category name.  Includes position order.
		
		self.raceName = ''				# Name of current race.
		self.versionCount = -1			# Current version of the local race.

		self.wsurl = 'ws://' + hostname + ':' + str(PORT_NUMBER) + '/'
	
	def setRaceState( self, message ):
		self.raceName = message['reference']['raceName']
		self.versionCount = message['reference']['versionCount']
	
	def processBaseline( self, message ):
		self.info = message['info']
		self.categoryDetails = message['categoryDetails']
		self.setRaceState( message )
		self.baselinePending = False
	
	def processRAM( self, message ):
		applyRAM( self.info, message['infoRAM'] );
		applyRAM( self.categoryDetails, message['categoryRAM'] );
		self.setRaceState( message )

	def printTop( self ):
		showTop = 5
		print( '********* Top {} Leaders ********* {}'.format(showTop, datetime.datetime.now()) )
		for cat in sorted( self.categoryDetails.values(), key=operator.itemgetter('iSort') ):
			if cat['iSort'] == 0:	# Ignore the 'All' category has iSort=0.
				continue
			print( cat['name'] )
			for rank, bib in enumerate(cat['pos'][:showTop], 1):
				r = self.info.get(str(bib), {})	# Access as a string, not an integer.
				print( '{}. {:4d}: {} {} ({})'.format( rank, bib, r.get('FirstName', ''), r.get('LastName', ''), r.get('Team','') ) )

	def onChange( self ):
		self.printTop()

	def onMessage( self, ws, btext ):
		try:
			message = json.loads( btext )
		except Exception as e:
			return
		if 'cmd' not in message:
			return
		
		if message['cmd'] == 'ram' and not self.baselinePending:
			if self.versionCount + 1 != message['reference']['versionCount'] or self.raceName != message['reference']['raceName']:
				# The versionCount or raceName is out of sync.  Request a full update.
				ws.send(json.dumps({'cmd':'send_baseline', 'raceName':message['reference']['raceName']}).encode())
				self.baselinePending = True	# Set a flag to ignore incremental updates until we get the new baseline.
			else:
				# This delta-update is for the next versionCount and is for this race.  Apply the incremental change.
				self.processRAM( message )
				self.onChange()
			
		elif message['cmd'] == 'baseline':
			self.processBaseline( message )
			self.onChange()
	
	def eventLoop( self ):
		while True:
			try:
				ws = websocket.create_connection( self.wsurl )
				ws.send(json.dumps({'cmd':'send_baseline', 'raceName':'CurrentResults'}).encode())
				while True:
					self.onMessage( ws, ws.recv() )
			except Exception as e:
				print( e )
			time.sleep( 1 )
		
if __name__ == '__main__':
	rd = SynchronizedRaceData()
	rd.eventLoop()	# Never returns.
