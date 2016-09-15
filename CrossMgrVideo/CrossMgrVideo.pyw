#---------------------------------------------------------------------------------------------------------------------------
# This software is protected under the provisions of the Berne Convention for the Protection of Literary and Artistic Works.
#---------------------------------------------------------------------------------------------------------------------------

try:
	import MainWin
except ImportError:
	from CrossMgrCamera import MainWin

if __name__ == '__main__':
	MainWin.MainLoop()