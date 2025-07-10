""""
File:		   Ubidium Server-Client Data Stream
Date:		   09.08.2023

Description:	Contains class and methods for Ubidium Client.
				UbidiumClient class contains methods for setting channel parameter and printing
				status and passing data.

"""

import os
import datetime
import asyncio
import grpc
from google.protobuf import duration_pb2 as _duration_pb2
import datetime

from UbidiumSDK.ubidium import service_pb2_grpc, service_command_pb2, service_status_pb2, service_passing_pb2
from UbidiumSDK.Certificates import Certificates

HOME_DIR = os.path.expanduser("~")

global_watcher = None
global_client = None

class UbidiumClient:

	def __init__(self, dataQ, messageQ):
		self.dataQ = dataQ
		self.messageQ = messageQ
		self.terminateSig = False
		self.channel = None
		self.UbidiumStub = None
		self.StatusStream = None
		self.PassingStream = None
		self.passing_correction = datetime.timedelta( seconds=0 )	# Correction between Ubidium's clock and our local clock.
		self.deviceID = ""
		self.address = ""
		
		self.tStart = datetime.datetime.now()
		self.logQ = asyncio.Queue()
		asyncio.create_task( self.handleLogFile() )

	async def handleLogFile( self ):
		dataDir = os.path.join( HOME_DIR, 'UbidiumData' )
		if not os.path.isdir( dataDir ):
			os.makedirs( dataDir )

		while not self.terminateSig:
			try:
				msg = await self.logQ.get()
			except asyncio.QueueShutDown:
				return
			
			self.fname = os.path.join( dataDir, self.tStart.strftime(f'Ubidium-{self.deviceID}-%Y-%m-%d-%H-%M-%S.txt') )
			if not os.path.exists( self.fname ):
				with open(self.fname, 'w', encoding='utf-8') as f:
					f.write( 'Tag,Discover Time\n' )
				
			with open(self.fname, 'a', encoding='utf-8') as f:
				while not self.terminateSig:
					if msg[0] == 'shutdown':
						self.logQ.task_done()
						break
					
					f.write( msg[1] if msg[1].endswith('\n') else msg[1] + '\n' )
					self.logQ.task_done()
					
					if self.logQ.empty():
						break
					try:
						msg = await self.logQ.get()
					except asyncio.QueueShutDown:
						return			

	# SetChannelSettings reads SSL certificate and sets credentials for secure channel to Ubidium Server
	def SetChannelSettings(self):
		self.cert_bytes = Certificates['cacert.pem']

		try:
			self.creds = grpc.ssl_channel_credentials(self.cert_bytes)
		except Exception as err:
			messageQ( ('Ubidium', f"Client: Could not create channel credentials. Error: {err}") )

	def CreateSecureChannel(self, ServerIP, UbidiumID):
		self.channel = grpc.aio.secure_channel(ServerIP, self.creds,
											   options=[
													('grpc.ssl_target_name_override', UbidiumID),
													('grpc.keepalive_time_ms', 20000),
													('grpc.keepalive_timeout_ms', 2000),
													('grpc.keepalive_permit_without_calls', True),
											   ])
		self.UbidiumStub = service_pb2_grpc.TimingSystemStub(self.channel)
		self.address = ServerIP

	def StartTasks(self):
		self.StatusStreamTask = asyncio.create_task(self.GetUbidiumStatus())
		self.PassingStreamTask = asyncio.create_task(self.GetUbidiumPassing())

	async def StopTasks(self):
		self.terminateSig = True
		await self.logQ.put( ('shutdown',) )

		if self.StatusStreamTask:
			await self.StatusStreamTask
		if self.PassingStreamTask:
			await self.PassingStreamTask

	def OpenStatusStream(self):
		self.StatusStream = self.UbidiumStub.OpenStatusStream()
	
	def OpenPassingStream(self):
		self.PassingStream = self.UbidiumStub.OpenPassingStream()

	async def CloseStatusStream(self):
		if self.StatusStream is None:
			messageQ.put_nowait( ('Ubidium', "UbidiumClient: Status stream not initialized") )
			return

		await self.StatusStream.done_writing()
		messageQ.put_nowait( ('Ubidium', f"UbidiumClient: Status stream closed for: {self.address}") )

	async def ClosePassingStream(self):
		if self.PassingStream is None:
			messageQ.put_nowait( ('Ubidium', "UbidiumClient: Passing stream not initialized") )
			return

		await self.PassingStream.done_writing()
		messageQ.put_nowait( ('Ubidium', f"UbidiumClient: Passing stream closed for: {self.address}") )

	# RequestStatus requests status updates from Ubidium and sets time interval for automated updates
	async def RequestStatus(self):
		pushTime = _duration_pb2.Duration(seconds=10, nanos=0)
		CmdGetStatus = service_status_pb2.CmdGetStatus(continues=True, push_time=pushTime)
		StatReq = service_status_pb2.StatusRequest(get=CmdGetStatus)

		await self.StatusStream.write(StatReq)

	# RequestPassings request passings from Ubidium and sets start and beginning of transmission
	async def RequestPassings(self):
		startRef = service_passing_pb2.CmdGetPassings.StartReference.START_REFERENCE_NOW
		endRef = service_passing_pb2.CmdGetPassings.EndReference.END_REFERENCE_UNTIL_STOPPED
		CmdGetPass = service_passing_pb2.CmdGetPassings(start_ref=startRef, end_ref=endRef)
		PassReq = service_passing_pb2.PassingRequest(get=CmdGetPass)

		await self.PassingStream.write(PassReq)

	# GetUbidiumStatus opens Status stream, awaits response from Server and prints received status data
	async def GetUbidiumStatus(self):
		messageQ.put_nowait( ('Ubidium', f"Client: Started to read status for: {self.address}") )

		while not self.terminateSig:
			try:
				response = await self.StatusStream.read()
				if response == grpc.aio.EOF:
					break
				await self.HandleStatus(response)
			except Exception as err:
				messageQ.put_nowait( ('Ubidium', f"Client: Error GetUbidiumStatus for {self.deviceID}: {err.details()}") )
				break

		messageQ.put_nowait( ('Ubidium', f"Client: Reading status is stopped for: {self.address}") )

		
	# GetUbidiumPassing opens Passing stream, awaits response from Server and prints received passing data
	async def GetUbidiumPassing(self):
		messageQ.put_nowait( ('Ubidium', f"Client: Started to read passings for: {self.address}") )

		while not self.terminateSig:
			try:
				response = await self.PassingStream.read()
				if response == grpc.aio.EOF:
					break
				await self.HandlePassing(response)
			except Exception as err:
				messageQ.put_nowait( ('Ubidium', f"Client: Error inside GetUbidiumPassing for {self.deviceID}: {err.details()}") )
				break

		messageQ.put_nowait( ('Ubidium', f"Client: Reading passings is stopped for: {self.address}") )

	# TransmitKey takes key parameter and transmits to Ubidium
	async def TransmitKey(self, Key: service_command_pb2.Key):
		await self.UbidiumStub.PressKey(service_command_pb2.CmdPressKey(key=Key))


	# HandleStatus displays received ubidium status via serial console
	async def HandleStatus(self, response):
		try:
			if response.WhichOneof("response") == "error":
				messageQ.put_nowait( ('Ubidium', f"Client: Error: {response.error}\n") )

			elif response.WhichOneof("response") == "status":
				if self.deviceID == "":
					self.deviceID = response.status.id
				# Compute a time correction between the Ubidium device and this computer.
				t_reader = response.status.time
				self.passing_correction = datetime.now() - t_reader
				messageQ.put_nowait( ('Ubidium', f"Client: Status (update) from: {self.deviceID} {response.status}") )
				messageQ.put_nowait( ('Ubidium', f"Client: Ubidium-Computer time correction: {self.passing_correction}") )

		except Exception as err:
			messageQ.put_nowait( ('Ubidium', f"Client: Error occurred on reading status stream. Error: {err}") )

	# HandlePassing displays received passing via serial console
	async def HandlePassing(self, response):
		try:
			if response.WhichOneof("response") == "passing":
				deviceID = response.passing.src.device_id

				if response.passing.WhichOneof("data") == "active":
					t = response.passing.time + self.passing_correction
					tag = response.passing.transponder.id
					self.dataQ.put_nowait( (tag, t) )
					self.logQ.put_nowait( ('msg', f'{tag}, {t}') )
				elif response.passing.WhichOneof("data") == "marker":
					messageQ.put_nowait( ('Ubidium', f"Client: Got marker from {deviceID}") )

			elif response.WhichOneof("response") == "welcome":
				messageQ.put_nowait( ('Ubidium', f"Client: Welcome: {response.welcome}") )

			elif response.WhichOneof("response") == "error":
				messageQ.put_nowait( ('Ubidium', f"Client: Error: {response.error}") )

		except Exception as err:
			messageQ.put_nowait( ('Ubidium', f"Client: Error occurred on reading passing stream. Error: {err}") )

#-----------------------------------------------------------------------

""""
File:		   Ubidium Server-Client Data Stream
Date:		   07.08.2023

Description:	This script shows an example how to connect a user (client) to Ubidium (Server).
				A Status and Passing Stream between client and server is showcased.

				The client can connect to Ubidium via a fix IP or listen to Ubidium broadcast.
				1) Connect with a fix IP
					> pass a fix IP, port 443 and Ubidium ID when executing client example (e.g. python3 main.py 192.168.1.112:443 U-40153)
					> In addition "Press Key" transmission to server is implemented.

				2) Listen to Ubidium broadcast
					> run with: python3 main.py
					> Ubidium will listen to Ubidiums broadcast in the background and will connect automatically to all Ubidiums which are found.

				Program can be terminated via "Strg+C".

				How to translate *.proto to *_pb2.py, *_pb2_grpc.py and *_pb2_pyi files
				> Terminal translate comands:
				python3 -m grpc_tools.protoc -I<PATH_TO_PROTOS> --python_out=<OUTPUT_DIR> --pyi_out=<OUTPUT_DIR> --grpc_python_out=<OUTPUT_DIR> <PATH_TO_PROTOS>*.proto

				Info: .proto files for usage with python are stored in the folder "proto" which is a subfolder of the "python" folder.
				Do not use the parent folder "proto" for transalation to .py/.pyi files. 
				The file "service_status.proto" differs from the original in variable names for avoiding collition with python syntax.
"""

# Imports from python
import asyncio
import sys
import time
import os
import grpc
import logging
import signal

# Imports from own project
from UbidiumWatcher import UbidiumWatcher
from UbidiumSDK.ubidium import service_command_pb2

# Global Variables
terminateSig = False

# SignalHandler sets termination flag which is checked inside tasks
def signalHandler(signum, frame):
	print("Inside Signal handler \n")
	global terminateSig
	terminateSig = True

global_watcher = None
global_client = None
async def StartClient( dataQ, messageQ, serverIP=None, ubidiumID=None ):
	global global_watcher
	global global_client

	await messageQ.put( ('Ubidium', 'state', False) )

	if not (serverIP or ubidiumID):
		messageQ.put_nowait( ('Ubidium', "Listening for Ubidium devices...") )

		watcher = global_watcher = UbidiumWatcher( messageQ )
		watcher.startMonitorBC()

		while not terminateSig:
			# Update which IPs are currently seen.
			await watcher.cleanupOldIPs()

			# Check if an IP is not found anymore and close the connection
			async with watcher.IPLock:
				for ip in list(watcher.activeCons.keys()):
					if ip not in watcher.foundIPs:
						client = watcher.activeCons[ip]

						messageQ.put_nowait( ('Ubidium', f"Closing Secure Channel ip={ip} device={client.deviceID}") )
						
						await client.CloseStatusStream()
						await client.ClosePassingStream()
						await client.StopTasks()

						# Close channel
						try:
							await asyncio.wait_for(client.channel.close(), timeout=1.0)
							messageQ.put_nowait( ('Ubidium', f"Secure Channel closed for: {client.deviceID}") )
						except asyncio.TimeoutError:
							messageQ.put_nowait( ('Ubidium', f"Timeout on closing channel for: {client.deviceID}") )
						except grpc.RpcError as err:
							messageQ.put_nowait( ('Ubidium', f"Could not close Secure Channel. Error: {err}") )

						del watcher.activeCons[ip]

			# Check new IPs and establish a connection
			async with watcher.IPLock:
				for ip, devID in watcher.foundIPs.items():
					# print(f"Found IP {ip} with ID {devID}")
					if ip not in watcher.activeCons:
						client = ubidiumclient.UbidiumClient( messageQ )

						client.SetChannelSettings()
						client.CreateSecureChannel( f"{ip}:443", devID )

						# Open streams
						client.OpenStatusStream()
						client.OpenPassingStream()

						# Request and read status and passings
						await client.RequestStatus()
						await client.RequestPassings()

						client.StartTasks()
						watcher.activeCons[ip] = client
						messageQ.put_nowait( ('Ubidium', f"Created client connection for {ip}:443, {devID}") )
						messageQ.put_nowait( ('Ubidium', 'state', True) )

			await asyncio.sleep(3)

		# Close all connections and stop listening to Ubidium broadcast
		await watcher.stopMonitorBC()

		async with watcher.IPLock:
			for ip in list(watcher.activeCons.keys()):
				client = watcher.activeCons[ip]
					
				await client.CloseStatusStream()
				await client.ClosePassingStream()
				await client.StopTasks()

				# Close channel
				try:
					await asyncio.wait_for(client.channel.close(), timeout=1.0)
					messageQ.put_nowait( ('Ubidium', f"Secure Channel closed for: {client.deviceID}") )
				except asyncio.TimeoutError:
					messageQ.put_nowait( ('Ubidium', f"Timeout on closing channel for: {client.deviceID}") )
				except grpc.RpcError as err:
					messageQ.put_nowait( ('Ubidium', f"Could not close Secure Channel. Error: {err}") )

				del watcher.activeCons[ip]
	else:
		messageQ.put_nowait( ('Ubidium', f"Attempting to create Ubidium device connecton: {serverIP}, {ubidiumID}") )

		# Set up client
		client = global_client = UbidiumClient(dataQ, messageQ)

		client.SetChannelSettings()
		client.CreateSecureChannel(serverIP, ubidiumID)

		# Open streams
		client.OpenStatusStream()
		client.OpenPassingStream()

		# Request and read status and passings
		await client.RequestStatus()
		await client.RequestPassings()

		client.StartTasks()

		while not terminateSig:
			await asyncio.sleep(0.5)

		await client.CloseStatusStream()
		await client.ClosePassingStream()
		await client.StopTasks()

		# Close channel
		try:
			await asyncio.wait_for(client.channel.close(), timeout=1.0)
			messageQ.put_nowait( ('Ubidium', f"Secure Channel closed for: {client.deviceID}") )
		except asyncio.TimeoutError:
			messageQ.put_nowait( ('Ubidium', f"Timeout on closing channel for: {client.deviceID}") )
		except grpc.RpcError as err:
			messageQ.put_nowait( ('Ubidium', f"Could not close Secure Channel. Error: {err}") )

	messageQ.put_nowait( ('Ubidium', "StartClient: exiting.") )
	dataQ.put_nowait( 'shutdown' )

async def StopClient():
	global global_watcher
	global global_client
	global terminateSig

	terminateSig = True

	if global_watcher:
		await global_watcher.stopTasks()
	elif global_client:
		await global_client.StopTasks()
	global_watcher = None
	global_client = None
	terminateSig = False

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	signal.signal(signal.SIGINT, signalHandler)
	try:
		serverIP, ubidiumID = sys.argv[1], sys.argv[2]
	except IndexError:
		serverIP, ubidiumID = None, None
	dataQ = asyncio.Queue()
	messageQ = asyncio.Queue()
	
	async def handleDataQ():
		while not terminateSig:
			try:
				print( await dataQ.get(), flush=True )
			except Exception as e:
				print( 'DataQ', e )
			dataQ.task_done()
	
	async def handleMessageQ():
		while not terminateSig:
			try:
				print( await messageQ.get(), flush=True )
			except Exception as e:
				print( 'MessageQ', e )
			messageQ.task_done()

	async def Launch():
		async with asyncio.TaskGroup() as tg:
			t1 = tg.create_task( handleDataQ() )
			t2 = tg.create_task( handleMessageQ() )
			t3 = tg.create_task( StartClient(dataQ, messageQ, serverIP, ubidiumID) )
			#asyncio.run(StartClient(dataQ, messageQ, serverIP, ubidiumID))

	asyncio.run(Launch())
