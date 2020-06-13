#!/usr/bin/env python
#------------------------------------------------------------------------------	
# JChipClient.py: JChip simulator program for testing JChip interface and CrossMgr.
#
# Copyright (C) Edward Sitarski, 2012.
import os
import time
import xlwt
import socket
import random
import operator
import datetime

#------------------------------------------------------------------------------	
# CrossMgr's port and socket.
DEFAULT_PORT = 53135
DEFAULT_HOST = '127.0.0.1'

#------------------------------------------------------------------------------	
# JChip delimiter (CR, **not** LF)
CR = '\r'

NumberOfStarters = 50

#------------------------------------------------------------------------------	
# Create some random rider numbers.
random.seed( 10101010 )
nums = [n for n in range(1,799+1)]
random.shuffle( nums )
nums = nums[:NumberOfStarters]

#------------------------------------------------------------------------------	
# Create a JChip-style hex tag for each number.
tag = {n: '41AA%03X' % n for n in nums }
tag[random.choice(list(tag.keys()))] = 'E2001018860B01290700D0D8'
tag[random.choice(list(tag.keys()))] = 'E2001018860B01530700D138'
tag[random.choice(list(tag.keys()))] = 'E2001018860B01370700D0F8'
tag[random.choice(list(tag.keys()))] = '1'
tag[random.choice(list(tag.keys()))] = '2'

#------------------------------------------------------------------------
def getRandomData( starters ):
	firstNames = '''
1. Noah
2. Liam
3. Jacob
4. Mason
5. William
6. Ethan
7. Michael
8. Alexander
9. Jayden
10. Daniel
11. Elijah
12. Aiden
13. James
14. Benjamin
15. Matthew
16. Jackson
17. Logan
18. David
19. Anthony
20. Joseph
21. Joshua
22. Andrew
23. Lucas
24. Gabriel
25. Samuel
26. Christopher
27. John
28. Dylan
29. Isaac
30. Ryan
31. Nathan
32. Carter
33. Caleb
34. Luke
35. Christian
36. Hunter
37. Henry
38. Owen
39. Landon
40. Jack
41. Wyatt
42. Jonathan
43. Eli
44. Isaiah
45. Sebastian
46. Jaxon
47. Julian
48. Brayden
49. Gavin
50. Levi
51. Aaron
52. Oliver
53. Jordan
54. Nicholas
55. Evan
56. Connor
57. Charles
58. Jeremiah
59. Cameron
60. Adrian
61. Thomas
62. Robert
63. Tyler
64. Colton
65. Austin
66. Jace
67. Angel
68. Dominic
69. Josiah
70. Brandon
71. Ayden
72. Kevin
73. Zachary
74. Parker
75. Blake
76. Jose
77. Chase
78. Grayson
79. Jason
80. Ian
81. Bentley
82. Adam
83. Xavier
84. Cooper
85. Justin
86. Nolan
87. Hudson
88. Easton
89. Jase
90. Carson
91. Nathaniel
92. Jaxson
93. Kayden
94. Brody
95. Lincoln
96. Luis
97. Tristan
98. Damian
99. Camden
100. Juan
'''

	lastNames = '''
1. Smith  
2. Johnson  
3. Williams  
4. Jones  
5. Brown  
6. Davis  
7. Miller  
8. Wilson  
9. Moore  
10. Taylor  
11. Anderson  
12. Thomas  
13. Jackson  
14. White  
15. Harris  
16. Martin  
17. Thompson  
18. Garcia  
19. Martinez  
20. Robinson  
21. Clark  
22. Rodriguez  
23. Lewis  
24. Lee  
25. Walker  
26. Hall  
27. Allen  
28. Young  
29. Hernandez  
30. King  
31. Wright  
32. Lopez  
33. Hill  
34. Scott  
35. Green  
36. Adams  
37. Baker  
38. Gonzalez  
39. Nelson  
40. Carter  
41. Mitchell  
42. Perez  
43. Roberts  
44. Turner  
45. Phillips  
46. Campbell  
47. Parker  
48. Evans  
49. Edwards  
50. Collins  
51. Stewart  
52. Sanchez  
53. Morris  
54. Rogers  
55. Reed  
56. Cook  
57. Morgan  
58. Bell  
59. Murphy  
60. Bailey  
61. Rivera  
62. Cooper  
63. Richardson  
64. Cox  
65. Howard  
66. Ward  
67. Torres  
68. Peterson  
69. Gray  
70. Ramirez  
71. James  
72. Watson  
73. Brooks  
74. Kelly  
75. Sanders  
76. Price  
77. Bennett  
78. Wood  
79. Barnes  
80. Ross  
81. Henderson  
82. Coleman  
83. Jenkins  
84. Perry  
85. Powell  
86. Long  
87. Patterson  
88. Hughes  
89. Flores  
90. Washington  
91. Butler  
92. Simmons  
93. Foster  
94. Gonzales  
95. Bryant   
96. Alexander  
97. Russell  
98. Griffin   
99. Diaz  
'''

	teams = '''
The Cyclomaniacs
Pesky Peddlers
Geared Up
Spoke & Mirrors
The Handlebar Army
Wheels of Steel
The Chaingang
Saddled & Addled
The Cyclepaths
Tour de Farce
Old Cranks
Magically Bikelicious
Look Ma No Hands!
Pedal Pushers
Kicking Asphault
Velociposse
Road Rascals
Spin Doctors
'''

	firstNames = [line.split('.')[1].strip() for line in firstNames.split('\n') if line.strip()]
	lastNames = [line.split('.')[1].strip() for line in lastNames.split('\n') if line.strip()]
	teams = [line.strip() for line in teams.split('\n') if line.strip()]
	bibs = [n for n in range(1,1+starters)]
	
	random.shuffle( firstNames )
	random.shuffle( lastNames )
	random.shuffle( teams )
	
	for i in range(starters):
		yield bibs[i], firstNames[i%len(firstNames)], lastNames[i%len(lastNames)], teams[i%len(teams)]
		
#------------------------------------------------------------------------------	
# Write out as a .xls file with the number tag data.
#
wb = xlwt.Workbook()
ws = wb.add_sheet( "JChipTest" )
for col, label in enumerate('Bib#,LastName,FirstName,Team,Tag,StartTime'.split(',')):
	ws.write( 0, col, label )
rdata = [d for d in getRandomData(len(tag))]
rowCur = 1
for r, (n, t) in enumerate(tag.items()):
	if t in ('1', '2'):
		continue
	
	bib, firstName, lastName, Team = rdata[r]
	for c, v in enumerate([n, lastName, firstName, Team, t, 5*rowCur/(24.0*60.0*60.0)]):
		ws.write( rowCur, c, v )
	rowCur += 1
wb.save('JChipTest.xls')
wb = None
print( 'Created JChipTest.xls.' )

#------------------------------------------------------------------------------	
# Also write out as a .csv file.
#
with open('JChipTest.csv', 'w') as f:
	f.write( 'Bib#,Tag,dummy3,dummy4,dummy5\n' )
	for n in nums:
		f.write( '{},{}\n'.format(n, tag[n]) )

sendDate = True

#------------------------------------------------------------------------------	
# Function to format number, lap and time in JChip format
# Z413A35 10:11:16.4433 10  10000      C7
count = 0
def formatMessage( n, lap, t ):
	global count
	message = "DJ%s %s 10  %05X      C7%s%s" % (
				tag[n],								# Tag code
				t.strftime('%H:%M:%S.%f'),			# hh:mm:ss.ff
				count,								# Data index number in hex.
				' date={}'.format( t.strftime('%Y%m%d') ) if sendDate else '',
				CR
			)
	count += 1
	return message

#------------------------------------------------------------------------------	
# Generate some random lap times.
random.seed()
numLapTimes = []
mean = 60.0							# Average lap time.
varFactor = 9.0 * 4.0
var = mean / varFactor				# Variance between riders.
lapMax = 61
for n in nums:
	lapTime = random.normalvariate( mean, mean/(varFactor * 4.0) )
	for lap in range(0, lapMax+1):
		numLapTimes.append( (n, lap, lapTime*lap) )
numLapTimes.sort( key = operator.itemgetter(1, 2) )	# Sort by lap, then race time.

def getCmd( sock ):
	received = ''
	while received[-1:] != CR:
		try:
			received += sock.recv(4096).decode()	# doing a decode() here only works if there are no multi-byte utf characters (which is true for JChip protocol).
		except socket.timeout:
			return received, True
	return received[:-1], False

#------------------------------------------------------------------------------	
# Connect to the CrossMgr server.
dBaseStart = None
iMessage = 1
while 1:
	print( 'Attempting to connect to CrossMgr server...' )
	sock = None		# Voodoo socket reset.
	while 1:
		try:
			#------------------------------------------------------------------------------	
			# Create a socket (SOCK_STREAM means a TCP socket)
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((DEFAULT_HOST, DEFAULT_PORT))
			break
		except Exception as e:
			print( 'Connection failed.  Waiting 5 seconds... ({})'.format(e) )
			sock = None
			time.sleep( 5 )

	# Set the timeout with CrossMgr to 2 seconds.  If CrossMgr fails to respond within this time, re-establish the connection.
	sock.settimeout( 2.0 )
			
	#------------------------------------------------------------------------------	
	print( 'Connection succeeded!' )
	name = '{}-{}'.format(socket.gethostname(), os.getpid())
	print( 'Sending name...', name )
	message = "N0000{}{}".format(name, CR)
	sock.send( message.encode() )

	#------------------------------------------------------------------------------	
	print( 'Waiting for get time command...' )
	received, timedOut = getCmd( sock )
	if timedOut:
		print( 'Timed out [1]' )
		continue
	
	print('Received cmd: "{}" from CrossMgr'.format(received) )
	if not received.startswith('GT'):
		print( 'Unknown cmd [1]' )
		continue

	#------------------------------------------------------------------------------
	dBase = datetime.datetime.now()
	dBase -= datetime.timedelta( seconds = 13*60+13.13 )	# Send the wrong time for testing purposes.
	if not dBaseStart:
		dBaseStart = dBase	# Record the first sent time to keep it as a basis for all transmitted times.

	#------------------------------------------------------------------------------	
	print( 'Send gettime data...' )
	# format is GT0HHMMSShh<CR> where hh is 100's of a second.  The '0' (zero) after GT is the number of days running and is ignored by CrossMgr.
	message = 'GT0{:02d}{:02d}{:02d}{:02d}{}{}'.format(
		dBase.hour, dBase.minute, dBase.second, int((dBase.microsecond / 1000000.0) * 100.0),
		' date={}'.format( dBase.strftime('%Y%m%d') ) if sendDate else '',
		CR)
	print( message[:-1] )
	sock.send( message.encode() )

	#------------------------------------------------------------------------------	
	print( 'Waiting for send command from CrossMgr...' )
	received, timedOut = getCmd( sock )
	if timedOut:
		print( 'Timed out [2]' )
		continue
	print('Received cmd: "{}" from CrossMgr'.format(received) )
	if not received.startswith('S'):
		print( 'Unknown cmd [2]' )
		continue

	#------------------------------------------------------------------------------	
	print( 'Sending data...' )

	while iMessage < len(numLapTimes):
		n, lap, t = numLapTimes[iMessage]
		dt = t - numLapTimes[iMessage-1][2]
		
		time.sleep( dt )
		
		# Send offsets relative to the transmit start time.
		message = formatMessage( n, lap, dBaseStart + datetime.timedelta(seconds = t - 0.5) )
		if iMessage & 15 == 0:
			print( 'sending: {}: {}\n'.format(iMessage, message[:-1]) )
		try:
			sock.send( message.encode() )
			iMessage += 1
		except:
			print( 'Disconnected.  Attempting to reconnect...' )
			break
		
	if iMessage >= len(numLapTimes):
		message = '<<<GarbageTerminateMessage>>>' + CR
		sock.send( message.encode() )
		break
		
