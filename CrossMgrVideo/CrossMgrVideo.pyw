#---------------------------------------------------------------------------------------------------------------------------
# This software is protected under the provisions of the Berne Convention for the Protection of Literary and Artistic Works.
#---------------------------------------------------------------------------------------------------------------------------

try:
	import MainWin
except ImportError:
	from CrossMgrVideo import MainWin

import multiprocessing
if __name__ == '__main__':
	multiprocessing.freeze_support()
	MainWin.MainLoop()
