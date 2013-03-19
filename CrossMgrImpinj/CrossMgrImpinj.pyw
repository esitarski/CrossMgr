try:
	import MainWin
except ImportError:
	from CrossMgr import MainWin
	
from multiprocessing import freeze_support

if __name__ == '__main__':
	freeze_support()			# Required so that multiprocessing works with py2exe.
	MainWin.MainLoop()
