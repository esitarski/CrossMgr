#!/usr/bin/env python

import os
try:
	r = os.urandom( 16 )
except:
	try:
		_urandomfd = open("/dev/urandom", O_RDONLY)
		close( _urandomfd )
		def urandom(n):
			"""urandom(n) -> str

			Return a string of n random bytes suitable for cryptographic use.

			"""
			try:
				_urandomfd = open("/dev/urandom", O_RDONLY)
			except:
				raise NotImplementedError("/dev/urandom (or equivalent) not found")
			bytes = ""
			while len(bytes) < n:
				bytes += read(_urandomfd, n - len(bytes))
			close(_urandomfd)
			return bytes
	except:
		# First override os.urandom so we can import random.
		os.urandom = lambda n: ''.join( chr((i*239)%255) for i in xrange(n) )
		# Now, get randint from random.
		from random import randint
		# Define our own random - not as good as /dev/urandom, but good enough (maybe).
		def urandom(n):
			return ''.join(chr(randint(0,255)) for i in xrange(n))

	# Define the missing urandom.
	os.urandom = urandom

import MainWin
from multiprocessing import freeze_support

if __name__ == '__main__':
	freeze_support()			# Required so that multiprocessing works with py2exe.
	MainWin.MainLoop()
