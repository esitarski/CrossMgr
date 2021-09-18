import socket

def GetMyIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		# doesn't have to be reachable
		s.connect(('10.255.255.255', 1))
		IP = s.getsockname()[0]
	except Exception as e:
		print( e )
		IP = '127.0.0.1'
	finally:
		s.close()
	return IP
	
if __name__ == '__main__':
	print( GetMyIP() )
