import os
import socket
import asyncio
import datetime

#------------------------------------------------------------------------------	
# JChip delimiter (CR, **not** LF)
CR = '\r'
bCR = CR.encode()
		
#------------------------------------------------------------------------------	
# Function to format number, lap and time in JChip format
# Z413A35 10:11:16.4433 10  10000      C7
count = 0
def formatMessage( tagID, t ):
	global count
	message = "DA{} {} 10  {:05X}      C7 date={}{}".format(
				tagID,								# Tag code in decimal, no leading zeros.
				t.strftime('%H:%M:%S.%f'),			# hh:mm:ss.ff
				count,								# Data index number in hex.
				t.strftime('%Y%m%d'),				# YYYYMMDD
				CR
			)
	count += 1
	return message

class Ubidium2JChip:
	def __init__( self, dataQ, messageQ, crossMgrHost, crossMgrPort ):
		''' Queues:
				dataQ:		tag/timestamp data to be written out to CrossMgr.
				messageQ:	queue to write status messages.
				shutdownQ:	queue to receive shutdown message to stop gracefully.
		'''
		self.dataQ = dataQ
		self.messageQ = messageQ
		self.crossMgrHost = crossMgrHost
		self.crossMgrPort = crossMgrPort
		self.keepGoing = True
		self.tagCount = 0
	
	def shutdown( self ):
		self.keepGoing = False
		
	def checkKeepGoing( self ):
		return self.keepGoing

	async def getCmd( self, reader ):
		# Read from the connection until we get data ending in the delimiter.
		# Handle all exceptions, and return them.
		received = b''
		while self.keepGoing and received[-1:] != bCR:
			try:
				async with asyncio.timeout(5):
					received += await reader.read(4096)
			except Exception as e:
				return received.decode(), e
		return received[:-1].decode(), None

	async def runServer( self ):
		instance_name = '{}-{}'.format(socket.gethostname(), os.getpid())
		while self.checkKeepGoing():
			await self.messageQ.put( ('Ubidium2JChip', 'state', False) )
			await self.messageQ.put( ('Ubidium2JChip', f'Trying to connect to CrossMgr at {self.crossMgrHost}:{self.crossMgrPort} as "{instance_name}"...') )

			#------------------------------------------------------------------------------	
			# Connect to the CrossMgr server.
			#
			self.tagCount = 0
			while self.checkKeepGoing():
				try:
					async with asyncio.timeout(4):
						reader, writer = await asyncio.open_connection( self.crossMgrHost, self.crossMgrPort )
						break
				except Exception as e:
					reader = writer = None
					await self.messageQ.put( ('Ubidium2JChip', f'CrossMgr Connection Failed: {e}.') )
					await self.messageQ.put( ('Ubidium2JChip', f'Trying again at {self.crossMgrHost}:{self.crossMgrPort} as "{instance_name}" in 2 sec...') )
					await asyncio.sleep( 2 )

			async def reset_connection():
				try:
					async with asyncio.timeout(5):
						writer.close()
						await writer.wait_close()
				except Exception:
					pass
				return None, None
				
			if not self.checkKeepGoing():
				break
				
			#------------------------------------------------------------------------------
			# Send client identity.
			#
			await self.messageQ.put( ('Ubidium2JChip', 'state', True) )
			await self.messageQ.put( ('Ubidium2JChip', '******************************' ) )
			await self.messageQ.put( ('Ubidium2JChip', 'CrossMgr Connection succeeded!' ) )
			await self.messageQ.put( ('Ubidium2JChip', f'Sending identifier "{instance_name}"...') )
			try:
				async with asyncio.timeout(5):
					writer.write( f"N0000{instance_name}{CR}".encode() )
					await writer.drain()
			except Exception as e:
				await self.messageQ.put( ('Ubidium2JChip', f'CrossMgr error: {e}.') )
				reader, writer = await reset_connection()
				continue

			#------------------------------------------------------------------------------	
			await self.messageQ.put( ('Ubidium2JChip', 'Waiting for GT (get time) command from CrossMgr...') )
			received, e = await self.getCmd( reader )
			if not self.checkKeepGoing():
				break
			if e:
				await self.messageQ.put( ('Ubidium2JChip', f'CrossMgr error: {e}.') )
				reader, writer = await reset_connection()
				continue
			await self.messageQ.put( ('Ubidium2JChip', f'Received: "{received}" from CrossMgr') )
			if received != 'GT':
				await self.messageQ.put( ('Ubidium2JChip', 'Incorrect command (expected GT).') )
				reader, writer = await reset_connection()
				continue

			# Send 'GT' (GetTime response to CrossMgr).
			await self.messageQ.put( ('Ubidium2JChip', 'Sending GT (get time) response...') )
			# format is GT0HHMMSShh<CR> where hh is 100's of a second.  The '0' (zero) after GT is the number of days running, ignored by CrossMgr.
			dBase = datetime.datetime.now()
			message = 'GT0{} date={}{}'.format(
				dBase.strftime('%H%M%S%f'),
				dBase.strftime('%Y%m%d'),
				CR)
			self.messageQ.put( ('Ubidium2JChip', message[:-1]) )
			try:
				async with asyncio.timeout(5):
					writer.write( message.encode() )
					await writer.drain()
			except Exception as e:
				await self.messageQ.put( ('Ubidium2JChip', f'CrossMgr exception: {e}.') )
				reader, writer = await reset_connection()
				continue

			#------------------------------------------------------------------------------	
			if not self.checkKeepGoing():
				break

			await self.messageQ.put( ('Ubidium2JChip', 'Waiting for S0000 (send) command from CrossMgr...') )
			received, e = await self.getCmd( reader )
			if not self.checkKeepGoing():
				break
			if e:
				await self.messageQ.put( ('Ubidium2JChip', f'CrossMgr error: {e}.') )
				reader, writer = await reset_connection()
				continue
			await self.messageQ.put( ('Ubidium2JChip', f'Received: "{received}" from CrossMgr') )
			if not received.startswith('S'):
				await self.messageQ.put( ('Ubidium2JChip', 'Incorrect command (expected S0000).') )
				reader, writer = await reset_connection()
				continue

			#------------------------------------------------------------------------------
			# Enter "Send" mode - keep sending data until we get a shutdown.
			# If the connection fails, return to the outer loop.
			#
			await self.messageQ.put( ('Ubidium2JChip', 'Start sending data to CrossMgr...') )
			await self.messageQ.put( ('Ubidium2JChip', 'Waiting for RFID reader data...') )
			while self.checkKeepGoing():
				# Get all the entries from the receiver and forward them to CrossMgr.
				try:
					async with asyncio.timeout(1):
						d = await self.dataQ.get()
				except TimeoutError:
					continue
				except Exception as e:
					await self.messageQ.put( ('Ubidium2JChip', f'Ubidium error: {e}.  Attempting to reconnect...') )
					break
				
				# Process the shutdown message.
				if d == 'shutdown':
					self.keepGoing = False
					self.dataQ.task_done()
					break
				
				# Expect message of the form [tag, time].
				message = formatMessage( d[0], d[1] )
				try:
					writer.write( message.encode() )
					async with asyncio.timeout(5):
						await writer.drain()
					self.tagCount += 1
					await self.messageQ.put( ('Ubidium2JChip', f'Forwarded {self.tagCount}: {message[:-1]}') )
				except Exception as e:
					await self.dataQ.put( d )	# Put the data back on the queue for resend.
					await self.messageQ.put( ('Ubidium2JChip', f'CrossMgr error: {e}.') )
					await self.messageQ.put( ('Ubidium2JChip', 'Attempting to reconnect...') )
					break

				self.dataQ.task_done()
				
			try:
				reader, writer = await reset_connection()
			except Exception:
				pass

ubidium2JChip = None
def CrossMgrServer( dataQ, messageQ, crossMgrHost, crossMgrPort ):
	global ubidium2JChip
	ubidium2JChip = Ubidium2JChip( dataQ, messageQ, crossMgrHost, crossMgrPort )
	asyncio.create_task( ubidium2JChip.runServer() )
	
def Shutdown():
	ubidium2JChip.keepGoing = False
