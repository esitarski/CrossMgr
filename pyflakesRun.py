import glob
import sys
import subprocess

for f in sorted(glob.glob('*.py')):
	with subprocess.Popen( ['pyflakes', f], stdout=subprocess.PIPE ) as p:
		ret = p.stdout.read().decode()
		for line in ret.split('\r\n'):
			line = line.strip()
			if "undefined name '_'" in line:
				continue
				
			sys.stdout.write( '{}\n'.format(line) )
			