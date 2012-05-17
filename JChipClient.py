import socket
import sys
import random
import time
import datetime
import JChip

CR = chr( 0x0d )	# JChip delimiter

random.seed( 10101010 )
nums = [random.randint(1,100) for x in xrange(25)]
tag = {}
for n in nums:
	tag[n] = 'J%06X' % n
	
count = 0

with open('JChipTest.csv', 'w') as f:
	f.write( 'Bib#,Tag,h3,h4,h5\n' )
	for n in nums:
		f.write( '%d,%s\n' % (n, tag[n]) )

# Z413A35 10:11:16.4433 10  10000      C7
def formatMessage( n, lap, t ):
	global count
	message = "D%s %s 10  %05X      C7%s" % (
				tag[n],								# Tag code
				t.strftime('%H:%M:%S.%f'),			# hh:mm:ss.mm
				count,								# Data index number in hex.
				CR
			)
	count += 1
	return message

random.seed()
numLapTimes = []
mean = 60.0					# Average lap time.
varFactor = 9.0
var = mean/varFactor		# Variance between riders.
lapMax = 6
for n in nums:
	lapTime = random.normalvariate( mean, mean/(varFactor * 4.0) )
	for lap in xrange(1, lapMax+1):
		numLapTimes.append( (n, lap, lapTime*lap) )
numLapTimes.sort( key = lambda x: (x[1], x[2]) )
numLapTimes = [(0,0,0)] + numLapTimes

#------------------------------------------------------------------------------	
PORT, HOST = JChip.DEFAULT_PORT, JChip.DEFAULT_HOST

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server.
print 'Connecting to server...'
while 1:
	try:
		sock.connect((HOST, PORT))
		break
	except:
		print 'Connection failed.  Waiting 5 seconds...'
		time.sleep( 5 )

print 'Sending indentifier...'
sock.send("N0000JCHIP-READER%s" % CR)

print 'Waiting for send command...'
while 1:
	received = sock.recv(1)
	if received == 'S':
		while received != CR:
			received = sock.recv(1)
		break

print 'Start sending data...'

dBase = datetime.datetime.now()
for i in xrange(1, len(numLapTimes)):
	n, lap, t = numLapTimes[i]
	dt = t - numLapTimes[i-1][2]
	message = formatMessage( n, lap, dBase + datetime.timedelta( seconds = t ) )
	sys.stdout.write( 'sending: %s\n' % message[:-1] )
	sock.send( message )
	time.sleep( dt )
	
sock.send( '<<<terminate>>>%s' % CR )
	
