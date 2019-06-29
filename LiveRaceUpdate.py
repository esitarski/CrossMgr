import json
import time
import datetime
import operator
import websocket

#-----------------------------------------------------------------------
#
# This program connects to CrossMgr's "announcer" websocket and shows
# a top 5 for each category of a live race.
#
# A good way to see it in action is to start CrossMgr then do "Tools|Simulation".
# Then start LiveRaceUpdate.py on the same machine.
# It processes the baseline and update messages from CrossMgr to show the top 5
# for each category (similar to the Announcer screen).
# The program can be used as a basis for real time external interfaces to
# CrossMgr like leaderboards, etc.
#
# There is no "polling" in the interface.
#
# Rather, after any race changes, CrossMgr sends an update message over the websocket.
# An update message is in RAM format (Remove, Add, Modify) (like CRUD, but everything renamed and no "R" ;).
# CrossMgr doesn't send an event on every race change, rather, it waits a second or two and
# bundles everyting one message.  This improves performance and eliminates update "nervousness".
#
# Of course, an update message can only be applied *if* you are on the current
# version of the race data.  This is indicated by the versionCount.
# If your local versionCount is one less than the update's versionCount, it can be
# applied safely.
# If not, you need to request a new baseline.  This retrieves all the information.
#
# There is an incredible amount of data in the "info" and "categoryDetails".
# I suggest printing it out to see what it there.
# This program only uses name and team from "info", and uses the name and pos fields in "categoryDetails".
# There is a ton more in there including gaps, status etc.
#
# This program is basically "fire and forget".  It will respond to updates when new race data
# is received, and calls "onChange".  Just like the Announcer screen in CrossMgr, it will also update
# for reference information changes, for example, if you correct a misspelled name or team.
#

PORT_NUMBER = 8765 + 1	# CrossMgr announter port.

def applyRAM( dest, ram ):
	# Apply the RAM information (RAM = Remove, Add, Modify).
	# It is only safe to apply the RAM update *if* the update versionCount is one greater than the last versionCount.
	# Otherwise if it necessary to request a new baseline.
	
	# First apply Add and Modify, which are key/object pairs.
	dest.update( ram['a'] )
	dest.update( ram['m'] )
	# Then apply Deletes, which are an array of keys to delete.
	for k in ram['r']:
		dest.pop( k, None )	# Use pop instead of del (safer).

class SynchronizedRaceData:
	def __init__( self, hostname='localhost', port=PORT_NUMBER ):
		self.info = {}					# Reference data accessed by bib number.
		self.categoryDetails = {}		# Category details accessed by category name.  Includes current position of all participats.
		
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
		# Example "do something" with the results.
		showTop = 5
		print( '********* Top {} Leaders ********* {}'.format(showTop, datetime.datetime.now()) )
		# Sort the categoryDetails by "iSort" so they come out in the same order as CrossMgr.
		for cat in sorted( self.categoryDetails.values(), key=operator.itemgetter('iSort') ):
			if cat['iSort'] == 0:	# Ignore the 'All' category has iSort=0.
				continue
			print( cat['name'] )
			for rank, bib in enumerate(cat['pos'][:showTop], 1):
				# Get the reference information for this bib number.
				r = self.info.get(str(bib), {})	# Access as a string, not an integer.
				print( '{}. {:4d}: {} {} ({})'.format( rank, bib, r.get('FirstName', ''), r.get('LastName', ''), r.get('Team','') ) )

	def onChange( self ):
		# Called after any change.  Subclass to specialize.
		self.printTop()

	def onMessage( self, ws, btext ):
		try:
			message = json.loads( btext )
		except Exception as e:
			return
		if 'cmd' not in message:
			return
		
		if message['cmd'] == 'ram':
			if not self.baselinePending:
				# If the versionCount or raceName is out of sync.  Request a full update.
				if self.versionCount + 1 != message['reference']['versionCount'] or self.raceName != message['reference']['raceName']:
					ws.send( json.dumps({'cmd':'send_baseline', 'raceName':message['reference']['raceName']}).encode() )
					self.baselinePending = True	# Set flag to ignore incremental updates until we get the new baseline.
				else:
					# Otherwise, it is safe to apply this update.
					self.processRAM( message )
					self.onChange()
			
		elif message['cmd'] == 'baseline':
			self.processBaseline( message )
			self.onChange()
	
	def onException( self, e ):
		# Called after connection exceptions.  Subclass to specialize.
		print( e )
	
	def eventLoop( self ):
		while True:
			try:
				ws = websocket.create_connection( self.wsurl )
				ws.send( json.dumps({'cmd':'send_baseline', 'raceName':'CurrentResults'}).encode() )
				while True:
					self.onMessage( ws, ws.recv() )
			except Exception as e:
				self.onException( e )
			time.sleep( 1 )
		
if __name__ == '__main__':
	rd = SynchronizedRaceData()
	rd.eventLoop()	# Never returns.
