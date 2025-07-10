import asyncio

import UbidiumClient

async def UbidiumServer( dataQ, messageQ, serverIP=None, ubidiumID=None ):
	if not UbidiumClient.terminateSig:
		await Shutdown()
	
	UbidiumClient.terminateSig = False
	asyncio.create_task( UbidiumClient.StartClient(dataQ, messageQ, serverIP, ubidiumID) )

async def Shutdown():
	UbidiumClient.terminateSig = True
	await asyncio.sleep( 0.5 )
