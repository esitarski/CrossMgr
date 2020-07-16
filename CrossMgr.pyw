#!/usr/bin/env python

#---------------------------------------------------------------------------------------------------------------------------
# This software is protected under the provisions of the Berne Convention for the Protection of Literary and Artistic Works.
#---------------------------------------------------------------------------------------------------------------------------

try:
	import MainWin
except ImportError:
	from CrossMgr import MainWin
	
if __name__ == '__main__':
	MainWin.MainLoop()

#from multiprocessing import freeze_support
#
#if __name__ == '__main__':
#	freeze_support()			# Required so that multiprocessing works with py2exe.
#	MainWin.MainLoop()
#
