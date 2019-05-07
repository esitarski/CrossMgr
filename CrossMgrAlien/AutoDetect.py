import re
import six
import socket
import subprocess

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

cmdStr = '''
alien							# default username
password						# default password

get ReaderName					# Use this to check if the login succeeded.
Quit
'''

# Transform the cmd string into an array of Alien reader commands (strip out comments and blank lines).
initCmds = [f.split('#')[0].strip() for f in cmdStr.split('\n') if f and not f.startswith('#')]
initCmds = [c for c in initCmds if c]	# Remove empty commands.
del cmdStr

DefaultAlienCmdPort = 23

CmdPrefix = chr(1)			# Causes Alien reader to suppress prompt on response.
CmdDelim = '\n'				# Delimiter of Alien commands (sent to reader).
ReaderDelim = '\0'			# Delimiter of Alien reader responses (received from reader).

def getResponse( conn ):
	# Read delimited data from the reader
	response = ''
	while not response.endswith( ReaderDelim ):
		more = conn.recv( 4096 )
		if not more:
			break
		response += more
	return response

def findAlienHost( alienPort = DefaultAlienCmdPort ):
	''' Search ip addresses adjacent to the computer in an attempt to find the reader. '''
	success = False
	ip = [int(i) for i in GetDefaultHost().split('.')]
	j = 0
	for i in six.moves.range(14):
		j = -j if j > 0 else -j + 1
		
		ipTest = list( ip )
		ipTest[-1] += j
		if not (0 <= ipTest[-1] < 256):
			continue
			
		alienHost = u'.'.join( u'{}'.format(v) for v in ipTest )
		
		cmdSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		cmdSocket.settimeout( 0.5 )
		try:
			cmdSocket.connect( (alienHost, alienPort) )
		except:
			continue
		
		for i, cmd in enumerate(initCmds):
			try:
				cmdSocket.sendall( u'{}{}{}'.format('' if i < 2 else CmdPrefix, cmd, CmdDelim).encode() )
			except:
				continue
			try:
				response = getResponse( cmdSocket )
			except:
				continue
			
			# Check if we could successfully get the ReaderName from the #2 command.  If so, the login was successful.
			# If the login fails, the reader just returns nothing.
			if i == 2:
				if response.lower().startswith('ReaderName'.lower()):
					success = True
			
		try:
			cmdSocket.close()
		except:
			pass
			
		if success:
			return alienHost
			
	return None

def AutoDetect( alienPort = DefaultAlienCmdPort ):
	return findAlienHost( alienPort ), GetDefaultHost()
		
if __name__ == '__main__':
	print ( AutoDetect(5084) )
