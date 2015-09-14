import subprocess
import os

def LaunchFileBrowser( path ):
	# Try the default startfile.
	try:
		os.startfile( path )
		return
	except:
		pass

	# Keep trying a command until something works.
	for cmd in ['nautilus', 'open', 'dolphin']:
		try:
			subprocess.Popen( '{} "{}"'.format(cmd, path) )
			break
		except:
			pass
			
if __name__ == '__main__':
	LaunchFileBrowser( '.' )
