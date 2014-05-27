import re
import socket
import subprocess
from pyllrp.pyllrp import *

def GetDefaultHost():
	DEFAULT_HOST = socket.gethostbyname(socket.gethostname())
	if DEFAULT_HOST == '127.0.0.1':
		reSplit = re.compile('[: \t]+')
		try:
			co = subprocess.Popen(['ifconfig'], stdout = subprocess.PIPE)
			ifconfig = co.stdout.read()
			for line in ifconfig.split('\n'):
				line = line.strip()
				try:
					if line.startswith('inet addr:'):
						fields = reSplit.split( line )
						addr = fields[2]
						if addr != '127.0.0.1':
							DEFAULT_HOST = addr
							break
				except:
					pass
		except:
			pass
	return DEFAULT_HOST
	
def findImpinjHost( impinjPort ):
	''' Search ip addresses adjacent to the computer in an attempt to find the reader. '''
	ip = [int(i) for i in GetDefaultHost().split('.')]
	j = 0
	for i in xrange(14):
		j = -j if j > 0 else -j + 1
		
		ipTest = list( ip )
		ipTest[-1] += j
		if not (0 <= ipTest[-1] < 256):
			continue
			
		impinjHost = '.'.join( '{}'.format(v) for v in ipTest )
		
		readerSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		readerSocket.settimeout( 3.0 )
		try:
			readerSocket.connect( (impinjHost, impinjPort) )
		except Exception as e:
			continue
		
		try:
			response = UnpackMessageFromSocket( readerSocket )
		except Exception as e:
			readerSocket.close()
			continue
			
		readerSocket.close()
		
		# Check that the return from the reader is valid.
		try:
			readerTime = response.getFirstParameterByClass(UTCTimestamp_Parameter).Microseconds
		except Exception as e:
			continue
		else:
			return impinjHost
			
	return None

def AutoDetect( impinjPort ):
	return findImpinjHost( impinjPort ), GetDefaultHost()
		
if __name__ == '__main__':
	print AutoDetect(5084)