""""
File:		   bcListener.py
Date:		   18.09.2024

Description:	UDP server which is listening to shout broadcast messages from Ubidiums.
				Server is listening on port 3603 and updates a list with detected devices.  
"""

import asyncio
import socket
from datetime import datetime, timedelta

from UbidiumSDK.ubidium import status_pb2

NOT_SEEN_THRESHOLD = timedelta(seconds=15)
PORT = 3603

class UbidiumWatcher:

	def __init__(self, messageQ):
		self.messageQ = messageQ
		self.deviceID = ""
		self.terminateSig = False
		self.foundIPs = {}
		self.lastSeen = {}
		self.activeCons = {}	# This is set externally to this class (bad programming!).
		self.udpTask = None
		self.IPLock = asyncio.Lock()

	def startMonitorBC(self):
		self.udpTask = asyncio.create_task(self.runUDPServer())
	
	async def stopMonitorBC(self):
		self.terminateSig = True
		if self.udpTask:
			await self.udpTask
			self.udpTask = None
	
	async def stopTasks(self):
		await stopMonitoringBC()
		for client in self.activeCons.values():
			await client.CloseStatusStream()
			await client.ClosePassingStream()
			await client.StopTasks()
		self.foundIPs.clear()
		self.lastSeen.clear()
		sellf.activeCons.clear()
	
	async def runUDPServer(self):
		loop = asyncio.get_running_loop()

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('0.0.0.0', PORT))
		sock.setblocking(False)
		sock.settimeout(5)

		while not self.terminateSig:
			try:
				data, addr = await loop.run_in_executor(None, sock.recvfrom, 4096)
			except socket.timeout:
				self.messageQ.put_nowait( ('Ubidium', "UbidiumWatcher: No Ubidium devices detected in the last 5 seconds...") )
				continue
			except Exception as err:
				self.messageQ.put_nowait( ('Ubidium', f"UbidiumWatcher: Error receiving data: {err}") )
				continue

			shout = status_pb2.Shout()
			if not shout.ParseFromString(data):
				self.messageQ.put_nowait( ('Ubidium', "UbidiumWatcher: Failed to parse Ubidium device notification data.") )
				continue

			ip = addr[0]
			async with self.IPLock:
				self.foundIPs[ip] = shout.status.id
				self.lastSeen[ip] = datetime.now()
				self.messageQ.put_nowait( ('Ubidium', f"UbidiumWatcher: Found Ubidium Server on {ip}.") )
		
		self.messageQ.put_nowait( ('Ubidium', "UbidiumWatcher: Stopped listening to Ubidium devices.") )
		sock.close()

	# cleanupOldIPs removes IPs that have not been seen for a while
	async def cleanupOldIPs(self):
		async with self.IPLock:
			if self.foundIPs:
				now = datetime.now()
				to_remove = [ip for ip, last_seen in self.lastSeen.items() if now - last_seen > NOT_SEEN_THRESHOLD]
				for ip in to_remove:
					del self.foundIPs[ip]
					del self.lastSeen[ip]
				if not self.foundIPs:
					self.messageQ.put_nowait( ('Ubidium', "UbidiumWatcher: no Ubidium connections.") )
					self.messageQ.put_nowait( ('Ubidium', 'state', False) )
