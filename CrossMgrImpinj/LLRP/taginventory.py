import random

'''
	Simulate inventory mode in a chip reader.
	Use fibonacci numbers as the tag group.
'''

MaxTagsInGroup = 50			# Number of tags in the group.
MaxSimultaneousTagReads = 5	# Max number of tags that can be differentiated in one read.

#----------------------------------------------------------------------------------------------

def fib(n):
	''' Generate N fibonacci numbers. '''
	a, b = 0, 1
	for c in xrange(n):
		yield a
		a, b = b, a + b

def toBin( bits, i ):
	''' Format an integer's bits in binary format. '''
	return ''.join( '1' if i & (1<<c) else '0' for c in xrange(bits-1, -1, -1) )

#----------------------------------------------------------------------------------------------

#tagGroup = [f for f in fib(MaxTagsInGroup+2)][2:]		# Initialize the simulated group of tags.
tagGroup = [random.randint(1,999999) for r in xrange(MaxTagsInGroup)]		# Initialize the simulated group of tags.

callCount = 0	# Function count.
def readTagsMatchinglowBits( bitCount, lowBits ):
	''' Return tags whose last bitCount bits equal lowBits. '''
	''' This is a capability of the Gen2 chips. '''
	global callCount
	callCount += 1
	print '%3d: lowBits: %10s' % (callCount, toBin(bitCount, lowBits))
	mask = (1<<bitCount) - 1
	readTags = [tag for tag in tagGroup if tag & mask == lowBits]	# Find tags that match the given lowBits
	success = (len(readTags) <= MaxSimultaneousTagReads)
	print 'read Success (%d tags)' % len(readTags) if success else 'Too many simultaneous tags (%d).' % len(readTags)
	return success, readTags

tagsRead = []
def findTags( bitCount = 0, lowBits = 0 ):
	success, tags = readTagsMatchinglowBits( bitCount, lowBits )
	if success:
		tagsRead.extend( tags )
	else:
		# We got a tag collision.  Add another bit to differentiate the tags and get a smaller number.
		findTags( bitCount+1, lowBits )						# Add a zero bit.
		findTags( bitCount+1, (1<<bitCount) | lowBits )		# Add a one bit.
		
def findAllTags():
	global callCount, tagsRead
	callCount = 0
	tagsRead = []
	findTags()
	return tagsRead
	
if __name__ == '__main__':
	print sorted(findAllTags())
