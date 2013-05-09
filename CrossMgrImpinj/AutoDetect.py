import socket
import Utils

def findImpinjHost( impinjPort ):
	''' Search ip addresses adjacent to the computer in an attempt to find the reader. '''
	ip = [int(i) for i in Utils.GetDefaultHost().split('.')]
	j = 0
	for i in xrange(14):
		j = -j if j > 0 else -j + 1
		
		ipTest = list( ip )
		ipTest[-1] += j
		if not (0 <= ipTest[-1] < 256):
			continue
			
		impinjHost = '.'.join( str(v) for v in ipTest )
		
		readerSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		readerSocket.settimeout( 0.5 )
		try:
			readerSocket.connect( (impinjHost, impinjPort) )
		except:
			continue
		
		try:
			response = UnpackMessageFromSocket( readerSocket )
		except:
			readerSocket.close()
			continue
			
		readerSocket.close()
		if response.success():
			return impinjHost
			
	return None

def AutoDetect( impinjPort ):
	return findImpinjHost( impinjPort ), Utils.GetDefaultHost()
		
if __name__ == '__main__':
	print AutoDetect(5084)