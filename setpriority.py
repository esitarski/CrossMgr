def setpriority(pid=None,priority=1):
	""" Set The Priority of a Windows Process.  Priority is a value between 0-5 where
		2 is normal priority.  Default sets the priority of the current
		python process but can take any valid process ID. """

	try:
		import win32api
		import win32process
		import win32con
		
		priorityclasses = [	win32process.IDLE_PRIORITY_CLASS,
							win32process.BELOW_NORMAL_PRIORITY_CLASS,
							win32process.NORMAL_PRIORITY_CLASS,
							win32process.ABOVE_NORMAL_PRIORITY_CLASS,
							win32process.HIGH_PRIORITY_CLASS,
							win32process.REALTIME_PRIORITY_CLASS]
		if pid is None:
			pid = win32api.GetCurrentProcessId()
		handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
		win32process.SetPriorityClass(handle, priorityclasses[priority])
		
	except ImportError:
		# win32pi not installed.
		pass
